ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

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

# ----------------------------------------
# Install ONLY required system packages
# ----------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-change-held-packages \
        gcc g++ make python3-dev pkg-config git wget bash xz-utils \
        # Tiny OpenGL platform libs (required for Calibre installer)
        libegl1 libopengl0 libgl1 \
        # User-supplied tools
        ${DOCKER_PROGRAMS_STR} \
        tesseract-ocr-${ISO3_LANG} || true && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------
# Build Python dependencies via your script
# ----------------------------------------
RUN chmod +x ebook2audiobook.sh && \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# ----------------------------------------
# Install Calibre (CLI only, GUI unused)
# ----------------------------------------
RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

# ----------------------------------------
# Clean up everything not needed at runtime
# ----------------------------------------
RUN set -eux; \
    # Remove Python caches
    find /usr /app -type d -name "__pycache__" -exec rm -rf {} +; \
    # Remove unnecessary OS documentation & translations
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/*; \
    # Remove icons, fonts, fontconfig cache
    rm -rf /usr/share/icons/* /usr/share/fonts/* /var/cache/fontconfig/*; \
    # Remove unused Calibre docs
    rm -rf /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages || true; \
    # Purge build tools
    apt-get purge -y --auto-remove gcc g++ make python3-dev pkg-config git; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

EXPOSE 7860

ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]
