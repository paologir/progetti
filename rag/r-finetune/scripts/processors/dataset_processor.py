#!/usr/bin/env python3
"""
Dataset Processor for R-LLM Fine-tuning
Processes and formats collected data into training-ready datasets
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Tuple
import random
from tqdm import tqdm
from datasets import Dataset
import numpy as np


class DatasetProcessor:
    def __init__(self, raw_data_dir: str = "./data/raw", processed_dir: str = "./data/processed"):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Instruction templates for data augmentation
        self.instruction_templates = [
            "How do I {task} in R?",
            "Write R code to {task}",
            "Show me how to {task} using R",
            "What's the R code for {task}?",
            "Help me {task} in R programming",
            "I need to {task} in R. How can I do this?",
            "Can you show me R code that {task}?",
            "Write an R script to {task}"
        ]
        
        # Common R tasks for synthetic data generation
        self.common_tasks = [
            "load a CSV file",
            "create a data frame",
            "filter rows based on a condition",
            "group data and calculate summary statistics",
            "create a scatter plot",
            "calculate correlation between variables",
            "perform a t-test",
            "create a histogram",
            "merge two data frames",
            "calculate mean and standard deviation",
            "remove missing values",
            "sort data by a column",
            "create a bar chart",
            "subset columns from a data frame",
            "calculate percentiles"
        ]
    
    def load_collected_data(self) -> Dict[str, List[Dict]]:
        """Load all collected data from different sources"""
        all_data = {
            'cran': [],
            'stackoverflow': [],
            'synthetic': []
        }
        
        # Load CRAN data
        cran_files = list(self.raw_data_dir.glob("*cran*.json"))
        for file in cran_files:
            with open(file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data['cran'].extend(data)
        
        # Load Stack Overflow data
        so_files = list(self.raw_data_dir.glob("*stackoverflow*.json"))
        for file in so_files:
            with open(file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data['stackoverflow'].extend(data)
        
        print(f"Loaded data:")
        print(f"  CRAN: {len(all_data['cran'])} samples")
        print(f"  Stack Overflow: {len(all_data['stackoverflow'])} samples")
        
        return all_data
    
    def generate_synthetic_data(self, num_samples: int = 1000) -> List[Dict]:
        """Generate synthetic R programming instruction-response pairs"""
        synthetic_data = []
        
        print(f"Generating {num_samples} synthetic samples...")
        
        for _ in tqdm(range(num_samples)):
            task = random.choice(self.common_tasks)
            template = random.choice(self.instruction_templates)
            
            instruction = template.format(task=task)
            response = self._generate_synthetic_response(task)
            
            if response:
                synthetic_data.append({
                    "instruction": instruction,
                    "response": response,
                    "source": "synthetic",
                    "task_type": self._classify_task(task)
                })
        
        return synthetic_data
    
    def _generate_synthetic_response(self, task: str) -> str:
        """Generate synthetic R code response for a given task"""
        task_lower = task.lower()
        
        if "load" in task_lower and "csv" in task_lower:
            return """To load a CSV file in R, use the read.csv() function:

```r
# Load CSV file
data <- read.csv("filename.csv")

# Or with additional options
data <- read.csv("filename.csv", header = TRUE, stringsAsFactors = FALSE)

# Using readr package (recommended)
library(readr)
data <- read_csv("filename.csv")
```"""
        
        elif "data frame" in task_lower and "create" in task_lower:
            return """To create a data frame in R:

```r
# Create a data frame from vectors
df <- data.frame(
  name = c("Alice", "Bob", "Charlie"),
  age = c(25, 30, 35),
  score = c(95, 87, 92)
)

# Or using tibble (tidyverse)
library(tibble)
df <- tibble(
  name = c("Alice", "Bob", "Charlie"),
  age = c(25, 30, 35),
  score = c(95, 87, 92)
)
```"""
        
        elif "filter" in task_lower and "rows" in task_lower:
            return """To filter rows based on a condition in R:

```r
# Base R approach
filtered_data <- data[data$column > value, ]

# Using dplyr (recommended)
library(dplyr)
filtered_data <- data %>%
  filter(column > value)

# Multiple conditions
filtered_data <- data %>%
  filter(column1 > value1 & column2 == "value2")
```"""
        
        elif "group" in task_lower and "summary" in task_lower:
            return """To group data and calculate summary statistics:

```r
# Using dplyr
library(dplyr)

summary_data <- data %>%
  group_by(grouping_variable) %>%
  summarise(
    mean_value = mean(numeric_column),
    count = n(),
    sd_value = sd(numeric_column)
  )

# Base R approach
aggregate(numeric_column ~ grouping_variable, data = data, FUN = mean)
```"""
        
        elif "scatter plot" in task_lower:
            return """To create a scatter plot in R:

