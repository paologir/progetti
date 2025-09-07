# 📊 Progetto Clienti - CRM Consulente Digital Marketing

## 🎯 Overview

Sistema di gestione clienti minimalista per consulente digital marketing freelance. Interfaccia CLI-first con supporto web per gestire anagrafiche, time tracking, scadenze fatturazione e todo list.

### 📊 Stato Attuale (7 settembre 2025)

**✅ SPRINT 1 COMPLETATO** - Sistema base funzionante:
- 🗄️ Database SQLite inizializzato con 54 clienti importati
- 🖥️ CLI completa con comandi `clienti`, `clienti client list/add/show`
- 📊 Dashboard principale accessibile con `clienti`
- 🔍 Ricerca e filtri clienti operativi
- 💾 Sistema backup e import/export funzionante

**✅ SPRINT 2 COMPLETATO** - Time Tracking operativo:
- ⏱️ Timer start/stop con persistence
- 📊 Report ore giornalieri/settimanali per cliente
- 💰 Calcolo automatico compensi e tariffe
- 📋 Export CSV completo con filtri
- 🎯 Sistema robusto con 8 comandi funzionali

**✅ SPRINT 3 COMPLETATO** - Scadenze Fatturazione avanzate:
- 💰 Sistema ricorrenze complete (mensile→annuale)
- 📋 Gestione stati workflow (pending→emessa→pagata)
- 🔄 Importi fissi E variabili per massima flessibilità
- 📊 Integrazione automatica ore time tracking
- 📄 Dati ready-to-copy per Microfatture/AdE
- 🎯 Sistema completo con 8 comandi + importi variabili

**✅ SPRINT 4 COMPLETATO** - Todo & Interventi operativi:
- 📋 Sistema Todo completo con 8 comandi CRUD
- 🎯 Priorità (alta/normale/bassa) e scadenze con alert overdue
- 👤 Associazione opzionale todo→cliente con filtri avanzati
- 📝 Log interventi con 6 comandi (call/email/meeting/lavoro/altro)
- ⏱️ Tracking durata e costi per fatturazione
- 📊 Timeline cronologica per cliente + export CSV
- 🎯 Sistema completo con tutti i comandi integrati nel dashboard

**✅ SPRINT 5 COMPLETATO** - Dashboard CLI avanzato:
- 📊 Dashboard avanzato con layout Rich professionale
- 📈 Statistiche dettagliate per periodo con breakdown clienti
- 📋 Report mensili/annuali con grafici ASCII
- 🚨 Sistema alert per todo/scadenze overdue + promemoria
- 🎯 KPI e progress bars verso obiettivi mensili
- 📊 4 nuovi comandi: stats, report, alerts, dashboard avanzato

**⏳ PROSSIMO**: Sprint 6 - Web Interface

### 🖥️ Comandi Attualmente Disponibili

