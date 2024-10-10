impott setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

# Read requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="ebook2audiobookXTTS",
    version="1.2",
    author="Drew Thomasson",
    description="Convert eBooks to audiobooks with chapters and metadata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DrewThomasson/ebook2audiobookXTTS",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'turnvoice=turnvoice.core.turnvoice:main',
            'ebook2audiobook=ebook2audiobook:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=requirements,
    keywords='replace, voice, ebook, audiobook, '
             'sentence-segmentation, TTS-engine, sentence-fragment, python'
)
