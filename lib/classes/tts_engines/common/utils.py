import os
import num2words
import regex as re
import stanza

from lib.models import loaded_tts, max_tts_in_memory

def detect_date_entities(text, stanza_nlp):
    doc = stanza_nlp(text)
    date_spans = []
    for ent in doc.ents:
        if ent.type == 'DATE':
            date_spans.append((ent.start_char, ent.end_char, ent.text))
    return date_spans

def year_to_words(match, lang_iso1):
    year = int(match.group())
    year_str = str(year)
    if len(year_str) != 4 or not year_str.isdigit():
        return num2words(year, lang=lang_iso1)
    first_two = int(year_str[:2])
    last_two = int(year_str[2:])
    return f"{num2words(first_two, lang=lang_iso1)} {num2words(last_two, lang=lang_iso1)}"  

def unload_tts(device, reserved_keys=None, tts_key=None):
    if len(loaded_tts) >= max_tts_in_memory:
        if reserved_keys is None:
            reserved_keys = []
        if tts_key is not None:
            if tts_key in loaded_tts.keys():
                del loaded_tts[tts_key]
        else:
            for key in list(loaded_tts.keys()):
                if key not in reserved_keys:
                    del loaded_tts[key]
                    
def append_sentence2vtt(sentence_obj, path):

    def format_timestamp(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{s:06.3f}"

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