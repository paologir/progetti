#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path
from typing import Optional, List
import hashlib
import secrets
from functools import wraps
import time


class SecurityValidator:
    """Validazione e sanitizzazione input per prevenire attacchi"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Rimuove caratteri pericolosi dai nomi file"""
        # Rimuovi path traversal
        filename = os.path.basename(filename)
        # Rimuovi caratteri speciali
        filename = re.sub(r'[^\w\s.-]', '', filename)
        # Limita lunghezza
        return filename[:255]
    
    @staticmethod
    def validate_file_path(file_path: Path, base_path: Path) -> bool:
        """Verifica che il path sia dentro la directory consentita"""
        try:
            resolved_path = file_path.resolve()
            resolved_base = base_path.resolve()
            return resolved_path.is_relative_to(resolved_base)
        except Exception:
            return False
    
    @staticmethod
    def validate_file_size(file_path: Path, max_size_mb: int) -> bool:
        """Verifica dimensione file"""
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            return size_mb <= max_size_mb
        except Exception:
            return False
    
    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 1000) -> str:
        """Sanitizza input utente"""
        # Rimuovi caratteri di controllo
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # Limita lunghezza
        text = text[:max_length]
        # Trim spazi
        return text.strip()
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Valida formato API key"""
        # Controlla formato base (alfanumerico con trattini)
        pattern = r'^[a-zA-Z0-9\-_]{20,}$'
        return bool(re.match(pattern, api_key))


class RateLimiter:
    """Rate limiting per prevenire abusi"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Verifica se la richiesta è consentita"""
        now = time.time()
        
        # Pulisci vecchie richieste
        self.requests[identifier] = [
            req_time for req_time in self.requests.get(identifier, [])
            if now - req_time < self.window_seconds
        ]
        
        # Verifica limite
        if len(self.requests.get(identifier, [])) >= self.max_requests:
            return False
        
        # Aggiungi nuova richiesta
        if identifier not in self.requests:
            self.requests[identifier] = []
        self.requests[identifier].append(now)
        
        return True
    
    def rate_limit_decorator(self, get_identifier_func):
        """Decorator per applicare rate limiting"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                identifier = get_identifier_func(*args, **kwargs)
                if not self.is_allowed(identifier):
                    raise Exception("Rate limit exceeded. Riprova più tardi.")
                return func(*args, **kwargs)
            return wrapper
        return decorator


class TokenBucket:
    """Token bucket per rate limiting più sofisticato"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Consuma token se disponibili"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Ricarica token basandosi sul tempo trascorso"""
        now = time.time()
        elapsed = now - self.last_refill
        
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


def generate_session_id() -> str:
    """Genera ID sessione sicuro"""
    return secrets.token_urlsafe(32)


def hash_content(content: str) -> str:
    """Hash contenuto per caching sicuro"""
    return hashlib.sha256(content.encode()).hexdigest()