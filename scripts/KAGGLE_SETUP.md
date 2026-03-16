# Kaggle Multilingual TTS Finetuning Setup

This guide explains how to finetune the Qwen3-TTS 0.6B model for multilingual TTS on Kaggle.

## Overview

We're finetuning the **Qwen3-TTS 0.6B model** for real-time multilingual TTS with support for:
- **Itawit** (itw) - Philippine indigenous language
- **Dutch/Flemish** (nl) - Belgian Dutch
- **Tagalog** (tl) - Philippine national language

## Files Created

| File | Description |
|------|-------------|
| `kaggle_multilingual_tts.py` | Prepares training data for Kaggle |
| `finetune_qwen_multilingual.py` | Finetuning script |
| `kaggle_finetune_notebook.py` | Kaggle notebook template |

## Step 1: Prepare Training Data

```bash
cd /Users/master/vbox/voicebox/scripts

# Create Kaggle dataset with all languages
python3 kaggle_multilingual_tts.py \
  -o ./kaggle_dataset \
  --create-manifest \
  --create-notebook \
  -l itw nl tl

# Or create with specific languages only
python3 kaggle_multilingual_tts.py \
  -o ./kaggle_dataset \
  --create-manifest \
  -l itw
```

This creates:
- `kaggle_dataset/` - Complete dataset directory
- `training_manifest.jsonl` - Training data manifest
- `kaggle_finetune_notebook.py` - Kaggle notebook script
- `realtime_config.json` - Real-time TTS configuration

## Step 2: Upload to Kaggle

1. Go to [Kaggle Datasets](https://www.kaggle.com/datasets)
2. Click "New Dataset"
3. Upload the `kaggle_dataset/` folder
4. Set visibility to **Public** or **Private**
5. Note the dataset ID (e.g., `eburon/multilingual-tts-dataset`)

## Step 3: Create Kaggle Notebook

1. Go to [Kaggle Notebooks](https://www.kaggle.com/code)
2. Click "New Notebook"
3. Copy the content from `kaggle_finetune_notebook.py`
4. Add your dataset as input:
   - Click "+ Add Data"
   - Search for your uploaded dataset
   - Add it to the notebook

## Step 4: Configure the Notebook

Update the notebook configuration:

```python
# Configuration
MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
OUTPUT_DIR = "/kaggle/working/tts-finetuned"
DATASET_DIR = "/kaggle/input/your-dataset-name"

# Training parameters
EPOCHS = 3
LEARNING_RATE = 2e-4
BATCH_SIZE = 4
GRADIENT_ACCUMULATION = 4
```

## Step 5: Run Training

Click "Run All" in the Kaggle notebook. The training will:

1. **Load the dataset** from Kaggle input
2. **Load the model** (Qwen3-TTS 0.6B with 4-bit quantization)
3. **Configure LoRA** for efficient fine-tuning
4. **Train** for the specified number of epochs
5. **Save the fine-tuned model** to `/kaggle/working/`

## Step 6: Download the Model

After training completes:

1. Go to the notebook's output section
2. Click on the `tts-finetuned` folder
3. Download the model files:
   - `adapter_model.safetensors` - LoRA weights
   - `tokenizer_config.json` - Tokenizer configuration
   - `training_config.json` - Training parameters

## Step 7: Deploy the Model

1. Copy the downloaded model to your local machine
2. Update the backend configuration to use the fine-tuned model

```bash
# Test the fine-tuned model
python3 finetune_qwen_multilingual.py \
  --model-size 0.6B \
  --dataset /path/to/dataset \
  --output /path/to/fine-tuned-model
```

## Model Architecture

```
Qwen3-TTS 0.6B Model
├── Base Model (0.6B parameters)
├── LoRA Adapters (16 rank)
│   ├── q_proj
│   ├── k_proj
│   ├── v_proj
│   ├── o_proj
│   ├── gate_proj
│   ├── up_proj
│   └── down_proj
└── Tokenizer (multilingual)
```

## Real-time TTS Configuration

The `realtime_config.json` contains settings for real-time inference:

```json
{
  "model": {
    "name": "Qwen3-TTS-12Hz-0.6B-Base",
    "size": "0.6B",
    "quantization": "4bit",
    "device": "mlx"
  },
  "realtime": {
    "latency_target_ms": 100,
    "streaming_enabled": true,
    "batch_size": 1,
    "cache_enabled": true
  }
}
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| **Latency** | <100ms | For real-time TTS |
| **Model Size** | ~400MB | After 4-bit quantization |
| **VRAM** | <2GB | On Apple Silicon MLX |
| **Throughput** | ~50 tokens/sec | With streaming |

## Training Data Statistics

| Language | Samples | Duration | Source |
|----------|---------|----------|--------|
| Itawit (itw) | ~100 | ~30 min | JW.org |
| Dutch (nl) | ~100 | ~25 min | Public domain |
| Tagalog (tl) | ~109 | ~35 min | Public domain |
| **Total** | **309** | **~90 min** | |

## Troubleshooting

### Out of Memory on Kaggle

- Use 4-bit quantization: `load_in_4bit=True`
- Reduce batch size: `batch_size=2`
- Use gradient accumulation: `gradient_accumulation_steps=8`

### Slow Training

- Enable mixed precision: `fp16=True`
- Use AdamW 8-bit optimizer
- Reduce `max_seq_length` if possible

### Model Quality Issues

- Ensure clean audio samples (no background noise)
- Use diverse training data (multiple speakers/accents)
- Train for more epochs (5-10) if needed

## References

- [Qwen3-TTS Hugging Face](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base)
- [Unsloth Documentation](https://github.com/unslothai/unsloth)
- [Kaggle GPU Limits](https://www.kaggle.com/docs/gpu)
- [MLX for Apple Silicon](https://github.com/ml-explore/mlx)
