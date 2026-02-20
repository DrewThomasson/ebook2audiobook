ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG APP_VERSION=26.2.19
ARG DEVICE_TAG=cu128
ARG DOCKER_DEVICE_STR='{"name": "cu128", "os": "manylinux_2_28", "arch": "x86_64", "pyvenv": [3, 12], "tag": "cu128", "note": "default device"}'
ARG DOCKER_PROGRAMS_STR="curl ffmpeg nodejs npm espeak-ng sox tesseract-ocr"
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
	PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends --allow-change-held-packages\
		gcc g++ make pkg-config cmake \
		curl wget git bash \
		fontconfig libfontconfig1 libfreetype6 \
		libgl1 libegl1 libopengl0 \
		libx11-6 libxext6 libxrender1 \
		libxcb1 libxcb-render0 libxcb-shm0 libxcb-xfixes0 libxcb-cursor0 \
		libgomp1 libsndfile1 \
		python3-dev \
		${DOCKER_PROGRAMS_STR} \
		tesseract-ocr-${ISO3_LANG}; \
	rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Optional Rust toolchain
# ------------------------------------------------------------
RUN if [ "${INSTALL_RUST}" = "1" ]; then \
		curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable; \
	else \
		echo "Skipping Rust toolchain"; \
	fi

# ------------------------------------------------------------
# Calibre (CLI use)
# ------------------------------------------------------------
RUN set -eux; \
	wget -nv "${CALIBRE_INSTALLER_URL}" -O /tmp/calibre.sh; \
	bash /tmp/calibre.sh; \
	rm -f /tmp/calibre.sh

# ------------------------------------------------------------
# Debian-compatible Calibre library aliases
# ------------------------------------------------------------
RUN set -eux; \
	ln -sf /usr/lib/*-linux-gnu/libfreetype.so.6 /usr/lib/libfreetype.so.6; \
	ln -sf /usr/lib/*-linux-gnu/libfontconfig.so.1 /usr/lib/libfontconfig.so.1; \
	ln -sf /usr/lib/*-linux-gnu/libpng16.so.16 /usr/lib/libpng16.so.16; \
	ln -sf /usr/lib/*-linux-gnu/libX11.so.6 /usr/lib/libX11.so.6; \
	ln -sf /usr/lib/*-linux-gnu/libXext.so.6 /usr/lib/libXext.so.6; \
	ln -sf /usr/lib/*-linux-gnu/libXrender.so.1 /usr/lib/libXrender.so.1

RUN pip install --upgrade pip setuptools wheel

VOLUME \
	/app/audiobooks \
	/app/voices \
	/app/models \
	/app/tmp \
	/app/ebooks

COPY ebook2audiobook.command /app/ebook2audiobook.sh
RUN chmod +x /app/ebook2audiobook.sh

COPY . /app

# Ensure Unix line endings
RUN find /app -type f \( -name "*.sh" -o -name "*.command" \) -exec sed -i 's/\r$//' {} \;

# ------------------------------------------------------------
# Build dependencies via project script
# ------------------------------------------------------------
RUN ./ebook2audiobook.command --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# ------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------
RUN set -eux; \
	find /usr /app -type d -name "__pycache__" -exec rm -rf {} +; \
	rm -rf \
		/usr/share/doc/* \
		/usr/share/man/* \
		/usr/share/locale/* \
		/usr/share/icons/* \
		/usr/share/fonts/* \
		/var/cache/fontconfig/* \
		/opt/calibre/*.txt \
		/opt/calibre/*.md \
		/opt/calibre/resources/man-pages \
		/root/.cache \
		/tmp/* \
		$HOME/.cargo \
		$HOME/.rustup || true; \
	apt-get purge -y --auto-remove gcc g++ make pkg-config python3-dev git; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/*

EXPOSE 7860

ENTRYPOINT ["python3", "-u", "app.py"]
CMD ["--script_mode", "full_docker"]