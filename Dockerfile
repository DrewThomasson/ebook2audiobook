ARG PYTHON_VERSION=3.12

# ============================================================
# SINGLE STAGE — BUILD + RUNTIME
# ============================================================
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG APP_VERSION=26.4.30
ARG DEVICE_TAG=cu130
ARG DOCKER_DEVICE_STR='{"name": "cu130", "os": "manylinux_2_28", "arch": "x86_64", "pyvenv": [3, 12], "tag": "cu130", "note": "default device"}'
ARG DOCKER_PROGRAMS_STR="curl ffmpeg mediainfo nodejs npm espeak-ng sox tesseract-ocr"
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng
ARG INSTALL_RUST=1

LABEL org.opencontainers.image.title="ebook2audiobook" \
	org.opencontainers.image.description="Generate audiobooks from e-books, voice cloning & 1158 languages!" \
	org.opencontainers.image.version="${APP_VERSION}" \
	org.opencontainers.image.authors="Drew Thomasson / Rob McDowell" \
	org.opencontainers.image.licenses="MIT" \
	org.opencontainers.image.source="https://github.com/DrewThomasson/ebook2audiobook"

ENV DEBIAN_FRONTEND=noninteractive \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	DOCKER_DEVICE_STR=${DOCKER_DEVICE_STR} \
	PIP_BREAK_SYSTEM_PACKAGES=1 \
	PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# System packages (build + runtime)
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends --allow-change-held-packages \
		gcc g++ make pkg-config cmake curl wget git bash xz-utils python3-dev \
		fontconfig libfontconfig1 libfreetype6 libgl1 libegl1 libopengl0 \
		libx11-6 libxext6 libxrender1 libxcb1 libxcb-render0 libxcb-shm0 \
		libxcb-xfixes0 libxcb-cursor0 libgomp1 libsndfile1 \
		${DOCKER_PROGRAMS_STR} tesseract-ocr-${ISO3_LANG}; \
	rm -rf /var/lib/apt/lists/*
	
RUN find /usr/local/lib/python3.12/site-packages/pip* -type f -delete 2>/dev/null; \
    find /usr/local/lib/python3.12/site-packages/pip* -type l -delete 2>/dev/null; \
    curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && \
    python3 /tmp/get-pip.py --ignore-installed && \
    rm -f /tmp/get-pip.py && \
    pip install --no-cache-dir setuptools wheel

# Rust toolchain
RUN bash -o pipefail -c '\
	if [ "${INSTALL_RUST}" = "1" ]; then \
		curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable; \
	else \
		echo "Skipping Rust toolchain"; \
	fi'

# Calibre (CLI)
RUN set -eux; \
	wget -nv "${CALIBRE_INSTALLER_URL}" -O /tmp/calibre.sh; \
	bash /tmp/calibre.sh; \
	rm -f /tmp/calibre.sh

# Debian-compatible Calibre library aliases
RUN set -eux; \
	ln -sf /usr/lib/*-linux-gnu/libfreetype.so.6 /usr/lib/libfreetype.so.6; \
	ln -sf /usr/lib/*-linux-gnu/libfontconfig.so.1 /usr/lib/libfontconfig.so.1; \
	ln -sf /usr/lib/*-linux-gnu/libpng16.so.16 /usr/lib/libpng16.so.16; \
	ln -sf /usr/lib/*-linux-gnu/libX11.so.6 /usr/lib/libX11.so.6; \
	ln -sf /usr/lib/*-linux-gnu/libXext.so.6 /usr/lib/libXext.so.6; \
	ln -sf /usr/lib/*-linux-gnu/libXrender.so.1 /usr/lib/libXrender.so.1

COPY . /app

# Ensure Unix line endings
RUN find /app -type f \( -name "*.sh" -o -name "*.command" \) -exec sed -i 's/\r$//' {} \;

# Build dependencies via project script
RUN ./ebook2audiobook.command --script_mode build_docker --docker_device "$DOCKER_DEVICE_STR"

# Cleanup build-only packages and Rust toolchain to shrink the image
RUN set -eux; \
    rustup self uninstall -y 2>/dev/null || true; \
    apt-get update; \
    apt-get purge -y --auto-remove gcc g++ make pkg-config cmake wget git xz-utils python3-dev; \
    rm -rf /var/lib/apt/lists/* /root/.cargo /root/.rustup /tmp/* || true

VOLUME \
	/app/ebooks \
	/app/audiobooks \
	/app/models \
	/app/voices \
	/app/run \
	/app/tmp

EXPOSE 7860

ENTRYPOINT ["bash", "ebook2audiobook.command"]
CMD ["--script_mode", "full_docker"]