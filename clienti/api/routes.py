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


# CLIENT EDIT/DELETE ROUTES

@app.post("/clienti/{cliente_id}/edit")
async def cliente_edit(
    cliente_id: int,
    nome: str = Form(...),
    indirizzo: str = Form(""),
    note: str = Form(""),
    stato: str = Form(...),
    db: Session = Depends(get_db)
):
    """Modifica cliente"""
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    
    # Update cliente fields
    cliente.nome = nome
    cliente.indirizzo = indirizzo if indirizzo else None
    cliente.note = note if note else None
    cliente.stato = stato
    
    db.commit()
    
    return RedirectResponse(url="/clienti", status_code=303)


@app.post("/clienti/{cliente_id}/delete")
async def cliente_delete(cliente_id: int, db: Session = Depends(get_db)):
    """Elimina cliente"""
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente non trovato")
    
    # Le foreign key constraints si occupano di eliminare a cascata
    # gli elementi collegati (interventi, todo, pagamenti)
    db.delete(cliente)
    db.commit()
    
    return RedirectResponse(url="/clienti", status_code=303)


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


@app.post("/timer/{session_id}/edit")
async def timer_session_edit(
    session_id: int,
    descrizione: str = Form(""),
    tariffa_oraria: float = Form(...),
    note: str = Form(""),
    fatturato: str = Form(...),
    db: Session = Depends(get_db)
):
    """Modifica sessione di time tracking"""
    
    session = db.query(TimeTracking).filter(TimeTracking.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    
    if session.fine is None:
        raise HTTPException(status_code=400, detail="Non puoi modificare una sessione attiva")
    
    # Update session fields
    session.descrizione = descrizione if descrizione else None
    session.tariffa_oraria = tariffa_oraria
    session.note = note if note else None
    session.fatturato = (fatturato == "true")
    
    db.commit()
    
    return RedirectResponse(url="/timer", status_code=303)


@app.post("/timer/{session_id}/delete")
async def timer_session_delete(session_id: int, db: Session = Depends(get_db)):
    """Elimina sessione di time tracking"""
    
    session = db.query(TimeTracking).filter(TimeTracking.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessione non trovata")
    
    if session.fine is None:
        raise HTTPException(status_code=400, detail="Non puoi eliminare una sessione attiva")
    
    db.delete(session)
    db.commit()
    
    return RedirectResponse(url="/timer", status_code=303)


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


@app.post("/todos/{todo_id}/edit")
async def todo_edit(
    todo_id: int,
    titolo: str = Form(...),
    descrizione: str = Form(""),
    cliente_id: int = Form(None),
    priorita: int = Form(0),
    scadenza: str = Form(""),
    db: Session = Depends(get_db)
):
    """Modifica todo"""
    
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo non trovato")
    
    scadenza_date = None
    if scadenza:
        try:
            scadenza_date = datetime.strptime(scadenza, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    # Update todo fields
    todo.titolo = titolo
    todo.descrizione = descrizione or None
    todo.cliente_id = cliente_id if cliente_id else None
    todo.priorita = priorita
    todo.scadenza = scadenza_date
    
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)


@app.post("/todos/{todo_id}/delete")
async def todo_delete(todo_id: int, db: Session = Depends(get_db)):
    """Elimina todo"""
    
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo non trovato")
    
    db.delete(todo)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)


# PAGAMENTI ROUTES

@app.get("/pagamenti", response_class=HTMLResponse)
async def pagamenti_list(request: Request, db: Session = Depends(get_db)):
    """Lista pagamenti con filtri"""
    
    today = date.today()
    
    # Tutti i pagamenti ordinati per scadenza
    pagamenti = db.query(ScadenzeFatturazione).join(Cliente).order_by(
        ScadenzeFatturazione.data_scadenza.desc()
    ).all()
    
    # Statistiche
    scadute = db.query(ScadenzeFatturazione).filter(
        and_(
            ScadenzeFatturazione.data_scadenza < today,
            ScadenzeFatturazione.emessa == False
        )
    ).count()
    
    prossime = db.query(ScadenzeFatturazione).filter(
        and_(
            ScadenzeFatturazione.data_scadenza >= today,
            ScadenzeFatturazione.data_scadenza <= today + timedelta(days=7),
            ScadenzeFatturazione.emessa == False
        )
    ).count()
    
    emesse = db.query(ScadenzeFatturazione).filter(
        ScadenzeFatturazione.emessa == True
    ).count()
    
    # Lista clienti per form
    clienti = db.query(Cliente).filter(Cliente.stato == 'attivo').order_by(Cliente.nome).all()
    
    # La proprietà is_overdue è già disponibile nel model ScadenzeFatturazione
    
    context = {
        "request": request,
        "pagamenti": pagamenti,
        "clienti": clienti,
        "scadute_count": scadute,
        "prossime_count": prossime,
        "emesse_count": emesse,
        "totali_count": len(pagamenti),
        "today": today,
    }
    
    return templates.TemplateResponse("pagamenti.html", context)


@app.post("/pagamenti/add")
async def pagamento_add(
    cliente_id: int = Form(...),
    tipo: str = Form(...),
    data_scadenza: str = Form(...),
    importo_previsto: float = Form(None),
    ricorrenza: str = Form(""),
    importo_variabile: bool = Form(False),
    descrizione: str = Form(""),
    db: Session = Depends(get_db)
):
    """Aggiungi nuovo pagamento"""
    
    try:
        scadenza_date = datetime.strptime(data_scadenza, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato data non valido")
    
    pagamento = ScadenzeFatturazione(
        cliente_id=cliente_id,
        tipo=tipo,
        data_scadenza=scadenza_date,
        importo_previsto=importo_previsto if importo_previsto else None,
        ricorrenza=ricorrenza if ricorrenza else None,
        importo_fisso=not importo_variabile,
        descrizione=descrizione or None
    )
    
    db.add(pagamento)
    db.commit()
    
    return RedirectResponse(url="/pagamenti", status_code=303)


@app.post("/pagamenti/{pagamento_id}/emessa")
async def pagamento_emessa(pagamento_id: int, db: Session = Depends(get_db)):
    """Marca pagamento come emesso"""
    
    pagamento = db.query(ScadenzeFatturazione).filter(ScadenzeFatturazione.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    
    pagamento.emessa = True
    pagamento.data_emissione = date.today()
    pagamento.numero_documento = f"DOC-{pagamento_id}-{date.today().strftime('%Y%m%d')}"
    
    db.commit()
    
    return RedirectResponse(url="/pagamenti", status_code=303)


@app.post("/pagamenti/{pagamento_id}/pagata")  
async def pagamento_pagata(pagamento_id: int, db: Session = Depends(get_db)):
    """Marca pagamento come pagato"""
    
    pagamento = db.query(ScadenzeFatturazione).filter(ScadenzeFatturazione.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    
    pagamento.pagato = True
    pagamento.data_pagamento = date.today()
    
    db.commit()
    
    return RedirectResponse(url="/pagamenti", status_code=303)


@app.get("/pagamenti/{pagamento_id}/edit")
async def pagamento_edit_redirect(pagamento_id: int):
    """Redirect GET requests to payments list"""
    return RedirectResponse(url="/pagamenti", status_code=303)


@app.post("/pagamenti/{pagamento_id}/edit")
async def pagamento_edit(
    pagamento_id: int,
    cliente_id: int = Form(...),
    tipo: str = Form(...),
    data_scadenza: str = Form(...),
    importo_previsto: float = Form(None),
    ricorrenza: str = Form(""),
    importo_variabile: bool = Form(False),
    descrizione: str = Form(""),
    db: Session = Depends(get_db)
):
    """Modifica pagamento"""
    
    pagamento = db.query(ScadenzeFatturazione).filter(ScadenzeFatturazione.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    
    try:
        scadenza_date = datetime.strptime(data_scadenza, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato data non valido")
    
    # Update payment fields
    pagamento.cliente_id = cliente_id
    pagamento.tipo = tipo
    pagamento.data_scadenza = scadenza_date
    pagamento.importo_previsto = importo_previsto if importo_previsto else None
    pagamento.ricorrenza = ricorrenza if ricorrenza else None
    pagamento.importo_fisso = not importo_variabile
    pagamento.descrizione = descrizione or None
    
    db.commit()
    
    return RedirectResponse(url="/pagamenti", status_code=303)


@app.post("/pagamenti/{pagamento_id}/delete")
async def pagamento_delete(pagamento_id: int, db: Session = Depends(get_db)):
    """Elimina pagamento"""
    
    pagamento = db.query(ScadenzeFatturazione).filter(ScadenzeFatturazione.id == pagamento_id).first()
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    
    db.delete(pagamento)
    db.commit()
    
    return RedirectResponse(url="/pagamenti", status_code=303)


# INTERVENTI ROUTES

@app.get("/interventi", response_class=HTMLResponse)
async def interventi_list(request: Request, db: Session = Depends(get_db)):
    """Lista interventi"""
    
    # Tutti gli interventi ordinati per data (più recenti primi)
    interventi = db.query(Intervento).join(Cliente).order_by(
        desc(Intervento.data)
    ).limit(50).all()  # Limitiamo a 50 per performance
    
    # Clienti attivi per filtri
    clienti = db.query(Cliente).filter(Cliente.stato == 'attivo').order_by(Cliente.nome).all()
    
    # Statistiche
    oggi = date.today()
    oggi_start = datetime.combine(oggi, datetime.min.time())
    oggi_end = datetime.combine(oggi, datetime.max.time())
    
    interventi_oggi = db.query(Intervento).filter(
        and_(
            Intervento.data >= oggi_start,
            Intervento.data <= oggi_end
        )
    ).count()
    
    # Totale ore e valore del mese
    mese_start = oggi.replace(day=1)
    mese_start_dt = datetime.combine(mese_start, datetime.min.time())
    
    interventi_mese = db.query(Intervento).filter(
        Intervento.data >= mese_start_dt
    ).all()
    
    ore_mese = sum(i.durata_ore for i in interventi_mese if i.durata_minuti)
    valore_mese = sum(i.costo for i in interventi_mese if i.costo)
    
    context = {
        "request": request,
        "interventi": interventi,
        "clienti": clienti,
        "interventi_oggi": interventi_oggi,
        "ore_mese": round(ore_mese, 1),
        "valore_mese": round(valore_mese, 2),
        "today": oggi
    }
    
    return templates.TemplateResponse("interventi.html", context)


@app.post("/interventi/add")
async def intervento_add(
    cliente_id: int = Form(...),
    tipo: str = Form(...),
    titolo: str = Form(...),
    descrizione: str = Form(""),
    durata_minuti: int = Form(None),
    costo: float = Form(None),
    db: Session = Depends(get_db)
):
    """Aggiungi nuovo intervento"""
    
    intervento = Intervento(
        cliente_id=cliente_id,
        tipo=tipo,
        titolo=titolo,
        descrizione=descrizione if descrizione else None,
        durata_minuti=durata_minuti if durata_minuti else None,
        costo=costo if costo else None
    )
    
    db.add(intervento)
    db.commit()
    
    return RedirectResponse(url="/interventi", status_code=303)


@app.post("/interventi/{intervento_id}/edit")
async def intervento_edit(
    intervento_id: int,
    cliente_id: int = Form(...),
    tipo: str = Form(...),
    titolo: str = Form(...),
    descrizione: str = Form(""),
    durata_minuti: int = Form(None),
    costo: float = Form(None),
    db: Session = Depends(get_db)
):
    """Modifica intervento"""
    
    intervento = db.query(Intervento).filter(Intervento.id == intervento_id).first()
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")
    
    # Update intervento fields
    intervento.cliente_id = cliente_id
    intervento.tipo = tipo
    intervento.titolo = titolo
    intervento.descrizione = descrizione if descrizione else None
    intervento.durata_minuti = durata_minuti if durata_minuti else None
    intervento.costo = costo if costo else None
    
    db.commit()
    
    return RedirectResponse(url="/interventi", status_code=303)


@app.post("/interventi/{intervento_id}/delete")
async def intervento_delete(intervento_id: int, db: Session = Depends(get_db)):
    """Elimina intervento"""
    
    intervento = db.query(Intervento).filter(Intervento.id == intervento_id).first()
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")
    
    db.delete(intervento)
    db.commit()
    
    return RedirectResponse(url="/interventi", status_code=303)


@app.post("/interventi/{intervento_id}/fatturato")
async def intervento_fatturato(intervento_id: int, db: Session = Depends(get_db)):
    """Marca intervento come fatturato"""
    
    intervento = db.query(Intervento).filter(Intervento.id == intervento_id).first()
    if not intervento:
        raise HTTPException(status_code=404, detail="Intervento non trovato")
    
    intervento.fatturato = True
    db.commit()
    
    return RedirectResponse(url="/interventi", status_code=303)