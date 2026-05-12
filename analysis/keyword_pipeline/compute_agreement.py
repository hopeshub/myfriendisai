#!/usr/bin/env python3
"""Compute per-keyword inter-rater agreement between primary and audit classifications.

Reads the primary classification file (output of Workflow 2) and the audit file
(output of Workflow 4) and produces:

  1. Per-keyword agreement rate (% of audit posts where audit label == primary label)
  2. List of disagreements with post number, primary call, audit call, both reasons
  3. Aggregated FP-pattern detection (audit-stricter disagreements grouped by keyword)

Usage:
    python compute_agreement.py \\
        --primary results/classified_batch_emotional_loss_2026-05-12.txt \\
        --audit   results/audit_batch_emotional_loss_2026-05-12.txt

Expected input formats:

  Primary (per parse_batch.py expectations):
    ## KEYWORD: heartbroken → Rupture
    1. YES  # reason
    2. NO   # reason
    ...
    100. YES  # reason
    PRECISION: 76/100 = 76%

  Audit (per Workflow 4):
    ## AUDIT: heartbroken → Rupture
    5. YES  # reason
    10. YES  # reason
    ...
    100. NO  # reason
    AGREEMENT_CHECK: classified 20 posts
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


SECTION_PATTERN = re.compile(r'^##\s*(?:KEYWORD|AUDIT):\s*(.+?)\s*→\s*(.+?)\s*$', re.MULTILINE)
LINE_PATTERN = re.compile(r'^(\d+)\.\s+(YES|NO)\b\s*(?:#\s*(.*))?$')


def parse_sections(filepath):
    """Parse a classification file into {keyword: {post_num: (label, reason)}}.

    Works for both primary (## KEYWORD: ...) and audit (## AUDIT: ...) formats.
    """
    text = Path(filepath).read_text()
    sections = {}
    current_keyword = None
    current_labels = {}

    for line in text.splitlines():
        m = SECTION_PATTERN.match(line)
        if m:
            if current_keyword:
                sections[current_keyword] = current_labels
            current_keyword = m.group(1).strip()
            current_labels = {}
            continue

        m = LINE_PATTERN.match(line)
        if m and current_keyword:
            post_num = int(m.group(1))
            label = m.group(2)
            reason = (m.group(3) or "").strip()
            current_labels[post_num] = (label, reason)

    if current_keyword:
        sections[current_keyword] = current_labels

    return sections


def compute_agreement(primary, audit):
    """Per-keyword agreement rate + disagreement records."""
    summary = []
    disagreements_by_keyword = defaultdict(list)

    for keyword, audit_labels in audit.items():
        primary_labels = primary.get(keyword, {})
        agree = 0
        total = 0
        for post_num, (audit_label, audit_reason) in audit_labels.items():
            if post_num not in primary_labels:
                continue
            total += 1
            primary_label, primary_reason = primary_labels[post_num]
            if audit_label == primary_label:
                agree += 1
            else:
                disagreements_by_keyword[keyword].append({
                    'post': post_num,
                    'primary': primary_label,
                    'primary_reason': primary_reason,
                    'audit': audit_label,
                    'audit_reason': audit_reason,
                })
        rate = (agree / total) if total else 0.0
        summary.append({
            'keyword': keyword,
            'agree': agree,
            'total': total,
            'rate': rate,
        })

    return summary, dict(disagreements_by_keyword)


def main():
    parser = argparse.ArgumentParser(description="Compute per-keyword audit agreement.")
    parser.add_argument("--primary", required=True, help="Primary classification file")
    parser.add_argument("--audit", required=True, help="Audit classification file")
    parser.add_argument("--show-disagreements", action="store_true",
                        help="Print full disagreement records")
    args = parser.parse_args()

    primary = parse_sections(args.primary)
    audit = parse_sections(args.audit)

    if not audit:
        print(f"ERROR: no audit sections found in {args.audit}", file=sys.stderr)
        sys.exit(1)

    summary, disagreements = compute_agreement(primary, audit)

    # Summary table
    print(f"{'keyword':<22} {'audit':>6}  {'rate':>5}  audit n  primary n")
    print('-' * 70)
    audit_n = {k: len(v) for k, v in audit.items()}
    primary_n = {k: len(v) for k, v in primary.items()}
    for row in summary:
        kw = row['keyword']
        flag = ''
        if row['rate'] < 0.85:
            flag = '  ← below 85% agreement gate'
        print(f"{kw:<22} {row['agree']:>3}/{row['total']:<2}  "
              f"{row['rate']*100:>4.0f}%  {audit_n.get(kw,0):>6}  {primary_n.get(kw,0):>9}{flag}")

    # Disagreement detail
    if args.show_disagreements:
        print()
        print('=' * 70)
        print('DISAGREEMENTS')
        print('=' * 70)
        for kw, recs in disagreements.items():
            print(f"\n{kw}:")
            for r in recs:
                print(f"  Post {r['post']}: primary {r['primary']} ({r['primary_reason']}) "
                      f"| audit {r['audit']} ({r['audit_reason']})")
    else:
        # Always print one-line disagreement summary
        print()
        for kw, recs in disagreements.items():
            patterns = defaultdict(int)
            for r in recs:
                # Naive pattern key: audit's reason as the categorizer
                patterns[r['audit_reason']] += 1
            top_pattern = max(patterns.items(), key=lambda x: x[1]) if patterns else None
            if top_pattern and top_pattern[1] >= 3:
                print(f"  {kw}: {len(recs)} disagreements; ≥3 share pattern: \"{top_pattern[0]}\" — investigate rubric gap")
            elif recs:
                print(f"  {kw}: {len(recs)} disagreements (no dominant pattern)")

    # Exit code reflects gate
    failures = [r for r in summary if r['rate'] < 0.85]
    if failures:
        sys.exit(2)


if __name__ == "__main__":
    main()
