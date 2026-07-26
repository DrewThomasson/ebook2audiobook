# Universal TTS Finetune

Prepare speech datasets, fine-tune supported TTS models, and test the resulting voice from one web interface or CLI.

```text
Audio + optional transcript → training dataset → fine-tuned model → test audio
```

The workflow supports Coqui recipes, XTTS, Piper, and OmniVoice. It can use existing transcripts, slice audiobook audio from WebVTT timestamps, force-align audio with text, or transcribe unlabelled recordings with Whisper.

## Quick start

Docker is the simplest way to launch the web interface.

From `components/Universal_TTS_Finetune`:

```bash
mkdir -p audio_data models finetune_models
docker compose up --build
```

Open <http://localhost:7862>. Put source audio in `audio_data` so it is available inside the container at `/app/audio_data`.

To run locally in an existing ebook2audiobook environment:

```bash
conda activate ./python_env
cd components/Universal_TTS_Finetune
python -m pip install -r requirements.txt
python web_gui.py --port 7862 --out_path /absolute/path/to/output
```

## Choose a workflow

| Starting material | Recommended path |
|---|---|
| Short audio clips plus matching transcript rows | Import the transcript map directly |
| Audiobook audio plus `.vtt` timestamps | VTT slicing; no transcription needed |
| Audio plus the corresponding plain text | Forced alignment |
| Audio without text | Whisper transcription |
| Recording containing multiple voices | Enable speaker diarization |

The prepared dataset is written to:

```text
<output_root>/dataset/LJSpeech-1.1/
```

Training runs are written to:

```text
<output_root>/training_runs/<model>/<timestamp>/
```

Successful runs contain `ready/artifacts.json`, which the web interface and CLI can load for synthesis.

## Choose a model

- **XTTS v2** is the best starting point for multilingual or speaker-conditioned fine-tuning.
- **Piper** is useful when lightweight ONNX inference is the priority.
- **OmniVoice** uses its official pretrained fine-tuning workflow and requires Python 3.12 or newer.
- **Single-speaker Coqui recipes** are useful for experimentation and recipe-specific training.

Available model families:

| Family | Models |
|---|---|
| Speaker-conditioned | XTTS v1, XTTS v2 |
| Lightweight | Piper TTS |
| OmniVoice | OmniVoice |
| Acoustic/recipe models | Align TTS, DelightfulTTS, FastPitch, FastSpeech, FastSpeech 2, Glow-TTS, NeuralHMM-TTS, Overflow, SpeedySpeech, VITS |
| Tacotron2 | Capacitron, DCA, DDC |

When a compatible Coqui pretrained checkpoint exists, the trainer can download and fine-tune it. Otherwise it prepares a recipe workspace that can use recipe defaults or a supplied checkpoint.

## Installation

### Local

First install ebook2audiobook, then activate its environment.

macOS or Linux:

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
./ebook2audiobook.command
conda activate ./python_env
cd components/Universal_TTS_Finetune
python -m pip install -r requirements.txt
```

Windows:

```bat
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
ebook2audiobook.cmd
conda activate .\python_env
cd components\Universal_TTS_Finetune
python -m pip install -r requirements.txt
```

Launch the interface:

```bash
python web_gui.py --port 7862 --out_path /absolute/path/to/output
```

The workflow uses CUDA when available and falls back to CPU. Training large models on CPU can be very slow.

### Docker

The included Compose file mounts:

- `audio_data` at `/app/audio_data`
- E2A `models` at `/ebook2audiobook/models`
- E2A `voices` at `/ebook2audiobook/voices`
- E2A `finetune_models` at `/ebook2audiobook/finetune_models`
- E2A `run` at `/ebook2audiobook/run`

It also requests an NVIDIA GPU. GPU use requires the NVIDIA Container Toolkit; adjust the Compose device reservation if you intend to run Docker without one.

```bash
docker compose up --build
```

## CLI: complete workflow

Run these examples from `components/Universal_TTS_Finetune`.

Prepare a dataset, fine-tune XTTS v2, and generate a test sample:

```bash
python headless_cli.py workflow \
  --model xtts_v2 \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --test-text "This is a quick validation sample."
```

List every supported model key:

```bash
python headless_cli.py list-models
```

For complete, current options:

```bash
python headless_cli.py --help
python headless_cli.py prepare-dataset --help
python headless_cli.py train --help
```

## CLI: prepare a dataset

### Transcribe audio with Whisper

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --whisper-model small
```

### Use an existing transcript map

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --transcript-file /absolute/path/to/metadata.csv
```

Accepted transcript maps include JSON, CSV, TSV, and pipe-delimited text. An audio key may be an absolute path, filename, or stem; a text field may be named `text`, `transcript`, `sentence`, or `utterance`.

### Slice an audiobook with WebVTT

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-file /absolute/path/to/audiobook.mp3 \
  --transcript-file /absolute/path/to/alignment.vtt
```

The VTT timestamps determine the clips, avoiding a new transcription pass.

### Force-align audio and text

Convert EPUB content to plain text first, then provide one audio file and its text:

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-file /absolute/path/to/chapter.mp3 \
  --transcript-file /absolute/path/to/chapter.txt \
  --language en
