FROM python:3.10-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.13 /uv /uvx /bin/

# Install system dependencies (Calibre for ebook conversion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    calibre \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Install the compatible spaCy English model with uv
RUN uv pip install --system --no-cache "$(python -m spacy info en_core_web_sm --url)"

# Copy application code
COPY . .

# Default mount point for ebook2audiobook
RUN mkdir -p /ebook2audiobook

# Expose Gradio default port
EXPOSE 7861

# Download the shared voice library when the mounted repository does not have it,
# then launch the web GUI accessible from outside the container.
CMD ["python", "-m", "sml_extractor.docker_entrypoint"]
