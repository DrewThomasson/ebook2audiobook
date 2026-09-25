import json
import sys
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DEVICE_INFO_JSON = os.path.normpath(os.path.join(ROOT_DIR, '.device_info.json'))

def handle_rocm_override():
    """Attempts to apply ROCm override; updates rocmfix if the GPU is unrecognized."""
    try:
        import rocmfix
        
        # 1. Attempt initial override using the local database
        applied = rocmfix.apply_override()
        
        # 2. If no override was applied and HSA_OVERRIDE_GFX_VERSION is missing,
        #    the GPU architecture might be unrecognized. Trigger a DB update.
        if not applied and "HSA_OVERRIDE_GFX_VERSION" not in os.environ:
            try:
                # Call update via rocmfix module or fallback to CLI execution
                if hasattr(rocmfix, "update"):
                    rocmfix.update()
                else:
                    rocmfix_script = os.path.join(SCRIPT_DIR, "rocmfix.py")
                    subprocess.run(
                        [sys.executable, rocmfix_script, "update"], 
                        check=False, 
                        capture_output=True
                    )
                
                # 3. Retry applying the override with the newly updated database
                rocmfix.apply_override()
            except Exception:
                pass  # Avoid crashing if the network is offline
    except ImportError:
        pass

def main() -> None:
    result = {'count': 0, 'backend': None, 'error': None}
    try:
        if not os.path.exists(DEVICE_INFO_JSON):
            result['error'] = f'device_info_json not found: {DEVICE_INFO_JSON}'
            print(json.dumps(result))
            sys.exit(1)
            
        with open(DEVICE_INFO_JSON, 'r', encoding='utf-8') as f:
            device_info = json.load(f)
            
        backend = device_info.get('name')
        result['backend'] = backend
        
        # Run ROCm check & fallback before PyTorch loads
        if backend == 'rocm':
            handle_rocm_override()
            
        import torch
        if backend in ('cuda', 'rocm') and torch.cuda.is_available():
            is_rocm = bool(getattr(torch.version, 'hip', None))
            if backend == 'rocm' and is_rocm:
                result['count'] = torch.cuda.device_count()
            elif backend == 'cuda' and not is_rocm:
                result['count'] = torch.cuda.device_count()
        elif backend == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
            result['count'] = torch.xpu.device_count()
        # mps, jetson, cpu → count stays 0 (single-device or no-device)
    except Exception as e:
        result['error'] = str(e)
        
    print(json.dumps(result))

if __name__ == '__main__':
    main()