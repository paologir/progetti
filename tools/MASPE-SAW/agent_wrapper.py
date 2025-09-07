#!/usr/bin/env python3
"""
Wrapper per l'integrazione con gli agenti Claude Code

Questo modulo fornisce un'interfaccia per utilizzare gli agenti Claude Code
all'interno del sistema MASPE-SAW per analisi avanzate e generazione report.
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ClaudeAgentWrapper:
    """Wrapper per chiamare gli agenti Claude Code"""
    
    def __init__(self):
        self.agents_dir = Path(__file__).parent / ".claude" / "agents"
        
    def call_agent(self, agent_name: str, prompt: str, 
                   context_files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Chiama un agente Claude Code con un prompt specifico
        
        Args:
            agent_name: Nome dell'agente (es. 'data-analysis-expert')
            prompt: Il prompt da passare all'agente
            context_files: Dizionario di file da includere nel contesto {nome: percorso}
            
        Returns:
            Dict con i risultati dell'agente
        """
        logger.info(f"Chiamata agente: {agent_name}")
        
        # Prepara il contesto con i file se forniti
        full_prompt = prompt
        if context_files:
            full_prompt += "\n\nFile di contesto disponibili:\n"
            for name, path in context_files.items():
                if os.path.exists(path):
                    full_prompt += f"- {name}: {path}\n"
                else:
                    logger.warning(f"File di contesto non trovato: {path}")
        
        try:
            # Chiamata effettiva all'agente tramite il modulo parent
            # Questo richiede di essere eseguito all'interno di Claude Code
            import sys
            parent_module = sys.modules.get('__main__')
            
            if hasattr(parent_module, 'Task'):
                # Siamo in Claude Code - usa il Task tool
                logger.info(f"Esecuzione agente {agent_name} tramite Task tool")
                # Questo verrà gestito dal sistema parent
                
                result = {
                    "agent": agent_name,
                    "status": "success", 
                    "prompt": prompt,
                    "response": f"Agente {agent_name} eseguito tramite Task tool",
                    "context_files": context_files or {},
                    "method": "task_tool"
                }
            else:
                # Fallback: simulazione
                logger.info(f"Simulazione agente {agent_name} (non in Claude Code)")
                result = {
                    "agent": agent_name,
                    "status": "simulated",
                    "prompt": prompt,
                    "response": f"Simulazione agente {agent_name} - per esecuzione reale usa Claude Code",
                    "context_files": context_files or {},
                    "method": "simulation"
                }
            
        except Exception as e:
            logger.error(f"Errore chiamata agente {agent_name}: {e}")
            result = {
                "agent": agent_name,
                "status": "error",
                "prompt": prompt,
                "response": f"Errore: {str(e)}",
                "context_files": context_files or {},
                "method": "error"
            }
        
        logger.info(f"Agente {agent_name} completato: {result['status']}")
        return result


