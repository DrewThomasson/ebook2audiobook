# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

# Build with the command: 
# docker build --platform linux/amd64 -t ebook2audiobook . 

FROM python:3.12

# Create and switch to a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set a working directory for temporary operations
WORKDIR /app

# Install system packages
USER root
RUN apt-get update && \
    apt-get install -y wget git calibre ffmpeg libmecab-dev mecab mecab-ipadic && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone the GitHub repository and set it as the working directory
USER root
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*
USER user
RUN git clone https://github.com/DrewThomasson/ebook2audiobook.git /home/user/app

# Set the cloned repository as the base working directory
WORKDIR /home/user/app

#Install Python dependences from the ebook2audiobook repo
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Do a test run to make sure that the base models are pre-downloaded and baked into the image
# RUN echo "This is a test sentence." > test.txt 
# RUN python app.py --headless --ebook test.txt
# RUN rm test.txt

# Expose the required port
EXPOSE 7860

# Start the Gradio app from the repository
CMD ["python", "app.py"]
