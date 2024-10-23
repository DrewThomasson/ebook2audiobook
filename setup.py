from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import os

cwd = os.path.dirname(os.path.abspath(__file__))

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.run([sys.executable, 'python -m', 'unidic', 'download'], check=True)

setup(
    name='ebook2audiobook',
    version='2.0.0',
    python_requires=">=3.10,<3.12",
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
    cmdclass={
        'install': PostInstallCommand,
    }
)
