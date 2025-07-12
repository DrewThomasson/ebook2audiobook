import os
import torch
import regex as re
import stanza

from lib.models import loaded_tts, max_tts_in_memory, TTS_ENGINES

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