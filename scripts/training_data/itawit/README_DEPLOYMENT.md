# Echobox Itawit TTS - Deployment & Training Guide

This guide covers setting up the Itawit (Itawis) Text-to-Speech system with voice cloning capabilities using Qwen3-TTS and Coqui XTTS.

## Prerequisites

- macOS (Apple Silicon recommended for MLX)
- Python 3.12+
- FFmpeg installed (`brew install ffmpeg`)

## Quick Start

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/eburondeveloperph-gif/symmetrical-spork.git
cd echovoice

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn soundfile numpy
pip install mlx mlx_audio
pip install coqui-tts torchcodec
```

### 2. Start the TTS Server

```bash
cd scripts
python eburon_tts_server.py
```

The server runs on `http://localhost:8000`

## API Endpoints

### Generate Itawit Speech

```bash
# Using multi-reference voice cloning (recommended)
curl -X POST http://localhost:8000/generate/itawit \
  -F "text=Ma-ngo! Mabbalat. Jehova i Dios." \
  -F "use_multi_ref=true"
```

### Clone Voice

```bash
curl -X POST http://localhost:8000/voice/clone \
  -F "name=My Itawit Voice" \
  -F "description=Custom Itawit voice" \
  -F "language=itw" \
  -F "reference_text=Ma-ngo!" \
  -F "audio=@/path/to/reference.wav"
```

### Training Data Management

```bash
# Scan training data
curl -X POST http://localhost:8000/training/scan

# Get training stats
curl http://localhost:8000/training/stats

# Get training data
curl http://localhost:8000/training/data
```

## Itawit Dataset

### Training Data Sources

The Itawit training data comes from JW.org publications in Itawit language:

1. **Nakakkasta nga Balita** (Good News) - 10 lessons
2. **Look, Listen & Live** - Audio Bible stories
3. **Knock Knock** - Evangelistic series
4. **Treasures** - Bible teaching

### Dataset Structure

```
scripts/training_data/itawit/
├── segments/           # 309 processed audio segments
│   └── itv_reader_01_*.wav
├── xtts_train/wav/     # 24kHz mono WAV for XTTS
├── voice_clones/       # Saved voice clones
├── ref.wav           # Reference audio
└── lexicon.txt       # Itawit vocabulary
```

### Lexicon

The lexicon contains verified Itawit translations:

| Itawit | English |
|---------|---------|
| ma_ngo | Hello |
| mabbalat | Thank you |
| oon | Yes |
| awan | No |
| napia | Good/Well |
| kunnasi ka | How are you? |
| jehova i Dios | Jehovah is God |
| ay_ayatan ta ka | I love you |

## Voice Cloning

### How It Works

1. **Reference Audio**: Upload a clean audio sample (5-30 seconds)
2. **Voice Extraction**: The system extracts voice features
3. **Multi-Reference Mode**: Uses multiple training samples for better cloning

### Creating a Voice Clone

```python
import requests

# Clone a voice
with open("reference.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/voice/clone",
        data={
            "name": "Itawit Speaker",
            "description": "Native Itawit speaker",
            "language": "itw",
            "reference_text": "Text spoken in the audio"
        },
        files={"audio": f}
    )
    print(response.json())
```

## Training Guide

### Option 1: Multi-Reference Voice Cloning (Recommended)

For immediate results without full model training:

```bash
# Generate using 20 reference samples
curl -X POST http://localhost:8000/generate/itawit \
  -F "text=Your Itawit text here" \
  -F "use_multi_ref=true"
```

The system uses multiple reference audios simultaneously for more natural voice cloning.

### Option 2: Fine-tuning XTTS

For permanent voice models:

1. **Prepare Training Data**

```bash
# Convert audio to 24kHz mono WAV
ffmpeg -i input.mp3 -ar 24000 -ac 1 output.wav
```

2. **Create Training Manifest**

```json
{
  "language": "itv",
  "samples": [
    {
      "audio": "path/to/audio.wav",
      "text": "Itawit transcription",
      "duration": 5.5
    }
  ]
}
```

3. **Run Fine-tuning**

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Fine-tune with your dataset
# (Requires GPU with 8GB+ VRAM)
tts.train(
    output_path="models/itawit_v1",
    dataset="path/to/manifest.json",
    epochs=50
)
```

### Option 3: Qwen3-TTS Training

The JW.org Itawit toolkit provides a complete pipeline:

```bash
cd /path/to/jw_qwen_itv_toolkit

# Run full pipeline
python -m jw_qwen_itv.run_itv_pipeline --workdir .

# This will:
# 1. Discover JW.org pages
# 2. Download audio
# 3. Extract transcripts
# 4. Normalize audio
# 5. Segment and align
# 6. Export to Qwen JSONL format
```

## Itawit Phrases for Testing

```itawit
Ma-ngo! Mabbalat.                    # Hello! Thank you.
Jehova i Dios.                       # Jehovah is God.
Kunnasi ka? Napia nak.               # How are you? I'm fine.
Anna yo ngahan mu?                   # What is your name?
Ay-ayatan ta ka.                      # I love you.
Ti biblian ti kasisirinan na.         # The Bible is the truth.
Nakakkasta nga Balita nga Naggafu kan Dios!  # Good News From God!
```

## Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (UI)                  │
│  - Eburon theme (black/lime green)          │
│  - Voice cloning interface                 │
│  - Emotion selection                       │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│           FastAPI Server                     │
│  - /generate (Qwen3-TTS)                   │
│  - /generate/itawit (Coqui XTTS)          │
│  - /voice/clone                            │
│  - /training/*                            │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────┐         ┌────▼─────┐
│ Qwen3-TTS│         │Coqui XTTS│
│ (MLX)    │         │Voice Clone│
└──────────┘         └──────────┘
```

## Performance Notes

- **MLX** provides fast inference on Apple Silicon
- **Multi-reference cloning** uses 20+ samples for better quality
- **Voice prompts** persist across server restarts

## Troubleshooting

### Server won't start

```bash
# Check port
lsof -i:8000

# Kill existing process
kill -9 <PID>
```

### Coqui TTS issues

```bash
# Reinstall with codec
pip install coqui-tts[codec]
```

### Audio quality issues

- Use clean reference audio (no background noise)
- Keep reference audio between 5-30 seconds
- Use multiple reference samples for better cloning

## License

This project uses:
- Qwen3-TTS (Apache 2.0)
- Coqui XTTS (CPML - non-commercial)
- JW.org audio content (permission granted for personal use)

## References

- [Qwen3-TTS Documentation](https://github.com)
- [Coqui TTS](https://coqui.ai)
- [JW.org Itawit Publications](https://www.jw.org/itv/)
- [GRN Itawit Recordings](https://globalrecordings.net)
