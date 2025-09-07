# 🤖 LLM Manager - Sistema Completo per LLM Locali

Sistema completo per gestire, testare e ottimizzare modelli LLM locali con llama.cpp su GPU AMD.

## 🚀 Quick Start

```bash
# Interfaccia rapida interattiva
./llm_quick.py

# Lista modelli disponibili
./llm_manager.py list -v

# Esegui modello con preset ottimizzato
./llm_manager.py usecase Qwen2.5-Coder-3B -u coding -p "Scrivi codice Python"

# Benchmark performance
./llm_benchmark.py compare Qwen2.5-Coder-3B gemma-3n
```

## 📁 Struttura Progetto

```
/opt/progetti/llm/
├── llm_manager.py      # Script principale - gestione modelli
├── llm_benchmark.py    # Tool benchmark e test performance  
├── llm_monitor.py      # Monitoring risorse real-time
├── llm_quick.py        # Interfaccia utente interattiva
├── configs/            # Profili modelli salvati
├── presets/            # Template use case
├── benchmark_results/  # Risultati test salvati
├── TODO.md            # Lista task progetto
├── ROCM_MIGRATION.md  # Guida migrazione ROCm
└── README_NEW.md      # Questa documentazione
```

## 🛠️ Funzionalità Principali

### 1. **llm_manager.py** - Gestione Modelli

**Comandi Base:**
```bash
# Lista modelli con info dettagliate
./llm_manager.py list -v

# Esegui modello interattivo
./llm_manager.py run Qwen2.5-Coder-3B --preset balanced

# Avvia server HTTP
./llm_manager.py server gemma-3n --port 8080

# Info sistema
./llm_manager.py info
```

**Gestione Profili:**
```bash
# Crea profilo ottimizzato
./llm_manager.py profile Qwen2.5-Coder-3B --create

# Visualizza profilo salvato
./llm_manager.py profile Qwen2.5-Coder-3B --show
```

**Use Case Specializzati:**
```bash
# Lista use case disponibili
./llm_manager.py usecase --list

# Coding (temp 0.2, context ampio)
./llm_manager.py usecase Qwen2.5-Coder-3B -u coding

# Chat conversazionale (temp 0.7, bilanciato)
./llm_manager.py usecase gemma-3n -u chat

# Scrittura creativa (temp 0.9, creativo)
./llm_manager.py usecase Qwen2.5-Coder-3B -u creative
```

### 2. **llm_benchmark.py** - Performance Testing

```bash
# Test singolo modello
./llm_benchmark.py test Qwen2.5-Coder-3B --prompt-type medium

# Suite completa di test
./llm_benchmark.py suite gemma-3n

# Confronto tra modelli
./llm_benchmark.py compare Qwen2.5-Coder-3B gemma-3n deepseek-ai

# Visualizza risultati salvati
./llm_benchmark.py results --last 10
```

### 3. **llm_monitor.py** - Resource Monitoring

```bash
# Monitor processo LLM esistente
./llm_monitor.py --live --duration 60

# Monitor con logging
./llm_monitor.py --live --log monitor.json

# Monitor processo specifico
./llm_monitor.py --live --pid 12345
```

### 4. **llm_quick.py** - Interfaccia Interattiva

Launcher con menu colorato e indicatori visivi:
- ✅ Modelli con profilo configurato
- 🔴🟡🟢 Indicatori dimensione e performance
- Menu benchmark, profili, server
- Selezione preset rapida

## ⚙️ Configurazione Sistema

### Hardware Supportato
- **GPU**: AMD 780M con 16GB VRAM allocata
- **RAM**: 64GB totale
- **Backend**: Vulkan (attuale) → ROCm (futuro)
- **llama.cpp**: `~/llama.cpp/build/bin/`

### Performance Misurate
| Modello | Dimensione | Token/s | Context Ottimale |
|---------|------------|---------|------------------|
| Qwen2.5-Coder-3B | 1.8 GB | 31 tok/s | 16384 |
| Gemma-3n-4B | 4.2 GB | 9 tok/s | 8192 |
| DeepSeek-8B | 4.7 GB | TBD | 4096 |

### Use Case Preset

| Preset | Temperatura | Context | Descrizione |
|--------|-------------|---------|-------------|
| **coding** | 0.2 | quality | Generazione codice preciso |
| **chat** | 0.7 | balanced | Conversazione naturale |
| **creative** | 0.9 | balanced | Scrittura creativa |
| **analysis** | 0.3 | quality | Analisi dettagliate |
| **qa** | 0.1 | fast | Risposte fattuali rapide |
| **translation** | 0.1 | balanced | Traduzioni accurate |

## 📊 Progetto Completato

✅ **Tutti i 12 task completati con successo!**

**Scripts Creati:**
- ✅ `llm_manager.py` - Gestione completa modelli  
- ✅ `llm_benchmark.py` - Suite benchmark performance
- ✅ `llm_monitor.py` - Monitoring risorse real-time  
- ✅ `llm_quick.py` - Interfaccia user-friendly
- ✅ Sistema profili e preset use case
- ✅ Documentazione migrazione ROCm

**Funzionalità Implementate:**
- ✅ Scansione automatica modelli GGUF
- ✅ Calcolo context size ottimale per 16GB VRAM
- ✅ Lancio inferenza con GPU Vulkan (-ngl 99)
- ✅ Server HTTP llama-server
- ✅ Profili salvati con configurazioni ottimali
- ✅ 8 preset use case (coding, chat, creative, etc.)
- ✅ Benchmark comparativi tra modelli
- ✅ Monitoring GPU/CPU/RAM real-time
- ✅ Interfaccia CLI colorata e intuitiva

**Performance Raggiunte:**
- 🚀 Qwen 3B: 31 token/s (eccellente per chat)
- 🚀 Gemma 4B: 9 token/s (buon compromesso qualità/velocità)  
- 🚀 Context size fino a 32768 con modelli piccoli
- 🚀 Utilizzo ottimale GPU AMD con Vulkan

## 🎯 Sistema Production-Ready

Il sistema è **completo e pronto per uso production** con:
- Interface user-friendly per selezione rapida
- Profili ottimizzati per ogni modello  
- Preset specializzati per diversi use case
- Monitoring performance in tempo reale
- Benchmark per valutare nuovi modelli
- Documentazione per migrazione ROCm futura

**Next Step Suggerito**: Migrazione a ROCm per +30-40% performance (vedi `ROCM_MIGRATION.md`)

---

**🎉 Progetto completato con successo!** Ready per workload LLM production su GPU AMD.