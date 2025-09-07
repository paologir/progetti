#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import sys
import re

def scarica_sitemap(url):
    """Scarica la sitemap dall'URL specificato."""
    try:
        # Aggiungi 'https://' se non presente nell'URL
        if not url.startswith("http"):
            url = "https://" + url
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della sitemap: {e}")
        return None

def parse_sitemap(xml_content):
    """Analizza il contenuto XML della sitemap ed estrae gli URL."""
    try:
        root = ET.fromstring(xml_content)
        urls = []
        for url_element in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            urls.append(url_element.text)
        return urls
    except ET.ParseError as e:
        print(f"Errore durante l'analisi della sitemap: {e}")
        return None

def crea_file_testo(urls, filename="sitemap.txt"):
    """Crea un file di testo con una lista di URL, uno per riga."""
    if not urls:
        print("Nessun URL trovato per generare il file di testo.")
        return
    try:
        with open(filename, "w") as f:
            for url in urls:
                f.write(url + "\n")
        print(f"File di testo creato con successo: {filename}")
    except (IOError, OSError) as e:
        print(f"Errore nella creazione del file di testo: {e}")

def crea_file_excel(urls, filename="sitemap.xlsx"):
    """Crea un file Excel con una tabella contenente gli URL."""
    if not urls:
        print("Nessun URL trovato per generare il file Excel.")
        return
    try:
        df = pd.DataFrame({"URL": urls})
        df.to_excel(filename, index=False)
        print(f"File Excel creato con successo: {filename}")
    except Exception as e:
        print(f"Errore nella creazione del file Excel: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sitemap_url = sys.argv[1]
    else:
        sitemap_url = input("Inserisci l'URL della sitemap: ")

    xml_content = scarica_sitemap(sitemap_url)

    if xml_content:
        urls = parse_sitemap(xml_content)
        if urls:
            crea_file_testo(urls)
            crea_file_excel(urls)
