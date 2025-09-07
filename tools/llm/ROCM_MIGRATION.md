# Migrazione a ROCm per Performance Migliori

Questa guida descrive come migrare da Vulkan a ROCm per ottenere performance migliori con la GPU AMD 780M.

## Stato Attuale

- **GPU**: AMD 780M con 16GB VRAM allocata
- **Backend**: Vulkan (funzionante ma non ottimale)
- **Performance**: ~31 token/s con Qwen 3B, ~9 token/s con Gemma 4B
- **Sistema**: Debian 12

## Vantaggi ROCm vs Vulkan

| Aspetto | Vulkan | ROCm |
|---------|---------|------|
| Compatibilità | Universale | AMD nativo |
| Performance | Buona | Eccellente |
| Memoria | Efficiente | Più efficiente |
| Debugging | Limitato | Completo |
| Ottimizzazioni | Generiche | GPU-specific |

**Performance attese con ROCm**: +20-40% token/s

## Prerequisiti

### Hardware Supportato
- ✅ AMD 780M (RDNA 3) - **Supportata**
- ✅ 64GB RAM di sistema
- ✅ Driver AMDGPU kernel attivi

### Verifica Supporto Hardware
```bash
# Verifica GPU
lspci | grep -E "(VGA|3D)"

# Verifica driver
lsmod | grep amdgpu

# Info dettagliate GPU
sudo dmesg | grep -i amdgpu
```

## Installazione ROCm su Debian 12

### 1. Preparazione Sistema

```bash
# Update sistema
sudo apt update && sudo apt upgrade -y

# Installa dipendenze
sudo apt install -y \
    wget \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl

# Aggiungi utente ai gruppi necessari
sudo usermod -a -G render,video $USER
```

### 2. Repository ROCm

```bash
# Download chiave GPG
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -

# Aggiungi repository (ROCm 6.0+)
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.0.2 jammy main' | \
    sudo tee /etc/apt/sources.list.d/rocm.list

# Update package list
sudo apt update
```

### 3. Installazione Pacchetti ROCm

```bash
# Pacchetti base ROCm
sudo apt install -y \
    rocm-dev \
    rocm-libs \
    rocm-utils \
    rocminfo \
    rocm-smi \
    hip-dev \
    hip-runtime-amd

# Tools aggiuntivi
sudo apt install -y \
    rccl-dev \
    rocblas-dev \
    rocfft-dev \
    rocsparse-dev \
    rocrand-dev
```

### 4. Configurazione Sistema

```bash
# Aggiungi ROCm al PATH
echo 'export PATH=$PATH:/opt/rocm/bin' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/rocm/lib' >> ~/.bashrc

# Ricarica configurazione
source ~/.bashrc

# Configura limiti memoria
echo '@rocm-dev        hard    memlock        unlimited' | sudo tee -a /etc/security/limits.conf
echo '@rocm-dev        soft    memlock        unlimited' | sudo tee -a /etc/security/limits.conf
```

### 5. Verifica Installazione

```bash
# Info sistema ROCm
rocminfo

# Lista GPU disponibili
rocm-smi

# Test HIP
/opt/rocm/bin/hipcc --version

# Test performance
rocm-bandwidth-test
```

## Compilazione llama.cpp con ROCm

### 1. Preparazione Build

```bash
cd ~/llama.cpp

# Backup build Vulkan esistente
mv build build_vulkan_backup

# Pulisci cache CMake
rm -rf CMakeCache.txt CMakeFiles/
```

### 2. Configurazione CMake ROCm

```bash
# Crea directory build
mkdir build && cd build

# Configura con ROCm
cmake .. \
    -DLLAMA_HIPBLAS=ON \
    -DLLAMA_AVX2=ON \
    -DLLAMA_AVX512=ON \
    -DLLAMA_FMA=ON \
    -DLLAMA_F16C=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_HIP_ARCHITECTURES="gfx1103" \
    -DAMDGPU_TARGETS="gfx1103" \
    -DGPU_TARGETS="gfx1103"
```

**Nota**: `gfx1103` è l'architettura per AMD 780M (RDNA 3)

### 3. Compilazione

```bash
# Build con tutti i core
make -j$(nproc)

# Verifica build
ls -la bin/
```

### 4. Test Funzionalità

```bash
# Test modello piccolo
./bin/llama-cli \
    -m /opt/llm/Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf \
    -p "Test ROCm" \
    -n 10 \
    -ngl 99

# Verifica utilizzo GPU
rocm-smi
```

## Aggiornamento Scripts

### 1. Modifica llm_manager.py

```python
# In __init__
self.use_rocm = True  # Invece di use_vulkan
self.gpu_backend = "rocm"  # Per logging

# Nel build comando
if self.use_rocm:
    cmd.extend(["-ngl", str(self.gpu_layers)])
else:
    cmd.extend(["-ngl", str(self.gpu_layers)])
```

