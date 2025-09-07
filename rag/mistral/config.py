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
    mistral_api_key: str
    
    # Paths
    documents_path: Path = Path("documents")
    faiss_index_path: Path = Path("faiss_index")
    raw_pdfs_path: Path = Path("raw_pdfs")
    
    # Model Configuration
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    llm_model_name: str = "mistral-small"
    temperature: float = 0.1
    
    # Retrieval Configuration
    top_k_chunks: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Security
    max_file_size_mb: int = 50
    allowed_file_extensions: set = {".pdf", ".txt", ".md"}
    
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
    
    @field_validator("mistral_api_key")
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