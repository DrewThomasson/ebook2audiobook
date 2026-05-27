# coding=utf-8
# Copyright 2026 The Alibaba Qwen team.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A gradio demo for Qwen3 TTS models.
"""

import argparse
import os
import tempfile
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import numpy as np
import torch

from .. import Qwen3TTSModel, VoiceClonePromptItem


def _title_case_display(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("_", " ")
    return " ".join([w[:1].upper() + w[1:] if w else "" for w in s.split()])


def _build_choices_and_map(items: Optional[List[str]]) -> Tuple[List[str], Dict[str, str]]:
    if not items:
        return [], {}
    display = [_title_case_display(x) for x in items]
    mapping = {d: r for d, r in zip(display, items)}
    return display, mapping


def _dtype_from_str(s: str) -> torch.dtype:
    s = (s or "").strip().lower()
    if s in ("bf16", "bfloat16"):
        return torch.bfloat16
    if s in ("fp16", "float16", "half"):
        return torch.float16
    if s in ("fp32", "float32"):
        return torch.float32
    raise ValueError(f"Unsupported torch dtype: {s}. Use bfloat16/float16/float32.")


def _maybe(v):
    return v if v is not None else gr.update()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qwen-tts-demo",
        description=(
            "Launch a Gradio demo for Qwen3 TTS models (CustomVoice / VoiceDesign / Base).\n\n"
            "Examples:\n"
            "  qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice\n"
            "  qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --port 8000 --ip 127.0.0.01\n"
            "  qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-Base --device cuda:0\n"
            "  qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --dtype bfloat16 --no-flash-attn\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )

    # Positional checkpoint (also supports -c/--checkpoint)
    parser.add_argument(
        "checkpoint_pos",
        nargs="?",
        default=None,
        help="Model checkpoint path or HuggingFace repo id (positional).",
    )
    parser.add_argument(
        "-c",
        "--checkpoint",
        default=None,
        help="Model checkpoint path or HuggingFace repo id (optional if positional is provided).",
    )

    # Model loading / from_pretrained args
    parser.add_argument(
        "--device",
        default="cuda:0",
        help="Device for device_map, e.g. cpu, cuda, cuda:0 (default: cuda:0).",
    )
    parser.add_argument(
        "--dtype",
        default="bfloat16",
        choices=["bfloat16", "bf16", "float16", "fp16", "float32", "fp32"],
        help="Torch dtype for loading the model (default: bfloat16).",
    )
    parser.add_argument(
        "--flash-attn/--no-flash-attn",
        dest="flash_attn",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Enable FlashAttention-2 (default: enabled).",
    )

    # Gradio server args
    parser.add_argument(
        "--ip",
        default="0.0.0.0",
        help="Server bind IP for Gradio (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port for Gradio (default: 8000).",
    )
    parser.add_argument(
        "--share/--no-share",
        dest="share",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Whether to create a public Gradio link (default: disabled).",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=16,
        help="Gradio queue concurrency (default: 16).",
    )

    # HTTPS args
    parser.add_argument(
        "--ssl-certfile",
        default=None,
        help="Path to SSL certificate file for HTTPS (optional).",
    )
    parser.add_argument(
        "--ssl-keyfile",
        default=None,
        help="Path to SSL key file for HTTPS (optional).",
    )
    parser.add_argument(
        "--ssl-verify/--no-ssl-verify",
        dest="ssl_verify",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Whether to verify SSL certificate (default: enabled).",
    )

    # Optional generation args
    parser.add_argument("--max-new-tokens", type=int, default=None, help="Max new tokens for generation (optional).")
    parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature (optional).")
    parser.add_argument("--top-k", type=int, default=None, help="Top-k sampling (optional).")
    parser.add_argument("--top-p", type=float, default=None, help="Top-p sampling (optional).")
    parser.add_argument("--repetition-penalty", type=float, default=None, help="Repetition penalty (optional).")
    parser.add_argument("--subtalker-top-k", type=int, default=None, help="Subtalker top-k (optional, only for tokenizer v2).")
    parser.add_argument("--subtalker-top-p", type=float, default=None, help="Subtalker top-p (optional, only for tokenizer v2).")
    parser.add_argument(
        "--subtalker-temperature", type=float, default=None, help="Subtalker temperature (optional, only for tokenizer v2)."
    )

    return parser


def _resolve_checkpoint(args: argparse.Namespace) -> str:
    ckpt = args.checkpoint or args.checkpoint_pos
    if not ckpt:
        raise SystemExit(0)  # main() prints help
    return ckpt


def _collect_gen_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    mapping = {
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_k": args.top_k,
        "top_p": args.top_p,
        "repetition_penalty": args.repetition_penalty,
        "subtalker_top_k": args.subtalker_top_k,
        "subtalker_top_p": args.subtalker_top_p,
        "subtalker_temperature": args.subtalker_temperature,
    }
    return {k: v for k, v in mapping.items() if v is not None}


def _normalize_audio(wav, eps=1e-12, clip=True):
    x = np.asarray(wav)

    if np.issubdtype(x.dtype, np.integer):
        info = np.iinfo(x.dtype)

        if info.min < 0:
            y = x.astype(np.float32) / max(abs(info.min), info.max)
        else:
            mid = (info.max + 1) / 2.0
            y = (x.astype(np.float32) - mid) / mid

    elif np.issubdtype(x.dtype, np.floating):
        y = x.astype(np.float32)
        m = np.max(np.abs(y)) if y.size else 0.0

        if m <= 1.0 + 1e-6:
            pass
        else:
            y = y / (m + eps)
    else:
        raise TypeError(f"Unsupported dtype: {x.dtype}")

    if clip:
        y = np.clip(y, -1.0, 1.0)
    
    if y.ndim > 1:
        y = np.mean(y, axis=-1).astype(np.float32)

    return y


def _audio_to_tuple(audio: Any) -> Optional[Tuple[np.ndarray, int]]:
    if audio is None:
        return None

    if isinstance(audio, tuple) and len(audio) == 2 and isinstance(audio[0], int):
        sr, wav = audio
        wav = _normalize_audio(wav)
        return wav, int(sr)

    if isinstance(audio, dict) and "sampling_rate" in audio and "data" in audio:
        sr = int(audio["sampling_rate"])
        wav = _normalize_audio(audio["data"])
        return wav, sr

    return None


def _wav_to_gradio_audio(wav: np.ndarray, sr: int) -> Tuple[int, np.ndarray]:
    wav = np.asarray(wav, dtype=np.float32)
    return sr, wav


def _detect_model_kind(ckpt: str, tts: Qwen3TTSModel) -> str:
    mt = getattr(tts.model, "tts_model_type", None)
    if mt in ("custom_voice", "voice_design", "base"):
        return mt
    else:
        raise ValueError(f"Unknown Qwen-TTS model type: {mt}")


def build_demo(tts: Qwen3TTSModel, ckpt: str, gen_kwargs_default: Dict[str, Any]) -> gr.Blocks:
    model_kind = _detect_model_kind(ckpt, tts)

    supported_langs_raw = None
    if callable(getattr(tts.model, "get_supported_languages", None)):
        supported_langs_raw = tts.model.get_supported_languages()

    supported_spks_raw = None
    if callable(getattr(tts.model, "get_supported_speakers", None)):
        supported_spks_raw = tts.model.get_supported_speakers()

    lang_choices_disp, lang_map = _build_choices_and_map([x for x in (supported_langs_raw or [])])
    spk_choices_disp, spk_map = _build_choices_and_map([x for x in (supported_spks_raw or [])])

    def _gen_common_kwargs() -> Dict[str, Any]:
        return dict(gen_kwargs_default)

    theme = gr.themes.Soft(
        font=[gr.themes.GoogleFont("Source Sans Pro"), "Arial", "sans-serif"],
    )

    css = ".gradio-container {max-width: none !important;}"

    with gr.Blocks(theme=theme, css=css) as demo:
        gr.Markdown(
            f"""
