"""
Utilities for managing language-specific LoRA adapters.
"""

import os
from pathlib import Path
from typing import Optional

from .. import config


def get_adapters_dir() -> Path:
    """Get the directory where LoRA adapters are stored."""
    # Store in data/models/adapters/
    adapters_dir = config.get_data_dir() / "models" / "adapters"
    adapters_dir.mkdir(parents=True, exist_ok=True)
    return adapters_dir


def get_adapter_path(language_code: str) -> Optional[Path]:
    """
    Get the path to a LoRA adapter for a specific language.
    
    Args:
        language_code: Language code (e.g., 'tl' for Tagalog)
        
    Returns:
        Path to adapter directory if it exists, otherwise None
    """
    # Normalize language code (e.g. 'chinese_simplified' -> 'zh')
    # Use the base language code for adapter lookup
    from .languages import map_to_tts_language
    base_code = map_to_tts_language(language_code)
    
    adapter_dir = get_adapters_dir() / base_code
    
    # Check if directory exists and contains standard LoRA files
    if adapter_dir.exists() and adapter_dir.is_dir():
        # Look for standard files like adapter_config.json or adapter_model.bin/safetensors
        if (adapter_dir / "adapter_config.json").exists():
            return adapter_dir
            
    return None


def has_adapter(language_code: str) -> bool:
    """Check if a LoRA adapter exists for a language."""
    return get_adapter_path(language_code) is not None
