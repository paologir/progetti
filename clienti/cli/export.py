#!/usr/bin/env python3
"""
Export module - Generate Obsidian-compatible Markdown files and other exports
"""
import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List
import csv

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.table import Table
import typer
from sqlalchemy import text

from core.database import SessionLocal
from core.models import Cliente, TimeTracking, Todo, ScadenzeFatturazione, Intervento

console = Console()


def export_obsidian_vault(output_dir: str, include_completed: bool = False):
    """
    Export all data to Obsidian-compatible Markdown files
    """
    if not output_dir:
        console.print("❌ Output directory richiesta", style="red")
        return False
    
    output_path = Path(output_dir)
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"❌ Errore creazione directory: {e}", style="red")
            return False
    
    console.print(f"📁 Export Obsidian vault in: {output_path}", style="blue")
    
    session = SessionLocal()
    try:
        # Crea directory strutturate
        directories = {
            'clienti': output_path / "Clienti",
            'progetti': output_path / "Progetti", 
            'reports': output_path / "Reports",
            'templates': output_path / "Templates"
        }
        
        for dir_path in directories.values():
            dir_path.mkdir(exist_ok=True)
        
        with Progress() as progress:
            # Task di export
            task_clienti = progress.add_task("Export clienti...", total=None)
            task_reports = progress.add_task("Export reports...", total=None) 
            task_templates = progress.add_task("Export templates...", total=None)
            
            # Export clienti individuali
            clienti = session.query(Cliente).all()
            progress.update(task_clienti, total=len(clienti))
            
            for i, cliente in enumerate(clienti):
                _export_cliente_markdown(cliente, directories['clienti'], session, include_completed)
                progress.update(task_clienti, advance=1)
            
            # Export report aggregati
            progress.update(task_reports, total=3)
            _export_dashboard_report(directories['reports'], session)
            progress.update(task_reports, advance=1)
            
            _export_statistics_report(directories['reports'], session)
            progress.update(task_reports, advance=1)
            
            _export_todo_report(directories['reports'], session, include_completed)
            progress.update(task_reports, advance=1)
            
            # Export templates
            progress.update(task_templates, total=2)
            _export_obsidian_templates(directories['templates'])
            progress.update(task_templates, advance=1)
            
            _export_index_file(output_path, len(clienti))
            progress.update(task_templates, advance=1)
    finally:
        session.close()
    
    console.print("✅ Export Obsidian completato!", style="green")
    return True


