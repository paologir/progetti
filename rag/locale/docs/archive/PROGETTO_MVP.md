# Progetto Mistral RAG MVP - Documento di Sviluppo

## 1. Panoramica del Sistema

Il sistema Mistral RAG MVP è un'applicazione di Retrieval Augmented Generation che utilizza:
- **Embeddings locali**: HuggingFace Sentence Transformers
- **Vector Store**: FAISS per indicizzazione e ricerca
- **LLM**: API Mistral per generazione risposte
- **Framework**: LangChain per orchestrazione

## 2. Architettura Attuale

### Componenti Principali:
1. **ingest.py**: Carica documenti, crea chunks e genera embeddings
2. **chatbot.py**: Interfaccia CLI per interrogare la knowledge base
3. **config.py**: Configurazione centralizzata (usa Pydantic)
4. **core/vector_store.py**: Astrazione avanzata per vector stores

### Flusso di Lavoro:
1. Documenti → Chunking → Embeddings → FAISS Index
2. Query utente → Retrieval → Contesto → Mistral API → Risposta

## 3. Configurazione Minima per MVP

### 3.1 Setup Ambiente

```bash
# 1. Creare virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 2. Installare dipendenze minime
pip install langchain langchain-community langchain-mistralai langchain-huggingface
pip install faiss-cpu sentence-transformers python-dotenv
pip install pypdf unstructured

# 3. Creare file .env
echo "MISTRAL_API_KEY=your_api_key_here" > .env
```

### 3.2 Struttura Directory
```
mistral_rag_mvp/
├── documents/          # Documenti da indicizzare
├── faiss_index/        # Index FAISS salvato
├── .env               # API key Mistral
├── ingest.py          # Script ingestione
├── chatbot.py         # Interfaccia chat
└── simple_rag.py      # Versione semplificata (da creare)
```

## 4. Versione Semplificata con Token Tracking

### 4.1 Script Semplificato (simple_rag.py)

```python
#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import tiktoken

load_dotenv()

class SimpleRAG:
    def __init__(self):
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.llm = None
        self.token_count = {"prompt": 0, "completion": 0, "total": 0}
        
    def load_index(self):
        """Carica l'indice FAISS esistente"""
        self.vector_store = FAISS.load_local(
            "faiss_index", 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        
    def setup_llm(self, model="mistral-tiny", temperature=0.1):
        """Inizializza il modello Mistral"""
        self.llm = ChatMistralAI(
            model_name=model, 
            mistral_api_key=self.mistral_api_key,
            temperature=temperature
        )
    
    def count_tokens(self, text, model="mistral"):
        """Stima approssimativa dei token"""
        # Mistral usa una tokenizzazione simile a GPT
        # Per una stima accurata servirebbe il tokenizer Mistral
        # Usiamo cl100k_base come approssimazione
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback: stima rozza (1 token ≈ 4 caratteri)
            return len(text) // 4
    
    def query(self, question, k=3):
        """Esegue una query RAG"""
        # 1. Retrieval
        docs = self.vector_store.similarity_search(question, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 2. Prompt
        prompt_template = """Rispondi basandoti SOLO sul seguente contesto:

Contesto:
{context}

Domanda: {question}

Risposta:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 3. Chain
        chain = prompt | self.llm | StrOutputParser()
        
        # 4. Calcola token del prompt
        full_prompt = prompt_template.format(context=context, question=question)
        prompt_tokens = self.count_tokens(full_prompt)
        self.token_count["prompt"] += prompt_tokens
        
        # 5. Genera risposta
        response = chain.invoke({"context": context, "question": question})
        
        # 6. Calcola token della risposta
        completion_tokens = self.count_tokens(response)
        self.token_count["completion"] += completion_tokens
        self.token_count["total"] = self.token_count["prompt"] + self.token_count["completion"]
        
        return response, {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cumulative_total": self.token_count["total"]
        }
```

## 5. Stima Costi Token Mistral

### Prezzi Mistral AI (Dicembre 2024):
- **mistral-tiny**: $0.14 / 1M input tokens, $0.42 / 1M output tokens
- **mistral-small**: $0.6 / 1M input tokens, $1.8 / 1M output tokens
- **mistral-medium**: $2.5 / 1M input tokens, $7.5 / 1M output tokens

### Esempio Calcolo per Query Tipica:
- Contesto (3 chunks × 1000 char): ~750 tokens
- Prompt sistema + domanda: ~100 tokens
- **Input totale**: ~850 tokens
- **Output medio**: ~150 tokens

**Costo per query (mistral-tiny)**:
- Input: 850 × $0.14 / 1M = $0.000119
- Output: 150 × $0.42 / 1M = $0.000063
- **Totale**: ~$0.00018 per query

## 6. Testing e Validazione

### 6.1 Test Base
```python
# test_rag.py
from simple_rag import SimpleRAG

rag = SimpleRAG()
rag.load_index()
rag.setup_llm()

# Test query
response, tokens = rag.query("Cos'è il RAG?")
print(f"Risposta: {response}")
print(f"Token utilizzati: {tokens}")
```

### 6.2 Metriche da Monitorare
1. **Latenza**: Tempo retrieval + tempo generazione
2. **Qualità retrieval**: Rilevanza dei chunks recuperati
3. **Token consumption**: Token per query e costi associati
4. **Accuracy**: Correttezza delle risposte

## 7. Prossimi Passi

### Fase 1 - MVP Base (Immediato)
- [ ] Creare simple_rag.py con tracking token
- [ ] Test con documenti di esempio
- [ ] Validare funzionamento end-to-end

### Fase 2 - Ottimizzazioni (1-2 settimane)
- [ ] Cache per query frequenti
- [ ] Batch processing per ingestione
- [ ] Migliorare chunking strategy
- [ ] API REST con FastAPI

### Fase 3 - Produzione (2-4 settimane)
- [ ] Autenticazione e rate limiting
- [ ] Monitoring e logging strutturato
- [ ] UI web base
- [ ] Deploy containerizzato

## 8. Note Implementative

### Considerazioni Performance:
1. **Embeddings**: all-MiniLM-L6-v2 è veloce ma per italiano considerare modelli multilingua
2. **Chunk size**: 1000 caratteri è un buon compromesso, ma dipende dal dominio
3. **Top-k**: 3-5 chunks bilanciano contesto e costi

### Sicurezza:
1. Mai esporre MISTRAL_API_KEY nel codice
2. Validare sempre input utente
3. Limitare dimensione file upload
4. Sanitizzare output LLM se mostrato in web UI

### Debug:
1. Loggare chunks recuperati per analisi qualità
2. Tracciare token usage per ottimizzazione costi
3. Monitorare latenze per identificare bottleneck