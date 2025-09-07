### Piano di Sviluppo: Monitoraggio Investimenti

-   **Fase 1: Ricerca e Definizione**
    -   [x] Ricerca di fonti dati affidabili e accessibili. **Scelta: Scraping da Borsa Italiana.**
    -   [x] Definizione di un formato per un file di configurazione (`config.json`) con ISIN e soglie.

-   **Fase 2: Sviluppo del Core**
    -   [x] Creazione di uno script Python principale (`monitor.py`) che legga la configurazione.
    -   [x] Implementazione della logica di scraping per recuperare i prezzi da Borsa Italiana.
        -   [x] Costruzione dinamica dell'URL.
        -   [x] Utilizzo di `pandas.read_html` per estrarre la tabella.
        -   [x] Gestione errori e pulizia del dato.
        -   [x] Inserimento di una pausa tra le richieste.
    -   [x] Implementazione della logica di controllo per confrontare i prezzi attuali con le soglie.

-   **Fase 3: Notifiche**
    -   [x] Sviluppo di un semplice sistema di notifica (stampa a console).

-   **Fase 4: Revisione**
    -   [x] Riepilogo delle modifiche e considerazioni finali.

---

### Revisione Finale

Il progetto è stato completato con successo. È stato creato uno script Python (`monitor.py`) che legge una lista di titoli di stato dal file `config.json` e ne monitora il prezzo. 

La fonte dati scelta è il sito ufficiale di Borsa Italiana, dal quale i dati vengono estratti tramite web scraping. Questa soluzione si è rivelata più affidabile rispetto all'uso di API generiche come `yfinance` per il mercato obbligazionario italiano.

Lo script implementa:
- Lettura di una configurazione flessibile.
- Scraping robusto con `pandas`, con una logica mirata a trovare il "Prezzo ufficiale".
- Gestione degli errori di rete e di parsing.
- Logica di confronto del prezzo con una soglia e notifica a console.
- Una pausa tra le richieste per un comportamento rispettoso verso il server.

Il codice è pronto per essere esteso con più titoli nel file `config.json` o con sistemi di notifica più avanzati (es. email, Telegram).

---

### Aggiornamento del 28 Giugno 2025

- **Estensione del Monitoraggio a Titoli Europei:**
  - [x] Aggiornato `config.json` con una nuova lista di titoli di stato europei (Belgio, Polonia, Austria, Germania, Ungheria, Francia, UE).
  - [x] Modificato `monitor.py` per gestire il recupero dei prezzi sia per i BTP italiani che per le obbligazioni europee.
  - [x] Implementata una logica di fallback: lo script prova prima a recuperare i dati dalla sezione "euro-obbligazioni" di Borsa Italiana e, in caso di fallimento, tenta con la pagina specifica dei BTP.
  - [x] Corretto il parsing del prezzo per i nuovi titoli, normalizzando il valore a un numero decimale corretto.
  - [x] Eseguiti test di verifica per assicurare il corretto funzionamento con la nuova configurazione.

- **Prossimi Passi:**
  - [x] Migliorare l'output per una visualizzazione più chiara e sintetica.
  - [ ] Introdurre un sistema di logging più strutturato.
  - [ ] Valutare l'aggiunta di un database per storicizzare i prezzi.

### Aggiornamento del 28 Giugno 2025 (sera)

- **Miglioramento dell'Output:**
    - [x] **Ricerca libreria per output colorato:** Scelta la libreria `colorama`.
    - [x] **Installazione dipendenze:** Aggiunta la dipendenza `colorama` (menzionata nei commenti).
    - [x] **Riformattazione output in tabella:** Modificata la funzione `main` in `monitor.py` per stampare i risultati in un formato tabellare.
    - [x] **Colorazione condizionale:** Implementata la logica per colorare le righe di rosso se il prezzo è sotto la soglia e di verde se è sopra.

### Revisione del 28 Giugno 2025 (sera)

Lo script `monitor.py` è stato aggiornato con successo per presentare i dati in un formato tabellare e colorato, migliorando notevolmente la leggibilità dell'output. La libreria `colorama` è stata utilizzata per gestire la colorazione del testo nel terminale, con righe verdi per i titoli sopra la soglia e rosse per quelli sotto.

È stata corretta anche la logica di parsing dei prezzi, assicurando che i valori recuperati da Borsa Italiana siano normalizzati e visualizzati correttamente. Lo script ora fornisce una visione chiara e immediata dello stato dei titoli monitorati.

I prossimi passi potrebbero includere l'aggiunta di un sistema di logging più avanzato e la storicizzazione dei dati, come previsto nel piano originale.

### Aggiornamento del 1 Luglio 2025

- **Aggiunta Calcolo Cedola Netta:**
  - [x] **Aggiorna `config.json`**: Aggiunto il campo `cedola_annua` a ogni titolo.
  - [x] **Modifica `monitor.py`**:
    - [x] Letto `cedola_annua` dalla configurazione.
    - [x] Creata la funzione `calcola_cedola_netta` per calcolare la cedola netta su 1000 euro di investimento (aliquota 12.5%).
    - [x] Formattato l'output della cedola per i BTP come "X + X euro".
  - [x] **Aggiorna output**: Aggiunta la colonna "Cedola Netta Annua (1k)" alla tabella.
  - [x] **Revisione**: Riepilogo delle modifiche.

### Revisione del 1 Luglio 2025

Lo script `monitor.py` è stato esteso per calcolare e visualizzare la cedola annuale netta per un investimento di 1000 euro. Le principali modifiche includono:

- **Aggiornamento di `config.json`**: È stato aggiunto il campo `cedola_annua` a ciascun titolo per memorizzare il tasso di interesse lordo.
- **Nuova Funzione `calcola_cedola_netta`**: Questa funzione calcola il rendimento netto annuo, applicando una ritenuta fiscale del 12.5%. Per i BTP, la cedola viene visualizzata in formato semestrale (es. "17.72 + 17.72 euro") per riflettere la reale modalità di pagamento.
- **Output Migliorato**: La tabella di output ora include una nuova colonna che mostra la cedola netta, fornendo una visione più completa del rendimento di ogni titolo.

Queste modifiche rendono lo strumento di monitoraggio ancora più utile per l'analisi degli investimenti, offrendo una stima chiara del guadagno netto da cedole.
