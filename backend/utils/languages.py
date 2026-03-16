"""
Language mapping and validation utilities.
"""

from typing import Dict, List, Optional, Tuple

# Full list of supported languages from the frontend
# Maps language code to display name
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "zh": "Chinese",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "de": "German",
    "fr": "French",
    "ru": "Russian",
    "pt": "Portuguese",
    "es": "Spanish",
    "it": "Italian",
    "flemish": "Flemish",
    "abkhaz": "Abkhaz",
    "acehnese": "Acehnese",
    "acholi": "Acholi",
    "afar": "Afar",
    "afrikaans": "Afrikaans",
    "albanian": "Albanian",
    "alur": "Alur",
    "amharic": "Amharic",
    "arabic": "Arabic",
    "armenian": "Armenian",
    "assamese": "Assamese",
    "avar": "Avar",
    "awadhi": "Awadhi",
    "aymara": "Aymara",
    "azerbaijani": "Azerbaijani",
    "balinese": "Balinese",
    "baluchi": "Baluchi",
    "bambara": "Bambara",
    "baoule": "Baoulé",
    "bashkir": "Bashkir",
    "basque": "Basque",
    "batak_karo": "Batak Karo",
    "batak_simalungun": "Batak Simalungun",
    "batak_toba": "Batak Toba",
    "belarusian": "Belarusian",
    "bemba": "Bemba",
    "bengali": "Bengali",
    "betawi": "Betawi",
    "bhojpuri": "Bhojpuri",
    "bikol": "Bikol",
    "bosnian": "Bosnian",
    "breton": "Breton",
    "bulgarian": "Bulgarian",
    "buryat": "Buryat",
    "cantonese": "Cantonese",
    "catalan": "Catalan",
    "cebuano": "Cebuano",
    "chamorro": "Chamorro",
    "chechen": "Chechen",
    "chichewa": "Chichewa",
    "chinese_simplified": "Chinese (Simplified)",
    "chinese_traditional": "Chinese (Traditional)",
    "chuukese": "Chuukese",
    "chuvash": "Chuvash",
    "corsican": "Corsican",
    "crimean_tatar_cyrillic": "Crimean Tatar (Cyrillic)",
    "crimean_tatar_latin": "Crimean Tatar (Latin)",
    "croatian": "Croatian",
    "czech": "Czech",
    "danish": "Danish",
    "dari": "Dari",
    "dhivehi": "Dhivehi",
    "dinka": "Dinka",
    "dogri": "Dogri",
    "dombe": "Dombe",
    "dutch": "Dutch",
    "dyula": "Dyula",
    "dzongkha": "Dzongkha",
    "esperanto": "Esperanto",
    "estonian": "Estonian",
    "ewe": "Ewe",
    "faroese": "Faroese",
    "fijian": "Fijian",
    "filipino": "Filipino",
    "finnish": "Finnish",
    "fon": "Fon",
    "french_canada": "French (Canada)",
    "frisian": "Frisian",
    "friulian": "Friulian",
    "fulani": "Fulani",
    "ga": "Ga",
    "galician": "Galician",
    "georgian": "Georgian",
    "greek": "Greek",
    "guarani": "Guarani",
    "gujarati": "Gujarati",
    "haitian_creole": "Haitian Creole",
    "hakha_chin": "Hakha Chin",
    "hausa": "Hausa",
    "hawaiian": "Hawaiian",
    "hebrew": "Hebrew",
    "hiligaynon": "Hiligaynon",
    "hindi": "Hindi",
    "hmong": "Hmong",
    "hungarian": "Hungarian",
    "hunsrik": "Hunsrik",
    "iban": "Iban",
    "icelandic": "Icelandic",
    "igbo": "Igbo",
    "ilocano": "Ilocano",
    "indonesian": "Indonesian",
    "inuktut_latin": "Inuktut (Latin)",
    "inuktut_syllabics": "Inuktut (Syllabics)",
    "irish": "Irish",
    "jamaican_patois": "Jamaican Patois",
    "javanese": "Javanese",
    "jingpo": "Jingpo",
    "kalaallisut": "Kalaallisut",
    "kannada": "Kannada",
    "kanuri": "Kanuri",
    "kapampangan": "Kapampangan",
    "kazakh": "Kazakh",
    "khasi": "Khasi",
    "khmer": "Khmer",
    "kiga": "Kiga",
    "kikongo": "Kikongo",
    "kinyarwanda": "Kinyarwanda",
    "kituba": "Kituba",
    "kokborok": "Kokborok",
    "komi": "Komi",
    "konkani": "Konkani",
    "krio": "Krio",
    "kurdish_kurmanji": "Kurdish (Kurmanji)",
    "kurdish_sorani": "Kurdish (Sorani)",
    "kyrgyz": "Kyrgyz",
    "lao": "Lao",
    "latgalian": "Latgalian",
    "latin": "Latin",
    "latvian": "Latvian",
    "ligurian": "Ligurian",
    "limburgish": "Limburgish",
    "lingala": "Lingala",
    "lithuanian": "Lithuanian",
    "lombard": "Lombard",
    "luganda": "Luganda",
    "luo": "Luo",
    "luxembourgish": "Luxembourgish",
    "macedonian": "Macedonian",
    "madurese": "Madurese",
    "maithili": "Maithili",
    "makassar": "Makassar",
    "malagasy": "Malagasy",
    "malay": "Malay",
    "malay_jawi": "Malay (Jawi)",
    "malayalam": "Malayalam",
    "maltese": "Maltese",
    "mam": "Mam",
    "manx": "Manx",
    "maori": "Maori",
    "marathi": "Marathi",
    "marshallese": "Marshallese",
    "marwadi": "Marwadi",
    "mauritian_creole": "Mauritian Creole",
    "meadow_mari": "Meadow Mari",
    "meiteilon_manipuri": "Meiteilon (Manipuri)",
    "minang": "Minang",
    "mizo": "Mizo",
    "mongolian": "Mongolian",
    "myanmar_burmese": "Myanmar (Burmese)",
    "nahuatl_eastern_huasteca": "Nahuatl (Eastern Huasteca)",
    "ndau": "Ndau",
    "ndebele_south": "Ndebele (South)",
    "nepalbhasa_newari": "Nepalbhasa (Newari)",
    "nepali": "Nepali",
    "nko": "NKo",
    "norwegian": "Norwegian",
    "nuer": "Nuer",
    "occitan": "Occitan",
    "odia_oriya": "Odia (Oriya)",
    "oromo": "Oromo",
    "ossetian": "Ossetian",
    "pangasinan": "Pangasinan",
    "papiamento": "Papiamento",
    "pashto": "Pashto",
    "persian": "Persian",
    "polish": "Polish",
    "portuguese_brazil": "Portuguese (Brazil)",
    "portuguese_portugal": "Portuguese (Portugal)",
    "punjabi_gurmukhi": "Punjabi (Gurmukhi)",
    "punjabi_shahmukhi": "Punjabi (Shahmukhi)",
    "quechua": "Quechua",
    "q_eqchi": "Qʼeqchiʼ",
    "romani": "Romani",
    "romanian": "Romanian",
    "rundi": "Rundi",
    "sami_north": "Sami (North)",
    "samoan": "Samoan",
    "sango": "Sango",
    "sanskrit": "Sanskrit",
    "santali_latin": "Santali (Latin)",
    "santali_ol_chiki": "Santali (Ol Chiki)",
    "scots_gaelic": "Scots Gaelic",
    "sepedi": "Sepedi",
    "serbian": "Serbian",
    "sesotho": "Sesotho",
    "seychellois_creole": "Seychellois Creole",
    "shan": "Shan",
    "shona": "Shona",
    "sicilian": "Sicilian",
    "silesian": "Silesian",
    "sindhi": "Sindhi",
    "sinhala": "Sinhala",
    "slovak": "Slovak",
    "slovenian": "Slovenian",
    "somali": "Somali",
    "sundanese": "Sundanese",
    "susu": "Susu",
    "swahili": "Swahili",
    "swati": "Swati",
    "swedish": "Swedish",
    "tahitian": "Tahitian",
    "tajik": "Tajik",
    "tamazight": "Tamazight",
    "tamazight_tifinagh": "Tamazight (Tifinagh)",
    "tamil": "Tamil",
    "tatar": "Tatar",
    "telugu": "Telugu",
    "tetum": "Tetum",
    "thai": "Thai",
    "tibetan": "Tibetan",
    "tigrinya": "Tigrinya",
    "tiv": "Tiv",
    "tok_pisin": "Tok Pisin",
    "tongan": "Tongan",
    "tshiluba": "Tshiluba",
    "tsonga": "Tsonga",
    "tswana": "Tswana",
    "tulu": "Tulu",
    "tumbuka": "Tumbuka",
    "turkish": "Turkish",
    "turkmen": "Turkmen",
    "tuvan": "Tuvan",
    "twi": "Twi",
    "udmurt": "Udmurt",
    "ukrainian": "Ukrainian",
    "urdu": "Urdu",
    "uyghur": "Uyghur",
    "uzbek": "Uzbek",
    "venda": "Venda",
    "venetian": "Venetian",
    "vietnamese": "Vietnamese",
    "waray": "Waray",
    "welsh": "Welsh",
    "wolof": "Wolof",
    "xhosa": "Xhosa",
    "yakut": "Yakut",
    "yiddish": "Yiddish",
    "yoruba": "Yoruba",
    "yucatec_maya": "Yucatec Maya",
    "zapotec": "Zapotec",
    "zulu": "Zulu",
}

