#!/usr/bin/env python3

"""
Script per ottimizzare i parametri di retrieval per Gemma 3-4B
"""

import os
from hybrid_retriever import HybridRetriever
from config import settings

def test_retrieval_parameters():
    """Testa diversi parametri per ottimizzare il retrieval"""
    
    # Query di test con risposta nota
    test_cases = [
        {
            "query": "Quali sono i concorrenti di Didonè Comacchio?",
            "expected_files": ["concorrenti.md"],
            "expected_client": "Didonè Comacchio"
        },
        {
            "query": "Che tipo di azienda è FIS Group?",
            "expected_files": ["corpus.md"],
            "expected_client": "FIS Group"
        }
    ]
    
    # Parametri da testare
    alpha_values = [0.4, 0.5, 0.6, 0.7, 0.8]
    k_values = [3, 5, 7]
    
    retriever = HybridRetriever(faiss_index_path="obsidian_index")
    retriever.load_index()
    
    best_config = {"alpha": 0.6, "k": 5, "accuracy": 0.0}
    
    print("🔍 OTTIMIZZAZIONE PARAMETRI RETRIEVAL")
    print("="*60)
    
    for alpha in alpha_values:
        for k in k_values:
            print(f"\nTest: α={alpha}, k={k}")
            
            total_accuracy = 0
            for test_case in test_cases:
                query = test_case["query"]
                expected_client = test_case["expected_client"]
                expected_files = test_case["expected_files"]
                
                docs = retriever.search(query, k=k, alpha=alpha)
                
                # Verifica se il primo documento è quello giusto
                if docs:
                    first_doc = docs[0]
                    cliente = first_doc.metadata.get('cliente', '')
                    filename = first_doc.metadata.get('filename', '')
                    
                    client_match = expected_client.lower() in cliente.lower()
                    file_match = any(ef in filename for ef in expected_files)
                    
                    if client_match and file_match:
                        accuracy = 1.0
                        print(f"  ✅ {query[:30]}... -> {cliente}/{filename}")
                    else:
                        accuracy = 0.0
                        print(f"  ❌ {query[:30]}... -> {cliente}/{filename}")
                else:
                    accuracy = 0.0
                    print(f"  ❌ {query[:30]}... -> NO DOCS")
                
                total_accuracy += accuracy
            
            avg_accuracy = total_accuracy / len(test_cases)
            print(f"  📊 Accuracy: {avg_accuracy:.1%}")
            
            if avg_accuracy > best_config["accuracy"]:
                best_config = {"alpha": alpha, "k": k, "accuracy": avg_accuracy}
    
    print(f"\n🏆 MIGLIOR CONFIGURAZIONE:")
    print(f"   Alpha: {best_config['alpha']} (Semantic:{best_config['alpha']:.1f} / BM25:{1-best_config['alpha']:.1f})")
    print(f"   K: {best_config['k']} documenti")
    print(f"   Accuracy: {best_config['accuracy']:.1%}")
    
    return best_config

if __name__ == "__main__":
    test_retrieval_parameters()