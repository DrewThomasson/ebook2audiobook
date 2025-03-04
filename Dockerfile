ARG BASE=python:3.12
FROM ${BASE}

# Set environment PATH for local installations
ENV PATH="/root/.local/bin:$PATH"

# Set a working directory for temporary operations
WORKDIR /app

# Set non-interactive mode to prevent tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && \
    apt-get install -y gcc g++ make wget git calibre ffmpeg libmecab-dev mecab mecab-ipadic-utf8 libsndfile1-dev libc-dev curl espeak-ng sox && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Rust compiler (to build sudachipy for Mac)
RUN curl --proto '=https' --tlsv1.2 -sSf "https://sh.rustup.rs" | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone the GitHub repository and set it as the working directory
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/DrewThomasson/ebook2audiobook.git /app && rm -rf /app/.git

# Ensure the repository is the current working directory
WORKDIR /app

# Install Python dependencies and UniDic
RUN pip install --no-cache-dir unidic-lite unidic
RUN python3 -m unidic download  # Download UniDic
RUN mkdir -p /root/.local/share/unidic
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Set environment variable so MeCab can locate UniDic
ENV UNIDIC_DIR=/root/.local/share/unidic

# Do a test run to pre-download and bake base models into the image
RUN echo "This is a test sentence." > test.txt 
RUN python app.py --headless --ebook test.txt --script_mode full_docker
RUN rm test.txt

# Expose the required port
EXPOSE 7860

# Start the Gradio app with the required flag
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]
