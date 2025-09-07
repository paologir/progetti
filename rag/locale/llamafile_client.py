#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from typing import Optional, Dict, Any
from config import settings

class LlamafileClient:
    """Client per interagire con il server llamafile"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or settings.llamafile_base_url
        self.timeout = timeout or settings.llamafile_timeout
        
    def is_available(self) -> bool:
        """Controlla se il server è disponibile"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Genera una risposta dal prompt"""
        if not self.is_available():
            raise ConnectionError("Server llamafile non disponibile")
        
        # Parametri di default
        params = {
            "prompt": prompt,
            "temperature": kwargs.get("temperature", settings.temperature),
            "max_tokens": kwargs.get("max_tokens", settings.llamafile_max_tokens),
            "stop": kwargs.get("stop", []),
            "stream": False
        }
        
        try:
            # Usa l'endpoint completion di llamafile
            response = requests.post(
                f"{self.base_url}/completion",
                json=params,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Il formato di risposta del llamafile è diverso da quello che mi aspettavo
            content = result.get("content", result.get("choices", [{}])[0].get("text", "")).strip()
            
            # Rimuovi token di fine turno specifici di Gemma
            content = content.replace("<end_of_turn>", "").strip()
            
            return content
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Errore nella richiesta al server llamafile: {e}")
    
    def invoke(self, prompt: str) -> str:
        """Compatibilità con l'interfaccia LangChain"""
        return self.generate(prompt)
    
    def get_info(self) -> Dict[str, Any]:
        """Ottieni informazioni sul modello"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}