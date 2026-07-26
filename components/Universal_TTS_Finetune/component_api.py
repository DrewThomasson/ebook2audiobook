"""Stable entry point for ebook2audiobook component integration."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_COMPONENT_DIR = Path(__file__).resolve().parent

COMPONENT = {
    "id": "universal-tts-finetune",
    "name": "Universal TTS Finetune",
    "description": "Prepare datasets, fine-tune TTS models, and test voices.",
    "default_port": 7862,
}


def _load():
    component_path = str(_COMPONENT_DIR)
    added = component_path not in sys.path
    if added:
        sys.path.insert(0, component_path)
    try:
        from tts_finetune_config import ComponentConfig

        module_name = "_universal_tts_finetune_web_gui"
        module = sys.modules.get(module_name)
        if module is None:
            spec = importlib.util.spec_from_file_location(
                module_name, _COMPONENT_DIR / "web_gui.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not load the TTS fine-tuning interface")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        return ComponentConfig, module.create_app
    finally:
        if added:
            sys.path.remove(component_path)


def create_app(
    *,
    e2a_root=None,
    output_dir=None,
    theme=None,
    css=None,
    **defaults,
):
    """Return an unlaunched Gradio app configured for E2A storage."""
    ComponentConfig, build_app = _load()
    config = ComponentConfig.resolve(e2a_root, output_dir).prepare()
    return build_app(config, theme=theme, css=css, **defaults)
