#!/usr/bin/env python3
"""
Orchestratore per l'Analisi Settimanale SEO/SEM di Maspe (MASPE-SAW)

Questo script coordina l'analisi automatizzata settimanale dei dati SEO/SEM di Maspe:
1. Esegue lo script R per estrarre i dati da Google Analytics
2. Usa l'agente data-analysis-expert per analizzare i dati
3. Usa l'agente seo-sem-report-expert per generare report professionali
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

# Importa configurazione
from config import *
from prompt_generator import PromptGenerator

# Configurazione logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MaspeSEOOrchestrator:
    def __init__(self, output_dir=None, use_mock=None):
        self.output_dir = Path(output_dir) if output_dir else REPORTS_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = TEMP_DIR
        self.use_mock = use_mock if use_mock is not None else USE_MOCK_DATA
        self.prompt_generator = PromptGenerator()
        
        # Seleziona script R in base alla modalità
        if self.use_mock:
            logger.info("Modalità MOCK attiva - userò dati di test")
            self.r_script_path = None  # Useremo il generatore Python
        else:
            logger.info("Modalità PRODUZIONE - userò dati reali da Google Analytics")
            self.r_script_path = R_SCRIPT_PATH
        
    def get_date_range(self, weeks_back=1):
        """Calcola il range di date per l'analisi (default: ultima settimana)"""
        end_date = datetime.now() - timedelta(days=1)  # Ieri
        start_date = end_date - timedelta(days=7 * weeks_back)
        
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    
    def run_r_script(self, start_date, end_date):
        """Esegue lo script R per estrarre i dati da Google Analytics"""
        logger.info(f"Estrazione dati per il periodo: {start_date} a {end_date}")
        
        try:
            if self.use_mock:
                # Usa generatore Python per dati mock
                logger.info("Generazione dati mock...")
                from generate_mock_data import generate_mock_data
                return generate_mock_data(start_date, end_date)
            else:
                # Usa script R reale
                logger.info("Connessione a Google Analytics...")
                
                # Esegui script R con argomenti da linea di comando
                result = subprocess.run(
                    ["Rscript", str(self.r_script_path), start_date, end_date],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    logger.error(f"Script R terminato con codice: {result.returncode}")
                    if result.stderr:
                        logger.error(f"Stderr: {result.stderr}")
                    return False
                
                logger.info("Script R completato con successo")
            
            # Verifica che i file di output siano stati creati
            files_ok = True
            for nome, filepath in TEMP_FILES.items():
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    logger.info(f"✓ {nome}: {filepath} ({size} bytes)")
                else:
                    logger.error(f"✗ {nome}: {filepath} NON TROVATO")
                    files_ok = False
                    
            return files_ok
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Script R fallito: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("R non trovato. Assicurati che R sia installato.")
            return False
        except Exception as e:
            logger.error(f"Errore: {e}")
            return False
    
    def analyze_data_with_agent(self, start_date, end_date):
        """Usa l'agente data-analysis-expert per analizzare i dati estratti"""
        logger.info("Analisi dati con agente data-analysis-expert")
        
        # Usa il nuovo sistema di integrazione Claude Code
        try:
            from claude_integration import ClaudeCodeIntegration
            
            integration = ClaudeCodeIntegration()
            
            # File dati da analizzare
            data_files = {
                "dati_giornalieri": str(TEMP_FILES["dati_giornalieri"]),
                "campagne": str(TEMP_FILES["campagne"]),
                "pagine": str(TEMP_FILES["pagine"]),
                "queries": str(TEMP_FILES["queries"])
            }
            
            # Esegui analisi con agente
            analysis_results = integration.analyze_data_with_claude(
                data_files, start_date, end_date
            )
            
            # Salva risultati analisi
            analysis_file = self.temp_dir / "maspe_analysis_results.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Risultati analisi salvati in: {analysis_file}")
            return analysis_file, analysis_results
            
        except ImportError as e:
            logger.warning(f"Integrazione Claude Code non disponibile: {e}")
            # Fallback: analisi di base
            return self._basic_analysis(start_date, end_date)
    
    def _basic_analysis(self, start_date, end_date):
        """Analisi di base senza agenti"""
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "status": "simulated",
            "method": "basic_fallback",
            "agent": "data-analysis-expert",
            "response": "Analisi di base - per analisi avanzate configurare integrazione Claude Code",
            "period": f"{start_date} - {end_date}"
        }
        
        # Salva risultati analisi
        analysis_file = self.temp_dir / "maspe_analysis_results.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Analisi di base salvata in: {analysis_file}")
        return analysis_file, analysis_results
    
    def generate_report_with_agent(self, analysis_results, start_date, end_date):
        """Usa l'agente seo-sem-report-expert per creare il report finale"""
        logger.info("Generazione report con agente seo-sem-report-expert")
        
        # Genera nome file report con data
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_filename = f"maspe_seo_report_{report_date}.html"
        report_path = self.output_dir / report_filename
        
        # Usa il nuovo sistema di integrazione Claude Code
        try:
            from claude_integration import ClaudeCodeIntegration
            
            integration = ClaudeCodeIntegration()
            
            # File dati da includere nel report
            data_files = {
                "dati_giornalieri": str(TEMP_FILES["dati_giornalieri"]),
                "campagne": str(TEMP_FILES["campagne"]),
                "pagine": str(TEMP_FILES["pagine"]),
                "queries": str(TEMP_FILES["queries"])
            }
            
            # Genera report con agente
            final_report_path = integration.generate_report_with_claude(
                analysis_results, data_files, start_date, end_date, str(report_path)
            )
            
            logger.info(f"Report avanzato generato: {final_report_path}")
            return report_path
            
        except ImportError as e:
            logger.warning(f"Integrazione Claude Code non disponibile: {e}")
            # Fallback: report di base
            return self._generate_basic_report(start_date, end_date, report_path)
    
    def _generate_basic_report(self, start_date, end_date, report_path):
        """Genera report HTML di base senza agenti"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Report SEO/SEM Maspe - {start_date} / {end_date}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin: 20px 0; }}
                h1 {{ color: #2c5aa0; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Report SEO/SEM Maspe</h1>
                <p>Periodo: {start_date} - {end_date}</p>
                <p>Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>Note</h2>
                <p>Report di base generato dal sistema MASPE-SAW.</p>
                <p>Per report avanzati configurare l'integrazione con Claude Code.</p>
            </div>
            
            <footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">
                <p>Generato da MASPE-SAW (SEO Analytics Weekly)</p>
            </footer>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info(f"Report di base generato: {report_path}")
        return report_path
    
    def cleanup_temp_files(self):
        """Pulisce i file temporanei"""
        logger.info("Pulizia file temporanei")
        temp_files = [
            "/tmp/maspe-dati.csv",
            "/tmp/maspe-campagne.csv", 
            "/tmp/maspe-pagine.csv",
            "/tmp/maspe-queries.csv",
            "/tmp/ts-maspe.jpg",
            "/tmp/maspe_analysis_results.json"
        ]
        
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    logger.debug(f"Rimosso: {file}")
            except Exception as e:
                logger.warning(f"Impossibile rimuovere {file}: {e}")
    
    def _generate_analysis_prompt(self, start_date, end_date, analysis_results):
        """Genera prompt per analisi LLM esterna"""
        logger.info("Generazione prompt per analisi LLM")
        
        # File dati da includere nel prompt
        data_files = {
            "dati_giornalieri": str(TEMP_FILES["dati_giornalieri"]),
            "campagne": str(TEMP_FILES["campagne"]),
            "pagine": str(TEMP_FILES["pagine"]),
            "queries": str(TEMP_FILES["queries"])
        }
        
        # Genera prompt
        prompt = self.prompt_generator.generate_analysis_prompt(
            data_files, start_date, end_date, analysis_results
        )
        
        # Salva prompt
        prompt_path = self.prompt_generator.save_prompt_to_file(prompt, self.output_dir)
        
        logger.info(f"📝 PROMPT GENERATO: {prompt_path}")
        logger.info("Puoi copiare il contenuto del file e incollarlo in Claude, ChatGPT o altro LLM")
        
        return prompt_path
    
    def run(self, weeks_back=1, cleanup=True, generate_prompt=False):
        """Metodo principale di orchestrazione"""
        logger.info("Avvio orchestrazione analisi SEO/SEM Maspe")
        
        try:
            # Step 1: Ottieni range date
            start_date, end_date = self.get_date_range(weeks_back)
            logger.info(f"Periodo analisi: {start_date} a {end_date}")
            
            # Step 2: Estrai dati con script R
            if not self.run_r_script(start_date, end_date):
                logger.error("Fallita estrazione dati con script R")
                return False
            
            # Step 3: Analizza dati
            analysis_file, analysis_results = self.analyze_data_with_agent(start_date, end_date)
            
            # Step 4: Genera report
            report_path = self.generate_report_with_agent(
                analysis_results, start_date, end_date
            )
            
            logger.info(f"Analisi completata! Report in: {report_path}")
            
            # Step 5: Genera prompt per analisi manuale (opzionale)
            if generate_prompt:
                self._generate_analysis_prompt(start_date, end_date, analysis_results)
            
            # Step 6: Pulizia (opzionale)
            if cleanup:
                self.cleanup_temp_files()
                
            return True
            
        except Exception as e:
            logger.error(f"Orchestrazione fallita: {e}", exc_info=True)
            return False


def main():
    """Interfaccia linea di comando"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Orchestratore Analisi Settimanale SEO/SEM Maspe (MASPE-SAW)"
    )
    parser.add_argument(
        "--settimane", 
        type=int, 
        default=1,
        help="Numero di settimane da analizzare (default: 1)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory output per i report (default: reports)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Mantieni i file temporanei dopo l'analisi"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Usa dati mock invece di dati reali"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Forza uso dati reali (override variabile ambiente)"
    )
    parser.add_argument(
        "--generate-prompt",
        action="store_true",
        help="Genera prompt per analisi con LLM esterno (Claude, ChatGPT, ecc.)"
    )
    
    args = parser.parse_args()
    
    # Determina modalità dati
    use_mock = None
    if args.real:
        use_mock = False
    elif args.mock:
        use_mock = True
    
    orchestrator = MaspeSEOOrchestrator(
        output_dir=args.output_dir,
        use_mock=use_mock
    )
    success = orchestrator.run(
        weeks_back=args.settimane,
        cleanup=not args.no_cleanup,
        generate_prompt=args.generate_prompt
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()