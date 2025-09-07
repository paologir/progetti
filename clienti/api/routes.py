"""
FastAPI routes for web interface
"""
from fastapi import Request, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, date, timedelta
import json

from . import app, templates
from core.database import get_db
from core.models import Cliente, TimeTracking, Todo, ScadenzeFatturazione, Intervento


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard principale web"""
    
    # Statistiche principali
    clienti_count = db.query(Cliente).filter(Cliente.stato == 'attivo').count()
    clienti_total = db.query(Cliente).count()
    
    # Timer attivo
    timer_attivo = db.query(TimeTracking).filter(TimeTracking.fine == None).first()
    
    # Todo oggi e overdue
    today = date.today()
    todos_oggi = db.query(Todo).filter(
        and_(Todo.scadenza == today, Todo.completato == False)
    ).count()
    
    todos_overdue = db.query(Todo).filter(
        and_(Todo.scadenza < today, Todo.completato == False)
    ).count()
    
    # Scadenze prossime (7 giorni)
    prossime_7_giorni = today + timedelta(days=7)
    scadenze_prossime = db.query(ScadenzeFatturazione).filter(
        and_(
            ScadenzeFatturazione.data_scadenza <= prossime_7_giorni,
            ScadenzeFatturazione.emessa == False
        )
    ).join(Cliente).all()
    
    # Interventi oggi
    oggi_start = datetime.combine(today, datetime.min.time())
    oggi_end = datetime.combine(today, datetime.max.time())
    
    interventi_oggi = db.query(Intervento).filter(
        and_(
            Intervento.data >= oggi_start,
            Intervento.data <= oggi_end
        )
    ).join(Cliente).all()
    
    # Ore mese corrente
    mese_start = today.replace(day=1)
    ore_mese = db.query(func.sum(
        (func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24
    )).filter(
        and_(
            TimeTracking.fine != None,
            func.date(TimeTracking.inizio) >= mese_start
        )
    ).scalar() or 0
    
    # Fatturato mese (approssimato)
    fatturato_mese = ore_mese * 50  # Tariffa media
    
    context = {
        "request": request,
        "clienti_count": clienti_count,
        "clienti_total": clienti_total,
        "timer_attivo": timer_attivo,
        "todos_oggi": todos_oggi,
        "todos_overdue": todos_overdue,
        "scadenze_prossime": scadenze_prossime,
        "interventi_oggi": interventi_oggi,
        "ore_mese": round(ore_mese, 1),
        "fatturato_mese": round(fatturato_mese, 0),
        "today": today,
    }
    
    return templates.TemplateResponse("dashboard.html", context)


@app.get("/clienti", response_class=HTMLResponse)
async def clienti_list(request: Request, search: str = "", stato: str = "attivo", db: Session = Depends(get_db)):
    """Lista clienti con ricerca e filtri"""
    
    query = db.query(Cliente)
    
    # Filtri
    if stato and stato != "tutti":
        query = query.filter(Cliente.stato == stato)
    
    if search:
        query = query.filter(Cliente.nome.ilike(f"%{search}%"))
    
    clienti = query.order_by(Cliente.nome).all()
    
    context = {
        "request": request,
        "clienti": clienti,
        "search": search,
        "stato": stato,
    }
    
    return templates.TemplateResponse("clienti/list.html", context)


@app.get("/clienti/{cliente_id}", response_class=HTMLResponse)
async def cliente_detail(request: Request, cliente_id: int, db: Session = Depends(get_db)):
    """Dettaglio cliente"""
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    
    # Ultimi interventi
    interventi = db.query(Intervento).filter(
        Intervento.cliente_id == cliente_id
    ).order_by(desc(Intervento.data)).limit(10).all()
    
    # Todo aperti
    todos = db.query(Todo).filter(
        and_(Todo.cliente_id == cliente_id, Todo.completato == False)
    ).order_by(Todo.scadenza.asc()).all()
    
    # Ore totali e non fatturate
    ore_totali = db.query(func.sum(
        (func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24
    )).filter(
        and_(TimeTracking.cliente_id == cliente_id, TimeTracking.fine != None)
    ).scalar() or 0
    
    ore_non_fatturate = db.query(func.sum(
        (func.julianday(TimeTracking.fine) - func.julianday(TimeTracking.inizio)) * 24
    )).filter(
        and_(
            TimeTracking.cliente_id == cliente_id,
            TimeTracking.fine != None,
            TimeTracking.fatturato == False
        )
    ).scalar() or 0
    
    context = {
        "request": request,
        "cliente": cliente,
        "interventi": interventi,
        "todos": todos,
        "ore_totali": round(ore_totali, 1),
        "ore_non_fatturate": round(ore_non_fatturate, 1),
        "compenso_non_fatturato": round(ore_non_fatturate * cliente.tariffa_oraria, 0),
    }
    
    return templates.TemplateResponse("clienti/detail.html", context)


@app.get("/timer", response_class=HTMLResponse)
async def timer_page(request: Request, db: Session = Depends(get_db)):
    """Pagina timer web"""
    
    # Timer attivo
    timer_attivo = db.query(TimeTracking).filter(TimeTracking.fine == None).first()
    
    # Clienti attivi per dropdown
    clienti = db.query(Cliente).filter(Cliente.stato == 'attivo').order_by(Cliente.nome).all()
    
    # Sessioni recenti (ultimi 7 giorni)
    week_ago = datetime.now() - timedelta(days=7)
    sessioni_recenti = db.query(TimeTracking).filter(
        and_(
            TimeTracking.inizio >= week_ago,
            TimeTracking.fine != None
        )
    ).join(Cliente).order_by(desc(TimeTracking.inizio)).limit(20).all()
    
    context = {
        "request": request,
        "timer_attivo": timer_attivo,
        "clienti": clienti,
        "sessioni_recenti": sessioni_recenti,
    }
    
    return templates.TemplateResponse("timer.html", context)


@app.post("/timer/start")
async def timer_start(
    cliente_id: int = Form(...),
    descrizione: str = Form(""),
    db: Session = Depends(get_db)
):
    """Avvia timer"""
    
    # Verifica che non ci sia già un timer attivo
    timer_esistente = db.query(TimeTracking).filter(TimeTracking.fine == None).first()
    if timer_esistente:
        raise HTTPException(status_code=400, detail="Timer già attivo")
    
    # Prendi cliente e tariffa
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    
    # Crea nuovo timer
    timer = TimeTracking(
        cliente_id=cliente_id,
        inizio=datetime.now(),
        descrizione=descrizione or "Lavoro",
        tariffa_oraria=cliente.tariffa_oraria
    )
    
    db.add(timer)
    db.commit()
    
    return RedirectResponse(url="/timer", status_code=303)


@app.post("/timer/stop")
async def timer_stop(db: Session = Depends(get_db)):
    """Ferma timer attivo"""
    
    timer = db.query(TimeTracking).filter(TimeTracking.fine == None).first()
    if not timer:
        raise HTTPException(status_code=404, detail="Nessun timer attivo")
    
    timer.fine = datetime.now()
    db.commit()
    
    return RedirectResponse(url="/timer", status_code=303)


@app.get("/api/timer/status")
async def timer_status_api(db: Session = Depends(get_db)):
    """API per stato timer (per aggiornamenti HTMX)"""
    
    timer = db.query(TimeTracking).filter(TimeTracking.fine == None).first()
    
    if timer:
        durata_secondi = (datetime.now() - timer.inizio).total_seconds()
        ore = int(durata_secondi // 3600)
        minuti = int((durata_secondi % 3600) // 60)
        secondi = int(durata_secondi % 60)
        
        return {
            "attivo": True,
            "cliente": timer.cliente.nome,
            "descrizione": timer.descrizione,
            "durata": f"{ore:02d}:{minuti:02d}:{secondi:02d}",
            "compenso": round((durata_secondi / 3600) * timer.tariffa_oraria, 2)
        }
    
    return {"attivo": False}


@app.get("/todos", response_class=HTMLResponse)
async def todos_page(request: Request, db: Session = Depends(get_db)):
    """Pagina gestione todos"""
    
    # Todo aperti ordinati per scadenza
    todos = db.query(Todo).filter(Todo.completato == False).order_by(
        Todo.scadenza.asc()
    ).all()
    
    # Clienti per dropdown
    clienti = db.query(Cliente).filter(Cliente.stato == 'attivo').order_by(Cliente.nome).all()
    
    context = {
        "request": request,
        "todos": todos,
        "clienti": clienti,
        "today": date.today(),
    }
    
    return templates.TemplateResponse("todos.html", context)


@app.post("/todos/add")
async def todo_add(
    titolo: str = Form(...),
    descrizione: str = Form(""),
    cliente_id: int = Form(None),
    priorita: int = Form(0),
    scadenza: str = Form(""),
    db: Session = Depends(get_db)
):
    """Aggiungi nuovo todo"""
    
    scadenza_date = None
    if scadenza:
        try:
            scadenza_date = datetime.strptime(scadenza, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    todo = Todo(
        titolo=titolo,
        descrizione=descrizione or None,
        cliente_id=cliente_id if cliente_id else None,
        priorita=priorita,
        scadenza=scadenza_date
    )
    
    db.add(todo)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)


@app.post("/todos/{todo_id}/complete")
async def todo_complete(todo_id: int, db: Session = Depends(get_db)):
    """Completa todo"""
    
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo non trovato")
    
    todo.completato = True
    todo.data_completamento = datetime.now()
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)