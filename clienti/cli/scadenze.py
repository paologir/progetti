"""
Scadenze fatturazione CLI commands for clienti CRM
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import calendar

from core.database import SessionLocal
from core.models import Cliente, ScadenzeFatturazione, TimeTracking

console = Console()

def get_cliente_by_name(nome: str, db: Session) -> Optional[Cliente]:
    """Find cliente by name (case insensitive search)"""
    return db.query(Cliente).filter(Cliente.nome.ilike(f"%{nome}%")).first()

def calculate_next_date(base_date: date, ricorrenza: str, giorni_custom: Optional[int] = None) -> date:
    """Calculate next date based on recurrence pattern"""
    if ricorrenza == "mensile":
        return base_date + relativedelta(months=1)
    elif ricorrenza == "bimestrale":
        return base_date + relativedelta(months=2)
    elif ricorrenza == "trimestrale":
        return base_date + relativedelta(months=3)
    elif ricorrenza == "semestrale":
        return base_date + relativedelta(months=6)
    elif ricorrenza == "annuale":
        return base_date + relativedelta(years=1)
    elif ricorrenza == "custom" and giorni_custom:
        return base_date + timedelta(days=giorni_custom)
    else:
        return base_date

def show_upcoming_deadlines(days: int = 30):
    """Mostra scadenze prossime"""
    db = SessionLocal()
    
    try:
        end_date = date.today() + timedelta(days=days)
        
        scadenze = db.query(ScadenzeFatturazione).filter(
            and_(
                ScadenzeFatturazione.emessa == False,
                ScadenzeFatturazione.data_scadenza <= end_date
            )
        ).order_by(ScadenzeFatturazione.data_scadenza.asc()).all()
        
        if not scadenze:
            console.print(f"✅ Nessuna scadenza nei prossimi {days} giorni", style="green")
            return
        
        table = Table(title=f"💰 Scadenze prossimi {days} giorni")
        table.add_column("Scadenza", style="cyan")
        table.add_column("Cliente", style="yellow")
        table.add_column("Tipo", style="white")
        table.add_column("Descrizione", style="dim")
        table.add_column("Importo", style="green", justify="right")
        table.add_column("Stato", style="red")
        
        total_overdue = 0
        total_upcoming = 0
        overdue_count = 0
        
        today = date.today()
        
        for scadenza in scadenze:
            is_overdue = scadenza.data_scadenza < today
            days_diff = (scadenza.data_scadenza - today).days
            
            if days_diff == 0:
                scadenza_str = "🔥 OGGI"
                style = "bold red"
            elif days_diff < 0:
                scadenza_str = f"🔴 {abs(days_diff)} gg fa"
                style = "red"
            elif days_diff <= 7:
                scadenza_str = f"⚠️ {days_diff} giorni"
                style = "yellow"
            else:
                scadenza_str = f"⏳ {days_diff} giorni"
                style = "dim"
            
            # Handle variable amounts
            if not scadenza.importo_fisso and (scadenza.importo_previsto is None or scadenza.importo_previsto == 0):
                importo_display = "DA DEFINIRE ⚠️"
                importo_value = 0
            else:
                importo_display = f"€{scadenza.importo_previsto or 0:.2f}"
                importo_value = scadenza.importo_previsto or 0
            
            table.add_row(
                f"[{style}]{scadenza_str}[/{style}]",
                scadenza.cliente.nome,
                f"{scadenza.tipo_icon} {scadenza.tipo}",
                scadenza.descrizione or "-",
                importo_display,
                "🔴 SCADUTA" if is_overdue else "⏳ Pending"
            )
            
            if is_overdue:
                total_overdue += importo_value
                overdue_count += 1
            else:
                total_upcoming += importo_value
        
        console.print(table)
        
        # Summary
        if overdue_count > 0:
            console.print(f"\n🚨 [bold red]{overdue_count} scadenze OVERDUE - €{total_overdue:.2f}[/bold red]")
        if total_upcoming > 0:
            console.print(f"⏳ Prossime scadenze: €{total_upcoming:.2f}")
        console.print(f"💰 [bold]TOTALE:[/bold] €{total_overdue + total_upcoming:.2f}")

    except Exception as e:
        console.print(f"❌ Errore visualizzazione scadenze: {e}", style="red")
    finally:
        db.close()

def add_scadenza(
    cliente_nome: str,
    tipo: str = typer.Option("fattura", help="Tipo documento (fattura/parcella)"),
    importo: Optional[float] = typer.Option(None, "--importo", "-i", help="Importo previsto"),
    descrizione: Optional[str] = typer.Option(None, "--desc", "-d", help="Descrizione"),
    scadenza: Optional[str] = typer.Option(None, "--data", help="Data scadenza (YYYY-MM-DD)"),
    ricorrenza: Optional[str] = typer.Option(None, "--ricorrenza", "-r", help="mensile|bimestrale|trimestrale|semestrale|annuale"),
    giorni_custom: Optional[int] = typer.Option(None, "--giorni", help="Giorni per ricorrenza custom"),
    importo_variabile: bool = typer.Option(False, "--importo-variabile", help="Importo varia ogni ricorrenza")
):
    """Aggiungi nuova scadenza fatturazione"""
    db = SessionLocal()
    
    try:
        # Find cliente
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return
        
        # Parse date
        if scadenza:
            try:
                data_scadenza = datetime.strptime(scadenza, "%Y-%m-%d").date()
            except ValueError:
                console.print("❌ Formato data non valido (usa YYYY-MM-DD)", style="red")
                return
        else:
            # Default to end of current month
            today = date.today()
            data_scadenza = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        
        # Validate tipo
        if tipo not in ['fattura', 'parcella']:
            console.print("❌ Tipo deve essere 'fattura' o 'parcella'", style="red")
            return
        
        # Validate ricorrenza
        valid_ricorrenze = ['mensile', 'bimestrale', 'trimestrale', 'semestrale', 'annuale', 'custom']
        if ricorrenza and ricorrenza not in valid_ricorrenze:
            console.print(f"❌ Ricorrenza non valida. Usa: {', '.join(valid_ricorrenze)}", style="red")
            return
        
        if ricorrenza == 'custom' and not giorni_custom:
            console.print("❌ Specifica --giorni per ricorrenza custom", style="red")
            return
        
        # Handle variable amount logic
        if importo_variabile:
            if not ricorrenza:
                console.print("❌ --importo-variabile richiede una ricorrenza", style="red")
                return
            # Set amount to 0 for variable amounts (to be defined later)
            final_importo = 0
            importo_fisso = False
        else:
            final_importo = importo
            importo_fisso = True
        
        # Create scadenza
        nuova_scadenza = ScadenzeFatturazione(
            cliente_id=cliente.id,
            tipo=tipo,
            data_scadenza=data_scadenza,
            importo_previsto=final_importo,
            descrizione=descrizione,
            ricorrenza=ricorrenza,
            giorni_ricorrenza=giorni_custom,
            importo_fisso=importo_fisso
        )
        
        db.add(nuova_scadenza)
        db.commit()
        
        console.print(f"✅ Scadenza aggiunta per [bold]{cliente.nome}[/bold]", style="green")
        console.print(f"📅 Data: {data_scadenza.strftime('%d/%m/%Y')}")
        
        if importo_variabile:
            console.print(f"💰 Importo: [yellow]VARIABILE (da definire ogni volta)[/yellow]")
        else:
            console.print(f"💰 Importo: €{final_importo or 0:.2f}")
            
        if ricorrenza:
            console.print(f"🔄 Ricorrenza: {ricorrenza}")
            if ricorrenza == 'custom':
                console.print(f"📆 Ogni {giorni_custom} giorni")

    except Exception as e:
        console.print(f"❌ Errore creazione scadenza: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def list_scadenze(
    cliente: Optional[str] = typer.Option(None, "--cliente", "-c", help="Filtra per cliente"),
    overdue: bool = typer.Option(False, "--overdue", help="Solo scadenze passate"),
    pending: bool = typer.Option(False, "--pending", help="Solo scadenze non emesse"),
    tipo: Optional[str] = typer.Option(None, "--tipo", help="Filtra per tipo (fattura/parcella)")
):
    """Lista scadenze fatturazione"""
    db = SessionLocal()
    
    try:
        query = db.query(ScadenzeFatturazione)
        
        # Apply filters
        if cliente:
            cliente_obj = get_cliente_by_name(cliente, db)
            if not cliente_obj:
                console.print(f"❌ Cliente '{cliente}' non trovato", style="red")
                return
            query = query.filter(ScadenzeFatturazione.cliente_id == cliente_obj.id)
        
        if overdue:
            query = query.filter(
                and_(
                    ScadenzeFatturazione.emessa == False,
                    ScadenzeFatturazione.data_scadenza < date.today()
                )
            )
        elif pending:
            query = query.filter(ScadenzeFatturazione.emessa == False)
        
        if tipo:
            query = query.filter(ScadenzeFatturazione.tipo == tipo)
        
        scadenze = query.order_by(ScadenzeFatturazione.data_scadenza.desc()).all()
        
        if not scadenze:
            console.print("📅 Nessuna scadenza trovata", style="dim")
            return
        
        table = Table(title="💰 Scadenze Fatturazione")
        table.add_column("ID", style="dim", width=3)
        table.add_column("Cliente", style="cyan")
        table.add_column("Tipo", style="white")
        table.add_column("Descrizione", style="dim")
        table.add_column("Scadenza", style="yellow")
        table.add_column("Importo", style="green", justify="right")
        table.add_column("Ricorrenza", style="magenta")
        table.add_column("Stato", style="red")
        
        total_pending = 0
        total_emesse = 0
        
        for scad in scadenze:
            is_overdue = scad.is_overdue
            
            if is_overdue:
                data_style = "red"
                data_str = f"🔴 {scad.data_scadenza.strftime('%d/%m/%Y')}"
            elif not scad.emessa and scad.data_scadenza <= date.today() + timedelta(days=7):
                data_style = "yellow"
                data_str = f"⚠️ {scad.data_scadenza.strftime('%d/%m/%Y')}"
            else:
                data_style = "dim"
                data_str = scad.data_scadenza.strftime('%d/%m/%Y')
            
            stato = "✅ Emessa" if scad.emessa else ("🔴 OVERDUE" if is_overdue else "⏳ Pending")
            
            # Handle variable amounts display
            if not scad.importo_fisso and (scad.importo_previsto is None or scad.importo_previsto == 0):
                importo_display = "[yellow]DA DEFINIRE[/yellow]"
                importo_style = "yellow"
            else:
                importo_display = f"€{scad.importo_previsto or 0:.2f}"
                importo_style = "green"
            
            table.add_row(
                str(scad.id),
                scad.cliente.nome,
                f"{scad.tipo_icon} {scad.tipo}",
                scad.descrizione or "-",
                f"[{data_style}]{data_str}[/{data_style}]",
                f"[{importo_style}]{importo_display}[/{importo_style}]",
                scad.ricorrenza or "-",
                stato
            )
            
            if scad.emessa:
                total_emesse += scad.importo_previsto or 0
            else:
                total_pending += scad.importo_previsto or 0
        
        console.print(table)
        console.print(f"\n💰 [bold]Pending:[/bold] €{total_pending:.2f}")
        console.print(f"✅ [bold]Emesse:[/bold] €{total_emesse:.2f}")

    except Exception as e:
        console.print(f"❌ Errore lista scadenze: {e}", style="red")
    finally:
        db.close()

def show_invoice_details(
    cliente_nome: str,
    next_only: bool = typer.Option(False, "--next", help="Solo prossima scadenza")
):
    """Mostra dettagli per compilazione fattura/parcella"""
    db = SessionLocal()
    
    try:
        # Find cliente
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return
        
        # Get scadenza
        if next_only:
            scadenza = db.query(ScadenzeFatturazione).filter(
                and_(
                    ScadenzeFatturazione.cliente_id == cliente.id,
                    ScadenzeFatturazione.emessa == False
                )
            ).order_by(ScadenzeFatturazione.data_scadenza.asc()).first()
            
            if not scadenza:
                console.print(f"❌ Nessuna scadenza pending per {cliente.nome}", style="yellow")
                return
        else:
            # Show latest pending or ask for selection
            scadenze = db.query(ScadenzeFatturazione).filter(
                and_(
                    ScadenzeFatturazione.cliente_id == cliente.id,
                    ScadenzeFatturazione.emessa == False
                )
            ).order_by(ScadenzeFatturazione.data_scadenza.asc()).all()
            
            if not scadenze:
                console.print(f"❌ Nessuna scadenza pending per {cliente.nome}", style="yellow")
                return
            
            scadenza = scadenze[0]  # Take first (earliest)
        
        # Get unbilled time tracking for this client
        ore_non_fatturate = db.query(TimeTracking).filter(
            and_(
                TimeTracking.cliente_id == cliente.id,
                TimeTracking.fine.isnot(None),
                TimeTracking.fatturato == False
            )
        ).all()
        
        # Calculate totals
        ore_extra_totali = sum(t.durata_ore for t in ore_non_fatturate)
        compenso_ore_extra = sum(t.compenso for t in ore_non_fatturate)
        
        # Display invoice details
        panel_content = []
        panel_content.append(f"[bold cyan]Cliente:[/bold cyan] {cliente.nome}")
        if cliente.piva:
            panel_content.append(f"[bold]P.IVA:[/bold] {cliente.piva}")
        if cliente.cf:
            panel_content.append(f"[bold]C.F.:[/bold] {cliente.cf}")
        if cliente.indirizzo_completo:
            panel_content.append(f"[bold]Indirizzo:[/bold] {cliente.indirizzo_completo}")
        
        panel_content.append("")
        panel_content.append(f"[bold yellow]Scadenza:[/bold yellow] {scadenza.data_scadenza.strftime('%d/%m/%Y')}")
        panel_content.append(f"[bold]Tipo:[/bold] {scadenza.tipo_icon} {scadenza.tipo}")
        
        panel_content.append("")
        panel_content.append("[bold green]Prestazioni questo periodo:[/bold green]")
        
        # Handle variable amounts
        base_amount = scadenza.importo_previsto or 0
        
        if not scadenza.importo_fisso and base_amount == 0:
            panel_content.append("[yellow]⚠️ IMPORTO DA DEFINIRE (scadenza variabile)[/yellow]")
            panel_content.append("[dim]Usa: clienti scadenze aggiorna <id> --importo <valore>[/dim]")
            panel_content.append("")
        
        # Show base service if there's an amount
        if scadenza.descrizione and base_amount > 0:
            panel_content.append(f"• {scadenza.descrizione}: €{base_amount:.2f}")
        
        # Always show unbilled hours if any
        if ore_extra_totali > 0:
            panel_content.append(f"• Ore extra ({ore_extra_totali:.1f}h): €{compenso_ore_extra:.2f}")
        
        # Calculate totals - for variable amounts, only include time tracking
        if not scadenza.importo_fisso and base_amount == 0:
            total_imponibile = compenso_ore_extra  # Only time tracking
        else:
            total_imponibile = base_amount + compenso_ore_extra
        
        # Standard rates for freelance consultant
        rivalsa_previdenziale = total_imponibile * 0.04  # 4%
        totale_documento = total_imponibile + rivalsa_previdenziale
        
        panel_content.append("")
        panel_content.append(f"[bold]Totale imponibile:[/bold] €{total_imponibile:.2f}")
        panel_content.append(f"[bold]Rivalsa previdenziale 4%:[/bold] €{rivalsa_previdenziale:.2f}")
        panel_content.append(f"[bold green]TOTALE DOCUMENTO:[/bold green] €{totale_documento:.2f}")
        
        panel = Panel(
            "\n".join(panel_content),
            title="💰 DATI PER MICROFATTURE/ADE",
            border_style="green"
        )
        
        console.print(panel)
        
        # Try to copy to clipboard (optional)
        try:
            import pyperclip
            clipboard_text = f"""Cliente: {cliente.nome}
