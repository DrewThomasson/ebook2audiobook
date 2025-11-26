# -----------------------------
# BASE IMAGE STAGE
# -----------------------------
ARG BASE=python:3.12
FROM ${BASE} AS base

ENV PATH="/root/.local/bin:$PATH"
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && \
    apt-get install -y \
        gcc g++ make wget git calibre ffmpeg \
        libmecab-dev mecab mecab-ipadic-utf8 \
        libsndfile1-dev libc-dev curl espeak-ng sox && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Rust toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# UniDic installation (torch-independent)
RUN pip install --no-cache-dir unidic-lite unidic && \
    python3 -m unidic download && \
    mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic


# -----------------------------
# PYTORCH + APPLICATION STAGE
# -----------------------------
ARG BASE_IMAGE=base
FROM ${BASE_IMAGE} AS pytorch

ARG TORCH_VERSION=""
ARG SKIP_XTTS_TEST="false"

WORKDIR /app
COPY . /app

# Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Optional model warm-up
RUN if [ "$SKIP_XTTS_TEST" != "true" ]; then \
        echo "Running XTTS model warm-up..."; \
        if [ "$TORCH_VERSION" = "xpu" ]; then \
            TORCH_DEVICE_BACKEND_AUTOLOAD=0 \
                python app.py --headless --ebook test.txt --script_mode full_docker; \
        else \
            python app.py --headless --language eng \
                --ebook tools/workflow-testing/test1.txt \
                --tts_engine XTTSv2 \
                --script_mode full_docker; \
        fi; \
    else \
        echo "Skipping XTTS test run."; \
    fi

EXPOSE 7860

ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]