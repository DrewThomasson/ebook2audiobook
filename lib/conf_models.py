import os, regex as re
from lib.conf import tts_dir, voices_dir

loaded_tts = {}
xtts_builtin_speakers_list = {}

TTS_ENGINES = {
    "XTTSv2": "xtts", 
    "BARK": "bark", 
    "VITS": "vits", 
    "FAIRSEQ": "fairseq", 
    "TACOTRON2": "tacotron", 
    "YOURTTS": "yourtts"
}

TTS_VOICE_CONVERSION = {
    "freevc24": {"path": "voice_conversion_models/multilingual/vctk/freevc24", "samplerate": 24000},
    "knnvc": {"path": "voice_conversion_models/multilingual/multi-dataset/knnvc", "samplerate": 16000},
    "openvoice_v1": {"path": "voice_conversion_models/multilingual/multi-dataset/openvoice_v1", "samplerate": 22050},
    "openvoice_v2": {"path": "voice_conversion_models/multilingual/multi-dataset/openvoice_v2", "samplerate": 22050}
}

TTS_SML = {
	"break": {"paired": False},
	"pause": {"paired": False},
	"voice": {"paired": True},
	"###": {"paired": False},
}

sml_tag_keys = "|".join(map(re.escape, TTS_SML.keys()))

SML_TAG_PATTERN = re.compile(
	rf'(?:‡|\['
	rf')(?P<close>/)?'
	rf'(?P<tag>{sml_tag_keys})'
	rf'(?:\:(?P<value>[^\]‡]+))?'
	rf'(?:‡|\])'
)

default_sml_pattern = re.compile(r'(###|‡[^‡]+‡)')
default_tts_engine = TTS_ENGINES['XTTSv2']
default_fine_tuned = 'internal'
default_vc_model = TTS_VOICE_CONVERSION['knnvc']['path']
default_voice_detection_model = 'drewThomasson/segmentation'

max_custom_model = 100
max_custom_voices = 1000

