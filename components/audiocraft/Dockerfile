# ===============================
# Stage 1: Builder
# ===============================
FROM nvidia/cuda:12.1.0-base-alpine3.19 AS builder

RUN apk add --no-cache python3 py3-pip ffmpeg git build-base

# Isolated virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Torch GPU build (works on CPU fallback)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir audiocraft

RUN rm -rf /root/.cache

# ===============================
# Stage 2: Runtime
# ===============================
FROM nvidia/cuda:12.1.0-base-alpine3.19

COPY --from=builder /opt/venv /opt/venv
RUN apk add --no-cache ffmpeg

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/models/cache \
    TORCH_HOME=/models/torch \
    HF_HOME=/models/huggingface

WORKDIR /app
COPY . .

# Remove unnecessary weight
RUN find /opt/venv -type d -name "tests" -exec rm -rf {} + \
 && find /opt/venv -type d -name "__pycache__" -exec rm -rf {} +

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["generate.py"]