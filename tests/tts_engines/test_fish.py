import os
import tempfile


def test_fish_convert_short_sentence():
    from lib.classes.tts_engines.fish import Fish

    session = {
        "tts_engine": "fish",
        "fine_tuned": "internal",
        "model_cache": "fish-internal",
        "language": "eng",
        "language_iso1": "en",
        "translate_enabled": False,
        "free_vram_gb": 16.0,
        "device": "cuda",
        "voice": None,
        "custom_model": None,
        "custom_model_dir": "",
        "is_gui_process": False,
        "script_mode": "cli",
        "process_dir": tempfile.mkdtemp(),
    }
    engine = Fish(session)
    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "sentence.wav")
        ok, error = engine.convert(out_path, "This is a short test sentence.")
        assert ok, error
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
