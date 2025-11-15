# ===============================
# Stage 1: Builder
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9 AS builder

# Enable EPEL, CRB, and RPM Fusion so ffmpeg installs cleanly
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
    dnf install -y --nobest python3 python3-pip git make gcc-c++ ffmpeg && \
    dnf clean all

# Create Python venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir audiocraft
RUN rm -rf /root/.cache

# ===============================
# Stage 2: Runtime
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9

# Enable repos and install ffmpeg runtime
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
    dnf install -y --nobest ffmpeg && \
    dnf clean all

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/models/cache \
    TORCH_HOME=/models/torch \
    HF_HOME=/models/huggingface

WORKDIR /app
COPY . .

RUN find /opt/venv -type d -name "tests" -exec rm -rf {} + \
 && find /opt/venv -type d -name "__pycache__" -exec rm -rf {} +

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["generate.py"]