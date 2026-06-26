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


def get_model_spec(model_key: str) -> ModelSpec:
    try:
        return MODEL_SPECS_BY_KEY[model_key]
    except KeyError as exc:
        supported = ", ".join(sorted(MODEL_SPECS_BY_KEY))
        raise ValueError(f"Unsupported model '{model_key}'. Supported models: {supported}") from exc


def list_model_choices() -> list[tuple[str, str]]:
    return [(spec.key, spec.label) for spec in MODEL_SPECS]
