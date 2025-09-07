# RAG-locale

Sistema RAG (Retrieval Augmented Generation) completamente locale con **Hybrid Search** avanzato per question-answering su documenti aziendali da vault Obsidian.

## ✨ Caratteristiche Principali

- 🔍 **Hybrid Search**: Combina ricerca semantica (FAISS) + keyword search (BM25)
- 👥 **Client-Aware**: Riconosce automaticamente i nomi dei clienti e prioritizza i documenti corretti
- 📁 **File-Type Boost**: Ottimizzato per trovare file specifici (concorrenti.md, corpus.md, dati.md)
- 📅 **Date-Aware**: Rileva query con date e prioritizza automaticamente le attività del Journal (oggi, ieri, DD/MM/YYYY)
- 📄 **Source Attribution**: Mostra sempre da quali file proviene ogni risposta con **link cliccabili**
- ⚡ **Script Eseguibili**: Tutti gli script principali hanno shebang e sono direttamente eseguibili
- 🎯 **K Dinamico**: Adatta automaticamente il numero di documenti (k=3-25) in base al tipo di query
- 📋 **Copy-Friendly**: Output senza bordi laterali per facile copia del testo
- 🔒 **100% Locale**: Nessuna API key richiesta, tutto funziona offline

## 🚀 Quick Start

```bash
# 1. Setup ambiente
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Indicizza vault Obsidian (RICHIESTO!)
./obsidian_ingest.py

# 3. Usa il sistema (SCRIPT ESEGUIBILI!)
./simple_rag.py

# Query esempi ottimizzate:
# File search (trova 14+ clienti con k=25):
"Per quali clienti ho scritto un file corpus?"

# Query specifiche clienti:
"Quali sono i concorrenti di Didonè Comacchio?"

# Query date e Journal:
"Cosa ho fatto oggi?"
"Attività del 24/07/2025"

# Apertura file dalle fonti:
# Dopo la risposta, digita 1-3 per aprire il file nel pager
```

## 📋 Requisiti

- Python 3.8+
- 8GB+ RAM  
- Vault Obsidian in `/opt/obsidian/appunti/`
- Modello LLM locale (Gemma 3-4B via llamafile)

## 🛠️ Componenti Principali

### Entry Points (tutti eseguibili con ./script.py)
- `simple_rag.py` - **PRINCIPALE**: CLI ottimizzata con k dinamico, source attribution e link cliccabili
- `chatbot.py` - Chatbot interattivo con source display
- `api.py` - REST API server (FastAPI)
- `debug_rag_flow.py` - Tool di debug per analisi hybrid search

### Pipeline Documenti  
- `obsidian_ingest.py` - **PRINCIPALE**: Indicizza vault Obsidian con metadata
- `hybrid_retriever.py` - **CORE**: Motore hybrid search con intelligent boosting e date detection
- `ingest.py` - (Legacy) Indicizzazione documenti standard
- `preprocess.py` - (Opzionale) Conversione PDF→Markdown con Docling

### Configurazione
- `config.py` - Configurazioni centralizzate
- `llm_adapter.py` - Integrazione LLM locale (Gemma 3-4B)

## 📚 Utilizzo

### Indicizzazione Documenti

```bash
# PRINCIPALE: Obsidian vault con hybrid search
python obsidian_ingest.py
# Output: obsidian_index/ (~6700 chunks da ~1100 documenti)

# Legacy: documenti standard
python ingest.py
```

### Query Sistema

```bash
# CLI ottimizzata con k dinamico
python simple_rag.py
> Per quali clienti ho scritto un file corpus?
# Output: Lista 14+ clienti + Fonti consultate con numerazione
# Digita 1-14 per aprire file nel pager (rich→less→more→cat)

# Chatbot interattivo
python chatbot.py

# Debug hybrid search con analisi dettagliata
python debug_rag_flow.py "Per quali clienti ho scritto un file corpus?"
# Mostra: semantic scores, BM25 scores, boost factors, k dinamico

# API REST
python api.py
```

## 🎯 Esempi di Query Ottimizzate

### 📁 Query File Search (k=25, deduplicazione intelligente)
```bash
"Per quali clienti ho scritto un file corpus?"
→ Trova: 14 clienti unici con corpus.md (vs 3 precedenti)
→ Fonti: [1] Progeo/corpus.md, [2] Maspe/clipwall/corpus.md, etc.
→ Link: Digita 1-14 per aprire file

"Quali clienti hanno un file concorrenti?"
→ K dinamico 25, trova tutti i clienti con concorrenti.md
```

