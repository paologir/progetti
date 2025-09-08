# Clienti CRM

Un sistema CRM completo per consulenti di digital marketing, progettato per gestire clienti, time tracking, todo e fatturazione in modo efficiente e professionale.

## 🚀 Caratteristiche Principali

### 💼 Gestione Clienti Completa
- **Database SQLite locale** per privacy e controllo totale
- **Profili cliente completi** con dati anagrafici, contatti, tariffe personalizzate
- **Sistema di tags** per categorizzazione e filtri avanzati
- **Stati cliente** (attivo/prospect/pausa) per workflow organizzati
- **Timeline attività** con storico completo interventi

### ⏱️ Time Tracking Professionale
- **Timer preciso** con persistenza attraverso riavvii
- **Calcolo compensi automatico** basato su tariffe personalizzate
- **Sessioni multiple** per progetti complessi
- **Report dettagliati** per periodo, cliente, progetto
- **Export timesheet** in CSV per fatturazione

### ✅ Todo Management
- **Todo collegati ai clienti** per non perdere nessun task
- **Priorità e scadenze** con alert automatici
- **Stati avanzati** (aperto/in corso/completato/posticipato)
- **Filtri multipli** per gestione efficiente
- **Dashboard priorità** con focus sui task urgenti

### 💰 Gestione Pagamenti e Fatturazione
- **Pagamenti ricorrenti** mensili/trimestrali/annuali automatici
- **Alert proattivi** per scadenze imminenti e pagamenti overdue
- **Dati pronti per AdE/Microfatture** con calcoli automatici
- **Tracking compensi non fatturati** per controllo cash flow
- **Gestione completa workflow** da emissione a pagamento
- **Eliminazione sicura** con conferma e dettagli

### 🌐 Interfaccia Web Moderna
- **Dashboard responsiva** con KPI in tempo reale  
- **Interfaccia mobile-friendly** per gestione ovunque
- **Timer web** con aggiornamenti live
- **Gestione todo** tramite browser
- **API REST** per integrazioni future

### 📊 Export e Backup
- **Export Obsidian** completo con template personalizzati
- **Backup automatici** configurabili
- **Export CSV** per analisi esterne
- **Sincronizzazione dati** tra CLI e web

## 🛠️ Installazione Rapida

### Prerequisiti
- Python 3.11 o superiore
- Git (per clonazione repository)
- Sistema operativo: Linux, macOS, Windows

### Setup Automatico

```bash
# 1. Clona il repository
git clone https://github.com/paologir/progetti.git
cd progetti/clienti

# 2. Esegui lo script di installazione
chmod +x install.sh
./install.sh

# 3. Il sistema è pronto!
clienti --help
```

### Setup Manuale

```bash
# 1. Crea ambiente virtuale
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\\Scripts\\activate     # Windows

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Inizializza database
python clienti.py init

# 4. Test installazione
python clienti.py --help

# 5. (Opzionale) Crea alias permanente
echo 'alias clienti="/path/to/clienti/venv/bin/python /path/to/clienti/clienti.py"' >> ~/.bashrc
source ~/.bashrc
```

## 📖 Guida Rapida

### Primo Avvio
```bash
# Inizializza il sistema
clienti init

# Aggiungi il primo cliente
clienti client add

# Visualizza dashboard
clienti dashboard

# Avvia server web (opzionale)
clienti serve --port 8080
```

### Workflow Tipico Giornaliero

```bash
# 1. Controlla priorità del giorno
clienti alerts                    # Alert urgent tasks/scadenze
clienti todo oggi                 # Todo con scadenza oggi

# 2. Avvia timer per lavoro cliente
clienti time start "Cliente ABC" --task "Ottimizzazione campagne Google Ads"

# 3. Durante il lavoro
clienti time status               # Verifica tempo e compenso corrente

# 4. Registra interventi/chiamate
clienti log add                   # Wizard per registrare intervento

# 5. Chiudi timer
clienti time stop

# 6. Gestisci todo
clienti todo add                  # Nuovo task
clienti todo done 12              # Completa task #12

# 7. Review giornaliera
clienti log oggi                  # Riassunto attività giornata
clienti time today                # Ore e compensi giornata
```

### Gestione Cliente Completa

```bash
# Visualizzazione e ricerca
clienti client list                        # Tutti i clienti
clienti client list --attivi              # Solo attivi
clienti client list --tag "ecommerce"     # Filtra per tag
clienti client show "Maspe Srl"           # Dettagli completi cliente

# Modifica (via wizard)
clienti client add                         # Nuovo cliente wizard completo
clienti client edit "Nome Cliente"        # Modifica dati esistenti

# Gestione contatti
clienti contact add "Cliente"             # Aggiungi contatto
clienti contact list "Cliente"            # Lista contatti cliente
```

### Time Tracking Avanzato

