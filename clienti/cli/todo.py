"""
Todo list CLI commands for clienti CRM
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import questionary

from core.database import SessionLocal
from core.models import Cliente, Todo

console = Console()

def get_cliente_by_name(nome: str, db: Session) -> Optional[Cliente]:
    """Find cliente by name (case insensitive search)"""
    return db.query(Cliente).filter(Cliente.nome.ilike(f"%{nome}%")).first()

def list_clienti_names(db: Session) -> list[str]:
    """Get list of client names for autocomplete"""
    clienti = db.query(Cliente).filter(Cliente.stato == 'attivo').all()
    return [c.nome for c in clienti]

def add_todo():
    """Aggiungi nuovo todo con wizard interattivo"""
    db = SessionLocal()
    
    try:
        console.print("📝 [bold]Nuovo Todo[/bold]", style="blue")
        
        # Input titolo
        titolo = questionary.text(
            "Titolo del todo:",
            validate=lambda x: len(x.strip()) > 0 or "Il titolo non può essere vuoto"
        ).ask()
        
        if not titolo:
            console.print("❌ Operazione annullata", style="red")
            return
            
        # Input descrizione opzionale
        descrizione = questionary.text("Descrizione (opzionale):").ask()
        
        # Selezione priorità
        priorita_choices = [
            {"name": "🔴 Alta", "value": 1},
            {"name": "🟡 Normale", "value": 0}, 
            {"name": "🟢 Bassa", "value": -1}
        ]
        priorita = questionary.select(
            "Priorità:",
            choices=priorita_choices
        ).ask()
        
        # Scadenza opzionale
        has_scadenza = questionary.confirm("Aggiungere scadenza?", default=False).ask()
        scadenza = None
        if has_scadenza:
            scadenza_choices = [
                {"name": "Oggi", "value": date.today()},
                {"name": "Domani", "value": date.today() + timedelta(days=1)},
                {"name": "Fine settimana", "value": date.today() + timedelta(days=(6-date.today().weekday()))},
                {"name": "Prossima settimana", "value": date.today() + timedelta(days=7)},
                {"name": "Data personalizzata", "value": "custom"}
            ]
            
            scadenza_sel = questionary.select(
                "Scadenza:",
                choices=scadenza_choices
            ).ask()
            
            if scadenza_sel == "custom":
                data_str = questionary.text(
                    "Data scadenza (YYYY-MM-DD):",
                    validate=lambda x: _validate_date(x)
                ).ask()
                if data_str:
                    scadenza = datetime.strptime(data_str, "%Y-%m-%d").date()
            else:
                scadenza = scadenza_sel
        
        # Cliente opzionale
        assign_client = questionary.confirm("Assegnare a un cliente?", default=False).ask()
        cliente = None
        if assign_client:
            clienti_names = list_clienti_names(db)
            if clienti_names:
                cliente_nome = questionary.autocomplete(
                    "Cliente:",
                    choices=clienti_names
                ).ask()
                
                if cliente_nome:
                    cliente = get_cliente_by_name(cliente_nome, db)
                    if not cliente:
                        console.print(f"⚠️ Cliente '{cliente_nome}' non trovato", style="yellow")
        
        # Crea il todo
        new_todo = Todo(
            titolo=titolo.strip(),
            descrizione=descrizione.strip() if descrizione else None,
            priorita=priorita,
            scadenza=scadenza,
            cliente_id=cliente.id if cliente else None
        )
        
        db.add(new_todo)
        db.commit()
        
        cliente_info = f" per {cliente.nome}" if cliente else ""
        scadenza_info = f" (scadenza: {scadenza})" if scadenza else ""
        
        console.print(f"✅ Todo creato{cliente_info}{scadenza_info}", style="green")
        
    except KeyboardInterrupt:
        console.print("❌ Operazione annullata", style="red")
    finally:
        db.close()

def _validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    if not date_str.strip():
        return True  # Empty is ok
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return "Formato data non valido (usa YYYY-MM-DD)"

def list_todos(
    completati: bool = False,
    cliente: Optional[str] = None,
    priorita: Optional[str] = None,
    overdue: bool = False
):
    """Lista todos con filtri"""
    db = SessionLocal()
    
    try:
        query = db.query(Todo)
        
        # Filtro completamento
        if not completati:
            query = query.filter(Todo.completato == False)
        
        # Filtro cliente
        if cliente:
            cliente_obj = get_cliente_by_name(cliente, db)
            if cliente_obj:
                query = query.filter(Todo.cliente_id == cliente_obj.id)
            else:
                console.print(f"❌ Cliente '{cliente}' non trovato", style="red")
                return
        
        # Filtro priorità
        if priorita:
            prio_map = {"alta": 1, "normale": 0, "bassa": -1}
            prio_val = prio_map.get(priorita.lower())
            if prio_val is not None:
                query = query.filter(Todo.priorita == prio_val)
        
        # Filtro overdue
        if overdue:
            today = date.today()
            query = query.filter(
                and_(
                    Todo.scadenza.isnot(None),
                    Todo.scadenza < today,
                    Todo.completato == False
                )
            )
        
        todos = query.order_by(Todo.priorita.desc(), Todo.scadenza.asc()).all()
        
        if not todos:
            msg = "nessun todo trovato"
            if overdue:
                msg = "nessun todo in scadenza"
            elif cliente:
                msg = f"nessun todo per {cliente}"
            console.print(f"ℹ️ {msg.capitalize()}", style="yellow")
            return
        
        # Costruisci tabella
        title = "📋 Todo List"
        if cliente:
            title += f" - {cliente}"
        if overdue:
            title += " (Overdue)"
        elif completati:
            title += " (Completati)"
            
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("ID", width=4, justify="center")
        table.add_column("Stato", width=6, justify="center")
        table.add_column("Priorità", width=12)
        table.add_column("Titolo", min_width=25)
        table.add_column("Cliente", width=15)
        table.add_column("Scadenza", width=12)
        
        for todo in todos:
            # Status icon
            if todo.completato:
                status = "✅"
            elif todo.is_overdue:
                status = "🔴"
            elif todo.scadenza and todo.scadenza == date.today():
                status = "🟡"
            else:
                status = "⏳"
            
            # Priorità con colore
            priorita_text = todo.priorita_text
            if todo.priorita == 1:
                priorita_style = "red"
            elif todo.priorita == -1:
                priorita_style = "green"
            else:
                priorita_style = "yellow"
            
            # Titolo con stile
            titolo = todo.titolo
            if todo.completato:
                titolo = f"[dim strikethrough]{titolo}[/dim strikethrough]"
            elif todo.is_overdue:
                titolo = f"[red]{titolo}[/red]"
            
            # Cliente
            cliente_nome = todo.cliente.nome if todo.cliente else "-"
            
            # Scadenza
            scadenza_text = "-"
            if todo.scadenza:
                scadenza_text = todo.scadenza.strftime("%d/%m")
                if todo.is_overdue and not todo.completato:
                    scadenza_text = f"[red]{scadenza_text}[/red]"
                elif todo.scadenza == date.today():
                    scadenza_text = f"[yellow]{scadenza_text}[/yellow]"
            
            table.add_row(
                str(todo.id),
                status,
                f"[{priorita_style}]{priorita_text}[/{priorita_style}]",
                titolo,
                cliente_nome,
                scadenza_text
            )
        
        console.print(table)
        
        # Statistiche
        completed = len([t for t in todos if t.completato])
        overdue_count = len([t for t in todos if t.is_overdue and not t.completato])
        
        stats_text = f"📊 Totale: {len(todos)}"
        if completed > 0:
            stats_text += f" | ✅ Completati: {completed}"
        if overdue_count > 0:
            stats_text += f" | 🔴 In ritardo: {overdue_count}"
            
        console.print(f"\n{stats_text}", style="dim")
        
    finally:
        db.close()

def show_today_todos():
    """Mostra todos con scadenza oggi"""
    db = SessionLocal()
    
    try:
        today = date.today()
        todos = db.query(Todo).filter(
            and_(
                Todo.scadenza == today,
                Todo.completato == False
            )
        ).order_by(Todo.priorita.desc()).all()
        
        if not todos:
            console.print("✨ Nessun todo in scadenza oggi", style="green")
            return
            
        console.print("📅 [bold]Todo di oggi[/bold]", style="blue")
        
        for todo in todos:
            priorita_emoji = "🔴" if todo.priorita == 1 else ("🟢" if todo.priorita == -1 else "🟡")
            cliente_info = f" [{todo.cliente.nome}]" if todo.cliente else ""
            
            console.print(f"  {priorita_emoji} {todo.titolo}{cliente_info}")
            if todo.descrizione:
                console.print(f"    [dim]{todo.descrizione}[/dim]")
        
    finally:
        db.close()

def show_week_todos():
    """Mostra todos della settimana"""
    db = SessionLocal()
    
    try:
        today = date.today()
        week_end = today + timedelta(days=7)
        
        todos = db.query(Todo).filter(
            and_(
                Todo.scadenza >= today,
                Todo.scadenza <= week_end,
                Todo.completato == False
            )
        ).order_by(Todo.scadenza.asc(), Todo.priorita.desc()).all()
        
        if not todos:
            console.print("✨ Nessun todo nella prossima settimana", style="green")
            return
            
        console.print("📅 [bold]Todo della settimana[/bold]", style="blue")
        
        current_date = None
        for todo in todos:
            # Raggruppa per data
            if todo.scadenza != current_date:
                current_date = todo.scadenza
                date_str = current_date.strftime("%A %d/%m")
                if current_date == today:
                    date_str += " (oggi)"
                elif current_date == today + timedelta(days=1):
                    date_str += " (domani)"
                    
                console.print(f"\n📆 [bold]{date_str}[/bold]")
            
            priorita_emoji = "🔴" if todo.priorita == 1 else ("🟢" if todo.priorita == -1 else "🟡")
            cliente_info = f" [{todo.cliente.nome}]" if todo.cliente else ""
            
            console.print(f"  {priorita_emoji} {todo.titolo}{cliente_info}")
            if todo.descrizione:
                console.print(f"    [dim]{todo.descrizione}[/dim]")
        
    finally:
        db.close()

def show_client_todos(cliente_nome: str):
    """Mostra todos per cliente specifico"""
    db = SessionLocal()
    
    try:
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return
            
        todos = db.query(Todo).filter(Todo.cliente_id == cliente.id).order_by(
            Todo.completato.asc(), 
            Todo.priorita.desc(), 
            Todo.scadenza.asc()
        ).all()
        
        if not todos:
            console.print(f"ℹ️ Nessun todo per {cliente.nome}", style="yellow")
            return
        
        console.print(f"📋 [bold]Todo per {cliente.nome}[/bold]", style="blue")
        
        pending = [t for t in todos if not t.completato]
        completed = [t for t in todos if t.completato]
        
        if pending:
            console.print("\n⏳ [bold]Da completare:[/bold]")
            for todo in pending:
                status_emoji = "🔴" if todo.is_overdue else "⏳"
                priorita_emoji = "🔴" if todo.priorita == 1 else ("🟢" if todo.priorita == -1 else "🟡")
                
                scadenza_info = ""
                if todo.scadenza:
                    scadenza_info = f" (scadenza: {todo.scadenza.strftime('%d/%m')})"
                    if todo.is_overdue:
                        scadenza_info = f"[red]{scadenza_info}[/red]"
                
                console.print(f"  {status_emoji} {priorita_emoji} {todo.titolo}{scadenza_info}")
                if todo.descrizione:
                    console.print(f"    [dim]{todo.descrizione}[/dim]")
        
        if completed:
            console.print(f"\n✅ [bold]Completati ({len(completed)}):[/bold]")
            for todo in completed[-5:]:  # Ultimi 5 completati
                data_completamento = ""
                if todo.data_completamento:
                    data_completamento = f" ({todo.data_completamento.strftime('%d/%m')})"
                console.print(f"  ✅ [dim strikethrough]{todo.titolo}[/dim strikethrough][dim]{data_completamento}[/dim]")
                
    finally:
        db.close()

def mark_todo_done(todo_id: int):
    """Marca todo come completato"""
    db = SessionLocal()
    
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            console.print(f"❌ Todo con ID {todo_id} non trovato", style="red")
            return
            
        if todo.completato:
            console.print(f"ℹ️ Todo '{todo.titolo}' già completato", style="yellow")
            return
        
        todo.completato = True
        todo.data_completamento = datetime.now()
        db.commit()
        
        cliente_info = f" per {todo.cliente.nome}" if todo.cliente else ""
        console.print(f"✅ Todo '{todo.titolo}' marcato come completato{cliente_info}", style="green")
        
    finally:
        db.close()

def edit_todo(
    todo_id: int,
    priorita: Optional[str] = None,
    scadenza: Optional[str] = None,
    titolo: Optional[str] = None
):
    """Modifica proprietà todo"""
    db = SessionLocal()
    
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            console.print(f"❌ Todo con ID {todo_id} non trovato", style="red")
            return
        
        changes = []
        
        # Modifica priorità
        if priorita:
            prio_map = {"alta": 1, "normale": 0, "bassa": -1}
            prio_val = prio_map.get(priorita.lower())
            if prio_val is not None:
                old_prio = todo.priorita_text
                todo.priorita = prio_val
                changes.append(f"priorità: {old_prio} → {todo.priorita_text}")
            else:
                console.print("❌ Priorità non valida (usa: alta, normale, bassa)", style="red")
                return
        
        # Modifica scadenza
        if scadenza:
            if scadenza.lower() == "rimuovi":
                old_scadenza = todo.scadenza.strftime('%d/%m/%Y') if todo.scadenza else "nessuna"
                todo.scadenza = None
                changes.append(f"scadenza: {old_scadenza} → rimossa")
            else:
                try:
                    new_scadenza = datetime.strptime(scadenza, "%Y-%m-%d").date()
                    old_scadenza = todo.scadenza.strftime('%d/%m/%Y') if todo.scadenza else "nessuna"
                    todo.scadenza = new_scadenza
                    changes.append(f"scadenza: {old_scadenza} → {new_scadenza.strftime('%d/%m/%Y')}")
                except ValueError:
                    console.print("❌ Formato data non valido (usa YYYY-MM-DD o 'rimuovi')", style="red")
                    return
        
        # Modifica titolo
        if titolo:
            old_titolo = todo.titolo
            todo.titolo = titolo.strip()
            changes.append(f"titolo: '{old_titolo}' → '{todo.titolo}'")
        
        if changes:
            db.commit()
            cliente_info = f" per {todo.cliente.nome}" if todo.cliente else ""
            console.print(f"✅ Todo aggiornato{cliente_info}:", style="green")
            for change in changes:
                console.print(f"  • {change}")
        else:
            console.print("ℹ️ Nessuna modifica specificata", style="yellow")
        
    finally:
        db.close()

def delete_todo(todo_id: int):
    """Elimina todo"""
    db = SessionLocal()
    
    try:
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not todo:
            console.print(f"❌ Todo con ID {todo_id} non trovato", style="red")
            return
        
        # Conferma eliminazione
        cliente_info = f" per {todo.cliente.nome}" if todo.cliente else ""
        confirm = questionary.confirm(
            f"Eliminare il todo '{todo.titolo}'{cliente_info}?",
            default=False
        ).ask()
        
        if not confirm:
            console.print("❌ Eliminazione annullata", style="yellow")
            return
        
        titolo = todo.titolo
        db.delete(todo)
        db.commit()
        
        console.print(f"🗑️ Todo '{titolo}' eliminato", style="green")
        
    except KeyboardInterrupt:
        console.print("❌ Eliminazione annullata", style="yellow")
    finally:
        db.close()