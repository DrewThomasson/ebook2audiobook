# lib/classes/tts_engines/common/xpu_workarounds.py
import os
import torch
import torch.nn as nn

def patch_coqui_hifigan_for_xpu(engine):
    """
    Universal XPU vocoder patcher:
    1. Built-in HiFi-GAN generators (XTTS, VITS): offload waveform_decoder to CPU
       to bypass the oneDNN JIT dilated-conv bug.
    2. Separate vocoders (GlowTTS, Tacotron2) loaded via Coqui's Synthesizer:
       clear use_cuda (so Coqui stops routing the vocoder input to 'cuda' on a
       CUDA-less XPU torch build) and offload the vocoder to CPU.
    """
    if os.environ.get("E2A_XPU_HIFIGAN_CPU", "1") != "1":
        return engine
    # is_initialized(), not is_available(): an engine moved to xpu has started the runtime already, a CPU one must not
    # start it here. Both callers run on every Coqui load, and on an Intel GPU torch xpu cannot run on (UHD 770 iGPU,
    # old driver) the is_available() probe is a Windows access violation
    if not hasattr(torch, 'xpu') or not torch.xpu.is_initialized():
        return engine

    print("[XPU Workaround] Scanning engine for vocoders (HiFi-GAN / separate)...")
    patched_count = 0

    def _patch_hifigan_module(module):
        nonlocal patched_count
        if getattr(module, '_xpu_cpu_patched', False):
            return
        # Coqui HifiganGenerator signature
        if hasattr(module, 'resblocks') and hasattr(module, 'ups'):
            print(f"[XPU Workaround] Found HiFi-GAN module ({module.__class__.__name__}). Moving to CPU.")
            original_forward = module.forward

            def cpu_forward(*args, **kwargs):
                target_device = None
                for a in args:
                    if isinstance(a, torch.Tensor):
                        target_device = a.device
                        break
                cpu_args = [a.cpu() if isinstance(a, torch.Tensor) else a for a in args]
                cpu_kwargs = {k: v.cpu() if isinstance(v, torch.Tensor) else v for k, v in kwargs.items()}
                result = original_forward(*cpu_args, **cpu_kwargs)
                if target_device is not None:
                    if isinstance(result, torch.Tensor):
                        return result.to(target_device)
                    elif isinstance(result, tuple):
                        return tuple(r.to(target_device) if isinstance(r, torch.Tensor) else r for r in result)
                return result

            module.forward = cpu_forward
            module.cpu()
            module._xpu_cpu_patched = True
            patched_count += 1

    # 1. Built-in HiFi-GAN — walk the engine and its synthesizer (XTTS, VITS)
    if isinstance(engine, nn.Module):
        for _, module in engine.named_modules():
            _patch_hifigan_module(module)

    syn = getattr(engine, 'synthesizer', None)
    if syn is not None:
        if isinstance(syn, nn.Module):
            for _, module in syn.named_modules():
                _patch_hifigan_module(module)

        # 2. Separate vocoder (GlowTTS, Tacotron2, ...)
        vocoder = getattr(syn, 'vocoder_model', None)
        if vocoder is not None and isinstance(vocoder, nn.Module):
            if not getattr(vocoder, '_xpu_cpu_patched', False):
                print(f"[XPU Workaround] Found separate vocoder ({vocoder.__class__.__name__}); routing to CPU for XPU.")
                # Coqui picks the vocoder device from use_cuda. On a CUDA-less XPU
                # torch build that routes the input to 'cuda' and crashes. Clear it
                # so the input is sent to CPU instead.
                syn.use_cuda = False
                vocoder.cpu().eval()
                vocoder._xpu_cpu_patched = True
                patched_count += 1

    if patched_count > 0:
        print(f"[XPU Workaround] Successfully patched {patched_count} vocoder module(s) to run on CPU.")
    else:
        print("[XPU Workaround] No patchable vocoder modules found.")

    return engine