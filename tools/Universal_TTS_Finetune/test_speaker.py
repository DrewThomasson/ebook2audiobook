from TTS.api import TTS
try:
    print("Loading model...")
    # The standard your_tts model has a speaker encoder
    tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
    print("Model loaded.")
    # See if we can extract an embedding
    print(dir(tts.synthesizer.tts_model.speaker_manager))
except Exception as e:
    print(e)
