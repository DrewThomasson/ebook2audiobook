# Use an official Python 3.10 image
FROM python:3.10-slim-buster

# Set non-interactive installation to avoid timezone and other prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    calibre \
    espeak \
    espeak-ng \
    ffmpeg \
    wget \
    tk \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /ebook2audiobookXTTS

# Clone the ebook2audiobookXTTS repository and install dependencies
RUN git clone https://github.com/DrewThomasson/ebook2audiobookXTTS.git .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install bs4 pydub nltk beautifulsoup4 ebooklib tqdm mecab-python3 tts==0.21.3

# Download unidic
RUN python -m unidic download

# Copy test audio file
COPY default_voice.wav /ebook2audiobookXTTS/

# Run a test to set up XTTS
RUN echo "import torch" > /tmp/script1.py && \
    echo "from TTS.api import TTS" >> /tmp/script1.py && \
    echo "device = 'cuda' if torch.cuda.is_available() else 'cpu'" >> /tmp/script1.py && \
    echo "print(TTS().list_models())" >> /tmp/script1.py && \
    echo "tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)" >> /tmp/script1.py && \
    echo "wav = tts.tts(text='Hello world!', speaker_wav='default_voice.wav', language='en')" >> /tmp/script1.py && \
    echo "tts.tts_to_file(text='Hello world!', speaker_wav='default_voice.wav', language='en', file_path='output.wav')" >> /tmp/script1.py && \
    yes | python3 /tmp/script1.py

# Remove the test audio file
RUN rm -f /ebook2audiobookXTTS/output.wav

# Set the command to run your GUI application
CMD ["python", "custom_model_ebook2audiobookXTTS_gradio.py"]
