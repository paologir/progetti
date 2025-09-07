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

class LavoroPDFPreprocessor:
    """
    Classe per preprocessare PDF dalla struttura organizzata /opt/lavoro/documenti_rag
    """
    
    def __init__(self):
        self.source_path = Path("/opt/lavoro/documenti_rag")
        self.output_path = Path("/opt/lavoro/documenti_rag_processed")
        self.converter = DocumentConverter()
        
        # Crea la directory di output se non esiste
        self.output_path.mkdir(exist_ok=True)
        
        # Crea la stessa struttura di directory nell'output
        for category in ["clienti", "proposte", "corpus", "documentazione", "spreadsheet"]:
            (self.output_path / category).mkdir(exist_ok=True)
    
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
            
            # Aggiungi metadata nel markdown
            relative_path = pdf_path.relative_to(self.source_path)
            category = relative_path.parts[0]
            
            metadata_header = f"""---
source_file: {pdf_path.name}
source_path: {relative_path}
category: {category}
processed_with: docling
---

"""
            
            logger.info(f"PDF {pdf_path.name} convertito con successo")
            return metadata_header + markdown_content
            
        except Exception as e:
            logger.error(f"Errore durante la conversione di {pdf_path}: {e}")
            raise
    
    def save_markdown_file(self, content: str, pdf_path: Path) -> Path:
        """
        Salva il contenuto Markdown mantenendo la struttura organizzativa
        """
        # Calcola il path di output mantenendo la struttura
        relative_path = pdf_path.relative_to(self.source_path)
        
        # Sostituisci l'estensione .pdf con .md
        output_relative_path = relative_path.with_suffix('.md')
        
        # Sanitizza il nome del file
        sanitized_name = self.sanitize_filename(pdf_path.name)
        output_path = self.output_path / output_relative_path.parent / sanitized_name
        
        # Crea la directory se non esiste
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"File Markdown salvato: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Errore durante il salvataggio di {output_path}: {e}")
            raise
    
    def process_all_pdfs(self, dry_run: bool = False) -> list:
        """
        Processa tutti i PDF nella struttura organizzata
        """
        pdf_files = list(self.source_path.rglob("*.pdf"))
        
        if not pdf_files:
            logger.info("Nessun file PDF trovato nella struttura documenti_rag")
            return []
        
        logger.info(f"Trovati {len(pdf_files)} file PDF da processare")
        processed_files = []
        
        # Statistiche per categoria
        category_stats = {}
        
        for pdf_file in pdf_files:
            try:
                relative_path = pdf_file.relative_to(self.source_path)
                category = relative_path.parts[0]
                
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1
                
                if dry_run:
                    print(f"[DRY-RUN] Processerei: {relative_path}")
                    continue
                    
                logger.info(f"Processando: {relative_path}")
                
                # Converti PDF in Markdown
                markdown_content = self.convert_pdf_to_markdown(pdf_file)
                
                # Salva il file Markdown
                output_path = self.save_markdown_file(markdown_content, pdf_file)
                processed_files.append(output_path)
                
            except Exception as e:
                logger.error(f"Errore durante il processamento di {pdf_file}: {e}")
                continue
        
        # Mostra statistiche
        print("\n=== Statistiche PDF per categoria ===")
        for cat, count in sorted(category_stats.items()):
            print(f"{cat}: {count} PDF")
        print(f"\nTotale: {len(pdf_files)} PDF")
        
        return processed_files
    
    def process_category(self, category: str, dry_run: bool = False) -> list:
        """
        Processa solo i PDF di una categoria specifica
        """
        category_path = self.source_path / category
        
        if not category_path.exists():
            raise ValueError(f"Categoria non trovata: {category}")
        
        pdf_files = list(category_path.rglob("*.pdf"))
        
        if not pdf_files:
            logger.info(f"Nessun file PDF trovato nella categoria {category}")
            return []
        
        logger.info(f"Trovati {len(pdf_files)} file PDF nella categoria {category}")
        processed_files = []
        
        for pdf_file in pdf_files:
            try:
                relative_path = pdf_file.relative_to(self.source_path)
                
                if dry_run:
                    print(f"[DRY-RUN] Processerei: {relative_path}")
                    continue
                    
                logger.info(f"Processando: {relative_path}")
                
                # Converti PDF in Markdown
                markdown_content = self.convert_pdf_to_markdown(pdf_file)
                
                # Salva il file Markdown
                output_path = self.save_markdown_file(markdown_content, pdf_file)
                processed_files.append(output_path)
                
            except Exception as e:
                logger.error(f"Errore durante il processamento di {pdf_file}: {e}")
                continue
        
        return processed_files


def main():
    """
    Funzione principale per il preprocessing dei PDF dalla struttura lavoro
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Preprocessa PDF dalla struttura documenti_rag")
    parser.add_argument("--dry-run", action="store_true", help="Mostra solo cosa verrebbe processato")
    parser.add_argument("--category", help="Processa solo una categoria specifica")
    parser.add_argument("--limit", type=int, help="Limita il numero di PDF da processare")
    
    args = parser.parse_args()
    
    preprocessor = LavoroPDFPreprocessor()
    
    print("=== PREPROCESSING PDF DALLA STRUTTURA LAVORO ===")
    print(f"Directory sorgente: {preprocessor.source_path}")
    print(f"Directory output: {preprocessor.output_path}")
    print()
    
    try:
        if args.category:
            processed_files = preprocessor.process_category(args.category, dry_run=args.dry_run)
        else:
            processed_files = preprocessor.process_all_pdfs(dry_run=args.dry_run)
        
        if args.dry_run:
            print(f"\n⚠️  MODALITÀ DRY-RUN: nessun file processato.")
            print("Usa senza --dry-run per eseguire effettivamente il preprocessing.")
        elif processed_files:
            print(f"\n✅ Preprocessing completato! {len(processed_files)} file processati")
            print(f"I file Markdown sono disponibili in: {preprocessor.output_path}")
            print("\nPuoi procedere con l'ingesting usando:")
            print("python ingest_v2.py --source /opt/lavoro/documenti_rag_processed")
        else:
            print("⚠️  Nessun file processato")
            
    except Exception as e:
        logger.error(f"Errore durante il preprocessing: {e}")
        print(f"❌ Errore: {e}")


if __name__ == "__main__":
    main()