# Come visualizzare preview mobile della landing page

## Metodo 1: Python HTTP Server (Più semplice)

Dalla directory del progetto, esegui:

```bash
cd /opt/progetti/landing-italplastick
python3 -m http.server 8000
```

Poi apri: http://localhost:8000

## Metodo 2: Node.js http-server

Se hai Node.js installato:

```bash
npx http-server -p 8000
```

## Metodo 3: VS Code Live Server

Se usi VS Code:
1. Installa estensione "Live Server"
2. Click destro su index.html
3. Seleziona "Open with Live Server"

## Test dispositivi comuni

Una volta aperto nel browser, usa i Developer Tools (F12) per testare:

### Smartphone:
- iPhone SE (375 x 667)
- iPhone 12/13 (390 x 844)
- Samsung Galaxy S20 (360 x 800)
- Pixel 5 (393 x 851)

### Tablet:
- iPad (768 x 1024)
- iPad Pro (1024 x 1366)

### Breakpoints CSS utilizzati:
- Mobile: < 768px
- Tablet: 768px - 991px
- Desktop: > 992px

## Shortcuts utili nei DevTools:
- `Ctrl+Shift+M`: Toggle responsive mode
- Click su dimensioni: Ruota orientamento
- Menu "⋮": Mostra rulers, cattura screenshot

## Test da fare:
1. ✓ Menu hamburger funzionante
2. ✓ Form compilabile senza zoom
3. ✓ Testi leggibili
4. ✓ Immagini non tagliate
5. ✓ Bottoni cliccabili (min 44x44px)
6. ✓ Scroll fluido