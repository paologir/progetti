# Python Utilities Collection

Questa directory contiene una raccolta di utility Python standalone per varie attività di elaborazione documenti, SEO, web scraping e automazione.

## Struttura del Progetto

```
python/
├── aiutofatture/         # Gestione fatture con JSON
├── carta_intestata/      # Generazione documenti DOCX da Markdown
├── landing_page_builder/ # Sistema completo per landing page
├── csv2markdown          # Conversione CSV → Markdown
├── csv2pdf              # Conversione CSV → PDF
├── md2latex             # Conversione Markdown → LaTeX
├── pdf-to-markdown      # Conversione PDF → Markdown
├── reindirizza301       # Gestione redirect 301
├── seo-analisi          # Analisi SEO siti web
├── sitemap.py           # Estrazione e analisi sitemap XML
├── sitoscraping         # Web scraping generico
└── url2md               # Conversione pagine web → Markdown
```

## Installazione Dipendenze

### Dipendenze Generali
```bash
# Installa le dipendenze comuni
pip install requests beautifulsoup4 pandas

# Per progetti specifici, vedi le sezioni dedicate
```

## Progetti Principali

### 📄 carta_intestata/
Generatore di documenti Word (DOCX) con intestazione e piè di pagina personalizzati da file Markdown.

**Installazione:**
```bash
pip install python-docx markdown beautifulsoup4
```

**Utilizzo:**
```bash
python3 carta_intestata/genera_documento.py input.md -o output.docx
```

**Caratteristiche:**
- Intestazione con nome e informazioni professionali
- Piè di pagina con contatti
- Conversione automatica stili Markdown → Word
- Supporto tabelle, liste, citazioni e codice

[Documentazione completa](carta_intestata/README.md)

### 🚀 landing_page_builder/
Sistema completo per generazione landing page ad alta conversione con 3 agenti specializzati Claude Code.

**Installazione:**
```bash
cd landing_page_builder
pip install -r requirements.txt
```

**Caratteristiche:**
- 5 template hero ottimizzati (lead gen, sales, eventi, ecc.)
- Core Web Vitals ottimizzati
- WCAG 2.1 AA compliance
- Sistema modulare con HTML/CSS/JS engines
- Zero dipendenze frontend

[Documentazione completa](landing_page_builder/README.md)

### 💰 aiutofatture/
Applicazione per gestione fatture con configurazione JSON.

**File di configurazione:**
- `clienti.json` - Database clienti
- `config_fatture.json` - Configurazione fatture
- `voci_preimpostate.txt` - Voci ricorrenti

**Utilizzo:**
```bash
python3 aiutofatture/aiutofatture_migliorato.py
```

### 🔍 seo-analisi
Tool per analisi SEO completa di siti web.

**Utilizzo:**
```bash
./seo-analisi https://example.com
```

**Analisi include:**
- Meta tag (title, description, keywords)
- Headers (H1-H6)
- Immagini (alt text)
- Link interni/esterni
- Performance base

### 🗺️ sitemap.py
Script per download e analisi sitemap XML.

**Utilizzo:**
```bash
python3 sitemap.py https://example.com/sitemap.xml
```

**Output:**
- `sitemap.txt` - Lista URL uno per riga
- `sitemap.xlsx` - File Excel con tabella URL
- Analisi struttura sito

## Utility di Conversione

### csv2markdown
Converte file CSV in tabelle Markdown.

```bash
./csv2markdown input.csv > output.md
```

### csv2pdf
Converte file CSV in PDF formattato.

```bash
./csv2pdf input.csv output.pdf
```

### md2latex
Converte Markdown in LaTeX per documenti accademici.

```bash
./md2latex input.md > output.tex
```

### pdf-to-markdown
Estrae testo da PDF e lo converte in Markdown.

```bash
./pdf-to-markdown input.pdf > output.md
```

### url2md
Scarica pagina web e la converte in Markdown pulito.

```bash
./url2md https://example.com/article > article.md
```

## Web Tools

### sitoscraping
Tool generico per web scraping configurabile.

```bash
./sitoscraping https://example.com "selector_css"
```

### reindirizza301
Gestione e test redirect 301 per SEO.

```bash
./reindirizza301 check urls.txt
./reindirizza301 generate old-urls.txt new-urls.txt
```

## Best Practices

### Esecuzione Script
- Usa sempre `python3` (non `python`) per compatibilità
- Verifica permessi esecuzione per script bash-like: `chmod +x script_name`
- Controlla dipendenze specifiche nei file import

### Gestione Dipendenze
```bash
# Crea virtual environment per progetti complessi
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate     # Windows

# Installa dipendenze progetto
pip install -r requirements.txt  # se presente
```

### Pattern Comuni
1. **Input/Output**: La maggior parte accetta file input e genera output
2. **Configurazione**: Progetti complessi usano JSON per config
3. **Standalone**: Ogni script è indipendente e autocontenuto
4. **CLI-first**: Progettati per uso da linea di comando

## Esempi d'Uso Completi

### Workflow Documentazione
```bash
# 1. Converti CSV dati in Markdown
./csv2markdown dati.csv > dati.md

# 2. Genera documento Word con intestazione
python3 carta_intestata/genera_documento.py dati.md -o report.docx

# 3. Oppure converti in LaTeX per paper
./md2latex dati.md > paper.tex
pdflatex paper.tex
```

### Workflow SEO
```bash
# 1. Analizza sito target
./seo-analisi https://competitor.com > analisi.txt

# 2. Estrai sitemap
python3 sitemap.py https://competitor.com/sitemap.xml

# 3. Scraping contenuti specifici
./url2md https://competitor.com/best-article > articolo.md
```

### Workflow Landing Page
```bash
# 1. Crea landing page
cd landing_page_builder
python3 builder.py

# 2. Analizza performance
python3 analyze_performance.py output/

# 3. Deploy su Netlify/Vercel
netlify deploy --prod --dir=output/
```

## Troubleshooting

### Errori Comuni

**ImportError: No module named 'xyz'**
```bash
# Installa modulo mancante
pip install xyz
```

**Permission denied**
```bash
# Aggiungi permessi esecuzione
chmod +x nome_script
```

**Python 2 vs Python 3**
```bash
# Verifica versione
python3 --version

# Usa sempre python3 esplicitamente
python3 script.py  # ✓
python script.py   # ✗ potrebbe usare Python 2
```

## Contribuire

Per aggiungere nuove utility:

1. Crea script standalone nella directory `/python/`
2. Includi shebang: `#!/usr/bin/env python3`
3. Documenta dipendenze nei commenti iniziali
4. Aggiungi esempio d'uso nel docstring
5. Mantieni filosofia "do one thing well"

## License

Tutti gli script sono rilasciati per uso interno. Verifica licenze delle dipendenze prima di distribuzione esterna.