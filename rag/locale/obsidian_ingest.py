#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Obsidian RAG Ingest System
Indicizza il vault Obsidian preservando struttura e metadati
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import settings


class ObsidianIngest:
    def __init__(self, vault_path: str = "/opt/obsidian/appunti"):
        self.vault_path = Path(vault_path)
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self.min_chunk_size = 100  # Chunk minimo per file molto corti
        
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Estrae metadati dal percorso file e contenuto"""
        relative_path = file_path.relative_to(self.vault_path)
        parts = relative_path.parts
        
        metadata = {
            "source": str(file_path),
            "relative_path": str(relative_path),
            "filename": file_path.name,
            "file_stem": file_path.stem,
            "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        }
        
        # Estrai informazioni dalla struttura directory
        if len(parts) >= 2:
            if parts[0] == "Clienti" and len(parts) >= 2:
                metadata["tipo"] = "cliente"
                metadata["cliente"] = parts[1]
                if len(parts) >= 3:
                    metadata["categoria"] = parts[2]
            elif parts[0] == "Journal":
                metadata["tipo"] = "journal"
                # Estrai data dal filename se possibile
                date_match = re.search(r'(\d{2}-\d{2}-\d{4})', file_path.name)
                if date_match:
                    metadata["data"] = date_match.group(1)
            elif parts[0] == "Paolo":
                metadata["tipo"] = "personale"
                if len(parts) >= 2:
                    metadata["categoria"] = parts[1]
            elif parts[0] == "Tact":
                metadata["tipo"] = "tact"
                if len(parts) >= 3 and parts[1] == "Clienti":
                    metadata["tipo"] = "tact_cliente"
                    metadata["cliente"] = parts[2]
                    metadata["agenzia"] = "Tact"
                    if len(parts) >= 4:
                        metadata["categoria"] = parts[3]
                
        return metadata
    
    def load_markdown_with_metadata(self, file_path: Path) -> List[Document]:
        """Carica file markdown con metadati ricchi"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Estrai metadati
            metadata = self.extract_metadata(file_path)
            
            # Aggiungi informazioni dal contenuto
            if content:
                # Cerca date nel contenuto
                date_patterns = [
                    r'(\d{2}/\d{2}/\d{4})',  # 14/05/2025
                    r'(\d{1,2}/\d{1,2}/\d{4})',  # 1/5/2025
                    r'(\d{4}-\d{2}-\d{2})',  # 2025-05-14
                ]
                
                for pattern in date_patterns:
                    dates = re.findall(pattern, content)
                    if dates:
                        metadata["date_mentioned"] = dates[0]
                        break
                
                # Cerca prezzi
                price_patterns = [
                    r'€(\d+)',  # €400
                    r'(\d+)€',  # 400€
                    r'(\d+)\s*euro',  # 400 euro
                ]
                
                prices = []
                for pattern in price_patterns:
                    found_prices = re.findall(pattern, content)
                    prices.extend(found_prices)
                
                if prices:
                    metadata["prices"] = prices
                
                # Conta parole per importanza
                metadata["word_count"] = len(content.split())
                
                # Primo paragrafo come summary
                first_paragraph = content.split('\n\n')[0][:200]
                metadata["summary"] = first_paragraph
            
            # Arricchisci il contenuto con informazioni contestuali per migliorare il retrieval
            enriched_content = content
            
            # Aggiungi info sul cliente e file se disponibili
            if metadata.get("tipo") == "cliente" and metadata.get("cliente"):
                context_header = f"[Cliente: {metadata['cliente']} - File: {metadata['filename']}]\n\n"
                enriched_content = context_header + content
            
            # Crea documento
            document = Document(
                page_content=enriched_content,
                metadata=metadata
            )
            
            return [document]
            
        except Exception as e:
            print(f"Errore caricamento {file_path}: {e}")
            return []
    
    def load_vault(self) -> List[Document]:
        """Carica tutto il vault Obsidian"""
        documents = []
        
        # Trova tutti i file markdown
        md_files = list(self.vault_path.rglob("*.md"))
        
        print(f"📚 Trovati {len(md_files)} file markdown nel vault")
        
        for file_path in md_files:
            # Salta file di sistema
            if file_path.name.startswith('.'):
                continue
                
            # Carica documento
            docs = self.load_markdown_with_metadata(file_path)
            documents.extend(docs)
            
            if len(documents) % 50 == 0:
                print(f"📄 Caricati {len(documents)} documenti...")
        
        print(f"✅ Caricati {len(documents)} documenti totali")
        return documents
    
    def create_index(self, output_path: str = "obsidian_index"):
        """Crea indice FAISS dal vault Obsidian"""
        print("🔍 Caricamento vault Obsidian...")
        documents = self.load_vault()
        
        if not documents:
            print("❌ Nessun documento caricato")
            return
        
        print("✂️ Chunking documenti...")
        chunks = []
        
        for doc in documents:
            # Se il documento è molto corto, mantienilo intero
            if len(doc.page_content.strip()) <= self.min_chunk_size:
                # Aggiungi metadati per identificare chunk piccoli
                doc.metadata["is_short_file"] = True
                doc.metadata["original_length"] = len(doc.page_content)
                chunks.append(doc)
                print(f"📄 File corto mantenuto intero: {doc.metadata.get('filename', 'N/A')} ({len(doc.page_content)} char)")
            else:
                # Chunking normale per file lunghi
                doc_chunks = self.text_splitter.split_documents([doc])
                chunks.extend(doc_chunks)
        
        print(f"📊 Creati {len(chunks)} chunk totali")
        
        # Aggiungi metadati di chunking
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_index"] = i
        
        print("🧮 Creazione embeddings...")
        vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        print(f"💾 Salvataggio indice in {output_path}...")
        vector_store.save_local(output_path)
        
        print("✅ Indice Obsidian creato con successo!")
        
        # Statistiche
        clients = set()
        types = set()
        for doc in documents:
            if "cliente" in doc.metadata:
                clients.add(doc.metadata["cliente"])
            if "tipo" in doc.metadata:
                types.add(doc.metadata["tipo"])
        
        print(f"📈 Statistiche:")
        print(f"  - Clienti: {len(clients)} ({', '.join(sorted(clients))})")
        print(f"  - Tipi: {len(types)} ({', '.join(sorted(types))})")
        print(f"  - Documenti: {len(documents)}")
        print(f"  - Chunk: {len(chunks)}")


def main():
    """Script principale"""
    print("=== Obsidian RAG Ingest ===")
    
    ingest = ObsidianIngest()
    ingest.create_index()


if __name__ == "__main__":
    main()