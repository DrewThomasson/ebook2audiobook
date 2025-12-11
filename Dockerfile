ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG APP_VERSION=25.12.12
ARG DEVICE_TAG=cpu
ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

LABEL org.opencontainers.image.title="ebook2audiobook" \
      org.opencontainers.image.description="Generate audiobooks from e-books, voice cloning & 1158 languages!" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.authors="Drew Thomasson / Rob McDowell" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/DrewThomasson/ebook2audiobook"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONWARNINGS="ignore::SyntaxWarning" \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-change-held-packages \
        gcc g++ make python3-dev pkg-config git wget bash xz-utils \
        libegl1 libopengl0 libgl1 \
        libxcb1 libx11-6 libxcb-cursor0 libxcb-render0 libxcb-shm0 libxcb-xfixes0 \
        ${DOCKER_PROGRAMS_STR} \
        tesseract-ocr-${ISO3_LANG} || true && \
    rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    . "$HOME/.cargo/env"
	
RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

RUN case "${DEVICE_TAG}" in \
        jetson51*) \
            echo "JetPack 5.1.x → copying CUDA 11.4 libs" && \
            CUDA_LIB_DIR="/usr/local/cuda-11.4/lib64" && \
            mkdir -p "$CUDA_LIB_DIR" && \
            cp -P /usr/lib/aarch64-linux-gnu/libcuda* \
                  /usr/lib/aarch64-linux-gnu/libcudart.so.11.0 \
                  /usr/lib/aarch64-linux-gnu/libcublas* \
                  /usr/lib/aarch64-linux-gnu/libcufft* \
                  /usr/lib/aarch64-linux-gnu/libcurand* \
                  /usr/lib/aarch64-linux-gnu/libcusparse* \
                  "$CUDA_LIB_DIR/" 2>/dev/null || true && \
            echo "LD_LIBRARY_PATH=$CUDA_LIB_DIR:\${LD_LIBRARY_PATH}" > /etc/profile.d/jetpack51-cuda.sh ;; \
        jetson60*|jetson61*) \
            echo "JetPack 6.x → no extra CUDA fix needed" ;; \
    esac

ENV LD_LIBRARY_PATH=/usr/local/cuda-11.4/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

RUN chmod +x ebook2audiobook.sh && \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

RUN set -eux; \
    find /usr /app -type d -name "__pycache__" -exec rm -rf {} +; \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/* \
           /usr/share/icons/* /usr/share/fonts/* /var/cache/fontconfig/* \
           /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages \
           /root/.cache /tmp/* $HOME/.rustup $HOME/.cargo || true; \
    apt-get purge -y --auto-remove gcc g++ make python3-dev pkg-config git; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/audiobooks && chmod 777 /app/audiobooks
VOLUME /app/audiobooks

EXPOSE 7860
ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]