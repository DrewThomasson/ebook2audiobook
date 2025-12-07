ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim-bookworm

############################
# BUILD STAGE
############################
FROM ${BASE} AS build

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    CALIBRE_DISABLE_CHECKS=1 \
    CALIBRE_DISABLE_GUI=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install build + runtime deps that calibre and your tools need
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc g++ make python3-dev pkg-config curl wget xz-utils bash git \
        libegl1 libopengl0 libx11-6 libglib2.0-0 libnss3 libdbus-1-3 \
        libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 libgomp1 \
        libfontconfig1 libsndfile1 libxrender1 libxext6 libxi6 libxcb1 \
        ${DOCKER_PROGRAMS_STR}; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy absolutely everything (exactly like you need)
COPY . /app

RUN chmod +x /app/ebook2audiobook.sh

# Your script runs with full access to the entire repo
RUN --mount=type=cache,target=/root/.cache/pip \
    /app/ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# Install calibre
RUN set -ex; \
    wget -nv "${CALIBRE_INSTALLER_URL}" -O /tmp/calibre-installer.sh; \
    bash /tmp/calibre-installer.sh; \
    rm -f /tmp/calibre-installer.sh

# Remove only the heavy build tools (calibre and your code stay!)
RUN apt-get purge -y --auto-remove \
        gcc g++ make python3-dev pkg-config git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

############################
# RUNTIME IMAGE
############################
FROM ${BASE}

ARG DOCKER_PROGRAMS_STR
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    CALIBRE_DISABLE_CHECKS=1 \
    CALIBRE_DISABLE_GUI=1 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:/root/.cargo/bin:/opt/calibre:/usr/local/bin:/usr/bin:/bin:${PATH}"

# Install only runtime packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libegl1 libopengl0 libx11-6 libglib2.0-0 libnss3 libdbus-1-3 \
        libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 \
        libfontconfig1 libsndfile1 libxrender1 libxext6 libxi6 libxcb1 \
        ${DOCKER_PROGRAMS_STR} \
        tesseract-ocr tesseract-ocr-${ISO3_LANG} || true; \
    rm -rf /var/lib/apt/lists/*

# Copy calibre + its root-local binaries
COPY --from=build /opt/calibre /opt/calibre
COPY --from=build /root/.local /root/.local
COPY --from=build /root/.cargo /root/.cargo

# Copy your entire project (all folders: assets, ebooks, voices, models, etc.)
COPY --from=build /app /app

WORKDIR /app
EXPOSE 7860

ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]