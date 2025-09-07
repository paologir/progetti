#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestione clienti e metadata per archivio documenti
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from utils.logger import StructuredLogger

logger = StructuredLogger(__name__)


class ClientMetadataManager:
    """Gestisce metadata e struttura clienti"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.clients_metadata = {}
        self._scan_clients()
    
    def _scan_clients(self):
        """Scansiona le directory cliente"""
        if not self.base_path.exists():
            logger.warning(f"Path base non esiste: {self.base_path}")
            return
        
        for client_dir in self.base_path.iterdir():
            if client_dir.is_dir():
                client_name = client_dir.name
                self.clients_metadata[client_name] = {
                    "path": str(client_dir),
                    "name": client_name,
                    "folders": self._scan_client_structure(client_dir),
                    "last_scan": datetime.now().isoformat()
                }
                logger.info(f"Cliente trovato: {client_name}")
    
    def _scan_client_structure(self, client_path: Path) -> Dict[str, int]:
        """Scansiona struttura interna cliente"""
        structure = {}
        for folder in client_path.iterdir():
            if folder.is_dir():
                file_count = sum(1 for _ in folder.rglob("*") if _.is_file())
                structure[folder.name] = file_count
        return structure
    
    def get_client_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Estrae metadata cliente da path file"""
        try:
            # Converti in path relativo rispetto a base_path
            relative_path = file_path.relative_to(self.base_path)
            parts = relative_path.parts
            
            if len(parts) < 1:
                return {}
            
            client_name = parts[0]
            client_info = self.clients_metadata.get(client_name, {})
            
            metadata = {
                "client_name": client_name,
                "client_path": client_info.get("path", ""),
                "relative_path": str(relative_path),
                "folder_depth": len(parts) - 1
            }
            
            # Aggiungi info sulla sottocartella se presente
            if len(parts) > 2:
                metadata["subfolder"] = parts[1]
                metadata["full_subfolder_path"] = "/".join(parts[1:-1])
            
            return metadata
            
        except ValueError:
            # Path non è relativo a base_path
            logger.warning(f"Path non relativo a base: {file_path}")
            return {}
    
    def filter_by_client(self, client_names: List[str]) -> List[Path]:
        """Ottiene tutti i file di specifici clienti"""
        files = []
        for client_name in client_names:
            if client_name in self.clients_metadata:
                client_path = Path(self.clients_metadata[client_name]["path"])
                files.extend(client_path.rglob("*"))
        return [f for f in files if f.is_file()]
    
    def get_clients_list(self) -> List[str]:
        """Ritorna lista dei clienti disponibili"""
        return list(self.clients_metadata.keys())
    
    def get_client_stats(self, client_name: str) -> Optional[Dict[str, Any]]:
        """Ottiene statistiche per un cliente"""
        if client_name not in self.clients_metadata:
            return None
        
        client_path = Path(self.clients_metadata[client_name]["path"])
        
        # Conta file per tipo
        file_types = {}
        total_size = 0
        
        for file_path in client_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
                total_size += file_path.stat().st_size
        
        return {
            "name": client_name,
            "total_files": sum(file_types.values()),
            "file_types": file_types,
            "total_size_mb": total_size / (1024 * 1024),
            "folders": self.clients_metadata[client_name]["folders"]
        }
    
    def save_metadata(self, output_path: Path):
        """Salva metadata clienti su file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.clients_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata salvati in: {output_path}")
    
    def load_metadata(self, metadata_path: Path):
        """Carica metadata da file"""
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.clients_metadata = json.load(f)
            logger.info(f"Metadata caricati da: {metadata_path}")


class ClientAwareDocumentProcessor:
    """Estende DocumentProcessor con supporto clienti"""
    
    def __init__(self, client_manager: ClientMetadataManager):
        self.client_manager = client_manager
    
    def enrich_document_metadata(self, document, file_path: Path):
        """Arricchisce documento con metadata cliente"""
        client_metadata = self.client_manager.get_client_metadata(file_path)
        
        if client_metadata:
            document.metadata.update(client_metadata)
            
            # Aggiungi tag per filtering
            document.metadata["tags"] = [
                f"client:{client_metadata['client_name']}",
                f"depth:{client_metadata['folder_depth']}"
            ]
            
            if "subfolder" in client_metadata:
                document.metadata["tags"].append(f"folder:{client_metadata['subfolder']}")
        
        return document