# Landing Page FIS

This project is a static landing page for FIS Group.

## Project Structure

The project is composed of static HTML, CSS and JavaScript files. The main files are:

*   `index.html`: The main landing page.
*   `thanks.html`: The "thank you" page after form submission.
*   `sendmail.php`: The script to handle the contact form.
*   `assets/`: This directory contains all the assets like CSS, JavaScript, images, etc.

## Technologies Used

*   HTML5
*   CSS3
*   JavaScript
*   Bootstrap
*   PHP (for the contact form)

## Setup and Deployment

This is a static website. To deploy it, you just need to copy the files to a web server with PHP support for the contact form. No special build process is required.

---

# Landing Page FIS Group - Ottimizzazioni per Google Ads

## Panoramica
Questo documento descrive le ottimizzazioni implementate sulla landing page di FIS Group per migliorare le performance delle campagne Google Ads e aumentare il tasso di conversione.

## 📊 Ottimizzazioni Implementate

### 🎯 **1. Tracciamento Conversioni Avanzato**
- **Google Analytics 4 Enhanced Events**: Implementati eventi personalizzati per micro-conversioni
- **Scroll Depth Tracking**: Tracciamento a 25%, 50%, 75%, 90% della pagina
- **Time on Page Tracking**: Misurazione engagement a 15s, 30s, 60s, 120s
- **Form Interaction Tracking**: Tracciamento interazioni con i campi del form
- **Form Abandonment Tracking**: Rilevamento abbandono form per ottimizzazione
- **CTA Click Tracking**: Tracciamento dettagliato di tutti i click sui bottoni con posizione

### 📝 **2. Ottimizzazione Form di Contatto**
- **Campi Obbligatori Ridotti**: Solo Nome, Email e Messaggio (rimosso Cognome obbligatorio)
- **Validazione Real-time**: Feedback visivo immediato sui campi compilati
- **Auto-completamento**: Abilitato per campi indirizzo (città, via)
- **Feedback Visivo**: Indicatori di successo/errore per ogni campo
- **Correzione Redirect**: Corretto il redirect da `/landing/thanks.html` a `thanks.html`

### 🎯 **3. CTA Ottimizzate e Coerenti**
- **CTA Hero**: "Richiedi Informazioni" con icona email (✉️)
- **CTA Sezioni Prodotto**: "Richiedi Info" e "Contattaci" con icona email
- **CTA Sticky Mobile**: "✉️ Contattaci Subito!" (appare al 30% scroll)
- **Coerenza Icone-Azioni**: Tutte le CTA che vanno al form usano l'icona email
- **Design Accattivante**: Gradiente rosso con effetti hover e animazioni

### ⚡ **4. Ottimizzazione Performance**
- **Lazy Loading**: Implementato per tutte le immagini sotto il fold
- **Intersection Observer**: Caricamento intelligente delle immagini
- **Preload Risorse Critiche**: CSS e font precaricati
- **Alt Text SEO**: Descrizioni ottimizzate per tutte le immagini
- **Formato WebP**: Mantenuto per immagini ottimizzate

### 🏆 **5. Above-the-fold Migliorato**
- **Value Proposition Chiara**: "Porte Garage di Qualità 100% Made in Italy"
- **Benefici Evidenziati**:
  - Progettazione personalizzata
  - Installazione professionale  
  - Produzione italiana
- **CTA Prominente**: Bottone hero visibile senza scroll
- **Background Ottimizzato**: Sfondo con overlay per leggibilità testo

### 📱 **6. Ottimizzazione Mobile**
- **CTA Sticky**: Bottone fisso in basso per mobile
- **Tap Targets**: Dimensioni minime 44px per tutti i bottoni
- **Form Responsive**: Campi full-width su mobile
- **Tipografia Scalabile**: Font size ottimizzato per dispositivi piccoli
- **Navigazione Mobile**: Logo ridimensionato e menu ottimizzato

### 🧪 **7. A/B Testing Framework**
- **Test Headline**: 3 varianti per il titolo principale
- **Test CTA**: 3 varianti per i testi dei bottoni
- **Test Form CTA**: 3 varianti per il bottone di invio
- **Persistenza Test**: Assegnazioni salvate in localStorage
- **Tracciamento Conversioni**: Eventi separati per ogni variante

