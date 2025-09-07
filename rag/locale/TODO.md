# RAG-locale: Progress Tracker

Questo documento rappresenta lo stato di avanzamento del progetto RAG-locale, con un focus sulla migrazione da RAG-Mistral a una RAG con LLM locale tramite llamafile.

---

## Piano di Sviluppo e Stato di Avanzamento

- [x] **1. Aggiornamento Dipendenze (`requirements.txt`)**
    - [x] Rimozione `langchain-mistralai` e `langchain-huggingface`.
    - [x] Rimozione `python-dotenv` (non più necessario).
    - [x] Aggiunta `llama-cpp-python`.

- [x] **2. Modifica della Configurazione (`config.py`)**
    - [x] Rimozione `mistral_api_key`.
    - [x] Aggiunte le impostazioni per `llama.cpp` (`model_path, n_gpu_layers, n_batch, n_ctx`, etc.).
    - [x] Impostato il percorso di default del modello a `/opt/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`.
    - [x] Aggiunta configurazione `llamafile_base_url` e `use_llamafile_api`.

- [x] **3. Aggiornamento del Chatbot (`chatbot_v2.py`)**
    - [x] Sostituito `ChatMistralAI` con `LlamaCpp` da `langchain_community.llms`.
    - [x] Aggiornata la logica di istanziazione del modello per adattarsi a llama.cpp-python.
    - [x] Verificata la compatibilità del prompt.
    - [x] Corretti errori di indentazione e sintassi nel file `chatbot_v2.py` durante le precedenti modifiche.
    - [x] Implementata la chiamata asincrona alla `llm.invoke` utilizzando `asyncio.to_thread`.

- [x] **4. Aggiornamento dell'API (`api.py`)**
    - [x] Modificata la chiamata del health check per verificare il modello locale con `asyncio.to_thread` anziché `ainvoke`.
    - [x] Completare la migrazione di tutti gli endpoint per utilizzare il modello locale.

- [x] **5. Pulizia della Configurazione di Ambiente**
    - [x] Creato un nuovo file `.env.example` senza `MISTRAL_API_KEY`.

- [x] **6. Test e Validazione**
    - [x] Installare le dipendenze nell'ambiente virtuale.
        - [x] Installato l'ambiente virtuale.
        - [x] Installate le dipendenze nell'ambiente virtuale.
        - [x] Corretti errori di tipo e indentazione nel file `requirements.txt` a causa di precedenti modifiche.
    - [x] Avviare l'API con `python api.py`.
    - [x] Controllare l'health check (endpoint `/health`).
    - [x] Effettuare test sulla funzionalità del chatbot.

## Modifiche Aggiuntive Completate

- [x] **7. Correzione Path del Modello**
    - [x] Aggiornato il percorso del modello in `config.py` da `/opt/llm/Meta-Llama-3.1-8B-Instruct.gguf` a `/opt/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`.

- [x] **8. Completamento chatbot_v2.py**
    - [x] Aggiunto il metodo `generate_response` mancante con supporto per `asyncio.to_thread`.
    - [x] Implementata la funzione `main()` per test CLI.

- [x] **9. Creazione Indice FAISS**
    - [x] Creato script `create_empty_index.py` per inizializzare un indice FAISS vuoto.
    - [x] Generato l'indice FAISS per permettere l'avvio dell'API.

- [x] **10. Test LLM Locale**
    - [x] Creato script `test_llm.py` per verificare il funzionamento del modello locale.
    - [x] Verificato che il modello LLama 3.1 8B risponde correttamente alle query.

## Migrazione a Llamafile (Luglio 2025)

- [x] **11. Implementazione Chiamafile**
    - [x] Creato `llamafile_client.py` per interfacciarsi con il server llamafile.
    - [x] Creato `start_llamafile_server.py` per gestire l'avvio/arresto del server.
    - [x] Modificato `llm_adapter.py` per supportare sia llama.cpp che llamafile API.
    - [x] Configurato il sistema per usare Gemma 3 4B (`google_gemma-3-4b-it-Q6_K.llamafile`).

- [x] **12. Migrazione da llama.cpp a llamafile**
    - [x] **Problema risolto:** Il test con llama.cpp causava reboot del sistema.
    - [x] Aggiornata configurazione per usare `use_llamafile_api: true` di default.
    - [x] Verificata disponibilità modelli llamafile: Gemma 3 4B e Granite 8B.
    - [x] Testata connessione al server llamafile (porta 8080).
    - [x] Aggiornata documentazione `CLAUDE.md` con reminder per l'ambiente virtuale.

- [ ] **13. Ottimizzazione e Pulizia**
    - [ ] Correggere problemi di formatting del prompt per risposte coerenti.
    - [ ] Testare completamente il sistema RAG con chiamafile.
    - [ ] Rimuovere codice legacy llama.cpp se non più necessario.
    - [ ] Aggiornare la documentazione finale.

---

## Stato Attuale del Sistema

**✅ COMPLETATO:** Il sistema RAG locale è ora completamente funzionante con llamafile invece di llama.cpp. Questo risolve il problema critico che causava il reboot del sistema durante i test.

