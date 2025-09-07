#!/usr/bin/env python3
import os
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_adapter import LLMAdapter
from config import settings
from hybrid_retriever import HybridRetriever

# Classe per gestire output colorato nel terminale
class ColoredOutput:
    # Colori ANSI
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colori testo
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Colori background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @staticmethod
    def colored(text, color='', bold=False, dim=False):
        """Restituisce testo colorato per il terminale"""
        if not sys.stdout.isatty():
            return text
        
        prefix = ''
        if bold:
            prefix += ColoredOutput.BOLD
        if dim:
            prefix += ColoredOutput.DIM
        if color:
            prefix += color
            
        if prefix:
            return f"{prefix}{text}{ColoredOutput.RESET}"
        return text
    
    @staticmethod
    def print_header(text):
        """Stampa un header colorato"""
        border = "═" * 60
        print(ColoredOutput.colored(border, ColoredOutput.BLUE, bold=True))
        print(ColoredOutput.colored(f"  {text}", ColoredOutput.CYAN, bold=True))
        print(ColoredOutput.colored(border, ColoredOutput.BLUE, bold=True))
    
    @staticmethod
    def print_separator():
        """Stampa un separatore"""
        print(ColoredOutput.colored("─" * 60, ColoredOutput.DIM))
    
    @staticmethod
    def print_success(text):
        """Stampa messaggio di successo"""
        print(ColoredOutput.colored(f"✓ {text}", ColoredOutput.GREEN))
    
    @staticmethod
    def print_error(text):
        """Stampa messaggio di errore"""
        print(ColoredOutput.colored(f"✗ {text}", ColoredOutput.RED))
    
    @staticmethod
    def print_info(text):
        """Stampa messaggio informativo"""
        print(ColoredOutput.colored(f"→ {text}", ColoredOutput.YELLOW))
    
    @staticmethod
    def print_response(text):
        """Stampa la risposta del bot senza bordi laterali per facilitare la copia"""
        print()
        # Header con titolo
        print(ColoredOutput.colored("╭─ Risposta ", ColoredOutput.GREEN, bold=True) + 
              ColoredOutput.colored("─" * 47, ColoredOutput.DIM) +
              ColoredOutput.colored("╮", ColoredOutput.DIM))
        print()
        
        # Testo della risposta senza bordi laterali
        lines = text.split('\n')
        for line in lines:
            print(line)
        
        # Footer separatore
        print()
        print(ColoredOutput.colored("╰" + "─" * 59 + "╯", ColoredOutput.DIM))
        print()
    
    @staticmethod
    def print_sources(sources):
        """Stampa le fonti consultate con formattazione colorata e link cliccabili"""
        print(ColoredOutput.colored("\n📄 Fonti consultate:", ColoredOutput.MAGENTA, bold=True))
        
        # Controlla se il terminale supporta i link (OSC 8)
        is_interactive = sys.stdout.isatty()
        
        for i, source in enumerate(sources, 1):
            # Costruisci il path completo del file
            # Assumiamo che i file siano in /opt/obsidian/appunti/Clienti/
            base_path = "/opt/obsidian/appunti/"
            
            # Gestisci diversi formati di source
            if source.startswith("Journal/"):
                # File Journal
                filename = source.replace("Journal/", "")
                full_path = os.path.join(base_path, "Journal", filename)
            elif source.startswith("Paolo/"):
                # File personali
                full_path = os.path.join(base_path, source)
            elif source.startswith("Tact/Clienti/"):
                # File Tact clienti
                full_path = os.path.join(base_path, source)
            elif source.startswith("Tact/"):
                # File Tact generali
                full_path = os.path.join(base_path, source)
            elif "/" in source:
                # File cliente standard
                cliente, filename = source.split("/", 1)
                full_path = os.path.join(base_path, "Clienti", cliente, filename)
            else:
                # Altri file
                full_path = os.path.join(base_path, source)
            
            # Se il terminale è interattivo, aggiungi info su come aprire
            if is_interactive:
                # Mostra il percorso con un numero per riferimento facile
                print(ColoredOutput.colored(f"   [{i}] {source}", ColoredOutput.CYAN))
                print(ColoredOutput.colored(f"       📂 {full_path}", ColoredOutput.DIM))
            else:
                print(ColoredOutput.colored(f"   • {source}", ColoredOutput.CYAN))

