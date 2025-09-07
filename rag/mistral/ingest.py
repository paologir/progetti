# ingest.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv() # Carica le variabili dal file .env

DOCUMENTS_PATH = "documents"
FAISS_INDEX_PATH = "faiss_index"

def load_documents(path):
    documents = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            documents.extend(loader.load())
            print(f"Caricato {filename} ({len(loader.load())} pagine)")
        elif filename.endswith(".md"):
            loader = UnstructuredMarkdownLoader(filepath)
            documents.extend(loader.load())
            print(f"Caricato {filename} ({len(loader.load())} documenti)")
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding='utf-8') # Specifica encoding se necessario
            documents.extend(loader.load())
            print(f"Caricato {filename} ({len(loader.load())} documenti)")
        else:
            print(f"Formato file non supportato per {filename}, skipping.")
    return documents

def main():
    print("Avvio processo di ingestione...")

    # 1. Caricamento documenti
    print(f"Caricamento documenti da: {DOCUMENTS_PATH}")
    raw_documents = load_documents(DOCUMENTS_PATH)
    if not raw_documents:
        print("Nessun documento caricato. Verifica la directory 'documents'.")
        return
    print(f"Totale documenti/pagine caricate: {len(raw_documents)}")

    # 2. Suddivisione in chunk
    print("Suddivisione documenti in chunk...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Dimensione dei chunk
        chunk_overlap=100 # Sovrapposizione tra chunk
    )
    docs_chunks = text_splitter.split_documents(raw_documents)
    print(f"Numero di chunk creati: {len(docs_chunks)}")
    if not docs_chunks:
        print("Nessun chunk creato. Verifica il contenuto dei documenti.")
        return

    # 3. Creazione Embeddings
    print("Creazione embeddings (modello: all-MiniLM-L6-v2)...")
    # Per italiano, potresti considerare 'paraphrase-multilingual-MiniLM-L12-v2'
    # ma 'all-MiniLM-L6-v2' è più leggero e spesso sufficiente per iniziare.
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Creazione e salvataggio dell'indice FAISS
    print("Creazione e salvataggio dell'indice FAISS...")
    try:
        vector_store = FAISS.from_documents(docs_chunks, embeddings_model)
        vector_store.save_local(FAISS_INDEX_PATH)
        print(f"Indice FAISS salvato in: {FAISS_INDEX_PATH}")
    except Exception as e:
        print(f"Errore durante la creazione o il salvataggio dell'indice FAISS: {e}")
        print("Assicurati che ci siano chunk validi e che il modello di embedding sia caricato correttamente.")

    print("Processo di ingestione completato.")

if __name__ == "__main__":
    main()