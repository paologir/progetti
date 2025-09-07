#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional
from config import settings

class LlamafileCLIClient:
    """Client per chiamate dirette CLI al llamafile (no server HTTP)"""
    
    def __init__(self, llamafile_path: str = None, model_gguf: str = None):
        # Percorso del llamafile
        self.llamafile_path = Path(llamafile_path or "/opt/llm/llamafiles/google_gemma-3-4b-it-Q6_K.llamafile")
        
        # Modello GGUF (opzionale, il llamafile dovrebbe averne uno built-in)
        self.model_gguf = model_gguf or "google_gemma-3-4b-it-Q6_K.gguf"
        
        # Verifica che il llamafile esista
        if not self.llamafile_path.exists():
            raise FileNotFoundError(f"Llamafile non trovato: {self.llamafile_path}")
    
    def is_available(self) -> bool:
        """Controlla se il llamafile è disponibile"""
        return self.llamafile_path.exists() and self.llamafile_path.is_file()
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Genera una risposta dal prompt usando chiamata CLI diretta"""
        if not self.is_available():
            raise FileNotFoundError(f"Llamafile non disponibile: {self.llamafile_path}")
        
        
        try:
            # Salva il prompt in un file temporaneo per evitare problemi di escape
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Modifica il comando per usare il file - DISABILITA GPU per stabilità
            cmd_modified = [
                str(self.llamafile_path),
                "--cli",
                "--gpu", "disable",  # Disabilita GPU per evitare crash
                "-ngl", "0",  # Nessun layer su GPU
                "-c", "8192",
                "-t", "8",
                "--temp", str(kwargs.get("temperature", settings.temperature)),
                "-n", str(kwargs.get("max_tokens", settings.llamafile_max_tokens)),
                "-f", prompt_file  # Usa file invece di -p per prompt lunghi
            ]
            
            # Converti in stringa per shell execution
            cmd_str = ' '.join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in cmd_modified)
            result = subprocess.run(
                cmd_str,
                shell=True,  # Necessario per i llamafile (sono boot sectors)
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            # Rimuovi il file temporaneo
            import os
            os.unlink(prompt_file)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Errore sconosciuto"
                raise Exception(f"Llamafile ha restituito codice di errore {result.returncode}: {error_msg}")
            
            # Pulisci l'output
            output = result.stdout.strip()
            
            # Rimuovi token di fine turno specifici di Gemma
            output = output.replace("<end_of_turn>", "").strip()
            
            # Rimuovi il prompt originale se presente nell'output
            if prompt in output:
                output = output.replace(prompt, "", 1).strip()
            
            return output
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Timeout nell'esecuzione del llamafile (60 secondi)")
        except Exception as e:
            raise Exception(f"Errore nell'esecuzione del llamafile CLI: {e}")
    
    def invoke(self, prompt: str) -> str:
        """Compatibilità con l'interfaccia LangChain"""
        return self.generate(prompt)
    
    def get_info(self) -> dict:
        """Ottieni informazioni sul modello"""
        return {
            "type": "llamafile_cli",
            "llamafile_path": str(self.llamafile_path),
            "model_gguf": self.model_gguf,
            "available": self.is_available()
        }