import os
import sys
import numpy as np
import torch
from pathlib import Path
import json

# Add backend to path
sys.path.append(os.getcwd())

from backend.backends import get_tts_backend
from backend.utils.audio import load_audio

async def extract_native_data(dataset_jsonl, output_jsonl):
    print(f"Extracting native codec tokens from {dataset_jsonl}...")
    
    backend = get_tts_backend()
    print(f"Using backend: {backend.__class__.__name__}")
    
    # Load model to get access to speech tokenizer
    print("Loading model...")
    await backend.load_model_async("1.7B")
    model = backend.model
    
    # In MLX backend, speech_tokenizer is an attribute of the model
    if not hasattr(model, 'speech_tokenizer') or model.speech_tokenizer is None:
        print("Error: Speech tokenizer not found in model.")
        return

    tokenizer = model.speech_tokenizer
    
    native_entries = []
    
    with open(dataset_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            audio_path = entry["audio"]
            text = entry["text"]
            
            print(f"Processing: {audio_path}")
            
            # Load audio (Qwen3-TTS expects 24kHz or it will resample)
            audio, sr = load_audio(audio_path, sample_rate=24000)
            
            # Convert to MLX array if needed
            import mlx.core as mx
            audio_mx = mx.array(audio)[None, None, :] # [1, 1, samples]
            
            # Encode to tokens
            # ref_codes shape: [1, num_quantizers, time]
            tokens = tokenizer.encode(audio_mx)
            mx.eval(tokens)
            
            # Convert to list for JSON storage
            tokens_list = np.array(tokens).tolist()
            
            native_entry = {
                "text": text,
                "tokens": tokens_list,
                "language": entry.get("language", "Tagalog")
            }
            native_entries.append(native_entry)
            
    # Save to JSONL
    with open(output_jsonl, "w", encoding="utf-8") as f:
        for entry in native_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"✓ Native data extraction complete. Saved {len(native_entries)} entries to {output_jsonl}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(extract_native_data("finetune_data/dataset.jsonl", "finetune_data/native_dataset.jsonl"))
