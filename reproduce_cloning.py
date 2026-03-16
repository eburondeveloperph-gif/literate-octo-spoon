import asyncio
import os
import sys
import torch
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.append(os.getcwd())

from backend.backends import get_tts_backend
from backend.utils.audio import load_audio, save_audio

async def test_cloning(audio_path, reference_text, output_text, language="en"):
    print(f"Testing cloning with:")
    print(f"  Audio: {audio_path}")
    print(f"  Ref Text: {reference_text}")
    print(f"  Output Text: {output_text}")
    print(f"  Language: {language}")

    # Get backend
    backend = get_tts_backend()
    print(f"Using backend: {backend.__class__.__name__}")

    # Load model
    print("Loading model...")
    await backend.load_model_async("1.7B")
    print("Model loaded.")

    # Create voice prompt
    print("Creating voice prompt...")
    voice_prompt, was_cached = await backend.create_voice_prompt(audio_path, reference_text, use_cache=False)
    print(f"Voice prompt created (cached: {was_cached})")
    print(f"Prompt keys: {list(voice_prompt.keys())}")

    # Generate
    print("Generating speech...")
    audio, sr = await backend.generate(output_text, voice_prompt, language=language)
    print(f"Speech generated. Audio shape: {audio.shape}, SR: {sr}")

    # Save output
    output_path = "reproduction_output.wav"
    save_audio(audio, output_path, sr)
    print(f"Saved output to: {output_path}")

if __name__ == "__main__":
    # Use provided file or fallback to a known one
    audio_file = "/Users/master/Downloads/ito-ang-karaniwang-reaksyon-ng.wav"
    if not os.path.exists(audio_file):
        print(f"File not found: {audio_file}")
        # Try to find a fallback from previous search
        audio_file = "./backend/venv/lib/python3.12/site-packages/gradio/media_assets/audio/sax.wav"
        ref_text = "A saxophone playing some jazz."
    else:
        ref_text = "ito ang karaniwang reaksyon ng" # Based on filename

    asyncio.run(test_cloning(
        audio_file, 
        ref_text,
        "Hello, this is a test of voice cloning quality.",
        "en"
    ))
