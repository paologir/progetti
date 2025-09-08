#!/usr/bin/env python3
"""
Clienti CRM - Sistema di gestione clienti per consulente digital marketing
Entry point principale CLI/Web
"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import init_database, get_database_info
from core.models import Cliente
from core.utils import import_clienti_json, backup_database, list_backups, restore_backup, cleanup_old_backups, auto_backup_if_enabled
from cli.clienti import list_clients, show_client, add_client, edit_client, delete_client
from cli.time import start_timer, stop_timer, timer_status, show_today_hours, show_week_report, show_client_report, show_unbilled, export_timesheet_csv, list_sessions, edit_session, delete_session
from cli.scadenze import show_upcoming_deadlines, add_scadenza, list_scadenze, show_invoice_details, mark_as_issued, mark_as_paid, process_recurring_invoices, aggiorna_scadenza, delete_scadenza
from cli.todo import add_todo, list_todos, show_today_todos, show_week_todos, show_client_todos, mark_todo_done, edit_todo, delete_todo
from cli.interventi import add_intervento, list_interventi, show_client_timeline, export_interventi_csv, mark_intervento_billed, show_today_summary, edit_intervento, delete_intervento
from cli.dashboard import show_advanced_dashboard, show_stats_command, show_monthly_report, show_alerts
from cli.export import export_obsidian_vault, export_cliente_markdown, export_csv_clienti, import_csv_clienti

console = Console()
app = typer.Typer(
    name="clienti",
    help="🚀 CRM per consulente digital marketing - Gestione clienti, time tracking e fatturazione",
    rich_markup_mode="rich",
    no_args_is_help=False  # Non mostrare help se no args
)

# Subcommands
client_app = typer.Typer(name="client", help="Gestione clienti")
time_app = typer.Typer(name="time", help="Time tracking")
todo_app = typer.Typer(name="todo", help="Todo list")
pagamenti_app = typer.Typer(name="pagamenti", help="Gestione pagamenti e fatturazione")
interventi_app = typer.Typer(name="interventi", help="Gestione interventi")
export_app = typer.Typer(name="export", help="Export dati")
backup_app = typer.Typer(name="backup", help="Gestione backup")

app.add_typer(client_app, name="client")
app.add_typer(time_app, name="time") 
app.add_typer(todo_app, name="todo")
app.add_typer(pagamenti_app, name="pagamenti")
app.add_typer(interventi_app, name="interventi")
app.add_typer(export_app, name="export")
app.add_typer(backup_app, name="backup")

@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """Callback principale - mostra dashboard se nessun comando"""
    # Auto backup on startup (silent)
    auto_backup_if_enabled()
    
    if ctx.invoked_subcommand is None:
        # Nessun comando specificato, mostra dashboard
        show_dashboard()

# Client commands
@client_app.command("list")
def client_list(
    attivi: bool = typer.Option(False, "--attivi", help="Solo clienti attivi"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filtra per tag"),
    cerca: Optional[str] = typer.Option(None, "--cerca", help="Cerca nel nome")
):
    """
    Lista tutti i clienti registrati nel CRM
    
    Visualizza una tabella colorata con informazioni essenziali di ogni cliente:
    nome, stato, P.IVA, tariffa oraria, budget mensile, tags e ultima attività.
    
    I clienti sono ordinati per data di ultima attività (più recenti in alto).
    
    Esempi:
        clienti client list                        # Lista completa di tutti i clienti
        clienti client list --attivi               # Solo clienti con stato 'attivo'
        clienti client list --tag "ecommerce"     # Solo clienti taggati come 'ecommerce'
        clienti client list --cerca "Maspe"       # Clienti con 'Maspe' nel nome
        clienti client list --attivi --tag "seo"  # Combinazione di filtri
    
    Colori nella tabella:
        • Verde: clienti attivi
        • Giallo: clienti prospect  
        • Grigio: clienti in pausa o archiviati
    """
    list_clients(attivi, tag, cerca)

@client_app.command("show")
def client_show(name: str = typer.Argument(..., help="Nome completo o parziale del cliente")):
    """
    Visualizza informazioni dettagliate di un cliente specifico
    
    Mostra tutte le informazioni memorizzate: dati anagrafici, contatti,
    statistiche ore lavorate, fatturati non emessi, todos aperti e
    timeline degli ultimi interventi.
    
    La ricerca è case-insensitive e supporta nomi parziali.
    
    Esempi:
        clienti client show "Maspe Srl"        # Nome completo
        clienti client show "maspe"            # Nome parziale (case-insensitive)
        clienti client show "Zero+"            # Funziona anche con caratteri speciali
    
    Sezioni visualizzate:
        • Informazioni anagrafiche complete
        • Statistiche ore lavorate e compensi
        • Ore non ancora fatturate (evidenziate in rosso)
        • Todo aperti collegati al cliente
        • Timeline ultimi 10 interventi
        • Lista contatti associati
    """
    show_client(name)

@client_app.command("add")
def client_add():
    """
    Aggiungi un nuovo cliente al CRM tramite wizard interattivo
    
    Avvia un processo guidato che richiede step-by-step tutte le informazioni
    necessarie per registrare un nuovo cliente. I campi obbligatori sono
    evidenziati e viene fornita validazione in tempo reale.
    
    Informazioni richieste:
        • Nome/ragione sociale (obbligatorio)
        • Partita IVA (opzionale, con validazione formato italiano)
        • Codice fiscale (opzionale)
        • Indirizzo completo (via, città, CAP, provincia)
        • Stato iniziale (attivo/prospect/pausa)
        • Tariffa oraria (default da configurazione)
        • Budget mensile (opzionale)
        • Tags per categorizzazione (separati da virgola)
        • Note aggiuntive
    
    Il sistema previene duplicati controllando nome e P.IVA esistenti.
    
    Esempi d'uso tipici:
        clienti client add          # Avvia il wizard completo
        
    Suggerimenti:
        • Usa tags coerenti: "ecommerce", "seo", "ads", "consulenza"
        • La tariffa oraria può essere modificata successivamente
        • Lo stato "prospect" è utile per potenziali clienti
    """
    add_client()

@client_app.command("edit")
def client_edit(cliente_id: int = typer.Argument(..., help="ID cliente da modificare")):
    """Modifica un cliente esistente"""
    edit_client(cliente_id)

@client_app.command("delete")
def client_delete(cliente_id: int = typer.Argument(..., help="ID cliente da eliminare")):
    """Elimina un cliente e tutti i dati collegati"""
    delete_client(cliente_id)

# Time tracking commands
@time_app.command("start")
def time_start(
    cliente: str = typer.Argument(..., help="Nome cliente"),
    task: Optional[str] = typer.Option(None, "--task", "-t", help="Descrizione attività"),
    tariffa: Optional[float] = typer.Option(None, "--tariffa", "-r", help="Tariffa oraria personalizzata")
):
    """
    Avvia un nuovo timer di time tracking per un cliente
    
    Crea una nuova sessione di lavoro tracciando automaticamente tempo e compenso.
    Solo un timer può essere attivo alla volta. Il sistema salva lo stato del timer
    per recuperarlo anche dopo riavvii dell'applicazione.
    
    Il cliente viene cercato per nome (ricerca case-insensitive e parziale).
    La tariffa oraria viene presa dal profilo cliente, ma può essere personalizzata.
    
    Esempi:
        clienti time start "Maspe Srl"                                    # Timer base
        clienti time start "maspe" --task "Ottimizzazione SEO"           # Con descrizione attività  
        clienti time start "Zero+" --task "Setup Google Ads" --tariffa 60 # Con tariffa custom
        clienti time start "fis" --task "Consulenza strategica"          # Nome parziale
    
    Funzionalità automatiche:
        • Calcolo compenso in tempo reale
        • Salvataggio stato per recupero sessione
        • Aggiornamento data ultima attività cliente
        • Persistenza attraverso riavvii applicazione
        
    Nota: Se esiste già un timer attivo, mostra le informazioni del timer corrente.
    """
    start_timer(cliente, task, tariffa)

@time_app.command("stop")
def time_stop():
    """
    Ferma il timer attualmente attivo e registra la sessione di lavoro
    
    Completa la sessione di time tracking corrente calcolando durata totale,
    compenso finale e salvando tutti i dati nel database. Il timer può essere
    fermato in qualsiasi momento e riprende da dove era stato lasciato.
    
    Operazioni automatiche:
        • Calcolo durata precisa in ore e minuti
        • Calcolo compenso basato su tariffa e tempo effettivo
        • Registrazione completa nel database
        • Pulizia stato timer temporaneo
        • Aggiornamento statistiche cliente
    
    Esempi:
        clienti time stop                  # Ferma il timer attivo
    
    Informazioni visualizzate:
        • Nome cliente e descrizione attività
        • Durata totale sessione (ore e minuti)
        • Compenso calcolato in base alla tariffa
        • Orario inizio e fine sessione
        
    Nota: Se non ci sono timer attivi, il comando mostra un messaggio informativo.
    """
    stop_timer()

@time_app.command("status")  
def time_status_cmd():
    """Mostra stato timer corrente"""
    timer_status()

@time_app.command("today")
def time_today():
    """Ore lavorate oggi"""
    show_today_hours()

@time_app.command("week")
def time_week():
    """Report settimanale ore"""
    show_week_report()

@time_app.command("report")
def time_report(
    cliente: Optional[str] = typer.Option(None, "--cliente", help="Report per cliente specifico")
):
    """Report ore per cliente"""
    if cliente:
        show_client_report(cliente)
    else:
        console.print("❌ Specifica un cliente con --cliente", style="red")

@time_app.command("unfiled")
def time_unfiled():
    """Ore non ancora fatturate"""
    show_unbilled()

@time_app.command("export")
def time_export(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Percorso file output CSV"),
    cliente: Optional[str] = typer.Option(None, "--cliente", "-c", help="Filtra per cliente"),
    month: Optional[int] = typer.Option(None, "--month", "-m", help="Filtra per mese (1-12)"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Filtra per anno")
):
    """Esporta timesheet in CSV"""
    export_timesheet_csv(output, cliente, month, year)

@time_app.command("list")
def time_list(
    cliente: Optional[str] = typer.Option(None, "--cliente", "-c", help="Filtra per cliente"),
    limit: int = typer.Option(10, "--limit", "-l", help="Numero massimo di sessioni da mostrare"),
    active: bool = typer.Option(False, "--active", "-a", help="Mostra solo sessioni attive")
):
    """Lista sessioni di time tracking"""
    list_sessions(cliente, limit, active)

@time_app.command("edit")  
def time_edit(session_id: int = typer.Argument(..., help="ID sessione da modificare")):
    """Modifica una sessione di time tracking"""
    edit_session(session_id)

@time_app.command("delete")
def time_delete(session_id: int = typer.Argument(..., help="ID sessione da eliminare")):
    """Elimina una sessione di time tracking"""
    delete_session(session_id)

# Pagamenti commands
@pagamenti_app.command("prossimi")
def pagamenti_prossimi(
    days: int = typer.Option(30, "--giorni", "-g", help="Giorni da controllare")
):
    """Pagamenti in scadenza nei prossimi giorni"""
    show_upcoming_deadlines(days)

@pagamenti_app.command("list")
def pagamenti_list(
    cliente: Optional[str] = typer.Option(None, "--cliente", "-c", help="Filtra per cliente"),
    overdue: bool = typer.Option(False, "--overdue", help="Solo pagamenti scaduti"),
    pending: bool = typer.Option(False, "--pending", help="Solo fatture non emesse"),
    tipo: Optional[str] = typer.Option(None, "--tipo", help="Filtra per tipo (fattura/parcella)")
):
    """Lista pagamenti e fatturazione con filtri avanzati"""
    list_scadenze(cliente, overdue, pending, tipo)

@pagamenti_app.command("add")
def pagamenti_add(
    cliente: str = typer.Argument(..., help="Nome cliente"),
    tipo: str = typer.Option("fattura", "--tipo", "-t", help="Tipo documento (fattura/parcella)"),
    importo: Optional[float] = typer.Option(None, "--importo", "-i", help="Importo previsto"),
    descrizione: Optional[str] = typer.Option(None, "--desc", "-d", help="Descrizione"),
    scadenza: Optional[str] = typer.Option(None, "--data", help="Data scadenza (YYYY-MM-DD)"),
    ricorrenza: Optional[str] = typer.Option(None, "--ricorrenza", "-r", help="mensile|bimestrale|trimestrale|semestrale|annuale"),
    giorni_custom: Optional[int] = typer.Option(None, "--giorni", help="Giorni per ricorrenza custom"),
    importo_variabile: bool = typer.Option(False, "--importo-variabile", help="Importo varia ogni ricorrenza")
):
    """Aggiungi nuovo pagamento/fatturazione ricorrente"""
    add_scadenza(cliente, tipo, importo, descrizione, scadenza, ricorrenza, giorni_custom, importo_variabile)

@pagamenti_app.command("dettaglio")
def pagamenti_dettaglio(
    cliente: str = typer.Argument(..., help="Nome cliente"),
    next_only: bool = typer.Option(False, "--next", help="Solo prossima scadenza")
):
    """Dettagli cliente per compilazione fattura/pagamento"""
    show_invoice_details(cliente, next_only)

@pagamenti_app.command("aggiorna")
def pagamenti_aggiorna(
    scadenza_id: int = typer.Argument(..., help="ID pagamento"),
    importo: Optional[float] = typer.Option(None, "--importo", "-i", help="Nuovo importo"),
    descrizione: Optional[str] = typer.Option(None, "--desc", "-d", help="Nuova descrizione"),
    ricorrenza: Optional[str] = typer.Option(None, "--ricorrenza", "-r", help="Nuova ricorrenza (mensile/bimestrale/trimestrale/semestrale/annuale/nessuna)"),
    data_scadenza: Optional[str] = typer.Option(None, "--data", help="Nuova data scadenza (YYYY-MM-DD)")
):
    """Aggiorna importo, descrizione, ricorrenza e/o data scadenza di un pagamento"""
    aggiorna_scadenza(scadenza_id, importo, descrizione, ricorrenza, data_scadenza)

@pagamenti_app.command("emessa")
def pagamenti_emessa(
    scadenza_id: int = typer.Argument(..., help="ID scadenza"),
    numero: str = typer.Argument(..., help="Numero documento"),
    data: Optional[str] = typer.Option(None, "--data", help="Data emissione (YYYY-MM-DD)")
):
    """Marca scadenza come emessa"""
    mark_as_issued(scadenza_id, numero, data)

@pagamenti_app.command("pagata")
def pagamenti_pagata(
    scadenza_id: int = typer.Argument(..., help="ID scadenza"),
    data: Optional[str] = typer.Option(None, "--data", help="Data pagamento (YYYY-MM-DD)")
):
    """Marca scadenza come pagata"""
    mark_as_paid(scadenza_id, data)

@pagamenti_app.command("process")
def pagamenti_process():
    """Processa scadenze ricorrenti"""
    process_recurring_invoices()

@pagamenti_app.command("delete")
def pagamenti_delete(
    pagamento_id: int = typer.Argument(..., help="ID del pagamento da eliminare")
):
    """
    Elimina un pagamento/fatturazione esistente
    
    Rimuove completamente un pagamento dal sistema dopo aver mostrato
    i dettagli e richiesto conferma. Operazione irreversibile.
    
    Per trovare l'ID del pagamento usa:
        clienti pagamenti list    # Lista tutti i pagamenti con ID
    
    Esempi:
        clienti pagamenti delete 15        # Elimina pagamento ID 15
        clienti pagamenti delete 23        # Elimina pagamento ID 23
    
    Attenzione: L'operazione è irreversibile. Viene mostrato un riepilogo
    del pagamento prima della conferma di eliminazione.
    """
    delete_scadenza(pagamento_id)

# Todo commands
@todo_app.command("add")
def todo_add():
    """Aggiungi nuovo todo"""
    add_todo()

@todo_app.command("list")
def todo_list(
    completati: bool = typer.Option(False, "--completati", help="Includi todos completati"),
    cliente: Optional[str] = typer.Option(None, "--cliente", help="Filtra per cliente"),
    priorita: Optional[str] = typer.Option(None, "--priorita", help="Filtra per priorità (alta/normale/bassa)"),
    overdue: bool = typer.Option(False, "--overdue", help="Solo todos in ritardo")
):
    """Lista todos con filtri"""
    list_todos(completati, cliente, priorita, overdue)

@todo_app.command("oggi")
def todo_today():
    """Todos con scadenza oggi"""
    show_today_todos()

@todo_app.command("settimana")
def todo_week():
    """Todos della settimana"""
    show_week_todos()

@todo_app.command("cliente")
def todo_client(cliente: str = typer.Argument(..., help="Nome cliente")):
    """Todos per cliente specifico"""
    show_client_todos(cliente)

@todo_app.command("done")
def todo_done(todo_id: int = typer.Argument(..., help="ID del todo da completare")):
    """Marca todo come completato"""
    mark_todo_done(todo_id)

@todo_app.command("edit")
def todo_edit(
    todo_id: int = typer.Argument(..., help="ID del todo"),
    priorita: Optional[str] = typer.Option(None, "--priorita", help="Nuova priorità (alta/normale/bassa)"),
    scadenza: Optional[str] = typer.Option(None, "--scadenza", help="Nuova scadenza (YYYY-MM-DD) o 'rimuovi'"),
    titolo: Optional[str] = typer.Option(None, "--titolo", help="Nuovo titolo")
):
    """Modifica proprietà todo"""
    edit_todo(todo_id, priorita, scadenza, titolo)

@todo_app.command("delete")
def todo_delete(todo_id: int = typer.Argument(..., help="ID del todo da eliminare")):
    """Elimina todo"""
    delete_todo(todo_id)

# Log/Interventi commands  
@interventi_app.command("add")
def log_add():
    """Registra nuovo intervento"""
    add_intervento()

@interventi_app.command("list")
def log_list(
    cliente: Optional[str] = typer.Option(None, "--cliente", help="Filtra per cliente"),
    tipo: Optional[str] = typer.Option(None, "--tipo", help="Filtra per tipo (call/email/meeting/lavoro/altro)"),
    oggi: bool = typer.Option(False, "--oggi", help="Solo interventi di oggi"),
    giorni: Optional[int] = typer.Option(None, "--giorni", help="Ultimi N giorni"),
    mese: Optional[int] = typer.Option(None, "--mese", help="Mese specifico (1-12)")
):
    """Lista interventi con filtri"""
    list_interventi(cliente, tipo, oggi, giorni, mese)

@interventi_app.command("oggi")
def log_today():
    """Riassunto attività di oggi"""
    show_today_summary()

@interventi_app.command("cliente")
def log_client(cliente: str = typer.Argument(..., help="Nome cliente")):
    """Timeline interventi per cliente"""
    show_client_timeline(cliente)

@interventi_app.command("export")
def log_export(
    output: Optional[str] = typer.Option(None, "--output", help="File di output"),
    cliente: Optional[str] = typer.Option(None, "--cliente", help="Filtra per cliente"),
    mese: Optional[int] = typer.Option(None, "--mese", help="Mese specifico (1-12)")
):
    """Export interventi in CSV"""
    export_interventi_csv(output, cliente, mese)

@interventi_app.command("fatturato")
def log_billed(intervento_id: int = typer.Argument(..., help="ID intervento")):
    """Marca intervento come fatturato"""
    mark_intervento_billed(intervento_id)

@interventi_app.command("edit")
def interventi_edit(intervento_id: int = typer.Argument(..., help="ID intervento")):
    """Modifica un intervento esistente"""
    edit_intervento(intervento_id)

@interventi_app.command("delete")
def interventi_delete(intervento_id: int = typer.Argument(..., help="ID intervento")):
    """Elimina un intervento"""
    delete_intervento(intervento_id)

@app.command("init")
def initialize_database():
    """Inizializza il database SQLite con tabelle e dati base"""
    console.print("🚀 Inizializzazione database...", style="blue")
    try:
        init_database()
        console.print("✅ Database inizializzato con successo!", style="green")
    except Exception as e:
        console.print(f"❌ Errore inizializzazione: {e}", style="red")
        raise typer.Exit(1)

@app.command("info")
def database_info():
    """Mostra informazioni sul database"""
    stats = get_database_info()
    
    if "error" in stats:
        console.print(f"❌ Errore: {stats['error']}", style="red")
        return
    
    table = Table(title="📊 Statistiche Database")
    table.add_column("Categoria", style="cyan")
    table.add_column("Valore", style="green")
    
    # Format file size
    size_mb = stats['database_size'] / (1024 * 1024) if stats['database_size'] > 0 else 0
    
    table.add_row("📄 File database", stats['database_path'])
    table.add_row("💾 Dimensione", f"{size_mb:.1f} MB")
    table.add_row("👥 Clienti totali", str(stats['clienti']))
    table.add_row("📞 Contatti", str(stats['contatti']))
    table.add_row("⏱️ Sessioni lavoro", str(stats['time_sessions']))
    table.add_row("✅ Todo aperti", str(stats['todos']))
    table.add_row("💰 Scadenze pending", str(stats['scadenze_pending']))
    table.add_row("📝 Interventi totali", str(stats['interventi']))
    
    console.print(table)

@app.command("version")
def show_version():
    """Mostra versione del sistema"""
    panel = Panel(
        "[bold blue]Clienti CRM v1.0.0[/bold blue]\n"
        "[dim]Sistema di gestione clienti per consulente digital marketing[/dim]\n\n"
        "🐍 Python 3.11+\n"
        "💾 SQLite database\n"  
        "🖥️ CLI-first interface",
        title="ℹ️ Informazioni Sistema",
        border_style="blue"
    )
    console.print(panel)

@app.command("dashboard") 
def show_dashboard():
    """Mostra dashboard avanzato con statistiche complete"""
    show_advanced_dashboard()

@app.command("stats")
def stats_command(
    year: Optional[int] = typer.Option(None, help="Anno di riferimento"),
    month: Optional[int] = typer.Option(None, help="Mese di riferimento (1-12)"),
    detailed: bool = typer.Option(False, "--detailed", help="Mostra dettagli per cliente")
):
    """Statistiche dettagliate per periodo"""
    show_stats_command(year, month, detailed)

@app.command("report")
def report_command(
    type: str = typer.Argument("month", help="Tipo report: month, year"),
    year: Optional[int] = typer.Option(None, help="Anno di riferimento")
):
    """Report mensili e annuali"""
    if type == "month":
        show_monthly_report(year)
    else:
        console.print("❌ Tipo report non supportato. Usa: month", style="red")

@app.command("alerts")
def alerts_command():
    """Mostra alert e promemoria importanti"""
    show_alerts()

# === EXPORT COMMANDS ===

@export_app.command("obsidian")
def export_obsidian(
    output: str = typer.Option(..., "--output", "-o", help="Directory output Obsidian vault"),
    include_completed: bool = typer.Option(False, "--completed", help="Includi todo completati")
):
    """Export completo per Obsidian vault"""
    if export_obsidian_vault(output, include_completed):
        console.print("🎉 Export Obsidian completato!", style="green")
    else:
        raise typer.Exit(1)

@export_app.command("client")
def export_single_client(
    cliente: str = typer.Argument(..., help="Nome cliente da esportare"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="File output (.md)")
):
    """Export singolo cliente in Markdown"""
    if export_cliente_markdown(cliente, output):
        console.print("✅ Cliente esportato con successo!", style="green")
    else:
        raise typer.Exit(1)

@export_app.command("csv")
def export_clients_csv(
    output: str = typer.Option("clienti_export.csv", "--output", "-o", help="File output CSV")
):
    """Export tutti i clienti in formato CSV"""
    if export_csv_clienti(output):
        console.print("📋 Export CSV completato!", style="green")
    else:
        raise typer.Exit(1)

@export_app.command("import-csv")
def import_clients_csv(
    input_file: str = typer.Argument(..., help="File CSV da importare"),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Simulazione import")
):
    """Import clienti da file CSV"""
    if import_csv_clienti(input_file, dry_run):
        if dry_run:
            console.print("🔍 Dry run completato - usa --no-dry-run per importare", style="blue")
        else:
            console.print("📥 Import completato!", style="green")
    else:
        raise typer.Exit(1)

# === BACKUP COMMANDS ===

@backup_app.command("create")
def backup_create():
    """Crea backup del database"""
    console.print("💾 Creazione backup database...", style="blue")
    backup_path = backup_database()
    if backup_path:
        cleanup_old_backups()
        console.print("✅ Backup completato!", style="green")
    else:
        raise typer.Exit(1)

@backup_app.command("list")
def backup_list():
    """Lista tutti i backup disponibili"""
    list_backups()

@backup_app.command("restore")
def backup_restore(
    backup_file: str = typer.Argument(..., help="File backup da ripristinare")
):
    """Ripristina database da backup"""
    # If only filename provided, look in backup directory
    if not backup_file.startswith('/'):
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "backups")
        backup_file = os.path.join(backup_dir, backup_file)
    
    if restore_backup(backup_file):
        console.print("✅ Ripristino completato!", style="green")
    else:
        raise typer.Exit(1)

@backup_app.command("cleanup")
def backup_cleanup(
    keep: int = typer.Option(10, "--keep", help="Numero di backup da mantenere")
):
    """Rimuovi backup vecchi"""
    console.print(f"🗑️  Pulizia backup (mantieni {keep})...", style="blue")
    cleanup_old_backups(keep)
    console.print("✅ Pulizia completata!", style="green")

@backup_app.command("auto")
def backup_auto():
    """Esegui backup automatico se necessario"""
    console.print("🤖 Controllo backup automatico...", style="blue")
    auto_backup_if_enabled()
    console.print("✅ Controllo completato!", style="green")

@app.command("import") 
def import_data(
    file_path: str = typer.Option(
        "/opt/progetti/languages/python/aiutofatture/clienti.json",
        "--from",
        help="Percorso del file JSON da importare"
    )
):
    """Importa clienti da file JSON esistente"""
    console.print(f"📥 Import clienti da: {file_path}", style="blue")
    
    if import_clienti_json(file_path):
        console.print("🎉 Import completato con successo!", style="green")
    else:
        console.print("💥 Import fallito", style="red")
        raise typer.Exit(1)

@app.command("backup")
def create_backup():
    """Crea backup del database (comando legacy)"""
    console.print("💾 Creazione backup database...", style="blue")
    console.print("ℹ️  Usa 'clienti backup create' per funzionalità avanzate", style="yellow")
    backup_path = backup_database()
    if backup_path:
        console.print("✅ Backup completato!", style="green")
    else:
        raise typer.Exit(1)

@app.command("serve")
def start_web_server(
    host: Optional[str] = typer.Option(None, help="Host del server (default da config.toml)"),
    port: Optional[int] = typer.Option(None, help="Porta del server (default da config.toml)"),
    reload: bool = typer.Option(False, help="Auto-reload per sviluppo")
):
    """Avvia il server web"""
    from core.config import get_config
    from core.logger import get_logger
    
    config = get_config()
    logger = get_logger()
    
    # Usa configurazione se non specificato
    actual_host = host or config.server.host
    actual_port = port or config.server.port
    
    logger.log_operation('WEB_SERVER_START', f'Starting server on {actual_host}:{actual_port}')
    console.print(f"🌐 Avvio server web su http://{actual_host}:{actual_port}", style="green")
    console.print(f"📋 Debug mode: {config.server.debug}", style="dim")
    
    try:
        import uvicorn
        from api import app as web_app
        uvicorn.run(web_app, host=actual_host, port=actual_port, reload=reload)
    except ImportError:
        logger.log_error('WEB_SERVER_START', ImportError("uvicorn not available"), "Missing dependency")
        console.print("❌ uvicorn non disponibile", style="red")
        raise typer.Exit(1)
    except Exception as e:
        logger.log_error('WEB_SERVER_START', e, f"Failed to start on {actual_host}:{actual_port}")
        console.print(f"❌ Errore avvio server: {e}", style="red")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()