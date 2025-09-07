#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import settings
from utils.logger import StructuredLogger
from utils.security import SecurityValidator, RateLimiter, generate_session_id
from utils.cache import get_cache
from core.vector_store import VectorStoreFactory, VectorStoreManager


logger = StructuredLogger(__name__, log_file=Path("logs/chatbot.log"))
cache = get_cache()
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)


class ConversationMemory:
    """Gestisce la memoria delle conversazioni"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """Aggiunge un messaggio alla conversazione"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Mantieni solo gli ultimi N messaggi
        if len(self.conversations[session_id]) > self.max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2:]
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Ottiene la storia della conversazione"""
        return self.conversations.get(session_id, [])
    
    def clear(self, session_id: str):
        """Pulisce la conversazione"""
        if session_id in self.conversations:
            del self.conversations[session_id]


class RAGChatbot:
    """Chatbot RAG migliorato"""
    
    def __init__(self, vector_store_type: str = "faiss"):
        # Inizializza componenti
        self.security_validator = SecurityValidator()
        self.memory = ConversationMemory()
        
        # Carica vector store
        self.vector_store = VectorStoreFactory.create(vector_store_type)
        self.vector_store.load(settings.faiss_index_path)
        self.vector_manager = VectorStoreManager(self.vector_store)
        
        # Inizializza LLM
        self.llm = ChatMistralAI(
            model=settings.llm_model_name,
            mistral_api_key=settings.mistral_api_key,
            temperature=settings.temperature,
            max_retries=3,
            timeout=30
        )
        
        # Prompt templates
        self.system_prompt = """Sei un assistente virtuale esperto e professionale. 
Il tuo compito è rispondere alle domande basandoti ESCLUSIVAMENTE sulle informazioni fornite nel contesto.

Regole importanti:
1. Usa SOLO le informazioni dal contesto fornito
2. Se non trovi informazioni sufficienti, dillo chiaramente
3. Sii conciso ma completo nelle risposte
4. Mantieni un tono professionale e cortese
5. Se la domanda è ambigua, chiedi chiarimenti
6. Cita le fonti quando possibile (usa i metadata)

