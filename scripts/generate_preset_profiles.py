"""
Script to generate synthetic voice training data and configuration for all supported languages.
Uses edge-tts to generate reference audio samples.
"""
import asyncio
import json
import os


# The complete list of languages we added
LANGUAGE_CODES = {
    "zh": "Chinese", "en": "English", "ja": "Japanese", "ko": "Korean",
    "de": "German", "fr": "French", "ru": "Russian", "pt": "Portuguese",
    "es": "Spanish", "it": "Italian", "flemish": "Flemish",
    "abkhaz": "Abkhaz", "acehnese": "Acehnese", "acholi": "Acholi",
    "afar": "Afar", "afrikaans": "Afrikaans", "albanian": "Albanian",
    "alur": "Alur", "amharic": "Amharic", "arabic": "Arabic",
    "armenian": "Armenian", "assamese": "Assamese", "avar": "Avar",
    "awadhi": "Awadhi", "aymara": "Aymara", "azerbaijani": "Azerbaijani",
    "balinese": "Balinese", "baluchi": "Baluchi", "bambara": "Bambara",
    "baoule": "Baoulé", "bashkir": "Bashkir", "basque": "Basque",
    "batak_karo": "Batak Karo", "batak_simalungun": "Batak Simalungun",
    "batak_toba": "Batak Toba", "belarusian": "Belarusian", "bemba": "Bemba",
    "bengali": "Bengali", "betawi": "Betawi", "bhojpuri": "Bhojpuri",
    "bikol": "Bikol", "bosnian": "Bosnian", "breton": "Breton",
    "bulgarian": "Bulgarian", "buryat": "Buryat", "cantonese": "Cantonese",
    "catalan": "Catalan", "cebuano": "Cebuano", "chamorro": "Chamorro",
    "chechen": "Chechen", "chichewa": "Chichewa",
    "chinese_simplified": "Chinese (Simplified)",
    "chinese_traditional": "Chinese (Traditional)", "chuukese": "Chuukese",
    "chuvash": "Chuvash", "corsican": "Corsican",
    "crimean_tatar_cyrillic": "Crimean Tatar (Cyrillic)",
    "crimean_tatar_latin": "Crimean Tatar (Latin)", "croatian": "Croatian",
    "czech": "Czech", "danish": "Danish", "dari": "Dari",
    "dhivehi": "Dhivehi", "dinka": "Dinka", "dogri": "Dogri",
    "dombe": "Dombe", "dutch": "Dutch", "dyula": "Dyula",
    "dzongkha": "Dzongkha", "esperanto": "Esperanto", "estonian": "Estonian",
    "ewe": "Ewe", "faroese": "Faroese", "fijian": "Fijian",
    "filipino": "Filipino", "finnish": "Finnish", "fon": "Fon",
    "french_canada": "French (Canada)", "frisian": "Frisian",
    "friulian": "Friulian", "fulani": "Fulani", "ga": "Ga",
    "galician": "Galician", "georgian": "Georgian", "greek": "Greek",
    "guarani": "Guarani", "gujarati": "Gujarati",
    "haitian_creole": "Haitian Creole", "hakha_chin": "Hakha Chin",
    "hausa": "Hausa", "hawaiian": "Hawaiian", "hebrew": "Hebrew",
    "hiligaynon": "Hiligaynon", "hindi": "Hindi", "hmong": "Hmong",
    "hungarian": "Hungarian", "hunsrik": "Hunsrik", "iban": "Iban",
    "icelandic": "Icelandic", "igbo": "Igbo", "ilocano": "Ilocano",
    "indonesian": "Indonesian", "inuktut_latin": "Inuktut (Latin)",
    "inuktut_syllabics": "Inuktut (Syllabics)", "irish": "Irish",
    "jamaican_patois": "Jamaican Patois", "javanese": "Javanese",
    "jingpo": "Jingpo", "kalaallisut": "Kalaallisut", "kannada": "Kannada",
    "kanuri": "Kanuri", "kapampangan": "Kapampangan", "kazakh": "Kazakh",
    "khasi": "Khasi", "khmer": "Khmer", "kiga": "Kiga", "kikongo": "Kikongo",
    "kinyarwanda": "Kinyarwanda", "kituba": "Kituba", "kokborok": "Kokborok",
    "komi": "Komi", "konkani": "Konkani", "krio": "Krio",
    "kurdish_kurmanji": "Kurdish (Kurmanji)",
    "kurdish_sorani": "Kurdish (Sorani)", "kyrgyz": "Kyrgyz", "lao": "Lao",
    "latgalian": "Latgalian", "latin": "Latin", "latvian": "Latvian",
    "ligurian": "Ligurian", "limburgish": "Limburgish", "lingala": "Lingala",
    "lithuanian": "Lithuanian", "lombard": "Lombard", "luganda": "Luganda",
    "luo": "Luo", "luxembourgish": "Luxembourgish",
    "macedonian": "Macedonian", "madurese": "Madurese",
    "maithili": "Maithili", "makassar": "Makassar", "malagasy": "Malagasy",
    "malay": "Malay", "malay_jawi": "Malay (Jawi)",
    "malayalam": "Malayalam", "maltese": "Maltese", "mam": "Mam",
    "manx": "Manx", "maori": "Maori", "marathi": "Marathi",
    "marshallese": "Marshallese", "marwadi": "Marwadi",
    "mauritian_creole": "Mauritian Creole", "meadow_mari": "Meadow Mari",
    "meiteilon_manipuri": "Meiteilon (Manipuri)", "minang": "Minang",
    "mizo": "Mizo", "mongolian": "Mongolian",
    "myanmar_burmese": "Myanmar (Burmese)",
    "nahuatl_eastern_huasteca": "Nahuatl (Eastern Huasteca)", "ndau": "Ndau",
    "ndebele_south": "Ndebele (South)",
    "nepalbhasa_newari": "Nepalbhasa (Newari)", "nepali": "Nepali",
    "nko": "NKo", "norwegian": "Norwegian", "nuer": "Nuer",
    "occitan": "Occitan", "odia_oriya": "Odia (Oriya)", "oromo": "Oromo",
    "ossetian": "Ossetian", "pangasinan": "Pangasinan",
    "papiamento": "Papiamento", "pashto": "Pashto", "persian": "Persian",
    "polish": "Polish", "portuguese_brazil": "Portuguese (Brazil)",
    "portuguese_portugal": "Portuguese (Portugal)",
    "punjabi_gurmukhi": "Punjabi (Gurmukhi)",
    "punjabi_shahmukhi": "Punjabi (Shahmukhi)", "quechua": "Quechua",
    "q_eqchi": "Qʼeqchiʼ", "romani": "Romani", "romanian": "Romanian",
    "rundi": "Rundi", "sami_north": "Sami (North)", "samoan": "Samoan",
    "sango": "Sango", "sanskrit": "Sanskrit", "santali_latin": "Santali (Latin)",
    "santali_ol_chiki": "Santali (Ol Chiki)",
    "scots_gaelic": "Scots Gaelic", "sepedi": "Sepedi", "serbian": "Serbian",
    "sesotho": "Sesotho", "seychellois_creole": "Seychellois Creole",
    "shan": "Shan", "shona": "Shona", "sicilian": "Sicilian",
    "silesian": "Silesian", "sindhi": "Sindhi", "sinhala": "Sinhala",
    "slovak": "Slovak", "slovenian": "Slovenian", "somali": "Somali",
    "sundanese": "Sundanese", "susu": "Susu", "swahili": "Swahili",
    "swati": "Swati", "swedish": "Swedish", "tahitian": "Tahitian",
    "tajik": "Tajik", "tamazight": "Tamazight",
    "tamazight_tifinagh": "Tamazight (Tifinagh)", "tamil": "Tamil",
    "tatar": "Tatar", "telugu": "Telugu", "tetum": "Tetum", "thai": "Thai",
    "tibetan": "Tibetan", "tigrinya": "Tigrinya", "tiv": "Tiv",
    "tok_pisin": "Tok Pisin", "tongan": "Tongan", "tshiluba": "Tshiluba",
    "tsonga": "Tsonga", "tswana": "Tswana", "tulu": "Tulu",
    "tumbuka": "Tumbuka", "turkish": "Turkish", "turkmen": "Turkmen",
    "tuvan": "Tuvan", "twi": "Twi", "udmurt": "Udmurt",
    "ukrainian": "Ukrainian", "urdu": "Urdu", "uyghur": "Uyghur",
    "uzbek": "Uzbek", "venda": "Venda", "venetian": "Venetian",
    "vietnamese": "Vietnamese", "waray": "Waray", "welsh": "Welsh",
    "wolof": "Wolof", "xhosa": "Xhosa", "yakut": "Yakut",
    "yiddish": "Yiddish", "yoruba": "Yoruba",
    "yucatec_maya": "Yucatec Maya", "zapotec": "Zapotec", "zulu": "Zulu"
}

