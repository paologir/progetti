#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script per query con filtering per cliente
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Assicurati di avere la directory corrente nel path
sys.path.insert(0, str(Path(__file__).parent))

from core.vector_store import VectorStoreFactory
from config import settings
from utils.logger import StructuredLogger

logger = StructuredLogger(__name__)


class ClientQuerySystem:
    """Sistema di query con filtering per cliente"""
    
    def __init__(self, faiss_index_path: Path = None):
        self.faiss_index_path = faiss_index_path or settings.faiss_index_path
        self.vector_store = None
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Carica il vector store"""
        try:
            self.vector_store = VectorStoreFactory.create("faiss")
            if self.faiss_index_path.exists():
                self.vector_store.load(self.faiss_index_path)
                logger.info(f"Vector store caricato da: {self.faiss_index_path}")
            else:
                logger.warning(f"Vector store non trovato in: {self.faiss_index_path}")
        except Exception as e:
            logger.error(f"Errore caricamento vector store: {e}")
            raise
    
    def search(self, query: str, k: int = 5, client_filter: str = None, 
               file_type_filter: str = None, folder_filter: str = None) -> List[Dict]:
        """
        Cerca documenti con filtering opzionale
        
        Args:
            query: Query di ricerca
            k: Numero di risultati
            client_filter: Nome cliente per filtrare
            file_type_filter: Tipo file (pdf, docx, etc.)
            folder_filter: Sottocartella per filtrare
        """
        if not self.vector_store:
            raise RuntimeError("Vector store non caricato")
        
        # Esegui ricerca base
        results = self.vector_store.similarity_search(query, k=k*3)  # Prendi più risultati per filtering
        
        # Applica filtri
        filtered_results = []
        
        for result in results:
            metadata = result.metadata
            
            # Filtro per cliente
            if client_filter and metadata.get('client_name') != client_filter:
                continue
            
            # Filtro per tipo file
            if file_type_filter and metadata.get('file_type') != file_type_filter:
                continue
            
            # Filtro per sottocartella
            if folder_filter and folder_filter not in metadata.get('subfolder', ''):
                continue
            
            filtered_results.append({
                'content': result.page_content,
                'metadata': metadata,
                'score': getattr(result, 'score', 0.0)
            })
            
            if len(filtered_results) >= k:
                break
        
        return filtered_results
    
    def get_available_clients(self) -> List[str]:
        """Ottiene lista clienti disponibili nell'indice"""
        if not self.vector_store:
            return []
        
        # Questo è un po' costoso ma fornisce info utile
        all_docs = self.vector_store.similarity_search("", k=10000)
        clients = set()
        
        for doc in all_docs:
            client_name = doc.metadata.get('client_name')
            if client_name:
                clients.add(client_name)
        
        return sorted(list(clients))
    
    def get_client_stats(self, client_name: str) -> Dict:
        """Ottiene statistiche per un cliente specifico"""
        if not self.vector_store:
            return {}
        
        # Cerca tutti i documenti del cliente
        all_docs = self.vector_store.similarity_search("", k=10000)
        client_docs = [doc for doc in all_docs if doc.metadata.get('client_name') == client_name]
        
        if not client_docs:
            return {}
        
        # Calcola statistiche
        file_types = {}
        folders = {}
        total_chunks = len(client_docs)
        
        for doc in client_docs:
            file_type = doc.metadata.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
            
            subfolder = doc.metadata.get('subfolder', 'root')
            folders[subfolder] = folders.get(subfolder, 0) + 1
        
        return {
            'total_chunks': total_chunks,
            'file_types': file_types,
            'folders': folders,
            'unique_sources': len(set(doc.metadata.get('source', '') for doc in client_docs))
        }