# Qwen3 TTS Demo
**Checkpoint:** `{ckpt}`  
**Model Type:** `{model_kind}`  
"""
        )

        if model_kind == "custom_voice":
            with gr.Row():
                with gr.Column(scale=2):
                    text_in = gr.Textbox(
                        label="Text (待合成文本)",
                        lines=4,
                        placeholder="Enter text to synthesize (输入要合成的文本).",
                    )
                    with gr.Row():
                        lang_in = gr.Dropdown(
                            label="Language (语种)",
                            choices=lang_choices_disp,
                            value="Auto",
                            interactive=True,
                        )
                        spk_in = gr.Dropdown(
                            label="Speaker (说话人)",
                            choices=spk_choices_disp,
                            value="Vivian",
                            interactive=True,
                        )
                    instruct_in = gr.Textbox(
                        label="Instruction (Optional) (控制指令，可不输入)",
                        lines=2,
                        placeholder="e.g. Say it in a very angry tone (例如：用特别伤心的语气说).",
                    )
                    btn = gr.Button("Generate (生成)", variant="primary")
                with gr.Column(scale=3):
                    audio_out = gr.Audio(label="Output Audio (合成结果)", type="numpy")
                    err = gr.Textbox(label="Status (状态)", lines=2)

            def run_instruct(text: str, lang_disp: str, spk_disp: str, instruct: str):
                try:
                    if not text or not text.strip():
                        return None, "Text is required (必须填写文本)."
                    if not spk_disp:
                        return None, "Speaker is required (必须选择说话人)."
                    language = lang_map.get(lang_disp, "Auto")
                    speaker = spk_map.get(spk_disp, spk_disp)
                    kwargs = _gen_common_kwargs()
                    wavs, sr = tts.generate_custom_voice(
                        text=text.strip(),
                        language=language,
                        speaker=speaker,
                        instruct=(instruct or "").strip() or None,
                        **kwargs,
                    )
                    return _wav_to_gradio_audio(wavs[0], sr), "Finished. (生成完成)"
                except Exception as e:
                    return None, f"{type(e).__name__}: {e}"

            btn.click(run_instruct, inputs=[text_in, lang_in, spk_in, instruct_in], outputs=[audio_out, err])

        elif model_kind == "voice_design":
            with gr.Row():
                with gr.Column(scale=2):
                    text_in = gr.Textbox(
                        label="Text (待合成文本)",
                        lines=4,
                        value="It's in the top drawer... wait, it's empty? No way, that's impossible! I'm sure I put it there!"
                    )
                    with gr.Row():
                        lang_in = gr.Dropdown(
                            label="Language (语种)",
                            choices=lang_choices_disp,
                            value="Auto",
                            interactive=True,
                        )
                    design_in = gr.Textbox(
                        label="Voice Design Instruction (音色描述)",
                        lines=3,
                        value="Speak in an incredulous tone, but with a hint of panic beginning to creep into your voice."
                    )
                    btn = gr.Button("Generate (生成)", variant="primary")
                with gr.Column(scale=3):
                    audio_out = gr.Audio(label="Output Audio (合成结果)", type="numpy")
                    err = gr.Textbox(label="Status (状态)", lines=2)

            def run_voice_design(text: str, lang_disp: str, design: str):
                try:
                    if not text or not text.strip():
                        return None, "Text is required (必须填写文本)."
                    if not design or not design.strip():
                        return None, "Voice design instruction is required (必须填写音色描述)."
                    language = lang_map.get(lang_disp, "Auto")
                    kwargs = _gen_common_kwargs()
                    wavs, sr = tts.generate_voice_design(
                        text=text.strip(),
                        language=language,
                        instruct=design.strip(),
                        **kwargs,
                    )
                    return _wav_to_gradio_audio(wavs[0], sr), "Finished. (生成完成)"
                except Exception as e:
                    return None, f"{type(e).__name__}: {e}"

            btn.click(run_voice_design, inputs=[text_in, lang_in, design_in], outputs=[audio_out, err])

        else:  # voice_clone for base
            with gr.Tabs():
                with gr.Tab("Clone & Generate (克隆并合成)"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            ref_audio = gr.Audio(
                                label="Reference Audio (参考音频)",
                            )
                            ref_text = gr.Textbox(
                                label="Reference Text (参考音频文本)",
                                lines=2,
                                placeholder="Required if not set use x-vector only (不勾选use x-vector only时必填).",
                            )
                            xvec_only = gr.Checkbox(
                                label="Use x-vector only (仅用说话人向量，效果有限，但不用传入参考音频文本)",
                                value=False,
                            )

                        with gr.Column(scale=2):
                            text_in = gr.Textbox(
                                label="Target Text (待合成文本)",
                                lines=4,
                                placeholder="Enter text to synthesize (输入要合成的文本).",
                            )
                            lang_in = gr.Dropdown(
                                label="Language (语种)",
                                choices=lang_choices_disp,
                                value="Auto",
                                interactive=True,
                            )
                            btn = gr.Button("Generate (生成)", variant="primary")

                        with gr.Column(scale=3):
                            audio_out = gr.Audio(label="Output Audio (合成结果)", type="numpy")
                            err = gr.Textbox(label="Status (状态)", lines=2)

                    def run_voice_clone(ref_aud, ref_txt: str, use_xvec: bool, text: str, lang_disp: str):
                        try:
                            if not text or not text.strip():
                                return None, "Target text is required (必须填写待合成文本)."
                            at = _audio_to_tuple(ref_aud)
                            if at is None:
                                return None, "Reference audio is required (必须上传参考音频)."
                            if (not use_xvec) and (not ref_txt or not ref_txt.strip()):
                                return None, (
                                    "Reference text is required when use x-vector only is NOT enabled.\n"
                                    "(未勾选 use x-vector only 时，必须提供参考音频文本；否则请勾选 use x-vector only，但效果会变差.)"
                                )
                            language = lang_map.get(lang_disp, "Auto")
                            kwargs = _gen_common_kwargs()
                            wavs, sr = tts.generate_voice_clone(
                                text=text.strip(),
                                language=language,
                                ref_audio=at,
                                ref_text=(ref_txt.strip() if ref_txt else None),
                                x_vector_only_mode=bool(use_xvec),
                                **kwargs,
                            )
                            return _wav_to_gradio_audio(wavs[0], sr), "Finished. (生成完成)"
                        except Exception as e:
                            return None, f"{type(e).__name__}: {e}"

                    btn.click(
                        run_voice_clone,
                        inputs=[ref_audio, ref_text, xvec_only, text_in, lang_in],
                        outputs=[audio_out, err],
                    )

                with gr.Tab("Save / Load Voice (保存/加载克隆音色)"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            gr.Markdown(
                                """
