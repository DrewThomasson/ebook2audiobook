"""Tests for English year pronunciation."""
import os, sys
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from lib.core import year2words  # noqa: E402
from lib.lang_eng import convert_years_in_context  # noqa: E402


def _y(year_str):
    return year2words(year_str, lang="eng", lang_iso1="en", is_num2words_compat=True)


# fmt: off
YEAR_CASES = [
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
    # XX01-XX09
    ("1805", "eighteen oh five"),
    ("1901", "nineteen oh one"),
    ("1904", "nineteen oh four"),
    ("2001", "twenty oh one"),
    ("2009", "twenty oh nine"),
    # XX00
    ("1100", "eleven hundred"),
    ("1200", "twelve hundred"),
    ("1300", "thirteen hundred"),
    ("1500", "fifteen hundred"),
    ("1700", "seventeen hundred"),
    ("1800", "eighteen hundred"),
    ("1900", "nineteen hundred"),
    # Round thousands
    ("1000", "one thousand"),
    ("2000", "two thousand"),
]

CONTEXT_CASES = [
    ("in 1978",             "in nineteen seventy-eight"),
    ("by 1985",             "by nineteen eighty-five"),
    ("from 1949",           "from nineteen forty-nine"),
    ("since 1992",          "since nineteen ninety-two"),
    ("after 1976",          "after nineteen seventy-six"),
    ("before 1949",         "before nineteen forty-nine"),
    ("until 1997",          "until nineteen ninety-seven"),
    ("during 1989",         "during nineteen eighty-nine"),
    ("around 1920",         "around nineteen twenty"),
    ("early 1989",          "early nineteen eighty-nine"),
    ("late 1776",           "late seventeen seventy-six"),
    ("January 1985",        "January nineteen eighty-five"),
    ("June 1989",           "June nineteen eighty-nine"),
    ("Dec 2020",            "Dec twenty twenty"),
    ("June 4, 1989",        "June 4, nineteen eighty-nine"),
    ("August 22, 1904",     "August 22, nineteen oh four"),
    ("the 1980s",           "the nineteen eightys"),
    ("the 1850s",           "the eighteen fiftys"),
    ("the 2010s",           "the twenty tens"),
    ("he had 1500 troops",  "he had 1500 troops"),
]
# fmt: on


@pytest.mark.parametrize("year_str,expected", YEAR_CASES, ids=[c[0] for c in YEAR_CASES])
def test_year2words(year_str, expected):
    assert _y(year_str) == expected


@pytest.mark.parametrize("text,expected", CONTEXT_CASES, ids=[c[0] for c in CONTEXT_CASES])
def test_context_detection(text, expected):
    result = convert_years_in_context(text, "eng", "en", True, year2words)
    assert result == expected
