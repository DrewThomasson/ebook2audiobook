"""English-specific TTS preprocessing. Only called when lang == 'eng'."""
import re
from num2words import num2words

YEAR_PREFIX_RE = re.compile(
    r'(?:'
    r'(?:(?:in|of|by|from|to|since|after|before|until|during|around|circa|year|early|late|mid)\s+)'
    r'|(?:(?:january|february|march|april|may|june|july|august|september|october|november|december'
    r'|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)[\s,]*)'
    r'|(?:\d{1,2},?\s+)'
    r')'
    r'((?:1[0-9]|20)[0-9]{2})\b',
    re.IGNORECASE
)

YEAR_DECADE_RE = re.compile(r'\b((?:1[0-9]|20)[0-9]{2})(?=s\b)', re.IGNORECASE)


def year2words_eng(year_str, lang_iso1, is_num2words_compat):
    """Handle XX00 ("nineteen hundred") and XX01-XX09 ("nineteen oh one").
    Returns None to fall through to default logic (e.g. round thousands).
    """
    if not is_num2words_compat:
        return None
    year = int(year_str)
    first_two = int(year_str[:2])
    last_two = int(year_str[2:])
    if last_two == 0:
        if year % 1000 == 0:
            return None
        return f'{num2words(first_two, lang=lang_iso1)} hundred'
    if last_two < 10:
        return f'{num2words(first_two, lang=lang_iso1)} oh {num2words(last_two, lang=lang_iso1)}'
    return None


def convert_years_in_context(text, lang, lang_iso1, is_num2words_compat, year2words_fn):
    """Replace years near English temporal keywords with spoken form."""
    def _repl(m):
        prefix = m.group(0)[:m.start(1) - m.start(0)]
        return prefix + year2words_fn(m.group(1), lang, lang_iso1, is_num2words_compat)

    text = YEAR_PREFIX_RE.sub(_repl, text)
    text = YEAR_DECADE_RE.sub(
        lambda m: year2words_fn(m.group(1), lang, lang_iso1, is_num2words_compat), text
    )
    return text
