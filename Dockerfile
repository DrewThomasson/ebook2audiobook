ARG BASE=python:3.12-slim

FROM ${BASE}

# Build-time only variable
ARG DEVICE_INFO_STR

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y bash && apt-get clean

WORKDIR /app
COPY . /app

RUN chmod +x ebook2audiobook.sh

RUN echo "Building image for: $DEVICE_INFO_STR"
RUN ./ebook2audiobook.sh --script_mode full_docker --install_pkg "$DEVICE_INFO_STR"

EXPOSE 7860

ENTRYPOINT ["python3", "app.py", "--script_mode", "full_docker"]