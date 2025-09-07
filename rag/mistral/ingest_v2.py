#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    UnstructuredMarkdownLoader,
    CSVLoader,
    JSONLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import settings
from utils.logger import StructuredLogger
from utils.security import SecurityValidator
from core.vector_store import VectorStoreFactory, VectorStoreManager
from utils.cache import get_cache


logger = StructuredLogger(__name__, log_file=Path("logs/ingest.log"))
cache = get_cache()


class DocumentProcessor:
    """Processa documenti per l'ingestione"""
    
    def __init__(self):
        self.security_validator = SecurityValidator()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.supported_loaders = {
            ".pdf": PyPDFLoader,
            ".txt": lambda path: TextLoader(path, encoding='utf-8'),
            ".md": UnstructuredMarkdownLoader,
            ".csv": CSVLoader,
            ".json": lambda path: JSONLoader(path, jq_schema='.[]', text_content=False)
        }
    
    def validate_file(self, file_path: Path) -> bool:
        """Valida un file prima del processing"""
        # Verifica estensione
        if file_path.suffix.lower() not in settings.allowed_file_extensions:
            logger.warning(f"Estensione non supportata: {file_path}")
            return False
        
        # Verifica path sicuro
        if not self.security_validator.validate_file_path(file_path, settings.documents_path):
            logger.warning(f"Path non sicuro: {file_path}")
            return False
        
        # Verifica dimensione
        if not self.security_validator.validate_file_size(file_path, settings.max_file_size_mb):
            logger.warning(f"File troppo grande: {file_path}")
            return False
        
        return True
    
    def load_document(self, file_path: Path) -> List[Document]:
        """Carica un singolo documento"""
        if not self.validate_file(file_path):
            return []
        
        try:
            # Check cache
            cache_key = f"doc:{file_path}:{file_path.stat().st_mtime}"
            cached_docs = cache.get(cache_key)
            if cached_docs:
                logger.debug(f"Documento caricato da cache: {file_path}")
                return cached_docs
            
            # Carica documento
            file_ext = file_path.suffix.lower()
            if file_ext not in self.supported_loaders:
                logger.warning(f"Loader non trovato per: {file_ext}")
                return []
            
            loader_class = self.supported_loaders[file_ext]
            loader = loader_class(str(file_path))
            documents = loader.load()
            
            # Aggiungi metadata
            for doc in documents:
                doc.metadata.update({
                    "source": str(file_path),
                    "file_name": file_path.name,
                    "file_type": file_ext[1:],  # Rimuovi il punto
                    "file_size_mb": file_path.stat().st_size / (1024 * 1024)
                })
            
            # Cache result
            cache.set(cache_key, documents, ttl=3600)
            
            logger.info(f"Caricato {file_path.name} ({len(documents)} pagine/sezioni)")
            return documents
            
        except Exception as e:
            logger.error(f"Errore caricamento documento", exception=e, file=str(file_path))
            return []
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """Processa e splitta documenti"""
        try:
            # Splitta in chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Aggiungi metadata ai chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)
            
            logger.info(f"Creati {len(chunks)} chunks da {len(documents)} documenti")
            return chunks
            
        except Exception as e:
            logger.error(f"Errore processing documenti", exception=e)
            return []
    
    def load_all_documents(self, directory: Path) -> List[Document]:
        """Carica tutti i documenti da una directory"""
        all_documents = []
        file_paths = []
        
        # Raccogli tutti i file
        for ext in settings.allowed_file_extensions:
            file_paths.extend(directory.glob(f"*{ext}"))
            file_paths.extend(directory.glob(f"**/*{ext}"))  # Ricorsivo
        
        if not file_paths:
            logger.warning(f"Nessun file trovato in {directory}")
            return []
        
        # Carica in parallelo
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self.load_document, file_path): file_path 
                for file_path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    documents = future.result()
                    all_documents.extend(documents)
                except Exception as e:
                    logger.error(f"Errore caricamento parallelo", exception=e, file=str(file_path))
        
        return all_documents


