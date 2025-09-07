#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings
import re
import os


class HybridRetriever:
    """
    Retriever ibrido che combina semantic search (FAISS) con keyword search (BM25)
    per migliorare la precisione del document retrieval
    """
    
    def __init__(self, faiss_index_path="obsidian_index"):
        self.faiss_index_path = faiss_index_path
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
        self.vector_store = None
        self.bm25 = None
        self.documents = []
        self.doc_texts = []
        
    def load_index(self):
        """Carica l'indice FAISS e prepara BM25"""
        print("Caricamento indice FAISS...")
        self.vector_store = FAISS.load_local(
            self.faiss_index_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Ottieni tutti i documenti per BM25
        print("Preparazione indice BM25...")
        all_docs = []
        all_texts = []
        
        # Estrai tutti i documenti dal docstore
        docstore = self.vector_store.docstore
        index_to_docstore_id = self.vector_store.index_to_docstore_id
        
        for i in range(self.vector_store.index.ntotal):
            try:
                # Ottieni l'ID del documento
                doc_id = index_to_docstore_id[i]
                # Ottieni il documento dal docstore
                doc = docstore.search(doc_id)
                if doc:
                    all_docs.append(doc)
                    all_texts.append(doc.page_content)
            except Exception as e:
                # Ignore errori di accesso a documenti specifici
                continue
        
        self.documents = all_docs
        self.doc_texts = all_texts
        
        # Prepara BM25
        tokenized_docs = [self._tokenize(text) for text in all_texts]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        print(f"✅ Hybrid retriever pronto con {len(self.documents)} documenti")
        
    def _tokenize(self, text):
        """Tokenizza il testo per BM25"""
        # Pulizia e tokenizzazione semplice
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Rimuovi punteggiatura
        tokens = text.split()
        return tokens
    
    def search(self, query, k=5, alpha=0.8):
        """
        Ricerca ibrida che combina semantic search e keyword search
        
        Args:
            query: Query di ricerca
            k: Numero di documenti da restituire
            alpha: Peso per semantic search (1-alpha per BM25)
        """
        if not self.vector_store or not self.bm25:
            raise RuntimeError("Carica prima l'indice con load_index()")
        
        # 1. Semantic search con FAISS
        print("🔍 Semantic search...")
        semantic_docs = self.vector_store.similarity_search_with_score(query, k=k*4)  # Aumentiamo k per avere più possibilità
        
        # 2. Keyword search con BM25
        print("🔍 Keyword search...")
        query_tokens = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # Ottieni i migliori documenti da BM25
        bm25_indices = np.argsort(bm25_scores)[::-1][:k*4]  # Aumentiamo anche qui
        
        # 2.5. Date-specific search - se la query contiene date, cerca documenti Journal corrispondenti
        date_specific_indices = self._find_date_specific_docs(query.lower())
        if date_specific_indices:
            print(f"🗓️ Found {len(date_specific_indices)} date-specific Journal entries")
            # Aggiungi questi indici ai risultati BM25 con priorità
            bm25_indices = np.concatenate([date_specific_indices, bm25_indices])
            bm25_indices = np.unique(bm25_indices)  # Rimuovi duplicati
        
        # 3. Fusion dei risultati
        print("🔄 Fusion dei risultati...")
        doc_scores = {}
        
        # Aggiungi punteggi semantic (inverti la distanza)
        for doc, distance in semantic_docs:
            doc_key = doc.page_content[:100]  # Usa i primi 100 caratteri come chiave
            semantic_score = 1 / (1 + distance)  # Converti distanza in score
            doc_scores[doc_key] = {
                'doc': doc,
                'semantic_score': semantic_score,
                'bm25_score': 0.0
            }
        
        # Aggiungi punteggi BM25
        for idx in bm25_indices:
            if idx < len(self.documents):
                doc = self.documents[idx]
                doc_key = doc.page_content[:100]
                bm25_score = bm25_scores[idx]
                
                # Boost artificiale per documenti date-specific
                if idx in date_specific_indices:
                    bm25_score = max(bm25_scores) * 2.0  # Score molto alto per date match
                
                if doc_key in doc_scores:
                    doc_scores[doc_key]['bm25_score'] = bm25_score
                else:
                    doc_scores[doc_key] = {
                        'doc': doc,
                        'semantic_score': 0.0,
                        'bm25_score': bm25_score
                    }
        
        # 4. Calcola punteggio finale con boost per file corti e riordina
        final_results = []
        for doc_key, scores in doc_scores.items():
            # Normalizza i punteggi
            semantic_norm = scores['semantic_score']
            bm25_norm = scores['bm25_score'] / (max(bm25_scores) + 1e-10)
            
            # Combina con alpha
            final_score = alpha * semantic_norm + (1 - alpha) * bm25_norm
            
            # BOOST PER FILE CORTI E RECENTI
            doc = scores['doc']
            boost_factor = 1.0
            
            # Boost per file corti (maggiore precisione)
            if doc.metadata.get('is_short_file', False):
                boost_factor += 0.3
                
            # Boost per documenti del cliente menzionato nella query
            doc_cliente = doc.metadata.get('cliente', '').lower()
            query_lower = query.lower()
            
            # Lista di clienti comuni da cercare
            clienti_keywords = {
                'didonè': 'Didonè Comacchio',
                'comacchio': 'Didonè Comacchio', 
                'fis': 'Fis',
                'maffeis': 'Maffeis Engineering',
                'progeo': 'Progeo',
                'maspe': 'Maspe'
            }
            
            # Cerca se un cliente è menzionato nella query
            for keyword, cliente_name in clienti_keywords.items():
                if keyword in query_lower and doc_cliente == cliente_name.lower():
                    boost_factor += 0.8
                    break
                
            # Boost per documenti recenti (2025)
            if doc.metadata.get('date_mentioned') and '2025' in doc.metadata.get('date_mentioned', ''):
                boost_factor += 0.2
                
            # Boost per documenti con prezzi se la query contiene termini di costo
            if any(term in query.lower() for term in ['€', 'costo', 'prezzo', 'proposta', 'mese']) and doc.metadata.get('prices'):
                boost_factor += 0.4
                
            # Boost per query con date specifiche - priorità per file Journal
            date_boost = self._detect_date_query(query_lower, doc)
            if date_boost > 0:
                boost_factor += date_boost
            
            # Boost per file specifici menzionati nella query
            file_keywords = {
                'concorrent': 'concorrenti.md',
                'competitor': 'concorrenti.md',
                'corpus': 'corpus.md',
                'dati': 'dati.md',
                'account': 'dati.md'
            }
            
            doc_filename = doc.metadata.get('filename', '').lower()
            
            # BOOST SPECIALE per query che chiedono informazioni generali SUL CLIENTE GIUSTO
            if any(term in query_lower for term in ['informazioni generali', 'generale', 'ditta', 'azienda', 'che tipo']):
                if doc_filename == 'corpus.md':
                    # Verifica che sia il corpus del cliente menzionato nella query
                    cliente_in_query = False
                    for keyword, cliente_name in clienti_keywords.items():
                        if keyword in query_lower and doc_cliente == cliente_name.lower():
                            cliente_in_query = True
                            break
                    
                    if cliente_in_query:
                        boost_factor += 3.5  # Boost molto alto per corpus.md del cliente giusto
                    else:
                        # Piccolo boost per corpus in generale, ma non del cliente sbagliato
                        boost_factor += 0.2
            
            for keyword, target_file in file_keywords.items():
                if keyword in query_lower and doc_filename == target_file:
                    boost_factor += 0.9
                    break
                    
            # SUPER BOOST quando la query contiene sia il cliente che un tipo di file
            if doc_cliente:
                # Check se il cliente è nella query
                cliente_in_query = any(word in query_lower for word in doc_cliente.split())
                
                # Check se un tipo di file è nella query
                file_type_in_query = any(keyword in query_lower for keyword in file_keywords.keys())
                
                # Se entrambi sono presenti e il doc è del cliente giusto con il file giusto
                if cliente_in_query and file_type_in_query:
                    for keyword, target_file in file_keywords.items():
                        if keyword in query_lower and doc_filename == target_file:
                            boost_factor += 2.0  # Super boost!
                            break
            
            # Applica boost
            final_score *= boost_factor
            
            final_results.append({
                'doc': scores['doc'],
                'final_score': final_score,
                'semantic_score': semantic_norm,
                'bm25_score': bm25_norm,
                'boost_factor': boost_factor
            })
        
        # Ordina per punteggio finale
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Restituisci i migliori k documenti
        best_docs = [result['doc'] for result in final_results[:k]]
        
        # Debug info con identificazione documento
        # Mostra più risultati (default 10, configurabile via env var)
        debug_results_limit = int(os.getenv('DEBUG_RESULTS_LIMIT', '10'))
        print(f"📊 Hybrid search results (top {min(debug_results_limit, len(final_results))}):")
        for i, result in enumerate(final_results[:debug_results_limit]):
            content = result['doc'].page_content
            # Tenta di identificare il cliente dal contenuto
            client_hints = []
            if 'fis' in content.lower(): client_hints.append("FIS")
            if 'maffeis' in content.lower(): client_hints.append("MAFFEIS")
            if 'progeo' in content.lower(): client_hints.append("PROGEO")
            if 'espa' in content.lower(): client_hints.append("ESPA")
            
            client_str = f"[{','.join(client_hints)}]" if client_hints else "[UNKNOWN]"
            boost_info = f"Boost: {result['boost_factor']:.2f}" if result['boost_factor'] > 1.0 else ""
            print(f"  {i+1}. Final: {result['final_score']:.3f} | Semantic: {result['semantic_score']:.3f} | BM25: {result['bm25_score']:.3f} {client_str} {boost_info}")
            print(f"     {content[:80]}...")
        
        return best_docs
    
    def _detect_date_query(self, query_lower, doc):
        """
        Rileva se la query contiene riferimenti a date specifiche e boost documenti Journal corrispondenti
        
        Args:
            query_lower: Query in lowercase
            doc: Documento da valutare
            
        Returns:
            float: Valore di boost (0.0 se nessun boost, >0 se boost applicabile)
        """
        import re
        from datetime import datetime, timedelta
        
        # Controlla se il documento è dalla directory Journal
        doc_path = doc.metadata.get('source', '')
        is_journal = 'Journal/' in doc_path or doc.metadata.get('tipo') == 'journal'
        
        if not is_journal:
            return 0.0
        
        # Pattern di date da cercare nella query
        date_patterns = [
            # Formato DD/MM/YYYY o DD-MM-YYYY
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            # Formato DD/MM o DD-MM
            r'(\d{1,2})[/-](\d{1,2})(?!\d)',
            # Formato "oggi", "ieri", "domani"
            r'\b(oggi|ieri|domani)\b',
            # Formato "lunedì", "martedì", etc.
            r'\b(lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica)\b',
            # Formato "DD mese YYYY" es. "17 luglio 2025" - DEVE ESSERE PRIMA degli altri pattern mese
            r'\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b',
            # Formato "mese anno" es. "luglio 2025"
            r'\b(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b',
            # Formato "DD mese" es. "15 luglio"  
            r'\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\b'
        ]
        
        # Cerca pattern di date nella query
        date_found = False
        target_date = None
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                date_found = True
                # Per semplicità, prendiamo il primo match
                match = matches[0]
                
                if pattern == r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})':
                    # Formato completo DD/MM/YYYY
                    day, month, year = match
                    target_date = f"{day.zfill(2)}-{month.zfill(2)}-{year}"
                elif pattern == r'(\d{1,2})[/-](\d{1,2})(?!\d)':
                    # Formato DD/MM (assumiamo anno corrente)
                    day, month = match
                    current_year = datetime.now().year
                    target_date = f"{day.zfill(2)}-{month.zfill(2)}-{current_year}"
                elif pattern == r'\b(oggi|ieri|domani)\b':
                    # Relativi temporali
                    oggi = datetime.now()
                    if match == 'oggi':
                        target_date = oggi.strftime("%d-%m-%Y")
                    elif match == 'ieri':
                        ieri = oggi - timedelta(days=1)
                        target_date = ieri.strftime("%d-%m-%Y")
                    elif match == 'domani':
                        domani = oggi + timedelta(days=1)
                        target_date = domani.strftime("%d-%m-%Y")
                elif pattern == r'\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b':
                    # Formato "DD mese YYYY"
                    day, month_name, year = match
                    # Converti nome mese in numero
                    mesi = {
                        'gennaio': '01', 'febbraio': '02', 'marzo': '03', 'aprile': '04',
                        'maggio': '05', 'giugno': '06', 'luglio': '07', 'agosto': '08',
                        'settembre': '09', 'ottobre': '10', 'novembre': '11', 'dicembre': '12'
                    }
                    month_num = mesi[month_name]
                    target_date = f"{day.zfill(2)}-{month_num}-{year}"
                break
        
        if not date_found:
            return 0.0
        
        # Estrai la data dal filename del documento Journal
        doc_filename = doc.metadata.get('filename', '')
        filename_match = re.match(r'(\d{2}-\d{2}-\d{4})\.md', doc_filename)
        
        if not filename_match:
            return 0.0
            
        doc_date = filename_match.group(1)
        
        # Se abbiamo una data target specifica, controlla corrispondenza esatta
        if target_date and target_date == doc_date:
            return 1.5  # Boost alto per corrispondenza esatta
        
        # Se la query menziona genericamente "data", "calendario", "attività", boost Journal files
        calendar_keywords = ['data', 'calendario', 'attività', 'appuntamento', 'meeting', 'riunione', 'impegno']
        if any(keyword in query_lower for keyword in calendar_keywords):
            return 0.7  # Boost moderato per query generiche di calendario
        
        return 0.0
    
    def _find_date_specific_docs(self, query_lower):
        """
        Trova documenti Journal specifici per date menzionate nella query
        
        Args:
            query_lower: Query in lowercase
            
        Returns:
            list: Indici dei documenti Journal che corrispondono alle date nella query
        """
        import re
        from datetime import datetime, timedelta
        
        # Pattern di date (usa gli stessi della detection)
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{1,2})[/-](\d{1,2})(?!\d)',
            r'\b(oggi|ieri|domani)\b',
            r'\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b',
        ]
        
        target_dates = []
        
        # Estrai tutte le date dalla query
        for pattern in date_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                if pattern == r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})':
                    day, month, year = match
                    target_dates.append(f"{day.zfill(2)}-{month.zfill(2)}-{year}")
                elif pattern == r'(\d{1,2})[/-](\d{1,2})(?!\d)':
                    day, month = match
                    current_year = datetime.now().year
                    target_dates.append(f"{day.zfill(2)}-{month.zfill(2)}-{current_year}")
                elif pattern == r'\b(oggi|ieri|domani)\b':
                    oggi = datetime.now()
                    if match == 'oggi':
                        target_dates.append(oggi.strftime("%d-%m-%Y"))
                    elif match == 'ieri':
                        ieri = oggi - timedelta(days=1)
                        target_dates.append(ieri.strftime("%d-%m-%Y"))
                    elif match == 'domani':
                        domani = oggi + timedelta(days=1)
                        target_dates.append(domani.strftime("%d-%m-%Y"))
                elif pattern == r'\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b':
                    # Formato "DD mese YYYY"
                    day, month_name, year = match
                    # Converti nome mese in numero
                    mesi = {
                        'gennaio': '01', 'febbraio': '02', 'marzo': '03', 'aprile': '04',
                        'maggio': '05', 'giugno': '06', 'luglio': '07', 'agosto': '08',
                        'settembre': '09', 'ottobre': '10', 'novembre': '11', 'dicembre': '12'
                    }
                    month_num = mesi[month_name]
                    target_dates.append(f"{day.zfill(2)}-{month_num}-{year}")
        
        if not target_dates:
            return []
        
        # Cerca documenti Journal con queste date
        matching_indices = []
        for i, doc in enumerate(self.documents):
            if doc.metadata.get('tipo') == 'journal':
                doc_filename = doc.metadata.get('filename', '')
                filename_match = re.match(r'(\d{2}-\d{2}-\d{4})\.md', doc_filename)
                if filename_match:
                    doc_date = filename_match.group(1)
                    if doc_date in target_dates:
                        matching_indices.append(i)
        
        return np.array(matching_indices)