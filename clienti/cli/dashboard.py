"""
Dashboard CLI avanzato for clienti CRM
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.tree import Tree
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, desc
import calendar

from core.database import SessionLocal
from core.models import Cliente, TimeTracking, Todo, ScadenzeFatturazione, Intervento

console = Console()

def get_advanced_stats() -> Dict[str, Any]:
    """Calcola statistiche avanzate per dashboard"""
    db = SessionLocal()
    
    try:
        today = date.today()
        this_month = today.month
        this_year = today.year
        last_month = (today - timedelta(days=30)).month
        
        # Clienti stats
        clienti_totali = db.query(Cliente).count()
        clienti_attivi = db.query(Cliente).filter(Cliente.stato == 'attivo').count()
        
        # Time tracking stats
        total_hours_query = db.query(
            func.sum((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24)
        ).filter(TimeTracking.fine.isnot(None))
        
        total_hours = total_hours_query.scalar() or 0
        
        # This month hours
        month_hours = db.query(
            func.sum((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24)
        ).filter(
            and_(
                TimeTracking.fine.isnot(None),
                extract('year', TimeTracking.inizio) == this_year,
                extract('month', TimeTracking.inizio) == this_month
            )
        ).scalar() or 0
        
        # Revenue stats
        total_revenue = db.query(
            func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
        ).filter(TimeTracking.fine.isnot(None)).scalar() or 0
        
        month_revenue = db.query(
            func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
        ).filter(
            and_(
                TimeTracking.fine.isnot(None),
                extract('year', TimeTracking.inizio) == this_year,
                extract('month', TimeTracking.inizio) == this_month
            )
        ).scalar() or 0
        
        # Todo stats
        todos_total = db.query(Todo).filter(Todo.completato == False).count()
        todos_overdue = db.query(Todo).filter(
            and_(
                Todo.completato == False,
                Todo.scadenza.isnot(None),
                Todo.scadenza < today
            )
        ).count()
        todos_today = db.query(Todo).filter(
            and_(
                Todo.completato == False,
                Todo.scadenza == today
            )
        ).count()
        
        # Scadenze stats
        scadenze_pending = db.query(ScadenzeFatturazione).filter(
            ScadenzeFatturazione.emessa == False
        ).count()
        scadenze_overdue = db.query(ScadenzeFatturazione).filter(
            and_(
                ScadenzeFatturazione.emessa == False,
                ScadenzeFatturazione.data_scadenza < today
            )
        ).count()
        
        # Interventi stats
        interventi_today = db.query(Intervento).filter(
            func.date(Intervento.data) == today.isoformat()
        ).count()
        
        interventi_month = db.query(Intervento).filter(
            and_(
                extract('year', Intervento.data) == this_year,
                extract('month', Intervento.data) == this_month
            )
        ).count()
        
        # Revenue from interventi
        interventi_revenue_month = db.query(
            func.sum(Intervento.costo)
        ).filter(
            and_(
                Intervento.costo.isnot(None),
                extract('year', Intervento.data) == this_year,
                extract('month', Intervento.data) == this_month
            )
        ).scalar() or 0
        
        # Non-billed revenue
        unbilled_hours = db.query(
            func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
        ).filter(
            and_(
                TimeTracking.fine.isnot(None),
                TimeTracking.fatturato == False
            )
        ).scalar() or 0
        
        unbilled_interventi = db.query(
            func.sum(Intervento.costo)
        ).filter(
            and_(
                Intervento.costo.isnot(None),
                Intervento.fatturato == False
            )
        ).scalar() or 0
        
        return {
            'clienti': {
                'totali': clienti_totali,
                'attivi': clienti_attivi,
                'percentage_attivi': (clienti_attivi / clienti_totali * 100) if clienti_totali > 0 else 0
            },
            'time_tracking': {
                'total_hours': total_hours,
                'month_hours': month_hours,
                'total_revenue': total_revenue,
                'month_revenue': month_revenue
            },
            'todos': {
                'total': todos_total,
                'overdue': todos_overdue,
                'today': todos_today
            },
            'scadenze': {
                'pending': scadenze_pending,
                'overdue': scadenze_overdue
            },
            'interventi': {
                'today': interventi_today,
                'month': interventi_month,
                'month_revenue': interventi_revenue_month
            },
            'unbilled': {
                'hours_revenue': unbilled_hours,
                'interventi_revenue': unbilled_interventi,
                'total': unbilled_hours + unbilled_interventi
            }
        }
        
    finally:
        db.close()

def show_advanced_dashboard():
    """Dashboard avanzato con statistiche complete"""
    console.print("📊 [bold blue]Dashboard CRM Avanzato[/bold blue]\n")
    
    # Get advanced stats
    stats = get_advanced_stats()
    
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=8),
        Layout(name="body"),
        Layout(name="footer", size=6)
    )
    
    # Header - KPI principali
    header_panels = []
    
    # Clienti panel
    clienti_info = f"[bold green]{stats['clienti']['attivi']}[/bold green] / {stats['clienti']['totali']}\n"
    clienti_info += f"[dim]{stats['clienti']['percentage_attivi']:.0f}% attivi[/dim]"
    header_panels.append(Panel(clienti_info, title="👥 Clienti"))
    
    # Revenue panel
    month_revenue = stats['time_tracking']['month_revenue'] + stats['interventi']['month_revenue']
    revenue_info = f"[bold green]€{month_revenue:.0f}[/bold green]\n[dim]questo mese[/dim]\n"
    revenue_info += f"[yellow]€{stats['unbilled']['total']:.0f}[/yellow] [dim]da fatturare[/dim]"
    header_panels.append(Panel(revenue_info, title="💰 Fatturato"))
    
    # Time panel
    month_hours = stats['time_tracking']['month_hours']
    time_info = f"[bold blue]{month_hours:.0f}h[/bold blue]\n[dim]questo mese[/dim]\n"
    time_info += f"[green]{stats['time_tracking']['total_hours']:.0f}h[/green] [dim]totali[/dim]"
    header_panels.append(Panel(time_info, title="⏱️ Ore"))
    
    # Tasks panel
    tasks_info = f"[bold yellow]{stats['todos']['total']}[/bold yellow] todo aperti\n"
    if stats['todos']['overdue'] > 0:
        tasks_info += f"[red]{stats['todos']['overdue']} in ritardo[/red]\n"
    if stats['todos']['today'] > 0:
        tasks_info += f"[yellow]{stats['todos']['today']} oggi[/yellow]"
    header_panels.append(Panel(tasks_info, title="✅ Todo"))
    
    layout["header"].update(Columns(header_panels))
    
    # Body - Dettagli e grafici
    body_layout = Layout()
    body_layout.split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    # Left panel - Alerts e priorità
    alerts_content = []
    
    if stats['scadenze']['overdue'] > 0:
        alerts_content.append(f"🔴 {stats['scadenze']['overdue']} scadenze in ritardo")
    if stats['todos']['overdue'] > 0:
        alerts_content.append(f"🔴 {stats['todos']['overdue']} todo in ritardo")
    if stats['todos']['today'] > 0:
        alerts_content.append(f"🟡 {stats['todos']['today']} todo per oggi")
    if stats['unbilled']['total'] > 1000:
        alerts_content.append(f"💰 €{stats['unbilled']['total']:.0f} da fatturare")
    
    if not alerts_content:
        alerts_content = ["✨ Tutto sotto controllo!"]
    
    alerts_panel = Panel(
        "\n".join(alerts_content),
        title="🚨 Alert & Priorità",
        border_style="red" if any("🔴" in alert for alert in alerts_content) else "green"
    )
    
    # Right panel - Quick stats
    quick_stats = []
    quick_stats.append(f"📊 Interventi oggi: {stats['interventi']['today']}")
    quick_stats.append(f"📊 Interventi mese: {stats['interventi']['month']}")
    quick_stats.append(f"💰 Ricavi interventi: €{stats['interventi']['month_revenue']:.0f}")
    quick_stats.append(f"📋 Scadenze pending: {stats['scadenze']['pending']}")
    
    quick_panel = Panel(
        "\n".join(quick_stats),
        title="📈 Statistiche Rapide"
    )
    
    body_layout["left"].update(alerts_panel)
    body_layout["right"].update(quick_panel)
    layout["body"].update(body_layout)
    
    # Footer - Progress bars
    footer_content = []
    
    # Monthly progress (assume 160h target)
    monthly_target = 160
    monthly_progress = (month_hours / monthly_target * 100) if monthly_target > 0 else 0
    
    footer_content.append(f"Progresso mensile ore: {month_hours:.0f}h / {monthly_target}h ({monthly_progress:.0f}%)")
    
    # Revenue progress (assume 8000€ target)
    revenue_target = 8000
    revenue_progress = (month_revenue / revenue_target * 100) if revenue_target > 0 else 0
    
    footer_content.append(f"Progresso fatturato: €{month_revenue:.0f} / €{revenue_target} ({revenue_progress:.0f}%)")
    
    layout["footer"].update(Panel("\n".join(footer_content), title="🎯 Obiettivi Mensili"))
    
    console.print(layout)
    
    # Quick actions
    console.print("\n🚀 [bold]Azioni rapide:[/bold]")
    console.print("• [cyan]clienti stats[/cyan] - Statistiche dettagliate")
    console.print("• [cyan]clienti report month[/cyan] - Report mensile")
    console.print("• [cyan]clienti todo overdue[/cyan] - Todo in ritardo")
    console.print("• [cyan]clienti scadenze overdue[/cyan] - Scadenze urgenti")

def show_stats_command(
    year: Optional[int] = None,
    month: Optional[int] = None,
    detailed: bool = False
):
    """Mostra statistiche dettagliate"""
    
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
        
    console.print(f"📊 [bold blue]Statistiche {calendar.month_name[month]} {year}[/bold blue]\n")
    
    db = SessionLocal()
    
    try:
        # Time tracking stats for period
        hours_query = db.query(
            func.sum((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24),
            func.count(TimeTracking.id)
        ).filter(
            and_(
                TimeTracking.fine.isnot(None),
                extract('year', TimeTracking.inizio) == year,
                extract('month', TimeTracking.inizio) == month
            )
        ).first()
        
        total_hours = hours_query[0] or 0
        total_sessions = hours_query[1] or 0
        
        # Revenue from time tracking
        revenue_query = db.query(
            func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
        ).filter(
            and_(
                TimeTracking.fine.isnot(None),
                extract('year', TimeTracking.inizio) == year,
                extract('month', TimeTracking.inizio) == month
            )
        ).scalar() or 0
        
        # Interventi stats
        interventi_stats = db.query(
            func.count(Intervento.id),
            func.sum(Intervento.durata_minuti),
            func.sum(Intervento.costo)
        ).filter(
            and_(
                extract('year', Intervento.data) == year,
                extract('month', Intervento.data) == month
            )
        ).first()
        
        interventi_count = interventi_stats[0] or 0
        interventi_minutes = interventi_stats[1] or 0
        interventi_revenue = interventi_stats[2] or 0
        
        # Create stats table
        table = Table(title=f"Riepilogo {calendar.month_name[month]} {year}")
        table.add_column("Categoria", style="cyan", no_wrap=True)
        table.add_column("Valore", style="green")
        table.add_column("Dettagli", style="dim")
        
        # Time tracking
        avg_session = total_hours / total_sessions if total_sessions > 0 else 0
        table.add_row(
            "⏱️ Time Tracking",
            f"{total_hours:.1f} ore",
            f"{total_sessions} sessioni (avg: {avg_session:.1f}h)"
        )
        
        table.add_row(
            "💰 Ricavi Time",
            f"€{revenue_query:.2f}",
            f"Tariffa media: €{revenue_query/total_hours:.0f}/h" if total_hours > 0 else "N/A"
        )
        
        # Interventi
        interventi_hours = interventi_minutes / 60 if interventi_minutes else 0
        table.add_row(
            "📝 Interventi",
            f"{interventi_count} totali",
            f"{interventi_hours:.1f} ore registrate"
        )
        
        table.add_row(
            "💰 Ricavi Interventi", 
            f"€{interventi_revenue:.2f}",
            f"Fatturabili: €{interventi_revenue:.0f}" if interventi_revenue else "N/A"
        )
        
        # Totals
        total_revenue = revenue_query + interventi_revenue
        total_time = total_hours + interventi_hours
        
        table.add_row("")
        table.add_row(
            "[bold]📊 TOTALI",
            f"[bold]€{total_revenue:.2f}",
            f"[bold]{total_time:.1f} ore totali"
        )
        
        console.print(table)
        
        # Detailed breakdown if requested
        if detailed:
            console.print("\n📈 [bold]Breakdown per cliente:[/bold]")
            
            # Top clients by revenue
            client_revenue = db.query(
                Cliente.nome,
                func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
            ).join(TimeTracking).filter(
                and_(
                    TimeTracking.fine.isnot(None),
                    extract('year', TimeTracking.inizio) == year,
                    extract('month', TimeTracking.inizio) == month
                )
            ).group_by(Cliente.nome).order_by(desc(func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria))).limit(5).all()
            
            if client_revenue:
                client_table = Table(title="Top 5 Clienti per Fatturato")
                client_table.add_column("Cliente", style="cyan")
                client_table.add_column("Fatturato", style="green", justify="right")
                client_table.add_column("% del totale", style="yellow", justify="right")
                
                for cliente, revenue in client_revenue:
                    percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                    client_table.add_row(
                        cliente,
                        f"€{revenue:.2f}",
                        f"{percentage:.1f}%"
                    )
                
                console.print(client_table)
        
    finally:
        db.close()

def create_ascii_chart(data: list, title: str, max_width: int = 50) -> str:
    """Crea un grafico ASCII semplice"""
    if not data or all(v == 0 for v in data):
        return f"{title}\nNessun dato disponibile"
    
    max_val = max(data)
    min_val = min(data)
    
    chart_lines = [title, "=" * len(title)]
    
    for i, value in enumerate(data):
        if max_val > 0:
            bar_length = int((value / max_val) * max_width)
            bar = "█" * bar_length + "░" * (max_width - bar_length)
            chart_lines.append(f"{i+1:2d}: {bar} {value:.1f}")
        else:
            chart_lines.append(f"{i+1:2d}: {'░' * max_width} 0.0")
    
    return "\n".join(chart_lines)

def show_monthly_report(year: Optional[int] = None):
    """Report mensile con trend"""
    if not year:
        year = datetime.now().year
        
    console.print(f"📈 [bold blue]Report Annuale {year}[/bold blue]\n")
    
    db = SessionLocal()
    
    try:
        # Collect monthly data
        monthly_hours = []
        monthly_revenue = []
        month_names = []
        
        for month in range(1, 13):
            # Hours for month
            hours = db.query(
                func.sum((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24)
            ).filter(
                and_(
                    TimeTracking.fine.isnot(None),
                    extract('year', TimeTracking.inizio) == year,
                    extract('month', TimeTracking.inizio) == month
                )
            ).scalar() or 0
            
            # Revenue for month
            revenue = db.query(
                func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
            ).filter(
                and_(
                    TimeTracking.fine.isnot(None),
                    extract('year', TimeTracking.inizio) == year,
                    extract('month', TimeTracking.inizio) == month
                )
            ).scalar() or 0
            
            # Add interventi revenue
            interventi_revenue = db.query(
                func.sum(Intervento.costo)
            ).filter(
                and_(
                    Intervento.costo.isnot(None),
                    extract('year', Intervento.data) == year,
                    extract('month', Intervento.data) == month
                )
            ).scalar() or 0
            
            monthly_hours.append(hours)
            monthly_revenue.append(revenue + interventi_revenue)
            month_names.append(calendar.month_abbr[month])
        
        # Create summary table
        summary_table = Table(title=f"Riepilogo {year}")
        summary_table.add_column("Mese", style="cyan")
        summary_table.add_column("Ore", style="blue", justify="right")
        summary_table.add_column("Fatturato", style="green", justify="right")
        summary_table.add_column("€/ora", style="yellow", justify="right")
        
        total_hours = sum(monthly_hours)
        total_revenue = sum(monthly_revenue)
        
        for i, (month_name, hours, revenue) in enumerate(zip(month_names, monthly_hours, monthly_revenue)):
            rate = revenue / hours if hours > 0 else 0
            summary_table.add_row(
                month_name,
                f"{hours:.1f}",
                f"€{revenue:.0f}",
                f"€{rate:.0f}"
            )
        
        # Add totals
        avg_rate = total_revenue / total_hours if total_hours > 0 else 0
        summary_table.add_row("")
        summary_table.add_row(
            "[bold]TOTALE",
            f"[bold]{total_hours:.1f}",
            f"[bold]€{total_revenue:.0f}",
            f"[bold]€{avg_rate:.0f}"
        )
        
        console.print(summary_table)
        
        # ASCII charts
        console.print(f"\n{create_ascii_chart(monthly_hours, '📊 Trend Ore Mensili')}")
        console.print(f"\n{create_ascii_chart(monthly_revenue, '💰 Trend Fatturato Mensile')}")
        
    finally:
        db.close()

def show_alerts():
    """Mostra alert e promemoria importanti"""
    console.print("🚨 [bold red]Alert e Promemoria[/bold red]\n")
    
    db = SessionLocal()
    
    try:
        today = date.today()
        alerts = []
        
        # Todo overdue
        todos_overdue = db.query(Todo).filter(
            and_(
                Todo.completato == False,
                Todo.scadenza.isnot(None),
                Todo.scadenza < today
            )
        ).order_by(Todo.scadenza).all()
        
        if todos_overdue:
            alerts.append("🔴 [bold]Todo in Ritardo:[/bold]")
            for todo in todos_overdue[:5]:  # Max 5
                days_overdue = (today - todo.scadenza).days
                cliente_info = f" ({todo.cliente.nome})" if todo.cliente else ""
                alerts.append(f"  • {todo.titolo}{cliente_info} - {days_overdue} giorni fa")
        
        # Scadenze overdue
        scadenze_overdue = db.query(ScadenzeFatturazione).filter(
            and_(
                ScadenzeFatturazione.emessa == False,
                ScadenzeFatturazione.data_scadenza < today
            )
        ).order_by(ScadenzeFatturazione.data_scadenza).all()
        
        if scadenze_overdue:
            alerts.append("\n💰 [bold]Scadenze in Ritardo:[/bold]")
            for scadenza in scadenze_overdue[:5]:  # Max 5
                days_overdue = (today - scadenza.data_scadenza).days
                alerts.append(f"  • {scadenza.cliente.nome}: {scadenza.descrizione or scadenza.tipo} - {days_overdue} giorni")
        
        # Todo today
        todos_today = db.query(Todo).filter(
            and_(
                Todo.completato == False,
                Todo.scadenza == today
            )
        ).all()
        
        if todos_today:
            alerts.append("\n🟡 [bold]Todo per Oggi:[/bold]")
            for todo in todos_today:
                cliente_info = f" ({todo.cliente.nome})" if todo.cliente else ""
                alerts.append(f"  • {todo.titolo}{cliente_info}")
        
        # Unbilled revenue alert
        unbilled_hours = db.query(
            func.sum(((func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24) * TimeTracking.tariffa_oraria)
        ).filter(
            and_(
                TimeTracking.fine.isnot(None),
                TimeTracking.fatturato == False
            )
        ).scalar() or 0
        
        unbilled_interventi = db.query(
            func.sum(Intervento.costo)
        ).filter(
            and_(
                Intervento.costo.isnot(None),
                Intervento.fatturato == False
            )
        ).scalar() or 0
        
        total_unbilled = unbilled_hours + unbilled_interventi
        
        if total_unbilled > 1000:
            alerts.append(f"\n💸 [bold]Fatturazione Pending:[/bold]")
            alerts.append(f"  • €{total_unbilled:.2f} totali da fatturare")
            if unbilled_hours > 0:
                alerts.append(f"  • €{unbilled_hours:.2f} da ore lavorate")
            if unbilled_interventi > 0:
                alerts.append(f"  • €{unbilled_interventi:.2f} da interventi")
        
        if alerts:
            console.print(Panel("\n".join(alerts), title="🚨 Richiede Attenzione", border_style="red"))
        else:
            console.print(Panel("✨ Tutto sotto controllo!\nNessun alert attivo.", title="✅ Status OK", border_style="green"))
        
    finally:
        db.close()