#!/usr/bin/env bash
# Post-backfill orchestrator. Run after the LLM backfill completes.
#
# Steps:
#  1. Retry pass for any lock-failed items (idempotent — skips classified).
#  2. Regenerate exports (keyword_trends.json + theme_health.json + verification_examples.json).
#  3. Copy to web/data.
#  4. Print the report summary.
#
# Does NOT: dispatch the calibration agent, parse calibration results, or
# flip the chart default. Those steps are Claude's responsibility (they
# require Agent tool calls and decision logic in conversation context).
#
# Usage:
#   set -a && source .env && set +a
#   bash scripts/run_overnight.sh

set -uo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ERROR: ANTHROPIC_API_KEY not set. Source .env first."
  exit 1
fi

VENV=".venv/bin/python"

echo "=== Step 1: retry pass (catches lock-failed items) ==="
# Build the full keyword list and re-run; idempotency skips done items.
KW=$($VENV -c "
from src.config import load_keywords
print(','.join(t for cat in load_keywords() for t in cat['terms']))
")
$VENV scripts/llm_verify_tags.py backfill --keywords "$KW" --surface both 2>&1 | tail -15

echo ""
echo "=== Step 2: regenerate exports ==="
$VENV -c "
from src.db.operations import export_keyword_trends_json, export_theme_health_json
export_keyword_trends_json()
export_theme_health_json()
print('keyword_trends.json + theme_health.json regenerated')
"

echo ""
echo "=== Step 3: build verification examples ==="
$VENV scripts/export_verification_examples.py

echo ""
echo "=== Step 4: copy data/ -> web/data/ ==="
cp data/keyword_trends.json web/data/keyword_trends.json
cp data/theme_health.json web/data/theme_health.json
cp data/verification_examples.json web/data/verification_examples.json 2>/dev/null || true
echo "Done."

echo ""
echo "=== Step 5: LLM verdict report (Haiku only) ==="
$VENV scripts/llm_verify_tags.py report --model claude-haiku-4-5-20251001 2>&1 | head -30
