# ===============================
# Stage 1: Builder
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9 AS builder

# Enable EPEL, CRB, and RPM Fusion for ffmpeg + dev libs
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
    dnf install -y --nobest python3 python3-pip git make gcc-c++ \
        ffmpeg ffmpeg-devel pkgconfig && \
    dnf clean all

# Create and prepare venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir audiocraft
RUN rm -rf /root/.cache /tmp/*

# ===============================
# Stage 2: Slim Runtime
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9

# Minimal deps: runtime ffmpeg only
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
    dnf install -y --nobest ffmpeg && \
    dnf autoremove -y && dnf clean all

# Copy only the ready-to-use virtualenv
COPY --from=builder /opt/venv /opt/venv

# Environment
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/models/cache \
    TORCH_HOME=/models/torch \
    HF_HOME=/models/huggingface

WORKDIR /app
COPY . .

# Strip unnecessary artifacts
RUN find /opt/venv -type d -name "__pycache__" -exec rm -rf {} + && \
    find /opt/venv -type d -name "tests" -exec rm -rf {} + && \
    strip --strip-unneeded /opt/venv/bin/* 2>/dev/null || true
	
RUN find /opt/venv/lib/python3.* -type d -name "*.dist-info" -prune -exec rm -rf {} + && \
    rm -rf /opt/venv/share /opt/venv/include

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["generate.py"]