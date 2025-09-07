# Progetti WebTimeAgency

Questo repository contiene una collezione di progetti sviluppati per diverse esigenze di automazione, analisi dati e servizi web.

## 📋 Panoramica

Il repository include tre progetti principali:

1. **LineeeBus** - Sistema di ricerca percorsi per trasporto pubblico
2. **Mistral RAG MVP** - Sistema di Retrieval Augmented Generation con Mistral AI
3. **MonitoraSiti-Up** - Sistema di monitoraggio uptime per siti web

## 🚀 Progetti

### 🚌 LineeeBus - Sistema Ricerca Percorsi Autobus

Un sistema completo per la pianificazione di percorsi di autobus che analizza orari Excel e fornisce raccomandazioni ottimali per i percorsi tra fermate.

**Caratteristiche principali:**
- Parser Excel per orari autobus (11 linee, 116 fermate, 1039 orari)
- Database relazionale SQLite con 5 tabelle
- Algoritmi di ricerca percorsi (diretti e con cambio)
- Ricerca fuzzy per nomi fermate
- Performance <100ms per ricerche dirette

**Tecnologie:** Python 3, SQLAlchemy 2.0, SQLite, xlrd

**Stato:** Parser dati ✅ | Database ✅ | Algoritmi ✅ | API 📋 | UI 📋

[Documentazione dettagliata](./lineebus/DOCUMENTAZIONE_SVILUPPO.md)

### 🤖 Mistral RAG MVP - Sistema RAG con AI

Sistema di Retrieval Augmented Generation che combina embeddings locali di documenti con l'API di Mistral AI per fornire risposte contestualizzate.

**Caratteristiche principali:**
- Ingestione documenti con chunking intelligente
- Ricerca vettoriale con FAISS
- Supporto multi-modello Mistral (tiny/small/medium)
- Tracking token e stima costi
- CLI interattiva per chat con knowledge base

**Tecnologie:** Python 3, LangChain, FAISS, HuggingFace, Mistral AI API

**Stato:** RAG base ✅ | Ingestione ✅ | Multi-modello ✅ | API 📋 | Web UI 📋

[Documentazione progetto](./mistral_rag_mvp/PROGETTO_MVP.md)

### 📊 MonitoraSiti-Up - Monitor Uptime Siti Web

Sistema di monitoraggio parallelo per siti web che verifica codici di stato HTTP e genera dashboard HTML responsive con statistiche in tempo reale.

**Caratteristiche principali:**
- Monitoraggio parallelo fino a 12 siti simultanei
- Dashboard HTML responsive con Bootstrap
- Indicatori performance color-coded
- Statistiche uptime e tempi di risposta
- Log rotation automatica
- Attualmente monitora 35+ siti in produzione

**Tecnologie:** Bash, curl, Bootstrap, cron

**Stato:** ✅ PRODUCTION READY

[Documentazione](./monitorasiti-up/README.md)

## 🛠️ Installazione e Utilizzo

### Requisiti Generali
- Python 3.8+ (per LineeeBus e Mistral RAG)
- Bash 4.0+ (per MonitoraSiti-Up)
- Git per clonare il repository

### Setup Rapido

```bash
# Clona il repository
git clone https://github.com/tuousername/progetti_webtimeagency.git
cd progetti_webtimeagency

# Per LineeeBus
cd lineebus
pip install -r requirements.txt
python test_route_complete.py

# Per Mistral RAG MVP
cd mistral_rag_mvp
pip install -r requirements.txt
cp .env.example .env  # Configura la tua API key Mistral
python simple_rag.py

# Per MonitoraSiti-Up
cd monitorasiti-up
chmod +x monitor-improved.sh
./monitor-improved.sh
```

### Configurazione Dettagliata

Ogni progetto ha la propria documentazione specifica nella rispettiva cartella. Consultare:
- `lineebus/DOCUMENTAZIONE_SVILUPPO.md` per LineeeBus
- `mistral_rag_mvp/README.md` per il sistema RAG
- `monitorasiti-up/README.md` per il monitor uptime