### Save Voice (保存音色)
Upload reference audio and text, choose use x-vector only or not, then save a reusable voice prompt file.  
(上传参考音频和参考文本，选择是否使用 use x-vector only 模式后保存为可复用的音色文件)
"""
                            )
                            ref_audio_s = gr.Audio(label="Reference Audio (参考音频)", type="numpy")
                            ref_text_s = gr.Textbox(
                                label="Reference Text (参考音频文本)",
                                lines=2,
                                placeholder="Required if not set use x-vector only (不勾选use x-vector only时必填).",
                            )
                            xvec_only_s = gr.Checkbox(
                                label="Use x-vector only (仅用说话人向量，效果有限，但不用传入参考音频文本)",
                                value=False,
                            )
                            save_btn = gr.Button("Save Voice File (保存音色文件)", variant="primary")
                            prompt_file_out = gr.File(label="Voice File (音色文件)")

                        with gr.Column(scale=2):
                            gr.Markdown(
                                """
### Load Voice & Generate (加载音色并合成)
Upload a previously saved voice file, then synthesize new text.  
(上传已保存提示文件后，输入新文本进行合成)
"""
                            )
                            prompt_file_in = gr.File(label="Upload Prompt File (上传提示文件)")
                            text_in2 = gr.Textbox(
                                label="Target Text (待合成文本)",
                                lines=4,
                                placeholder="Enter text to synthesize (输入要合成的文本).",
                            )
                            lang_in2 = gr.Dropdown(
                                label="Language (语种)",
                                choices=lang_choices_disp,
                                value="Auto",
                                interactive=True,
                            )
                            gen_btn2 = gr.Button("Generate (生成)", variant="primary")

                        with gr.Column(scale=3):
                            audio_out2 = gr.Audio(label="Output Audio (合成结果)", type="numpy")
                            err2 = gr.Textbox(label="Status (状态)", lines=2)

                    def save_prompt(ref_aud, ref_txt: str, use_xvec: bool):
                        try:
                            at = _audio_to_tuple(ref_aud)
                            if at is None:
                                return None, "Reference audio is required (必须上传参考音频)."
                            if (not use_xvec) and (not ref_txt or not ref_txt.strip()):
                                return None, (
                                    "Reference text is required when use x-vector only is NOT enabled.\n"
                                    "(未勾选 use x-vector only 时，必须提供参考音频文本；否则请勾选 use x-vector only，但效果会变差.)"
                                )
                            items = tts.create_voice_clone_prompt(
                                ref_audio=at,
                                ref_text=(ref_txt.strip() if ref_txt else None),
                                x_vector_only_mode=bool(use_xvec),
                            )
                            payload = {
                                "items": [asdict(it) for it in items],
                            }
                            fd, out_path = tempfile.mkstemp(prefix="voice_clone_prompt_", suffix=".pt")
                            os.close(fd)
                            torch.save(payload, out_path)
                            return out_path, "Finished. (生成完成)"
                        except Exception as e:
                            return None, f"{type(e).__name__}: {e}"

                    def load_prompt_and_gen(file_obj, text: str, lang_disp: str):
                        try:
                            if file_obj is None:
                                return None, "Voice file is required (必须上传音色文件)."
                            if not text or not text.strip():
                                return None, "Target text is required (必须填写待合成文本)."

                            path = getattr(file_obj, "name", None) or getattr(file_obj, "path", None) or str(file_obj)
                            payload = torch.load(path, map_location="cpu", weights_only=True)
                            if not isinstance(payload, dict) or "items" not in payload:
                                return None, "Invalid file format (文件格式不正确)."

                            items_raw = payload["items"]
                            if not isinstance(items_raw, list) or len(items_raw) == 0:
                                return None, "Empty voice items (音色为空)."

                            items: List[VoiceClonePromptItem] = []
                            for d in items_raw:
                                if not isinstance(d, dict):
                                    return None, "Invalid item format in file (文件内部格式错误)."
                                ref_code = d.get("ref_code", None)
                                if ref_code is not None and not torch.is_tensor(ref_code):
                                    ref_code = torch.tensor(ref_code)
                                ref_spk = d.get("ref_spk_embedding", None)
                                if ref_spk is None:
                                    return None, "Missing ref_spk_embedding (缺少说话人向量)."
                                if not torch.is_tensor(ref_spk):
                                    ref_spk = torch.tensor(ref_spk)

                                items.append(
                                    VoiceClonePromptItem(
                                        ref_code=ref_code,
                                        ref_spk_embedding=ref_spk,
                                        x_vector_only_mode=bool(d.get("x_vector_only_mode", False)),
                                        icl_mode=bool(d.get("icl_mode", not bool(d.get("x_vector_only_mode", False)))),
                                        ref_text=d.get("ref_text", None),
                                    )
                                )

                            language = lang_map.get(lang_disp, "Auto")
                            kwargs = _gen_common_kwargs()
                            wavs, sr = tts.generate_voice_clone(
                                text=text.strip(),
                                language=language,
                                voice_clone_prompt=items,
                                **kwargs,
                            )
                            return _wav_to_gradio_audio(wavs[0], sr), "Finished. (生成完成)"
                        except Exception as e:
                            return None, (
                                f"Failed to read or use voice file. Check file format/content.\n"
                                f"(读取或使用音色文件失败，请检查文件格式或内容)\n"
                                f"{type(e).__name__}: {e}"
                            )

                    save_btn.click(save_prompt, inputs=[ref_audio_s, ref_text_s, xvec_only_s], outputs=[prompt_file_out, err2])
                    gen_btn2.click(load_prompt_and_gen, inputs=[prompt_file_in, text_in2, lang_in2], outputs=[audio_out2, err2])

        gr.Markdown(
            """
