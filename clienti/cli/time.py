"""
Time tracking CLI commands for clienti CRM
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
import json
import os
import csv
from pathlib import Path

from core.database import SessionLocal
from core.models import Cliente, TimeTracking, Configurazione
from core.logger import get_logger

logger = get_logger()

console = Console()

def get_cliente_by_name(nome: str, db: Session) -> Optional[Cliente]:
    """Find cliente by name (case insensitive search)"""
    return db.query(Cliente).filter(Cliente.nome.ilike(f"%{nome}%")).first()

def get_active_timer(db: Session) -> Optional[TimeTracking]:
    """Get active timer session"""
    return db.query(TimeTracking).filter(TimeTracking.fine.is_(None)).first()

def save_timer_state(session: TimeTracking):
    """Save timer state to file for persistence"""
    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "timer_state.json")
    state = {
        "session_id": session.id,
        "cliente_id": session.cliente_id,
        "cliente_nome": session.cliente.nome,
        "inizio": session.inizio.isoformat(),
        "descrizione": session.descrizione,
        "tariffa_oraria": session.tariffa_oraria
    }
    
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        console.print(f"⚠️ Warning: Could not save timer state: {e}", style="yellow")

def load_timer_state():
    """Load timer state from file"""
    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "timer_state.json")
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def clear_timer_state():
    """Clear timer state file"""
    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "timer_state.json")
    try:
        if os.path.exists(state_file):
            os.remove(state_file)
    except Exception:
        pass

def start_timer(
    cliente_nome: str,
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Descrizione dell'attività"),
    tariffa: Optional[float] = typer.Option(None, "--tariffa", "-r", help="Tariffa oraria personalizzata")
):
    """Avvia timer per un cliente"""
    db = SessionLocal()
    
    try:
        # Check if there's already an active timer
        active = get_active_timer(db)
        if active:
            console.print(f"⚠️ Timer già attivo per [bold]{active.cliente.nome}[/bold]", style="yellow")
            console.print(f"📝 Attività: {active.descrizione or 'N/A'}")
            
            elapsed = datetime.now() - active.inizio
            hours = elapsed.total_seconds() / 3600
            console.print(f"⏱️ Tempo trascorso: {hours:.1f}h")
            
            stop_current = typer.confirm("Vuoi fermare il timer attuale e iniziarne uno nuovo?")
            if stop_current:
                _stop_timer(active, db)
            else:
                return

        # Find cliente
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            # Show suggestions
            similar = db.query(Cliente).filter(Cliente.nome.ilike(f"%{cliente_nome.split()[0]}%")).limit(5).all()
            if similar:
                console.print("🔍 Clienti simili:")
                for c in similar:
                    console.print(f"  • {c.nome}")
            return

        # Determine hourly rate
        if not tariffa:
            tariffa = cliente.tariffa_oraria or 50.0

        # Create new tracking session
        session = TimeTracking(
            cliente_id=cliente.id,
            inizio=datetime.now(),
            descrizione=task,
            tariffa_oraria=tariffa
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Save state for persistence
        save_timer_state(session)
        
        # Update cliente last activity
        cliente.data_ultima_attivita = datetime.now()
        db.commit()
        
        logger.log_timer_start(cliente.nome, task or "")
        
        console.print(f"▶️ Timer avviato per [bold green]{cliente.nome}[/bold green]", style="green")
        if task:
            console.print(f"📝 Attività: {task}")
        console.print(f"💰 Tariffa: €{tariffa}/h")
        console.print(f"🕒 Inizio: {session.inizio.strftime('%H:%M:%S')}")

    except Exception as e:
        console.print(f"❌ Errore avvio timer: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def _stop_timer(session: TimeTracking, db: Session):
    """Internal function to stop a timer session"""
    session.fine = datetime.now()
    db.commit()
    
    # Calculate duration and compensation
    duration_hours = session.durata_ore
    compensation = session.compenso
    
    clear_timer_state()
    
    logger.log_timer_stop(session.cliente.nome, f"{duration_hours:.2f}h", compensation)
    
    console.print(f"⏹️ Timer fermato per [bold]{session.cliente.nome}[/bold]")
    console.print(f"⏱️ Durata: {duration_hours:.2f}h")
    console.print(f"💰 Compenso: €{compensation:.2f}")
    
    return session

def stop_timer():
    """Ferma il timer attivo"""
    db = SessionLocal()
    
    try:
        active = get_active_timer(db)
        if not active:
            console.print("❌ Nessun timer attivo", style="yellow")
            return
        
        stopped_session = _stop_timer(active, db)
        
        # Ask if user wants to add notes
        try:
            add_notes = typer.confirm("Vuoi aggiungere delle note alla sessione?", default=False)
            if add_notes:
                note = typer.prompt("Note", default="")
                if note.strip():
                    stopped_session.note = note
                    db.commit()
                    console.print("📝 Note aggiunte", style="green")
        except Exception:
            # Skip notes if in non-interactive environment
            pass

    except Exception as e:
        console.print(f"❌ Errore stop timer: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def timer_status():
    """Mostra stato del timer corrente"""
    db = SessionLocal()
    
    try:
        active = get_active_timer(db)
        if not active:
            console.print("⏸️ Nessun timer attivo", style="dim")
            
            # Check if there's a saved state (crashed session recovery)
            saved_state = load_timer_state()
            if saved_state:
                console.print("🔧 Trovata sessione salvata - possibile recovery needed", style="yellow")
                console.print(f"Cliente: {saved_state.get('cliente_nome')}")
                console.print(f"Inizio: {saved_state.get('inizio')}")
                
                recover = typer.confirm("Vuoi ripristinare questa sessione?")
                if recover:
                    # Try to find the session in DB
                    session = db.query(TimeTracking).filter_by(id=saved_state['session_id']).first()
                    if session and session.fine is None:
                        elapsed = datetime.now() - session.inizio
                        hours = elapsed.total_seconds() / 3600
                        console.print(f"✅ Sessione ripristinata: {hours:.1f}h elapsed", style="green")
                    else:
                        clear_timer_state()
                        console.print("❌ Sessione non più valida", style="red")
                else:
                    clear_timer_state()
            return

        # Calculate elapsed time
        elapsed = datetime.now() - active.inizio
        hours = elapsed.total_seconds() / 3600
        estimated_compensation = hours * (active.tariffa_oraria or 50.0)
        
        panel = Panel(
            f"👤 [bold]Cliente:[/bold] {active.cliente.nome}\n"
            f"📝 [bold]Attività:[/bold] {active.descrizione or 'N/A'}\n"
            f"🕒 [bold]Inizio:[/bold] {active.inizio.strftime('%H:%M:%S')}\n"
            f"⏱️ [bold]Tempo trascorso:[/bold] {hours:.1f}h\n"
            f"💰 [bold]Compenso stimato:[/bold] €{estimated_compensation:.2f}\n"
            f"💵 [bold]Tariffa:[/bold] €{active.tariffa_oraria}/h",
            title="⏳ Timer Attivo",
            border_style="green"
        )
        
        console.print(panel)

    except Exception as e:
        console.print(f"❌ Errore status timer: {e}", style="red")
    finally:
        db.close()

def show_today_hours():
    """Mostra ore lavorate oggi"""
    db = SessionLocal()
    
    try:
        today = date.today()
        sessions = db.query(TimeTracking).filter(
            and_(
                extract('year', TimeTracking.inizio) == today.year,
                extract('month', TimeTracking.inizio) == today.month,
                extract('day', TimeTracking.inizio) == today.day,
                TimeTracking.fine.isnot(None)  # Only completed sessions
            )
        ).order_by(TimeTracking.inizio.desc()).all()
        
        if not sessions:
            console.print(f"📅 Nessuna sessione completata oggi ({today.strftime('%d/%m/%Y')})", style="dim")
            return
        
        table = Table(title=f"⏱️ Ore lavorate oggi - {today.strftime('%d/%m/%Y')}")
        table.add_column("Cliente", style="cyan")
        table.add_column("Attività", style="white")
        table.add_column("Inizio", style="dim")
        table.add_column("Fine", style="dim")
        table.add_column("Durata", style="green")
        table.add_column("Compenso", style="yellow")
        
        total_hours = 0
        total_compensation = 0
        
        for session in sessions:
            duration = session.durata_ore
            compensation = session.compenso
            
            table.add_row(
                session.cliente.nome,
                session.descrizione or "-",
                session.inizio.strftime('%H:%M'),
                session.fine.strftime('%H:%M') if session.fine else "-",
                f"{duration:.1f}h",
                f"€{compensation:.2f}"
            )
            
            total_hours += duration
            total_compensation += compensation
        
        console.print(table)
        console.print(f"\n📊 [bold]Totale oggi:[/bold] {total_hours:.1f}h - €{total_compensation:.2f}")

    except Exception as e:
        console.print(f"❌ Errore visualizzazione ore: {e}", style="red")
    finally:
        db.close()

def show_week_report():
    """Report ore settimanali"""
    db = SessionLocal()
    
    try:
        # Calculate week range (Monday to Sunday)
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        
        sessions = db.query(TimeTracking).filter(
            and_(
                TimeTracking.inizio >= monday,
                TimeTracking.inizio <= sunday + timedelta(days=1),  # Include full Sunday
                TimeTracking.fine.isnot(None)
            )
        ).order_by(TimeTracking.inizio.desc()).all()
        
        if not sessions:
            console.print(f"📅 Nessuna sessione questa settimana ({monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')})", style="dim")
            return
        
        # Group by client
        client_stats = {}
        total_hours = 0
        total_compensation = 0
        
        for session in sessions:
            client = session.cliente.nome
            duration = session.durata_ore
            compensation = session.compenso
            
            if client not in client_stats:
                client_stats[client] = {'hours': 0, 'compensation': 0, 'sessions': 0}
            
            client_stats[client]['hours'] += duration
            client_stats[client]['compensation'] += compensation
            client_stats[client]['sessions'] += 1
            
            total_hours += duration
            total_compensation += compensation
        
        table = Table(title=f"📊 Report settimanale {monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}")
        table.add_column("Cliente", style="cyan")
        table.add_column("Sessioni", style="dim", justify="right")
        table.add_column("Ore totali", style="green", justify="right")
        table.add_column("Compenso", style="yellow", justify="right")
        table.add_column("€/h medio", style="magenta", justify="right")
        
        for client, stats in sorted(client_stats.items(), key=lambda x: x[1]['hours'], reverse=True):
            avg_rate = stats['compensation'] / stats['hours'] if stats['hours'] > 0 else 0
            table.add_row(
                client,
                str(stats['sessions']),
                f"{stats['hours']:.1f}h",
                f"€{stats['compensation']:.2f}",
                f"€{avg_rate:.0f}/h"
            )
        
        console.print(table)
        console.print(f"\n📈 [bold]Totale settimana:[/bold] {total_hours:.1f}h - €{total_compensation:.2f}")
        
        # Calculate daily average
        days_worked = len(set(s.inizio.date() for s in sessions))
        if days_worked > 0:
            avg_daily_hours = total_hours / days_worked
            console.print(f"📊 [bold]Media giornaliera:[/bold] {avg_daily_hours:.1f}h/giorno ({days_worked} giorni lavorati)")

    except Exception as e:
        console.print(f"❌ Errore report settimanale: {e}", style="red")
    finally:
        db.close()

def show_client_report(cliente_nome: str):
    """Report ore per cliente specifico"""
    db = SessionLocal()
    
    try:
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return
        
        sessions = db.query(TimeTracking).filter(
            and_(
                TimeTracking.cliente_id == cliente.id,
                TimeTracking.fine.isnot(None)
            )
        ).order_by(TimeTracking.inizio.desc()).limit(20).all()
        
        if not sessions:
            console.print(f"📅 Nessuna sessione per {cliente.nome}", style="dim")
            return
        
        table = Table(title=f"⏱️ Ultime 20 sessioni - {cliente.nome}")
        table.add_column("Data", style="cyan")
        table.add_column("Attività", style="white")
        table.add_column("Durata", style="green")
        table.add_column("Tariffa", style="dim")
        table.add_column("Compenso", style="yellow")
        table.add_column("Fatturato", style="red")
        
        total_hours = 0
        total_compensation = 0
        unbilled_hours = 0
        unbilled_compensation = 0
        
        for session in sessions:
            duration = session.durata_ore
            compensation = session.compenso
            billed_icon = "✅" if session.fatturato else "⏳"
            
            table.add_row(
                session.inizio.strftime('%d/%m/%Y'),
                session.descrizione or "-",
                f"{duration:.1f}h",
                f"€{session.tariffa_oraria}/h",
                f"€{compensation:.2f}",
                billed_icon
            )
            
            total_hours += duration
            total_compensation += compensation
            
            if not session.fatturato:
                unbilled_hours += duration
                unbilled_compensation += compensation
        
        console.print(table)
        console.print(f"\n📊 [bold]Totale (ultime 20):[/bold] {total_hours:.1f}h - €{total_compensation:.2f}")
        
        if unbilled_hours > 0:
            console.print(f"💰 [bold red]Da fatturare:[/bold red] {unbilled_hours:.1f}h - €{unbilled_compensation:.2f}")

    except Exception as e:
        console.print(f"❌ Errore report cliente: {e}", style="red")
    finally:
        db.close()

def show_unbilled():
    """Mostra ore non ancora fatturate"""
    db = SessionLocal()
    
    try:
        unbilled = db.query(TimeTracking).filter(
            and_(
                TimeTracking.fine.isnot(None),
                TimeTracking.fatturato == False
            )
        ).order_by(TimeTracking.inizio.desc()).all()
        
        if not unbilled:
            console.print("✅ Tutte le ore sono state fatturate!", style="green")
            return
        
        # Group by client
        client_totals = {}
        for session in unbilled:
            client = session.cliente.nome
            if client not in client_totals:
                client_totals[client] = {'hours': 0, 'compensation': 0, 'sessions': []}
            
            client_totals[client]['hours'] += session.durata_ore
            client_totals[client]['compensation'] += session.compenso
            client_totals[client]['sessions'].append(session)
        
        table = Table(title="💰 Ore da fatturare")
        table.add_column("Cliente", style="cyan")
        table.add_column("Sessioni", style="dim", justify="right")
        table.add_column("Ore totali", style="green", justify="right")
        table.add_column("Compenso", style="yellow", justify="right")
        table.add_column("Più vecchia", style="red")
        
        total_hours = 0
        total_compensation = 0
        
        for client, data in sorted(client_totals.items(), key=lambda x: x[1]['compensation'], reverse=True):
            oldest_session = min(data['sessions'], key=lambda x: x.inizio)
            
            table.add_row(
                client,
                str(len(data['sessions'])),
                f"{data['hours']:.1f}h",
                f"€{data['compensation']:.2f}",
                oldest_session.inizio.strftime('%d/%m/%Y')
            )
            
            total_hours += data['hours']
            total_compensation += data['compensation']
        
        console.print(table)
        console.print(f"\n📊 [bold red]TOTALE DA FATTURARE:[/bold red] {total_hours:.1f}h - €{total_compensation:.2f}")

    except Exception as e:
        console.print(f"❌ Errore ore non fatturate: {e}", style="red")
    finally:
        db.close()

def edit_session(session_id: int):
    """Modifica una sessione di time tracking"""
    db = SessionLocal()
    
    try:
        session = db.query(TimeTracking).filter(TimeTracking.id == session_id).first()
        if not session:
            console.print(f"❌ Sessione con ID {session_id} non trovata", style="red")
            return
        
        if session.fine is None:
            console.print("⚠️ Non puoi modificare una sessione attiva. Fermala prima.", style="yellow")
            return
        
        console.print(f"✏️ [bold]Modifica Sessione ID {session_id}[/bold]", style="blue")
        console.print(f"Cliente: {session.cliente.nome}")
        console.print(f"Data: {session.inizio.strftime('%d/%m/%Y')}")
        console.print(f"Orario: {session.inizio.strftime('%H:%M')} - {session.fine.strftime('%H:%M') if session.fine else 'N/A'}")
        console.print(f"Durata: {session.durata_ore:.2f}h")
        console.print(f"Attività: {session.descrizione or 'N/A'}")
        console.print(f"Tariffa: €{session.tariffa_oraria}/h")
        console.print(f"Note: {session.note or 'Nessuna nota'}")
        
        import questionary
        
        # Modifica descrizione
        new_descrizione = questionary.text(
            "Nuova descrizione (lascia vuoto per non modificare):",
            default=session.descrizione or ""
        ).ask()
        
        # Modifica tariffa oraria
        new_tariffa = questionary.text(
            f"Nuova tariffa oraria (attuale: €{session.tariffa_oraria}/h):",
            default=str(session.tariffa_oraria)
        ).ask()
        
        try:
            new_tariffa = float(new_tariffa)
        except (ValueError, TypeError):
            console.print("❌ Tariffa non valida, mantengo quella attuale", style="yellow")
            new_tariffa = session.tariffa_oraria
        
        # Modifica note
        new_note = questionary.text(
            "Nuove note (lascia vuoto per non modificare):",
            default=session.note or ""
        ).ask()
        
        # Modifica stato fatturato
        fatturato_attuale = "Sì" if session.fatturato else "No"
        new_fatturato = questionary.select(
            f"Fatturato (attuale: {fatturato_attuale}):",
            choices=["Sì", "No"],
            default=fatturato_attuale
        ).ask()
        
        # Applica modifiche
        session.descrizione = new_descrizione if new_descrizione else None
        session.tariffa_oraria = new_tariffa
        session.note = new_note if new_note else None
        session.fatturato = (new_fatturato == "Sì")
        
        db.commit()
        
        console.print(f"✅ Sessione ID {session_id} aggiornata con successo", style="green")
        console.print(f"Nuovo compenso: €{session.compenso:.2f}")
        
    except KeyboardInterrupt:
        console.print("❌ Operazione annullata", style="red")
    except Exception as e:
        console.print(f"❌ Errore modifica sessione: {e}", style="red")
        db.rollback()
    finally:
        db.close()


def delete_session(session_id: int):
    """Elimina una sessione di time tracking"""
    db = SessionLocal()
    
    try:
        session = db.query(TimeTracking).filter(TimeTracking.id == session_id).first()
        if not session:
            console.print(f"❌ Sessione con ID {session_id} non trovata", style="red")
            return
        
        if session.fine is None:
            console.print("⚠️ Non puoi eliminare una sessione attiva. Fermala prima.", style="yellow")
            return
        
        # Mostra dettagli della sessione da eliminare
        console.print(f"🗑️ [bold red]Elimina Sessione ID {session_id}[/bold red]")
        console.print(f"Cliente: {session.cliente.nome}")
        console.print(f"Data: {session.inizio.strftime('%d/%m/%Y')}")
        console.print(f"Orario: {session.inizio.strftime('%H:%M')} - {session.fine.strftime('%H:%M')}")
        console.print(f"Durata: {session.durata_ore:.2f}h")
        console.print(f"Attività: {session.descrizione or 'N/A'}")
        console.print(f"Compenso: €{session.compenso:.2f}")
        
        import questionary
        
        # Doppia conferma
        if not questionary.confirm("⚠️ Sei sicuro di voler eliminare questa sessione?", default=False).ask():
            console.print("❌ Operazione annullata", style="yellow")
            return
        
        if not questionary.confirm("⚠️ ATTENZIONE: Questa azione è irreversibile! Confermi l'eliminazione?", default=False).ask():
            console.print("❌ Operazione annullata", style="yellow")
            return
        
        # Elimina la sessione
        db.delete(session)
        db.commit()
        
        console.print(f"✅ Sessione ID {session_id} eliminata con successo", style="green")
        
    except KeyboardInterrupt:
        console.print("❌ Operazione annullata", style="red")
    except Exception as e:
        console.print(f"❌ Errore eliminazione sessione: {e}", style="red")
        db.rollback()
    finally:
        db.close()


def list_sessions(
    cliente_nome: Optional[str] = None,
    limit: int = 10,
    show_active: bool = False
):
    """Lista sessioni di time tracking con ID per edit/delete"""
    db = SessionLocal()
    
    try:
        query = db.query(TimeTracking)
        
        # Filter by client if specified
        if cliente_nome:
            cliente = get_cliente_by_name(cliente_nome, db)
            if not cliente:
                console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
                return
            query = query.filter(TimeTracking.cliente_id == cliente.id)
        
        # Filter by active/completed sessions
        if show_active:
            query = query.filter(TimeTracking.fine.is_(None))
        else:
            query = query.filter(TimeTracking.fine.isnot(None))
        
        sessions = query.order_by(TimeTracking.inizio.desc()).limit(limit).all()
        
        if not sessions:
            status_text = "attive" if show_active else "completate"
            console.print(f"📅 Nessuna sessione {status_text} trovata", style="dim")
            return
        
        status_text = "Attive" if show_active else f"Ultime {len(sessions)} completate"
        table = Table(title=f"⏱️ Sessioni {status_text}")
        table.add_column("ID", width=4, justify="right", style="cyan")
        table.add_column("Data", style="dim")
        table.add_column("Cliente", style="white")
        table.add_column("Attività", style="green")
        table.add_column("Durata", style="yellow", justify="right")
        table.add_column("Compenso", style="magenta", justify="right")
        table.add_column("Fatturato", style="red", justify="center")
        
        for session in sessions:
            if show_active:
                # For active sessions, show elapsed time
                elapsed = datetime.now() - session.inizio
                duration_display = f"{elapsed.total_seconds()/3600:.1f}h*"
                compenso_display = f"€{(elapsed.total_seconds()/3600) * session.tariffa_oraria:.2f}*"
            else:
                duration_display = f"{session.durata_ore:.1f}h"
                compenso_display = f"€{session.compenso:.2f}"
            
            fatturato_icon = "✅" if session.fatturato else "⏳"
            
            table.add_row(
                str(session.id),
                session.inizio.strftime('%d/%m/%Y'),
                session.cliente.nome,
                session.descrizione or "-",
                duration_display,
                compenso_display,
                fatturato_icon
            )
        
        console.print(table)
        
        if show_active:
            console.print("* = valori stimati per sessioni attive")
        
        # Show usage commands
        if not show_active:
            console.print("\n💡 [dim]Comandi utili:[/dim]")
            console.print("[dim]  clienti time edit <ID>    - Modifica sessione[/dim]")  
            console.print("[dim]  clienti time delete <ID>  - Elimina sessione[/dim]")
        
    except Exception as e:
        console.print(f"❌ Errore lista sessioni: {e}", style="red")
    finally:
        db.close()


def export_timesheet_csv(
    output_path: Optional[str] = None,
    cliente_nome: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """Esporta timesheet in formato CSV"""
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(TimeTracking).filter(TimeTracking.fine.isnot(None))
        
        # Filter by client if specified
        if cliente_nome:
            cliente = get_cliente_by_name(cliente_nome, db)
            if not cliente:
                console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
                return
            query = query.filter(TimeTracking.cliente_id == cliente.id)
        
        # Filter by month/year if specified
        current_date = date.today()
        if month:
            query = query.filter(extract('month', TimeTracking.inizio) == month)
        if year:
            query = query.filter(extract('year', TimeTracking.inizio) == year)
        elif month:  # If month specified without year, use current year
            query = query.filter(extract('year', TimeTracking.inizio) == current_date.year)
        
        sessions = query.order_by(TimeTracking.inizio.desc()).all()
        
        if not sessions:
            console.print("📅 Nessuna sessione trovata per i criteri specificati", style="yellow")
            return
        
        # Determine output path
        if not output_path:
            # Create exports directory if it doesn't exist
            exports_dir = Path(__file__).parent.parent / "data" / "exports"
            exports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_parts = ["timesheet", timestamp]
            
            if cliente_nome:
                # Sanitize client name for filename
                safe_client_name = "".join(c for c in cliente_nome if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_client_name = safe_client_name.replace(' ', '_')
                filename_parts.append(safe_client_name)
            
            if month and year:
                filename_parts.append(f"{year}_{month:02d}")
            elif month:
                filename_parts.append(f"{current_date.year}_{month:02d}")
            
            filename = "_".join(filename_parts) + ".csv"
            output_path = exports_dir / filename
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Data',
                'Cliente',
                'Inizio',
                'Fine', 
                'Durata (ore)',
                'Attività',
                'Tariffa oraria',
                'Compenso',
                'Fatturato',
                'Note'
            ])
            
            # Data rows
            total_hours = 0
            total_compensation = 0
            
            for session in sessions:
                duration = session.durata_ore
                compensation = session.compenso
                
                writer.writerow([
                    session.inizio.strftime('%Y-%m-%d'),
                    session.cliente.nome,
                    session.inizio.strftime('%H:%M:%S'),
                    session.fine.strftime('%H:%M:%S') if session.fine else '',
                    f"{duration:.2f}",
                    session.descrizione or '',
                    session.tariffa_oraria or '',
                    f"{compensation:.2f}",
                    'Sì' if session.fatturato else 'No',
                    session.note or ''
                ])
                
                total_hours += duration
                total_compensation += compensation
            
            # Add summary row
            writer.writerow([])  # Empty row
            writer.writerow([
                'TOTALE',
                '',
                '',
                '',
                f"{total_hours:.2f}",
                '',
                '',
                f"{total_compensation:.2f}",
                '',
                ''
            ])
        
        console.print(f"📊 Timesheet esportato: [bold green]{output_path}[/bold green]")
        console.print(f"📈 {len(sessions)} sessioni - {total_hours:.1f}h - €{total_compensation:.2f}")
        
        # Show path for easy access
        abs_path = Path(output_path).resolve()
        console.print(f"🔗 Percorso completo: {abs_path}")

    except Exception as e:
        console.print(f"❌ Errore export CSV: {e}", style="red")
    finally:
        db.close()