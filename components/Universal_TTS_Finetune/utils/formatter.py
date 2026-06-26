import os
import gc
import torchaudio
import pandas
from faster_whisper import WhisperModel
from glob import glob

from tqdm import tqdm

from TTS.tts.layers.xtts.tokenizer import multilingual_cleaners
# Add support for JA train
# from utils.tokenizer import multilingual_cleaners

import torch
import torchaudio
# torch.set_num_threads(1)


torch.set_num_threads(16)
import os

audio_types = (".wav", ".mp3", ".flac")

def find_latest_best_model(folder_path):
        search_path = os.path.join(folder_path, '**', 'best_model.pth')
        files = glob(search_path, recursive=True)
        latest_file = max(files, key=os.path.getctime, default=None)
        return latest_file


def list_audios(basePath, contains=None):
    # return the set of files that are valid
    return list_files(basePath, validExts=audio_types, contains=contains)

def list_files(basePath, validExts=None, contains=None):
    # loop over the directory structure
    for (rootDir, dirNames, filenames) in os.walk(basePath):
        # loop over the filenames in the current directory
        for filename in filenames:
            # if the contains string is not none and the filename does not contain
            # the supplied string, then ignore the file
            if contains is not None and filename.find(contains) == -1:
                continue

            # determine the file extension of the current file
            ext = filename[filename.rfind("."):].lower()

            # check to see if the file is an audio and should be processed
            if validExts is None or ext.endswith(validExts):
                # construct the path to the audio and yield it
                audioPath = os.path.join(rootDir, filename)
                yield audioPath

def format_audio_list(audio_files, asr_model, target_language="en", out_path=None, buffer=0.2, eval_percentage=0.15, speaker_name="coqui", gradio_progress=None):
    audio_total_size = 0
    os.makedirs(out_path, exist_ok=True)

    lang_file_path = os.path.join(out_path, "lang.txt")
    current_language = None

    # Check and update language file
    if os.path.exists(lang_file_path):
        with open(lang_file_path, 'r', encoding='utf-8') as existing_lang_file:
            current_language = existing_lang_file.read().strip()
    if current_language != target_language:
        with open(lang_file_path, 'w', encoding='utf-8') as lang_file:
            lang_file.write(target_language + '\n')
        print("Warning: Language mismatch, updated to target language.")
    else:
        print("Language matches target.")

    # Initialize metadata
    metadata = {"audio_file": [], "text": [], "original_text": []}
    metadata_path = os.path.join(out_path, "metadata.csv")

    tqdm_object = gradio_progress.tqdm(audio_files, desc="Formatting...") if gradio_progress else tqdm(audio_files)

    # Process audio files
    for audio_path in tqdm_object:
        wav, sr = torchaudio.load(audio_path)
        if wav.size(0) != 1:
            wav = torch.mean(wav, dim=0, keepdim=True)
        wav = wav.squeeze()
        audio_total_size += (wav.size(-1) / sr)

        segments, _ = asr_model.transcribe(audio_path, vad_filter=True, word_timestamps=True, language=target_language)

        # Prepare sentences
        sentence = ""
        sentence_start = None
        first_word = True
        words_list = [word for segment in segments for word in segment.words]

        i = 0  # Index for audio segments
        for word_idx, word in enumerate(words_list):
            if first_word:
                sentence_start = max(word.start - buffer, 0)
                sentence = word.word
                first_word = False
            else:
                sentence += word.word

            # Check for sentence-ending punctuation
            if word.word[-1] in ["!", "。", ".", "?"]:
                # Clean up the sentence
                sentence = sentence.strip()
                sentence_cleaned = multilingual_cleaners(sentence, target_language)

                # Generate audio file name
                audio_file_name = os.path.splitext(os.path.basename(audio_path))[0]
                audio_file = f"{audio_file_name}_{str(i).zfill(8)}.wav"

                # Calculate word end
                if word_idx + 1 < len(words_list):
                    next_word_start = words_list[word_idx + 1].start
                else:
                    next_word_start = (wav.shape[0] - 1) / sr

                word_end = min((word.end + next_word_start) / 2, word.end + buffer)

                # Save the audio segment
                absolute_path = os.path.join(out_path, audio_file)
                os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
                audio_segment = wav[int(sr * sentence_start):int(sr * word_end)].unsqueeze(0)
                if audio_segment.size(-1) >= sr / 3:
                    torchaudio.save(absolute_path, audio_segment, sr)
                else:
                    continue  # Skip segments that are too short

                # Update metadata
                metadata["audio_file"].append(audio_file)
                metadata["text"].append(sentence_cleaned)
                metadata["original_text"].append(sentence)

                # Reset for next sentence
                sentence = ""
                first_word = True
                i += 1

    # Save the raw metadata
    df = pandas.DataFrame(metadata)
    df.to_csv(metadata_path, sep="|", index=False, header=False)

    # Paths for shuffled and split metadata
    shuffled_metadata_path = os.path.join(out_path, "metadata_shuf.csv")
    train_metadata_path = os.path.join(out_path, "metadata_train.csv")
    val_metadata_path = os.path.join(out_path, "metadata_val.csv")

    # Shuffle and split metadata using pandas instead of shell commands
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    df_shuffled.to_csv(shuffled_metadata_path, sep="|", index=False, header=False)

    # Split into training and validation sets based on eval_percentage
    num_total_samples = len(df_shuffled)
    num_val_samples = int(num_total_samples * eval_percentage)
    num_train_samples = num_total_samples - num_val_samples

    df_train = df_shuffled.iloc[:num_train_samples]
    df_val = df_shuffled.iloc[num_train_samples:]

    df_train.to_csv(train_metadata_path, sep="|", index=False, header=False)
    df_val.to_csv(val_metadata_path, sep="|", index=False, header=False)

    return metadata_path, shuffled_metadata_path, train_metadata_path, val_metadata_path, audio_total_size
