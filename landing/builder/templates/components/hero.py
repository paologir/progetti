"""
Hero Component Templates

Pre-built hero section templates optimized for different conversion goals.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class HeroTemplate:
    name: str
    description: str
    conversion_focus: str
    config: Dict[str, Any]


class HeroComponent:
    """
    Hero section component with conversion-optimized templates.
    """
    
    @staticmethod
    def get_templates() -> Dict[str, HeroTemplate]:
        """Get all available hero templates."""
        return {
            "lead_generation": HeroTemplate(
                name="Lead Generation Hero",
                description="Ottimizzato per la generazione di lead con form prominente",
                conversion_focus="lead_capture",
                config={
                    "layout": "split",
                    "title_max_words": 8,
                    "subtitle_required": True,
                    "cta_prominence": "high",
                    "form_integration": True,
                    "trust_signals": True
                }
            ),
            "product_launch": HeroTemplate(
                name="Product Launch Hero",
                description="Per il lancio di prodotti con video/immagine prominente",
                conversion_focus="product_awareness",
                config={
                    "layout": "centered",
                    "media_required": True,
                    "title_max_words": 6,
                    "countdown_timer": True,
                    "social_proof": True,
                    "multiple_cta": True
                }
            ),
            "sales_page": HeroTemplate(
                name="Sales Page Hero",
                description="Per pagine di vendita con benefici e urgenza",
                conversion_focus="direct_sales",
                config={
                    "layout": "full_width",
                    "benefit_bullets": True,
                    "price_display": True,
                    "scarcity_elements": True,
                    "guarantee_badge": True,
                    "testimonial_snippet": True
                }
            ),
            "event_registration": HeroTemplate(
                name="Event Registration Hero",
                description="Per eventi con data/luogo prominenti",
                conversion_focus="event_signup",
                config={
                    "layout": "split",
                    "event_details": True,
                    "speaker_preview": True,
                    "early_bird_pricing": True,
                    "agenda_highlight": True,
                    "location_map": True
                }
            ),
            "app_download": HeroTemplate(
                name="App Download Hero", 
                description="Per promuovere download di app mobile",
                conversion_focus="app_install",
                config={
                    "layout": "device_mockup",
                    "app_screenshots": True,
                    "store_badges": True,
                    "feature_highlights": True,
                    "user_count": True,
                    "rating_display": True
                }
            )
        }
    
    @staticmethod
    def generate_lead_generation_hero(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lead generation hero configuration."""
        return {
            "title": config.get("title", "Ottieni Risultati Straordinari con la Nostra Soluzione"),
            "subtitle": config.get("subtitle", "Unisciti a migliaia di professionisti che hanno già trasformato il loro business"),
            "description": config.get("description", "Scopri come la nostra piattaforma può aiutarti a raggiungere i tuoi obiettivi in modo semplice ed efficace."),
            "cta": {
                "text": config.get("cta_text", "Scarica la Guida Gratuita"),
                "url": config.get("cta_url", "#lead-form"),
                "description": "Nessun costo, nessun impegno. Cancellati quando vuoi."
            },
            "media": {
                "type": "image",
                "url": config.get("hero_image", "assets/images/hero-dashboard.jpg"),
                "alt": "Dashboard della nostra piattaforma"
            },
            "trust_signals": [
                "✓ Oltre 10.000 clienti soddisfatti",
                "✓ Garanzia di rimborso 30 giorni", 
                "✓ Supporto clienti 24/7"
            ],
            "form_teaser": {
                "title": "Inizia Gratuitamente",
                "fields_preview": ["Email", "Nome"],
                "privacy_note": "I tuoi dati sono al sicuro con noi"
            }
        }
    
    @staticmethod
    def generate_product_launch_hero(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product launch hero configuration."""
        return {
            "title": config.get("title", "Il Futuro è Arrivato"),
            "subtitle": config.get("subtitle", "Scopri il prodotto che cambierà il tuo modo di lavorare"),
            "description": config.get("description", "Innovazione, semplicità e risultati concreti in un'unica soluzione rivoluzionaria."),
            "cta": {
                "text": config.get("primary_cta", "Acquista Ora"),
                "url": config.get("cta_url", "#pricing"),
                "description": f"Offerta di lancio: {config.get('discount', '30% di sconto')} fino al {config.get('deadline', '31 Dicembre')}"
            },
            "secondary_cta": {
                "text": config.get("secondary_cta", "Guarda la Demo"),
                "url": config.get("demo_url", "#video-demo")
            },
            "media": {
                "type": config.get("media_type", "video"),
                "url": config.get("media_url", "assets/videos/product-demo.mp4"),
                "poster": config.get("video_poster", "assets/images/video-poster.jpg"),
                "alt": "Demo del prodotto in azione"
            },
            "launch_countdown": {
                "end_date": config.get("launch_date", "2024-12-31T23:59:59"),
                "label": "Offerta di lancio termina tra:"
            },
            "social_proof": {
                "user_count": config.get("beta_users", "500+ beta tester"),
                "rating": config.get("rating", "4.9/5"),
                "featured_logos": config.get("partner_logos", [])
            }
        }
    
    @staticmethod
    def generate_sales_page_hero(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales page hero configuration."""
        return {
            "title": config.get("title", "Trasforma la Tua Vita in 30 Giorni"),
            "subtitle": config.get("subtitle", "Il Sistema Completo che Ha Già Aiutato 5.000+ Persone"),
            "description": config.get("description", "Finalmente una soluzione che funziona davvero. Risultati garantiti o ti rimborsiamo tutto."),
            "benefit_bullets": [
                f"✓ {benefit}" for benefit in config.get("key_benefits", [
                    "Risultati visibili in 7 giorni",
                    "Sistema passo-passo facile da seguire", 
                    "Supporto personalizzato incluso",
                    "Garanzia soddisfatti o rimborsati"
                ])
            ],
            "price_highlight": {
                "original_price": config.get("original_price", "297€"),
                "current_price": config.get("sale_price", "197€"),
                "savings": config.get("savings", "100€ di risparmio"),
                "payment_options": config.get("payment_options", "Oppure 3 rate da 66€")
            },
            "cta": {
                "text": config.get("cta_text", "Ottieni l'Accesso Ora"),
                "url": config.get("checkout_url", "#checkout"),
                "urgency": config.get("urgency_text", "⏰ Offerta limitata - Solo oggi!")
            },
            "guarantee": {
                "type": config.get("guarantee_type", "30_day_money_back"),
                "text": config.get("guarantee_text", "Garanzia Soddisfatti o Rimborsati 30 Giorni"),
                "badge": config.get("guarantee_badge", "assets/images/guarantee-badge.png")
            },
            "scarcity": {
                "type": config.get("scarcity_type", "limited_spots"),
                "message": config.get("scarcity_message", "Solo 27 posti disponibili questo mese"),
                "counter": config.get("spots_left", 27)
            },
            "testimonial_snippet": {
                "text": config.get("featured_testimonial", "\"Ho ottenuto risultati incredibili in solo 2 settimane!\""),
                "author": config.get("testimonial_author", "Marco R., Imprenditore"),
                "photo": config.get("testimonial_photo", "assets/images/testimonial-marco.jpg")
            }
        }
    
    @staticmethod
    def generate_event_registration_hero(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate event registration hero configuration."""
        return {
            "title": config.get("title", "Summit Digitale 2024"),
            "subtitle": config.get("subtitle", "3 giorni per rivoluzionare il tuo business online"),
            "description": config.get("description", "Impara dalle migliori menti del settore e trasforma la tua azienda con strategie digitali vincenti."),
            "event_details": {
                "date": config.get("event_date", "15-17 Marzo 2024"),
                "time": config.get("event_time", "09:00 - 18:00"),
                "location": config.get("location", "Milano + Streaming Online"),
                "format": config.get("format", "Ibrido: Presenza e Online")
            },
            "cta": {
                "text": config.get("cta_text", "Prenota il Tuo Posto"),
                "url": config.get("registration_url", "#registration"),
                "description": config.get("early_bird", "Early Bird: Sconto 40% fino al 1° Febbraio")
            },
            "speaker_preview": {
                "title": "Speaker di Fama Mondiale",
                "speakers": config.get("featured_speakers", [
                    {
                        "name": "Sarah Johnson",
                        "role": "CEO di TechCorp",
                        "photo": "assets/images/speaker-sarah.jpg"
                    },
                    {
                        "name": "Marco Rossi", 
                        "role": "Digital Marketing Expert",
                        "photo": "assets/images/speaker-marco.jpg"
                    }
                ])
            },
            "agenda_highlight": {
                "title": "Cosa Imparerai",
                "sessions": config.get("key_sessions", [
                    "Strategie di Marketing Digitale 2024",
                    "AI e Automazione per il Business",
                    "E-commerce: Vendere di Più Online"
                ])
            },
            "pricing": {
                "early_bird": config.get("early_price", "297€"),
                "regular": config.get("regular_price", "497€"),
                "deadline": config.get("early_deadline", "1 Febbraio 2024")
            },
            "social_proof": {
                "past_attendees": config.get("attendee_count", "2.500+ partecipanti nel 2023"),
                "satisfaction": config.get("satisfaction_rate", "98% di soddisfazione"),
                "companies": config.get("company_logos", [])
            }
        }
    
    @staticmethod
    def generate_app_download_hero(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate app download hero configuration."""
        return {
            "title": config.get("title", "L'App che Semplifica la Tua Vita"),
            "subtitle": config.get("subtitle", "Tutto quello di cui hai bisogno, sempre a portata di mano"),
            "description": config.get("description", "Scarica gratis l'app più amata dagli utenti e scopri perché milioni di persone non possono più farne a meno."),
            "app_preview": {
                "screenshots": config.get("screenshots", [
                    "assets/images/app-screen-1.jpg",
                    "assets/images/app-screen-2.jpg", 
                    "assets/images/app-screen-3.jpg"
                ]),
                "device_mockup": config.get("device_mockup", "assets/images/phone-mockup.png")
            },
            "download_buttons": {
                "ios": {
                    "url": config.get("ios_url", "https://apps.apple.com/app/..."),
                    "badge": "assets/images/app-store-badge.png"
                },
                "android": {
                    "url": config.get("android_url", "https://play.google.com/store/apps/..."),
                    "badge": "assets/images/google-play-badge.png"
                }
            },
            "key_features": config.get("features", [
                "🚀 Veloce e intuitiva",
                "🔒 Sicura e privata", 
                "📱 Funziona offline",
                "🎨 Design moderno"
            ]),
            "app_stats": {
                "downloads": config.get("download_count", "1M+ download"),
                "rating": config.get("app_rating", "4.8/5"),
                "reviews": config.get("review_count", "50k+ recensioni"),
                "size": config.get("app_size", "Solo 12MB")
            },
            "user_testimonials": {
                "featured_review": config.get("featured_review", "La migliore app che abbia mai usato!"),
                "reviewer": config.get("reviewer_name", "Anna M."),
                "rating_stars": config.get("review_rating", 5)
            }
        }
    
    @staticmethod
    def get_template_by_type(template_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get hero configuration by template type."""
        generators = {
            "lead_generation": HeroComponent.generate_lead_generation_hero,
            "product_launch": HeroComponent.generate_product_launch_hero,
            "sales_page": HeroComponent.generate_sales_page_hero,
            "event_registration": HeroComponent.generate_event_registration_hero,
            "app_download": HeroComponent.generate_app_download_hero
        }
        
        generator = generators.get(template_type)
        if not generator:
            raise ValueError(f"Template type '{template_type}' not found")
        
        return generator(config)