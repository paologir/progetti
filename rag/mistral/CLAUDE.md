# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Mistral RAG MVP system** - a Retrieval Augmented Generation system that uses Mistral AI's API for language generation. The system ingests documents into a vector database and allows users to query the knowledge base using natural language.

## Commands

### Setup and Installation
```bash
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to add your MISTRAL_API_KEY
```

### Document Processing and Ingestion

#### PDF Preprocessing with Docling
```bash
# Convert PDFs in /raw_pdfs to Markdown files in /documents
python preprocess.py

# Full pipeline: preprocessing + ingesting
python full_pipeline.py

# Only preprocessing
python full_pipeline.py --preprocessing-only

# Only ingesting
python full_pipeline.py --ingesting-only

# Check directories status
python full_pipeline.py --status
```

#### Standard Document Ingestion
```bash
# Ingest documents from /documents folder into vector store
python ingest.py

# Advanced ingestion with custom settings
python ingest_v2.py
```

### Running the System
```bash
# Simple CLI interface
python simple_rag.py

# Advanced CLI chatbot with debug features  
python chatbot.py

# REST API server (production ready)
python api.py
```

### Development and Testing
```bash
# No specific test commands defined in this codebase
# Lint/format commands not configured - ask user if needed
```

## Code Architecture

### Core Components
1. **simple_rag.py** - Basic RAG implementation with token cost tracking
2. **ingest.py** - Document processing and vectorization pipeline
3. **chatbot.py** - Interactive CLI interface with conversation history
4. **api.py** - FastAPI REST API with endpoints for chat, ingestion, file upload

### Configuration System
- **config.py** - Centralized Pydantic configuration
- **.env** - Environment variables (API keys, model settings)
- Default embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Default LLM: `mistral-small`

### Data Flow

#### Standard Flow
```
Documents → Chunking (1000 chars, 200 overlap) → Embeddings → FAISS Vector Store
User Query → Retrieval (top 5 chunks) → Context → Mistral API → Response
```

#### Enhanced Flow with Docling Preprocessing
```
Raw PDFs → Docling → Markdown → Chunking → Embeddings → FAISS Vector Store
User Query → Retrieval (top 5 chunks) → Context → Mistral API → Response
```

### Key Modules
- **core/vector_store.py** - Abstract vector store implementations (FAISS primary, Chroma alternative)
- **utils/cache.py** - Multi-backend caching (memory, disk, Redis)
- **utils/logger.py** - Structured JSON logging
- **utils/security.py** - Input validation and sanitization

### Document Processing

#### Standard Processing
- Supported formats: PDF, TXT, MD
- Uses LangChain loaders and text splitters
- Documents placed in `/documents` folder for ingestion

#### Enhanced Processing with Docling
- Raw PDFs placed in `/raw_pdfs` folder
- **preprocess.py** - Converts PDFs to high-quality Markdown using Docling
- **full_pipeline.py** - Complete workflow: PDF preprocessing + ingesting
- Configurable via `enable_docling_preprocessing` in config.py
- Option to clean processed PDFs automatically

### API Endpoints (api.py)
- `POST /chat` - Chat with the RAG system
- `POST /ingest` - Ingest new documents
- `POST /upload` - Upload and ingest files
- `GET /stats` - System statistics and costs
- `GET /health` - Health check

## Development Notes

### Token Cost Tracking
The system includes built-in cost estimation using Mistral pricing tiers. All responses show estimated costs based on input/output tokens.

### Multiple Versions
- **MVP versions**: `simple_rag.py`, `ingest.py`, `chatbot.py` - basic functionality
- **Advanced versions**: `api.py`, `chatbot_v2.py`, `ingest_v2.py` - production features

### Vector Store Flexibility
The system supports multiple vector store backends through abstract interfaces. FAISS is the primary choice, with ChromaDB as an alternative.

### Caching Strategy
Multi-level caching system with configurable backends for performance optimization in production deployments.

## Flusso di lavoro standard
1. Per prima cosa, analizza il problema, cerca i file rilevanti nel codice e scrivi un piano per todo.md. 
2. Il piano dovrebbe contenere una lista di cose da fare che puoi spuntare man mano che le completi.
3. Prima di iniziare a lavorare, contattami e verificherò il piano.
4. Quindi, inizia a lavorare sulle cose da fare, contrassegnandole come completate man mano che procedi.
5. Per favore, per ogni passaggio, forniscimi una spiegazione dettagliata delle modifiche apportate.
6. Semplifica il più possibile ogni attività e modifica al codice. Vogliamo evitare modifiche massicce o complesse. Ogni modifica dovrebbe avere un impatto minimo sul codice. Tutto ruota intorno alla semplicità.
7. Infine, aggiungi una sezione di revisione al file todo.md con un riepilogo delle modifiche apportate e qualsiasi altra informazione pertinente.