```bash
# Dashboard e informazioni (✅ NUOVO Sprint 5)
clienti                          # Dashboard avanzato con Rich layout
clienti --help                   # Guida completa  
clienti version                  # Informazioni versione
clienti info                     # Statistiche database
clienti dashboard               # Dashboard avanzato con KPI e alert
clienti stats                   # Statistiche dettagliate per periodo
clienti stats --year 2025 --month 9 --detailed  # Stats con breakdown clienti
clienti report month            # Report mensile con grafici ASCII
clienti alerts                  # Alert todo/scadenze overdue

# Gestione clienti
clienti client list             # Lista tutti i clienti
clienti client list --attivi    # Solo clienti attivi
clienti client list --cerca FIS # Ricerca per nome
clienti client show "Maspe Srl" # Dettagli cliente completi
clienti client add              # Wizard nuovo cliente

# Time tracking (✅ Sprint 2)
clienti time start "Cliente"    # Avvia timer
clienti time start "Cliente" --task "Descrizione attività" --tariffa 60
clienti time stop               # Ferma timer attivo
clienti time status             # Stato timer corrente
clienti time today              # Report ore oggi
clienti time week               # Report settimanale
clienti time report --cliente "Nome"  # Report per cliente
clienti time unfiled            # Ore non ancora fatturate
clienti time export --cliente "Nome" --month 9  # Export CSV

# Scadenze fatturazione (✅ Sprint 3)
clienti scadenze prossime       # Vista scadenze con alert
clienti scadenze list           # Lista con filtri avanzati
clienti scadenze add "Cliente" --importo 500 --ricorrenza mensile  # Importo fisso
clienti scadenze add "Cliente" --ricorrenza mensile --importo-variabile  # Importo variabile
clienti scadenze aggiorna 5 --importo 750  # Modifica importo/desc
clienti scadenze dettaglio "Cliente" --next  # Dati per Microfatture
clienti scadenze emessa 3 "2025-001"  # Marca emessa + ricorrenza
clienti scadenze pagata 3       # Gestione pagamenti

# Todo list (✅ NUOVO Sprint 4)
clienti todo add                # Wizard nuovo todo interattivo
clienti todo list               # Lista tutti i todos aperti
clienti todo list --completati  # Includi todos completati
clienti todo list --cliente "Nome" --priorita alta  # Filtri avanzati
clienti todo list --overdue     # Solo todos in ritardo
clienti todo oggi               # Todos con scadenza oggi
clienti todo settimana          # Todos della settimana
clienti todo cliente "Nome"     # Todos specifici per cliente
clienti todo done 5             # Marca todo come completato
clienti todo edit 3 --priorita alta --scadenza 2025-09-15  # Modifica todo
clienti todo delete 7           # Elimina todo

# Log interventi (✅ NUOVO Sprint 4) 
clienti log add                 # Wizard nuovo intervento
clienti log list                # Lista tutti gli interventi
clienti log list --cliente "Nome" --tipo call --giorni 7  # Filtri avanzati
clienti log oggi                # Riassunto attività di oggi
clienti log cliente "Nome"      # Timeline completa per cliente
clienti log export              # Export CSV per fatturazione
clienti log export --cliente "Nome" --mese 9  # Export filtrato
clienti log fatturato 12        # Marca intervento come fatturato

# Utilità
clienti import                  # Importa da clienti.json
clienti backup                  # Backup database
```

## 📋 Requisiti Principali

- ✅ Gestione anagrafica clienti con categorizzazione
- ✅ Time tracking con tariffa oraria (50€/h default)
- ✅ Scadenze fatture/parcelle (dati per Microfatture/AdE)
- ✅ Todo list per cliente e generale con priorità e scadenze
- ✅ Log interventi e attività con tracking durata e costi
- ✅ Interfaccia CLI veloce e produttiva
- ✅ Dashboard web complementare
- ✅ Export per Obsidian
- ✅ Backup semplice (copia file SQLite)

## 🏗️ Architettura Tecnica

### Stack Scelto
- **Backend**: Python 3.11+ con FastAPI
- **Database**: SQLite (file singolo)
- **CLI**: Typer + Rich per interfaccia colorata
- **Web**: HTMX + Pico.css (no build step)
- **Deploy**: Virtual environment Python su Debian 12

### Struttura Directory

```
/opt/progetti/clienti/
├── venv/                  # Virtual environment Python
├── clienti.py             # Entry point CLI/Web unificato
├── database.db            # SQLite database
├── config.toml            # Configurazione
│
├── core/
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy models
│   ├── database.py       # Connection manager  
│   └── utils.py          # Helper functions
│
├── cli/
│   ├── __init__.py       
│   ├── clienti.py        # Comandi gestione clienti
│   ├── time.py           # ✅ Time tracking completo (8 comandi)
│   ├── scadenze.py       # Vista scadenze fatture/parcelle
│   └── todo.py           # Todo list management
│
├── api/
│   ├── __init__.py       # FastAPI app
│   └── routes.py         # Endpoint REST minimali
│
├── web/
│   ├── index.html        # Dashboard HTMX
│   ├── style.css         # Pico.css
│   └── htmx.min.js       # HTMX locale
│
├── data/
│   ├── exports/          # ✅ Export CSV timesheet e Obsidian
│   └── backups/          # Backup automatici SQLite
│
├── timer_state.json      # ✅ Stato timer persistente per recovery
│
├── requirements.txt       # Dipendenze Python
└── PROGETTO.md           # Questo documento
```

