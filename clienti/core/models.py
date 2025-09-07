"""
SQLAlchemy models for clienti CRM
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, REAL, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import json
from datetime import datetime

class Cliente(Base):
    __tablename__ = "clienti"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    piva = Column(String)
    cf = Column(String)
    indirizzo = Column(String)
    citta = Column(String)
    cap = Column(String)
    provincia = Column(String)
    stato = Column(String, default='attivo')  # attivo|prospect|pausa|archiviato
    tags = Column(Text)  # JSON array
    tariffa_oraria = Column(REAL, default=50.0)
    budget_mensile = Column(REAL)
    note = Column(Text)
    data_creazione = Column(DateTime, default=func.now())
    data_ultima_attivita = Column(DateTime)
    
    # Relationships
    contatti = relationship("Contatto", back_populates="cliente", cascade="all, delete-orphan")
    time_tracking = relationship("TimeTracking", back_populates="cliente", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="cliente")
    scadenze = relationship("ScadenzeFatturazione", back_populates="cliente", cascade="all, delete-orphan")
    interventi = relationship("Intervento", back_populates="cliente", cascade="all, delete-orphan")
    
    @property
    def tags_list(self):
        """Get tags as list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    @tags_list.setter 
    def tags_list(self, value):
        """Set tags from list"""
        if isinstance(value, list):
            self.tags = json.dumps(value)
        else:
            self.tags = None
    
    def add_tag(self, tag):
        """Add a tag"""
        tags = self.tags_list
        if tag not in tags:
            tags.append(tag)
            self.tags_list = tags
    
    def remove_tag(self, tag):
        """Remove a tag"""
        tags = self.tags_list
        if tag in tags:
            tags.remove(tag)
            self.tags_list = tags
    
    @property
    def indirizzo_completo(self):
        """Get complete address"""
        parts = [p for p in [self.indirizzo, f"{self.cap} {self.citta}".strip(), f"({self.provincia})"] if p and p.strip()]
        return " - ".join(parts) if parts else ""
    
    def __str__(self):
        return f"{self.nome} ({self.stato})"


class Contatto(Base):
    __tablename__ = "contatti"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clienti.id', ondelete='CASCADE'), nullable=False)
    nome = Column(String, nullable=False)
    ruolo = Column(String)
    email = Column(String)
    telefono = Column(String)
    principale = Column(Boolean, default=False)
    attivo = Column(Boolean, default=True)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="contatti")
    
    def __str__(self):
        return f"{self.nome} ({self.ruolo})" if self.ruolo else self.nome


class TimeTracking(Base):
    __tablename__ = "time_tracking"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clienti.id', ondelete='CASCADE'), nullable=False)
    inizio = Column(DateTime, nullable=False)
    fine = Column(DateTime)
    descrizione = Column(String)
    tariffa_oraria = Column(REAL)  # At time of tracking
    fatturato = Column(Boolean, default=False)
    note = Column(Text)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="time_tracking")
    
    @property
    def durata_ore(self):
        """Get duration in hours"""
        if self.fine and self.inizio:
            delta = self.fine - self.inizio
            return delta.total_seconds() / 3600
        return 0
    
    @property
    def compenso(self):
        """Get total compensation"""
        if self.tariffa_oraria and self.durata_ore:
            return self.durata_ore * self.tariffa_oraria
        return 0
    
    @property
    def is_active(self):
        """Check if tracking is active (no end time)"""
        return self.fine is None
    
    def __str__(self):
        status = "⏱️ Attivo" if self.is_active else f"✅ {self.durata_ore:.1f}h"
        return f"{self.cliente.nome}: {self.descrizione or 'Lavoro'} ({status})"