def _export_cliente_markdown(cliente: Cliente, output_dir: Path, session, include_completed: bool):
    """Export singolo cliente in formato Markdown"""
    
    filename = f"{cliente.nome.replace('/', '_').replace(' ', '_')}.md"
    filepath = output_dir / filename
    
    # Raccolta dati
    ore_totali = session.query(
        session.query(TimeTracking).filter(
            TimeTracking.cliente_id == cliente.id,
            TimeTracking.fine != None
        ).count()
    ).scalar() or 0
    
    ore_non_fatturate = session.query(TimeTracking).filter(
        TimeTracking.cliente_id == cliente.id,
        TimeTracking.fine != None,
        TimeTracking.fatturato == False
    ).count()
    
    # Todo aperti
    todos_aperti = session.query(Todo).filter(
        Todo.cliente_id == cliente.id,
        Todo.completato == False
    ).order_by(Todo.scadenza.asc()).all()
    
    # Ultimi interventi
    interventi = session.query(Intervento).filter(
        Intervento.cliente_id == cliente.id
    ).order_by(Intervento.data.desc()).limit(10).all()
    
    # Scadenze attive
    scadenze = session.query(ScadenzeFatturazione).filter(
        ScadenzeFatturazione.cliente_id == cliente.id,
        ScadenzeFatturazione.emessa == False
    ).order_by(ScadenzeFatturazione.data_scadenza.asc()).all()
    
    # Genera Markdown
    content = f"""# {cliente.nome}

## 📊 Informazioni

| Campo | Valore |
|-------|--------|
| **Stato** | {cliente.stato} |
| **P.IVA** | {cliente.piva or 'N/A'} |
| **Indirizzo** | {cliente.indirizzo_completo or 'N/A'} |
| **Tariffa** | €{cliente.tariffa_oraria}/h |
| **Tags** | {', '.join(cliente.tags_list) if cliente.tags_list else 'Nessun tag'} |

## 📈 Statistiche

- **Ore totali**: {ore_totali}h
- **Ore da fatturare**: {ore_non_fatturate}h  
- **Todo aperti**: {len(todos_aperti)}
- **Scadenze attive**: {len(scadenze)}

## ✅ Todo Aperti

"""
    
    if todos_aperti:
        for todo in todos_aperti:
            priorita_emoji = "🔴" if todo.priorita == 1 else "🟢" if todo.priorita == -1 else "🟡"
            scadenza_str = f" (📅 {todo.scadenza.strftime('%d/%m/%Y')})" if todo.scadenza else ""
            content += f"- [ ] {priorita_emoji} **{todo.titolo}**{scadenza_str}\n"
            if todo.descrizione:
                content += f"  > {todo.descrizione}\n"
        content += "\n"
    else:
        content += "Nessun todo aperto.\n\n"
    
    # Scadenze
    content += "## 💰 Scadenze Attive\n\n"
    if scadenze:
        for scadenza in scadenze:
            urgente = "🔴 " if scadenza.is_overdue else ""
            importo = f"€{scadenza.importo_previsto}" if scadenza.importo_fisso else "DA DEFINIRE"
            content += f"- {urgente}**{scadenza.data_scadenza.strftime('%d/%m/%Y')}** - {scadenza.descrizione or scadenza.tipo} ({importo})\n"
        content += "\n"
    else:
        content += "Nessuna scadenza attiva.\n\n"
    
    # Ultimi interventi  
    content += "## 📝 Ultimi Interventi\n\n"
    if interventi:
        for intervento in interventi:
            durata = f" ({intervento.durata_minuti}min)" if intervento.durata_minuti else ""
            content += f"- **{intervento.data.strftime('%d/%m/%Y %H:%M')}** {intervento.tipo_icon} {intervento.titolo}{durata}\n"
            if intervento.descrizione:
                content += f"  > {intervento.descrizione}\n"
        content += "\n"
    else:
        content += "Nessun intervento registrato.\n\n"
    
    # Note
    if cliente.note:
        content += f"## 📝 Note\n\n{cliente.note}\n\n"
    
    # Collegamenti
    content += """## 🔗 Collegamenti

- [[Dashboard CRM]] - Torna alla dashboard principale
- [[Reports]] - Visualizza reports
- #cliente"""
    
    if cliente.tags_list:
        for tag in cliente.tags_list:
            content += f" #{tag.lower().replace(' ', '_')}"
    
    content += f"\n\n---\n*Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}*"
    
    # Scrivi file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def _export_dashboard_report(output_dir: Path, session):
    """Export report dashboard generale"""
    
    filepath = output_dir / "Dashboard_CRM.md"
    oggi = date.today()
    
    # Statistiche
    clienti_attivi = session.query(Cliente).filter(Cliente.stato == 'attivo').count()
    clienti_totali = session.query(Cliente).count()
    
    # Timer attivo
    timer_attivo = session.query(TimeTracking).filter(TimeTracking.fine == None).first()
    
    # Todo urgenti
    todos_overdue = session.query(Todo).filter(
        Todo.scadenza < oggi,
        Todo.completato == False
    ).count()
    
    todos_oggi = session.query(Todo).filter(
        Todo.scadenza == oggi,
        Todo.completato == False
    ).count()
    
    content = f"""# Dashboard CRM

*Report generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}*

## 📊 Panoramica

| Metrica | Valore |
|---------|--------|
| **Clienti Attivi** | {clienti_attivi}/{clienti_totali} |
| **Timer Attivo** | {'✅ ' + timer_attivo.cliente.nome if timer_attivo else '❌ Nessuno'} |
| **Todo Overdue** | {todos_overdue} |
| **Todo Oggi** | {todos_oggi} |

## 🚨 Alert

"""
    
    if todos_overdue > 0:
        content += f"- 🔴 **{todos_overdue} todo in ritardo** - Richiede attenzione immediata\n"
    
    if todos_oggi > 0:
        content += f"- 🟡 **{todos_oggi} todo in scadenza oggi**\n"
    
    if timer_attivo:
        durata = datetime.now() - timer_attivo.inizio
        ore = durata.total_seconds() / 3600
        content += f"- ⏱️ **Timer attivo**: {timer_attivo.cliente.nome} ({ore:.1f}h)\n"
    
    if todos_overdue == 0 and todos_oggi == 0:
        content += "✅ Tutto sotto controllo!\n"
    
    content += """

## 🔗 Collegamenti Rapidi

- [[Clienti]] - Elenco clienti
- [[Reports/Statistiche]] - Report dettagliati  
- [[Templates]] - Template utili

## 📱 Azioni Rapide

- [ ] Controllare scadenze prossime
- [ ] Aggiornare time tracking
- [ ] Rivedere todo prioritari

#dashboard #crm
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def _export_statistics_report(output_dir: Path, session):
    """Export report statistiche dettagliate"""
    
    filepath = output_dir / "Statistiche.md"
    oggi = date.today()
    mese_corrente = oggi.replace(day=1)
    
    # Statistiche mese
    ore_mese = session.execute(text("""
        SELECT COALESCE(SUM((julianday(fine) - julianday(inizio)) * 24), 0)
        FROM time_tracking 
        WHERE fine IS NOT NULL 
        AND date(inizio) >= :mese_corrente
    """), {"mese_corrente": mese_corrente}).scalar()
    
    clienti_per_stato = session.execute(text("""
        SELECT stato, COUNT(*) 
        FROM clienti 
        GROUP BY stato
    """)).fetchall()
    
    content = f"""# Statistiche CRM

