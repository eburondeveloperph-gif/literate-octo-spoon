#!/usr/bin/env python3
"""
Prepare multilingual TTS dataset using Dataset Maker Integration
This script automates the process of creating training data for multilingual TTS.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Optional, List
from dataset_maker_integration import DatasetMakerIntegration

# Language configurations
# Mapping from language code to directory name
LANGUAGE_CONFIGS = {
    "itw": {
        "name": "Itawit",
        "dir_name": "itawit",
        "ref_audio": "ref.wav",
    },
    "nl": {
        "name": "Dutch (Flemish)",
        "dir_name": "dutch_be",
        "ref_audio": "ref.wav",
    },
    "tl": {
        "name": "Tagalog",
        "dir_name": "tagalog",
        "ref_audio": "ref.wav",
    },
    "en": {
        "name": "English",
        "dir_name": "english",
        "ref_audio": "ref.wav",
    },
}


def prepare_multilingual_dataset(
    languages: Optional[List[str]] = None,
    output_dir: str = "./multilingual_dataset",
    use_existing: bool = False,
):
    """
    Prepare multilingual dataset from training data.
    """
    if languages is None:
        languages = ["itw", "nl", "tl"]

    integration = DatasetMakerIntegration()
    script_dir = Path(__file__).parent
    # Training data is in scripts/training_data
    training_data_dir = script_dir / "training_data"

    print("=" * 60)
    print("Preparing Multilingual TTS Dataset")
    print("=" * 60)
    print(f"Languages: {languages}")
    print(f"Output: {output_dir}")
    print()

    projects = []

    for lang_code in languages:
        if lang_code not in LANGUAGE_CONFIGS:
            print(f"⚠️  Warning: Language {lang_code} not configured, skipping")
            continue

        config = LANGUAGE_CONFIGS[lang_code]
        project_name = f"tts_{lang_code}"

        print(f"Processing {config['name']} ({lang_code})...")

        # Check if audio directory exists
        audio_dir = training_data_dir / config["dir_name"] / "segments"
        if not audio_dir.exists():
            print(f"  ❌ Audio directory not found: {audio_dir}")
            print(f"     Expected: {config['dir_name']}/segments")
            continue

        # Check if reference audio exists
        ref_audio_path = training_data_dir / config["dir_name"] / config["ref_audio"]
        if not ref_audio_path.exists():
            print(f"  ⚠️  Reference audio not found: {ref_audio_path}")
            print(f"     Using first audio file as reference")

        # Create project
        project_path = integration.create_project(project_name, lang_code)

        # Add audio samples
        sample_count = integration.add_audio_samples(
            project_name=project_name,
            audio_dir=str(audio_dir),
            language=lang_code,
        )

        if sample_count > 0:
            # Run transcription
            integration.run_transcription(project_name)

            # Export to Qwen3 TTS format
            # Use first available audio file as reference if ref.wav doesn't exist
            transcribe_dir = project_path / "transcribe"
            if transcribe_dir.exists() and any(transcribe_dir.iterdir()):
                ref_audio = sorted(transcribe_dir.iterdir())[0].name
            elif ref_audio_path.exists():
                ref_audio = config["ref_audio"]
            else:
                print(f"  ⚠️  No audio files found for reference")
                continue

            integration.export_to_qwen3_tts(
                project_name=project_name,
                ref_audio_name=ref_audio,
                output_dir=str(Path(output_dir) / lang_code),
            )
            integration.export_to_qwen3_tts(
                project_name=project_name,
                ref_audio_name=ref_audio,
                output_dir=str(Path(output_dir) / lang_code),
            )

            # Add to projects list
            projects.append(
                {
                    "name": project_name,
                    "language": lang_code,
                    "ref_audio": ref_audio,
                }
            )

            print(f"  ✅ Completed: {sample_count} samples")
        else:
            print(f"  ⚠️  No samples found")

    # Create combined multilingual dataset
    if projects:
        print("\n" + "=" * 60)
        print("Creating combined multilingual dataset...")
        print("=" * 60)

        combined_output = integration.create_multilingual_dataset(
            projects=projects,
            output_dir=output_dir,
        )

        # Create Kaggle-ready dataset
        create_kaggle_dataset(combined_output, languages)

        print("\n" + "=" * 60)
        print("✅ Dataset preparation complete!")
        print("=" * 60)
        print(f"Output directory: {combined_output}")
        print(f"Total projects: {len(projects)}")
        print()
        print("Next steps:")
        print("1. Review the dataset in the output directory")
        print("2. Upload to Kaggle for finetuning")
        print("3. Run the finetuning notebook")
    else:
        print("\n❌ No projects were created. Check the training data directories.")


def create_kaggle_dataset(dataset_path: Path, languages: list):
    """Create Kaggle dataset metadata."""
    kaggle_metadata = {
        "title": "Multilingual TTS Training Dataset",
        "id": "eburon/multilingual-tts-dataset",
        "description": "Training dataset for finetuning Qwen3-TTS 0.6B model with multilingual support",
        "licenses": [{"name": "CC-BY-4.0"}],
        "resources": [
            {
                "path": "dataset_config.json",
                "description": "Dataset configuration and statistics",
            },
            {
                "path": "training_manifest.jsonl",
                "description": "Training data manifest in JSONL format",
            },
        ],
    }

    with open(dataset_path / "kaggle-metadata.json", "w") as f:
        json.dump(kaggle_metadata, f, indent=2)

    # Also copy language-specific configs
    for lang in languages:
        lang_dir = dataset_path / lang
        if lang_dir.exists():
            config_path = lang_dir / "language_config.json"
            if config_path.exists():
                kaggle_metadata["resources"].append(
                    {
                        "path": f"{lang}/language_config.json",
                        "description": f"{LANGUAGE_CONFIGS[lang]['name']} configuration",
                    }
                )

    with open(dataset_path / "kaggle-metadata.json", "w") as f:
        json.dump(kaggle_metadata, f, indent=2)

    print(f"✅ Kaggle metadata created")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare multilingual TTS dataset from training data"
    )
    parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        default=["itw", "nl", "tl"],
        help="Languages to include (default: itw nl tl)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./multilingual_dataset",
        help="Output directory for the dataset",
    )
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Use existing projects if they exist",
    )

    args = parser.parse_args()

    prepare_multilingual_dataset(
        languages=args.languages,
        output_dir=args.output,
        use_existing=args.use_existing,
    )


if __name__ == "__main__":
    main()
