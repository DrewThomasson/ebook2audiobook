#!/usr/bin/env bash

# Exit on error, undefined variables, or pipe failures
set -euo pipefail

# Define script path variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
INPUT_TXT="/home/drew/Downloads/ljspeech_prompts.txt"
OUTPUT_DIR="$SCRIPT_DIR/audiobooks/synthetic_deathpuss"
FINETUNE_DIR="$SCRIPT_DIR/tools/Universal_TTS_Finetune"
TRAINING_OUT="$SCRIPT_DIR/training_out_piper"

echo "====================================================================="
echo "   Piper TTS English Model Fine-Tuning Workflow (DeathPussInBoots)"
echo "====================================================================="
echo ""

# 1. Validate prompt file exists
if [ ! -f "$INPUT_TXT" ]; then
    echo "Error: Prompts file not found at $INPUT_TXT"
    exit 1
fi

# 2. Generate synthetic audio with ebook2audiobook
echo "[STEP 1/4] Generating synthetic audio with ebook2audiobook..."
echo "---------------------------------------------------------------------"
echo "Input text prompts: $INPUT_TXT"
echo "TTS engine: XTTS"
echo "Fine-tuned voice: DeathPussInBoots"
echo "Output format: MP3"
echo "Device: CUDA"
echo "---------------------------------------------------------------------"

MP3_FILE="$OUTPUT_DIR/ljspeech_prompts.mp3"
VTT_FILE="$OUTPUT_DIR/ljspeech_prompts.vtt"

if [ -f "$MP3_FILE" ] && [ -f "$VTT_FILE" ]; then
    echo "Found existing synthetic audio and alignment files at $OUTPUT_DIR. Skipping generation step."
else
    # Run ebook2audiobook in headless mode
    # This outputs ljspeech_prompts.mp3 and ljspeech_prompts.vtt to $OUTPUT_DIR
    "$SCRIPT_DIR/ebook2audiobook.sh" \
        --headless \
        --ebook "$INPUT_TXT" \
        --tts_engine xtts \
        --fine_tuned DeathPussInBoots \
        --language eng \
        --device CUDA \
        --output_format mp3 \
        --output_dir "$OUTPUT_DIR"
fi

if [ ! -f "$MP3_FILE" ] || [ ! -f "$VTT_FILE" ]; then
    echo "Error: ebook2audiobook generation failed. Files not found:"
    echo "  Expected MP3: $MP3_FILE"
    echo "  Expected VTT: $VTT_FILE"
    exit 1
fi

echo ""
echo "Synthetic audio generated successfully!"
echo "  Audio: $MP3_FILE"
echo "  Alignment: $VTT_FILE"
echo ""

# 3. Slice audio and prepare training dataset
echo "[STEP 2/4] Preparing dataset using alignment timestamps..."
echo "---------------------------------------------------------------------"
echo "This step parses the VTT timestamps and slices the audiobook into"
echo "individual training clips automatically with 0% transcription errors."
echo "---------------------------------------------------------------------"

mkdir -p "$TRAINING_OUT"

"$FINETUNE_DIR/finetune.sh" prepare-dataset \
    --output-root "$TRAINING_OUT" \
    --audio-file "$MP3_FILE" \
    --transcript-file "$VTT_FILE" \
    --language en

DATASET_CSV="$TRAINING_OUT/dataset/LJSpeech-1.1/metadata.csv"
if [ ! -f "$DATASET_CSV" ]; then
    echo "Error: Dataset preparation failed. $DATASET_CSV not found."
    exit 1
fi

# 4. Calculate optimal training epochs
echo ""
echo "[STEP 3/4] Calculating optimal epochs for training..."
echo "---------------------------------------------------------------------"

SAMPLE_COUNT=$(wc -l < "$DATASET_CSV")
BATCH_SIZE=8
STEPS_PER_EPOCH=$(( SAMPLE_COUNT / BATCH_SIZE ))

if [ "$STEPS_PER_EPOCH" -lt 1 ]; then
    STEPS_PER_EPOCH=1
fi

# Target 100,000 steps for highest-quality audiobook-tuned models
TARGET_STEPS=100000
CALCULATED_EPOCHS=$(( TARGET_STEPS / STEPS_PER_EPOCH ))

# Ensure a minimum number of epochs to allow periodic samples
if [ "$CALCULATED_EPOCHS" -lt 20 ]; then
    CALCULATED_EPOCHS=20
fi

echo "Dataset analysis:"
echo "  Total clips: $SAMPLE_COUNT"
echo "  Batch size: $BATCH_SIZE"
echo "  Steps per epoch: $STEPS_PER_EPOCH"
echo "  Target training steps: $TARGET_STEPS"
echo "  Optimal calculated epochs: $CALCULATED_EPOCHS"
echo "---------------------------------------------------------------------"
echo ""

# 5. Start Piper fine-tuning
echo "[STEP 4/4] Launching Piper TTS fine-tuning..."
echo "---------------------------------------------------------------------"
echo "Training logs will stream below."
echo "Every 10 epochs, a voice sample will be generated and saved under:"
echo "  $TRAINING_OUT/training_runs/piper/<timestamp>/epoch_samples/"
echo ""
echo "Press Ctrl+C to stop training early if you are satisfied with the sample quality."
echo "If training is stopped early, package it manually by running:"
echo "  python $FINETUNE_DIR/export_checkpoint.py $TRAINING_OUT/training_runs/piper/<timestamp>"
echo "---------------------------------------------------------------------"

"$FINETUNE_DIR/finetune.sh" train \
    --model piper \
    --output-root "$TRAINING_OUT" \
    --dataset-dir "$TRAINING_OUT/dataset/LJSpeech-1.1" \
    --language en \
    --epochs "$CALCULATED_EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --sample-epoch-interval 10 \
    --sample-text "This is a periodic audio validation sample of the Piper Text to Speech model trained on the Death Puss in Boots voice."

echo ""
echo "====================================================================="
echo "Workflow completed successfully!"
echo "====================================================================="
