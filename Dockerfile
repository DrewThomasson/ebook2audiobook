ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG APP_VERSION=25.12.12
LABEL org.opencontainers.image.title="ebook2audiobook" \
      org.opencontainers.image.description="Generate audiobooks from e-books, voice cloning & 1158 languages!" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.authors="Drew Thomasson / Rob McDowell" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/DrewThomasson/ebook2audiobook"

ARG DEVICE_TAG=cpu
ARG DOCKER_DEVICE_STR='{"name": "cpu", "os": "linux", "arch": "x86_64", "pyvenv": [3, 12], "tag": "cpu", "note": ""}'
ARG DOCKER_PROGRAMS_STR=cmake libgomp1 libfontconfig1 libsndfile1 curl ffmpeg nodejs espeak-ng sox tesseract-ocr
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

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

RUN set -eux; \
    if command -v curl >/dev/null 2>&1; then \
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; \
    elif command -v wget >/dev/null 2>&1; then \
        wget -qO- https://sh.rustup.rs | sh -s -- -y; \
    else \
        echo "ERROR: curl or wget required to install rustup"; exit 1; \
    fi && \
    . "$HOME/.cargo/env" && \
    chmod +x ebook2audiobook.sh && \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

RUN case "${DEVICE_TAG}" in \
    jetson51*) \
        echo "JetPack 5.1.x → copying CUDA 11.4 libs" && \
        mkdir -p /usr/local/cuda-11.4/lib64 && \
        ( cp -P /usr/lib/aarch64-linux-gnu/libcuda* /usr/local/cuda-11.4/lib64/ 2>/dev/null || true ) && \
        ( cp -P /usr/lib/aarch64-linux-gnu/libcudart.so.11.0 /usr/local/cuda-11.4/lib64/ 2>/dev/null || true ) && \
        ( cp -P /usr/lib/aarch64-linux-gnu/libcublas* /usr/local/cuda-11.4/lib64/ 2>/dev/null || true ) && \
        ( cp -P /usr/lib/aarch64-linux-gnu/libcufft* /usr/local/cuda-11.4/lib64/ 2>/dev/null || true ) && \
        ( cp -P /usr/lib/aarch64-linux-gnu/libcurand* /usr/local/cuda-11.4/lib64/ 2>/dev/null || true ) && \
        ( cp -P /usr/lib/aarch64-linux-gnu/libcusparse* /usr/local/cuda-11.4/lib64/ 2>/dev/null || true ) ;; \
    jetson60*|jetson61*) \
        echo "JetPack 6.x → no extra CUDA lib copy needed" ;; \
	xpu*) \
        echo "Intel XPU detected — using IPEX" ;; \
    rocm*) \
        echo "AMD ROCm detected — using ROCm PyTorch" ;; \
    *) ;; \
esac

RUN if [ "${DEVICE_TAG}" = jetson51* ]; then \
        echo "LD_LIBRARY_PATH=/usr/local/cuda-11.4/lib64" >> /etc/environment; \
    else \
        echo "LD_LIBRARY_PATH=" >> /etc/environment; \
    fi
ENV LD_LIBRARY_PATH=/usr/local/cuda-11.4/lib64

RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && rm -f /tmp/calibre.sh

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