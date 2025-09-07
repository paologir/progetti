""" 
Pricing Component Templates

Pre-built pricing section templates optimized for conversions and sales.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class PricingTemplate:
    name: str
    description: str
    conversion_focus: str
    config: Dict[str, Any]


class PricingComponent:
    """
    Pricing section component with conversion-optimized templates.
    """
    
    @staticmethod
    def get_templates() -> Dict[str, PricingTemplate]:
        """Get all available pricing templates."""
        return {
            "saas_pricing": PricingTemplate(
                name="SaaS Subscription Pricing",
                description="Piani mensili/annuali con trial gratuito",
                conversion_focus="subscription_growth",
                config={
                    "layout": "three_tier",
                    "highlight_popular": True,
                    "annual_discount": True,
                    "free_trial": True,
                    "feature_comparison": True
                }
            ),
            "course_pricing": PricingTemplate(
                name="Course/Training Pricing",
                description="Prezzi per corsi online con bonus e garanzie",
                conversion_focus="educational_value",
                config={
                    "layout": "single_offer_focus",
                    "payment_plans": True,
                    "bonus_stacking": True,
                    "money_back_guarantee": True,
                    "early_bird_pricing": True
                }
            ),
            "service_pricing": PricingTemplate(
                name="Service/Consulting Pricing",
                description="Pacchetti di servizi con prezzi personalizzabili",
                conversion_focus="value_justification",
                config={
                    "layout": "tiered_packages",
                    "custom_quote": True,
                    "consultation_included": True,
                    "roi_calculator": True,
                    "case_study_links": True
                }
            ),
            "product_pricing": PricingTemplate(
                name="Physical Product Pricing",
                description="E-commerce con varianti e sconti volume",
                conversion_focus="purchase_urgency",
                config={
                    "layout": "product_variants",
                    "bulk_discounts": True,
                    "limited_time_offers": True,
                    "shipping_calculator": True,
                    "secure_checkout": True
                }
            ),
            "freemium_pricing": PricingTemplate(
                name="Freemium Model Pricing",
                description="Piano gratuito + upgrade premium",
                conversion_focus="free_to_paid_conversion",
                config={
                    "layout": "free_vs_premium",
                    "usage_limits": True,
                    "upgrade_incentives": True,
                    "feature_gating": True,
                    "trial_upgrade_flow": True
                }
            )
        }
    
    @staticmethod
    def generate_saas_pricing(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SaaS subscription pricing configuration."""
        default_plans = [
            {
                "name": "Starter",
                "subtitle": "Perfetto per iniziare",
                "price": {
                    "monthly": 29,
                    "annually": 290,
                    "currency": "€",
                    "billing_cycle": "al mese"
                },
                "features": [
                    "Fino a 1.000 contatti",
                    "5 campagne al mese",
                    "Analytics di base",
                    "Supporto email",
                    "Integrazione Zapier"
                ],
                "cta": "Inizia Gratis",
                "trial_days": 14,
                "setup_fee": None,
                "popular": False
            },
            {
                "name": "Professional",
                "subtitle": "Il più scelto",
                "price": {
                    "monthly": 79,
                    "annually": 790,
                    "currency": "€",
                    "billing_cycle": "al mese"
                },
                "features": [
                    "Fino a 10.000 contatti",
                    "Campagne illimitate",
                    "Analytics avanzate",
                    "Supporto prioritario",
                    "Tutte le integrazioni",
                    "Automazioni avanzate",
                    "A/B testing"
                ],
                "cta": "Prova Gratis",
                "trial_days": 14,
                "setup_fee": None,
                "popular": True,
                "savings": "Risparmi €158/anno"
            },
            {
                "name": "Enterprise",
                "subtitle": "Per grandi team",
                "price": {
                    "monthly": 199,
                    "annually": 1990,
                    "currency": "€",
                    "billing_cycle": "al mese"
                },
                "features": [
                    "Contatti illimitati",
                    "Tutto del Pro +",
                    "Account manager dedicato",
                    "SLA garantito",
                    "Integrazioni custom",
                    "White label",
                    "SSO e sicurezza avanzata"
                ],
                "cta": "Contattaci",
                "trial_days": 30,
                "setup_fee": "Gratis (valore €500)",
                "popular": False
            }
        ]
        
        return {
            "section_title": config.get("title", "Scegli il Piano Perfetto per Te"),
            "section_subtitle": config.get("subtitle", "Inizia gratis, paga solo quando cresci"),
            "billing_toggle": {
                "monthly_label": "Mensile",
                "annual_label": "Annuale",
                "annual_discount": "Risparmia 2 mesi",
                "default": "annual"
            },
            "plans": config.get("plans", default_plans),
            "layout": {
                "style": "cards",
                "columns": 3,
                "highlight_popular": True,
                "equal_height": True
            },
            "trust_elements": {
                "money_back_guarantee": "Garanzia 30 giorni",
                "no_setup_fees": "Nessun costo di attivazione",
                "cancel_anytime": "Cancella quando vuoi",
                "secure_payment": "Pagamenti sicuri SSL"
            },
            "feature_comparison": {
                "show_full_table": True,
                "categories": [
                    "Contatti e Database",
                    "Campagne Marketing",
                    "Analytics e Report",
                    "Supporto e Servizi"
                ]
            },
            "faq_preview": [
                {
                    "question": "Posso cambiare piano in qualsiasi momento?",
                    "answer": "Sì, puoi aggiornare o ridurre il piano quando vuoi."
                },
                {
                    "question": "Cosa succede dopo il trial gratuito?",
                    "answer": "Scegli un piano o continua gratis con funzionalità limitate."
                }
            ]
        }
    
    @staticmethod
    def generate_course_pricing(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate course/training pricing configuration."""
        return {
            "section_title": config.get("title", "Investi nel Tuo Futuro Oggi"),
            "section_subtitle": config.get("subtitle", "Ottieni accesso completo al corso + bonus esclusivi"),
            "main_offer": {
                "course_title": config.get("course_title", "Corso Completo di Digital Marketing"),
                "original_price": config.get("original_price", 997),
                "current_price": config.get("current_price", 497),
                "currency": "€",
                "discount_percentage": 50,
                "payment_options": [
                    {
                        "type": "full",
                        "price": 497,
                        "label": "Pagamento Unico",
                        "savings": "Risparmi €50",
                        "popular": True
                    },
                    {
                        "type": "installments",
                        "price": 182,
                        "installments": 3,
                        "label": "3 rate mensili",
                        "total": 546,
                        "popular": False
                    }
                ]
            },
            "bonus_stack": {
                "title": "Bonus Esclusivi Inclusi",
                "total_value": config.get("bonus_value", 2847),
                "items": config.get("bonuses", [
                    {
                        "name": "Template Email Marketing",
                        "value": 297,
                        "description": "50+ template pronti all'uso"
                    },
                    {
                        "name": "Checklist Strategiche",
                        "value": 197,
                        "description": "Tutti i passaggi essenziali"
                    },
                    {
                        "name": "Gruppo Facebook Privato",
                        "value": 497,
                        "description": "Community esclusiva degli studenti"
                    },
                    {
                        "name": "Sessione Q&A Live Mensile",
                        "value": 997,
                        "description": "Accesso diretto all'esperto"
                    },
                    {
                        "name": "Aggiornamenti a Vita",
                        "value": 297,
                        "description": "Sempre al passo coi tempi"
                    }
                ])
            },
            "guarantee": {
                "type": "money_back",
                "period": "60 giorni",
                "title": "Garanzia Soddisfatti o Rimborsati",
                "description": "Prova il corso senza rischi. Se non sei soddisfatto, ti rimborsiamo tutto.",
                "badge_image": "assets/images/60-day-guarantee.png"
            },
            "urgency_elements": {
                "limited_spots": {
                    "enabled": True,
                    "remaining": config.get("spots_left", 23),
                    "total": 100,
                    "message": "Solo {remaining} posti rimasti a questo prezzo!"
                },
                "early_bird": {
                    "enabled": True,
                    "deadline": config.get("deadline", "2024-12-31T23:59:59"),
                    "discount_expires": "Offerta Early Bird scade tra:"
                }
            },
            "social_proof": {
                "students_count": config.get("students", "3.247+"),
                "success_rate": config.get("success_rate", "94%"),
                "average_rating": config.get("rating", "4.9/5"),
                "completion_rate": config.get("completion", "87%")
            },
            "course_details": {
                "modules": config.get("modules", 12),
                "videos": config.get("videos", 87),
                "duration": config.get("duration", "25+ ore"),
                "certificate": True,
                "lifetime_access": True,
                "mobile_access": True
            },
            "instructor_credibility": {
                "name": config.get("instructor", "Marco Rossi"),
                "credentials": config.get("credentials", [
                    "15+ anni di esperienza",
                    "Consulente per Fortune 500",
                    "Autore bestseller",
                    "Speaker internazionale"
                ]),
                "results": config.get("instructor_results", [
                    "Ha formato 50.000+ professionisti",
                    "Risultati medi: +200% ROI",
                    "Metodo testato su 1.000+ progetti"
                ])
            }
        }
    
    @staticmethod
    def generate_service_pricing(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service/consulting pricing configuration."""
        default_packages = [
            {
                "name": "Consulenza Base",
                "subtitle": "Analisi e strategia",
                "price": {
                    "amount": 2500,
                    "currency": "€",
                    "unit": "progetto"
                },
                "duration": "2-3 settimane",
                "deliverables": [
                    "Analisi approfondita del business",
                    "Piano strategico personalizzato",
                    "Roadmap implementazione",
                    "2 call di follow-up"
                ],
                "ideal_for": "Startup e PMI",
                "cta": "Richiedi Proposta",
                "popular": False
            },
            {
                "name": "Implementazione Pro",
                "subtitle": "Strategia + Esecuzione",
                "price": {
                    "amount": 7500,
                    "currency": "€",
                    "unit": "progetto"
                },
                "duration": "6-8 settimane",
                "deliverables": [
                    "Tutto del pacchetto Base +",
                    "Implementazione completa",
                    "Setup tecnico e configurazioni",
                    "Training del team",
                    "30 giorni di supporto post-lancio"
                ],
                "ideal_for": "Aziende in crescita",
                "cta": "Inizia Subito",
                "popular": True,
                "savings": "Risparmi €1.500 vs servizi separati"
            },
            {
                "name": "Partnership Enterprise",
                "subtitle": "Soluzione completa",
                "price": {
                    "amount": "Su misura",
                    "currency": "",
                    "unit": "",
                    "starting_from": 15000
                },
                "duration": "3-6 mesi",
                "deliverables": [
                    "Tutto del pacchetto Pro +",
                    "Account manager dedicato",
                    "Ottimizzazioni continue",
                    "Report mensili KPI",
                    "Supporto prioritario 24/7",
                    "Accesso agli strumenti enterprise"
                ],
                "ideal_for": "Grandi aziende",
                "cta": "Prenota Call",
                "popular": False
            }
        ]
        
        return {
            "section_title": config.get("title", "Pacchetti di Servizi"),
            "section_subtitle": config.get("subtitle", "Soluzioni professionali per ogni budget e obiettivo"),
            "packages": config.get("packages", default_packages),
            "layout": {
                "style": "detailed_cards",
                "show_comparison": True,
                "highlight_recommended": True
            },
            "value_proposition": {
                "expertise": "15+ anni di esperienza",
                "track_record": "500+ progetti completati",
                "results": "ROI medio 300% in 12 mesi",
                "guarantee": "Risultati garantiti o rimborso"
            },
            "roi_calculator": {
                "enabled": True,
                "title": "Calcola il Tuo ROI",
                "inputs": [
                    {"label": "Fatturato mensile attuale", "type": "number", "unit": "€"},
                    {"label": "Margine di profitto", "type": "percentage", "unit": "%"},
                    {"label": "Obiettivo di crescita", "type": "percentage", "unit": "%"}
                ],
                "cta": "Calcola il Potenziale ROI"
            },
            "consultation_offer": {
                "title": "Consulenza Gratuita di 30 Minuti",
                "description": "Analizziamo insieme la tua situazione e ti proponiamo la soluzione migliore",
                "includes": [
                    "Analisi della situazione attuale",
                    "Identificazione opportunità",
                    "Proposta strategica personalizzata",
                    "Piano d'azione preliminare"
                ],
                "cta": "Prenota Consulenza Gratuita",
                "booking_url": config.get("booking_url", "#consultation")
            },
            "case_studies_preview": {
                "title": "Risultati dei Nostri Clienti",
                "examples": config.get("case_examples", [
                    {"client": "E-commerce Fashion", "result": "+250% vendite online"},
                    {"client": "SaaS B2B", "result": "+400% lead qualificati"},
                    {"client": "Consulenza", "result": "+180% fatturato annuo"}
                ]),
                "cta": "Vedi Tutti i Casi Studio"
            },
            "payment_terms": {
                "options": [
                    "50% all'inizio, 50% a completamento",
                    "Rate mensili per progetti lunghi",
                    "Pagamento unico (sconto 5%)"
                ],
                "currencies": ["€", "$"],
                "invoicing": "Fatturazione elettronica inclusa"
            }
        }
    
    @staticmethod
    def generate_product_pricing(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate physical product pricing configuration."""
        default_variants = [
            {
                "name": "Confezione Singola",
                "quantity": 1,
                "price": 49.99,
                "original_price": 69.99,
                "savings": 20,
                "per_unit": 49.99,
                "shipping": 9.99,
                "delivery": "3-5 giorni",
                "popular": False
            },
            {
                "name": "Confezione Doppia",
                "quantity": 2,
                "price": 89.99,
                "original_price": 139.98,
                "savings": 50,
                "per_unit": 44.99,
                "shipping": "Gratis",
                "delivery": "3-5 giorni",
                "popular": True,
                "badge": "Più Conveniente"
            },
            {
                "name": "Confezione Famiglia",
                "quantity": 4,
                "price": 159.99,
                "original_price": 279.96,
                "savings": 120,
                "per_unit": 39.99,
                "shipping": "Gratis",
                "delivery": "3-5 giorni",
                "popular": False,
                "badge": "Miglior Valore"
            }
        ]
        
        return {
            "section_title": config.get("title", "Scegli la Tua Confezione"),
            "section_subtitle": config.get("subtitle", "Più acquisti, più risparmi! Spedizione gratuita da 2 pezzi"),
            "product_variants": config.get("variants", default_variants),
            "layout": {
                "style": "product_grid",
                "show_savings": True,
                "highlight_value": True
            },
            "urgency_elements": {
                "limited_stock": {
                    "enabled": True,
                    "remaining": config.get("stock_remaining", 47),
                    "message": "Solo {remaining} pezzi rimasti!"
                },
                "flash_sale": {
                    "enabled": config.get("flash_sale", True),
                    "discount": 30,
                    "expires": "2024-12-31T23:59:59",
                    "message": "Flash Sale: 30% di sconto ancora per:"
                }
            },
            "shipping_info": {
                "free_threshold": 79,
                "standard_cost": 9.99,
                "express_available": True,
                "express_cost": 19.99,
                "delivery_areas": "Spediamo in tutta Italia",
                "tracking": "Tracking incluso"
            },
            "guarantees": {
                "satisfaction": {
                    "period": "30 giorni",
                    "title": "Soddisfatti o Rimborsati",
                    "description": "Non ti piace? Ti rimborsiamo tutto senza domande"
                },
                "warranty": {
                    "period": "2 anni",
                    "title": "Garanzia del Produttore",
                    "description": "Riparazione o sostituzione gratuita"
                }
            },
            "payment_security": {
                "ssl_secured": True,
                "payment_methods": ["Carta di credito", "PayPal", "Apple Pay", "Google Pay"],
                "secure_checkout": "Checkout sicuro e protetto",
                "data_protection": "I tuoi dati sono al sicuro"
            },
            "reviews_summary": {
                "average_rating": config.get("rating", 4.8),
                "total_reviews": config.get("reviews_count", 2847),
                "recommendation_rate": config.get("recommendation", 96),
                "featured_review": config.get("featured_review", {
                    "text": "Prodotto fantastico, supera le aspettative!",
                    "author": "Claudia M.",
                    "rating": 5,
                    "verified": True
                })
            },
            "bundle_offers": {
                "enabled": True,
                "title": "Aggiungi al Tuo Ordine",
                "items": config.get("bundle_items", [
                    {
                        "name": "Accessorio Premium",
                        "price": 19.99,
                        "original_price": 29.99,
                        "image": "assets/images/accessory.jpg",
                        "popular": True
                    }
                ])
            }
        }
    
    @staticmethod
    def generate_freemium_pricing(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate freemium model pricing configuration."""
        return {
            "section_title": config.get("title", "Inizia Gratis, Cresci con Noi"),
            "section_subtitle": config.get("subtitle", "Prova tutte le funzionalità gratuitamente, aggiorna quando sei pronto"),
            "plans_comparison": {
                "free_plan": {
                    "name": "Gratuito",
                    "subtitle": "Per sempre",
                    "price": 0,
                    "features": [
                        {"name": "Fino a 100 contatti", "included": True},
                        {"name": "5 email al mese", "included": True},
                        {"name": "Template di base", "included": True},
                        {"name": "Analytics di base", "included": True},
                        {"name": "Supporto community", "included": True},
                        {"name": "Branding rimovibile", "included": False},
                        {"name": "Email illimitate", "included": False},
                        {"name": "Automazioni", "included": False},
                        {"name": "Analytics avanzate", "included": False},
                        {"name": "Supporto prioritario", "included": False}
                    ],
                    "limitations": [
                        "Branding nella footer",
                        "Limite 5 email/mese",
                        "Solo template base"
                    ],
                    "cta": "Inizia Gratis"
                },
                "premium_plan": {
                    "name": "Premium",
                    "subtitle": "Il più completo",
                    "price": 29,
                    "billing": "al mese",
                    "features": [
                        {"name": "Fino a 10.000 contatti", "included": True},
                        {"name": "Email illimitate", "included": True},
                        {"name": "Tutti i template", "included": True},
                        {"name": "Analytics avanzate", "included": True},
                        {"name": "Supporto prioritario", "included": True},
                        {"name": "Branding rimosso", "included": True},
                        {"name": "Automazioni avanzate", "included": True},
                        {"name": "A/B testing", "included": True},
                        {"name": "Integrazioni premium", "included": True},
                        {"name": "API access", "included": True}
                    ],
                    "cta": "Aggiorna Ora",
                    "trial_days": 14
                }
            },
            "upgrade_incentives": {
                "usage_approaching_limit": {
                    "trigger": "80% del limite",
                    "message": "Stai raggiungendo il limite. Aggiorna per continuare senza interruzioni.",
                    "discount": "50% di sconto sul primo mese"
                },
                "feature_discovery": {
                    "locked_features": [
                        "Automazioni email",
                        "Segmentazione avanzata",
                        "Report dettagliati",
                        "Integrazioni premium"
                    ],
                    "trial_offer": "Prova Premium gratis per 14 giorni"
                }
            },
            "migration_support": {
                "title": "Passaggio Senza Problemi",
                "benefits": [
                    "Migrazione dati automatica",
                    "Assistenza dedicata",
                    "Nessuna interruzione del servizio",
                    "Downgrade possibile in qualsiasi momento"
                ],
                "onboarding": {
                    "setup_call": "Call di setup gratuita",
                    "training_resources": "Video tutorial dedicati",
                    "success_manager": "Success manager personale"
                }
            },
            "success_metrics": {
                "free_to_paid_rate": config.get("conversion_rate", "23%"),
                "user_satisfaction": config.get("satisfaction", "4.7/5"),
                "average_upgrade_time": config.get("upgrade_time", "45 giorni"),
                "feature_adoption": config.get("adoption", "89%")
            },
            "faq_upgrade": [
                {
                    "question": "Cosa succede ai miei dati se aggiorno?",
                    "answer": "Tutti i tuoi dati rimangono intatti e ottieni immediatamente accesso alle funzioni premium."
                },
                {
                    "question": "Posso tornare al piano gratuito?",
                    "answer": "Sì, puoi fare downgrade in qualsiasi momento. I dati rimarranno salvati."
                },
                {
                    "question": "Come funziona il periodo di prova premium?",
                    "answer": "14 giorni gratis con tutte le funzioni premium. Nessun vincolo, cancelli quando vuoi."
                }
            ]
        }
    
    @staticmethod
    def get_template_by_type(template_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing configuration by template type."""
        generators = {
            "saas_pricing": PricingComponent.generate_saas_pricing,
            "course_pricing": PricingComponent.generate_course_pricing,
            "service_pricing": PricingComponent.generate_service_pricing,
            "product_pricing": PricingComponent.generate_product_pricing,
            "freemium_pricing": PricingComponent.generate_freemium_pricing
        }
        
        generator = generators.get(template_type)
        if not generator:
            raise ValueError(f"Template type '{template_type}' not found")
        
        return generator(config)