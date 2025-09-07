# Sistema RAG per Archivio Clienti

## Panoramica

Il sistema RAG per l'archivio clienti è un'estensione del sistema RAG locale che permette di:

- **Ingerire documenti** da strutture gerarchiche di clienti
- **Filtrare contenuti sensibili** automaticamente
- **Tracciare file processati** per aggiornamenti incrementali
- **Fare query con filtri** per cliente, tipo file, cartella
- **Gestire metadata** specifici per ogni cliente

## Caratteristiche Principali

### 🔒 Sicurezza
- Esclusione automatica file sensibili (`dati.txt`, `credentials.txt`, etc.)
- Redazione automatica di email, P.IVA, telefoni, IBAN
- Validazione dimensione file e formati supportati

### 📁 Supporto Formati
- **PDF** - Documenti principali
- **DOCX/DOC** - Documenti Office
- **XLSX/XLS** - Fogli di calcolo
- **CSV** - Dati strutturati
- **TXT** - File di testo
- **MD** - Documenti Markdown

### 🔄 Ingest Incrementale
- Tracking automatico file processati
- Skip file non modificati
- Calcolo hash per rilevare modifiche
- Database SQLite per persistenza

### 👥 Gestione Clienti
- Metadata automatico per ogni cliente
- Struttura gerarchica preservata
- Statistiche per cliente
- Filtering nelle query

## Installazione

### Prerequisiti
```bash
# Attiva virtual environment
source .venv/bin/activate

# Le dipendenze sono già installate se il sistema RAG funziona
pip install -r requirements.txt
```

### Verifica Installazione
```bash
# Test su ambiente di prova
python3 test_client_ingest.py
```

## Utilizzo

### 1. Ingest dei Documenti

#### Ingest Completo
```bash
# Ingest di tutto l'archivio /opt/lavoro
python3 ingest_clienti.py

# Ingest ambiente di test
python3 ingest_clienti.py --test-mode
```

#### Ingest Selettivo
```bash
# Solo clienti specifici
python3 ingest_clienti.py --clients maspe espa

# Dry-run per vedere cosa verrà processato
python3 ingest_clienti.py --dry-run
```

#### Manutenzione
```bash
# Mostra statistiche
python3 ingest_clienti.py --stats

# Resetta tracking (per ri-processare tutto)
python3 ingest_clienti.py --reset-tracking

# Pulisce record orfani
python3 ingest_clienti.py --cleanup
```

### 2. Query dei Documenti

#### Query Base
```bash
# Ricerca semplice
python3 query_clienti.py "proposte commerciali"

# Con filtri
python3 query_clienti.py "report analytics" --client maspe --limit 5
```

#### Query Avanzata
```bash
# Filtra per tipo file
python3 query_clienti.py "contratti" --file-type pdf

# Filtra per cartella
python3 query_clienti.py "logo" --folder logo

# Combina filtri
python3 query_clienti.py "seo" --client maspe --file-type docx
```

#### Esplorazione
```bash
# Lista clienti disponibili
python3 query_clienti.py --list-clients

# Statistiche cliente
python3 query_clienti.py --client-stats maspe

# Modalità interattiva
python3 query_clienti.py --interactive
```

### 3. Modalità Interattiva

```bash
python3 query_clienti.py --interactive
```

Comandi disponibili:
- `<query>`: Cerca documenti
- `client:<nome>`: Filtra per cliente
- `type:<tipo>`: Filtra per tipo file
- `folder:<cartella>`: Filtra per cartella
- `limit:<n>`: Imposta limite risultati
- `clients`: Lista clienti
- `stats:<cliente>`: Statistiche cliente
- `exit`: Esci

Esempio: `"contratti client:maspe type:pdf limit:3"`

## Struttura Dati

### Metadata dei Documenti
Ogni documento include:
```python
{
    "source": "/path/to/file.pdf",
    "file_name": "file.pdf",
    "file_type": "pdf",
    "file_size_mb": 2.5,
    "client_name": "maspe",
    "client_path": "/opt/lavoro/maspe",
    "relative_path": "maspe/proposte/proposta.pdf",
    "subfolder": "proposte",
    "folder_depth": 2,
    "chunk_index": 0,
    "total_chunks": 5,
    "tags": ["client:maspe", "depth:2", "folder:proposte"]
}
```

