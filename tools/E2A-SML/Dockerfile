FROM python:3.10-slim

# Install system dependencies (Calibre for ebook conversion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    calibre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Default mount point for ebook2audiobook
RUN mkdir -p /ebook2audiobook

# Expose Gradio default port
EXPOSE 7860

# Default: launch the web GUI accessible from outside the container
CMD ["python", "cli.py", "--gui", "--host", "0.0.0.0"]
