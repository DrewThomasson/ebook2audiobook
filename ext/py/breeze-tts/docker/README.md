# Container build

The image uses the public PyTorch 2.9.1 CUDA 12.8 development image and builds
FlashAttention 2.8.3 from source. It also installs Qwen TTS, the API runtime
dependencies and the repository test dependencies.

Build:

```bash
bash docker/build.sh
```

The default FlashAttention target is H100/Hopper (`FLASH_ATTN_CUDA_ARCHS=90`). To
build for another GPU, override it explicitly, for example:

```bash
FLASH_ATTN_CUDA_ARCHS=80 bash docker/build.sh
```

Run with a local model directory:

```bash
bash docker/run.sh /path/to/breeze-model \
  --fast-all
```

The model is mounted read-only and is never copied into the image. The build
runs an import/version smoke check and the CPU-safe core unit tests. GPU graph
capture happens only when fast stages are explicitly enabled on an NVIDIA GPU.
