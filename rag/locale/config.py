#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings
import logging


class Settings(BaseSettings):
    # API Keys
    
    # Paths
    documents_path: Path = Path("documents")
    faiss_index_path: Path = Path("faiss_index")
    raw_pdfs_path: Path = Path("raw_pdfs")
    
    # Model Configuration
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    llm_model_name: str = "gemma3-4b-local"
    
    # LlamaCpp Configuration (legacy)
    model_path: Optional[str] = "/opt/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    n_gpu_layers: int = 0
    n_batch: int = 512
    n_ctx: int = 2048
    temperature: float = 0.1
    
    # Llamafile Configuration
    use_llamafile_cli: bool = True   # Modalità CLI diretta (raccomandato)
    use_llamafile_api: bool = False  # Modalità server HTTP (backup)
    llamafile_base_url: str = "http://127.0.0.1:8080"
    llamafile_timeout: int = 30  # Ridotto per Gemma3-4B (più veloce)
    llamafile_max_tokens: int = 2048  # Aumentato per risposte complete
    
    # Retrieval Configuration - ridotti per Gemma3-4B
    top_k_chunks: int = 3  # Meno chunk per evitare prompt troppo lunghi
    chunk_size: int = 800  # Chunk più piccoli
    chunk_overlap: int = 200
    
    # Security
    max_file_size_mb: int = 50
    allowed_file_extensions: set = {".pdf", ".txt", ".md", ".docx", ".doc", ".xlsx", ".xls", ".csv"}
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    
    # Docling Preprocessing
    enable_docling_preprocessing: bool = True
    docling_export_format: str = "markdown"
    docling_clean_processed_pdfs: bool = False
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    @field_validator("documents_path", "faiss_index_path", "raw_pdfs_path")
    @classmethod
    def validate_paths(cls, v):
        return Path(v)
    
    @classmethod
    def validate_api_key(cls, v):
        if not v:
            raise ValueError("MISTRAL_API_KEY è obbligatoria")
        return v


settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)