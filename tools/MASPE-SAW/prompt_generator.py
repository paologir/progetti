#!/usr/bin/env python3
"""
Generatore di prompt per analisi SEO/SEM con LLM
Crea un prompt strutturato con tutti i dati rilevanti per l'analisi manuale
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Genera prompt strutturati per analisi SEO/SEM con LLM esterni"""
    
    def __init__(self):
        self.max_rows_per_table = 20  # Limita righe per mantenere prompt gestibile
        
    def generate_analysis_prompt(self, data_files: Dict[str, str], 
                               start_date: str, end_date: str,
                               analysis_results: Optional[Dict[str, Any]] = None) -> str:
        """
        Genera un prompt completo con tutti i dati per l'analisi
        
        Args:
            data_files: Dizionario con percorsi dei file CSV
            start_date: Data inizio periodo
            end_date: Data fine periodo
            analysis_results: Risultati analisi base (opzionale)
            
        Returns:
            Prompt formattato per LLM
        """
        logger.info(f"Generazione prompt analisi per periodo {start_date} - {end_date}")
        
        # Raccogli dati da tutti i file
        data_sections = []
        
        # 1. Dati traffico giornaliero
        if 'dati_giornalieri' in data_files and os.path.exists(data_files['dati_giornalieri']):
            traffic_section = self._format_traffic_data(data_files['dati_giornalieri'])
            if traffic_section:
                data_sections.append(traffic_section)
        
        # 2. Performance campagne
        if 'campagne' in data_files and os.path.exists(data_files['campagne']):
            campaigns_section = self._format_campaigns_data(data_files['campagne'])
            if campaigns_section:
                data_sections.append(campaigns_section)
        
        # 3. Top pagine organiche
        if 'pagine' in data_files and os.path.exists(data_files['pagine']):
            pages_section = self._format_pages_data(data_files['pagine'])
            if pages_section:
                data_sections.append(pages_section)
        
        # 4. Top query di ricerca
        if 'queries' in data_files and os.path.exists(data_files['queries']):
            queries_section = self._format_queries_data(data_files['queries'])
            if queries_section:
                data_sections.append(queries_section)
        
        # Costruisci prompt completo
        prompt = self._build_complete_prompt(
            data_sections, start_date, end_date, analysis_results
        )
        
        return prompt
    
    def _format_traffic_data(self, filepath: str) -> Optional[str]:
        """Formatta i dati di traffico giornaliero"""
        try:
            df = pd.read_csv(filepath)
            
            # Calcola metriche aggregate
            total_users = df['utenti'].sum()
            total_organic = df['utenti_organici'].sum() if 'utenti_organici' in df else 0
            total_conversions = df['moduli'].sum() if 'moduli' in df else 0
            avg_users = df['utenti'].mean()
            
            # Prepara tabella riassuntiva
            section = f"""## DATI TRAFFICO GIORNALIERO

**Metriche Aggregate:**
- Utenti totali: {total_users:,}
- Utenti organici: {total_organic:,}
- Conversioni totali: {total_conversions}
- Media utenti/giorno: {avg_users:.0f}

**Dettaglio Giornaliero (ultimi {min(len(df), self.max_rows_per_table)} giorni):**
```
{df.tail(self.max_rows_per_table).to_string(index=False)}
```
"""
            return section
            
        except Exception as e:
            logger.error(f"Errore formattazione dati traffico: {e}")
            return None
    
    def _format_campaigns_data(self, filepath: str) -> Optional[str]:
        """Formatta i dati delle campagne"""
        try:
            df = pd.read_csv(filepath)
            
            # Calcola metriche aggregate
            total_cost = df['costo'].sum() if 'costo' in df else 0
            total_conversions = df['conversioni'].sum() if 'conversioni' in df else 0
            
            # Calcola ROI per campagna
            if 'conversioni' in df and 'costo' in df:
                df['CPA'] = df.apply(lambda x: x['costo']/x['conversioni'] if x['conversioni'] > 0 else 0, axis=1)
                df['CPA'] = df['CPA'].round(2)
            
            section = f"""## PERFORMANCE CAMPAGNE

**Metriche Aggregate:**
- Costo totale: €{total_cost:,.2f}
- Conversioni totali: {total_conversions}
- CPA medio: €{(total_cost/total_conversions if total_conversions > 0 else 0):.2f}

**Dettaglio per Campagna:**
```
{df.to_string(index=False)}
```
"""
            return section
            
        except Exception as e:
            logger.error(f"Errore formattazione dati campagne: {e}")
            return None
    
    def _format_pages_data(self, filepath: str) -> Optional[str]:
        """Formatta i dati delle pagine top"""
        try:
            df = pd.read_csv(filepath)
            
            # Limita alle top 10
            df_top = df.head(10)
            
            # Calcola CTR se possibile
            if 'impressioni' in df and 'click' in df:
                df_top['CTR'] = (df_top['click'] / df_top['impressioni'] * 100).round(2)
            
            section = f"""## TOP 10 PAGINE ORGANICHE

```
{df_top.to_string(index=False)}
```
"""
            return section
            
        except Exception as e:
            logger.error(f"Errore formattazione dati pagine: {e}")
            return None
    
    def _format_queries_data(self, filepath: str) -> Optional[str]:
        """Formatta i dati delle query di ricerca"""
        try:
            df = pd.read_csv(filepath)
            
            # Limita alle top 10
            df_top = df.head(10)
            
            # Formatta posizione media
            if 'posizione' in df:
                df_top['posizione'] = df_top['posizione'].round(1)
            
            section = f"""## TOP 10 QUERY DI RICERCA

```
{df_top.to_string(index=False)}
```
"""
            return section
            
        except Exception as e:
            logger.error(f"Errore formattazione dati query: {e}")
            return None
    
    def _build_complete_prompt(self, data_sections: list, start_date: str, 
                              end_date: str, analysis_results: Optional[Dict] = None) -> str:
        """Costruisce il prompt completo per l'LLM"""
        
        # Intestazione
        prompt = f"""# Analisi SEO/SEM Maspe - Periodo {start_date} al {end_date}

Sei un esperto di digital marketing specializzato in SEO/SEM. Analizza i seguenti dati di performance del sito Maspe (www.maspe.com) e fornisci insights strategici.

"""
        
        # Aggiungi tutte le sezioni dati
        for section in data_sections:
            prompt += section + "\n"
        
        # Aggiungi risultati analisi base se disponibili
        if analysis_results:
            prompt += f"""
## ANALISI PRELIMINARE
{json.dumps(analysis_results, indent=2, ensure_ascii=False)}

"""
        
        # Richiesta di analisi
        prompt += """
## RICHIESTA DI ANALISI

Sulla base dei dati forniti, genera un report professionale che includa:

### 1. EXECUTIVE SUMMARY (massimo 1 pagina)
- **3 Principali Successi**: risultati positivi più rilevanti del periodo
- **3 Aree Critiche**: problemi o cali che richiedono attenzione immediata  
- **3 Azioni Immediate**: cosa fare subito per migliorare le performance
- **KPI Dashboard**: tabella riassuntiva delle metriche chiave con variazioni %

### 2. ANALISI DETTAGLIATA

#### A. Performance Traffico
- Analisi trend utenti (totali vs organici)
- Identificazione pattern settimanali/giornalieri
- Anomalie significative e possibili cause
- Confronto conversioni per fonte di traffico

#### B. Performance Campagne Paid
- ROI per campagna con raccomandazioni budget
- Analisi CPA e opportunità di ottimizzazione
- Campagne da potenziare vs ridurre/eliminare
- Suggerimenti per migliorare Quality Score

#### C. Performance SEO Organico
- Analisi CTR delle pagine top (opportunità quick win)
- Query ad alto potenziale da ottimizzare
- Pagine con calo di performance da investigare
- Raccomandazioni per migliorare posizionamento

### 3. RACCOMANDAZIONI STRATEGICHE

#### Quick Wins (implementabili in 1 settimana)
- Azioni immediate ad alto impatto
- Ottimizzazioni tecniche semplici
- Aggiustamenti campagne PPC

#### Medio Termine (1 mese)
- Nuove campagne o ristrutturazioni
- Ottimizzazioni contenuti esistenti
- Test A/B da implementare

#### Lungo Termine (3 mesi)
- Strategie di contenuto
- Espansione keyword strategy
- Investimenti strutturali

### 4. METRICHE DA MONITORARE
- KPI critici per le prossime settimane
- Soglie di allarme da impostare
- Benchmark di riferimento

**Note importanti per l'analisi:**
- Maspe è un'azienda B2B di servizi
- Le conversioni principali sono form di contatto (modulo_generico e modulo_infoprodotto)
- Considera la stagionalità del business B2B (weekend meno traffico)
- Fornisci numeri specifici e percentuali precise
- Usa un tono professionale ma accessibile
- Evidenzia sempre il ROI e l'impatto sul business

Genera il report in formato strutturato e professionale.
"""
        
        return prompt
    
    def save_prompt_to_file(self, prompt: str, output_dir: Path) -> str:
        """Salva il prompt in un file di testo"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"analysis_prompt_{timestamp}.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        logger.info(f"Prompt salvato in: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    # Test del generatore
    print("Test generatore prompt MASPE-SAW")
    
    generator = PromptGenerator()
    
    # File di test
    test_files = {
        "dati_giornalieri": "/tmp/maspe-dati.csv",
        "campagne": "/tmp/maspe-campagne.csv",
        "pagine": "/tmp/maspe-pagine.csv",
        "queries": "/tmp/maspe-queries.csv"
    }
    
    # Genera prompt
    prompt = generator.generate_analysis_prompt(
        test_files,
        "2025-07-21",
        "2025-07-28"
    )
    
    print("\n--- PROMPT GENERATO ---")
    print(prompt[:1000] + "...\n")  # Mostra solo primi 1000 caratteri
    
    # Salva su file
    output_path = generator.save_prompt_to_file(prompt, Path("/tmp"))
    print(f"Prompt completo salvato in: {output_path}")