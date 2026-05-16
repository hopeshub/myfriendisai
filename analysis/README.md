# analysis/

Tooling for the keyword-validation pipeline — the scripts that build samples,
score keyword precision, and watch for keyword meaning-drift over time.

The raw artifacts of individual validation runs (batch files, classifier
output, per-keyword post samples) are kept locally but not committed: they are
intermediate working files, not results. The conclusions of every run are
written up in [`docs/`](../docs/) — see the `validation_*`, `*_audit_*`, and
`keyword_*` reports there, and the methodology summary on the
[About page](https://myfriendisai.com/about).

`keyword_pipeline/` holds the current scripts; `audit_keyword_status.py`
checks that every below-threshold keyword in the keyword config carries a
documented status.
