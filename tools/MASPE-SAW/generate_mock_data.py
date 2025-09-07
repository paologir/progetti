#!/usr/bin/env python3
"""
Generatore di dati mock per test MASPE-SAW
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_mock_data(start_date, end_date):
    """Genera dati mock per il periodo specificato"""
    
    # Converti stringhe in date
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # Genera range di date
    date_range = pd.date_range(start=start, end=end, freq='D')
    n_days = len(date_range)
    
    print(f"Generazione dati mock per {n_days} giorni: {start_date} - {end_date}")
    
    # Imposta seed per riproducibilità
    np.random.seed(42)
    
    # Genera dati giornalieri
    df_maspe = pd.DataFrame({
        'data': date_range,
        'day_of_week': [d.strftime('%A') for d in date_range],
        'utenti': np.random.normal(150, 30, n_days).astype(int),
        'organici': np.random.normal(100, 20, n_days).astype(int),
        'modulo_infoprodotto': np.random.poisson(2, n_days),
        'modulo_generico': np.random.poisson(3, n_days),
        'costo': np.round(np.random.uniform(50, 200, n_days), 2)
    })
    
    # Assicura valori positivi
    df_maspe['utenti'] = df_maspe['utenti'].clip(lower=50)
    df_maspe['organici'] = df_maspe['organici'].clip(lower=30)
    df_maspe['moduli'] = df_maspe['modulo_infoprodotto'] + df_maspe['modulo_generico']
    
    # Salva dati giornalieri
    df_maspe.to_csv('/tmp/maspe-dati.csv', index=False)
    print("✓ Creato /tmp/maspe-dati.csv")
    
    # Genera dati campagne
    campagne = pd.DataFrame({
        'campaignName': ['Brand', 'Prodotti', 'Servizi', 'Remarketing'],
        'AdvertiserAdCost': [450.50, 320.75, 280.00, 150.25],
        'conversions:modulo_generico': [12, 8, 10, 5],
        'conversions:modulo_infoprodotto': [5, 3, 7, 2]
    })
    campagne.to_csv('/tmp/maspe-campagne.csv', index=False)
    print("✓ Creato /tmp/maspe-campagne.csv")
    
    # Genera dati pagine
    pages = pd.DataFrame({
        'page': ['/', '/servizi', '/contatti', '/chi-siamo', '/prodotti/dettaglio-1'],
        'clicks': [250, 180, 120, 90, 75],
        'impressions': [3500, 2800, 1500, 1200, 900],
        'ctr': [7.14, 6.43, 8.00, 7.50, 8.33],
        'position': [2.5, 3.2, 4.1, 5.3, 6.7]
    })
    pages.to_csv('/tmp/maspe-pagine.csv', index=False)
    print("✓ Creato /tmp/maspe-pagine.csv")
    
    # Genera dati queries
    queries = pd.DataFrame({
        'query': ['maspe', 'servizi maspe', 'azienda maspe', 'prodotti industriali', 'consulenza tecnica'],
        'clicks': [180, 120, 85, 60, 45],
        'impressions': [2200, 1800, 1200, 950, 720],
        'ctr': [8.18, 6.67, 7.08, 6.32, 6.25],
        'position': [1.2, 2.8, 3.5, 4.2, 5.1]
    })
    queries.to_csv('/tmp/maspe-queries.csv', index=False)
    print("✓ Creato /tmp/maspe-queries.csv")
    
    # Crea grafico mock (file vuoto per ora)
    with open('/tmp/ts-maspe.jpg', 'wb') as f:
        # Crea un file JPG vuoto minimo
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9')
    print("✓ Creato /tmp/ts-maspe.jpg (placeholder)")
    
    # Mostra statistiche
    print("\n=== STATISTICHE MOCK ===")
    print(f"Utenti totali: {df_maspe['utenti'].sum()}")
    print(f"Media utenti/giorno: {df_maspe['utenti'].mean():.1f}")
    print(f"Conversioni totali: {df_maspe['moduli'].sum()}")
    print(f"Costo totale: €{df_maspe['costo'].sum():.2f}")
    
    return True

if __name__ == "__main__":
    import sys
    
    # Se chiamato da linea di comando con date
    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    else:
        # Date di default (ultima settimana)
        end = datetime.now() - timedelta(days=1)
        start = end - timedelta(days=7)
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")
    
    success = generate_mock_data(start_date, end_date)
    sys.exit(0 if success else 1)