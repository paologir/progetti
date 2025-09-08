"""
Database connection and session management for clienti CRM
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import sqlite3

from .config import get_config
from .logger import get_logger

# Get configuration
config = get_config()
logger = get_logger()

# Database configuration from config.toml
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), config.database.path)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # For SQLite
        "timeout": config.database.timeout
    },
    echo=config.database.echo  # Echo from configuration
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enable foreign keys and UTF-8 in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA encoding='UTF-8'")
        cursor.close()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def init_database():
    """Initialize database with tables and basic data"""
    logger.log_operation('DB_INIT_START', 'Initializing database')
    
    create_tables()
    
    # Add basic configuration
    db = SessionLocal()
    try:
        from .models import Configurazione
        
        # Check if already initialized
        existing_config = db.query(Configurazione).filter_by(chiave="initialized").first()
        if existing_config:
            logger.log_operation('DB_INIT_SKIP', 'Database already initialized')
            return
        
        # Add default configuration - now sourced from config.toml
        default_configs = [
            Configurazione(chiave="initialized", valore="true", descrizione="Database initialized flag"),
            Configurazione(chiave="tariffa_oraria_default", valore=str(config.business.default_hourly_rate), descrizione="Default hourly rate"),
            Configurazione(chiave="backup_auto", valore=str(config.backup.auto_enabled).lower(), descrizione="Enable automatic backups"),
            Configurazione(chiave="export_obsidian_path", valore=config.export.obsidian_default_path, descrizione="Path for Obsidian exports")
        ]
        
        for db_config in default_configs:
            db.add(db_config)
        
        db.commit()
        logger.log_operation('DB_INIT_COMPLETE', f'Added {len(default_configs)} default configurations')
        print("✅ Database initialized successfully")
        
    except Exception as e:
        error_msg = f"Error initializing database: {e}"
        logger.log_error('DB_INIT', e, 'Failed to initialize database')
        print(f"❌ {error_msg}")
        db.rollback()
    finally:
        db.close()

def get_database_info():
    """Get database statistics"""
    db = SessionLocal()
    try:
        from .models import Cliente, Contatto, TimeTracking, Todo, ScadenzeFatturazione, Intervento
        
        stats = {
            "database_path": DATABASE_PATH,
            "database_size": os.path.getsize(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else 0,
            "clienti": db.query(Cliente).count(),
            "contatti": db.query(Contatto).count(), 
            "time_sessions": db.query(TimeTracking).count(),
            "todos": db.query(Todo).filter_by(completato=False).count(),
            "scadenze_pending": db.query(ScadenzeFatturazione).filter_by(emessa=False).count(),
            "interventi": db.query(Intervento).count()
        }
        return stats
    except Exception as e:
        print(f"Error getting database info: {e}")
        return {"error": str(e)}
    finally:
        db.close()