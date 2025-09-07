# Script R per Analisi Web

Questa directory contiene script R per l'analisi del traffico web, principalmente per Google Analytics e Google Search Console.

## Script principali

### maspe-console-json.r
Script completo per l'analisi dei dati di Google Analytics e Google Search Console per il sito maspe.com.

#### Funzionalità
- Estrazione dati utenti e sessioni da Google Analytics
- Analisi statistica del traffico (media, mediana, outliers)
- Analisi delle conversioni (moduli compilati)
- Dati delle campagne pubblicitarie e costi
- Estrazione query di ricerca e pagine da Google Search Console
- Analisi Bayesiana del tasso di conversione
- Generazione grafici e export CSV

#### Output generati
- `/tmp/maspe-dati.csv` - Dati giornalieri utenti, organici, moduli e costi
- `/tmp/maspe-campagne.csv` - Dati campagne pubblicitarie
- `/tmp/maspe-queries.csv` - Query di ricerca da Search Console
- `/tmp/maspe-pagine.csv` - Pagine più visitate da Search Console
- `/tmp/ts-maspe.jpg` - Grafico serie temporale utenti vs organici

### Altri script
- `datiweb-capehorn.r` - Analisi traffico per capehorn
- `statistica-beta-traffico-sito.r` - Analisi statistica con distribuzione Beta
- `utentiwebmaspega4.r` - Analisi utenti web con GA4

## Requisiti

### Librerie R necessarie
```r
install.packages(c(
  "googleAnalyticsR",
  "txtplot",
  "dplyr", 
  "tidyr",
  "UsingR",
  "outliers",
  "readr",
  "moments",
  "ggplot2"
))
```

### Installazione searchConsoleR
Il pacchetto `searchConsoleR` non è disponibile su CRAN per R 4.2.x, quindi deve essere installato da GitHub:

```r
# Installa remotes se non presente
if (!requireNamespace('remotes', quietly = TRUE)) {
  install.packages('remotes')
}

# Installa searchConsoleR da GitHub
remotes::install_github('MarkEdmondson1234/searchConsoleR')
```

## Configurazione

### Autenticazione
Gli script utilizzano un service account JSON per l'autenticazione sia con Google Analytics che con Search Console:

```r
# Google Analytics
ga_auth(json_file = '/path/to/your/service-account.json')

# Search Console
scr_auth(json_file = '/path/to/your/service-account.json')
```

**Importante**: Assicurarsi che il service account abbia i permessi necessari sia per Google Analytics che per Search Console.

### Permessi necessari
- Google Analytics: Accesso in lettura alla proprietà
- Google Search Console: Proprietario o utente completo del sito

## Utilizzo

1. Assicurarsi che tutte le librerie siano installate
2. Configurare il percorso del file JSON del service account nello script
3. Eseguire lo script:
   ```bash
   Rscript maspe-console-json.r
   ```
4. Inserire le date di inizio e fine quando richiesto (formato YYYY-MM-DD)

## Note
- Gli script sono interattivi e richiedono input da tastiera per le date
- I file di output vengono salvati in `/tmp/`
- Il grafico della serie temporale viene salvato come immagine JPG