## 💾 Schema Database SQLite

```sql
-- Clienti principali
CREATE TABLE clienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    piva TEXT,
    cf TEXT,
    indirizzo TEXT,
    citta TEXT,
    cap TEXT,
    provincia TEXT,
    stato TEXT DEFAULT 'attivo',  -- attivo|prospect|pausa|archiviato
    tags TEXT,                     -- JSON array di tag
    tariffa_oraria REAL DEFAULT 50.0,
    budget_mensile REAL,
    note TEXT,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultima_attivita TIMESTAMP
);

-- Contatti multipli per cliente
CREATE TABLE contatti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    ruolo TEXT,  -- es: "Marketing Manager", "CEO"
    email TEXT,
    telefono TEXT,
    principale BOOLEAN DEFAULT FALSE,
    attivo BOOLEAN DEFAULT TRUE
);

-- Tracking tempo lavorato
CREATE TABLE time_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE CASCADE,
    inizio TIMESTAMP NOT NULL,
    fine TIMESTAMP,
    descrizione TEXT,
    tariffa_oraria REAL,  -- Al momento dell'inizio
    fatturato BOOLEAN DEFAULT FALSE,
    note TEXT
);

-- Todo list per cliente e generali
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE SET NULL,
    titolo TEXT NOT NULL,
    descrizione TEXT,
    completato BOOLEAN DEFAULT FALSE,
    priorita INTEGER DEFAULT 0,  -- 0=normale, 1=alta, -1=bassa
    scadenza DATE,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_completamento TIMESTAMP
);

-- Scadenze fatturazione (per Microfatture/AdE)
CREATE TABLE scadenze_fatturazione (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL,  -- 'fattura' o 'parcella'
    data_scadenza DATE NOT NULL,
    importo_previsto REAL,
    descrizione TEXT,  -- es: "Consulenza SEO mensile"
    ricorrenza TEXT,   -- mensile|bimestrale|trimestrale|semestrale|annuale|custom
    giorni_ricorrenza INTEGER,  -- Per ricorrenze custom
    emessa BOOLEAN DEFAULT FALSE,
    data_emissione DATE,
    numero_documento TEXT,  -- Riferimento dopo emissione
    pagata BOOLEAN DEFAULT FALSE,
    data_pagamento DATE,
    note TEXT
);

-- Log interventi e attività
CREATE TABLE interventi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE CASCADE,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT NOT NULL,  -- call|email|meeting|lavoro|altro
    titolo TEXT NOT NULL,
    descrizione TEXT,
    durata_minuti INTEGER,
    costo REAL,  -- Se fatturabile
    fatturato BOOLEAN DEFAULT FALSE
);

-- Configurazioni sistema
CREATE TABLE configurazione (
    chiave TEXT PRIMARY KEY,
    valore TEXT,  -- JSON per flessibilità
    descrizione TEXT
);

-- Viste helper
CREATE VIEW clienti_attivi AS
SELECT * FROM clienti WHERE stato = 'attivo';

CREATE VIEW prossime_scadenze AS
SELECT 
    c.nome as cliente,
    c.piva,
    s.tipo,
    s.data_scadenza,
    s.importo_previsto,
    s.descrizione,
    s.id
FROM scadenze_fatturazione s
JOIN clienti c ON s.cliente_id = c.id
WHERE s.emessa = FALSE
  AND s.data_scadenza <= date('now', '+30 days')
ORDER BY s.data_scadenza;

CREATE VIEW ore_da_fatturare AS
SELECT 
    c.nome as cliente,
    COUNT(t.id) as sessioni,
    SUM((julianday(t.fine) - julianday(t.inizio)) * 24) as ore_totali,
    SUM(((julianday(t.fine) - julianday(t.inizio)) * 24) * t.tariffa_oraria) as importo
FROM time_tracking t
JOIN clienti c ON t.cliente_id = c.id
WHERE t.fine IS NOT NULL 
  AND t.fatturato = FALSE
GROUP BY t.cliente_id, c.nome;
```

## 🖥️ Comandi CLI

### Setup e Utilizzo Base

