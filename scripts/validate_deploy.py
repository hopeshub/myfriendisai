#!/usr/bin/env python3
"""Pre-deploy validation: checks data files and frontend build before pushing.

Run manually or called by push_and_deploy.sh. Exits non-zero if any check fails.

Usage:
    python scripts/validate_deploy.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
FAIL = False


def check(name, passed, detail=""):
    global FAIL
    status = "✓" if passed else "✗"
    msg = f"  {status} {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    if not passed:
        FAIL = True


def main():
    print("=" * 60)
    print("Pre-deploy validation")
    print("=" * 60)

    # ── 1. Data files exist and are valid JSON ──
    print("\n1. Data files")
    data_files = [
        "data/keyword_trends.json",
        "data/snapshots.json",
        "data/subreddits.json",
    ]
    # Only validate web copies for files that are actually deployed to the frontend
    web_copies = [f"web/data/{Path(f).name}" for f in data_files]

    for f in data_files + web_copies:
        path = ROOT / f
        if not path.exists():
            check(f, False, "missing")
            continue
        try:
            data = json.loads(path.read_text())
            size_kb = path.stat().st_size / 1024
            check(f, True, f"{size_kb:.0f} KB")
        except json.JSONDecodeError as e:
            check(f, False, f"invalid JSON: {e}")

    # ── 2. keyword_trends.json structure ──
    print("\n2. Keyword trends structure")
    kt_path = ROOT / "data/keyword_trends.json"
    if kt_path.exists():
        kt = json.loads(kt_path.read_text())

        expected_themes = ["therapy", "consciousness", "addiction", "romance", "sexual_erp", "rupture"]
        for theme in expected_themes:
            entries = kt.get(theme, [])
            check(f"{theme} theme", len(entries) > 100, f"{len(entries)} entries")
            if entries:
                sample = entries[-1]
                has_fields = all(k in sample for k in ["date", "count"])
                check(f"  has required fields", has_fields, str(list(sample.keys())))

        total_posts = kt.get("_total_posts", [])
        check("_total_posts exists", len(total_posts) > 100, f"{len(total_posts)} entries")

        # Check for anomalous values
        if total_posts:
            counts = [e["count"] for e in total_posts[-90:]]
            median = sorted(counts)[len(counts) // 2]
            outliers = [e for e in total_posts[-30:] if e["count"] > median * 4]
            check("no recent post count outliers", len(outliers) == 0,
                  f"{len(outliers)} days > 4x median ({median})" if outliers else f"median={median}")

            zeros = [e for e in total_posts[-30:] if e["count"] == 0]
            check("no zero-count days (last 30)", len(zeros) == 0,
                  f"{len(zeros)} zero days" if zeros else "")

    # ── 3. snapshots.json structure ──
    print("\n3. Snapshots")
    snap_path = ROOT / "data/snapshots.json"
    if snap_path.exists():
        snaps = json.loads(snap_path.read_text())
        subs = set(s["subreddit"] for s in snaps)
        dates = set(s["snapshot_date"] for s in snaps)
        check("has subreddits", len(subs) >= 20, f"{len(subs)} subreddits")
        check("has date range", len(dates) > 100, f"{len(dates)} dates")

        # Check for recent data
        latest_date = max(dates)
        from datetime import date, timedelta
        stale_cutoff = (date.today() - timedelta(days=3)).isoformat()
        check("data is fresh", latest_date >= stale_cutoff, f"latest={latest_date}")

    # ── 4. subreddits.json ──
    print("\n4. Subreddits")
    sub_path = ROOT / "data/subreddits.json"
    if sub_path.exists():
        subs = json.loads(sub_path.read_text())
        check("has subreddits", len(subs) >= 20, f"{len(subs)} entries")

        # Check for case duplicates
        names = [s["subreddit"] for s in subs]
        lower_names = [n.lower() for n in names]
        dupes = len(lower_names) - len(set(lower_names))
        check("no case-duplicate subreddits", dupes == 0,
              f"{dupes} duplicates" if dupes else "")

    # ── 5. web/data matches data/ ──
    print("\n5. Web data copies match source")
    for f in data_files:
        src = ROOT / f
        dst = ROOT / f"web/data/{Path(f).name}"
        if src.exists() and dst.exists():
            match = src.read_bytes() == dst.read_bytes()
            check(f"{Path(f).name}", match, "mismatch!" if not match else "")

    # ── 6. Frontend builds ──
    print("\n6. Frontend build")
    import subprocess
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=ROOT / "web",
        capture_output=True,
        text=True,
        timeout=120,
    )
    check("next.js build", result.returncode == 0,
          result.stderr.strip().split("\n")[-1] if result.returncode != 0 else "ok")

    # ── Summary ──
    print("\n" + "=" * 60)
    if FAIL:
        print("VALIDATION FAILED — do not deploy")
        return 1
    else:
        print("All checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
