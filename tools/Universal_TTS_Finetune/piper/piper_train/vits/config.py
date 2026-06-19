"""Configuration classes"""
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class MelAudioConfig:
    filter_length: int = 1024
    hop_length: int = 256
    win_length: int = 1024
    mel_channels: int = 80
    sample_rate: int = 22050
    sample_bytes: int = 2
    channels: int = 1
    mel_fmin: float = 0.0
    mel_fmax: Optional[float] = None


@dataclass
class ModelAudioConfig:
    resblock: str
    resblock_kernel_sizes: Tuple[int, ...]
    resblock_dilation_sizes: Tuple[Tuple[int, ...], ...]
    upsample_rates: Tuple[int, ...]
    upsample_initial_channel: int
    upsample_kernel_sizes: Tuple[int, ...]

    @staticmethod
    def low_quality() -> "ModelAudioConfig":
        return ModelAudioConfig(
            resblock="2",
            resblock_kernel_sizes=(3, 5, 7),
            resblock_dilation_sizes=(
                (1, 2),
                (2, 6),
                (3, 12),
            ),
            upsample_rates=(8, 8, 4),
            upsample_initial_channel=256,
            upsample_kernel_sizes=(16, 16, 8),
        )

    @staticmethod
    def high_quality() -> "ModelAudioConfig":
        return ModelAudioConfig(
            resblock="1",
            resblock_kernel_sizes=(3, 7, 11),
            resblock_dilation_sizes=(
                (1, 3, 5),
                (1, 3, 5),
                (1, 3, 5),
            ),
            upsample_rates=(8, 8, 2, 2),
            upsample_initial_channel=512,
            upsample_kernel_sizes=(16, 16, 4, 4),
        )


@dataclass
class ModelConfig:
    num_symbols: int
    n_speakers: int
    audio: ModelAudioConfig
    mel: MelAudioConfig = field(default_factory=MelAudioConfig)

    inter_channels: int = 192
    hidden_channels: int = 192
    filter_channels: int = 768
    n_heads: int = 2
    n_layers: int = 6
    kernel_size: int = 3
    p_dropout: float = 0.1
    n_layers_q: int = 3
    use_spectral_norm: bool = False
    gin_channels: int = 0  # single speaker
    use_sdp: bool = True  # StochasticDurationPredictor
    segment_size: int = 8192

    @property
    def is_multispeaker(self) -> bool:
        return self.n_speakers > 1

    @property
    def resblock(self) -> str:
        return self.audio.resblock

    @property
    def resblock_kernel_sizes(self) -> Tuple[int, ...]:
        return self.audio.resblock_kernel_sizes

    @property
    def resblock_dilation_sizes(self) -> Tuple[Tuple[int, ...], ...]:
        return self.audio.resblock_dilation_sizes

    @property
    def upsample_rates(self) -> Tuple[int, ...]:
        return self.audio.upsample_rates

    @property
    def upsample_initial_channel(self) -> int:
        return self.audio.upsample_initial_channel

    @property
    def upsample_kernel_sizes(self) -> Tuple[int, ...]:
        return self.audio.upsample_kernel_sizes

    def __post_init__(self):
        if self.is_multispeaker and (self.gin_channels == 0):
            self.gin_channels = 512


@dataclass
class TrainingConfig:
    learning_rate: float = 2e-4
    betas: Tuple[float, float] = field(default=(0.8, 0.99))
    eps: float = 1e-9
    # batch_size: int = 32
    fp16_run: bool = False
    lr_decay: float = 0.999875
    init_lr_ratio: float = 1.0
    warmup_epochs: int = 0
    c_mel: int = 45
    c_kl: float = 1.0
    grad_clip: Optional[float] = None


# @dataclass
# class PhonemesConfig(DataClassJsonMixin):
#     phoneme_separator: str = " "
#     """Separator between individual phonemes in CSV input"""

#     word_separator: str = "#"
#     """Separator between word phonemes in CSV input (must not match phoneme_separator)"""

#     phoneme_to_id: typing.Optional[typing.Dict[str, int]] = None
#     pad: typing.Optional[str] = "_"
#     bos: typing.Optional[str] = None
#     eos: typing.Optional[str] = None
#     blank: typing.Optional[str] = "#"
#     blank_word: typing.Optional[str] = None
#     blank_between: typing.Union[str, BlankBetween] = BlankBetween.WORDS
#     blank_at_start: bool = True
#     blank_at_end: bool = True
#     simple_punctuation: bool = True
#     punctuation_map: typing.Optional[typing.Dict[str, str]] = None
#     separate: typing.Optional[typing.List[str]] = None
#     separate_graphemes: bool = False
#     separate_tones: bool = False
#     tone_before: bool = False
#     phoneme_map: typing.Optional[typing.Dict[str, typing.List[str]]] = None
#     auto_bos_eos: bool = False
#     minor_break: typing.Optional[str] = IPA.BREAK_MINOR.value
#     major_break: typing.Optional[str] = IPA.BREAK_MAJOR.value
#     break_phonemes_into_graphemes: bool = False
#     break_phonemes_into_codepoints: bool = False
#     drop_stress: bool = False
#     symbols: typing.Optional[typing.List[str]] = None

#     def split_word_phonemes(self, phonemes_str: str) -> typing.List[typing.List[str]]:
#         """Split phonemes string into a list of lists (outer is words, inner is individual phonemes in each word)"""
#         return [
#             word_phonemes_str.split(self.phoneme_separator)
#             if self.phoneme_separator
#             else list(word_phonemes_str)
#             for word_phonemes_str in phonemes_str.split(self.word_separator)
#         ]

