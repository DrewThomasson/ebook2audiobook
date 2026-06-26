import sys
import json
from pathlib import Path
import shutil

# Make sure we can import from tools/Universal_TTS_Finetune
_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DIR))

from utils.piper_utils import export_piper_onnx
from utils.pipeline import _latest_matching_file, _finalize_training_artifacts

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_checkpoint.py <run_dir_path>")
        sys.exit(1)
        
    run_dir = Path(sys.argv[1]).resolve()
    if not run_dir.exists():
        print(f"Error: Run directory {run_dir} does not exist.")
        sys.exit(1)
        
    # Check what kind of files are inside to auto-detect model type
    # Piper uses Lightning (.ckpt), Coqui uses standard PyTorch (.pth)
    has_ckpt = list(run_dir.glob("**/*.ckpt")) or list(run_dir.glob("*.ckpt"))
    has_pth = list(run_dir.glob("**/*.pth")) or list(run_dir.glob("*.pth"))
    
    # Try to infer model key from folder name: training_runs/<model_key>/<timestamp>
    model_key = run_dir.parent.name
    
    if has_ckpt and (not has_pth or model_key == "piper"):
        print("Detected model family: Piper (ONNX format)")
        
        preprocessed_dir = run_dir / "preprocessed"
        config_path = preprocessed_dir / "config.json"
        if not config_path.exists():
            print(f"Error: config.json not found under {preprocessed_dir}")
            sys.exit(1)
            
        lightning_logs_dir = preprocessed_dir / "lightning_logs"
        trained_ckpt = _latest_matching_file(lightning_logs_dir, ["**/*.ckpt", "*.ckpt"])
        if not trained_ckpt:
            trained_ckpt = _latest_matching_file(run_dir, ["**/*.ckpt", "*.ckpt"])
            
        if not trained_ckpt:
            print(f"Error: No .ckpt file found in {run_dir}")
            sys.exit(1)
            
        print(f"Using checkpoint: {trained_ckpt}")
        
        ready_dir = run_dir / "ready"
        ready_dir.mkdir(parents=True, exist_ok=True)
        ready_onnx = ready_dir / "model.onnx"
        
        print("Exporting to ONNX...")
        export_piper_onnx(trained_ckpt, ready_onnx, config_path)
        
        log_path = run_dir / "training.log"
        artifacts = {
            "model_key": "piper",
            "model_label": "Piper TTS",
            "family": "piper",
            "training_root": str(run_dir),
            "dataset_dir": "",
            "checkpoint": str(ready_onnx),
            "config": str(ready_onnx) + ".json",
            "reference_wav": "",
            "log_path": str(log_path) if log_path.exists() else "",
            "unused_overrides": {},
        }
        
        artifacts_path = ready_dir / "artifacts.json"
        artifacts_path.write_text(json.dumps(artifacts, indent=2), encoding="utf-8")
        print("Successfully exported model and wrote artifacts.json!")
        
    elif has_pth:
        print(f"Detected model family: Coqui PTH (Model key inferred: {model_key})")
        
        # Use pipeline's built-in finalizer for Coqui models (which handles XTTS optimizations too)
        try:
            artifacts = _finalize_training_artifacts(
                spec_key=model_key,
                training_root=run_dir,
                dataset_dir=Path(""),
                reference_wav=""
            )
            print("Successfully packaged Coqui checkpoint and wrote artifacts.json!")
        except Exception as e:
            print(f"Error finalizing Coqui artifacts: {e}")
            sys.exit(1)
    else:
        print("Error: Could not find any .ckpt or .pth files to export.")
        sys.exit(1)
        
    print(f"You can now test this model in the GUI or via: python headless_cli.py synthesize --artifacts {run_dir}/ready --text '...' --model {model_key}")

if __name__ == "__main__":
    main()
