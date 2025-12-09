###############################
#         STAGE 1: BUILD
###############################
ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim
FROM ${BASE} AS build

MAINTAINER Ebbok2Audiobook version: 25.12.9

# Build-time ARGs
ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

# ENV
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .
RUN chmod +x ebook2audiobook.sh

# --- Install OS build dependencies ---
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends --allow-change-held-packages \
        gcc g++ make python3-dev pkg-config git wget bash xz-utils \
        libglib2.0-0 libnss3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 \
        libx11-6 libegl1 libopengl0 libxrender1 libxext6 libxi6 libxcb1 \
        ${DOCKER_PROGRAMS_STR} tesseract-ocr-${ISO3_LANG} || true && \
    rm -rf /var/lib/apt/lists/*

# --- Run build script ---
RUN --mount=type=cache,target=/root/.cache/pip \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# --- Install Calibre ---
RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh \
 && bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

# --- Cleanup build stage ---
RUN find /usr -type d -name "__pycache__" -exec rm -rf {} + && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/* /usr/share/icons/* && \
    rm -rf /usr/share/fonts/* /var/cache/fontconfig/* && \
    rm -rf /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages || true && \
    find /app -type d -name "__pycache__" -exec rm -rf {} + || true

###############################
#       STAGE 2: RUNTIME
###############################
FROM python:${PYTHON_VERSION}-slim AS runtime

# Runtime ENV
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_CPU_FALLBACK=1

WORKDIR /app

############################################
#      MINIMAL COPY FROM BUILD STAGE
############################################

# Python site-packages only (pip installs from build)
COPY --from=build /usr/local/lib/python3.*/ /usr/local/lib/

# Calibre runtime
COPY --from=build /opt/calibre /opt/calibre

# Your application files
COPY --from=build /app /app

#######################################################
#  GPU Auto-Detection: CUDA (nvcc), ROCm, Intel XPU
#######################################################

EXPOSE 7860

ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]