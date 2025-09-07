""" 
CTA (Call-to-Action) Component Templates

Pre-built CTA section templates optimized for maximum conversions.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class CTATemplate:
    name: str
    description: str
    conversion_focus: str
    config: Dict[str, Any]


class CTAComponent:
    """
    CTA section component with conversion-optimized templates.
    """
    
    @staticmethod
    def get_templates() -> Dict[str, CTATemplate]:
        """Get all available CTA templates."""
        return {
            "lead_generation": CTATemplate(
                name="Lead Generation CTA",
                description="Per catturare email con lead magnet",
                conversion_focus="email_capture",
                config={
                    "style": "form_prominent",
                    "urgency": "medium",
                    "social_proof": True,
                    "privacy_reassurance": True,
                    "multi_step_form": False
                }
            ),
            "sales_conversion": CTATemplate(
                name="Sales Conversion CTA",
                description="Per spingere all'acquisto immediato",
                conversion_focus="direct_purchase",
                config={
                    "style": "urgency_driven",
                    "scarcity_elements": True,
                    "guarantee_display": True,
                    "payment_security": True,
                    "one_click_purchase": True
                }
            ),
            "trial_signup": CTATemplate(
                name="Free Trial CTA",
                description="Per trial gratuiti di software/servizi",
                conversion_focus="trial_conversion",
                config={
                    "style": "risk_free_emphasis",
                    "trial_benefits": True,
                    "no_credit_card": True,
                    "feature_preview": True,
                    "instant_access": True
                }
            ),
            "consultation_booking": CTATemplate(
                name="Consultation Booking CTA",
                description="Per prenotare consulenze o call",
                conversion_focus="appointment_booking",
                config={
                    "style": "calendar_integration",
                    "availability_display": True,
                    "expertise_highlights": True,
                    "consultation_value": True,
                    "timezone_smart": True
                }
            ),
            "newsletter_subscription": CTATemplate(
                name="Newsletter Subscription CTA",
                description="Per iscrizioni newsletter con valore aggiunto",
                conversion_focus="content_subscription",
                config={
                    "style": "value_proposition",
                    "content_preview": True,
                    "frequency_clarity": True,
                    "subscriber_benefits": True,
                    "unsubscribe_easy": True
                }
            ),
            "app_download": CTATemplate(
                name="App Download CTA",
                description="Per promuovere download di app mobile",
                conversion_focus="app_installation",
                config={
                    "style": "platform_buttons",
                    "qr_code": True,
                    "app_preview": True,
                    "size_info": True,
                    "rating_display": True
                }
            )
        }
    
    @staticmethod
    def generate_lead_generation_cta(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lead generation CTA configuration."""
        return {
            "section_title": config.get("title", "Scarica la Guida Gratuita"),
            "section_subtitle": config.get("subtitle", "Ottieni accesso immediato alle strategie che hanno aiutato 10.000+ professionisti"),
            "value_proposition": {
                "headline": config.get("value_headline", "Tutto quello che ti serve per iniziare"),
                "benefits": config.get("benefits", [
                    "✓ Strategie testate e funzionanti",
                    "✓ Template pronti all'uso",
                    "✓ Checklist step-by-step",
                    "✓ Bonus: 1 ora di consulenza gratuita"
                ]),
                "format_info": config.get("format", "PDF di 47 pagine + video bonus")
            },
            "lead_form": {
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "placeholder": "La tua email migliore",
                        "required": True,
                        "validation": "email"
                    },
                    {
                        "name": "name",
                        "type": "text",
                        "placeholder": "Il tuo nome",
                        "required": True,
                        "validation": "text"
                    }
                ],
                "submit_button": {
                    "text": config.get("cta_text", "Scarica Ora Gratis"),
                    "style": "primary-large",
                    "loading_text": "Invio in corso..."
                },
                "privacy_note": config.get("privacy_text", "Non invieremo spam. Puoi disiscriverti in qualsiasi momento.")
            },
            "social_proof": {
                "downloads_count": config.get("downloads", "15.247+"),
                "testimonial": {
                    "text": config.get("testimonial_text", "La guida più completa che abbia mai letto!"),
                    "author": config.get("testimonial_author", "Marco R., Entrepreneur"),
                    "photo": config.get("testimonial_photo", "assets/images/testimonial-marco.jpg")
                },
                "company_logos": config.get("social_logos", [])
            },
            "urgency_elements": {
                "limited_time": {
                    "enabled": config.get("show_urgency", True),
                    "message": "Offerta limitata: solo per i prossimi 100 download",
                    "countdown": config.get("countdown_end", None)
                }
            },
            "success_message": {
                "title": "Perfetto! Controlla la Tua Email",
                "description": "Ti abbiamo appena inviato il link per scaricare la guida. Se non vedi l'email, controlla la cartella spam.",
                "next_steps": [
                    "Scarica la guida dal link nell'email",
                    "Implementa la prima strategia oggi stesso",
                    "Prenota la tua consulenza gratuita"
                ]
            }
        }
    
    @staticmethod
    def generate_sales_conversion_cta(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales conversion CTA configuration."""
        return {
            "section_title": config.get("title", "Non Aspettare Oltre - Inizia Oggi Stesso!"),
            "section_subtitle": config.get("subtitle", "Unisciti alle migliaia di clienti che hanno già trasformato il loro business"),
            "urgency_header": {
                "message": config.get("urgency_message", "⏰ Offerta Limitata: Scade Tra"),
                "countdown": config.get("countdown_end", "2024-12-31T23:59:59"),
                "scarcity_text": config.get("scarcity", "Solo 23 posti rimasti a questo prezzo!")
            },
            "offer_summary": {
                "product_name": config.get("product", "Corso Completo + Bonus"),
                "original_price": config.get("original_price", 997),
                "sale_price": config.get("sale_price", 497),
                "currency": "€",
                "savings": config.get("savings", "Risparmi €500"),
                "payment_options": config.get("payment_options", [
                    "Pagamento unico: €497",
                    "3 rate da €166/mese"
                ])
            },
            "risk_reversal": {
                "guarantee": {
                    "type": config.get("guarantee_type", "60_day_money_back"),
                    "title": "Garanzia Totale 60 Giorni",
                    "description": "Prova senza rischi. Se non sei completamente soddisfatto, ti rimborsiamo tutto.",
                    "badge": "assets/images/guarantee-badge.png"
                },
                "testimonials_snippet": [
                    {
                        "text": "Il miglior investimento che abbia mai fatto!",
                        "author": "Laura B.",
                        "result": "+300% fatturato"
                    },
                    {
                        "text": "Risultati incredibili in solo 30 giorni",
                        "author": "Roberto M.",
                        "result": "+150% conversioni"
                    }
                ]
            },
            "cta_buttons": {
                "primary": {
                    "text": config.get("primary_cta", "Sì, Voglio Iniziare Ora!"),
                    "url": config.get("checkout_url", "#checkout"),
                    "style": "extra-large primary pulsing",
                    "icon": "🚀"
                },
                "secondary": {
                    "text": config.get("secondary_cta", "Paga in 3 Rate"),
                    "url": config.get("installments_url", "#installments"),
                    "style": "large secondary"
                }
            },
            "payment_security": {
                "ssl_badge": True,
                "payment_methods": ["Visa", "Mastercard", "PayPal", "Apple Pay"],
                "security_text": "Pagamento sicuro e protetto SSL 256-bit",
                "satisfaction_rate": config.get("satisfaction", "98.7% clienti soddisfatti")
            },
            "final_push": {
                "fomo_text": config.get("fomo", "2.847 persone hanno già iniziato questo mese"),
                "action_consequence": {
                    "positive": "Chi inizia oggi ottiene risultati in 30 giorni",
                    "negative": "Chi aspetta rimane al punto di partenza"
                }
            }
        }
    
    @staticmethod
    def generate_trial_signup_cta(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate free trial CTA configuration."""
        return {
            "section_title": config.get("title", "Prova Gratis per 14 Giorni"),
            "section_subtitle": config.get("subtitle", "Nessuna carta di credito richiesta. Inizia in 30 secondi."),
            "trial_benefits": {
                "headline": "Cosa Otterrai nel Tuo Trial Gratuito:",
                "features": config.get("trial_features", [
                    "✓ Accesso completo a tutte le funzioni",
                    "✓ Supporto dedicato via email e chat",
                    "✓ Setup guidato con il nostro team",
                    "✓ Template e risorse gratuite",
                    "✓ Nessun impegno o contratto"
                ]),
                "duration": config.get("trial_days", 14),
                "full_access": True
            },
            "signup_form": {
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "placeholder": "Email lavorativa",
                        "required": True
                    },
                    {
                        "name": "company",
                        "type": "text",
                        "placeholder": "Nome azienda",
                        "required": False
                    }
                ],
                "submit_button": {
                    "text": config.get("cta_text", "Inizia Trial Gratuito"),
                    "style": "large primary",
                    "icon": "⚡"
                },
                "no_card_text": "Nessuna carta di credito necessaria"
            },
            "risk_free_messaging": {
                "no_commitment": "Zero Impegno",
                "cancel_anytime": "Cancella Quando Vuoi",
                "no_hidden_fees": "Nessun Costo Nascosto",
                "instant_access": "Accesso Immediato"
            },
            "social_proof": {
                "trial_users": config.get("trial_users", "5.000+"),
                "conversion_rate": config.get("trial_to_paid", "89%"),
                "average_rating": config.get("rating", "4.8/5"),
                "featured_companies": config.get("company_logos", [])
            },
            "onboarding_preview": {
                "title": "Ti Guidiamo Passo Dopo Passo",
                "steps": [
                    {"step": 1, "title": "Setup Account", "duration": "2 min"},
                    {"step": 2, "title": "Configurazione", "duration": "5 min"},
                    {"step": 3, "title": "Primi Risultati", "duration": "10 min"}
                ],
                "total_time": "Pronto in meno di 20 minuti"
            },
            "after_trial": {
                "what_happens": "Cosa Succede Dopo il Trial?",
                "options": [
                    "Scegli un piano che fa per te",
                    "Continua gratis con funzioni limitate",
                    "Cancella senza spiegazioni"
                ],
                "migration_help": "Il nostro team ti aiuterà a scegliere"
            }
        }
    
    @staticmethod
    def generate_consultation_booking_cta(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consultation booking CTA configuration."""
        return {
            "section_title": config.get("title", "Prenota la Tua Consulenza Strategica Gratuita"),
            "section_subtitle": config.get("subtitle", "30 minuti con un esperto per analizzare la tua situazione e trovare soluzioni concrete"),
            "consultation_value": {
                "headline": "Cosa Otterrai nella Consulenza (Valore €300):",
                "deliverables": config.get("consultation_includes", [
                    "✓ Analisi approfondita della tua situazione attuale",
                    "✓ Identificazione delle 3 opportunità principali",
                    "✓ Piano d'azione personalizzato",
                    "✓ Stima ROI potenziale dei miglioramenti",
                    "✓ Risorse e strumenti raccomandati"
                ]),
                "format": config.get("format", "Videocall di 30 minuti"),
                "expert_info": {
                    "name": config.get("expert_name", "Marco Rossi"),
                    "title": config.get("expert_title", "Senior Business Strategist"),
                    "experience": config.get("expert_experience", "15+ anni di esperienza"),
                    "photo": config.get("expert_photo", "assets/images/expert-marco.jpg")
                }
            },
            "availability": {
                "next_available": config.get("next_slot", "Oggi alle 15:30"),
                "timezone": "Europe/Rome",
                "calendar_link": config.get("booking_url", "#calendar"),
                "flexibility": "Orari flessibili, anche weekend"
            },
            "booking_form": {
                "fields": [
                    {
                        "name": "name",
                        "type": "text",
                        "placeholder": "Nome e Cognome",
                        "required": True
                    },
                    {
                        "name": "email",
                        "type": "email",
                        "placeholder": "Email",
                        "required": True
                    },
                    {
                        "name": "company",
                        "type": "text",
                        "placeholder": "Azienda (opzionale)",
                        "required": False
                    },
                    {
                        "name": "challenge",
                        "type": "textarea",
                        "placeholder": "Descrivi brevemente la tua sfida principale",
                        "required": True,
                        "rows": 3
                    }
                ],
                "submit_button": {
                    "text": config.get("booking_cta", "Prenota Consulenza Gratuita"),
                    "style": "large primary",
                    "icon": "📅"
                }
            },
            "trust_indicators": {
                "consultations_done": config.get("consultations_count", "1.247+"),
                "satisfaction_rate": config.get("satisfaction", "99.2%"),
                "average_improvement": config.get("avg_improvement", "+180% risultati"),
                "industry_focus": config.get("industries", ["E-commerce", "SaaS", "Servizi", "Manufacturing"])
            },
            "social_proof": {
                "recent_feedback": [
                    {
                        "text": "In 30 minuti ho capito più di quanto avevo compreso in mesi",
                        "author": "Giulia S., CEO",
                        "company": "TechStart"
                    },
                    {
                        "text": "Consigli pratici e immediatamente applicabili",
                        "author": "Roberto L., Marketing Director",
                        "company": "Fashion Brand"
                    }
                ]
            },
            "preparation_guide": {
                "title": "Come Prepararti per Ottenere il Massimo",
                "tips": [
                    "Porta i dati delle tue performance attuali",
                    "Definisci 2-3 obiettivi specifici",
                    "Prepara domande sui tuoi dubbi principali",
                    "Tieni a portata i benchmark del settore"
                ]
            },
            "urgency": {
                "limited_slots": config.get("slots_available", 3),
                "high_demand": "Agende piene per le prossime 2 settimane",
                "booking_deadline": "Prenota entro oggi per avere priorità"
            }
        }
    
    @staticmethod
    def generate_newsletter_subscription_cta(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate newsletter subscription CTA configuration."""
        return {
            "section_title": config.get("title", "Resta Aggiornato con i Migliori Contenuti"),
            "section_subtitle": config.get("subtitle", "Strategie, case study e insights esclusivi direttamente nella tua inbox"),
            "value_proposition": {
                "headline": config.get("value_headline", "Cosa Riceverai (Solo per Iscritti):"),
                "benefits": config.get("newsletter_benefits", [
                    "📊 Analisi settimanali dei trend di mercato",
                    "🚀 Case study esclusivi con dati reali",
                    "🎯 Strategie pratiche testate sul campo",
                    "📚 Template e risorse scaricabili",
                    "🔥 Anteprime di prodotti e servizi"
                ]),
                "frequency": config.get("frequency", "Ogni Giovedì mattina"),
                "content_type": config.get("content_type", "Contenuti originali, mai spam")
            },
            "content_preview": {
                "recent_issues": [
                    {
                        "title": "Come Aumentare le Conversioni del 300% con l'A/B Testing",
                        "date": "15 Nov 2024",
                        "read_time": "7 min",
                        "preview": "La strategia step-by-step che ha trasformato..."
                    },
                    {
                        "title": "Il Framework per Landing Page da €1M+ di Fatturato",
                        "date": "8 Nov 2024",
                        "read_time": "5 min",
                        "preview": "Decostruiamo le 7 landing page più profittevoli..."
                    }
                ],
                "archive_link": config.get("archive_url", "#newsletter-archive")
            },
            "subscription_form": {
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "placeholder": "La tua email migliore",
                        "required": True
                    },
                    {
                        "name": "interests",
                        "type": "select",
                        "placeholder": "Il tuo interesse principale",
                        "options": config.get("interest_options", [
                            "Marketing Digitale",
                            "E-commerce",
                            "SaaS Growth",
                            "Startup",
                            "Consulenza"
                        ]),
                        "required": False
                    }
                ],
                "submit_button": {
                    "text": config.get("subscribe_cta", "Iscriviti Gratuitamente"),
                    "style": "medium primary",
                    "loading_text": "Iscrizione in corso..."
                },
                "privacy_note": "Mai spam. Cancellati in 1 click quando vuoi."
            },
            "subscriber_benefits": {
                "community_access": "Accesso al gruppo Telegram esclusivo",
                "early_access": "Anteprime di nuovi prodotti e servizi",
                "exclusive_discounts": "Sconti riservati agli iscritti",
                "direct_line": "Linea diretta con il team per domande"
            },
            "social_proof": {
                "subscriber_count": config.get("subscribers", "12.500+"),
                "open_rate": config.get("open_rate", "67%"),
                "testimonials": [
                    {
                        "text": "La newsletter più utile che ricevo. Contenuti sempre di qualità!",
                        "author": "Anna M.",
                        "role": "Marketing Manager"
                    },
                    {
                        "text": "Ogni email è una mini-masterclass. Impossibile non implementare!",
                        "author": "Luca P.",
                        "role": "E-commerce Owner"
                    }
                ]
            },
            "sample_newsletter": {
                "title": "Vuoi vedere com'è fatta?",
                "cta": "Leggi l'Ultima Newsletter",
                "url": config.get("sample_url", "#sample-newsletter")
            }
        }
    
    @staticmethod
    def generate_app_download_cta(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate app download CTA configuration."""
        return {
            "section_title": config.get("title", "Scarica l'App e Porta Tutto Sempre con Te"),
            "section_subtitle": config.get("subtitle", "Disponibile gratis su iOS e Android. Over 1 milione di download!"),
            "app_preview": {
                "hero_screenshot": config.get("hero_screenshot", "assets/images/app-hero-screen.jpg"),
                "device_mockup": config.get("device_mockup", "assets/images/phone-mockup.png"),
                "key_features": config.get("preview_features", [
                    "🚀 Interfaccia veloce e intuitiva",
                    "🔄 Sincronizzazione automatica",
                    "📱 Funziona anche offline",
                    "🔔 Notifiche smart personalizzabili"
                ])
            },
            "download_buttons": {
                "ios": {
                    "url": config.get("ios_url", "#ios-download"),
                    "badge_image": "assets/images/app-store-badge.png",
                    "version": config.get("ios_version", "Richiede iOS 14+"),
                    "size": config.get("ios_size", "42.3 MB")
                },
                "android": {
                    "url": config.get("android_url", "#android-download"),
                    "badge_image": "assets/images/google-play-badge.png",
                    "version": config.get("android_version", "Richiede Android 8+"),
                    "size": config.get("android_size", "38.7 MB")
                },
                "qr_code": {
                    "enabled": config.get("show_qr", True),
                    "image": "assets/images/download-qr.png",
                    "text": "Scansiona per scaricare"
                }
            },
            "app_stats": {
                "downloads": config.get("download_count", "1.2M+"),
                "rating": {
                    "ios": config.get("ios_rating", 4.8),
                    "android": config.get("android_rating", 4.6),
                    "average": config.get("avg_rating", 4.7)
                },
                "reviews_count": config.get("reviews", "45K+"),
                "featured_in": config.get("featured_stores", ["App Store Today", "Google Play Editors' Choice"])
            },
            "user_reviews": {
                "featured_reviews": [
                    {
                        "text": "La migliore app della categoria. Non posso più farne a meno!",
                        "author": "MarcoPro95",
                        "rating": 5,
                        "platform": "iOS"
                    },
                    {
                        "text": "Veloce, stabile e con tutte le funzioni che servono.",
                        "author": "TechLover",
                        "rating": 5,
                        "platform": "Android"
                    }
                ]
            },
            "device_compatibility": {
                "ios_devices": ["iPhone", "iPad", "Apple Watch"],
                "android_devices": ["Smartphone", "Tablet", "Wear OS"],
                "sync_features": "Sincronizzazione multi-device automatica"
            },
            "app_benefits": {
                "offline_mode": "Accesso completo anche offline",
                "push_notifications": "Notifiche intelligenti personalizzabili",
                "cloud_sync": "Backup automatico nel cloud",
                "security": "Crittografia avanzata e Face/Touch ID",
                "updates": "Aggiornamenti frequenti con nuove funzioni"
            },
            "alternative_access": {
                "web_app": {
                    "available": True,
                    "url": config.get("web_app_url", "#web-app"),
                    "text": "Preferisci il browser? Usa la Web App"
                },
                "desktop": {
                    "available": config.get("desktop_available", False),
                    "platforms": ["Windows", "macOS", "Linux"],
                    "url": config.get("desktop_url", "#desktop")
                }
            }
        }
    
    @staticmethod
    def get_template_by_type(template_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get CTA configuration by template type."""
        generators = {
            "lead_generation": CTAComponent.generate_lead_generation_cta,
            "sales_conversion": CTAComponent.generate_sales_conversion_cta,
            "trial_signup": CTAComponent.generate_trial_signup_cta,
            "consultation_booking": CTAComponent.generate_consultation_booking_cta,
            "newsletter_subscription": CTAComponent.generate_newsletter_subscription_cta,
            "app_download": CTAComponent.generate_app_download_cta
        }
        
        generator = generators.get(template_type)
        if not generator:
            raise ValueError(f"Template type '{template_type}' not found")
        
        return generator(config)