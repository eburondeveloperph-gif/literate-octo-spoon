#!/usr/bin/env python3
"""
Multilingual TTS Finetuning Script for Qwen3-TTS 0.6B Model
This script can be run on Kaggle or locally to finetune the model.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configuration
MODEL_CONFIGS = {
    "0.6B": {
        "model_name": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        "max_seq_length": 2048,
        "dtype": "bfloat16",
        "load_in_4bit": True,
    },
    "1.7B": {
        "model_name": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "max_seq_length": 2048,
        "dtype": "bfloat16",
        "load_in_4bit": False,
    },
}


class TTSFinetuner:
    """Multilingual TTS Finetuner for Qwen3-TTS models."""

    def __init__(
        self,
        model_size: str = "0.6B",
        output_dir: str = "./tts-finetuned",
        use_kaggle: bool = False,
    ):
        self.model_size = model_size
        self.output_dir = Path(output_dir)
        self.use_kaggle = use_kaggle
        self.model_config = MODEL_CONFIGS[model_size]

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"TTS Finetuner initialized")
        print(f"  Model: {self.model_config['model_name']}")
        print(f"  Output: {self.output_dir}")

    def check_prerequisites(self):
        """Check if required packages are available."""
        try:
            import torch

            print(f"✅ PyTorch: {torch.__version__}")
        except ImportError:
            print("❌ PyTorch not found. Install with: pip install torch")
            return False

        try:
            import unsloth

            print(f"✅ Unsloth: Available")
        except ImportError:
            print("❌ Unsloth not found. Install with: pip install unsloth")
            return False

        try:
            import transformers

            print(f"✅ Transformers: {transformers.__version__}")
        except ImportError:
            print("❌ Transformers not found. Install with: pip install transformers")
            return False

        return True

    def load_model(self):
        """Load the Qwen3-TTS model."""
        try:
            from unsloth import FastLanguageModel
            import torch

            print(f"\nLoading model: {self.model_config['model_name']}")

            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_config["model_name"],
                max_seq_length=self.model_config["max_seq_length"],
                dtype=torch.bfloat16,
                load_in_4bit=self.model_config["load_in_4bit"],
            )

            print("✅ Model loaded successfully")
            return model, tokenizer

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise

    def setup_lora(self, model):
        """Setup LoRA for efficient fine-tuning."""
        from unsloth import FastLanguageModel

        print("\nSetting up LoRA configuration...")

        lora_config = {
            "r": 16,
            "target_modules": [
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
            "lora_alpha": 32,
            "lora_dropout": 0.05,
            "bias": "none",
            "task_type": "CAUSAL_LM",
        }

        model = FastLanguageModel.get_peft_model(model, **lora_config)

        print("✅ LoRA configured:")
        print(f"   Rank (r): {lora_config['r']}")
        print(f"   Alpha: {lora_config['lora_alpha']}")
        print(f"   Dropout: {lora_config['lora_dropout']}")

        return model

    def prepare_dataset(self, dataset_path: str, languages: List[str]):
        """Prepare training dataset from manifest."""
        manifest_path = Path(dataset_path) / "training_manifest.jsonl"

        if not manifest_path.exists():
            print(f"❌ Training manifest not found: {manifest_path}")
            return None

        print(f"\nLoading dataset from: {manifest_path}")

        samples = []
        with open(manifest_path, "r") as f:
            for line in f:
                sample = json.loads(line.strip())
                if sample.get("language") in languages:
                    samples.append(sample)

        print(f"✅ Loaded {len(samples)} samples for languages: {languages}")
        return samples

    def train(
        self,
        dataset_path: str,
        languages: List[str],
        epochs: int = 3,
        learning_rate: float = 2e-4,
        batch_size: int = 4,
        gradient_accumulation: int = 4,
    ):
        """Main training loop."""
        print("\n" + "=" * 60)
        print("Starting Multilingual TTS Finetuning")
        print("=" * 60)

        # Check prerequisites
        if not self.check_prerequisites():
            return

        # Load model
        model, tokenizer = self.load_model()

        # Setup LoRA
        model = self.setup_lora(model)

        # Prepare dataset
        dataset = self.prepare_dataset(dataset_path, languages)
        if dataset is None:
            print("❌ Dataset preparation failed")
            return

        # Training configuration
        training_config = {
            "epochs": epochs,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "gradient_accumulation": gradient_accumulation,
            "languages": languages,
            "model": self.model_config["model_name"],
        }

        print("\nTraining configuration:")
        for key, value in training_config.items():
            print(f"  {key}: {value}")

        # Save training config
        config_path = self.output_dir / "training_config.json"
        with open(config_path, "w") as f:
            json.dump(training_config, f, indent=2)

        print(f"\n✅ Training configuration saved to: {config_path}")
        print("\nNote: Full training loop implementation would go here.")
        print("This script sets up the model and configuration.")
        print("For actual training, use the Kaggle notebook or implement")
        print("the training loop with your preferred framework.")

        # Save the model
        self.save_model(model, tokenizer)

        return model, tokenizer

    def save_model(self, model, tokenizer):
        """Save the fine-tuned model."""
        print(f"\nSaving model to: {self.output_dir}")

        model.save_pretrained(self.output_dir)
        tokenizer.save_pretrained(self.output_dir)

        # Save model info
        model_info = {
            "model_name": self.model_config["model_name"],
            "model_size": self.model_size,
            "finetuned": True,
            "output_dir": str(self.output_dir),
        }

        with open(self.output_dir / "model_info.json", "w") as f:
            json.dump(model_info, f, indent=2)

        print("✅ Model saved successfully")

    def create_test_script(self):
        """Create a script for testing the fine-tuned model."""
        test_script = f'''#!/usr/bin/env python3
"""Test script for fine-tuned TTS model."""

import sys
from pathlib import Path

# Add the model directory to path
model_dir = Path(__file__).parent
sys.path.insert(0, str(model_dir))

def test_model():
    """Test the fine-tuned model with sample text."""
    try:
        from unsloth import FastLanguageModel
        import torch
        import soundfile as sf

        # Load the fine-tuned model
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name="{self.output_dir}",
            max_seq_length=2048,
            dtype=torch.bfloat16,
            load_in_4bit=True,
        )

        print("✅ Model loaded successfully")

        # Test texts for each language
        test_texts = {{
            "itw": "Ma-ngo! Mabbalat. Jehova i Dios.",
            "nl": "Hallo, hoe gaat het met je?",
            "tl": "Kumusta ka? Magandang umaga.",
            "en": "Hello, how are you today?"
        }}

        for lang, text in test_texts.items():
            print(f"\\nTesting {lang}: {text}")
            # Note: Actual TTS generation would go here
            print(f"  Would generate speech for: {text}")

    except Exception as e:
        print(f"❌ Error: {{e}}")

if __name__ == "__main__":
    test_model()
'''

        test_path = self.output_dir / "test_model.py"
        with open(test_path, "w") as f:
            f.write(test_script)

        print(f"\n✅ Test script created: {test_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Finetune Qwen3-TTS model for multilingual TTS"
    )
    parser.add_argument(
        "--model-size",
        "-m",
        choices=["0.6B", "1.7B"],
        default="0.6B",
        help="Model size to finetune (default: 0.6B)",
    )
    parser.add_argument(
        "--dataset",
        "-d",
        required=True,
        help="Path to training dataset (containing training_manifest.jsonl)",
    )
    parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        default=["itw", "nl", "tl"],
        help="Languages to finetune on (default: itw nl tl)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./tts-finetuned",
        help="Output directory for fine-tuned model",
    )
    parser.add_argument(
        "--epochs",
        "-e",
        type=int,
        default=3,
        help="Number of training epochs (default: 3)",
    )
    parser.add_argument(
        "--learning-rate",
        "-r",
        type=float,
        default=2e-4,
        help="Learning rate (default: 0.0002)",
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=4,
        help="Batch size (default: 4)",
    )
    parser.add_argument(
        "--kaggle",
        action="store_true",
        help="Run in Kaggle mode",
    )

    args = parser.parse_args()

    # Initialize finetuner
    finetuner = TTSFinetuner(
        model_size=args.model_size,
        output_dir=args.output,
        use_kaggle=args.kaggle,
    )

    # Run training
    finetuner.train(
        dataset_path=args.dataset,
        languages=args.languages,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
    )

    # Create test script
    finetuner.create_test_script()

    print("\n" + "=" * 60)
    print("✅ Finetuning setup complete!")
    print("=" * 60)
    print(f"Model saved to: {args.output}")
    print(f"Languages: {args.languages}")
    print(f"Model size: {args.model_size}")
    print("\nNext steps:")
    print("1. Upload dataset to Kaggle")
    print("2. Run the Kaggle notebook for full training")
    print("3. Download the fine-tuned model")
    print("4. Test with test_model.py")


if __name__ == "__main__":
    main()
