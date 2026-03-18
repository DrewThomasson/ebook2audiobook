from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class CambAI(TTSUtils, TTSRegistry, name='cambai'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.resampler_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets('cambai')
            self.params = {}

            fine_tuned = self.session.get('fine_tuned', 'mars-flash')
            if fine_tuned not in self.models:
                fine_tuned = 'mars-flash'
            model_cfg = self.models[fine_tuned]

            self.params['samplerate'] = model_cfg.get('samplerate', 22050)
            self.speech_model = model_cfg.get('speech_model', 'mars-flash')
            self.voice_id = self.session.get('voice_id', model_cfg.get('voice_id', 147320))
            from lib.conf_models import default_engine_settings, TTS_ENGINES
            lang_map = default_engine_settings[TTS_ENGINES['CAMBAI']].get('languages', {})
            lang_key = self.session.get('language', 'eng')
            self.language = lang_map.get(lang_key, 'en-us')

            # Init CAMB AI client
            api_key = self.session.get('cambai_api_key', os.environ.get('CAMB_API_KEY', ''))
            if not api_key:
                raise ValueError("CAMB AI API key is required. Set cambai_api_key in session or CAMB_API_KEY env var.")

            from camb.client import CambAI as CambClient
            self.client = CambClient(api_key=api_key)
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        msg = f"Loading CAMB AI TTS engine…"
        print(msg)
        return self.client

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            from camb.client import save_stream_to_file

            final_sentence_file = os.path.join(
                self.session['sentences_dir'],
                f'{sentence_index}.{default_audio_proc_format}'
            )

            response = self.client.text_to_speech.tts(
                text=sentence,
                voice_id=int(self.voice_id),
                language=self.language,
                speech_model=self.speech_model
            )

            save_stream_to_file(response, final_sentence_file)

            if not os.path.exists(final_sentence_file):
                error = f"Cannot create {final_sentence_file}"
                print(error)
                return False

            logger.info(f"CambAI TTS: Converted sentence {sentence_index} -> {final_sentence_file}")
            return True
        except Exception as e:
            error = f'CambAI.convert(): {e}'
            print(error)
            logger.error(f"CambAI TTS error on sentence {sentence_index}: {e}")
            return False

    def create_vtt(self, all_sentences:list)->bool:
        try:
            audio_dir = self.session['sentences_dir']
            vtt_path = os.path.join(self.session['process_dir'], Path(self.session['final_name']).stem + '.vtt')
            if self._build_vtt_file(all_sentences, audio_dir, vtt_path):
                return True
            return False
        except Exception as e:
            logger.error(f"CambAI VTT creation error: {e}")
            return False
