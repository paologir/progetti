"""
HTML Generator - Semantic HTML5 with WCAG Compliance

Generates accessible, semantic HTML structure for landing pages
following modern web standards and conversion optimization principles.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ComponentType(Enum):
    HERO = "hero"
    FEATURES = "features"
    TESTIMONIALS = "testimonials"
    PRICING = "pricing"
    CTA = "cta"
    FORM = "form"
    FOOTER = "footer"


@dataclass
class SEOConfig:
    title: str
    description: str
    keywords: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None


@dataclass
class AccessibilityConfig:
    lang: str = "it"
    skip_navigation: bool = True
    high_contrast_mode: bool = False
    screen_reader_optimization: bool = True


class HTMLGenerator:
    """
    Core HTML generator for landing pages with semantic structure
    and accessibility compliance.
    """
    
    def __init__(self, seo_config: SEOConfig, accessibility_config: AccessibilityConfig = None):
        self.seo_config = seo_config
        self.accessibility_config = accessibility_config or AccessibilityConfig()
        self.components: List[Dict[str, Any]] = []
        
    def add_component(self, component_type: ComponentType, config: Dict[str, Any]) -> None:
        """Add a component to the landing page structure."""
        self.components.append({
            "type": component_type,
            "config": config,
            "id": f"{component_type.value}_{len(self.components)}"
        })
    
    def generate_head(self) -> str:
        """Generate semantic HTML head section with SEO and performance optimization."""
        head_parts = [
            '<!DOCTYPE html>',
            f'<html lang="{self.accessibility_config.lang}">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <meta http-equiv="X-UA-Compatible" content="IE=edge">',
            f'    <title>{self.seo_config.title}</title>',
            f'    <meta name="description" content="{self.seo_config.description}">',
        ]
        
        # SEO Meta Tags
        if self.seo_config.keywords:
            head_parts.append(f'    <meta name="keywords" content="{self.seo_config.keywords}">')
        
        if self.seo_config.canonical_url:
            head_parts.append(f'    <link rel="canonical" href="{self.seo_config.canonical_url}">')
        
        # Open Graph Meta Tags
        og_title = self.seo_config.og_title or self.seo_config.title
        og_description = self.seo_config.og_description or self.seo_config.description
        
        head_parts.extend([
            f'    <meta property="og:title" content="{og_title}">',
            f'    <meta property="og:description" content="{og_description}">',
            '    <meta property="og:type" content="website">',
        ])
        
        if self.seo_config.og_image:
            head_parts.append(f'    <meta property="og:image" content="{self.seo_config.og_image}">')
        
        # Twitter Card Meta Tags
        head_parts.extend([
            '    <meta name="twitter:card" content="summary_large_image">',
            f'    <meta name="twitter:title" content="{og_title}">',
            f'    <meta name="twitter:description" content="{og_description}">',
        ])
        
        # Performance and Security Headers
        head_parts.extend([
            '    <meta name="robots" content="index, follow">',
            '    <meta name="theme-color" content="#ffffff">',
            '    <link rel="preconnect" href="https://fonts.googleapis.com">',
            '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '    <link rel="dns-prefetch" href="//www.google-analytics.com">',
        ])
        
        # CSS Links
        head_parts.extend([
            '    <link rel="stylesheet" href="assets/css/framework.css">',
            '    <link rel="stylesheet" href="assets/css/components/all.css">',
        ])
        
        # Structured Data
        structured_data = self._generate_structured_data()
        if structured_data:
            head_parts.append(f'    <script type="application/ld+json">{structured_data}</script>')
        
        head_parts.append('</head>')
        return '\n'.join(head_parts)
    
    def generate_body_start(self) -> str:
        """Generate body opening with accessibility features."""
        body_parts = ['<body>']
        
        # Skip Navigation Link for Screen Readers
        if self.accessibility_config.skip_navigation:
            body_parts.extend([
                '    <a href="#main-content" class="skip-link">Salta al contenuto principale</a>',
            ])
        
        # High Contrast Mode Toggle
        if self.accessibility_config.high_contrast_mode:
            body_parts.extend([
                '    <button id="contrast-toggle" class="accessibility-toggle" aria-label="Attiva/Disattiva modalità alto contrasto">',
                '        <span class="visually-hidden">Alto Contrasto</span>',
                '    </button>',
            ])
        
        return '\n'.join(body_parts)
    
    def generate_hero_section(self, config: Dict[str, Any]) -> str:
        """Generate semantic hero section with conversion optimization."""
        hero_html = [
            '    <header class="hero-section" role="banner" aria-labelledby="hero-heading">',
            '        <div class="hero-container">',
            '            <div class="hero-content">',
            f'                <h1 id="hero-heading" class="hero-title">{config.get("title", "")}</h1>',
        ]
        
        if config.get("subtitle"):
            hero_html.append(f'                <p class="hero-subtitle">{config["subtitle"]}</p>')
        
        if config.get("description"):
            hero_html.append(f'                <div class="hero-description">{config["description"]}</div>')
        
        # Call to Action Button
        if config.get("cta"):
            cta = config["cta"]
            hero_html.extend([
                '                <div class="hero-cta">',
                f'                    <a href="{cta.get("url", "#")}" class="btn btn-primary btn-lg" ',
                f'                       role="button" aria-describedby="cta-description">',
                f'                        {cta.get("text", "Inizia Ora")}',
                '                    </a>',
            ])
            
            if cta.get("description"):
                hero_html.append(f'                    <p id="cta-description" class="cta-description">{cta["description"]}</p>')
            
            hero_html.append('                </div>')
        
        # Hero Image/Video
        if config.get("media"):
            media = config["media"]
            if media.get("type") == "image":
                hero_html.extend([
                    '            </div>',
                    '            <div class="hero-media">',
                    f'                <img src="{media["url"]}" alt="{media.get("alt", "")}" ',
                    '                     class="hero-image" loading="eager" fetchpriority="high">',
                ])
            elif media.get("type") == "video":
                hero_html.extend([
                    '            </div>',
                    '            <div class="hero-media">',
                    '                <video class="hero-video" autoplay muted loop playsinline>',
                    f'                    <source src="{media["url"]}" type="video/mp4">',
                    '                    <p>Il tuo browser non supporta il video HTML5.</p>',
                    '                </video>',
                ])
        
        hero_html.extend([
            '            </div>',
            '        </div>',
            '    </header>',
        ])
        
        return '\n'.join(hero_html)
    
    def generate_features_section(self, config: Dict[str, Any]) -> str:
        """Generate features section with semantic structure."""
        features_html = [
            '    <section class="features-section" aria-labelledby="features-heading">',
            '        <div class="container">',
        ]
        
        if config.get("title"):
            features_html.extend([
                f'            <h2 id="features-heading" class="section-title">{config["title"]}</h2>',
            ])
        
        if config.get("subtitle"):
            features_html.append(f'            <p class="section-subtitle">{config["subtitle"]}</p>')
        
        features_html.append('            <div class="features-grid">')
        
        for i, feature in enumerate(config.get("features", [])):
            features_html.extend([
                f'                <article class="feature-item" aria-labelledby="feature-{i}-title">',
                '                    <div class="feature-icon" aria-hidden="true">',
                f'                        {feature.get("icon", "")}',
                '                    </div>',
                '                    <div class="feature-content">',
                f'                        <h3 id="feature-{i}-title" class="feature-title">{feature.get("title", "")}</h3>',
                f'                        <p class="feature-description">{feature.get("description", "")}</p>',
                '                    </div>',
                '                </article>',
            ])
        
        features_html.extend([
            '            </div>',
            '        </div>',
            '    </section>',
        ])
        
        return '\n'.join(features_html)
    
    def generate_testimonials_section(self, config: Dict[str, Any]) -> str:
        """Generate testimonials section with structured data."""
        testimonials_html = [
            '    <section class="testimonials-section" aria-labelledby="testimonials-heading">',
            '        <div class="container">',
        ]
        
        if config.get("title"):
            testimonials_html.append(f'            <h2 id="testimonials-heading" class="section-title">{config["title"]}</h2>')
        
        testimonials_html.append('            <div class="testimonials-grid">')
        
        for i, testimonial in enumerate(config.get("testimonials", [])):
            testimonials_html.extend([
                f'                <blockquote class="testimonial-item" cite="{testimonial.get("source", "")}">',
                f'                    <p class="testimonial-text">"{testimonial.get("text", "")}"</p>',
                '                    <footer class="testimonial-author">',
                f'                        <cite class="author-name">{testimonial.get("author", "")}</cite>',
            ])
            
            if testimonial.get("role"):
                testimonials_html.append(f'                        <span class="author-role">{testimonial["role"]}</span>')
            
            if testimonial.get("company"):
                testimonials_html.append(f'                        <span class="author-company">{testimonial["company"]}</span>')
            
            testimonials_html.extend([
                '                    </footer>',
                '                </blockquote>',
            ])
        
        testimonials_html.extend([
            '            </div>',
            '        </div>',
            '    </section>',
        ])
        
        return '\n'.join(testimonials_html)
    
    def generate_cta_section(self, config: Dict[str, Any]) -> str:
        """Generate call-to-action section optimized for conversions."""
        cta_html = [
            '    <section class="cta-section" aria-labelledby="cta-heading">',
            '        <div class="container">',
            '            <div class="cta-content">',
        ]
        
        if config.get("title"):
            cta_html.append(f'                <h2 id="cta-heading" class="cta-title">{config["title"]}</h2>')
        
        if config.get("description"):
            cta_html.append(f'                <p class="cta-description">{config["description"]}</p>')
        
        # Primary CTA Button
        if config.get("primary_cta"):
            cta = config["primary_cta"]
            cta_html.extend([
                '                <div class="cta-buttons">',
                f'                    <a href="{cta.get("url", "#")}" class="btn btn-primary btn-xl" ',
                '                       role="button" onclick="trackConversion(\'primary_cta\')">',
                f'                        {cta.get("text", "Inizia Ora")}',
                '                    </a>',
            ])
            
            # Secondary CTA Button
            if config.get("secondary_cta"):
                secondary = config["secondary_cta"]
                cta_html.extend([
                    f'                    <a href="{secondary.get("url", "#")}" class="btn btn-secondary btn-xl" ',
                    '                       role="button" onclick="trackConversion(\'secondary_cta\')">',
                    f'                        {secondary.get("text", "Scopri di più")}',
                    '                    </a>',
                ])
            
            cta_html.append('                </div>')
        
        # Trust Signals
        if config.get("trust_signals"):
            cta_html.append('                <div class="trust-signals">')
            for signal in config["trust_signals"]:
                cta_html.append(f'                    <span class="trust-signal">{signal}</span>')
            cta_html.append('                </div>')
        
        cta_html.extend([
            '            </div>',
            '        </div>',
            '    </section>',
        ])
        
        return '\n'.join(cta_html)
    
    def generate_form_section(self, config: Dict[str, Any]) -> str:
        """Generate accessible form with validation."""
        form_html = [
            '    <section class="form-section" aria-labelledby="form-heading">',
            '        <div class="container">',
        ]
        
        if config.get("title"):
            form_html.append(f'            <h2 id="form-heading" class="section-title">{config["title"]}</h2>')
        
        form_html.extend([
            f'            <form class="landing-form" method="post" action="{config.get("action", "#")}" ',
            '                  novalidate aria-describedby="form-instructions">',
        ])
        
        if config.get("instructions"):
            form_html.append(f'                <p id="form-instructions" class="form-instructions">{config["instructions"]}</p>')
        
        # Generate form fields
        for field in config.get("fields", []):
            form_html.extend(self._generate_form_field(field))
        
        # Submit button
        submit_text = config.get("submit_text", "Invia")
        form_html.extend([
            '                <div class="form-group">',
            f'                    <button type="submit" class="btn btn-primary btn-block" onclick="trackConversion(\'form_submit\')">',
            f'                        {submit_text}',
            '                    </button>',
            '                </div>',
        ])
        
        # Privacy notice
        if config.get("privacy_notice"):
            form_html.extend([
                '                <div class="privacy-notice">',
                f'                    <small>{config["privacy_notice"]}</small>',
                '                </div>',
            ])
        
        form_html.extend([
            '            </form>',
            '        </div>',
            '    </section>',
        ])
        
        return '\n'.join(form_html)
    
    def _generate_form_field(self, field: Dict[str, Any]) -> List[str]:
        """Generate individual form field with proper accessibility."""
        field_type = field.get("type", "text")
        field_name = field.get("name", "")
        field_id = f"field_{field_name}"
        required = field.get("required", False)
        
        field_html = ['                <div class="form-group">']
        
        # Label
        label_text = field.get("label", "")
        required_marker = " *" if required else ""
        field_html.append(f'                    <label for="{field_id}" class="form-label">{label_text}{required_marker}</label>')
        
        # Input field
        if field_type == "textarea":
            field_html.extend([
                f'                    <textarea id="{field_id}" name="{field_name}" class="form-control" ',
                f'                              placeholder="{field.get("placeholder", "")}"',
                f'                              {"required" if required else ""} ',
                f'                              aria-describedby="{field_id}_help">',
                '                    </textarea>',
            ])
        elif field_type == "select":
            field_html.extend([
                f'                    <select id="{field_id}" name="{field_name}" class="form-control" ',
                f'                            {"required" if required else ""} aria-describedby="{field_id}_help">',
            ])
            
            for option in field.get("options", []):
                field_html.append(f'                        <option value="{option["value"]}">{option["text"]}</option>')
            
            field_html.append('                    </select>')
        else:
            field_html.extend([
                f'                    <input type="{field_type}" id="{field_id}" name="{field_name}" ',
                f'                           class="form-control" placeholder="{field.get("placeholder", "")}" ',
                f'                           {"required" if required else ""} aria-describedby="{field_id}_help">',
            ])
        
        # Help text
        if field.get("help_text"):
            field_html.append(f'                    <small id="{field_id}_help" class="form-help">{field["help_text"]}</small>')
        
        field_html.append('                </div>')
        return field_html
    
    def generate_footer(self, config: Dict[str, Any]) -> str:
        """Generate semantic footer with proper navigation."""
        footer_html = [
            '    <footer class="site-footer" role="contentinfo">',
            '        <div class="container">',
            '            <div class="footer-content">',
        ]
        
        # Company info section
        if config.get("company_info"):
            info = config["company_info"]
            footer_html.extend([
                '                <div class="footer-company">',
                f'                    <h3 class="company-name">{info.get("name", "")}</h3>',
            ])
            
            if info.get("description"):
                footer_html.append(f'                    <p class="company-description">{info["description"]}</p>')
            
            if info.get("address"):
                footer_html.append(f'                    <address class="company-address">{info["address"]}</address>')
            
            # Contact info
            if info.get("phone") or info.get("email"):
                footer_html.append('                    <div class="company-contact">')
                
                if info.get("phone"):
                    footer_html.append(f'                        <a href="tel:{info["phone"]}" aria-label="Telefono">📞 {info["phone"]}</a>')
                
                if info.get("email"):
                    footer_html.append(f'                        <a href="mailto:{info["email"]}" aria-label="Email">✉️ {info["email"]}</a>')
                
                footer_html.append('                    </div>')
            
            footer_html.append('                </div>')
        
        # Footer navigation links
        if config.get("links"):
            footer_html.extend([
                '                <div class="footer-nav">',
                '                    <h4>Link Utili</h4>',
                '                    <nav aria-label="Link del footer">',
                '                        <ul class="footer-links">',
            ])
            
            for link in config["links"]:
                footer_html.append(f'                            <li><a href="{link["url"]}">{link["text"]}</a></li>')
            
            footer_html.extend([
                '                        </ul>',
                '                    </nav>',
                '                </div>',
            ])
        
        # Social media links
        if config.get("social_links"):
            footer_html.extend([
                '                <div class="footer-social">',
                '                    <h4>Seguici</h4>',
                '                    <div class="social-links" aria-label="Link social media">',
            ])
            
            # Map platform names to icons
            platform_icons = {
                'facebook': '📘',
                'twitter': '🐦', 
                'linkedin': '💼',
                'instagram': '📷'
            }
            
            for social in config["social_links"]:
                platform = social["platform"]
                icon = platform_icons.get(platform, platform)
                footer_html.extend([
                    f'                        <a href="{social["url"]}" class="social-link" ',
                    f'                           data-platform="{platform}" aria-label="{platform.title()}" ',
                    f'                           target="_blank" rel="noopener">',
                    f'                            {icon}',
                    '                        </a>',
                ])
            
            footer_html.extend([
                '                    </div>',
                '                </div>',
            ])
        
        # Close footer-content div
        footer_html.append('            </div>')
        
        # Copyright
        if config.get("copyright"):
            footer_html.append(f'            <div class="footer-copyright">{config["copyright"]}</div>')
        
        footer_html.extend([
            '        </div>',
            '    </footer>',
        ])
        
        return '\n'.join(footer_html)
    
    def generate_scripts(self) -> str:
        """Generate optimized JavaScript includes and analytics."""
        scripts = [
            '    <!-- Core JavaScript -->',
            '    <script src="assets/js/core.js" defer></script>',
            '    <script src="assets/js/components/all.js" defer></script>',
            '',
            '    <!-- Analytics -->',
            '    <script>',
            '        // Google Analytics 4',
            '        window.dataLayer = window.dataLayer || [];',
            '        function gtag(){dataLayer.push(arguments);}',
            '        gtag(\'js\', new Date());',
            '        gtag(\'config\', \'GA_MEASUREMENT_ID\');',
            '        ',
            '        // Conversion tracking function',
            '        function trackConversion(event_name, value = null) {',
            '            gtag(\'event\', \'conversion\', {',
            '                \'event_category\': \'landing_page\',',
            '                \'event_label\': event_name,',
            '                \'value\': value',
            '            });',
            '        }',
            '    </script>',
            '</body>',
            '</html>',
        ]
        
        return '\n'.join(scripts)
    
    def _generate_structured_data(self) -> Optional[str]:
        """Generate JSON-LD structured data for SEO."""
        # Basic organization structured data
        structured_data = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": self.seo_config.title,
            "description": self.seo_config.description,
            "url": self.seo_config.canonical_url,
        }
        
        import json
        return json.dumps(structured_data, ensure_ascii=False)
    
    def generate_complete_page(self) -> str:
        """Generate complete landing page HTML."""
        html_parts = [
            self.generate_head(),
            self.generate_body_start(),
            '    <main id="main-content" role="main">',
        ]
        
        # Generate components in order
        for component in self.components:
            comp_type = component["type"]
            config = component["config"]
            
            if comp_type == ComponentType.HERO:
                html_parts.append(self.generate_hero_section(config))
            elif comp_type == ComponentType.FEATURES:
                html_parts.append(self.generate_features_section(config))
            elif comp_type == ComponentType.TESTIMONIALS:
                html_parts.append(self.generate_testimonials_section(config))
            elif comp_type == ComponentType.CTA:
                html_parts.append(self.generate_cta_section(config))
            elif comp_type == ComponentType.FORM:
                html_parts.append(self.generate_form_section(config))
        
        html_parts.append('    </main>')
        
        # Add footer if configured
        footer_component = next((c for c in self.components if c["type"] == ComponentType.FOOTER), None)
        if footer_component:
            html_parts.append(self.generate_footer(footer_component["config"]))
        
        html_parts.append(self.generate_scripts())
        
        return '\n'.join(html_parts)