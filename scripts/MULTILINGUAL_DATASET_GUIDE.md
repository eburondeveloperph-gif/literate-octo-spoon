# Multilingual TTS Dataset Guide

This guide explains how to prepare training data for multilingual TTS finetuning using various dataset sources.

## Available Dataset Sources

### 1. **Itawit Training Data** (Local)
- **Location**: `scripts/training_data/itawit/`
- **Samples**: 309 audio segments
- **Language**: Itawit (itw)
- **Source**: JW.org publications

### 2. **Dutch/Flemish Data** (Local)
- **Location**: `scripts/training_data/dutch_be/`
- **Language**: Dutch/Flemish (nl)
- **Note**: Currently empty - needs data collection

### 3. **Tagalog Data** (Local)
- **Location**: `scripts/training_data/tagalog/`
- **Language**: Tagalog (tl)
- **Note**: Currently empty - needs data collection

### 4. **MLCommons People's Speech** (External)
- **Dataset**: [MLCommons/peoples_speech](https://huggingface.co/datasets/MLCommons/peoples_speech)
- **Size**: 12,000+ hours
- **Languages**: 100+ languages
- **License**: CC BY
- **Usage**: Requires filtering and language identification

### 5. **Common Voice** (External)
- **Dataset**: [mozilla/common_voice](https://huggingface.co/datasets/mozilla/common_voice)
- **Languages**: 100+ languages
- **License**: CC0
- **Usage**: Good for TTS training

### 6. **VoxPopuli** (External)
- **Dataset**: [facebook/voxpopuli](https://huggingface.co/datasets/facebook/voxpopuli)
- **Languages**: 23 European languages
- **License**: CC BY-NC-ND
- **Usage**: Speech recognition + TTS

## Setup Scripts

### 1. Kaggle Dataset Preparation

```bash
cd /Users/master/vbox/voicebox/scripts

# Prepare Kaggle dataset with Itawit data
python3 kaggle_multilingual_tts.py \
  -o ./kaggle_dataset \
  --create-manifest \
  --create-notebook \
  -l itw
```

**Output**: `kaggle_dataset/` containing:
- `training_manifest.jsonl` - Training data manifest
- `kaggle_finetune_notebook.py` - Kaggle notebook
- `realtime_config.json` - Real-time TTS config

### 2. Dataset Maker Integration

```bash
# Prepare multilingual dataset using Dataset Maker
python3 prepare_multilingual_dataset.py \
  -l itw nl tl \
  -o ./multilingual_dataset
```

### 3. People's Speech Integration

```bash
# Check dataset info
python3 peoples_speech_integration.py --info

# Load metadata
python3 peoples_speech_integration.py --metadata

# Create subset
python3 peoples_speech_integration.py \
  -l en es fr \
  -o ./peoples_speech_subset
```

## Finetuning Workflow

### Step 1: Prepare Training Data

```bash
# Option A: Use existing training data
python3 prepare_multilingual_dataset.py -l itw -o ./dataset

# Option B: Download from Hugging Face
python3 peoples_speech_integration.py -l en -o ./dataset
```

### Step 2: Upload to Kaggle

1. Go to [Kaggle Datasets](https://www.kaggle.com/datasets)
2. Create new dataset
3. Upload the dataset folder
4. Set visibility (Public/Private)
5. Note the dataset ID

### Step 3: Run Finetuning Notebook

1. Create new Kaggle notebook
2. Add your dataset as input
3. Copy `kaggle_finetune_notebook.py` content
4. Update dataset path
5. Run training

### Step 4: Download Fine-tuned Model

1. After training completes
2. Download model files from Kaggle output
3. Deploy locally

## Training Data Structure

### Qwen3-TTS Format (JSONL)

```json
{"audio": "./data/audio1.wav", "text": "Hello world", "ref_audio": "./data/ref.wav"}
{"audio": "./data/audio2.wav", "text": "Another sample", "ref_audio": "./data/ref.wav"}
```

### Directory Structure

```
multilingual_dataset/
├── itw/                          # Itawit language
│   ├── data/
│   │   ├── audio1.wav
│   │   ├── audio2.wav
│   │   └── ref_audio.wav
│   ├── train.jsonl
│   └── language_config.json
├── nl/                           # Dutch/Flemish
├── tl/                           # Tagalog
├── training_manifest.jsonl       # Combined manifest
├── dataset_config.json           # Dataset info
└── kaggle-metadata.json          # Kaggle metadata
```

## Language Codes

| Code | Language | Directory |
|------|----------|-----------|
| `itw` | Itawit | `itawit/` |
| `nl` | Dutch/Flemish | `dutch_be/` |
| `tl` | Tagalog | `tagalog/` |
| `en` | English | `english/` |
| `es` | Spanish | `spanish/` |
| `fr` | French | `french/` |

## Model Configuration

### Qwen3-TTS 0.6B (Real-time)

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
  },
  "finetuning": {
    "epochs": 3,
    "learning_rate": 2e-4,
    "batch_size": 4,
    "lora_rank": 16,
    "lora_alpha": 32
  }
}
```

### Training Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Epochs | 3 | Can increase to 5-10 |
| Learning Rate | 2e-4 | For LoRA fine-tuning |
| Batch Size | 4 | Adjust based on GPU |
| LoRA Rank | 16 | For efficient fine-tuning |
| Max Seq Length | 2048 | Tokenizer limit |

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Latency | <100ms | Real-time TTS |
| Model Size | ~400MB | After 4-bit quantization |
| VRAM | <2GB | Apple Silicon MLX |
| Throughput | ~50 tokens/sec | With streaming |

## Troubleshooting

### Empty Training Data

```bash
# Check audio files
find training_data -name "*.wav" -o -name "*.mp3" | wc -l

# Check segments
find training_data -name "segments" -type d
```

### Path Issues

Ensure paths in `LANGUAGE_CONFIGS` match actual directory structure:
- `dutch_be/` not `dutch/`
- `itawit/` not `itw/`

### Kaggle Upload Issues

- Compress large datasets
- Use Git LFS for very large files
- Split into multiple datasets if needed

## References

- [Qwen3-TTS Hugging Face](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base)
- [Unsloth Documentation](https://github.com/unslothai/unsloth)
- [MLCommons People's Speech](https://huggingface.co/datasets/MLCommons/peoples_speech)
- [Dataset Maker](https://github.com/eburondeveloperph-gif/dataset-maker)
- [Kaggle GPU](https://www.kaggle.com/docs/gpu)
