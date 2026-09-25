from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES_ROOT = REPO_ROOT / "recipes" / "ljspeech"


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    recipe_dir: str
    train_script: str
    family: str
    official_model_id: str | None = None
    default_vocoder_id: str | None = None
    supports_language: bool = False
    requires_speaker_wav: bool = False
    notes: str = ""

    @property
    def recipe_path(self) -> Path:
        return RECIPES_ROOT / self.recipe_dir

    @property
    def train_script_path(self) -> Path:
        return self.recipe_path / self.train_script


MODEL_SPECS = (
    ModelSpec(
        key="align_tts",
        label="Align TTS",
        recipe_dir="align_tts",
        train_script="train_aligntts.py",
        family="tts",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="delightful_tts",
        label="DelightfulTTS",
        recipe_dir="delightful_tts",
        train_script="train_delightful_tts.py",
        family="tts",
    ),
    ModelSpec(
        key="fast_pitch",
        label="FastPitch",
        recipe_dir="fast_pitch",
        train_script="train_fast_pitch.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/fast_pitch",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="fast_speech",
        label="FastSpeech",
        recipe_dir="fast_speech",
        train_script="train_fast_speech.py",
        family="tts",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="fastspeech2",
        label="FastSpeech 2",
        recipe_dir="fastspeech2",
        train_script="train_fastspeech2.py",
        family="tts",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="glow_tts",
        label="Glow-TTS",
        recipe_dir="glow_tts",
        train_script="train_glowtts.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/glow-tts",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="neuralhmm_tts",
        label="NeuralHMM-TTS",
        recipe_dir="neuralhmm_tts",
        train_script="train_neuralhmmtts.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/neural_hmm",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="overflow",
        label="Overflow",
        recipe_dir="overflow",
        train_script="train_overflow.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/overflow",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="speedy_speech",
        label="SpeedySpeech",
        recipe_dir="speedy_speech",
        train_script="train_speedy_speech.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/speedy-speech",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="tacotron2_capacitron",
        label="Tacotron2 Capacitron",
        recipe_dir="tacotron2-Capacitron",
        train_script="train_capacitron_t2.py",
        family="tts",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="tacotron2_dca",
        label="Tacotron2 DCA",
        recipe_dir="tacotron2-DCA",
        train_script="train_tacotron_dca.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/tacotron2-DCA",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="tacotron2_ddc",
        label="Tacotron2 DDC",
        recipe_dir="tacotron2-DDC",
        train_script="train_tacotron_ddc.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/tacotron2-DDC",
        default_vocoder_id="vocoder_models/en/ljspeech/univnet",
    ),
    ModelSpec(
        key="vits_tts",
        label="VITS",
        recipe_dir="vits_tts",
        train_script="train_vits.py",
        family="tts",
        official_model_id="tts_models/en/ljspeech/vits",
    ),
    ModelSpec(
        key="xtts_v1",
        label="XTTS v1",
        recipe_dir="xtts_v1",
        train_script="train_gpt_xtts.py",
        family="xtts",
        official_model_id="tts_models/multilingual/multi-dataset/xtts_v1.1",
        supports_language=True,
        requires_speaker_wav=True,
    ),
    ModelSpec(
        key="xtts_v2",
        label="XTTS v2",
        recipe_dir="xtts_v2",
        train_script="train_gpt_xtts.py",
        family="xtts",
        official_model_id="tts_models/multilingual/multi-dataset/xtts_v2",
        supports_language=True,
        requires_speaker_wav=True,
    ),
    ModelSpec(
        key="piper",
        label="Piper TTS",
        recipe_dir="piper",
        train_script="piper_train",
        family="piper",
        supports_language=True,
        requires_speaker_wav=False,
    ),
)

MODEL_SPECS_BY_KEY = {spec.key: spec for spec in MODEL_SPECS}