```bash
# Installazione
cd /opt/progetti/clienti
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Alias comodo in .bashrc
echo 'alias clienti="/opt/progetti/clienti/venv/bin/python /opt/progetti/clienti/clienti.py"' >> ~/.bashrc

# Utilizzo
clienti --help                    # Help generale
clienti version                   # Versione applicativo
```

### Gestione Clienti

```bash
# CRUD Clienti
clienti client add                    # Wizard interattivo nuovo cliente
clienti client list                   # Lista tutti i clienti
clienti client list --attivi          # Solo clienti attivi
clienti client list --tag "ecommerce" # Filtra per tag
clienti client show "Maspe Srl"       # Dettagli cliente completi
clienti client edit "Maspe Srl"       # Modifica dati cliente
clienti client archive "Nome"         # Archivia cliente
clienti client tag "Maspe" --add "seo,ads"  # Aggiungi tag

# Contatti
clienti contact add "Maspe Srl"       # Aggiungi contatto a cliente
clienti contact list "Maspe Srl"      # Lista contatti cliente
```

### Time Tracking

```bash
# Timer sessioni
clienti time start "Maspe Srl" --task "Ottimizzazione campagne Google Ads"
clienti time status                   # Stato timer corrente
clienti time stop                     # Ferma timer e salva
clienti time pause                    # Pausa timer
clienti time resume                   # Riprendi timer

# Report e visualizzazione
clienti time today                    # Ore lavorate oggi
clienti time week                     # Report settimanale
clienti time month                    # Report mensile
clienti time report --cliente "Maspe" # Report specifico cliente
clienti time unfiled                  # Ore non ancora fatturate

# Export
clienti time export csv --month       # Export CSV del mese
clienti time export --cliente "Maspe" # Export ore cliente
```

### Scadenze e Fatturazione

```bash
# Gestione scadenze (per Microfatture/AdE)
clienti scadenze prossime             # Prossimi 7 giorni
clienti scadenze mese                 # Scadenze del mese corrente
clienti scadenze list --overdue       # Scadenze passate non emesse
clienti scadenze add "Maspe" --tipo parcella --importo 500 --mensile
clienti scadenze dettaglio "Maspe" --next  # Dati per compilazione

# Output esempio dettaglio:
# ━━━ DATI PER MICROFATTURE/ADE ━━━
# Cliente: Maspe Srl
# P.IVA: 1777400241  
# Indirizzo: Via Balbi, 20 - 36022 Cassola (VI)
# 
# Prestazioni questo periodo:
# - Consulenza SEO mensile: €400
# - Gestione campagne Ads: €100  
# - Ore extra (3.5h): €175
#
# Totale imponibile: €675
# Rivalsa previdenziale 4%: €27
# TOTALE DOCUMENTO: €702
# 
# [Copiato negli appunti per incolla facile ✓]

# Gestione post-emissione
clienti scadenze emessa "Maspe" --numero "2024-001" --data oggi
clienti scadenze pagata "Maspe" --numero "2024-001"
```

### Todo Management (✅ Sprint 4)

```bash
# CRUD Todo
clienti todo add                      # Wizard interattivo completo
clienti todo list                     # Tutti i todo aperti con tabella colorata
clienti todo list --completati        # Includi todos completati
clienti todo list --overdue           # Solo todos in ritardo
clienti todo list --cliente "FIS" --priorita alta  # Filtri combinati
clienti todo oggi                     # Todo con scadenza oggi
clienti todo settimana                # Todo della settimana
clienti todo cliente "Maspe Srl"      # Todo specifici per cliente

# Gestione stati
clienti todo done 15                  # Completa todo ID 15
clienti todo edit 10 --priorita alta --scadenza 2025-09-20  # Modifica proprietà
clienti todo delete 12                # Elimina todo con conferma

# Output esempio todo list:
# ┏━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
# ┃  ID  ┃ Stato  ┃ Priorità     ┃ Titolo                    ┃ Cliente         ┃ Scadenza    ┃
# ┡━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
# │  3   │   🔴   │ 🔴 Alta      │ Aggiornare campagne       │ Cliente ABC     │ 06/09       │
# │  1   │   🟡   │ 🔴 Alta      │ Preparare report SEO      │ Cliente XYZ     │ 07/09       │
# └──────┴────────┴──────────────┴───────────────────────────┴─────────────────┴─────────────┘
```

