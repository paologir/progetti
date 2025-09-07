"""
CLI commands for client management
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from typing import Optional, List
import questionary
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from core.database import SessionLocal, get_db
from core.models import Cliente, Contatto

console = Console()

def list_clients(
    active_only: bool = typer.Option(False, "--attivi", help="Solo clienti attivi"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filtra per tag"),
    search: Optional[str] = typer.Option(None, "--cerca", help="Cerca nel nome")
):
    """Lista tutti i clienti"""
    db = SessionLocal()
    try:
        query = db.query(Cliente)
        
        # Filters
        if active_only:
            query = query.filter(Cliente.stato == 'attivo')
        
        if search:
            query = query.filter(Cliente.nome.ilike(f'%{search}%'))
        
        clienti = query.order_by(Cliente.nome).all()
        
        if tag:
            # Filter by tag (JSON search)
            clienti = [c for c in clienti if tag.lower() in [t.lower() for t in c.tags_list]]
        
        if not clienti:
            console.print("❌ Nessun cliente trovato", style="yellow")
            return
        
        # Create table - optimized for narrow terminals
        table = Table(title=f"👥 Clienti ({len(clienti)})")
        table.add_column("ID", width=3)
        table.add_column("Nome", style="cyan", no_wrap=False)
        table.add_column("Stato", width=8) 
        table.add_column("Città", width=15)
        table.add_column("€/h", width=5)
        
        for cliente in clienti:
            # Status with color
            status_colors = {
                'attivo': 'green',
                'prospect': 'yellow', 
                'pausa': 'orange',
                'archiviato': 'dim'
            }
            status_style = status_colors.get(cliente.stato, 'white')
            
            # Tags display
            tags_display = ", ".join(cliente.tags_list[:3]) if cliente.tags_list else "-"
            if len(cliente.tags_list) > 3:
                tags_display += "..."
                
            table.add_row(
                str(cliente.id),
                cliente.nome,
                f"[{status_style}]{cliente.stato}[/{status_style}]",
                cliente.citta or "-",
                f"€{cliente.tariffa_oraria:.0f}"
            )
        
        console.print(table)
        
        # Show summary
        stati = {}
        for cliente in clienti:
            stati[cliente.stato] = stati.get(cliente.stato, 0) + 1
        
        summary = " • ".join([f"{stato}: {count}" for stato, count in stati.items()])
        console.print(f"\n📊 [dim]{summary}[/dim]")
        
    except Exception as e:
        console.print(f"❌ Errore: {e}", style="red")
    finally:
        db.close()

def show_client(name: str):
    """Mostra dettagli di un cliente"""
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.nome.ilike(f'%{name}%')).first()
        
        if not cliente:
            console.print(f"❌ Cliente '{name}' non trovato", style="red")
            return
        
        # Client info panel
        info_text = f"""[bold]{cliente.nome}[/bold]
        
📍 {cliente.indirizzo_completo or 'Indirizzo non specificato'}
🏢 P.IVA: {cliente.piva or 'N/A'} | CF: {cliente.cf or 'N/A'}
💰 Tariffa: €{cliente.tariffa_oraria:.0f}/h | Budget mensile: €{cliente.budget_mensile or 0:.0f}
📊 Stato: {cliente.stato}
🏷️ Tags: {', '.join(cliente.tags_list) if cliente.tags_list else 'Nessun tag'}

