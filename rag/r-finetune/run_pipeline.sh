#!/bin/bash

# R-LLM Fine-tuning Pipeline
# Complete automation script for the entire fine-tuning process

set -e  # Exit on any error

echo "🚀 Starting R-LLM Fine-tuning Pipeline"
echo "======================================"

# Configuration
VENV_NAME="r-llm-env"
MAX_SAMPLES=1000  # Limit for initial testing

# Function to print status
print_status() {
    echo ""
    echo "📍 $1"
    echo "----------------------------------------"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
print_status "Checking system dependencies"

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists R; then
    echo "❌ R is required but not installed"
    echo "Please install R: https://www.r-project.org/"
    exit 1
fi

echo "✅ Python and R are available"

# Setup virtual environment
print_status "Setting up Python environment"

if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_NAME
fi

echo "Activating virtual environment..."
source $VENV_NAME/bin/activate

echo "Installing/upgrading dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Environment setup complete"

# Data Collection Phase
print_status "Phase 1: Data Collection"

echo "Collecting CRAN documentation..."
python scripts/collectors/cran_scraper.py

echo "Collecting Stack Overflow data..."
python scripts/collectors/stackoverflow_scraper.py

echo "✅ Data collection complete"

# Data Processing Phase
print_status "Phase 2: Data Processing"

echo "Processing and formatting datasets..."
python scripts/processors/dataset_processor.py

echo "✅ Data processing complete"

# Check if datasets were created
if [ ! -f "data/final/train.jsonl" ]; then
    echo "❌ Training dataset not found. Data processing may have failed."
    exit 1
fi

# Training Phase
print_status "Phase 3: Model Training"

echo "Starting model fine-tuning..."
echo "This may take several hours depending on your hardware..."

python scripts/training/train_gemma_r.py --config configs/training_config.yaml

echo "✅ Training complete"

# Evaluation Phase
print_status "Phase 4: Model Evaluation"

MODEL_PATH="./models/r-llm-checkpoints/final_model"

if [ ! -d "$MODEL_PATH" ]; then
    echo "❌ Trained model not found at $MODEL_PATH"
    echo "Training may have failed or model saved to different location"
    exit 1
fi

echo "Evaluating trained model..."
python scripts/evaluation/evaluate_r_model.py \
    --model-path "$MODEL_PATH" \
    --test-data "./data/final/test.jsonl" \
    --max-samples $MAX_SAMPLES

echo "✅ Evaluation complete"

# Final Summary
print_status "Pipeline Complete! 🎉"

echo "Results Summary:"
echo "- Training data: $(wc -l < data/final/train.jsonl) samples"
echo "- Validation data: $(wc -l < data/final/validation.jsonl) samples"
echo "- Test data: $(wc -l < data/final/test.jsonl) samples"
echo "- Model saved to: $MODEL_PATH"
echo "- Evaluation results: ./evaluation/"

echo ""
echo "Next Steps:"
echo "1. Review evaluation results in ./evaluation/evaluation_report.md"
echo "2. Test the model with custom prompts"
echo "3. Deploy for your R programming tasks"

echo ""
echo "Test the model:"
echo "python scripts/training/train_gemma_r.py --test-prompt 'How do I create a scatter plot in R?'"

echo ""
echo "🎯 Happy R Programming with your custom AI assistant!"