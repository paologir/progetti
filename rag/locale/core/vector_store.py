#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import numpy as np

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb

from utils.logger import StructuredLogger
from config import settings


logger = StructuredLogger(__name__)


class VectorStore(ABC):
    """Abstract base class per vector stores"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Aggiunge documenti al vector store"""
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Cerca documenti simili"""
        pass
    
    @abstractmethod
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Cerca documenti simili con score"""
        pass
    
    @abstractmethod
    def save(self, path: Path) -> None:
        """Salva il vector store"""
        pass
    
    @abstractmethod
    def load(self, path: Path) -> None:
        """Carica il vector store"""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Elimina documenti per ID"""
        pass


class FAISSVectorStore(VectorStore):
    """Implementazione FAISS del vector store"""
    
    def __init__(self, embedding_model_name: str = None):
        self.embedding_model_name = embedding_model_name or settings.embedding_model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.vector_store: Optional[FAISS] = None
        logger.info(f"Inizializzato FAISS vector store con modello: {self.embedding_model_name}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Aggiunge documenti al vector store"""
        try:
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                logger.info(f"Creato nuovo FAISS index con {len(documents)} documenti")
            else:
                self.vector_store.add_documents(documents)
                logger.info(f"Aggiunti {len(documents)} documenti all'index esistente")
        except Exception as e:
            logger.error(f"Errore nell'aggiunta documenti", exception=e)
            raise
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Cerca documenti simili"""
        if self.vector_store is None:
            logger.warning("Vector store non inizializzato")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Trovati {len(results)} documenti per query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Errore nella ricerca", exception=e, query=query)
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Cerca documenti simili con score"""
        if self.vector_store is None:
            logger.warning("Vector store non inizializzato")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.debug(f"Trovati {len(results)} documenti con score per query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Errore nella ricerca con score", exception=e, query=query)
            return []
    
    def save(self, path: Path) -> None:
        """Salva il vector store"""
        if self.vector_store is None:
            logger.warning("Nessun vector store da salvare")
            return
        
        try:
            self.vector_store.save_local(str(path))
            logger.info(f"Vector store salvato in: {path}")
        except Exception as e:
            logger.error(f"Errore nel salvataggio", exception=e, path=str(path))
            raise
    
    def load(self, path: Path) -> None:
        """Carica il vector store"""
        try:
            # Nota: in produzione, rimuovere allow_dangerous_deserialization
            # e usare un formato di serializzazione sicuro
            self.vector_store = FAISS.load_local(
                str(path), 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Vector store caricato da: {path}")
        except Exception as e:
            logger.error(f"Errore nel caricamento", exception=e, path=str(path))
            raise
    
    def delete(self, ids: List[str]) -> None:
        """FAISS non supporta eliminazione diretta"""
        logger.warning("FAISS non supporta l'eliminazione di documenti singoli")
        raise NotImplementedError("FAISS non supporta l'eliminazione di documenti")


class ChromaVectorStore(VectorStore):
    """Implementazione Chroma del vector store"""
    
    def __init__(self, embedding_model_name: str = None, persist_directory: str = "./chroma_db"):
        self.embedding_model_name = embedding_model_name or settings.embedding_model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self.persist_directory = persist_directory
        
        # Inizializza Chroma client
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "rag_collection"
        
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        logger.info(f"Inizializzato Chroma vector store in: {persist_directory}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Aggiunge documenti al vector store"""
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Aggiunti {len(documents)} documenti a Chroma")
        except Exception as e:
            logger.error(f"Errore nell'aggiunta documenti a Chroma", exception=e)
            raise
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Cerca documenti simili"""
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Trovati {len(results)} documenti in Chroma")
            return results
        except Exception as e:
            logger.error(f"Errore nella ricerca Chroma", exception=e)
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Cerca documenti simili con score"""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Errore nella ricerca con score Chroma", exception=e)
            return []
    
    def save(self, path: Path) -> None:
        """Chroma persiste automaticamente"""
        logger.info("Chroma persiste automaticamente i dati")
    
    def load(self, path: Path) -> None:
        """Chroma carica automaticamente dal persist_directory"""
        logger.info("Chroma carica automaticamente i dati dal persist_directory")
    
    def delete(self, ids: List[str]) -> None:
        """Elimina documenti per ID"""
        try:
            self.vector_store.delete(ids)
            logger.info(f"Eliminati {len(ids)} documenti da Chroma")
        except Exception as e:
            logger.error(f"Errore nell'eliminazione documenti", exception=e)
            raise


class VectorStoreFactory:
    """Factory per creare vector stores"""
    
    @staticmethod
    def create(store_type: str = "faiss", **kwargs) -> VectorStore:
        """Crea un vector store del tipo specificato"""
        store_type = store_type.lower()
        
        if store_type == "faiss":
            return FAISSVectorStore(**kwargs)
        elif store_type == "chroma":
            return ChromaVectorStore(**kwargs)
        else:
            raise ValueError(f"Tipo di vector store non supportato: {store_type}")


class VectorStoreManager:
    """Manager per gestire operazioni avanzate sui vector stores"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        logger.info("Inizializzato VectorStoreManager")
    
    def search_with_metadata_filter(
        self, 
        query: str, 
        k: int = 4, 
        metadata_filter: Dict[str, Any] = None
    ) -> List[Document]:
        """Cerca con filtri sui metadata"""
        # Prima ottieni tutti i risultati
        results = self.vector_store.similarity_search(query, k=k*3)  # Prendi più risultati
        
        if not metadata_filter:
            return results[:k]
        
        # Filtra per metadata
        filtered_results = []
        for doc in results:
            match = True
            for key, value in metadata_filter.items():
                if key not in doc.metadata or doc.metadata[key] != value:
                    match = False
                    break
            if match:
                filtered_results.append(doc)
        
        return filtered_results[:k]
    
    def hybrid_search(
        self,
        query: str,
        k: int = 4,
        keyword_weight: float = 0.3
    ) -> List[Document]:
        """Ricerca ibrida: semantic + keyword"""
        # Ricerca semantica
        semantic_results = self.vector_store.similarity_search_with_score(query, k=k*2)
        
        # Ricerca keyword semplice (scoring basato su presenza parole)
        query_words = set(query.lower().split())
        
        # Combina scores
        combined_scores = {}
        for doc, semantic_score in semantic_results:
            doc_words = set(doc.page_content.lower().split())
            keyword_score = len(query_words.intersection(doc_words)) / len(query_words)
            
            # Combina scores (normalizza semantic score)
            normalized_semantic = 1 / (1 + semantic_score)  # FAISS restituisce distanze
            combined_score = (1 - keyword_weight) * normalized_semantic + keyword_weight * keyword_score
            
            combined_scores[doc] = combined_score
        
        # Ordina per score combinato
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [doc for doc, _ in sorted_results[:k]]