import json
import sys
import os
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DEVICE_INFO_JSON = os.path.normpath(os.path.join(ROOT_DIR, '.device_info.json'))
HSA_OVERRIDE_ENV = "HSA_OVERRIDE_GFX_VERSION"

def handle_rocm_override()->Optional[str]:
    """Sets HSA_OVERRIDE_GFX_VERSION in this process before torch loads.
    Returns the effective override (user-provided or resolved), or None."""
    if os.environ.get(HSA_OVERRIDE_ENV):
        return os.environ[HSA_OVERRIDE_ENV]
    try:
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        import rocmfix
        gpus = rocmfix.detect_gpus()
        if not gpus:
            return None
        # pass 0: offline lookup, bundled fallback DB + last downloaded cache, no network
        if rocmfix.DB_CACHE_FILE.exists():
            try:
                rocmfix.GPU_DATABASE.update(rocmfix._validate_db(json.loads(rocmfix.DB_CACHE_FILE.read_text())))
            except Exception:
                pass  # corrupt cache: keep the fallback DB
        override = None
        for attempt in range(2):
            overrides:set = set()
            native_targets:set = set()
            has_unknown = False
            for gpu in gpus:
                info = rocmfix.GPU_DATABASE.get(gpu['pci_id'])
                if info is None:
                    has_unknown = True
                elif info.get('override'):
                    overrides.add(info['override'])
                elif info.get('supported'):
                    native_targets.add(info['gfx_target'])
            override = None
            if len(overrides) == 1:
                override = overrides.pop()
                # HSA_OVERRIDE_GFX_VERSION is process-wide: it also retargets natively supported cards,
                # so only apply it when they share its target ('10.3.0' -> 'gfx1030', '12.0.1' -> 'gfx1201')
                major, minor, step = (int(part) for part in override.split('.'))
                if native_targets - {f"gfx{major}{minor}{step:x}"}:
                    override = None
            if not has_unknown or attempt == 1:
                break
            # pass 1: a card is not in the DB, download it now
            rocmfix.sync_gpu_database(force=True)
        if override:
            os.environ[HSA_OVERRIDE_ENV] = override
        return override
    except Exception:
        return None  # rocmfix missing, offline, or unwritable ~/.rocmfix: never block GPU detection

def main() -> None:
    result = {'count': 0, 'backend': None, 'hsa_override': None, 'error': None}
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
            result['hsa_override'] = handle_rocm_override()
            
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
