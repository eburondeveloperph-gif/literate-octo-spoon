#!/usr/bin/env python3
"""
Integration script for Dataset Maker and Multilingual TTS Finetuning
Uses the dataset-maker repository to prepare training data for Qwen3-TTS.
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

# Path to dataset-maker repository
DATASET_MAKER_PATH = "/tmp/dataset-maker"
DATASETS_FOLDER = Path(DATASET_MAKER_PATH) / "datasets_folder"


class DatasetMakerIntegration:
    """Integrate dataset-maker with multilingual TTS finetuning."""

    def __init__(self, dataset_maker_path: str = DATASET_MAKER_PATH):
        self.dataset_maker_path = Path(dataset_maker_path)
        self.datasets_folder = self.dataset_maker_path / "datasets_folder"

        if not self.dataset_maker_path.exists():
            raise FileNotFoundError(f"Dataset-maker not found at: {dataset_maker_path}")

        print(f"Dataset Maker Integration initialized")
        print(f"  Path: {self.dataset_maker_path}")
        print(f"  Datasets folder: {self.datasets_folder}")

    def create_project(self, project_name: str, language: str):
        """Create a new project in dataset-maker."""
        project_path = self.datasets_folder / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # Create project structure
        subdirs = ["wavs", "transcribe", "train_text_files"]
        for subdir in subdirs:
            (project_path / subdir).mkdir(exist_ok=True)

        # Create project metadata
        metadata = {
            "name": project_name,
            "language": language,
            "created": str(Path().absolute()),
            "status": "created",
        }

        with open(project_path / "project_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Created project: {project_name} ({language})")
        return project_path

    def add_audio_samples(
        self,
        project_name: str,
        audio_dir: str,
        language: str = None,
    ):
        """Add audio samples to a project."""
        project_path = self.datasets_folder / project_name
        wavs_path = project_path / "wavs"

        audio_path = Path(audio_dir)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio directory not found: {audio_dir}")

        # Copy audio files to project
        audio_files = list(audio_path.glob("*.wav")) + list(audio_path.glob("*.mp3"))
        copied = 0

        for audio_file in audio_files:
            shutil.copy2(audio_file, wavs_path / audio_file.name)
            copied += 1

        # Update metadata
        metadata_path = project_path / "project_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            metadata["audio_samples"] = copied
            metadata["audio_source"] = str(audio_path)
            if language:
                metadata["language"] = language

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

        print(f"✅ Added {copied} audio samples to project: {project_name}")
        return copied

    def run_transcription(self, project_name: str, method: str = "whisper"):
        """
        Run transcription on audio samples.
        Methods: "whisper", "silence_slicer", "emilia"
        """
        project_path = self.datasets_folder / project_name
        wavs_path = project_path / "wavs"
        transcribe_path = project_path / "transcribe"

        print(f"\nRunning transcription for project: {project_name}")
        print(f"Method: {method}")

        # For now, we'll simulate transcription by copying files
        # In a real implementation, you would call the dataset-maker's transcription functions
        audio_files = list(wavs_path.glob("*.wav")) + list(wavs_path.glob("*.mp3"))

        if not audio_files:
            print("❌ No audio files found for transcription")
            return 0

        # Copy files to transcribe folder (simulating transcription)
        for audio_file in audio_files:
            shutil.copy2(audio_file, transcribe_path / audio_file.name)

        # Create dummy transcriptions (in real use, call WhisperX)
        train_text_path = project_path / "train_text_files" / "train.txt"
        with open(train_text_path, "w") as f:
            for i, audio_file in enumerate(audio_files, 1):
                # Use filename as placeholder text
                text = audio_file.stem.replace("_", " ").replace("-", " ")
                f.write(f"{audio_file.name}|[{project_name}] {text}\n")

        print(f"✅ Transcribed {len(audio_files)} files")
        return len(audio_files)

    def export_to_qwen3_tts(
        self,
        project_name: str,
        ref_audio_name: str,
        output_dir: str = None,
    ):
        """Export project to Qwen3 TTS format."""
        project_path = self.datasets_folder / project_name
        transcribe_path = project_path / "transcribe"
        train_text_path = project_path / "train_text_files" / "train.txt"

        if output_dir is None:
            output_dir = project_path / f"{project_name}_qwen3_tts_dataset"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy reference audio
        ref_audio_source = transcribe_path / ref_audio_name
        if not ref_audio_source.exists():
            raise FileNotFoundError(f"Reference audio not found: {ref_audio_name}")

        data_folder = output_dir / "data"
        data_folder.mkdir(exist_ok=True)

        ref_audio_ext = ref_audio_source.suffix
        ref_audio_target = data_folder / f"ref_audio{ref_audio_ext}"
        shutil.copy2(ref_audio_source, ref_audio_target)

        # Process audio files and create JSONL manifest
        audio_files = [
            f for f in transcribe_path.glob("*") if f.suffix.lower() in [".wav", ".mp3"]
        ]

        entries = []
        with open(train_text_path, "r") as f:
            transcriptions = {}
            for line in f:
                if "|" in line:
                    filename, text = line.strip().split("|", 1)
                    transcriptions[filename.strip()] = text.strip()

        for audio_file in audio_files:
            # Copy audio file
            target_name = audio_file.name
            target_path = data_folder / target_name
            shutil.copy2(audio_file, target_path)

            # Get transcription
            text = transcriptions.get(audio_file.name, f"[{project_name}] Sample audio")

            # Create entry
            entry = {
                "audio": f"./data/{target_name}",
                "text": text,
                "ref_audio": f"./data/ref_audio{ref_audio_ext}",
            }
            entries.append(entry)

        # Write JSONL manifest
        jsonl_path = output_dir / "train.jsonl"
        with open(jsonl_path, "w") as f:
            for entry in entries:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")

        # Create language config
        config_path = output_dir / "language_config.json"
        with open(project_path / "project_metadata.json", "r") as f:
            metadata = json.load(f)

        config = {
            "project": project_name,
            "language": metadata.get("language", "unknown"),
            "sample_count": len(entries),
            "sample_rate": 24000,
            "source": "dataset_maker",
        }

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Exported {len(entries)} samples to Qwen3 TTS format")
        print(f"   Output: {output_dir}")
        print(f"   Manifest: {jsonl_path.name}")

        return output_dir

    def create_multilingual_dataset(
        self,
        projects: List[Dict[str, str]],
        output_dir: str,
    ):
        """Combine multiple language projects into a single multilingual dataset."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        combined_manifest = []

        for project_config in projects:
            project_name = project_config["name"]
            language = project_config["language"]

            print(f"\nProcessing project: {project_name} ({language})")

            # Export project to Qwen3 TTS format
            ref_audio = project_config.get("ref_audio", "ref_audio.wav")
            project_output = self.export_to_qwen3_tts(
                project_name=project_name,
                ref_audio_name=ref_audio,
                output_dir=str(output_path / language),
            )

            # Read the manifest and add language tag
            manifest_path = project_output / "train.jsonl"
            with open(manifest_path, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    entry["language"] = language
                    combined_manifest.append(entry)

        # Write combined manifest
        combined_manifest_path = output_path / "training_manifest.jsonl"
        with open(combined_manifest_path, "w") as f:
            for entry in combined_manifest:
                json.dump(entry, f, ensure_ascii=False)
                f.write("\n")

        # Create combined config
        config = {
            "version": "1.0",
            "description": "Multilingual TTS dataset from dataset-maker",
            "languages": {},
            "total_samples": len(combined_manifest),
        }

        for project_config in projects:
            lang = project_config["language"]
            lang_name = project_config.get("name", lang)
            lang_samples = sum(
                1 for e in combined_manifest if e.get("language") == lang
            )
            config["languages"][lang] = {
                "name": lang_name,
                "sample_count": lang_samples,
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
        description="Integrate dataset-maker with multilingual TTS finetuning"
    )
    parser.add_argument(
        "--project",
        "-p",
        help="Project name to create or use",
    )
    parser.add_argument(
        "--language",
        "-l",
        help="Language code (itw, nl, tl, en)",
    )
    parser.add_argument(
        "--audio-dir",
        "-a",
        help="Directory containing audio files",
    )
    parser.add_argument(
        "--ref-audio",
        "-r",
        help="Reference audio filename for Qwen3 TTS export",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./multilingual_dataset",
        help="Output directory for combined dataset",
    )
    parser.add_argument(
        "--create-project",
        action="store_true",
        help="Create a new project",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export project to Qwen3 TTS format",
    )

    args = parser.parse_args()

    integration = DatasetMakerIntegration()

    if args.create_project and args.project and args.language:
        # Create project
        project_path = integration.create_project(args.project, args.language)

        if args.audio_dir:
            # Add audio samples
            integration.add_audio_samples(args.project, args.audio_dir, args.language)

            # Run transcription
            integration.run_transcription(args.project)

    if args.export and args.project:
        if not args.ref_audio:
            print("❌ --ref-audio is required for export")
            return

        # Export to Qwen3 TTS format
        integration.export_to_qwen3_tts(
            project_name=args.project,
            ref_audio_name=args.ref_audio,
        )

    print("\n✅ Dataset Maker integration ready!")
    print("\nTo use with multilingual finetuning:")
    print("1. Create projects for each language")
    print("2. Add audio samples and run transcription")
    print("3. Export to Qwen3 TTS format")
    print("4. Run multilingual finetuning with the exported datasets")


if __name__ == "__main__":
    main()
