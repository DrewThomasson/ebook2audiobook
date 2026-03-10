ARG PYTHON_VERSION=3.12

# ============================================================
# SINGLE STAGE — BUILD + RUNTIME
# ============================================================
FROM python:${PYTHON_VERSION}-slim-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG PYTHON_VERSION=3.12
ARG APP_VERSION=26.3.10
ARG DEVICE_TAG=cu128
ARG DOCKER_DEVICE_STR='{"name": "cu128", "os": "manylinux_2_28", "arch": "x86_64", "pyvenv": [3, 12], "tag": "cu128", "note": "default device"}'
ARG DOCKER_PROGRAMS_STR="curl ffmpeg mediainfo nodejs npm espeak-ng sox tesseract-ocr"
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng
ARG INSTALL_RUST=1

ENV DOCKER_DEVICE_STR=${DOCKER_DEVICE_STR}

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
	PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# System packages (build + runtime)
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends --allow-change-held-packages \
		gcc g++ make pkg-config cmake curl wget git bash xz-utils python3-dev \
		fontconfig libfontconfig1 libfreetype6 libgl1 libegl1 libopengl0 \
		libx11-6 libxext6 libxrender1 libxcb1 libxcb-render0 libxcb-shm0 libxcb-xfixes0 libxcb-cursor0 \
		libgomp1 libsndfile1 \
		${DOCKER_PROGRAMS_STR} tesseract-ocr-${ISO3_LANG}; \
	rm -rf /var/lib/apt/lists/*

# Optional Rust toolchain
RUN if [ "${INSTALL_RUST}" = "1" ]; then \
		curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable; \
	else \
		echo "Skipping Rust toolchain"; \
	fi

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

RUN pip install --upgrade pip setuptools wheel

COPY ebook2audiobook.command /app/ebook2audiobook.sh
RUN chmod 755 /app/ebook2audiobook.sh
COPY . /app

# Ensure Unix line endings
RUN find /app -type f \( -name "*.sh" -o -name "*.command" \) -exec sed -i 's/\r$//' {} \;

# Build dependencies via project script
RUN ./ebook2audiobook.command --script_mode build_docker --docker_device "$DOCKER_DEVICE_STR"

# Cleanup build-only packages and Rust toolchain to shrink the image
RUN set -eux; \
	apt-get update; \
	apt-get purge -y --auto-remove gcc g++ make pkg-config cmake wget git xz-utils python3-dev; \
	rm -rf /var/lib/apt/lists/* /root/.cargo /root/.rustup /tmp/*

VOLUME \
	/app/ebooks \
	/app/audiobooks \
	/app/models \
	/app/voices \
	/app/tmp

EXPOSE 7860

ENTRYPOINT ["python3", "-u", "app.py"]
CMD ["--script_mode", "full_docker"]