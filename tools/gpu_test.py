import torch

def gpu_test():
    print("Checking PyTorch GPU support...")

    # Check if CUDA is available
    if not torch.cuda.is_available():
        print("CUDA is NOT available. Running on CPU.")
        return

    # Get number of GPUs
    num_gpus = torch.cuda.device_count()
    print(f"CUDA is available. Number of GPUs: {num_gpus}")

    # List all GPUs
    for i in range(num_gpus):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

    # Run a small test on the first GPU
    device = torch.device("cuda:0")
    print(f"Running a small test on {torch.cuda.get_device_name(0)}...")

    # Test computation
    try:
        x = torch.rand(1000, 1000, device=device)
        y = torch.mm(x, x)
        print("GPU computation successful!")
    except Exception as e:
        print(f"GPU computation failed: {e}")

if __name__ == "__main__":
    gpu_test()