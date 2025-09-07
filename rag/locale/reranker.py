#!/usr/bin/env python3
"""
Modulo di reranking per migliorare la precisione del retrieval.
Usa un Cross-Encoder per riordinare i documenti recuperati dal hybrid search.
"""

import numpy as np
from typing import List, Tuple
from sentence_transformers import CrossEncoder
from langchain.schema import Document
import time
from utils.logger import StructuredLogger

logger = StructuredLogger(__name__)

class CrossEncoderReranker:
    """
    Reranker basato su Cross-Encoder per riordinare documenti
    in base alla rilevanza rispetto alla query.
    """
    
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        """
        Inizializza il reranker con un modello cross-encoder.
        
        Args:
            model_name: Nome del modello HuggingFace da usare
        """
        logger.info(f"Inizializzazione Cross-Encoder reranker con modello: {model_name}")
        self.model = CrossEncoder(model_name)
        self.model_name = model_name
        
    def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """
        Riordina i documenti in base alla rilevanza rispetto alla query.
        
        Args:
            query: Query di ricerca
            documents: Lista di documenti da riordinare
            top_k: Numero di documenti top da restituire
            
        Returns:
            Lista dei top_k documenti riordinati
        """
        if not documents:
            return []
            
        start_time = time.time()
        
        # Prepara coppie query-documento
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Calcola scores di rilevanza
        logger.info(f"Calcolo scores per {len(pairs)} documenti...")
        scores = self.model.predict(pairs)
        
        # Riordina per score decrescente
        sorted_indices = np.argsort(scores)[::-1]
        
        # Prendi solo i top_k
        top_indices = sorted_indices[:min(top_k, len(documents))]
        reranked_docs = [documents[i] for i in top_indices]
        
        # Log dei risultati
        elapsed_time = time.time() - start_time
        logger.info(f"Reranking completato in {elapsed_time:.2f}s")
        
        # Debug: mostra top scores
        for i, idx in enumerate(top_indices[:3]):
            score = scores[idx]
            doc = documents[idx]
            source = doc.metadata.get('source', 'unknown')
            logger.debug(f"  {i+1}. Score: {score:.3f} - {source}")
        
        return reranked_docs
    
    def rerank_with_scores(self, query: str, documents: List[Document], top_k: int = 5) -> List[Tuple[Document, float]]:
        """
        Riordina i documenti restituendo anche gli scores.
        
        Args:
            query: Query di ricerca
            documents: Lista di documenti da riordinare
            top_k: Numero di documenti top da restituire
            
        Returns:
            Lista di tuple (documento, score)
        """
        if not documents:
            return []
            
        # Prepara coppie query-documento
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Calcola scores
        scores = self.model.predict(pairs)
        
        # Riordina per score decrescente
        sorted_indices = np.argsort(scores)[::-1]
        
        # Prendi solo i top_k con scores
        top_indices = sorted_indices[:min(top_k, len(documents))]
        results = [(documents[i], scores[i]) for i in top_indices]
        
        return results


class LightweightReranker:
    """
    Reranker leggero basato su similarità semantica migliorata.
    Alternativa più veloce al Cross-Encoder per sistemi con vincoli di risorse.
    """
    
    def __init__(self):
        """Inizializza il reranker leggero."""
        from langchain_huggingface import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
    def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """
        Riordina usando embeddings e boost intelligenti.
        
        Args:
            query: Query di ricerca
            documents: Lista di documenti da riordinare
            top_k: Numero di documenti top da restituire
            
        Returns:
            Lista dei top_k documenti riordinati
        """
        if not documents:
            return []
            
        # Calcola embedding della query
        query_embedding = self.embeddings.embed_query(query)
        
        # Calcola scores per ogni documento
        doc_scores = []
        for doc in documents:
            # Embedding del documento
            doc_embedding = self.embeddings.embed_query(doc.page_content[:500])
            
            # Similarità coseno
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            
            # Boost basati su metadata
            boost = 1.0
            metadata = doc.metadata
            
            # Boost per documenti recenti
            if metadata.get('modified_time'):
                # Implementa logica per boost temporale
                pass
                
            # Boost per match esatti nel titolo/filename
            filename = metadata.get('filename', '').lower()
            if any(term in filename for term in query.lower().split()):
                boost *= 1.5
                
            final_score = similarity * boost
            doc_scores.append((doc, final_score))
        
        # Ordina per score e restituisci top_k
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in doc_scores[:top_k]]


def create_reranker(reranker_type: str = "cross-encoder") -> object:
    """
    Factory function per creare il reranker appropriato.
    
    Args:
        reranker_type: Tipo di reranker ("cross-encoder" o "lightweight")
        
    Returns:
        Istanza del reranker
    """
    if reranker_type == "cross-encoder":
        return CrossEncoderReranker()
    elif reranker_type == "lightweight":
        return LightweightReranker()
    else:
        raise ValueError(f"Tipo di reranker non supportato: {reranker_type}")


if __name__ == "__main__":
    # Test del reranker
    from langchain.schema import Document
    
    # Documenti di esempio
    test_docs = [
        Document(
            page_content="FIS Group è un'azienda leader nel settore chimico",
            metadata={"source": "fis/corpus.md"}
        ),
        Document(
            page_content="I concorrenti principali di FIS sono aziende chimiche internazionali",
            metadata={"source": "fis/concorrenti.md"}
        ),
        Document(
            page_content="Maffeis Engineering si occupa di ingegneria strutturale",
            metadata={"source": "maffeis/corpus.md"}
        ),
    ]
    
    # Test Cross-Encoder
    print("Testing Cross-Encoder Reranker...")
    reranker = CrossEncoderReranker()
    
    query = "Che tipo di azienda è FIS Group?"
    reranked = reranker.rerank_with_scores(query, test_docs, top_k=3)
    
    print(f"\nQuery: {query}")
    print("Risultati reranked:")
    for i, (doc, score) in enumerate(reranked):
        print(f"{i+1}. Score: {score:.3f} - {doc.metadata['source']}")
        print(f"   {doc.page_content[:100]}...")