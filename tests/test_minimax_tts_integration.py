"""Integration tests for MiniMax TTS engine using live API."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

API_KEY = os.environ.get('MINIMAX_API_KEY', '')
BASE_URL = os.environ.get('MINIMAX_BASE_URL', 'https://api.minimax.io')


@unittest.skipUnless(API_KEY, 'MINIMAX_API_KEY not set, skipping integration tests')
class TestMiniMaxTTSIntegration(unittest.TestCase):
    """Integration tests that call the real MiniMax TTS API."""

    def test_synthesize_basic(self):
        """Test basic speech synthesis returns valid audio."""
        from lib.classes.tts_engines.minimax import MiniMax

        with tempfile.TemporaryDirectory() as tmpdir:
            session = {
                'tts_engine': 'minimax',
                'fine_tuned': 'speech-2.8-hd',
                'model_cache': 'minimax-speech-2.8-hd',
                'sentences_dir': tmpdir,
                'process_dir': tmpdir,
                'final_name': 'test.m4b',
                'voice': None,
                'language': 'eng',
                'language_iso1': 'en',
                'device': 'cpu',
                'free_vram_gb': 0,
                'is_gui_process': False,
                'custom_model': None,
                'custom_model_dir': tmpdir,
            }
            engine = MiniMax(session)
            audio_data = engine._synthesize(
                'Hello, this is a MiniMax TTS test.',
                'English_Graceful_Lady',
            )
            self.assertIsInstance(audio_data, bytes)
            self.assertGreater(len(audio_data), 100)

    def test_convert_creates_audio_file(self):
        """Test full convert pipeline creates an audio file."""
        from lib.classes.tts_engines.minimax import MiniMax

        with tempfile.TemporaryDirectory() as tmpdir:
            session = {
                'tts_engine': 'minimax',
                'fine_tuned': 'speech-2.8-hd',
                'model_cache': 'minimax-speech-2.8-hd',
                'sentences_dir': tmpdir,
                'process_dir': tmpdir,
                'final_name': 'test.m4b',
                'voice': None,
                'language': 'eng',
                'language_iso1': 'en',
                'device': 'cpu',
                'free_vram_gb': 0,
                'is_gui_process': False,
                'custom_model': None,
                'custom_model_dir': tmpdir,
            }
            engine = MiniMax(session)
            result = engine.convert(0, 'This is sentence number one for audiobook.')
            self.assertTrue(result, 'convert() should return True on success')

            from lib.conf import default_audio_proc_format
            output_file = os.path.join(tmpdir, f'0.{default_audio_proc_format}')
            self.assertTrue(
                os.path.exists(output_file),
                f'Output file should exist: {output_file}',
            )
            self.assertGreater(
                os.path.getsize(output_file), 100,
                'Output file should have content',
            )

    def test_convert_with_different_voice(self):
        """Test convert with a specific voice ID."""
        from lib.classes.tts_engines.minimax import MiniMax

        with tempfile.TemporaryDirectory() as tmpdir:
            session = {
                'tts_engine': 'minimax',
                'fine_tuned': 'speech-2.8-hd',
                'model_cache': 'minimax-speech-2.8-hd',
                'sentences_dir': tmpdir,
                'process_dir': tmpdir,
                'final_name': 'test.m4b',
                'voice': 'English_Persuasive_Man',
                'language': 'eng',
                'language_iso1': 'en',
                'device': 'cpu',
                'free_vram_gb': 0,
                'is_gui_process': False,
                'custom_model': None,
                'custom_model_dir': tmpdir,
            }
            engine = MiniMax(session)
            result = engine.convert(0, 'Testing with a male voice.')
            self.assertTrue(result)

    def test_convert_turbo_model(self):
        """Test convert with the turbo model."""
        from lib.classes.tts_engines.minimax import MiniMax

        with tempfile.TemporaryDirectory() as tmpdir:
            session = {
                'tts_engine': 'minimax',
                'fine_tuned': 'speech-2.8-turbo',
                'model_cache': 'minimax-speech-2.8-turbo',
                'sentences_dir': tmpdir,
                'process_dir': tmpdir,
                'final_name': 'test.m4b',
                'voice': None,
                'language': 'eng',
                'language_iso1': 'en',
                'device': 'cpu',
                'free_vram_gb': 0,
                'is_gui_process': False,
                'custom_model': None,
                'custom_model_dir': tmpdir,
            }
            engine = MiniMax(session)
            result = engine.convert(0, 'Testing with the turbo model.')
            self.assertTrue(result)

    def test_tts_api_direct(self):
        """Test direct TTS API call with raw HTTP."""
        from urllib.request import Request, urlopen

        payload = {
            'model': 'speech-2.8-hd',
            'text': 'MiniMax integration test.',
            'stream': False,
            'voice_setting': {
                'voice_id': 'English_Graceful_Lady',
                'speed': 1,
                'vol': 1,
                'pitch': 0,
            },
            'audio_setting': {
                'sample_rate': 32000,
                'bitrate': 128000,
                'format': 'mp3',
                'channel': 1,
            },
        }

        req = Request(
            f'{BASE_URL}/v1/t2a_v2',
            data=json.dumps(payload).encode(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
            },
        )
        resp = urlopen(req, timeout=60)
        result = json.loads(resp.read().decode())

        self.assertEqual(result['base_resp']['status_code'], 0)
        self.assertIn('audio', result['data'])
        self.assertGreater(len(result['data']['audio']), 0)
        self.assertEqual(result['data']['status'], 2)

        # Verify hex decoding works
        audio_bytes = bytes.fromhex(result['data']['audio'])
        self.assertGreater(len(audio_bytes), 100)


if __name__ == '__main__':
    unittest.main()
