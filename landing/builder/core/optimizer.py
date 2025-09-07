"""Performance optimizer for landing pages."""

import re
from typing import Dict, List, Tuple, Optional
import json


class PerformanceOptimizer:
    """Optimizes landing page performance through various techniques."""
    
    def __init__(self):
        self.optimization_rules = {
            'minify_html': True,
            'minify_css': True,
            'minify_js': True,
            'inline_critical_css': True,
            'lazy_load_images': True,
            'preload_fonts': True,
            'compress_assets': True
        }
    
    def optimize_html(self, html: str) -> str:
        """Optimize HTML content."""
        if self.optimization_rules['minify_html']:
            html = self._minify_html(html)
        
        if self.optimization_rules['lazy_load_images']:
            html = self._add_lazy_loading(html)
        
        return html
    
    def optimize_css(self, css: str) -> str:
        """Optimize CSS content."""
        if self.optimization_rules['minify_css']:
            css = self._minify_css(css)
        
        return css
    
    def optimize_js(self, js: str) -> str:
        """Optimize JavaScript content."""
        if self.optimization_rules['minify_js']:
            js = self._minify_js(js)
        
        return js
    
    def _minify_html(self, html: str) -> str:
        """Basic HTML minification."""
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        # Remove excessive whitespace
        html = re.sub(r'\s+', ' ', html)
        # Remove whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        return html.strip()
    
    def _minify_css(self, css: str) -> str:
        """Basic CSS minification."""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove excessive whitespace
        css = re.sub(r'\s+', ' ', css)
        # Remove spaces around selectors
        css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
        return css.strip()
    
    def _minify_js(self, js: str) -> str:
        """Basic JavaScript minification."""
        # Remove single-line comments
        js = re.sub(r'//.*?$', '', js, flags=re.MULTILINE)
        # Remove multi-line comments
        js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
        # Remove excessive whitespace (careful with strings)
        lines = js.split('\n')
        minified_lines = []
        for line in lines:
            line = line.strip()
            if line:
                minified_lines.append(line)
        return ' '.join(minified_lines)
    
    def _add_lazy_loading(self, html: str) -> str:
        """Add lazy loading to images."""
        # Add loading="lazy" to img tags that don't have it
        html = re.sub(
            r'<img\s+(?![^>]*loading\s*=)([^>]+)>',
            r'<img loading="lazy" \1>',
            html
        )
        return html
    
    def get_critical_css(self, css: str) -> str:
        """Extract critical CSS for above-the-fold content."""
        # This is a simplified version - in production, you'd use tools like critical
        critical_selectors = [
            'body', 'html', 'header', 'nav', '.hero', '.above-fold',
            'h1', 'h2', '.btn-primary', '.container'
        ]
        
        critical_css = []
        css_rules = css.split('}')
        
        for rule in css_rules:
            if any(selector in rule for selector in critical_selectors):
                critical_css.append(rule + '}')
        
        return ''.join(critical_css)
    
    def generate_performance_report(self, html: str, css: str, js: str) -> Dict:
        """Generate a performance optimization report."""
        original_size = len(html) + len(css) + len(js)
        
        optimized_html = self.optimize_html(html)
        optimized_css = self.optimize_css(css)
        optimized_js = self.optimize_js(js)
        
        optimized_size = len(optimized_html) + len(optimized_css) + len(optimized_js)
        
        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'reduction_percentage': round((1 - optimized_size / original_size) * 100, 2),
            'optimizations_applied': [
                key for key, value in self.optimization_rules.items() if value
            ]
        }
    
    def get_performance_hints(self) -> List[str]:
        """Get performance optimization hints."""
        return [
            "Enable Gzip compression on your server",
            "Use a CDN for static assets",
            "Implement browser caching headers",
            "Consider using WebP format for images",
            "Minify and bundle CSS/JS files",
            "Use async/defer for non-critical scripts",
            "Implement Critical CSS for faster rendering",
            "Enable HTTP/2 on your server",
            "Optimize images before uploading",
            "Use resource hints (preload, prefetch, preconnect)"
        ]