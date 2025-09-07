#!/usr/bin/env python3
"""
Dataset di test per valutazione del sistema di retrieval
Include query reali e documenti rilevanti attesi (ground truth)
"""

# Dataset di test strutturato: query -> documenti rilevanti attesi
EVALUATION_DATASET = [
    {
        "query": "Quali sono i concorrenti di Didonè Comacchio?",
        "expected_files": [
            "Didonè Comacchio/concorrenti.md"
        ],
        "client": "Didonè Comacchio",
        "file_type": "concorrenti",
        "difficulty": "easy"  # Query specifica, file dedicato
    },
    {
        "query": "Che tipo di azienda è FIS Group?",
        "expected_files": [
            "Fis/corpus.md"
        ],
        "client": "Fis",
        "file_type": "corpus",
        "difficulty": "easy"
    },
    {
        "query": "Informazioni generali su Maffeis Engineering",
        "expected_files": [
            "Maffeis Engineering/corpus.md"
        ],
        "client": "Maffeis Engineering", 
        "file_type": "corpus",
        "difficulty": "easy"
    },
    {
        "query": "Dati di accesso per Progeo",
        "expected_files": [
            "Progeo/dati.md"
        ],
        "client": "Progeo",
        "file_type": "dati",
        "difficulty": "easy"
    },
    {
        "query": "Quali sono i competitor di Maspe?",
        "expected_files": [
            "Maspe/concorrenti.md"
        ],
        "client": "Maspe",
        "file_type": "concorrenti", 
        "difficulty": "medium"  # Query più generica
    },
    {
        "query": "Account e credenziali di Seit",
        "expected_files": [
            "Seit/dati.md"
        ],
        "client": "Seit",
        "file_type": "dati",
        "difficulty": "medium"
    },
    {
        "query": "Come funziona l'azienda ASAS?",
        "expected_files": [
            "ASAS/corpus.md"
        ],
        "client": "ASAS",
        "file_type": "corpus",
        "difficulty": "medium"
    },
    {
        "query": "Dettagli su Change Italia",
        "expected_files": [
            "Change Italia/corpus.md"
        ],
        "client": "Change Italia",
        "file_type": "corpus",
        "difficulty": "medium"
    },
    {
        "query": "Concorrenti",  # Query molto generica
        "expected_files": [
            "Didonè Comacchio/concorrenti.md",
            "Maspe/concorrenti.md",
            "Maffeis Engineering/concorrenti.md"
        ],
        "client": None,
        "file_type": "concorrenti",
        "difficulty": "hard"
    },
    {
        "query": "Informazioni sui dati aziendali",  # Query ambigua
        "expected_files": [
            "Progeo/dati.md",
            "Seit/dati.md", 
            "Maffeis Engineering/dati.md"
        ],
        "client": None,
        "file_type": "dati",
        "difficulty": "hard"
    },
    {
        "query": "Chi è Francesca Endrizzi?",  # Query che richiede ricerca nel contenuto
        "expected_files": [
            "Didonè Comacchio/concorrenti.md"
        ],
        "client": "Didonè Comacchio",
        "file_type": "concorrenti",
        "difficulty": "hard"
    },
    {
        "query": "MTMA Architetti dove si trova?",
        "expected_files": [
            "Didonè Comacchio/concorrenti.md"
        ],
        "client": "Didonè Comacchio",
        "file_type": "concorrenti", 
        "difficulty": "hard"
    },
    {
        "query": "Casa nf firmato da didonè",  # Query basata su contenuto specifico
        "expected_files": [
            "Didonè Comacchio/analisi preliminare.md"
        ],
        "client": "Didonè Comacchio",
        "file_type": "analisi", 
        "difficulty": "hard"
    },
    {
        "query": "Proposte commerciali FIS",
        "expected_files": [
            "Fis/proposta.md"
        ],
        "client": "Fis",
        "file_type": "proposta",
        "difficulty": "medium"
    },
    {
        "query": "Quanto costa la proposta per FIS Group?", 
        "expected_files": [
            "Fis/proposta.md"
        ],
        "client": "Fis", 
        "file_type": "proposta",
        "difficulty": "medium"
    }
]

def get_dataset_by_difficulty(difficulty=None):
    """Filtra dataset per difficoltà"""
    if difficulty is None:
        return EVALUATION_DATASET
    return [item for item in EVALUATION_DATASET if item["difficulty"] == difficulty]

def get_dataset_by_client(client):
    """Filtra dataset per cliente"""
    return [item for item in EVALUATION_DATASET if item["client"] == client]

def get_dataset_stats():
    """Statistiche del dataset"""
    stats = {
        "total_queries": len(EVALUATION_DATASET),
        "by_difficulty": {},
        "by_client": {},
        "by_file_type": {}
    }
    
    for item in EVALUATION_DATASET:
        # Conta per difficoltà
        diff = item["difficulty"]
        stats["by_difficulty"][diff] = stats["by_difficulty"].get(diff, 0) + 1
        
        # Conta per cliente
        client = item["client"] or "Generic"
        stats["by_client"][client] = stats["by_client"].get(client, 0) + 1
        
        # Conta per tipo file
        file_type = item["file_type"]
        stats["by_file_type"][file_type] = stats["by_file_type"].get(file_type, 0) + 1
    
    return stats

if __name__ == "__main__":
    print("=== Dataset di Valutazione RAG ===")
    stats = get_dataset_stats()
    print(f"Totale query: {stats['total_queries']}")
    print(f"Per difficoltà: {stats['by_difficulty']}")
    print(f"Per cliente: {stats['by_client']}")
    print(f"Per tipo file: {stats['by_file_type']}")
    
    print("\n=== Query di esempio ===")
    for i, item in enumerate(EVALUATION_DATASET[:3]):
        print(f"{i+1}. Query: {item['query']}")
        print(f"   Expected: {item['expected_files']}")
        print(f"   Difficulty: {item['difficulty']}\n")