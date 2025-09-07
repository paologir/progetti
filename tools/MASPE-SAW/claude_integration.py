#!/usr/bin/env python3
"""
Integrazione diretta con Claude Code per MASPE-SAW
Questo modulo gestisce le chiamate agli agenti tramite il Task tool
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from agent_wrapper import DataAnalysisAgent, ReportGeneratorAgent

logger = logging.getLogger(__name__)


class ClaudeCodeIntegration:
    """Gestisce l'integrazione con Claude Code per analisi e report avanzati"""
    
    def __init__(self):
        self.data_agent = DataAnalysisAgent()
        self.report_agent = ReportGeneratorAgent()
        
    def analyze_data_with_claude(self, data_files: Dict[str, str], 
                                start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Esegue analisi avanzata dei dati SEO/SEM usando l'agente data-analysis-expert
        """
        logger.info("Avvio analisi dati con agente Claude Code")
        
        # Verifica esistenza file
        existing_files = {}
        for name, path in data_files.items():
            if os.path.exists(path):
                existing_files[name] = path
            else:
                logger.warning(f"File non trovato: {path}")
        
        if not existing_files:
            logger.error("Nessun file dati disponibile per l'analisi")
            return {"error": "Nessun file dati disponibile"}
        
        # Esegui analisi con agente
        analysis_result = self.data_agent.analyze_seo_data(
            existing_files, start_date, end_date
        )
        
        return analysis_result
    
    def generate_report_with_claude(self, analysis_results: Dict[str, Any],
                                   data_files: Dict[str, str],
                                   start_date: str, end_date: str,
                                   output_path: str) -> str:
        """
        Genera report professionale usando l'agente seo-sem-report-expert
        """
        logger.info("Generazione report con agente Claude Code")
        
        # Verifica esistenza file dati
        existing_files = {}
        for name, path in data_files.items():
            if os.path.exists(path):
                existing_files[name] = path
        
        # Genera report con agente
        report_content = self.report_agent.generate_report(
            analysis_results,
            existing_files,
            start_date,
            end_date,
            "html"
        )
        
        # Se il report è stato generato come contenuto, salvalo
        if isinstance(report_content, str) and len(report_content) > 100:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Report salvato in: {output_path}")
        else:
            # Genera report HTML di base con i risultati dell'analisi
            html_content = self._generate_enhanced_html_report(
                analysis_results, existing_files, start_date, end_date
            )
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Report HTML migliorato salvato in: {output_path}")
        
        return output_path
    
    def _generate_enhanced_html_report(self, analysis_results: Dict[str, Any],
                                     data_files: Dict[str, str],
                                     start_date: str, end_date: str) -> str:
        """
        Genera un report HTML migliorato con i dati estratti
        """
        from datetime import datetime
        import pandas as pd
        
        # Leggi dati per statistiche
        stats = self._extract_statistics(data_files)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Report SEO/SEM Maspe - {start_date} / {end_date}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f7fa;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 30px;
                }}
                .kpi-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .kpi-card {{
                    background: #f8f9ff;
                    border: 1px solid #e1e5e9;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }}
                .kpi-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 5px;
                }}
                .kpi-label {{
                    color: #666;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #fafbfc;
                    border-radius: 8px;
                }}
                .section h2 {{
                    color: #4a5568;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .data-table th,
                .data-table td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e1e5e9;
                }}
                .data-table th {{
                    background-color: #667eea;
                    color: white;
                    font-weight: 600;
                }}
                .data-table tr:nth-child(even) {{
                    background-color: #f8f9ff;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.8em;
                    font-weight: bold;
                }}
                .status-success {{
                    background-color: #48bb78;
                    color: white;
                }}
                .status-simulated {{
                    background-color: #ed8936;
                    color: white;
                }}
                .footer {{
                    background-color: #2d3748;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Report SEO/SEM Maspe</h1>
                    <p><strong>Periodo:</strong> {start_date} - {end_date}</p>
                    <p>Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>🎯 KPI Principali</h2>
                        <div class="kpi-grid">
                            <div class="kpi-card">
                                <div class="kpi-value">{stats.get('total_users', 'N/A')}</div>
                                <div class="kpi-label">Utenti Totali</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-value">{stats.get('avg_users_day', 'N/A')}</div>
                                <div class="kpi-label">Media Utenti/Giorno</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-value">{stats.get('total_conversions', 'N/A')}</div>
                                <div class="kpi-label">Conversioni</div>
                            </div>
                            <div class="kpi-card">
                                <div class="kpi-value">€{stats.get('total_cost', 'N/A')}</div>
                                <div class="kpi-label">Costo Campagne</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🔍 Stato Analisi</h2>
                        <p><strong>Metodo Analisi:</strong> 
                        <span class="status-badge status-{analysis_results.get('status', 'simulated')}">
                            {analysis_results.get('method', 'Simulazione').title()}
                        </span></p>
                        <p><strong>Agente:</strong> {analysis_results.get('agent', 'data-analysis-expert')}</p>
                        <p><strong>Risultato:</strong> {analysis_results.get('response', 'Analisi completata')}</p>
                    </div>
                    
                    <div class="section">
                        <h2>📁 File Dati Elaborati</h2>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Tipo Dato</th>
                                    <th>File</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Aggiungi righe per ogni file
        for name, path in data_files.items():
            status = "✅ Disponibile" if os.path.exists(path) else "❌ Non trovato"
            html_content += f"""
                                <tr>
                                    <td>{name.replace('_', ' ').title()}</td>
                                    <td>{path}</td>
                                    <td>{status}</td>
                                </tr>
            """
        
        html_content += f"""
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2>🚀 Prossimi Passi</h2>
                        <ul>
                            <li>✅ Dati estratti con successo da Google Analytics</li>
                            <li>✅ Report di base generato automaticamente</li>
                            <li>🔄 Per analisi avanzate: integrare completamente gli agenti Claude Code</li>
                            <li>📈 Configurare esecuzione settimanale automatica</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🤖 Generato da <strong>MASPE-SAW</strong> (SEO Analytics Weekly)</p>
                    <p>Sistema di automazione analisi SEO/SEM per Maspe</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _extract_statistics(self, data_files: Dict[str, str]) -> Dict[str, Any]:
        """Estrae statistiche dai file CSV per il report"""
        stats = {}
        
        try:
            import pandas as pd
            
            # Leggi dati principali
            if 'dati_giornalieri' in data_files and os.path.exists(data_files['dati_giornalieri']):
                df = pd.read_csv(data_files['dati_giornalieri'])
                stats['total_users'] = f"{df['utenti'].sum():,}"
                stats['avg_users_day'] = f"{df['utenti'].mean():.0f}"
                if 'moduli' in df.columns:
                    stats['total_conversions'] = f"{df['moduli'].sum()}"
                if 'costo' in df.columns:
                    stats['total_cost'] = f"{df['costo'].sum():.2f}"
            
        except Exception as e:
            logger.warning(f"Errore estrazione statistiche: {e}")
            stats = {
                'total_users': 'N/A',
                'avg_users_day': 'N/A', 
                'total_conversions': 'N/A',
                'total_cost': 'N/A'
            }
        
        return stats


if __name__ == "__main__":
    # Test integrazione
    print("Test integrazione Claude Code per MASPE-SAW")
    
    integration = ClaudeCodeIntegration()
    
    # File di test
    test_files = {
        "dati_giornalieri": "/tmp/maspe-dati.csv",
        "campagne": "/tmp/maspe-campagne.csv",
        "pagine": "/tmp/maspe-pagine.csv",
        "queries": "/tmp/maspe-queries.csv"
    }
    
    # Test analisi
    analysis = integration.analyze_data_with_claude(
        test_files, "2025-07-19", "2025-07-26"
    )
    print(f"Analisi: {analysis['status']}")
    
    # Test report
    report_path = "/tmp/test_report.html"
    integration.generate_report_with_claude(
        analysis, test_files, "2025-07-19", "2025-07-26", report_path
    )
    print(f"Report generato: {report_path}")