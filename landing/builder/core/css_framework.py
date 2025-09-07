"""
CSS Framework - Responsive Grid/Flexbox System

Modern CSS framework optimized for landing pages with Core Web Vitals
performance and conversion-focused design patterns.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class BreakpointSize(Enum):
    XS = "xs"  # 0px+
    SM = "sm"  # 576px+
    MD = "md"  # 768px+
    LG = "lg"  # 992px+
    XL = "xl"  # 1200px+
    XXL = "xxl"  # 1400px+


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


class CSSFramework:
    """
    Modern CSS framework for high-converting landing pages.
    """
    
    def __init__(self, color_scheme: ColorScheme = None, typography: Typography = None):
        self.color_scheme = color_scheme or self._get_default_colors()
        self.typography = typography or self._get_default_typography()
        self.breakpoints = self._get_breakpoints()
        
    def _get_default_colors(self) -> ColorScheme:
        """Get default conversion-optimized color scheme."""
        return ColorScheme(
            primary="#2563eb",      # Blue - trust and action
            secondary="#7c3aed",    # Purple - premium feel
            accent="#f59e0b",       # Orange - urgency/CTA
            success="#10b981",      # Green - success states
            warning="#f59e0b",      # Amber - warnings
            error="#ef4444",        # Red - errors
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
    
    def _get_default_typography(self) -> Typography:
        """Get default typography optimized for readability."""
        return Typography(
            font_family_primary="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            font_family_secondary="'Playfair Display', Georgia, serif",
            font_size_base="16px",
            line_height_base=1.6,
            letter_spacing_base="-0.01em",
            h1_size="clamp(2.5rem, 4vw, 4rem)",      # 40-64px responsive
            h2_size="clamp(2rem, 3vw, 3rem)",        # 32-48px responsive  
            h3_size="clamp(1.5rem, 2.5vw, 2rem)",    # 24-32px responsive
            h4_size="clamp(1.25rem, 2vw, 1.5rem)",   # 20-24px responsive
            h5_size="1.125rem",                       # 18px
            h6_size="1rem"                            # 16px
        )
    
    def _get_breakpoints(self) -> Dict[str, str]:
        """Get responsive breakpoints."""
        return {
            "xs": "0",
            "sm": "576px", 
            "md": "768px",
            "lg": "992px",
            "xl": "1200px",
            "xxl": "1400px"
        }
    
    def generate_css_variables(self) -> str:
        """Generate CSS custom properties for theming."""
        css_vars = [
            ":root {",
            "  /* Colors */",
            f"  --color-primary: {self.color_scheme.primary};",
            f"  --color-secondary: {self.color_scheme.secondary};", 
            f"  --color-accent: {self.color_scheme.accent};",
            f"  --color-success: {self.color_scheme.success};",
            f"  --color-warning: {self.color_scheme.warning};",
            f"  --color-error: {self.color_scheme.error};",
            "",
            "  /* Neutral Colors */",
            f"  --color-neutral-50: {self.color_scheme.neutral_50};",
            f"  --color-neutral-100: {self.color_scheme.neutral_100};",
            f"  --color-neutral-200: {self.color_scheme.neutral_200};",
            f"  --color-neutral-300: {self.color_scheme.neutral_300};",
            f"  --color-neutral-400: {self.color_scheme.neutral_400};",
            f"  --color-neutral-500: {self.color_scheme.neutral_500};",
            f"  --color-neutral-600: {self.color_scheme.neutral_600};",
            f"  --color-neutral-700: {self.color_scheme.neutral_700};",
            f"  --color-neutral-800: {self.color_scheme.neutral_800};",
            f"  --color-neutral-900: {self.color_scheme.neutral_900};",
            "",
            "  /* Typography */",
            f"  --font-family-primary: {self.typography.font_family_primary};",
            f"  --font-family-secondary: {self.typography.font_family_secondary};",
            f"  --font-size-base: {self.typography.font_size_base};",
            f"  --line-height-base: {self.typography.line_height_base};",
            f"  --letter-spacing-base: {self.typography.letter_spacing_base};",
            "",
            "  /* Heading Sizes */",
            f"  --font-size-h1: {self.typography.h1_size};",
            f"  --font-size-h2: {self.typography.h2_size};",
            f"  --font-size-h3: {self.typography.h3_size};",
            f"  --font-size-h4: {self.typography.h4_size};",
            f"  --font-size-h5: {self.typography.h5_size};",
            f"  --font-size-h6: {self.typography.h6_size};",
            "",
            "  /* Spacing */",
            "  --spacing-xs: 0.25rem;    /* 4px */",
            "  --spacing-sm: 0.5rem;     /* 8px */",
            "  --spacing-md: 1rem;       /* 16px */",
            "  --spacing-lg: 1.5rem;     /* 24px */",
            "  --spacing-xl: 2rem;       /* 32px */",
            "  --spacing-2xl: 3rem;      /* 48px */",
            "  --spacing-3xl: 4rem;      /* 64px */",
            "  --spacing-4xl: 6rem;      /* 96px */",
            "",
            "  /* Shadows */",
            "  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);",
            "  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);",
            "  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);",
            "  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);",
            "",
            "  /* Border Radius */",
            "  --radius-sm: 0.25rem;     /* 4px */",
            "  --radius-md: 0.375rem;    /* 6px */",
            "  --radius-lg: 0.5rem;      /* 8px */",
            "  --radius-xl: 0.75rem;     /* 12px */",
            "  --radius-2xl: 1rem;       /* 16px */",
            "  --radius-full: 9999px;",
            "",
            "  /* Transitions */",
            "  --transition-fast: 150ms ease-out;",
            "  --transition-base: 300ms ease-out;",
            "  --transition-slow: 500ms ease-out;",
            "",
            "  /* Z-index */",
            "  --z-dropdown: 1000;",
            "  --z-sticky: 1020;",
            "  --z-fixed: 1030;",
            "  --z-modal: 1040;",
            "  --z-popover: 1050;",
            "  --z-tooltip: 1060;",
            "}"
        ]
        
        return '\n'.join(css_vars)
    
    def generate_reset_styles(self) -> str:
        """Generate modern CSS reset for consistency."""
        reset_css = [
            "/* Modern CSS Reset */",
            "*,",
            "*::before,",
            "*::after {",
            "  box-sizing: border-box;",
            "}",
            "",
            "* {",
            "  margin: 0;",
            "  padding: 0;",
            "}",
            "",
            "html {",
            "  scroll-behavior: smooth;",
            "}",
            "",
            "body {",
            "  font-family: var(--font-family-primary);",
            "  font-size: var(--font-size-base);",
            "  line-height: var(--line-height-base);",
            "  letter-spacing: var(--letter-spacing-base);",
            "  color: var(--color-neutral-800);",
            "  background-color: var(--color-neutral-50);",
            "  -webkit-font-smoothing: antialiased;",
            "  -moz-osx-font-smoothing: grayscale;",
            "}",
            "",
            "img,",
            "picture,",
            "video,",
            "canvas,",
            "svg {",
            "  display: block;",
            "  max-width: 100%;",
            "  height: auto;",
            "}",
            "",
            "input,",
            "button,",
            "textarea,",
            "select {",
            "  font: inherit;",
            "}",
            "",
            "button {",
            "  cursor: pointer;",
            "  border: none;",
            "  background: none;",
            "}",
            "",
            "a {",
            "  color: inherit;",
            "  text-decoration: none;",
            "}",
            "",
            "ul,",
            "ol {",
            "  list-style: none;",
            "}",
            "",
            "/* Focus styles for accessibility */",
            "*:focus-visible {",
            "  outline: 2px solid var(--color-primary);",
            "  outline-offset: 2px;",
            "}"
        ]
        
        return '\n'.join(reset_css)
    
    def generate_grid_system(self) -> str:
        """Generate CSS Grid and Flexbox utility classes."""
        grid_css = [
            "/* Container */",
            ".container {",
            "  width: 100%;",
            "  max-width: 1200px;",
            "  margin: 0 auto;",
            "  padding: 0 var(--spacing-md);",
            "}",
            "",
            ".container-fluid {",
            "  width: 100%;",
            "  padding: 0 var(--spacing-md);",
            "}",
            "",
            "/* CSS Grid System */",
            ".grid {",
            "  display: grid;",
            "  gap: var(--spacing-lg);",
            "}",
            "",
            ".grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }",
            ".grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }",
            ".grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }",
            ".grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }",
            ".grid-cols-6 { grid-template-columns: repeat(6, minmax(0, 1fr)); }",
            ".grid-cols-12 { grid-template-columns: repeat(12, minmax(0, 1fr)); }",
            "",
            "/* Column Spans */", 
            ".col-span-1 { grid-column: span 1 / span 1; }",
            ".col-span-2 { grid-column: span 2 / span 2; }",
            ".col-span-3 { grid-column: span 3 / span 3; }",
            ".col-span-4 { grid-column: span 4 / span 4; }",
            ".col-span-6 { grid-column: span 6 / span 6; }",
            ".col-span-full { grid-column: 1 / -1; }",
            "",
            "/* Flexbox Utilities */",
            ".flex { display: flex; }",
            ".inline-flex { display: inline-flex; }",
            "",
            "/* Flex Direction */",
            ".flex-row { flex-direction: row; }",
            ".flex-col { flex-direction: column; }",
            ".flex-row-reverse { flex-direction: row-reverse; }",
            ".flex-col-reverse { flex-direction: column-reverse; }",
            "",
            "/* Flex Wrap */",
            ".flex-wrap { flex-wrap: wrap; }",
            ".flex-nowrap { flex-wrap: nowrap; }",
            "",
            "/* Justify Content */",
            ".justify-start { justify-content: flex-start; }",
            ".justify-end { justify-content: flex-end; }",
            ".justify-center { justify-content: center; }",
            ".justify-between { justify-content: space-between; }",
            ".justify-around { justify-content: space-around; }",
            ".justify-evenly { justify-content: space-evenly; }",
            "",
            "/* Align Items */",
            ".items-start { align-items: flex-start; }",
            ".items-end { align-items: flex-end; }",
            ".items-center { align-items: center; }",
            ".items-baseline { align-items: baseline; }",
            ".items-stretch { align-items: stretch; }",
            "",
            "/* Gap */",
            ".gap-xs { gap: var(--spacing-xs); }",
            ".gap-sm { gap: var(--spacing-sm); }",
            ".gap-md { gap: var(--spacing-md); }",
            ".gap-lg { gap: var(--spacing-lg); }",
            ".gap-xl { gap: var(--spacing-xl); }",
            ".gap-2xl { gap: var(--spacing-2xl); }",
        ]
        
        # Add responsive variants
        for breakpoint, size in self.breakpoints.items():
            if breakpoint == "xs":
                continue
                
            grid_css.extend([
                f"",
                f"/* {breakpoint.upper()} Breakpoint ({size}+) */",
                f"@media (min-width: {size}) {{",
                f"  .{breakpoint}\\:grid-cols-1 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }}",
                f"  .{breakpoint}\\:grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}",
                f"  .{breakpoint}\\:grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}",
                f"  .{breakpoint}\\:grid-cols-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}",
                f"  .{breakpoint}\\:col-span-1 {{ grid-column: span 1 / span 1; }}",
                f"  .{breakpoint}\\:col-span-2 {{ grid-column: span 2 / span 2; }}",
                f"  .{breakpoint}\\:col-span-3 {{ grid-column: span 3 / span 3; }}",
                f"  .{breakpoint}\\:col-span-4 {{ grid-column: span 4 / span 4; }}",
                f"  .{breakpoint}\\:flex-row {{ flex-direction: row; }}",
                f"  .{breakpoint}\\:flex-col {{ flex-direction: column; }}",
                f"}}",
            ])
        
        return '\n'.join(grid_css)
    
    def generate_typography_styles(self) -> str:
        """Generate typography styles optimized for conversion."""
        typography_css = [
            "/* Typography */",
            "h1, h2, h3, h4, h5, h6 {",
            "  font-family: var(--font-family-secondary);",
            "  font-weight: 700;",
            "  line-height: 1.2;",
            "  letter-spacing: -0.02em;",
            "  margin-bottom: var(--spacing-md);",
            "  color: var(--color-neutral-900);",
            "}",
            "",
            "h1 { font-size: var(--font-size-h1); }",
            "h2 { font-size: var(--font-size-h2); }",
            "h3 { font-size: var(--font-size-h3); }",
            "h4 { font-size: var(--font-size-h4); }",
            "h5 { font-size: var(--font-size-h5); }",
            "h6 { font-size: var(--font-size-h6); }",
            "",
            "p {",
            "  margin-bottom: var(--spacing-md);",
            "  color: var(--color-neutral-700);",
            "}",
            "",
            "/* Lead text for hero sections */",
            ".lead {",
            "  font-size: 1.25rem;",
            "  font-weight: 300;",
            "  line-height: 1.4;",
            "  color: var(--color-neutral-600);",
            "}",
            "",
            "/* Text sizes */",
            ".text-xs { font-size: 0.75rem; }      /* 12px */",
            ".text-sm { font-size: 0.875rem; }     /* 14px */",
            ".text-base { font-size: 1rem; }       /* 16px */",
            ".text-lg { font-size: 1.125rem; }     /* 18px */",
            ".text-xl { font-size: 1.25rem; }      /* 20px */",
            ".text-2xl { font-size: 1.5rem; }      /* 24px */",
            ".text-3xl { font-size: 1.875rem; }    /* 30px */",
            ".text-4xl { font-size: 2.25rem; }     /* 36px */",
            "",
            "/* Font weights */",
            ".font-light { font-weight: 300; }",
            ".font-normal { font-weight: 400; }",
            ".font-medium { font-weight: 500; }",
            ".font-semibold { font-weight: 600; }",
            ".font-bold { font-weight: 700; }",
            ".font-extrabold { font-weight: 800; }",
            "",
            "/* Text alignment */",
            ".text-left { text-align: left; }",
            ".text-center { text-align: center; }",
            ".text-right { text-align: right; }",
            "",
            "/* Text colors */",
            ".text-primary { color: var(--color-primary); }",
            ".text-secondary { color: var(--color-secondary); }",
            ".text-accent { color: var(--color-accent); }",
            ".text-neutral-600 { color: var(--color-neutral-600); }",
            ".text-neutral-700 { color: var(--color-neutral-700); }",
            ".text-neutral-800 { color: var(--color-neutral-800); }",
            ".text-neutral-900 { color: var(--color-neutral-900); }",
        ]
        
        return '\n'.join(typography_css)
    
    def generate_button_styles(self) -> str:
        """Generate button styles optimized for conversions."""
        button_css = [
            "/* Button Base */",
            ".btn {",
            "  display: inline-flex;",
            "  align-items: center;",
            "  justify-content: center;",
            "  gap: var(--spacing-sm);",
            "  padding: var(--spacing-sm) var(--spacing-lg);",
            "  font-family: inherit;",
            "  font-size: var(--font-size-base);",
            "  font-weight: 600;",
            "  line-height: 1.5;",
            "  text-align: center;",
            "  text-decoration: none;",
            "  border: 2px solid transparent;",
            "  border-radius: var(--radius-lg);",
            "  cursor: pointer;",
            "  transition: all var(--transition-fast);",
            "  user-select: none;",
            "  white-space: nowrap;",
            "}",
            "",
            ".btn:disabled {",
            "  opacity: 0.6;",
            "  cursor: not-allowed;",
            "}",
            "",
            "/* Button Sizes */",
            ".btn-sm {",
            "  padding: var(--spacing-xs) var(--spacing-md);",
            "  font-size: 0.875rem;",
            "}",
            "",
            ".btn-lg {",
            "  padding: var(--spacing-md) var(--spacing-xl);",
            "  font-size: 1.125rem;",
            "}",
            "",
            ".btn-xl {",
            "  padding: var(--spacing-lg) var(--spacing-2xl);",
            "  font-size: 1.25rem;",
            "}",
            "",
            "/* Primary Button - Main CTA */",
            ".btn-primary {",
            "  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);",
            "  color: white;",
            "  box-shadow: var(--shadow-md);",
            "}",
            "",
            ".btn-primary:hover {",
            "  transform: translateY(-2px);",
            "  box-shadow: var(--shadow-lg);",
            "}",
            "",
            ".btn-primary:active {",
            "  transform: translateY(0);",
            "  box-shadow: var(--shadow-md);",
            "}",
            "",
            "/* Secondary Button */",
            ".btn-secondary {",
            "  background: transparent;",
            "  color: var(--color-primary);",
            "  border-color: var(--color-primary);",
            "}",
            "",
            ".btn-secondary:hover {",
            "  background: var(--color-primary);",
            "  color: white;",
            "}",
            "",
            "/* Accent Button - Urgency/Special offers */",
            ".btn-accent {",
            "  background: var(--color-accent);",
            "  color: white;",
            "  box-shadow: var(--shadow-md);",
            "  animation: pulse-glow 2s infinite;",
            "}",
            "",
            ".btn-accent:hover {",
            "  background: color-mix(in srgb, var(--color-accent) 90%, black);",
            "  transform: translateY(-2px);",
            "  box-shadow: var(--shadow-lg);",
            "}",
            "",
            "/* Success Button */",
            ".btn-success {",
            "  background: var(--color-success);",
            "  color: white;",
            "}",
            "",
            ".btn-success:hover {",
            "  background: color-mix(in srgb, var(--color-success) 90%, black);",
            "}",
            "",
            "/* Block Button */",
            ".btn-block {",
            "  width: 100%;",
            "}",
            "",
            "/* Button Animations */",
            "@keyframes pulse-glow {",
            "  0%, 100% {",
            "    box-shadow: var(--shadow-md), 0 0 0 0 rgba(245, 158, 11, 0.7);",
            "  }",
            "  50% {",
            "    box-shadow: var(--shadow-lg), 0 0 0 8px rgba(245, 158, 11, 0);",
            "  }",
            "}",
            "",
            "/* Loading state */",
            ".btn-loading {",
            "  position: relative;",
            "  color: transparent;",
            "}",
            "",
            ".btn-loading::after {",
            "  content: '';",
            "  position: absolute;",
            "  width: 16px;",
            "  height: 16px;",
            "  top: 50%;",
            "  left: 50%;",
            "  margin-top: -8px;",
            "  margin-left: -8px;",
            "  border: 2px solid transparent;",
            "  border-top-color: currentColor;",
            "  border-radius: 50%;",
            "  animation: btn-spin 0.8s linear infinite;",
            "}",
            "",
            "@keyframes btn-spin {",
            "  to { transform: rotate(360deg); }",
            "}"
        ]
        
        return '\n'.join(button_css)
    
    def generate_form_styles(self) -> str:
        """Generate form styles optimized for conversions."""
        form_css = [
            "/* Form Styles */",
            ".form-group {",
            "  margin-bottom: var(--spacing-lg);",
            "}",
            "",
            ".form-label {",
            "  display: block;",
            "  margin-bottom: var(--spacing-sm);",
            "  font-weight: 600;",
            "  color: var(--color-neutral-800);",
            "}",
            "",
            ".form-control {",
            "  width: 100%;",
            "  padding: var(--spacing-md);",
            "  font-family: inherit;",
            "  font-size: var(--font-size-base);",
            "  line-height: 1.5;",
            "  color: var(--color-neutral-800);",
            "  background: var(--color-neutral-50);",
            "  border: 2px solid var(--color-neutral-200);",
            "  border-radius: var(--radius-lg);",
            "  transition: all var(--transition-fast);",
            "}",
            "",
            ".form-control:focus {",
            "  outline: none;",
            "  border-color: var(--color-primary);",
            "  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);",
            "}",
            "",
            ".form-control:invalid {",
            "  border-color: var(--color-error);",
            "}",
            "",
            ".form-control::placeholder {",
            "  color: var(--color-neutral-400);",
            "}",
            "",
            "/* Form Help Text */",
            ".form-help {",
            "  display: block;",
            "  margin-top: var(--spacing-xs);",
            "  font-size: 0.875rem;",
            "  color: var(--color-neutral-600);",
            "}",
            "",
            "/* Form Error States */",
            ".form-error {",
            "  color: var(--color-error);",
            "  font-size: 0.875rem;",
            "  margin-top: var(--spacing-xs);",
            "}",
            "",
            ".form-control.error {",
            "  border-color: var(--color-error);",
            "  background: rgba(239, 68, 68, 0.05);",
            "}",
            "",
            "/* Checkbox and Radio */",
            ".form-check {",
            "  display: flex;",
            "  align-items: flex-start;",
            "  gap: var(--spacing-sm);",
            "}",
            "",
            ".form-check-input {",
            "  width: 1.25rem;",
            "  height: 1.25rem;",
            "  margin-top: 0.125rem;",
            "  border: 2px solid var(--color-neutral-300);",
            "  border-radius: var(--radius-sm);",
            "}",
            "",
            ".form-check-input[type='radio'] {",
            "  border-radius: var(--radius-full);",
            "}",
            "",
            ".form-check-input:checked {",
            "  background: var(--color-primary);",
            "  border-color: var(--color-primary);",
            "}",
            "",
            ".form-check-label {",
            "  flex: 1;",
            "  font-size: 0.875rem;",
            "  line-height: 1.5;",
            "  color: var(--color-neutral-700);",
            "}",
            "",
            "/* Privacy Notice */",
            ".privacy-notice {",
            "  margin-top: var(--spacing-md);",
            "  padding: var(--spacing-md);",
            "  background: var(--color-neutral-100);",
            "  border-radius: var(--radius-lg);",
            "  font-size: 0.875rem;",
            "  color: var(--color-neutral-600);",
            "  text-align: center;",
            "}"
        ]
        
        return '\n'.join(form_css)
    
    def generate_utility_classes(self) -> str:
        """Generate utility classes for spacing, colors, etc."""
        utilities_css = [
            "/* Spacing Utilities */",
            "/* Margin */",
            ".m-0 { margin: 0; }",
            ".m-auto { margin: auto; }",
            ".mx-auto { margin-left: auto; margin-right: auto; }",
            ".my-auto { margin-top: auto; margin-bottom: auto; }",
            "",
            ".m-xs { margin: var(--spacing-xs); }",
            ".m-sm { margin: var(--spacing-sm); }",
            ".m-md { margin: var(--spacing-md); }",
            ".m-lg { margin: var(--spacing-lg); }",
            ".m-xl { margin: var(--spacing-xl); }",
            ".m-2xl { margin: var(--spacing-2xl); }",
            "",
            "/* Margin Top */",
            ".mt-0 { margin-top: 0; }",
            ".mt-xs { margin-top: var(--spacing-xs); }",
            ".mt-sm { margin-top: var(--spacing-sm); }",
            ".mt-md { margin-top: var(--spacing-md); }",
            ".mt-lg { margin-top: var(--spacing-lg); }",
            ".mt-xl { margin-top: var(--spacing-xl); }",
            ".mt-2xl { margin-top: var(--spacing-2xl); }",
            "",
            "/* Margin Bottom */",
            ".mb-0 { margin-bottom: 0; }",
            ".mb-xs { margin-bottom: var(--spacing-xs); }",
            ".mb-sm { margin-bottom: var(--spacing-sm); }",
            ".mb-md { margin-bottom: var(--spacing-md); }",
            ".mb-lg { margin-bottom: var(--spacing-lg); }",
            ".mb-xl { margin-bottom: var(--spacing-xl); }",
            ".mb-2xl { margin-bottom: var(--spacing-2xl); }",
            "",
            "/* Padding */",
            ".p-0 { padding: 0; }",
            ".p-xs { padding: var(--spacing-xs); }",
            ".p-sm { padding: var(--spacing-sm); }",
            ".p-md { padding: var(--spacing-md); }",
            ".p-lg { padding: var(--spacing-lg); }",
            ".p-xl { padding: var(--spacing-xl); }",
            ".p-2xl { padding: var(--spacing-2xl); }",
            "",
            "/* Background Colors */",
            ".bg-primary { background-color: var(--color-primary); }",
            ".bg-secondary { background-color: var(--color-secondary); }",
            ".bg-accent { background-color: var(--color-accent); }",
            ".bg-success { background-color: var(--color-success); }",
            ".bg-neutral-50 { background-color: var(--color-neutral-50); }",
            ".bg-neutral-100 { background-color: var(--color-neutral-100); }",
            ".bg-neutral-800 { background-color: var(--color-neutral-800); }",
            ".bg-neutral-900 { background-color: var(--color-neutral-900); }",
            "",
            "/* Border Radius */",
            ".rounded-none { border-radius: 0; }",
            ".rounded-sm { border-radius: var(--radius-sm); }",
            ".rounded-md { border-radius: var(--radius-md); }",
            ".rounded-lg { border-radius: var(--radius-lg); }",
            ".rounded-xl { border-radius: var(--radius-xl); }",
            ".rounded-2xl { border-radius: var(--radius-2xl); }",
            ".rounded-full { border-radius: var(--radius-full); }",
            "",
            "/* Shadows */",
            ".shadow-none { box-shadow: none; }",
            ".shadow-sm { box-shadow: var(--shadow-sm); }",
            ".shadow-md { box-shadow: var(--shadow-md); }",
            ".shadow-lg { box-shadow: var(--shadow-lg); }",
            ".shadow-xl { box-shadow: var(--shadow-xl); }",
            "",
            "/* Visibility */",
            ".hidden { display: none; }",
            ".block { display: block; }",
            ".inline-block { display: inline-block; }",
            "",
            "/* Screen Reader Only */",
            ".sr-only {",
            "  position: absolute;",
            "  width: 1px;",
            "  height: 1px;",
            "  padding: 0;",
            "  margin: -1px;",
            "  overflow: hidden;",
            "  clip: rect(0, 0, 0, 0);",
            "  white-space: nowrap;",
            "  border: 0;",
            "}",
            "",
            "/* Skip Links for Accessibility */",
            ".skip-link {",
            "  position: absolute;",
            "  top: -40px;",
            "  left: 6px;",
            "  background: var(--color-primary);",
            "  color: white;",
            "  padding: 8px;",
            "  text-decoration: none;",
            "  border-radius: var(--radius-md);",
            "  z-index: var(--z-tooltip);",
            "}",
            "",
            ".skip-link:focus {",
            "  top: 6px;",
            "}"
        ]
        
        return '\n'.join(utilities_css)
    
    def generate_complete_css(self) -> str:
        """Generate complete CSS framework."""
        css_parts = [
            "/* Landing Page Builder CSS Framework */",
            "/* Optimized for conversion and Core Web Vitals */",
            "",
            self.generate_css_variables(),
            "",
            self.generate_reset_styles(),
            "",
            self.generate_grid_system(),
            "",
            self.generate_typography_styles(),
            "",
            self.generate_button_styles(),
            "",
            self.generate_form_styles(),
            "",
            self.generate_utility_classes(),
        ]
        
        return '\n'.join(css_parts)