### 2. Aggiornamento Monitoring

```bash
# Aggiungi to llm_monitor.py
def get_rocm_stats(self):
    """Monitor GPU con rocm-smi"""
    try:
        result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram', '--json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Parse JSON rocm-smi
            return data
    except:
        pass
    return {}
```

## Performance Tuning ROCm

### 1. Variabili Ambiente Ottimizzate

```bash
# Aggiungi a ~/.bashrc
export HSA_OVERRIDE_GFX_VERSION=11.0.3
export HIP_VISIBLE_DEVICES=0
export ROC_ENABLE_PRE_VEGA=1
export AMD_LOG_LEVEL=1

# Per debugging (opzionale)
export HIP_LAUNCH_BLOCKING=1
export ROCBLAS_LAYER=1
```

### 2. Ottimizzazioni Memoria

```bash
# Configurazione GPU memory
echo 'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash amdgpu.gartsize=512"' | \
    sudo tee -a /etc/default/grub

# Update GRUB
sudo update-grub
```

### 3. Governor CPU

```bash
# Performance mode per CPU durante inferenza
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

## Benchmark Performance

### Test Comparativo Post-Migrazione

```bash
# Benchmark con ROCm
./llm_benchmark.py compare \
    Qwen2.5-Coder-3B \
    gemma-3n \
    deepseek-ai > benchmark_rocm.txt

# Confronta con risultati Vulkan precedenti
./llm_benchmark.py results --last 20
```

### Performance Attese

| Modello | Vulkan (attuale) | ROCm (atteso) | Miglioramento |
|---------|------------------|---------------|---------------|
| Qwen 3B | ~31 tok/s | ~40-45 tok/s | +30-45% |
| Gemma 4B | ~9 tok/s | ~12-15 tok/s | +35-65% |

## Troubleshooting

### Problemi Comuni

1. **GPU non rilevata**
   ```bash
   # Verifica driver
   sudo dmesg | grep amdgpu
   rocminfo | grep "Agent 1"
   ```

2. **Errori di memoria**
   ```bash
   # Aumenta limite memory lock
   ulimit -l unlimited
   ```

3. **Performance basse**
   ```bash
   # Verifica frequencies
   rocm-smi --showclocks
   
   # Forza performance mode
   echo high | sudo tee /sys/class/drm/card0/device/power_dpm_force_performance_level
   ```

### Logs Utili

```bash
# ROCm debug log
export AMD_LOG_LEVEL=4
export HIP_PRINT_ENV=1

# llama.cpp debug
export GGML_DEBUG=1
```

## Rollback a Vulkan

Se ROCm causa problemi:

```bash
cd ~/llama.cpp

# Rimuovi build ROCm
rm -rf build

# Ripristina build Vulkan
mv build_vulkan_backup build

# Test funzionalità
./build/bin/llama-cli --help
```

## Stato Migrazione - Aggiornamento (2025-07-11)

### ✅ Completato
- **Hardware**: AMD 780M (gfx1103) rilevata e supportata
- **ROCm 6.0.2**: Installazione parziale completata
- **Monitoring**: ROCm SMI funzionante con 16GB VRAM, temperatura e potenza
- **Python Scripts**: llm_monitor.py aggiornato con supporto ROCm completo

### ⚠️ Problemi Identificati
- **llama.cpp HIP Build**: Errore di compatibilità `__hmax` non trovato
- **Conflitti Package**: ROCm 6.0.2 packages hanno conflitti con versioni esistenti
- **Compilazione**: GPU backend non funziona, CPU performance degradate

### 🔧 Workaround Attuale
- **Vulkan**: Manteniamo il backend Vulkan funzionante (31 tok/s Qwen3B)
- **ROCm Monitoring**: Disponibile via rocm-smi per analisi
- **Hybrid Setup**: Vulkan per inferenza + ROCm per monitoring/debug

### 📋 Prossimi Passi
1. **llama.cpp Fix**: Attendere patch per compatibilità HIP/__hmax
2. **Alternative**: Valutare llama.cpp fork con ROCm support
3. **Performance**: Test comparativi Vulkan vs possibili soluzioni ROCm

## Cronologia Aggiornamenti

- **v1.0** (2025-07-11): Documentazione iniziale migrazione ROCm
- **v1.1** (2025-07-11): Migrazione parziale completata - ROCm monitoring funzionante

## Note Performance Finali

**ROCm è raccomandato per**:
- Workload production intensive
- Development con debug GPU
- Performance massime

**Vulkan rimane valido per**:
- Setup rapidi
- Compatibility testing
- Sistemi mixed-vendor

---

**⚠️ Importante**: Esegui backup completo prima della migrazione e testa su modelli piccoli prima di usare modelli production.