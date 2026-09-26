import json
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DEVICE_INFO_JSON = os.path.normpath(os.path.join(ROOT_DIR, '.device_info.json'))
HSA_OVERRIDE_ENV = "HSA_OVERRIDE_GFX_VERSION"

def handle_rocm_override()->str|None:
    """Sets HSA_OVERRIDE_GFX_VERSION in this process before torch loads.
    Returns the effective override (user-provided or resolved), or None."""
    if (override := os.environ.get(HSA_OVERRIDE_ENV)):
        return override
    try:
        if SCRIPT_DIR not in sys.path:
            sys.path.insert(0, SCRIPT_DIR)
        import rocmfix
        gpus = rocmfix.detect_gpus()
        if not gpus:
            return None
        # pass 0: offline lookup, bundled fallback DB + last downloaded cache, no network
        try:
            rocmfix.GPU_DATABASE.update(rocmfix._validate_db(json.loads(rocmfix.DB_CACHE_FILE.read_text(encoding='utf-8'))))
        except Exception:
            pass  # no cache yet or corrupt cache: keep the fallback DB
        for attempt in range(2):
            overrides:set[str] = set()
            native_targets:set[str] = set()
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
                major, minor, step = map(int, override.split('.'))
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

def main()->None:
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
            if os.path.exists('/dev/kfd') and not os.access('/dev/kfd', os.R_OK | os.W_OK):
                result['error'] = 'no read/write access to /dev/kfd: user not in its group (render or video), relaunch ebook2audiobook.command or log out and back in'

        # torch import costs seconds: only pay it when there is a device count to read
        if backend in ('cuda', 'rocm', 'xpu') and result['error'] is None:
            import torch
            match backend:
                case 'cuda' | 'rocm' if torch.cuda.is_available() and bool(getattr(torch.version, 'hip', None)) == (backend == 'rocm'):
                    # wheel vendor must match the tag: a CUDA wheel on a rocm tag (or the reverse) keeps count at 0
                    result['count'] = torch.cuda.device_count()
                case 'xpu' if hasattr(torch, 'xpu') and torch.xpu.is_available():
                    result['count'] = torch.xpu.device_count()
        # mps, jetson, cpu → no torch import, count stays 0 (single-device or no-device)
    except Exception as e:
        result['error'] = str(e)

    print(json.dumps(result))

if __name__ == '__main__':
    main()
