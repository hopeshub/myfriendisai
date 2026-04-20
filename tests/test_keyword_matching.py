"""Tests for src/keyword_matching.py — the core regex engine behind every theme."""

from src.keyword_matching import build_patterns, match_text


SAMPLE_CATEGORIES = [
    {"name": "therapy", "terms": ["therapist", "emotional support"]},
    {"name": "romance", "terms": ["my boyfriend", "my girlfriend"]},
    {"name": "rupture", "terms": ["lobotomized", "nerfed"]},
]


def test_build_patterns_returns_one_entry_per_term():
    patterns = build_patterns(SAMPLE_CATEGORIES)
    assert len(patterns) == 6
    names = [p[0] for p in patterns]
    assert names.count("therapy") == 2
    assert names.count("romance") == 2
    assert names.count("rupture") == 2


def test_single_word_uses_word_boundary():
    patterns = build_patterns([{"name": "t", "terms": ["therapist"]}])
    assert match_text("my therapist said", patterns) == [("t", "therapist")]
    # Substring inside a longer word should not match
    assert match_text("therapistical", patterns) == []


def test_multi_word_phrase_uses_word_boundary():
    patterns = build_patterns([{"name": "r", "terms": ["my boyfriend"]}])
    assert match_text("I told my boyfriend about it", patterns) == [("r", "my boyfriend")]
    assert match_text("with my boyfriend!", patterns) == [("r", "my boyfriend")]


def test_multi_word_phrase_not_matched_as_substring():
    # Regression: multi-word terms were previously compiled without \b boundaries,
    # which made "dating my" match "updating my" / "validating my" inside other
    # words. Word boundaries on both sides prevent this.
    patterns = build_patterns([{"name": "r", "terms": ["dating my"]}])
    assert match_text("I've been dating my AI", patterns) == [("r", "dating my")]
    assert match_text("updating my profile", patterns) == []
    assert match_text("validating my feelings", patterns) == []
    assert match_text("invalidating my point", patterns) == []


def test_match_is_case_insensitive():
    patterns = build_patterns([{"name": "t", "terms": ["therapist"]}])
    assert match_text("My Therapist Said", patterns) == [("t", "therapist")]
    assert match_text("MY THERAPIST SAID", patterns) == [("t", "therapist")]


def test_empty_text_returns_no_matches():
    patterns = build_patterns(SAMPLE_CATEGORIES)
    assert match_text("", patterns) == []
    assert match_text(None, patterns) == []


def test_deduplication_same_term_matches_once():
    patterns = build_patterns([{"name": "t", "terms": ["therapist"]}])
    # Two occurrences should produce only one match entry
    result = match_text("therapist and therapist again", patterns)
    assert result == [("t", "therapist")]


def test_multiple_terms_across_categories():
    patterns = build_patterns(SAMPLE_CATEGORIES)
    text = "my therapist and my boyfriend both think I'm being lobotomized"
    result = match_text(text, patterns)
    assert ("therapy", "therapist") in result
    assert ("romance", "my boyfriend") in result
    assert ("rupture", "lobotomized") in result
    assert len(result) == 3


def test_regex_special_chars_are_escaped():
    # A term with regex metacharacters should be treated literally
    patterns = build_patterns([{"name": "t", "terms": ["a.b"]}])
    assert match_text("a.b matches", patterns) == [("t", "a.b")]
    # Regex-style wildcard should NOT match "axb" since . is escaped
    assert match_text("axb should not match", patterns) == []


def test_word_boundary_handles_punctuation():
    patterns = build_patterns([{"name": "t", "terms": ["nerfed"]}])
    assert match_text("It was nerfed.", patterns) == [("t", "nerfed")]
    assert match_text("Nerfed!", patterns) == [("t", "nerfed")]
    assert match_text("(nerfed)", patterns) == [("t", "nerfed")]
