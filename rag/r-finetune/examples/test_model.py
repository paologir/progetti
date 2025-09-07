#!/usr/bin/env python3
"""
Test Script for the Fine-tuned R-LLM Model
Interactive testing and example usage
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.training.train_gemma_r import GemmaRTrainer


def test_model_responses():
    """Test the model with various R programming prompts"""
    
    # Initialize trainer
    model_path = "./models/r-llm-checkpoints/final_model"
    trainer = GemmaRTrainer()
    
    # Load the trained model
    try:
        trainer.setup_model()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Test prompts covering different R tasks
    test_prompts = [
        # Data manipulation
        "How do I filter rows in a data frame where age > 30?",
        "Write R code to group data by category and calculate mean values",
        "How can I merge two data frames in R?",
        
        # Data visualization
        "Create a histogram using ggplot2",
        "How do I make a scatter plot with a trend line in R?",
        "Write code for a bar chart showing counts by category",
        
        # Statistics
        "How do I perform a t-test in R?",
        "Calculate correlation between two variables",
        "Fit a linear regression model in R",
        
        # Data import/export
        "How do I read a CSV file in R?",
        "Write data to an Excel file using R",
        
        # Basic operations
        "Calculate mean and standard deviation of a vector",
        "How do I remove missing values from data?",
        "Create a sequence of numbers from 1 to 100"
    ]
    
    print("\n🧪 Testing R-LLM Model Responses")
    print("="*50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        print("-" * 60)
        
        try:
            response = trainer.generate_sample(prompt, max_length=300)
            print(f"🤖 Response:\n{response}")
            
            # Basic quality check
            has_code = any(indicator in response.lower() for indicator in 
                          ['library(', '<-', 'data.frame', 'ggplot', '%>%', '```'])
            quality = "✅ Contains R code" if has_code else "⚠️ No clear R code detected"
            print(f"\n{quality}")
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
        
        print("\n" + "="*60)
    
    print("\n🎯 Testing complete!")


def interactive_test():
    """Interactive testing mode"""
    
    # Initialize trainer
    trainer = GemmaRTrainer()
    
    try:
        trainer.setup_model()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    print("\n🎯 Interactive R-LLM Testing")
    print("Type your R programming questions. Type 'quit' to exit.")
    print("="*50)
    
    while True:
        try:
            prompt = input("\n📝 Your question: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not prompt:
                continue
            
            print("\n🤖 Thinking...")
            response = trainer.generate_sample(prompt, max_length=400)
            
            print(f"\n🤖 Response:\n{response}")
            print("\n" + "-"*50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def benchmark_performance():
    """Benchmark model performance on standard tasks"""
    
    trainer = GemmaRTrainer()
    
    try:
        trainer.setup_model()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Standard R tasks for benchmarking
    benchmark_tasks = [
        {
            "prompt": "Load a CSV file and display first 5 rows",
            "expected_keywords": ["read.csv", "head", "read_csv"]
        },
        {
            "prompt": "Create a bar plot using ggplot2",
            "expected_keywords": ["ggplot", "geom_bar", "aes"]
        },
        {
            "prompt": "Calculate summary statistics for a numeric variable",
            "expected_keywords": ["summary", "mean", "sd", "median"]
        },
        {
            "prompt": "Filter data where column value equals specific condition",
            "expected_keywords": ["filter", "subset", "==", "%>%"]
        },
        {
            "prompt": "Perform simple linear regression",
            "expected_keywords": ["lm", "~", "summary"]
        }
    ]
    
    print("\n📊 Benchmarking Model Performance")
    print("="*50)
    
    total_score = 0
    
    for i, task in enumerate(benchmark_tasks, 1):
        print(f"\n🔍 Benchmark {i}: {task['prompt']}")
        
        try:
            response = trainer.generate_sample(task['prompt'], max_length=250)
            
            # Score based on keyword presence
            score = 0
            found_keywords = []
            
            for keyword in task['expected_keywords']:
                if keyword.lower() in response.lower():
                    score += 1
                    found_keywords.append(keyword)
            
            task_score = score / len(task['expected_keywords'])
            total_score += task_score
            
            print(f"📈 Score: {task_score:.2f} ({score}/{len(task['expected_keywords'])} keywords found)")
            print(f"✅ Found: {', '.join(found_keywords)}")
            print(f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("-" * 50)
    
    avg_score = total_score / len(benchmark_tasks)
    print(f"\n🎯 Overall Benchmark Score: {avg_score:.2f} ({avg_score*100:.1f}%)")
    
    if avg_score >= 0.8:
        print("🌟 Excellent performance!")
    elif avg_score >= 0.6:
        print("👍 Good performance!")
    elif avg_score >= 0.4:
        print("⚠️ Moderate performance - consider more training")
    else:
        print("❌ Poor performance - model needs improvement")


def main():
    """Main function to run different test modes"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the fine-tuned R-LLM model")
    parser.add_argument("--mode", choices=["test", "interactive", "benchmark"], 
                       default="test", help="Testing mode")
    
    args = parser.parse_args()
    
    if args.mode == "test":
        test_model_responses()
    elif args.mode == "interactive":
        interactive_test()
    elif args.mode == "benchmark":
        benchmark_performance()


if __name__ == "__main__":
    main()