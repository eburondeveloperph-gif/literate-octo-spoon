#!/usr/bin/env python3
"""Simple TTS script using Qwen3 TTS via MLX."""

from mlx_audio.tts import load
import numpy as np
import soundfile as sf
import sys
import os

MODEL_PATH = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"

_model = None


def get_model():
    global _model
    if _model is None:
        print("Loading Qwen3 TTS model...", file=sys.stderr)
        _model = load(MODEL_PATH)
        print("Model loaded!", file=sys.stderr)
    return _model


def speak(text: str, output_path: str = "/tmp/tts_output.wav"):
    """Generate speech and save to file."""
    model = get_model()
    result = list(model.generate(text=text))[-1]
    sf.write(output_path, result.audio, result.sample_rate)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: qwen_tts.py "Your text here" [output_file]')
        sys.exit(1)

    text = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/tts_output.wav"

    path = speak(text, output)
    print(f"Saved to: {path}")
