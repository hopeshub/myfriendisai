#!/usr/bin/env python3
"""Discipline check: every below-80% keyword in keywords_v8.yaml must have
one of three documented statuses (researcher-accepted, LOW VOLUME placeholder,
AUDIT-GATE FAIL). If a below-gate keyword is shipping without one of these
annotations, this script flags it.

Run after any keyword change:
    python3 analysis/keyword_pipeline/audit_keyword_status.py

Exit code 0 if clean, 1 if discipline gaps found.
"""

import re
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
KW_FILE = PROJECT_ROOT / "config" / "keywords_v8.yaml"


def keyword_line_precision(raw: str, kw: str):
    """Extract precision % from the single line where the keyword is defined."""
    for line in raw.splitlines():
        if re.match(rf'\s*-\s*("{re.escape(kw)}"|{re.escape(kw)})\s*(#|$)', line):
            if '#' not in line:
                return None
            comment = line.split('#', 1)[1]
            pcts = re.findall(r'(\d{1,3}(?:\.\d)?)\s*%', comment)
            return float(pcts[-1]) if pcts else None
    return None


def keyword_block(raw: str, kw: str) -> str:
    """Full annotation block including continuation comments."""
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf'\s*-\s*("{re.escape(kw)}"|{re.escape(kw)})\s*(#|$)', line):
            block = [line]
            for j in range(1, 12):
                if i + j >= len(lines):
                    break
                stripped = lines[i + j].strip()
                if stripped.startswith('#') and 'KEYWORD' not in stripped.upper():
                    block.append(lines[i + j])
                else:
                    break
            return '\n'.join(block)
    return ''


def has_status_annotation(block: str):
    statuses = []
    lower = block.lower()
    if 'researcher-accepted' in lower or 'researcher accepted' in lower:
        statuses.append('researcher-accepted')
    if 'LOW VOLUME' in block or ('low volume' in lower and 'placeholder' in lower):
        statuses.append('LOW VOLUME')
    if 'audit-gate fail' in lower or 'AUDIT-GATE FAIL' in block:
        statuses.append('AUDIT-GATE FAIL')
    return bool(statuses), statuses


def main():
    raw = KW_FILE.read_text()
    cfg = yaml.safe_load(raw)

    undocumented = []
    documented = []
    pass_keywords = 0

    for cat in cfg.get('keyword_categories', []):
        theme = cat['name']
        for kw in cat.get('terms', []):
            prec = keyword_line_precision(raw, kw)
            block = keyword_block(raw, kw)
            has_status, statuses = has_status_annotation(block)

            if prec is None:
                if not has_status:
                    undocumented.append((theme, kw, None, 'NO PRECISION + NO STATUS'))
                continue
            if prec >= 80:
                pass_keywords += 1
                continue
            if has_status:
                documented.append((theme, kw, prec, statuses))
            else:
                undocumented.append((theme, kw, prec, 'BELOW 80% WITHOUT STATUS'))

    print(f"Keyword status audit ({KW_FILE.name})")
    print("=" * 60)
    print(f"Pass (>=80% precision):            {pass_keywords:>3}")
    print(f"Below-gate with documented status: {len(documented):>3}")
    print(f"Below-gate UNDOCUMENTED:           {len(undocumented):>3}")
    print()

    if documented:
        print("Documented below-gate keywords (acceptable):")
        for theme, kw, prec, statuses in sorted(documented, key=lambda x: -x[2]):
            print(f"  {theme:<14} {kw:<28} {prec:>5.1f}%  [{', '.join(statuses)}]")
        print()

    if undocumented:
        print("DISCIPLINE GAP - undocumented below-gate keywords:")
        for theme, kw, prec, reason in undocumented:
            p = f"{prec:.1f}%" if prec is not None else '-'
            print(f"  {theme:<14} {kw:<28} {p:>6}  {reason}")
        print()
        print("Each undocumented keyword needs one of: 'researcher-accepted',")
        print("'LOW VOLUME placeholder', or 'AUDIT-GATE FAIL' in its inline annotation.")
        sys.exit(1)
    else:
        print("All below-gate keywords have documented status. Discipline maintained.")
        sys.exit(0)


if __name__ == "__main__":
    main()