class SimpleRAG:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
        self.vector_store = None
        self.hybrid_retriever = HybridRetriever(faiss_index_path="obsidian_index")
        self.llm = None
        self.current_model = "llamafile"  # Default model
        self.token_count = {"prompt": 0, "completion": 0, "total": 0}
        
    def load_index(self, index_path="obsidian_index"):
        """Carica l'indice FAISS esistente"""
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Indice FAISS non trovato in {index_path}")
            
        self.vector_store = FAISS.load_local(
            index_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        ColoredOutput.print_success(f"Indice FAISS caricato da {index_path}")
        
        # Carica anche il hybrid retriever
        self.hybrid_retriever.load_index()
        
    def setup_llm(self, model="llamafile", temperature=0.1):
        """Inizializza il modello locale"""
        self.llm = LLMAdapter()
        self.current_model = model  # Salva il nome del modello
        if self.llm.is_available():
            ColoredOutput.print_success(f"Modello locale inizializzato: {self.llm.llm_type}")
        else:
            raise RuntimeError("Modello locale non disponibile")
    
    def estimate_tokens(self, text):
        """Stima approssimativa dei token (1 token ≈ 4 caratteri)"""
        # Per Mistral, questa è una stima rozza
        # In produzione, usare il tokenizer ufficiale
        return len(text) // 4
    
    def query(self, question, k=3):
        """Esegue una query RAG con k dinamico basato sul tipo di query"""
        if not self.vector_store or not self.llm:
            raise RuntimeError("Inizializza prima load_index() e setup_llm()")
            
        # Rileva se la query riguarda attività/lista di un giorno specifico
        import re
        from datetime import datetime, timedelta
        
        is_journal_list_query = False
        target_journal_date = None
        query_lower = question.lower()
        
        # Pattern per query "quali clienti hanno file X"
        file_search_patterns = [
            r'quali clienti.*\b(corpus|concorrenti|dati|analisi|interventi)\b',
            r'per quali.*\b(corpus|concorrenti|dati|analisi|interventi)\b',
            r'elenco.*clienti.*\b(corpus|concorrenti|dati|analisi|interventi)\b',
            r'lista.*clienti.*\b(corpus|concorrenti|dati|analisi|interventi)\b',
            r'tutti.*\b(corpus|concorrenti|dati|analisi|interventi)\b.*clienti',
        ]
        
        # Controlla se è una query di ricerca file specifici
        is_file_search_query = False
        target_file_type = None
        for pattern in file_search_patterns:
            match = re.search(pattern, query_lower)
            if match:
                is_file_search_query = True
                target_file_type = match.group(1)
                # Per query di elenco file, usa k gestibile + deduplicazione intelligente
                k = 25
                ColoredOutput.print_info(f"Query di ricerca file '{target_file_type}' rilevata - aumento k a {k}")
                break
        
        # Pattern per query di elenco/lista generiche
        list_keywords = ['quali', 'elenco', 'lista', 'tutti', 'ogni', 'ciascun']
        enumeration_keywords = ['cosa ho fatto', 'cosa ho segnato', 'attività', 'journal']
        
        # Se contiene keywords di enumerazione e non è già una file search, aumenta k
        if not is_file_search_query:
            has_list_keyword = any(keyword in query_lower for keyword in list_keywords)
            has_enumeration = any(keyword in query_lower for keyword in enumeration_keywords)
            
            if has_list_keyword or has_enumeration:
                # Per query di tipo lista/elenco, usa k più alto
                k = max(k, 10)
                ColoredOutput.print_info(f"Query di tipo elenco rilevata - uso k={k}")
        else:
            has_list_keyword = False
        
        # Pattern di date
        date_patterns = [
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', 'full'),
            (r'(\d{1,2})[/-](\d{1,2})(?!\d)', 'partial'),
            (r'\b(oggi|ieri|domani)\b', 'relative'),
            (r'\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b', 'month_year'),
        ]
        
        # Cerca date nella query
        for pattern, pattern_type in date_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                match = matches[0]
                
                if pattern_type == 'full':
                    day, month, year = match
                    target_journal_date = f"{day.zfill(2)}-{month.zfill(2)}-{year}"
                    is_journal_list_query = has_list_keyword
                elif pattern_type == 'partial':
                    day, month = match
                    current_year = datetime.now().year
                    target_journal_date = f"{day.zfill(2)}-{month.zfill(2)}-{current_year}"
                    is_journal_list_query = has_list_keyword
                elif pattern_type == 'relative':
                    oggi = datetime.now()
                    if match == 'oggi':
                        target_journal_date = oggi.strftime("%d-%m-%Y")
                    elif match == 'ieri':
                        ieri = oggi - timedelta(days=1)
                        target_journal_date = ieri.strftime("%d-%m-%Y")
                    elif match == 'domani':
                        domani = oggi + timedelta(days=1)
                        target_journal_date = domani.strftime("%d-%m-%Y")
                    is_journal_list_query = has_list_keyword
                elif pattern_type == 'month_year':
                    day, month_name, year = match
                    mesi = {
                        'gennaio': '01', 'febbraio': '02', 'marzo': '03', 'aprile': '04',
                        'maggio': '05', 'giugno': '06', 'luglio': '07', 'agosto': '08',
                        'settembre': '09', 'ottobre': '10', 'novembre': '11', 'dicembre': '12'
                    }
                    month_num = mesi[month_name]
                    target_journal_date = f"{day.zfill(2)}-{month_num}-{year}"
                    is_journal_list_query = has_list_keyword
                break
        
        # Se è una query per lista Journal, aumenta k per recuperare tutti i chunk del giorno
        if is_journal_list_query and target_journal_date:
            # Usa un k molto più alto per essere sicuri di prendere tutti i chunk del giorno
            k = 20
            ColoredOutput.print_info(f"Query Journal rilevata per il {target_journal_date} - recupero tutti i chunk")
        
        # 1. Hybrid Retrieval (Semantic + BM25)
        docs = self.hybrid_retriever.search(question, k=k)
        
        # Per query di ricerca file specifici, deduplicazione intelligente
        if is_file_search_query and target_file_type:
            # Estrai clienti unici che hanno il file target
            unique_clients = set()
            client_docs = {}  # cliente -> primo documento trovato
            
            for doc in docs:
                filename = doc.metadata.get('filename', '')
                cliente = doc.metadata.get('cliente', 'unknown')
                
                # Se è il tipo di file che stiamo cercando
                if target_file_type.lower() in filename.lower() and cliente != 'unknown':
                    if cliente not in unique_clients:
                        unique_clients.add(cliente)
                        client_docs[cliente] = doc  # Salva il primo documento per questo cliente
            
            # Se abbiamo trovato clienti, crea un context semplificato
            if unique_clients:
                ColoredOutput.print_success(f"Trovati {len(unique_clients)} clienti unici con file {target_file_type}.md")
                # Usa solo un documento rappresentativo per cliente per ridurre il context
                docs = list(client_docs.values())[:15]  # Massimo 15 clienti per non sovraccaricare
        
        # Se è una query Journal specifica, filtra solo i documenti di quel giorno
        if is_journal_list_query and target_journal_date:
            filtered_docs = []
            target_filename = f"{target_journal_date}.md"
            
            for doc in docs:
                doc_filename = doc.metadata.get('filename', '')
                # Verifica se è il Journal del giorno target
                if doc_filename == target_filename:
                    filtered_docs.append(doc)
            
            # Se abbiamo trovato chunk del giorno specifico, usa solo quelli
            if filtered_docs:
                docs = filtered_docs
                ColoredOutput.print_success(f"Trovati {len(docs)} chunk per il Journal del {target_journal_date}")
        
        # Costruisci contesto con metadati per file Journal
        context_parts = []
        for doc in docs:
            filename = doc.metadata.get('filename', 'unknown')
            # Se è un file Journal, aggiungi la data come header
            if 'Journal/' in doc.metadata.get('source', '') or filename.endswith('.md') and len(filename) == 14 and filename[2] == '-' and filename[5] == '-':
                # Estrai data dal filename (formato: DD-MM-YYYY.md)
                if filename != 'unknown':
                    date_part = filename.replace('.md', '')
                    context_parts.append(f"=== Journal del {date_part} ===\n{doc.page_content}")
                else:
                    context_parts.append(doc.page_content)
            else:
                context_parts.append(doc.page_content)
        
        context = "\n\n".join(context_parts)
        
        # Debug: mostra chunks recuperati con source files (solo in modalità debug)
        source_files = []
        if os.getenv('DEBUG_RAG', '').lower() == 'true':
            print(ColoredOutput.colored(f"\n--- Chunks recuperati con Hybrid Search (k={k}) ---", ColoredOutput.DIM))
            for i, doc in enumerate(docs):
                # Usa il path originale completo dal campo 'source' dei metadati
                source_full_path = doc.metadata.get('source', '')
                base_path = "/opt/obsidian/appunti/"
                
                # Se il source contiene il path completo, calcoliamo il path relativo
                if source_full_path and source_full_path.startswith(base_path):
                    source_path = source_full_path[len(base_path):]
                else:
                    # Fallback alla logica precedente se il source non è valido
                    filename = doc.metadata.get('filename', 'unknown')
                    cliente = doc.metadata.get('cliente', 'unknown')
                    tipo = doc.metadata.get('tipo', '')
                    
                    if tipo == 'journal':
                        source_path = f"Journal/{filename}"
                    elif tipo == 'personale':
                        source_path = f"Paolo/{filename}"
                    elif tipo == 'tact':
                        source_path = f"Tact/{filename}"
                    elif tipo == 'tact_cliente' and cliente != 'unknown':
                        source_path = f"Tact/Clienti/{cliente}/{filename}"
                    elif cliente != 'unknown':
                        source_path = f"{cliente}/{filename}"
                    else:
                        source_path = filename
                
                source_files.append(source_path)
                print(ColoredOutput.colored(f"Chunk {i+1} [{source_path}]: {doc.page_content[:150]}...", ColoredOutput.DIM))
            print(ColoredOutput.colored("---\n", ColoredOutput.DIM))
        else:
            for doc in docs:
                # Usa il path originale completo dal campo 'source' dei metadati
                source_full_path = doc.metadata.get('source', '')
                base_path = "/opt/obsidian/appunti/"
                
                # Se il source contiene il path completo, calcoliamo il path relativo
                if source_full_path and source_full_path.startswith(base_path):
                    source_path = source_full_path[len(base_path):]
                else:
                    # Fallback alla logica precedente se il source non è valido
                    filename = doc.metadata.get('filename', 'unknown')
                    cliente = doc.metadata.get('cliente', 'unknown')
                    tipo = doc.metadata.get('tipo', '')
                    
                    if tipo == 'journal':
                        source_path = f"Journal/{filename}"
                    elif tipo == 'personale':
                        source_path = f"Paolo/{filename}"
                    elif tipo == 'tact':
                        source_path = f"Tact/{filename}"
                    elif tipo == 'tact_cliente' and cliente != 'unknown':
                        source_path = f"Tact/Clienti/{cliente}/{filename}"
                    elif cliente != 'unknown':
                        source_path = f"{cliente}/{filename}"
                    else:
                        source_path = filename
                
                source_files.append(source_path)
        
        # 2. Prompt ottimizzato per tipo di query
        if is_file_search_query and target_file_type:
            # Prompt specifico e ottimizzato per query di ricerca file
            prompt_template = f"""Basandoti sul contesto, elenca tutti i clienti che hanno un file {target_file_type}.md.

CONTESTO:
{{context}}

DOMANDA: {{question}}

Fornisci una risposta con formato:
Ho scritto un file {target_file_type}.md per i seguenti clienti:
1. [Nome Cliente]
2. [Nome Cliente]
...

RISPOSTA:"""
        elif has_list_keyword or has_enumeration:
            # Prompt per query di tipo elenco
            prompt_template = """Usa il contesto fornito per creare un ELENCO COMPLETO.

CONTESTO:
{context}

DOMANDA: {question}

IMPORTANTE:
- Fornisci TUTTI gli elementi trovati, non solo alcuni esempi
- Per liste di attività, includi lo stato [x] o [ ] di ogni voce
- Usa un formato lista chiaro e leggibile

RISPOSTA:"""
        else:
            # Prompt standard
            prompt_template = """Usa SOLO il contesto fornito per rispondere. Sii preciso e conciso.

CONTESTO:
{context}

DOMANDA: {question}

ISTRUZIONI:
- Rispondi SOLO basandoti sul contesto sopra
- Se la domanda riguarda una lista di cose da fare, riporta TUTTE le voci della lista così come appaiono nel contesto
- Se la domanda riguarda un cliente specifico, usa SOLO i suoi dati
- Mantieni la risposta breve e diretta
- Se non hai informazioni sufficienti, dillo chiaramente
- Per liste di attività, includi lo stato [x] o [ ] di ogni voce

RISPOSTA:"""
        
        # 3. Costruisci prompt finale
        full_prompt = prompt_template.format(context=context, question=question)
        
        # 4. Calcola token del prompt
        prompt_tokens = self.estimate_tokens(full_prompt)
        self.token_count["prompt"] += prompt_tokens
        
        # 5. Genera risposta direttamente con LLMAdapter
        response = self.llm.invoke(full_prompt)
        
        # 6. Calcola token della risposta
        completion_tokens = self.estimate_tokens(response)
        self.token_count["completion"] += completion_tokens
        self.token_count["total"] = self.token_count["prompt"] + self.token_count["completion"]
        
        # 7. Costo zero per modello locale
        cost_input = 0.0
        cost_output = 0.0
        cost_total = 0.0
        
        token_info = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cumulative_total": self.token_count["total"],
            "estimated_cost": {
                "input": f"${cost_input:.6f}",
                "output": f"${cost_output:.6f}",
                "total": f"${cost_total:.6f} (locale - gratis)"
            }
        }
        
        # Prepara lista fonti uniche
        unique_sources = list(dict.fromkeys(source_files))  # Rimuovi duplicati mantenendo ordine
        
        return response, token_info, unique_sources

