# Architettura del Sistema RAG Locale

## Panoramica

Il sistema RAG (Retrieval Augmented Generation) locale è progettato per fornire un'interfaccia di question-answering basata su documenti aziendali, operando completamente offline senza dipendenze da API esterne.

## Stack Tecnologico

### Modelli e Inferenza
- **LLM**: Gemma3-4B (quantizzato Q6_K) servito via llamafile - ~50x più veloce di Granite 8B
- **Embeddings**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384 dimensioni)
- **Server**: llamafile HTTP API su localhost:8080

### Storage e Retrieval
- **Vector Store**: FAISS (Facebook AI Similarity Search) 
- **Indice**: 3731 chunks totali da documenti aziendali e Obsidian vault
- **Retrieval**: Sistema ibrido che combina:
  - Ricerca semantica (FAISS - 60% peso)
  - Ricerca keyword (BM25 - 40% peso)
  - Boosting intelligente per documenti recenti e client specifici

### Framework e Librerie
- **LangChain**: Per orchestrazione RAG e chunking documenti
- **FastAPI**: REST API server
- **Pydantic**: Configurazione e validazione
- **HuggingFace Transformers**: Per embeddings multilingue

## Architettura dei Componenti

```
┌─────────────────────┐     ┌─────────────────────┐
│   Entry Points      │     │   Document Sources  │
├─────────────────────┤     ├─────────────────────┤
│ • simple_rag.py     │     │ • /documents        │
│ • chatbot_v2.py     │     │ • /raw_pdfs         │
│ • api.py (FastAPI)  │     │ • Obsidian vault    │
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   LLM Adapter       │     │   Ingestion Pipeline│
├─────────────────────┤     ├─────────────────────┤
│ • LlamafileClient   │     │ • preprocess.py     │
│ • HTTP API calls    │     │ • ingest_v2.py      │
│ • Response parsing  │     │ • obsidian_ingest.py│
└──────────┬──────────┘     └──────────┬──────────┘
           │                           │
           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Llamafile Server   │     │   Vector Store      │
├─────────────────────┤     ├─────────────────────┤
│ • Gemma 3 4B        │     │ • FAISS index       │
│ • CLI mode          │     │ • 6900+ chunks      │
│ • 120s timeout      │     │ • In-memory         │
└─────────────────────┘     └─────────────────────┘
           │                           │
           └───────────┬───────────────┘
                       ▼
             ┌─────────────────────┐
             │  Hybrid Retriever   │
             ├─────────────────────┤
             │ • Semantic (FAISS)  │
             │ • Keyword (BM25)    │
             │ • Score fusion      │
             │ • Metadata boost    │
             └─────────────────────┘
```

## Flusso di Elaborazione

### 1. Ingestion dei Documenti
1. **Preprocessing** (opzionale): Conversione PDF→Markdown con Docling
2. **Loading**: Caricamento documenti (PDF, TXT, MD, DOCX, etc.)
3. **Chunking**: Divisione in chunks di 1500 caratteri con 300 di overlap
4. **Embedding**: Generazione vettori con modello multilingue
5. **Indexing**: Memorizzazione in FAISS con metadati

### 2. Query Processing
1. **Input**: Query utente in linguaggio naturale
2. **Retrieval**: 
   - Embedding della query
   - Ricerca semantica FAISS (top-k)
   - Ricerca BM25 per keyword matching
   - Fusione scores con pesi configurabili
3. **Context Building**: Selezione top-5 chunks più rilevanti
4. **Generation**: Prompt engineering + chiamata LLM locale
5. **Response**: Risposta formattata con metriche di performance

## Configurazione Attuale

### Modelli
- **LLM**: `/opt/llm/granite-3.2-8b-instruct.Q4_K_M.gguf`
- **Context**: 2048 token
- **Temperature**: 0.1 (output deterministico)
- **Max tokens**: 2048

### Retrieval
- **Chunk size**: 1500 caratteri
- **Overlap**: 300 caratteri  
- **Top-k**: 5 chunks
- **Pesi**: 60% semantic, 40% keyword