VOICE_MAPPING = {
    'zh': ('zh-CN-XiaoxiaoNeural', '你好，这是一个声音测试，我可以说中文。'),
    'en': ('en-US-AriaNeural', 'Hello, this is a voice test, I can speak English.'),
    'ja': ('ja-JP-NanamiNeural', 'こんにちは、これは音声テストです、私は日本語を話せます。'),
    'ko': ('ko-KR-SunHiNeural', '안녕하세요, 음성 테스트입니다, 저는 한국어를 할 수 있습니다.'),
    'de': ('de-DE-KatjaNeural', 'Hallo, dies ist ein Sprachtest, ich kann Deutsch sprechen.'),
    'fr': ('fr-FR-DeniseNeural', 'Bonjour, ceci est un test vocal, je peux parler français.'),
    'ru': ('ru-RU-SvetlanaNeural', 'Здравствуйте, это проверка голоса, я умею говорить по-русски.'),
    'pt': ('pt-PT-RaquelNeural', 'Olá, este é um teste de voz, eu posso falar português.'),
    'es': ('es-ES-ElviraNeural', 'Hola, esta es una prueba de voz, puedo hablar español.'),
    'it': ('it-IT-IsabellaNeural', 'Ciao, questo è un test vocale, posso parlare italiano.'),
    'afrikaans': ('af-ZA-AdriNeural', 'Hallo, dit is n stemtoets, ek kan Afrikaans praat.'),
    'albanian': ('sq-AL-AnilaNeural', 'Përshëndetje, ky është një test zëri, unë mund të flas shqip.'),
    'amharic': ('am-ET-MekdesNeural', 'ሰላም፡ ይህ የድምጽ ሙከራ ነው፡ አማርኛ መናገር እችላለሁ።'),
    'arabic': ('ar-SA-ZariyahNeural', 'مرحبًا، هذا اختبار صوتي، يمكنني التحدث باللغة العربية.'),
    'azerbaijani': ('az-AZ-BanuNeural', 'Salam, bu səs testidir, mən Azərbaycan dilində danışa bilirəm.'),
    'bengali': ('bn-BD-NabanitaNeural', 'হ্যালো, এটি একটি ভয়েস পরীক্ষা, আমি বাংলায় কথা বলতে পারি।'),
    'bosnian': ('bs-BA-VesnaNeural', 'Zdravo, ovo je test glasa, ja mogu govoriti bosanski.'),
    'bulgarian': ('bg-BG-KalinaNeural', 'Здравейте, това е гласов тест, аз мога да говоря български.'),
    'catalan': ('ca-ES-JoanaNeural', 'Hola, això és una prova de veu, puc parlar català.'),
    'chinese_simplified': ('zh-CN-XiaoxiaoNeural', '你好，这是一个声音测试，我可以说中文。'),
    'chinese_traditional': ('zh-TW-HsiaoChenNeural', '你好，這是一個聲音測試，我能說中文。'),
    'croatian': ('hr-HR-GabrijelaNeural', 'Bok, ovo je test glasa, mogu govoriti hrvatski.'),
    'czech': ('cs-CZ-VlastaNeural', 'Ahoj, toto je hlasový test, umím mluvit česky.'),
    'danish': ('da-DK-ChristelNeural', 'Hej, dette er en stemmetest, jeg kan tale dansk.'),
    'dutch': ('nl-NL-ColetteNeural', 'Hallo, dit is een stemtest, ik kan Nederlands spreken.'),
    'estonian': ('et-EE-AnuNeural', 'Tere, see on hääletest, ma oskan rääkida eesti keelt.'),
    'filipino': ('fil-PH-BlessicaNeural', 'Kamusta, ito ay isang voice test, marunong akong magsalita ng Filipino.'),
    'finnish': ('fi-FI-SelmaNeural', 'Hei, tämä on äänitesti, osaan puhua suomea.'),
    'french_canada': ('fr-CA-SylvieNeural', 'Bonjour, ceci est un test vocal, je peux parler français.'),
    'galician': ('gl-ES-SabelaNeural', 'Ola, esta é unha proba de voz, podo falar galego.'),
    'georgian': ('ka-GE-EkaNeural',
                 'გამარჯობა, ეს არის ხმის ტესტი, მე შეমিძლიا ქართულად საუბარი.'),
    'greek': ('el-GR-AthinaNeural',
              'Γεια σας, αυτό είναι ένα φωνητικό τεστ, μπορώ να μιλήσω Ελληνικά.'),
    'gujarati': ('gu-IN-DhwaniNeural',
                 'હેલો, આ અવાજ પરીક્ષણ છે, હું ગુજરાતી બોલી શકું છું.'),
    'hebrew': ('he-IL-HilaNeural', 'שלום, זו בדיקת קול, אני יכולה לדבר עברית.'),
    'hindi': ('hi-IN-SwaraNeural',
              'नमस्ते, यह एक आवाज परीक्षण है, मैं हिंदी बोल सकती हूँ।'),
    'hungarian': ('hu-HU-NoemiNeural', 'Szia, ez egy hangteszt, tudok magyarul beszélni.'),
    'icelandic': ('is-IS-GudrunNeural', 'Halló, þetta er raddpróf, ég get talað íslensku.'),
    'indonesian': ('id-ID-GadisNeural',
                   'Halo, ini adalah tes suara, saya bisa berbicara bahasa Indonesia.'),
    'irish': ('ga-IE-OrlaNeural',
              'Dia duit, is tástáil ghutha é seo, is féidir liom Gaeilge a labhairt.'),
    'javanese': ('jv-ID-SitiNeural', 'Halo, iki test swara, aku iso ngomong basa Jawa.'),
    'kannada': ('kn-IN-SapnaNeural', 'ನಮಸ್ಕಾರ, ಇದು ಧ್ವನಿ ಪರೀಕ್ಷೆ, ನಾನು ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಬಲ್ಲೆ.'),
    'kazakh': ('kk-KZ-AigulNeural',
               'Сәлем, бұл дауыс тесті, мен қазақша сөйлей аламын.'),
    'khmer': ('km-KH-SreymomNeural',
              'សួស្តី នេះគឺជាការសាកល្បងសំឡេង ខ្ញុំអាចនិយាយភាសាខ្មែរបាន។'),
    'lao': ('lo-LA-KeomanyNeural',
            'ສະບາຍດີ, ນີ້ແມ່ນການທົດສອບສຽງ, ຂ້ອຍສາມາດເວົ້າພາສາລາວໄດ້.'),
    'latvian': ('lv-LV-EveritaNeural',
                'Sveiki, šī ir balss pārbaude, es varu runāt latviski.'),
    'lithuanian': ('lt-LT-OnaNeural',
                   'Sveiki, tai balso testas, aš galiu kalbėti lietuviškai.'),
    'macedonian': ('mk-MK-MarijaNeural',
                   'Здраво, ова е тест за глас, јас можам да зборувам македонски.'),
    'malay': ('ms-MY-YasminNeural',
              'Helo, ini ujian suara, saya boleh bercakap bahasa Melayu.'),
    'malayalam': ('ml-IN-SobhanaNeural',
                  'നമസ്കാരം, ഇതൊരു ശബ്ദ പരിശോധനയാണ്, എനിക്ക് മലയാളം സംസാരിക്കാനാകും.'),
    'maltese': ('mt-MT-GraceNeural',
                'Bongu, dan huwa test tal-vuċi, nista nitkellem bil-Malti.'),
    'marathi': ('mr-IN-AarohiNeural',
                'नमस्कार, ही एक व्हॉइस टेस्ट आहे, मी मराठी बोलू शकते.'),
    'mongolian': ('mn-MN-YesuiNeural',
                  'Сайн байна уу, энэ бол дуу хоолойн тест, би монгол хэлээр ярьж чадна.'),
    'myanmar_burmese': ('my-MM-NilarNeural',
                        'မင်္ဂလာပါ၊ ဒါက အသံစမ်းသပ်မှုတစ်ခုပါ၊ ကျွန်တော် မြန်မာစကားကို ပြောတတ်ပါတယ်။'),
    'nepali': ('ne-NP-HemkalaNeural', 'नमस्ते, यो आवाज परीक्षण हो, म नेपाली बोल्न सक्छु।'),
    'norwegian': ('nb-NO-PernilleNeural', 'Hei, dette er en stemmetest, jeg kan snakke norsk.'),
    'pashto': ('ps-AF-LatifaNeural',
               'سلام، دا د غږ ازموینه ده، زه کولی شم په پښتو خبرې وکړم.'),
    'persian': ('fa-IR-DilaraNeural',
                'سلام، این یک تست صدا است، من می توانم فارسی صحبت کنم.'),
    'polish': ('pl-PL-AgnieszkaNeural', 'Cześć, to jest test głosowy, potrafię mówić po polsku.'),
    'portuguese_brazil': ('pt-BR-FranciscaNeural', 'Olá, este é um teste de voz, eu posso falar português.'),
    'portuguese_portugal': ('pt-PT-RaquelNeural',
                            'Olá, este é um teste de voz, eu posso falar português.'),
    'romanian': ('ro-RO-AlinaNeural', 'Bună, acesta este un test vocal, pot vorbi românește.'),
    'serbian': ('sr-RS-SophieNeural', 'Zdravo, ovo je test glasa, ja mogu govoriti srpski.'),
    'sinhala': ('si-LK-ThiliniNeural',
                'හෙලෝ, මෙය හඬ පරීක්ෂණයකි, මට සිංහල කතා කළ හැකිය.'),
    'slovak': ('sk-SK-ViktoriaNeural', 'Ahoj, toto je hlasový test, viem po slovensky.'),
    'slovenian': ('sl-SI-PetraNeural', 'Živjo, to je glasovni preizkus, govorim slovensko.'),
    'somali': ('so-SO-UbaxNeural',
               'Salaan, kani waa tijaabo cod, waxaan ku hadli karaa af-soomaali.'),
    'sundanese': ('su-ID-TutiNeural',
                'Halo, ieu tes sora, kuring bisa nyarita basa Sunda.'),
    'swahili': ('sw-KE-ZuriNeural',
                'Hujambo, hili ni jaribio la sauti, ninaweza kuzungumza Kiswahili.'),
    'swedish': ('sv-SE-SofieNeural', 'Hej, det här är ett rösttest, jag kan prata svenska.'),
    'tamil': ('ta-IN-PallaviNeural',
              'வணக்கம், இது ஒரு குரல் சோதனை, என்னால் தமிழ் பேச முடியும்.'),
    'telugu': ('te-IN-ShrutiNeural', 'నమస్కారం, ఇది వాయిస్ పరీక్ష, నేను తెలుగు మాట్లాడగలను.'),
    'thai': ('th-TH-PremwadeeNeural',
             'สวัสดี นี่คือการทดสอบเสียง ฉันสามารถพูดภาษาไทยได้'),
    'turkish': ('tr-TR-EmelNeural', 'Merhaba, bu bir ses testi, Türkçe konuşabiliyorum.'),
    'ukrainian': ('uk-UA-PolinaNeural', 'Привіт, це голосовий тест, я можу говорити українською.'),
    'urdu': ('ur-PK-UzmaNeural', 'ہیلو، یہ ایک آواز کا ٹیسٹ ہے، میں اردو بول سکتی ہوں۔'),
    'uzbek': ('uz-UZ-MadinaNeural',
              'Salom, bu ovoz testi, men o\'zbek tilida gapira olaman.'),
    'vietnamese': ('vi-VN-HoaiMyNeural',
                   'Xin chào, đây là một bài kiểm tra giọng nói, tôi có thể nói tiếng Việt.'),
    'welsh': ('cy-GB-NiaNeural', 'Helo, prawf llais yw hwn, gallaf siarad Cymraeg.'),
    'zulu': ('zu-ZA-ThandoNeural', 'Sawubona, lokhu kuwukuhlola izwi, ngingakwazi ukukhuluma isiZulu.')
}

