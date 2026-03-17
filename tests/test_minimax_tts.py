"""Unit tests for MiniMax TTS engine."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMiniMaxConfig(unittest.TestCase):
    """Test MiniMax TTS configuration and registration."""

    def test_engine_registered_in_tts_engines(self):
        from lib.conf_models import TTS_ENGINES
        self.assertIn('MINIMAX', TTS_ENGINES)
        self.assertEqual(TTS_ENGINES['MINIMAX'], 'minimax')

    def test_engine_registered_in_default_settings(self):
        from lib.conf_models import TTS_ENGINES, default_engine_settings
        self.assertIn(TTS_ENGINES['MINIMAX'], default_engine_settings)

    def test_default_settings_have_required_fields(self):
        from lib.conf_models import TTS_ENGINES, default_engine_settings
        settings = default_engine_settings[TTS_ENGINES['MINIMAX']]
        self.assertIn('languages', settings)
        self.assertIn('samplerate', settings)
        self.assertIn('voices', settings)
        self.assertIn('rating', settings)

    def test_samplerate_is_valid(self):
        from lib.conf_models import TTS_ENGINES, default_engine_settings
        settings = default_engine_settings[TTS_ENGINES['MINIMAX']]
        self.assertEqual(settings['samplerate'], 32000)

    def test_voices_not_empty(self):
        from lib.conf_models import TTS_ENGINES, default_engine_settings
        settings = default_engine_settings[TTS_ENGINES['MINIMAX']]
        self.assertGreater(len(settings['voices']), 0)
        self.assertIn('English_Graceful_Lady', settings['voices'])

    def test_english_language_supported(self):
        from lib.conf_models import TTS_ENGINES, default_engine_settings
        settings = default_engine_settings[TTS_ENGINES['MINIMAX']]
        self.assertIn('eng', settings['languages'])
        self.assertEqual(settings['languages']['eng'], 'en')

    def test_rating_no_vram_required(self):
        from lib.conf_models import TTS_ENGINES, default_engine_settings
        settings = default_engine_settings[TTS_ENGINES['MINIMAX']]
        self.assertEqual(settings['rating']['VRAM'], 0)

    def test_engine_in_tts_registry(self):
        from lib.classes.tts_registry import TTSRegistry
        # Force import to trigger registration
        from lib.classes.tts_engines.minimax import MiniMax
        self.assertIn('minimax', TTSRegistry.ENGINES)
        self.assertEqual(TTSRegistry.ENGINES['minimax'], MiniMax)


class TestMiniMaxPresets(unittest.TestCase):
    """Test MiniMax TTS preset models."""

    def test_presets_loadable(self):
        from lib.classes.tts_engines.presets.minimax_presets import models
        self.assertIsInstance(models, dict)
        self.assertGreater(len(models), 0)

    def test_preset_speech_28_hd(self):
        from lib.classes.tts_engines.presets.minimax_presets import models
        self.assertIn('speech-2.8-hd', models)
        hd = models['speech-2.8-hd']
        self.assertEqual(hd['model'], 'speech-2.8-hd')
        self.assertIn('samplerate', hd)
        self.assertIn('voice', hd)

    def test_preset_speech_28_turbo(self):
        from lib.classes.tts_engines.presets.minimax_presets import models
        self.assertIn('speech-2.8-turbo', models)
        turbo = models['speech-2.8-turbo']
        self.assertEqual(turbo['model'], 'speech-2.8-turbo')

    def test_preset_default_voice(self):
        from lib.classes.tts_engines.presets.minimax_presets import models
        for name, preset in models.items():
            self.assertIn('voice', preset, f'Preset {name} missing voice')
            self.assertEqual(preset['voice'], 'English_Graceful_Lady')


class TestMiniMaxEngine(unittest.TestCase):
    """Test MiniMax TTS engine initialization and methods."""

    def _make_session(self, **overrides):
        defaults = {
            'tts_engine': 'minimax',
            'fine_tuned': 'speech-2.8-hd',
            'model_cache': 'minimax-speech-2.8-hd',
            'sentences_dir': '/tmp/test_sentences',
            'process_dir': '/tmp/test_process',
            'final_name': 'test.m4b',
            'voice': None,
            'language': 'eng',
            'language_iso1': 'en',
            'device': 'cpu',
            'free_vram_gb': 0,
            'is_gui_process': False,
            'custom_model': None,
            'custom_model_dir': '/tmp/custom',
        }
        defaults.update(overrides)
        return defaults

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-api-key'})
    def test_init_with_api_key(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session()
        engine = MiniMax(session)
        self.assertEqual(engine.api_key, 'test-api-key')
        self.assertEqual(engine.params['model'], 'speech-2.8-hd')
        self.assertEqual(engine.params['samplerate'], 32000)

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_fails(self):
        from lib.classes.tts_engines.minimax import MiniMax
        # Remove MINIMAX_API_KEY if set
        os.environ.pop('MINIMAX_API_KEY', None)
        session = self._make_session()
        with self.assertRaises(ValueError) as ctx:
            MiniMax(session)
        self.assertIn('MINIMAX_API_KEY', str(ctx.exception))

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_init_invalid_fine_tuned(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session(fine_tuned='nonexistent-model')
        with self.assertRaises(ValueError) as ctx:
            MiniMax(session)
        self.assertIn('Invalid fine_tuned model', str(ctx.exception))

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_get_voice_id_default(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session(voice=None)
        engine = MiniMax(session)
        self.assertEqual(engine._get_voice_id(), 'English_Graceful_Lady')

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_get_voice_id_custom(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session(voice='English_Persuasive_Man')
        engine = MiniMax(session)
        self.assertEqual(engine._get_voice_id(), 'English_Persuasive_Man')

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_get_voice_id_invalid_falls_back(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session(voice='/some/local/file.wav')
        engine = MiniMax(session)
        self.assertEqual(engine._get_voice_id(), 'English_Graceful_Lady')

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_custom_base_url(self):
        from lib.classes.tts_engines.minimax import MiniMax
        os.environ['MINIMAX_BASE_URL'] = 'https://api.minimaxi.com'
        try:
            session = self._make_session()
            engine = MiniMax(session)
            self.assertEqual(engine.base_url, 'https://api.minimaxi.com')
        finally:
            os.environ.pop('MINIMAX_BASE_URL', None)

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_turbo_model_preset(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session(fine_tuned='speech-2.8-turbo')
        engine = MiniMax(session)
        self.assertEqual(engine.params['model'], 'speech-2.8-turbo')

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_synthesize_request_format(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session()
        engine = MiniMax(session)

        # Mock urlopen to capture the request
        hex_audio = b'ID3'.hex()
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'data': {'audio': hex_audio, 'status': 2},
            'base_resp': {'status_code': 0, 'status_msg': 'success'},
        }).encode()

        with patch('lib.classes.tts_engines.minimax.urlopen', return_value=mock_response) as mock_url:
            result = engine._synthesize('Hello world', 'English_Graceful_Lady')
            self.assertEqual(result, bytes.fromhex(hex_audio))

            # Verify request was made
            call_args = mock_url.call_args
            req = call_args[0][0]
            self.assertIn('/v1/t2a_v2', req.full_url)
            self.assertEqual(req.get_header('Authorization'), 'Bearer test-key')
            body = json.loads(req.data.decode())
            self.assertEqual(body['model'], 'speech-2.8-hd')
            self.assertEqual(body['text'], 'Hello world')
            self.assertEqual(body['voice_setting']['voice_id'], 'English_Graceful_Lady')

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_synthesize_api_error(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session()
        engine = MiniMax(session)

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'data': {},
            'base_resp': {'status_code': 1004, 'status_msg': 'authentication failed'},
        }).encode()

        with patch('lib.classes.tts_engines.minimax.urlopen', return_value=mock_response):
            with self.assertRaises(RuntimeError) as ctx:
                engine._synthesize('Hello', 'English_Graceful_Lady')
            self.assertIn('1004', str(ctx.exception))

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_convert_strips_sml_tags(self):
        from lib.classes.tts_engines.minimax import MiniMax
        session = self._make_session()

        with tempfile.TemporaryDirectory() as tmpdir:
            session['sentences_dir'] = tmpdir
            engine = MiniMax(session)

            hex_audio = b'\xff\xfb\x90\x00'.hex()
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                'data': {'audio': hex_audio, 'status': 2},
                'base_resp': {'status_code': 0, 'status_msg': 'success'},
            }).encode()

            with patch('lib.classes.tts_engines.minimax.urlopen', return_value=mock_response) as mock_url, \
                 patch.object(engine, '_mp3_to_target_format', return_value=True) as mock_conv:
                # Sentence with SML tags
                engine.convert(0, 'Hello [break] world [pause:0.5] end')

                # Check that SML tags are stripped
                call_args = mock_url.call_args
                req = call_args[0][0]
                body = json.loads(req.data.decode())
                self.assertNotIn('[break]', body['text'])
                self.assertNotIn('[pause', body['text'])
                self.assertIn('Hello', body['text'])
                self.assertIn('world', body['text'])


class TestMiniMaxTTSManager(unittest.TestCase):
    """Test that MiniMax works with TTSManager."""

    @patch.dict(os.environ, {'MINIMAX_API_KEY': 'test-key'})
    def test_tts_manager_loads_minimax(self):
        from lib.classes.tts_manager import TTSManager
        session = {
            'tts_engine': 'minimax',
            'fine_tuned': 'speech-2.8-hd',
            'model_cache': 'minimax-speech-2.8-hd',
            'sentences_dir': '/tmp/test',
            'process_dir': '/tmp/test',
            'final_name': 'test.m4b',
            'voice': None,
            'language': 'eng',
            'language_iso1': 'en',
            'device': 'cpu',
            'free_vram_gb': 0,
            'is_gui_process': False,
            'custom_model': None,
            'custom_model_dir': '/tmp/custom',
        }
        manager = TTSManager(session)
        from lib.classes.tts_engines.minimax import MiniMax
        self.assertIsInstance(manager.engine, MiniMax)


if __name__ == '__main__':
    unittest.main()
