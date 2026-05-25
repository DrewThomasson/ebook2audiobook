from __future__ import annotations

# Patch pkgutil.ImpImporter and importlib.machinery.FileFinder.find_module for Python 3.12 compatibility with older pkg_resources / setuptools
import pkgutil
import importlib.machinery

if not hasattr(pkgutil, "ImpImporter"):
    class DummyImpImporter:
        pass
    pkgutil.ImpImporter = DummyImpImporter

if not hasattr(importlib.machinery.FileFinder, "find_module"):
    def find_module_shim(self, fullname, path=None):
        spec = self.find_spec(fullname, path)
        return spec.loader if spec is not None else None
    importlib.machinery.FileFinder.find_module = find_module_shim

# Patch PyTorch 2.6+ to default to weights_only=False in torch.load for compatibility with older checkpoints
try:
    import torch
    if hasattr(torch, "load"):
        original_load = torch.load
        def patched_load(*args, **kwargs):
            if "weights_only" not in kwargs:
                kwargs["weights_only"] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
except ImportError:
    pass

import argparse
import json

from utils.pipeline import (
    default_test_output,
    dropdown_choices,
    find_latest_artifacts,
    list_supported_models,
    load_artifacts,
    prepare_dataset,
    synthesize,
    train_model,
    _json_ready,
)


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _calculate_viable_epochs(model_key: str, sample_count: int, batch_size: int) -> int:
    steps_per_epoch = max(1, sample_count // batch_size)
    
    if model_key.startswith("xtts_"):
        target_steps = 1500
    elif model_key in ["tacotron2_capacitron", "tacotron2_dca", "tacotron2_ddc", "fast_pitch", "fast_speech", "fastspeech2"]:
        target_steps = 15000
    else:
        # VITS, Glow-TTS, Align TTS, DelightfulTTS, SpeedySpeech, Overflow, NeuralHMM-TTS
        target_steps = 10000
        
    return max(1, target_steps // steps_per_epoch)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Headless workflow for Universal Coqui TTS fine-tuning.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-models", help="List supported training recipes.")

    prepare = subparsers.add_parser("prepare-dataset", help="Build an LJSpeech-style dataset from audio files.")
    prepare.add_argument("--output-root", required=True)
    prepare.add_argument("--audio-dir")
    prepare.add_argument("--audio-file", action="append", default=[])
    prepare.add_argument("--transcript-file")
    prepare.add_argument("--language", default="en")
    prepare.add_argument("--whisper-model", default="small")
    prepare.add_argument("--eval-percentage", type=float, default=0.15)
    prepare.add_argument("--min-segment-seconds", type=float, default=0.5)
    prepare.add_argument("--max-segment-seconds", type=float, default=12.0)
    prepare.add_argument("--segment-buffer-seconds", type=float, default=0.2)
    prepare.add_argument("--diarize-speakers", action="store_true", help="Automatically cluster audio into separate speaker datasets")
    prepare.add_argument("--expected-speakers", type=int, default=0, help="Expected number of speaker clusters (0 to auto-detect based on threshold)")
    prepare.add_argument("--diarize-threshold", type=float, default=0.3, help="Distance threshold for speaker clustering auto-detection (used if expected-speakers is 0)")

    train = subparsers.add_parser("train", help="Train or fine-tune a selected Coqui recipe.")
    train.add_argument("--model", required=True, choices=[key for key, _ in dropdown_choices()])
    train.add_argument("--output-root", required=True)
    train.add_argument("--dataset-dir")
    train.add_argument("--language", default="en")
    train.add_argument("--epochs", type=int, default=10)
    train.add_argument("--batch-size", type=int, default=8)
    train.add_argument("--grad-accum", type=int, default=1)
    train.add_argument("--max-audio-seconds", type=int, default=11)
    train.add_argument("--restore-path")
    train.add_argument("--extra-overrides-json")
    train.add_argument("--no-pretrained", action="store_true")
    train.add_argument("--dry-run", action="store_true")
    train.add_argument("--no-stream-logs", action="store_true", help="Disable streaming of training logs to the console")
    train.add_argument("--sample-epoch-interval", type=int, default=0, help="Generate and save an audio sample every N epochs. Set to 0 to disable.")
    train.add_argument("--sample-text", default="", help="Text sentence to synthesize at each interval.")

    infer = subparsers.add_parser("synthesize", help="Generate speech from the latest or selected trained model.")
    infer.add_argument("--artifacts", required=True, help="Path to artifacts.json, a ready/ folder, or an output root.")
    infer.add_argument("--model")
    infer.add_argument("--text", required=True)
    infer.add_argument("--language", default="en")
    infer.add_argument("--speaker-wav")
    infer.add_argument("--output-file")

    workflow = subparsers.add_parser("workflow", help="Prepare dataset, train, and optionally synthesize in one command.")
    workflow.add_argument("--model", required=True, choices=[key for key, _ in dropdown_choices()])
    workflow.add_argument("--output-root", required=True)
    workflow.add_argument("--audio-dir")
    workflow.add_argument("--audio-file", action="append", default=[])
    workflow.add_argument("--transcript-file")
    workflow.add_argument("--language", default="en")
    workflow.add_argument("--whisper-model", default="small")
    workflow.add_argument("--epochs", type=int, default=10)
    workflow.add_argument("--batch-size", type=int, default=8)
    workflow.add_argument("--grad-accum", type=int, default=1)
    workflow.add_argument("--max-audio-seconds", type=int, default=11)
    workflow.add_argument("--restore-path")
    workflow.add_argument("--extra-overrides-json")
    workflow.add_argument("--no-pretrained", action="store_true")
    workflow.add_argument("--test-text")
    workflow.add_argument("--speaker-wav")
    workflow.add_argument("--output-file")
    workflow.add_argument("--no-stream-logs", action="store_true", help="Disable streaming of training logs to the console")
    workflow.add_argument("--diarize-speakers", action="store_true", help="Automatically cluster audio into separate speaker datasets")
    workflow.add_argument("--expected-speakers", type=int, default=0, help="Expected number of speaker clusters (0 to auto-detect based on threshold)")
    workflow.add_argument("--diarize-threshold", type=float, default=0.3, help="Distance threshold for speaker clustering auto-detection (used if expected-speakers is 0)")
    workflow.add_argument("--sample-epoch-interval", type=int, default=0, help="Generate and save an audio sample every N epochs. Set to 0 to disable.")
    workflow.add_argument("--sample-text", default="", help="Text sentence to synthesize at each interval.")

    batch_test = subparsers.add_parser("batch-test", help="Test all supported models sequentially on the same dataset.")
    batch_test.add_argument("--output-root", required=True)
    batch_test.add_argument("--audio-dir")
    batch_test.add_argument("--audio-file", action="append", default=[])
    batch_test.add_argument("--transcript-file")
    batch_test.add_argument("--language", default="en")
    batch_test.add_argument("--whisper-model", default="small")
    batch_test.add_argument("--epochs", type=int, default=1)
    batch_test.add_argument("--batch-size", type=int, default=8)
    batch_test.add_argument("--grad-accum", type=int, default=1)
    batch_test.add_argument("--max-audio-seconds", type=int, default=11)
    batch_test.add_argument("--test-text", default="This is a quick validation sample from the batch test.")
    batch_test.add_argument("--discard-models", action="store_true", help="Delete model checkpoints after generating sample audio to save space.")
    batch_test.add_argument("--auto-calculate-epochs", action="store_true", help="Automatically calculate viable epochs based on dataset size and model architecture.")
    batch_test.add_argument("--diarize-speakers", action="store_true", help="Automatically cluster audio into separate speaker datasets")
    batch_test.add_argument("--expected-speakers", type=int, default=0, help="Expected number of speaker clusters (0 to auto-detect based on threshold)")
    batch_test.add_argument("--diarize-threshold", type=float, default=0.3, help="Distance threshold for speaker clustering auto-detection (used if expected-speakers is 0)")
    batch_test.add_argument("--no-stream-logs", action="store_true", help="Disable streaming of training logs to the console")
    batch_test.add_argument("--extra-overrides-json")

    latest = subparsers.add_parser("latest-artifacts", help="Resolve the newest trained model artifacts.")
    latest.add_argument("--output-root", required=True)
    latest.add_argument("--model")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "list-models":
        _print_json({"models": list_supported_models()})
        return

    if args.command == "prepare-dataset":
        result = prepare_dataset(
            output_root=args.output_root,
            audio_dir=args.audio_dir,
            audio_files=args.audio_file,
            transcript_file=args.transcript_file,
            language=args.language,
            whisper_model_name=args.whisper_model,
            eval_percentage=args.eval_percentage,
            min_segment_seconds=args.min_segment_seconds,
            max_segment_seconds=args.max_segment_seconds,
            segment_buffer_seconds=args.segment_buffer_seconds,
            diarize_speakers=args.diarize_speakers,
            expected_speakers=args.expected_speakers,
            diarize_threshold=args.diarize_threshold,
        )
        _print_json(result)
        return

    if args.command == "train":
        result = train_model(
            model_key=args.model,
            output_root=args.output_root,
            dataset_dir=args.dataset_dir,
            language=args.language,
            epochs=args.epochs,
            batch_size=args.batch_size,
            grad_accum=args.grad_accum,
            max_audio_seconds=args.max_audio_seconds,
            restore_path=args.restore_path,
            use_pretrained=not args.no_pretrained,
            extra_overrides_json=args.extra_overrides_json,
            dry_run=args.dry_run,
            stream_logs=not args.no_stream_logs,
            sample_epoch_interval=args.sample_epoch_interval,
            sample_text=args.sample_text,
        )
        _print_json(result)
        return

    if args.command == "synthesize":
        artifacts = load_artifacts(args.artifacts, model_key=args.model)
        output_file = args.output_file or default_test_output(artifacts["training_root"])
        result = synthesize(
            artifacts_path_or_dir=artifacts["artifacts_file"],
            model_key=args.model,
            text=args.text,
            language=args.language,
            speaker_wav=args.speaker_wav,
            output_file=output_file,
        )
        _print_json(result)
        return

    if args.command == "workflow":
        dataset = prepare_dataset(
            output_root=args.output_root,
            audio_dir=args.audio_dir,
            audio_files=args.audio_file,
            transcript_file=args.transcript_file,
            language=args.language,
            whisper_model_name=args.whisper_model,
            diarize_speakers=args.diarize_speakers,
            expected_speakers=args.expected_speakers,
            diarize_threshold=args.diarize_threshold,
        )
        training = train_model(
            model_key=args.model,
            output_root=args.output_root,
            dataset_dir=dataset["dataset_dir"],
            language=args.language,
            epochs=args.epochs,
            batch_size=args.batch_size,
            grad_accum=args.grad_accum,
            max_audio_seconds=args.max_audio_seconds,
            restore_path=args.restore_path,
            use_pretrained=not args.no_pretrained,
            extra_overrides_json=args.extra_overrides_json,
            stream_logs=not args.no_stream_logs,
            sample_epoch_interval=args.sample_epoch_interval,
            sample_text=args.sample_text,
        )
        payload = {"dataset": dataset, "training": training}
        if args.test_text:
            payload["synthesis"] = synthesize(
                artifacts_path_or_dir=training["training_root"],
                model_key=args.model,
                text=args.test_text,
                language=args.language,
                speaker_wav=args.speaker_wav,
                output_file=args.output_file or default_test_output(args.output_root),
            )
        _print_json(payload)
        return

    if args.command == "batch-test":
        dataset = prepare_dataset(
            output_root=args.output_root,
            audio_dir=args.audio_dir,
            audio_files=args.audio_file,
            transcript_file=args.transcript_file,
            language=args.language,
            whisper_model_name=args.whisper_model,
            diarize_speakers=args.diarize_speakers,
            expected_speakers=args.expected_speakers,
            diarize_threshold=args.diarize_threshold,
        )
        
        import shutil
        from pathlib import Path
        import traceback
        
        batch_results_dir = Path(args.output_root) / "batch_results"
        batch_results_dir.mkdir(parents=True, exist_ok=True)
        
        results = {"dataset": dataset, "models": {}}
        sample_count = dataset.get("created_sample_count", 0)
        
        for model_key, model_label in dropdown_choices():
            print(f"\n==================================================")
            print(f"Batch testing: {model_label} ({model_key})")
            print(f"==================================================\n")
            
            if args.auto_calculate_epochs and sample_count > 0:
                current_epochs = _calculate_viable_epochs(model_key, sample_count, args.batch_size)
                print(f"Auto-calculated epochs for {model_label}: {current_epochs} (Dataset clips: {sample_count}, Batch size: {args.batch_size})")
            else:
                current_epochs = args.epochs
            
            try:
                training = train_model(
                    model_key=model_key,
                    output_root=args.output_root,
                    dataset_dir=dataset["dataset_dir"],
                    language=args.language,
                    epochs=current_epochs,
                    batch_size=args.batch_size,
                    grad_accum=args.grad_accum,
                    max_audio_seconds=args.max_audio_seconds,
                    restore_path=None,
                    use_pretrained=True,
                    extra_overrides_json=args.extra_overrides_json,
                    stream_logs=not args.no_stream_logs,
                )
                
                output_wav = batch_results_dir / f"{model_key}.wav"
                
                synthesis = synthesize(
                    artifacts_path_or_dir=training["training_root"],
                    model_key=model_key,
                    text=args.test_text,
                    language=args.language,
                    speaker_wav=None,
                    output_file=str(output_wav),
                )
                
                results["models"][model_key] = {
                    "status": "success",
                    "training": training,
                    "synthesis": synthesis,
                    "sample_audio": str(output_wav)
                }
                
                if args.discard_models:
                    print(f"Discarding model artifacts for {model_key} to save space...")
                    
                    # Preserve the log file before deleting
                    log_file = Path(training["training_root"]) / "training.log"
                    if log_file.exists():
                        dest_log = batch_results_dir / f"{model_key}_training.log"
                        shutil.copy2(log_file, dest_log)
                        
                    shutil.rmtree(training["training_root"], ignore_errors=True)
                    results["models"][model_key]["discarded"] = True
                    
            except Exception as e:
                print(f"FAILED to test {model_key}: {e}")
                traceback.print_exc()
                results["models"][model_key] = {
                    "status": "error",
                    "error_message": str(e)
                }
                
        # Save the full batch summary to a file
        summary_path = batch_results_dir / "batch_summary.json"
        summary_path.write_text(json.dumps(_json_ready(results), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nBatch test complete! Summary saved to: {summary_path}")
        
        _print_json(results)
        return

    if args.command == "latest-artifacts":
        _print_json(find_latest_artifacts(args.output_root, model_key=args.model))
        return


if __name__ == "__main__":
    main()
