# Tagalog Training Data for Eburon TTS

## Setup Instructions

1. Download audio files from JW.org (tl)
   - Go to jw.org > Publications > Audio
   - Search for "Tagalog" 
   - Download "Good News" (Beginner) or "Learn From" (Intermediate) audio

2. Place audio files in this directory:
   /Users/master/vbox/echovoice/scripts/training_data/tagalog/

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

## Language Code: tl

This directory is used by Eburon TTS for native Tagalog voice synthesis.
