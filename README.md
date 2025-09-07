# Progetti - Collezione di Script e Strumenti

Questo repository contiene una vasta collezione di script e piccoli progetti organizzati per linguaggi di programmazione e domini di applicazione.

## Struttura del Repository

### 📁 ASM - Assembly Language
Esempi di programmazione in Assembly per architettura x86:

- **`hello.asm`** - Classico "Hello, World!" in Assembly con syscall Linux
- **`io.asm`** - Esempio di input/output, legge un numero dall'utente e lo stampa

**Compilazione**: `nasm -f elf32 file.asm && ld -m elf_i386 file.o -o file`

### 📁 Bash - Script Shell

Utilities per automazione e gestione del sistema:

- **`cambiacase`** - Rinomina file in maiuscolo/minuscolo
  - Uso: `./cambiacase [-l | -u] [directory]`
  - `-l` = minuscolo, `-u` = maiuscolo

- **`cancellalineebianche`** - Rimuove linee vuote da file
  - Uso: `./cancellalineebianche file`

- **`center`** - Centra testo con larghezza specificata
  - Uso: `./center [-w width] [file...]`
  - Di Heiner Steven, tool professionale per formatting

- **`find_large_files`** - Trova file di grandi dimensioni
  - Uso: `./find_large_files [dimensione] [directory]`
  - Esempio: `./find_large_files 200M /tmp`

- **`md2pdf`** - Converte Markdown in PDF con Pandoc
  - Uso: `./md2pdf <file.md> [output.pdf] [--toc]`
  - Richiede: pandoc, xelatex, template eisvogel

- **`tarra`** - Crea archivi tar.gz
  - Uso: `./tarra directory nome_archivio`

- **`zippa`** - Crea archivi ZIP
  - Uso: `./zippa directory nome_archivio`

### 📁 C - Programmi C

Utilities matematiche e di calcolo:

- **`bond_duration.c`** - Calcola rendimento e duration di obbligazioni
  - Compilazione: `gcc -O3 -Wall -o bond_duration bond_duration.c -lm`
  - Supporta modalità interattiva e parametri da linea di comando

- **`diffdate.c`** - Calcola differenza tra due date
  - Supporta formati: gg/mm/yyyy, gg-mm-yyyy

- **`differenza_percentuale.c`** - Calcola differenza percentuale tra due valori
  - Versione robusta con gestione errori

- **`diffperc.c`** - Versione semplificata per calcolo percentuale
  - Supporta virgola e punto decimale

### 📁 LLM - Strumenti per Large Language Models

Script per l'integrazione con modelli di linguaggio:

- **`annunciads`** - Genera annunci Google Ads da URL
  - Python script che usa llm per creare titoli e descrizioni
  - Dipendenze: requests, markdownify, pyperclip

- **`set-annunciads`** - Versione bash per Google Ads
  - Usa Jina AI per estrazione contenuto
  - Genera titoli, descrizioni, sitelink e callout

- **`titoliseo`** - Genera titoli e descrizioni SEO
  - Analogo a set-annunciads ma per SEO
  - Supporta vari modelli LLM

### 📁 Mistral RAG MVP - Sistema RAG

Prototipo di sistema Retrieval-Augmented Generation:

- **`chatbot.py`** - Chatbot con RAG usando Mistral AI
  - Dipendenze: langchain, faiss-cpu, sentence-transformers
  - Usa FAISS per similarity search

- **`ingest.py`** - Indicizzazione documenti
  - Supporta PDF, Markdown, TXT
  - Crea indice FAISS per ricerca vettoriale

- **`documents/`** - Directory per documenti da indicizzare

**Setup**:
```bash
pip install langchain langchain-community langchain-mistralai faiss-cpu sentence-transformers python-dotenv
# Configura MISTRAL_API_KEY nel file .env
python ingest.py  # Indicizza documenti
python chatbot.py # Avvia chatbot
```

### 📁 Python - Script Python

#### Sottodirectory: aiutofatture
Sistema completo per gestione fatture:

