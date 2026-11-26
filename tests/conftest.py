"""
pytest configuration: inject lightweight stubs for every heavy dependency that
lib/core.py pulls in at import time.  The stubs are intentionally thin – they
only need to satisfy attribute lookups that happen during module-level
execution, not actual ML inference.
"""
import sys
import types
import re as stdlib_re

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _stub(name, **attrs):
    """Return (or create) a stub module with the given attributes."""
    m = sys.modules.get(name)
    if m is None:
        m = types.ModuleType(name)
        sys.modules[name] = m
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


# ---------------------------------------------------------------------------
# 'regex' is used as 're' alias (with Unicode properties) in core.py
# ---------------------------------------------------------------------------
sys.modules.setdefault('regex', stdlib_re)

# ---------------------------------------------------------------------------
# Standard-ish libs that may not be installed in a slim test environment
# ---------------------------------------------------------------------------
_stub('ebooklib')
_eb_epub = _stub('ebooklib.epub', EpubBook=object, EpubHtml=object)
sys.modules['ebooklib'].epub = _eb_epub          # type: ignore[attr-defined]

_stub('psutil')
_stub('requests')
_stub('stanza')
_stub('stanza.pipeline.core', Pipeline=object, DownloadMethod=object)
_stub('uvicorn')

# gradio – stub the attributes used at module level in core.py
class _GrUpdate:
    def __init__(self, **kw): self.__dict__.update(kw)

class _GrError(Exception): pass
class _GrWarning(Exception): pass
class _GrInfo(Exception): pass
class _GrSuccess(Exception): pass
class _GrRequest: pass

_gr = _stub(
    'gradio',
    update=_GrUpdate,
    Error=_GrError,
    Warning=_GrWarning,
    Info=_GrInfo,
    Success=_GrSuccess,
    Request=_GrRequest,
    Blocks=object,
    State=object,
    HTML=object,
    Textbox=object,
    Button=object,
    Dropdown=object,
    Row=object,
    Column=object,
    Tab=object,
    Tabs=object,
    Accordion=object,
    Label=object,
    Image=object,
    Audio=object,
    File=object,
    Slider=object,
    Checkbox=object,
    CheckboxGroup=object,
    Radio=object,
    Number=object,
    Markdown=object,
    DataFrame=object,
    Gallery=object,
    Progress=object,
    ChatInterface=object,
    StatusTracker=object,
)
_stub('gradio.components')

# PIL
_pil_image = _stub('PIL.Image', Image=object, open=lambda *a, **kw: None)
_pil_seq   = _stub('PIL.ImageSequence', Iterator=object)
_pil       = _stub('PIL', Image=_pil_image, ImageSequence=_pil_seq)

_stub('tqdm', tqdm=lambda iterable=(), *a, **kw: iter(iterable))
_stub('bs4', BeautifulSoup=object, NavigableString=object, Tag=object)
_stub('iso639', Lang=object)
_stub('markdown', markdown=lambda s, **kw: s)
_stub('langdetect', detect=lambda s: 'en')

_pydub = _stub('pydub', AudioSegment=object)
_stub('pydub.utils', mediainfo=lambda f: {})

_stub('num2words2', num2words=lambda n, **kw: str(n))
_stub('unidecode', unidecode=lambda s: s)
_stub('phonemizer', phonemize=lambda s, **kw: s)

class _KakasiConverter:
    def do(self, s): return s

class _Kakasi:
    def setMode(self, *a): pass
    def getConverter(self): return _KakasiConverter()

_stub('pykakasi', kakasi=_Kakasi)
_stub('pypinyin',
      pinyin=lambda w, style=None: [[c] for c in w],
      Style=types.SimpleNamespace(NORMAL=0))

# ---------------------------------------------------------------------------
# lib.classes sub-modules (the real lib/ package is importable; only
# classes with heavy deps need stubbing)
# ---------------------------------------------------------------------------

class _NonTextFilter:
    def __init__(self, **kw): pass
    def __call__(self, t): return t

_stub('lib.classes.subprocess_pipe', SubprocessPipe=object)
_stub('lib.classes.bug_reporter',    bug_reporter=lambda *a, **kw: None)
_stub('lib.classes.vram_detector',   VRAMDetector=object)
_stub('lib.classes.voice_extractor', VoiceExtractor=object)
_stub('lib.classes.non_text_filter', NonTextFilter=_NonTextFilter)
_stub('lib.classes.argos_translator', ArgosTranslator=object)
_stub('lib.classes.tts_manager',     TTSManager=object)
_stub('lib.classes.tts_engines')
_stub('lib.classes.tts_engines.common')
_stub('lib.classes.tts_engines.common.audio',
      get_audiolist_duration=lambda *a: 0.0,
      get_audio_duration=lambda *a: 0.0)
_stub('lib.classes.tts_engines.common.utils',
      build_vtt_file=lambda *a: None,
      format_timestamp=lambda *a: '',
      gpu_fault=lambda *a: None,
      gpu_fault_alert=lambda *a: None)
