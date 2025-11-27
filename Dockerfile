# ------------------------------------------
# BASE STAGE
# ------------------------------------------
ARG BASE=python:3.12
FROM ${BASE} AS base

ENV PATH="/root/.local/bin:$PATH"
ENV DEBIAN_FRONTEND=noninteractive

# Rust needed for some TTS engines
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Install unidic
RUN pip install --no-cache-dir unidic-lite unidic && \
    python3 -m unidic download && \
    mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Your script that sets up ebook2audiobook environment
# This stage does NOT touch PyTorch — correct design
COPY . /app
RUN ./ebook2audiobook.sh --script_mode full_docker

# ------------------------------------------
# PYTORCH STAGE
# ------------------------------------------
# Build args passed from build_docker_with_torch.sh
ARG TORCH_WHEEL
ARG TORCHAUDIO_WHEEL
ARG DEVICE

FROM base AS pytorch

WORKDIR /app

# Copy your project files
COPY . /app

# Install the correct PyTorch + Torchaudio wheels
# They are already validated and constructed in your bash script
RUN echo "Installing Torch wheel: $TORCH_WHEEL" && \
    pip install --no-cache-dir "$TORCH_WHEEL" && \
    echo "Installing Torchaudio wheel: $TORCHAUDIO_WHEEL" && \
    pip install --no-cache-dir "$TORCHAUDIO_WHEEL"

# Expose your port (Gradio or API)
EXPOSE 7860

# Runtime entrypoint
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]