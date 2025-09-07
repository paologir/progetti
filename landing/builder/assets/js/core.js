// Landing Page Builder - Core JavaScript
// Optimized for performance and conversion tracking

(function(window, document) {
    'use strict';

    // Core utility functions
    const LandingPage = {
        // DOM utilities
        $: function(selector) {
            return document.querySelector(selector);
        },

        $$: function(selector) {
            return document.querySelectorAll(selector);
        },

        ready: function(callback) {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', callback);
            } else {
                callback();
            }
        },

        // Debounce function for performance
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Throttle function for scroll events
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        // Element visibility checker
        isInViewport: function(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        },

        // Smooth element scrolling
        scrollToElement: function(element, offset = 0) {
            const elementTop = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementTop - offset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        },

        // Cookie utilities
        setCookie: function(name, value, days = 30) {
            const expires = new Date();
            expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
        },

        getCookie: function(name) {
            const nameEQ = name + '=';
            const ca = document.cookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        },

        // Local storage with fallback
        storage: {
            set: function(key, value) {
                try {
                    localStorage.setItem(key, JSON.stringify(value));
                } catch (e) {
                    LandingPage.setCookie(key, JSON.stringify(value));
                }
            },

            get: function(key) {
                try {
                    const item = localStorage.getItem(key);
                    return item ? JSON.parse(item) : null;
                } catch (e) {
                    const cookie = LandingPage.getCookie(key);
                    return cookie ? JSON.parse(cookie) : null;
                }
            }
        }
    };

    // Make LandingPage globally available
    window.LandingPage = LandingPage;

    // Form Validation System
    LandingPage.FormValidator = {
        rules: {},
        messages: {},

        // Initialize form validation
        init: function() {
            const forms = LandingPage.$$('form[data-validate]');
            forms.forEach(form => this.setupForm(form));
        },

        // Setup individual form
        setupForm: function(form) {
            const fields = form.querySelectorAll('input, textarea, select');
            fields.forEach(field => this.setupField(field));

            form.addEventListener('submit', (e) => this.handleSubmit(e, form));
        },

        // Setup individual field
        setupField: function(field) {
            // Real-time validation on input
            field.addEventListener('input', LandingPage.debounce(() => {
                this.validateField(field);
            }, 300));

            // Validation on blur
            field.addEventListener('blur', () => {
                this.validateField(field);
            });
        },

        // Validate individual field
        validateField: function(field) {
            const value = field.value.trim();
            const fieldName = field.name || field.id;
            let isValid = true;
            let errorMessage = '';

            // Required field validation
            if (field.hasAttribute('required') && !value) {
                isValid = false;
                errorMessage = 'Questo campo è obbligatorio';
            }

            // Email validation
            else if (field.type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    errorMessage = 'Inserisci un indirizzo email valido';
                }
            }

            // Phone validation
            else if (field.type === 'tel' && value) {
                const phoneRegex = /^[\+]?[1-9][\d\s\-\(\)]{7,15}$/;
                if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                    isValid = false;
                    errorMessage = 'Inserisci un numero di telefono valido';
                }
            }

            // Minimum length validation
            else if (field.hasAttribute('data-min-length') && value) {
                const minLength = parseInt(field.getAttribute('data-min-length'));
                if (value.length < minLength) {
                    isValid = false;
                    errorMessage = `Minimo ${minLength} caratteri richiesti`;
                }
            }

            // Maximum length validation
            else if (field.hasAttribute('data-max-length') && value) {
                const maxLength = parseInt(field.getAttribute('data-max-length'));
                if (value.length > maxLength) {
                    isValid = false;
                    errorMessage = `Massimo ${maxLength} caratteri consentiti`;
                }
            }

            // Custom pattern validation
            else if (field.hasAttribute('pattern') && value) {
                const pattern = new RegExp(field.getAttribute('pattern'));
                if (!pattern.test(value)) {
                    isValid = false;
                    errorMessage = field.getAttribute('data-pattern-message') || 'Formato non valido';
                }
            }

            this.showFieldFeedback(field, isValid, errorMessage);
            return isValid;
        },

        // Show field validation feedback
        showFieldFeedback: function(field, isValid, message) {
            const formGroup = field.closest('.form-group');
            if (!formGroup) return;

            // Remove existing feedback
            const existingError = formGroup.querySelector('.form-error');
            if (existingError) existingError.remove();

            // Update field classes
            field.classList.remove('error', 'success');
            field.classList.add(isValid ? 'success' : 'error');

            // Add error message if invalid
            if (!isValid && message) {
                const errorElement = document.createElement('div');
                errorElement.className = 'form-error';
                errorElement.textContent = message;
                errorElement.setAttribute('role', 'alert');
                formGroup.appendChild(errorElement);
            }
        },

        // Handle form submission
        handleSubmit: function(event, form) {
            event.preventDefault();

            const fields = form.querySelectorAll('input, textarea, select');
            let isFormValid = true;

            // Validate all fields
            fields.forEach(field => {
                if (!this.validateField(field)) {
                    isFormValid = false;
                }
            });

            if (isFormValid) {
                this.submitForm(form);
            } else {
                // Focus on first invalid field
                const firstError = form.querySelector('.error');
                if (firstError) {
                    firstError.focus();
                    LandingPage.scrollToElement(firstError, 100);
                }
            }
        },

        // Submit validated form
        submitForm: function(form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            // Show loading state
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;

            // Collect form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Track conversion
            if (window.gtag) {
                gtag('event', 'form_submit', {
                    'event_category': 'engagement',
                    'event_label': form.id || 'landing_form'
                });
            }

            // Submit via AJAX
            fetch(form.action || '/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    this.showSuccessMessage(form, result.message);
                    form.reset();
                    form.submitted = true;

                    // Track successful conversion
                    if (window.gtag) {
                        gtag('event', 'conversion', {
                            'event_category': 'form',
                            'event_label': 'form_success'
                        });
                    }
                } else {
                    this.showErrorMessage(form, result.message || 'Si è verificato un errore');
                }
            })
            .catch(error => {
                console.error('Form submission error:', error);
                this.showErrorMessage(form, 'Errore di connessione. Riprova più tardi.');
            })
            .finally(() => {
                // Reset button state
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        },

        // Show success message
        showSuccessMessage: function(form, message) {
            const successDiv = document.createElement('div');
            successDiv.className = 'form-success alert alert-success';
            successDiv.innerHTML = `
                <strong>Successo!</strong> ${message || 'Form inviato correttamente.'}
            `;
            form.parentNode.insertBefore(successDiv, form);

            // Auto-hide after 5 seconds
            setTimeout(() => {
                if (successDiv.parentNode) {
                    successDiv.remove();
                }
            }, 5000);
        },

        // Show error message
        showErrorMessage: function(form, message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error alert alert-error';  
            errorDiv.innerHTML = `
                <strong>Errore!</strong> ${message}
            `;
            form.parentNode.insertBefore(errorDiv, form);

            // Auto-hide after 7 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 7000);
        }
    };

    // Analytics & Conversion Tracking
    LandingPage.Analytics = {
        init: function() {
            this.trackPageView();
            this.setupScrollTracking();
            this.setupClickTracking();
            this.setupFormTracking();
        },

        trackPageView: function() {
            if (window.gtag) {
                gtag('config', 'GA_MEASUREMENT_ID', {
                    page_title: document.title,
                    page_location: window.location.href
                });
            }

            // Track time spent on page
            const startTime = Date.now();
            window.addEventListener('beforeunload', () => {
                const timeSpent = Math.round((Date.now() - startTime) / 1000);
                if (window.gtag && timeSpent > 10) {
                    gtag('event', 'engagement_time', {
                        'event_category': 'engagement',
                        'value': timeSpent
                    });
                }
            });
        },

        setupScrollTracking: function() {
            let scrollPercents = [25, 50, 75, 90];
            let trackedPercents = [];

            const trackScroll = LandingPage.throttle(() => {
                const scrollPercent = Math.round(
                    (window.pageYOffset / (document.documentElement.scrollHeight - window.innerHeight)) * 100
                );

                scrollPercents.forEach(percent => {
                    if (scrollPercent >= percent && !trackedPercents.includes(percent)) {
                        trackedPercents.push(percent);
                        if (window.gtag) {
                            gtag('event', 'scroll_depth', {
                                'event_category': 'engagement',
                                'event_label': `${percent}%`,
                                'value': percent
                            });
                        }
                    }
                });
            }, 250);

            window.addEventListener('scroll', trackScroll);
        },

        setupClickTracking: function() {
            // Track CTA button clicks
            const ctaButtons = LandingPage.$$('.btn-primary, .btn-accent, [data-track="cta"]');
            ctaButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const buttonText = e.target.textContent.trim();
                    const buttonId = e.target.id || 'unnamed_cta';

                    if (window.gtag) {
                        gtag('event', 'cta_click', {
                            'event_category': 'conversion',
                            'event_label': buttonText,
                            'button_id': buttonId
                        });
                    }
                });
            });

            // Track external link clicks
            const externalLinks = LandingPage.$$('a[href^="http"]:not([href*="' + window.location.hostname + '"])');
            externalLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    if (window.gtag) {
                        gtag('event', 'external_link_click', {
                            'event_category': 'engagement',
                            'event_label': e.target.href
                        });
                    }
                });
            });
        },

        setupFormTracking: function() {
            const forms = LandingPage.$$('form');
            forms.forEach(form => {
                // Track form start (first interaction)
                let formStarted = false;
                const inputs = form.querySelectorAll('input, textarea, select');

                inputs.forEach(input => {
                    input.addEventListener('focus', () => {
                        if (!formStarted) {
                            formStarted = true;
                            if (window.gtag) {
                                gtag('event', 'form_start', {
                                    'event_category': 'engagement',
                                    'event_label': form.id || 'landing_form'
                                });
                            }
                        }
                    });
                });

                // Track form abandonment
                let formTouched = false;
                inputs.forEach(input => {
                    input.addEventListener('input', () => {
                        formTouched = true;
                    });
                });

                window.addEventListener('beforeunload', () => {
                    if (formTouched && !form.submitted) {
                        if (window.gtag) {
                            gtag('event', 'form_abandon', {
                                'event_category': 'conversion',
                                'event_label': form.id || 'landing_form'
                            });
                        }
                    }
                });
            });
        },

        // Custom event tracking function
        track: function(eventName, category = 'custom', label = '', value = null) {
            if (window.gtag) {
                const eventData = {
                    'event_category': category
                };

                if (label) eventData.event_label = label;
                if (value !== null) eventData.value = value;

                gtag('event', eventName, eventData);
            }

            // Also send to Facebook Pixel if available
            if (window.fbq) {
                fbq('track', 'CustomEvent', {
                    event_name: eventName,
                    event_category: category
                });
            }
        }
    };

    // Initialize all systems when DOM is ready
    LandingPage.ready(() => {
        // Initialize core systems
        LandingPage.FormValidator.init();
        LandingPage.Analytics.init();

        // Custom initialization hook for page-specific code
        if (typeof window.landingPageInit === 'function') {
            window.landingPageInit();
        }

        // Performance monitoring
        if ('performance' in window && 'measure' in performance) {
            performance.mark('landing-page-init-complete');
        }
    });

})(window, document);