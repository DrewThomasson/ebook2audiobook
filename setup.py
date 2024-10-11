import os
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


cwd = os.path.dirname(os.path.abspath(__file__))

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        os.system('python -m unidic download')


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        os.system('python -m unidic download')

setup(
    name='ebook2audiobookXTTS',
    version='1.2.0',
    author="Drew Thomasson",
    description="Convert eBooks to audiobooks with chapters and metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DrewThomasson/ebook2audiobookXTTS",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ebook2audiobook = app:main",
        ],
    },
    keywords='ebook, audiobook, TTS-engine, python',
)
