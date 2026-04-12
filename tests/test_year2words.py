import os
import sys

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

os.chdir(PROJECT_ROOT)
from lib.conf_lang import default_language_code, language_math_phonemes  # noqa: E402
from lib.lang_eng import convert_years_in_context  # noqa: E402
from num2words import num2words  # noqa: E402


# Stub of year2words matching lib/core.py logic — delegates English cases to lang_eng
from lib.lang_eng import year2words_eng  # noqa: E402


def year2words(year_str, lang, lang_iso1, is_num2words_compat):
    try:
        year = int(year_str)
        first_two = int(year_str[:2])
        last_two = int(year_str[2:])
        lang_iso1 = lang_iso1 if lang in language_math_phonemes.keys() else default_language_code
        lang_iso1 = lang_iso1.replace('zh', 'zh_CN')
        if not year_str.isdigit() or len(year_str) != 4:
            if is_num2words_compat:
                return num2words(year, lang=lang_iso1)
            else:
                return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in year_str)
        if lang == 'eng' and last_two < 10:
            eng_result = year2words_eng(year_str, lang_iso1, is_num2words_compat)
            if eng_result is not None:
                return eng_result
        if last_two < 10:
            if is_num2words_compat:
                return num2words(year, lang=lang_iso1)
            else:
                return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in year_str)
        if is_num2words_compat:
            return f'{num2words(first_two, lang=lang_iso1)} {num2words(last_two, lang=lang_iso1)}'
        else:
            return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in first_two) + ' ' + ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in last_two)
    except Exception as e:
        print(f'year2words() error: {e}')
        return False


# year test case
YEAR_CASES_ENGLISH = [
    # Standard years — split into two halves
    ("1776", "seventeen seventy-six"),
    ("1848", "eighteen forty-eight"),
    ("1917", "nineteen seventeen"),
    ("1949", "nineteen forty-nine"),
    ("1978", "nineteen seventy-eight"),
    ("1985", "nineteen eighty-five"),
    ("1989", "nineteen eighty-nine"),
    ("1992", "nineteen ninety-two"),
    ("1997", "nineteen ninety-seven"),
    ("1999", "nineteen ninety-nine"),
    ("2010", "twenty ten"),
    ("2020", "twenty twenty"),
    ("2024", "twenty twenty-four"),

    # XX01–XX09 — "oh" form
    ("1805", "eighteen oh five"),
    ("1901", "nineteen oh one"),
    ("1904", "nineteen oh four"),
    ("2001", "twenty oh one"),
    ("2009", "twenty oh nine"),

    # XX00 — "hundred" form
    ("1100", "eleven hundred"),
    ("1200", "twelve hundred"),
    ("1300", "thirteen hundred"),
    ("1500", "fifteen hundred"),
    ("1700", "seventeen hundred"),
    ("1800", "eighteen hundred"),
    ("1900", "nineteen hundred"),

    # Round thousands — cardinal form
    ("1000", "one thousand"),
    ("2000", "two thousand"),
]


@pytest.mark.parametrize(
    "year_str,expected",
    YEAR_CASES_ENGLISH,
    ids=[c[0] for c in YEAR_CASES_ENGLISH],
)
def test_year2words_english(year_str, expected):
    result = year2words(year_str, lang="eng", lang_iso1="en", is_num2words_compat=True)
    assert result == expected


# context words indicating years
CONTEXT_CASES_ENGLISH = [
    ("in 1978", "in nineteen seventy-eight"),
    ("by 1985", "by nineteen eighty-five"),
    ("from 1949", "from nineteen forty-nine"),
    ("since 1992", "since nineteen ninety-two"),
    ("after 1976", "after nineteen seventy-six"),
    ("before 1949", "before nineteen forty-nine"),
    ("until 1997", "until nineteen ninety-seven"),
    ("during 1989", "during nineteen eighty-nine"),
    ("around 1920", "around nineteen twenty"),
    ("early 1989", "early nineteen eighty-nine"),
    ("late 1776", "late seventeen seventy-six"),
    ("January 1985", "January nineteen eighty-five"),
    ("June 1989", "June nineteen eighty-nine"),
    ("Dec 2020", "Dec twenty twenty"),
    ("June 4, 1989", "June 4, nineteen eighty-nine"),
    ("August 22, 1904", "August 22, nineteen oh four"),
    ("the 1980s", "the nineteen eightys"),
    ("the 1850s", "the eighteen fiftys"),
    ("the 2010s", "the twenty tens"),
    ("he had 1500 troops", "he had 1500 troops"),
]


@pytest.mark.parametrize(
    "input_text,expected",
    CONTEXT_CASES_ENGLISH,
    ids=[c[0] for c in CONTEXT_CASES_ENGLISH],
)
def test_convert_years_in_context(input_text, expected):
    result = convert_years_in_context(
        input_text, lang="eng", lang_iso1="en",
        is_num2words_compat=True, year2words_fn=year2words,
    )
    assert result == expected
