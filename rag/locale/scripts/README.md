# Script RAG Locale - Versione Semplificata

Questi script permettono di usare il sistema RAG migliorato da qualsiasi directory.

## Script Principali

### `rag-ingest`
Script per l'ingestione dei documenti dalla Knowledge Base Obsidian nel sistema RAG.
- **Utilizzo**: `rag-ingest`
- **Funzione**: Processa i documenti da `/opt/obsidian/appunti/` e crea l'indice FAISS
- **Output**: Crea/aggiorna la directory `obsidian_index/`

### `rag-query` 
Script per interrogare il sistema RAG con le domande.
- **Utilizzo**: `rag-query`
- **Funzione**: Interfaccia interattiva per fare domande al sistema
- **Caratteristiche**: 
  - Token limit aumentato a 2048 (risposte complete)
  - K dinamico (fino a 50 per query di ricerca file)
  - Pattern matching intelligente
  - UI migliorata con box completi

## Installazione Produzione

Per l'ambiente di produzione, copiare solo gli script wrapper in `/home/paolo/script/llm/`:

```bash
# Assicurarsi che la directory esista
mkdir -p /home/paolo/script/llm

# Copiare solo gli script wrapper (leggeri)
cp rag-query rag-ingest /home/paolo/script/llm/
chmod +x /home/paolo/script/llm/rag-*
```

Gli script wrapper:
1. **Sono eseguiti** da `/home/paolo/script/llm/` (nel PATH)
2. **Lavorano sui file** in `/opt/progetti/RAG-locale/` (directory fissa)
3. **Non richiedono** duplicazione dei file Python
4. **Modalità CLI**: Usano llamafile CLI diretto (no server HTTP)

## Esempi Query Migliorate

- **File specifici**: "Per quali clienti ho scritto un file corpus?"
- **Clienti**: "Quali sono i concorrenti di Didonè Comacchio?"  
- **Date/Journal**: "Cosa ho fatto oggi?" / "Attività del 15/08/2024"

## Miglioramenti Implementati

- ✅ **Token limit**: 1024 → 2048 (risposte non più tagliate)
- ✅ **K dinamico ottimizzato**: File search=25 (vs 50 precedente), deduplicazione intelligente
- ✅ **Pattern matching**: Riconoscimento automatico query tipo "quali clienti hanno file X"
- ✅ **UI copy-friendly**: Output senza bordi laterali per facile copia testo
- ✅ **Link cliccabili**: Apertura file dalle fonti con path corretti
- ✅ **GPU disabilitata**: Maggiore stabilità, no crash
- ✅ **Context overflow**: Risolto problema blocco retrieval

## Configurazione

### Directory di Lavoro
Gli script wrapper usano sempre la directory fissa:
- **Progetto**: `/opt/progetti/RAG-locale/` (hardcoded)
- **Scripts**: Eseguibili da `/home/paolo/script/llm/` (nel PATH)
- **Semplice**: Nessuna configurazione di path necessaria

### Variabili Opzionali
```bash
export SHOW_TOKENS=true    # Mostra conteggio token in rag-query
export DEBUG_RAG=true      # Modalità debug con chunk recuperati
```

## Note

- Gli script gestiscono automaticamente l'ambiente virtuale Python
- Il sistema ora usa llamafile CLI (no server HTTP, maggiore stabilità)
- L'indice deve essere creato con `rag-ingest` prima di usare `rag-query`
- Gli script tornano sempre alla directory originale dopo l'esecuzione