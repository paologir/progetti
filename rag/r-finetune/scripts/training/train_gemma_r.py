#!/usr/bin/env python3
"""
Fine-tuning Gemma-3 270M for R Programming
Using Unsloth for efficient training with QLoRA
"""

import os
import json
import yaml
import torch
from pathlib import Path
from datasets import Dataset, load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel
import wandb
from typing import Dict, List, Optional


class GemmaRTrainer:
    def __init__(self, config_path: str = "./configs/training_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # Set up paths
        self.model_name = self.config['model']['name']
        self.output_dir = Path(self.config['training']['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model and tokenizer
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        print(f"Initializing trainer for {self.model_name}")
        print(f"Output directory: {self.output_dir}")
    
    def load_config(self) -> Dict:
        """Load training configuration"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def setup_model(self):
        """Initialize model and tokenizer with Unsloth"""
        print("Loading model with Unsloth...")
        
        # Unsloth FastLanguageModel setup
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.model_name,
            max_seq_length=self.config['dataset']['max_seq_length'],
            dtype=None,  # Auto-detect
            load_in_4bit=self.config['quantization']['load_in_4bit'],
        )
        
        # Apply LoRA adapters
        model = FastLanguageModel.get_peft_model(
            model,
            r=self.config['lora']['r'],
            target_modules=self.config['lora']['target_modules'],
            lora_alpha=self.config['lora']['lora_alpha'],
            lora_dropout=self.config['lora']['lora_dropout'],
            bias=self.config['lora']['bias'],
            use_gradient_checkpointing="unsloth",  # Use Unsloth's optimized checkpointing
            random_state=42,
        )
        
        self.model = model
        self.tokenizer = tokenizer
        
        print("Model and tokenizer loaded successfully")
        print(f"Model parameters: {model.num_parameters():,}")
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"Trainable parameters: {trainable_params:,}")
    
    def load_datasets(self) -> Dict[str, Dataset]:
        """Load training and validation datasets"""
        print("Loading datasets...")
        
        datasets = {}
        
        for split in ['train', 'validation']:
            dataset_path = self.config['dataset'][f'{split}_dataset_path']
            
            if not Path(dataset_path).exists():
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")
            
            # Load JSONL dataset
            dataset = load_dataset('json', data_files=dataset_path, split='train')
            datasets[split] = dataset
            
            print(f"{split} dataset: {len(dataset)} samples")
        
        return datasets
    
    def format_dataset(self, dataset: Dataset) -> Dataset:
        """Format dataset for training"""
        def formatting_prompts_func(examples):
            texts = []
            for text in examples[self.config['dataset']['dataset_text_field']]:
                texts.append(text)
            return {"text": texts}
        
        formatted_dataset = dataset.map(
            formatting_prompts_func,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return formatted_dataset
    
    def setup_training_arguments(self) -> TrainingArguments:
        """Setup training arguments"""
        training_config = self.config['training']
        
        args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=training_config['num_train_epochs'],
            per_device_train_batch_size=training_config['per_device_train_batch_size'],
            per_device_eval_batch_size=training_config['per_device_eval_batch_size'],
            gradient_accumulation_steps=training_config['gradient_accumulation_steps'],
            optim=training_config['optim'],
            save_steps=training_config['save_steps'],
            logging_steps=training_config['logging_steps'],
            learning_rate=training_config['learning_rate'],
            weight_decay=training_config['weight_decay'],
            fp16=training_config['fp16'],
            bf16=training_config['bf16'],
            max_grad_norm=training_config['max_grad_norm'],
            max_steps=training_config['max_steps'],
            warmup_ratio=training_config['warmup_ratio'],
            group_by_length=training_config['group_by_length'],
            lr_scheduler_type=training_config['lr_scheduler_type'],
            report_to=training_config.get('report_to', None),
            
            # Evaluation settings
            evaluation_strategy=self.config['evaluation']['evaluation_strategy'],
            eval_steps=self.config['evaluation']['eval_steps'],
            save_strategy=self.config['evaluation']['save_strategy'],
            load_best_model_at_end=self.config['evaluation']['load_best_model_at_end'],
            metric_for_best_model=self.config['evaluation']['metric_for_best_model'],
            greater_is_better=self.config['evaluation']['greater_is_better'],
            
            # Additional settings for stability
            dataloader_pin_memory=False,  # Avoid memory issues
            remove_unused_columns=False,
        )
        
        return args
    
    def setup_trainer(self, datasets: Dict[str, Dataset]) -> SFTTrainer:
        """Setup SFT trainer"""
        print("Setting up SFT trainer...")
        
        training_args = self.setup_training_arguments()
        
        # Format datasets
        train_dataset = self.format_dataset(datasets['train'])
        eval_dataset = self.format_dataset(datasets['validation'])
        
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            dataset_text_field="text",
            max_seq_length=self.config['sft']['max_seq_length'],
            dataset_num_proc=2,
            packing=self.config['sft']['packing'],
            args=training_args,
        )
        
        return trainer
    
    def train(self):
        """Run the training process"""
        print("Starting training...")
        
        # Setup model
        self.setup_model()
        
        # Load datasets
        datasets = self.load_datasets()
        
        # Setup trainer
        self.trainer = self.setup_trainer(datasets)
        
        # Enable gradient checkpointing for memory efficiency
        self.model.gradient_checkpointing_enable()
        
        # Start training
        train_result = self.trainer.train()
        
        # Save training metrics
        metrics = train_result.metrics
        self.trainer.log_metrics("train", metrics)
        self.trainer.save_metrics("train", metrics)
        
        # Save the final model
        self.save_model()
        
        print("Training completed!")
        return train_result
    
    def save_model(self):
        """Save the trained model"""
        print("Saving model...")
        
        # Save with Unsloth's optimized save method
        self.model.save_pretrained_merged(
            str(self.output_dir / "final_model"),
            tokenizer=self.tokenizer,
            save_method="merged_16bit"  # Save as 16-bit merged model
        )
        
        # Also save LoRA adapters separately
        self.model.save_pretrained(str(self.output_dir / "lora_adapters"))
        self.tokenizer.save_pretrained(str(self.output_dir / "lora_adapters"))
        
        # Save training config
        config_save_path = self.output_dir / "training_config.yaml"
        with open(config_save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        print(f"Model saved to {self.output_dir}")
    
    def evaluate(self, dataset_path: Optional[str] = None):
        """Evaluate the model"""
        if not self.trainer:
            print("Trainer not initialized. Please run train() first.")
            return
        
        print("Running evaluation...")
        
        if dataset_path:
            eval_dataset = load_dataset('json', data_files=dataset_path, split='train')
            eval_dataset = self.format_dataset(eval_dataset)
        else:
            # Use validation dataset
            datasets = self.load_datasets()
            eval_dataset = self.format_dataset(datasets['validation'])
        
        eval_result = self.trainer.evaluate(eval_dataset=eval_dataset)
        
        # Save evaluation metrics
        self.trainer.log_metrics("eval", eval_result)
        self.trainer.save_metrics("eval", eval_result)
        
        print(f"Evaluation results: {eval_result}")
        return eval_result
    
    def generate_sample(self, prompt: str, max_length: int = 512) -> str:
        """Generate a sample response for testing"""
        if not self.model or not self.tokenizer:
            self.setup_model()
        
        # Format prompt for Gemma-3
        formatted_prompt = f"""<start_of_turn>user
{prompt}<end_of_turn>
<start_of_turn>model
"""
        
        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the model's response
        if "<start_of_turn>model" in response:
            response = response.split("<start_of_turn>model")[-1].strip()
        
        return response


def main():
    """Main training script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Gemma-3 270M for R programming")
    parser.add_argument("--config", default="./configs/training_config.yaml", 
                       help="Path to training configuration file")
    parser.add_argument("--eval-only", action="store_true", 
                       help="Only run evaluation")
    parser.add_argument("--test-prompt", type=str, 
                       help="Test prompt for generation")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = GemmaRTrainer(config_path=args.config)
    
    if args.test_prompt:
        # Test generation
        response = trainer.generate_sample(args.test_prompt)
        print(f"Prompt: {args.test_prompt}")
        print(f"Response: {response}")
    
    elif args.eval_only:
        # Run evaluation only
        trainer.setup_model()
        trainer.evaluate()
    
    else:
        # Run full training
        trainer.train()
        
        # Test with a sample prompt
        test_prompt = "How do I create a histogram in R using ggplot2?"
        response = trainer.generate_sample(test_prompt)
        print(f"\nTest generation:")
        print(f"Prompt: {test_prompt}")
        print(f"Response: {response}")


if __name__ == "__main__":
    main()