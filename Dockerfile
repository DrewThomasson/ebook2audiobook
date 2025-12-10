ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim-bookworm

FROM ${BASE}

MAINTAINER Ebbok2Audiobook version: 25.12.10

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY . .

# OS deps (no explicit Qt/X11/GTK – Calibre brings its own Qt in /opt/calibre)
RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-change-held-packages \
        gcc g++ make python3-dev pkg-config git wget bash xz-utils \
        ${DOCKER_PROGRAMS_STR} \
        tesseract-ocr-${ISO3_LANG} || true && \
    rm -rf /var/lib/apt/lists/*

RUN chmod +x ebook2audiobook.sh
RUN ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# Install Calibre (CLI tools incl. ebook-convert; its own Qt lives in /opt/calibre)
RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

# Cleanup to shrink image
RUN set -eux; \
    find /usr /app -type d -name "__pycache__" -exec rm -rf {} +; \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/*; \
    rm -rf /usr/share/icons/* /usr/share/fonts/* /var/cache/fontconfig/*; \
    rm -rf /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages || true; \
    apt-get purge -y --auto-remove gcc g++ make python3-dev pkg-config git; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

EXPOSE 7860
ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]
