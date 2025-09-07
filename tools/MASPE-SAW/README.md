# MASPE-SAW (SEO Analytics Weekly)

Sistema professionale di automazione per l'analisi settimanale SEO/SEM di Maspe con integrazione **Claude Code** per analisi avanzate.

## 🎯 Panoramica

MASPE-SAW automatizza l'intero workflow di analisi SEO/SEM aziendale:
- **Estrazione automatica** dati da Google Analytics e Search Console
- **Analisi avanzata** con agenti Claude Code specializzati
- **Report professionali** HTML responsive con KPI e raccomandazioni
- **Scheduling automatico** settimanale

## 🏗️ Architettura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Google APIs   │ -> │  Python + R      │ -> │ Claude Agents   │
│ Analytics + SC  │    │  Orchestrator    │    │ Analysis + Rep. │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                  │
                       ┌──────────────────┐
                       │  Professional    │
                       │  HTML Reports    │
                       └──────────────────┘
```

### Componenti Principali
1. **Script R Automatizzato** → estrazione dati Google APIs
2. **Python Orchestrator** → coordinamento flusso completo
3. **Claude Code Agents** → analisi SEO/SEM professionale
4. **Report Generator** → output HTML visualmente accattivanti
5. **Scheduler** → esecuzione settimanale automatica

## 📦 Installazione

### Prerequisiti
- **Python 3.8+** con pip
- **R 4.0+** con librerie:
  - `googleAnalyticsR`
  - `searchConsoleR` 
  - `ggplot2`
  - `dplyr`
- **Credenziali Google Service Account** (file JSON)
- **Claude Code** (opzionale, per analisi avanzate)

### Setup Rapido
```bash
cd /opt/progetti/MASPE-SAW

# 1. Crea ambiente virtuale
python3 -m venv venv

# 2. Attiva ambiente
source activate.sh  # Script helper con comandi disponibili

# 3. Installa dipendenze Python
pip install -r requirements-minimal.txt

# 4. Test sistema
python orchestrator.py --mock
```

## 🚀 Utilizzo

### Modalità Base
```bash
# Attiva ambiente
source activate.sh

# Analisi con dati reali Google Analytics
python orchestrator.py --real

# Analisi con dati mock (test)
python orchestrator.py --mock

# Analisi ultime 2 settimane
python orchestrator.py --real --settimane 2

# Mantieni file temporanei per debug
python orchestrator.py --real --no-cleanup

# NUOVO: Genera prompt per analisi con LLM esterno
python orchestrator.py --real --generate-prompt
```

### Modalità Avanzata (con Claude Code)
```bash
# All'interno di Claude Code
python run_with_claude_agents.py --real

# Con dati mock per test
python run_with_claude_agents.py --mock
```

### Modalità Prompt per Analisi Manuale (NUOVO)
```bash
# Genera un prompt completo con tutti i dati per analisi con LLM
python orchestrator.py --real --generate-prompt

# Il comando crea un file: reports/analysis_prompt_YYYY-MM-DD_HH-MM.txt
# Puoi copiare il contenuto e incollarlo in:
# - Claude (claude.ai)
# - ChatGPT
# - Gemini
# - Qualsiasi altro LLM

# Esempio automatizzato con cron (ogni lunedì alle 8:00)
0 8 * * 1 cd /opt/progetti/MASPE-SAW && source venv/bin/activate && python orchestrator.py --real --generate-prompt
```

### Variabili Ambiente
```bash
# Forza modalità mock globalmente
export MASPE_USE_MOCK=true

# Livello logging
export MASPE_LOG_LEVEL=DEBUG
```

## 📊 Output e Report

### Report Generati
- **Path**: `reports/maspe_seo_report_YYYY-MM-DD.html`
- **Formato**: HTML responsive con CSS moderno
- **Contenuto**:
  - Dashboard KPI principali
  - Analisi trend traffico e conversioni
  - Performance campagne (ROI, CPA)
  - Insights SEO organico
  - Raccomandazioni prioritizzate
  - Tabelle dati dettagliate

### File Dati Temporanei
Durante l'esecuzione vengono creati in `/tmp/`:
- `maspe-dati.csv` - Metriche giornaliere utenti/conversioni
- `maspe-campagne.csv` - Performance campagne pubblicitarie  
- `maspe-pagine.csv` - Top pagine da Search Console
- `maspe-queries.csv` - Top query di ricerca
- `ts-maspe.jpg` - Grafico serie temporale traffico

### File Prompt Generato (NUOVO)
- **Path**: `reports/analysis_prompt_YYYY-MM-DD_HH-MM.txt`
- **Contenuto**: Prompt strutturato con tutti i dati del periodo
- **Uso**: Copia/incolla in qualsiasi LLM per analisi avanzata
- **Dimensione**: ~5-10 KB (dipende dal periodo analizzato)

## ⚙️ Configurazione

### Credenziali Google
```
File: /opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json
Property ID: 353989568 (Maspe GA4)
Sito: https://www.maspe.com
```

### File Configurazione
- `config.py` - Impostazioni principali
- `requirements-minimal.txt` - Dipendenze Python core
- `maspe-console-automated.r` - Script R automatizzato

## 🤖 Agenti Claude Code

### Agenti Disponibili
1. **data-analysis-expert** 
   - Analisi statistica avanzata
   - Identificazione trend e anomalie
   - Calcolo KPI e performance metrics

2. **seo-sem-report-expert**
   - Generazione report professionali
   - Visualizzazioni e dashboard
   - Raccomandazioni strategiche

### File Agenti
```
/opt/progetti/MASPE-SAW/.claude/agents/
├── data-analysis-expert.md
└── seo-sem-report-expert.md
```

## 🔧 Automazione

### Scheduling Settimanale
```bash
# Aggiungi a crontab per esecuzione ogni lunedì alle 8:00
crontab -e

