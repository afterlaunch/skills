#!/usr/bin/env python3
"""The near-duplicate gate: is this draft too close to anything we posted or
drafted in the last N hours?

Why it exists. r/AISearchLab rule 6: "posting the same or almost the same
comment in more than one thread within 24 h is spam", a 7-day ban, then
permanent. Rule 5 of r/SaaS, Bot Bouncer and Scan Slop catch the same shape
site-wide. So a cross-thread near-duplicate is a BAN risk, not a style note,
and a mention counter cannot see it. This does.

It is a token-overlap (Jaccard) check over the draft bodies in drafts/*.md
and the ledger's "What was posted" column, windowed by date. Pure, offline,
deterministic. It flags; a session decides. A flag means "read both before
posting", never "rewrite automatically".

Usage:
    python3 neardup.py < draft.txt
    python3 neardup.py --hours 48 < draft.txt
    python3 neardup.py --file drafts/2026-08-28.md   # check every draft in a file against the others

Exit 0 = clear, 1 = at least one near-duplicate flagged, 2 = usage.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(os.environ.get('REDDIT_DESK') or Path.home() / '.claude' / 'content' / 'reddit').resolve()
THRESHOLD = 0.6  # conservative: only substantially-the-same text collapses

STOP = set('the a an and or of to in on for with is are was were be been it this that as at by from you your we our they their if not but so than then there here what which who how'.split())


def tokens(text: str) -> set[str]:
    words = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).split()
    return {w for w in words if w not in STOP and len(w) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


MIN_WORDS = 20  # below this a block is a note, not a comment


def bodies_in(text: str, name: str) -> list[tuple[str, str]]:
    """(label, body) for every draft in one file. Two shapes are read, because
    the estate carries both: a '### Text' block (2026-08-28 onwards), and a
    '## A. r/sub, "title"' section whose comment is the blockquoted lines
    (2026-08-22). A section with neither, such as a mod email, is not a
    comment and is skipped."""
    out: list[tuple[str, str]] = []
    n = 0
    for section in re.split(r'^## ', text, flags=re.M)[1:]:
        # A '### Text' heading may carry a suffix ("### Text as loaded (v2)"),
        # which is exactly how the one LIVE, unsent draft was labelled on
        # 2026-08-28; an exact-line match silently skipped it (QA, 2026-08-30).
        # Anchor on the heading's start, not its whole line.
        text_blocks = re.split(r'^### Text\b.*$', section, flags=re.M)[1:]
        if text_blocks:
            for block in text_blocks:
                body = re.split(r'^---\s*$', block, maxsplit=1, flags=re.M)[0].strip()
                if len(body.split()) >= MIN_WORDS:
                    n += 1
                    out.append((f'{name} draft {n}', body))
            continue
        # The blockquote shape (2026-08-22) is a draft only where the section
        # carries a draft marker; a blockquote elsewhere is something we QUOTED
        # (a sub's rule, a mod's words), not something we wrote, and treating it
        # as ours produced a false "draft" out of a quoted rule (QA, 2026-08-30).
        heading = section.split('\n', 1)[0]
        if not (re.match(r'(?:[A-Z]\.\s+r/|Draft\b)', heading) or re.search(r'\b(Claims used|Product):', section)):
            continue
        quoted = [ln[2:] if ln.startswith('> ') else '' for ln in section.splitlines() if ln.startswith('>')]
        body = '\n'.join(quoted).strip()
        if len(body.split()) >= MIN_WORDS:
            n += 1
            out.append((f'{name} draft {n}', body))
    return out


def draft_bodies(hours: int) -> list[tuple[str, str]]:
    """Every draft in drafts/ whose file date falls inside the window."""
    out: list[tuple[str, str]] = []
    cutoff = datetime.now() - timedelta(hours=hours)
    for p in sorted((HERE / 'drafts').glob('*.md')):
        m = re.match(r'(\d{4}-\d{2}-\d{2})', p.name)
        if m and datetime.fromisoformat(m.group(1)) < cutoff - timedelta(days=1):
            continue
        out.extend(bodies_in(p.read_text(encoding='utf-8'), p.name))
    return out


def check(candidate: str, hours: int, exclude: str | None = None) -> list[tuple[str, float]]:
    cand = tokens(candidate)
    hits = []
    for label, body in draft_bodies(hours):
        if exclude and label == exclude:
            continue
        s = jaccard(cand, tokens(body))
        if s >= THRESHOLD:
            hits.append((label, s))
    return sorted(hits, key=lambda h: -h[1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=int, default=24)
    ap.add_argument('--file', help='check every draft in this file against the others')
    args = ap.parse_args()

    if args.file:
        p = Path(args.file)
        text = p.read_text(encoding='utf-8')
        flagged = 0
        drafts = bodies_in(text, p.name)
        for label, body in drafts:
            for other, s in check(body, args.hours, exclude=label):
                print(f'NEAR-DUPLICATE: {label} vs {other} ({s:.0%} overlap)')
                flagged += 1
        print(f'{len(drafts)} drafts read; ' + ('clear' if flagged == 0 else f'{flagged} flagged: read both before either is posted'))
        return 1 if flagged else 0

    candidate = sys.stdin.read()
    if not candidate.strip():
        print('usage: neardup.py < draft.txt', file=sys.stderr)
        return 2
    hits = check(candidate, args.hours)
    for label, s in hits:
        print(f'NEAR-DUPLICATE: vs {label} ({s:.0%} overlap)')
    print('clear' if not hits else f'{len(hits)} flagged inside {args.hours}h: read both before posting')
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
