"""corpus_composition.py takes its window from the calendar and its
per-theme start months from the published export, not hard-coded values."""

import json
from datetime import datetime, timezone

from analysis.keyword_pipeline import corpus_composition as cc


def test_last_complete_month_is_the_month_before():
    assert cc.last_complete_month(datetime(2026, 11, 20, tzinfo=timezone.utc)) == "2026-10"
    assert cc.last_complete_month(datetime(2027, 1, 3, tzinfo=timezone.utc)) == "2026-12"


def test_coverage_start_reads_the_export(tmp_path):
    p = tmp_path / "kt.json"
    p.write_text(json.dumps({"_coverage_start": {t: "2024-03-01" for t in cc.THEMES}}))
    assert cc.load_coverage_start(p) == {t: "2024-03" for t in cc.THEMES}


def test_coverage_start_falls_back_when_unreadable(tmp_path):
    assert cc.load_coverage_start(tmp_path / "missing.json") == cc._COVERAGE_START_FALLBACK
