"""The theme-page `drifting` chip (CLAUDE.md item 17c, 2026-11).

A keyword is marked drifting when its latest post-level re-check is below 60%
on at least DRIFT_FLAG_MIN_N matches. Smaller re-checks are still exported but
do not carry the chip.
"""

from scripts.export_keyword_details import (
    DRIFT_FLAG_BELOW,
    DRIFT_FLAG_MIN_N,
    is_drifting,
)


def test_below_line_with_enough_matches_is_drifting():
    assert is_drifting({"precision": 54.0, "n": 50})
    assert is_drifting({"precision": 59.1, "n": DRIFT_FLAG_MIN_N})


def test_small_rechecks_do_not_chip():
    assert not is_drifting({"precision": 54.5, "n": 11})   # memory wiped, Oct
    assert not is_drifting({"precision": 50.0, "n": 8})    # memory reset, Oct
    assert not is_drifting({"precision": 10.0, "n": DRIFT_FLAG_MIN_N - 1})


def test_at_or_above_the_line_is_not_drifting():
    assert not is_drifting({"precision": DRIFT_FLAG_BELOW * 100, "n": 50})
    assert not is_drifting({"precision": 82.0, "n": 50})


def test_missing_checks_are_not_drifting():
    assert not is_drifting(None)
    assert not is_drifting({})
    assert not is_drifting({"precision": None, "n": 50})
    assert not is_drifting({"precision": 40.0, "n": None})