# Published Coqui checkpoints whose model architecture matches an existing UFT
# recipe. Keep the full model ID: dataset and voice variants are distinct bases.
# English defaults remain in ModelSpec.official_model_id for older callers.
PRETRAINED_MODEL_IDS: dict[str, dict[str, tuple[str, ...]]] = {
    "glow_tts": {
        "tr": ("tts_models/tr/common-voice/glow-tts",),
        "it": ("tts_models/it/mai_female/glow-tts", "tts_models/it/mai_male/glow-tts"),
        "uk": ("tts_models/uk/mai/glow-tts",),
        "fa": ("tts_models/fa/custom/glow-tts",),
        "be": ("tts_models/be/common-voice/glow-tts",),
    },
    "tacotron2_dca": {
        "de": ("tts_models/de/thorsten/tacotron2-DCA",),
    },
    "tacotron2_ddc": {
        "es": ("tts_models/es/mai/tacotron2-DDC",),
        "fr": ("tts_models/fr/mai/tacotron2-DDC",),
        "nl": ("tts_models/nl/mai/tacotron2-DDC",),
        "de": ("tts_models/de/thorsten/tacotron2-DDC",),
        "ja": ("tts_models/ja/kokoro/tacotron2-DDC",),
    },
    "vits_tts": {
        "bg": ("tts_models/bg/cv/vits",),
        "cs": ("tts_models/cs/cv/vits",),
        "da": ("tts_models/da/cv/vits",),
        "et": ("tts_models/et/cv/vits",),
        "ga": ("tts_models/ga/cv/vits",),
        "es": ("tts_models/es/css10/vits",),
        "fr": ("tts_models/fr/css10/vits",),
        "nl": ("tts_models/nl/css10/vits",),
        "de": ("tts_models/de/thorsten/vits",),
        "it": ("tts_models/it/mai_female/vits", "tts_models/it/mai_male/vits"),
        "hu": ("tts_models/hu/css10/vits",),
        "pl": ("tts_models/pl/mai_female/vits",),
        "pt": ("tts_models/pt/cv/vits",),
        "el": ("tts_models/el/cv/vits",),
        "fi": ("tts_models/fi/css10/vits",),
        "hr": ("tts_models/hr/cv/vits",),
        "lt": ("tts_models/lt/cv/vits",),
        "lv": ("tts_models/lv/cv/vits",),
        "mt": ("tts_models/mt/cv/vits",),
        "ro": ("tts_models/ro/cv/vits",),
        "sk": ("tts_models/sk/cv/vits",),
        "sl": ("tts_models/sl/cv/vits",),
        "sv": ("tts_models/sv/cv/vits",),
        "ca": ("tts_models/ca/custom/vits",),
        "uk": ("tts_models/uk/mai/vits",),
    },
}

XTTS_LANGUAGES = {
    "xtts_v1": frozenset("en es fr de it pt pl tr ru nl cs ar zh-cn ja".split()),
    "xtts_v2": frozenset("en es fr de it pt pl tr ru nl cs ar zh-cn hu ko ja hi".split()),
}


def normalize_language(language: str) -> str:
    normalized = language.lower().replace("_", "-")
    return "zh-cn" if normalized == "zh" else normalized


def pretrained_model_choices(model_key: str, language: str) -> tuple[str, ...]:
    spec = get_model_spec(model_key)
    language = normalize_language(language)
    if spec.family == "xtts":
        return (spec.official_model_id,) if spec.official_model_id and language in XTTS_LANGUAGES[model_key] else ()
    if language == "en":
        return (spec.official_model_id,) if spec.official_model_id else ()
    return PRETRAINED_MODEL_IDS.get(model_key, {}).get(language, ())


def get_model_spec(model_key: str) -> ModelSpec:
    try:
        return MODEL_SPECS_BY_KEY[model_key]
    except KeyError as exc:
        supported = ", ".join(sorted(MODEL_SPECS_BY_KEY))
        raise ValueError(f"Unsupported model '{model_key}'. Supported models: {supported}") from exc


def list_model_choices() -> list[tuple[str, str]]:
    return [(spec.key, spec.label) for spec in MODEL_SPECS]
