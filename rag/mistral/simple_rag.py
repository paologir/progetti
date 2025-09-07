#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class SimpleRAG:
    def __init__(self):
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not self.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY non trovata nel file .env")
            
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.llm = None
        self.current_model = "mistral-tiny"  # Default model
        self.token_count = {"prompt": 0, "completion": 0, "total": 0}
        
    def load_index(self, index_path="faiss_index"):
        """Carica l'indice FAISS esistente"""
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Indice FAISS non trovato in {index_path}")
            
        self.vector_store = FAISS.load_local(
            index_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        print(f"Indice FAISS caricato da {index_path}")
        
    def setup_llm(self, model="mistral-tiny", temperature=0.1):
        """Inizializza il modello Mistral"""
        self.llm = ChatMistralAI(
            model_name=model, 
            mistral_api_key=self.mistral_api_key,
            temperature=temperature
        )
        self.current_model = model  # Salva il nome del modello
        print(f"Modello Mistral inizializzato: {model}")
    
    def estimate_tokens(self, text):
        """Stima approssimativa dei token (1 token ≈ 4 caratteri)"""
        # Per Mistral, questa è una stima rozza
        # In produzione, usare il tokenizer ufficiale
        return len(text) // 4
    
    def query(self, question, k=3):
        """Esegue una query RAG"""
        if not self.vector_store or not self.llm:
            raise RuntimeError("Inizializza prima load_index() e setup_llm()")
            
        # 1. Retrieval
        docs = self.vector_store.similarity_search(question, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Debug: mostra chunks recuperati
        print(f"\n--- Chunks recuperati (k={k}) ---")
        for i, doc in enumerate(docs):
            print(f"Chunk {i+1}: {doc.page_content[:100]}...")
        print("---\n")
        
        # 2. Prompt
        prompt_template = """Rispondi basandoti SOLO sul seguente contesto. Se non trovi informazioni sufficienti, dillo chiaramente.

Contesto:
{context}

Domanda: {question}

Risposta:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 3. Chain
        chain = prompt | self.llm | StrOutputParser()
        
        # 4. Calcola token del prompt
        full_prompt = prompt_template.format(context=context, question=question)
        prompt_tokens = self.estimate_tokens(full_prompt)
        self.token_count["prompt"] += prompt_tokens
        
        # 5. Genera risposta
        response = chain.invoke({"context": context, "question": question})
        
        # 6. Calcola token della risposta
        completion_tokens = self.estimate_tokens(response)
        self.token_count["completion"] += completion_tokens
        self.token_count["total"] = self.token_count["prompt"] + self.token_count["completion"]
        
        # 7. Calcola costi stimati in base al modello
        model_costs = {
            "mistral-tiny": {"input": 0.14, "output": 0.42},
            "mistral-small": {"input": 0.60, "output": 1.80},
            "mistral-medium": {"input": 2.50, "output": 7.50}
        }
        
        # Ottieni il nome del modello salvato
        model_name = self.current_model
        costs = model_costs.get(model_name, model_costs["mistral-tiny"])
        
        cost_input = prompt_tokens * costs["input"] / 1_000_000
        cost_output = completion_tokens * costs["output"] / 1_000_000
        cost_total = cost_input + cost_output
        
        token_info = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cumulative_total": self.token_count["total"],
            "estimated_cost": {
                "input": f"${cost_input:.6f}",
                "output": f"${cost_output:.6f}",
                "total": f"${cost_total:.6f}"
            }
        }
        
        return response, token_info

def main():
    """Esempio di utilizzo"""
    print("=== Mistral RAG MVP - Versione Semplificata ===\n")
    
    # Selezione modello
    print("Modelli Mistral disponibili:")
    print("1. mistral-tiny    ($0.14/1M input, $0.42/1M output) - Veloce ed economico")
    print("2. mistral-small   ($0.60/1M input, $1.80/1M output) - Bilanciato")
    print("3. mistral-medium  ($2.50/1M input, $7.50/1M output) - Più potente")
    
    while True:
        scelta = input("\nScegli il modello (1-3) [default: 1]: ").strip()
        if scelta == "" or scelta == "1":
            model_name = "mistral-tiny"
            break
        elif scelta == "2":
            model_name = "mistral-small"
            break
        elif scelta == "3":
            model_name = "mistral-medium"
            break
        else:
            print("Scelta non valida. Inserisci 1, 2 o 3.")
    
    print(f"\nModello selezionato: {model_name}")
    
    try:
        # Inizializza RAG
        rag = SimpleRAG()
        rag.load_index()
        rag.setup_llm(model=model_name)
        
        print("\nRAG pronto. Digita 'exit' per uscire.\n")
        
        while True:
            question = input("Domanda: ")
            if question.lower() in ['exit', 'quit', 'esci']:
                break
                
            if not question.strip():
                continue
                
            try:
                response, tokens = rag.query(question)
                
                print(f"\nRisposta: {response}")
                print(f"\n--- Token Usage ---")
                print(f"Prompt: {tokens['prompt_tokens']} tokens")
                print(f"Completion: {tokens['completion_tokens']} tokens")
                print(f"Totale query: {tokens['total_tokens']} tokens")
                print(f"Totale sessione: {tokens['cumulative_total']} tokens")
                print(f"Costo stimato query: {tokens['estimated_cost']['total']}")
                print("-" * 50 + "\n")
                
            except Exception as e:
                print(f"Errore: {e}\n")
                
    except Exception as e:
        print(f"Errore inizializzazione: {e}")

if __name__ == "__main__":
    main()