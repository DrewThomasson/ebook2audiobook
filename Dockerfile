ARG BASE=python:3.12
ARG BASE_IMAGE=base

FROM ${BASE} AS base
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

ARG TORCH_VERSION=""
ARG SKIP_XTTS_TEST="false"

WORKDIR /app
COPY . /app

RUN ./ebook2audiobook.sh --script_mode FULL_DOCKER

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

EXPOSE 7860

ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]