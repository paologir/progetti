# TODO - Progetto LLM Manager con llama.cpp

## Configurazione Sistema
- **llama.cpp**: ~/llama.cpp/build/bin (llama-cli, llama-server)
- **GPU**: AMD 780M con 16GB VRAM allocata (Vulkan, -ngl 99)
- **RAM**: 64GB totali
- **Modelli**: /opt/llm

## Tasks - Alta Priorità

### 1. ✅ Creare script principale llm_manager.py per gestione modelli in /opt/llm
- Scanner per modelli GGUF
- Gestione configurazioni
- Interfaccia unificata

### 2. ✅ Implementare funzione per scansione e catalogazione modelli GGUF in /opt/llm
- Lettura metadata modelli
- Salvataggio info in JSON
- Cache informazioni modelli

### 3. ✅ Creare script per lancio inferenza con llama-cli (parametri: -ngl 99, context size ottimale)
- Wrapper per llama-cli
- Parametri GPU Vulkan
- Gestione context size

### 4. ✅ Implementare calcolo automatico context size basato su dimensione modello e RAM disponibile
- Stima memoria richiesta
- Ottimizzazione per 16GB VRAM
- Fallback su RAM sistema

### 5. ✅ Creare script per avvio llama-server con configurazioni predefinite per ogni modello
- Wrapper per llama-server
- Port 8080 default
- Configurazioni per modello

## Tasks - Media Priorità

### 6. ✅ Implementare sistema di profili modello (salvare configurazioni ottimali per ogni modello)
- JSON con configurazioni
- Parametri ottimali testati
- Override manuale

### 7. ✅ Creare script di benchmark per testare velocità generazione token/s
- Test standardizzati
- Metriche: token/s, latenza
- Report comparativo

### 8. ✅ Implementare test comparativo tra modelli (stesso prompt, metriche di performance)
- Prompt di test standard
- Confronto prestazioni
- Export risultati

### 9. ✅ Aggiungere interfaccia CLI user-friendly per selezione rapida modelli
- Menu interattivo
- Ricerca modelli
- Quick launch

## Tasks - Bassa Priorità

### 10. ✅ Creare script di monitoring risorse (VRAM, RAM, CPU) durante inferenza
- Monitor real-time
- Log utilizzo risorse
- Alert sovraccarico

### 11. ✅ Implementare gestione preset per diversi use case (chat, coding, creative writing)
- Template prompt
- Parametri ottimizzati
- Quick select

### 12. ✅ Preparare documentazione per futura migrazione a ROCm
- Requisiti ROCm Debian
- Procedura compilazione
- Benchmark attesi

## Note Implementazione

### Struttura Directory Progetto
```
/opt/progetti/llm/
├── llm_manager.py      # Script principale
├── llm_benchmark.py    # Tool benchmark
├── llm_monitor.py      # Monitor risorse
├── configs/            # Configurazioni modelli
├── presets/            # Preset use case
└── TODO.md            # Questo file
```

### Parametri Chiave llama-cli
- `-ngl 99` - Offload tutti i layer su GPU
- `-c [context]` - Dimensione contesto
- `-t [threads]` - Thread CPU
- `--vulkan` - Backend Vulkan per AMD

### Parametri Chiave llama-server
- `--port 8080` - Porta server
- `--host 0.0.0.0` - Bind su tutte le interfacce
- Stessi parametri GPU di llama-cli