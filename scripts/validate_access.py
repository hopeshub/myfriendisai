#!/usr/bin/env python3
"""Validate that each subreddit in communities.yaml is accessible via .json endpoints.

Outputs a classification for each:
  sfw_accessible  — about.json returned data successfully
  nsfw_blocked    — 403 Forbidden (private or NSFW-gated)
  not_found       — 404 (subreddit doesn't exist)
  error           — Network or other error

Usage:
    python scripts/validate_access.py
    python scripts/validate_access.py --all-tiers   # include inactive communities too
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from src.reddit_client import RedditClient, SubredditNotFound, SubredditForbidden, RedditError
from src.utils.rate_limiter import RateLimiter

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

CONFIG_PATH = Path(__file__).parent.parent / "config" / "communities.yaml"

STATUS_LABELS = {
    "sfw_accessible": "✓ SFW accessible",
    "nsfw_blocked":   "✗ NSFW/private blocked",
    "not_found":      "✗ Not found (404)",
    "error":          "✗ Error",
}


def validate_all(communities: list[dict], client: RedditClient) -> list[dict]:
    results = []
    for c in communities:
        subreddit = c["subreddit"]
        print(f"  Checking r/{subreddit}...", end=" ", flush=True)
        result = {"subreddit": subreddit, "tier": c.get("tier"), "category": c.get("category")}

        try:
            about = client.get_about(subreddit)
            result["status"] = "sfw_accessible"
            result["subscribers"] = about.get("subscribers")
            result["over_18"] = about.get("over_18")
            print(f"ok ({about.get('subscribers') or 'N/A'} subscribers)")

        except SubredditForbidden:
            result["status"] = "nsfw_blocked"
            result["subscribers"] = None
            result["over_18"] = True
            print("BLOCKED (private or NSFW)")

        except SubredditNotFound:
            result["status"] = "not_found"
            result["subscribers"] = None
            result["over_18"] = None
            print("NOT FOUND")

        except RedditError as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["subscribers"] = None
            result["over_18"] = None
            print(f"ERROR: {e}")

        results.append(result)

    return results


def print_report(results: list[dict]):
    accessible = [r for r in results if r["status"] == "sfw_accessible"]
    blocked = [r for r in results if r["status"] == "nsfw_blocked"]
    not_found = [r for r in results if r["status"] == "not_found"]
    errors = [r for r in results if r["status"] == "error"]

    print(f"\n{'='*60}")
    print(f"ACCESS VALIDATION REPORT ({len(results)} subreddits checked)")
    print(f"{'='*60}")
    print(f"  Accessible:   {len(accessible)}")
    print(f"  Blocked:      {len(blocked)}")
    print(f"  Not found:    {len(not_found)}")
    print(f"  Errors:       {len(errors)}")

    if blocked:
        print("\nNSFW/BLOCKED — route through Redlib or Arctic Shift:")
        for r in blocked:
            print(f"  r/{r['subreddit']} (Tier {r['tier']}, {r['category']})")

    if not_found:
        print("\nNOT FOUND — remove from config or verify subreddit name:")
        for r in not_found:
            print(f"  r/{r['subreddit']}")

    if errors:
        print("\nERRORS:")
        for r in errors:
            print(f"  r/{r['subreddit']}: {r.get('error')}")

    print("\nACCESSIBLE:")
    for r in accessible:
        subs = f"{r['subscribers']:,}" if r.get("subscribers") else "N/A"
        nsfw_flag = " [over_18]" if r.get("over_18") else ""
        print(f"  r/{r['subreddit']}: {subs} subscribers{nsfw_flag}")


def main():
    parser = argparse.ArgumentParser(description="Validate subreddit access via .json endpoints")
    parser.add_argument("--all-tiers", action="store_true", help="Include inactive communities")
    args = parser.parse_args()

    with open(CONFIG_PATH) as f:
        data = yaml.safe_load(f)
    communities = data.get("communities", [])
    if not args.all_tiers:
        communities = [c for c in communities if c.get("is_active", True)]

    print(f"Validating {len(communities)} subreddit(s)...")
    print("(using 3s between requests for faster validation)\n")

    client = RedditClient(rate_limiter=RateLimiter(min_interval=3.0))
    results = validate_all(communities, client)
    print_report(results)

    blocked_or_missing = [r for r in results if r["status"] in ("nsfw_blocked", "not_found", "error")]
    return 1 if blocked_or_missing else 0


if __name__ == "__main__":
    sys.exit(main())
