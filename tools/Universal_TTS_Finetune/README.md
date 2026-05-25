# Universal_TTS_Finetune

Universal Coqui & Rhasspy Piper TTS fine-tuning workflow with:
- a Gradio web GUI
- a headless CLI
- LJSpeech-style dataset generation from your own audio
- optional automatic transcription with Whisper when transcripts are not provided
- quick post-training inference for the model you just trained

## Supported models

The current workflow targets the bundled `recipes/ljspeech` training recipes for these Coqui models:

- Align TTS
- DelightfulTTS
- FastPitch
- FastSpeech
- FastSpeech 2
- Glow-TTS
- NeuralHMM-TTS
- Overflow
- SpeedySpeech
- Tacotron2 Capacitron
- Tacotron2 DCA
- Tacotron2 DDC
- VITS
- XTTS v1
- XTTS v2
- Piper TTS (Rhasspy)

When Coqui publishes a matching pretrained checkpoint, the trainer can auto-download it and continue from it. Otherwise the workflow still prepares the recipe workspace and can train from a user-supplied checkpoint or recipe defaults.

## What it does

### 1. Prepare a dataset

Point the app at audio files or a folder of audio.

- If you provide a transcript map (`csv`, `tsv`, `txt`, or `json`), it uses that text.
- If you do not provide text, it transcribes with Whisper and chunks longer recordings into sentence-sized clips.
- **Speaker Diarization**: Optionally enable speaker diarization to separate multiple speakers into distinct datasets. This uses a high-performance **PyAnnote ResNet-34 VoxCeleb** speaker model (`pyannote/wespeaker-voxceleb-resnet34-LM`) to extract embeddings and group clips by voice. You can configure:
  - **Expected Speakers**: Force the clustering into exactly N speaker folders.
  - **Distance Threshold**: Fine-tune the sensitivity of auto-detecting speakers when expected speakers is set to 0.
- **Re-diarization**: Once a dataset has been prepared, the original mixed audio clips are preserved. You can re-diarize the dataset with new speaker counts or thresholds via the web GUI without re-running the slow Whisper transcription step.
- It writes an LJSpeech-style dataset under:

```text
<output_root>/dataset/LJSpeech-1.1/
```

including:
- `wavs/`
- `metadata.csv`
- `metadata_shuf.csv`
- `metadata_train.csv`
- `metadata_val.csv`
- `dataset_info.json`

### 2. Train or fine-tune a model

Pick one of the supported Coqui recipes, then train from the GUI or CLI.

Training artifacts are written under:

```text
<output_root>/training_runs/<model>/<timestamp>/ready/
```

with an `artifacts.json` file that the GUI and CLI can load later.

### 3. Test the trained model

After training, load the generated `artifacts.json` (or the training folder) and synthesize test audio.

- XTTS models use a speaker reference WAV.
- Single-speaker recipe models synthesize directly.

## Install

Install the required dependencies using pip:

```bash
git clone https://github.com/DrewThomasson/ebook2audiobook.git
cd ebook2audiobook
./ebook2audiobook.command #Mac/Linux or ebook2audiobook.cmd #Window | locally install ebook2audiobook first
conda activate ./python_env  # Activate the created python env for E2A
cd ebook2audiobook/tools/Universal_TTS_Finetune # Go into Universal_TTS_Finetune dir
pip install -r requirements.txt # Install additional requirments for E2A SML
```

## Run the web GUI

Run the application directly with Python:

```bash
python web_gui.py --port 5003 --out_path /absolute/path/to/output
```

## Run with Docker

To run the application using Docker, simply use `docker-compose`. This handles installing all system dependencies and setting up GPU support automatically:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:5003`.

## Headless CLI

*Note: By default, the training commands (`train` and `workflow`) will stream live training logs to your console so you can see progress in real time. If you prefer to suppress this output (e.g., when running in a background job), you can pass the `--no-stream-logs` flag.*

List models:

```bash
python headless_cli.py list-models
```

Prepare a dataset from a folder of audio and auto-transcribe with Whisper:

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --whisper-model small \
  --diarize-speakers
```

*Note: The `--diarize-speakers` flag is optional. If provided, the pipeline will extract speaker embeddings using a pre-trained **PyAnnote ResNet-34** speaker model and cluster them by distinct speakers. You can optionally specify `--expected-speakers <count>` to cluster into exactly that many speakers, or adjust `--diarize-threshold <float>` to control auto-detection sensitivity. It will output separate datasets (e.g., `dataset/LJSpeech-1.1_Speaker_1/`) and default to returning the speaker with the most training data.*

Prepare a dataset using an existing transcript file:

```bash
python headless_cli.py prepare-dataset \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --transcript-file /absolute/path/to/metadata.csv
```

Dry-run a training workspace:

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

Run the whole workflow in one command:

```bash
python headless_cli.py workflow \
  --model xtts_v2 \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --test-text "This is a quick validation sample."
```

Test all supported models sequentially on a dataset, saving sample audio and discarding the checkpoints to save space:

```bash
python headless_cli.py batch-test \
  --output-root /absolute/path/to/output \
  --audio-dir /absolute/path/to/audio \
  --language en \
  --discard-models \
  --auto-calculate-epochs \
  --diarize-speakers
```

*Note: The `--auto-calculate-epochs` flag ignores the `--epochs` argument and dynamically computes the optimal number of epochs for each model family (e.g., targeting 1,500 steps for XTTS and 15,000 steps for Tacotron2) based on the exact size of your provided dataset.*

Generate speech from the newest trained model:

```bash
python headless_cli.py synthesize \
  --artifacts /absolute/path/to/output \
  --model xtts_v2 \
  --text "Testing the fine-tuned voice." \
  --language en
```

## Transcript file formats

Accepted transcript formats:
- `json` dictionary or list of objects
- `csv`
- `tsv`
- pipe-delimited text

The audio key can be an absolute path, file name, or stem. The text field can be named `text`, `transcript`, `sentence`, or `utterance`.

## Notes

- The workflow automatically uses CUDA when available and falls back to CPU otherwise.
- XTTS models are the best option when you need multilingual fine-tuning or speaker-conditioned inference.
- Some upstream Coqui recipes still depend on recipe-specific assumptions. If you need deeper tuning, use the `extra_overrides_json` field/flag to override recipe values before launch.
