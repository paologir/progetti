#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import hashlib
from typing import Any, Optional, Dict, Callable
from functools import wraps
from pathlib import Path
import pickle
import redis
from datetime import datetime, timedelta

from utils.logger import StructuredLogger
from config import settings


logger = StructuredLogger(__name__)


class CacheBackend:
    """Abstract base class per cache backends"""
    
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        raise NotImplementedError
    
    def clear(self) -> None:
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        raise NotImplementedError


class InMemoryCache(CacheBackend):
    """Cache in-memory semplice con TTL"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        logger.info("Inizializzata cache in-memory")
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if entry['expires_at'] and time.time() > entry['expires_at']:
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit per key: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        expires_at = None
        if ttl:
            expires_at = time.time() + ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        logger.debug(f"Valore salvato in cache per key: {key}")
    
    def delete(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Eliminata entry cache: {key}")
    
    def clear(self) -> None:
        self.cache.clear()
        logger.info("Cache svuotata")
    
    def exists(self, key: str) -> bool:
        if key not in self.cache:
            return False
        
        entry = self.cache[key]
        if entry['expires_at'] and time.time() > entry['expires_at']:
            del self.cache[key]
            return False
        
        return True
    
    def cleanup_expired(self) -> int:
        """Rimuove entries scadute"""
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self.cache.items():
            if entry['expires_at'] and current_time > entry['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Rimosse {len(expired_keys)} entries scadute")
        
        return len(expired_keys)


class DiskCache(CacheBackend):
    """Cache su disco con serializzazione"""
    
    def __init__(self, cache_dir: Path = Path("./cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self._load_index()
        logger.info(f"Inizializzata cache su disco in: {cache_dir}")
    
    def _load_index(self):
        """Carica indice delle entries"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
    
    def _save_index(self):
        """Salva indice delle entries"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f)
    
    def _get_cache_file(self, key: str) -> Path:
        """Ottiene path del file cache"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.index:
            return None
        
        entry = self.index[key]
        if entry['expires_at'] and time.time() > entry['expires_at']:
            self.delete(key)
            return None
        
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                value = pickle.load(f)
            logger.debug(f"Cache hit su disco per key: {key}")
            return value
        except Exception as e:
            logger.error(f"Errore lettura cache", exception=e, key=key)
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        expires_at = None
        if ttl:
            expires_at = time.time() + ttl
        
        cache_file = self._get_cache_file(key)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
            
            self.index[key] = {
                'expires_at': expires_at,
                'created_at': time.time(),
                'file': str(cache_file.name)
            }
            self._save_index()
            logger.debug(f"Valore salvato su disco per key: {key}")
        except Exception as e:
            logger.error(f"Errore scrittura cache", exception=e, key=key)
    
    def delete(self, key: str) -> None:
        if key in self.index:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
            del self.index[key]
            self._save_index()
            logger.debug(f"Eliminata entry cache su disco: {key}")
    
    def clear(self) -> None:
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        self.index = {}
        self._save_index()
        logger.info("Cache su disco svuotata")
    
    def exists(self, key: str) -> bool:
        if key not in self.index:
            return False
        
        entry = self.index[key]
        if entry['expires_at'] and time.time() > entry['expires_at']:
            self.delete(key)
            return False
        
        return self._get_cache_file(key).exists()


class RedisCache(CacheBackend):
    """Cache Redis per deployment distribuiti"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.client.ping()
            logger.info(f"Connesso a Redis: {host}:{port}")
        except Exception as e:
            logger.error(f"Errore connessione Redis", exception=e)
            raise
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Redis cache hit per key: {key}")
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Errore lettura Redis", exception=e, key=key)
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        try:
            serialized = json.dumps(value)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            logger.debug(f"Valore salvato in Redis per key: {key}")
        except Exception as e:
            logger.error(f"Errore scrittura Redis", exception=e, key=key)
    
    def delete(self, key: str) -> None:
        self.client.delete(key)
        logger.debug(f"Eliminata entry Redis: {key}")
    
    def clear(self) -> None:
        self.client.flushdb()
        logger.info("Cache Redis svuotata")
    
    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))


class CacheManager:
    """Manager per gestire caching con diversi backends"""
    
    def __init__(self, backend: CacheBackend = None):
        self.backend = backend or InMemoryCache()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        value = self.backend.get(key)
        if value is not None:
            self.stats['hits'] += 1
        else:
            self.stats['misses'] += 1
        return value
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        self.backend.set(key, value, ttl)
        self.stats['sets'] += 1
    
    def delete(self, key: str) -> None:
        self.backend.delete(key)
        self.stats['deletes'] += 1
    
    def clear(self) -> None:
        self.backend.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche cache"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def cache_decorator(self, ttl: int = None, key_prefix: str = ""):
        """Decorator per caching automatico di funzioni"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Genera cache key
                cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
                cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                
                # Controlla cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Esegui funzione
                result = func(*args, **kwargs)
                
                # Salva in cache
                self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator


# Singleton globale per cache
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Ottiene istanza singleton della cache"""
    global _cache_instance
    
    if _cache_instance is None:
        if settings.enable_cache:
            # Puoi cambiare backend qui
            backend = InMemoryCache()
            _cache_instance = CacheManager(backend)
            logger.info("Cache manager inizializzato")
        else:
            # Null cache se disabilitata
            _cache_instance = CacheManager(NullCache())
    
    return _cache_instance


class NullCache(CacheBackend):
    """Cache nulla che non salva niente"""
    
    def get(self, key: str) -> Optional[Any]:
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        pass
    
    def delete(self, key: str) -> None:
        pass
    
    def clear(self) -> None:
        pass
    
    def exists(self, key: str) -> bool:
        return False