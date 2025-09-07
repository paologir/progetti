""" 
Features Component Templates

Pre-built features section templates optimized for different conversion goals.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class FeaturesTemplate:
    name: str
    description: str
    conversion_focus: str
    config: Dict[str, Any]


class FeaturesComponent:
    """
    Features section component with conversion-optimized templates.
    """
    
    @staticmethod
    def get_templates() -> Dict[str, FeaturesTemplate]:
        """Get all available features templates."""
        return {
            "product_benefits": FeaturesTemplate(
                name="Product Benefits Features",
                description="Evidenzia i benefici chiave del prodotto con icone e descrizioni",
                conversion_focus="benefit_communication",
                config={
                    "layout": "grid_3_columns",
                    "icon_style": "modern",
                    "benefit_emphasis": True,
                    "stats_integration": True,
                    "cta_per_feature": False
                }
            ),
            "saas_features": FeaturesTemplate(
                name="SaaS Features Showcase",
                description="Per software con molte funzionalità tecniche",
                conversion_focus="feature_depth",
                config={
                    "layout": "alternating_rows",
                    "screenshots": True,
                    "feature_categories": True,
                    "technical_details": True,
                    "integration_logos": True
                }
            ),
            "service_offerings": FeaturesTemplate(
                name="Service Offerings Features",
                description="Per servizi professionali e consulenza",
                conversion_focus="trust_building",
                config={
                    "layout": "cards_with_hover",
                    "process_steps": True,
                    "expertise_badges": True,
                    "case_study_links": True,
                    "consultation_cta": True
                }
            ),
            "comparison_features": FeaturesTemplate(
                name="Comparison Features",
                description="Confronto con competitor o alternative",
                conversion_focus="differentiation",
                config={
                    "layout": "comparison_table",
                    "competitor_columns": True,
                    "highlight_advantages": True,
                    "pricing_comparison": True,
                    "switch_incentive": True
                }
            ),
            "mobile_app_features": FeaturesTemplate(
                name="Mobile App Features",
                description="Funzionalità di app mobile con screenshots",
                conversion_focus="app_value",
                config={
                    "layout": "carousel_with_device",
                    "device_mockups": True,
                    "gesture_animations": True,
                    "platform_badges": True,
                    "feature_videos": True
                }
            )
        }
    
    @staticmethod
    def generate_product_benefits_features(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product benefits features configuration."""
        default_features = [
            {
                "icon": "⚡",
                "title": "Velocità Incredibile",
                "description": "Risparmia ore di lavoro ogni settimana con la nostra soluzione ultra-veloce",
                "stat": "10x più veloce"
            },
            {
                "icon": "🔒",
                "title": "Sicurezza Garantita",
                "description": "I tuoi dati sono protetti con crittografia di livello bancario",
                "stat": "99.99% uptime"
            },
            {
                "icon": "📈",
                "title": "Risultati Misurabili",
                "description": "Monitora i tuoi progressi con analytics dettagliate in tempo reale",
                "stat": "+250% ROI medio"
            }
        ]
        
        return {
            "section_title": config.get("title", "Perché Scegliere la Nostra Soluzione"),
            "section_subtitle": config.get("subtitle", "Funzionalità progettate per il tuo successo"),
            "features": config.get("features", default_features),
            "layout": {
                "type": "grid",
                "columns": 3,
                "gap": "large",
                "animation": "fade-in-up"
            },
            "styling": {
                "icon_size": "large",
                "icon_background": True,
                "hover_effects": True,
                "stat_highlight": True
            },
            "cta_section": {
                "enabled": config.get("show_cta", True),
                "text": config.get("cta_text", "Scopri Tutte le Funzionalità"),
                "url": config.get("cta_url", "#all-features")
            }
        }
    
    @staticmethod
    def generate_saas_features(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SaaS features showcase configuration."""
        default_features = [
            {
                "category": "Gestione Progetti",
                "title": "Organizza Tutto in Un Solo Posto",
                "description": "Dashboard intuitiva per gestire progetti, task e team con facilità",
                "screenshot": "assets/images/feature-dashboard.jpg",
                "benefits": [
                    "Vista Kanban e Gantt",
                    "Automazioni personalizzate",
                    "Collaborazione in tempo reale"
                ]
            },
            {
                "category": "Analytics & Reports",
                "title": "Insights Che Fanno la Differenza",
                "description": "Report dettagliati e analytics avanzate per decisioni data-driven",
                "screenshot": "assets/images/feature-analytics.jpg",
                "benefits": [
                    "Dashboard personalizzabili",
                    "Export in tutti i formati",
                    "Alerts intelligenti"
                ]
            }
        ]
        
        return {
            "section_title": config.get("title", "Funzionalità Potenti per Team Ambiziosi"),
            "section_subtitle": config.get("subtitle", "Tutto quello che serve per portare il tuo business al livello successivo"),
            "features": config.get("features", default_features),
            "layout": {
                "type": "alternating",
                "image_position": "auto",
                "spacing": "extra-large",
                "container": "wide"
            },
            "integrations": {
                "title": "Si Integra con i Tuoi Tool Preferiti",
                "logos": config.get("integration_logos", [
                    "slack", "google", "microsoft", "zapier", "stripe"
                ])
            },
            "trial_cta": {
                "text": config.get("trial_cta", "Prova Gratis per 14 Giorni"),
                "url": config.get("trial_url", "#free-trial"),
                "note": "Nessuna carta di credito richiesta"
            }
        }
    
    @staticmethod
    def generate_service_offerings_features(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service offerings features configuration."""
        default_services = [
            {
                "icon": "🎯",
                "title": "Consulenza Strategica",
                "description": "Analizziamo il tuo business e creiamo un piano su misura per i tuoi obiettivi",
                "process": [
                    "Analisi approfondita",
                    "Piano personalizzato",
                    "Implementazione guidata"
                ],
                "cta": "Richiedi Consulenza"
            },
            {
                "icon": "🚀",
                "title": "Implementazione Completa",
                "description": "Il nostro team si occupa di tutto, dalla A alla Z",
                "process": [
                    "Setup iniziale",
                    "Configurazione avanzata",
                    "Training del team"
                ],
                "cta": "Scopri di Più"
            },
            {
                "icon": "📊",
                "title": "Supporto Continuativo", 
                "description": "Assistenza dedicata per garantire risultati costanti nel tempo",
                "process": [
                    "Monitoraggio KPI",
                    "Ottimizzazioni mensili",
                    "Report dettagliati"
                ],
                "cta": "Vedi i Piani"
            }
        ]
        
        return {
            "section_title": config.get("title", "I Nostri Servizi"),
            "section_subtitle": config.get("subtitle", "Soluzioni complete per ogni esigenza"),
            "services": config.get("services", default_services),
            "layout": {
                "type": "cards",
                "columns": 3,
                "card_style": "elevated",
                "hover_animation": "lift"
            },
            "trust_elements": {
                "certifications": config.get("certifications", [
                    "ISO 9001", "Google Partner", "Microsoft Certified"
                ]),
                "experience": config.get("experience", "15+ anni di esperienza"),
                "clients_served": config.get("clients", "500+ clienti soddisfatti")
            },
            "consultation_cta": {
                "title": "Parliamo del Tuo Progetto",
                "text": config.get("consultation_text", "Consulenza Gratuita"),
                "url": config.get("consultation_url", "#consultation"),
                "form_fields": ["Nome", "Email", "Telefono", "Messaggio"]
            }
        }
    
    @staticmethod
    def generate_comparison_features(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison features configuration."""
        return {
            "section_title": config.get("title", "Perché Siamo la Scelta Migliore"),
            "section_subtitle": config.get("subtitle", "Confronta e scopri la differenza"),
            "comparison_table": {
                "headers": [
                    "Funzionalità",
                    config.get("our_name", "Noi"),
                    "Competitor A",
                    "Competitor B"
                ],
                "features": config.get("comparison_features", [
                    {
                        "name": "Prezzo mensile",
                        "us": "€49",
                        "competitor_a": "€99",
                        "competitor_b": "€79",
                        "highlight": True
                    },
                    {
                        "name": "Utenti illimitati",
                        "us": "✓",
                        "competitor_a": "Max 10",
                        "competitor_b": "Max 25"
                    },
                    {
                        "name": "Supporto 24/7",
                        "us": "✓",
                        "competitor_a": "✗",
                        "competitor_b": "Solo email"
                    },
                    {
                        "name": "API Access",
                        "us": "✓",
                        "competitor_a": "Piano Enterprise",
                        "competitor_b": "✓"
                    },
                    {
                        "name": "Formazione inclusa",
                        "us": "✓",
                        "competitor_a": "€500 extra",
                        "competitor_b": "✗"
                    }
                ])
            },
            "advantages_summary": {
                "title": "I Vantaggi in Breve",
                "points": config.get("key_advantages", [
                    "50% più economico della concorrenza",
                    "Funzionalità complete senza costi nascosti",
                    "Migrazione gratuita dai competitor"
                ])
            },
            "switch_incentive": {
                "title": "Passa a Noi Senza Rischi",
                "offer": config.get("switch_offer", "3 mesi gratis se vieni dalla concorrenza"),
                "cta": config.get("switch_cta", "Inizia la Migrazione"),
                "url": config.get("switch_url", "#migrate")
            }
        }
    
    @staticmethod
    def generate_mobile_app_features(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mobile app features configuration."""
        default_features = [
            {
                "title": "Interfaccia Intuitiva",
                "description": "Design pulito e navigazione semplice per un'esperienza utente perfetta",
                "screenshot": "assets/images/app-feature-ui.jpg",
                "gesture_hint": "Swipe per scoprire"
            },
            {
                "title": "Notifiche Smart",
                "description": "Resta aggiornato con notifiche intelligenti e personalizzabili",
                "screenshot": "assets/images/app-feature-notifications.jpg",
                "gesture_hint": "Tap per personalizzare"
            },
            {
                "title": "Modalità Offline",
                "description": "Lavora anche senza connessione, sincronizzazione automatica",
                "screenshot": "assets/images/app-feature-offline.jpg",
                "gesture_hint": "Sempre disponibile"
            }
        ]
        
        return {
            "section_title": config.get("title", "Un'App Pensata per Te"),
            "section_subtitle": config.get("subtitle", "Funzionalità innovative per semplificarti la vita"),
            "features": config.get("features", default_features),
            "layout": {
                "type": "carousel",
                "device_frame": "iphone-13",
                "auto_rotate": True,
                "rotation_delay": 5000
            },
            "platform_features": {
                "ios": {
                    "exclusive": ["Widget iOS", "Siri Shortcuts", "Apple Watch"],
                    "min_version": "iOS 14+"
                },
                "android": {
                    "exclusive": ["Widget Android", "Google Assistant", "Wear OS"],
                    "min_version": "Android 8+"
                }
            },
            "performance_stats": {
                "app_size": config.get("app_size", "< 50MB"),
                "battery_usage": config.get("battery", "Ottimizzata"),
                "offline_capability": config.get("offline", "100% funzionale")
            },
            "download_section": {
                "title": "Scarica Ora e Inizia Subito",
                "ios_url": config.get("ios_url", "#"),
                "android_url": config.get("android_url", "#"),
                "qr_code": config.get("show_qr", True)
            }
        }
    
    @staticmethod
    def get_template_by_type(template_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get features configuration by template type."""
        generators = {
            "product_benefits": FeaturesComponent.generate_product_benefits_features,
            "saas_features": FeaturesComponent.generate_saas_features,
            "service_offerings": FeaturesComponent.generate_service_offerings_features,
            "comparison_features": FeaturesComponent.generate_comparison_features,
            "mobile_app_features": FeaturesComponent.generate_mobile_app_features
        }
        
        generator = generators.get(template_type)
        if not generator:
            raise ValueError(f"Template type '{template_type}' not found")
        
        return generator(config)