#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from config import settings
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class PDFPreprocessor:
    """
    Classe per preprocessare PDF usando Docling e convertirli in Markdown
    """
    
    def __init__(self):
        self.raw_pdfs_path = settings.raw_pdfs_path
        self.documents_path = settings.documents_path
        self.converter = DocumentConverter()
        
        # Crea le directory se non esistono
        self.raw_pdfs_path.mkdir(exist_ok=True)
        self.documents_path.mkdir(exist_ok=True)
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizza il nome del file per evitare caratteri problematici
        """
        # Rimuovi estensione PDF e aggiungi .md
        base_name = Path(filename).stem
        # Sostituisci caratteri problematici
        sanitized = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        # Sostituisci spazi con underscore
        sanitized = sanitized.replace(' ', '_')
        return f"{sanitized}.md"
    
    def convert_pdf_to_markdown(self, pdf_path: Path) -> str:
        """
        Converte un singolo PDF in Markdown usando Docling
        """
        try:
            logger.info(f"Conversione di {pdf_path.name} in Markdown...")
            
            # Converti il PDF
            result = self.converter.convert(str(pdf_path))
            
            # Esporta in Markdown
            markdown_content = result.document.export_to_markdown()
            
            logger.info(f"PDF {pdf_path.name} convertito con successo")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Errore durante la conversione di {pdf_path}: {e}")
            raise
    
    def save_markdown_file(self, content: str, filename: str) -> Path:
        """
        Salva il contenuto Markdown nella directory documents
        """
        sanitized_filename = self.sanitize_filename(filename)
        output_path = self.documents_path / sanitized_filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"File Markdown salvato: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Errore durante il salvataggio di {output_path}: {e}")
            raise
    
    def clean_processed_pdf(self, pdf_path: Path):
        """
        Rimuove il PDF processato se configurato per farlo
        """
        if settings.docling_clean_processed_pdfs:
            try:
                pdf_path.unlink()
                logger.info(f"PDF processato rimosso: {pdf_path}")
            except Exception as e:
                logger.warning(f"Impossibile rimuovere il PDF {pdf_path}: {e}")
    
    def process_all_pdfs(self) -> list:
        """
        Processa tutti i PDF nella directory raw_pdfs
        """
        pdf_files = list(self.raw_pdfs_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.info("Nessun file PDF trovato nella directory raw_pdfs")
            return []
        
        logger.info(f"Trovati {len(pdf_files)} file PDF da processare")
        processed_files = []
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processando: {pdf_file.name}")
                
                # Converti PDF in Markdown
                markdown_content = self.convert_pdf_to_markdown(pdf_file)
                
                # Salva il file Markdown
                output_path = self.save_markdown_file(markdown_content, pdf_file.name)
                processed_files.append(output_path)
                
                # Pulisci il PDF se configurato
                self.clean_processed_pdf(pdf_file)
                
            except Exception as e:
                logger.error(f"Errore durante il processamento di {pdf_file.name}: {e}")
                continue
        
        return processed_files
    
    def process_single_pdf(self, pdf_filename: str) -> Path:
        """
        Processa un singolo PDF specificato
        """
        pdf_path = self.raw_pdfs_path / pdf_filename
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"File PDF non trovato: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"Il file {pdf_filename} non è un PDF")
        
        logger.info(f"Processando singolo PDF: {pdf_filename}")
        
        # Converti PDF in Markdown
        markdown_content = self.convert_pdf_to_markdown(pdf_path)
        
        # Salva il file Markdown
        output_path = self.save_markdown_file(markdown_content, pdf_filename)
        
        # Pulisci il PDF se configurato
        self.clean_processed_pdf(pdf_path)
        
        return output_path


def main():
    """
    Funzione principale per il preprocessing dei PDF
    """
    if not settings.enable_docling_preprocessing:
        logger.info("Preprocessing Docling disabilitato nella configurazione")
        return
    
    preprocessor = PDFPreprocessor()
    
    print("=== PREPROCESSING PDF CON DOCLING ===")
    print(f"Directory PDF: {preprocessor.raw_pdfs_path}")
    print(f"Directory output: {preprocessor.documents_path}")
    print()
    
    try:
        processed_files = preprocessor.process_all_pdfs()
        
        if processed_files:
            print(f"✅ Preprocessing completato! {len(processed_files)} file processati:")
            for file_path in processed_files:
                print(f"  - {file_path.name}")
            print()
            print("I file Markdown sono ora disponibili nella directory 'documents'")
            print("Puoi procedere con l'ingesting usando: python ingest.py")
        else:
            print("⚠️  Nessun file processato")
            
    except Exception as e:
        logger.error(f"Errore durante il preprocessing: {e}")
        print(f"❌ Errore: {e}")


if __name__ == "__main__":
    main()