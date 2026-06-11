import regex as re
import unicodedata

from typing import Optional
from lib.conf_lang import punctuation_split_hard_set, punctuation_list_set, chars_remove, emojis_list, language_math_phonemes

class NonTextFilter:

    '''Strip non-prose content (math, code, equations, chem formulas, urls, emoji)
    while preserving prose, numbers, dates, currencies, SML tags, and math
    symbols covered by language_math_phonemes (so the vocalizer can speak them).
    Language-agnostic via conf_lang tables — covers Latin, Cyrillic, Arabic, CJK,
    Indic, Ethiopic, Tibetan, Khmer, Thai, Hebrew, Lao scripts. Works for all
    supported languages: math symbols are preserved using the global union of
    language_math_phonemes, then vocalized per-language (or via fallback) by
    math2words downstream.
    Stateless during filter(); safe to share across threads/processes.
    '''

    _NO_SPACE_LANGS = frozenset({'zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm', 'bod'})

    _NO_SPACE_RANGES = [
        (0x0E00, 0x0E7F),    # Thai
        (0x0E80, 0x0EFF),    # Lao
        (0x1000, 0x109F),    # Myanmar
        (0x1780, 0x17FF),    # Khmer
        (0x0F00, 0x0FFF),    # Tibetan
        (0x4E00, 0x9FFF),    # CJK unified
        (0x3040, 0x309F),    # Hiragana
        (0x30A0, 0x30FF),    # Katakana
        (0xAC00, 0xD7AF),    # Hangul
    ]

    _MATH_UNICODE_RANGES = [
        (0x2070, 0x209F),    # super/subscripts
        (0x2100, 0x214F),    # letterlike (ℝ, ℕ, ℏ, …)
        (0x2190, 0x21FF),    # arrows
        (0x2200, 0x22FF),    # math operators (∑, ∫, ∀, …)
        (0x2300, 0x23FF),    # misc technical
        (0x25A0, 0x25FF),    # geometric shapes
        (0x27C0, 0x27EF),    # misc math A
        (0x2900, 0x297F),    # supplemental arrows
        (0x2980, 0x29FF),    # misc math B
        (0x2A00, 0x2AFF),    # supplemental math operators
        (0x1D400, 0x1D7FF),  # math alphanumerics (𝐀, 𝛼, …)
    ]

    # Global union of single-char math symbols any language can vocalize.
    # Built once at import; identical for every language. math2words decides
    # the actual pronunciation per-language (with eng fallback for unsupported).
    _MATH_KEEP = frozenset(
        k for d in language_math_phonemes.values() for k in d
        if len(k) == 1 and not k.isalnum()
    )

    _SENT_TERMINATORS = ''.join(re.escape(c) for c in punctuation_split_hard_set)
    _SENT_SPLIT = re.compile(
        rf'(?<=[{_SENT_TERMINATORS}])\s+'
        rf'|(?<=[{_SENT_TERMINATORS}])(?=\S)'
    )

    _TEXT_PUNCT = frozenset(
        punctuation_list_set | {'\'', '-', '/', '%', '$', '&'}
    )

    _CHARS_REMOVE_RE = re.compile('[' + re.escape(''.join(chars_remove)) + ']')
    _EMOJI_RE        = re.compile('[' + ''.join(emojis_list) + ']')

    _SPECIAL_CATEGORIES = frozenset({
        'So',    # Symbol, other (☆, ♠, ☢, ⚛, …)
        'Sm',    # Symbol, math (∑, ∫, ∇, …)
        'Sk',    # Symbol, modifier (˄, ˅, ˆ, …)
        'Sc',    # Symbol, currency
        'Co',    # Private use area
        'Cn',    # Unassigned
        'Cf',    # Format chars (ZWJ, ZWNJ, BOM)
    })
    _KEEP_CURRENCY = frozenset('$€£¥₹₽¢₩₪')

    _LATEX_BLOCK = re.compile(
        r'\\begin\{(equation|align|math|displaymath|gather|multline|array|matrix)\*?\}'
        r'.*?\\end\{\1\*?\}',
        re.DOTALL,
    )
    _LATEX_INLINE  = re.compile(r'\$\$.*?\$\$|\$[^\$\n]+\$|\\\(.*?\\\)|\\\[.*?\\\]', re.DOTALL)
    _CODE_FENCE    = re.compile(r'```.*?```|~~~.*?~~~', re.DOTALL)
    _CODE_INLINE   = re.compile(r'`[^`\n]+`')
    _URL           = re.compile(r'https?://\S+|www\.\S+|ftp://\S+')
    _FILE_PATH     = re.compile(r'(?:[A-Za-z]:\\|(?<=\s)/)[\w./\\-]{3,}')
    _CHEM_EQUATION = re.compile(
        r'\b\d*[A-Z][a-z]?\d*(?:\s*[+\-]\s*\d*[A-Z][a-z]?\d*)*'
        r'\s*(?:->|→|⇌|↔)\s*'
        r'\d*[A-Z][a-z]?\d*(?:\s*[+\-]\s*\d*[A-Z][a-z]?\d*)*'
    )
    _BARE_EQUATION = re.compile(
        r'(?:[A-Za-z]\w*|\d+(?:\.\d+)?)'
        r'(?:\s*[\(\)])?'
        r'\s*[=≠≈≤≥<>]+\s*'
        r'(?:[A-Za-z]\w*|\d+(?:\.\d+)?)'
        r'(?:\s*[+\-*/^]\s*(?:[A-Za-z]\w*|\d+(?:\.\d+)?))*'
    )
    _PLACEHOLDER_RE = re.compile(r'SMLZZ(\d+)ZZSML')

    def __init__(
        self,
        alpha_ratio:float = 0.75,
        min_words:int = 2,
        aggressive:bool = True,
        sml_pattern:Optional[re.Pattern] = None,
        lang:Optional[str] = None,
    )->None:
        '''
        alpha_ratio : min text-like density per sentence (0..1)
        min_words   : drop sentences with fewer alnum words (or chars*2 in
                      no-space scripts) than this
        aggressive  : also strip bare equations like 'x = y + 3'
        sml_pattern : compiled re.Pattern matching SML tags to preserve
        lang        : ISO-639-3 code, used only for no-space-script handling.
                      Math symbol preservation is global (see _MATH_KEEP).
        '''
        self.alpha_ratio = alpha_ratio
        self.min_words   = min_words
        self.aggressive  = aggressive
        self.sml_pattern = sml_pattern
        self.lang        = lang
        self._no_space   = lang in self._NO_SPACE_LANGS if lang else None

    def filter(self, text:str)->str:
        if not text:
            return ''

        tags:list = []
        if self.sml_pattern is not None:
            text = self._protect_tags(text, tags)

        text = self._LATEX_BLOCK.sub(' ', text)
        text = self._CODE_FENCE.sub(' ', text)
        text = self._LATEX_INLINE.sub(' ', text)
        text = self._CODE_INLINE.sub(' ', text)
        text = self._URL.sub(' ', text)
        text = self._FILE_PATH.sub(' ', text)
        text = self._CHEM_EQUATION.sub(' ', text)
        if self.aggressive:
            text = self._BARE_EQUATION.sub(' ', text)
        text = self._strip_unicode_math(text)
        text = self._EMOJI_RE.sub(' ', text)
        text = self._CHARS_REMOVE_RE.sub(' ', text)
        text = self._strip_special_chars(text)
        text = self._filter_sentences(text)

        if self.sml_pattern is not None:
            text = self._restore_tags(text, tags)
        return re.sub(r'\s+', ' ', text).strip()

    __call__ = filter

    def filter_many(self, texts:list)->list:
        return [self.filter(t) for t in texts]

    def _protect_tags(self, text:str, store:list)->str:
        def repl(m:re.Match)->str:
            idx = len(store)
            store.append(m.group(0))
            return f'SMLZZ{idx}ZZSML'
        return self.sml_pattern.sub(repl, text)

    def _restore_tags(self, text:str, store:list)->str:
        return self._PLACEHOLDER_RE.sub(lambda m: store[int(m.group(1))], text)

    def _strip_unicode_math(self, s:str)->str:
        ranges = self._MATH_UNICODE_RANGES
        keep   = self._MATH_KEEP
        return ''.join(
            ch for ch in s
            if ch in keep or not any(lo <= ord(ch) <= hi for lo, hi in ranges)
        )

    def _strip_special_chars(self, s:str)->str:
        keep_punct    = self._TEXT_PUNCT
        keep_currency = self._KEEP_CURRENCY
        keep_math     = self._MATH_KEEP
        bad_cats      = self._SPECIAL_CATEGORIES
        out:list = []
        for ch in s:
            if (ch.isspace() or ch.isalnum()
                    or ch in keep_punct
                    or ch in keep_currency
                    or ch in keep_math):
                out.append(ch)
                continue
            if unicodedata.category(ch) in bad_cats:
                out.append(' ')
            else:
                out.append(ch)
        return ''.join(out)

    @staticmethod
    def _is_mark(ch:str)->bool:
        # Mn/Mc/Me: combining vowel signs, viramas, nukta, anusvara, etc.
        # In abugida scripts (Devanagari, Bengali, Telugu, Tamil, Gujarati,
        # Kannada, …) these are integral letters of a syllable, not noise,
        # so they must count as prose in the text-density ratio.
        return unicodedata.category(ch)[0] == 'M'

    def _detect_no_space(self, s:str)->bool:
        ranges = self._NO_SPACE_RANGES
        sample = [c for c in s if not c.isspace() and not c.isascii()][:30]
        if not sample:
            return False
        hits = sum(
            1 for c in sample
            if any(lo <= ord(c) <= hi for lo, hi in ranges)
        )
        return hits / len(sample) > 0.5

    def _filter_sentences(self, text:str)->str:
        kept:list = []
        punct = self._TEXT_PUNCT
        no_space = (
            self._no_space if self._no_space is not None
            else self._detect_no_space(text)
        )
        for sent in self._SENT_SPLIT.split(text):
            s = sent.strip() if sent else ''
            if not s:
                continue
            non_space = [c for c in s if not c.isspace()]
            if not non_space:
                continue
            text_chars = sum(
                1 for c in non_space
                if c.isalpha() or c.isdigit() or c in punct
                or self._is_mark(c)
            )
            if text_chars / len(non_space) < self.alpha_ratio:
                continue
            if no_space:
                if not any(c.isalnum() for c in s):
                    continue
                if sum(1 for c in s
                       if c.isalnum() or self._is_mark(c)) < self.min_words * 2:
                    continue
            else:
                words = [w for w in re.split(r'\s+', s) if any(c.isalnum() for c in w)]
                if len(words) < self.min_words:
                    continue
            kept.append(s)
        return ' '.join(kept)
