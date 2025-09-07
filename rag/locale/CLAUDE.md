# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Local RAG MVP system** - a Retrieval Augmented Generation system that uses a local LLM (Gemma 3-4B) for language generation. The system ingests documents from an Obsidian vault into a vector database using an advanced hybrid retrieval system (Semantic Search + BM25) and allows users to query the knowledge base using natural language without requiring API keys or internet connectivity.

### Key Features
- **Hybrid Retrieval**: Combines semantic search (FAISS embeddings) with keyword search (BM25) for optimal document retrieval
- **Client-Aware Search**: Intelligently prioritizes documents based on client names mentioned in queries
- **File-Type Boost**: Enhanced search for specific file types (concorrenti.md, corpus.md, dati.md, etc.)
- **Date-Specific Queries**: Automatically detects and prioritizes Journal entries for date-based queries (oggi, ieri, DD/MM/YYYY, etc.)
- **Source Attribution**: Shows which files were consulted to generate each response
- **Content Enrichment**: Automatically adds client/filename context to improve search accuracy
- **Executable Scripts**: Main scripts have shebang and are directly executable

## Commands

### Setup and Installation
```bash
# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# IMPORTANTE: Attivare SEMPRE l'ambiente virtuale prima di eseguire qualsiasi script Python
source .venv/bin/activate

# Ingest Obsidian vault documents (REQUIRED - run this first!)
./obsidian_ingest.py

# Test local LLM functionality
python test_llm.py
```

### Document Processing and Ingestion

#### Primary Data Source: Obsidian Vault
The system is configured to use `/opt/obsidian/appunti/` as the primary data source:
```bash
# Index all documents from Obsidian vault (MAIN COMMAND)
./obsidian_ingest.py

# This creates 'obsidian_index' with ~6900+ chunks from ~1100+ documents
# Including client-specific folders and Journal entries:
# - Clienti/Didonè Comacchio/concorrenti.md
# - Clienti/FIS Group/corpus.md
# - Journal/24-07-2025.md (daily activity logs)
# - etc.
```

#### Legacy Document Processing (Optional)
```bash
# Convert PDFs in /raw_pdfs to Markdown files in /documents
python preprocess.py

# Full pipeline: preprocessing + ingesting
python full_pipeline.py

# Ingest documents from /documents folder into vector store
python ingest.py
```

### Running the System
```bash
# Simple CLI interface with source attribution (EXECUTABLE)
./simple_rag.py

# Advanced CLI chatbot with debug features (EXECUTABLE)
./chatbot.py

# REST API server (production ready) (EXECUTABLE)
./api.py

# Debug/development tool with detailed hybrid search analysis (EXECUTABLE)
./debug_rag_flow.py "your question here"

# Alternative: traditional Python execution still works
python simple_rag.py
```

### Example Output with Source Attribution
```
Bot: Francesca Endrizzi architetto interior designer, MTMA Architetti, Architect For You.

📄 **Fonti consultate:**
- Didonè Comacchio/concorrenti.md
- Didonè Comacchio/corpus.md
- Didonè Comacchio/analisi preliminare.md
```

### Date-Based Query Examples
The system now intelligently handles date-specific queries and prioritizes Journal entries:

```bash
# Query for today's activities
./simple_rag.py
> Cosa ho fatto oggi?
Bot: - [x] Corso RAG
- [x] Check siti per Maspe - email risposta  
- [ ] Segnalare aggiornamento versione php a Progeo...

📄 **Fonti consultate:**
- unknown/24-07-2025.md

# Query for specific date
> Attività del 23/07/2025
Bot: [Returns content from Journal/23-07-2025.md]

# Supported date formats:
- "oggi", "ieri", "domani" (relative dates)
- "24/07/2025", "24-07-2025" (DD/MM/YYYY format)
- "24/07" (DD/MM - assumes current year)
- "lunedì", "martedì", etc. (day names - planned)
- "luglio 2025" (month year - planned)
```