- **`aiutofatture`** - Gestore fatture e avvisi professionale
  - Gestione clienti (CRUD completo)
  - Configurazione esterna JSON
  - Calcolo IVA e totali

- **`aiutofatture_migliorato.py`** - Versione avanzata
- **`clienti.json`** - Database clienti
- **`config_fatture.json`** - Configurazione sistema

#### Sottodirectory: carta_intestata
Generatore documenti professionali:

- **`genera_documento.py`** - Converte Markdown in DOCX con intestazione
  - Usa template professionale con fonts Montserrat/Proxima Nova
  - Supporto completo Markdown (tabelle, liste, codice)
  - Dipendenze: python-docx, markdown, beautifulsoup4

- **`analyze_docx.py`** / **`analyze_docx_detailed.py`** - Analizzatori documenti DOCX

#### Sottodirectory: statistica
- **`beta.py`** - Script per analisi statistiche

#### Script Python principali:

- **`csv2markdown`** - Converte CSV in tabelle Markdown
  - Uso: `./csv2markdown file.csv`

- **`csv2pdf`** - Converte CSV in PDF con formattazione
  - Dipendenze: pandas, reportlab
  - Supporta orientamento, font personalizzati

- **`md2latex`** - Converte Markdown in LaTeX
  - Supporta tabelle, liste, formattazione

- **`pdf-to-markdown`** - Estrae testo e tabelle da PDF
  - Dipendenze: PyPDF2, pdfminer, tabula-py
  - Estrae tabelle come Markdown

- **`reindirizza301`** - Genera regole .htaccess per redirect 301
  - Legge coppie URL e genera configurazione Apache

- **`seo-analisi`** - Analisi SEO completa di siti web
  - Analisi meta tag, densità keywords, link
  - Output: JSON, CSV, clipboard
  - Dipendenze: requests, beautifulsoup4

- **`sitemap.py`** - Estrae URL da sitemap XML
  - Genera file TXT e Excel con URL

- **`sitoscraping`** - Web scraping completo di siti
  - Estrae tutto il contenuto in Markdown
  - Supporta crawling ricorsivo

- **`url2md`** - Converte singoli URL in Markdown
  - Usa crawl4ai per estrazione avanzata
  - Supporta copia su clipboard

### 📁 R - Script R

Analisi dati e reporting:

- **`datiweb-capehorn.r`** - Analisi Google Analytics per cliente specifico
  - Integrazione Google Analytics 4
  - Analisi costi pubblicitari e revenue

- **`maspe-console-json.r`** - Analisi completa GA4 + Search Console
  - Autenticazione service account
  - Analisi traffico e performance

- **`statistica-beta-traffico-sito.r`** - Statistiche traffico sito
- **`utentiwebmaspega4.r`** - Analisi utenti GA4

**Dipendenze R comuni**: googleAnalyticsR, dplyr, ggplot2, searchConsoleR

## Dipendenze Generali

### Python
```bash
# Dipendenze base
pip install requests beautifulsoup4 pandas

# Per documenti
pip install python-docx markdown markdownify

# Per PDF
pip install PyPDF2 pdfminer.six tabula-py reportlab

# Per web scraping
pip install crawl4ai pyperclip

# Per LLM/RAG
pip install langchain langchain-community faiss-cpu sentence-transformers
```

### Bash
- pandoc (per md2pdf)
- xelatex (per PDF)
- curl, jq (per script LLM)

### C
- gcc, build-essential
- libm (math library)

### R
```r
install.packages(c("googleAnalyticsR", "dplyr", "ggplot2", "searchConsoleR"))
```

## Utilizzo Generale

1. **Script eseguibili**: La maggior parte degli script ha lo shebang e può essere eseguita direttamente
2. **Help integrato**: Molti script supportano `-h` o `--help`
3. **Gestione errori**: Script robusti con validazione input
4. **Configurazione**: Molti tool supportano file di configurazione esterni

## Contributi

Vedi `OpenCode.md` per linee guida su stile e contribuzione.

## Licenza

Vari script hanno licenze diverse. Controllare i singoli file per dettagli.