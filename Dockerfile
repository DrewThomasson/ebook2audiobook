ARG BASE=python:3.12
ARG BASE_IMAGE=base

FROM ${BASE} AS base
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app

RUN ./ebook2audiobook.sh --script_mode full_docker

EXPOSE 7860

ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]