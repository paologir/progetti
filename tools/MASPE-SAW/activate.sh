#!/bin/bash
# Script per attivare l'ambiente virtuale MASPE-SAW

echo "Attivazione ambiente virtuale MASPE-SAW..."
source $(dirname "$0")/venv/bin/activate
echo "✓ Ambiente attivato. Usa 'deactivate' per uscire."
echo ""
echo "Comandi disponibili:"
echo "  python orchestrator.py --mock   - Analisi con dati mock"
echo "  python orchestrator.py --real   - Analisi con dati reali"
echo "  python run_with_claude_agents.py --real  - Analisi avanzata con Claude Code"
echo "  python generate_mock_data.py   - Genera dati di test"
echo ""
echo "Variabili ambiente:"
echo "  export MASPE_USE_MOCK=true      - Modalità mock di default"
echo ""
echo "Agenti Claude Code:"
echo "  .claude/agents/data-analysis-expert.md"
echo "  .claude/agents/seo-sem-report-expert.md"
echo ""