ARG BASE=python:3.12-slim
FROM ${BASE}

ARG DOCKER_DEVICE
ARG DOCKER_PROGRAMS
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update \
 && apt-get install -y --no-install-recommends --allow-change-held-packages \
      wget xz-utils bash git \
      libgl1 libegl1 libopengl0 libglu1-mesa \
      libxrender1 libfontconfig1 libxcomposite1 \
      libxi6 libxtst6 libsm6 libice6 libdbus-1-3 \
      libxcb1 libxcb-cursor0 libxcb-xinerama0 libxcb-shape0 libxrandr2 \
      libxdamage1 libxfixes3 libx11-xcb1 \
      libatk1.0-0 libgtk-3-0 libgdk-pixbuf2.0-0 libglib2.0-0 \
      libnss3 libasound2 \
      tesseract-ocr tesseract-ocr-$ISO3_LANG \
 && apt-get install -y --no-install-recommends --allow-change-held-packages \
      $DOCKER_PROGRAMS \
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