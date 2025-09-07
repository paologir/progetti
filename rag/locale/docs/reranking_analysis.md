# Analisi Reranking per RAG-locale

## Tecniche di Reranking Disponibili

### 1. Cross-Encoder
- **Pro**: Alta precisione, considera query e documento insieme
- **Contro**: Più lento del bi-encoder
- **Modelli consigliati**:
  - `cross-encoder/ms-marco-MiniLM-L-6-v2` (veloce, multilingue)
  - `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (ottimizzato per italiano)

### 2. ColBERT v2
- **Pro**: Bilancia velocità e precisione
- **Contro**: Richiede indicizzazione speciale
- **Modelli**: `colbert-ir/colbertv2.0`

### 3. MonoT5
- **Pro**: Basato su T5, molto accurato
- **Contro**: Più pesante computazionalmente
- **Modelli**: `castorini/monot5-base-msmarco`

### 4. BGE-Reranker
- **Pro**: Ottimizzato per multilingue
- **Contro**: Modello più grande
- **Modelli**: `BAAI/bge-reranker-large`

## Implementazione Proposta

### Fase 1: Cross-Encoder Semplice
```python
from sentence_transformers import CrossEncoder

class RerankerPipeline:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.reranker = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: List[Document], top_k: int = 5):
        # Prepara coppie query-documento
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Calcola scores
        scores = self.reranker.predict(pairs)
        
        # Riordina per score
        sorted_indices = np.argsort(scores)[::-1][:top_k]
        
        return [documents[i] for i in sorted_indices]
```

### Fase 2: Pipeline Integrata
```
Query → Hybrid Retrieval (top-20) → Reranking (top-5) → LLM
```

### Benefici Attesi
- **MRR**: +15-25% di miglioramento atteso
- **Precision@1**: +20-30% per query difficili
- **Latenza**: +200-500ms (accettabile)

### Metriche di Valutazione
- Confronto MRR pre/post reranking
- Precision@k con k={1,3,5}
- Latenza aggiuntiva
- Trade-off precisione/velocità