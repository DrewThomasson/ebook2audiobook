# Vendored copy of Breeze TTS 2's PyTorch inference code.
#
#   Upstream:      https://github.com/breezeblue-ai/breeze-tts
#   Model weights: https://huggingface.co/BreezeBlue/breeze-tts-2
#   Code license:  Apache-2.0, preserved verbatim in ./LICENSE. The audio
#                  tokenizer derives from Qwen3-TTS (Alibaba Qwen Team), also
#                  Apache-2.0.
#   Weights:       NOT Apache. Governed by the BreezeBlue Research and
#                  Non-Commercial License, which grants no commercial rights.
#                  Disclosed next to the engine list in this repo's README.
#
# Upstream ships no setup.py/pyproject.toml; this file is local. The only edit to
# upstream source is renaming its `models` module, which collides on install, to
# `breeze_models`.
from setuptools import find_packages, setup

# torch, torchaudio and transformers are omitted: DeviceInstaller resolves those
# per device, and pinning them here would fight that resolution.
REQUIRED = [
    "qwen-tts==0.1.1",
    "uvicorn>=0.30",
    "python-multipart>=0.0.18",
]

setup(
    name="breeze-tts",
    version="0.0.0",
    url="https://github.com/breezeblue-ai/breeze-tts",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"configs": ["*.json"]},
    include_package_data=True,
    install_requires=REQUIRED,
)
