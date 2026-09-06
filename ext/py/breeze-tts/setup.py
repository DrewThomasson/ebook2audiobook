# Upstream ships no setup.py/pyproject.toml; authored here so this vendored copy
# installs editable the same way ./ext/py/demucs already does.
from setuptools import setup, find_packages

setup(
    name="breeze-tts",
    version="0.0.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"configs": ["*.json"]},
    include_package_data=True,
    install_requires=[],  # deps already listed in this repo's requirements.txt
)