*Report generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}*

## 📅 Mese Corrente ({mese_corrente.strftime('%B %Y')})

- **Ore lavorate**: {ore_mese:.1f}h
- **Fatturato stimato**: €{ore_mese * 50:.0f}

## 👥 Distribuzione Clienti

"""
    
    for stato, count in clienti_per_stato:
        emoji = {"attivo": "🟢", "prospect": "🟡", "pausa": "⏸️", "archiviato": "📦"}.get(stato, "⚪")
        content += f"- {emoji} **{stato.title()}**: {count}\n"
    
    content += """

## 📈 Trend

> Per statistiche complete utilizzare `clienti stats` da CLI

#statistiche #report #kpi
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def _export_todo_report(output_dir: Path, session, include_completed: bool):
    """Export report todo e task"""
    
    filepath = output_dir / "Todo_Report.md"
    oggi = date.today()
    
    # Todo per priorità e stato
    todos_query = session.query(Todo)
    if not include_completed:
        todos_query = todos_query.filter(Todo.completato == False)
    
    todos = todos_query.order_by(Todo.priorita.desc(), Todo.scadenza.asc()).all()
    
    content = f"""# Report Todo

*Report generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}*

## 📊 Statistiche

| Stato | Count |
|-------|-------|
| **Aperti** | {len([t for t in todos if not t.completato])} |
"""
    
    if include_completed:
        content += f"| **Completati** | {len([t for t in todos if t.completato])} |\n"
    
    overdue = [t for t in todos if not t.completato and t.is_overdue]
    oggi_scadenza = [t for t in todos if not t.completato and t.scadenza == oggi]
    
    content += f"| **In ritardo** | {len(overdue)} |\n"
    content += f"| **Scadono oggi** | {len(oggi_scadenza)} |\n"
    
    # Todo per priorità
    content += "\n## 🔴 Alta Priorità\n\n"
    alta_priorita = [t for t in todos if not t.completato and t.priorita == 1]
    if alta_priorita:
        for todo in alta_priorita:
            status = "🔴 OVERDUE" if todo.is_overdue else "⏳"
            cliente_str = f" - [[{todo.cliente.nome}]]" if todo.cliente else ""
            scadenza_str = f" (📅 {todo.scadenza.strftime('%d/%m')})" if todo.scadenza else ""
            content += f"- [ ] **{todo.titolo}**{cliente_str}{scadenza_str} {status}\n"
    else:
        content += "Nessun todo ad alta priorità.\n"
    
    content += "\n## 🟡 Priorità Normale\n\n"
    normale = [t for t in todos if not t.completato and t.priorita == 0][:10]  # Primi 10
    if normale:
        for todo in normale:
            status = "🔴 OVERDUE" if todo.is_overdue else "⏳"
            cliente_str = f" - [[{todo.cliente.nome}]]" if todo.cliente else ""
            scadenza_str = f" (📅 {todo.scadenza.strftime('%d/%m')})" if todo.scadenza else ""
            content += f"- [ ] {todo.titolo}{cliente_str}{scadenza_str} {status}\n"
        if len([t for t in todos if not t.completato and t.priorita == 0]) > 10:
            restanti = len([t for t in todos if not t.completato and t.priorita == 0]) - 10
            content += f"\n*... e altri {restanti} todo normali*\n"
    else:
        content += "Nessun todo a priorità normale.\n"
    
    content += "\n#todo #task #planning\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def _export_obsidian_templates(output_dir: Path):
    """Crea template Obsidian utili"""
    
    # Template cliente
    template_cliente = """# {{title}}

## 📊 Informazioni

| Campo | Valore |
|-------|--------|
| **Stato** | |
| **P.IVA** | |
| **Indirizzo** | |
| **Tariffa** | €/h |
| **Tags** | |

## 📝 Note

## ✅ Todo

- [ ] 

## 📞 Log Contatti

### {{date}}
- 

#cliente #template
"""
    
    # Template progetto
    template_progetto = """# Progetto {{title}}

**Cliente**: [[]]
**Data inizio**: {{date}}
**Budget**: €
**Stato**: 🟡 In corso

## 🎯 Obiettivi

- 

## 📋 Task

- [ ] 
- [ ] 
- [ ] 

## 📝 Note

## 🔗 Risorse

#progetto #template
"""
    
    # Template meeting
    template_meeting = """# Meeting {{title}}

**Data**: {{date}} {{time}}
**Partecipanti**: 
**Cliente**: [[]]

## 📋 Agenda

- 

## 📝 Note

## ✅ Action Items

- [ ] 
- [ ] 

## 🔗 Follow-up

#meeting #template
"""
    
    templates = {
        "Template_Cliente.md": template_cliente,
        "Template_Progetto.md": template_progetto,
        "Template_Meeting.md": template_meeting
    }
    
    for filename, content in templates.items():
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def _export_index_file(output_dir: Path, num_clienti: int):
    """Crea file indice principale"""
    
    filepath = output_dir / "README.md"
    
    content = f"""# CRM Clienti - Obsidian Vault

Export generato il {datetime.now().strftime('%d/%m/%Y %H:%M')} dal sistema Clienti CRM.

## 📁 Struttura

- **Clienti/** - {num_clienti} schede clienti individuali
- **Progetti/** - Progetti e iniziative 
- **Reports/** - Dashboard e statistiche
- **Templates/** - Template per nuovi contenuti

## 🔗 Collegamenti Principali

- [[Dashboard CRM]] - Panoramica generale
- [[Reports/Statistiche]] - KPI e metriche
- [[Reports/Todo Report]] - Task e attività

## 📱 Come Usare

1. Apri con Obsidian
2. Abilita i plugin Graph View e Templates
3. Usa i collegamenti [[]] per navigare
4. Cerca per tag: #cliente #progetto #meeting

## 🔄 Aggiornamento

Per aggiornare i dati, esegui da CLI:
```bash
clienti export obsidian --output /path/to/vault/
```

#crm #index #obsidian
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def export_cliente_markdown(cliente_nome: str, output_file: str = None):
    """Export specifico cliente in Markdown"""
    
    session = SessionLocal()
    try:
        cliente = session.query(Cliente).filter(Cliente.nome.ilike(f"%{cliente_nome}%")).first()
        
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return False
        
        if not output_file:
            output_file = f"{cliente.nome.replace(' ', '_')}.md"
        
        output_path = Path(output_file)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        _export_cliente_markdown(cliente, output_dir, session, True)
        
        console.print(f"✅ Cliente esportato: {output_path}", style="green")
        return True
    finally:
        session.close()


def export_csv_clienti(output_file: str):
    """Export clienti in formato CSV"""
    
    session = SessionLocal()
    try:
        clienti = session.query(Cliente).all()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['nome', 'piva', 'cf', 'indirizzo', 'citta', 'cap', 'provincia', 
                         'stato', 'tariffa_oraria', 'budget_mensile', 'tags', 'note']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for cliente in clienti:
                writer.writerow({
                    'nome': cliente.nome,
                    'piva': cliente.piva or '',
                    'cf': cliente.cf or '',
                    'indirizzo': cliente.indirizzo or '',
                    'citta': cliente.citta or '',
                    'cap': cliente.cap or '',
                    'provincia': cliente.provincia or '',
                    'stato': cliente.stato,
                    'tariffa_oraria': cliente.tariffa_oraria,
                    'budget_mensile': cliente.budget_mensile or '',
                    'tags': ', '.join(cliente.tags_list) if cliente.tags_list else '',
                    'note': cliente.note or ''
                })
        
        console.print(f"✅ {len(clienti)} clienti esportati in: {output_file}", style="green")
        return True
    finally:
        session.close()


def import_csv_clienti(input_file: str, dry_run: bool = True):
    """Import clienti da file CSV"""
    
    if not os.path.exists(input_file):
        console.print(f"❌ File non trovato: {input_file}", style="red")
        return False
    
    console.print(f"📥 Import clienti da: {input_file}", style="blue")
    
    session = SessionLocal()
    try:
        importati = 0
        errori = 0
        
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    # Controlla se cliente esiste già
                    esistente = session.query(Cliente).filter(
                        Cliente.nome == row['nome']
                    ).first()
                    
                    if esistente:
                        console.print(f"⚠️  Cliente già esistente: {row['nome']}", style="yellow")
                        continue
                    
                    if not dry_run:
                        # Crea nuovo cliente
                        tags_list = [t.strip() for t in row.get('tags', '').split(',') if t.strip()]
                        
                        cliente = Cliente(
                            nome=row['nome'],
                            piva=row.get('piva') or None,
                            cf=row.get('cf') or None,
                            indirizzo=row.get('indirizzo') or None,
                            citta=row.get('citta') or None,
                            cap=row.get('cap') or None,
                            provincia=row.get('provincia') or None,
                            stato=row.get('stato', 'attivo'),
                            tariffa_oraria=float(row.get('tariffa_oraria', 50)),
                            budget_mensile=float(row.get('budget_mensile')) if row.get('budget_mensile') else None,
                            note=row.get('note') or None
                        )
                        
                        if tags_list:
                            cliente.tags_list = tags_list
                        
                        session.add(cliente)
                        
                    importati += 1
                    
                except Exception as e:
                    console.print(f"❌ Errore riga {reader.line_num}: {e}", style="red")
                    errori += 1
        
        if not dry_run:
            session.commit()
            console.print(f"✅ {importati} clienti importati, {errori} errori", style="green")
        else:
            console.print(f"🔍 DRY RUN: {importati} clienti da importare, {errori} errori", style="blue")
            console.print("Usa --no-dry-run per importare realmente", style="yellow")
        
        return True
    finally:
        session.close()