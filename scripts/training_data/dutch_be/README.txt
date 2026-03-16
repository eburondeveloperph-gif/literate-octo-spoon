# Dutch (Flemish) Training Data for Eburon TTS

## Setup Instructions

1. Download audio files from JW.org (nl-be)
   - Go to jw.org > Publications > Audio
   - Search for "Dutch (Flemish)" 
   - Download "Good News" (Beginner) or "Learn From" (Intermediate) audio

2. Place audio files in this directory:
   /Users/master/vbox/echovoice/scripts/training_data/dutch_be/

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

## Language Code: nl-be

This directory is used by Eburon TTS for native Dutch (Flemish) voice synthesis.
