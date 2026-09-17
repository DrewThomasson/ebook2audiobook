ARG PYTHON_VERSION=3.12

# ============================================================
# SINGLE STAGE — BUILD + RUNTIME
# ============================================================
# trixie, not bookworm:
# Intel's NEO/IGC debs are built on Ubuntu 24.04 and need
# glibc >= 2.38 / libstdc++ >= 13.1. bookworm is 2.36 / 12.2
# and cannot host them, and its Level Zero loader (libze1 1.8.12)
# predates zesInit.
FROM python:${PYTHON_VERSION}-slim-trixie

ARG APP_VERSION=26.9.17
ARG DEVICE_TAG=cu130
ARG DOCKER_DEVICE_STR='{ "name": "cuda", "os": "manylinux_2_28", "arch": "x86_64", "pyvenv": [3, 12], "tag": "cu130", "note": "default device" }'
ARG DOCKER_PROGRAMS_STR="curl ffmpeg mediainfo nodejs npm espeak-ng sox tesseract-ocr"
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng
ARG INSTALL_RUST=1

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=utf-8 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    DOCKER_DEVICE_STR=${DOCKER_DEVICE_STR} \
    DEVICE_TAG=${DEVICE_TAG} \
    TTS_CACHE=/app/models \
    TESSDATA_PREFIX=/app/models/tessdata \
    TMPDIR=/app/run \
    PATH="/root/.local/bin:/root/.cargo/bin:${PATH}" \
    IN_DOCKER=1

# uv is required because device_installer.py now calls `uv pip ...`.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Runtime directories.
RUN set -eux; \
    mkdir -p \
        /app/ebooks \
        /app/audiobooks \
        /app/models \
        /app/models/tessdata \
        /app/voices \
        /app/run \
        /app/tmp; \
    chmod -R 777 /app/ebooks /app/audiobooks /app/models /app/voices /app/run /app/tmp

# System packages.
#
# DOCKER_PROGRAMS_STR is passed by the build script when available.
# tesseract-ocr-[lang] and calibre are handled below.
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		ca-certificates \
		wget \
		git \
		xz-utils \
		build-essential \
		gcc \
		g++ \
		make \
		pkg-config \
		cmake \
		python3-dev \
		libgomp1 \
		libglib2.0-0 \
		libgl1 \
		libsndfile1 \
		libstdc++6 \
		libgcc-s1 \
		libegl1 \
		libopengl0 \
		libxcb-cursor0 \
		libxcb-xinerama0 \
		libxkbcommon-x11-0 \
		${DOCKER_PROGRAMS_STR}; \
	if [ -n "${ISO3_LANG}" ]; then \
		apt-get install -y --no-install-recommends "tesseract-ocr-${ISO3_LANG}" || true; \
	fi; \
	rm -rf /var/lib/apt/lists/*

# Calibre.
#
# calibre is intentionally not part of DOCKER_PROGRAMS_STR because the package
# manager version is often too old; use the upstream installer.
RUN set -eux; \
    if ! command -v ebook-convert >/dev/null 2>&1; then \
        wget -nv -O- "${CALIBRE_INSTALLER_URL}" | sh /dev/stdin; \
    fi; \
    ebook-convert --version

# Rust / cargo.
#
# Some Python packages still need a Rust toolchain at build time.
# It is removed again after the Python dependency build.
RUN set -eux; \
    if [ "${INSTALL_RUST}" = "1" ]; then \
        curl -fsSL https://sh.rustup.rs | sh -s -- -y; \
    fi

# Bootstrap minimal Python build tooling with uv.
#
# Do not upgrade pip here. The application now uses uv for package installation.
RUN set -eux; \
    uv pip install --system --no-cache 'setuptools<82' wheel

COPY . /app

# Make sure the launcher exists.
#
# Historical builds use ebook2audiobook.command. Some checkouts may have e2a.sh
# or ebook2audiobook.sh only, so create a compatible launcher if needed.
RUN set -eux; \
    if [ -f ./ebook2audiobook.command ]; then \
        chmod +x ./ebook2audiobook.command; \
    elif [ -f ./e2a.sh ]; then \
        chmod +x ./e2a.sh; \
        ln -sf ./e2a.sh ./ebook2audiobook.command; \
    elif [ -f ./ebook2audiobook.sh ]; then \
        chmod +x ./ebook2audiobook.sh; \
        ln -sf ./ebook2audiobook.sh ./ebook2audiobook.command; \
    else \
        echo "No launcher found: expected ebook2audiobook.command, e2a.sh, or ebook2audiobook.sh"; \
        exit 1; \
    fi

# Build the Python stack selected by DOCKER_DEVICE_STR.
#
# This calls device_installer.py, which now uses uv internally:
#   uv pip install --python <interpreter> ...
RUN set -eux; \
    ./ebook2audiobook.command --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"; \
    rustup self uninstall -y 2>/dev/null || true; \
    apt-get update; \
    apt-get purge -y --auto-remove \
        gcc \
        g++ \
        make \
        pkg-config \
        cmake \
        wget \
        git \
        xz-utils \
        python3-dev \
        build-essential || true; \
    rm -rf \
        /var/lib/apt/lists/* \
        /root/.cargo \
        /root/.rustup \
        /tmp/* \
        /app/tmp/* \
        /app/run/* || true

VOLUME ["/app/ebooks", "/app/audiobooks", "/app/models", "/app/voices", "/app/run", "/app/tmp"]

EXPOSE 7860

ENTRYPOINT ["bash", "ebook2audiobook.command", "--script_mode", "full_docker"]