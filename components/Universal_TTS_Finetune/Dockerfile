FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for TTS and audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the Gradio port
EXPOSE 7862

# Run the Gradio demo by default
CMD ["python", "web_gui.py", "--host", "0.0.0.0", "--port", "7862"]