NON inventare MAI informazioni non presenti nel contesto."""

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history", optional=True),
            ("human", "Contesto:\n{context}\n\nDomanda: {question}")
        ])
        
        logger.info(f"RAG Chatbot inizializzato con {vector_store_type}")
    
    def format_docs(self, docs: List[Document]) -> str:
        """Formatta documenti per il contesto"""
        if not docs:
            return "Nessun documento rilevante trovato."
        
        formatted_docs = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            chunk_info = f"Chunk {doc.metadata.get('chunk_index', '?')}/{doc.metadata.get('total_chunks', '?')}"
            
            formatted_docs.append(
                f"[Documento {i} - {Path(source).name} - {chunk_info}]\n"
                f"{doc.page_content}\n"
            )
        
        return "\n---\n".join(formatted_docs)
    
    def retrieve_context(self, query: str, session_id: str) -> Tuple[List[Document], str]:
        """Recupera contesto rilevante"""
        # Sanitizza query
        clean_query = self.security_validator.sanitize_user_input(query)
        
        # Check cache
        cache_key = f"context:{session_id}:{hash(clean_query)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug("Contesto recuperato da cache", session_id=session_id)
            return cached_result
        
        # Recupera documenti con ricerca ibrida
        retrieved_docs = self.vector_manager.hybrid_search(
            clean_query, 
            k=settings.top_k_chunks,
            keyword_weight=0.3
        )
        
        # Formatta contesto
        formatted_context = self.format_docs(retrieved_docs)
        
        # Cache result
        result = (retrieved_docs, formatted_context)
        cache.set(cache_key, result, ttl=settings.cache_ttl_seconds)
        
        logger.info(
            "Documenti recuperati",
            session_id=session_id,
            query_length=len(clean_query),
            docs_found=len(retrieved_docs)
        )
        
        return result
    
    @rate_limiter.rate_limit_decorator(lambda self, query, session_id: session_id)
    async def generate_response(self, query: str, session_id: str) -> Dict[str, Any]:
        """Genera risposta alla query"""
        start_time = datetime.utcnow()
        
        try:
            # Recupera contesto
            retrieved_docs, context = self.retrieve_context(query, session_id)
            
            # Prepara storia conversazione
            history = []
            for msg in self.memory.get_history(session_id)[-6:]:  # Ultimi 3 scambi
                if msg["role"] == "user":
                    history.append(HumanMessage(content=msg["content"]))
                else:
                    history.append(AIMessage(content=msg["content"]))
            
            # Genera risposta
            response = await self.llm.ainvoke(
                self.prompt_template.format_messages(
                    context=context,
                    question=query,
                    history=history
                )
            )
            
            response_text = response.content
            
            # Salva in memoria
            self.memory.add_message(session_id, "user", query)
            self.memory.add_message(session_id, "assistant", response_text)
            
            # Calcola metriche
            elapsed_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "response": response_text,
                "sources": [doc.metadata.get("source", "Unknown") for doc in retrieved_docs],
                "chunks_used": len(retrieved_docs),
                "response_time": elapsed_time,
                "cached": False,
                "session_id": session_id
            }
            
            logger.info(
                "Risposta generata",
                session_id=session_id,
                response_time=elapsed_time,
                chunks_used=len(retrieved_docs)
            )
            
            return result
            
        except Exception as e:
            logger.error("Errore generazione risposta", exception=e, session_id=session_id)
            return {
                "response": "Mi dispiace, si è verificato un errore nell'elaborazione della richiesta.",
                "error": str(e),
                "session_id": session_id
            }
    
    def run_interactive(self):
        """Modalità interattiva CLI"""
        print("\n🤖 RAG Chatbot v2.0")
        print("=" * 50)
        print("Comandi speciali:")
        print("  /new     - Nuova conversazione")
        print("  /history - Mostra storia conversazione")
        print("  /stats   - Mostra statistiche")
        print("  /exit    - Esci")
        print("=" * 50)
        
        session_id = generate_session_id()
        print(f"\n📝 Sessione: {session_id[:8]}...")
        
        while True:
            try:
                user_input = input("\n👤 Tu: ").strip()
                
                if not user_input:
                    continue
                
                # Gestisci comandi speciali
                if user_input.lower() == "/exit":
                    print("\n👋 Arrivederci!")
                    break
                
                if user_input.lower() == "/new":
                    self.memory.clear(session_id)
                    session_id = generate_session_id()
                    print(f"\n🆕 Nuova sessione: {session_id[:8]}...")
                    continue
                
                if user_input.lower() == "/history":
                    history = self.memory.get_history(session_id)
                    if not history:
                        print("\n📭 Nessuna conversazione in memoria")
                    else:
                        print("\n📜 Storia conversazione:")
                        for msg in history:
                            role_emoji = "👤" if msg["role"] == "user" else "🤖"
                            print(f"\n{role_emoji} {msg['role'].title()} ({msg['timestamp']}):")
                            print(f"   {msg['content'][:100]}...")
                    continue
                
                if user_input.lower() == "/stats":
                    stats = cache.get_stats()
                    print("\n📊 Statistiche:")
                    print(f"   Cache hits: {stats['hits']}")
                    print(f"   Cache misses: {stats['misses']}")
                    print(f"   Hit rate: {stats['hit_rate']:.1%}")
                    continue
                
                # Genera risposta
                print("\n🤖 Bot: ", end="", flush=True)
                print("⏳ Sto pensando...", end="\r", flush=True)
                
                # Run async
                result = asyncio.run(self.generate_response(user_input, session_id))
                
                # Pulisci linea e mostra risposta
                print(" " * 50, end="\r")  # Clear line
                print(f"🤖 Bot: {result['response']}")
                
                # Mostra metadata se disponibili
                if result.get('sources'):
                    unique_sources = list(set(Path(s).name for s in result['sources']))
                    print(f"\n📚 Fonti: {', '.join(unique_sources[:3])}")
                
                if result.get('response_time'):
                    print(f"⏱️  Tempo: {result['response_time']:.2f}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrotto. Arrivederci!")
                break
            except Exception as e:
                logger.error("Errore nel loop interattivo", exception=e)
                print(f"\n❌ Errore: {e}")


def main():
    """Entry point"""
    try:
        # Verifica configurazione
        if not settings.mistral_api_key:
            print("❌ MISTRAL_API_KEY non configurata")
            return
        
        if not settings.faiss_index_path.exists():
            print(f"❌ Indice non trovato. Esegui prima ingest_v2.py")
            return
        
        # Avvia chatbot
        chatbot = RAGChatbot()
        chatbot.run_interactive()
        
    except Exception as e:
        logger.critical("Errore critico", exception=e)
        print(f"\n❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()