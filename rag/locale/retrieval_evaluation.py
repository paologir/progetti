#!/usr/bin/env python3
"""
Sistema di valutazione del retrieval con metriche standard:
- Mean Reciprocal Rank (MRR)
- Recall@k
- Precision@k 
- Mean Average Precision (MAP)
"""

import json
from typing import List, Dict, Tuple, Any
from hybrid_retriever import HybridRetriever
from evaluation_dataset import EVALUATION_DATASET, get_dataset_stats

class RetrievalEvaluator:
    def __init__(self, index_path="obsidian_index"):
        self.hybrid_retriever = HybridRetriever(faiss_index_path=index_path)
        self.hybrid_retriever.load_index()
        print(f"✅ Evaluator inizializzato con {self.hybrid_retriever.vector_store.index.ntotal} documenti")
    
    def extract_file_path(self, doc) -> str:
        """Estrae il path relativo cliente/file dai metadati"""
        metadata = getattr(doc, 'metadata', {})
        cliente = metadata.get('cliente', 'unknown')
        filename = metadata.get('filename', 'unknown')
        return f"{cliente}/{filename}"
    
    def retrieve_documents(self, query: str, k: int = 10) -> List[str]:
        """Recupera documenti e restituisce lista di file paths"""
        docs = self.hybrid_retriever.search(query, k=k)
        return [self.extract_file_path(doc) for doc in docs]
    
    def calculate_precision_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calcola Precision@k"""
        if k == 0:
            return 0.0
        
        retrieved_at_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_at_k) & set(relevant))
        return relevant_retrieved / k
    
    def calculate_recall_at_k(self, retrieved: List[str], relevant: List[str], k: int) -> float:
        """Calcola Recall@k"""
        if len(relevant) == 0:
            return 0.0
        
        retrieved_at_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_at_k) & set(relevant))
        return relevant_retrieved / len(relevant)
    
    def calculate_reciprocal_rank(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calcola Reciprocal Rank per una singola query"""
        for i, doc in enumerate(retrieved):
            if doc in relevant:
                return 1.0 / (i + 1)
        return 0.0
    
    def calculate_average_precision(self, retrieved: List[str], relevant: List[str]) -> float:
        """Calcola Average Precision per una singola query"""
        if len(relevant) == 0:
            return 0.0
        
        score = 0.0
        num_hits = 0.0
        
        for i, doc in enumerate(retrieved):
            if doc in relevant:
                num_hits += 1.0
                precision_at_i = num_hits / (i + 1.0)
                score += precision_at_i
        
        return score / len(relevant)
    
    def evaluate_single_query(self, query_data: Dict, k_values: List[int] = [1, 3, 5, 10]) -> Dict[str, Any]:
        """Valuta una singola query"""
        query = query_data["query"]
        expected_files = query_data["expected_files"]
        
        # Recupera documenti
        retrieved_files = self.retrieve_documents(query, k=max(k_values))
        
        # Calcola metriche
        results = {
            "query": query,
            "expected_files": expected_files,
            "retrieved_files": retrieved_files[:10],  # Mostra solo top 10
            "reciprocal_rank": self.calculate_reciprocal_rank(retrieved_files, expected_files),
            "average_precision": self.calculate_average_precision(retrieved_files, expected_files),
            "precision_at_k": {},
            "recall_at_k": {}
        }
        
        # Calcola precision e recall per diversi k
        for k in k_values:
            results["precision_at_k"][k] = self.calculate_precision_at_k(retrieved_files, expected_files, k)
            results["recall_at_k"][k] = self.calculate_recall_at_k(retrieved_files, expected_files, k)
        
        return results
    
    def evaluate_dataset(self, dataset: List[Dict] = None, k_values: List[int] = [1, 3, 5, 10]) -> Dict[str, Any]:
        """Valuta l'intero dataset"""
        if dataset is None:
            dataset = EVALUATION_DATASET
        
        print(f"🔍 Valutazione su {len(dataset)} query...")
        
        all_results = []
        
        # Accumula metriche
        total_rr = 0.0
        total_ap = 0.0
        total_precision_at_k = {k: 0.0 for k in k_values}
        total_recall_at_k = {k: 0.0 for k in k_values}
        
        for i, query_data in enumerate(dataset):
            print(f"  Query {i+1}/{len(dataset)}: {query_data['query'][:50]}...")
            
            result = self.evaluate_single_query(query_data, k_values)
            all_results.append(result)
            
            # Accumula per medie
            total_rr += result["reciprocal_rank"]
            total_ap += result["average_precision"]
            
            for k in k_values:
                total_precision_at_k[k] += result["precision_at_k"][k]
                total_recall_at_k[k] += result["recall_at_k"][k]
        
        # Calcola medie
        n_queries = len(dataset)
        summary = {
            "total_queries": n_queries,
            "mean_reciprocal_rank": total_rr / n_queries,
            "mean_average_precision": total_ap / n_queries,
            "mean_precision_at_k": {k: total_precision_at_k[k] / n_queries for k in k_values},
            "mean_recall_at_k": {k: total_recall_at_k[k] / n_queries for k in k_values},
            "detailed_results": all_results
        }
        
        return summary
    
    def print_evaluation_report(self, results: Dict[str, Any]):
        """Stampa report di valutazione leggibile"""
        print("\n" + "="*60)
        print("🏆 REPORT DI VALUTAZIONE RETRIEVAL")
        print("="*60)
        
        print(f"📊 Statistiche generali:")
        print(f"   • Totale query valutate: {results['total_queries']}")
        print(f"   • Mean Reciprocal Rank (MRR): {results['mean_reciprocal_rank']:.3f}")
        print(f"   • Mean Average Precision (MAP): {results['mean_average_precision']:.3f}")
        
        print(f"\n📈 Precision@k (media):")
        for k, precision in results['mean_precision_at_k'].items():
            print(f"   • P@{k}: {precision:.3f}")
        
        print(f"\n📉 Recall@k (media):")
        for k, recall in results['mean_recall_at_k'].items():
            print(f"   • R@{k}: {recall:.3f}")
        
        # Analisi per difficoltà
        difficulty_analysis = self.analyze_by_difficulty(results['detailed_results'])
        print(f"\n🎯 Analisi per difficoltà:")
        for difficulty, metrics in difficulty_analysis.items():
            print(f"   • {difficulty.capitalize()}: MRR={metrics['mrr']:.3f}, MAP={metrics['map']:.3f}, P@3={metrics['p3']:.3f}")
        
        # Top errori
        print(f"\n❌ Query con performance peggiori (RR=0):")
        failures = [r for r in results['detailed_results'] if r['reciprocal_rank'] == 0.0]
        for i, failure in enumerate(failures[:3]):
            print(f"   {i+1}. \"{failure['query']}\"")
            print(f"      Expected: {failure['expected_files']}")
            print(f"      Got: {failure['retrieved_files'][:3]}")
    
    def analyze_by_difficulty(self, detailed_results: List[Dict]) -> Dict[str, Dict]:
        """Analizza risultati per livello di difficoltà"""
        # Mappa query a difficoltà
        query_to_difficulty = {item["query"]: item["difficulty"] for item in EVALUATION_DATASET}
        
        difficulty_groups = {"easy": [], "medium": [], "hard": []}
        
        for result in detailed_results:
            difficulty = query_to_difficulty.get(result["query"], "unknown")
            if difficulty in difficulty_groups:
                difficulty_groups[difficulty].append(result)
        
        analysis = {}
        for difficulty, results in difficulty_groups.items():
            if results:
                analysis[difficulty] = {
                    "count": len(results),
                    "mrr": sum(r["reciprocal_rank"] for r in results) / len(results),
                    "map": sum(r["average_precision"] for r in results) / len(results),
                    "p3": sum(r["precision_at_k"][3] for r in results) / len(results)
                }
        
        return analysis
    
    def save_results(self, results: Dict[str, Any], filename: str = "evaluation_results.json"):
        """Salva risultati in JSON per analisi future"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Risultati salvati in {filename}")

def main():
    print("🚀 Avvio valutazione sistema di retrieval...")
    
    # Mostra statistiche dataset
    stats = get_dataset_stats()
    print(f"📋 Dataset: {stats['total_queries']} query")
    print(f"   Difficoltà: {stats['by_difficulty']}")
    
    # Inizializza evaluator
    evaluator = RetrievalEvaluator()
    
    # Esegui valutazione
    results = evaluator.evaluate_dataset()
    
    # Mostra report
    evaluator.print_evaluation_report(results)
    
    # Salva risultati
    evaluator.save_results(results)

if __name__ == "__main__":
    main()