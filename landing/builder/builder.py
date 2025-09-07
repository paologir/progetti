"""
Landing Page Builder - Main Interface

Complete landing page generation system with HTML, CSS, and JavaScript
optimized for conversions and Core Web Vitals performance.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core import HTMLGenerator, CSSFramework, JSEngine
from core.html_generator import SEOConfig, AccessibilityConfig, ComponentType
from core.css_framework import ColorScheme, Typography
from core.js_engine import JSConfig, ValidationRule, InteractionType
from templates.components.hero import HeroComponent


@dataclass
class LandingPageConfig:
    # Basic Information
    title: str
    description: str
    target_audience: str
    conversion_goal: str
    
    # SEO & Meta
    seo_config: SEOConfig
    
    # Design & Styling
    color_scheme: Optional[ColorScheme] = None
    typography: Optional[Typography] = None
    
    # Functionality
    accessibility_config: Optional[AccessibilityConfig] = None
    js_config: Optional[JSConfig] = None
    
    # Output Settings
    output_directory: str = "output"
    include_analytics: bool = True
    minify_output: bool = True


class LandingPageBuilder:
    """
    Main builder class for creating complete landing pages.
    """
    
    def __init__(self, config: LandingPageConfig):
        self.config = config
        
        # Initialize core engines
        self.html_generator = HTMLGenerator(
            seo_config=config.seo_config,
            accessibility_config=config.accessibility_config
        )
        
        self.css_framework = CSSFramework(
            color_scheme=config.color_scheme,
            typography=config.typography
        )
        
        self.js_engine = JSEngine(
            config=config.js_config or JSConfig()
        )
        
        # Ensure output directory exists
        os.makedirs(config.output_directory, exist_ok=True)
        os.makedirs(f"{config.output_directory}/assets/css", exist_ok=True)
        os.makedirs(f"{config.output_directory}/assets/js", exist_ok=True)
        os.makedirs(f"{config.output_directory}/assets/images", exist_ok=True)
    
    def add_hero_section(self, template_type: str, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add hero section using predefined template."""
        hero_config = HeroComponent.get_template_by_type(template_type, config)
        self.html_generator.add_component(ComponentType.HERO, hero_config)
        return self
    
    def add_features_section(self, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add features/benefits section."""
        self.html_generator.add_component(ComponentType.FEATURES, config)
        return self
    
    def add_testimonials_section(self, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add testimonials/social proof section."""
        self.html_generator.add_component(ComponentType.TESTIMONIALS, config)
        return self
    
    def add_pricing_section(self, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add pricing section."""
        self.html_generator.add_component(ComponentType.PRICING, config)
        return self
    
    def add_cta_section(self, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add call-to-action section."""
        self.html_generator.add_component(ComponentType.CTA, config)
        return self
    
    def add_form_section(self, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add form section with validation."""
        self.html_generator.add_component(ComponentType.FORM, config)
        
        # Add validation rules for form fields
        for field in config.get("fields", []):
            if field.get("required"):
                rule = ValidationRule(
                    field_name=field["name"],
                    rule_type="required",
                    message=f"{field.get('label', field['name'])} è obbligatorio"
                )
                self.js_engine.add_validation_rule(rule)
            
            if field.get("type") == "email":
                rule = ValidationRule(
                    field_name=field["name"],
                    rule_type="email",
                    message="Inserisci un indirizzo email valido"
                )
                self.js_engine.add_validation_rule(rule)
        
        return self
    
    def add_footer(self, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add footer section."""
        self.html_generator.add_component(ComponentType.FOOTER, config)
        return self
    
    def add_interaction(self, interaction_type: InteractionType, config: Dict[str, Any]) -> 'LandingPageBuilder':
        """Add interactive JavaScript component."""
        self.js_engine.add_interaction(interaction_type, config)
        return self
    
    def generate_files(self) -> Dict[str, str]:
        """Generate all landing page files."""
        files = {}
        
        # Generate HTML
        html_content = self.html_generator.generate_complete_page()
        html_file = f"{self.config.output_directory}/index.html"
        
        if self.config.minify_output:
            html_content = self._minify_html(html_content)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        files['html'] = html_file
        
        # Generate CSS
        css_content = self.css_framework.generate_complete_css()
        css_file = f"{self.config.output_directory}/assets/css/framework.css"
        
        if self.config.minify_output:
            css_content = self._minify_css(css_content)
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        files['css'] = css_file
        
        # Generate JavaScript
        js_content = self.js_engine.generate_complete_js()
        js_file = f"{self.config.output_directory}/assets/js/core.js"
        
        if self.config.minify_output:
            js_content = self._minify_js(js_content)
        
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        files['js'] = js_file
        
        # Generate additional files
        files.update(self._generate_additional_files())
        
        return files
    
    def _generate_additional_files(self) -> Dict[str, str]:
        """Generate additional files like README, config files, etc."""
        files = {}
        
        # Generate README
        readme_content = self._generate_readme()
        readme_file = f"{self.config.output_directory}/README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files['readme'] = readme_file
        
        # Generate .gitignore
        gitignore_content = self._generate_gitignore()
        gitignore_file = f"{self.config.output_directory}/.gitignore"
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        files['gitignore'] = gitignore_file
        
        # Generate robots.txt
        robots_content = self._generate_robots_txt()
        robots_file = f"{self.config.output_directory}/robots.txt"
        with open(robots_file, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        files['robots'] = robots_file
        
        # Generate sitemap.xml
        sitemap_content = self._generate_sitemap()
        sitemap_file = f"{self.config.output_directory}/sitemap.xml"
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        files['sitemap'] = sitemap_file
        
        return files
    
    def _generate_readme(self) -> str:
        """Generate project README."""
        return f"""# {self.config.title}

## Descrizione
{self.config.description}

## Target Audience
{self.config.target_audience}

## Obiettivo di Conversione
{self.config.conversion_goal}

## Struttura del Progetto

```
{self.config.output_directory}/
├── index.html              # Pagina principale
├── assets/
│   ├── css/
│   │   └── framework.css   # CSS framework ottimizzato
│   ├── js/
│   │   └── core.js        # JavaScript per interazioni
│   └── images/            # Immagini e media
├── README.md              # Questo file
├── robots.txt             # Configurazione SEO per bot
└── sitemap.xml           # Mappa del sito per SEO

```

## Caratteristiche

### ✅ Ottimizzazioni Implementate
- **SEO**: Meta tags, structured data, sitemap
- **Performance**: Core Web Vitals ottimizzati, lazy loading
- **Accessibilità**: WCAG compliance, skip links, ARIA labels
- **Responsive**: Mobile-first design con breakpoint ottimizzati
- **Analytics**: Tracking conversioni e comportamento utenti
- **Validazione**: Form validation in tempo reale
- **Sicurezza**: CSP headers, sanitizzazione input

### 🎯 Conversion Optimization
- Design ottimizzato per conversioni
- CTA strategicamente posizionati
- Trust signals integrati
- A/B testing ready
- Performance monitoring

## Come Utilizzare

### 1. Hosting Statico
Carica tutti i file su qualsiasi servizio di hosting statico:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

### 2. Server Web
Configura il tuo server web per servire i file statici.

### 3. Analytics Setup
1. Sostituisci `GA_MEASUREMENT_ID` nel JavaScript con il tuo ID Google Analytics
2. Configura Facebook Pixel se necessario
3. Imposta conversion tracking

### 4. Personalizzazione
- Modifica colori nel CSS (`--color-primary`, `--color-secondary`)
- Aggiorna contenuti nell'HTML
- Personalizza validazioni nel JavaScript

## Testing & Optimization

### Performance Testing
- Google PageSpeed Insights
- GTmetrix
- WebPageTest

### A/B Testing
- Google Optimize
- Optimizely
- VWO

### Analytics
- Google Analytics 4
- Google Search Console
- Facebook Analytics

## Supporto
Per domande o problemi, contatta il team di sviluppo.

---
Generato automaticamente con Landing Page Builder
"""
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""
        return """# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Dependencies
node_modules/
bower_components/

# Build outputs
dist/
build/

# Environment files
.env
.env.local
.env.production

# Cache
.cache/
*.tmp

# Analytics
.analytics/
"""
    
    def _generate_robots_txt(self) -> str:
        """Generate robots.txt for SEO."""
        base_url = self.config.seo_config.canonical_url or "https://example.com"
        return f"""User-agent: *
Allow: /

# Sitemaps
Sitemap: {base_url}/sitemap.xml

# Disallow sensitive areas
Disallow: /admin/
Disallow: /api/
Disallow: /private/
Disallow: /.git/
"""
    
    def _generate_sitemap(self) -> str:
        """Generate sitemap.xml for SEO."""
        base_url = self.config.seo_config.canonical_url or "https://example.com"
        from datetime import datetime
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>
"""
    
    def _minify_html(self, html: str) -> str:
        """Basic HTML minification."""
        import re
        
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html)
        
        # Remove comments (but keep IE conditionals)
        html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)
        
        # Remove whitespace around tags
        html = re.sub(r'>\s+<', '><', html)
        
        return html.strip()
    
    def _minify_css(self, css: str) -> str:
        """Basic CSS minification."""
        import re
        
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        
        # Remove extra whitespace
        css = re.sub(r'\s+', ' ', css)
        
        # Remove whitespace around certain characters
        css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)
        
        return css.strip()
    
    def _minify_js(self, js: str) -> str:
        """Basic JavaScript minification."""
        import re
        
        # Remove single-line comments (but keep URLs)
        js = re.sub(r'(?<!:)//(?![^\r\n]*http).*', '', js)
        
        # Remove multi-line comments
        js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
        
        # Remove extra whitespace (but preserve strings)
        js = re.sub(r'(?<!["\'])\s+(?!["\'])', ' ', js)
        
        return js.strip()
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate performance analysis report."""
        report = {
            "html_size": 0,
            "css_size": 0,
            "js_size": 0,
            "total_size": 0,
            "components_count": len(self.html_generator.components),
            "validation_rules_count": len(self.js_engine.validation_rules),
            "interactions_count": len(self.js_engine.interactions),
            "accessibility_features": [],
            "seo_features": [],
            "performance_features": []
        }
        
        # Calculate file sizes if files exist
        try:
            html_file = f"{self.config.output_directory}/index.html"
            if os.path.exists(html_file):
                report["html_size"] = os.path.getsize(html_file)
            
            css_file = f"{self.config.output_directory}/assets/css/framework.css"
            if os.path.exists(css_file):
                report["css_size"] = os.path.getsize(css_file)
            
            js_file = f"{self.config.output_directory}/assets/js/core.js"
            if os.path.exists(js_file):
                report["js_size"] = os.path.getsize(js_file)
            
            report["total_size"] = report["html_size"] + report["css_size"] + report["js_size"]
        except Exception:
            pass
        
        # Analyze features
        if self.config.accessibility_config:
            if self.config.accessibility_config.skip_navigation:
                report["accessibility_features"].append("Skip Navigation Links")
            if self.config.accessibility_config.screen_reader_optimization:
                report["accessibility_features"].append("Screen Reader Optimization")
        
        if self.config.seo_config:
            report["seo_features"].append("Meta Tags Optimization")
            report["seo_features"].append("Structured Data")
            if self.config.seo_config.canonical_url:
                report["seo_features"].append("Canonical URL")
        
        if self.config.js_config:
            if self.config.js_config.lazy_loading:
                report["performance_features"].append("Lazy Loading")
            if self.config.js_config.enable_analytics:
                report["performance_features"].append("Analytics Integration")
        
        return report
    
    def validate_output(self) -> Dict[str, Any]:
        """Validate the generated output for common issues."""
        validation_results = {
            "html_valid": True,
            "css_valid": True,
            "js_valid": True,
            "accessibility_score": 0,
            "seo_score": 0,
            "performance_score": 0,
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Basic validation checks
        html_file = f"{self.config.output_directory}/index.html"
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
                # Check for common HTML issues
                if '<title>' not in html_content:
                    validation_results["issues"].append("Missing page title")
                    validation_results["html_valid"] = False
                
                if 'lang=' not in html_content:
                    validation_results["warnings"].append("Missing language attribute")
                
                if 'alt=' not in html_content and '<img' in html_content:
                    validation_results["warnings"].append("Images may be missing alt attributes")
        
        # Calculate scores (simplified)
        issues_count = len(validation_results["issues"])
        warnings_count = len(validation_results["warnings"])
        
        validation_results["accessibility_score"] = max(0, 100 - (issues_count * 20) - (warnings_count * 5))
        validation_results["seo_score"] = max(0, 100 - (issues_count * 15) - (warnings_count * 3))
        validation_results["performance_score"] = max(0, 100 - (issues_count * 10) - (warnings_count * 2))
        
        return validation_results


# Convenience function for quick page generation
def create_landing_page(
    title: str,
    description: str,
    hero_type: str = "lead_generation",
    hero_config: Dict[str, Any] = None,
    output_dir: str = "landing_page_output"
) -> LandingPageBuilder:
    """
    Quick function to create a basic landing page.
    
    Args:
        title: Page title
        description: Meta description
        hero_type: Type of hero section
        hero_config: Hero section configuration  
        output_dir: Output directory
    
    Returns:
        LandingPageBuilder instance
    """
    seo_config = SEOConfig(
        title=title,
        description=description,
        og_title=title,
        og_description=description
    )
    
    config = LandingPageConfig(
        title=title,
        description=description,
        target_audience="Professionisti e aziende",
        conversion_goal="Generazione lead qualificati",
        seo_config=seo_config,
        output_directory=output_dir
    )
    
    builder = LandingPageBuilder(config)
    
    # Add hero section
    builder.add_hero_section(hero_type, hero_config or {})
    
    return builder


if __name__ == "__main__":
    # Example usage
    builder = create_landing_page(
        title="Trasforma il Tuo Business Online",
        description="Scopri come aumentare le conversioni del 300% con la nostra strategia digitale comprovata",
        hero_type="lead_generation",
        hero_config={
            "title": "Raddoppia le Tue Conversioni in 30 Giorni",
            "subtitle": "La strategia segreta usata da oltre 1000 aziende italiane",
            "cta_text": "Scarica la Guida Gratuita"
        }
    )
    
    # Add more sections
    builder.add_features_section({
        "title": "Perché Scegliere la Nostra Soluzione",
        "features": [
            {
                "title": "Risultati Garantiti",
                "description": "Aumento delle conversioni del 200-400% in 60 giorni",
                "icon": "🎯"
            },
            {
                "title": "Supporto Completo", 
                "description": "Team di esperti dedicato al tuo successo",
                "icon": "🚀"
            },
            {
                "title": "Tecnologia Avanzata",
                "description": "Strumenti all'avanguardia per l'ottimizzazione",
                "icon": "⚡"
            },
            {
                "title": "Sicurezza Certificata",
                "description": "Protezione dati conforme GDPR e standard internazionali",
                "icon": "🔒"
            }
        ]
    })
    
    builder.add_cta_section({
        "title": "Pronto a Iniziare?",
        "description": "Unisciti a migliaia di imprenditori che hanno già trasformato il loro business",
        "primary_cta": {
            "text": "Inizia Ora Gratuitamente",
            "url": "#contact"
        }
    })
    
    # Add contact form
    builder.add_form_section({
        "id": "contact",
        "title": "Richiedi una Consulenza Gratuita",
        "subtitle": "Compila il form e ti ricontatteremo entro 24 ore",
        "description": "I nostri esperti analizzeranno gratuitamente la tua situazione e ti proporranno la strategia migliore per il tuo business.",
        "fields": [
            {
                "name": "nome",
                "type": "text",
                "label": "Nome e Cognome",
                "placeholder": "Inserisci il tuo nome completo",
                "required": True
            },
            {
                "name": "email",
                "type": "email", 
                "label": "Email",
                "placeholder": "tua@email.com",
                "required": True,
                "help_text": "Useremo questa email per ricontattarti"
            },
            {
                "name": "telefono",
                "type": "tel",
                "label": "Telefono",
                "placeholder": "+39 123 456 7890",
                "required": False,
                "help_text": "Opzionale - per un contatto più rapido"
            },
            {
                "name": "azienda",
                "type": "text",
                "label": "Nome Azienda",
                "placeholder": "La tua azienda",
                "required": False
            },
            {
                "name": "settore",
                "type": "select",
                "label": "Settore di Attività",
                "required": False,
                "options": [
                    {"value": "", "text": "Seleziona il tuo settore"},
                    {"value": "ecommerce", "text": "E-commerce"},
                    {"value": "servizi", "text": "Servizi Professionali"},
                    {"value": "tecnologia", "text": "Tecnologia/Software"},
                    {"value": "consulenza", "text": "Consulenza"},
                    {"value": "manifattura", "text": "Manifattura"},
                    {"value": "altro", "text": "Altro"}
                ]
            },
            {
                "name": "messaggio",
                "type": "textarea",
                "label": "Messaggio",
                "placeholder": "Raccontaci del tuo progetto e dei tuoi obiettivi...",
                "required": True,
                "help_text": "Più dettagli fornisci, migliore sarà la nostra proposta"
            }
        ],
        "submit_text": "Richiedi Consulenza Gratuita",
        "privacy_notice": "Rispettiamo la tua privacy. I tuoi dati saranno utilizzati solo per ricontattarti e non saranno mai condivisi con terzi. Puoi cancellarti in qualsiasi momento."
    })
    
    # Add footer
    builder.add_footer({
        "company_info": {
            "name": "La Tua Azienda",
            "address": "Via Roma 123, 00100 Roma (RM)",
            "phone": "+39 06 1234567",
            "email": "info@tuaazienda.it"
        },
        "links": [
            {"text": "Privacy Policy", "url": "/privacy"},
            {"text": "Termini di Servizio", "url": "/terms"},
            {"text": "Contatti", "url": "/contact"},
            {"text": "Blog", "url": "/blog"}
        ],
        "social_links": [
            {"platform": "facebook", "url": "https://facebook.com/tuaazienda"},
            {"platform": "twitter", "url": "https://twitter.com/tuaazienda"},
            {"platform": "linkedin", "url": "https://linkedin.com/company/tuaazienda"},
            {"platform": "instagram", "url": "https://instagram.com/tuaazienda"}
        ],
        "copyright": "© 2024 La Tua Azienda. Tutti i diritti riservati."
    })
    
    # Generate files
    files = builder.generate_files()
    report = builder.generate_performance_report()
    validation = builder.validate_output()
    
    print("Landing page generata con successo!")
    print(f"File creati: {list(files.keys())}")
    print(f"Dimensione totale: {report['total_size']} bytes")
    print(f"Score accessibilità: {validation['accessibility_score']}/100")