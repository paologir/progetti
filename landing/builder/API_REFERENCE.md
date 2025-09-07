# API Reference - Landing Page Builder

> Documentazione completa delle API per tutti i componenti del sistema

## 📚 Indice

- [Core Classes](#core-classes)
  - [LandingPageBuilder](#landingpagebuilder)
  - [LandingPageConfig](#landingpageconfig)
- [HTML Generator](#html-generator)
  - [HTMLGenerator](#htmlgenerator)
  - [SEOConfig](#seoconfig)
  - [AccessibilityConfig](#accessibilityconfig)
- [CSS Framework](#css-framework)
  - [CSSFramework](#cssframework)
  - [ColorScheme](#colorscheme)
  - [Typography](#typography)
- [JavaScript Engine](#javascript-engine)
  - [JSEngine](#jsengine)
  - [JSConfig](#jsconfig)
  - [ValidationRule](#validationrule)
- [Template System](#template-system)
  - [HeroComponent](#herocomponent)
  - [HeroTemplate](#herotemplate)
- [Enums & Constants](#enums--constants)
- [Utility Functions](#utility-functions)
- [Examples](#examples)

---

## Core Classes

### LandingPageBuilder

La classe principale per la creazione di landing page complete.

```python
class LandingPageBuilder:
    """
    Main builder class for creating complete landing pages.
    """
    
    def __init__(self, config: LandingPageConfig):
        """
        Initialize the landing page builder.
        
        Args:
            config (LandingPageConfig): Configuration object with all settings
        """
```

#### Metodi Principali

##### `add_hero_section(template_type: str, config: Dict[str, Any]) -> 'LandingPageBuilder'`

Aggiunge una sezione hero utilizzando un template predefinito.

**Parametri:**
- `template_type` (str): Tipo di template hero
  - `"lead_generation"` - Ottimizzato per cattura lead
  - `"product_launch"` - Per lanci prodotto
  - `"sales_page"` - Per pagine di vendita
  - `"event_registration"` - Per registrazione eventi
  - `"app_download"` - Per download app
- `config` (Dict[str, Any]): Configurazione specifica del template

**Ritorna:** Self per method chaining

**Esempio:**
```python
builder.add_hero_section("lead_generation", {
    "title": "Trasforma il Tuo Business",
    "subtitle": "La strategia che funziona davvero",
    "cta_text": "Scarica la Guida Gratuita",
    "cta_url": "#lead-form"
})
```

##### `add_features_section(config: Dict[str, Any]) -> 'LandingPageBuilder'`

Aggiunge una sezione caratteristiche/benefici.

**Parametri:**
- `config` (Dict[str, Any]): Configurazione della sezione
  - `title` (str): Titolo della sezione
  - `subtitle` (str, optional): Sottotitolo
  - `features` (List[Dict]): Lista delle caratteristiche

**Esempio:**
```python
builder.add_features_section({
    "title": "Perché Scegliere la Nostra Soluzione",
    "subtitle": "Benefici concreti per il tuo business", 
    "features": [
        {
            "title": "Risultati Garantiti",
            "description": "Aumento conversioni del 200-400%",
            "icon": "🎯"
        },
        {
            "title": "Supporto 24/7",
            "description": "Team dedicato sempre disponibile",
            "icon": "🚀"
        }
    ]
})
```

##### `add_testimonials_section(config: Dict[str, Any]) -> 'LandingPageBuilder'`

Aggiunge sezione testimonial per social proof.

**Parametri:**
- `config` (Dict[str, Any]): Configurazione testimonial
  - `title` (str): Titolo della sezione
  - `testimonials` (List[Dict]): Lista dei testimonial

**Esempio:**
```python
builder.add_testimonials_section({
    "title": "Cosa Dicono i Nostri Clienti",
    "testimonials": [
        {
            "text": "Risultati incredibili in 30 giorni!",
            "author": "Marco R.",
            "role": "CEO",
            "company": "TechStart",
            "rating": 5
        }
    ]
})
```

##### `add_pricing_section(config: Dict[str, Any]) -> 'LandingPageBuilder'`

Aggiunge sezione prezzi/piani.

**Parametri:**
- `config` (Dict[str, Any]): Configurazione pricing
  - `title` (str): Titolo della sezione
  - `plans` (List[Dict]): Lista dei piani

**Esempio:**
```python
builder.add_pricing_section({
    "title": "Scegli il Tuo Piano",
    "plans": [
        {
            "name": "Base",
            "price": "99€",
            "features": ["Feature 1", "Feature 2"],
            "cta_text": "Inizia Ora"
        }
    ]
})
```

##### `add_form_section(config: Dict[str, Any]) -> 'LandingPageBuilder'`

Aggiunge form con validazione automatica.

**Parametri:**
- `config` (Dict[str, Any]): Configurazione form
  - `title` (str): Titolo del form
  - `action` (str): URL di submit
  - `fields` (List[Dict]): Lista dei campi
  - `submit_text` (str): Testo del bottone

**Esempio:**
```python
builder.add_form_section({
    "title": "Richiedi Informazioni",
    "action": "/submit",
    "fields": [
        {
            "name": "email",
            "type": "email",
            "label": "Email",
            "required": True
        },
        {
            "name": "nome",
            "type": "text",
            "label": "Nome",
            "required": True
        }
    ],
    "submit_text": "Invia Richiesta"
})
```

##### `add_interaction(interaction_type: InteractionType, config: Dict[str, Any]) -> 'LandingPageBuilder'`

Aggiunge componenti JavaScript interattivi.

**Parametri:**
- `interaction_type` (InteractionType): Tipo di interazione
- `config` (Dict[str, Any]): Configurazione specifica

**Tipi disponibili:**
- `InteractionType.FORM_VALIDATION` - Validazione form
- `InteractionType.SMOOTH_SCROLL` - Scroll fluido
- `InteractionType.LAZY_LOADING` - Caricamento differito
- `InteractionType.MODAL` - Finestre modali
- `InteractionType.COUNTDOWN_TIMER` - Timer conto alla rovescia
- `InteractionType.STICKY_CTA` - CTA fisso
- `InteractionType.ACCORDION` - Fisarmonica
- `InteractionType.CAROUSEL` - Carosello

**Esempio:**
```python
from core.js_engine import InteractionType

builder.add_interaction(InteractionType.COUNTDOWN_TIMER, {
    "target": ".hero-section",
    "end_date": "2024-12-31T23:59:59",
    "message": "Offerta termina tra:"
})
```

##### `generate_files() -> Dict[str, str]`

Genera tutti i file della landing page.

**Ritorna:** Dict con i percorsi dei file generati
- `html` (str): Percorso file HTML
- `css` (str): Percorso file CSS
- `js` (str): Percorso file JavaScript
- `readme` (str): Percorso README
- `robots` (str): Percorso robots.txt
- `sitemap` (str): Percorso sitemap.xml

**Esempio:**
```python
files = builder.generate_files()
print(f"HTML: {files['html']}")
print(f"CSS: {files['css']}")
print(f"JS: {files['js']}")
```

##### `generate_performance_report() -> Dict[str, Any]`

Genera report dettagliato delle performance.

**Ritorna:** Dict con metriche performance
- `html_size` (int): Dimensione HTML in bytes
- `css_size` (int): Dimensione CSS in bytes
- `js_size` (int): Dimensione JavaScript in bytes
- `total_size` (int): Dimensione totale
- `components_count` (int): Numero componenti
- `validation_rules_count` (int): Numero regole validazione
- `accessibility_features` (List[str]): Feature accessibilità
- `seo_features` (List[str]): Feature SEO

**Esempio:**
```python
report = builder.generate_performance_report()
print(f"Dimensione totale: {report['total_size']} bytes")
print(f"Componenti: {report['components_count']}")
```

##### `validate_output() -> Dict[str, Any]`

Valida l'output generato per problemi comuni.

**Ritorna:** Dict con risultati validazione
- `html_valid` (bool): HTML valido
- `css_valid` (bool): CSS valido
- `js_valid` (bool): JavaScript valido
- `accessibility_score` (int): Score accessibilità 0-100
- `seo_score` (int): Score SEO 0-100
- `performance_score` (int): Score performance 0-100
- `issues` (List[str]): Problemi critici
- `warnings` (List[str]): Avvisi
- `suggestions` (List[str]): Suggerimenti

**Esempio:**
```python
validation = builder.validate_output()
print(f"Accessibilità: {validation['accessibility_score']}/100")
print(f"Issues: {len(validation['issues'])}")
```

---

### LandingPageConfig

Classe di configurazione principale per il builder.

```python
@dataclass
class LandingPageConfig:
    # Informazioni base
    title: str
    description: str
    target_audience: str
    conversion_goal: str
    
    # SEO & Meta
    seo_config: SEOConfig
    
    # Design & Styling
    color_scheme: Optional[ColorScheme] = None
    typography: Optional[Typography] = None
    
    # Funzionalità
    accessibility_config: Optional[AccessibilityConfig] = None
    js_config: Optional[JSConfig] = None
    
    # Output Settings
    output_directory: str = "output"
    include_analytics: bool = True
    minify_output: bool = True
```

**Parametri:**

##### Informazioni Base
- `title` (str): Titolo della landing page
- `description` (str): Descrizione della pagina
- `target_audience` (str): Audience target
- `conversion_goal` (str): Obiettivo di conversione

##### Configurazioni Opzionali
- `color_scheme` (ColorScheme, optional): Schema colori personalizzato
- `typography` (Typography, optional): Configurazione tipografica
- `accessibility_config` (AccessibilityConfig, optional): Configurazione accessibilità
- `js_config` (JSConfig, optional): Configurazione JavaScript

##### Output Settings
- `output_directory` (str): Directory di output (default: "output")
- `include_analytics` (bool): Includi analytics (default: True)
- `minify_output` (bool): Minifica l'output (default: True)

**Esempio:**
```python
config = LandingPageConfig(
    title="Corso Marketing Digitale",
    description="Il corso più completo per diventare esperto",
    target_audience="Professionisti e imprenditori",
    conversion_goal="Vendita corso online",
    seo_config=seo_config,
    color_scheme=custom_colors,
    output_directory="my_landing_page",
    minify_output=True
)
```

---

## HTML Generator

### HTMLGenerator

Generatore di HTML semantico con compliance WCAG.

```python
class HTMLGenerator:
    """
    Core HTML generator for landing pages with semantic structure
    and accessibility compliance.
    """
    
    def __init__(self, seo_config: SEOConfig, accessibility_config: AccessibilityConfig = None):
        """
        Initialize HTML generator.
        
        Args:
            seo_config (SEOConfig): SEO configuration
            accessibility_config (AccessibilityConfig, optional): Accessibility settings
        """
```

#### Metodi Principali

##### `add_component(component_type: ComponentType, config: Dict[str, Any]) -> None`

Aggiunge un componente alla struttura della pagina.

**Parametri:**
- `component_type` (ComponentType): Tipo di componente
- `config` (Dict[str, Any]): Configurazione del componente

##### `generate_head() -> str`

Genera la sezione HEAD con ottimizzazioni SEO e performance.

**Ritorna:** HTML della sezione head

##### `generate_complete_page() -> str`

Genera la pagina HTML completa.

**Ritorna:** HTML completo della pagina

---

### SEOConfig

Configurazione SEO per meta tags e structured data.

```python
@dataclass
class SEOConfig:
    title: str
    description: str
    keywords: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
```

**Parametri:**
- `title` (str): Titolo SEO della pagina
- `description` (str): Meta description
- `keywords` (str, optional): Keywords separate da virgola
- `og_title` (str, optional): Titolo Open Graph
- `og_description` (str, optional): Descrizione Open Graph
- `og_image` (str, optional): URL immagine Open Graph
- `canonical_url` (str, optional): URL canonico

**Esempio:**
```python
seo_config = SEOConfig(
    title="Corso Marketing Digitale - Diventa Esperto",
    description="Il corso più completo per diventare esperto di marketing digitale. 5000+ studenti soddisfatti.",
    keywords="marketing digitale, corso online, lead generation",
    og_title="🚀 Corso Marketing Digitale - Da Zero a Esperto",
    og_description="Trasforma la tua carriera con il nostro corso completo",
    og_image="https://example.com/og-image.jpg",
    canonical_url="https://example.com/corso-marketing"
)
```

---

### AccessibilityConfig

Configurazione per l'accessibilità WCAG.

```python
@dataclass
class AccessibilityConfig:
    lang: str = "it"
    skip_navigation: bool = True
    high_contrast_mode: bool = False
    screen_reader_optimization: bool = True
```

**Parametri:**
- `lang` (str): Lingua della pagina (default: "it")
- `skip_navigation` (bool): Abilita link skip navigation (default: True)
- `high_contrast_mode` (bool): Modalità alto contrasto (default: False)
- `screen_reader_optimization` (bool): Ottimizzazioni screen reader (default: True)

---

## CSS Framework

### CSSFramework

Framework CSS moderno con Grid/Flexbox e Custom Properties.

```python
class CSSFramework:
    """
    Modern CSS framework for high-converting landing pages.
    """
    
    def __init__(self, color_scheme: ColorScheme = None, typography: Typography = None):
        """
        Initialize CSS framework.
        
        Args:
            color_scheme (ColorScheme, optional): Custom color scheme
            typography (Typography, optional): Custom typography settings
        """
```

#### Metodi Principali

##### `generate_complete_css() -> str`

Genera il CSS completo del framework.

**Ritorna:** CSS completo con tutte le utilities

##### `generate_css_variables() -> str`

Genera le Custom Properties CSS per il theming.

**Ritorna:** CSS con variabili personalizzate

##### `generate_grid_system() -> str`

Genera il sistema di griglia responsive.

**Ritorna:** CSS del grid system

##### `generate_button_styles() -> str`

Genera stili per i bottoni ottimizzati per conversioni.

**Ritorna:** CSS dei bottoni

---

### ColorScheme

Schema colori per il framework CSS.

```python
@dataclass
class ColorScheme:
    primary: str
    secondary: str
    accent: str
    success: str
    warning: str
    error: str
    neutral_50: str
    neutral_100: str
    neutral_200: str
    neutral_300: str
    neutral_400: str
    neutral_500: str
    neutral_600: str
    neutral_700: str
    neutral_800: str
    neutral_900: str
```

**Parametri:**
- `primary` (str): Colore primario (es. "#2563eb")
- `secondary` (str): Colore secondario (es. "#7c3aed")
- `accent` (str): Colore accent per CTA (es. "#f59e0b")
- `success` (str): Verde per stati di successo
- `warning` (str): Giallo per avvisi
- `error` (str): Rosso per errori
- `neutral_*` (str): Scala di grigi da 50 a 900

**Esempio:**
```python
colors = ColorScheme(
    primary="#1e40af",      # Blu professionale
    secondary="#7c3aed",    # Viola premium
    accent="#f59e0b",       # Orange urgenza
    success="#10b981",      # Verde successo
    warning="#f59e0b",      # Giallo warning
    error="#ef4444",        # Rosso errore
    neutral_50="#f9fafb",
    neutral_100="#f3f4f6",
    # ... altri colori neutral
    neutral_900="#111827"
)
```

---

### Typography

Configurazione tipografica responsive.

```python
@dataclass
class Typography:
    font_family_primary: str
    font_family_secondary: str
    font_size_base: str
    line_height_base: float
    letter_spacing_base: str
    h1_size: str
    h2_size: str
    h3_size: str
    h4_size: str
    h5_size: str
    h6_size: str
```

**Parametri:**
- `font_family_primary` (str): Font primario per il corpo
- `font_family_secondary` (str): Font secondario per titoli
- `font_size_base` (str): Dimensione base (default: "16px")
- `line_height_base` (float): Altezza riga base (default: 1.6)
- `letter_spacing_base` (str): Spaziatura lettere (default: "-0.01em")
- `h1_size` (str): Dimensione H1 responsive
- ... (h2-h6 simili)

**Esempio:**
```python
typography = Typography(
    font_family_primary="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    font_family_secondary="'Playfair Display', Georgia, serif",
    font_size_base="16px",
    line_height_base=1.6,
    letter_spacing_base="-0.01em",
    h1_size="clamp(2.5rem, 4vw, 4rem)",  # 40-64px responsive
    h2_size="clamp(2rem, 3vw, 3rem)",    # 32-48px responsive
    h3_size="clamp(1.5rem, 2.5vw, 2rem)" # 24-32px responsive
    # ... altri heading
)
```

---

## JavaScript Engine

### JSEngine

Engine JavaScript per interazioni e validazioni.

```python
class JSEngine:
    """
    JavaScript engine for landing page interactions and optimizations.
    """
    
    def __init__(self, config: JSConfig = None):
        """
        Initialize JavaScript engine.
        
        Args:
            config (JSConfig, optional): JavaScript configuration
        """
```

#### Metodi Principali

##### `add_interaction(interaction_type: InteractionType, config: Dict[str, Any]) -> None`

Aggiunge un'interazione JavaScript.

**Parametri:**
- `interaction_type` (InteractionType): Tipo di interazione
- `config` (Dict[str, Any]): Configurazione dell'interazione

##### `add_validation_rule(rule: ValidationRule) -> None`

Aggiunge regola di validazione per i form.

**Parametri:**
- `rule` (ValidationRule): Regola di validazione

##### `generate_complete_js() -> str`

Genera il JavaScript completo.

**Ritorna:** Codice JavaScript ottimizzato

---

### JSConfig

Configurazione per il JavaScript engine.

```python
@dataclass
class JSConfig:
    enable_analytics: bool = True
    lazy_loading: bool = True
    smooth_scroll: bool = True
    form_validation: bool = True
    progressive_enhancement: bool = True
```

**Parametri:**
- `enable_analytics` (bool): Abilita tracking analytics
- `lazy_loading` (bool): Abilita lazy loading immagini
- `smooth_scroll` (bool): Abilita scroll fluido
- `form_validation` (bool): Abilita validazione form
- `progressive_enhancement` (bool): Progressive enhancement

---

### ValidationRule

Regola di validazione per campi form.

```python
@dataclass
class ValidationRule:
    field_name: str
    rule_type: str  # required, email, phone, min_length, max_length, pattern
    value: Optional[Any] = None
    message: str = ""
```

**Parametri:**
- `field_name` (str): Nome del campo da validare
- `rule_type` (str): Tipo di validazione
  - `"required"` - Campo obbligatorio
  - `"email"` - Validazione email
  - `"phone"` - Validazione telefono
  - `"min_length"` - Lunghezza minima
  - `"max_length"` - Lunghezza massima
  - `"pattern"` - Pattern regex personalizzato
- `value` (Any, optional): Valore per la regola (es. lunghezza)
- `message` (str): Messaggio di errore personalizzato

**Esempio:**
```python
# Validazione email
email_rule = ValidationRule(
    field_name="email",
    rule_type="email",
    message="Inserisci un indirizzo email valido"
)

# Validazione lunghezza minima
password_rule = ValidationRule(
    field_name="password", 
    rule_type="min_length",
    value=8,
    message="La password deve essere di almeno 8 caratteri"
)

# Validazione pattern personalizzato
phone_rule = ValidationRule(
    field_name="telefono",
    rule_type="pattern",
    value=r"^[\+]?[1-9][\d\s\-\(\)]{7,15}$",
    message="Inserisci un numero di telefono valido"
)
```

---

## Template System

### HeroComponent

Componente per sezioni hero con template ottimizzati.

```python
class HeroComponent:
    """
    Hero section component with conversion-optimized templates.
    """
```

#### Metodi Statici

##### `get_templates() -> Dict[str, HeroTemplate]`

Ottiene tutti i template hero disponibili.

**Ritorna:** Dict con i template disponibili

##### `get_template_by_type(template_type: str, config: Dict[str, Any]) -> Dict[str, Any]`

Ottiene configurazione hero per tipo specifico.

**Parametri:**
- `template_type` (str): Tipo di template
- `config` (Dict[str, Any]): Configurazione utente

**Template disponibili:**
- `"lead_generation"` - Ottimizzato per cattura lead
- `"product_launch"` - Per lanci prodotto
- `"sales_page"` - Per pagine di vendita
- `"event_registration"` - Per eventi
- `"app_download"` - Per download app

**Esempio:**
```python
# Ottieni template lead generation
hero_config = HeroComponent.get_template_by_type("lead_generation", {
    "title": "Trasforma il Tuo Business",
    "subtitle": "La strategia che funziona davvero",
    "cta_text": "Scarica Gratis",
    "cta_url": "#form"
})

# Usa nel builder
builder.add_hero_section("lead_generation", hero_config)
```

---

### HeroTemplate

Definizione di un template hero.

```python
@dataclass
class HeroTemplate:
    name: str
    description: str
    conversion_focus: str
    config: Dict[str, Any]
```

**Parametri:**
- `name` (str): Nome del template
- `description` (str): Descrizione dell'uso ottimale
- `conversion_focus` (str): Focus di conversione
- `config` (Dict[str, Any]): Configurazione template

---

## Enums & Constants

### ComponentType

Tipi di componenti disponibili.

```python
class ComponentType(Enum):
    HERO = "hero"
    FEATURES = "features"
    TESTIMONIALS = "testimonials"
    PRICING = "pricing"
    CTA = "cta"
    FORM = "form"
    FOOTER = "footer"
```

### InteractionType

Tipi di interazioni JavaScript.

```python
class InteractionType(Enum):
    FORM_VALIDATION = "form_validation"
    SMOOTH_SCROLL = "smooth_scroll"
    LAZY_LOADING = "lazy_loading"
    MODAL = "modal"
    COUNTDOWN_TIMER = "countdown_timer"
    STICKY_CTA = "sticky_cta"
    PROGRESS_BAR = "progress_bar"
    ACCORDION = "accordion"
    TABS = "tabs"
    CAROUSEL = "carousel"
```

### BreakpointSize

Breakpoint per responsive design.

```python
class BreakpointSize(Enum):
    XS = "xs"   # 0px+
    SM = "sm"   # 576px+
    MD = "md"   # 768px+
    LG = "lg"   # 992px+
    XL = "xl"   # 1200px+
    XXL = "xxl" # 1400px+
```

---

## Utility Functions

### create_landing_page()

Funzione di convenienza per creare landing page rapidamente.

```python
def create_landing_page(
    title: str,
    description: str,
    hero_type: str = "lead_generation",
    hero_config: Dict[str, Any] = None,
    output_dir: str = "landing_page_output"
) -> LandingPageBuilder:
```

**Parametri:**
- `title` (str): Titolo della pagina
- `description` (str): Meta description  
- `hero_type` (str): Tipo di hero (default: "lead_generation")
- `hero_config` (Dict, optional): Configurazione hero personalizzata
- `output_dir` (str): Directory di output (default: "landing_page_output")

**Ritorna:** Istanza di LandingPageBuilder configurata

**Esempio:**
```python
builder = create_landing_page(
    title="Corso Online Marketing",
    description="Il corso più completo del settore",
    hero_type="sales_page",
    hero_config={
        "title": "Da Zero a Marketing Expert",
        "sale_price": "397€",
        "original_price": "997€"
    }
)
```

---

## Examples

### Esempio Completo - E-commerce Product Page

```python
from builder import LandingPageBuilder, LandingPageConfig
from core.html_generator import SEOConfig, AccessibilityConfig
from core.css_framework import ColorScheme, Typography
from core.js_engine import JSConfig, ValidationRule, InteractionType

# Configurazione completa e-commerce
seo_config = SEOConfig(
    title="Smartwatch Pro - Tecnologia Avanzata al Polso",
    description="Il smartwatch più avanzato del 2024. GPS, monitoraggio salute, batteria 7 giorni. Spedizione gratuita.",
    keywords="smartwatch, orologio intelligente, fitness tracker, GPS",
    og_title="⌚ Smartwatch Pro - Il Futuro al Tuo Polso",
    og_description="Tecnologia avanzata, design elegante, prestazioni eccezionali",
    og_image="https://shop.example.com/images/smartwatch-og.jpg",
    canonical_url="https://shop.example.com/smartwatch-pro"
)

# Schema colori e-commerce
ecommerce_colors = ColorScheme(
    primary="#1a56db",      # Blu affidabilità
    secondary="#9333ea",    # Viola premium
    accent="#ea580c",       # Orange urgenza acquisto
    success="#16a34a",      # Verde disponibilità
    warning="#ca8a04",      # Giallo scorte limitate
    error="#dc2626",        # Rosso non disponibile
    neutral_50="#f9fafb",
    neutral_100="#f3f4f6",
    neutral_200="#e5e7eb",
    neutral_300="#d1d5db",
    neutral_400="#9ca3af",
    neutral_500="#6b7280",
    neutral_600="#4b5563",
    neutral_700="#374151",
    neutral_800="#1f2937",
    neutral_900="#111827"
)

# Configurazione JavaScript e-commerce
js_config = JSConfig(
    enable_analytics=True,      # Track conversioni
    lazy_loading=True,          # Immagini prodotto
    smooth_scroll=True,         # Navigazione fluida
    form_validation=True,       # Validazione checkout
    progressive_enhancement=True # Fallback senza JS
)

# Config completa
config = LandingPageConfig(
    title="Smartwatch Pro - Tecnologia Avanzata al Polso",
    description="Il smartwatch più avanzato per professionisti e sportivi",
    target_audience="Professionisti, sportivi, tech enthusiast 25-45 anni",
    conversion_goal="Vendita diretta smartwatch con upsell accessori",
    seo_config=seo_config,
    color_scheme=ecommerce_colors,
    js_config=js_config,
    output_directory="smartwatch_product_page",
    include_analytics=True,
    minify_output=True
)

# Inizializza builder
builder = LandingPageBuilder(config)

# Hero prodotto con gallery
builder.add_hero_section("product_launch", {
    "title": "Smartwatch Pro 2024",
    "subtitle": "La Tecnologia del Futuro, Oggi al Tuo Polso",
    "media_type": "image",
    "media_url": "assets/images/smartwatch-hero.jpg",
    "primary_cta": "Acquista Ora - 299€",
    "secondary_cta": "Scopri le Caratteristiche",
    "cta_url": "#buy-now",
    "demo_url": "#features",
    "launch_date": "2024-12-31T23:59:59",
    "social_proof": {
        "user_count": "10.000+ venduti",
        "rating": "4.9/5 ⭐",
        "featured_logos": ["tech-review.png", "fitness-magazine.png"]
    }
})

# Features prodotto dettagliate
builder.add_features_section({
    "title": "Caratteristiche Avanzate",
    "subtitle": "Tutto quello che cerchi in un smartwatch premium",
    "features": [
        {
            "title": "Batteria 7 Giorni",
            "description": "Non preoccuparti mai più di rimanere senza carica. Batteria ultra-efficiente per una settimana di autonomia.",
            "icon": "🔋"
        },
        {
            "title": "GPS Precision+",
            "description": "Tracking preciso per running, ciclismo e outdoor. Mappe offline integrate per avventure senza limiti.",
            "icon": "🛰️"
        },
        {
            "title": "Monitoraggio Salute 24/7", 
            "description": "Frequenza cardiaca, ossigeno nel sangue, stress, sonno. La tua salute sempre sotto controllo.",
            "icon": "❤️"
        },
        {
            "title": "Resistente all'Acqua 10ATM",
            "description": "Nuoto, immersioni, doccia. Progettato per accompagnarti ovunque, anche sott'acqua.",
            "icon": "💧"
        },
        {
            "title": "120+ Sport Modes",
            "description": "Dalla corsa al tennis, dal ciclismo al surf. Ogni sport ha le sue metriche specifiche.",
            "icon": "🏃"
        },
        {
            "title": "Display Always-On AMOLED",
            "description": "Schermo brillante e nitido anche sotto il sole. Touch responsivo con vetro Gorilla Glass.",
            "icon": "📱"
        }
    ]
})

# Testimonial verificati
builder.add_testimonials_section({
    "title": "Perché Scegliere Smartwatch Pro",
    "testimonials": [
        {
            "text": "Dopo 6 mesi di uso intensivo posso dire che è il miglior smartwatch mai posseduto. Batteria incredibile e GPS precisissimo.",
            "author": "Marco Bianchi",
            "role": "Maratoneta",
            "company": "Running Club Milano",
            "rating": 5
        },
        {
            "text": "Lo uso per lavoro e sport. Le notifiche sono perfette, il design elegante. Ottimo rapporto qualità-prezzo.",
            "author": "Laura Rossi", 
            "role": "Manager",
            "company": "Tech Solutions",
            "rating": 5
        },
        {
            "text": "Il monitoraggio del sonno è fantastico. Finalmente capisco come migliorare il mio riposo. Consigliatissimo!",
            "author": "Giuseppe Verde",
            "role": "Personal Trainer",
            "rating": 5
        }
    ]
})

# Sezione pricing con urgenza
builder.add_pricing_section({
    "title": "Scegli la Tua Versione",
    "subtitle": "Spedizione gratuita in 24h • Garanzia 2 anni • Reso gratuito 30 giorni",
    "plans": [
        {
            "name": "Smartwatch Pro",
            "price": "299€",
            "original_price": "399€",
            "savings": "100€ di sconto",
            "features": [
                "✅ Display AMOLED 1.4\"",
                "✅ GPS integrato", 
                "✅ Batteria 7 giorni",
                "✅ 120+ modalità sport",
                "✅ Monitoraggio salute 24/7",
                "✅ Resistente all'acqua 10ATM",
                "✅ Garanzia 2 anni"
            ],
            "cta_text": "Acquista Ora - 299€",
            "is_featured": True,
            "stock_info": "🟢 Disponibile - Spedizione oggi"
        },
        {
            "name": "Pro + Accessori Bundle",
            "price": "399€",
            "original_price": "549€", 
            "savings": "150€ di sconto",
            "features": [
                "✅ Tutto del piano precedente",
                "✅ Cinturino sport extra",
                "✅ Cinturino elegante in pelle",
                "✅ Caricatore wireless",
                "✅ Pellicola protettiva",
                "✅ Custodia da viaggio",
                "✅ Setup personalizzato gratuito"
            ],
            "cta_text": "Bundle Completo - 399€",
            "is_featured": false,
            "stock_info": "🟡 Solo 24 kit disponibili"
        }
    ]
})

# Form checkout ottimizzato
builder.add_form_section({
    "title": "Completa il Tuo Acquisto",
    "subtitle": "Pagamento sicuro SSL • Spedizione gratuita • Garanzia 2 anni",
    "action": "/ecommerce/checkout",
    "fields": [
        {
            "name": "prodotto",
            "type": "select",
            "label": "Versione Scelta",
            "options": [
                {"value": "smartwatch-pro", "text": "Smartwatch Pro - 299€"},
                {"value": "pro-bundle", "text": "Pro + Accessori Bundle - 399€"}
            ],
            "required": True
        },
        {
            "name": "colore",
            "type": "select", 
            "label": "Colore",
            "options": [
                {"value": "nero", "text": "Nero Elegante"},
                {"value": "argento", "text": "Argento Classico"},
                {"value": "blu", "text": "Blu Navy"},
                {"value": "rosa", "text": "Rosa Gold"}
            ],
            "required": True
        },
        {
            "name": "nome",
            "type": "text",
            "label": "Nome Completo",
            "placeholder": "Mario Rossi",
            "required": True
        },
        {
            "name": "email",
            "type": "email",
            "label": "Email",
            "placeholder": "mario@email.com",
            "required": True,
            "help_text": "Per ricevere aggiornamenti spedizione"
        },
        {
            "name": "telefono", 
            "type": "tel",
            "label": "Telefono",
            "placeholder": "+39 333 123 4567",
            "required": True,
            "help_text": "Per comunicazioni urgenti sulla spedizione"
        },
        {
            "name": "indirizzo",
            "type": "text",
            "label": "Indirizzo Completo",
            "placeholder": "Via Roma 123, 20100 Milano MI",
            "required": True
        },
        {
            "name": "newsletter",
            "type": "checkbox",
            "label": "Iscriviti alla newsletter per offerte esclusive e novità tech"
        },
        {
            "name": "privacy",
            "type": "checkbox", 
            "label": "Accetto i termini di vendita e la privacy policy",
            "required": True
        }
    ],
    "submit_text": "Completa Acquisto Sicuro 🔒",
    "privacy_notice": "Pagamento sicuro con crittografia SSL. Dati protetti secondo GDPR. Spedizione gratuita in 24-48h."
})

# Aggiungi interazioni e-commerce avanzate
builder.add_interaction(InteractionType.COUNTDOWN_TIMER, {
    "target": ".pricing-section",
    "end_date": "2024-12-25T23:59:59",
    "message": "🎄 Offerta Natale termina tra:"
})

builder.add_interaction(InteractionType.STICKY_CTA, {
    "text": "Acquista Ora - 299€ 🛒",
    "url": "#buy-now",
    "show_after_scroll": 600,
    "style": "ecommerce"
})

builder.add_interaction(InteractionType.MODAL, {
    "trigger": "[data-modal='size-guide']",
    "target": "#size-guide-modal",
    "title": "Guida alle Taglie"
})

# Footer e-commerce completo
builder.add_footer({
    "company_info": {
        "name": "TechStore Italia",
        "description": "I migliori prodotti tech, spedizione gratuita, garanzia italiana.",
        "address": "Via Milano 123, 20100 Milano (MI) • P.IVA 12345678901"
    },
    "links": [
        {"text": "Chi Siamo", "url": "/about"},
        {"text": "Spedizioni", "url": "/shipping"},
        {"text": "Resi", "url": "/returns"},
        {"text": "Garanzia", "url": "/warranty"},
        {"text": "Contatti", "url": "/contact"},
        {"text": "Privacy", "url": "/privacy"},
        {"text": "Termini", "url": "/terms"}
    ],
    "social_links": [
        {"platform": "Instagram", "url": "https://instagram.com/techstore", "icon": "📸"},
        {"platform": "Facebook", "url": "https://facebook.com/techstore", "icon": "📘"},
        {"platform": "YouTube", "url": "https://youtube.com/techstore", "icon": "📺"},
        {"platform": "TikTok", "url": "https://tiktok.com/@techstore", "icon": "🎵"}
    ],
    "copyright": "© 2024 TechStore Italia. Tutti i diritti riservati. • Made with ❤️ in Italy"
})

# Genera tutto
files = builder.generate_files()
performance = builder.generate_performance_report()
validation = builder.validate_output()

print("🛒 E-commerce product page generata!")
print(f"📄 HTML: {files['html']}")
print(f"🎨 CSS: {files['css']}")  
print(f"⚡ JS: {files['js']}")
print(f"📊 Dimensione: {performance['total_size']} bytes")
print(f"🏆 Accessibilità: {validation['accessibility_score']}/100")
print(f"🔍 SEO: {validation['seo_score']}/100")
print(f"⚡ Performance: {validation['performance_score']}/100")
```

---

Questa API Reference fornisce una documentazione completa di tutti i componenti del Landing Page Builder System. Per esempi più specifici e guide dettagliate, consulta la [Getting Started Guide](GETTING_STARTED.md) e l'[Architecture Overview](ARCHITECTURE.md).