### Development and Testing
```bash
# Alpha optimization testing (EXECUTABLE)
./test_alpha_optimization.py

# Single query analysis (EXECUTABLE)
./analyze_single_query.py "your test query"

# Retrieval evaluation with IR metrics (EXECUTABLE)
./retrieval_evaluation.py

# Analyze optimization results (EXECUTABLE)
./analyze_alpha_results.py

# Lint/format commands not configured - ask user if needed
```

## Code Architecture

### Core Components
1. **obsidian_ingest.py** - Primary document processing pipeline for Obsidian vault
2. **hybrid_retriever.py** - Advanced hybrid search combining semantic + keyword search with intelligent boosting and date-specific query handling
3. **simple_rag.py** - Basic RAG implementation with source attribution and token tracking
4. **chatbot.py** - Interactive CLI interface with conversation history and source display
5. **debug_rag_flow.py** - Development tool for analyzing hybrid search behavior
6. **api.py** - FastAPI REST API with endpoints for chat, ingestion, file upload

### Configuration System
- **config.py** - Centralized Pydantic configuration
- Default embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Default LLM: Gemma 3-4B via llamafile CLI (completely local)
- Data source: `/opt/obsidian/appunti/` Obsidian vault
- Index location: `obsidian_index/` (FAISS + metadata)
- No API keys required - everything runs locally

### Data Flow

#### Current Hybrid RAG Flow
```
Obsidian Vault (/opt/obsidian/appunti/) → 
Content Enrichment ([Client: X - File: Y] headers) → 
Chunking (1000 chars, 200 overlap) → 
Embeddings + BM25 Index → 
FAISS Vector Store (obsidian_index)

User Query → 
Date Detection (if applicable) → 
Hybrid Search (Semantic + BM25 + Intelligent Boosting + Date Priority) → 
Top chunks with client/file/date prioritization → 
Context + Source Attribution → 
Local LLM → 
Response with "📄 Fonti consultate"
```

#### Intelligent Boosting System
- **Client Boost**: +0.8 when query mentions client name (e.g., "Didonè Comacchio")
- **File Type Boost**: +0.9 for specific files (concorrenti.md, corpus.md, dati.md)
- **Date Query Boost**: +1.5 for Journal entries matching detected dates (oggi, DD/MM/YYYY, etc.)
- **Super Boost**: +2.0 when query contains both client name and file type
- **Content Enrichment**: Each document prefixed with `[Cliente: X - File: Y]` for better BM25 matching
- **Date-Specific Search**: Automatic Journal file discovery for date queries with 2x BM25 score multiplier

### Key Modules
- **hybrid_retriever.py** - Advanced hybrid search engine with intelligent boosting
- **obsidian_ingest.py** - Obsidian vault document processing with metadata extraction
- **llm_adapter.py** - Local LLM integration (Gemma 3-4B via llamafile)
- **utils/cache.py** - Multi-backend caching (memory, disk, Redis)
- **utils/logger.py** - Structured JSON logging  
- **utils/security.py** - Input validation and sanitization

### Document Processing

#### Primary: Obsidian Vault Processing
- **Source**: `/opt/obsidian/appunti/` directory structure
- **Supported formats**: Markdown (.md files)
- **Client structure**: `Clienti/[ClientName]/[filename].md`
- **Journal structure**: `Journal/DD-MM-YYYY.md` (daily activity logs)
- **Metadata extraction**: Automatic client name, file type, dates, prices, journal dates
- **Content enrichment**: Headers added for better search (`[Cliente: X - File: Y]`)
- **Output**: `obsidian_index/` with ~6900+ chunks from ~1100+ documents (including ~960 Journal entries)

#### Legacy: Standard Processing  
- Documents in `/documents` folder (PDF, TXT, MD)
- Basic chunking without client-aware processing
- Creates `faiss_index/` (now deprecated in favor of obsidian_index)

### API Endpoints (api.py)
- `POST /chat` - Chat with the RAG system
- `POST /ingest` - Ingest new documents
- `POST /upload` - Upload and ingest files
- `GET /stats` - System statistics and costs
- `GET /health` - Health check

