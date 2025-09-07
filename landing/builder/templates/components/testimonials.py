""" 
Testimonials Component Templates

Pre-built testimonials section templates optimized for building trust and credibility.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class TestimonialsTemplate:
    name: str
    description: str
    conversion_focus: str
    config: Dict[str, Any]


class TestimonialsComponent:
    """
    Testimonials section component with conversion-optimized templates.
    """
    
    @staticmethod
    def get_templates() -> Dict[str, TestimonialsTemplate]:
        """Get all available testimonials templates."""
        return {
            "social_proof": TestimonialsTemplate(
                name="Social Proof Testimonials",
                description="Testimonianze con focus su risultati e metriche",
                conversion_focus="trust_metrics",
                config={
                    "layout": "cards_grid",
                    "show_metrics": True,
                    "verified_badges": True,
                    "company_logos": True,
                    "rating_display": True
                }
            ),
            "video_testimonials": TestimonialsTemplate(
                name="Video Testimonials",
                description="Testimonianze video per massima autenticità",
                conversion_focus="authenticity",
                config={
                    "layout": "video_carousel",
                    "autoplay": False,
                    "captions": True,
                    "thumbnail_quotes": True,
                    "play_button_style": "centered"
                }
            ),
            "case_studies": TestimonialsTemplate(
                name="Case Study Testimonials",
                description="Storie di successo dettagliate con dati",
                conversion_focus="detailed_results",
                config={
                    "layout": "expandable_cards",
                    "before_after": True,
                    "timeline": True,
                    "roi_metrics": True,
                    "full_story_link": True
                }
            ),
            "industry_specific": TestimonialsTemplate(
                name="Industry Specific Testimonials",
                description="Testimonianze organizzate per settore",
                conversion_focus="relevance",
                config={
                    "layout": "tabbed_categories",
                    "industry_filters": True,
                    "role_badges": True,
                    "company_size": True,
                    "use_case_tags": True
                }
            ),
            "influencer_testimonials": TestimonialsTemplate(
                name="Influencer Testimonials",
                description="Testimonianze da opinion leader e influencer",
                conversion_focus="authority",
                config={
                    "layout": "featured_spotlight",
                    "social_links": True,
                    "follower_count": True,
                    "media_mentions": True,
                    "endorsement_badges": True
                }
            )
        }
    
    @staticmethod
    def generate_social_proof_testimonials(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social proof testimonials configuration."""
        default_testimonials = [
            {
                "text": "Abbiamo aumentato le conversioni del 250% in soli 3 mesi. Risultati incredibili!",
                "author": "Marco Rossi",
                "role": "CEO",
                "company": "TechStart Milano",
                "company_logo": "assets/logos/techstart.png",
                "rating": 5,
                "metrics": {
                    "conversions": "+250%",
                    "revenue": "+180%",
                    "time_saved": "20h/settimana"
                },
                "verified": True
            },
            {
                "text": "Il miglior investimento fatto quest'anno. ROI del 400% in 6 mesi.",
                "author": "Laura Bianchi",
                "role": "Marketing Director",
                "company": "E-commerce Pro",
                "company_logo": "assets/logos/ecommerce-pro.png",
                "rating": 5,
                "metrics": {
                    "roi": "400%",
                    "sales": "+320%",
                    "customers": "+1500"
                },
                "verified": True
            },
            {
                "text": "Supporto eccezionale e risultati che superano le aspettative.",
                "author": "Giuseppe Verdi",
                "role": "Founder",
                "company": "Digital Agency Roma",
                "company_logo": "assets/logos/digital-agency.png",
                "rating": 5,
                "metrics": {
                    "efficiency": "+85%",
                    "clients": "+40",
                    "revenue": "2x"
                },
                "verified": True
            }
        ]
        
        return {
            "section_title": config.get("title", "Cosa Dicono i Nostri Clienti"),
            "section_subtitle": config.get("subtitle", "Risultati reali da aziende come la tua"),
            "testimonials": config.get("testimonials", default_testimonials),
            "layout": {
                "type": "grid",
                "columns": 3,
                "style": "cards",
                "spacing": "medium"
            },
            "display_options": {
                "show_ratings": True,
                "show_metrics": True,
                "show_company_logos": True,
                "verified_badge": True,
                "hover_effect": "elevate"
            },
            "summary_stats": {
                "total_clients": config.get("total_clients", "5.000+"),
                "average_rating": config.get("avg_rating", "4.9/5"),
                "success_rate": config.get("success_rate", "98%"),
                "years_experience": config.get("experience", "10+")
            },
            "cta": {
                "text": config.get("cta_text", "Unisciti a Loro"),
                "url": config.get("cta_url", "#signup"),
                "style": "primary"
            }
        }
    
    @staticmethod
    def generate_video_testimonials(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video testimonials configuration."""
        default_videos = [
            {
                "video_url": "assets/videos/testimonial-1.mp4",
                "thumbnail": "assets/images/testimonial-thumb-1.jpg",
                "duration": "2:15",
                "quote": "La soluzione che ha trasformato il nostro business",
                "author": "Anna Martini",
                "role": "COO, Fashion Brand",
                "key_points": [
                    "Vendite aumentate del 300%",
                    "Processo automatizzato",
                    "Team più produttivo"
                ]
            },
            {
                "video_url": "assets/videos/testimonial-2.mp4",
                "thumbnail": "assets/images/testimonial-thumb-2.jpg",
                "duration": "1:45",
                "quote": "Risultati oltre ogni aspettativa",
                "author": "Roberto Ferrari",
                "role": "CEO, Tech Startup",
                "key_points": [
                    "ROI in 2 mesi",
                    "Scalabilità infinita",
                    "Supporto eccellente"
                ]
            }
        ]
        
        return {
            "section_title": config.get("title", "Ascolta Chi l'Ha Provato"),
            "section_subtitle": config.get("subtitle", "Storie vere di successo dai nostri clienti"),
            "videos": config.get("videos", default_videos),
            "layout": {
                "type": "carousel",
                "autoplay": False,
                "controls": True,
                "thumbnails_visible": 3
            },
            "player_config": {
                "show_captions": True,
                "show_transcript": True,
                "play_button": "centered",
                "progress_bar": True
            },
            "engagement_features": {
                "related_case_studies": True,
                "share_buttons": True,
                "download_transcript": True
            },
            "fallback_quotes": config.get("text_testimonials", [
                {
                    "text": "Un game changer per la nostra azienda",
                    "author": "Cliente Verificato",
                    "company": "Azienda Fortune 500"
                }
            ])
        }
    
    @staticmethod
    def generate_case_studies_testimonials(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate case studies testimonials configuration."""
        default_cases = [
            {
                "company": "Global Retail Chain",
                "industry": "E-commerce",
                "challenge": "Conversioni basse e carrelli abbandonati al 70%",
                "solution": "Implementazione del nostro sistema di ottimizzazione",
                "results": {
                    "conversion_rate": {"before": "2%", "after": "6.5%"},
                    "cart_abandonment": {"before": "70%", "after": "45%"},
                    "revenue": {"increase": "+225%", "timeframe": "4 mesi"}
                },
                "testimonial": "Hanno superato ogni nostra aspettativa. Un partner strategico essenziale.",
                "author": "Direttore E-commerce",
                "full_story_url": "#case-study-1"
            },
            {
                "company": "SaaS Startup",
                "industry": "Technology",
                "challenge": "Acquisizione clienti costosa e churn rate alto",
                "solution": "Strategia completa di growth hacking e retention",
                "results": {
                    "cac": {"before": "€500", "after": "€150"},
                    "churn_rate": {"before": "15%", "after": "5%"},
                    "ltv": {"increase": "+400%", "timeframe": "6 mesi"}
                },
                "testimonial": "Il loro approccio data-driven ha rivoluzionato il nostro business model.",
                "author": "CEO & Founder",
                "full_story_url": "#case-study-2"
            }
        ]
        
        return {
            "section_title": config.get("title", "Storie di Successo"),
            "section_subtitle": config.get("subtitle", "Come abbiamo aiutato aziende come la tua a crescere"),
            "case_studies": config.get("case_studies", default_cases),
            "layout": {
                "type": "expandable_cards",
                "initial_state": "collapsed",
                "show_timeline": True
            },
            "display_features": {
                "before_after_comparison": True,
                "results_visualization": "charts",
                "industry_badges": True,
                "implementation_timeline": True
            },
            "interaction": {
                "expand_animation": "smooth",
                "share_case_study": True,
                "download_pdf": True,
                "request_similar_analysis": True
            },
            "related_content": {
                "show_similar_cases": True,
                "industry_reports": True,
                "methodology_link": config.get("methodology_url", "#our-process")
            }
        }
    
    @staticmethod
    def generate_industry_specific_testimonials(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate industry specific testimonials configuration."""
        default_industries = {
            "ecommerce": [
                {
                    "text": "Vendite online aumentate del 300% in 6 mesi",
                    "author": "Maria Russo",
                    "company": "Fashion Store Online",
                    "role": "E-commerce Manager",
                    "company_size": "50-200 dipendenti",
                    "use_cases": ["Ottimizzazione conversioni", "Email marketing", "Personalizzazione"]
                }
            ],
            "saas": [
                {
                    "text": "Churn ridotto del 60% e LTV triplicato",
                    "author": "Paolo Verdi",
                    "company": "CloudTech Solutions",
                    "role": "Head of Growth",
                    "company_size": "10-50 dipendenti",
                    "use_cases": ["Onboarding", "Retention", "Upselling"]
                }
            ],
            "services": [
                {
                    "text": "Lead qualificati aumentati del 400%",
                    "author": "Francesca Bianchi",
                    "company": "Consulting Group",
                    "role": "Marketing Director",
                    "company_size": "200+ dipendenti",
                    "use_cases": ["Lead generation", "Nurturing", "Sales enablement"]
                }
            ]
        }
        
        return {
            "section_title": config.get("title", "Testimonianze dal Tuo Settore"),
            "section_subtitle": config.get("subtitle", "Scopri come aiutiamo aziende nel tuo mercato"),
            "industries": config.get("industries", default_industries),
            "layout": {
                "type": "tabs",
                "default_tab": config.get("default_industry", "ecommerce"),
                "show_filters": True
            },
            "filters": {
                "by_industry": True,
                "by_company_size": True,
                "by_use_case": True,
                "by_role": True
            },
            "display_options": {
                "show_company_info": True,
                "show_use_case_tags": True,
                "show_implementation_time": True,
                "highlight_similar_companies": True
            },
            "personalization": {
                "auto_detect_industry": True,
                "show_relevant_first": True,
                "custom_cta_by_industry": True
            },
            "cta_by_industry": config.get("industry_ctas", {
                "ecommerce": "Ottieni la Tua Analisi E-commerce Gratuita",
                "saas": "Richiedi Demo Personalizzata",
                "services": "Prenota Consulenza Strategica"
            })
        }
    
    @staticmethod
    def generate_influencer_testimonials(config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate influencer testimonials configuration."""
        default_influencers = [
            {
                "name": "Giulia Romano",
                "title": "Top Marketing Influencer",
                "photo": "assets/images/influencer-giulia.jpg",
                "testimonial": "Questa è la soluzione che consiglio a tutti i miei follower. Risultati garantiti!",
                "social_proof": {
                    "platform": "LinkedIn",
                    "followers": "150K+",
                    "engagement_rate": "8.5%"
                },
                "credentials": [
                    "Forbes 30 Under 30",
                    "TEDx Speaker",
                    "Autore Bestseller"
                ],
                "featured_in": ["Il Sole 24 Ore", "Forbes Italia", "Millionaire"],
                "social_links": {
                    "linkedin": "#",
                    "twitter": "#",
                    "instagram": "#"
                }
            },
            {
                "name": "Alessandro Conti",
                "title": "CEO & Digital Strategist",
                "photo": "assets/images/influencer-alessandro.jpg",
                "testimonial": "Ho testato decine di soluzioni. Questa è semplicemente la migliore sul mercato.",
                "social_proof": {
                    "platform": "YouTube",
                    "followers": "500K+",
                    "videos_views": "50M+"
                },
                "credentials": [
                    "Google Partner Premier",
                    "Facebook Marketing Partner",
                    "10+ anni esperienza"
                ],
                "featured_in": ["La Repubblica", "Corriere", "Sky TG24"],
                "social_links": {
                    "youtube": "#",
                    "linkedin": "#",
                    "website": "#"
                }
            }
        ]
        
        return {
            "section_title": config.get("title", "Raccomandato dai Leader del Settore"),
            "section_subtitle": config.get("subtitle", "Gli esperti più influenti parlano di noi"),
            "influencers": config.get("influencers", default_influencers),
            "layout": {
                "type": "spotlight",
                "featured_count": 2,
                "secondary_grid": True
            },
            "display_features": {
                "show_credentials": True,
                "show_social_proof": True,
                "show_media_mentions": True,
                "verified_checkmark": True
            },
            "engagement": {
                "social_links_active": True,
                "share_testimonial": True,
                "follow_cta": True,
                "endorsement_badges": True
            },
            "trust_indicators": {
                "total_reach": config.get("total_reach", "5M+ persone raggiunte"),
                "media_logos": config.get("media_logos", [
                    "forbes", "techcrunch", "entrepreneur", "inc"
                ]),
                "industry_awards": config.get("awards", [
                    "Best Marketing Tool 2024",
                    "Innovation Award"
                ])
            },
            "influencer_cta": {
                "text": "Diventa Anche Tu un Success Story",
                "url": "#get-started",
                "style": "premium"
            }
        }
    
    @staticmethod
    def get_template_by_type(template_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get testimonials configuration by template type."""
        generators = {
            "social_proof": TestimonialsComponent.generate_social_proof_testimonials,
            "video_testimonials": TestimonialsComponent.generate_video_testimonials,
            "case_studies": TestimonialsComponent.generate_case_studies_testimonials,
            "industry_specific": TestimonialsComponent.generate_industry_specific_testimonials,
            "influencer_testimonials": TestimonialsComponent.generate_influencer_testimonials
        }
        
        generator = generators.get(template_type)
        if not generator:
            raise ValueError(f"Template type '{template_type}' not found")
        
        return generator(config)