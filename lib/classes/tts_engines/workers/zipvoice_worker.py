# Runs inside lib/classes/tts_engines/venvs/zipvoice, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 24000|48000, "device": "...", "backend": "torch"|"onnx", "checkpoint": repo} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "voice", "file", "num_step", "guidance_scale", "t_shift", "speed", "target_rms"}
#   stdout <- {"ok": true, "file": "...", "samplerate": n, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
import os, sys, re, json, argparse, hashlib, gc, types, faulthandler

# whisper language code -> espeak-ng voice, where they differ (the prompt transcript is phonemized in the voice's own
# language, the text in the checkpoint's)
espeak_voices:dict = {"en": "en-us", "zh": "cmn", "pt": "pt-br", "jw": "jv", "haw": "haw", "yue": "yue"}

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True)
    parser.add_argument('--lina_src', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--model_dir', required=True)
    parser.add_argument('--assets_dir', required=True)
    parser.add_argument('--vocoder', required=True)
    parser.add_argument('--vocoder_dir', required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--asr_model', default='openai/whisper-large-v3-turbo')
    parser.add_argument('--asr_dir', required=True)
    parser.add_argument('--cache_dir', required=True)
    parser.add_argument('--ref_max', type=float, default=6.0)
    args = parser.parse_args()
    try:
        ckpt_cfg = json.loads(args.checkpoint)
        vocoder_cfg = json.loads(args.vocoder)
        os.makedirs(args.cache_dir, exist_ok=True)
        from huggingface_hub import snapshot_download

        def fetch(cfg:dict, model_dir:str, assets_dir:str)->tuple:
            # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink
            # probe races under threaded downloads (WinError 1314 on windows without symlink rights).
            # Only the checkpoint's own files: a repo can hold several models (k2-fsa/ZipVoice). Downloaded once,
            # then never checked again (an offline start keeps working).
            onnx_files = cfg.get('onnx') or {}
            if onnx_files:
                ckpt_file = weights_file = ''
                model_files = list(onnx_files.values())
            else:
                # a .pt checkpoint, or one whose keys carry a prefix (a transformers wrapper's "model."), is kept
                # as the one weight set inference loads (see below): its .e2a.safetensors
                ckpt_file = os.path.join(model_dir, cfg['ckpt'])
                weights_file = f'{os.path.splitext(ckpt_file)[0]}.e2a.safetensors' if ckpt_file.endswith('.pt') or cfg.get('prefix') else ckpt_file
                model_files = [] if os.path.exists(weights_file) else [cfg['ckpt']]
            # model.json / tokens.txt come from assets_repo when the checkpoint ships without them (fine-tunes of
            # the base model keep its config and its token table)
            assets_repo = cfg.get('assets_repo') or cfg['repo']
            assets_dir = assets_dir if assets_repo != cfg['repo'] else model_dir
            asset_files = [cfg['config'], cfg['tokens']]
            if assets_dir == model_dir:
                model_files += asset_files
            model_files = [f for f in model_files if not os.path.exists(os.path.join(model_dir, f))]
            if model_files:
                snapshot_download(cfg['repo'], local_dir=model_dir, allow_patterns=model_files)
            if assets_dir != model_dir and not all(os.path.exists(os.path.join(assets_dir, f)) for f in asset_files):
                snapshot_download(assets_repo, local_dir=assets_dir, allow_patterns=asset_files)
            return model_dir, ckpt_file, weights_file, onnx_files, os.path.join(assets_dir, cfg['config']), os.path.join(assets_dir, cfg['tokens'])

        try:
            model_dir, ckpt_file, weights_file, onnx_files, config_file, token_file = fetch(ckpt_cfg, args.model_dir, args.assets_dir)
        except Exception as e:
            # a gated repo refuses the download until the account of HF_TOKEN accepted its conditions: its
            # ungated "fallback" checkpoint then (its own folder beside the gated one's under models/tts/zipvoice)
            refused = type(e).__name__ in ('GatedRepoError', 'RepositoryNotFoundError') or getattr(getattr(e, 'response', None), 'status_code', None) in (401, 403)
            if not (refused and ckpt_cfg.get('fallback')):
                raise
            print(f"{ckpt_cfg['repo']} refused ({type(e).__name__}): {ckpt_cfg['fallback']['repo']} instead", file=sys.stderr)
            ckpt_cfg = ckpt_cfg['fallback']
            fallback_dir = os.path.join(os.path.dirname(args.model_dir), ckpt_cfg['repo'].replace('/', '--'))
            model_dir, ckpt_file, weights_file, onnx_files, config_file, token_file = fetch(ckpt_cfg, fallback_dir, fallback_dir)
        if not all(os.path.exists(os.path.join(args.vocoder_dir, f)) for f in vocoder_cfg['files']):
            snapshot_download(vocoder_cfg['repo'], local_dir=args.vocoder_dir, allow_patterns=vocoder_cfg['files'])
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS
            # +vulkan builds): encodec (imported by vocos) reads torch.distributed.ReduceOp at import and calls
            # is_initialized() at run time; single-process inference only needs them to exist
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import torchaudio
        import soundfile as sf
        # upstream is not a package: imported from its pinned tree
        sys.path.insert(0, args.src)
        from zipvoice.models.zipvoice import ZipVoice
        from zipvoice.models.zipvoice_distill import ZipVoiceDistill
        from zipvoice.models.modules.solver import get_time_steps
        from zipvoice.tokenizer.tokenizer import EmiliaTokenizer, EspeakTokenizer, SimpleTokenizer
        from zipvoice.utils.feature import VocosFbank
        from zipvoice.utils.infer import add_punctuation, batchify_tokens, chunk_tokens_punctuation, cross_fade_concat, remove_silence, rms_norm
        torch.manual_seed(666)
        device = args.device
        with open(config_file, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        # some community repos name it config.json and add their own keys around "model" / "feature"
        if model_config.get('feature', {}).get('type', 'vocos') != 'vocos':
            raise ValueError(f"unsupported feature type {model_config['feature']['type']!r}")
        feature_sr = int(model_config.get('feature', {}).get('sampling_rate', 24000))

        def make_tokenizer(lang:str)->object:
            if ckpt_cfg['tokenizer'] == 'espeak':
                return EspeakTokenizer(token_file=token_file, lang=lang)
            if ckpt_cfg['tokenizer'] == 'simple':
                return SimpleTokenizer(token_file=token_file)
            return EmiliaTokenizer(token_file=token_file)

        tokenizer = make_tokenizer(ckpt_cfg.get('lang', 'en-us'))
        prompt_tokenizers = {}
        backend = 'onnx' if onnx_files else 'torch'
        if backend == 'onnx':
            # ONNX-only releases (k2-fsa's export format: text encoder + one flow-matching step with its
            # classifier-free guidance inside), run by onnxruntime on cpu with every core
            import onnxruntime as ort
            session_opts = ort.SessionOptions()
            session_opts.intra_op_num_threads = os.cpu_count() or 1
            session_opts.inter_op_num_threads = 1
            text_encoder = ort.InferenceSession(os.path.join(model_dir, onnx_files['text_encoder']), sess_options=session_opts, providers=['CPUExecutionProvider'])
            fm_decoder = ort.InferenceSession(os.path.join(model_dir, onnx_files['fm_decoder']), sess_options=session_opts, providers=['CPUExecutionProvider'])
            feat_dim = int(model_config['model']['feat_dim'])
            model = None
        else:
            if weights_file != ckpt_file and not os.path.exists(weights_file):
                # icefall checkpoints ({"model": state_dict}, training ones with the optimizer, the sampler and
                # the averaged model too: 1.8 GB for 123M params), plain state dicts (fp16 ones too) and
                # safetensors whose keys carry a prefix: the weights alone are saved once as fp32 safetensors
                # with upstream's key names, read through mmap, and the original is dropped.
                # weights_only False: icefall pickles its params (zipvoice.utils.common.AttributeDict) beside
                # the weights, importable now that the tree is on sys.path
                from safetensors.torch import save_file, load_file
                if ckpt_file.endswith('.safetensors'):
                    checkpoint = load_file(ckpt_file)
                else:
                    checkpoint = torch.load(ckpt_file, map_location='cpu', weights_only=False, mmap=True)
                state = checkpoint['model'] if isinstance(checkpoint, dict) and isinstance(checkpoint.get('model'), dict) else checkpoint
                prefix = ckpt_cfg.get('prefix', '')
                # DDP training saves every key under module.; a wrapper's own keys (no prefix) are not the model's
                state = {k.removeprefix('module.').removeprefix(prefix): v.float() if v.is_floating_point() else v for k, v in state.items() if isinstance(v, torch.Tensor) and k.removeprefix('module.').startswith(prefix)}
                save_file({k: v.contiguous() for k, v in state.items()}, f'{weights_file}.part')
                os.replace(f'{weights_file}.part', weights_file)
                del checkpoint, state
                gc.collect()
                os.unlink(ckpt_file)
            # zipvoice: flow matching with classifier-free guidance (2 passes a step); zipvoice_distill: the
            # guidance scale is an input embedding (1 pass a step, 4 to 8 steps)
            model_class = ZipVoiceDistill if ckpt_cfg['model'] == 'zipvoice_distill' else ZipVoice
            model = model_class(**model_config['model'], vocab_size=tokenizer.vocab_size, pad_id=tokenizer.pad_id)
            import safetensors.torch
            # strict: a base checkpoint in the distill class (or the reverse) stops here, not with noise
            safetensors.torch.load_model(model, weights_file, strict=True)
            model = model.to(device).eval()
        feature_extractor = VocosFbank()
        if vocoder_cfg['name'] == 'lux48k':
            # LuxTTS' 48 kHz vocoder: Vocos backbone + LinaCodec's upsampler and 48 kHz head, merged with the 24 kHz
            # head under 4 kHz. Only LinaCodec's vocoder modules are loaded: its package __init__ imports the whole
            # codec (flash-attn, jsonargparse...), so linacodec is registered as a bare package over its tree and its
            # config.yaml class paths (linacodec.vocoder.upsampler_block...) resolve from there
            from torch.nn.utils import parametrize
            linacodec = types.ModuleType('linacodec')
            linacodec.__path__ = [os.path.join(args.lina_src, 'src', 'linacodec')]
            sys.modules['linacodec'] = linacodec
            from linacodec.vocoder.vocos import Vocos as LinaVocos
            vocoder = LinaVocos.from_hparams(os.path.join(args.vocoder_dir, vocoder_cfg['files'][0]))
            # vocos.bin holds the plain weights of the weight-normed transposed convolutions
            for layer in vocoder.upsampler.upsample_layers:
                parametrize.remove_parametrizations(layer, 'weight')
            vocoder.load_state_dict(torch.load(os.path.join(args.vocoder_dir, vocoder_cfg['files'][1]), map_location='cpu', weights_only=True))
        else:
            # upstream's own vocoder (get_vocoder in zipvoice/bin/infer_zipvoice.py), from its plain folder
            from vocos import Vocos
            vocoder = Vocos.from_hparams(os.path.join(args.vocoder_dir, vocoder_cfg['files'][0]))
            vocoder.load_state_dict(torch.load(os.path.join(args.vocoder_dir, vocoder_cfg['files'][1]), map_location='cpu', weights_only=True))
        vocoder = vocoder.to(device).eval()
        sampling_rate = int(vocoder_cfg['samplerate'])
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1

    def onnx_sample(tokens:list, prompt_tokens:list, prompt_features:'torch.Tensor', speed:float, t_shift:float, guidance_scale:float, num_step:int)->'torch.Tensor':
        # upstream's sample() of zipvoice/bin/infer_zipvoice_onnx.py, feat_dim read from model.json (not every
        # export carries upstream's metadata)
        feeds = [np.asarray([tokens], dtype=np.int64), np.asarray([prompt_tokens], dtype=np.int64), np.asarray(prompt_features.size(1), dtype=np.int64), np.asarray(speed, dtype=np.float32)]
        text_condition = text_encoder.run([text_encoder.get_outputs()[0].name], {i.name: v for i, v in zip(text_encoder.get_inputs(), feeds)})[0]
        num_frames = text_condition.shape[1]
        timesteps = get_time_steps(t_start=0.0, t_end=1.0, num_step=num_step, t_shift=t_shift)
        x = torch.randn(1, num_frames, feat_dim).numpy()
        speech_condition = torch.nn.functional.pad(prompt_features.cpu(), (0, 0, 0, num_frames - prompt_features.size(1))).numpy()
        names = [i.name for i in fm_decoder.get_inputs()]
        for step in range(num_step):
            values = [np.asarray(float(timesteps[step]), dtype=np.float32), x, text_condition, speech_condition, np.asarray(guidance_scale, dtype=np.float32)]
            v = fm_decoder.run([fm_decoder.get_outputs()[0].name], dict(zip(names, values)))[0]
            x = x + v * float(timesteps[step + 1] - timesteps[step])
        return torch.from_numpy(x[:, prompt_features.size(1):, :])

    def prompt_tokens_for(text:str, lang:str)->list:
        # espeak checkpoints: the transcript phonemized in the voice's own language (Whisper's), the token table is
        # shared IPA; emilia reads English and Chinese by script, simple ones read characters
        if ckpt_cfg['tokenizer'] == 'espeak' and lang:
            voice = espeak_voices.get(lang, lang)
            if voice.split('-')[0] != ckpt_cfg.get('lang', '').split('-')[0]:
                if voice not in prompt_tokenizers:
                    prompt_tokenizers[voice] = make_tokenizer(voice)
                tokens = prompt_tokenizers[voice].texts_to_tokens([text])[0]
                if tokens:
                    return tokens
        return tokenizer.texts_to_tokens([text])[0]

    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': device, 'backend': backend, 'checkpoint': ckpt_cfg['repo']}) + '\n')
    refs = {}
    asr = None
    while True:
        raw = sys.stdin.buffer.readline()
        if not raw:
            break
        try:
            req = json.loads(raw)
        except Exception as e:
            proto.write(json.dumps({'ok': False, 'error': f'bad request: {e}', 'oom': False}) + '\n')
            continue
        if req.get('op') != 'tts':
            proto.write(json.dumps({'ok': False, 'error': f"unknown op {req.get('op')!r}", 'oom': False}) + '\n')
            continue
        try:
            voice = req['voice']
            target_rms = float(req.get('target_rms', 0.1))
            voice_key = f'{voice}:{os.path.getmtime(voice)}:{args.ref_max}'
            if voice_key not in refs:
                clip = os.path.join(args.cache_dir, hashlib.sha1(voice_key.encode('utf-8')).hexdigest() + '.wav')
                if not os.path.exists(clip):
                    # keep at most ref_max (ZipVoice asks for a short prompt: a long one slows every sentence and
                    # leaks into the speech), cutting at the quietest 50 ms of the last 3 s so no word is clipped
                    data, sr = sf.read(voice, dtype='float32', always_2d=True)
                    mono = data.mean(axis=1)
                    max_len = int(args.ref_max * sr)
                    if len(mono) > max_len:
                        start = max(0, max_len - 3 * sr)
                        frame = int(0.05 * sr)
                        tail = mono[start:max_len]
                        energies = [float(np.mean(tail[i:i + frame] ** 2)) for i in range(0, len(tail) - frame, frame)]
                        mono = mono[:start + int(np.argmin(energies)) * frame + frame // 2] if energies else mono[:max_len]
                    sf.write(clip, mono, sr)
                data, sr = sf.read(clip, dtype='float32', always_2d=True)
                prompt_wav = torch.from_numpy(data.mean(axis=1)).unsqueeze(0)
                # the transcript and its language are kept beside the clip: Whisper runs once per voice, ever
                text_file = f'{clip[:-4]}.json'
                if os.path.exists(text_file):
                    with open(text_file, 'r', encoding='utf-8') as f:
                        ref = json.load(f)
                else:
                    # Whisper on cpu (no VRAM taken from the model), downloaded as a plain folder, its language
                    # detected (the voice is often not in the book's language); released after use. Complete once
                    # the marker exists: config.json lands first, so a download cut during the weights would
                    # otherwise look finished forever; snapshot_download resumes what is missing
                    asr_marker = os.path.join(args.asr_dir, '.e2a_complete')
                    if not os.path.exists(asr_marker):
                        snapshot_download(args.asr_model, local_dir=args.asr_dir)
                        open(asr_marker, 'w').close()
                    import transformers
                    from transformers import WhisperForConditionalGeneration, WhisperProcessor
                    from transformers.utils import logging as transformers_logging
                    verbosity = transformers_logging.get_verbosity()
                    transformers_logging.set_verbosity_error()
                    try:
                        processor = WhisperProcessor.from_pretrained(args.asr_dir)
                        # fp32 on cpu: transformers 5 loads the checkpoint's own dtype by default (fp16 for large-v3-turbo)
                        dtype_kwarg = 'dtype' if int(transformers.__version__.split('.')[0]) >= 5 else 'torch_dtype'
                        asr = WhisperForConditionalGeneration.from_pretrained(args.asr_dir, **{dtype_kwarg: torch.float32}).eval()
                        audio_16k = torchaudio.functional.resample(prompt_wav[0], sr, 16000).numpy()
                        features = processor(audio_16k, sampling_rate=16000, return_tensors='pt').input_features
                        with torch.inference_mode():
                            lang = ''
                            if hasattr(asr, 'detect_language'):
                                lang_ids = asr.detect_language(features)
                                lang = processor.tokenizer.convert_ids_to_tokens(lang_ids.tolist())[0].strip('<|>')
                            ids = asr.generate(features, language=lang or None, task='transcribe')
                        ref = {'text': processor.batch_decode(ids, skip_special_tokens=True)[0].strip(), 'lang': lang}
                    finally:
                        asr = None
                        transformers_logging.set_verbosity(verbosity)
                        gc.collect()
                    if not ref['text']:
                        raise ValueError(f'no speech found in the voice reference {voice}')
                    with open(text_file, 'w', encoding='utf-8') as f:
                        json.dump(ref, f, ensure_ascii=False)
                # upstream's prompt preparation (generate_sentence in zipvoice/bin/infer_zipvoice.py): resampled to
                # the feature rate, inner silences over 1 s and the edges cut, 0.2 s of trailing silence so the
                # prompt does not leak into the speech, loudness raised to target_rms
                if sr != feature_sr:
                    prompt_wav = torchaudio.functional.resample(prompt_wav, sr, feature_sr)
                prompt_wav = remove_silence(prompt_wav, feature_sr, only_edge=False, trail_sil=200)
                prompt_wav, prompt_rms = rms_norm(prompt_wav, target_rms)
                prompt_features = feature_extractor.extract(prompt_wav, sampling_rate=feature_sr).to(device).unsqueeze(0) * 0.1
                ref_text = ref['text'].lower() if ckpt_cfg.get('lowercase') else ref['text']
                prompt_tokens_str = prompt_tokens_for(add_punctuation(ref_text), ref.get('lang', ''))
                if not prompt_tokens_str:
                    raise ValueError(f"the voice reference transcript has no token of this model: {ref['text']!r}")
                refs[voice_key] = (prompt_features, float(prompt_rms), prompt_wav.shape[-1] / feature_sr, prompt_tokens_str)
            prompt_features, prompt_rms, prompt_duration, prompt_tokens_str = refs[voice_key]
            text = req['text'].strip()
            if ckpt_cfg.get('lowercase'):
                text = text.lower()
            num_step = int(req.get('num_step', 16))
            speed = float(req.get('speed', 1.0)) * float(ckpt_cfg.get('speed_factor', 1.0))
            if ckpt_cfg.get('short_text'):
                # ViZipVoice's own rule (vizipvoice.py get_sentence_inference_params): one word gets more steps and
                # slower speech, two to four words slower speech
                words = len(re.findall(r'\w+', text, flags=re.UNICODE))
                if words == 1:
                    num_step, speed = max(num_step, 24), speed * 0.6
                elif 2 <= words <= 4:
                    speed *= 0.8
            guidance_scale = float(req.get('guidance_scale', 1.0))
            t_shift = float(req.get('t_shift', 0.5))
            tokens_str = tokenizer.texts_to_tokens([add_punctuation(text)])[0]
            if not tokens_str:
                raise ValueError('the text has no token of this model')
            # upstream's chunking: each prompt + chunk stays around 25 s, chunks cut on punctuation
            token_duration = prompt_duration / (len(prompt_tokens_str) * speed)
            max_tokens = max(1, int((25 - prompt_duration) / token_duration))
            chunked_tokens = tokenizer.tokens_to_token_ids(chunk_tokens_punctuation(tokens_str, max_tokens=max_tokens))
            prompt_tokens = tokenizer.tokens_to_token_ids([prompt_tokens_str])[0]
            chunked_features = []
            with torch.inference_mode():
                if model is not None:
                    tokens_batches, chunked_index = batchify_tokens(chunked_tokens, 100, prompt_duration, token_duration)
                    for batch_tokens in tokens_batches:
                        batch_size = len(batch_tokens)
                        pred_features, pred_features_lens, _, _ = model.sample(
                            tokens=batch_tokens,
                            prompt_tokens=[prompt_tokens] * batch_size,
                            prompt_features=prompt_features.repeat(batch_size, 1, 1),
                            prompt_features_lens=torch.full((batch_size,), prompt_features.size(1), device=device),
                            speed=speed,
                            t_shift=t_shift,
                            duration='predict',
                            num_step=num_step,
                            guidance_scale=guidance_scale
                        )
                        pred_features = pred_features.permute(0, 2, 1) / 0.1
                        chunked_features += [pred_features[i][None, :, :pred_features_lens[i]] for i in range(batch_size)]
                else:
                    chunked_index = list(range(len(chunked_tokens)))
                    for chunk in chunked_tokens:
                        pred_features = onnx_sample(chunk, prompt_tokens, prompt_features, speed, t_shift, guidance_scale, num_step)
                        chunked_features.append((pred_features.permute(0, 2, 1) / 0.1).to(device))
                wavs = []
                for features in chunked_features:
                    wav = vocoder.decode(features).squeeze(1).clamp(-1, 1).float().cpu()
                    if prompt_rms < target_rms:
                        wav = wav * prompt_rms / target_rms
                    wavs.append(wav)
            wavs = [wav for _, wav in sorted(zip(chunked_index, wavs), key=lambda item: item[0])]
            # the vocoder's rate from here on (48 kHz for LuxTTS' vocoder), not the feature rate upstream assumes
            final_wav = cross_fade_concat(wavs, fade_duration=0.1, sample_rate=sampling_rate)
            final_wav = remove_silence(final_wav, sampling_rate, only_edge=True, trail_sil=0)
            audio = final_wav.reshape(-1).numpy().astype(np.float32)
            if audio.size == 0:
                raise ValueError('no audio generated')
            sf.write(req['file'], audio, sampling_rate, subtype='FLOAT')
            reply = {'ok': True, 'file': req['file'], 'samplerate': sampling_rate, 'samples': int(audio.shape[0])}
        except Exception as e:
            # no retry here: e2a's convert() returns False and core.py unloads the
            # engine, which closes stdin and ends this process.
            error = f'{type(e).__name__}: {e}'
            reply = {'ok': False, 'error': error, 'oom': 'out of memory' in error.lower()}
            try:
                if device == 'cuda':
                    torch.cuda.empty_cache()
                elif device == 'xpu':
                    torch.xpu.empty_cache()
                elif device == 'mps':
                    torch.mps.empty_cache()
            except Exception:
                pass
        proto.write(json.dumps(reply) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
