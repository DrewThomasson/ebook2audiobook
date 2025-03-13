ARG BASE=python:3.12
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
RUN curl --proto '=https' --tlsv1.2 -sSf "https://sh.rustup.rs" | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy everything except requirements.txt
WORKDIR /app
COPY . /app
RUN if [ -f requirements.txt ]; then cp requirements.txt requirements.txt.orig; fi

# Install UniDic (non-torch dependent)
RUN pip install --no-cache-dir unidic-lite unidic
RUN python3 -m unidic download
RUN mkdir -p /root/.local/share/unidic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Second stage for PyTorch installation
FROM base AS pytorch

# Add parameter for PyTorch version
ARG TORCH_VERSION=default

# Define torch versions
RUN echo '#!/bin/bash \n\
declare -A TORCH_VERSIONS \n\
TORCH_VERSIONS["default"]="torch" \n\
TORCH_VERSIONS["cuda12"]="torch==2.2.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121" \n\
TORCH_VERSIONS["cuda11"]="torch==2.2.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118" \n\
TORCH_VERSIONS["cpu"]="torch==2.2.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu" \n\
\n\
if [ -n "${TORCH_VERSIONS[$TORCH_VERSION]}" ]; then \n\
  echo "Using predefined torch version: $TORCH_VERSION -> ${TORCH_VERSIONS[$TORCH_VERSION]}" \n\
  TORCH_LINE="${TORCH_VERSIONS[$TORCH_VERSION]}" \n\
else \n\
  echo "Using custom torch version: $TORCH_VERSION" \n\
  TORCH_LINE="$TORCH_VERSION" \n\
fi \n\
\n\
cp requirements.txt.orig requirements.txt \n\
sed -i "s|^torch.*$|${TORCH_LINE}|" requirements.txt \n\
cat requirements.txt | grep torch \n\
' > /app/update_torch.sh && chmod +x /app/update_torch.sh

# Replace torch line in requirements.txt
RUN /app/update_torch.sh $TORCH_VERSION

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Do a test run to pre-download and bake base models into the image
RUN echo "This is a test sentence." > test.txt 
RUN python app.py --headless --ebook test.txt --script_mode full_docker
RUN rm test.txt

# Expose the required port
EXPOSE 7860

# Start the Gradio app with the required flag
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]