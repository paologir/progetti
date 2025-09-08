# Visualizzazione Pagamenti nella Scheda Cliente

## Panoramica

La scheda cliente del sistema CRM ora include una sezione dedicata ai pagamenti che mostra tutti i pagamenti associati al cliente con una distinzione chiara tra **parcelle** e **fatture** per il calcolo degli incassi.

## Funzionalità Implementate

### 📊 Riepilogo Pagamenti

La sezione presenta 4 card riassuntive con totali calcolati automaticamente:

1. **📋 Da Emettere**: Somma degli importi dei pagamenti non ancora emessi (`emessa=False`)
2. **⏳ Emesso non Pagato**: Somma degli importi emessi ma non ancora pagati (`emessa=True` AND `pagata=False`)
3. **💼 Fatture Incassate**: Somma degli importi delle **sole fatture** pagate (`tipo='fattura'` AND `emessa=True` AND `pagata=True`)
4. **📝 Parcelle Pagate**: Somma degli importi delle **sole parcelle** pagate (`tipo='parcella'` AND `emessa=True` AND `pagata=True`)

### 📋 Lista Dettagliata Pagamenti

Ogni pagamento mostra:

- **Tipo documento**: Badge colorato distintivo
  - 💼 **Fattura** (blu): `tipo='fattura'`
  - 📝 **Parcella** (viola): `tipo='parcella'`
- **Importo**: Valore monetario o "DA DEFINIRE" per importi variabili
- **Descrizione**: Descrizione del servizio/prodotto
- **Date**:
  - 📅 **Data scadenza** (sempre presente)
  - ✅ **Data emissione** (se emessa)
  - 💰 **Data pagamento** (se pagata)
- **Ricorrenza**: Badge per pagamenti ricorrenti
- **Stato visivo**:
  - ✅ **Pagato** (verde)
  - 📋 **Emesso** (blu)
  - 🔴 **In ritardo** (rosso, se scaduto e non emesso)
  - ⏳ **Da emettere** (giallo)

## Logica di Calcolo "Incassati"

⚠️ **Importante**: Come richiesto, il sistema considera "incassati" **solo i pagamenti fatturati**.

### Criteri per "Fatture Incassate":
```sql
tipo = 'fattura' 
AND emessa = True 
AND pagata = True
```

### Parcelle vs Fatture:
- **Parcelle pagate**: Mostrate separatamente, NON incluse negli "incassati"
- **Fatture pagate**: Considerate come veri "incassi" aziendali

Questo permette di distinguere tra:
- **Compensi professionali** (parcelle) 
- **Fatturato aziendale** (fatture)

## Implementazione Tecnica

### Backend (`api/routes.py`)

```python
# Query pagamenti cliente
pagamenti = db.query(ScadenzeFatturazione).filter(
    ScadenzeFatturazione.cliente_id == cliente_id
).order_by(desc(ScadenzeFatturazione.data_scadenza)).all()

# Calcolo totale incassato (solo fatture)
totale_incassato_fatture = db.query(func.sum(ScadenzeFatturazione.importo_previsto)).filter(
    and_(
        ScadenzeFatturazione.cliente_id == cliente_id,
        ScadenzeFatturazione.tipo == 'fattura',  # Solo fatture
        ScadenzeFatturazione.emessa == True,
        ScadenzeFatturazione.pagata == True,
        ScadenzeFatturazione.importo_previsto.isnot(None)
    )
).scalar() or 0
```

### Frontend (`web/templates/clienti/detail.html`)

Sezione completa con:
- Grid responsivo per le card riassuntive
- Lista pagamenti con layout a griglia (icona-contenuto-stato)
- Stili CSS personalizzati per ogni tipo di pagamento
- Indicatori visivi per stati e scadenze

### Stili CSS

```css
/* Card riassuntive con bordi colorati */
.summary-card.incassato-fatture {
    border-left: 4px solid #28a745; /* Verde per incassi */
}

.summary-card.parcelle-pagate {
    border-left: 4px solid #6f42c1; /* Viola per parcelle */
}

/* Badge tipo documento */
.tipo-fattura {
    background: rgba(0, 123, 255, 0.15);
    color: #007bff;
}

.tipo-parcella {
    background: rgba(111, 66, 193, 0.15);
    color: #6f42c1;
}
```

## Utilizzo

### Accesso alla Funzionalità

1. Navigare alla lista clienti: `/clienti`
2. Cliccare su un cliente per aprire la scheda dettaglio
3. Scorrere fino alla sezione "💰 Pagamenti"

### Interpretazione dei Dati

- **Verde (Fatture Incassate)**: Denaro effettivamente incassato dall'azienda
- **Viola (Parcelle Pagate)**: Compensi professionali ricevuti
- **Giallo (Da Emettere)**: Fatturazione da preparare
- **Blu (Emesso non Pagato)**: Documenti emessi in attesa di pagamento
- **Rosso (In ritardo)**: Pagamenti scaduti che richiedono attenzione

### Caso d'Uso Esempio

**Cliente: Fis Group srl**
- Da Emettere: €334.88 → Prepara fattura
- Fatture Incassate: €0 → Nessun incasso ancora registrato
- Parcelle Pagate: €0 → Nessun compenso professionale

**Cliente: Mans & Co. Srl** 
- Emesso non Pagato: €314.08 → Segui per incasso
- Parcelle vs Fatture → Distinzione chiara per reporting

## Benefici

1. **📈 Visibilità Completa**: Tutti i pagamenti del cliente in un'unica vista
2. **🎯 Calcolo Preciso**: Solo le fatture pagate contano come "incassati"
3. **🚨 Alert Visivi**: Pagamenti in ritardo immediatamente identificabili
4. **📊 Reportistica**: Dati pronti per analisi finanziarie
5. **🔄 Gestione Ricorrenze**: Visibilità su pagamenti periodici
6. **💼 Professionalità**: Distinzione chiara tra parcelle e fatture

## Note per lo Sviluppo

- I calcoli sono eseguiti a runtime per garantire dati sempre aggiornati
- La sezione si integra perfettamente con l'interfaccia esistente
- Responsive design per mobile e tablet
- Accessibilità garantita con ARIA labels appropriati
- Performance ottimizzate con query SQL efficienti

---

**Implementato il**: 2025-09-08  
**Versione**: 1.0.0  
**Compatibilità**: Sistema CRM Clienti v1.0.0+