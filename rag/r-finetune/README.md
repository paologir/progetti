# R-LLM Fine-tuning Project

A complete pipeline for fine-tuning a 270M parameter language model (Gemma-3) specifically for R programming and data analysis tasks.

## 🎯 Project Overview

This project creates a specialized small language model for R programming by:
- Collecting high-quality R programming datasets from CRAN documentation and Stack Overflow
- Processing and formatting data for instruction tuning
- Fine-tuning Gemma-3 270M using Unsloth for efficient training
- Comprehensive evaluation of code generation capabilities

## 🏗️ Project Structure

```
r-llm-finetune/
├── data/
│   ├── raw/           # Raw collected data
│   ├── processed/     # Cleaned instruction-response pairs
│   └── final/         # Training-ready datasets (train/val/test)
├── scripts/
│   ├── collectors/    # Data collection scripts
│   │   ├── cran_scraper.py        # CRAN package documentation scraper
│   │   └── stackoverflow_scraper.py # Stack Overflow Q&A scraper
│   ├── processors/    # Data processing & formatting
│   │   └── dataset_processor.py   # Dataset cleaning and formatting
│   └── training/      # Fine-tuning scripts
│       └── train_gemma_r.py      # Main training script
├── evaluation/        # Evaluation scripts and results
│   └── evaluate_r_model.py       # Comprehensive evaluation
├── configs/           # Configuration files
│   └── training_config.yaml      # Training parameters
├── models/            # Saved model checkpoints
└── requirements.txt   # Python dependencies
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd r-llm-finetune

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Collection

```bash
# Collect CRAN documentation
python scripts/collectors/cran_scraper.py

# Collect Stack Overflow Q&A (requires API setup)
python scripts/collectors/stackoverflow_scraper.py
```

### 3. Data Processing

```bash
# Process and format all collected data
python scripts/processors/dataset_processor.py
```

### 4. Model Training

```bash
# Train the model
python scripts/training/train_gemma_r.py --config configs/training_config.yaml
```

### 5. Evaluation

```bash
# Evaluate the trained model
python scripts/evaluation/evaluate_r_model.py --model-path ./models/r-llm-checkpoints/final_model
```

## 📊 Dataset Details

### Data Sources

1. **CRAN Package Documentation (40%)**
   - Function documentation and examples from top R packages
   - Covers: tidyverse, ggplot2, dplyr, stats, lme4, caret, shiny
   - Format: Instruction → Working code example

2. **Stack Overflow Q&A (30%)**
   - High-quality R programming questions and answers
   - Filtered for score > 5 and verified solutions
   - Includes error fixes and debugging scenarios

3. **R Vignettes & Tutorials (20%)**
   - Package vignettes converted to instruction-response pairs
   - Statistical explanations with accompanying code
   - Complete data analysis workflows

4. **Synthetic R Tasks (10%)**
   - Generated variations of common R tasks
   - Data manipulation, visualization, statistical tests
   - Ensures coverage of fundamental operations

### Dataset Statistics

- **Expected Size**: ~50,000 instruction-response pairs
- **Average Length**: 100-200 tokens per example
- **Total Training Tokens**: ~10M tokens
- **Split**: 80% train, 10% validation, 10% test

## 🔧 Configuration

### Training Parameters

The model uses efficient fine-tuning with:
- **Base Model**: `unsloth/gemma-3-270m-it-GGUF` (270M parameters)
- **Method**: QLoRA (4-bit quantization + LoRA adapters)
- **LoRA Rank**: 16
- **Learning Rate**: 2e-4
- **Batch Size**: 4 (with gradient accumulation)
- **Epochs**: 3

### Hardware Requirements

- **Minimum**: 8GB GPU memory (with 4-bit quantization)
- **Recommended**: 16GB+ GPU memory
- **Training Time**: ~2-4 hours on modern GPU

## 📈 Evaluation Metrics

The evaluation script measures:

1. **Code Generation Rate**: Percentage of responses containing R code
2. **Syntax Accuracy**: Percentage of generated code with valid R syntax
3. **Execution Success**: Percentage of code that runs without errors
4. **Semantic Score**: Relevance and correctness of generated solutions
5. **Response Quality**: Length, structure, and completeness

### Sample Results

Expected performance after fine-tuning:
- Code Generation Rate: ~85%
- Syntax Accuracy: ~90%
- Execution Success: ~75%
- Average Semantic Score: ~0.7

## 🎯 Use Cases

The fine-tuned model excels at:

### Data Manipulation
```
Input: "How do I filter rows where age > 30 in R?"
Output: "Use dplyr::filter():
library(dplyr)
filtered_data <- data %>% filter(age > 30)"
```

### Data Visualization
```
Input: "Create a histogram of the mpg variable using ggplot2"
Output: "library(ggplot2)
ggplot(data, aes(x = mpg)) + 
  geom_histogram(bins = 20, fill = 'skyblue')"
```

### Statistical Analysis
```
Input: "Perform a t-test comparing two groups"
Output: "t.test(group1_data, group2_data)
# Or with formula: t.test(value ~ group, data = df)"
```

## 🛠️ Advanced Usage

### Custom Dataset Training

1. Prepare your data in JSONL format:
```json
{"instruction": "Your R question", "response": "R code solution"}
```

2. Update `training_config.yaml` with your dataset path

3. Run training:
```bash
python scripts/training/train_gemma_r.py --config your_config.yaml
```

### Model Deployment

The trained model can be deployed using:
- **Hugging Face Transformers**: Standard inference
- **Unsloth**: Optimized inference
- **GGUF Format**: For llama.cpp deployment

### Integration Examples

```python
from unsloth import FastLanguageModel

# Load model
model, tokenizer = FastLanguageModel.from_pretrained("path/to/your/model")

# Generate R code
prompt = "How do I calculate correlation in R?"
response = generate_response(model, tokenizer, prompt)
```

## 📋 Requirements

### Python Dependencies
- torch >= 2.0.0
- transformers >= 4.36.0
- unsloth (for efficient training)
- datasets >= 2.16.0
- pandas, numpy
- requests, beautifulsoup4 (for data collection)

### System Requirements
- Python 3.8+
- CUDA-capable GPU (recommended)
- R installation (for code evaluation)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

### Areas for Contribution
- Additional data sources (GitHub repos, R documentation)
- Improved evaluation metrics
- Support for other R-focused models
- Integration with R environments

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Unsloth**: For efficient fine-tuning implementation
- **Google**: For the Gemma model family
- **R Community**: For extensive documentation and examples
- **Stack Overflow**: For community-driven Q&A content

## 📞 Contact

For questions or issues:
- Open an issue on GitHub
- Discuss in the project's discussion forum

## 🔮 Future Enhancements

- [ ] Support for R Markdown and notebook formats
- [ ] Integration with RStudio addins
- [ ] Specialized models for bioinformatics R packages
- [ ] Multi-language support (Python + R code generation)
- [ ] Real-time code completion features
- [ ] Integration with R package development workflows

---

**Happy R Programming with AI! 🤖📊**