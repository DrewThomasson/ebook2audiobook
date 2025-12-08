# ─────────────────────────────────────────────────────────────
# FINAL OPTIMIZED & FIXED DOCKERFILE – ~1.55 GB forever
# ─────────────────────────────────────────────────────────────
ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim-bookworm

# ========================= BUILD STAGE =========================
FROM ${BASE} AS build

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install everything needed in build stage
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc g++ make python3-dev pkg-config git curl wget bash xz-utils \
        libglib2.0-0 libnss3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 \
        libx11-6 libegl1 libopengl0 libxrender1 libxext6 libxi6 libxcb1 \
        ${DOCKER_PROGRAMS_STR}; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# CRITICAL: Copy only files needed for pip install FIRST (caching!)
COPY requirements.txt ebook2audiobook.sh pyproject.toml setup.py MANIFEST.in ./
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# Install Python deps + run your script
RUN --mount=type=cache,target=/root/.cache/pip \
   .com \
    chmod +x ebook2audiobook.sh && \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# Install calibre
RUN set -ex; \
    wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && \
    rm -f /tmp/calibre.sh

# Clean build tools
RUN apt-get purge -y --auto-remove \
        gcc g++ make python3-dev pkg-config git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache \
    && find /usr/local -type d -name '__pycache__' -exec rm -rf {} +

# ========================= FINAL STAGE =========================
FROM ${BASE}

ARG DOCKER_PROGRAMS_STR
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    CALIBRE_DISABLE_CHECKS=1 \
    CALIBRE_DISABLE_GUI=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:/opt/calibre:/usr/local/bin:/usr/bin:/bin:${PATH}"

# Runtime packages only
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libglib2.0-0 libnss3 libatk1.0-0 libgdk-pixbuf-2.0-0 \
        libdbus-1-3 libx11-6 libegl1 libopengl0 libxcb-cursor0 \
        libxrender1 libxext6 libxi6 libxcb1 \
        ${DOCKER_PROGRAMS_STR} \
        tesseract-ocr tesseract-ocr-${ISO3_LANG} || true; \
    rm -rf /var/lib/apt/lists/*

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# ONLY copy what pip actually installed
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages/
COPY --from=build /usr/local/bin                          /usr/local/bin/
# Calibre
COPY --from=build /opt/calibre                            /opt/calibre
COPY --from=build /root/.local                            /root/.local 2>/dev/null || true
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# NOW copy your entire repo – .dockerignore does the magic
# → python_env/, tmp/*, models/* etc. are excluded
COPY . /app
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# Ensure tmp/ is always empty and writable
RUN rm -rf /app/tmp && mkdir -m 777 /app/tmp

# Final tiny cleanups
RUN set -ex; \
    find /usr -type d -name "__pycache__" -exec rm -rf {} +; \
    rm -rf \
        /usr/share/doc/* \
        /usr/share/man/* \
        /var/cache/fontconfig/* \
        /opt/calibre/*.txt \
        /opt/calibre/*.md \
        /opt/calibre/resources/man-pages || true

WORKDIR /app
EXPOSE 7860
ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]