### Interventi e Log Attività (✅ Sprint 4)

```bash
# Registrazione interventi
clienti log add                       # Wizard interattivo completo
clienti log list                      # Tutti gli interventi con tabella
clienti log list --cliente "Maspe" --tipo call --giorni 7  # Filtri combinati
clienti log oggi                      # Riassunto attività di oggi
clienti log cliente "Maspe"           # Timeline completa cliente

# Export e fatturazione  
clienti log export                    # Export CSV completo
clienti log export --cliente "Maspe" --mese 9  # Export filtrato
clienti log fatturato 12              # Marca intervento come fatturato

# Output esempio log oggi:
# 📅 Attività di oggi
# 
# 📞 Chiamate (1):
#   08:17 Cliente ABC: Discussione strategia SEO (45m) - €37.50
# 
# 💻 Lavoro (1):
#   09:17 Cliente ABC: Ottimizzazione landing page (2h) - €100.00
# 
# 📊 Totali giornata:
#   • Interventi: 2
#   • Tempo: 2h 45m  
#   • Valore: €137.50
```

### Dashboard e Report (✅ NUOVO Sprint 5)

```bash
# Dashboard avanzato con Rich
clienti dashboard                     # Dashboard con layout professionale
clienti stats                         # Statistiche dettagliate mese corrente
clienti stats --year 2025 --month 9 --detailed  # Stats complete con breakdown
clienti report month                  # Report annuale con grafici ASCII
clienti alerts                       # Alert todo/scadenze overdue

# Output esempio dashboard:
# 📊 Dashboard CRM Avanzato
# 
# ╭─ 👥 Clienti ─╮ ╭── 💰 Fatturato ───╮ ╭─── ⏱️ Ore ───╮ ╭─── ✅ Todo ───╮
# │ 54 / 54      │ │ €8,245           │ │ 165h        │ │ 3 todo aperti│
# │ 100% attivi  │ │ questo mese      │ │ questo mese │ │ 1 in ritardo │
# ╰──────────────╯ │ €1,200 da fattur │ │ 890h totali │ │              │
#                  ╰──────────────────╯ ╰─────────────╯ ╰──────────────╯
# 
# ╭──────── 🚨 Alert & Priorità ─────────╮╭─────── 📈 Statistiche Rapide ──────╮
# │ 🔴 1 todo in ritardo                 ││ 📊 Interventi oggi: 3              │
# │ 💰 €1,200 da fatturare              ││ 📊 Interventi mese: 42             │
# ╰──────────────────────────────────────╯╰────────────────────────────────────╯
# 
# 🎯 Obiettivi Mensili: Progresso ore: 165h/160h (103%) | Fatturato: €8,245/€8,000 (103%)

# Output esempio report month:
# 📈 Report Annuale 2025
# ┏━━━━━━━━┳━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
# ┃ Mese   ┃ Ore ┃ Fatturato ┃  €/ora ┃
# ┡━━━━━━━━╇━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
# │ Jan    │ 145 │     €7250 │    €50 │
# │ Feb    │ 160 │     €8000 │    €50 │
# │ Mar    │ 155 │     €7750 │    €50 │
# │ TOTALE │ 460 │    €23000 │    €50 │
# └────────┴─────┴───────────┴────────┘
# 
# 📊 Trend Ore Mensili
# ===================
#  1: ████████████████████████████████████████████ 145.0
#  2: ██████████████████████████████████████████████████ 160.0
#  3: ████████████████████████████████████████████████ 155.0
```

### Import/Export e Backup

```bash
# Import iniziale da dati esistenti
clienti import --from /opt/progetti/languages/python/aiutofatture/clienti.json

# Export Obsidian
clienti export obsidian --output /path/to/vault/Clienti/
clienti export markdown --cliente "Maspe Srl"

# Backup database
clienti backup create                 # Backup in data/backups/
clienti backup restore --file backup_20250106.db
```

### Server Web

