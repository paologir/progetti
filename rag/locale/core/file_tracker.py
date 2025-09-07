#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema di tracking file per ingest incrementale
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import sqlite3
from contextlib import contextmanager

from utils.logger import StructuredLogger

logger = StructuredLogger(__name__)


class FileTracker:
    """Traccia stato dei file per ingest incrementale"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path("file_tracker.db")
        self._init_database()
    
    def _init_database(self):
        """Inizializza database SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    file_path TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    last_modified REAL NOT NULL,
                    processed_at TEXT NOT NULL,
                    chunk_count INTEGER DEFAULT 0,
                    client_name TEXT,
                    status TEXT DEFAULT 'processed'
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_at ON processed_files(processed_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_client_name ON processed_files(client_name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON processed_files(status)
            """)
    
    @contextmanager
    def get_connection(self):
        """Context manager per connessione database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcola hash SHA256 del file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Errore calcolo hash per {file_path}: {e}")
            return ""
    
    def is_file_processed(self, file_path: Path) -> bool:
        """Verifica se un file è già stato processato"""
        if not file_path.exists():
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT file_hash, last_modified FROM processed_files WHERE file_path = ?",
                (str(file_path),)
            )
            result = cursor.fetchone()
            
            if not result:
                return False
            
            # Verifica se il file è stato modificato
            current_hash = self._calculate_file_hash(file_path)
            current_mtime = file_path.stat().st_mtime
            
            return (result["file_hash"] == current_hash and 
                   result["last_modified"] == current_mtime)
    
    def mark_file_processed(self, file_path: Path, chunk_count: int = 0, client_name: str = None):
        """Marca un file come processato"""
        if not file_path.exists():
            logger.warning(f"File non esiste: {file_path}")
            return
        
        file_hash = self._calculate_file_hash(file_path)
        file_stat = file_path.stat()
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO processed_files 
                (file_path, file_hash, file_size, last_modified, processed_at, chunk_count, client_name, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(file_path),
                file_hash,
                file_stat.st_size,
                file_stat.st_mtime,
                datetime.now().isoformat(),
                chunk_count,
                client_name,
                'processed'
            ))
            conn.commit()
        
        logger.info(f"File marcato come processato: {file_path}")
    
    def mark_file_failed(self, file_path: Path, error_message: str = ""):
        """Marca un file come fallito"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO processed_files 
                (file_path, file_hash, file_size, last_modified, processed_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(file_path),
                "",  # Hash vuoto per file falliti
                0,
                0,
                datetime.now().isoformat(),
                'failed'
            ))
            conn.commit()
        
        logger.warning(f"File marcato come fallito: {file_path}")
    
    def get_unprocessed_files(self, directory: Path, allowed_extensions: Set[str]) -> List[Path]:
        """Ottiene lista file non ancora processati"""
        unprocessed = []
        
        for ext in allowed_extensions:
            for file_path in directory.rglob(f"*{ext}"):
                if file_path.is_file() and not self.is_file_processed(file_path):
                    unprocessed.append(file_path)
        
        return unprocessed
    
    def get_processed_files(self, client_name: str = None) -> List[Dict]:
        """Ottiene lista file processati"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if client_name:
                cursor.execute("""
                    SELECT * FROM processed_files 
                    WHERE client_name = ? AND status = 'processed'
                    ORDER BY processed_at DESC
                """, (client_name,))
            else:
                cursor.execute("""
                    SELECT * FROM processed_files 
                    WHERE status = 'processed'
                    ORDER BY processed_at DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_failed_files(self) -> List[Dict]:
        """Ottiene lista file falliti"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processed_files 
                WHERE status = 'failed'
                ORDER BY processed_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def remove_file_record(self, file_path: Path):
        """Rimuove record di un file dal tracking"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM processed_files WHERE file_path = ?", (str(file_path),))
            conn.commit()
        
        logger.info(f"Record rimosso per file: {file_path}")
    
    def get_stats(self) -> Dict:
        """Ottiene statistiche sui file processati"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Conta per status
            cursor.execute("""
                SELECT status, COUNT(*) as count, SUM(file_size) as total_size
                FROM processed_files 
                GROUP BY status
            """)
            status_stats = {row["status"]: {"count": row["count"], "total_size": row["total_size"] or 0} 
                          for row in cursor.fetchall()}
            
            # Conta per client
            cursor.execute("""
                SELECT client_name, COUNT(*) as count, SUM(chunk_count) as total_chunks
                FROM processed_files 
                WHERE status = 'processed' AND client_name IS NOT NULL
                GROUP BY client_name
            """)
            client_stats = {row["client_name"]: {"count": row["count"], "chunks": row["total_chunks"] or 0} 
                          for row in cursor.fetchall()}
            
            return {
                "status_stats": status_stats,
                "client_stats": client_stats,
                "total_processed": status_stats.get("processed", {}).get("count", 0),
                "total_failed": status_stats.get("failed", {}).get("count", 0)
            }
    
    def cleanup_orphaned_records(self):
        """Rimuove record di file che non esistono più"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM processed_files")
            
            removed_count = 0
            for row in cursor.fetchall():
                file_path = Path(row["file_path"])
                if not file_path.exists():
                    conn.execute("DELETE FROM processed_files WHERE file_path = ?", (str(file_path),))
                    removed_count += 1
            
            conn.commit()
            logger.info(f"Rimossi {removed_count} record orfani")
    
    def reset_all(self):
        """Resetta tutto il tracking"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM processed_files")
            conn.commit()
        
        logger.info("Tracking resettato completamente")
    
    def export_to_json(self, output_path: Path):
        """Esporta tracking in formato JSON"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM processed_files ORDER BY processed_at DESC")
            
            data = [dict(row) for row in cursor.fetchall()]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Tracking esportato in: {output_path}")