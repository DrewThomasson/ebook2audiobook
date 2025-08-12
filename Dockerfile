ARG BASE=python:3.12
ARG BASE_IMAGE=base
FROM ${BASE} AS base

# Set environment PATH for local installations
ENV PATH="/root/.local/bin:$PATH"
# Set non-interactive mode to prevent tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive
# Install system packages
RUN apt-get update && \
    apt-get install -y gcc g++ make wget git calibre ffmpeg libmecab-dev mecab mecab-ipadic-utf8 libsndfile1-dev libc-dev curl espeak-ng sox && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Install Rust compiler
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
# Copy the application
WORKDIR /app
COPY . /app
# Install UniDic (non-torch dependent)
RUN pip install --no-cache-dir unidic-lite unidic && \
    python3 -m unidic download && \
    mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Second stage for PyTorch installation + swappable base image if you want to use a pulled image
FROM $BASE_IMAGE AS pytorch
# Add parameter for PyTorch version with a default empty value
ARG TORCH_VERSION=""
# Add parameter to control whether to skip the XTTS test
ARG SKIP_XTTS_TEST="false"


# Extract torch versions from requirements.txt or set to empty strings if not found
RUN TORCH_VERSION_REQ=$(grep -E "^torch==" requirements.txt | cut -d'=' -f3 || echo "") && \
    TORCHAUDIO_VERSION_REQ=$(grep -E "^torchaudio==" requirements.txt | cut -d'=' -f3 || echo "") && \
    TORCHVISION_VERSION_REQ=$(grep -E "^torchvision==" requirements.txt | cut -d'=' -f3 || echo "") && \
    echo "Found in requirements: torch==$TORCH_VERSION_REQ torchaudio==$TORCHAUDIO_VERSION_REQ torchvision==$TORCHVISION_VERSION_REQ"

# Install PyTorch with CUDA support if specified
RUN if [ ! -z "$TORCH_VERSION" ]; then \
        # Check if we need to use specific versions or get the latest
        if [ ! -z "$TORCH_VERSION_REQ" ] && [ ! -z "$TORCHVISION_VERSION_REQ" ] && [ ! -z "$TORCHAUDIO_VERSION_REQ" ]; then \
            echo "Using specific versions from requirements.txt" && \
            TORCH_SPEC="torch==${TORCH_VERSION_REQ}" && \
            TORCHVISION_SPEC="torchvision==${TORCHVISION_VERSION_REQ}" && \
            TORCHAUDIO_SPEC="torchaudio==${TORCHAUDIO_VERSION_REQ}"; \
        else \
            echo "Using latest versions for the selected variant" && \
            TORCH_SPEC="torch" && \
            TORCHVISION_SPEC="torchvision" && \
            TORCHAUDIO_SPEC="torchaudio"; \
        fi && \
        \
        # Check if TORCH_VERSION contains "cuda" and extract version number
        if echo "$TORCH_VERSION" | grep -q "cuda"; then \
            CUDA_VERSION=$(echo "$TORCH_VERSION" | sed 's/cuda//g') && \
            echo "Detected CUDA version: $CUDA_VERSION" && \
            echo "Attempting to install PyTorch nightly for CUDA $CUDA_VERSION..." && \
            #if ! pip install --no-cache-dir --pre $TORCH_SPEC $TORCHVISION_SPEC $TORCHAUDIO_SPEC --index-url https://download.pytorch.org/whl/nightly/cu${CUDA_VERSION}; then \
            if ! pip install --no-cache-dir --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu${CUDA_VERSION}; then \
                echo "❌ Nightly build for CUDA $CUDA_VERSION not available or failed" && \
                echo "🔄 Trying stable release for CUDA $CUDA_VERSION..." && \
                #if pip install --no-cache-dir $TORCH_SPEC $TORCHVISION_SPEC $TORCHAUDIO_SPEC --extra-index-url https://download.pytorch.org/whl/cu${CUDA_VERSION}; then \
                if pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu${CUDA_VERSION}; then \
                    echo "✅ Successfully installed stable PyTorch for CUDA $CUDA_VERSION"; \
                else \
                    echo "❌ Both nightly and stable builds failed for CUDA $CUDA_VERSION"; \
                    echo "💡 This CUDA version may not be supported by PyTorch"; \
                    exit 1; \
                fi; \
            else \
                echo "✅ Successfully installed nightly PyTorch for CUDA $CUDA_VERSION"; \
            fi; \
        else \
            # Handle non-CUDA cases (existing functionality)
            case "$TORCH_VERSION" in \
                "rocm") \
                    # Using the correct syntax for ROCm PyTorch installation
                    pip install --no-cache-dir $TORCH_SPEC $TORCHVISION_SPEC $TORCHAUDIO_SPEC --extra-index-url https://download.pytorch.org/whl/rocm6.2 \
                    ;; \
                "xpu") \
                    # Install PyTorch with Intel XPU support through IPEX
                    pip install --no-cache-dir $TORCH_SPEC $TORCHVISION_SPEC $TORCHAUDIO_SPEC && \
                    pip install --no-cache-dir intel-extension-for-pytorch --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/ \
                    ;; \
                "cpu") \
                    pip install --no-cache-dir $TORCH_SPEC $TORCHVISION_SPEC $TORCHAUDIO_SPEC --extra-index-url https://download.pytorch.org/whl/cpu \
                    ;; \
                *) \
                    pip install --no-cache-dir $TORCH_VERSION \
                    ;; \
            esac; \
        fi && \
        # Install remaining requirements, skipping torch packages that might be there
        grep -v -E "^torch==|^torchvision==|^torchaudio==|^torchvision$" requirements.txt > requirements_no_torch.txt && \
        pip install --no-cache-dir --upgrade -r requirements_no_torch.txt && \
        rm requirements_no_torch.txt; \
    else \
        # Install all requirements as specified
        pip install --no-cache-dir --upgrade -r requirements.txt; \
    fi

# Do a test run to pre-download and bake base models into the image, but only if SKIP_XTTS_TEST is not true
RUN if [ "$SKIP_XTTS_TEST" != "true" ]; then \
        echo "Running XTTS test to pre-download models..."; \
        if [ "$TORCH_VERSION" = "xpu" ]; then \
            TORCH_DEVICE_BACKEND_AUTOLOAD=0 python app.py --headless --ebook test.txt --script_mode full_docker; \
        else \
            python app.py --headless --language eng --ebook "tools/workflow-testing/test1.txt" --tts_engine XTTSv2 --script_mode full_docker; \
        fi; \
    else \
        echo "Skipping XTTS test run as requested."; \
    fi


# Expose the required port
EXPOSE 7860
# Start the Gradio app with the required flag
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]


#docker build --pull --build-arg BASE_IMAGE=athomasson2/ebook2audiobook:latest -t your-image-name .
#The --pull flag forces Docker to always try to pull the latest version of the image, even if it already exists locally.
#Without --pull, Docker will only use the local version if it exists, which might not be the latest.