```bash
# Avvio server web
clienti serve                        # Avvia su http://localhost:8000
clienti serve --port 8080            # Porta custom
clienti serve --host 0.0.0.0        # Accessibile da rete locale
```

## 🌐 Interfaccia Web

Dashboard web complementare alla CLI con:

- **Home Dashboard**: KPI principali, timer attivo, prossime scadenze
- **Clienti**: CRUD con ricerca live e filtri
- **Time Tracking**: Timer web con storico sessioni
- **Todo**: Lista con drag&drop per priorità
- **Scadenze**: Calendario visuale con alert
- **Report**: Grafici e statistiche interattive

Tecnologie: FastAPI + Jinja2 + HTMX + Pico.css

## 📦 Dipendenze Python

```txt
# Backend core
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
python-dateutil>=2.8.0

# CLI interface  
typer>=0.9.0
rich>=13.7.0
questionary>=2.0.0
tabulate>=0.9.0

# Utilities
python-dotenv>=1.0.0
toml>=0.10.0
pandas>=2.0.0
pyperclip>=1.8.0

# Web interface
jinja2>=3.1.0
python-multipart>=0.0.6
```

## 🚀 Checklist Sviluppo

### ✅ Sprint 1: Foundation & Import (COMPLETATO - 6 settembre 2025)
- [x] Setup virtual environment e struttura directory
- [x] Creazione schema database SQLite con SQLAlchemy (6 tabelle complete)
- [x] Modelli base: Cliente, Contatto, TimeTracking, Todo, Scadenze, Interventi
- [x] CLI entry point con Typer + Rich per interfaccia colorata
- [x] Import dati da clienti.json esistente (54 clienti importati)
- [x] Comando `clienti client list` funzionante con filtri e ricerca
- [x] Comando `clienti client add` con wizard interattivo
- [x] Test base funzionalità clienti - Tutto operativo
- [x] **EXTRA**: Script wrapper globale `clienti` in ~/script/app
- [x] **EXTRA**: Dashboard principale con `clienti` (senza argomenti)
- [x] **EXTRA**: Ottimizzazione tabelle per terminali stretti

### ✅ Sprint 2: Time Tracking (COMPLETATO - 6 settembre 2025)
- [x] Modello TimeTracking completato con calcoli automatici
- [x] Comandi `clienti time start/stop/status` funzionanti
- [x] Timer con stato persistente (timer_state.json)
- [x] Vista ore lavorate con Rich tables colorate
- [x] Calcolo automatico compensi e durata in tempo reale
- [x] Report ore per cliente/periodo (today/week/report)
- [x] Export CSV timesheet completo con filtri
- [x] **EXTRA**: 8 comandi time tracking implementati
- [x] **EXTRA**: Sistema di recovery per sessioni interrotte
- [x] **EXTRA**: Dashboard aggiornata con statistiche time tracking

### ✅ Sprint 3: Scadenze Fatturazione (COMPLETATO - 6 settembre 2025)
- [x] Modello ScadenzeFatturazione con campo importo_fisso
- [x] Sistema ricorrenze completo (mensile→annuale + custom)
- [x] Vista scadenze prossime con alert colorati e overdue
- [x] Comando dettaglio per copia dati Microfatture/AdE
- [x] Gestione stati completa (pending→emessa→pagata)
- [x] Integrazione automatica con time tracking per calcolo ore
- [x] **EXTRA**: Sistema importi variabili per consulenze flessibili
- [x] **EXTRA**: Comando `aggiorna` per modificare importi/descrizioni
- [x] **EXTRA**: 8 comandi scadenze + workflow completo ricorrenze
- [x] **EXTRA**: Copy-to-clipboard automatico per dati fatturazione

### ✅ Sprint 4: Todo & Interventi (COMPLETATO - 7 settembre 2025)
- [x] Modello Todo con priorità e scadenze
- [x] CRUD completo todo list con 8 comandi
- [x] Associazione todo a clienti con filtri avanzati
- [x] Modello Interventi per log attività completo
- [x] Timeline attività per cliente con export CSV
- [x] Vista todo giornaliera/settimanale con overdue alerts
- [x] **EXTRA**: Sistema priorità colorato (alta🔴/normale🟡/bassa🟢)
- [x] **EXTRA**: 6 comandi log interventi con tracking durata/costi
- [x] **EXTRA**: 5 tipi intervento (call/email/meeting/lavoro/altro)
- [x] **EXTRA**: Dashboard aggiornato con statistiche complete
- [x] **EXTRA**: Wizard interattivi per creazione todo e interventi
- [x] **EXTRA**: Sistema fatturazione interventi integrato