P.IVA: {cliente.piva or 'N/A'}
Indirizzo: {cliente.indirizzo_completo or 'N/A'}

Prestazioni:
- {scadenza.descrizione or 'Consulenza'}: €{base_amount:.2f}
{f'- Ore extra ({ore_extra_totali:.1f}h): €{compenso_ore_extra:.2f}' if ore_extra_totali > 0 else ''}

Totale imponibile: €{total_imponibile:.2f}
Rivalsa previdenziale 4%: €{rivalsa_previdenziale:.2f}
TOTALE DOCUMENTO: €{totale_documento:.2f}"""
            
            pyperclip.copy(clipboard_text)
            console.print("\n📋 [bold green]Dati copiati negli appunti! ✓[/bold green]")
        except ImportError:
            console.print("\n💡 [dim]Installa pyperclip per copiare automaticamente negli appunti[/dim]")
        except Exception:
            pass  # Ignore clipboard errors

    except Exception as e:
        console.print(f"❌ Errore dettaglio fattura: {e}", style="red")
    finally:
        db.close()

def aggiorna_scadenza(
    scadenza_id: int,
    importo: Optional[float] = typer.Option(None, "--importo", "-i", help="Nuovo importo"),
    descrizione: Optional[str] = typer.Option(None, "--desc", "-d", help="Nuova descrizione"),
    ricorrenza: Optional[str] = typer.Option(None, "--ricorrenza", "-r", help="Nuova ricorrenza (mensile/bimestrale/trimestrale/semestrale/annuale/nessuna)"),
    data_scadenza: Optional[str] = typer.Option(None, "--data", help="Nuova data scadenza (YYYY-MM-DD)")
):
    """Aggiorna importo, descrizione, ricorrenza e/o data scadenza di un pagamento"""
    db = SessionLocal()
    
    try:
        scadenza = db.query(ScadenzeFatturazione).filter_by(id=scadenza_id).first()
        if not scadenza:
            console.print(f"❌ Scadenza ID {scadenza_id} non trovata", style="red")
            return
        
        if scadenza.emessa:
            console.print(f"⚠️ Attenzione: stai modificando una scadenza già emessa", style="yellow")
            confirm = typer.confirm("Vuoi continuare?")
            if not confirm:
                console.print("Operazione annullata", style="dim")
                return
        
        # Track changes
        changes = []
        
        # Update amount
        if importo is not None:
            old_amount = scadenza.importo_previsto or 0
            scadenza.importo_previsto = importo
            
            # If setting an amount > 0 on a variable amount scadenza, make it fixed
            if not scadenza.importo_fisso and importo > 0:
                scadenza.importo_fisso = True
                changes.append(f"Tipo cambiato da VARIABILE a FISSO")
            
            changes.append(f"Importo: €{old_amount:.2f} → €{importo:.2f}")
        
        # Update description
        if descrizione is not None:
            old_desc = scadenza.descrizione or "N/A"
            scadenza.descrizione = descrizione
            changes.append(f"Descrizione: '{old_desc}' → '{descrizione}'")
        
        # Update ricorrenza
        if ricorrenza is not None:
            old_ricorrenza = scadenza.ricorrenza or "Nessuna"
            
            # Validate ricorrenza values
            valid_ricorrenze = ["mensile", "bimestrale", "trimestrale", "semestrale", "annuale", "nessuna", ""]
            ricorrenza_lower = ricorrenza.lower() if ricorrenza else ""
            
            if ricorrenza_lower not in valid_ricorrenze:
                console.print(f"❌ Ricorrenza non valida. Valori ammessi: {', '.join(valid_ricorrenze[:-2])}, nessuna", style="red")
                return
            
            # Set ricorrenza (None for "nessuna" or empty)
            new_ricorrenza = ricorrenza_lower if ricorrenza_lower and ricorrenza_lower != "nessuna" else None
            scadenza.ricorrenza = new_ricorrenza
            
            new_ricorrenza_display = new_ricorrenza or "Nessuna"
            changes.append(f"Ricorrenza: '{old_ricorrenza}' → '{new_ricorrenza_display.title()}'")
        
        # Update data_scadenza
        if data_scadenza is not None:
            old_data = scadenza.data_scadenza.strftime('%d/%m/%Y')
            
            try:
                from datetime import datetime
                new_data = datetime.strptime(data_scadenza, "%Y-%m-%d").date()
                scadenza.data_scadenza = new_data
                changes.append(f"Data scadenza: {old_data} → {new_data.strftime('%d/%m/%Y')}")
            except ValueError:
                console.print("❌ Formato data non valido. Usa YYYY-MM-DD (es: 2024-12-31)", style="red")
                return
        
        if not changes:
            console.print("❌ Specifica almeno --importo, --desc, --ricorrenza o --data", style="red")
            return
        
        db.commit()
        
        console.print(f"✅ Scadenza ID {scadenza_id} aggiornata:", style="green")
        console.print(f"👤 Cliente: {scadenza.cliente.nome}")
        console.print(f"📅 Scadenza: {scadenza.data_scadenza.strftime('%d/%m/%Y')}")
        
        for change in changes:
            console.print(f"🔄 {change}")

    except Exception as e:
        console.print(f"❌ Errore aggiornamento scadenza: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def mark_as_issued(
    scadenza_id: int,
    numero_documento: str,
    data_emissione: Optional[str] = typer.Option(None, help="Data emissione (YYYY-MM-DD), default oggi")
):
    """Marca scadenza come emessa"""
    db = SessionLocal()
    
    try:
        scadenza = db.query(ScadenzeFatturazione).filter_by(id=scadenza_id).first()
        if not scadenza:
            console.print(f"❌ Scadenza ID {scadenza_id} non trovata", style="red")
            return
        
        if scadenza.emessa:
            console.print(f"⚠️ Scadenza già marcata come emessa", style="yellow")
            return
        
        # Parse emission date
        if data_emissione:
            try:
                emissione = datetime.strptime(data_emissione, "%Y-%m-%d").date()
            except ValueError:
                console.print("❌ Formato data non valido (usa YYYY-MM-DD)", style="red")
                return
        else:
            emissione = date.today()
        
        # Update scadenza
        scadenza.emessa = True
        scadenza.data_emissione = emissione
        scadenza.numero_documento = numero_documento
        
        # If recurrent, create next occurrence
        if scadenza.ricorrenza:
            next_date = calculate_next_date(scadenza.data_scadenza, scadenza.ricorrenza, scadenza.giorni_ricorrenza)
            
            # For variable amounts, set to 0, otherwise keep same amount
            if scadenza.importo_fisso:
                next_importo = scadenza.importo_previsto
                status_msg = f"€{next_importo or 0:.2f}"
            else:
                next_importo = 0  # Variable amount to be defined
                status_msg = "VARIABILE"
            
            next_scadenza = ScadenzeFatturazione(
                cliente_id=scadenza.cliente_id,
                tipo=scadenza.tipo,
                data_scadenza=next_date,
                importo_previsto=next_importo,
                descrizione=scadenza.descrizione,
                ricorrenza=scadenza.ricorrenza,
                giorni_ricorrenza=scadenza.giorni_ricorrenza,
                importo_fisso=scadenza.importo_fisso
            )
            
            db.add(next_scadenza)
            console.print(f"🔄 Prossima ricorrenza creata: {next_date.strftime('%d/%m/%Y')} ({status_msg})")
        
        db.commit()
        
        console.print(f"✅ Scadenza marcata come emessa:", style="green")
        console.print(f"📄 Documento: {numero_documento}")
        console.print(f"📅 Data emissione: {emissione.strftime('%d/%m/%Y')}")
        console.print(f"👤 Cliente: {scadenza.cliente.nome}")

    except Exception as e:
        console.print(f"❌ Errore aggiornamento scadenza: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def mark_as_paid(
    scadenza_id: int,
    data_pagamento: Optional[str] = typer.Option(None, help="Data pagamento (YYYY-MM-DD), default oggi")
):
    """Marca scadenza come pagata"""
    db = SessionLocal()
    
    try:
        scadenza = db.query(ScadenzeFatturazione).filter_by(id=scadenza_id).first()
        if not scadenza:
            console.print(f"❌ Scadenza ID {scadenza_id} non trovata", style="red")
            return
        
        if not scadenza.emessa:
            console.print(f"⚠️ Scadenza non ancora emessa", style="yellow")
            return
        
        if scadenza.pagata:
            console.print(f"⚠️ Scadenza già marcata come pagata", style="yellow")
            return
        
        # Parse payment date
        if data_pagamento:
            try:
                pagamento = datetime.strptime(data_pagamento, "%Y-%m-%d").date()
            except ValueError:
                console.print("❌ Formato data non valido (usa YYYY-MM-DD)", style="red")
                return
        else:
            pagamento = date.today()
        
        # Update scadenza
        scadenza.pagata = True
        scadenza.data_pagamento = pagamento
        db.commit()
        
        console.print(f"💰 Scadenza marcata come pagata:", style="green")
        console.print(f"📅 Data pagamento: {pagamento.strftime('%d/%m/%Y')}")
        console.print(f"👤 Cliente: {scadenza.cliente.nome}")
        console.print(f"💵 Importo: €{scadenza.importo_previsto or 0:.2f}")

    except Exception as e:
        console.print(f"❌ Errore aggiornamento pagamento: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def process_recurring_invoices():
    """Process recurring invoices (utile per cron jobs)"""
    db = SessionLocal()
    
    try:
        today = date.today()
        
        # Find expired recurring invoices
        recurring_scadenze = db.query(ScadenzeFatturazione).filter(
            and_(
                ScadenzeFatturazione.ricorrenza.isnot(None),
                ScadenzeFatturazione.emessa == True,
                ScadenzeFatturazione.data_scadenza <= today
            )
        ).all()
        
        created_count = 0
        
        for scadenza in recurring_scadenze:
            # Check if next occurrence already exists
            next_date = calculate_next_date(scadenza.data_scadenza, scadenza.ricorrenza, scadenza.giorni_ricorrenza)
            
            existing = db.query(ScadenzeFatturazione).filter(
                and_(
                    ScadenzeFatturazione.cliente_id == scadenza.cliente_id,
                    ScadenzeFatturazione.data_scadenza == next_date,
                    ScadenzeFatturazione.emessa == False
                )
            ).first()
            
            if not existing:
                next_scadenza = ScadenzeFatturazione(
                    cliente_id=scadenza.cliente_id,
                    tipo=scadenza.tipo,
                    data_scadenza=next_date,
                    importo_previsto=scadenza.importo_previsto,
                    descrizione=scadenza.descrizione,
                    ricorrenza=scadenza.ricorrenza,
                    giorni_ricorrenza=scadenza.giorni_ricorrenza
                )
                
                db.add(next_scadenza)
                created_count += 1
        
        db.commit()
        
        if created_count > 0:
            console.print(f"🔄 Creazioni automatiche: {created_count} nuove scadenze ricorrenti", style="green")
        else:
            console.print("✅ Nessuna scadenza ricorrente da processare", style="dim")

    except Exception as e:
        console.print(f"❌ Errore processing ricorrenze: {e}", style="red")
        db.rollback()
    finally:
        db.close()

def delete_scadenza(scadenza_id: int):
    """Elimina una scadenza/pagamento"""
    db = SessionLocal()
    try:
        # Find scadenza by ID
        scadenza = db.query(ScadenzeFatturazione).filter(ScadenzeFatturazione.id == scadenza_id).first()
        
        if not scadenza:
            console.print(f"❌ Pagamento con ID {scadenza_id} non trovato", style="red")
            return
        
        # Show scadenza details before deletion
        console.print(f"\n📋 Dettagli pagamento da eliminare:")
        console.print(f"   Cliente: {scadenza.cliente.nome}")
        console.print(f"   Tipo: {scadenza.tipo}")
        console.print(f"   Importo: €{scadenza.importo_previsto or 'N/A'}")
        console.print(f"   Scadenza: {scadenza.data_scadenza.strftime('%d/%m/%Y')}")
        console.print(f"   Descrizione: {scadenza.descrizione or 'N/A'}")
        console.print(f"   Emessa: {'Sì' if scadenza.emessa else 'No'}")
        if scadenza.emessa:
            console.print(f"   Numero documento: {scadenza.numero_documento or 'N/A'}")
            console.print(f"   Pagata: {'Sì' if scadenza.pagato else 'No'}")
        
        # Confirmation
        import questionary
        if questionary.confirm(
            f"Sei sicuro di voler eliminare questo pagamento?",
            default=False
        ).ask():
            db.delete(scadenza)
            db.commit()
            console.print(f"✅ Pagamento ID {scadenza_id} eliminato con successo", style="green")
        else:
            console.print("❌ Eliminazione annullata", style="yellow")
            
    except Exception as e:
        console.print(f"❌ Errore durante eliminazione: {e}", style="red")
        db.rollback()
    finally:
        db.close()