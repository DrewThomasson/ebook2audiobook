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
        gcc g++ make python3-dev python3-pip pkg-config curl wget xz-utils bash git \
        libegl1 libopengl0 libx11-6 libglib2.0-0 libnss3 libdbus-1-3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 \
        tesseract-ocr tesseract-ocr-$ISO3_LANG $DOCKER_PROGRAMS_STR && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && . "$HOME/.cargo/env" && \
    wget -nv -O- "$CALIBRE_INSTALLER_URL" | sh /dev/stdin

# Add calibre binaries to PATH
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