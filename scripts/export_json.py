#!/usr/bin/env python3
"""Export frontend-ready JSON files from tracker.db.

Regenerates data/*.json and copies them to web/data/ for Vercel builds.
No data collection — just reads the DB and writes JSON.

Usage:
    python scripts/export_json.py
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.schema import initialize as init_db
from src.db.operations import aggregate_posts_to_snapshots, export_snapshots_json, export_subreddits_json, export_keyword_trends_json
from src.keyword_scanner import export_keywords_json

WEB_DATA_DIR = Path(__file__).parent.parent / "web" / "data"


def main():
    conn = init_db()

    inserted = aggregate_posts_to_snapshots(conn=conn)
    print(f"Aggregated posts → {inserted} new snapshot rows inserted (data_source='arctic_shift')")

    snap_path = export_snapshots_json(conn=conn)
    print(f"Exported {snap_path}")

    sub_path = export_subreddits_json(conn=conn)
    print(f"Exported {sub_path}")

    kw_path = export_keywords_json(conn=conn)
    print(f"Exported {kw_path}")

    trends_path = export_keyword_trends_json(conn=conn)
    print(f"Exported {trends_path}")

    conn.close()

    # Copy to web/data/ for Vercel
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for src in (snap_path, sub_path, kw_path, trends_path):
        dst = WEB_DATA_DIR / src.name
        shutil.copy2(src, dst)
        print(f"Copied to {dst}")

    print("Done.")


if __name__ == "__main__":
    main()
