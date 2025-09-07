#!/usr/bin/env python3
"""
Stack Overflow R Questions Scraper
Extracts high-quality R programming Q&A pairs from Stack Overflow
"""

import requests
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm
from bs4 import BeautifulSoup
import html


class StackOverflowScraper:
    def __init__(self, output_dir: str = "./data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Stack Exchange API endpoint
        self.api_base = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
        
        # Request parameters
        self.headers = {
            'User-Agent': 'R-LLM Dataset Builder (Educational Purpose)'
        }
        
        # Quality filters
        self.min_score = 5  # Minimum question score
        self.min_answer_score = 3  # Minimum answer score
        self.max_questions = 5000  # Maximum questions to collect
        
        # R-related tags to focus on
        self.r_tags = [
            "r", "dplyr", "ggplot2", "tidyverse", "data.table", "shiny",
            "r-markdown", "tidyr", "stringr", "lubridate", "purrr",
            "data-manipulation", "data-visualization", "statistics",
            "regression", "time-series", "machine-learning"
        ]
    
    def get_questions(self, tag: str, page: int = 1, pagesize: int = 100) -> Dict:
        """Get questions from Stack Overflow API"""
        url = f"{self.api_base}/questions"
        
        params = {
            'order': 'desc',
            'sort': 'votes',
            'tagged': tag,
            'site': self.site,
            'page': page,
            'pagesize': pagesize,
            'filter': 'withbody',  # Include question body
            'min': self.min_score
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle API rate limiting
            if 'backoff' in data:
                time.sleep(data['backoff'])
            
            return data
            
        except Exception as e:
            print(f"Error fetching questions for tag {tag}: {e}")
            return {"items": []}
    
    def get_answers(self, question_id: int) -> Dict:
        """Get answers for a specific question"""
        url = f"{self.api_base}/questions/{question_id}/answers"
        
        params = {
            'order': 'desc',
            'sort': 'votes',
            'site': self.site,
            'filter': 'withbody',
            'min': self.min_answer_score
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle API rate limiting
            if 'backoff' in data:
                time.sleep(data['backoff'])
            
            return data
            
        except Exception as e:
            print(f"Error fetching answers for question {question_id}: {e}")
            return {"items": []}
    
    def clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract text/code"""
        if not html_content:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract code blocks and preserve them
        code_blocks = []
        for code in soup.find_all(['code', 'pre']):
            code_text = code.get_text()
            placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
            code_blocks.append(code_text)
            code.replace_with(placeholder)
        
        # Get clean text
        text = soup.get_text()
        text = html.unescape(text)
        
        # Restore code blocks with proper formatting
        for i, code_text in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            if '\n' in code_text or len(code_text) > 50:
                # Multi-line code block
                text = text.replace(placeholder, f"\n```r\n{code_text}\n```\n")
            else:
                # Inline code
                text = text.replace(placeholder, f"`{code_text}`")
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive newlines
        text = text.strip()
        
        return text
    
    def is_r_question(self, question: Dict) -> bool:
        """Check if question is relevant for R programming"""
        title = question.get('title', '').lower()
        body = question.get('body', '').lower()
        tags = [tag.lower() for tag in question.get('tags', [])]
        
        # Must have R in tags
        if 'r' not in tags:
            return False
        
        # Filter out questions that are too basic or off-topic
        exclude_patterns = [
            'install', 'installation', 'package not found', 'error loading',
            'homework', 'assignment', 'please help', 'urgent'
        ]
        
        title_body = f"{title} {body}"
        for pattern in exclude_patterns:
            if pattern in title_body:
                return False
        
        # Prefer questions with code
        if 'library(' in body or 'data.frame' in body or '<-' in body:
            return True
        
        return True
    
    def extract_code_from_text(self, text: str) -> List[str]:
        """Extract R code snippets from text"""
        code_snippets = []
        
        # Extract code blocks
        code_pattern = r'```r?\n(.*?)\n```'
        matches = re.findall(code_pattern, text, re.DOTALL)
        code_snippets.extend(matches)
        
        # Extract inline code that looks like R
        inline_pattern = r'`([^`]*(?:<-|library|data\.frame|ggplot|dplyr)[^`]*)`'
        inline_matches = re.findall(inline_pattern, text)
        code_snippets.extend(inline_matches)
        
        return [code.strip() for code in code_snippets if code.strip()]
    
    def create_instruction_pairs(self, questions_data: List[Dict]) -> List[Dict]:
        """Convert Q&A pairs to instruction-response format"""
        instruction_pairs = []
        
        for qa in questions_data:
            question = qa['question']
            answer = qa['answer']
            
            # Extract title and clean question body
            title = question.get('title', '')
            question_body = self.clean_html(question.get('body', ''))
            answer_body = self.clean_html(answer.get('body', ''))
            
            if not answer_body or len(answer_body) < 50:
                continue
            
            # Extract code from answer
            code_snippets = self.extract_code_from_text(answer_body)
            
            if not code_snippets:
                continue
            
            # Create instruction variations
            instructions = [
                f"{title}",
                f"How to solve: {title}",
                f"R programming question: {title}",
                f"{question_body[:200]}..." if len(question_body) > 200 else question_body
            ]
            
            # Create clean response
            response = answer_body
            
            # Add metadata about code complexity
            has_dplyr = any('dplyr' in code or '%>%' in code for code in code_snippets)
            has_ggplot = any('ggplot' in code or 'geom_' in code for code in code_snippets)
            has_stats = any(func in answer_body.lower() for func in ['lm(', 'glm(', 't.test', 'anova'])
            
            complexity = "basic"
            if has_dplyr or has_ggplot:
                complexity = "intermediate"
            if has_stats:
                complexity = "advanced"
            
            for instruction in instructions:
                if instruction and len(instruction.strip()) > 10:
                    instruction_pairs.append({
                        "instruction": instruction.strip(),
                        "response": response,
                        "question_id": question.get('question_id'),
                        "question_score": question.get('score', 0),
                        "answer_score": answer.get('score', 0),
                        "tags": question.get('tags', []),
                        "complexity": complexity,
                        "has_code": len(code_snippets) > 0,
                        "code_snippets": code_snippets,
                        "source": "stackoverflow"
                    })
        
        return instruction_pairs
    
    def scrape_questions_by_tag(self, tag: str, max_pages: int = 5) -> List[Dict]:
        """Scrape questions for a specific tag"""
        all_qa_pairs = []
        
        print(f"Scraping questions for tag: {tag}")
        
        for page in range(1, max_pages + 1):
            print(f"  Page {page}/{max_pages}")
            
            questions_data = self.get_questions(tag, page)
            questions = questions_data.get('items', [])
            
            if not questions:
                break
            
            for question in tqdm(questions, desc=f"Processing {tag} questions"):
                if not self.is_r_question(question):
                    continue
                
                # Get answers for this question
                answers_data = self.get_answers(question['question_id'])
                answers = answers_data.get('items', [])
                
                if not answers:
                    continue
                
                # Take the best answer (first one, sorted by votes)
                best_answer = answers[0]
                
                all_qa_pairs.append({
                    'question': question,
                    'answer': best_answer
                })
                
                time.sleep(0.1)  # Rate limiting
        
        return all_qa_pairs
    
    def scrape_all_tags(self) -> List[Dict]:
        """Scrape questions for all R-related tags"""
        all_qa_pairs = []
        
        print(f"Scraping Stack Overflow for {len(self.r_tags)} R-related tags...")
        
        for tag in self.r_tags:
            qa_pairs = self.scrape_questions_by_tag(tag, max_pages=3)
            all_qa_pairs.extend(qa_pairs)
            
            # Save intermediate results
            tag_file = self.output_dir / f"stackoverflow_{tag.replace('-', '_')}.json"
            instruction_pairs = self.create_instruction_pairs(qa_pairs)
            
            with open(tag_file, 'w') as f:
                json.dump(instruction_pairs, f, indent=2)
            
            print(f"Collected {len(qa_pairs)} Q&A pairs for {tag}")
            time.sleep(2)  # Be respectful to the API
        
        # Create all instruction pairs
        all_instruction_pairs = self.create_instruction_pairs(all_qa_pairs)
        
        # Remove duplicates based on question_id
        seen_questions = set()
        unique_pairs = []
        for pair in all_instruction_pairs:
            q_id = pair.get('question_id')
            if q_id not in seen_questions:
                seen_questions.add(q_id)
                unique_pairs.append(pair)
        
        # Save all results
        all_file = self.output_dir / "stackoverflow_all_pairs.json"
        with open(all_file, 'w') as f:
            json.dump(unique_pairs, f, indent=2)
        
        print(f"\nStack Overflow scraping complete!")
        print(f"Total unique Q&A pairs: {len(unique_pairs)}")
        
        return unique_pairs


def main():
    scraper = StackOverflowScraper()
    instruction_pairs = scraper.scrape_all_tags()
    
    print(f"\nDataset creation complete!")
    print(f"Created {len(instruction_pairs)} instruction-response pairs from Stack Overflow")


if __name__ == "__main__":
    main()