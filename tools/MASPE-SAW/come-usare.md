# 🚀 Come Usare MASPE-SAW

Guida rapida per l'utilizzo del sistema di analisi SEO/SEM automatizzato.

## ⚡ Quick Start (5 minuti)

```bash
# 1. Vai nella directory del progetto
cd /opt/progetti/MASPE-SAW

# 2. Attiva l'ambiente virtuale
source activate.sh

# 3. Esegui analisi con dati reali
python orchestrator.py --real

# 4. Apri il report generato
firefox reports/maspe_seo_report_$(date +%Y-%m-%d).html
```

## 📋 Comandi Principali

### Analisi Base
```bash
# Analisi ultima settimana con dati reali
python orchestrator.py --real

# Analisi con dati di test
python orchestrator.py --mock

# Analisi ultime 2 settimane  
python orchestrator.py --real --settimane 2
```

### Analisi Avanzata (con Claude Code)
```bash
# All'interno di Claude Code per analisi complete
python run_with_claude_agents.py --real

# Test con dati mock
python run_with_claude_agents.py --mock
```

### Test e Debug
```bash
# Test completo del sistema
python orchestrator.py --mock

# Test connessione Google Analytics
python orchestrator.py --real

# Mantieni file temporanei per debug
python orchestrator.py --real --no-cleanup
```

## 📊 Output

### Report HTML
- **Posizione**: `reports/maspe_seo_report_YYYY-MM-DD.html`
- **Contenuto**: KPI, trend, performance campagne, raccomandazioni SEO

### File Dati (temporanei in /tmp/)
- `maspe-dati.csv` - Dati giornalieri utenti/conversioni
- `maspe-campagne.csv` - Performance campagne  
- `maspe-pagine.csv` - Top pagine Search Console
- `maspe-queries.csv` - Top query di ricerca

## 🔧 Opzioni Avanzate

### Variabili Ambiente
```bash
# Modalità mock di default
export MASPE_USE_MOCK=true

# Log dettagliati
export MASPE_LOG_LEVEL=DEBUG
```

### Parametri Comando
```bash
# Aiuto completo
python orchestrator.py --help

# Opzioni principali:
--real           # Usa dati reali Google Analytics
--mock           # Usa dati di test
--settimane N    # Analizza N settimane precedenti
--no-cleanup     # Mantieni file temporanei
--output-dir DIR # Directory output custom
```

## ⏰ Automazione Settimanale

### Setup Cron (esecuzione automatica)
```bash
# Modifica crontab
crontab -e

# Aggiungi per esecuzione ogni lunedì alle 8:00
0 8 * * 1 cd /opt/progetti/MASPE-SAW && source venv/bin/activate && python orchestrator.py --real
```

### Con Notifiche Email
```bash
# Cron con email di notifica
0 8 * * 1 cd /opt/progetti/MASPE-SAW && source venv/bin/activate && python orchestrator.py --real && echo "Report SEO Maspe generato" | mail -s "MASPE-SAW Weekly Report" admin@maspe.com
```

## 🆘 Risoluzione Problemi

### Problemi Comuni

**❌ "R non trovato"**
```bash
# Verifica installazione R
which R
Rscript --version

# Installa se mancante (Debian/Ubuntu)
sudo apt install r-base
```

**❌ "Ambiente virtuale non attivo"**
```bash
# Verifica ambiente attivo
which python
# Dovrebbe mostrare: /opt/progetti/MASPE-SAW/venv/bin/python

# Riattiva
source venv/bin/activate
```

**❌ "Errore autenticazione Google"**
```bash
# Verifica file credenziali
ls -la /opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json

# Test autenticazione diretta
Rscript maspe-console-automated.r 2025-07-19 2025-07-26
```

**❌ "Dipendenze Python mancanti"**
```bash
# Reinstalla dipendenze
pip install -r requirements-minimal.txt
```

**❌ "Librerie R mancanti"**
```bash
# Installa librerie R necessarie
Rscript -e "install.packages(c('googleAnalyticsR', 'searchConsoleR', 'ggplot2', 'dplyr'))"
```

### Log e Debug
```bash
# Esecuzione con log dettagliati
MASPE_LOG_LEVEL=DEBUG python orchestrator.py --real --no-cleanup

# Controlla log file
tail -f maspe_seo_analysis.log

# Verifica file generati
ls -la /tmp/maspe-*.csv reports/
```

## 📱 Modalità di Utilizzo

### 🔄 Uso Regolare (Settimanale)
```bash
# Lunedì mattina - Analisi settimana precedente
cd /opt/progetti/MASPE-SAW
source activate.sh
python orchestrator.py --real
```

### 🧪 Test e Sviluppo
```bash
# Test con dati mock
python orchestrator.py --mock --no-cleanup

# Test sistema completo
python orchestrator.py --mock
```

### 📊 Analisi Ad-hoc
```bash
# Analisi periodo custom (ultime 4 settimane)
python orchestrator.py --real --settimane 4

# Con Claude Code per insights avanzati
python run_with_claude_agents.py --real --settimane 2
```

### 🔍 Debug e Maintenance
```bash
# Debug completo con file mantenuti
MASPE_LOG_LEVEL=DEBUG python orchestrator.py --real --no-cleanup

# Test solo estrazione dati
python orchestrator.py --real --no-cleanup

# Pulizia manuale file temporanei
rm /tmp/maspe-*.csv /tmp/maspe-*.jpg
```

## ✅ Checklist Pre-Esecuzione

Prima di ogni analisi verifica:

- [ ] **Ambiente attivo**: `source activate.sh` eseguito
- [ ] **Credenziali Google**: File JSON esistente e accessibile
- [ ] **Connessione internet**: Per accesso Google APIs
- [ ] **Spazio disco**: Almeno 100MB liberi in `/tmp/` e `reports/`
- [ ] **Dipendenze R**: Librerie Google Analytics installate

## 📈 Interpretazione Report

### KPI Dashboard
- **Utenti Totali**: Traffico complessivo del periodo
- **Media/Giorno**: Performance giornaliera media
- **Conversioni**: Moduli/obiettivi completati
- **Costo Campagne**: Investimento pubblicitario totale

### Sezioni Report
1. **🎯 KPI Principali** - Metriche chiave periodo
2. **🔍 Stato Analisi** - Modalità esecuzione e agenti utilizzati
3. **📁 File Elaborati** - Status elaborazione dati
4. **🚀 Prossimi Passi** - Raccomandazioni e azioni

### Modalità Agenti
- **🟢 Success**: Agenti Claude Code eseguiti correttamente
- **🟠 Simulated**: Analisi base senza agenti avanzati
- **🔴 Error**: Problemi nell'esecuzione

---

## 🎯 Tips Utili

1. **Prima esecuzione**: Usa sempre `--mock` per test
2. **Debug**: Aggiungi `--no-cleanup` per esaminare file generati
3. **Performance**: I report sono più dettagliati con Claude Code
4. **Automazione**: Configura cron per esecuzione regolare
5. **Backup**: Salva report importanti in location sicura

---

💡 **Per supporto tecnico o domande**: Consulta il `README.md` completo o i file di log del sistema.