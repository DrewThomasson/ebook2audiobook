# breeze-tts's own upstream repo (github.com/breezeblue-ai/breeze-tts) ships no
# setup.py/pyproject.toml, so it is not pip-installable as-is. This file was authored
# for this vendored copy (ext/py/breeze-tts) so it can be installed in editable mode
# the same way ./ext/py/demucs already is in this repo's requirements.txt - it is not
# copied from upstream. Upstream's top-level `models` package was renamed to
# `breeze_models` here (and all internal imports updated to match) since `models`
# is too generic a name to install globally editable without risking collisions.
from setuptools import setup, find_packages

setup(
    name="breeze-tts",
    version="0.0.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"configs": ["*.json"]},
    include_package_data=True,
    install_requires=[],  # deps already listed in this repo's requirements.txt
)
