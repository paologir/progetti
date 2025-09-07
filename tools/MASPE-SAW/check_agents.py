#!/usr/bin/env python3
"""
Script per verificare gli agenti Claude Code disponibili in MASPE-SAW
"""

from pathlib import Path
import sys

def check_agents():
    """Verifica agenti Claude Code disponibili"""
    print("🤖 VERIFICA AGENTI CLAUDE CODE")
    print("=" * 40)
    
    agents_dir = Path(__file__).parent / ".claude" / "agents"
    
    print(f"📂 Directory agenti: {agents_dir}")
    print(f"✅ Esiste: {agents_dir.exists()}")
    
    if not agents_dir.exists():
        print("❌ Directory agenti non trovata!")
        print("\n🔧 Per creare la directory:")
        print("mkdir -p .claude/agents")
        return False
    
    # Lista agenti disponibili
    agents = list(agents_dir.glob("*.md"))
    
    print(f"\n📋 Agenti trovati: {len(agents)}")
    
    if not agents:
        print("⚠️  Nessun agente trovato!")
        print("\n📥 Per copiare gli agenti:")
        print("cp /opt/progetti/llm/.claude/agents/*.md .claude/agents/")
        return False
    
    print("\n🎯 Agenti disponibili:")
    for agent in sorted(agents):
        print(f"  ✓ {agent.stem}")
        
        # Leggi prima riga per descrizione
        try:
            with open(agent, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Cerca la riga description nei metadati YAML
                for line in lines[:10]:
                    if line.startswith('description:'):
                        desc = line.replace('description:', '').strip()
                        if len(desc) > 80:
                            desc = desc[:77] + "..."
                        print(f"    📝 {desc}")
                        break
        except Exception as e:
            print(f"    ⚠️ Errore lettura: {e}")
    
    # Test integrazione
    print(f"\n🧪 TEST INTEGRAZIONE")
    try:
        from agent_wrapper import ClaudeAgentWrapper
        wrapper = ClaudeAgentWrapper()
        print(f"✅ Import wrapper: OK")
        print(f"✅ Path configurato: {wrapper.agents_dir}")
        print(f"✅ Directory accessibile: {wrapper.agents_dir.exists()}")
    except Exception as e:
        print(f"❌ Errore integrazione: {e}")
        return False
    
    print(f"\n🎉 Sistema agenti configurato correttamente!")
    return True

if __name__ == "__main__":
    success = check_agents()
    sys.exit(0 if success else 1)