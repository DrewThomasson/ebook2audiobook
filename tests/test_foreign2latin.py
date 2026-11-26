"""
Tests for foreign2latin() - specifically that hyphens inside compound words
are preserved without extra spaces being inserted (issue #2234).

The bug: foreign2latin() rebuilt spacing by tokenizing on word/sign boundaries
and adding a space before every word that followed a non-word sign, turning
"Peut-etre" into "Peut- etre" and "well-known" into "well- known".

The fix: romanize words in-place with re.sub, leaving everything between
them (hyphens, apostrophes, slashes, spaces) exactly as written.
"""
# conftest.py installs all the necessary stubs before this module is imported.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.core import foreign2latin


class TestForeign2LatinHyphens:
    """Hyphens inside compound words must survive foreign2latin unchanged."""

    def test_french_compound_peut_etre(self):
        # 'Peut-etre' must not become 'Peut- etre'
        result = foreign2latin('Peut-etre', 'fra')
        assert '- ' not in result, f"space inserted after hyphen: {result!r}"
        assert ' -' not in result, f"space inserted before hyphen: {result!r}"
        assert '-' in result, f"hyphen was removed: {result!r}"

    def test_french_compound_arc_en_ciel(self):
        result = foreign2latin('arc-en-ciel', 'fra')
        assert '- ' not in result, f"space after hyphen: {result!r}"
        assert ' -' not in result, f"space before hyphen: {result!r}"

    def test_french_inverted_verb_viens_tu(self):
        # 'Viens-tu ?' stays intact
        result = foreign2latin('Viens-tu ?', 'fra')
        assert '- ' not in result, f"space after hyphen: {result!r}"

    def test_english_hyphenated_well_known(self):
        result = foreign2latin('well-known', 'eng')
        assert result == 'well-known', f"unexpected: {result!r}"

    def test_english_email(self):
        result = foreign2latin('e-mail', 'eng')
        assert result == 'e-mail', f"unexpected: {result!r}"

    def test_slash_not_spaced(self):
        # and/or should not become "and/ or"
        result = foreign2latin('and/or', 'eng')
        assert '/ ' not in result, f"space after slash: {result!r}"

    def test_latin_words_unchanged(self):
        # Pure-latin text with no foreign chars passes through as-is
        text = 'Hello world.'
        result = foreign2latin(text, 'eng')
        assert result == text, f"unexpected change: {result!r}"

    def test_dialogue_dash_with_space(self):
        # Dialogue opening: '- Hello' already has a space, should not gain another
        result = foreign2latin('- Hello', 'fra')
        assert result == '- Hello', f"unexpected: {result!r}"
