# ===============================
# Stage 1: Builder
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9 AS builder

# Enable EPEL and install core packages
RUN dnf install -y epel-release && \
    dnf install -y python3 python3-pip ffmpeg git make gcc-c++ && \
    dnf clean all

# Create isolated environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip & install deps
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Torch (GPU build works on CPU fallback)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Audiocraft
RUN pip install --no-cache-dir audiocraft
RUN rm -rf /root/.cache

# ===============================
# Stage 2: Runtime
# ===============================
FROM nvidia/cuda:12.1.0-runtime-rockylinux9

# Enable EPEL for ffmpeg
RUN dnf install -y epel-release && \
    dnf install -y ffmpeg && \
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