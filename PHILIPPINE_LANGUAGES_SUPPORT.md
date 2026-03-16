# Philippine Languages Support - Implementation Summary

## Changes Made

### 1. Language Support Added (`backend/models.py`)

Added Tagalog (tl) and Ilocano (ilo) language codes:

```python
# Before
language: str = Field(default="en", pattern="^(zh|en|ja|ko|de|fr|ru|pt|es|it)$")

# After  
language: str = Field(default="en", pattern="^(zh|en|ja|ko|de|fr|ru|pt|es|it|tl|ilo)$")
```

### 2. Voice Cloning Fix (`backend/backends/mlx_backend.py`)

Fixed the silent fallback issue that was causing voice profiles to be ignored:

**Before:**
```python
except Exception as e:
    # If voice cloning fails, try without it
    for result in self.model.generate(text):  # Voice LOST!
        ...
```

**After:**
```python
if ref_audio and not supports_ref_audio:
    raise ValueError(
        f"The current TTS model does not support voice cloning. "
        f"Voice samples will be ignored."
    )
```

### 3. Language Parameter Passing

Both backends now properly pass the language parameter to the model:

```python
# Check if model supports language parameter
if supports_language and language:
    gen_kwargs["language"] = language
```

### 4. Better Logging

Added detailed logging to help debug issues:

```python
print(f"[MLX TTS] Generating audio:")
print(f"  Text: {text[:100]}...")
print(f"  Language: {language}")
print(f"  Voice cloning: {'ENABLED' if ref_audio else 'DISABLED'}")
```

## Creating Training Data

### Tagalog (Filipino)

```bash
cd /Users/master/vbox/voicebox
python gather_finetune_data.py
```

### Ilocano

```bash
cd /Users/master/vbox/voicebox
python gather_ilocano_data.py
```

This collects audio-text pairs from JW.org's Bible publications.

## Using Philippine Languages

### API Example

```bash
# Create a Tagalog voice profile
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "Tagalog Speaker", "language": "tl"}'

# Create an Ilocano voice profile
curl -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "Ilocano Speaker", "language": "ilo"}'
```

### Python Example

```python
import requests

# Create profile
response = requests.post('http://localhost:8000/profiles', json={
    'name': 'Ilocano Voice',
    'language': 'ilo'
})
profile_id = response.json()['id']

# Upload voice sample (audio file)
with open('ilocano_sample.wav', 'wb') as f:
    requests.post(
        f'http://localhost:8000/profiles/{profile_id}/samples',
        files={'file': f},
        data={'reference_text': 'Naimbag a bigat.'}
    )

# Generate speech
response = requests.post('http://localhost:8000/generate', json={
    'profile_id': profile_id,
    'text': 'Naimbag a bigat. Kasano ka?',
    'language': 'ilo'
})
```

## Troubleshooting

### Voice Cloning Not Working

If you see: "The current TTS model does not support voice cloning"

**Solution:** Ensure your TTS model supports the `ref_audio` parameter. Check:
1. Model version - older versions may not support voice cloning
2. Model is fully loaded before generation
3. Voice sample is valid (proper format, duration)

### Language Not Working

If generated audio doesn't match the selected language:

**Solution:** The base model may need fine-tuning for Philippine languages:
1. Collect training data using `gather_ilocano_data.py`
2. Fine-tune the TTS model with Philippine language data
3. The language parameter is passed but may not be fully effective without fine-tuning

### Files Structure

```
finetune_data/
├── audio/
│   ├── genesis_1.mp3
│   ├── genesis_2.mp3
│   └── ...
├── dataset.jsonl          # Tagalog data
├── native_dataset.jsonl   # Native format
└── ilocano/
    ├── audio/
    │   └── ...
    └── ilocano_dataset.jsonl
```

## Future Work

1. **Collect More Data**: Expand to other Philippine languages (Cebuano, Hiligaynon, etc.)
2. **Fine-tune Models**: Train TTS models specifically for Philippine languages
3. **Native Speaker Recordings**: Replace JW.org data with native speaker recordings
4. **Quality Evaluation**: Add metrics for pronunciation accuracy