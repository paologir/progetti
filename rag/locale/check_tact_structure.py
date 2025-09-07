#!/usr/bin/env python3

"""
Verifica la struttura Tact nel filesystem e nell'indice
"""

import os
from pathlib import Path

def check_tact_filesystem():
    """Controlla struttura Tact nel filesystem"""
    vault_path = Path("/opt/obsidian/appunti")
    tact_path = vault_path / "Tact"
    
    print("🔍 VERIFICA STRUTTURA TACT NEL FILESYSTEM")
    print("="*60)
    
    if not tact_path.exists():
        print("❌ Directory Tact non trovata")
        return
    
    print(f"✅ Directory Tact trovata: {tact_path}")
    
    # Cerca Tact/Clienti
    tact_clienti_path = tact_path / "Clienti"
    if tact_clienti_path.exists():
        print(f"✅ Directory Tact/Clienti trovata: {tact_clienti_path}")
        
        # Lista clienti Tact
        clienti_tact = []
        for client_dir in tact_clienti_path.iterdir():
            if client_dir.is_dir():
                clienti_tact.append(client_dir.name)
                # Conta file .md
                md_files = list(client_dir.glob("**/*.md"))
                print(f"   📁 {client_dir.name}: {len(md_files)} file .md")
        
        print(f"\n📊 Trovati {len(clienti_tact)} clienti Tact:")
        for cliente in clienti_tact:
            print(f"   • {cliente}")
    else:
        print("❌ Directory Tact/Clienti non trovata")
    
    # Lista tutto in Tact/
    print(f"\n📂 Contenuto completo di {tact_path}:")
    for item in tact_path.iterdir():
        if item.is_dir():
            sub_items = len(list(item.iterdir()))
            print(f"   📁 {item.name}/ ({sub_items} elementi)")
        else:
            print(f"   📄 {item.name}")

def check_tact_in_index():
    """Controlla clienti Tact nell'indice"""
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        from config import settings
        
        print(f"\n🔍 VERIFICA CLIENTI TACT NELL'INDICE")
        print("="*60)
        
        embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
        vector_store = FAISS.load_local('obsidian_index', embeddings, allow_dangerous_deserialization=True)
        
        docstore = vector_store.docstore
        index_to_docstore_id = vector_store.index_to_docstore_id
        
        tact_docs = []
        tact_clienti_docs = []
        
        # Controlla primi 500 documenti per non sovraccaricare
        total_docs = min(500, vector_store.index.ntotal)
        
        for i in range(total_docs):
            try:
                doc_id = index_to_docstore_id[i]
                doc = docstore.search(doc_id)
                if doc:
                    # Tact generici
                    if doc.metadata.get('tipo') == 'tact':
                        tact_docs.append({
                            'cliente': doc.metadata.get('cliente', 'N/A'),
                            'filename': doc.metadata.get('filename', 'N/A'),
                            'path': doc.metadata.get('relative_path', 'N/A')
                        })
                    
                    # Tact clienti
                    if doc.metadata.get('tipo') == 'tact_cliente':
                        tact_clienti_docs.append({
                            'cliente': doc.metadata.get('cliente', 'N/A'),
                            'filename': doc.metadata.get('filename', 'N/A'),
                            'agenzia': doc.metadata.get('agenzia', 'N/A'),
                            'path': doc.metadata.get('relative_path', 'N/A')
                        })
            except:
                continue
        
        print(f"📊 Documenti Tact generici trovati: {len(tact_docs)}")
        for doc in tact_docs[:5]:  # Mostra primi 5
            print(f"   📄 {doc['filename']} - {doc['path']}")
        
        print(f"\n📊 Documenti clienti Tact trovati: {len(tact_clienti_docs)}")
        
        # Raggruppa per cliente
        clienti_tact = {}
        for doc in tact_clienti_docs:
            cliente = doc['cliente']
            if cliente not in clienti_tact:
                clienti_tact[cliente] = []
            clienti_tact[cliente].append(doc['filename'])
        
        for cliente, files in clienti_tact.items():
            print(f"   🏢 {cliente}: {len(files)} documenti")
        
        if len(tact_clienti_docs) == 0:
            print("⚠️  Nessun documento cliente Tact trovato nell'indice!")
            print("   Potrebbe essere necessario rifare l'ingestion")
            
    except Exception as e:
        print(f"❌ Errore durante controllo indice: {e}")

if __name__ == "__main__":
    check_tact_filesystem()
    check_tact_in_index()