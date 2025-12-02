ARG BASE=python:3.12-slim
FROM ${BASE}

ARG DOCKER_DEVICE
ARG DOCKER_PROGRAMS
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"
ENV CALIBRE_DISABLE_CHECKS=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends --allow-change-held-packages \
      wget xz-utils bash git \
      libegl1 libopengl0 \
      libx11-6 libglib2.0-0 libnss3 libdbus-1-3 \
      libatk1.0-0 libgdk-pixbuf-2.0-0 \
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