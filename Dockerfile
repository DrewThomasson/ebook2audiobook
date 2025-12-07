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

ENV DEBIAN_FRONTEND=noninteractive
ENV CALIBRE_DISABLE_CHECKS=1
ENV CALIBRE_DISABLE_GUI=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:/root/.cargo/bin:/opt/calibre:/usr/local/bin:/usr/bin:${PATH}"

RUN set -ex && apt-get update
RUN apt-get install -y --no-install-recommends --allow-change-held-packages gcc g++ make python3-dev pkg-config curl wget xz-utils bash git libegl1 libopengl0 libx11-6 libglib2.0-0 libnss3 libdbus-1-3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0
RUN chmod +x /app/ebook2audiobook.sh
RUN /bin/bash -c "/app/ebook2audiobook.sh --script_mode build_docker --docker_device '${DOCKER_DEVICE_STR}'"
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

############################
# RUNTIME IMAGE
############################
FROM ${BASE}

ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL
ARG ISO3_LANG

ENV DEBIAN_FRONTEND=noninteractive
ENV CALIBRE_DISABLE_CHECKS=1
ENV CALIBRE_DISABLE_GUI=1
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV PATH="/root/.local/bin:/root/.cargo/bin:/opt/calibre:/usr/local/bin:/usr/bin:${PATH}"

RUN set -ex && apt-get update && apt-get install -y --no-install-recommends --allow-change-held-packages libgomp1 libfontconfig1 libsndfile1 libxrender1 libxext6 libxi6 libxcb1 ${DOCKER_PROGRAMS_STR} tesseract-ocr-${ISO3_LANG}
RUN wget -nv -O- "${CALIBRE_INSTALLER_URL}" | sh /dev/stdin
RUN apt-get purge -y --auto-remove
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/ /usr/local/
COPY --from=build /app /app

WORKDIR /app
EXPOSE 7860
ENTRYPOINT ["python3","app.py","--script_mode","full_docker"]