def main():
    parser = argparse.ArgumentParser(description='Query sistema RAG clienti')
    parser.add_argument('query', nargs='?', help='Query di ricerca')
    parser.add_argument('--client', '-c', help='Filtra per cliente specifico')
    parser.add_argument('--file-type', '-t', help='Filtra per tipo file (pdf, docx, etc.)')
    parser.add_argument('--folder', '-f', help='Filtra per sottocartella')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Numero massimo risultati')
    parser.add_argument('--list-clients', action='store_true', help='Mostra clienti disponibili')
    parser.add_argument('--client-stats', help='Mostra statistiche per cliente')
    parser.add_argument('--interactive', '-i', action='store_true', help='Modalità interattiva')
    
    args = parser.parse_args()
    
    # Inizializza sistema
    try:
        query_system = ClientQuerySystem()
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        return 1
    
    # Lista clienti
    if args.list_clients:
        print("👥 Clienti disponibili:")
        clients = query_system.get_available_clients()
        for client in clients:
            print(f"  - {client}")
        return 0
    
    # Statistiche cliente
    if args.client_stats:
        print(f"📊 Statistiche per cliente: {args.client_stats}")
        stats = query_system.get_client_stats(args.client_stats)
        if stats:
            print(f"  Chunks totali: {stats['total_chunks']}")
            print(f"  File unici: {stats['unique_sources']}")
            print(f"  Tipi file: {stats['file_types']}")
            print(f"  Cartelle: {stats['folders']}")
        else:
            print("  Nessun dato trovato per questo cliente")
        return 0
    
    # Modalità interattiva
    if args.interactive:
        print("🔍 Modalità Query Interattiva")
        print("Usa 'exit' per uscire, 'help' per aiuto")
        
        while True:
            try:
                query = input("\n> ").strip()
                
                if query.lower() == 'exit':
                    break
                
                if query.lower() == 'help':
                    print("""
Comandi disponibili:
  - <query>: Cerca documenti
  - client:<nome>: Filtra per cliente
  - type:<tipo>: Filtra per tipo file
  - folder:<cartella>: Filtra per cartella
  - limit:<n>: Imposta limite risultati
  - clients: Lista clienti disponibili
  - stats:<cliente>: Statistiche cliente
  - exit: Esci
  
Esempio: "proposte contratti client:maspe limit:3"
                    """)
                    continue
                
                if query.lower() == 'clients':
                    clients = query_system.get_available_clients()
                    print("Clienti:", ", ".join(clients))
                    continue
                
                if query.startswith('stats:'):
                    client_name = query[6:]
                    stats = query_system.get_client_stats(client_name)
                    if stats:
                        print(f"Statistiche {client_name}:")
                        print(f"  Chunks: {stats['total_chunks']}")
                        print(f"  File: {stats['unique_sources']}")
                        print(f"  Tipi: {stats['file_types']}")
                    else:
                        print(f"Nessun dato per {client_name}")
                    continue
                
                # Parsing query e filtri
                parts = query.split()
                actual_query = []
                client_filter = None
                file_type_filter = None
                folder_filter = None
                limit = 5
                
                for part in parts:
                    if part.startswith('client:'):
                        client_filter = part[7:]
                    elif part.startswith('type:'):
                        file_type_filter = part[5:]
                    elif part.startswith('folder:'):
                        folder_filter = part[7:]
                    elif part.startswith('limit:'):
                        limit = int(part[6:])
                    else:
                        actual_query.append(part)
                
                if not actual_query:
                    print("❌ Query vuota")
                    continue
                
                query_text = ' '.join(actual_query)
                
                # Esegui ricerca
                results = query_system.search(
                    query_text, 
                    k=limit,
                    client_filter=client_filter,
                    file_type_filter=file_type_filter,
                    folder_filter=folder_filter
                )
                
                # Mostra risultati
                print(f"\n📋 {len(results)} risultati per '{query_text}':")
                
                for i, result in enumerate(results, 1):
                    metadata = result['metadata']
                    print(f"\n{i}. {metadata.get('file_name', 'Unknown')} ({metadata.get('client_name', 'Unknown')})")
                    print(f"   📁 {metadata.get('subfolder', 'root')} | 📄 {metadata.get('file_type', 'unknown')}")
                    print(f"   📝 {result['content'][:200]}...")
                
                if not results:
                    print("❌ Nessun risultato trovato")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Errore: {e}")
        
        return 0
    
    # Query singola
    if not args.query:
        print("❌ Query richiesta. Usa --help per opzioni")
        return 1
    
    try:
        results = query_system.search(
            args.query,
            k=args.limit,
            client_filter=args.client,
            file_type_filter=args.file_type,
            folder_filter=args.folder
        )
        
        print(f"📋 {len(results)} risultati per '{args.query}':")
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            print(f"\n{i}. {metadata.get('file_name', 'Unknown')} ({metadata.get('client_name', 'Unknown')})")
            print(f"   📁 {metadata.get('subfolder', 'root')} | 📄 {metadata.get('file_type', 'unknown')}")
            print(f"   📝 {result['content'][:300]}...")
        
        if not results:
            print("❌ Nessun risultato trovato")
            
    except Exception as e:
        print(f"❌ Errore durante query: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())