### Performance
- **Timeout LLM**: 120 secondi
- **Cache TTL**: 3600 secondi
- **Max file size**: 50 MB

## Problemi Identificati

### 1. Performance LLM
- **Lentezza**: ~5-10 secondi per risposta con Gemma 3 4B (migliorato dal precedente Granite 8B che impiegava 30-60s)
- **Timeout frequenti**: 120s spesso insufficienti per query complesse
- **Single-threaded**: Nessun batching o parallelizzazione

### 2. Qualità Retrieval
- **Falsi positivi**: Chunks non pertinenti nei risultati
- **Chunking rigido**: Divisione per caratteri rompe il contesto semantico
- **Scarsa precisione**: Difficoltà con query specifiche su documenti brevi

### 3. Scalabilità
- **Memoria**: Intero indice FAISS caricato in RAM
- **No persistenza**: Indice ricreato ad ogni avvio
- **Limiti dimensionali**: Performance degrada con molti documenti

### 4. Architettura
- **Codice legacy**: Riferimenti residui a Mistral API
- **Duplicazioni**: Versioni multiple degli stessi componenti (v1, v2)
- **Configurazione complessa**: Troppi entry point e opzioni

## Proposte di Miglioramento

### A. Ottimizzazione Modelli
1. **LLM più veloce**: 
   - Phi-3 mini (3.8B)
   - Qwen 2.5 (1.5B-7B)
   - Gemma 2 (2B)
2. **Quantizzazione aggressiva**: Q3_K_S o Q2_K
3. **Inference ottimizzata**: vLLM, TGI, o llama.cpp con GPU

### B. Retrieval Avanzato
1. **Re-ranker neurale**: Cross-encoder per filtrare risultati
2. **Chunking semantico**: Basato su paragrafi/sezioni
3. **Query expansion**: Riformulazione automatica query
4. **Metadata filtering**: Pre-filtro su client/date/tipo

### C. Architettura Pulita
1. **Single entry point**: Un'unica interfaccia principale
2. **Rimozione legacy**: Eliminare dipendenze Mistral
3. **Modularizzazione**: Separazione netta componenti
4. **API standardizzata**: OpenAI-compatible per interoperabilità

### D. Performance e Scale
1. **GPU acceleration**: Supporto CUDA/ROCm per LLM
2. **Distributed FAISS**: Sharding per grandi indici
3. **Async processing**: Queue per richieste multiple
4. **Caching intelligente**: Cache semantica delle risposte

## Metriche di Valutazione

### Performance Attuali (Post-Gemma3)
- **Latenza media**: 1-5 secondi/query (miglioramento 50x)
- **Throughput**: 10-20 query/minuto
- **Precisione retrieval**: ~60% (stima)
- **Utilizzo RAM**: 2-4 GB con indice caricato

### Target Miglioramento
- **Latenza target**: <5 secondi/query
- **Throughput target**: 10+ query/minuto
- **Precisione target**: >85%
- **Efficienza RAM**: <1 GB base + scaling lineare

## Ottimizzazioni Completate (Luglio 2025)

### ✅ Switch a Gemma3-4B
- **Performance**: 50x miglioramento latenza (da 30-60s a <1s)
- **Stabilità**: Eliminati timeout frequenti
- **Configurazione**: Parametri minimali (--server --nobrowser --port 8080)
- **RAM**: Ridotto footprint da 6-8GB a 3-4GB

**Lesson learned**: Gemma3 funziona meglio con parametri default, evitare override di -c, -t, -temp.

## Prossimi Passi

1. ✅ ~~Benchmark modelli più veloci~~ → **Completato con Gemma3-4B**
2. **Ottimizzazione retrieval**: Implementare re-ranking per precisione
3. **Fine-tuning parametri**: Ottimizzare chunk_size e top_k per Gemma3
4. **Test utente**: Validare miglioramenti con casi reali
5. **Monitoring**: Implementare metriche di qualità automatiche