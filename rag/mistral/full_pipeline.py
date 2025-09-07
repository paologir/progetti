#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import subprocess
from pathlib import Path
from config import settings
import logging

logger = logging.getLogger(__name__)

def run_preprocessing():
    """
    Esegue il preprocessing dei PDF con Docling
    """
    print("🔄 FASE 1: Preprocessing PDF con Docling")
    print("=" * 50)
    
    try:
        from preprocess import PDFPreprocessor
        
        preprocessor = PDFPreprocessor()
        processed_files = preprocessor.process_all_pdfs()
        
        if processed_files:
            print(f"✅ Preprocessing completato! {len(processed_files)} file convertiti")
            return True
        else:
            print("⚠️  Nessun PDF da processare nella directory raw_pdfs")
            return False
            
    except ImportError as e:
        print(f"❌ Errore di importazione: {e}")
        print("Assicurati che Docling sia installato: pip install docling")
        return False
    except Exception as e:
        print(f"❌ Errore durante il preprocessing: {e}")
        return False

def run_ingesting():
    """
    Esegue l'ingesting dei documenti nel vector store
    """
    print("\n🔄 FASE 2: Ingesting documenti nel vector store")
    print("=" * 50)
    
    try:
        # Importa e esegue il modulo ingest
        import ingest
        ingest.main()
        print("✅ Ingesting completato!")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante l'ingesting: {e}")
        return False

def check_dependencies():
    """
    Verifica che le dipendenze necessarie siano installate
    """
    try:
        import docling
        return True
    except ImportError:
        print("❌ Docling non installato. Installa con: pip install docling")
        return False

def print_status():
    """
    Mostra lo status delle directory
    """
    print("📊 STATUS DELLE DIRECTORY")
    print("=" * 50)
    
    # Controlla raw_pdfs
    raw_pdfs = Path(settings.raw_pdfs_path)
    pdf_count = len(list(raw_pdfs.glob("*.pdf"))) if raw_pdfs.exists() else 0
    print(f"📁 {raw_pdfs}: {pdf_count} PDF")
    
    # Controlla documents
    documents = Path(settings.documents_path)
    doc_count = len(list(documents.glob("*"))) - 1 if documents.exists() else 0  # -1 per README.txt
    print(f"📁 {documents}: {doc_count} documenti")
    
    # Controlla vector store
    faiss_index = Path(settings.faiss_index_path)
    has_index = faiss_index.exists() and any(faiss_index.iterdir())
    print(f"🗂️  Vector store: {'✅ Presente' if has_index else '❌ Non presente'}")
    print()

def main():
    """
    Funzione principale del pipeline completo
    """
    parser = argparse.ArgumentParser(description="Pipeline completo per RAG: Preprocessing + Ingesting")
    parser.add_argument("--preprocessing-only", action="store_true", 
                       help="Esegue solo il preprocessing dei PDF")
    parser.add_argument("--ingesting-only", action="store_true", 
                       help="Esegue solo l'ingesting dei documenti")
    parser.add_argument("--status", action="store_true", 
                       help="Mostra lo status delle directory")
    
    args = parser.parse_args()
    
    print("🚀 PIPELINE COMPLETO RAG")
    print("=" * 50)
    
    # Mostra status se richiesto
    if args.status:
        print_status()
        return
    
    # Solo preprocessing
    if args.preprocessing_only:
        if not settings.enable_docling_preprocessing:
            print("⚠️  Preprocessing Docling disabilitato nella configurazione")
            return
        
        if not check_dependencies():
            return
            
        run_preprocessing()
        return
    
    # Solo ingesting
    if args.ingesting_only:
        run_ingesting()
        return
    
    # Pipeline completo
    print_status()
    
    success = True
    
    # Fase 1: Preprocessing (se abilitato)
    if settings.enable_docling_preprocessing:
        if not check_dependencies():
            return
        
        preprocessing_success = run_preprocessing()
        if not preprocessing_success:
            print("⚠️  Preprocessing fallito, ma continuiamo con l'ingesting...")
    else:
        print("⚠️  Preprocessing Docling disabilitato nella configurazione")
        print("Saltando alla fase di ingesting...")
    
    # Fase 2: Ingesting
    ingesting_success = run_ingesting()
    success = success and ingesting_success
    
    # Risultato finale
    print("\n" + "=" * 50)
    if success:
        print("🎉 PIPELINE COMPLETATO CON SUCCESSO!")
        print("Il sistema RAG è pronto per ricevere query.")
        print("Usa: python simple_rag.py o python chatbot.py")
    else:
        print("❌ PIPELINE COMPLETATO CON ERRORI")
        print("Controlla i log sopra per dettagli.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()