## 📁 Struttura Repository

```
progetti_webtimeagency/
├── README.md                 # Questo file
├── lineebus/                 # Sistema ricerca percorsi autobus
│   ├── bus_parser.py         # Parser dati Excel
│   ├── models.py             # Modelli database SQLAlchemy
│   ├── route_algorithms.py   # Algoritmi ricerca percorsi
│   └── orari_autobus.db      # Database SQLite
├── mistral_rag_mvp/          # Sistema RAG con Mistral AI
│   ├── simple_rag.py         # Implementazione RAG principale
│   ├── ingest.py             # Pipeline ingestione documenti
│   ├── core/                 # Componenti core del sistema
│   └── faiss_index/          # Indici vettoriali FAISS
└── monitorasiti-up/          # Monitor uptime siti web
    ├── monitor-improved.sh   # Script principale migliorato
    ├── monitorasiti          # File configurazione siti
    └── README.md             # Documentazione dettagliata
```

## 🤝 Contribuire

I contributi sono benvenuti! Per contribuire:

1. Fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Linee Guida
- Mantieni il codice pulito e ben documentato
- Aggiungi test per nuove funzionalità
- Aggiorna la documentazione quando necessario
- Segui le convenzioni di codice esistenti

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 📞 Contatti

Per domande o supporto riguardo ai progetti, aprire una issue su GitHub o contattare il team di sviluppo.

---

*Sviluppato con ❤️ da WebTimeAgency*

---

## 🤖 Mistral RAG MVP - Documentazione Specifica

# Mistral RAG MVP

Un sistema RAG (Retrieval Augmented Generation) di Aumenta Media / LaCloud da usare su proprio hosting. Elaborazione LLM via API Mistral.

## Overview

Il sistema recupera documenti rilevanti da una knowledge base e utilizza i modelli Mistral per generare risposte basate sulle informazioni recuperate. Supporta due modalità di elaborazione documenti:

- **Modalità Standard**: Caricamento diretto di PDF, TXT, MD nella cartella `/documents`
- **Modalità Avanzata**: Preprocessing di PDF con Docling per conversione in Markdown di alta qualità

## Installazione

### 1. Clona il repository e configura l'ambiente

```bash
git clone <repository-url>
cd mistral_rag_mvp
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 2. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 3. Configurazione

```bash
# Copia il file di configurazione di esempio
cp .env.example .env

# Modifica .env e aggiungi la tua MISTRAL_API_KEY
nano .env
```

Il file `.env` deve contenere:
```
MISTRAL_API_KEY=your_api_key_here
```

## Struttura del Progetto

```
mistral_rag_mvp/
├── raw_pdfs/           # PDF da preprocessare con Docling
├── documents/          # Documenti pronti per l'ingesting
├── faiss_index/        # Indice vettoriale FAISS
├── config.py           # Configurazione centralizzata
├── preprocess.py       # Preprocessing PDF → Markdown
├── ingest.py           # Ingesting documenti nel vector store
├── full_pipeline.py    # Pipeline completo
├── simple_rag.py       # Interfaccia RAG semplice
├── chatbot.py          # Chatbot interattivo
├── api.py              # Server API REST
└── core/               # Moduli core
    └── vector_store.py
