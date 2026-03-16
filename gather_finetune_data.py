import os
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup

def get_mp3_url(book_num, track_num, lang="TL"):
    """Fetch MP3 URL from JW.org API."""
    api_url = f"https://b.jw-cdn.org/apis/pub-media/GETPUBMEDIALINKS?pub=nwt&langwritten={lang}&fileformat=MP3&booknum={book_num}&track={track_num}&output=json"
    try:
        response = requests.get(api_url)
        data = response.json()
        # Find the first valid MP3 URL
        files = data.get("files", {}).get(lang, {}).get("MP3", [])
        for f in files:
            url = f.get("file", {}).get("url")
            if url:
                return url
    except Exception as e:
        print(f"Error fetching MP3 URL for track {track_num}: {e}")
    return None

def get_chapter_text(book_num, track_num, lang="tl"):
    """Fetch chapter text from WOL.JW.ORG."""
    # WOL URL pattern for Tagalog NWT
    wol_url = f"https://wol.jw.org/{lang}/wol/b/r27/lp-tg/nwt/1/{track_num}"
    try:
        response = requests.get(wol_url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Verses are usually in <span> with class 'v'
        verses = soup.find_all("span", class_="v")
        text_parts = []
        for v in verses:
            # Remove verse number (usually in a <a> inside the span)
            for a in v.find_all("a"):
                a.decompose()
            text_parts.append(v.get_text().strip())
        return " ".join(text_parts)
    except Exception as e:
        print(f"Error fetching text for chapter {track_num}: {e}")
    return None

def prepare_data(num_chapters=2):
    """Gather data and save to JSONL format for Unsloth."""
    data_dir = Path("finetune_data")
    data_dir.mkdir(exist_ok=True)
    
    audio_dir = data_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    jsonl_entries = []
    
    print(f"Starting data collection for {num_chapters} chapters...")
    
    for i in range(1, num_chapters + 1):
        print(f"Processing Genesis Chapter {i}...")
        
        # 1. Get Audio
        mp3_url = get_mp3_url(1, i)
        if not mp3_url:
            continue
            
        audio_path = audio_dir / f"genesis_{i}.mp3"
        if not audio_path.exists():
            print(f"  Downloading audio...")
            r = requests.get(mp3_url)
            with open(audio_path, "wb") as f:
                f.write(r.content)
        
        # 2. Get Text
        text = get_chapter_text(1, i)
        if not text:
            continue
            
        # 3. Create entry
        entry = {
            "audio": str(audio_path.absolute()),
            "text": text,
            "language": "Tagalog"
        }
        jsonl_entries.append(entry)
        
    # Save to JSONL
    output_file = data_dir / "dataset.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in jsonl_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"✓ Data collection complete. Saved {len(jsonl_entries)} entries to {output_file}")

if __name__ == "__main__":
    # We need requests and beautifulsoup4
    # Check if they are installed in the venv
    prepare_data(2) # Limit to 2 chapters for demo