```bash
# Timer base
clienti time start "Cliente" --task "Descrizione lavoro"
clienti time status                       # Stato corrente
clienti time stop                         # Ferma e salva

# Report e analisi
clienti time today                        # Report giornaliero
clienti time week                         # Report settimanale
clienti time month                        # Report mensile
clienti time report --cliente "Nome"     # Report specifico cliente
clienti time unfiled                      # Ore non ancora fatturate

# Export per fatturazione
clienti time export csv --month 9        # Timesheet CSV del mese
clienti time export --cliente "Nome"     # Export specifico cliente
```

### Todo Management Efficace

```bash
# Creazione e gestione
clienti todo add                          # Wizard completo nuovo todo
clienti todo list                         # Tutti i todo aperti
clienti todo list --overdue               # Solo quelli in ritardo
clienti todo list --cliente "Nome"       # Todo per cliente specifico
clienti todo list --priorita alta        # Alta priorità

# Filtraggio avanzato
clienti todo oggi                         # Scadenza oggi
clienti todo settimana                    # Scadenze settimana
clienti todo cliente "Cliente"           # Todo specifici cliente

# Gestione stati
clienti todo done 15                      # Completa todo #15
clienti todo edit 10 --priorita alta     # Modifica priorità
clienti todo delete 12                    # Elimina todo
```

### Pagamenti e Fatturazione

```bash
# Visualizzazione pagamenti
clienti pagamenti prossimi                # Prossimi 7 giorni
clienti pagamenti list                    # Tutti i pagamenti
clienti pagamenti list --overdue          # Solo pagamenti scaduti
clienti pagamenti list --pending          # Solo da emettere
clienti pagamenti list --cliente "Nome"   # Filtra per cliente

# Gestione pagamenti
clienti pagamenti add "Cliente"           # Nuovo pagamento wizard
clienti pagamenti dettaglio "Cliente"     # Dati per fatturazione
clienti pagamenti emessa 5 --numero "2024-001" --data oggi
clienti pagamenti pagata 5 --data oggi
clienti pagamenti delete 12               # Elimina pagamento

# Esempio output dettaglio per fatturazione:
# ━━━ DATI PER MICROFATTURE/ADE ━━━
# Cliente: Maspe Srl  
# P.IVA: 1777400241
# Prestazioni periodo: €500 + rivalsa 4% = €520 totale
# [Dati copiati in clipboard per incolla facile]
```

### Dashboard e Report

```bash
# Dashboard principale con overview completa
clienti dashboard                         # Dashboard ricco con statistiche

# Statistiche dettagliate
clienti stats                             # Mese corrente
clienti stats --month 9 --year 2025      # Periodo specifico
clienti report month                      # Report mensile con grafici ASCII
clienti alerts                           # Alert e promemoria importanti

# Esempio output dashboard:
# 📊 Dashboard CRM Avanzato
# ╭─ 👥 Clienti ─╮ ╭── 💰 Fatturato ───╮ ╭─── ⏱️ Ore ───╮ 
# │ 54 attivi    │ │ €8,245 mese      │ │ 165h mese   │
# │ 100% attivi  │ │ €1,200 da fattur │ │ 890h totali │
# ╰──────────────╯ ╰──────────────────╯ ╰─────────────╯
```

### Export e Backup

```bash
# Backup automatici (configurati)
clienti backup create                     # Backup manuale
clienti backup list                       # Lista backup esistenti
clienti backup restore backup_file.db     # Ripristina backup
clienti backup cleanup                     # Pulizia backup vecchi

# Export Obsidian completo
clienti export obsidian /path/to/vault    # Export completo vault
clienti export client "Cliente" --output file.md  # Export singolo cliente

# Export CSV per analisi
clienti export csv /path/to/export.csv    # Tutti i clienti
clienti export csv --attivi-only          # Solo clienti attivi

# Import da sistemi esterni
clienti import clienti.json               # Import da JSON esistente
clienti export import-csv file.csv --dry-run  # Preview import CSV
```

## 🔧 Configurazione

Il sistema utilizza un file `config.toml` per tutte le configurazioni:

```toml
[app]
name = "Clienti CRM"
version = "1.0.0"

[server]
host = "127.0.0.1"
port = 8080
debug = false

[business]
default_hourly_rate = 50.0
rivalsa_percentage = 4.0
currency_symbol = "€"

[backup]
auto_enabled = true
auto_interval_hours = 24
max_backups = 30

[logging]
level = "INFO"
file = "logs/clienti.log"
web_enabled = true
timer_enabled = true
```

### Override con Environment Variables

```bash
# Cambia porta server
export CLIENTI_SERVER_PORT=9000

# Cambia tariffa oraria default
export CLIENTI_BUSINESS_DEFAULT_HOURLY_RATE=60.0

# Disabilita backup automatici
export CLIENTI_BACKUP_AUTO_ENABLED=false
```

