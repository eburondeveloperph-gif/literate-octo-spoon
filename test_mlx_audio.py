from mlx_audio.tts import load
import numpy as np
import soundfile as sf
from pathlib import Path

# Load model
model = load("mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16")

# Setup cloning
ref_audio = "./backend/venv/lib/python3.12/site-packages/gradio/media_assets/audio/sax.wav"
ref_text = "A saxophone playing some jazz music in a dimly lit room."
output_text = "This is a test of voice cloning using a saxophone recording as reference."
lang_code = "english"

if not Path(ref_audio).exists():
    print(f"File not found: {ref_audio}")
    exit(1)

print("Generating...")
audio_chunks = []
sample_rate = 24000

for result in model.generate(
    output_text, 
    ref_audio=ref_audio, 
    ref_text=ref_text,
    lang_code=lang_code,
    verbose=True,
    top_k=0,
):
    audio_chunks.append(np.array(result.audio))
    sample_rate = result.sample_rate

if audio_chunks:
    audio = np.concatenate(audio_chunks)
    sf.write("mlx_direct_output.wav", audio, sample_rate)
    print(f"Success! Saved to mlx_direct_output.wav. Shape: {audio.shape}")
else:
    print("Failed: No audio generated.")
