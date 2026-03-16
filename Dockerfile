# Build multi-platform Docker image for Eburon TTS
FROM --platform=linux/amd64 python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    numpy \
    scipy \
    soundfile \
    torch \
    transformers \
    accelerate \
    coqui-tts \
    faster-whisper \
    httpx \
    python-multipart \
    pydantic

# Create app directory
WORKDIR /app

# Copy application files
COPY scripts/eburon_tts_server.py /app/
COPY scripts/itawit_voice_clone.py /app/
COPY scripts/xtts_finetune.py /app/
COPY scripts/training_data/itawit/ /app/training_data/itawit/

# Create necessary directories
RUN mkdir -p /app/output /app/models /app/voice_clones

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the server
CMD ["python", "eburon_tts_server.py"]