class IngestPipeline:
    """Pipeline completa di ingestione"""
    
    def __init__(self, vector_store_type: str = "faiss"):
        self.processor = DocumentProcessor()
        self.vector_store = VectorStoreFactory.create(vector_store_type)
        self.vector_manager = VectorStoreManager(self.vector_store)
        logger.info(f"Pipeline inizializzata con {vector_store_type} vector store")
    
    def run(self, documents_path: Path = None) -> Dict[str, Any]:
        """Esegue pipeline di ingestione"""
        documents_path = documents_path or settings.documents_path
        
        logger.info(f"Avvio ingestione da: {documents_path}")
        
        # 1. Carica documenti
        logger.info("Fase 1: Caricamento documenti...")
        raw_documents = self.processor.load_all_documents(documents_path)
        
        if not raw_documents:
            logger.error("Nessun documento caricato")
            return {"status": "error", "message": "Nessun documento caricato"}
        
        # 2. Processa documenti
        logger.info("Fase 2: Processing documenti...")
        chunks = self.processor.process_documents(raw_documents)
        
        if not chunks:
            logger.error("Nessun chunk creato")
            return {"status": "error", "message": "Nessun chunk creato"}
        
        # 3. Crea embeddings e salva
        logger.info("Fase 3: Creazione embeddings e indicizzazione...")
        try:
            self.vector_store.add_documents(chunks)
            self.vector_store.save(settings.faiss_index_path)
            
            # Statistiche
            stats = {
                "status": "success",
                "documents_loaded": len(raw_documents),
                "chunks_created": len(chunks),
                "unique_sources": len(set(doc.metadata.get("source", "") for doc in chunks)),
                "total_size_mb": sum(doc.metadata.get("file_size_mb", 0) for doc in raw_documents)
            }
            
            logger.info("Ingestione completata", **stats)
            return stats
            
        except Exception as e:
            logger.error("Errore nella creazione embeddings", exception=e)
            return {"status": "error", "message": str(e)}
    
    def update_document(self, file_path: Path) -> Dict[str, Any]:
        """Aggiorna un singolo documento nell'indice"""
        logger.info(f"Aggiornamento documento: {file_path}")
        
        # Carica documento
        documents = self.processor.load_document(file_path)
        if not documents:
            return {"status": "error", "message": "Impossibile caricare documento"}
        
        # Processa
        chunks = self.processor.process_documents(documents)
        
        # TODO: Implementare rimozione vecchi chunks prima di aggiungere nuovi
        # Per ora aggiungiamo solo i nuovi
        
        try:
            self.vector_store.add_documents(chunks)
            self.vector_store.save(settings.faiss_index_path)
            
            return {
                "status": "success",
                "chunks_added": len(chunks)
            }
        except Exception as e:
            logger.error("Errore aggiornamento documento", exception=e)
            return {"status": "error", "message": str(e)}


def main():
    """Entry point"""
    try:
        # Verifica API key
        if not settings.mistral_api_key:
            logger.error("MISTRAL_API_KEY non configurata")
            print("❌ MISTRAL_API_KEY non trovata nel file .env")
            return
        
        # Verifica directory documenti
        if not settings.documents_path.exists():
            logger.error(f"Directory documenti non trovata: {settings.documents_path}")
            print(f"❌ Directory '{settings.documents_path}' non trovata")
            return
        
        # Esegui pipeline
        pipeline = IngestPipeline()
        result = pipeline.run()
        
        if result["status"] == "success":
            print("\n✅ Ingestione completata con successo!")
            print(f"📄 Documenti caricati: {result['documents_loaded']}")
            print(f"🔢 Chunks creati: {result['chunks_created']}")
            print(f"📁 Sorgenti uniche: {result['unique_sources']}")
            print(f"💾 Dimensione totale: {result['total_size_mb']:.2f} MB")
        else:
            print(f"\n❌ Errore: {result['message']}")
            
    except Exception as e:
        logger.critical("Errore critico nella pipeline", exception=e)
        print(f"\n❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()