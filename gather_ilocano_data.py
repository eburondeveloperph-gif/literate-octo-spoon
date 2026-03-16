"""
Gather Ilocano (Iloko) training data for TTS finetuning.
Uses JW.org API to fetch audio and corresponding text.

Ilocano (ISO 639-3: ilo) is spoken in Northern Luzon, Philippines.
"""

import os
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
import time

# Ilocano language codes
LANG_CODE = "ilo"  # ISO 639-3
JW_LANG_CODE = "ilo"  # JW.org uses 'ilo' for Ilocano


def get_available_publications(lang="ilo"):
    """Fetch available publications in Ilocano from JW.org."""
    try:
        # Bible publications
        api_url = f"https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS?output=json&pub=nwt&langwritten={lang}"
        response = requests.get(api_url, timeout=30)
        data = response.json()

        if data.get("files", {}).get(lang):
            print(f"Found Ilocano Bible content")
            return True

        # Try alternative publications
        pubs_to_try = ["nwtsty", "bi12", "bi6", "br", "fy"]
        for pub in pubs_to_try:
            api_url = f"https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS?output=json&pub={pub}&langwritten={lang}"
            try:
                response = requests.get(api_url, timeout=30)
                data = response.json()
                if data.get("files", {}).get(lang):
                    print(f"Found Ilocano publication: {pub}")
                    return True
            except:
                continue

        return False
    except Exception as e:
        print(f"Error checking publications: {e}")
        return False


def get_book_audio_and_text(book_num, chapter_num, lang="ilo"):
    """
    Fetch audio URL and text for a Bible book/chapter in Ilocano.

    Args:
        book_num: Bible book number (1 = Genesis, etc.)
        chapter_num: Chapter number
        lang: Language code

    Returns:
        Tuple of (audio_url, text) or (None, None) if not found
    """
    # Get audio from JW.org API
    # Try different publication codes
    pubs_to_try = ["nwt", "nwtsty", "bi12"]
    audio_url = None

    for pub in pubs_to_try:
        api_url = f"https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS?pub={pub}&langwritten={lang}&fileformat=MP3&booknum={book_num}&track={chapter_num}&output=json"
        try:
            response = requests.get(api_url, timeout=30)
            data = response.json()
            files = data.get("files", {}).get(lang, {}).get("MP3", [])
            for f in files:
                url = f.get("file", {}).get("url")
                if url:
                    audio_url = url
                    break
            if audio_url:
                break
        except Exception as e:
            print(f"  Error fetching audio for {pub}: {e}")
            continue

    # Get text from WOL
    # WOL URL for Ilocano may use different path
    wol_urls = [
        f"https://wol.jw.org/{lang}/wol/b/r27/lp-tl/nwt/{book_num}/{chapter_num}",
        f"https://wol.jw.org/en/wol/b/r1/lp-e/nwt/{book_num}/{chapter_num}",  # Fallback to English
    ]

    text = None
    for wol_url in wol_urls:
        try:
            response = requests.get(wol_url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")

            # Try different verse extraction patterns
            verses = soup.find_all("span", class_="v")
            if verses:
                text_parts = []
                for v in verses:
                    for a in v.find_all("a"):
                        a.decompose()
                    text_parts.append(v.get_text().strip())
                text = " ".join(text_parts)
                break

            # Alternative: look for paragraph content
            paragraphs = soup.find_all("p", class_="sb")
            if paragraphs:
                text = " ".join([p.get_text().strip() for p in paragraphs])
                break
        except Exception as e:
            print(f"  Error fetching text: {e}")
            continue

    return audio_url, text


def prepare_ilocano_dataset(output_dir="finetune_data/ilocano", num_chapters=5):
    """
    Gather Ilocano data and save in JSONL format for TTS finetuning.

    Args:
        output_dir: Directory to save data
        num_chapters: Number of chapters to collect
    """
    data_dir = Path(output_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    audio_dir = data_dir / "audio"
    audio_dir.mkdir(exist_ok=True)

    jsonl_entries = []

    print(f"Starting Ilocano data collection...")
    print(f"Checking for Ilocano content on JW.org...")

    available = get_available_publications(JW_LANG_CODE)
    if not available:
        print("WARNING: Ilocano content may not be available on JW.org")
        print("Will attempt to collect data anyway...")

    # Books to try (Genesis, Psalms, Matthew have good content)
    books_to_try = [
        (1, "Genesis"),  # Book 1
        (19, "Psalms"),  # Book 19
        (40, "Matthew"),  # Book 40
    ]

    collected = 0

    for book_num, book_name in books_to_try:
        if collected >= num_chapters:
            break

        print(f"\nProcessing {book_name}...")

        for chapter in range(1, min(num_chapters + 1, 51)):  # Max 50 chapters
            if collected >= num_chapters:
                break

            print(f"  Chapter {chapter}...")

            try:
                audio_url, text = get_book_audio_and_text(
                    book_num, chapter, JW_LANG_CODE
                )

                if not audio_url:
                    print(f"    Skipping: No audio found")
                    continue

                # Download audio
                audio_path = audio_dir / f"{book_name.lower()}_{chapter}.mp3"
                if not audio_path.exists():
                    print(f"    Downloading audio...")
                    r = requests.get(audio_url, timeout=60)
                    r.raise_for_status()
                    with open(audio_path, "wb") as f:
                        f.write(r.content)

                # Skip if no text (will need manual transcription)
                if not text:
                    print(f"    WARNING: No text found - may need manual transcription")
                    # Still keep audio for potential manual transcription
                    text = (
                        f"[MANUAL TRANSCRIPTION NEEDED: {book_name} Chapter {chapter}]"
                    )

                entry = {
                    "audio": str(audio_path.absolute()),
                    "text": text,
                    "language": "Ilocano",
                    "source": "JW.org",
                    "book": book_name,
                    "chapter": chapter,
                }
                jsonl_entries.append(entry)
                collected += 1
                print(f"    ✓ Collected ({collected}/{num_chapters})")

                # Be polite to the server
                time.sleep(1)

            except Exception as e:
                print(f"    Error: {e}")
                continue

    # Save to JSONL
    if jsonl_entries:
        output_file = data_dir / "ilocano_dataset.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for entry in jsonl_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        print(f"\n✓ Ilocano data collection complete!")
        print(f"  Saved {len(jsonl_entries)} entries to {output_file}")
        print(f"  Audio files: {audio_dir}")

        if any("[MANUAL TRANSCRIPTION NEEDED]" in e["text"] for e in jsonl_entries):
            print(f"\n⚠️  Some entries need manual transcription.")
            print(f"   Edit the JSONL file to add correct Ilocano text.")
    else:
        print("\n❌ No Ilocano data collected. Check JW.org availability.")

    return jsonl_entries


if __name__ == "__main__":
    print("=" * 50)
    print("Ilocano TTS Finetune Data Collector")
    print("=" * 50)
    print()
    print("Ilocano (Iloko) is a language spoken in Northern Luzon,")
    print("Philippines. This script collects audio-text pairs from")
    print("JW.org for TTS model finetuning.")
    print()

    entries = prepare_ilocano_dataset(
        output_dir="finetune_data/ilocano", num_chapters=10
    )

    if entries:
        print(f"\n📝 Sample entry:")
        print(json.dumps(entries[0], indent=2, ensure_ascii=False))
