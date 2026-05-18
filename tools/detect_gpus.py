import json
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEVICE_INFO_JSON = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '.device_info.json'))

def main()->None:
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