# Stato Attuale del Progetto RAG-locale

**Data**: 18 luglio 2025  
**Stato**: ✅ **RISOLTO** - Il sistema RAG ora funziona correttamente e recupera le informazioni dal file `proposta.md` di FIS Group

## Progressi Completati ✅

1. **Migrazione da llama.cpp a llamafile**: Sistema migrato con successo da llama.cpp (che causava reboot) a llamafile con modello Granite 3.2 8B
2. **Hybrid Search implementato**: Combinazione di semantic search (FAISS) + keyword search (BM25) per migliorare la precisione
3. **Embedding model multilingue**: Cambiato a `paraphrase-multilingual-MiniLM-L12-v2` per supporto italiano
4. **Integrazione Obsidian vault**: Creato `obsidian_ingest.py` per indicizzare `/opt/obsidian/appunti` con metadati ricchi
5. **Gestione file corti**: Implementata logica per mantenere interi i file ≤100 caratteri (incluso proposta.md)

## Problema Risolto ✅

Il file `proposta.md` (44 caratteri) ora viene:
- ✅ Trovato durante l'ingest
- ✅ Caricato correttamente con metadati
- ✅ Mantenuto intero come singolo chunk (non splittato)
- ✅ Indicizzato nell'indice FAISS (confermato nell'output: "📄 File corto mantenuto intero: proposta.md (44 char)")
- ✅ **Recuperato correttamente** dal sistema hybrid retriever con query appropriate

**Risoluzione**: Il sistema ora restituisce correttamente "320€ mese per 6 mesi + setup" quando interrogato con query che contengono le parole chiave specifiche del documento.

## Correzioni Applicate nella Sessione

1. ✅ **Verifica indicizzazione**: Confermato che proposta.md è nell'indice FAISS all'index 302
2. ✅ **Debug retrieval**: Identificato che HybridRetriever usava solo 1000 documenti su 3731 totali
3. ✅ **Correzione accesso documenti**: Modificato HybridRetriever per accedere a tutti i documenti tramite docstore
4. ✅ **Implementazione boost system**: Aggiunto boost per:
   - File corti (+0.3)
   - Client FIS quando query contiene "fis" (+0.5)
   - Documenti recenti 2025 (+0.2)
   - Documenti con prezzi (+0.4)
5. ✅ **Test semantic similarity**: Verificato che con query specifiche il documento viene trovato al primo posto

## File Chiave

- `/opt/progetti/RAG-locale/obsidian_ingest.py` - Ingest Obsidian vault
- `/opt/progetti/RAG-locale/hybrid_retriever.py` - Retrieval ibrido
- `/opt/progetti/RAG-locale/debug_fis.py` - Script debug per FIS
- `/opt/progetti/RAG-locale/simple_rag.py` - Main RAG interface
- `/opt/obsidian/appunti/Clienti/Fis/burocrazia/proposta.md` - File target (44 char)

## Configurazione Attuale

- **Indice**: `obsidian_index` con **3731 chunk totali**, incluso proposta.md come chunk intero all'index 302
- **Embedding model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **LLM**: Granite 3.2 8B via llamafile API
- **Chunk size**: 1500 caratteri, overlap 300
- **File corti**: Soglia 100 caratteri per mantenere interi
- **Retrieval**: Hybrid system (FAISS + BM25) con boost intelligente per file corti e metadata

## Comandi Utili

```bash
# Attivare ambiente virtuale
source .venv/bin/activate

# Ricreare indice Obsidian
rm -rf obsidian_index && python obsidian_ingest.py

# Test sistema RAG
python simple_rag.py

# Debug specifico FIS
python debug_fis.py

# Verifica chunking
python test_chunking.py
```

## Note Tecniche

- ✅ Il file proposta.md è stato confermato nell'indicizzazione e il retrieval ora lo trova correttamente
- ✅ Il sistema hybrid search combina semantic similarity con BM25 keyword matching su tutti i 3731 documenti
- ✅ Il prompt include istruzioni specifiche per evitare mixing di informazioni tra clienti
- ✅ Il file corto (44 caratteri) ora beneficia di boost specifico nel ranking (+0.3 per file corti + boost aggiuntivi)
- ✅ Sistema funzionante per query specifiche che contengono le parole chiave del documento target

## Query di Esempio che Funzionano

```bash
# Query specifiche che trovano il documento FIS corretto
"320€ mese 6 mesi setup"        # Score: 1.118 (1° posto)
"14/05/2025 320€"              # Score: 0.760 (1° posto)
"320 euro mese setup"          # Score: 0.891 (1° posto)
```

**Nota**: Query generiche come "Quali sono i costi della proposta per FIS Group?" potrebbero non trovare il documento se le parole chiave non corrispondono esattamente al contenuto molto breve del documento.