## Development Notes

### Hybrid Search Optimization
The system uses a sophisticated hybrid approach that solved critical retrieval issues:
- **Problem solved**: Documents like `concorrenti.md` weren't found because content didn't match query keywords
- **Solution**: Content enrichment + intelligent boosting + BM25/semantic fusion
- **Result**: Accurate retrieval of client-specific files with source attribution

### Client-Aware Architecture
Designed for multi-client consulting environment:
- Automatic client detection from folder structure (`Clienti/[ClientName]/`)
- Query-based client prioritization (when "Didonè Comacchio" mentioned, boost those docs)
- File-type awareness (concorrenti.md, corpus.md, dati.md have semantic meaning)
- Cross-client contamination prevention

### Source Attribution & Transparency  
All responses include source file information for verification:
```
📄 **Fonti consultate:**
- Didonè Comacchio/concorrenti.md
- Didonè Comacchio/corpus.md
```

### Performance Characteristics
- **Index size**: ~6900 chunks from ~1100 documents (including ~960 Journal entries)
- **Search time**: <2 seconds for hybrid retrieval
- **Accuracy**: High precision for client-specific and date-based queries
- **Memory usage**: Efficient FAISS + BM25 co-indexing
- **Alpha optimization**: Current α=0.6 (60% semantic, 40% BM25) - verified optimal through testing

## Example Queries

### Client-Specific Queries
```bash
# Works perfectly - finds concorrenti.md for Didonè Comacchio
"Quali sono i concorrenti di Didonè Comacchio?"

# Works - finds corpus.md and other FIS documents  
"Che tipo di azienda è FIS Group?"

# Works - finds dati.md with account information
"Quali sono i dati di accesso per Maffeis?"
```

### Date-Based Queries (NEW)
```bash
# Works perfectly - finds today's Journal entry
"Cosa ho fatto oggi?"

# Works - finds specific date's activities
"Attività del 24/07/2025"

# Works - relative dates
"Cosa ho fatto ieri?"

# Works - various date formats
"24/07/2025", "24-07-2025", "24/07"
```

### File-Type Queries
```bash
# Finds corpus.md files for general company info
"Informazioni generali su [ClientName]"

# Finds concorrenti.md files
"Chi sono i competitor di [ClientName]"

# Finds dati.md files  
"Account e credenziali di [ClientName]"
```

## Troubleshooting

### If Retrieval Seems Incorrect
1. Check which index is being used: should be `obsidian_index/` not `faiss_index/`
2. Verify Obsidian vault path: `/opt/obsidian/appunti/` should exist
3. Rebuild index if documents were added: `python obsidian_ingest.py`
4. Use debug tool: `python debug_rag_flow.py "your query"` to see search details

### If Documents Are Missing
1. Ensure documents are in correct Obsidian structure: `Clienti/[ClientName]/[file].md`
2. Check file permissions on `/opt/obsidian/appunti/`
3. Rebuild index after adding documents
4. Verify index statistics in console output

## Flusso di lavoro standard
1. Per prima cosa, analizza il problema, cerca i file rilevanti nel codice e scrivi un piano per todo.md. 
2. Il piano dovrebbe contenere una lista di cose da fare che puoi spuntare man mano che le completi.
3. Prima di iniziare a lavorare, contattami e verificherò il piano.
4. Quindi, inizia a lavorare sulle cose da fare, contrassegnandole come completate man mano che procedi.
5. Per favore, per ogni passaggio, forniscimi una spiegazione dettagliata delle modifiche apportate.
6. Semplifica il più possibile ogni attività e modifica al codice. Vogliamo evitare modifiche massicce o complesse. Ogni modifica dovrebbe avere un impatto minimo sul codice. Tutto ruota intorno alla semplicità.
7. Infine, aggiungi una sezione di revisione al file todo.md con un riepilogo delle modifiche apportate e qualsiasi altra informazione pertinente.