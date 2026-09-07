"""Download and safely install the shared ebook2audiobook voice library."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path


DEFAULT_REPO_ID = "ebook2audiobook/E2A-Voices"
DEFAULT_FILENAME = "voices.zip"


def has_voices(voices_dir: Path) -> bool:
    """Return whether a voice directory contains at least one WAV file."""
    return voices_dir.is_dir() and any(voices_dir.rglob("*.wav"))


def _safe_extract(archive: Path, destination: Path) -> None:
    """Extract a ZIP archive while rejecting paths outside the destination."""
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"Unsafe symlink in voice archive: {member.filename}")
            member_path = (destination / member.filename).resolve()
            if member_path != destination and destination not in member_path.parents:
                raise ValueError(f"Unsafe path in voice archive: {member.filename}")
        bundle.extractall(destination)


def ensure_voice_library(
    e2a_path: str | Path,
    repo_id: str = DEFAULT_REPO_ID,
    filename: str = DEFAULT_FILENAME,
) -> bool:
    """Install the Hub voice archive if ``e2a_path/voices`` is empty.

    Returns ``True`` when a download was performed and ``False`` when an
    existing voice library was reused.
    """
    e2a_path = Path(e2a_path).expanduser().resolve()
    voices_dir = e2a_path / "voices"
    if has_voices(voices_dir):
        return False

    from huggingface_hub import hf_hub_download

    e2a_path.mkdir(parents=True, exist_ok=True)
    print(f"No voices found in {voices_dir}; downloading {repo_id}/{filename}...")
    archive = Path(
        hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    )

    with tempfile.TemporaryDirectory(prefix="e2a-voices-") as temp_dir:
        extracted_root = Path(temp_dir)
        _safe_extract(archive, extracted_root)
        extracted_voices = extracted_root / "voices"
        if not has_voices(extracted_voices):
            raise RuntimeError("Downloaded voice archive contains no WAV files under voices/")
        shutil.copytree(extracted_voices, voices_dir, dirs_exist_ok=True)

    if not has_voices(voices_dir):
        raise RuntimeError(f"Voice library installation failed: {voices_dir} is empty")
    print(f"Voice library installed in {voices_dir}")
    return True


def configured_e2a_path() -> Path:
    """Return the repository mount used by the standalone Docker image."""
    return Path(os.environ.get("E2A_PATH", "/ebook2audiobook"))
