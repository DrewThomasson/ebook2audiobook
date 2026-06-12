import os

from trainer import Trainer, TrainerArgs

from TTS.config import BaseAudioConfig, BaseDatasetConfig
from TTS.tts.configs.speedy_speech_config import SpeedySpeechConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models.forward_tts import ForwardTTS
from TTS.tts.utils.text.tokenizer import TTSTokenizer
from TTS.utils.audio import AudioProcessor

output_path = os.path.dirname(os.path.abspath(__file__))
dataset_config = BaseDatasetConfig(
    formatter="ljspeech", meta_file_train="metadata.csv", path=os.path.join(output_path, "../LJSpeech-1.1/")
)

audio_config = BaseAudioConfig(
    sample_rate=22050,
    do_trim_silence=True,
    trim_db=60.0,
    signal_norm=False,
    mel_fmin=0.0,
    mel_fmax=8000,
    spec_gain=1.0,
    log_func="np.log",
    ref_level_db=20,
    preemphasis=0.0,
)

config = SpeedySpeechConfig(
    run_name="speedy_speech_ljspeech",
    audio=audio_config,
    batch_size=32,
    eval_batch_size=16,
    num_loader_workers=4,
    num_eval_loader_workers=4,
    compute_input_seq_cache=True,
    run_eval=True,
    test_delay_epochs=-1,
    epochs=1000,
    text_cleaner="english_cleaners",
    use_phonemes=True,
    phoneme_language="en-us",
    phoneme_cache_path=os.path.join(output_path, "phoneme_cache"),
    precompute_num_workers=4,
    print_step=50,
    print_eval=False,
    mixed_precision=False,
    min_seq_len=13,
    max_seq_len=500000,
    output_path=output_path,
    datasets=[dataset_config],
)

# INITIALIZE THE AUDIO PROCESSOR
# Audio processor is used for feature extraction and audio I/O.
# It mainly serves to the dataloader and the training loggers.
ap = AudioProcessor.init_from_config(config)

# INITIALIZE THE TOKENIZER
# Tokenizer is used to convert text to sequences of token IDs.
# If characters are not defined in the config, default characters are passed to the config
tokenizer, config = TTSTokenizer.init_from_config(config)

# LOAD DATA SAMPLES
# Each sample is a list of ```[text, audio_file_path, speaker_name]```
# You can define your custom sample loader returning the list of samples.
# Or define your custom formatter and pass it to the `load_tts_samples`.
# Check `TTS.tts.datasets.load_tts_samples` for more details.
try:
    train_samples, eval_samples = load_tts_samples(
        dataset_config,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )
except AssertionError as e:
    if "You do not have enough samples for the evaluation set" in str(e):
        total_samples = load_tts_samples(dataset_config, eval_split=False)
        num_samples = len(total_samples)
        if num_samples > 0:
            new_eval_split_size = 1.0 / num_samples
            print(f" > Recalculating eval_split_size to {new_eval_split_size} (at least 1 evaluation sample)")
            config.eval_split_size = new_eval_split_size
            train_samples, eval_samples = load_tts_samples(
                dataset_config,
                eval_split=True,
                eval_split_max_size=config.eval_split_max_size,
                eval_split_size=config.eval_split_size,
            )
        else:
            raise e
    else:
        raise e

# Filter by actual phoneme token length (min_seq_len in config only checks character count,
# but the encoder kernel_size=13 requires ≥13 PHONEME tokens or it crashes at runtime).
_ENCODER_KERNEL_SIZE = 13

def _phoneme_len_ok(sample):
    try:
        ids = tokenizer.text_to_ids(sample["text"], sample.get("language", None))
        return len(ids) >= _ENCODER_KERNEL_SIZE
    except Exception:
        return True  # keep sample if we can't check

_before = len(train_samples) + len(eval_samples)
train_samples = [s for s in train_samples if _phoneme_len_ok(s)]
eval_samples  = [s for s in eval_samples  if _phoneme_len_ok(s)]
_after = len(train_samples) + len(eval_samples)
if _before != _after:
    print(f" > Dropped {_before - _after} sample(s) whose phoneme sequence was shorter than encoder kernel_size={_ENCODER_KERNEL_SIZE}")

# init model
model = ForwardTTS(config, ap, tokenizer)

# INITIALIZE THE TRAINER
# Trainer provides a generic API to train all the 🐸TTS models with all its perks like mixed-precision training,
# distributed training, etc.
trainer = Trainer(
    TrainerArgs(), config, output_path, model=model, train_samples=train_samples, eval_samples=eval_samples
)

# AND... 3,2,1... 🚀
trainer.fit()
