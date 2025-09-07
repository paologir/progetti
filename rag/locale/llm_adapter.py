#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional
from langchain_community.llms import LlamaCpp
from llamafile_client import LlamafileClient
from llamafile_cli_client import LlamafileCLIClient
from config import settings

class LLMAdapter:
    """Adapter per supportare LlamaCpp, Llamafile API e Llamafile CLI"""
    
    def __init__(self):
        self.client = None
        self.llm_type = None
        
        try:
            # Priorità: CLI > API > LlamaCpp
            if settings.use_llamafile_cli:
                self.client = LlamafileCLIClient()
                self.llm_type = "llamafile_cli"
            elif settings.use_llamafile_api:
                self.client = LlamafileClient()
                self.llm_type = "llamafile_api"
            else:
                self.client = LlamaCpp(
                    model_path=settings.model_path,
                    n_gpu_layers=settings.n_gpu_layers,
                    n_batch=settings.n_batch,
                    n_ctx=settings.n_ctx,
                    f16_kv=True,
                    temperature=settings.temperature,
                )
                self.llm_type = "llamacpp"
        except Exception as e:
            print(f"Errore durante l'inizializzazione del modello LLM: {e}")
            self.client = None
            self.llm_type = None
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoca il modello LLM"""
        if self.client is None:
            raise Exception("Modello LLM non inizializzato correttamente")
        
        try:
            if self.llm_type == "llamafile_cli":
                # Modalità CLI diretta - non richiede server
                result = self.client.generate(prompt, **kwargs)
                if result is None:
                    raise Exception("Llamafile CLI ha restituito None")
                return result
            elif self.llm_type == "llamafile_api":
                # Controlla se il server è disponibile
                if not self.client.is_available():
                    raise ConnectionError("Server llamafile non disponibile. Avvia con: python start_llamafile_server.py start")
                
                result = self.client.generate(prompt, **kwargs)
                if result is None:
                    raise Exception("Il server llamafile ha restituito None")
                return result
            else:
                result = self.client.invoke(prompt, **kwargs)
                if result is None:
                    raise Exception("LlamaCpp ha restituito None")
                return result
        except Exception as e:
            raise Exception(f"Errore nell'invocazione del modello LLM ({self.llm_type}): {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Ottieni informazioni sul modello"""
        if self.llm_type == "llamafile_cli":
            return {
                "type": "llamafile_cli",
                "model_info": self.client.get_info()
            }
        elif self.llm_type == "llamafile_api":
            return {
                "type": "llamafile_api",
                "base_url": settings.llamafile_base_url,
                "model_info": self.client.get_info()
            }
        else:
            return {
                "type": "llamacpp",
                "model_path": settings.model_path,
                "n_gpu_layers": settings.n_gpu_layers,
                "n_ctx": settings.n_ctx
            }
    
    def is_available(self) -> bool:
        """Controlla se il modello è disponibile"""
        if self.client is None:
            return False
        
        if self.llm_type in ["llamafile_cli", "llamafile_api"]:
            return self.client.is_available()
        else:
            return True  # LlamaCpp è sempre disponibile se caricato correttamente