async def generate_audio():
    """
    Generate audio files for each language and create a configuration mapping.
    """
    config_dict = {}

    os.makedirs('data/voices', exist_ok=True)

    for code, lang in LANGUAGE_CODES.items():
        if code in VOICE_MAPPING:
            voice_id, text = VOICE_MAPPING[code]
            filepath = f"data/voices/{code}.wav"
            print(f"Generating audio for {lang} ({code}) using {voice_id}...")
            
            # Use edge-tts directly 
            try:
                # Use -t instead of --text and ensure clean quoting
                python_path = os.getenv('PYTHONPATH', '')
                cmd = (f"export PYTHONPATH={python_path}; python3 -m edge_tts "
                       f"--voice {voice_id} -t \"{text}\" --write-media {filepath}")
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await process.communicate()
                
                if process.returncode == 0:
                    config_dict[code] = {
                        "language_code": code,
                        "language_name": lang,
                        "reference_audio": filepath,
                        "reference_text": text
                    }
                else:
                    print(f"Failed to generate {code}: {stderr.decode()}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error executing edge-tts for {code}: {e}")
        else:
            # Fallback for languages not supported by edge-tts directly
            code_fallback = 'en'
            voice_id, _ = VOICE_MAPPING[code_fallback]
            text = f"Hello, this is a simulated voice test for {lang}. I am speaking with a default voice model."
            filepath = f"data/voices/{code}.wav"
            
            print(f"Generating fallback audio for {lang} ({code}) using {voice_id}...")
            
            try:
                python_path = os.getenv('PYTHONPATH', '')
                cmd = (f"export PYTHONPATH={python_path}; python3 -m edge_tts "
                       f"--voice {voice_id} -t \"{text}\" --write-media {filepath}")
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await process.communicate()
                
                if process.returncode == 0:
                    config_dict[code] = {
                        "language_code": code,
                        "language_name": lang,
                        "reference_audio": filepath,
                        "reference_text": text
                    }
                else:
                    print(f"Failed to generate {code}: {stderr.decode()}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error executing edge-tts for {code}: {e}")
                
    # Write the config mapping file
    with open('data/voices/config.json', 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=2)
    print(f"\nSuccessfully generated config for {len(config_dict)} "
          f"languages: data/voices/config.json")

if __name__ == "__main__":
    asyncio.run(generate_audio())
