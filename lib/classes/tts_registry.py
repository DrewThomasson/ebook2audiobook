class TTSRegistry:

    ENGINES = {}

    def __init_subclass__(cls, *, name, **kwargs):
        super().__init_subclass__(**kwargs)

        if not isinstance(name, str):
            raise TypeError("TTS engine name must be a string")

        if name in TTSRegistry.ENGINES:
            raise ValueError(f"Duplicate TTS engine name: {name}")

        TTSRegistry.ENGINES[name] = cls

    def __init__(self, session):
        self.session = session

    def convert(self, sentence_number, sentence):
        raise NotImplementedError