# ===============================
# Stage 1: Builder
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9 AS builder

# --- Environment setup ---
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_BUILD_ISOLATION=0 \
    PIP_NO_DEPENDENCIES=0

# --- Enable EPEL, CRB, and RPM Fusion for ffmpeg ---
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
    dnf install -y --nobest python3 python3-pip python3-devel git make gcc-c++ \
        ffmpeg ffmpeg-devel pkgconfig && \
    dnf clean all

# --- Virtual environment setup ---
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# --- Copy dependencies ---
COPY requirements.txt /tmp/requirements.txt

# --- Install pip & build tools ---
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# --- Fix for PyAV (requires Cython) ---
RUN pip install --no-cache-dir Cython==3.0.10

# --- Install pinned dependencies ---
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# --- Clean up ---
RUN rm -rf /root/.cache /tmp/*

# ===============================
# Stage 2: Slim Runtime
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9

# --- Enable repos and install runtime ffmpeg only ---
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
    dnf install -y --nobest ffmpeg && \
    dnf autoremove -y && dnf clean all

# --- Copy prebuilt Python environment ---
COPY --from=builder /opt/venv /opt/venv

# --- Set environment variables ---
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/models/cache \
    TORCH_HOME=/models/torch \
    HF_HOME=/models/huggingface

# --- Working directory ---
WORKDIR /app
COPY . .

# --- Cleanup unnecessary data ---
RUN find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + && \
    find /opt/venv -type d -name "tests" -exec rm -rf {} + && \
    strip --strip-unneeded /opt/venv/bin/* 2>/dev/null || true
	
RUN find /opt/venv/lib/python3.* -type d -name "*.dist-info" -prune -exec rm -rf {} + && \
    rm -rf /opt/venv/share /opt/venv/include

# --- Metadata labels ---
LABEL org.opencontainers.image.version="1.3.0-cuda12.1-rocky9" \
      org.opencontainers.image.created="2025-11-15" \
      org.opencontainers.image.source="https://github.com/facebookresearch/audiocraft" \
      org.opencontainers.image.description="Audiocraft reproducible CUDA12.1 Rocky9 slim build"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["generate.py"]