class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clienti.id', ondelete='SET NULL'))
    titolo = Column(String, nullable=False)
    descrizione = Column(Text)
    completato = Column(Boolean, default=False)
    priorita = Column(Integer, default=0)  # 1=alta, 0=normale, -1=bassa
    scadenza = Column(Date)
    data_creazione = Column(DateTime, default=func.now())
    data_completamento = Column(DateTime)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="todos")
    
    @property
    def priorita_text(self):
        """Get priority as text"""
        if self.priorita == 1:
            return "🔴 Alta"
        elif self.priorita == -1:
            return "🟢 Bassa"
        return "🟡 Normale"
    
    @property
    def is_overdue(self):
        """Check if todo is overdue"""
        if self.scadenza and not self.completato:
            return self.scadenza < datetime.now().date()
        return False
    
    def __str__(self):
        status = "✅" if self.completato else ("🔴" if self.is_overdue else "⏳")
        cliente = f" ({self.cliente.nome})" if self.cliente else ""
        return f"{status} {self.titolo}{cliente}"


class ScadenzeFatturazione(Base):
    __tablename__ = "scadenze_fatturazione"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clienti.id', ondelete='CASCADE'), nullable=False)
    tipo = Column(String, nullable=False)  # 'fattura' o 'parcella'
    data_scadenza = Column(Date, nullable=False)
    importo_previsto = Column(REAL)
    descrizione = Column(String)
    ricorrenza = Column(String)  # mensile|bimestrale|trimestrale|semestrale|annuale|custom
    giorni_ricorrenza = Column(Integer)  # For custom recurrence
    importo_fisso = Column(Boolean, default=True)  # True=fixed amount, False=variable amount
    emessa = Column(Boolean, default=False)
    data_emissione = Column(Date)
    numero_documento = Column(String)
    pagata = Column(Boolean, default=False)
    data_pagamento = Column(Date)
    note = Column(Text)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="scadenze")
    
    @property
    def is_overdue(self):
        """Check if invoice/bill is overdue"""
        if not self.emessa:
            return self.data_scadenza < datetime.now().date()
        return False
    
    @property
    def tipo_icon(self):
        """Get icon for document type"""
        return "💰" if self.tipo == "fattura" else "📋"
    
    def __str__(self):
        status = "✅" if self.emessa else ("🔴" if self.is_overdue else "⏳")
        
        # Handle variable amounts
        if not self.importo_fisso and (self.importo_previsto is None or self.importo_previsto == 0):
            amount_str = "DA DEFINIRE"
        else:
            amount_str = f"€{self.importo_previsto or 0:.0f}"
            
        return f"{status} {self.tipo_icon} {self.cliente.nome}: {self.descrizione or self.tipo} - {amount_str}"


class Intervento(Base):
    __tablename__ = "interventi"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clienti.id', ondelete='CASCADE'), nullable=False)
    data = Column(DateTime, default=func.now())
    tipo = Column(String, nullable=False)  # call|email|meeting|lavoro|altro
    titolo = Column(String, nullable=False)
    descrizione = Column(Text)
    durata_minuti = Column(Integer)
    costo = Column(REAL)  # If billable
    fatturato = Column(Boolean, default=False)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="interventi")
    
    @property
    def tipo_icon(self):
        """Get icon for intervention type"""
        icons = {
            'call': '📞',
            'email': '📧', 
            'meeting': '🤝',
            'lavoro': '💻',
            'altro': '📝'
        }
        return icons.get(self.tipo, '📝')
    
    @property
    def durata_ore(self):
        """Get duration in hours"""
        return self.durata_minuti / 60 if self.durata_minuti else 0
    
    def __str__(self):
        durata = f" ({self.durata_minuti}min)" if self.durata_minuti else ""
        return f"{self.tipo_icon} {self.titolo}{durata} - {self.cliente.nome}"


class Configurazione(Base):
    __tablename__ = "configurazione"
    
    chiave = Column(String, primary_key=True)
    valore = Column(Text)
    descrizione = Column(Text)
    
    def get_json(self):
        """Get value as JSON"""
        try:
            return json.loads(self.valore) if self.valore else None
        except:
            return self.valore
    
    def set_json(self, value):
        """Set value as JSON"""
        if isinstance(value, (dict, list)):
            self.valore = json.dumps(value)
        else:
            self.valore = str(value)
    
    def __str__(self):
        return f"{self.chiave}: {self.valore}"