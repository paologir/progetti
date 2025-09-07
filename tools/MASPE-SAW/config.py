"""
Configurazione MASPE-SAW
"""

import os
from pathlib import Path

# Path base del progetto
BASE_DIR = Path(__file__).parent

# Configurazione Google Analytics
GOOGLE_SERVICE_ACCOUNT_JSON = "/opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json"
GA_PROPERTY_ID = "353989568"  # Maspe da marzo 2023

# Script R
R_SCRIPT_PATH = BASE_DIR / "maspe-console-automated.r"  # Script automatizzato
R_SCRIPT_ORIGINAL = "/opt/progetti/r/maspe-console-json.r"  # Script originale interattivo
R_SCRIPT_MOCK_PATH = BASE_DIR / "test_r_mock.r"

# Modalità di esecuzione
USE_MOCK_DATA = os.getenv("MASPE_USE_MOCK", "false").lower() == "true"

# Directory output
REPORTS_DIR = BASE_DIR / "reports"
TEMP_DIR = Path("/tmp")

# File temporanei generati dallo script R
TEMP_FILES = {
    "dati_giornalieri": "/tmp/maspe-dati.csv",
    "campagne": "/tmp/maspe-campagne.csv", 
    "pagine": "/tmp/maspe-pagine.csv",
    "queries": "/tmp/maspe-queries.csv",
    "grafico": "/tmp/ts-maspe.jpg"
}

# Configurazione report
REPORT_SETTINGS = {
    "formato_default": "html",
    "includi_grafici": True,
    "lingua": "it"
}

# Logging
LOG_LEVEL = os.getenv("MASPE_LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "maspe_seo_analysis.log"

# Configurazione prompt generator
PROMPT_SETTINGS = {
    "max_rows_per_table": 20,  # Numero massimo di righe per tabella nel prompt
    "include_analysis_results": True,  # Include risultati analisi base nel prompt
    "prompt_filename_prefix": "analysis_prompt",  # Prefisso per i file prompt generati
}