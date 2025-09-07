#!/usr/bin/env python3
"""
CRAN Package Documentation Scraper
Extracts R function documentation, examples, and usage patterns from CRAN packages
"""

import requests
import re
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
import pandas as pd
from tqdm import tqdm


class CRANScraper:
    def __init__(self, output_dir: str = "./data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://cran.r-project.org"
        self.session = requests.Session()
        
        # Top R packages for data science and statistics
        self.target_packages = [
            "dplyr", "ggplot2", "tidyr", "readr", "stringr", "lubridate",
            "purrr", "tibble", "forcats", "stats", "base", "utils",
            "lme4", "ggplot2", "lattice", "MASS", "survival", "cluster",
            "boot", "class", "foreign", "KernSmooth", "mgcv", "nlme",
            "rpart", "spatial", "nnet", "caret", "randomForest", "e1071",
            "shiny", "DT", "plotly", "leaflet", "htmlwidgets", "knitr",
            "rmarkdown", "devtools", "testthat", "roxygen2", "usethis"
        ]
    
    def get_package_info(self, package: str) -> Dict:
        """Get basic package information from CRAN"""
        url = f"{self.base_url}/web/packages/{package}/index.html"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract package description
            description = ""
            desc_tag = soup.find('p')
            if desc_tag:
                description = desc_tag.get_text().strip()
            
            return {
                "package": package,
                "description": description,
                "url": url
            }
        except Exception as e:
            print(f"Error getting info for {package}: {e}")
            return {"package": package, "description": "", "url": url}
    
    def get_function_documentation(self, package: str) -> List[Dict]:
        """Extract function documentation from package manual"""
        functions_data = []
        
        # Try to get the reference manual PDF link
        package_url = f"{self.base_url}/web/packages/{package}/index.html"
        
        try:
            response = self.session.get(package_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for manual/reference links
            manual_links = soup.find_all('a', href=re.compile(r'\.pdf$'))
            
            # For now, we'll use a simpler approach - scrape from online documentation
            # Many packages have online documentation at rdrr.io
            self._scrape_rdrr_documentation(package, functions_data)
            
        except Exception as e:
            print(f"Error getting documentation for {package}: {e}")
        
        return functions_data
    
    def _scrape_rdrr_documentation(self, package: str, functions_data: List[Dict]):
        """Scrape function documentation from rdrr.io"""
        try:
            # Get package page from rdrr.io
            rdrr_url = f"https://rdrr.io/cran/{package}/"
            response = self.session.get(rdrr_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find function links
                function_links = soup.find_all('a', href=re.compile(r'/man/.*\.html$'))
                
                for link in function_links[:10]:  # Limit to first 10 functions per package
                    func_name = link.get_text().strip()
                    func_url = "https://rdrr.io" + link['href']
                    
                    # Get function documentation
                    func_doc = self._get_function_details(func_url, func_name, package)
                    if func_doc:
                        functions_data.append(func_doc)
                    
                    time.sleep(0.5)  # Be respectful to the server
                        
        except Exception as e:
            print(f"Error scraping rdrr.io for {package}: {e}")
    
    def _get_function_details(self, func_url: str, func_name: str, package: str) -> Dict:
        """Get detailed documentation for a specific function"""
        try:
            response = self.session.get(func_url, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract description
            description = ""
            desc_section = soup.find('h2', string='Description')
            if desc_section and desc_section.find_next_sibling('p'):
                description = desc_section.find_next_sibling('p').get_text().strip()
            
            # Extract usage
            usage = ""
            usage_section = soup.find('h2', string='Usage')
            if usage_section and usage_section.find_next_sibling('pre'):
                usage = usage_section.find_next_sibling('pre').get_text().strip()
            
            # Extract examples
            examples = ""
            examples_section = soup.find('h2', string='Examples')
            if examples_section and examples_section.find_next_sibling('pre'):
                examples = examples_section.find_next_sibling('pre').get_text().strip()
            
            # Extract arguments
            arguments = []
            args_section = soup.find('h2', string='Arguments')
            if args_section:
                args_dl = args_section.find_next_sibling('dl')
                if args_dl:
                    dt_tags = args_dl.find_all('dt')
                    dd_tags = args_dl.find_all('dd')
                    for dt, dd in zip(dt_tags, dd_tags):
                        arguments.append({
                            "name": dt.get_text().strip(),
                            "description": dd.get_text().strip()
                        })
            
            return {
                "function": func_name,
                "package": package,
                "description": description,
                "usage": usage,
                "examples": examples,
                "arguments": arguments,
                "url": func_url
            }
            
        except Exception as e:
            print(f"Error getting details for {func_name}: {e}")
            return None
    
    def create_instruction_pairs(self, functions_data: List[Dict]) -> List[Dict]:
        """Convert function documentation to instruction-response pairs"""
        instruction_pairs = []
        
        for func_data in functions_data:
            if not func_data.get('examples') or not func_data.get('description'):
                continue
            
            # Create multiple instruction variations
            variations = [
                f"How do I use the {func_data['function']} function in R?",
                f"Write R code using {func_data['function']} from the {func_data['package']} package",
                f"Show me an example of {func_data['function']} in R",
                f"What does the {func_data['function']} function do in R?"
            ]
            
            # Create response with description and example
            response = f"{func_data['description']}\n\nExample usage:\n```r\n{func_data['examples']}\n```"
            
            for instruction in variations:
                instruction_pairs.append({
                    "instruction": instruction,
                    "response": response,
                    "function": func_data['function'],
                    "package": func_data['package'],
                    "source": "cran_documentation"
                })
        
        return instruction_pairs
    
    def scrape_all_packages(self) -> List[Dict]:
        """Scrape documentation for all target packages"""
        all_functions = []
        
        print(f"Scraping {len(self.target_packages)} packages...")
        
        for package in tqdm(self.target_packages, desc="Processing packages"):
            print(f"\nProcessing {package}...")
            
            # Get package info
            package_info = self.get_package_info(package)
            
            # Get function documentation
            functions = self.get_function_documentation(package)
            all_functions.extend(functions)
            
            # Save intermediate results
            package_file = self.output_dir / f"{package}_functions.json"
            with open(package_file, 'w') as f:
                json.dump(functions, f, indent=2)
            
            time.sleep(1)  # Be respectful to servers
        
        # Save all functions
        all_file = self.output_dir / "all_cran_functions.json"
        with open(all_file, 'w') as f:
            json.dump(all_functions, f, indent=2)
        
        # Create instruction pairs
        instruction_pairs = self.create_instruction_pairs(all_functions)
        
        # Save instruction pairs
        pairs_file = self.output_dir / "cran_instruction_pairs.json"
        with open(pairs_file, 'w') as f:
            json.dump(instruction_pairs, f, indent=2)
        
        print(f"\nScraping complete!")
        print(f"Functions collected: {len(all_functions)}")
        print(f"Instruction pairs created: {len(instruction_pairs)}")
        
        return instruction_pairs


def main():
    scraper = CRANScraper()
    instruction_pairs = scraper.scrape_all_packages()
    
    print(f"\nDataset creation complete!")
    print(f"Created {len(instruction_pairs)} instruction-response pairs from CRAN documentation")


if __name__ == "__main__":
    main()