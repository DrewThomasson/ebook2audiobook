from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
def get_models_dir()->Path:
    shared_dir = _PROJECT_ROOT.parent.parent / 'models'
    repository_component = shared_dir.parent / 'components' / 'Universal_TTS_Finetune'
    in_repository = repository_component.resolve() == _PROJECT_ROOT and shared_dir.is_dir()
    models_dir = shared_dir if in_repository else _PROJECT_ROOT / 'models'
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir
