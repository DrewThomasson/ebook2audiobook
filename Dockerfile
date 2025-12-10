ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-alpine

FROM ${BASE}

MAINTAINER Ebbok2Audiobook version: 25.12.10

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN chmod +x ebook2audiobook.sh

RUN apk add --no-cache \
    bash gcc g++ make python3-dev pkgconfig git wget xz \
    glib libx11 mesa-gl mesa-egl mesa-gbm fontconfig libgomp libsndfile \
    curl ffmpeg nodejs espeak-ng sox tesseract-ocr tesseract-ocr-data-eng || true && \
    rm -rf /var/cache/apk/*

# This single line fixes pymupdf-layout (and many other wheels) on Alpine
RUN apk add --no-cache --virtual .build-deps build-base && \
    pip install --no-cache-dir --upgrade pip setuptools wheel

RUN ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

RUN find /usr -type d -name "__pycache__" -exec rm -rf {} + && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/* && \
    rm -rf /usr/share/icons/* /usr/share/fonts/* /var/cache/fontconfig/* && \
    rm -rf /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages || true && \
    find /app -type d -name "__pycache__" -exec rm -rf {} + || true

RUN apk del gcc g++ make python3-dev pkgconfig git .build-deps && \
    rm -rf /var/cache/apk/* /tmp/* /root/.cache

EXPOSE 7860

ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]