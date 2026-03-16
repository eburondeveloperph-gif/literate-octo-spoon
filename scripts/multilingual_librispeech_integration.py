#!/usr/bin/env python3
"""
Integration with Facebook Multilingual LibriSpeech Dataset
https://huggingface.co/datasets/facebook/multilingual_librispeech

Features:
- 1000+ hours of speech
- 12 languages: Dutch, English, French, German, Italian, Polish, Portuguese, Russian, Spanish, Turkish, Welsh, Mandarin
- High-quality transcriptions
- Speaker information included
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any


class MultilingualLibriSpeechIntegration:
    """Integrate Facebook Multilingual LibriSpeech for TTS training."""

    def __init__(self):
        self.dataset_name = "facebook/multilingual_librispeech"
        # Available languages in the dataset
        self.languages = {
            "dutch": "nl",
            "english": "en",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "polish": "pl",
            "portuguese": "pt",
            "russian": "ru",
            "spanish": "es",
            "turkish": "tr",
            "welsh": "cy",
            "mandarin": "zh",
        }

        print(f"Multilingual LibriSpeech Integration")
        print(f"  Dataset: {self.dataset_name}")
        print(f"  Languages: {len(self.languages)}")
        print(f"  Available: {', '.join(self.languages.keys())}")

    def list_available_languages(self):
        """List all available languages in the dataset."""
        print("\nAvailable languages:")
        for config_lang, code in self.languages.items():
            print(f"  {config_lang:12} -> {code}")

    def get_dataset_info(self):
        """Get dataset information."""
        try:
            from huggingface_hub import HfApi

            api = HfApi()
            dataset_info = api.dataset_info(self.dataset_name)

            print(f"\nDataset Information:")
            print(f"  ID: {dataset_info.id}")
            print(f"  Downloads: {dataset_info.downloads}")
            print(f"  Likes: {dataset_info.likes}")
            print(f"  License: {dataset_info.license}")

            return dataset_info
        except ImportError:
            print("⚠️  huggingface_hub not installed")
            return None

    def sample_language_data(
        self,
        language: str,
        samples: int = 10,
        split: str = "dev",
    ):
        """Sample data from a specific language."""
        import requests

        print(f"\nSampling {language} data ({split} split, {samples} samples)...")

        # Check if language config exists
        if language not in self.languages:
            print(f"❌ Language '{language}' not available")
            print(f"   Available: {list(self.languages.keys())}")
            return []

        # Fetch samples from Hugging Face API
        url = f"https://datasets-server.huggingface.co/rows"
        params = {
            "dataset": self.dataset_name,
            "config": language,
            "split": split,
            "offset": 0,
            "length": samples,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "rows" not in data:
                print(f"⚠️  No data returned for {language}")
                return []

            rows = data["rows"]
            print(f"✅ Retrieved {len(rows)} samples")

            # Display sample information
            for i, row in enumerate(rows[:3], 1):
                item = row["row"]
                print(f"\nSample {i}:")
                print(f"  Speaker: {item.get('speaker_id', 'N/A')}")
                print(f"  Duration: {item.get('audio_duration', 'N/A')}s")
                print(f"  Transcript: {item.get('transcript', '')[:60]}...")

            return rows

        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return []

    def export_language_data(
        self,
        language: str,
        output_dir: str,
        samples: int = 100,
        split: str = "train",
    ):
        """Export data for a specific language to Qwen3-TTS format."""
        import requests
        import shutil

        output_path = Path(output_dir) / language
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nExporting {language} data to: {output_path}")

        # Create data directory
        data_dir = output_path / "data"
        data_dir.mkdir(exist_ok=True)

        # Fetch data in batches
        batch_size = 100
        entries = []
        offset = 0

        print(f"Fetching {samples} samples in batches of {batch_size}...")

        while offset < samples:
            current_batch = min(batch_size, samples - offset)

            url = f"https://datasets-server.huggingface.co/rows"
            params = {
                "dataset": self.dataset_name,
                "config": language,
                "split": split,
                "offset": offset,
                "length": current_batch,
            }

            try:
                response = requests.get(url, params=params)
                data = response.json()

                if "rows" not in data or not data["rows"]:
                    break

                for row in data["rows"]:
                    item = row["row"]
                    transcript = item.get("transcript", "").strip()

                    if transcript:
                        # Note: Actual audio download would require the full dataset
                        # For now, we'll create a placeholder entry
                        entry = {
                            "audio": f"./data/{language}_{len(entries):06d}.wav",
                            "text": transcript,
                            "ref_audio": f"./data/ref_audio.wav",
                            "language": language,
                            "duration": item.get("audio_duration", 0),
                            "speaker_id": item.get("speaker_id", ""),
                        }
                        entries.append(entry)

                offset += current_batch
                print(f"  Fetched {len(entries)} samples so far...")

            except Exception as e:
                print(f"  Error in batch: {e}")
                break

        # Create language config
        config = {
            "language": language,
            "language_code": self.languages[language],
            "sample_count": len(entries),
            "source": "facebook/multilingual_librispeech",
            "split": split,
        }

        # Write manifest
        manifest_path = output_path / "train.jsonl"
        with open(manifest_path, "w") as f:
            for entry in entries:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")

        # Write config
        config_path = output_path / "language_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Exported {len(entries)} samples to {output_path}")
        return output_path

    def create_multilingual_dataset(
        self,
        languages: List[str],
        output_dir: str,
        samples_per_lang: int = 100,
    ):
        """Create a multilingual dataset from multiple languages."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nCreating multilingual dataset:")
        print(f"  Languages: {languages}")
        print(f"  Samples per language: {samples_per_lang}")
        print(f"  Output: {output_path}")

        combined_manifest = []

        for lang in languages:
            if lang not in self.languages:
                print(f"⚠️  Skipping unknown language: {lang}")
                continue

            print(f"\nProcessing {lang}...")
            lang_dir = self.export_language_data(
                language=lang,
                output_dir=str(output_path),
                samples=samples_per_lang,
            )

            # Read manifest and add to combined
            manifest_path = lang_dir / "train.jsonl"
            if manifest_path.exists():
                with open(manifest_path, "r") as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        combined_manifest.append(entry)

        # Create combined manifest
        combined_manifest_path = output_path / "training_manifest.jsonl"
        with open(combined_manifest_path, "w") as f:
            for entry in combined_manifest:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")

        # Create dataset config
        config = {
            "version": "1.0",
            "source": "facebook/multilingual_librispeech",
            "description": "Multilingual LibriSpeech subset for TTS training",
            "languages": {},
            "total_samples": len(combined_manifest),
        }

        for lang in languages:
            lang_samples = sum(
                1 for e in combined_manifest if e.get("language") == lang
            )
            config["languages"][lang] = {
                "sample_count": lang_samples,
                "code": self.languages.get(lang, lang),
            }

        config_path = output_path / "dataset_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Multilingual dataset created!")
        print(f"   Total samples: {len(combined_manifest)}")
        print(f"   Languages: {list(config['languages'].keys())}")
        print(f"   Output: {output_path}")

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Integrate Multilingual LibriSpeech for TTS training"
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available languages",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Get dataset information",
    )
    parser.add_argument(
        "--sample",
        "-s",
        help="Sample data from a language (e.g., 'dutch')",
    )
    parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        default=["dutch", "english", "french", "spanish"],
        help="Languages to include (default: dutch english french spanish)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./multilingual_librispeech",
        help="Output directory",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Samples per language",
    )

    args = parser.parse_args()

    integration = MultilingualLibriSpeechIntegration()

    if args.list_languages:
        integration.list_available_languages()

    if args.info:
        integration.get_dataset_info()

    if args.sample:
        integration.sample_language_data(args.sample)

    if args.languages:
        integration.create_multilingual_dataset(
            languages=args.languages,
            output_dir=args.output,
            samples_per_lang=args.samples,
        )


if __name__ == "__main__":
    main()
