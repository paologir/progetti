# LLM - Strumenti e Utilità per Large Language Models

Questa directory contiene una collezione di script e utilità che sfruttano Large Language Models (LLM) per varie applicazioni pratiche. Gli strumenti sono progettati per integrare diverse API e modelli LLM in workflow produttivi.

## 📁 Struttura del Progetto

```
llm/
├── annunciads          # Script Python per generare annunci Google Ads
├── errideluca          # Emulatore dello stile di scrittura di Erri De Luca
├── gemma27-hetzner     # Client per server Gemma 2 7B locale
├── kraus               # Emulatore dello stile aforistico di Karl Kraus
├── set-annunciads      # Script Bash per Google Ads con jina.ai
└── titoliseo           # Generatore di titoli e descrizioni SEO
```

## 🛠️ Strumenti Disponibili

### 1. **annunciads** - Generatore Annunci Google Ads (Python)
Script Python che analizza il contenuto di una pagina web e genera:
- 20 titoli ottimizzati (max 30 caratteri)
- 8 descrizioni lunghe (max 90 caratteri)
- 3 descrizioni brevi (max 60 caratteri)
- Suggerimenti per sitelink e callout

**Requisiti**: `requests`, `markdownify`, `pyperclip`, `llm`

### 2. **set-annunciads** - Generatore Annunci Google Ads (Bash)
Versione Bash dello strumento precedente con funzionalità avanzate:
- Integrazione con r.jina.ai per l'estrazione contenuti
- Supporto multi-modello LLM
- Output colorato e formattato
- Opzioni per clipboard e salvataggio file

**Requisiti**: `curl`, `llm` CLI

### 3. **titoliseo** - Ottimizzazione SEO
Script Bash per generare titoli e descrizioni SEO ottimizzati:
- Analisi automatica del contenuto web
- Generazione multipla di varianti
- Supporto multilingua
- Integrazione con vari modelli LLM

**Requisiti**: `curl`, `llm` CLI

### 4. **errideluca** - Emulatore Stile Erri De Luca
Chatbot interattivo che emula lo stile di scrittura di Erri De Luca:
- Stile scarno, fisico e poetico
- Lessico concreto e materia
- Prospettiva spirituale e ancestrale
- Interfaccia conversazionale

**Requisiti**: `google-generativeai`, `pyperclip`, `prompt_toolkit`

### 5. **kraus** - Emulatore Stile Karl Kraus
Chatbot che riproduce lo stile aforistico e satirico di Karl Kraus:
- Aforismi taglienti e paradossi
- Critica sociale e linguistica
- Analisi delle ipocrisie contemporanee
- Precisione lessicale estrema

**Requisiti**: `google-generativeai`, `pyperclip`, `prompt_toolkit`

### 6. **gemma27-hetzner** - Client Gemma 2 7B
Client Python per interagire con un server Gemma 2 7B locale:
- Connessione a server LLM locale (porta 8080)
- Conversazione interattiva
- Supporto input multilinea
- Copia automatica negli appunti

**Requisiti**: Server LLM locale, `requests`, `pyperclip`

## 🚀 Utilizzo Rapido

### Per gli script Bash:
```bash
# Genera annunci Google Ads
./set-annunciads -c -m gemini https://example.com

# Crea titoli SEO
./titoliseo -n 10 -l inglese https://example.com
```

### Per gli script Python:
```bash
# Avvia l'emulatore Erri De Luca
python3 errideluca

# Genera annunci con lo script Python
python3 annunciads https://example.com
```

## 📋 Requisiti Generali

- **Python 3.x** per gli script Python
- **Bash** per gli script shell
- **llm CLI** (installabile con `pip install llm`)
- **API Keys** per i servizi LLM utilizzati (es. GOOGLE_API_KEY, MISTRAL_API_KEY)

## 🔑 Configurazione API

Molti script richiedono chiavi API configurate come variabili d'ambiente:

```bash
export GOOGLE_API_KEY="tua-chiave-api"
export MISTRAL_API_KEY="tua-chiave-api"
```

## 📝 Note

- Gli script sono progettati per essere autonomi e facilmente integrabili in workflow esistenti
- Ogni strumento include opzioni di help dettagliate (`-h` o `--help`)
- L'output può essere salvato su file o copiato negli appunti per maggiore praticità