```r
# Base R
plot(data$x_variable, data$y_variable, 
     main = "Scatter Plot",
     xlab = "X Variable", 
     ylab = "Y Variable")

# Using ggplot2 (recommended)
library(ggplot2)
ggplot(data, aes(x = x_variable, y = y_variable)) +
  geom_point() +
  labs(title = "Scatter Plot", x = "X Variable", y = "Y Variable")
```"""
        
        elif "correlation" in task_lower:
            return """To calculate correlation between variables in R:

```r
# Correlation between two variables
correlation <- cor(data$var1, data$var2)

# Correlation matrix for multiple variables
cor_matrix <- cor(data[, c("var1", "var2", "var3")])

# With missing value handling
correlation <- cor(data$var1, data$var2, use = "complete.obs")
```"""
        
        elif "t-test" in task_lower or "t test" in task_lower:
            return """To perform a t-test in R:

```r
# One-sample t-test
t.test(data$variable, mu = expected_mean)

# Two-sample t-test
t.test(group1_data, group2_data)

# Paired t-test
t.test(before_data, after_data, paired = TRUE)

# T-test with formula notation
t.test(variable ~ group, data = data)
```"""
        
        elif "histogram" in task_lower:
            return """To create a histogram in R:

```r
# Base R
hist(data$variable, 
     main = "Histogram", 
     xlab = "Variable", 
     breaks = 20)

# Using ggplot2
library(ggplot2)
ggplot(data, aes(x = variable)) +
  geom_histogram(bins = 20, fill = "skyblue", color = "black") +
  labs(title = "Histogram", x = "Variable", y = "Frequency")
```"""
        
        # Add more synthetic responses as needed
        else:
            return None
    
    def _classify_task(self, task: str) -> str:
        """Classify the type of R task"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["load", "read", "import"]):
            return "data_import"
        elif any(word in task_lower for word in ["plot", "chart", "graph", "histogram"]):
            return "visualization"
        elif any(word in task_lower for word in ["filter", "group", "merge", "sort"]):
            return "data_manipulation"
        elif any(word in task_lower for word in ["test", "correlation", "regression", "model"]):
            return "statistics"
        else:
            return "general"
    
    def clean_and_validate_data(self, data: List[Dict]) -> List[Dict]:
        """Clean and validate instruction-response pairs"""
        cleaned_data = []
        
        print("Cleaning and validating data...")
        
        for item in tqdm(data):
            if not isinstance(item, dict):
                continue
            
            instruction = item.get('instruction', '').strip()
            response = item.get('response', '').strip()
            
            # Basic validation
            if not instruction or not response:
                continue
            
            if len(instruction) < 10 or len(response) < 20:
                continue
            
            # Clean instruction
            instruction = self._clean_text(instruction)
            response = self._clean_text(response)
            
            # Validate R code presence in response
            if not self._contains_r_code(response):
                continue
            
            # Check for quality indicators
            quality_score = self._calculate_quality_score(instruction, response)
            if quality_score < 0.5:
                continue
            
            cleaned_item = {
                'instruction': instruction,
                'response': response,
                'source': item.get('source', 'unknown'),
                'quality_score': quality_score
            }
            
            # Add metadata if available
            for key in ['complexity', 'task_type', 'tags']:
                if key in item:
                    cleaned_item[key] = item[key]
            
            cleaned_data.append(cleaned_item)
        
        print(f"Kept {len(cleaned_data)} out of {len(data)} samples after cleaning")
        return cleaned_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common encoding issues
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _contains_r_code(self, text: str) -> bool:
        """Check if text contains R code"""
        r_indicators = [
            'library(', 'require(', '<-', '%>%', 'data.frame',
            'ggplot', 'geom_', 'mutate(', 'filter(', 'select(',
            'summarise(', 'group_by(', 'read.csv', 'write.csv'
        ]
        
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in r_indicators)
    
    def _calculate_quality_score(self, instruction: str, response: str) -> float:
        """Calculate quality score for instruction-response pair"""
        score = 0.0
        
        # Length check
        if 20 <= len(instruction) <= 200:
            score += 0.2
        if 50 <= len(response) <= 2000:
            score += 0.2
        
        # R code presence
        if '```r' in response or '```R' in response:
            score += 0.3
        elif '`' in response and self._contains_r_code(response):
            score += 0.2
        
        # Quality indicators in response
        quality_words = ['example', 'usage', 'function', 'parameter', 'argument']
        if any(word in response.lower() for word in quality_words):
            score += 0.1
        
        # Instruction clarity
        question_words = ['how', 'what', 'write', 'create', 'show', 'help']
        if any(word in instruction.lower() for word in question_words):
            score += 0.2
        
        return min(score, 1.0)
    
    def format_for_training(self, data: List[Dict]) -> List[Dict]:
        """Format data for training with Gemma-3 instruction format"""
        formatted_data = []
        
        print("Formatting data for training...")
        
        for item in tqdm(data):
            # Gemma-3 instruction format
            formatted_text = f"""<start_of_turn>user
{item['instruction']}<end_of_turn>
<start_of_turn>model
{item['response']}<end_of_turn>"""
            
            formatted_item = {
                'text': formatted_text,
                'instruction': item['instruction'],
                'response': item['response'],
                'source': item.get('source', 'unknown'),
                'quality_score': item.get('quality_score', 0.0)
            }
            
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    def create_train_validation_split(self, data: List[Dict], 
                                     train_ratio: float = 0.8, 
                                     val_ratio: float = 0.1) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Split data into train, validation, and test sets"""
        
        # Shuffle data
        random.shuffle(data)
        
        total_size = len(data)
        train_size = int(total_size * train_ratio)
        val_size = int(total_size * val_ratio)
        
        train_data = data[:train_size]
        val_data = data[train_size:train_size + val_size]
        test_data = data[train_size + val_size:]
        
        print(f"Data split:")
        print(f"  Training: {len(train_data)} samples")
        print(f"  Validation: {len(val_data)} samples")
        print(f"  Test: {len(test_data)} samples")
        
        return train_data, val_data, test_data
    
    def save_datasets(self, train_data: List[Dict], val_data: List[Dict], test_data: List[Dict]):
        """Save processed datasets"""
        
        # Save as JSON Lines
        datasets = {
            'train': train_data,
            'validation': val_data,
            'test': test_data
        }
        
        final_dir = Path("./data/final")
        final_dir.mkdir(parents=True, exist_ok=True)
        
        for split_name, data in datasets.items():
            # Save as JSONL
            jsonl_file = final_dir / f"{split_name}.jsonl"
            with open(jsonl_file, 'w') as f:
                for item in data:
                    f.write(json.dumps(item) + '\n')
            
            # Save as JSON for inspection
            json_file = final_dir / f"{split_name}.json"
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        # Save statistics
        stats = {
            'total_samples': len(train_data) + len(val_data) + len(test_data),
            'train_samples': len(train_data),
            'validation_samples': len(val_data),
            'test_samples': len(test_data),
            'sources': {},
            'quality_distribution': {}
        }
        
        # Analyze sources
        all_data = train_data + val_data + test_data
        for item in all_data:
            source = item.get('source', 'unknown')
            stats['sources'][source] = stats['sources'].get(source, 0) + 1
        
        # Analyze quality scores
        quality_scores = [item.get('quality_score', 0.0) for item in all_data]
        stats['quality_distribution'] = {
            'mean': np.mean(quality_scores),
            'median': np.median(quality_scores),
            'std': np.std(quality_scores)
        }
        
        stats_file = final_dir / "dataset_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\nDatasets saved to {final_dir}")
        print(f"Statistics: {stats}")
    
    def process_all_data(self):
        """Main processing pipeline"""
        print("Starting data processing pipeline...")
        
        # Load collected data
        collected_data = self.load_collected_data()
        
        # Generate synthetic data
        synthetic_data = self.generate_synthetic_data(num_samples=1000)
        collected_data['synthetic'] = synthetic_data
        
        # Combine all data
        all_data = []
        for source, data_list in collected_data.items():
            all_data.extend(data_list)
        
        print(f"Total collected samples: {len(all_data)}")
        
        # Clean and validate
        cleaned_data = self.clean_and_validate_data(all_data)
        
        # Format for training
        formatted_data = self.format_for_training(cleaned_data)
        
        # Create train/val/test split
        train_data, val_data, test_data = self.create_train_validation_split(formatted_data)
        
        # Save datasets
        self.save_datasets(train_data, val_data, test_data)
        
        print("\nData processing complete!")
        return train_data, val_data, test_data


def main():
    processor = DatasetProcessor()
    train_data, val_data, test_data = processor.process_all_data()
    
    print(f"\nFinal dataset summary:")
    print(f"Training samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")
    print(f"Test samples: {len(test_data)}")


if __name__ == "__main__":
    main()