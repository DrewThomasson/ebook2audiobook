import asyncio
import base64
import time
import uuid
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional
import subprocess

import ebooklib
import gradio as gr
import torch
import torchaudio
from ebooklib import epub
from bs4 import BeautifulSoup

from auralis import TTS, TTSRequest, TTSOutput, AudioPreprocessingConfig, setup_logger
import hashlib
logger = setup_logger(__file__)

tts = TTS()
model_path = "AstraMindAI/xttsv2"  # change this if you have a different model
gpt_model = "AstraMindAI/xtts2-gpt"
try:
    tts = tts.from_pretrained(model_path, gpt_model=gpt_model)
    logger.info(f"Successfully loaded model {model_path}")
except Exception as e:
    logger.error(f"Failed to load model: {e}. Ensure that the model exists at {model_path}")

# Create a temporary directory to store short-named files
temp_dir = Path("/tmp/auralis")
temp_dir.mkdir(exist_ok=True)

def convert_ebook_to_txt(input_path: str) -> str:
    """
    Convert any ebook format to txt using calibre's ebook-convert
    Returns the path to the converted txt file
    """
    output_path = str(temp_dir / f"{uuid.uuid4().hex[:8]}.txt")
    try:
        subprocess.run(['ebook-convert', input_path, output_path], 
                      check=True, capture_output=True, text=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Conversion failed: {e.stderr}")
        raise RuntimeError(f"Failed to convert ebook: {e.stderr}")

def shorten_filename(original_path: str) -> str:
    """Copies the given file to a temporary directory with a shorter, random filename."""
    ext = Path(original_path).suffix
    short_name = "file_" + uuid.uuid4().hex[:8] + ext
    short_path = temp_dir / short_name
    shutil.copyfile(original_path, short_path)
    return str(short_path)

def text_from_file(file_path: str) -> str:
    """Read text from a file, converting if necessary."""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext in ['.txt']:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Convert other formats to txt first
        txt_path = convert_ebook_to_txt(file_path)
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()

def clone_voice(audio_path: str):
    """Clone a voice from an audio path."""
    audio_short_path = shorten_filename(audio_path)
    with open(audio_short_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode('utf-8')
    return audio_data

def process_text_and_generate(input_text, ref_audio_files, speed, enhance_speech, temperature, top_p, top_k, repetition_penalty, language, *args):
    """Process text and generate audio."""
    log_messages = ""
    if not ref_audio_files:
        log_messages += "Please provide at least one reference audio!\n"
        return None, log_messages

    # clone voices from all file paths (shorten them)
    base64_voices = ref_audio_files[:5]

    request = TTSRequest(
        text=input_text,
        speaker_files=base64_voices,
        stream=False,
        enhance_speech=enhance_speech,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        language=language,
    )

    try:
        with torch.no_grad():
            output = tts.generate_speech(request)
            if output:
                if speed != 1:
                    output.change_speed(speed)
                log_messages += f"✅ Successfully Generated audio\n"
                return (output.sample_rate, output.array), log_messages
            else:
                log_messages += "❌ No output was generated. Check that the model was correctly loaded\n"
                return None, log_messages
    except Exception as e:
        logger.error(f"Error: {e}")
        log_messages += f"❌ An Error occured: {e}\n"
        return None, log_messages

def build_gradio_ui():
    """Builds and launches the Gradio UI for Auralis."""
    with gr.Blocks(title="Auralis TTS Demo", theme="soft") as ui:
        gr.Markdown(
            """
            # Auralis Text-to-Speech Demo 🌌
            Convert text or ebooks to speech with advanced voice cloning and enhancement.
            """
        )

        with gr.Tab("File to Speech"):
            with gr.Row():
                with gr.Column():
                    file_input = gr.File(
                        label="Upload Book/Text File", 
                        file_types=[
                            ".txt", ".epub", ".mobi", ".azw3", ".fb2", 
                            ".htmlz", ".lit", ".pdb", ".pdf", ".rtf"
                        ]
                    )
                    ref_audio_files = gr.Files(
                        label="Reference Audio Files", 
                        file_types=["audio"]
                    )
                    with gr.Accordion("Advanced settings", open=False):
                        speed = gr.Slider(
                            label="Playback speed", 
                            minimum=0.5, 
                            maximum=2.0, 
                            value=1.0, 
                            step=0.1
                        )
                        enhance_speech = gr.Checkbox(
                            label="Enhance Reference Speech", 
                            value=False
                        )
                        temperature = gr.Slider(
                            label="Temperature", 
                            minimum=0.5, 
                            maximum=1.0, 
                            value=0.75, 
                            step=0.05
                        )
                        top_p = gr.Slider(
                            label="Top P", 
                            minimum=0.5, 
                            maximum=1.0, 
                            value=0.85, 
                            step=0.05
                        )
                        top_k = gr.Slider(
                            label="Top K", 
                            minimum=0, 
                            maximum=100, 
                            value=50, 
                            step=10
                        )
                        repetition_penalty = gr.Slider(
                            label="Repetition penalty", 
                            minimum=1.0, 
                            maximum=10.0, 
                            value=5.0, 
                            step=0.5
                        )
                        language = gr.Dropdown(
                            label="Target Language", 
                            choices=[
                                "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru",
                                "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi", "auto",
                            ], 
                            value="auto"
                        )
                    generate_button = gr.Button("Generate Speech")
                with gr.Column():
                    audio_output = gr.Audio(label="Generated Audio")
                    log_output = gr.Text(label="Log Output")

            def process_file_and_generate(
                file_input, ref_audio_files, speed, enhance_speech,
                temperature, top_p, top_k, repetition_penalty, language
            ):
                if not file_input:
                    return None, "Please provide an input file!"

                try:
                    # Convert input file to text
                    input_text = text_from_file(file_input.name)
                    
                    return process_text_and_generate(
                        input_text, ref_audio_files, speed, enhance_speech,
                        temperature, top_p, top_k, repetition_penalty, language
                    )
                except Exception as e:
                    logger.error(f"Error processing file: {e}")
                    return None, f"Error processing file: {str(e)}"

            generate_button.click(
                process_file_and_generate,
                inputs=[
                    file_input, ref_audio_files, speed, enhance_speech,
                    temperature, top_p, top_k, repetition_penalty, language
                ],
                outputs=[audio_output, log_output],
            )

        with gr.Tab("Clone With Microphone"):
            with gr.Row():
                with gr.Column():
                    file_input_mic = gr.File(
                        label="Upload Book/Text File",
                        file_types=[
                            ".txt", ".epub", ".mobi", ".azw3", ".fb2",
                            ".htmlz", ".lit", ".pdb", ".pdf", ".rtf"
                        ]
                    )
                    mic_ref_audio = gr.Audio(
                        label="Record Reference Audio",
                        sources=["microphone"]
                    )

                    with gr.Accordion("Advanced settings", open=False):
                        speed_mic = gr.Slider(
                            label="Playback speed",
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1
                        )
                        enhance_speech_mic = gr.Checkbox(
                            label="Enhance Reference Speech",
                            value=True
                        )
                        temperature_mic = gr.Slider(
                            label="Temperature",
                            minimum=0.5,
                            maximum=1.0,
                            value=0.75,
                            step=0.05
                        )
                        top_p_mic = gr.Slider(
                            label="Top P",
                            minimum=0.5,
                            maximum=1.0,
                            value=0.85,
                            step=0.05
                        )
                        top_k_mic = gr.Slider(
                            label="Top K",
                            minimum=0,
                            maximum=100,
                            value=50,
                            step=10
                        )
                        repetition_penalty_mic = gr.Slider(
                            label="Repetition penalty",
                            minimum=1.0,
                            maximum=10.0,
                            value=5.0,
                            step=0.5
                        )
                        language_mic = gr.Dropdown(
                            label="Target Language",
                            choices=[
                                "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru",
                                "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi", "auto",
                            ],
                            value="auto"
                        )
                    generate_button_mic = gr.Button("Generate Speech")
                with gr.Column():
                    audio_output_mic = gr.Audio(label="Generated Audio")
                    log_output_mic = gr.Text(label="Log Output")

            def process_mic_and_generate(
                file_input, mic_ref_audio, speed_mic, enhance_speech_mic,
                temperature_mic, top_p_mic, top_k_mic, repetition_penalty_mic, language_mic
            ):
                if not mic_ref_audio:
                    return None, "Please record an audio!"
                if not file_input:
                    return None, "Please provide an input file!"

                try:
                    # Convert input file to text
                    input_text = text_from_file(file_input.name)

                    # Save microphone audio
                    data = str(time.time()).encode("utf-8")
                    hash = hashlib.sha1(data).hexdigest()[:10]
                    output_path = temp_dir / (f"mic_{hash}.wav")

                    torch_audio = torch.from_numpy(mic_ref_audio[1].astype(float))
                    torchaudio.save(
                        str(output_path),
                        torch_audio.unsqueeze(0),
                        mic_ref_audio[0]
                    )

                    return process_text_and_generate(
                        input_text, [Path(output_path)], speed_mic,
                        enhance_speech_mic, temperature_mic, top_p_mic,
                        top_k_mic, repetition_penalty_mic, language_mic
                    )
                except Exception as e:
                    logger.error(f"Error processing input: {e}")
                    return None, f"Error processing input: {str(e)}"

            generate_button_mic.click(
                process_mic_and_generate,
                inputs=[
                    file_input_mic, mic_ref_audio, speed_mic,
                    enhance_speech_mic, temperature_mic, top_p_mic,
                    top_k_mic, repetition_penalty_mic, language_mic
                ],
                outputs=[audio_output_mic, log_output_mic],
            )

    return ui

if __name__ == "__main__":
    ui = build_gradio_ui()
    ui.launch(debug=True, share=True, server_name="0.0.0.0", server_port=7860)