📝 {cliente.note or 'Nessuna nota'}"""

        panel = Panel(info_text, title=f"👤 {cliente.nome}", border_style="blue")
        console.print(panel)
        
        # Contacts
        if cliente.contatti:
            table = Table(title="📞 Contatti")
            table.add_column("Nome")
            table.add_column("Ruolo")
            table.add_column("Email") 
            table.add_column("Telefono")
            table.add_column("Status")
            
            for contatto in cliente.contatti:
                status = "⭐ Principale" if contatto.principale else ("✅ Attivo" if contatto.attivo else "❌ Inattivo")
                table.add_row(
                    contatto.nome,
                    contatto.ruolo or "-",
                    contatto.email or "-",
                    contatto.telefono or "-",
                    status
                )
            console.print(table)
        
        # Recent activity summary
        console.print(f"\n📅 Creato: {cliente.data_creazione.strftime('%d/%m/%Y %H:%M') if cliente.data_creazione else 'N/A'}")
        if cliente.data_ultima_attivita:
            console.print(f"🔄 Ultima attività: {cliente.data_ultima_attivita.strftime('%d/%m/%Y %H:%M')}")
        
    except Exception as e:
        console.print(f"❌ Errore: {e}", style="red")
    finally:
        db.close()

def add_client():
    """Wizard per aggiungere un nuovo cliente"""
    console.print("🆕 [bold blue]Nuovo Cliente - Inserimento guidato[/bold blue]")
    
    # Required fields
    nome = questionary.text("Nome cliente:", validate=lambda x: len(x.strip()) > 0).ask()
    if not nome:
        console.print("❌ Operazione annullata", style="yellow")
        return
    
    # Optional fields with validation
    piva = questionary.text("P.IVA (opzionale):", default="").ask()
    cf = questionary.text("Codice Fiscale (opzionale):", default="").ask()
    
    # Address
    indirizzo = questionary.text("Indirizzo (opzionale):", default="").ask()
    citta = questionary.text("Città (opzionale):", default="").ask()
    cap = questionary.text("CAP (opzionale):", default="").ask()
    provincia = questionary.text("Provincia (opzionale):", default="").ask()
    
    # Status
    stato = questionary.select(
        "Stato cliente:",
        choices=['attivo', 'prospect', 'pausa', 'archiviato'],
        default='attivo'
    ).ask()
    
    # Tags
    tags_input = questionary.text(
        "Tags (separati da virgola, es: seo,ads,ecommerce):", 
        default=""
    ).ask()
    tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
    
    # Financial
    try:
        tariffa_default = questionary.text("Tariffa oraria (€):", default="50").ask()
        tariffa_oraria = float(tariffa_default) if tariffa_default else 50.0
    except:
        tariffa_oraria = 50.0
    
    try:
        budget_input = questionary.text("Budget mensile (€, opzionale):", default="").ask()
        budget_mensile = float(budget_input) if budget_input else None
    except:
        budget_mensile = None
    
    # Notes
    note = questionary.text("Note (opzionale):", default="").ask()
    
    # Confirmation
    console.print("\n📋 [bold]Riepilogo nuovo cliente:[/bold]")
    console.print(f"👤 Nome: {nome}")
    console.print(f"🏢 P.IVA: {piva or 'N/A'}")
    console.print(f"📍 {indirizzo or 'N/A'}, {cap} {citta} ({provincia})" if any([indirizzo, cap, citta, provincia]) else "📍 Indirizzo: N/A")
    console.print(f"📊 Stato: {stato}")
    console.print(f"🏷️ Tags: {', '.join(tags_list) if tags_list else 'Nessuno'}")
    console.print(f"💰 €{tariffa_oraria:.0f}/h | Budget: €{budget_mensile or 0:.0f}/mese")
    if note:
        console.print(f"📝 Note: {note}")
    
    if not questionary.confirm("Confermi la creazione del cliente?").ask():
        console.print("❌ Operazione annullata", style="yellow")
        return
    
    # Save to database
    db = SessionLocal()
    try:
        cliente = Cliente(
            nome=nome,
            piva=piva or None,
            cf=cf or None,
            indirizzo=indirizzo or None,
            citta=citta or None,
            cap=cap or None,
            provincia=provincia or None,
            stato=stato,
            tariffa_oraria=tariffa_oraria,
            budget_mensile=budget_mensile,
            note=note or None
        )
        
        # Set tags
        if tags_list:
            cliente.tags_list = tags_list
        
        db.add(cliente)
        db.commit()
        
        console.print(f"✅ Cliente '{nome}' creato con successo (ID: {cliente.id})", style="green")
        
        # Ask for contacts
        if questionary.confirm("Vuoi aggiungere un contatto?").ask():
            add_contact_to_client(cliente.id)
        
    except Exception as e:
        console.print(f"❌ Errore durante il salvataggio: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def add_contact_to_client(cliente_id: int):
    """Add a contact to existing client"""
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter_by(id=cliente_id).first()
        if not cliente:
            console.print("❌ Cliente non trovato", style="red")
            return
        
        console.print(f"\n👤 [bold]Nuovo contatto per {cliente.nome}[/bold]")
        
        nome = questionary.text("Nome contatto:", validate=lambda x: len(x.strip()) > 0).ask()
        if not nome:
            console.print("❌ Operazione annullata", style="yellow")
            return
        
        ruolo = questionary.text("Ruolo (es: Marketing Manager):", default="").ask()
        email = questionary.text("Email:", default="").ask()
        telefono = questionary.text("Telefono:", default="").ask()
        
        # Check if should be main contact
        principale = False
        if not cliente.contatti:  # First contact
            principale = True
            console.print("ℹ️ Questo sarà il contatto principale (primo contatto)")
        else:
            principale = questionary.confirm("È il contatto principale?").ask()
            
            # If setting as main, remove main flag from others
            if principale:
                for contatto in cliente.contatti:
                    contatto.principale = False
        
        contatto = Contatto(
            cliente_id=cliente_id,
            nome=nome,
            ruolo=ruolo or None,
            email=email or None,
            telefono=telefono or None,
            principale=principale
        )
        
        db.add(contatto)
        db.commit()
        
        console.print(f"✅ Contatto '{nome}' aggiunto a {cliente.nome}", style="green")
        
    except Exception as e:
        console.print(f"❌ Errore: {e}", style="red")
        db.rollback()
    finally:
        db.close()

# Export functions for use in main CLI
__all__ = ['list_clients', 'show_client', 'add_client', 'add_contact_to_client']