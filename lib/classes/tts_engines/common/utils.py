import os
import gc
import torch
import regex as re
import stanza

from typing import Any, Union
from lib.models import loaded_tts, max_tts_in_memory, TTS_ENGINES

def cleanup_garbage():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.synchronize()

def unload_tts(device:str, reserved_keys:list[str]|None, tts_key:str)->bool:
    try:
        if len(loaded_tts) > max_tts_in_memory:
            if reserved_keys is None:
                if tts_key in loaded_tts:
                    loaded_tts.pop(tts_key, False)
            else:
                if tts_key not in reserved_keys:
                    if tts_key in loaded_tts:
                        loaded_tts.pop(tts_key, False)
        cleanup_garbage()
        return True
    except Exception as e:
        error = f"unload_tts() error: {e}"
        print(error)
        return False

def append_sentence2vtt(sentence_obj:dict[str, Any], path:str)->Union[int, bool]:

    def format_timestamp(seconds:float)->str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{s:06.3f}"

    try:
        index = 1
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "-->" in line:
                        index += 1
        if index > 1 and "resume_check" in sentence_obj and sentence_obj["resume_check"] < index:
            return index  # Already written
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
        with open(path, "a", encoding="utf-8") as f:
            start = format_timestamp(float(sentence_obj["start"]))
            end = format_timestamp(float(sentence_obj["end"]))
            text = re.sub(r"[\r\n]+", " ", str(sentence_obj["text"])).strip()
            f.write(f"{start} --> {end}\n{text}\n\n")
        return index + 1
    except Exception as e:
        error = f"append_sentence2vtt() error: {e}"
        print(error)
        return False
