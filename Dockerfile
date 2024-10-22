# Use an official NVIDIA CUDA image with cudnn8 and Ubuntu 20.04 as the base
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Set non-interactive installation to avoid timezone and other prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages including Miniconda
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    espeak \
    espeak-ng \
    ffmpeg \
    tk \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    build-essential \
    calibre \
    && rm -rf /var/lib/apt/lists/*

RUN ebook-convert --version

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh


# Set PATH to include conda
ENV PATH=/opt/conda/bin:$PATH

# Create a conda environment with Python 3.10
RUN conda create -n ebookenv python=3.10 -y

# Activate the conda environment
SHELL ["conda", "run", "-n", "ebookenv", "/bin/bash", "-c"]

# Install Python dependencies using conda and pip
RUN conda install -n ebookenv -c conda-forge \
    pydub \
    nltk \
    mecab-python3 \
    && pip install --no-cache-dir \
    bs4 \
    beautifulsoup4 \
    ebooklib \
    translate \
    tqdm \
    tts==0.21.3 \
    unidic \
    gradio \
    docker

# Download unidic
RUN python -m unidic download

# Download spacy NLP
RUN python -m spacy download en_core_web_sm

# Set the working directory in the container
WORKDIR /ebook2audiobookXTTS

# Clone the ebook2audiobookXTTS repository
RUN git clone https://github.com/DrewThomasson/ebook2audiobookXTTS.git .

# Copy test audio file
COPY ./voices/adult/female/en/default_voice.wav /ebook2audiobookXTTS/

# Run a test to set up XTTS
RUN echo "import torch" > /tmp/script1.py && \
    echo "from TTS.api import TTS" >> /tmp/script1.py && \
    echo "device = 'cuda' if torch.cuda.is_available() else 'cpu'" >> /tmp/script1.py && \
    echo "print(TTS().list_models())" >> /tmp/script1.py && \
    echo "tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)" >> /tmp/script1.py && \
    echo "wav = tts.tts(text='Hello world!', speaker_wav='default_voice.wav', language='en')" >> /tmp/script1.py && \
    echo "tts.tts_to_file(text='Hello world!', speaker_wav='default_voice.wav', language='en', file_path='output.wav')" >> /tmp/script1.py && \
    yes | python /tmp/script1.py

# Remove the test audio file
RUN rm -f /ebook2audiobookXTTS/output.wav

# Verify that the script exists and has the correct permissions
RUN ls -la /ebook2audiobookXTTS/

# Check if the script exists and log its presence
RUN if [ -f /ebook2audiobookXTTS/custom_model_ebook2audiobookXTTS_with_link_gradio.py ]; then echo "Script found."; else echo "Script not found."; exit 1; fi

# Modify the Python script to set share=True
RUN sed -i 's/demo.launch(share=False)/demo.launch(share=True)/' /ebook2audiobookXTTS/custom_model_ebook2audiobookXTTS_with_link_gradio.py

# Download the punkt package for nltk
RUN python -m nltk.downloader punkt

# Set the command to run your GUI application using the conda environment
CMD ["conda", "run", "--no-capture-output", "-n", "ebookenv", "python", "/ebook2audiobookXTTS/custom_model_ebook2audiobookXTTS_with_link_gradio.py"]

