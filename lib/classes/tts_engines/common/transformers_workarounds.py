# lib/classes/tts_engines/common/transformers_workarounds.py
import sys, functools, inspect

# coqui-tts' GPT2InferenceModel classes: XTTS, and the Tortoise one it was copied from
coqui_gpt_inference_models = [
    ('TTS.tts.layers.xtts.gpt_inference', 'GPT2InferenceModel'),
    ('TTS.tts.layers.tortoise.autoregressive', 'GPT2InferenceModel'),
]

def _cache_as_past_key_values(forward):
    @functools.wraps(forward)
    def _forward(self, *args, cache=None, **kwargs):
        if cache is not None and kwargs.get('past_key_values') is None:
            kwargs['past_key_values'] = cache
        return forward(self, *args, **kwargs)
    _forward._e2a_cache_compat = True
    return _forward

def patch_coqui_gpt_cache()->int:
    """Makes coqui-tts' GPT2InferenceModel.forward() take the generation cache under the name transformers >= 5.24
    passes it. 5.24 renamed it past_key_values -> cache: generate() hands forward() cache=..., coqui-tts 0.28 reads
    past_key_values, which stays None, and the first decoding step dies on past_key_values.get_seq_length() (crash report
    db80ee0ce029d98b). The cache goes back in as past_key_values: GPT2Model and the output classes still take that name
    (deprecated until 5.40), and the output is token for token the one of 5.23. Before 5.24 cache= never arrives and the
    wrapper passes everything through. A forward() that declares cache itself (a fixed coqui-tts) is left alone.
    Class level and idempotent: safe at every engine load. Only modules already imported are touched: the engine that
    uses one has imported it, and VITS and the other Coqui models do not pay a transformers import for it.
    Remove it once no python_env runs a coqui-tts without the fix: python 3.10 (Jetson) stays on 0.28.0
    (DeviceInstaller.coqui_tts_py310_max) after requirements.txt moves to a fixed release.
    Returns the number of classes wrapped by this call"""
    patched = 0
    for module_name, class_name in coqui_gpt_inference_models:
        cls = getattr(sys.modules.get(module_name), class_name, None)
        if cls is None:
            continue
        forward = cls.forward
        if getattr(forward, '_e2a_cache_compat', False):
            continue
        try:
            if 'cache' in inspect.signature(forward).parameters:
                continue
        except (TypeError, ValueError):
            continue
        cls.forward = _cache_as_past_key_values(forward)
        patched += 1
    return patched
