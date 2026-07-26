"""Runtime configuration shared by standalone and future E2A launches."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ComponentConfig:
    e2a_root: Path
    models_dir: Path
    voices_dir: Path
    output_dir: Path
    run_dir: Path

    @classmethod
    def resolve(
        cls,
        e2a_root: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> "ComponentConfig":
        component_dir = Path(__file__).resolve().parent
        detected_root = component_dir.parent.parent
        root = Path(
            e2a_root or os.environ.get("E2A_ROOT") or detected_root
        ).expanduser().resolve()
        models = Path(
            os.environ.get("E2A_MODELS_DIR", root / "models")
        ).expanduser().resolve()
        voices = Path(
            os.environ.get("E2A_VOICES_DIR", root / "voices")
        ).expanduser().resolve()
        output = Path(
            output_dir
            or os.environ.get("E2A_FINETUNE_OUTPUT_DIR")
            or root / "finetune_models"
        ).expanduser().resolve()
        run = Path(
            os.environ.get(
                "E2A_RUN_DIR", root / "run" / "components" / "tts-finetune"
            )
        ).expanduser().resolve()
        return cls(root, models, voices, output, run)

    def prepare(self) -> "ComponentConfig":
        for directory in (self.models_dir, self.output_dir, self.run_dir):
            directory.mkdir(parents=True, exist_ok=True)

        model_cache = self.models_dir / "tts"
        model_cache.mkdir(parents=True, exist_ok=True)
        env = {
            "E2A_ROOT": self.e2a_root,
            "E2A_MODELS_DIR": self.models_dir,
            "E2A_VOICES_DIR": self.voices_dir,
            "E2A_FINETUNE_OUTPUT_DIR": self.output_dir,
            "HF_HOME": model_cache,
            "HUGGINGFACE_HUB_CACHE": model_cache,
            "HF_DATASETS_CACHE": model_cache,
            "TORCH_HOME": model_cache,
            "TTS_HOME": self.models_dir,
            "TTS_CACHE": model_cache,
            "XDG_CACHE_HOME": self.models_dir,
            "XDG_CONFIG_HOME": self.models_dir / "config",
            "TMPDIR": self.run_dir,
            "GRADIO_TEMP_DIR": self.run_dir / "gradio",
        }
        for name, value in env.items():
            if name in {"TMPDIR", "GRADIO_TEMP_DIR"}:
                os.environ.setdefault(name, str(value))
            else:
                os.environ[name] = str(value)
        if tempfile.tempdir is None:
            tempfile.tempdir = os.environ.get("TMPDIR", str(self.run_dir))
        return self


def e2a_theme():
    """Return the same base theme used by ebook2audiobook."""
    import gradio as gr

    return gr.themes.Origin(
        primary_hue="green",
        secondary_hue="amber",
        neutral_hue="gray",
        radius_size="lg",
        font_mono=[
            "JetBrains Mono",
            "monospace",
            "Consolas",
            "Menlo",
            "Liberation Mono",
        ],
    )


E2A_COMPONENT_CSS = """
.e2a-component-header { margin-bottom: 1rem; }
.e2a-primary {
    background: linear-gradient(90deg, #22c55e 0%, #eab308 100%) !important;
    color: white !important;
    border: none !important;
}
.e2a-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.35) !important;
}
"""
