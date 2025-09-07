"""
Database connection and session management for clienti CRM
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import sqlite3

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # For SQLite
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enable foreign keys in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
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
    create_tables()
    
    # Add basic configuration
    db = SessionLocal()
    try:
        from .models import Configurazione
        
        # Check if already initialized
        existing_config = db.query(Configurazione).filter_by(chiave="initialized").first()
        if existing_config:
            return
        
        # Add default configuration
        default_configs = [
            Configurazione(chiave="initialized", valore="true", descrizione="Database initialized flag"),
            Configurazione(chiave="tariffa_oraria_default", valore="50.0", descrizione="Default hourly rate"),
            Configurazione(chiave="backup_auto", valore="true", descrizione="Enable automatic backups"),
            Configurazione(chiave="export_obsidian_path", valore="", descrizione="Path for Obsidian exports")
        ]
        
        for config in default_configs:
            db.add(config)
        
        db.commit()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
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