def main():
    """Interfaccia CLI colorata per RAG"""
    # Clear screen per un inizio pulito
    os.system('clear' if os.name == 'posix' else 'cls')
    
    ColoredOutput.print_header("🤖 Local RAG MVP - Sistema Q&A Obsidian")
    
    # Determina il modello in base alla configurazione
    from config import settings
    if settings.use_llamafile_cli:
        ColoredOutput.print_info("Modello: Gemma 3-4B (CLI locale - gratuito)")
    elif settings.use_llamafile_api:
        ColoredOutput.print_info("Modello: Gemma 3-4B (Server locale - gratuito)")
    else:
        ColoredOutput.print_info("Modello: LlamaCpp (locale - gratuito)")
    
    model_name = "llamafile"
    
    try:
        # Inizializza RAG
        rag = SimpleRAG()
        rag.load_index()
        rag.setup_llm(model=model_name)
        
        print()
        ColoredOutput.print_separator()
        print(ColoredOutput.colored("Sistema pronto! ", ColoredOutput.GREEN, bold=True))
        print(ColoredOutput.colored("Comandi: ", ColoredOutput.CYAN) + 
              ColoredOutput.colored("exit/quit/q", ColoredOutput.BOLD) + " per uscire, " +
              ColoredOutput.colored("clear/cls", ColoredOutput.BOLD) + " per pulire")
        ColoredOutput.print_separator()
        print()
        
        while True:
            # Prompt colorato
            question = input(ColoredOutput.colored("❓ Domanda: ", ColoredOutput.YELLOW, bold=True))
            
            # Gestione comandi
            if question.lower() in ['exit', 'quit', 'q', 'esci']:
                print(ColoredOutput.colored("\n👋 Arrivederci!\n", ColoredOutput.CYAN))
                break
            
            if question.lower() in ['clear', 'cls']:
                os.system('clear' if os.name == 'posix' else 'cls')
                ColoredOutput.print_header("🤖 Local RAG MVP - Sistema Q&A Obsidian")
                continue
                
            if not question.strip():
                continue
                
            try:
                response, tokens, sources = rag.query(question)
                
                # Stampa risposta con box colorato
                ColoredOutput.print_response(response)
                
                # Stampa fonti in modo elegante
                if sources:
                    ColoredOutput.print_sources(sources)
                    
                    # Offri di aprire una fonte
                    print()
                    print(ColoredOutput.colored("💡 Digita il numero di una fonte per aprirla nel pager, o premi INVIO per continuare", ColoredOutput.YELLOW, dim=True))
                    
                    try:
                        choice = input(ColoredOutput.colored("   Apri fonte [1-" + str(len(sources)) + "]: ", ColoredOutput.DIM))
                        if choice.strip().isdigit():
                            source_idx = int(choice.strip()) - 1
                            if 0 <= source_idx < len(sources):
                                # Costruisci il path del file usando il path relativo
                                source = sources[source_idx]
                                base_path = "/opt/obsidian/appunti/"
                                
                                # Il source ora contiene già il path relativo corretto
                                full_path = os.path.join(base_path, source)
                                
                                # Apri con rich pager se disponibile, altrimenti less/more
                                if os.path.exists(full_path):
                                    import subprocess
                                    try:
                                        # Prova prima con rich
                                        subprocess.run(["rich", "--pager", full_path], check=True)
                                    except (subprocess.CalledProcessError, FileNotFoundError):
                                        try:
                                            # Fallback a less
                                            subprocess.run(["less", full_path], check=True)
                                        except (subprocess.CalledProcessError, FileNotFoundError):
                                            try:
                                                # Fallback a more
                                                subprocess.run(["more", full_path], check=True)
                                            except (subprocess.CalledProcessError, FileNotFoundError):
                                                # Ultimo fallback: stampa contenuto
                                                ColoredOutput.print_error(f"Nessun pager disponibile. Contenuto di {source}:")
                                                with open(full_path, 'r') as f:
                                                    content = f.read()
                                                    print(ColoredOutput.colored(content[:2000], ColoredOutput.DIM))
                                                    if len(content) > 2000:
                                                        print(ColoredOutput.colored("... (contenuto troncato)", ColoredOutput.DIM))
                                else:
                                    ColoredOutput.print_error(f"File non trovato: {full_path}")
                    except (ValueError, KeyboardInterrupt):
                        pass  # Utente ha premuto INVIO o CTRL+C
                
                # Token usage (più discreto)
                if os.getenv('SHOW_TOKENS', '').lower() == 'true':
                    print()
                    print(ColoredOutput.colored("📊 Token Usage", ColoredOutput.DIM))
                    print(ColoredOutput.colored(f"   Prompt: {tokens['prompt_tokens']} | Completion: {tokens['completion_tokens']} | Total: {tokens['total_tokens']}", ColoredOutput.DIM))
                    print(ColoredOutput.colored(f"   Session total: {tokens['cumulative_total']} tokens", ColoredOutput.DIM))
                
                ColoredOutput.print_separator()
                print()
                
            except Exception as e:
                ColoredOutput.print_error(f"Errore: {e}")
                print()
                
    except Exception as e:
        ColoredOutput.print_error(f"Errore inizializzazione: {e}")

if __name__ == "__main__":
    main()