# Landing Page Italplastick

Landing page professionale per **Italplastick**, azienda specializzata nella produzione e installazione di infissi in PVC con oltre 60 anni di esperienza. La pagina promuove i vantaggi dell'Ecobonus con detrazioni fiscali fino al 50% valide fino al 31/12/2025.

## Informazioni Azienda

**Italplastick Srl**
- **Sede**: Viale dell'Artigianato, 20 - 35013 Cittadella (PD)
- **Telefono**: [049 9417888](tel:049%209417888)
- **Email**: [commerciale@italplastick.com](mailto:commerciale@italplastick.com)
- **Sito web**: [www.italplastick.com](http://www.italplastick.com)
- **Esperienza**: Oltre 60 anni nella fabbricazione di infissi in PVC su misura

## Caratteristiche Principali

### 🎯 Obiettivo
Generazione di lead qualificati per la vendita di infissi in PVC attraverso la promozione dell'Ecobonus 50%

### ✨ Funzionalità
- **Design responsive** ottimizzato per desktop, tablet e mobile
- **Form di contatto integrato** con Formspree per gestione automatica delle richieste
- **Showcase prodotti** con esempi di configurazioni di infissi
- **Sezioni informative** sui vantaggi del PVC e dell'Ecobonus
- **Call-to-action strategiche** per massimizzare le conversioni
- **Ottimizzazione SEO** per keyword locali e settoriali
- **Performance ottimizzate** con immagini WebP e lazy loading

## Tecnologie Utilizzate

### Frontend
- **HTML5** con markup semantico
- **Bootstrap 5.1** per layout responsive e componenti UI
- **CSS3** con media queries avanzate per ottimizzazione mobile
- **JavaScript vanilla** per interazioni e form handling
- **Font**: Inter Tight (Google Fonts)

### Gestione Form
- **Formspree** (https://formspree.io/f/xzzvjqjz) per l'invio automatico delle richieste
- **Validazione HTML5** nativa per i campi obbligatori
- **Redirect automatico** alla pagina di ringraziamento

### Ottimizzazione
- **Immagini WebP** per performance superiori
- **Lazy loading** per immagini sotto la piega
- **Preload strategico** per font e CSS critici
- **Minificazione** di CSS e JavaScript

## Struttura del Progetto

```
landing-italplastick/
├── index.html                    # Landing page principale
├── grazie.html                   # Pagina di ringraziamento post-form
├── project.mobirise              # File progetto Mobirise
├── README.md                     # Documentazione del progetto
├── DOCUMENTAZIONE_COMPLETA.md    # Documentazione tecnica estesa
├── preview_mobile.md             # Anteprima ottimizzazioni mobile
└── assets/
    ├── bootstrap/                # Framework Bootstrap
    │   ├── css/
    │   │   ├── bootstrap.min.css
    │   │   ├── bootstrap-grid.min.css
    │   │   └── bootstrap-reboot.min.css
    │   └── js/
    │       └── bootstrap.bundle.min.js
    ├── images/                   # Risorse grafiche
    │   ├── head.webp            # Immagine hero principale
    │   ├── file-testo.webp      # Infografica vantaggi
    │   ├── 50.webp              # Grafica Ecobonus 50%
    │   ├── finestre*.png        # Showcase prodotti (4 tipologie)
    │   ├── filelanding*.jpg     # Immagini aggiuntive
    │   ├── logo-footer.png      # Logo aziendale
    │   └── materiali/           # Versioni originali immagini
    ├── theme/                   # Stili personalizzati
    │   ├── css/style.css
    │   └── js/script.js
    ├── mobirise/                # Stili aggiuntivi Mobirise
    │   └── css/mbr-additional.css
    ├── dropdown/                # Menu navigation
    │   ├── css/style.css
    │   └── js/navbar-dropdown.js
    ├── smoothscroll/            # Smooth scrolling
    │   └── smooth-scroll.js
    ├── ytplayer/                # Video player utilities
    │   └── index.js
    └── witsec-mailform/         # Sistema PHP mail (non utilizzato)
        └── [file PHP vari]
```

## Installazione e Setup

### Requisiti
- Server web con supporto HTML/CSS/JavaScript
- Connessione internet per font esterni e Bootstrap CDN
- Account Formspree configurato per gestione form

### Installazione Locale
1. **Clona o scarica il progetto**:
   ```bash
   git clone [repository-url]
   cd landing-italplastick
   ```

2. **Avvia un server locale**:
   ```bash
   # Con Python
   python3 -m http.server 8000
   
   # Con Node.js (http-server)
   npx http-server
   
   # Con PHP
   php -S localhost:8000
   ```

3. **Apri nel browser**: `http://localhost:8000`

### Deploy in Produzione
1. **Upload file** su server web via FTP/SFTP
2. **Verifica permessi** per le directory assets/
3. **Configura redirect** per la pagina di ringraziamento se necessario
4. **Testa il form** per verificare la ricezione email

## Configurazione Form di Contatto

### Formspree Setup
Il form utilizza Formspree per l'invio automatico delle email:

```html
<form action="https://formspree.io/f/xzzvjqjz" method="POST" id="formspree-contact">
  <input type="hidden" name="_subject" value="Richiesta informazioni Landing Italplastick">
  <input type="hidden" name="_next" value="https://www.italplastick.com/paolo/grazie.html">
  <!-- Campi del form -->
</form>
```

### Campi del Form
- **Nome e Cognome** (obbligatorio)
- **Email** (obbligatorio)
- **Telefono** (obbligatorio)
- **Città** (obbligatorio)
- **Indirizzo** (opzionale)
- **Messaggio** (obbligatorio)

### Personalizzazione Formspree
Per modificare la configurazione:
1. Cambia l'ID form in `action="https://formspree.io/f/TUO_ID"`
2. Modifica `_next` per il redirect post-invio
3. Personalizza `_subject` per l'oggetto email

## Sezioni della Landing Page

### 1. Header/Navigation
- Logo aziendale con link al sito principale
- Menu con contatti diretti (telefono, email, sito web)
- Design responsive con hamburger menu su mobile

### 2. Hero Section
- Immagine principale accattivante
- Headline: "Migliora il comfort della tua casa con gli infissi in PVC di Ital-plastick!"
- Messaggio di valore incentrato sul comfort abitativo

### 3. Offerta Esclusiva
- Sezione "SCOPRI LA NOSTRA OFFERTA ESCLUSIVA"
- Showcase di 6 infissi esempio con specifiche tecniche:
  - 2 finestre una anta (900x1450 mm)
  - 2 finestre due ante (1500x1400 mm)  
  - 1 portafinestra piccola (900x2400 mm)
  - 1 portafinestra grande (1500x2400 mm)

### 4. Richiamo Ecobonus
- Sezione dedicata all'Ecobonus 50%
- Evidenza grafica del risparmio
- Scadenza: "fino al 31/12/2025"

### 5. Vantaggi Competitivi
Quattro punti di forza evidenziati:
- **Risparmio energetico garantito**: Riduzione dispersione termica
- **Innovazione tecnologica**: Profili PVC progettati internamente
- **Design personalizzato**: Soluzioni su misura
- **Installazione professionale**: Team tecnico esperto

### 6. Form di Contatto
- Headline: "Approfitta dell'Ecobonus e ottieni una detrazione fino al 50%!"
- Subtitle: "Contattaci o compila il form per una consulenza gratuita e su misura"
- Form a 6 campi con validazione HTML5

### 7. Footer
- Logo aziendale
- Informazioni di contatto complete
- Design pulito e professionale

## Ottimizzazioni Mobile

### Design Responsive
La landing page è completamente ottimizzata per dispositivi mobili con:

- **Breakpoint personalizzati**:
  - Mobile: `max-width: 767px`
  - Tablet: `768px - 991px`
  - Desktop: `min-width: 992px`

- **Ottimizzazioni tipografiche**:
  ```css
  @media (max-width: 767px) {
    .display-2 { font-size: 2rem !important; }
    .display-5 { font-size: 1.5rem !important; }
    .display-7 { font-size: 1.1rem !important; }
  }
  ```

- **Form mobile-friendly**:
  - Font-size 16px per prevenire zoom su iOS
  - Padding ottimizzato per touch
  - Layout verticale su schermi piccoli

- **Immagini responsive**:
  - `max-width: 100%` e `height: auto`
  - Ottimizzazione per connessioni lente

### Performance Mobile
- Immagini in formato WebP per ridurre i tempi di caricamento
- Lazy loading per immagini sotto la piega
- CSS critici inline per First Contentful Paint rapido

## Personalizzazione

### Colori Brand
Il tema utilizza una palette coerente:
- **Primario**: `#e74c3c` (rosso Italplastick)
- **Secondario**: `#c0392b` (rosso scuro)
- **Neutri**: `#333` (testi), `#666` (secondari), `#f8f9fa` (backgrounds)

### Font Typography
- **Font principale**: Inter Tight (Google Fonts)
- **Pesi utilizzati**: 400, 600, 700
- **Fallback**: Arial, sans-serif

### Modifica Contenuti
Per aggiornare testi e immagini:

1. **Testi**: Modifica direttamente nel file `index.html`
2. **Immagini**: Sostituisci i file in `assets/images/`
3. **Colori**: Aggiorna le variabili nel `<style>` di `index.html`
4. **Logo**: Sostituisci `logo-footer.png` mantenendo proporzioni

### SEO Optimization
La pagina include:
- Meta description ottimizzata per keyword locali
- Title tag con parole chiave strategiche
- Open Graph tags per social sharing
- Alt text descrittivi per tutte le immagini
- Markup semantico HTML5

## Analytics e Tracking

### Google Tag Manager
- **Container ID**: `GTM-PNS9843`
- Implementato su tutte le pagine (index.html e grazie.html)
- Configurato per tracciare eventi personalizzati

### Eventi Personalizzati Tracciati
- **`invia_modulo`**: Scatenato all'invio del form di contatto
- **Parametri evento**:
  - `form_name`: contact_form_italplastick
  - `form_destination`: formspree  
  - `event_category`: Form
  - `event_action`: Submit
  - `event_label`: Contact Form Italplastick

### Configurazione GTM Necessaria

#### 1. Trigger da Creare
```
Tipo: Evento personalizzato
Nome evento: invia_modulo
Attivazione: Tutti gli eventi personalizzati
```

#### 2. Tag GA4 da Creare  
```
Tipo: Google Analytics: Evento GA4
ID misurazione: [TUO_GA4_ID]
Nome evento: form_submission
Trigger: invia_modulo
Parametri evento (opzionali):
- form_name: {{form_name}}
- form_destination: {{form_destination}}
- event_category: {{event_category}}
```

#### 3. Configurazione Conversione GA4
1. In GA4: Admin > Eventi > Contrassegna come conversione
2. Trova l'evento `form_submission` e attivalo
3. L'evento sarà automaticamente disponibile in Google Ads come obiettivo

### Problema Risolto: Formspree Gratuito
**Problema**: Formspree gratuito non reindirizza a grazie.html ma alla sua pagina  
**Soluzione**: L'evento `invia_modulo` viene tracciato PRIMA del submit, garantendo il tracciamento anche senza redirect alla nostra pagina di ringraziamento

## Manutenzione e Aggiornamenti

### Controlli Periodici
- **Form testing**: Verifica mensile funzionamento invio
- **Link esterni**: Controllo trimestrale link a sito principale
- **Immagini**: Ottimizzazione continua per performance
- **Content**: Aggiornamento scadenze Ecobonus

### Backup e Versioning
- Mantieni backup del progetto prima di modifiche
- Documenta cambiamenti significativi
- Testa su ambiente staging prima del deploy

### Performance Monitoring
Metriche da monitorare:
- **Page Load Speed**: < 3 secondi
- **Form Conversion Rate**: Obiettivo > 5%
- **Mobile Usability**: Score > 90/100
- **SEO Score**: Mantenere > 85/100

## Supporto e Contatti

Per assistenza tecnica o modifiche al progetto, contattare il team di sviluppo mantenendo questo README aggiornato con le evoluzioni della landing page.

---

## 🔄 Stato Lavori e Modifiche Recenti

### 29 Agosto 2025 ✅
1. **Placeholder telefono**: Rimossa la dicitura "(es. 049 9417888)" dal campo telefono
2. **Evento tracciamento GA4**: Implementato evento `invia_modulo` per superare limitazioni Formspree gratuito
3. **Documentazione README**: Aggiornata con configurazione GTM completa e stato lavori

### Modifiche Precedenti
- **Setup iniziale**: Implementazione landing page con Formspree
- **Ottimizzazioni mobile**: Design responsive e performance
- **SEO**: Meta tags e ottimizzazioni per motori ricerca
- **GTM**: Implementazione Google Tag Manager per analytics

### ⚡ Implementazioni Immediate Necessarie
Per attivare il tracciamento conversioni:
1. **Google Tag Manager**: Creare trigger e tag come documentato sopra
2. **Google Analytics 4**: Contrassegnare evento `form_submission` come conversione  
3. **Google Ads**: Importare conversione per campagne

### 🎯 Obiettivi Completati
- ✅ Form funzionante con Formspree
- ✅ Design responsive ottimizzato  
- ✅ Tracciamento eventi per conversioni GA4/Ads
- ✅ SEO base implementato
- ✅ Performance mobile ottimizzate

---

**Ultima modifica**: 29 Agosto 2025  
**Versione**: 2.1  
**Stato**: Produzione + Configurazione GTM in attesa  
**Browser supportati**: Chrome, Firefox, Safari, Edge (ultime 2 versioni)