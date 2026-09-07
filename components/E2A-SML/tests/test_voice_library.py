import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from sml_extractor.voice_library import _safe_extract, ensure_voice_library


class VoiceLibraryTests(unittest.TestCase):
    def test_existing_library_skips_download(self):
        with tempfile.TemporaryDirectory() as root:
            voice = Path(root, "voices", "eng", "adult", "female", "voice.wav")
            voice.parent.mkdir(parents=True)
            voice.write_bytes(b"wav")

            self.assertFalse(ensure_voice_library(root))

    def test_downloads_and_installs_voice_archive(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as source:
            archive = Path(source, "voices.zip")
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("voices/eng/adult/female/voice.wav", b"wav")

            download = Mock(return_value=str(archive))
            fake_hub = SimpleNamespace(hf_hub_download=download)
            with patch.dict("sys.modules", {"huggingface_hub": fake_hub}):
                self.assertTrue(ensure_voice_library(root))

            self.assertTrue(Path(root, "voices/eng/adult/female/voice.wav").is_file())
            download.assert_called_once_with(
                repo_id="ebook2audiobook/E2A-Voices",
                filename="voices.zip",
                repo_type="dataset",
            )

    def test_rejects_archive_path_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            archive = Path(root, "voices.zip")
            destination = Path(root, "extract")
            destination.mkdir()
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("../escaped.wav", b"wav")

            with self.assertRaisesRegex(ValueError, "Unsafe path"):
                _safe_extract(archive, destination)
            self.assertFalse(Path(root, "escaped.wav").exists())


if __name__ == "__main__":
    unittest.main()