```

## Utilizzo

### Modalità 1: Workflow Standard

Per documenti già pronti (PDF, TXT, MD):

```bash
# 1. Copia i documenti nella cartella documents/
cp your_documents/* documents/

# 2. Esegui l'ingesting
python ingest.py

# 3. Interroga il sistema
python simple_rag.py
# oppure
python chatbot.py
```

### Modalità 2: Workflow con Preprocessing Docling

Per PDF che necessitano di preprocessing avanzato:

```bash
# 1. Copia i PDF nella cartella raw_pdfs/
cp your_pdfs/* raw_pdfs/

# 2. Esegui il preprocessing (PDF → Markdown)
python preprocess.py

# 3. Esegui l'ingesting (Markdown → Vector Store)
python ingest.py

# 4. Interroga il sistema
python simple_rag.py
```

### Modalità 3: Pipeline Completo

Per automatizzare tutto il processo:

```bash
# Pipeline completo: preprocessing + ingesting
python full_pipeline.py

# Solo preprocessing
python full_pipeline.py --preprocessing-only

# Solo ingesting
python full_pipeline.py --ingesting-only

# Verifica stato directory
python full_pipeline.py --status
```

## Interfacce Disponibili

### 1. Simple RAG (`simple_rag.py`)
Interfaccia semplice per query singole con tracking dei costi.

### 2. Chatbot Interattivo (`chatbot.py`)
Chatbot con cronologia conversazioni e funzionalità debug.

### 3. API REST (`api.py`)
Server FastAPI per integrazione con altre applicazioni.

```bash
# Avvia il server API
python api.py

# Endpoints disponibili:
# POST /chat - Chat con il sistema RAG
# POST /ingest - Ingest nuovi documenti
# POST /upload - Upload e ingest file
# GET /stats - Statistiche e costi
# GET /health - Health check
```

## Configurazione Avanzata

### Modelli Supportati

- **mistral-tiny**: Veloce ed economico
- **mistral-small**: Bilanciato (default)
- **mistral-medium**: Massima qualità

### Parametri Configurabili (`config.py`)

```python
# Modelli
embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
llm_model_name = "mistral-small"

# Chunking
chunk_size = 1000
chunk_overlap = 200
top_k_chunks = 5

# Docling
enable_docling_preprocessing = True
docling_clean_processed_pdfs = False
```

## Monitoraggio Costi

Il sistema include tracking automatico dei costi:

- **mistral-tiny**: $0.14/1M input, $0.42/1M output tokens
- **mistral-small**: $0.60/1M input, $1.80/1M output tokens  
- **mistral-medium**: $2.50/1M input, $7.50/1M output tokens

## Troubleshooting

### Problemi Comuni

1. **Errore API Key**: Verifica che `MISTRAL_API_KEY` sia configurata correttamente
2. **Dipendenze mancanti**: Esegui `pip install -r requirements.txt`
3. **Docling non funziona**: Verifica installazione con `pip install docling`
4. **Nessun documento trovato**: Controlla che i file siano nelle directory corrette

### Log e Debug

I log sono disponibili in formato strutturato. Per debug avanzato:

```bash
# Chatbot con debug
python chatbot.py --debug

# Verifica configurazione
python -c "from config import settings; print(settings)"
```

## Features

### Funzionalità Principali
- ✅ Elaborazione documenti PDF, TXT, MD
- ✅ Preprocessing avanzato PDF con Docling
- ✅ Vector store FAISS con embedding multilingue
- ✅ API REST per integrazione
- ✅ Tracking costi in tempo reale
- ✅ Cache multi-backend
- ✅ Validazione input e sicurezza

### Funzionalità Avanzate
- ✅ Streaming responses
- ✅ Session management
- ✅ Health checks
- ✅ Structured logging
- ✅ Rate limiting
- ✅ File upload API

## Architettura

### Flusso Dati Standard
```
Documents → Chunking → Embeddings → FAISS Vector Store
User Query → Retrieval → Context → Mistral API → Response
```

### Flusso Dati con Docling
```
Raw PDFs → Docling → Markdown → Chunking → Embeddings → FAISS Vector Store
User Query → Retrieval → Context → Mistral API → Response
```

## Sviluppo

### Comandi Utili

```bash
# Test installazione
python -c "import docling; print('Docling OK')"

# Verifica configurazione
python -c "from config import settings; print(f'Docling enabled: {settings.enable_docling_preprocessing}')"

# Controllo stato
python full_pipeline.py --status
```

### Estensioni Future

- Supporto per più vector store (Pinecone, Weaviate)
- Interfaccia web
- Batch processing
- Monitoraggio avanzato
- Multi-tenancy

## Supporto

Per problemi o feature request, consulta la documentazione o contatta il team di sviluppo.

---

**Sviluppato da**: Aumenta Media / LaCloud  
**Versione**: MVP 1.0  
**Licenza**: [Specifica la licenza]
