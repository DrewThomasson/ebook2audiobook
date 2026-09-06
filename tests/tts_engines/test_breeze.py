import os
import tempfile


def test_breeze_convert_short_sentence():
    from lib.classes.tts_engines.breeze import Breeze

    session = {
        "tts_engine": "breeze",
        "fine_tuned": "internal",
        "model_cache": "breeze-internal",
        "device": "cuda",
        "voice": None,
        "custom_model": None,
        "custom_model_dir": "",
        "is_gui_process": False,
        "script_mode": "cli",
    }
    engine = Breeze(session)
    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "sentence.wav")
        ok, error = engine.convert(out_path, "This is a short test sentence.")
        assert ok, error
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