### 👥 Query Clienti Specifici (k=3)
```bash
"Quali sono i concorrenti di Didonè Comacchio?"
→ Trova: Didonè Comacchio/concorrenti.md + corpus.md
→ Link: [1] Clienti/Didonè Comacchio/concorrenti.md

"Account e credenziali Maffeis"
→ Trova: Maffeis/dati.md con boost file-type
```

### 📅 Query Date e Journal (k=20 per Journal)
```bash
"Cosa ho fatto oggi?"
→ Trova: Journal/14-08-2025.md con tutti i chunk del giorno
→ Link: [1] Journal/14-08-2025.md

"Attività del 23/07/2025"
→ Rileva data DD/MM/YYYY, priorità Journal

"Cosa ho fatto ieri?"
→ Calcolo automatico data-1, trova Journal corrispondente
```

### 📋 Query Liste (k=10)
```bash
"Elenco tutti i clienti"
"Lista attività di oggi"
→ K automatico 10 per query di tipo lista
```

## 🔧 Configurazione

Modifica `config.py` per personalizzare:

- **LLM**: `llamafile_max_tokens: 2048` (aumentato per risposte complete)
- **Embeddings**: `embedding_model_name` (multilingue di default)
- **K Dinamico**: File search=25, Liste=10, Default=3
- **GPU**: Disabilitata per stabilità (`--gpu disable`)
- **Performance**: `cache_ttl_seconds`, `llamafile_timeout`

## 📊 Architettura

Sistema ibrido ottimizzato:
- **Retrieval**: FAISS (semantico) + BM25 (keyword) con boost intelligenti
- **LLM**: Gemma 3 4B via llamafile CLI (completamente locale, GPU disabled)
- **Storage**: Indice FAISS con 6947+ chunks da ~1100 documenti Obsidian
- **K Dinamico**: Pattern matching per adattare automaticamente il retrieval
- **Deduplicazione**: Clienti unici per query di ricerca file (max 15)

Per dettagli tecnici completi vedere [ARCHITECTURE.md](ARCHITECTURE.md).

## ✅ Miglioramenti Implementati

1. ✅ **Performance Ottimizzata**: Token limit 2048, k dinamico, GPU disabled per stabilità
2. ✅ **Retrieval Accurato**: Trova 14+ clienti corpus vs 3 precedenti, boost intelligenti
3. ✅ **UI Migliorata**: Output copy-friendly, link cliccabili per file, box completi
4. ✅ **System Stability**: Nessun crash GPU, gestione context overflow

## 🚨 Limitazioni Rimanenti

- **Tempo risposta**: ~30-60s per query complesse (modello locale Gemma 3-4B)
- **Path accuracy**: Dipende dalla struttura Obsidian vault

## 📁 Struttura Progetto

```
RAG-locale/
├── simple_rag.py         # 🎯 ENTRY POINT principale - CLI ottimizzata
├── obsidian_ingest.py    # 📚 INGEST principale - Obsidian vault
├── hybrid_retriever.py   # 🔍 CORE - Hybrid search + k dinamico
├── config.py            # ⚙️  Configurazione (token: 2048, GPU: disabled)
├── llm_adapter.py       # 🤖 LLM integration (Gemma 3-4B)
├── scripts/            # 🛠️  Script wrapper per produzione
│   ├── rag-query       # Wrapper per simple_rag.py
│   └── rag-ingest      # Wrapper per obsidian_ingest.py
├── utils/             # 🔧 Utility (cache, logger, security)
├── obsidian_index/    # 💾 Indice FAISS (6947+ chunks)
└── docs/             # 📄 Documentazione
```

## 🐛 Troubleshooting

```bash
# Se retrieval sembra scorretto
./debug_rag_flow.py "tua query"  # Analizza k dinamico e boost

# Se file non si aprono dalle fonti
ls -la "/opt/obsidian/appunti/Clienti/[Cliente]/"  # Verifica path

# Ricostruire indice dopo modifiche vault
./obsidian_ingest.py  # Crea backup automatico del vecchio

# Sistema si blocca su query complesse
# K ottimizzato automaticamente (25→15 clienti max per context)

# Performance lenta
# GPU già disabilitata per stabilità, usa llamafile CLI diretto
```

## 📄 Licenza

MIT License - vedi LICENSE per dettagli.