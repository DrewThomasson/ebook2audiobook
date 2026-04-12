"""English-specific text-to-speech preprocessing.

Handles year detection heuristics that rely on English keywords
(temporal prepositions, month names, etc.). Only called when
the conversion language is English.
"""
import re

# Matches 4-digit years (1000-2099) preceded by English temporal context
YEAR_PREFIX_RE = re.compile(
    r'(?:'
    r'(?:(?:in|of|by|from|to|since|after|before|until|during|around|circa|year|early|late|mid)'
    r'\s+)'                                         # temporal keyword + space
    r'|(?:(?:january|february|march|april|may|june|july|august|september|october|november|december'
    r'|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)'
    r'[\s,]*)'                                      # month name + optional comma/space
    r'|(?:\d{1,2},?\s+)'                            # day number ("15, " or "15 ")
    r')'
    r'((?:1[0-9]|20)[0-9]{2})\b',
    re.IGNORECASE
)

# Matches decade references like "1980s", "2010s"
YEAR_DECADE_RE = re.compile(
    r'\b((?:1[0-9]|20)[0-9]{2})(?=s\b)',
    re.IGNORECASE
)


def convert_years_in_context(text, lang, lang_iso1, is_num2words_compat, year2words_fn):
    """Replace years detected by English keyword heuristics with spoken form.

    Args:
        text: Input text to process.
        lang: ISO-639-3 language code (e.g. "eng").
        lang_iso1: ISO-639-1 language code (e.g. "en").
        is_num2words_compat: Whether num2words supports this language.
        year2words_fn: The year2words function from core.py.

    Returns:
        Text with contextually detected years converted to words.
    """
    def _ctx_year_repl(m):
        return m.group(0)[:m.start(1) - m.start(0)] + year2words_fn(m.group(1), lang, lang_iso1, is_num2words_compat)

    text = YEAR_PREFIX_RE.sub(_ctx_year_repl, text)
    text = YEAR_DECADE_RE.sub(
        lambda m: year2words_fn(m.group(1), lang, lang_iso1, is_num2words_compat), text
    )
    return text
