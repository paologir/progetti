# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a multi-language utility collection organized by purpose and domain. Each directory contains independent tools grouped by functionality for better navigation and maintenance.

## Common Development Commands

### Python Projects
```bash
# Install dependencies for specific projects
pip install python-docx markdown beautifulsoup4  # For carta_intestata
pip install langchain-community langchain-huggingface langchain-mistralai faiss-cpu python-dotenv  # For RAG projects

# Run Python scripts
python3 script.py
```

### C Programs
```bash
# Compile C programs
gcc program.c -o program
./program
```

### Bash Scripts
```bash
# Most bash scripts are executable
./script_name
# Or run with bash
bash script_name
```

### Assembly
```bash
# Assemble and link (example for Linux x86-64)
nasm -f elf64 program.asm
ld program.o -o program
```

## High-Level Architecture

### New Directory Structure (Reorganized)

- **Landing Pages** (`landing/`):
  - `landing/fis/` - Landing page for FIS project
  - `landing/italplastick/` - Landing page for Italplastick
  - `landing/builder/` - Landing page builder tool

- **RAG & AI Projects** (`rag/`):
  - `rag/mistral-mvp/` - RAG chatbot using Mistral AI, LangChain, and FAISS
  - `rag/locale/` - Local RAG implementation with Gemma model
  - `rag/mistral/` - Mistral-based RAG system  
  - `rag/r-finetune/` - R language LLM fine-tuning project

- **Languages** (`languages/`):
  - `languages/python/` - Python utilities and tools
    - `carta_intestata/` - DOCX letterhead generator
    - `seo-analisi/`, `sitemap.py`, `url2md/` - SEO and web tools
    - `statistica/` - Statistical analysis tools
    - `aiutofatture/` - Invoice helper application
  - `languages/c/` - C programs (financial calculations, utilities)
  - `languages/bash/` - Bash scripts (file management, text processing)
  - `languages/r/` - R scripts (web traffic analysis)
  - `languages/asm/` - Assembly programs

- **Web Projects** (`web/`):
  - `web/sito-gironi/` - Tournament bracket website

- **Tools & Utilities** (`tools/`):
  - `tools/agents/` - AI agent configurations
  - `tools/MASPE-SAW/` - SEO analysis automation workflow
  - `tools/investimenti/` - Investment analysis tools
  - `tools/llm/` - LLM utilities and scripts

### Key Design Patterns

1. **Standalone Scripts**: Each script is self-contained with its own dependencies
2. **Purpose-Based Organization**: Tools grouped by functionality (landing pages, RAG systems, etc.)
3. **No Central Build System**: Each project manages its own dependencies
4. **Direct Execution**: Scripts are run directly without a build step (except C programs)
5. **Clean Separation**: Different domains are isolated in their respective folders

### Important Considerations

- Python scripts typically use Python 3.x and should be run with `python3` command (not `python`)
- Some Python projects have specific dependencies (check imports or README files)
- RAG projects require API keys stored in .env files (see individual project README files)
- RAG locale project uses .gitignore to exclude large model files and venv directories
- No formal test suites - scripts are tested by direct execution
- Follow existing code patterns within each domain directory
- Use the specialized agents for domain-specific tasks (RAG, landing pages, etc.)

## Agenti Specializzati Disponibili (8 agenti totali)

### Agenti per Task Complessi
- **general-purpose**: Ricerca complessa, task multi-step, ricerca codice
- **web-research-expert**: Ricerca web approfondita, verifica fonti, analisi di mercato
- **data-analysis-expert**: Analisi dati, pulizia dataset, visualizzazioni, test statistici

### Agenti per Sviluppo e Documentazione  
- **rag-systems-expert**: Sistemi RAG, vector databases, LangChain, FAISS, ChromaDB
- **documentation-writer-expert**: API docs, README, guide tecniche, changelog
- **git-expert**: Git workflows avanzati, branching, merge conflicts, hooks

### Agenti per Marketing e Web
- **seo-sem-report-expert**: Report SEO/SEM, analisi performance, KPI
- **marketing-copywriter-expert**: Copy persuasivo, landing pages, email campaigns
- **landing-page-builder-expert**: Landing pages ad alta conversione, A/B testing

### Come Usare gli Agenti
```bash
# Esempio di utilizzo tramite Task tool per analisi dati
Task(description="Analizza dataset", prompt="Analizza questo CSV per trend", subagent_type="data-analysis-expert")

# Esempio per documentazione
Task(description="Crea docs", prompt="Genera documentazione API", subagent_type="documentation-writer-expert")

# Esempio per sistemi RAG
Task(description="Ottimizza RAG", prompt="Migliora retrieval accuracy", subagent_type="rag-systems-expert")
```