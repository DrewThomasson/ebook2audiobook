# ------------------------------------------
# BASE STAGE
# ------------------------------------------
ARG BASE=python:3.12
FROM ${BASE} AS base

ENV DEBIAN_FRONTEND=noninteractive

# Expose your port (Gradio or API)
EXPOSE 7860

# Runtime entrypoint
ENTRYPOINT ["python", "app.py", "--script_mode", "full_docker"]