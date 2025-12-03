ARG BASE=python:3.12-slim
FROM ${BASE}

ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"
ENV CALIBRE_DISABLE_CHECKS=1
ENV CALIBRE_DISABLE_GUI=1

WORKDIR /app
COPY . /app
RUN chmod +x /app/ebook2audiobook.sh

RUN set -ex && \
	BUILD_DEPS="gcc g++ make build-essential python3-dev pkg-config cargo rustc" && \
	RUNTIME_DEPS="wget xz-utils bash git \
		libegl1 libopengl0 \
		libx11-6 libglib2.0-0 libnss3 libdbus-1-3 \
		libatk1.0-0 libgdk-pixbuf-2.0-0 \
		libxcb-cursor0 \
		tesseract-ocr tesseract-ocr-$ISO3_LANG \
		$DOCKER_PROGRAMS_STR" && \
	apt-get update && \
	apt-get install -y --no-install-recommends --allow-change-held-packages \
		$BUILD_DEPS \
		$RUNTIME_DEPS && \
	wget -nv -O- "$CALIBRE_INSTALLER_URL" | sh /dev/stdin && \
	echo "Building image for Ebook2Audiobook on Linux Debian Slim" && \
	/app/ebook2audiobook.sh --script_mode build_docker --docker_device "$DOCKER_DEVICE_STR" && \
	apt-get purge -y $BUILD_DEPS && \
	apt-get autoremove -y --purge && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

EXPOSE 7860
ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]