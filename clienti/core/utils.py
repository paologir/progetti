"""
Utility functions for clienti CRM
"""
import json
import os
from typing import Dict, List, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime, timedelta
import shutil

from .database import SessionLocal
from .models import Cliente, Contatto

console = Console()

def import_clienti_json(file_path: str) -> bool:
    """
    Import clienti from existing JSON file (aiutofatture format)
    """
    if not os.path.exists(file_path):
        console.print(f"❌ File non trovato: {file_path}", style="red")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        clienti_data = data.get('clienti', [])
        if not clienti_data:
            console.print("❌ Nessun cliente trovato nel file JSON", style="red")
            return False
        
        db = SessionLocal()
        imported = 0
        skipped = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Import clienti in corso...", total=len(clienti_data))
            
            for cliente_json in clienti_data:
                progress.update(task, advance=1)
                
                nome = cliente_json.get('Cliente', '').strip()
                if not nome:
                    skipped += 1
                    continue
                
                # Check if client already exists
                existing = db.query(Cliente).filter_by(nome=nome).first()
                if existing:
                    console.print(f"⏭️  Cliente '{nome}' già presente, salto...", style="yellow")
                    skipped += 1
                    continue
                
                # Create new client
                cliente = Cliente(
                    nome=nome,
                    piva=cliente_json.get('PIVA', '').strip() or None,
                    cf=cliente_json.get('CF', '').strip() or None,
                    indirizzo=cliente_json.get('Indirizzo', '').strip() or None,
                    citta=cliente_json.get('Città', '').strip() or None,
                    cap=cliente_json.get('CAP', '').strip() or None,
                    provincia=cliente_json.get('Provincia', '').strip() or None,
                    stato='attivo',  # Default status for imported clients
                    tariffa_oraria=50.0  # Default rate
                )
                
                db.add(cliente)
                db.flush()  # Get the ID
                
                # Create a default contact if we have enough info
                if nome and (cliente.piva or cliente.cf):
                    contatto = Contatto(
                        cliente_id=cliente.id,
                        nome=nome,  # Use client name as contact name
                        ruolo="Titolare",
                        principale=True,
                        attivo=True
                    )
                    db.add(contatto)
                
                imported += 1
        
        try:
            db.commit()
            console.print(f"✅ Import completato: {imported} clienti importati, {skipped} saltati", style="green")
            return True
        except Exception as e:
            db.rollback()
            console.print(f"❌ Errore durante il salvataggio: {e}", style="red")
            return False
        
    except json.JSONDecodeError as e:
        console.print(f"❌ Errore parsing JSON: {e}", style="red")
        return False
    except Exception as e:
        console.print(f"❌ Errore durante l'import: {e}", style="red")
        return False
    finally:
        db.close()

def backup_database(backup_path: str = None) -> str:
    """
    Create a backup of the database
    """
    if not backup_path:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"clienti_backup_{timestamp}.db")
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
    
    if not os.path.exists(db_path):
        console.print("❌ Database non trovato", style="red")
        return ""
    
    try:
        shutil.copy2(db_path, backup_path)
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        console.print(f"✅ Backup creato: {backup_path} ({size_mb:.1f} MB)", style="green")
        return backup_path
    except Exception as e:
        console.print(f"❌ Errore creazione backup: {e}", style="red")
        return ""

def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    db = SessionLocal()
    try:
        from .models import Configurazione
        config = db.query(Configurazione).filter_by(chiave=key).first()
        if config:
            return config.get_json()
        return default
    except:
        return default
    finally:
        db.close()

def set_config_value(key: str, value: Any, description: str = "") -> bool:
    """Set configuration value"""
    db = SessionLocal()
    try:
        from .models import Configurazione
        config = db.query(Configurazione).filter_by(chiave=key).first()
        
        if config:
            config.set_json(value)
            if description:
                config.descrizione = description
        else:
            config = Configurazione(chiave=key, descrizione=description)
            config.set_json(value)
            db.add(config)
        
        db.commit()
        return True
    except Exception as e:
        console.print(f"❌ Errore salvataggio configurazione: {e}", style="red")
        db.rollback()
        return False
    finally:
        db.close()

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"€{amount:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def format_duration(hours: float) -> str:
    """Format hours as duration"""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}min"
    else:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h}h {m}min" if m > 0 else f"{h}h"

def get_status_icon(status: str) -> str:
    """Get icon for status"""
    icons = {
        'attivo': '🟢',
        'prospect': '🟡', 
        'pausa': '🟠',
        'archiviato': '⚫'
    }
    return icons.get(status, '❓')

def clean_phone(phone: str) -> str:
    """Clean and format phone number"""
    if not phone:
        return ""
    
    # Remove all non-digits except +
    clean = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Italian mobile format
    if clean.startswith('39') and len(clean) == 12:
        return f"+{clean[:2]} {clean[2:5]} {clean[5:8]} {clean[8:]}"
    elif clean.startswith('+39') and len(clean) == 13:
        return f"{clean[:3]} {clean[3:6]} {clean[6:9]} {clean[9:]}"
    elif len(clean) == 10 and clean.startswith('3'):
        return f"+39 {clean[:3]} {clean[3:6]} {clean[6:]}"
    
    return clean

def validate_piva(piva: str) -> bool:
    """Validate Italian P.IVA (basic check)"""
    if not piva:
        return True  # Optional field
    
    # Remove spaces and convert to uppercase
    piva = piva.replace(' ', '').upper()
    
    # Italian P.IVA: 11 digits
    if len(piva) == 11 and piva.isdigit():
        return True
    
    # EU P.IVA format (basic)
    if len(piva) > 4 and piva[:2].isalpha():
        return True
    
    return False

def search_clients(query: str, limit: int = 10) -> List[Cliente]:
    """Search clients by name, city, or tags"""
    db = SessionLocal()
    try:
        # Search in multiple fields
        clients = db.query(Cliente).filter(
            Cliente.nome.ilike(f'%{query}%') |
            Cliente.citta.ilike(f'%{query}%') |
            Cliente.tags.ilike(f'%{query}%')
        ).limit(limit).all()
        
        return clients
    except:
        return []
    finally:
        db.close()