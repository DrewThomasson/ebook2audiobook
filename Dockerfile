ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim

############################
# BUILD STAGE
############################
FROM ${BASE} AS build

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG

ENV DEBIAN_FRONTEND=noninteractive \
    CALIBRE_DISABLE_CHECKS=1 \
    CALIBRE_DISABLE_GUI=1 \
    PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

RUN set -ex && \
    apt-get update && \
    apt-get install -y --allow-change-held-packages --no-install-recommends \
        gcc g++ make python3-dev pkg-config curl wget xz-utils bash git \
        libegl1 libopengl0 libx11-6 libglib2.0-0 libnss3 libdbus-1-3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 \
        tesseract-ocr tesseract-ocr-$ISO3_LANG $DOCKER_PROGRAMS_STR \
		fonts-dejavu-core fonts-liberation2 fonts-noto-core fonts-noto-extra fonts-noto-mono \
		fonts-noto-cjk fonts-noto-cjk-extra fonts-ipafont-gothic fonts-ipafont-mincho \
		fonts-noto-arabic fonts-noto-naskh-arabic fonts-noto-kufi-arabic fonts-noto-hebrew fonts-noto-syriac fonts-noto-armenian fonts-noto-georgian \
		fonts-noto-devanagari fonts-noto-bengali fonts-noto-gujarati fonts-noto-gurmukhi fonts-noto-oriya fonts-noto-tamil fonts-noto-telugu fonts-noto-kannada fonts-noto-malayalam \
		fonts-noto-thai fonts-noto-lao fonts-noto-khmer fonts-noto-buhid fonts-noto-tagbanwa fonts-noto-batak fonts-noto-balinese fonts-noto-javanese \
		fonts-noto-ethiopic fonts-noto-tifinagh fonts-noto-cherokee fonts-noto-osage fonts-STIX fonts-STIX-two \
		fonts-noto-math fonts-noto-color-emoji fonts-symbola && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    . "$HOME/.cargo/env" && \
    wget -nv -O- "$CALIBRE_INSTALLER_URL" | sh /dev/stdin

ENV PATH="/root/.local/bin:/root/.cargo/bin:/opt/calibre:/usr/local/bin:/usr/bin:${PATH}"

WORKDIR /app
COPY . /app
RUN chmod +x /app/ebook2audiobook.sh

RUN /bin/bash -c "/app/ebook2audiobook.sh --script_mode build_docker --docker_device '${DOCKER_DEVICE_STR}'"

############################
# RUNTIME IMAGE
############################
FROM ${BASE}

ENV DEBIAN_FRONTEND=noninteractive \
    CALIBRE_DISABLE_CHECKS=1 \
    CALIBRE_DISABLE_GUI=1 \
    PATH="/root/.local/bin:/root/.cargo/bin:/opt/calibre:/usr/local/bin:/usr/bin:${PATH}"

# Copy all runtime binaries
COPY --from=build /usr/bin/ /usr/bin/
COPY --from=build /usr/local/ /usr/local/
COPY --from=build /opt/calibre/ /opt/calibre/
COPY --from=build /app /app

WORKDIR /app
EXPOSE 7860
ENTRYPOINT ["python3","app.py","--script_mode","full_docker"]