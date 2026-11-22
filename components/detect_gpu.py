import json
import sys
import os
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DEVICE_INFO_JSON = os.path.normpath(os.path.join(ROOT_DIR, '.device_info.json'))
HSA_OVERRIDE_ENV = "HSA_OVERRIDE_GFX_VERSION"

def rocm_arch_list()->set[str]|None:
    """GPU targets the installed ROCm torch was built for ('gfx1200', ...), read without starting the HIP runtime: HSA
    reads HSA_OVERRIDE_GFX_VERSION once, when torch first touches the GPU. torch.cuda.get_arch_list() would start it,
    torch._C._cuda_getArchFlags() is the build's own string (what torch.utils.cpp_extension reads on ROCm).
    None when torch cannot say: not a ROCm build, or no such string."""
    try:
        import torch
        flags = torch._C._cuda_getArchFlags() if getattr(torch.version, 'hip', None) else None
    except Exception:
        return None
    if not flags:
        return None
    # 'gfx90a:xnack-' -> 'gfx90a'
    return {flag.split(':', 1)[0] for flag in str(flags).split()}

def handle_rocm_override(arch_list:set[str]|None=None)->str|None:
    """Sets HSA_OVERRIDE_GFX_VERSION in this process before torch touches the GPU.
    arch_list: the installed torch's GPU targets (rocm_arch_list()), None to decide from the DB alone.
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
        # a GPU whose own target the installed torch was built for runs as itself, whatever the DB says: its entries
        # follow the ROCm releases that lacked the target (the bundled RX 9060 XT, gfx1200 -> '12.0.1', native since
        # ROCm 6.4.2), and a card the DB knows never gets the downloaded update. Under that override the first tensor
        # moved to the GPU killed e2a (crash report ec3a0208c4c44215: segfault in stanza's model.to('cuda'))
        for attempt in range(2):
            overrides:set[str] = set()
            native_targets:set[str] = set()
            has_unknown = False
            for gpu in gpus:
                info = rocmfix.GPU_DATABASE.get(gpu['pci_id'])
                if info is None:
                    has_unknown = True
                elif arch_list is not None and info.get('gfx_target') in arch_list:
                    native_targets.add(info['gfx_target'])
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

def rocm_denied_nodes()->list[str]:
    """Returns the ROCm device nodes this process cannot open read/write.
    ROCm opens /dev/kfd plus the render node of every amdgpu device, and udev rules can put them in different groups."""
    nodes:list[str] = ['/dev/kfd']
    for sys_node in sorted(glob.glob('/sys/class/drm/renderD*')):
        # hybrid boxes: skip Intel/NVIDIA render nodes, ROCm never opens them
        if os.path.basename(os.path.realpath(os.path.join(sys_node, 'device', 'driver'))) == 'amdgpu':
            nodes.append(os.path.join('/dev/dri', os.path.basename(sys_node)))
    return [node for node in nodes if os.path.exists(node) and not os.access(node, os.R_OK | os.W_OK)]

def hip_runtime(candidates:list[str])->dict:
    """The system HIP runtime's device count and version ('--hip-runtime', from DeviceInstaller.check_hardware). Asked
    here, in a child: a libamdhip64 loaded in e2a's process stays there, and torch imported later binds its own ROCm
    libraries to it by soname (libamdhip64.so.7), running torch built for one ROCm on the system's other one.
    The DB override is set first, as the system probe always had it; it does not leave this process"""
    handle_rocm_override()
    import ctypes
    for lib_name in candidates:
        try:
            libhip = ctypes.CDLL(lib_name)
        except OSError:
            continue
        try:
            count = ctypes.c_int()
            version = ctypes.c_int()
            return {
                'count': count.value if libhip.hipGetDeviceCount(ctypes.byref(count)) == 0 else 0,
                'version': version.value if libhip.hipRuntimeGetVersion(ctypes.byref(version)) == 0 else None,
            }
        except AttributeError:
            continue
    return {}

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
            result['hsa_override'] = handle_rocm_override(rocm_arch_list())
            if (denied := rocm_denied_nodes()):
                result['error'] = f"no read/write access to {', '.join(denied)}: user not in its group (render or video), relaunch ebook2audiobook.command or log out and back in"

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
    if len(sys.argv) > 2 and sys.argv[1] == '--hip-runtime':
        print(json.dumps(hip_runtime(json.loads(sys.argv[2]))))
    else:
        main()
