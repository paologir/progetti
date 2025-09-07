#!/usr/bin/env python3

import json
import os
import time
import pandas as pd
import requests
from colorama import Fore, Style, init

# Inizializza colorama per resettare automaticamente i colori
init(autoreset=True)

# Get the absolute path of the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the absolute path to the config file
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')


def leggi_configurazione() -> dict:
    """Legge il file di configurazione JSON."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Errore: File di configurazione {CONFIG_PATH} non trovato")
        exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Errore: File di configurazione {CONFIG_PATH} malformato")
        exit(1)


def calcola_cedola_netta(cedola_annua: float, nome_titolo: str) -> str:
    """Calcola la cedola netta per 1000 euro di investimento."""
    cedola_lorda_1000 = 1000 * (cedola_annua / 100)
    cedola_netta_1000 = cedola_lorda_1000 * 0.875  # Ritenuta fiscale al 12.5%

    if "Btp" in nome_titolo:
        cedola_semestrale = cedola_netta_1000 / 2
        return f"{cedola_semestrale:.2f} + {cedola_semestrale:.2f} euro"
    else:
        return f"{cedola_netta_1000:.2f} euro"


def recupera_prezzo(isin: str) -> float | None:
    """Recupera il prezzo di un titolo e lo normalizza."""
    urls = [
        f"https://www.borsaitaliana.it/borsa/obbligazioni/mot/euro-obbligazioni/dati-completi.html?isin={isin}&lang=it",
        f"https://www.borsaitaliana.it/borsa/obbligazioni/mot/btp/scheda/{isin}.html?lang=it"
    ]
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    headers = {
        'User-Agent': USER_AGENTS[int(time.time()) % len(USER_AGENTS)]
    }

    for i, url in enumerate(urls):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            tables = pd.read_html(response.content)

            prezzo_str = None
            # Logica per Euro-obbligazioni
            if i == 0 and len(tables) > 2:
                # Cerca il prezzo nell'etichetta 'Ultimo Prezzo' o come fallback in una posizione fissa
                prezzo_row = tables[2][tables[2][0] == 'Ultimo Prezzo']
                if not prezzo_row.empty:
                    prezzo_str = str(prezzo_row.iloc[0, 1])
                else:
                    prezzo_str = str(tables[2].iloc[8, 1]) # Fallback

            # Logica per BTP
            elif i == 1 and len(tables) > 0:
                prezzo_row = tables[0][tables[0][0] == 'Prezzo Ultimo Contratto']
                if not prezzo_row.empty:
                    prezzo_str = str(prezzo_row.iloc[0, 1])

            if prezzo_str and prezzo_str != '--':
                # Pulisce la stringa e converte in float
                valore_pulito = prezzo_str.replace('.', '').replace(',', '.')
                # Divide per 100 come suggerito
                return float(valore_pulito) / 100.0

        except (requests.exceptions.RequestException, IndexError, KeyError, ValueError):
            continue

    return None


def main() -> None:
    """Esegue il monitoraggio dei titoli in base alla configurazione e mostra i risultati."""
    """Funzione principale del programma."""
    config = leggi_configurazione()
    print("--- Avvio Monitoraggio Titoli ---")
    print(f"{'NOME TITOLO':<30} | {'QUOTAZIONE':>15} | {'SOGLIA':>10} | {'CEDOLA NETTA ANNUA (1k)':>25}")
    print("-" * 90)

    for titolo in config['titoli']:
        isin = titolo['isin']
        nome = titolo['nome']
        soglia = titolo['soglia_prezzo']
        cedola_annua = titolo.get('cedola_annua', 0.0)

        prezzo = recupera_prezzo(isin)
        cedola_formattata = calcola_cedola_netta(cedola_annua, nome)

        if prezzo is not None:
            colore = Fore.GREEN if prezzo >= soglia else Fore.RED
            print(f"{colore}{nome:<30} | {prezzo:>15.3f} | {soglia:>10.2f} | {cedola_formattata:>25}")
        else:
            print(f"{Fore.YELLOW}{nome:<30} | {'N/D':>15} | {soglia:>10.2f} | {cedola_formattata:>25}")
        
        time.sleep(1)

    print()
    print("--- Monitoraggio completato ---")


if __name__ == "__main__":
    main()
