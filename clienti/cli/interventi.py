"""
Interventi (Activity Log) CLI commands for clienti CRM
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, desc
import questionary
import csv
from pathlib import Path

from core.database import SessionLocal
from core.models import Cliente, Intervento

console = Console()

def get_cliente_by_name(nome: str, db: Session) -> Optional[Cliente]:
    """Find cliente by name (case insensitive search)"""
    return db.query(Cliente).filter(Cliente.nome.ilike(f"%{nome}%")).first()

def list_clienti_names(db: Session) -> list[str]:
    """Get list of client names for autocomplete"""
    clienti = db.query(Cliente).filter(Cliente.stato == 'attivo').all()
    return [c.nome for c in clienti]

def add_intervento():
    """Registra nuovo intervento con wizard interattivo"""
    db = SessionLocal()
    
    try:
        console.print("📝 [bold]Nuovo Intervento[/bold]", style="blue")
        
        # Selezione cliente
        clienti_names = list_clienti_names(db)
        if not clienti_names:
            console.print("❌ Nessun cliente attivo trovato", style="red")
            return
            
        cliente_nome = questionary.autocomplete(
            "Cliente:",
            choices=clienti_names
        ).ask()
        
        if not cliente_nome:
            console.print("❌ Operazione annullata", style="red")
            return
            
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return
        
        # Selezione tipo intervento
        tipo_choices = [
            {"name": "📞 Chiamata", "value": "call"},
            {"name": "📧 Email", "value": "email"},
            {"name": "🤝 Meeting", "value": "meeting"},
            {"name": "💻 Lavoro", "value": "lavoro"},
            {"name": "📝 Altro", "value": "altro"}
        ]
        
        tipo = questionary.select(
            "Tipo intervento:",
            choices=tipo_choices
        ).ask()
        
        if not tipo:
            console.print("❌ Operazione annullata", style="red")
            return
        
        # Input titolo
        titolo = questionary.text(
            "Titolo/Oggetto:",
            validate=lambda x: len(x.strip()) > 0 or "Il titolo non può essere vuoto"
        ).ask()
        
        if not titolo:
            console.print("❌ Operazione annullata", style="red")
            return
        
        # Input descrizione opzionale
        descrizione = questionary.text("Descrizione dettagliata (opzionale):").ask()
        
        # Durata opzionale
        has_durata = questionary.confirm("Specificare durata?", default=False).ask()
        durata_minuti = None
        if has_durata:
            durata_str = questionary.text(
                "Durata in minuti:",
                validate=lambda x: x.isdigit() and int(x) > 0 or "Inserire un numero positivo"
            ).ask()
            if durata_str:
                durata_minuti = int(durata_str)
        
        # Costo opzionale (per lavoro fatturabile)
        costo = None
        if tipo in ['lavoro', 'meeting'] or questionary.confirm("Intervento fatturabile?", default=False).ask():
            costo_str = questionary.text("Costo (€, opzionale):").ask()
            if costo_str and costo_str.replace('.', '').replace(',', '').isdigit():
                costo = float(costo_str.replace(',', '.'))
        
        # Crea l'intervento
        new_intervento = Intervento(
            cliente_id=cliente.id,
            tipo=tipo,
            titolo=titolo.strip(),
            descrizione=descrizione.strip() if descrizione else None,
            durata_minuti=durata_minuti,
            costo=costo
        )
        
        db.add(new_intervento)
        db.commit()
        
        # Conferma
        tipo_name = {
            'call': 'Chiamata', 'email': 'Email', 'meeting': 'Meeting',
            'lavoro': 'Lavoro', 'altro': 'Altro'
        }[tipo]
        
        durata_info = f" ({durata_minuti} min)" if durata_minuti else ""
        costo_info = f" - €{costo:.2f}" if costo else ""
        
        console.print(f"✅ {tipo_name} registrata per {cliente.nome}{durata_info}{costo_info}", style="green")
        
    except KeyboardInterrupt:
        console.print("❌ Operazione annullata", style="red")
    finally:
        db.close()

def list_interventi(
    cliente: Optional[str] = None,
    tipo: Optional[str] = None,
    today: bool = False,
    days: Optional[int] = None,
    month: Optional[int] = None
):
    """Lista interventi con filtri"""
    db = SessionLocal()
    
    try:
        query = db.query(Intervento)
        
        # Filtro cliente
        if cliente:
            cliente_obj = get_cliente_by_name(cliente, db)
            if cliente_obj:
                query = query.filter(Intervento.cliente_id == cliente_obj.id)
            else:
                console.print(f"❌ Cliente '{cliente}' non trovato", style="red")
                return
        
        # Filtro tipo
        if tipo:
            if tipo not in ['call', 'email', 'meeting', 'lavoro', 'altro']:
                console.print("❌ Tipo non valido (usa: call, email, meeting, lavoro, altro)", style="red")
                return
            query = query.filter(Intervento.tipo == tipo)
        
        # Filtri temporali
        if today:
            today_date = date.today()
            query = query.filter(
                extract('year', Intervento.data) == today_date.year,
                extract('month', Intervento.data) == today_date.month,
                extract('day', Intervento.data) == today_date.day
            )
        elif days:
            since_date = datetime.now() - timedelta(days=days)
            query = query.filter(Intervento.data >= since_date)
        elif month:
            year = datetime.now().year
            query = query.filter(
                extract('year', Intervento.data) == year,
                extract('month', Intervento.data) == month
            )
        
        interventi = query.order_by(desc(Intervento.data)).all()
        
        if not interventi:
            msg = "Nessun intervento trovato"
            if today:
                msg = "Nessun intervento oggi"
            elif cliente:
                msg = f"Nessun intervento per {cliente}"
            console.print(f"ℹ️ {msg}", style="yellow")
            return
        
        # Costruisci tabella
        title = "📝 Interventi"
        if cliente:
            title += f" - {cliente}"
        if tipo:
            tipo_names = {
                'call': 'Chiamate', 'email': 'Email', 'meeting': 'Meeting',
                'lavoro': 'Lavoro', 'altro': 'Altri'
            }
            title += f" ({tipo_names[tipo]})"
        if today:
            title += " - Oggi"
        elif days:
            title += f" - Ultimi {days} giorni"
        elif month:
            title += f" - Mese {month}"
            
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Data", width=12)
        table.add_column("Tipo", width=8, justify="center")
        table.add_column("Cliente", width=20)
        table.add_column("Titolo", min_width=25)
        table.add_column("Durata", width=8, justify="center")
        table.add_column("Costo", width=8, justify="right")
        
        total_duration = 0
        total_cost = 0
        
        for intervento in interventi:
            # Data e ora
            data_str = intervento.data.strftime("%d/%m %H:%M")
            if intervento.data.date() == date.today():
                data_str = f"[green]{data_str}[/green]"
            
            # Tipo con icona
            tipo_icon = intervento.tipo_icon
            
            # Cliente
            cliente_nome = intervento.cliente.nome
            
            # Titolo con descrizione se presente
            titolo = intervento.titolo
            if intervento.descrizione and len(intervento.descrizione) > 0:
                titolo += f"\n[dim]{intervento.descrizione[:50]}{'...' if len(intervento.descrizione) > 50 else ''}[/dim]"
            
            # Durata
            durata_str = "-"
            if intervento.durata_minuti:
                hours = intervento.durata_minuti // 60
                minutes = intervento.durata_minuti % 60
                if hours > 0:
                    durata_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
                else:
                    durata_str = f"{minutes}m"
                total_duration += intervento.durata_minuti
            
            # Costo
            costo_str = "-"
            if intervento.costo:
                costo_str = f"€{intervento.costo:.2f}"
                if not intervento.fatturato:
                    costo_str = f"[yellow]{costo_str}[/yellow]"  # Non fatturato
                total_cost += intervento.costo
            
            table.add_row(
                data_str,
                tipo_icon,
                cliente_nome,
                titolo,
                durata_str,
                costo_str
            )
        
        console.print(table)
        
        # Statistiche
        stats_parts = [f"📊 Totale interventi: {len(interventi)}"]
        
        if total_duration > 0:
            total_hours = total_duration // 60
            total_mins = total_duration % 60
            time_str = f"{total_hours}h {total_mins}m" if total_hours > 0 else f"{total_mins}m"
            stats_parts.append(f"⏱️ Durata totale: {time_str}")
        
        if total_cost > 0:
            stats_parts.append(f"💰 Valore totale: €{total_cost:.2f}")
            
            # Controlla quanti non sono fatturati
            non_fatturati = [i for i in interventi if i.costo and not i.fatturato]
            if non_fatturati:
                valore_non_fatturato = sum(i.costo for i in non_fatturati)
                stats_parts.append(f"[yellow]💸 Da fatturare: €{valore_non_fatturato:.2f}[/yellow]")
        
        console.print(f"\n{' | '.join(stats_parts)}", style="dim")
        
    finally:
        db.close()

def show_client_timeline(cliente_nome: str):
    """Mostra timeline completa degli interventi per cliente"""
    db = SessionLocal()
    
    try:
        cliente = get_cliente_by_name(cliente_nome, db)
        if not cliente:
            console.print(f"❌ Cliente '{cliente_nome}' non trovato", style="red")
            return
        
        interventi = db.query(Intervento).filter(
            Intervento.cliente_id == cliente.id
        ).order_by(desc(Intervento.data)).limit(20).all()
        
        if not interventi:
            console.print(f"ℹ️ Nessun intervento registrato per {cliente.nome}", style="yellow")
            return
        
        console.print(f"📋 [bold]Timeline interventi - {cliente.nome}[/bold]", style="blue")
        
        current_date = None
        total_time = 0
        total_value = 0
        
        for intervento in interventi:
            # Raggruppa per data
            intervento_date = intervento.data.date()
            if intervento_date != current_date:
                current_date = intervento_date
                date_str = current_date.strftime("%A %d/%m/%Y")
                if current_date == date.today():
                    date_str += " (oggi)"
                elif current_date == date.today() - timedelta(days=1):
                    date_str += " (ieri)"
                    
                console.print(f"\n📅 [bold]{date_str}[/bold]")
            
            # Dettagli intervento
            time_str = intervento.data.strftime("%H:%M")
            tipo_icon = intervento.tipo_icon
            
            durata_info = ""
            if intervento.durata_minuti:
                total_time += intervento.durata_minuti
                hours = intervento.durata_minuti // 60
                minutes = intervento.durata_minuti % 60
                if hours > 0:
                    durata_info = f" ({hours}h {minutes}m)" if minutes > 0 else f" ({hours}h)"
                else:
                    durata_info = f" ({minutes}m)"
            
            costo_info = ""
            if intervento.costo:
                total_value += intervento.costo
                fatturato_status = "" if intervento.fatturato else " [yellow](da fatturare)[/yellow]"
                costo_info = f" - €{intervento.costo:.2f}{fatturato_status}"
            
            console.print(f"  {time_str} {tipo_icon} {intervento.titolo}{durata_info}{costo_info}")
            
            if intervento.descrizione:
                console.print(f"    [dim]{intervento.descrizione}[/dim]")
        
        # Statistiche finali
        console.print(f"\n📊 [bold]Riepilogo (ultimi 20):[/bold]")
        console.print(f"  • Interventi: {len(interventi)}")
        
        if total_time > 0:
            total_hours = total_time // 60
            total_mins = total_time % 60
            time_str = f"{total_hours}h {total_mins}m" if total_hours > 0 else f"{total_mins}m"
            console.print(f"  • Tempo totale: {time_str}")
        
        if total_value > 0:
            console.print(f"  • Valore totale: €{total_value:.2f}")
        
    finally:
        db.close()

def export_interventi_csv(
    output_file: Optional[str] = None,
    cliente: Optional[str] = None,
    month: Optional[int] = None
):
    """Export interventi to CSV"""
    db = SessionLocal()
    
    try:
        query = db.query(Intervento)
        
        # Filtri
        if cliente:
            cliente_obj = get_cliente_by_name(cliente, db)
            if cliente_obj:
                query = query.filter(Intervento.cliente_id == cliente_obj.id)
            else:
                console.print(f"❌ Cliente '{cliente}' non trovato", style="red")
                return
        
        if month:
            year = datetime.now().year
            query = query.filter(
                extract('year', Intervento.data) == year,
                extract('month', Intervento.data) == month
            )
        
        interventi = query.order_by(desc(Intervento.data)).all()
        
        if not interventi:
            console.print("ℹ️ Nessun intervento da esportare", style="yellow")
            return
        
        # Genera nome file se non specificato
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"interventi_{timestamp}"
            if cliente:
                filename += f"_{cliente.replace(' ', '_').lower()}"
            if month:
                filename += f"_m{month:02d}"
            output_file = f"data/exports/{filename}.csv"
        
        # Assicurati che la directory esista
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Scrivi CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'data', 'ora', 'tipo', 'cliente', 'titolo', 'descrizione',
                'durata_minuti', 'costo', 'fatturato'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for intervento in interventi:
                writer.writerow({
                    'data': intervento.data.strftime('%Y-%m-%d'),
                    'ora': intervento.data.strftime('%H:%M'),
                    'tipo': intervento.tipo,
                    'cliente': intervento.cliente.nome,
                    'titolo': intervento.titolo,
                    'descrizione': intervento.descrizione or '',
                    'durata_minuti': intervento.durata_minuti or '',
                    'costo': intervento.costo or '',
                    'fatturato': 'Sì' if intervento.fatturato else 'No'
                })
        
        console.print(f"✅ Export completato: {output_file}", style="green")
        console.print(f"📊 {len(interventi)} interventi esportati", style="dim")
        
    except Exception as e:
        console.print(f"❌ Errore durante l'export: {e}", style="red")
    finally:
        db.close()

def mark_intervento_billed(intervento_id: int):
    """Marca intervento come fatturato"""
    db = SessionLocal()
    
    try:
        intervento = db.query(Intervento).filter(Intervento.id == intervento_id).first()
        if not intervento:
            console.print(f"❌ Intervento con ID {intervento_id} non trovato", style="red")
            return
        
        if not intervento.costo:
            console.print(f"ℹ️ Intervento '{intervento.titolo}' non ha costo associato", style="yellow")
            return
            
        if intervento.fatturato:
            console.print(f"ℹ️ Intervento '{intervento.titolo}' già fatturato", style="yellow")
            return
        
        intervento.fatturato = True
        db.commit()
        
        console.print(f"✅ Intervento '{intervento.titolo}' marcato come fatturato (€{intervento.costo:.2f})", style="green")
        
    finally:
        db.close()

def show_today_summary():
    """Mostra riassunto interventi di oggi"""
    db = SessionLocal()
    
    try:
        today = date.today()
        interventi = db.query(Intervento).filter(
            extract('year', Intervento.data) == today.year,
            extract('month', Intervento.data) == today.month,
            extract('day', Intervento.data) == today.day
        ).order_by(Intervento.data).all()
        
        if not interventi:
            console.print("✨ Nessun intervento registrato oggi", style="green")
            return
        
        console.print("📅 [bold]Attività di oggi[/bold]", style="blue")
        
        # Raggruppa per tipo
        by_type = {}
        total_time = 0
        total_value = 0
        
        for intervento in interventi:
            tipo = intervento.tipo
            if tipo not in by_type:
                by_type[tipo] = []
            by_type[tipo].append(intervento)
            
            if intervento.durata_minuti:
                total_time += intervento.durata_minuti
            if intervento.costo:
                total_value += intervento.costo
        
        # Mostra per tipo
        for tipo, items in by_type.items():
            tipo_names = {
                'call': '📞 Chiamate', 'email': '📧 Email', 'meeting': '🤝 Meeting',
                'lavoro': '💻 Lavoro', 'altro': '📝 Altri'
            }
            console.print(f"\n{tipo_names[tipo]} ({len(items)}):")
            
            for intervento in items:
                time_str = intervento.data.strftime("%H:%M")
                cliente_name = intervento.cliente.nome
                
                durata_info = ""
                if intervento.durata_minuti:
                    hours = intervento.durata_minuti // 60
                    minutes = intervento.durata_minuti % 60
                    if hours > 0:
                        durata_info = f" ({hours}h {minutes}m)" if minutes > 0 else f" ({hours}h)"
                    else:
                        durata_info = f" ({minutes}m)"
                
                costo_info = f" - €{intervento.costo:.2f}" if intervento.costo else ""
                
                console.print(f"  {time_str} {cliente_name}: {intervento.titolo}{durata_info}{costo_info}")
        
        # Totali
        console.print(f"\n📊 [bold]Totali giornata:[/bold]")
        console.print(f"  • Interventi: {len(interventi)}")
        
        if total_time > 0:
            hours = total_time // 60
            minutes = total_time % 60
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            console.print(f"  • Tempo: {time_str}")
        
        if total_value > 0:
            console.print(f"  • Valore: €{total_value:.2f}")
        
    finally:
        db.close()