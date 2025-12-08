ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim-bookworm

# ========================= BUILD STAGE =========================
FROM ${BASE} AS build

MAINTAINER Ebbok2Audiobook version: 25.12.9

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked --mount=type=cache,target=/root/.cache \
    set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends --allow-change-held-packages gcc g++ make python3-dev pkg-config git wget bash xz-utils libglib2.0-0 libnss3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 libx11-6 libegl1 libopengl0 libxrender1 libxext6 libxi6 libxcb1
    apt-get install -y --no-install-recommends --allow-change-held-packages ${DOCKER_PROGRAMS_STR}
    apt-get install -y --no-install-recommends tesseract-ocr-${ISO3_LANG} || true
RUN rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip /app/ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# Install calibre (latest stable)
RUN set -ex
RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

# Remove everything that is NOT needed at runtime
RUN apt-get purge -y --auto-remove gcc g++ make python3-dev pkg-config git && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

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

# 2. Remove documentation, man pages, locales, icons, etc. (saves ~40–70 MB)
RUN set -ex; \
    find /usr -type d -name "__pycache__" -exec rm -rf {} +; \
    rm -rf \
        /usr/share/doc/* \
        /usr/share/man/* \
		/usr/share/locale/* \
        /usr/share/icons/* \
        /usr/share/fonts/* \
        /var/cache/fontconfig/* \
        /opt/calibre/*.txt \
        /opt/calibre/*.md \
        /opt/calibre/resources/man-pages || true
RUN find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

WORKDIR /app
COPY --from=build . /app

EXPOSE 7860

ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]