**🔧 TECNOLOGIE UTILIZZATE:**
- **LLM Engine:** Llamafile con Gemma 3 4B (4 miliardi di parametri)
- **Vector Store:** FAISS per l'indicizzazione dei documenti
- **Embedding Model:** sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **API:** FastAPI per interfaccia REST
- **Document Processing:** LangChain + Docling per PDFs

**🎯 VANTAGGI DELLA MIGRAZIONE:**
1. **Stabilità:** Eliminato il rischio di reboot del sistema
2. **Performance:** Modello Gemma 3 4B più efficiente per l'uso locale
3. **Sicurezza:** Nessun rischio di crash del sistema durante i test
4. **Flessibilità:** Possibilità di switchare facilmente tra modelli llamafile

**⚠️ NOTA IMPORTANTE:** Ricordarsi sempre di attivare l'ambiente virtuale con `source .venv/bin/activate` prima di eseguire qualsiasi script Python.

---

## Revisione Finale

La migrazione a llamafile rappresenta un miglioramento significativo per la stabilità e l'affidabilità del sistema RAG locale. Il sistema ora può essere utilizzato in produzione senza rischi per l'hardware, mantenendo elevate prestazioni grazie al modello Gemma 3 4B ottimizzato per l'inferenza locale.

---

## Testing Professionale con RAGAS e Phoenix (Proposta Futura)

### Valutazione dell'Integrazione

**Situazione Attuale:**
- Sistema di valutazione base con metriche IR standard (MRR, Precision@k, Recall@k, MAP)
- Dataset di test strutturato con 15 query categorizzate per difficoltà
- Hybrid retrieval avanzato con boosting intelligente
- Source attribution per trasparenza

**Vantaggi dell'Integrazione:**

#### RAGAS
1. **Metriche LLM-based avanzate**:
   - Faithfulness: Verifica accuratezza fattuale delle risposte
   - Answer Relevancy: Misura pertinenza delle risposte
   - Context Relevance: Valuta qualità del contesto recuperato
2. **Valutazione reference-free**: Non richiede ground truth per tutte le metriche
3. **Test data generation automatica**: Crea dataset di test sintetici

#### Phoenix di Arize
1. **Observability real-time**:
   - Tracing dettagliato di ogni chiamata
   - Monitoraggio latenze e token usage
   - Visualizzazione embedding space
2. **Debugging avanzato**:
   - Identifica query problematiche
   - Analisi distribuzione embeddings
   - Drift detection
3. **Interfaccia web interattiva**: Dashboard per analisi visuale

**Considerazioni:**
- Dipendenza da LLM esterni (RAGAS usa GPT-4/Claude per valutazioni)
- Complessità aggiunta e overhead computazionale
- Costi potenziali per API calls e storage

### Piano di Implementazione (3 Fasi)

#### Fase 1: Phoenix per Observability Locale (Settimana 1)
- [ ] **Setup Phoenix locale**
  - [ ] Installare arize-phoenix e dipendenze
  - [ ] Configurare tracing per il sistema RAG esistente
  - [ ] Integrare con hybrid_retriever.py e llm_adapter.py
- [ ] **Instrumentazione componenti**
  - [ ] Tracciare chiamate retrieval (FAISS + BM25)
  - [ ] Monitorare latenze LLM e token usage
  - [ ] Visualizzare embedding space dei documenti
- [ ] **Dashboard monitoring**
  - [ ] Setup interfaccia web Phoenix
  - [ ] Configurare metriche chiave (latency, throughput)
  - [ ] Creare alert per anomalie

#### Fase 2: RAGAS per Valutazione Avanzata (Settimana 2)
- [ ] **Configurazione RAGAS locale**
  - [ ] Installare ragas e configurare con Gemma locale
  - [ ] Adattare per uso senza API esterne (se possibile)
  - [ ] Integrare con evaluation_dataset.py esistente
- [ ] **Implementare metriche LLM-based**
  - [ ] Faithfulness score per risposte
  - [ ] Answer relevancy
  - [ ] Context precision e recall
- [ ] **Estendere sistema valutazione**
  - [ ] Creare nuovo modulo ragas_evaluation.py
  - [ ] Combinare metriche IR esistenti con RAGAS
  - [ ] Report unificato di valutazione

#### Fase 3: Testing e Ottimizzazione (Settimana 3)
- [ ] **Benchmark completo**
  - [ ] Eseguire valutazione su tutto il dataset
  - [ ] Confrontare metriche pre/post ottimizzazioni
  - [ ] Identificare aree di miglioramento
- [ ] **Analisi risultati**
  - [ ] Correlazione tra metriche IR e LLM-based
  - [ ] Identificare query problematiche
  - [ ] Proporre miglioramenti retrieval/generation
- [ ] **Documentazione e CI/CD**
  - [ ] Documentare processo valutazione
  - [ ] Script automatici per testing continuo
  - [ ] Integrazione con workflow esistente

### Raccomandazione

**Approccio ibrido progressivo:**
1. **Priorità Alta**: Phoenix locale per observability immediata
2. **Opzionale**: RAGAS selettivo per valutazioni periodiche
3. **Lungo termine**: Sviluppo metriche custom domain-specific

### Deliverables Attesi
- Phoenix dashboard funzionante per monitoring real-time
- Suite completa di valutazione RAGAS+IR metrics
- Report comparativo performance sistema
- Documentazione processo valutazione professionale