### ✅ Sprint 5: Dashboard CLI (COMPLETATO - 7 settembre 2025)
- [x] Dashboard testuale con Rich Layout professionale
- [x] Statistiche principali (fatturato, ore, clienti) con KPI
- [x] Report mensili/annuali con tabelle dettagliate
- [x] Grafici ASCII per trend ore/fatturato
- [x] Alert per scadenze e promemoria overdue
- [x] **EXTRA**: Progress bars verso obiettivi mensili
- [x] **EXTRA**: 4 comandi dashboard: stats, report, alerts, dashboard
- [x] **EXTRA**: Breakdown per cliente con top performers
- [x] **EXTRA**: Query ottimizzate SQLite per performance
- [x] **EXTRA**: Layout responsive per terminali diversi
- [x] **EXTRA**: Sistema alert colorato con priorità

### Sprint 6: Web Interface (2-3 giorni)
- [ ] Setup FastAPI con routing base
- [ ] Template Jinja2 con Pico.css
- [ ] Dashboard web principale
- [ ] CRUD clienti via web
- [ ] Timer web interface
- [ ] Calendario scadenze

### Sprint 7: Import/Export (1-2 giorni)
- [ ] Export Markdown per Obsidian
- [ ] Backup automatico database
- [ ] Import CSV/Excel clienti
- [ ] Sincronizzazione con aiutofatture esistente
- [ ] Template personalizzabili

### Sprint 8: Polish & Documentation (1 giorno)
- [ ] Configurazione via config.toml
- [ ] Logging delle operazioni
- [ ] Help contestuale comandi
- [ ] Documentazione README
- [ ] Script installazione automatica

## 🔧 Installazione e Setup Rapido

```bash
# 1. Clona o crea la struttura
cd /opt/progetti
git clone <repo> clienti  # O copia manuale dei file

# 2. Setup ambiente
cd clienti
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Inizializza database
python clienti.py init

# 4. Import dati esistenti (opzionale)
python clienti.py import --from ../languages/python/aiutofatture/clienti.json

# 5. Test funzionalità base
python clienti.py client list
python clienti.py --help

# 6. Alias permanente
echo 'alias clienti="/opt/progetti/clienti/venv/bin/python /opt/progetti/clienti/clienti.py"' >> ~/.bashrc
source ~/.bashrc

# 7. Avvia server web (opzionale)
clienti serve --port 8080
```

## 🎯 Obiettivi di Performance

- ✅ Avvio CLI in < 200ms
- ✅ Database SQLite < 100MB per 1000 clienti
- ✅ RAM usage < 50MB
- ✅ Backup completo < 5 secondi
- ✅ Ricerche clienti < 100ms
- ✅ Web UI responsive su mobile

## 🔒 Considerazioni Sicurezza

- Database SQLite locale (no esposizione rete)
- Backup criptati opzionali
- No password in chiaro
- Logs operazioni sensibili
- Validazione input CLI/Web

## 🚀 Roadmap Future

### Versione 1.0
- [ ] Tutte le funzionalità base
- [ ] Interfacce CLI e Web complete
- [ ] Import/Export Obsidian
- [ ] Backup automatici

### Versione 1.1 (Future)
- [ ] API REST pubblica
- [ ] Plugin Obsidian nativi
- [ ] Integrazione email/calendario
- [ ] Mobile app (PWA)
- [ ] Multi-utente con autenticazione

### Versione 2.0 (Future)  
- [ ] Cloud sync opzionale
- [ ] Integrazione CRM esterni
- [ ] AI per categorizzazione automatica
- [ ] Reporting avanzato con PDF

---

**Progetto iniziato**: Gennaio 2025  
**Versione target**: 1.0  
**Linguaggio**: Python 3.11+  
**License**: Uso personale