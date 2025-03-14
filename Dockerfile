ARG BASE=python:3.12
FROM ${BASE} AS base
# Set environment PATH for local installations
ENV PATH="/root/.local/bin:$PATH"
# Set non-interactive mode to prevent tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive
# Install system packages
RUN apt-get update && \
    apt-get install -y gcc g++ make wget git calibre ffmpeg libmecab-dev mecab mecab-ipadic-utf8 libsndfile1-dev libc-dev curl espeak-ng sox && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Install Rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
# Copy the application
WORKDIR /app
COPY . /app
# Install UniDic (non-torch dependent)
RUN pip install --no-cache-dir unidic-lite unidic && \
    python3 -m unidic download && \
    mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Second stage for PyTorch installation
FROM base AS pytorch
# Add parameter for PyTorch version with a default empty value
ARG TORCH_VERSION=""

# Extract torch versions from requirements.txt
RUN TORCH_VERSION_REQ=$(grep -E "^torch==" requirements.txt | cut -d'=' -f3) && \
    TORCHAUDIO_VERSION_REQ=$(grep -E "^torchaudio==" requirements.txt | cut -d'=' -f3) && \
    TORCHVISION_VERSION_REQ=$(grep -E "^torchvision==" requirements.txt | cut -d'=' -f3) && \
    echo "Found in requirements: torch==$TORCH_VERSION_REQ torchaudio==$TORCHAUDIO_VERSION_REQ torchvision==$TORCHVISION_VERSION_REQ"

# Install PyTorch with CUDA support if specified
RUN if [ ! -z "$TORCH_VERSION" ]; then \
        TORCH_VERSION_REQ=$(grep -E "^torch==" requirements.txt | cut -d'=' -f3) && \
        TORCHAUDIO_VERSION_REQ=$(grep -E "^torchaudio==" requirements.txt | cut -d'=' -f3) && \
        TORCHVISION_VERSION_REQ=$(grep -E "^torchvision==" requirements.txt | cut -d'=' -f3) && \
        case "$TORCH_VERSION" in \
            "cuda12") \
                pip install --no-cache-dir torch==${TORCH_VERSION_REQ} torchvision==${TORCHVISION_VERSION_REQ} torchaudio==${TORCHAUDIO_VERSION_REQ} --extra-index-url https://download.pytorch.org/whl/cu121 \
                ;; \
            "cuda11") \
                pip install --no-cache-dir torch==${TORCH_VERSION_REQ} torchvision==${TORCHVISION_VERSION_REQ} torchaudio==${TORCHAUDIO_VERSION_REQ} --extra-index-url https://download.pytorch.org/whl/cu118 \
                ;; \
            "cpu") \
                pip install --no-cache-dir torch==${TORCH_VERSION_REQ} torchvision==${TORCHVISION_VERSION_REQ} torchaudio==${TORCHAUDIO_VERSION_REQ} --extra-index-url https://download.pytorch.org/whl/cpu \
                ;; \
            *) \
                pip install --no-cache-dir $TORCH_VERSION \
                ;; \
        esac && \
        # Install remaining requirements, skipping torch packages
        grep -v -E "^torch==|^torchvision==|^torchaudio==" requirements.txt > requirements_no_torch.txt && \
        pip install --no-cache-dir --upgrade -r requirements_no_torch.txt && \
        rm requirements_no_torch.txt; \
    else \
        # Install all requirements as specified
        pip install --no-cache-dir --upgrade -r requirements.txt; \
    fi

# Do a test run to pre-download and bake base models into the image
RUN echo "This is a test sentence." > test.txt && \
    python app.py --headless --ebook test.txt --script_mode full_docker && \
    rm test.txt
# Expose the required port
EXPOSE 7860
# Start the Gradio app with the required flag
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]
