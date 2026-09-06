FROM pytorch/pytorch:2.9.1-cuda12.8-cudnn9-devel

ARG FLASH_ATTN_CUDA_ARCHS=90

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TOKENIZERS_PARALLELISM=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        ffmpeg \
        git \
        libsndfile1 \
        ninja-build \
        sox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/breeze-infer

COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel packaging ninja \
    && python -m pip install -r requirements.txt \
    && MAX_JOBS=8 FLASH_ATTN_CUDA_ARCHS=${FLASH_ATTN_CUDA_ARCHS} python -m pip install \
        --no-build-isolation \
        --no-deps \
        "flash-attn==2.8.3"

COPY . .

RUN python docker/smoke_check.py \
    && python -m pytest -q \
        tests/test_logits_process.py \
        tests/test_templates.py \
        tests/test_warmup_profile.py

ENTRYPOINT ["/opt/breeze-infer/docker/entrypoint.sh"]
CMD ["python", "-m", "breeze_infer.api", "--help"]