default_engine_settings = {
    TTS_ENGINES['XTTSv2']: {
        "repo": "coqui/XTTS-v2",
        "languages": {"ara": "ar", "ces": "cs", "deu": "de", "eng": "en", "fra": "fr", "hin": "hi", "hun": "hu", "ita": "it", "jpn": "ja", "kor": "ko", "nld": "nl", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "tur": "tr", "zho": "zh-cn"},
        "samplerate": 24000,
        "temperature": 0.75,
        #"codec_temperature": 0.3,
        "length_penalty": 1.0,
        "num_beams": 1,
        "repetition_penalty": 2.0,
        #"cvvp_weight": 0.3,
        "top_k": 40,
        "top_p": 0.95,
        "speed": 1.0,
        #"gpt_cond_len": 512,
        #"gpt_batch_size": 1,
        "enable_text_splitting": False,
        "files": ['config.json', 'model.pth', 'vocab.json', 'ref.wav'],
        "voices": {
            "ClaribelDervla": "Claribel Dervla", "DaisyStudious": "Daisy Studious", "GracieWise": "Gracie Wise",
            "TammieEma": "Tammie Ema", "AlisonDietlinde": "Alison Dietlinde", "AnaFlorence": "Ana Florence",
            "AnnmarieNele": "Annmarie Nele", "AsyaAnara": "Asya Anara", "BrendaStern": "Brenda Stern",
            "GittaNikolina": "Gitta Nikolina", "HenrietteUsha": "Henriette Usha", "SofiaHellen": "Sofia Hellen",
            "TammyGrit": "Tammy Grit", "TanjaAdelina": "Tanja Adelina", "VjollcaJohnnie": "Vjollca Johnnie",
            "AndrewChipper": "Andrew Chipper", "BadrOdhiambo": "Badr Odhiambo", "DionisioSchuyler": "Dionisio Schuyler",
            "RoystonMin": "Royston Min", "ViktorEka": "Viktor Eka", "AbrahanMack": "Abrahan Mack",
            "AddeMichal": "Adde Michal", "BaldurSanjin": "Baldur Sanjin", "CraigGutsy": "Craig Gutsy",
            "DamienBlack": "Damien Black", "GilbertoMathias": "Gilberto Mathias", "IlkinUrbano": "Ilkin Urbano",
            "KazuhikoAtallah": "Kazuhiko Atallah", "LudvigMilivoj": "Ludvig Milivoj", "SuadQasim": "Suad Qasim",
            "TorcullDiarmuid": "Torcull Diarmuid", "ViktorMenelaos": "Viktor Menelaos", "ZacharieAimilios": "Zacharie Aimilios",
            "NovaHogarth": "Nova Hogarth", "MajaRuoho": "Maja Ruoho", "UtaObando": "Uta Obando",
            "LidiyaSzekeres": "Lidiya Szekeres", "ChandraMacFarland": "Chandra MacFarland", "SzofiGranger": "Szofi Granger",
            "CamillaHolmström": "Camilla Holmström", "LilyaStainthorpe": "Lilya Stainthorpe", "ZofijaKendrick": "Zofija Kendrick",
            "NarelleMoon": "Narelle Moon", "BarboraMacLean": "Barbora MacLean", "AlexandraHisakawa": "Alexandra Hisakawa",
            "AlmaMaría": "Alma María", "RosemaryOkafor": "Rosemary Okafor", "IgeBehringer": "Ige Behringer",
            "FilipTraverse": "Filip Traverse", "DamjanChapman": "Damjan Chapman", "WulfCarlevaro": "Wulf Carlevaro",
            "AaronDreschner": "Aaron Dreschner", "KumarDahl": "Kumar Dahl", "EugenioMataracı": "Eugenio Mataracı",
            "FerranSimen": "Ferran Simen", "XavierHayasaka": "Xavier Hayasaka", "LuisMoray": "Luis Moray",
            "MarcosRudaski": "Marcos Rudaski"
        },
        "rating": {"VRAM": 4, "CPU": 2, "RAM": 4, "Realism": 5}
    },
    TTS_ENGINES['BARK']: {
        "languages": {"deu": "de", "eng": "en", "fra": "fr", "hin": "hi", "ita": "it", "jpn": "ja", "kor": "ko", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "tur": "tr", "zho": "zh-cn"},
        "samplerate": 24000,
        "text_temp": 0.22,
        "waveform_temp": 0.44,
        "files": ["text_2.pt", "coarse_2.pt", "fine_2.pt"],
        "speakers_path": os.path.join(voices_dir, '__bark'),
        "voices": {
            "de_speaker_0": "Speaker 0", "de_speaker_1": "Speaker 1", "de_speaker_2": "Speaker 2",
            "de_speaker_3": "Speaker 3", "de_speaker_4": "Speaker 4", "de_speaker_5": "Speaker 5",
            "de_speaker_6": "Speaker 6", "de_speaker_7": "Speaker 7", "de_speaker_8": "Speaker 8",
            "de_speaker_9": "Speaker 9", "en_speaker_0": "Speaker 0", "en_speaker_1": "Speaker 1",
            "en_speaker_2": "Speaker 2", "en_speaker_3": "Speaker 3", "en_speaker_4": "Speaker 4",
            "en_speaker_5": "Speaker 5", "en_speaker_6": "Speaker 6", "en_speaker_7": "Speaker 7",
            "en_speaker_8": "Speaker 8", "en_speaker_9": "Speaker 9", "es_speaker_0": "Speaker 0",
            "es_speaker_1": "Speaker 1", "es_speaker_2": "Speaker 2", "es_speaker_3": "Speaker 3",
            "es_speaker_4": "Speaker 4", "es_speaker_5": "Speaker 5", "es_speaker_6": "Speaker 6",
            "es_speaker_7": "Speaker 7", "es_speaker_8": "Speaker 8", "es_speaker_9": "Speaker 9",
            "fr_speaker_0": "Speaker 0", "fr_speaker_1": "Speaker 1", "fr_speaker_2": "Speaker 2",
            "fr_speaker_3": "Speaker 3", "fr_speaker_4": "Speaker 4", "fr_speaker_5": "Speaker 5",
            "fr_speaker_6": "Speaker 6", "fr_speaker_7": "Speaker 7", "fr_speaker_8": "Speaker 8",
            "fr_speaker_9": "Speaker 9", "hi_speaker_0": "Speaker 0", "hi_speaker_1": "Speaker 1",
            "hi_speaker_2": "Speaker 2", "hi_speaker_3": "Speaker 3", "hi_speaker_4": "Speaker 4",
            "hi_speaker_5": "Speaker 5", "hi_speaker_6": "Speaker 6", "hi_speaker_7": "Speaker 7",
            "hi_speaker_8": "Speaker 8", "hi_speaker_9": "Speaker 9", "it_speaker_0": "Speaker 0",
            "it_speaker_1": "Speaker 1", "it_speaker_2": "Speaker 2", "it_speaker_3": "Speaker 3",
            "it_speaker_4": "Speaker 4", "it_speaker_5": "Speaker 5", "it_speaker_6": "Speaker 6",
            "it_speaker_7": "Speaker 7", "it_speaker_8": "Speaker 8", "it_speaker_9": "Speaker 9",
            "ja_speaker_0": "Speaker 0", "ja_speaker_1": "Speaker 1", "ja_speaker_2": "Speaker 2",
            "ja_speaker_3": "Speaker 3", "ja_speaker_4": "Speaker 4", "ja_speaker_5": "Speaker 5",
            "ja_speaker_6": "Speaker 6", "ja_speaker_7": "Speaker 7", "ja_speaker_8": "Speaker 8",
            "ja_speaker_9": "Speaker 9", "ko_speaker_0": "Speaker 0", "ko_speaker_1": "Speaker 1",
            "ko_speaker_2": "Speaker 2", "ko_speaker_3": "Speaker 3", "ko_speaker_4": "Speaker 4",
            "ko_speaker_5": "Speaker 5", "ko_speaker_6": "Speaker 6", "ko_speaker_7": "Speaker 7",
            "ko_speaker_8": "Speaker 8", "ko_speaker_9": "Speaker 9", "pl_speaker_0": "Speaker 0",
            "pl_speaker_1": "Speaker 1", "pl_speaker_2": "Speaker 2", "pl_speaker_3": "Speaker 3",
            "pl_speaker_4": "Speaker 4", "pl_speaker_5": "Speaker 5", "pl_speaker_6": "Speaker 6",
            "pl_speaker_7": "Speaker 7", "pl_speaker_8": "Speaker 8", "pl_speaker_9": "Speaker 9",
            "pt_speaker_0": "Speaker 0", "pt_speaker_1": "Speaker 1", "pt_speaker_2": "Speaker 2",
            "pt_speaker_3": "Speaker 3", "pt_speaker_4": "Speaker 4", "pt_speaker_5": "Speaker 5",
            "pt_speaker_6": "Speaker 6", "pt_speaker_7": "Speaker 7", "pt_speaker_8": "Speaker 8",
            "pt_speaker_9": "Speaker 9", "ru_speaker_0": "Speaker 0", "ru_speaker_1": "Speaker 1",
            "ru_speaker_2": "Speaker 2", "ru_speaker_3": "Speaker 3", "ru_speaker_4": "Speaker 4",
            "ru_speaker_5": "Speaker 5", "ru_speaker_6": "Speaker 6", "ru_speaker_7": "Speaker 7",
            "ru_speaker_8": "Speaker 8", "ru_speaker_9": "Speaker 9", "tr_speaker_0": "Speaker 0",
            "tr_speaker_1": "Speaker 1", "tr_speaker_2": "Speaker 2", "tr_speaker_3": "Speaker 3",
            "tr_speaker_4": "Speaker 4", "tr_speaker_5": "Speaker 5", "tr_speaker_6": "Speaker 6",
            "tr_speaker_7": "Speaker 7", "tr_speaker_8": "Speaker 8", "tr_speaker_9": "Speaker 9",
            "zh_speaker_0": "Speaker 0", "zh_speaker_1": "Speaker 1", "zh_speaker_2": "Speaker 2",
            "zh_speaker_3": "Speaker 3", "zh_speaker_4": "Speaker 4", "zh_speaker_5": "Speaker 5",
            "zh_speaker_6": "Speaker 6", "zh_speaker_7": "Speaker 7", "zh_speaker_8": "Speaker 8",
            "zh_speaker_9": "Speaker 9"
        },
        "rating": {"VRAM": 6, "CPU": 1, "RAM": 6, "Realism": 5}
    },
    TTS_ENGINES['VITS']: {
        "languages": {"ben": "bn", "bul": "bg", "cat": "ca", "ces": "cs", "dan": "da", "deu": "de", "ell": "el", "eng": "en", "est": "et", "ewe": "ewe", "fas": "fa", "fin": "fi", "fra": "fr", "gle": "ga", "hau": "hau", "hrv": "hr", "hun": "hu", "ita": "it", "lav": "lv", "lin": "lin", "lit": "lt", "mlt": "mt", "nld": "nl", "pol": "pl", "por": "pt", "rom": "ro", "slk": "sk", "sln": "sl", "spa": "es", "swe": "sv", "tw_akuapem": "tw_akuapem", "tw_asante": "tw_asante", "ukr": "uk", "yor": "yor"},
        "samplerate": 22050,
        "files": ['config.json', 'model_file.pth', 'language_ids.json'],
        "voices": {},
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['FAIRSEQ']: {
        "languages": {"ara": "ar", "ben": "bn", "eng": "en", "fas": "fa", "fra": "fr", "deu": "de", "hin": "hi", "hun": "hu", "ind": "id", "jav": "jv", "kor": "ko", "pol": "pl", "por": "pt", "rus": "ru", "spa": "es", "tam": "ta", "tel": "te", "tur": "tr", "yor": "yo", "abi": "abi", "ace": "ace", "aca": "aca", "acn": "acn", "acr": "acr", "ach": "ach", "acu": "acu", "guq": "guq", "ade": "ade", "adj": "adj", "agd": "agd", "agx": "agx", "agn": "agn", "aha": "aha", "aka": "ak", "knj": "knj", "ake": "ake", "aeu": "aeu", "ahk": "ahk", "bss": "bss", "alj": "alj", "sqi": "sq", "alt": "alt", "alp": "alp", "alz": "alz", "kab": "kab", "amk": "amk", "mmg": "mmg", "amh": "am", "ami": "ami", "azg": "azg", "agg": "agg", "boj": "boj", "cko": "cko", "any": "any", "arl": "arl", "atq": "atq", "luc": "luc", "hyw": "hyw", "apr": "apr", "aia": "aia", "msy": "msy", "cni": "cni", "cjo": "cjo", "cpu": "cpu", "cpb": "cpb", "asm": "as", "asa": "asa", "teo": "teo", "ati": "ati", "djk": "djk", "ava": "av", "avn": "avn", "avu": "avu", "awb": "awb", "kwi": "kwi", "awa": "awa", "agr": "agr", "agu": "agu", "ayr": "ayr", "ayo": "ayo", "abp": "abp", "blx": "blx", "sgb": "sgb", "azj-script_cyrillic": "azj-script_cyrillic", "azj-script_latin": "azj-script_latin", "azb": "azb", "bba": "bba", "bhz": "bhz", "bvc": "bvc", "bfy": "bfy", "bgq": "bgq", "bdq": "bdq", "bdh": "bdh", "bqi": "bqi", "bjw": "bjw", "blz": "blz", "ban": "ban", "bcc-script_latin": "bcc-script_latin", "bcc-script_arabic": "bcc-script_arabic", "bam": "bm", "ptu": "ptu", "bcw": "bcw", "bqj": "bqj", "bno": "bno", "bbb": "bbb", "bfa": "bfa", "bjz": "bjz", "bak": "ba", "eus": "eu", "bsq": "bsq", "akb": "akb", "btd": "btd", "btx": "btx", "bts": "bts", "bbc": "bbc", "bvz": "bvz", "bjv": "bjv", "bep": "bep", "bkv": "bkv", "bzj": "bzj", "bem": "bem", "bng": "bng", "bom": "bom", "btt": "btt", "bha": "bha", "bgw": "bgw", "bht": "bht", "beh": "beh", "sne": "sne", "ubl": "ubl", "bcl": "bcl", "bim": "bim", "bkd": "bkd", "bjr": "bjr", "bfo": "bfo", "biv": "biv", "bib": "bib", "bis": "bi", "bzi": "bzi", "bqp": "bqp", "bpr": "bpr", "bps": "bps", "bwq": "bwq", "bdv": "bdv", "bqc": "bqc", "bus": "bus", "bnp": "bnp", "bmq": "bmq", "bdg": "bdg", "boa": "boa", "ksr": "ksr", "bor": "bor", "bru": "bru", "box": "box", "bzh": "bzh", "bgt": "bgt", "sab": "sab", "bul": "bg", "bwu": "bwu", "bmv": "bmv", "mya": "my", "tte": "tte", "cjp": "cjp", "cbv": "cbv", "kaq": "kaq", "cot": "cot", "cbc": "cbc", "car": "car", "cat": "ca", "ceb": "ceb", "cme": "cme", "cbi": "cbi", "ceg": "ceg", "cly": "cly", "cya": "cya", "che": "ce", "hne": "hne", "nya": "ny", "dig": "dig", "dug": "dug", "bgr": "bgr", "cek": "cek", "cfm": "cfm", "cnh": "cnh", "hlt": "hlt", "mwq": "mwq", "ctd": "ctd", "tcz": "tcz", "zyp": "zyp", "cco": "cco", "cnl": "cnl", "cle": "cle", "chz": "chz", "cpa": "cpa", "cso": "cso", "cnt": "cnt", "cuc": "cuc", "hak": "hak", "nan": "nan", "xnj": "xnj", "cap": "cap", "cax": "cax", "ctg": "ctg", "ctu": "ctu", "chf": "chf", "cce": "cce", "crt": "crt", "crq": "crq", "cac-dialect_sansebasti\u00e1ncoat\u00e1n": "cac-dialect_sansebasti\u00e1ncoat\u00e1n", "cac-dialect_sanmateoixtat\u00e1n": "cac-dialect_sanmateoixtat\u00e1n", "ckt": "ckt", "ncu": "ncu", "cdj": "cdj", "chv": "cv", "caa": "caa", "asg": "asg", "con": "con", "crn": "crn", "cok": "cok", "crk-script_latin": "crk-script_latin", "crk-script_syllabics": "crk-script_syllabics", "crh": "crh", "cui": "cui", "ces": "cs", "dsh": "dsh", "dbq": "dbq", "dga": "dga", "dgi": "dgi", "dgk": "dgk", "dnj-dialect_gweetaawueast": "dnj-dialect_gweetaawueast", "dnj-dialect_blowowest": "dnj-dialect_blowowest", "daa": "daa", "dnt": "dnt", "dnw": "dnw", "dar": "dar", "tcc": "tcc", "dwr": "dwr", "ded": "ded", "mzw": "mzw", "ntr": "ntr", "ddn": "ddn", "des": "des", "dso": "dso", "nfa": "nfa", "dhi": "dhi", "gud": "gud", "did": "did", "mhu": "mhu", "dip": "dip", "dik": "dik", "tbz": "tbz", "dts": "dts", "dos": "dos", "dgo": "dgo", "mvp": "mvp", "jen": "jen", "dzo": "dz", "idd": "idd", "eka": "eka", "cto": "cto", "emp": "emp", "enx": "enx", "sja": "sja", "myv": "myv", "mcq": "mcq", "ese": "ese", "evn": "evn", "eza": "eza", "ewe": "ee", "fal": "fal", "fao": "fo", "far": "far", "fij": "fj", "fin": "fi", "fon": "fon", "frd": "frd", "ful": "ff", "flr": "flr", "gau": "gau", "gbk": "gbk", "gag-script_cyrillic": "gag-script_cyrillic", "gag-script_latin": "gag-script_latin", "gbi": "gbi", "gmv": "gmv", "lug": "lg", "pwg": "pwg", "gbm": "gbm", "cab": "cab", "grt": "grt", "krs": "krs", "gso": "gso", "nlg": "nlg", "gej": "gej", "gri": "gri", "kik": "ki", "acd": "acd", "glk": "glk", "gof-script_latin": "gof-script_latin", "gog": "gog", "gkn": "gkn", "wsg": "wsg", "gjn": "gjn", "gqr": "gqr", "gor": "gor", "gux": "gux", "gbo": "gbo", "ell": "el", "grc": "grc", "guh": "guh", "gub": "gub", "grn": "gn", "gyr": "gyr", "guo": "guo", "gde": "gde", "guj": "gu", "gvl": "gvl", "guk": "guk", "rub": "rub", "dah": "dah", "gwr": "gwr", "gwi": "gwi", "hat": "ht", "hlb": "hlb", "amf": "amf", "hag": "hag", "hnn": "hnn", "bgc": "bgc", "had": "had", "hau": "ha", "hwc": "hwc", "hvn": "hvn", "hay": "hay", "xed": "xed", "heb": "he", "heh": "heh", "hil": "hil", "hif": "hif", "hns": "hns", "hoc": "hoc", "hoy": "hoy", "hus-dialect_westernpotosino": "hus-dialect_westernpotosino", "hus-dialect_centralveracruz": "hus-dialect_centralveracruz", "huv": "huv", "hui": "hui", "hap": "hap", "iba": "iba", "isl": "is", "dbj": "dbj", "ifa": "ifa", "ifb": "ifb", "ifu": "ifu", "ifk": "ifk", "ife": "ife", "ign": "ign", "ikk": "ikk", "iqw": "iqw", "ilb": "ilb", "ilo": "ilo", "imo": "imo", "inb": "inb", "ipi": "ipi", "irk": "irk", "icr": "icr", "itv": "itv", "itl": "itl", "atg": "atg", "ixl-dialect_sanjuancotzal": "ixl-dialect_sanjuancotzal", "ixl-dialect_sangasparchajul": "ixl-dialect_sangasparchajul", "ixl-dialect_santamarianebaj": "ixl-dialect_santamarianebaj", "nca": "nca", "izr": "izr", "izz": "izz", "jac": "jac", "jam": "jam", "jvn": "jvn", "kac": "kac", "dyo": "dyo", "csk": "csk", "adh": "adh", "jun": "jun", "jbu": "jbu", "dyu": "dyu", "bex": "bex", "juy": "juy", "gna": "gna", "urb": "urb", "kbp": "kbp", "cwa": "cwa", "dtp": "dtp", "kbr": "kbr", "cgc": "cgc", "kki": "kki", "kzf": "kzf", "lew": "lew", "cbr": "cbr", "kkj": "kkj", "keo": "keo", "kqe": "kqe", "kak": "kak", "kyb": "kyb", "knb": "knb", "kmd": "kmd", "kml": "kml", "ify": "ify", "xal": "xal", "kbq": "kbq", "kay": "kay", "ktb": "ktb", "hig": "hig", "gam": "gam", "cbu": "cbu", "xnr": "xnr", "kmu": "kmu", "kne": "kne", "kan": "kn", "kby": "kby", "pam": "pam", "cak-dialect_santamar\u00edadejes\u00fas": "cak-dialect_santamar\u00edadejes\u00fas", "cak-dialect_southcentral": "cak-dialect_southcentral", "cak-dialect_yepocapa": "cak-dialect_yepocapa", "cak-dialect_western": "cak-dialect_western", "cak-dialect_santodomingoxenacoj": "cak-dialect_santodomingoxenacoj", "cak-dialect_central": "cak-dialect_central", "xrb": "xrb", "krc": "krc", "kaa": "kaa", "krl": "krl", "pww": "pww", "xsm": "xsm", "cbs": "cbs", "pss": "pss", "kxf": "kxf", "kyz": "kyz", "kyu": "kyu", "txu": "txu", "kaz": "kk", "ndp": "ndp", "kbo": "kbo", "kyq": "kyq", "ken": "ken", "ker": "ker", "xte": "xte", "kyg": "kyg", "kjh": "kjh", "kca": "kca", "khm": "km", "kxm": "kxm", "kjg": "kjg", "nyf": "nyf", "kij": "kij", "kia": "kia", "kqr": "kqr", "kqp": "kqp", "krj": "krj", "zga": "zga", "kin": "rw", "pkb": "pkb", "geb": "geb", "gil": "gil", "kje": "kje", "kss": "kss", "thk": "thk", "klu": "klu", "kyo": "kyo", "kog": "kog", "kfb": "kfb", "kpv": "kpv", "bbo": "bbo", "xon": "xon", "kma": "kma", "kno": "kno", "kxc": "kxc", "ozm": "ozm", "kqy": "kqy", "coe": "coe", "kpq": "kpq", "kpy": "kpy", "kyf": "kyf", "kff-script_telugu": "kff-script_telugu", "kri": "kri", "rop": "rop", "ktj": "ktj", "ted": "ted", "krr": "krr", "kdt": "kdt", "kez": "kez", "cul": "cul", "kle": "kle", "kdi": "kdi", "kue": "kue", "kum": "kum", "kvn": "kvn", "cuk": "cuk", "kdn": "kdn", "xuo": "xuo", "key": "key", "kpz": "kpz", "knk": "knk", "kmr-script_latin": "kmr-script_latin", "kmr-script_arabic": "kmr-script_arabic", "kmr-script_cyrillic": "kmr-script_cyrillic", "xua": "xua", "kru": "kru", "kus": "kus", "kub": "kub", "kdc": "kdc", "kxv": "kxv", "blh": "blh", "cwt": "cwt", "kwd": "kwd", "tnk": "tnk", "kwf": "kwf", "cwe": "cwe", "kyc": "kyc", "tye": "tye", "kir": "ky", "quc-dialect_north": "quc-dialect_north", "quc-dialect_east": "quc-dialect_east", "quc-dialect_central": "quc-dialect_central", "lac": "lac", "lsi": "lsi", "lbj": "lbj", "lhu": "lhu", "las": "las", "lam": "lam", "lns": "lns", "ljp": "ljp", "laj": "laj", "lao": "lo", "lat": "la", "lav": "lv", "law": "law", "lcp": "lcp", "lzz": "lzz", "lln": "lln", "lef": "lef", "acf": "acf", "lww": "lww", "mhx": "mhx", "eip": "eip", "lia": "lia", "lif": "lif", "onb": "onb", "lis": "lis", "loq": "loq", "lob": "lob", "yaz": "yaz", "lok": "lok", "llg": "llg", "ycl": "ycl", "lom": "lom", "ngl": "ngl", "lon": "lon", "lex": "lex", "lgg": "lgg", "ruf": "ruf", "dop": "dop", "lnd": "lnd", "ndy": "ndy", "lwo": "lwo", "lee": "lee", "mev": "mev", "mfz": "mfz", "jmc": "jmc", "myy": "myy", "mbc": "mbc", "mda": "mda", "mad": "mad", "mag": "mag", "ayz": "ayz", "mai": "mai", "mca": "mca", "mcp": "mcp", "mak": "mak", "vmw": "vmw", "mgh": "mgh", "kde": "kde", "mlg": "mg", "zlm": "zlm", "pse": "pse", "mkn": "mkn", "xmm": "xmm", "mal": "ml", "xdy": "xdy", "div": "dv", "mdy": "mdy", "mup": "mup", "mam-dialect_central": "mam-dialect_central", "mam-dialect_northern": "mam-dialect_northern", "mam-dialect_southern": "mam-dialect_southern", "mam-dialect_western": "mam-dialect_western", "mqj": "mqj", "mcu": "mcu", "mzk": "mzk", "maw": "maw", "mjl": "mjl", "mnk": "mnk", "mge": "mge", "mbh": "mbh", "knf": "knf", "mjv": "mjv", "mbt": "mbt", "obo": "obo", "mbb": "mbb", "mzj": "mzj", "nld": "nld", "sjm": "sjm", "mrw": "mrw", "mar": "mr", "mpg": "mpg", "mhr": "mhr", "enb": "enb", "mah": "mh", "myx": "myx", "klv": "klv", "mfh": "mfh", "met": "met", "mcb": "mcb", "mop": "mop", "yua": "yua", "mfy": "mfy", "maz": "maz", "vmy": "vmy", "maq": "maq", "mzi": "mzi", "maj": "maj", "maa-dialect_sanantonio": "maa-dialect_sanantonio", "maa-dialect_sanjer\u00f3nimo": "maa-dialect_sanjer\u00f3nimo", "mhy": "mhy", "mhi": "mhi", "zmz": "zmz", "myb": "myb", "gai": "gai", "mqb": "mqb", "mbu": "mbu", "med": "med", "men": "men", "mee": "mee", "mwv": "mwv", "meq": "meq", "zim": "zim", "mgo": "mgo", "mej": "mej", "mpp": "mpp", "min": "min", "gum": "gum", "mpx": "mpx", "mco": "mco", "mxq": "mxq", "pxm": "pxm", "mto": "mto", "mim": "mim", "xta": "xta", "mbz": "mbz", "mip": "mip", "mib": "mib", "miy": "miy", "mih": "mih", "miz": "miz", "xtd": "xtd", "mxt": "mxt", "xtm": "xtm", "mxv": "mxv", "xtn": "xtn", "mie": "mie", "mil": "mil", "mio": "mio", "mdv": "mdv", "mza": "mza", "mit": "mit", "mxb": "mxb", "mpm": "mpm", "soy": "soy", "cmo-script_latin": "cmo-script_latin", "cmo-script_khmer": "cmo-script_khmer", "mfq": "mfq", "old": "old", "mfk": "mfk", "mif": "mif", "mkl": "mkl", "mox": "mox", "myl": "myl", "mqf": "mqf", "mnw": "mnw", "mon": "mn", "mog": "mog", "mfe": "mfe", "mor": "mor", "mqn": "mqn", "mgd": "mgd", "mtj": "mtj", "cmr": "cmr", "mtd": "mtd", "bmr": "bmr", "moz": "moz", "mzm": "mzm", "mnb": "mnb", "mnf": "mnf", "unr": "unr", "fmu": "fmu", "mur": "mur", "tih": "tih", "muv": "muv", "muy": "muy", "sur": "sur", "moa": "moa", "wmw": "wmw", "tnr": "tnr", "miq": "miq", "mos": "mos", "muh": "muh", "nas": "nas", "mbj": "mbj", "nfr": "nfr", "kfw": "kfw", "nst": "nst", "nag": "nag", "nch": "nch", "nhe": "nhe", "ngu": "ngu", "azz": "azz", "nhx": "nhx", "ncl": "ncl", "nhy": "nhy", "ncj": "ncj", "nsu": "nsu", "npl": "npl", "nuz": "nuz", "nhw": "nhw", "nhi": "nhi", "nlc": "nlc", "nab": "nab", "gld": "gld", "nnb": "nnb", "npy": "npy", "pbb": "pbb", "ntm": "ntm", "nmz": "nmz", "naw": "naw", "nxq": "nxq", "ndj": "ndj", "ndz": "ndz", "ndv": "ndv", "new": "new", "nij": "nij", "sba": "sba", "gng": "gng", "nga": "nga", "nnq": "nnq", "ngp": "ngp", "gym": "gym", "kdj": "kdj", "nia": "nia", "nim": "nim", "nin": "nin", "nko": "nko", "nog": "nog", "lem": "lem", "not": "not", "nhu": "nhu", "nob": "nb", "bud": "bud", "nus": "nus", "yas": "yas", "nnw": "nnw", "nwb": "nwb", "nyy": "nyy", "nyn": "nyn", "rim": "rim", "lid": "lid", "nuj": "nuj", "nyo": "nyo", "nzi": "nzi", "ann": "ann", "ory": "ory", "ojb-script_latin": "ojb-script_latin", "ojb-script_syllabics": "ojb-script_syllabics", "oku": "oku", "bsc": "bsc", "bdu": "bdu", "orm": "om", "ury": "ury", "oss": "os", "ote": "ote", "otq": "otq", "stn": "stn", "sig": "sig", "kfx": "kfx", "bfz": "bfz", "sey": "sey", "pao": "pao", "pau": "pau", "pce": "pce", "plw": "plw", "pmf": "pmf", "pag": "pag", "pap": "pap", "prf": "prf", "pab": "pab", "pbi": "pbi", "pbc": "pbc", "pad": "pad", "ata": "ata", "pez": "pez", "peg": "peg", "pcm": "pcm", "pis": "pis", "pny": "pny", "pir": "pir", "pjt": "pjt", "poy": "poy", "pps": "pps", "pls": "pls", "poi": "poi", "poh-dialect_eastern": "poh-dialect_eastern", "poh-dialect_western": "poh-dialect_western", "prt": "prt", "pui": "pui", "pan": "pa", "tsz": "tsz", "suv": "suv", "lme": "lme", "quy": "quy", "qvc": "qvc", "quz": "quz", "qve": "qve", "qub": "qub", "qvh": "qvh", "qwh": "qwh", "qvw": "qvw", "quf": "quf", "qvm": "qvm", "qul": "qul", "qvn": "qvn", "qxn": "qxn", "qxh": "qxh", "qvs": "qvs", "quh": "quh", "qxo": "qxo", "qxr": "qxr", "qvo": "qvo", "qvz": "qvz", "qxl": "qxl", "quw": "quw", "kjb": "kjb", "kek": "kek", "rah": "rah", "rjs": "rjs", "rai": "rai", "lje": "lje", "rnl": "rnl", "rkt": "rkt", "rap": "rap", "yea": "yea", "raw": "raw", "rej": "rej", "rel": "rel", "ril": "ril", "iri": "iri", "rgu": "rgu", "rhg": "rhg", "rmc-script_latin": "rmc-script_latin", "rmc-script_cyrillic": "rmc-script_cyrillic", "rmo": "rmo", "rmy-script_latin": "rmy-script_latin", "rmy-script_cyrillic": "rmy-script_cyrillic", "ron": "ro", "rol": "rol", "cla": "cla", "rng": "rng", "rug": "rug", "run": "rn", "lsm": "lsm", "spy": "spy", "sck": "sck", "saj": "saj", "sch": "sch", "sml": "sml", "xsb": "xsb", "sbl": "sbl", "saq": "saq", "sbd": "sbd", "smo": "sm", "rav": "rav", "sxn": "sxn", "sag": "sg", "sbp": "sbp", "xsu": "xsu", "srm": "srm", "sas": "sas", "apb": "apb", "sgw": "sgw", "tvw": "tvw", "lip": "lip", "slu": "slu", "snw": "snw", "sea": "sea", "sza": "sza", "seh": "seh", "crs": "crs", "ksb": "ksb", "shn": "shn", "sho": "sho", "mcd": "mcd", "cbt": "cbt", "xsr": "xsr", "shk": "shk", "shp": "shp", "sna": "sn", "cjs": "cjs", "jiv": "jiv", "snp": "snp", "sya": "sya", "sid": "sid", "snn": "snn", "sri": "sri", "srx": "srx", "sil": "sil", "sld": "sld", "akp": "akp", "xog": "xog", "som": "so", "bmu": "bmu", "khq": "khq", "ses": "ses", "mnx": "mnx", "srn": "srn", "sxb": "sxb", "suc": "suc", "tgo": "tgo", "suk": "suk", "sun": "su", "suz": "suz", "sgj": "sgj", "sus": "sus", "swh": "swh", "swe": "sv", "syl": "syl", "dyi": "dyi", "myk": "myk", "spp": "spp", "tap": "tap", "tby": "tby", "tna": "tna", "shi": "shi", "klw": "klw", "tgl": "tl", "tbk": "tbk", "tgj": "tgj", "blt": "blt", "tbg": "tbg", "omw": "omw", "tgk": "tg", "tdj": "tdj", "tbc": "tbc", "tlj": "tlj", "tly": "tly", "ttq-script_tifinagh": "ttq-script_tifinagh", "taj": "taj", "taq": "taq", "tpm": "tpm", "tgp": "tgp", "tnn": "tnn", "tac": "tac", "rif-script_latin": "rif-script_latin", "rif-script_arabic": "rif-script_arabic", "tat": "tt", "tav": "tav", "twb": "twb", "tbl": "tbl", "kps": "kps", "twe": "twe", "ttc": "ttc", "kdh": "kdh", "tes": "tes", "tex": "tex", "tee": "tee", "tpp": "tpp", "tpt": "tpt", "stp": "stp", "tfr": "tfr", "twu": "twu", "ter": "ter", "tew": "tew", "tha": "th", "nod": "nod", "thl": "thl", "tem": "tem", "adx": "adx", "bod": "bo", "khg": "khg", "tca": "tca", "tir": "ti", "txq": "txq", "tik": "tik", "dgr": "dgr", "tob": "tob", "tmf": "tmf", "tng": "tng", "tlb": "tlb", "ood": "ood", "tpi": "tpi", "jic": "jic", "lbw": "lbw", "txa": "txa", "tom": "tom", "toh": "toh", "tnt": "tnt", "sda": "sda", "tcs": "tcs", "toc": "toc", "tos": "tos", "neb": "neb", "trn": "trn", "trs": "trs", "trc": "trc", "tri": "tri", "cof": "cof", "tkr": "tkr", "kdl": "kdl", "cas": "cas", "tso": "ts", "tuo": "tuo", "iou": "iou", "tmc": "tmc", "tuf": "tuf", "tuk-script_latin": "tk", "tuk-script_arabic": "tk", "bov": "bov", "tue": "tue", "kcg": "kcg", "tzh-dialect_bachaj\u00f3n": "tzh-dialect_bachaj\u00f3n", "tzh-dialect_tenejapa": "tzh-dialect_tenejapa", "tzo-dialect_chenalh\u00f3": "tzo-dialect_chenalh\u00f3", "tzo-dialect_chamula": "tzo-dialect_chamula", "tzj-dialect_western": "tzj-dialect_western", "tzj-dialect_eastern": "tzj-dialect_eastern", "aoz": "aoz", "udm": "udm", "udu": "udu", "ukr": "uk", "ppk": "ppk", "ubu": "ubu", "urk": "urk", "ura": "ura", "urt": "urt", "urd-script_devanagari": "ur", "urd-script_arabic": "ur", "urd-script_latin": "ur", "upv": "upv", "usp": "usp", "uig-script_arabic": "ug", "uig-script_cyrillic": "ug", "uzb-script_cyrillic": "uz", "vag": "vag", "bav": "bav", "vid": "vid", "vie": "vi", "vif": "vif", "vun": "vun", "vut": "vut", "prk": "prk", "wwa": "wwa", "rro": "rro", "bao": "bao", "waw": "waw", "lgl": "lgl", "wlx": "wlx", "cou": "cou", "hub": "hub", "gvc": "gvc", "mfi": "mfi", "wap": "wap", "wba": "wba", "war": "war", "way": "way", "guc": "guc", "cym": "cy", "kvw": "kvw", "tnp": "tnp", "hto": "hto", "huu": "huu", "wal-script_latin": "wal-script_latin", "wal-script_ethiopic": "wal-script_ethiopic", "wlo": "wlo", "noa": "noa", "wob": "wob", "kao": "kao", "xer": "xer", "yad": "yad", "yka": "yka", "sah": "sah", "yba": "yba", "yli": "yli", "nlk": "nlk", "yal": "yal", "yam": "yam", "yat": "yat", "jmd": "jmd", "tao": "tao", "yaa": "yaa", "ame": "ame", "guu": "guu", "yao": "yao", "yre": "yre", "yva": "yva", "ybb": "ybb", "pib": "pib", "byr": "byr", "pil": "pil", "ycn": "ycn", "ess": "ess", "yuz": "yuz", "atb": "atb", "zne": "zne", "zaq": "zaq", "zpo": "zpo", "zad": "zad", "zpc": "zpc", "zca": "zca", "zpg": "zpg", "zai": "zai", "zpl": "zpl", "zam": "zam", "zaw": "zaw", "zpm": "zpm", "zac": "zac", "zao": "zao", "ztq": "ztq", "zar": "zar", "zpt": "zpt", "zpi": "zpi", "zas": "zas", "zaa": "zaa", "zpz": "zpz", "zab": "zab", "zpu": "zpu", "zae": "zae", "zty": "zty", "zav": "zav", "zza": "zza", "zyb": "zyb", "ziw": "ziw", "zos": "zos", "gnd": "gnd"},
        "samplerate": 16000,
        "files": ['config.json', 'G_100000.pth', 'vocab.json'],
        "voices": {},
        "rating": {"VRAM": 2, "CPU": 4, "RAM": 4, "Realism": 4}
    },
    TTS_ENGINES['TACOTRON2']: {
        "languages": {"deu": "de", "eng": "en", "fra": "fr", "jpn": "ja", "nld": "nl", "spa": "es", "zho": "zh-CN"},
        "samplerate": 22050,
        "files": ['config.json', 'best_model.pth', 'vocoder_config.json', 'vocoder_model.pth'],
        "voices": {},
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 2, "Realism": 3}
    },
    TTS_ENGINES['YOURTTS']: {
        "languages": {"eng": "en", "fra": "fr", "por": "pt"},
        "samplerate": 16000,
        "files": ['config.json', 'model_file.pth'],
        "voices": {"Machinella-5": "female-en-5", "ElectroMale-2": "male-en-2", 'Machinella-4': 'female-pt-4\n', 'ElectroMale-3': 'male-pt-3\n'},
        "rating": {"VRAM": 1, "CPU": 5, "RAM": 1, "Realism": 2}
    }
}