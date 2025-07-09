import os
import torch
import regex as re
import stanza

from num2words import num2words
from lib.models import loaded_tts, max_tts_in_memory, TTS_ENGINES
from lib.lang import default_language_code, language_math_phonemes
        
def check_num2words_compat(lang_iso1):
    try:
        num2words(1, lang=lang_iso1)
        return True
    except NotImplementedError:
        return False
    except Exception as e:
        return False

def detect_date_entities(text, stanza_nlp):
    try:
        doc = stanza_nlp(text)
        date_spans = []
        for ent in doc.ents:
            if ent.type == 'DATE':
                date_spans.append((ent.start_char, ent.end_char, ent.text))
        return date_spans
    except Exception as e:
        error = f'detect_date_entities() error: {e}'
        print(error)
        return False

def year_to_words(year_str, lang, lang_iso1, is_num2words_compat):
    try:
        year = int(year_str)
        lang_iso1 = lang_iso1 if lang in language_math_phonemes.keys() else default_language_code
        if len(year_str) != 4 or not year_str.isdigit():
            if is_num2words_compat:
                return num2words(year, lang=lang_iso1)
            else:
                return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in year_str)
        first_two = int(year_str[:2])
        last_two = int(year_str[2:])
        if is_num2words_compat:
            return f"{num2words(first_two, lang=lang_iso1)} {num2words(last_two, lang=lang_iso1)}" 
        else:
            return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in first_two) + ' ' + ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in last_two)
    except Exception as e:
        error = f'year_to_words() error: {e}'
        print(error)
        raise
        return False

def check_formatted_number(text, lang_iso1, is_num2words_compat, max_single_value=999_999_999):
    text = text.strip()
    digit_count = sum(c.isdigit() for c in text)
    # --- 1) Pure small integers up to 9 digits: leave as-is ---
    if digit_count <= 9 and text.isdigit():
        return text
    # --- 2) “Thousands-grouped” numbers (at most 2 commas) ---
    # e.g. "1,234" or "12,345,678.90", but NOT long lists like "626,262,636,626,262,…"
    grouped_num_pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d+)?'
    if text.count(',') <= 2 and re.fullmatch(grouped_num_pattern, text):
        # try parsing as a float
        try:
            val = float(text.replace(',', ''))
            if abs(val) <= max_single_value:
                return text
        except ValueError:
            pass
    # --- 3) Otherwise tokenize and process each number/token individually ---
    # captures decimals, ints, punctuation, words, and whitespace
    token_re = re.compile(r'\d*\.\d+|\d+|[^\w\s]|\w+|\s+')
    tokens = token_re.findall(text)
    result = []
    for tok in tokens:
        # decimal numbers like "123.45"
        if re.fullmatch(r'\d*\.\d+', tok):
            if is_num2words_compat:
                num = float(tok)
                result.append(num2words(num, lang=lang_iso1))
            else:
                result.append(tok)
        # pure integer tokens
        elif tok.isdigit():
            if is_num2words_compat:
                num = int(tok)
                result.append(num2words(num, lang=lang_iso1))
            else:
                result.append(tok)
        # anything else (commas, Russian text, punctuation, spaces…)
        else:
            result.append(tok)
    return ''.join(result)

