#!/usr/bin/env python3
"""
Script per eseguire MASPE-SAW con integrazione completa Claude Code
Questo script deve essere eseguito all'interno di Claude Code per utilizzare gli agenti
"""

import sys
import os
from pathlib import Path

# Aggiungi il path del progetto
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import MaspeSEOOrchestrator
import logging

logger = logging.getLogger(__name__)

def run_with_claude_agents(use_real_data=False, weeks_back=1):
    """
    Esegue MASPE-SAW con integrazione completa Claude Code
    """
    print("🚀 MASPE-SAW con Agenti Claude Code")
    print("=" * 50)
    
    # Verifica se siamo in Claude Code
    try:
        # Tenta di accedere al Task tool di Claude Code
        if 'Task' in globals() or hasattr(__builtins__, 'Task'):
            print("✅ Rilevato ambiente Claude Code")
            claude_available = True
        else:
            print("⚠️  Non in ambiente Claude Code - usando simulazione")
            claude_available = False
    except:
        claude_available = False
    
    # Configura orchestratore
    orchestrator = MaspeSEOOrchestrator(use_mock=not use_real_data)
    
    try:
        print(f"\n📊 Avvio analisi {'con dati reali' if use_real_data else 'con dati mock'}")
        print(f"📅 Periodo: ultime {weeks_back} settimane")
        
        # Esegui analisi
        success = orchestrator.run(weeks_back=weeks_back, cleanup=False)
        
        if success:
            print("\n✅ ANALISI COMPLETATA CON SUCCESSO!")
            print(f"📁 Report generato in: {orchestrator.output_dir}")
            
            if claude_available:
                print("🤖 Agenti Claude Code utilizzati per analisi avanzate")
            else:
                print("📝 Report di base generato (per analisi avanzate eseguire in Claude Code)")
                
        else:
            print("\n❌ ANALISI FALLITA")
            
        return success
        
    except Exception as e:
        print(f"\n💥 ERRORE: {e}")
        logger.error(f"Errore esecuzione: {e}", exc_info=True)
        return False

def main():
    """Interfaccia command line"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MASPE-SAW con Agenti Claude Code"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Usa dati reali da Google Analytics"
    )
    parser.add_argument(
        "--settimane",
        type=int,
        default=1,
        help="Numero di settimane da analizzare"
    )
    
    args = parser.parse_args()
    
    success = run_with_claude_agents(
        use_real_data=args.real,
        weeks_back=args.settimane
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()