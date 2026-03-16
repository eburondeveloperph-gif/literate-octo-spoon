"""
Script to import generated voice presets into the database.
"""
import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime

def import_presets():
    """
    Import generated voice presets into the SQLite database.
    This script assumes that generate_preset_profiles.py has been run
    and data/voices/config.json and .wav files exist.
    """
    # Paths
    project_root = Path(__file__).parent.parent
    config_path = project_root / "data" / "voices" / "config.json"
    db_path = project_root / "data" / "voicebox.db"

    if not config_path.exists():
        print(f"Error: {config_path} not found. Run generate_preset_profiles.py first.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not config:
        print("No voices found in config.json")
        return

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get default channel ID
    cursor.execute("SELECT id FROM audio_channels WHERE is_default = 1 LIMIT 1")
    row = cursor.fetchone()
    default_channel_id = row[0] if row else None

    if not default_channel_id:
        print("Warning: Default audio channel not found. "
              "Profiles will not be assigned to a channel.")

    imported_count = 0
    for data in config.values():
        lang_code = data["language_code"]
        lang_name = data["language_name"]
        audio_path = data["reference_audio"]
        reference_text = data["reference_text"]

        # Check if profile already exists for this language preset
        profile_name = f"{lang_name} (Preset)"
        cursor.execute("SELECT id FROM profiles WHERE name = ?", (profile_name,))
        existing_profile = cursor.fetchone()

        if existing_profile:
            profile_id = existing_profile[0]
            print(f"Profile for {lang_name} already exists. Updating sample...")
        else:
            profile_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO profiles (id, name, description, language, "
                "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (profile_id, profile_name, f"System preset for {lang_name}",
                 lang_code, now, now)
            )

            # Map to default channel
            if default_channel_id:
                cursor.execute(
                    "INSERT OR IGNORE INTO profile_channel_mappings "
                    "(profile_id, channel_id) VALUES (?, ?)",
                    (profile_id, default_channel_id)
                )

        # Add or update sample
        # We delete old samples for this preset profile to keep it clean
        cursor.execute("DELETE FROM profile_samples WHERE profile_id = ?", (profile_id,))

        sample_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO profile_samples (id, profile_id, audio_path, "
            "reference_text) VALUES (?, ?, ?, ?)",
            (sample_id, profile_id, audio_path, reference_text)
        )

        imported_count += 1
        if imported_count % 10 == 0:
            print(f"Imported {imported_count} voices...")

    conn.commit()
    conn.close()
    print(f"\nSuccessfully imported {imported_count} voice presets into the database.")

if __name__ == "__main__":
    import_presets()
