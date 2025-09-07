#!/usr/bin/env python3
"""
Evaluation Script for R-LLM Model
Tests code generation, syntax correctness, and semantic accuracy
"""

import json
import re
import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from unsloth import FastLanguageModel
import matplotlib.pyplot as plt
import seaborn as sns


class RModelEvaluator:
    def __init__(self, model_path: str, test_data_path: str = "./data/final/test.jsonl"):
        self.model_path = model_path
        self.test_data_path = test_data_path
        
        # Load model and tokenizer
        self.model = None
        self.tokenizer = None
        self.load_model()
        
        # Load test data
        self.test_data = self.load_test_data()
        
        # R test environment setup
        self.r_script_template = """
library(methods)
tryCatch({{
    {code}
    cat("SUCCESS\\n")
}}, error = function(e) {{
    cat("ERROR:", conditionMessage(e), "\\n")
}}, warning = function(w) {{
    cat("WARNING:", conditionMessage(w), "\\n")
}})
"""
        
        # Evaluation metrics
        self.results = {
            'syntax_correct': [],
            'runs_without_error': [],
            'semantic_scores': [],
            'response_lengths': [],
            'code_coverage': []
        }
    
    def load_model(self):
        """Load the fine-tuned model"""
        print(f"Loading model from {self.model_path}")
        
        try:
            # Try loading as Unsloth model first
            model, tokenizer = FastLanguageModel.from_pretrained(
                self.model_path,
                max_seq_length=512,
                dtype=None,
                load_in_4bit=True,
            )
            
            # Set to evaluation mode
            FastLanguageModel.for_inference(model)
            
        except Exception as e:
            print(f"Failed to load as Unsloth model: {e}")
            # Fallback to standard transformers
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        self.model = model
        self.tokenizer = tokenizer
        print("Model loaded successfully")
    
    def load_test_data(self) -> List[Dict]:
        """Load test dataset"""
        test_data = []
        
        with open(self.test_data_path, 'r') as f:
            for line in f:
                test_data.append(json.loads(line))
        
        print(f"Loaded {len(test_data)} test samples")
        return test_data
    
    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """Generate response for a given prompt"""
        # Format prompt for Gemma-3
        formatted_prompt = f"""<start_of_turn>user
{prompt}<end_of_turn>
<start_of_turn>model
"""
        
        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        
        # Move to device if needed
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=len(inputs['input_ids'][0]) + max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                top_p=0.9
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the model's response
        if "<start_of_turn>model" in response:
            response = response.split("<start_of_turn>model")[-1].strip()
        
        # Remove end token if present
        if "<end_of_turn>" in response:
            response = response.split("<end_of_turn>")[0].strip()
        
        return response
    
    def extract_r_code(self, text: str) -> List[str]:
        """Extract R code blocks from generated text"""
        code_blocks = []
        
        # Extract code blocks with ```r or ```R
        pattern = r'```[rR]?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        code_blocks.extend(matches)
        
        # Extract inline code that looks like R
        inline_pattern = r'`([^`]*(?:<-|library|data\.frame|ggplot|%>%)[^`]*)`'
        inline_matches = re.findall(inline_pattern, text)
        code_blocks.extend(inline_matches)
        
        # If no code blocks found, try to extract R-like statements
        if not code_blocks:
            lines = text.split('\n')
            r_lines = []
            for line in lines:
                line = line.strip()
                if any(indicator in line for indicator in ['<-', 'library(', 'data.frame', '%>%', 'ggplot']):
                    r_lines.append(line)
            if r_lines:
                code_blocks.append('\n'.join(r_lines))
        
        return [code.strip() for code in code_blocks if code.strip()]
    
    def check_syntax(self, code: str) -> bool:
        """Check if R code has valid syntax"""
        try:
            # Create a temporary R script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
                f.write(f"tryCatch({{ parse(text = {repr(code)}) }}, error = function(e) quit(status = 1))")
                temp_file = f.name
            
            # Run R to check syntax
            result = subprocess.run(
                ['R', '--slave', '--no-restore', '--file=' + temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def run_r_code(self, code: str) -> Tuple[bool, str]:
        """Run R code and check if it executes without errors"""
        try:
            # Create R script
            r_script = self.r_script_template.format(code=code)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
                f.write(r_script)
                temp_file = f.name
            
            # Run R script
            result = subprocess.run(
                ['R', '--slave', '--no-restore', '--file=' + temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            os.unlink(temp_file)
            
            # Check output
            output = result.stdout + result.stderr
            success = "SUCCESS" in output and "ERROR" not in output
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def calculate_semantic_score(self, instruction: str, generated_response: str, expected_response: str = None) -> float:
        """Calculate semantic similarity score"""
        score = 0.0
        
        # Extract code from both responses
        generated_code = self.extract_r_code(generated_response)
        
        if not generated_code:
            return 0.0
        
        # Check if response addresses the instruction
        instruction_lower = instruction.lower()
        response_lower = generated_response.lower()
        
        # Key concept matching
        key_concepts = {
            'visualization': ['plot', 'ggplot', 'hist', 'scatter', 'bar', 'chart'],
            'data_manipulation': ['filter', 'select', 'mutate', 'arrange', 'group_by', 'summarise'],
            'statistics': ['mean', 'median', 'sd', 'cor', 't.test', 'lm', 'anova'],
            'data_import': ['read.csv', 'read_csv', 'load', 'import'],
            'packages': ['library', 'require', 'dplyr', 'ggplot2', 'tidyr']
        }
        
        # Check concept relevance
        for concept, keywords in key_concepts.items():
            if any(kw in instruction_lower for kw in keywords):
                if any(kw in response_lower for kw in keywords):
                    score += 0.2
                    break
        
        # Check for code structure
        main_code = generated_code[0] if generated_code else ""
        
        if 'plot' in instruction_lower or 'chart' in instruction_lower or 'histogram' in instruction_lower:
            if any(plot_kw in main_code.lower() for plot_kw in ['ggplot', 'plot(', 'hist(', 'geom_']):
                score += 0.3
        
        if 'filter' in instruction_lower or 'subset' in instruction_lower:
            if any(filter_kw in main_code for filter_kw in ['filter(', 'subset(', '[', 'which(']):
                score += 0.3
        
        if 'group' in instruction_lower or 'summary' in instruction_lower:
            if any(group_kw in main_code for group_kw in ['group_by', 'aggregate', 'tapply']):
                score += 0.3
        
        # Bonus for executable code
        if generated_code:
            syntax_valid = self.check_syntax(main_code)
            if syntax_valid:
                score += 0.2
        
        return min(score, 1.0)
    
    def evaluate_sample(self, sample: Dict) -> Dict:
        """Evaluate a single test sample"""
        instruction = sample['instruction']
        expected_response = sample.get('response', '')
        
        # Generate response
        generated_response = self.generate_response(instruction)
        
        # Extract R code
        generated_code = self.extract_r_code(generated_response)
        
        # Initialize results
        results = {
            'instruction': instruction,
            'generated_response': generated_response,
            'generated_code': generated_code,
            'syntax_correct': False,
            'runs_without_error': False,
            'semantic_score': 0.0,
            'response_length': len(generated_response),
            'has_code': len(generated_code) > 0,
            'execution_output': ''
        }
        
        if generated_code:
            main_code = generated_code[0]
            
            # Check syntax
            results['syntax_correct'] = self.check_syntax(main_code)
            
            # Try to run code
            if results['syntax_correct']:
                runs_ok, output = self.run_r_code(main_code)
                results['runs_without_error'] = runs_ok
                results['execution_output'] = output
            
            # Calculate semantic score
            results['semantic_score'] = self.calculate_semantic_score(
                instruction, generated_response, expected_response
            )
        
        return results
    
    def run_evaluation(self, max_samples: Optional[int] = None) -> Dict:
        """Run full evaluation on test dataset"""
        print("Starting evaluation...")
        
        test_samples = self.test_data
        if max_samples:
            test_samples = test_samples[:max_samples]
        
        all_results = []
        
        for sample in tqdm(test_samples, desc="Evaluating samples"):
            result = self.evaluate_sample(sample)
            all_results.append(result)
            
            # Update running metrics
            self.results['syntax_correct'].append(result['syntax_correct'])
            self.results['runs_without_error'].append(result['runs_without_error'])
            self.results['semantic_scores'].append(result['semantic_score'])
            self.results['response_lengths'].append(result['response_length'])
            self.results['code_coverage'].append(result['has_code'])
        
        # Calculate summary metrics
        summary = self.calculate_summary_metrics()
        
        # Save detailed results
        self.save_results(all_results, summary)
        
        return summary
    
    def calculate_summary_metrics(self) -> Dict:
        """Calculate summary evaluation metrics"""
        total_samples = len(self.results['syntax_correct'])
        
        summary = {
            'total_samples': total_samples,
            'syntax_accuracy': sum(self.results['syntax_correct']) / total_samples if total_samples > 0 else 0,
            'execution_success_rate': sum(self.results['runs_without_error']) / total_samples if total_samples > 0 else 0,
            'code_generation_rate': sum(self.results['code_coverage']) / total_samples if total_samples > 0 else 0,
            'average_semantic_score': sum(self.results['semantic_scores']) / total_samples if total_samples > 0 else 0,
            'average_response_length': sum(self.results['response_lengths']) / total_samples if total_samples > 0 else 0,
        }
        
        # Additional metrics
        code_samples = [i for i, has_code in enumerate(self.results['code_coverage']) if has_code]
        if code_samples:
            code_syntax_correct = [self.results['syntax_correct'][i] for i in code_samples]
            code_runs_ok = [self.results['runs_without_error'][i] for i in code_samples]
            
            summary['syntax_accuracy_among_code'] = sum(code_syntax_correct) / len(code_syntax_correct)
            summary['execution_success_among_code'] = sum(code_runs_ok) / len(code_runs_ok)
        
        return summary
    
    def save_results(self, detailed_results: List[Dict], summary: Dict):
        """Save evaluation results"""
        results_dir = Path("./evaluation")
        results_dir.mkdir(exist_ok=True)
        
        # Save detailed results
        detailed_file = results_dir / "detailed_results.json"
        with open(detailed_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        # Save summary
        summary_file = results_dir / "evaluation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Create evaluation report
        self.create_evaluation_report(detailed_results, summary, results_dir)
        
        print(f"Results saved to {results_dir}")
    
    def create_evaluation_report(self, detailed_results: List[Dict], summary: Dict, output_dir: Path):
        """Create a comprehensive evaluation report"""
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Metric comparison
        metrics = ['syntax_accuracy', 'execution_success_rate', 'code_generation_rate', 'average_semantic_score']
        values = [summary[metric] for metric in metrics]
        
        axes[0, 0].bar(metrics, values)
        axes[0, 0].set_title('Overall Performance Metrics')
        axes[0, 0].set_ylim(0, 1)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Response length distribution
        axes[0, 1].hist(self.results['response_lengths'], bins=20, alpha=0.7)
        axes[0, 1].set_title('Response Length Distribution')
        axes[0, 1].set_xlabel('Response Length (characters)')
        axes[0, 1].set_ylabel('Frequency')
        
        # 3. Semantic score distribution
        axes[1, 0].hist(self.results['semantic_scores'], bins=20, alpha=0.7, color='green')
        axes[1, 0].set_title('Semantic Score Distribution')
        axes[1, 0].set_xlabel('Semantic Score')
        axes[1, 0].set_ylabel('Frequency')
        
        # 4. Success rate breakdown
        categories = ['Generates Code', 'Syntax Correct', 'Runs Successfully']
        rates = [
            summary['code_generation_rate'],
            summary['syntax_accuracy'],
            summary['execution_success_rate']
        ]
        
        axes[1, 1].bar(categories, rates, color=['blue', 'orange', 'green'])
        axes[1, 1].set_title('Success Rate Breakdown')
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_dir / "evaluation_charts.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create markdown report
        report_content = f"""# R-LLM Model Evaluation Report

## Summary Metrics

- **Total Samples Evaluated**: {summary['total_samples']}
- **Code Generation Rate**: {summary['code_generation_rate']:.2%}
- **Syntax Accuracy**: {summary['syntax_accuracy']:.2%}
- **Execution Success Rate**: {summary['execution_success_rate']:.2%}
- **Average Semantic Score**: {summary['average_semantic_score']:.3f}
- **Average Response Length**: {summary['average_response_length']:.1f} characters

## Detailed Analysis

### Code Quality
- Among samples that generated code:
  - **Syntax Accuracy**: {summary.get('syntax_accuracy_among_code', 0):.2%}
  - **Execution Success**: {summary.get('execution_success_among_code', 0):.2%}

### Response Characteristics
- **Average Response Length**: {summary['average_response_length']:.1f} characters
- **Code Generation Coverage**: {summary['code_generation_rate']:.2%}

## Sample Results

### Best Performing Samples
"""
        
        # Add some sample results
        sorted_results = sorted(detailed_results, key=lambda x: x['semantic_score'], reverse=True)
        
        for i, result in enumerate(sorted_results[:3]):
            report_content += f"""
#### Sample {i+1} (Score: {result['semantic_score']:.3f})
**Instruction**: {result['instruction']}

**Generated Response**: 
{result['generated_response'][:300]}{'...' if len(result['generated_response']) > 300 else ''}

**Syntax Correct**: {result['syntax_correct']}
**Runs Successfully**: {result['runs_without_error']}

---
"""
        
        # Save report
        report_file = output_dir / "evaluation_report.md"
        with open(report_file, 'w') as f:
            f.write(report_content)
    
    def compare_with_baseline(self, baseline_results_path: str):
        """Compare results with a baseline model"""
        # Load baseline results
        with open(baseline_results_path, 'r') as f:
            baseline = json.load(f)
        
        current = self.calculate_summary_metrics()
        
        print("Comparison with baseline:")
        for metric in ['syntax_accuracy', 'execution_success_rate', 'average_semantic_score']:
            current_val = current[metric]
            baseline_val = baseline[metric]
            improvement = current_val - baseline_val
            print(f"{metric}: {current_val:.3f} vs {baseline_val:.3f} ({improvement:+.3f})")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate R-LLM model")
    parser.add_argument("--model-path", required=True, help="Path to the fine-tuned model")
    parser.add_argument("--test-data", default="./data/final/test.jsonl", help="Path to test dataset")
    parser.add_argument("--max-samples", type=int, help="Maximum number of samples to evaluate")
    parser.add_argument("--baseline", help="Path to baseline results for comparison")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = RModelEvaluator(args.model_path, args.test_data)
    
    # Run evaluation
    summary = evaluator.run_evaluation(max_samples=args.max_samples)
    
    # Print summary
    print("\nEvaluation Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Compare with baseline if provided
    if args.baseline:
        evaluator.compare_with_baseline(args.baseline)


if __name__ == "__main__":
    main()