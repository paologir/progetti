#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def start_llamafile_server():
    """Avvia il server llamafile"""
    
    # Percorso del llamafile
    llamafile_path = Path("/opt/llm/llamafiles/google_gemma-3-4b-it-Q6_K.llamafile")
    
    if not llamafile_path.exists():
        print(f"❌ Llamafile non trovato: {llamafile_path}")
        return False
    
    # Parametri per il server - ottimizzati per GPU ROCm
    cmd = [
        str(llamafile_path),
        "--server",
        "--nobrowser",
        "--port", "8080",
        "-ngl", "35",      # GPU layers - offload completo su GPU
        "-c", "8192",      # Context window esteso
        "--gpu", "AUTO",   # Auto-detect GPU (ROCm)
        "-t", "8"          # Thread per CPU layers residui
    ]
    
    print(f"🚀 Avvio del server llamafile...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        # Avvia il processo usando shell=True per compatibilità
        cmd_str = ' '.join(cmd)
        process = subprocess.Popen(
            cmd_str,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Attendi che il server sia pronto
        print("⏳ Attendo che il server sia pronto...")
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://127.0.0.1:8080/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server llamafile avviato con successo!")
                    print("🔗 Endpoint: http://127.0.0.1:8080")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            
            # Controlla se il processo è ancora in esecuzione
            if process.poll() is not None:
                print("❌ Il processo del server è terminato inaspettatamente")
                return False
        
        print("❌ Timeout: il server non è diventato disponibile")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Errore nell'avvio del server: {e}")
        return False

def check_server_status():
    """Controlla se il server è in esecuzione"""
    try:
        response = requests.get("http://127.0.0.1:8080/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def stop_server():
    """Ferma il server llamafile"""
    try:
        # Trova e termina il processo
        result = subprocess.run(
            ["pkill", "-f", "granite-3.2-8b-instruct-Q4_K_M.llamafile"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("🛑 Server fermato con successo")
            return True
        else:
            print("⚠️  Nessun processo server trovato")
            return False
    except Exception as e:
        print(f"❌ Errore nel fermare il server: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            start_llamafile_server()
        elif sys.argv[1] == "stop":
            stop_server()
        elif sys.argv[1] == "status":
            if check_server_status():
                print("✅ Server in esecuzione")
            else:
                print("❌ Server non in esecuzione")
        else:
            print("Uso: python start_llamafile_server.py [start|stop|status]")
    else:
        start_llamafile_server()