# Aggiungi questa riga:
0 8 * * 1 cd /opt/progetti/MASPE-SAW && source venv/bin/activate && python orchestrator.py --real
```

### Notifiche Email (opzionale)
```bash
# Con notifica email in caso di successo/errore
0 8 * * 1 cd /opt/progetti/MASPE-SAW && source venv/bin/activate && python orchestrator.py --real && echo "Report SEO generato con successo" | mail -s "MASPE-SAW Success" admin@maspe.com
```

## 🧪 Test e Debug

### Test Completo Sistema
```bash
# Test con dati mock
python orchestrator.py --mock

# Test connessione Google Analytics
python orchestrator.py --real --settimane 1

# Test integrazione Claude Code
python run_with_claude_agents.py --mock
```

### Debug e Troubleshooting
```bash
# Esecuzione con log dettagliati
MASPE_LOG_LEVEL=DEBUG python orchestrator.py --real --no-cleanup

# Controllo file generati
ls -la /tmp/maspe-*.csv

# Verifica autenticazione Google
Rscript maspe-console-automated.r 2025-07-19 2025-07-26
```

## 📁 Struttura Progetto

```
MASPE-SAW/
├── README.md                     # Documentazione principale
├── come-usare.md                 # Guida utilizzo rapido
├── requirements-minimal.txt      # Dipendenze Python
├── config.py                     # Configurazione sistema
├── orchestrator.py               # Orchestratore principale
├── claude_integration.py         # Integrazione agenti Claude
├── agent_wrapper.py              # Wrapper agenti
├── maspe-console-automated.r     # Script R automatizzato
├── generate_mock_data.py         # Generatore dati test
├── run_with_claude_agents.py     # Runner con agenti Claude
├── prompt_generator.py           # Generatore prompt per LLM
├── activate.sh                   # Script attivazione ambiente
├── .claude/                      # Agenti Claude Code
│   └── agents/
│       ├── data-analysis-expert.md
│       └── seo-sem-report-expert.md
├── venv/                         # Ambiente virtuale Python
└── reports/                      # Report generati
    └── maspe_seo_report_*.html
```

## 🔒 Sicurezza

- **Credenziali**: File service account Google protetti
- **API Keys**: Non committiamo mai credenziali nel repository
- **Accessi**: Solo lettura sui dati Google Analytics/Search Console
- **File temporanei**: Pulizia automatica dopo elaborazione

## 🆘 Troubleshooting

### Errori Comuni

**Errore autenticazione Google:**
```bash
# Verifica esistenza file credenziali
ls -la /opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json

# Test autenticazione R
Rscript -e "library(googleAnalyticsR); ga_auth(json_file='/path/to/file.json')"
```

**Ambiente virtuale non attivo:**
```bash
# Verifica ambiente attivo
which python
# Dovrebbe mostrare: /opt/progetti/MASPE-SAW/venv/bin/python

# Riattiva se necessario
source venv/bin/activate
```

**Dipendenze R mancanti:**
```bash
# Installa librerie R necessarie
Rscript -e "install.packages(c('googleAnalyticsR', 'searchConsoleR', 'ggplot2', 'dplyr'))"
```

## 🔄 Aggiornamenti

### Versioning
- **v1.0** - Sistema base con estrazione dati
- **v2.0** - Integrazione agenti Claude Code  
- **v2.1** - Report HTML avanzati
- **v2.2** - Generazione prompt per analisi LLM (attuale)

### Roadmap Futura
- [ ] Integrazione Search Console completa
- [ ] Dashboard web interattiva
- [ ] Alerting automatico anomalie
- [ ] Confronti competitor
- [ ] Previsioni AI/ML

## 👥 Contributi

Per modifiche e miglioramenti:
1. Testare sempre con `--mock` prima di dati reali
2. Aggiornare documentazione se necessario
3. Seguire convenzioni di naming esistenti

## 📄 Licenza

Uso interno Maspe - Sistema proprietario di analisi SEO/SEM

---

🤖 **Generato con Claude Code** | 🏢 **Sistema MASPE-SAW** | 📊 **SEO Analytics Weekly**