### Database File Tracking
```sql
CREATE TABLE processed_files (
    file_path TEXT PRIMARY KEY,
    file_hash TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    last_modified REAL NOT NULL,
    processed_at TEXT NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    client_name TEXT,
    status TEXT DEFAULT 'processed'
);
```

## Configurazione

### Filtri Dati Sensibili
File esclusi automaticamente:
- `**/dati.txt`
- `**/credentials.txt`
- `**/password*`
- `**/secrets*`
- `**/.env`

Pattern redatti nel testo:
- Email: `[EMAIL_REDACTED]`
- P.IVA: `[PIVA_REDACTED]`
- Telefono: `[TEL_REDACTED]`
- IBAN: `[IBAN_REDACTED]`
- Codice Fiscale: `[CF_REDACTED]`

### Personalizzazione
Modifica `config.py` per:
- Formati file supportati
- Dimensioni massime
- Parametri di chunking
- Modelli di embedding

## Workflow Consigliato

### Setup Iniziale
1. **Backup** del sistema esistente
2. **Test** su ambiente limitato
3. **Ingest incrementale** dell'archivio completo
4. **Verifica** qualità dei risultati

### Manutenzione
1. **Ingest periodico** per nuovi file
2. **Pulizia** record orfani
3. **Monitoraggio** statistiche
4. **Backup** indici e database

### Esempi di Query Utili

```bash
# Trova tutti i contratti di un cliente
python3 query_clienti.py "contratto" --client maspe

# Cerca report analytics per tutti i clienti
python3 query_clienti.py "analytics google" --file-type pdf

# Documenti in sottocartelle specifiche
python3 query_clienti.py "logo" --folder logo

# Proposte commerciali recenti
python3 query_clienti.py "proposta commerciale" --file-type docx

# Materiali di marketing
python3 query_clienti.py "marketing catalogo" --folder marketing
```

## Troubleshooting

### Problemi Comuni

**1. Path non sicuro**
```bash
# Disabilita validazione path in ingest_v2.py linea 73-76
```

**2. File non trovati**
```bash
# Verifica path assoluti
python3 ingest_clienti.py --dry-run
```

**3. Troppi file esclusi**
```bash
# Controlla filtri in utils/security.py
# Mostra file esclusi nei log
```

**4. Query senza risultati**
```bash
# Verifica indice caricato
python3 query_clienti.py --list-clients

# Controlla spelling e filtri
python3 query_clienti.py "query" --interactive
```

### Log e Debug
```bash
# Log dettagliati in logs/ingest.log
tail -f logs/ingest.log

# Database tracking
sqlite3 logs/file_tracker.db ".tables"
```

## Prestazioni

### Ottimizzazioni
- **Caching** documenti con hash
- **Processing parallelo** con ThreadPoolExecutor
- **Chunking ottimizzato** per tipo documento
- **Indici database** per query veloci

### Monitoraggio
```bash
# Statistiche processamento
python3 ingest_clienti.py --stats

# Statistiche query
python3 query_clienti.py --client-stats <cliente>
```

## Estensioni Future

### Possibili Miglioramenti
1. **OCR** per immagini e PDF scansionati
2. **Classificazione automatica** documenti
3. **Estrazione entità** (date, importi, nomi)
4. **Integrazione email** per ingest automatico
5. **API REST** per interfacce web
6. **Dashboard** per monitoring

### Integrazione con Altri Sistemi
- **CRM** per correlazione contatti
- **ERP** per documentazione progetti
- **Email** per aggiornamenti automatici
- **Cloud** per backup e sincronizzazione

## Sicurezza

### Raccomandazioni
1. **Backup regolari** di indici e database
2. **Accesso controllato** ai file sensibili
3. **Audit trail** delle query
4. **Crittografia** per dati sensibili
5. **Rotazione** credenziali API

### Compliance
- Automatica **redazione** dati personali
- **Esclusione** file sensibili
- **Logging** accessi e modifiche
- **Retention policy** configurabile

---

Per supporto tecnico o domande, consultare la documentazione del sistema RAG principale o contattare il team di sviluppo.