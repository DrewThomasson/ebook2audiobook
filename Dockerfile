ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

LABEL org.opencontainers.image.title="ebook2audiobook" \
      org.opencontainers.image.description="Generate audiobooks from e-books, voice cloning & 1158 languages" \
      org.opencontainers.image.version="25.12.10" \
      org.opencontainers.image.authors="Ebbok2Audiobook" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/DrewThomasson/ebook2audiobook"

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONWARNINGS="ignore::SyntaxWarning" \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-change-held-packages \
        gcc g++ make python3-dev pkg-config git wget bash xz-utils \
        libegl1 libopengl0 libgl1 \
        libxcb1 libx11-6 libxcb-cursor0 libxcb-render0 libxcb-shm0 libxcb-xfixes0 \
        ${DOCKER_PROGRAMS_STR} \
        tesseract-ocr-${ISO3_LANG} || true && \
    rm -rf /var/lib/apt/lists/*

RUN if [ "$(dpkg --print-architecture)" = "arm64" ]; then \
        dpkg --add-architecture arm64 && \
        apt-get update && \
        apt-get install -y --no-install-recommends libc6-dev:arm64 && \
        rm -rf /var/lib/apt/lists/*; \
    fi

RUN if [ "$(dpkg --print-architecture)" = "arm64" ]; then \
        export PIP_PLATFORM=linux_aarch64; \
    fi

RUN chmod +x ebook2audiobook.sh && \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

RUN set -eux; \
    find /usr /app -type d -name "__pycache__" -exec rm -rf {} +; \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/*; \
    rm -rf /usr/share/icons/* /usr/share/fonts/* /var/cache/fontconfig/*; \
    rm -rf /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages || true; \
    apt-get purge -y --auto-remove gcc g++ make python3-dev pkg-config git; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

RUN mkdir -p /app/audiobooks && chmod 777 /app/audiobooks
VOLUME /app/audiobooks

EXPOSE 7860
ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]