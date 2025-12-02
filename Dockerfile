ARG BASE=python:3.12-slim
FROM ${BASE}

ARG DOCKER_DEVICE
ARG DOCKER_PROGRAMS
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update \
 && apt-get install -y \
      wget xz-utils bash git \
      libgl1 libegl1 libxcb1 libxkbcommon0 libdbus-1-3 \
      tesseract-ocr tesseract-ocr-$ISO3_LANG \
 && apt-get install -y $DOCKER_PROGRAMS \
 && wget -nv -O- "$CALIBRE_INSTALLER_URL" | sh /dev/stdin \
 && ln -s /opt/calibre/ebook-convert /usr/bin/ebook-convert \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN chmod +x ebook2audiobook.sh

RUN echo "Building image for: $DOCKER_DEVICE"
RUN ./ebook2audiobook.sh --script_mode build_docker --docker_device "$DOCKER_DEVICE"

EXPOSE 7860
ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]