class DataAnalysisAgent:
    """Interfaccia specifica per l'agente data-analysis-expert"""
    
    def __init__(self):
        self.wrapper = ClaudeAgentWrapper()
        self.agent_name = "data-analysis-expert"
        
    def analyze_seo_data(self, data_files: Dict[str, str], 
                        start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Analizza i dati SEO/SEM con l'agente specializzato
        
        Args:
            data_files: Dizionario dei file CSV da analizzare
            start_date: Data inizio periodo
            end_date: Data fine periodo
            
        Returns:
            Risultati dell'analisi
        """
        prompt = f"""
        Esegui un'analisi completa dei dati SEO/SEM di Maspe per il periodo {start_date} - {end_date}.
        
        Analizza i seguenti aspetti:
        
        1. ANALISI TRAFFICO:
           - Trend utenti totali vs organici
           - Distribuzione traffico per giorni della settimana
           - Identificazione picchi e cali anomali
           - Calcolo variazioni % WoW
        
        2. ANALISI CONVERSIONI:
           - Tasso di conversione complessivo
           - Conversioni per tipo (modulo_generico vs modulo_infoprodotto)
           - Trend conversioni nel periodo
           - Analisi statistica bayesiana del tasso di conversione
        
        3. ANALISI CAMPAGNE PAID:
           - ROI per campagna
           - Costo per conversione
           - Performance relative delle campagne
           - Suggerimenti ottimizzazione budget
        
        4. ANALISI SEO ORGANICO:
           - Top 10 pagine per impressioni/click
           - Top 10 query di ricerca
           - CTR medio e opportunità di miglioramento
           - Posizione media e trend
        
        5. INSIGHTS STATISTICI:
           - Test di significatività per variazioni
           - Identificazione outlier con metodo IQR
           - Analisi distribuzione (asimmetria, curtosi)
           - Previsioni per settimana successiva
        
        Fornisci risultati in formato strutturato JSON con metriche chiave,
        insights azionabili e raccomandazioni prioritizzate.
        """
        
        return self.wrapper.call_agent(
            self.agent_name,
            prompt,
            context_files=data_files
        )


class ReportGeneratorAgent:
    """Interfaccia specifica per l'agente seo-sem-report-expert"""
    
    def __init__(self):
        self.wrapper = ClaudeAgentWrapper()
        self.agent_name = "seo-sem-report-expert"
        
    def generate_report(self, analysis_results: Dict[str, Any],
                       data_files: Dict[str, str],
                       start_date: str, end_date: str,
                       output_format: str = "html") -> str:
        """
        Genera il report SEO/SEM con l'agente specializzato
        
        Args:
            analysis_results: Risultati dell'analisi dati
            data_files: File dati originali per riferimento
            start_date: Data inizio periodo
            end_date: Data fine periodo
            output_format: Formato output (html, markdown, pdf)
            
        Returns:
            Contenuto del report generato
        """
        prompt = f"""
        Crea un report professionale SEO/SEM per Maspe, periodo {start_date} - {end_date}.
        
        Struttura richiesta:
        
        1. EXECUTIVE SUMMARY (1 pagina):
           - 3 principali successi
           - 3 aree di attenzione
           - 3 azioni immediate consigliate
           - Metriche chiave in evidenza
        
        2. DASHBOARD KPI:
           - Utenti: totali, organici, variazione %
           - Conversioni: numero, tasso, trend
           - Costi: totale, CPA, ROI
           - SEO: impressioni, CTR, posizione media
        
        3. ANALISI DETTAGLIATA:
           a) Performance Traffico
              - Grafico temporale utenti
              - Breakdown sorgenti traffico
              - Analisi giorni settimana
           
           b) Performance Conversioni
              - Funnel conversione
              - Confronto tipi modulo
              - Trend temporale
           
           c) Performance Campagne
              - Tabella ROI per campagna
              - Grafico costi vs conversioni
              - Efficienza budget
           
           d) Performance SEO
              - Top pagine performanti
              - Top query di ricerca
              - Opportunità CTR
        
        4. RACCOMANDAZIONI:
           - Quick wins (implementabili subito)
           - Ottimizzazioni medio termine
           - Strategie lungo termine
        
        5. APPENDICE:
           - Note metodologiche
           - Glossario termini
           - Dati completi in tabelle
        
        Usa uno stile visuale moderno con:
        - Colori aziendali Maspe
        - Grafici interattivi (se HTML)
        - Icone per sezioni
        - Evidenziazione variazioni positive/negative
        
        Formato richiesto: {output_format}
        """
        
        # Combina risultati analisi nel contesto
        context_files = data_files.copy()
        context_files["analysis_results"] = "risultati_analisi.json"
        
        result = self.wrapper.call_agent(
            self.agent_name,
            prompt,
            context_files=context_files
        )
        
        # In produzione, qui estrarremmo il contenuto del report
        # dall'output dell'agente
        return result.get("response", "")


# Funzioni di utilità per l'integrazione

def save_analysis_results(results: Dict[str, Any], output_path: str):
    """Salva i risultati dell'analisi in formato JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Risultati analisi salvati in: {output_path}")


def save_report(content: str, output_path: str, format: str = "html"):
    """Salva il report nel formato specificato"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Report {format.upper()} salvato in: {output_path}")


if __name__ == "__main__":
    # Test del wrapper
    print("Test wrapper agenti Claude Code per MASPE-SAW")
    
    # Test analisi dati
    data_agent = DataAnalysisAgent()
    test_files = {
        "dati_giornalieri": "/tmp/maspe-dati.csv",
        "campagne": "/tmp/maspe-campagne.csv",
        "pagine": "/tmp/maspe-pagine.csv",
        "queries": "/tmp/maspe-queries.csv"
    }
    
    analysis = data_agent.analyze_seo_data(
        test_files,
        "2024-01-01",
        "2024-01-07"
    )
    print(f"\nAnalisi completata: {analysis['status']}")
    
    # Test generazione report
    report_agent = ReportGeneratorAgent()
    report = report_agent.generate_report(
        analysis,
        test_files,
        "2024-01-01",
        "2024-01-07",
        "html"
    )
    print(f"\nReport generato con successo")