import sys

from . import conf

# lib/conf.py is the file users are told to edit (README, the crash reports line) and to put back after an update: one
# kept from an older version, or with an entry removed, lacks a device this version addresses by name, and e2a died far
# from the cause (crash report d53d2fd414aa8596: KeyError 'VULKAN' in DeviceInstaller.vulkan_torch_ok, filed as a bug).
# Checked here, the first code of any lib import (app.py, the launchers' DeviceInstaller calls, tools): a shipped
# conf.py always passes
conf_device_keys = ['CPU', 'CUDA', 'MPS', 'ROCM', 'XPU', 'JETSON', 'VULKAN']
conf_missing = [f"devices['{key}']" for key in conf_device_keys if key not in getattr(conf, 'devices', {})]
if conf_missing:
    from .lang import legends
    error = legends['error_conf_outdated'].format(file=conf.__file__, missing=', '.join(conf_missing))
    print(error, file=sys.stderr)
    sys.exit(1)

from .conf import (
    DEVICE_SYSTEM, FULL_DOCKER, NATIVE, BUILD_DOCKER, workflow_id, fernet_key, fernet_data, audiobooks_cli_dir, audiobooks_gradio_dir,
    audiobooks_host_dir, debug_mode, default_audio_proc_samplerate, max_upload_size,
    default_audio_proc_format, default_device, default_gpu_wiki, 
    default_output_format, default_output_channel, systems, archs, cli_options, devices, vulkan_loader, device_info_json, device_info_dict, ebook_formats,
    ebooks_dir, interface_component_options, interface_concurrency_limit, interface_progress_interval,
    interface_host, interface_port, interface_shared_tmp_expire,
    max_python_version, min_python_version, models_dir,
    output_formats, prog_version, python_env_dir, python_exec,
    requirements_file, components_dir, root_dir, tmp_dir, run_dir, gradio_cache_dir, tmp_expire, max_ebook_textarea_length,
    tts_dir, voice_formats, voices_dir, default_output_split, default_output_split_hours,
    default_abs_url, default_abs_api_token, default_abs_library,
    default_py_major, default_py_minor, default_pytorch_url, default_pytorch_amd_url, default_pytorch_nightly_url, default_torchcodec_arm_url, default_jetson_url,
    torch_matrix, torchaudio_max, transformers_caps, cuda_version_range, rocm_version_range, mps_version_range, xpu_version_range, jetson_version_range,
    voices_url, detect_gpu_script, default_vram_flush_ratio
)

from .conf_lang import (
    abbreviations_mapping, chapter_word_mapping, default_language_code, language_separator,
    roman_numbers_tuples, roman_lookalikes, language_ordinal_before, emojis_list, install_info, session_info, ipa_mapping, language_mapping,
    language_math_phonemes, language_clock, punctuation_list, 
    punctuation_list_set, punctuation_split_hard, punctuation_split_hard_set,
    punctuation_split_soft, punctuation_split_soft_set, punctuation_switch,
    specialchars_mapping, chars_remove, year_to_decades_languages, acronym_as_word_languages, language_decimal_comma,
    language_number_words, currency_symbols,
)

from .conf_models import (
    TTS_ENGINES, TTS_VOICE_CONVERSION, TTS_SML, SML_TAG_PATTERN, IPA_REMAINING_PATTERN, sml_escape_tag, default_fine_tuned, default_tts_engine, 
    default_engine_settings, default_vc_model, default_voice_detection_model, default_voice_separation_model, tts_engines_from_coqui, tts_engines_with_inner_speaker, tts_engines_with_custom_model,
    loaded_tts, xtts_builtin_speakers_list,
    max_custom_model, max_custom_voices,
    sml_tag_keys, default_speaker
)

from .conf_interlude import (
    interlude_duration_range, interlude_fade_in_range, interlude_fade_out_range, interlude_duck_db, interlude_duck_threshold, interlude_duck_ratio,
    interlude_duck_attack, interlude_duck_release, interlude_classifier_repo, interlude_genre_min_score,
    interlude_templates, interlude_moods, interlude_genre_styles, interlude_classifier_languages, interlude_neutral_style, interlude_neutral_moods
)

__all__ = [

    # from conf
    "DEVICE_SYSTEM", "FULL_DOCKER", "NATIVE", "BUILD_DOCKER", "workflow_id", "fernet_key", "fernet_data", "audiobooks_cli_dir", "audiobooks_gradio_dir",
    "audiobooks_host_dir", "debug_mode", "default_audio_proc_samplerate", "max_upload_size",
    "default_audio_proc_format", "default_device", "default_gpu_wiki",
    "default_output_format", "default_output_channel", "systems", "archs", "cli_options", "devices", "vulkan_loader", "device_info_json", "device_info_dict", "ebook_formats",
    "ebooks_dir", "interface_component_options", "interface_concurrency_limit", "interface_progress_interval",
    "interface_host", "interface_port", "interface_shared_tmp_expire",
    "max_python_version", "min_python_version", "models_dir",
    "output_formats", "prog_version", "python_env_dir", "python_exec",
    "requirements_file", "components_dir", "root_dir", "tmp_dir", "run_dir", "gradio_cache_dir", "tmp_expire", "max_ebook_textarea_length", 
    "tts_dir", "voice_formats", "voices_dir", "default_output_split", "default_output_split_hours",
    "default_abs_url", "default_abs_api_token", "default_abs_library",
    "default_py_major", "default_py_minor", "default_pytorch_url", "default_pytorch_nightly_url", "default_pytorch_amd_url", "default_torchcodec_arm_url", "default_jetson_url",
    "torch_matrix", "torchaudio_max", "transformers_caps", "cuda_version_range", "rocm_version_range", "mps_version_range", "xpu_version_range", "jetson_version_range",
    "voices_url", "detect_gpu_script", "default_vram_flush_ratio",

    # from conf_lang
    "abbreviations_mapping", "chapter_word_mapping", "default_language_code", "language_separator",
    "roman_numbers_tuples", "roman_lookalikes", "language_ordinal_before", "emojis_list", "install_info", "session_info", "ipa_mapping", "language_mapping",
    "language_math_phonemes", "language_clock", "punctuation_list", 
    "punctuation_list_set", "punctuation_split_hard", "punctuation_split_hard_set",
    "punctuation_split_soft", "punctuation_split_soft_set", "punctuation_switch",
    "specialchars_mapping", "chars_remove", "year_to_decades_languages", "acronym_as_word_languages", "language_decimal_comma",
    "language_number_words", "currency_symbols",
    
    # from conf_models
    "TTS_ENGINES", "TTS_VOICE_CONVERSION", "TTS_SML", "SML_TAG_PATTERN", "IPA_REMAINING_PATTERN", "sml_escape_tag", "default_fine_tuned", "default_tts_engine",
    "default_engine_settings", "default_vc_model", "default_voice_detection_model", "default_voice_separation_model", "tts_engines_from_coqui", "tts_engines_with_inner_speaker", "tts_engines_with_custom_model",
    "loaded_tts", "xtts_builtin_speakers_list", "max_custom_model",
    "max_custom_voices",
    "sml_tag_keys", "default_speaker",
    
    # from conf_interlude
    "interlude_duration_range", "interlude_fade_in_range", "interlude_fade_out_range", "interlude_duck_db", "interlude_duck_threshold", "interlude_duck_ratio",
    "interlude_duck_attack", "interlude_duck_release", "interlude_classifier_repo", "interlude_genre_min_score", "interlude_templates",
    "interlude_moods", "interlude_genre_styles", "interlude_classifier_languages", "interlude_neutral_style", "interlude_neutral_moods"
]
