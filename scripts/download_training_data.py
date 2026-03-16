#!/usr/bin/env python3
"""
Download sample training data for TTS from JW.org
Usage: python download_training_data.py <language_code>
Languages: tl (Tagalog), nl (Dutch), nl-be (Flemish)
"""

import os
import sys
import urllib.request
import json
import subprocess
from pathlib import Path

LANGUAGE_CONFIGS = {
    "tl": {
        "name": "Tagalog",
        "jw_lang": "tl",
        "output_dir": "/Users/master/vbox/echovoice/scripts/training_data/tagalog",
    },
    "nl": {
        "name": "Dutch (Netherlands)",
        "jw_lang": "nl",
        "output_dir": "/Users/master/vbox/echovoice/scripts/training_data/dutch_nl",
    },
    "nl-be": {
        "name": "Dutch (Flemish)",
        "jw_lang": "nl-be",
        "output_dir": "/Users/master/vbox/echovoice/scripts/training_data/dutch_be",
    },
}

JW_PUBLICATIONS = {
    "tl": [
        ("jw_t30_TL_01", "Good News - Tagalog"),
        ("jw_t30_TL_02", "Good News - Tagalog"),
        ("jw_ll_TL_01", "Learn From - Tagalog"),
        ("jw_ll_TL_02", "Learn From - Tagalog"),
    ],
    "nl": [
        ("jw_t30_NL_01", "Good News - Dutch"),
        ("jw_t30_NL_02", "Good News - Dutch"),
        ("jw_ll_NL_01", "Learn From - Dutch"),
        ("jw_ll_NL_02", "Learn From - Dutch"),
    ],
    "nl-be": [
        ("jw_t30_NLBE_01", "Good News - Flemish"),
        ("jw_ll_NLBE_01", "Learn From - Flemish"),
    ],
}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    for subdir in ["segments", "models", "voice_clones"]:
        os.makedirs(os.path.join(path, subdir), exist_ok=True)


def download_sample_audio(lang_code):
    """Download sample audio files from JW.org for the given language."""
    config = LANGUAGE_CONFIGS.get(lang_code)
    if not config:
        print(f"Unknown language: {lang_code}")
        return False

    output_dir = config["output_dir"]
    ensure_dir(output_dir)

    print(f"\n=== Downloading {config['name']} Training Data ===")
    print(f"Output directory: {output_dir}")

    publications = JW_PUBLICATIONS.get(lang_code, [])

    for pub_id, desc in publications:
        print(f"\nDownloading: {desc} ({pub_id})")

        sample_files = [
            f"https://b.jw-cdn.org/apis/pub-media/GETPUI?langcode={config['jw_lang']}&pub={pub_id}&fileformat=mp3",
        ]

        output_file = os.path.join(output_dir, f"{pub_id}.mp3")

        try:
            if os.path.exists(output_file):
                print(f"  Already exists: {output_file}")
                continue

            print(f"  Note: Direct API download not implemented")
            print(f"  Please manually download from JW.org:")
            print(f"  1. Go to jw.org > Publications > Audio > {config['name']}")
            print(f"  2. Download 'Good News' or 'Learn From' audio files")
            print(f"  3. Save as {pub_id}.mp3 in {output_dir}")

        except Exception as e:
            print(f"  Error: {e}")

    create_lexicon_file(lang_code, output_dir)
    create_readme(lang_code, config)

    print(f"\n=== Setup Complete ===")
    print(f"Add your audio files to: {output_dir}")
    print(f"Then run the TTS server to use the language.")

    return True


def create_lexicon_file(lang_code, output_dir):
    """Create a lexicon file for the language."""
    lexicons = {
        "tl": {
            "kamusta": "Hello",
            "magandang_umaga": "Good morning",
            "magandang_hapon": "Good afternoon",
            "magandang_gabi": "Good evening",
            "salamat": "Thank you",
            "paalam": "Goodbye",
            "oo": "Yes",
            "hindi": "No",
            "pakiusap": "Please",
            "iniibig_kita": "I love you",
            "anong_pangalan_mo": "What is your name",
            "saan_ka_nakatira": "Where do you live",
        },
        "nl": {
            "hallo": "Hello",
            "goedemorgen": "Good morning",
            "goedenavond": "Good evening",
            "dank_u": "Thank you",
            "tot_ziens": "Goodbye",
            "ja": "Yes",
            "nee": "No",
            "alstublieft": "Please",
            "ik_liefde_je": "I love you",
            "hoe_gaat_het": "How are you",
            "wat_is_je_naam": "What is your name",
        },
        "nl-be": {
            "hallo": "Hello",
            "goedemorgen": "Good morning",
            "goedenavond": "Good evening",
            "dank_u": "Thank you",
            "tot_ziens": "Goodbye",
            "ja": "Yes",
            "nee": "No",
            "alstublieft": "Please",
            "ik_liefde_je": "I love you",
        },
    }

    lexicon = lexicons.get(lang_code, {})
    lexicon_file = os.path.join(output_dir, "lexicon.txt")

    with open(lexicon_file, "w") as f:
        f.write(f"# {lang_code.upper()} Lexicon for Eburon TTS\n")
        f.write("# Format: word = translation\n\n")
        for word, translation in lexicon.items():
            f.write(f"{word} = {translation}\n")

    print(f"Created lexicon: {lexicon_file}")


def create_readme(lang_code, config):
    """Create a README file with instructions."""
    readme_file = os.path.join(config["output_dir"], "README.txt")

    content = f"""# {config["name"]} Training Data for Eburon TTS

## Setup Instructions

1. Download audio files from JW.org ({config["jw_lang"]})
   - Go to jw.org > Publications > Audio
   - Search for "{config["name"]}" 
   - Download "Good News" (Beginner) or "Learn From" (Intermediate) audio

2. Place audio files in this directory:
   {config["output_dir"]}/

3. Supported file formats: .mp3, .wav, .flac

4. For best results:
   - Use 5-30 second audio clips
   - Ensure clear audio quality
   - Include various speakers (male and female)
   - Cover different speaking speeds

5. Restart the TTS server to detect new training data

## File Naming Convention

Recommended naming:
- jw_t30_XX_01.mp3 = Good News (Beginner) - Language XX - Track 01
- jw_ll_XX_01.mp3 = Learn From - Language XX - Track 01
- kt_XX_01.mp3 = Custom Track - Language XX - Track 01

## Language Code: {lang_code}

This directory is used by Eburon TTS for native {config["name"]} voice synthesis.
"""

    with open(readme_file, "w") as f:
        f.write(content)

    print(f"Created README: {readme_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_training_data.py <language_code>")
        print("Languages:")
        print("  tl      - Tagalog")
        print("  nl      - Dutch (Netherlands)")
        print("  nl-be   - Dutch (Flemish)")
        sys.exit(1)

    lang_code = sys.argv[1].lower()
    download_sample_audio(lang_code)