#     def join_word_phonemes(self, word_phonemes: typing.List[typing.List[str]]) -> str:
#         """Split phonemes string into a list of lists (outer is words, inner is individual phonemes in each word)"""
#         return self.word_separator.join(
#             self.phoneme_separator.join(wp) for wp in word_phonemes
#         )


# class Phonemizer(str, Enum):
#     SYMBOLS = "symbols"
#     GRUUT = "gruut"
#     ESPEAK = "espeak"
#     EPITRAN = "epitran"


# class Aligner(str, Enum):
#     KALDI_ALIGN = "kaldi_align"


# class TextCasing(str, Enum):
#     LOWER = "lower"
#     UPPER = "upper"


# class MetadataFormat(str, Enum):
#     TEXT = "text"
#     PHONEMES = "phonemes"
#     PHONEME_IDS = "ids"


# @dataclass
# class DatasetConfig:
#     name: str
#     metadata_format: MetadataFormat = MetadataFormat.TEXT
#     multispeaker: bool = False
#     text_language: typing.Optional[str] = None
#     audio_dir: typing.Optional[typing.Union[str, Path]] = None
#     cache_dir: typing.Optional[typing.Union[str, Path]] = None

#     def get_cache_dir(self, output_dir: typing.Union[str, Path]) -> Path:
#         if self.cache_dir is not None:
#             cache_dir = Path(self.cache_dir)
#         else:
#             cache_dir = Path("cache") / self.name

#         if not cache_dir.is_absolute():
#             cache_dir = Path(output_dir) / str(cache_dir)

#         return cache_dir


# @dataclass
# class AlignerConfig:
#     aligner: typing.Optional[Aligner] = None
#     casing: typing.Optional[TextCasing] = None


# @dataclass
# class InferenceConfig:
#     length_scale: float = 1.0
#     noise_scale: float = 0.667
#     noise_w: float = 0.8


# @dataclass
# class TrainingConfig(DataClassJsonMixin):
#     seed: int = 1234
#     epochs: int = 10000
#     learning_rate: float = 2e-4
#     betas: typing.Tuple[float, float] = field(default=(0.8, 0.99))
#     eps: float = 1e-9
#     batch_size: int = 32
#     fp16_run: bool = False
#     lr_decay: float = 0.999875
#     segment_size: int = 8192
#     init_lr_ratio: float = 1.0
#     warmup_epochs: int = 0
#     c_mel: int = 45
#     c_kl: float = 1.0
#     grad_clip: typing.Optional[float] = None

#     min_seq_length: typing.Optional[int] = None
#     max_seq_length: typing.Optional[int] = None

#     min_spec_length: typing.Optional[int] = None
#     max_spec_length: typing.Optional[int] = None

#     min_speaker_utterances: typing.Optional[int] = None

#     last_epoch: int = 1
#     global_step: int = 1
#     best_loss: typing.Optional[float] = None
#     audio: AudioConfig = field(default_factory=AudioConfig)
#     model: ModelConfig = field(default_factory=ModelConfig)
#     phonemes: PhonemesConfig = field(default_factory=PhonemesConfig)
#     text_aligner: AlignerConfig = field(default_factory=AlignerConfig)
#     text_language: typing.Optional[str] = None
#     phonemizer: typing.Optional[Phonemizer] = None
#     datasets: typing.List[DatasetConfig] = field(default_factory=list)
#     inference: InferenceConfig = field(default_factory=InferenceConfig)

#     version: int = 1
#     git_commit: str = ""

#     @property
#     def is_multispeaker(self):
#         return self.model.is_multispeaker or any(d.multispeaker for d in self.datasets)

#     def save(self, config_file: typing.TextIO):
#         """Save config as JSON to a file"""
#         json.dump(self.to_dict(), config_file, indent=4)

#     def get_speaker_id(self, dataset_name: str, speaker_name: str) -> int:
#         if self.speaker_id_map is None:
#             self.speaker_id_map = {}

#         full_speaker_name = f"{dataset_name}_{speaker_name}"
#         speaker_id = self.speaker_id_map.get(full_speaker_name)
#         if speaker_id is None:
#             speaker_id = len(self.speaker_id_map)
#             self.speaker_id_map[full_speaker_name] = speaker_id

#         return speaker_id

#     @staticmethod
#     def load(config_file: typing.TextIO) -> "TrainingConfig":
#         """Load config from a JSON file"""
#         return TrainingConfig.from_json(config_file.read())

#     @staticmethod
#     def load_and_merge(
#         config: "TrainingConfig",
#         config_files: typing.Iterable[typing.Union[str, Path, typing.TextIO]],
#     ) -> "TrainingConfig":
#         """Loads one or more JSON configuration files and overlays them on top of an existing config"""
#         base_dict = config.to_dict()
#         for maybe_config_file in config_files:
#             if isinstance(maybe_config_file, (str, Path)):
#                 # File path
#                 config_file = open(maybe_config_file, "r", encoding="utf-8")
#             else:
#                 # File object
#                 config_file = maybe_config_file

#             with config_file:
#                 # Load new config and overlay on existing config
#                 new_dict = json.load(config_file)
#                 TrainingConfig.recursive_update(base_dict, new_dict)

#         return TrainingConfig.from_dict(base_dict)

#     @staticmethod
#     def recursive_update(
#         base_dict: typing.Dict[typing.Any, typing.Any],
#         new_dict: typing.Mapping[typing.Any, typing.Any],
#     ) -> None:
#         """Recursively overwrites values in base dictionary with values from new dictionary"""
#         for key, value in new_dict.items():
#             if isinstance(value, collections.Mapping) and (
#                 base_dict.get(key) is not None
#             ):
#                 TrainingConfig.recursive_update(base_dict[key], value)
#             else:
#                 base_dict[key] = value
