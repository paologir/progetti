# Generatore Documenti con Carta Intestata

Script Python per generare documenti Word (docx) con intestazione e piè di pagina personalizzati a partire da file Markdown.

## Requisiti

- Python 3.x
- Librerie Python: `python-docx`, `markdown`, `beautifulsoup4`

## Installazione

```bash
pip install python-docx markdown beautifulsoup4
```

## Utilizzo

```bash
python3 genera_documento.py input.md -o output.docx
```

### Parametri

- `input.md`: File Markdown di input (obbligatorio)
- `-o`, `--output`: Nome del file di output (default: `output.docx`)

## Esempio

```bash
python3 genera_documento.py esempio.md -o proposta_seo.docx
```

## Caratteristiche

Lo script genera documenti con:

- **Intestazione**: Contiene nome, titolo professionale e informazioni di contatto
- **Piè di pagina**: Email e sito web
- **Stili automatici**: 
  - Titoli H1-H6 convertiti in stili Heading 1-6
  - Supporto per grassetto, corsivo e codice inline
  - Liste puntate e numerate
  - Citazioni (blockquote)
  - Blocchi di codice

## Formattazione Markdown supportata

- `# Titolo 1` → Heading 1 (20pt, Montserrat SemiBold)
- `## Titolo 2` → Heading 2 (16pt, Montserrat SemiBold)
- `### Titolo 3` → Heading 3 (14pt, Montserrat SemiBold)
- `**grassetto**` → Testo in grassetto
- `*corsivo*` → Testo in corsivo
- `` `codice` `` → Font Courier New
- Liste puntate e numerate
- Tabelle (con estensione `extra`)
- Citazioni con `>`

## Note

- Il documento generato usa formato A4 con margini personalizzati
- Font principali: Montserrat per intestazioni, Proxima Nova per il testo
- I margini sono impostati come nel modello originale