# Mapping of detailed language codes to base codes supported by Qwen3-TTS
# Based on officially listed best-supported languages:
# zh, en, ja, ko, de, fr, ru, pt, es, it
TTS_LANGUAGE_MAPPING: Dict[str, str] = {
    "chinese_simplified": "zh",
    "chinese_traditional": "zh",
    "cantonese": "zh",
    "french_canada": "fr",
    "portuguese_brazil": "pt",
    "portuguese_portugal": "pt",
    "spanish": "es",
}

# Mapping for Whisper STT (Speech-to-Text)
# Whisper is more flexible but ISO 639-1 codes are safest
STT_LANGUAGE_MAPPING: Dict[str, str] = {
    "chinese_simplified": "zh",
    "chinese_traditional": "zh",
    "cantonese": "zh",
    "french_canada": "fr",
    "portuguese_brazil": "pt",
    "portuguese_portugal": "pt",
    "flemish": "nl",
}


def map_to_tts_language(language_code: str) -> str:
    """
    Map a detailed language code to a code supported by the TTS model.
    
    Args:
        language_code: Detailed language code (e.g. 'chinese_simplified')
        
    Returns:
        Base language code (e.g. 'zh') or the original code if no mapping exists.
    """
    if not language_code:
        return "en"
        
    # First check explicit mapping
    if language_code in TTS_LANGUAGE_MAPPING:
        return TTS_LANGUAGE_MAPPING[language_code]
    
    # Check if it's already a base code
    base_codes = ["zh", "en", "ja", "ko", "de", "fr", "ru", "pt", "es", "it"]
    if language_code in base_codes:
        return language_code
        
    # Default: return original code and hope the model handles it,
    # or fallback to 'en' if it's not even in our supported list
    if language_code not in SUPPORTED_LANGUAGES:
        return "en"
        
    return language_code


def map_to_stt_language(language_code: Optional[str]) -> Optional[str]:
    """
    Map a detailed language code to a code supported by Whisper.
    
    Args:
        language_code: Detailed language code
        
    Returns:
        Mapped language code or None
    """
    if not language_code:
        return None
        
    if language_code in STT_LANGUAGE_MAPPING:
        return STT_LANGUAGE_MAPPING[language_code]
        
    return language_code


def validate_language_code(language_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a language code is supported.
    
    Args:
        language_code: Language code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if language_code in SUPPORTED_LANGUAGES:
        return True, None
    
    # Also allow base codes
    base_codes = ["zh", "en", "ja", "ko", "de", "fr", "ru", "pt", "es", "it"]
    if language_code in base_codes:
        return True, None
        
    return False, f"Unsupported language code: {language_code}"
