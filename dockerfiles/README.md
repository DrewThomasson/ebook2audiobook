## Guide for the New entry points for the main Dockerfile



Being this `Dockerfile` ``

### Available PyTorch Variant Options

- **cuda11** – Use this variant for systems with CUDA 11.
- **cuda12** – Use this variant for systems with CUDA 12.
- **amd** – Use this variant for AMD GPU support.
- **intel** – Use this variant for Intel GPU/ROCm support.
- **cpu** (Optional) – Use this variant for CPU-only installation (if you create and use a CPU-specific wheel).


### **Pre-Built, Tagged Images**

- **How It Works:**  
  You build a separate image for each variant by passing a build argument (`PYTORCH_VARIANT`) and tag each image accordingly (e.g., `athomasson2/ebook2audiobook:cuda11`, `:cuda12`, etc.).

- **Pros:**  
  - Faster startup since the correct PyTorch wheel is already installed.  
  - Clear versioning and explicit control over each build.

- **Example Commands:**

  ```bash
  docker build --platform linux/amd64 -t athomasson2/ebook2audiobook:cuda11 --build-arg PYTORCH_VARIANT=cuda11 .
  docker push athomasson2/ebook2audiobook:cuda11

  docker build --platform linux/amd64 -t athomasson2/ebook2audiobook:cuda12 --build-arg PYTORCH_VARIANT=cuda12 .
  docker push athomasson2/ebook2audiobook:cuda12

  docker build --platform linux/amd64 -t athomasson2/ebook2audiobook:amd --build-arg PYTORCH_VARIANT=amd .
  docker push athomasson2/ebook2audiobook:amd

  docker build --platform linux/amd64 -t athomasson2/ebook2audiobook:intel --build-arg PYTORCH_VARIANT=intel .
  docker push athomasson2/ebook2audiobook:intel
  ```

- **Usage:**  
  Pull and run the appropriate image based on your hardware:
  ```bash
  docker run -p 7860:7860 athomasson2/ebook2audiobook:cuda11
  ```

---

### **Unified Image with Runtime Selection**

- **How It Works:**  
  You have one image that contains all precompiled wheels. At container startup, an entrypoint script reads the `PYTORCH_VARIANT` environment variable and installs the correct wheel.

- **Pros:**  
  - Flexibility: One image supports multiple hardware configurations.
  - Simplified deployment if you want to decide at runtime.

- **Cons:**  
  - Extra installation step at startup.
  - Container remains larger since it includes all wheels.

- **Usage:**  
  To use the default or override the variant at runtime:
  ```bash
  # Default (cuda11)
  docker run -p 7860:7860 athomasson2/ebook2audiobook:latest

  # Override for CUDA 12
  docker run -p 7860:7860 -e PYTORCH_VARIANT=cuda12 athomasson2/ebook2audiobook:latest
  ```

---

### **Auto-Detection and Docker Compose**

- **Auto-Detection:**  
  Containers are isolated from the host system, so auto-detecting GPU hardware from within the container is challenging.  
  - NVIDIA Container Toolkit can help expose GPU details to the container, but auto-selecting the correct PyTorch wheel based solely on that info requires custom logic.
  - You could write a startup script that queries GPU details (using `nvidia-smi` or similar tools) and then installs the right wheel—but this adds complexity and may not cover non-NVIDIA hardware well.

- **Docker Compose:**  
  Docker Compose itself doesn’t auto-detect hardware, but you can define services with specific images or environment variables. For example, you might have different services in your `docker-compose.yml` file for different hardware
