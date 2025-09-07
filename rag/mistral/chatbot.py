#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# chatbot.py
import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda # Aggiungi RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document # Per il type hinting se necessario

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
FAISS_INDEX_PATH = "faiss_index"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K_CHUNKS = 3

def format_docs(docs: list[Document]) -> str: # Aggiunto type hint
    """Formatta i documenti recuperati in una stringa unica per il contesto."""
    return "\n\n---\n\n".join([d.page_content for d in docs])

def debug_retrieved_chunks(query: str, retrieved_docs: list[Document]): # Aggiunto type hint
    """Stampa i chunk recuperati per il debug."""
    print(f"\n--- DEBUG: Query dell'utente: {query} ---")
    print(f"--- DEBUG: Chunk Recuperati (TOP_K_CHUNKS={TOP_K_CHUNKS}) ---")
    if retrieved_docs:
        for i, doc in enumerate(retrieved_docs):
            print(f"\nDEBUG CHUNK {i+1}:")
            if isinstance(doc, tuple) and len(doc) == 2 and isinstance(doc[1], float):
                print(f"Score: {doc[1]}")
                print(doc[0].page_content)
                print("Metadata:", doc[0].metadata if hasattr(doc[0], 'metadata') else "N/A")
            else:
                print(doc.page_content)
                print("Metadata:", doc.metadata if hasattr(doc, 'metadata') else "N/A")
            print("--------------------")
    else:
        print("DEBUG: Nessun chunk recuperato.")
    print("--- FINE DEBUG CHUNKS ---\n")

def main():
    if not MISTRAL_API_KEY:
        print("MISTRAL_API_KEY non trovata. Assicurati sia nel file .env")
        return

    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"Indice FAISS non trovato in {FAISS_INDEX_PATH}. Esegui prima ingest.py.")
        return

    print("Caricamento embedder e indice FAISS...")
    try:
        embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    except Exception as e:
        print(f"Errore nell'inizializzazione del modello di embedding ({EMBEDDING_MODEL_NAME}): {e}")
        return

    try:
        vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings_model, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Errore nel caricamento dell'indice FAISS: {e}")
        return

    retriever = vector_store.as_retriever(search_kwargs={"k": TOP_K_CHUNKS})

    try:
        llm = ChatMistralAI(model_name="mistral-tiny", mistral_api_key=MISTRAL_API_KEY, temperature=0.1)
    except Exception as e:
        print(f"Errore nell'inizializzazione del modello ChatMistralAI: {e}")
        return

    prompt_template_str = """
    Sei un assistente virtuale. Il tuo compito è rispondere alle domande degli utenti basandoti ESCLUSIVAMENTE sulle informazioni fornite nel seguente contesto.
    Non devi MAI inventare informazioni o usare conoscenze esterne.
    Il tuo tono deve essere professionale, conciso e utile.
    Se le informazioni nel contesto non sono sufficienti per rispondere alla domanda, rispondi:
    "Mi dispiace, non ho trovato informazioni sufficienti nei documenti forniti per rispondere alla tua domanda."
    Non aggiungere frasi come "Spero questo aiuti" o simili. Sii diretto.
    Non fare riferimento a te stesso come "un modello linguistico" o "un'IA".

    Contesto fornito:
    {context}

    Domanda dell'utente:
    {question}

    Risposta:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template_str)

    # Definiamo una funzione che il RunnableLambda possa chiamare
    # Questa funzione prenderà l'output del retriever (la query) e lo userà
    def retrieve_and_debug_runnable(query: str):
        retrieved_docs = retriever.invoke(query)
        debug_retrieved_chunks(query, retrieved_docs) # Chiamiamo la nostra funzione di debug
        return retrieved_docs # Ritorniamo i documenti per la catena successiva

    # Creazione della catena RAG
    rag_chain = (
        {
            "context": RunnableLambda(retrieve_and_debug_runnable) | format_docs, # Usiamo RunnableLambda
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("\nChatbot RAG inizializzato. Digita 'esci' per terminare.")
    print("----------------------------------------------------")

    while True:
        user_query = input("Tu: ")
        if user_query.lower() == 'esci':
            break
        if not user_query.strip():
            continue

        print("Bot: Sto pensando...")
        try:
            # Quando invochiamo la catena, la query utente (user_query)
            # viene passata come input a `retrieve_and_debug_runnable`
            # e anche a "question": RunnablePassthrough()
            response = rag_chain.invoke(user_query)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"Bot: Si è verificato un errore: {e}")
            # import traceback
            # traceback.print_exc()
        print("----------------------------------------------------")

if __name__ == "__main__":
    main()