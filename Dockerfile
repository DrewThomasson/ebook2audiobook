###############################
#         STAGE 1: BUILD
###############################
ARG PYTHON_VERSION=3.12
ARG BASE=python:${PYTHON_VERSION}-slim
FROM ${BASE} AS build

MAINTAINER Ebbok2Audiobook version: 25.12.9

# ─────────────── ARG (build-time only) ───────────────
ARG DOCKER_DEVICE_STR
ARG DOCKER_PROGRAMS_STR
ARG CALIBRE_INSTALLER_URL="https://download.calibre-ebook.com/linux-installer.sh"
ARG ISO3_LANG=eng

# ─────────────── ENV (persists inside container) ───────────────
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ─────────────── App source ───────────────
WORKDIR /app
COPY . .
RUN chmod +x ebook2audiobook.sh

# ─────────────── Install OS Dependencies ───────────────
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends --allow-change-held-packages \
        gcc g++ make python3-dev pkg-config git wget bash xz-utils \
        libglib2.0-0 libnss3 libatk1.0-0 libgdk-pixbuf-2.0-0 libxcb-cursor0 \
        libx11-6 libegl1 libopengl0 libxrender1 libxext6 libxi6 libxcb1 \
        ${DOCKER_PROGRAMS_STR} tesseract-ocr-${ISO3_LANG} || true && \
    rm -rf /var/lib/apt/lists/*

# ─────────────── Your build script ───────────────
RUN --mount=type=cache,target=/root/.cache/pip \
    ./ebook2audiobook.sh --script_mode build_docker --docker_device "${DOCKER_DEVICE_STR}"

# ─────────────── Install Calibre ───────────────
RUN wget -nv "$CALIBRE_INSTALLER_URL" -O /tmp/calibre.sh && \
    bash /tmp/calibre.sh && \
	rm -f /tmp/calibre.sh

# ─────────────── Cleanup (shrink image) ───────────────
RUN find /usr -type d -name "__pycache__" -exec rm -rf {} + && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/share/locale/* && \
    rm -rf /usr/share/icons/* /usr/share/fonts/* /var/cache/fontconfig/* && \
    rm -rf /opt/calibre/*.txt /opt/calibre/*.md /opt/calibre/resources/man-pages || true && \
    find /app -type d -name "__pycache__" -exec rm -rf {} + || true

RUN apt-get purge -y --auto-remove gcc g++ make python3-dev pkg-config git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

###############################
#      STAGE 2: RUNTIME
###############################
FROM python:${PYTHON_VERSION}-slim AS runtime

# Same ENV
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_CPU_FALLBACK=1

WORKDIR /app

# Copy only results from build stage
COPY --from=build /app /app
COPY --from=build /opt/calibre /opt/calibre
COPY --from=build /usr/bin /usr/bin
COPY --from=build /usr/lib /usr/lib
COPY --from=build /lib /lib

# ─────────────── Universal GPU Auto-Detection (nvcc / rocminfo / sycl-ls) ───────────────
ENTRYPOINT ["bash", "-c", "\
echo 'Detecting GPU backend...'; \
if command -v nvcc >/dev/null 2>&1; then \
    echo '▶ CUDA detected via nvcc — enabling CUDA backend'; \
    export GPU_BACKEND=cuda; \
elif command -v rocminfo >/dev/null 2>&1; then \
    echo '▶ ROCm detected via rocminfo — enabling HIP backend'; \
    export GPU_BACKEND=rocm; \
elif command -v sycl-ls >/dev/null 2>&1; then \
    echo '▶ Intel XPU detected via SYCL — enabling XPU backend'; \
    export GPU_BACKEND=xpu; \
else \
    echo '▶ No GPU detected — CPU fallback enabled'; \
    export GPU_BACKEND=cpu; \
fi; \
python3 app.py --script_mode full_docker"]

EXPOSE 7860