**Disclaimer (免责声明)**  
- The audio is automatically generated/synthesized by an AI model solely to demonstrate the model’s capabilities; it may be inaccurate or inappropriate, does not represent the views of the developer/operator, and does not constitute professional advice. You are solely responsible for evaluating, using, distributing, or relying on this audio; to the maximum extent permitted by applicable law, the developer/operator disclaims liability for any direct, indirect, incidental, or consequential damages arising from the use of or inability to use the audio, except where liability cannot be excluded by law. Do not use this service to intentionally generate or replicate unlawful, harmful, defamatory, fraudulent, deepfake, or privacy/publicity/copyright/trademark‑infringing content; if a user prompts, supplies materials, or otherwise facilitates any illegal or infringing conduct, the user bears all legal consequences and the developer/operator is not responsible.
- 音频由人工智能模型自动生成/合成，仅用于体验与展示模型效果，可能存在不准确或不当之处；其内容不代表开发者/运营方立场，亦不构成任何专业建议。用户应自行评估并承担使用、传播或依赖该音频所产生的一切风险与责任；在适用法律允许的最大范围内，开发者/运营方不对因使用或无法使用本音频造成的任何直接、间接、附带或后果性损失承担责任（法律另有强制规定的除外）。严禁利用本服务故意引导生成或复制违法、有害、诽谤、欺诈、深度伪造、侵犯隐私/肖像/著作权/商标等内容；如用户通过提示词、素材或其他方式实施或促成任何违法或侵权行为，相关法律后果由用户自行承担，与开发者/运营方无关。
"""
        )

    return demo


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.checkpoint and not args.checkpoint_pos:
        parser.print_help()
        return 0

    ckpt = _resolve_checkpoint(args)

    dtype = _dtype_from_str(args.dtype)
    attn_impl = "flash_attention_2" if args.flash_attn else None

    tts = Qwen3TTSModel.from_pretrained(
        ckpt,
        device_map=args.device,
        dtype=dtype,
        attn_implementation=attn_impl,
    )

    gen_kwargs_default = _collect_gen_kwargs(args)
    demo = build_demo(tts, ckpt, gen_kwargs_default)

    launch_kwargs: Dict[str, Any] = dict(
        server_name=args.ip,
        server_port=args.port,
        share=args.share,
        ssl_verify=True if args.ssl_verify else False,
    )
    if args.ssl_certfile is not None:
        launch_kwargs["ssl_certfile"] = args.ssl_certfile
    if args.ssl_keyfile is not None:
        launch_kwargs["ssl_keyfile"] = args.ssl_keyfile

    demo.queue(default_concurrency_limit=int(args.concurrency)).launch(**launch_kwargs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