### 🔍 **8. SEO Tecnico**
- **Meta Description**: Ottimizzata per Google Ads Quality Score
- **Title Tag**: "Porte Garage Made in Italy | FIS Group - Preventivo Gratuito"
- **Schema Markup**: JSON-LD completo per LocalBusiness
- **Open Graph**: Meta tag per social media
- **Canonical URL**: Implementato per evitare contenuti duplicati
- **Structured Data**: Informazioni azienda, prodotti e contatti

## 🚫 Elementi Rimossi/Corretti

### ❌ **Problemi Corretti**
1. **Headline Errata**: "Le Migliori Porte Garage del Made in Italy" → "Porte Garage Italiane di Alta Qualità"
2. **Icone Incoerenti**: Icona telefono per CTA che andavano al form → Icona email
3. **Claim Inventati**: 
   - ❌ "Preventivo in 24h"
   - ❌ "Garanzia 5 anni" 
   - ✅ Sostituiti con benefici reali
4. **Social Proof Generico**: ❌ "Oltre 1000 clienti soddisfatti" → Rimosso
5. **Trust Badge Eccessivo**: ❌ Icona coppa "Dal 1967" → Rimosso
6. **CTA Fuorvianti**: ❌ "Scopri i prezzi" → ✅ "Richiedi Info"
7. **Barra Progresso Form**: ❌ Elemento inutile → Completamente rimossa

## 📈 KPI da Monitorare

### **Metriche Primarie**
- **Conversion Rate**: Percentuale form completati/visite
- **Cost per Conversion**: Costo per acquisizione lead da Google Ads
- **Quality Score**: Punteggio qualità annunci Google

### **Metriche Secondarie**
- **Bounce Rate**: Percentuale abbandono immediato
- **Time on Page**: Tempo medio sulla pagina
- **Scroll Depth**: Profondità scroll medio
- **Form Abandonment Rate**: Percentuale abbandono form

### **A/B Testing**
- **Click-through Rate**: Per ogni variante CTA
- **Conversion Rate**: Per ogni variante headline
- **Statistical Significance**: Raggiungimento soglia test

## 🔧 Setup Google Tag Manager

### **Eventi da Configurare**
1. `scroll_depth` - Trigger: Custom Event
2. `time_on_page` - Trigger: Custom Event  
3. `form_start` - Trigger: Custom Event
4. `form_submit` - Trigger: Custom Event (CONVERSIONE)
5. `cta_click` - Trigger: Custom Event
6. `sticky_cta_shown` - Trigger: Custom Event
7. `ab_test_assigned` - Trigger: Custom Event

### **Conversioni Google Ads**
- **Evento Principale**: `form_submit`
- **Enhanced Conversions**: Abilitato con email hash
- **Attribution Model**: Data-driven (consigliato)

## 📁 File Modificati

### **File Principali**
- `index.html` - Landing page principale (ottimizzazioni complete)
- `sendmail.php` - Correzione redirect
- `thanks.html` - Pagina ringraziamento (invariata)

### **Modifiche Strutturali**
- **HTML**: Aggiunti data attributes per tracking e A/B testing
- **CSS**: Nuovi stili per CTA, validazione form, mobile
- **JavaScript**: Framework completo per tracking e testing
- **Schema Markup**: JSON-LD per SEO locale

## 🎯 Risultati Attesi

### **Incrementi Previsti**
- **Conversion Rate**: +15-25% (rimozione friction form)
- **Quality Score**: +10-20% (SEO e UX migliorati)
- **Mobile Conversions**: +20-30% (CTA sticky e ottimizzazioni)
- **Cost per Click**: -5-15% (Quality Score migliorato)

### **Metriche Engagement**
- **Time on Page**: +20-30%
- **Scroll Depth**: +15-25%
- **Form Completion Rate**: +10-20%

---

*Documento aggiornato: 2 Settembre 2025*
*Ottimizzazioni implementate per campagne Google Ads FIS Group*

---

## Changelog

*   **Improved HTML Semantics:** Restructured `index.html` to use semantic tags (`<header>`, `<main>`, `<footer>`). This improves accessibility and SEO.
*   **Updated README.md:** Added a general project description, including structure, technologies, and deployment instructions.