## 🌐 Interfaccia Web

Avvia il server web per accedere all'interfaccia moderna:

```bash
# Avvio server
clienti serve                            # Default: http://127.0.0.1:8080  
clienti serve --host 0.0.0.0 --port 9000 # Personalizzato

# Funzionalità web disponibili:
# • Dashboard con KPI real-time
# • Timer con aggiornamenti live
# • Gestione todo completa
# • Gestione pagamenti completa
# • Visualizzazione clienti
# • Report e statistiche
```

### Funzionalità Web vs CLI

| Funzione | Web | CLI |
|----------|-----|-----|
| Dashboard | ✅ Completa | ✅ Avanzata |
| Timer | ✅ Live updates | ✅ Completo |
| Clienti | ✅ View only | ✅ CRUD completo |
| Todo | ✅ Add/Complete | ✅ CRUD + filtri |
| Pagamenti | ✅ CRUD + filtri | ✅ CRUD + avanzati |
| Report | ✅ Basic | ✅ Avanzati |
| Export | ❌ | ✅ Completi |
| Configurazione | ❌ | ✅ Completa |

## 📱 Utilizzo Mobile

L'interfaccia web è ottimizzata per mobile:

- **Design responsivo** per smartphone e tablet
- **Touch-friendly** per timer e todo
- **Offline capability** per dati critici (future)
- **PWA support** per installazione come app (future)

## 🔒 Sicurezza e Privacy

- **Database SQLite locale** - nessun dato in cloud
- **Backup criptati** opzionali (configurabili)
- **Logging sicuro** per audit trail
- **No telemetria** o tracking
- **Controllo completo** dei propri dati

## 🔧 Troubleshooting

### Problemi Comuni

**Timer non si avvia:**
```bash
# Controlla se c'è già un timer attivo
clienti time status

# Se necessario, ferma il timer precedente
clienti time stop
```

**Database corrotto:**
```bash
# Ripristina da backup
clienti backup list
clienti backup restore backup_file.db

# Se non ci sono backup, reinizializza
mv database.db database.db.backup
clienti init
```

**Server web non si avvia:**
```bash
# Controlla se la porta è occupata
netstat -tlnp | grep 8080

# Usa porta diversa
clienti serve --port 9000

# Controlla log per errori dettagliati
tail -f logs/clienti.log
```

**Export Obsidian fallisce:**
```bash
# Verifica permessi directory
ls -la /path/to/export/

# Usa directory con permessi completi
clienti export obsidian ~/Documents/ObsidianVault
```

### Log e Debugging

```bash
# Log file principale
tail -f logs/clienti.log

# Debugging mode
export CLIENTI_LOGGING_LEVEL=DEBUG
clienti dashboard

# Controllo integrità database
sqlite3 database.db "PRAGMA integrity_check;"
```

## 🛣️ Roadmap

### Versione 1.0 (Attuale)
- ✅ Gestione clienti completa
- ✅ Time tracking preciso
- ✅ Todo management
- ✅ Interfacce CLI e Web
- ✅ Export Obsidian/CSV
- ✅ Backup automatici
- ✅ Configurazione esterna
- ✅ Logging completo

### Versione 1.1 (Pianificata)
- [ ] API REST pubblica
- [ ] Plugin Obsidian nativi
- [ ] Integrazione email/calendario
- [ ] App mobile PWA
- [ ] Multi-utente con autenticazione
- [ ] Dashboard analytics avanzate

### Versione 2.0 (Futuro)
- [ ] Cloud sync opzionale
- [ ] Integrazione CRM esterni (HubSpot, etc.)
- [ ] AI per categorizzazione automatica
- [ ] Reporting PDF avanzato
- [ ] Workflow automation

## 🤝 Contributi

Il progetto è attualmente in sviluppo attivo. Per contributi:

1. Fork del repository
2. Branch per feature: `git checkout -b feature/nuova-funzionalita`
3. Commit delle modifiche: `git commit -am 'Aggiunge nuova funzionalità'`
4. Push al branch: `git push origin feature/nuova-funzionalita`
5. Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi file `LICENSE` per dettagli.

## 🆘 Supporto

- **Issues**: [GitHub Issues](https://github.com/paologir/progetti/issues)
- **Documentazione**: Questo README + `clienti --help`
- **Wiki**: [GitHub Wiki](https://github.com/paologir/progetti/wiki) (future)

## 🙏 Riconoscimenti

Costruito con:
- **FastAPI** per web interface moderna
- **Typer + Rich** per CLI professionale
- **SQLAlchemy** per database robusto
- **Pico.css** per UI minimale e responsive

---

**Sviluppato con ❤️ per consulenti digital marketing che vogliono focus sui clienti, non sulla burocrazia.**