"""Tests for keyword precision parsing and keyword-set version fingerprinting.

Regression coverage for two 2026-05 fixes:
  - parse_precision() used to return the *first* percentage in a YAML comment,
    publishing stale precision and sometimes audit-agreement figures.
  - tag_keywords.py now fingerprints the keyword set so a config change forces
    a full re-tag instead of silently skipping already-tagged posts.
"""

from scripts.export_keyword_details import parse_precision
from src.config import keyword_fingerprint


class TestParsePrecision:
    def test_single_value(self):
        assert parse_precision("98.0%, 104 hits") == 98.0

    def test_no_percentage(self):
        assert parse_precision("LOW VOLUME, not auditable") is None

    def test_takes_latest_precision_in_a_chain(self):
        # Chained re-measurements: the most recent precision is canonical.
        assert parse_precision("69.0% -> 87.0% (2026-04-23)") == 87.0

    def test_ignores_audit_agreement_after_number(self):
        # "85% audit agreement" is a different metric, not precision.
        assert parse_precision("92.0% (R1) -> 85% audit agreement") == 92.0

    def test_ignores_audit_agreement_before_number(self):
        assert parse_precision("100.0% -> audit 75% (2026-05-12).") == 100.0

    def test_ignores_audit_inside_parens(self):
        assert (
            parse_precision("100% -> 96.0% (2026-05-12 fresh; audit agreement 95%).")
            == 96.0
        )

    def test_audit_does_not_shadow_real_precision(self):
        assert parse_precision("89.0%, 340 hits. Audit agreement 85%.") == 89.0


def _cats(*pairs):
    """Build a minimal keyword_categories structure from (name, [terms])."""
    return [{"name": n, "terms": list(t)} for n, t in pairs]


class TestKeywordFingerprint:
    def test_deterministic(self):
        cats = _cats(("therapy", ["for therapy", "as a therapist"]))
        assert keyword_fingerprint(cats) == keyword_fingerprint(cats)

    def test_order_insensitive(self):
        a = _cats(("therapy", ["a", "b"]), ("romance", ["c"]))
        b = _cats(("romance", ["c"]), ("therapy", ["b", "a"]))
        assert keyword_fingerprint(a) == keyword_fingerprint(b)

    def test_added_term_changes_fingerprint(self):
        before = _cats(("therapy", ["a", "b"]))
        after = _cats(("therapy", ["a", "b", "c"]))
        assert keyword_fingerprint(before) != keyword_fingerprint(after)

    def test_renamed_category_changes_fingerprint(self):
        a = _cats(("therapy", ["a"]))
        b = _cats(("therapeutic", ["a"]))
        assert keyword_fingerprint(a) != keyword_fingerprint(b)
