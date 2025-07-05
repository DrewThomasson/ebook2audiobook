import os
import torch
import regex as re
import stanza

from num2words import num2words
from lib.models import loaded_tts, max_tts_in_memory

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

def year_to_words(year_str, lang_iso1):
    try:
        year = int(year_str)
        if len(year_str) != 4 or not year_str.isdigit():
            return num2words(year, lang=lang_iso1)
        first_two = int(year_str[:2])
        last_two = int(year_str[2:])
        return f"{num2words(first_two, lang=lang_iso1)} {num2words(last_two, lang=lang_iso1)}"  
    except Exception as e:
        error = f'year_to_words() error: {e}'
        print(error)
        raise
        return False

def get_model_vocab(obj):
    try:
        if hasattr(obj, "characters"):
            punctuations = ''
            if hasattr(obj.characters, "punctuations"):
                punctuations = obj.characters.punctuations
            return set(obj.characters.characters + punctuations)
        if hasattr(obj, "tokenizer") and hasattr(obj.tokenizer, "symbols"):
            return set(obj.tokenizer.symbols)
        if hasattr(obj, "symbols"):
            return set(obj.symbols)
        if hasattr(obj, "tts_model") and hasattr(obj.tts_model, "tokenizer"):
            tokenizer = obj.tts_model.tokenizer
            if hasattr(tokenizer, "symbols"):
                return set(tokenizer.symbols)
        if hasattr(obj.tts_checkpoint):
            vocab_path = os.path.join(obj.tts_checkpoint, 'vocab.txt')
            if os.path.isfile(vocab_path):
                return set(''.join(line.strip() for line in open('vocab.txt', encoding='utf-8') if line.strip()))
        return False
    except Exception as e:
        error = f'check_vocab_support() error: {e}'
        print(error)
        return False

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