```

Text is split into sentence-sized units automatically. If the file already contains exactly one sentence per line:

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-file /absolute/path/to/chapter.mp3 \
  --transcript-file /absolute/path/to/chapter.txt \
  --language en \
  --no-auto-split-sentences
```

When `--audio-dir` is used without a global transcript, matching local files are detected automatically:

- `chapter1.mp3` + `chapter1.vtt`: slice from VTT timestamps
- `chapter2.mp3` + `chapter2.txt`: force-align the text
- `chapter3.mp3` without a match: fall back to Whisper

All resulting clips are merged into the final dataset.

### Separate multiple speakers

Add diarization to a preparation command:

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --diarize-speakers
```

The PyAnnote ResNet-34 VoxCeleb model embeds and clusters the clips by speaker. Use `--expected-speakers 3` when the speaker count is known, or tune `--diarize-threshold` for automatic detection. The web interface can re-diarize preserved source clips without repeating Whisper transcription.

## CLI: train and test

Check the workspace without starting training:

```bash
python headless_cli.py train \
  --model xtts_v2 \
  --output-root /absolute/path/to/output \
  --dry-run
```

Train a model:

```bash
python headless_cli.py train \
  --model glow_tts \
  --output-root /absolute/path/to/output \
  --epochs 50 \
  --batch-size 16
```

Training logs stream by default. Add `--no-stream-logs` for background jobs.

Synthesize with the newest matching trained model:

```bash
python headless_cli.py synthesize \
  --artifacts /absolute/path/to/output \
  --model xtts_v2 \
  --text "Testing the fine-tuned voice." \
  --language en
```

XTTS synthesis may also need `--speaker-wav /path/to/reference.wav`. Single-speaker recipe models synthesize directly.

### OmniVoice

OmniVoice fine-tuning starts from `k2-fsa/OmniVoice`; training from scratch is not exposed. The prepared LJSpeech dataset is converted to JSONL, tokenized into WebDataset shards, trained through Accelerate, and packaged as a Hugging Face-style checkpoint.

```bash
python headless_cli.py train \
  --model omnivoice \
  --output-root /absolute/path/to/output \
  --dataset-dir /absolute/path/to/output/dataset/LJSpeech-1.1 \
  --language en \
  --epochs 100
```

The epoch count is converted to steps from the dataset size. Advanced settings can be supplied as JSON:

```bash
python headless_cli.py train \
  --model omnivoice \
  --output-root /absolute/path/to/output \
  --language en \
  --extra-overrides-json '{"steps": 5000, "learning_rate": 0.00001}'
```

OmniVoice defaults to SDPA attention for compatibility. The special `audio_tokenizer` override selects another tokenizer.

### Batch testing

Test all supported models sequentially:

```bash
python headless_cli.py batch-test \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --discard-models \
  --auto-calculate-epochs
```

`--auto-calculate-epochs` estimates epochs from the dataset size and family-specific target steps. `--discard-models` retains samples while removing checkpoints to save disk space.

## Stop early and export a checkpoint

Ask training to generate periodic samples:

```bash
python headless_cli.py train \
  --model xtts_v2 \
  --output-root /absolute/path/to/output \
  --sample-epoch-interval 1 \
  --sample-text "Listen to this training sample."
```

Samples are written to the run’s `epoch_samples` directory. Press `Ctrl+C` after a satisfactory sample; supported PyTorch Lightning trainers save intermediate `.ckpt` files at epoch boundaries.

Package the latest checkpoint:

```bash
python export_checkpoint.py /path/to/training_runs/model/timestamp
```

This creates the run’s `ready` directory and `artifacts.json`. Piper exports ONNX; Coqui and XTTS package their applicable model artifacts.

## Dataset layout

A standard prepared dataset contains:

```text
LJSpeech-1.1/
├── wavs/
├── metadata.csv
├── metadata_shuf.csv
├── metadata_train.csv
├── metadata_val.csv
└── dataset_info.json
```

Speaker diarization may create suffixed datasets such as `LJSpeech-1.1_Speaker_1`.

## Advanced tuning

Some upstream recipes retain model-specific assumptions. Use `--restore-path` to supply a checkpoint or `--extra-overrides-json` to change recipe values. Inspect the selected command’s `--help` output before launching a long run.

## E2A integration API

`component_api.py` is the stable entry point for a future ebook2audiobook launcher. Its `create_app()` function returns an unlaunched Gradio app, so E2A can render it in a tab or manage its launch without starting a server during import.

Configuration can be injected with `e2a_root`, `output_dir`, `theme`, `css`, and UI defaults such as `num_epochs`. Standalone and embedded launches share:

| Data | Default location |
|---|---|
| Model downloads and caches | `models/` |
| Existing E2A voices | `voices/` |
| Datasets and fine-tuned runs | `finetune_models/` |
| Temporary working data | `run/components/tts-finetune/` |

The corresponding environment overrides are `E2A_ROOT`, `E2A_MODELS_DIR`, `E2A_VOICES_DIR`, `E2A_FINETUNE_OUTPUT_DIR`, and `E2A_RUN_DIR`. Cache-related environment variables are pointed into `models/`, preventing implicit downloads into a user home directory.
