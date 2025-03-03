# Build with:
# docker build --platform linux/amd64 -t athomasson2/ebook2audiobook:latest .

FROM python:3.12

# Set default PyTorch variant; override with -e PYTORCH_VARIANT=... when running if needed.
ENV PYTORCH_VARIANT=cuda11

# Copy precompiled PyTorch wheels and unified entrypoint script into the image.
# (Make sure the 'pytorch_wheels' directory and 'entrypoint.sh' exist in your build context.)
COPY pytorch_wheels /pytorch_wheels
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create and switch to a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set a working directory for temporary operations
WORKDIR /app

# Install system packages
USER root
RUN apt-get update && \
    apt-get install -y wget git calibre ffmpeg libmecab-dev mecab mecab-ipadic-utf8 curl espeak-ng sox && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone the GitHub repository and set it as the working directory
USER root
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*
USER user
RUN git clone --depth 1 https://github.com/DrewThomasson/ebook2audiobook.git /home/user/app && rm -rf /home/user/app/.git

# Set the cloned repository as the base working directory
WORKDIR /home/user/app

# Install Python dependencies (UniDic and others)
RUN pip install --no-cache-dir unidic-lite unidic
RUN python3 -m unidic download  # Download UniDic
RUN mkdir -p /home/user/.local/share/unidic && \
    mv ~/.local/share/unidic/* /home/user/.local/share/unidic/ || true
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Set environment variable to ensure MeCab can locate UniDic
ENV UNIDIC_DIR=/home/user/.local/share/unidic

# Test run to ensure base models are pre-downloaded
RUN echo "This is a test sentence." > test.txt 
RUN python app.py --headless --ebook test.txt --script_mode full_docker
RUN rm test.txt

# Expose the required port
EXPOSE 7860

# Use the unified entrypoint script to install the correct PyTorch and start the app.
ENTRYPOINT ["/entrypoint.sh", "python", "app.py", "--script_mode", "full_docker"]
