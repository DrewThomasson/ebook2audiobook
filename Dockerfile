ARG BASE=python:3.12
FROM ${BASE} AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY . /app

RUN chmod +x ebook2audiobook.sh

# Update apt and ensure basic tools
RUN apt-get update

# Install everything for Docker image
RUN ./ebook2audiobook.sh --script_mode full_docker --install_pkg all

EXPOSE 7860
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]