def math2word(text, lang, lang_iso1, tts_engine, is_num2words_compat):
    def rep_num(match):
        try:
            number = match.group()
            trailing = ''
            if number and number[-1] in '.,':
                trailing = number[-1]
                number = number[:-1]
            if "." in number or "e" in number.lower():
                number_value = float(number)
            else:
                number_value = int(number)
            print(f'---------{number_value}-----------')
            if is_num2words_compat:
                return num2words(number_value, lang=lang_iso1)
            else:
                return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in number_value)
        except Exception as e:
            print(f"Error converting number: {number}, Error: {e}")
            return match.group(0)

    def replace_ambiguous(match):
        # handles "num SYMBOL num" and "SYMBOL num"
        if match.group(2) and match.group(2) in ambiguous_replacements:
            return f"{match.group(1)} {ambiguous_replacements[match.group(2)]} {match.group(3)}"
        if match.group(3) and match.group(3) in ambiguous_replacements:
            return f"{ambiguous_replacements[match.group(3)]} {match.group(4)}"
        return match.group(0)

    # 1) Pre-process formatted series (e.g. phone numbers) if needed
    text = check_formatted_number(text, lang_iso1, is_num2words_compat)
    # 2) Symbol phonemes
    phonemes_list = language_math_phonemes.get(lang, language_math_phonemes[default_language_code])
    ambiguous_symbols = {"-", "/", "*", "x"}
    replacements         = {k: v for k, v in phonemes_list.items() if not k.isdigit()}
    normal_replacements  = {k: v for k, v in replacements.items() if k not in ambiguous_symbols}
    ambiguous_replacements = {k: v for k, v in replacements.items() if k in ambiguous_symbols}
    # 3) Replace unambiguous symbols everywhere
    if normal_replacements:
        sym_pat = r'(' + '|'.join(map(re.escape, normal_replacements.keys())) + r')'
        text = re.sub(sym_pat, lambda m: f" {normal_replacements[m.group(1)]} ", text)
        print(f'normal_replacements------------{text}------------')
    # 4) Replace ambiguous symbols only in valid equation contexts
    if ambiguous_replacements:
        amb_pat = (
            r'(?<!\S)'               # no non-space before
            r'(\d+)\s*([-/*x])\s*(\d+)'  # num SYMBOL num
            r'(?!\S)'               # no non-space after
            r'|'                    # or
            r'(?<!\S)([-/*x])\s*(\d+)(?!\S)'  # SYMBOL num
        )
        text = re.sub(amb_pat, replace_ambiguous, text)
        print(f'ambiguous_replacements------------{text}------------')
    # split long digit-runs (3-digit groups)
    text = re.sub(r'(\d{3})(?=\d{3}(?!\.\d))', r'\1 ', text)
    if tts_engine != TTS_ENGINES['XTTSv2']:
        # 5) Number-to-words: build a pattern that finds any standalone number,
        #    with commas, decimals or exponents.
        number_pattern = (
            r'(?<!\S)'                                      # whitespace or start
            r'(-?\d{1,3}(?:,\d{3})*'                        # integer with optional commas
            r'(?:\.\d+)?'                                   # optional decimal
            r'(?:[eE][+-]?\d+)?)'                           # optional exponent
            r'(?!\S)'                                       # whitespace or end
        )
        # *this* re.sub will now find every standalone number and convert it
        text = re.sub(number_pattern, rep_num, text)
        print(f'ambiguous_replacements------------{text}------------')
    return text

def unload_tts(device, reserved_keys=None, tts_key=None):
    try:
        if len(loaded_tts) >= max_tts_in_memory:
            if reserved_keys is None:
                reserved_keys = []
            if tts_key is not None:
                if tts_key in loaded_tts.keys():
                    del loaded_tts[tts_key]
                if device == 'cuda':
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            else:
                for key in list(loaded_tts.keys()):
                    if key not in reserved_keys:
                        del loaded_tts[key]
    except Exception as e:
        error = f'unload_tts() error: {e}'
        print(error)
        return False
        
def append_sentence2vtt(sentence_obj, path):

    def format_timestamp(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{s:06.3f}"

    try:
        index = 1
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if "-->" in line:
                        index += 1
        if index > 1 and "resume_check" in sentence_obj and sentence_obj["resume_check"] < index:
            return index  # Already written
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
        with open(path, "a", encoding="utf-8") as f:
            start = format_timestamp(sentence_obj["start"])
            end = format_timestamp(sentence_obj["end"])
            text = re.sub(r'[\r\n]+', ' ', sentence_obj["text"]).strip()
            f.write(f"{start} --> {end}\n{text}\n\n")
        return index + 1
    except Exception as e:
        error = f'append_sentence2vtt() error: {e}'
        print(error)
        return False