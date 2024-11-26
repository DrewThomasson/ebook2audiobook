from setuptools import setup, find_packages

setup(
    name='ebook2audiobook',
    version='2.0.0',
    python_requires=">=3.10,<3.12",
    author="Drew Thomasson",
    description="Convert eBooks to audiobooks with chapters and metadata",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DrewThomasson/ebook2audiobook",
    packages=find_packages(include=["ebook2audiobook", "ebook2audiobook.*", "lib", "lib.*"]),
    install_requires=[
        "beautifulsoup4",
        "coqui-tts",
        "cutlet",
        "deep_translator",
        "docker",
        "ebooklib",
        "gensim",
        "gradio>=4.44",
        "hangul-romanize",
        "indic-nlp-library",
        "iso-639",
        "jieba",
        "pydub",
        "pypinyin",
        "ray",
        "transformers",
        "translate",
        "tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ebook2audiobook = ebook2audiobook.app:main",
        ],
    },
)
