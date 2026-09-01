#!/usr/bin/env python3
"""The near-duplicate gate: is this draft too close to anything we posted or
drafted in the last N hours?

Why it exists. Subs write this rule down, and one in seed/VENUES.md puts it
plainly: "posting the same or almost the same comment in more than one thread
within 24 h is spam", a 7-day ban, then permanent. Where no rule says it, a
moderation bot catches the shape anyway. So a cross-thread near-duplicate is a
BAN risk in any room, not a style note, and a mention counter cannot see it.
This does.

It is a token-overlap (Jaccard) check over the draft bodies in drafts/*.md.
Pure, offline, deterministic. It flags; a session decides. A flag means "read
both before posting", never "rewrite automatically".

KNOWN LIMIT, stated because a safety gate must not overclaim: this compares
DRAFTS against DRAFTS. It does not read REPLY_LEDGER.md, so it cannot see the
text you actually posted. Since the drafts here are raw material for your own
rewrite, the posted wording is the wording a ban attaches to, and that is the
wording this cannot check. Read the ledger yourself before posting into a sub
you have replied in recently. Wiring the ledger in is tracked in the backlog.

Usage:
    python3 neardup.py < draft.txt
    python3 neardup.py --hours 48 < draft.txt
    python3 neardup.py --file drafts/2026-08-28.md   # check every draft in a file against the others

--file reads a path inside the desk workspace and nowhere else. Anything
outside it is refused in one line rather than opened.

Exit 0 = clear, 1 = at least one near-duplicate flagged, 2 = usage.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# The estate. REDDIT_DESK still wins for anyone already using it; otherwise
# this skill lives under the suite's shared SKILLS_ESTATE, so one variable
# configures the whole pack.
def _estate():
    import os
    from pathlib import Path
    explicit = os.environ.get('REDDIT_DESK')
    if explicit:
        return Path(explicit).resolve()
    shared = os.environ.get('SKILLS_ESTATE')
    root = Path(shared) if shared else Path.home() / '.claude' / 'content'
    return (root / 'reddit').resolve()

MAX_INPUT_BYTES = 4 * 1024 * 1024  # a draft is kilobytes
HERE = _estate()
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


def text_blocks_in(chunk: str) -> list[str]:
    """The body under every '### Text' heading in one chunk of markdown.

    A '### Text' heading may carry a suffix ("### Text as loaded (v2)"), which
    is exactly how the one LIVE, unsent draft was labelled on 2026-08-28; an
    exact-line match silently skipped it (QA, 2026-08-30). Anchor on the
    heading's start, not its whole line."""
    out: list[str] = []
    for block in re.split(r'^### Text\b.*$', chunk, flags=re.M)[1:]:
        body = re.split(r'^---\s*$', block, maxsplit=1, flags=re.M)[0].strip()
        if len(body.split()) >= MIN_WORDS:
            out.append(body)
    return out


def bodies_in(text: str, name: str) -> list[tuple[str, str]]:
    """(label, body) for every draft in one file. Two shapes are read, because
    the estate carries both: a '### Text' block (2026-08-28 onwards), and a
    '## A. r/sub, "title"' section whose comment is the blockquoted lines
    (2026-08-22). A section with neither, such as a mod email, is not a
    comment and is skipped.

    A '### Text' block counts wherever it sits, nested under a '## ' section or
    at the top level of the file. SKILL.md prescribes the top-level form, and
    this used to read the '## '-delimited sections ONLY: a drafts file written
    exactly as the skill instructs yielded '0 drafts read; clear', so the gate
    passed because it had read nothing. A gate that is blind to the format its
    own skill prescribes fails OPEN, and this one guards a 7-day ban that turns
    permanent (QA, 2026-09-01)."""
    out: list[tuple[str, str]] = []
    n = 0
    # Index 0 is whatever precedes the first '## ' heading, which on a file
    # written as prescribed is every draft in it. It has no section heading, so
    # only the '### Text' shape can be recognised there; the blockquote shape
    # below needs a heading to tell our own draft from something we quoted.
    sections = re.split(r'^## ', text, flags=re.M)
    for i, section in enumerate(sections):
        blocks = text_blocks_in(section)
        if blocks:
            for body in blocks:
                n += 1
                out.append((f'{name} draft {n}', body))
            continue
        if i == 0:
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
        # --file is a READ, and a reader that will open any absolute path on
        # the machine is a wider surface than this desk needs: the skill's
        # promise is one workspace, and a promise scoped to writes alone is
        # half a promise. Contain it, and answer both failure modes in a line
        # rather than a traceback.
        p = Path(args.file).resolve()
        try:
            p.relative_to(HERE)
        except ValueError:
            print(f'refused: {p} is outside the desk workspace ({HERE}). '
                  'Pass a file inside it, or pipe the text in on stdin.',
                  file=sys.stderr)
            return 2
        if not p.is_file():
            print(f'no such file: {p}', file=sys.stderr)
            return 2
        try:
            text = p.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as exc:
            print(f'could not read {p} as text: {exc}', file=sys.stderr)
            return 2
        flagged = 0
        drafts = bodies_in(text, p.name)
        for label, body in drafts:
            for other, s in check(body, args.hours, exclude=label):
                print(f'NEAR-DUPLICATE: {label} vs {other} ({s:.0%} overlap)')
                flagged += 1
        print(f'{len(drafts)} drafts read; ' + ('clear' if flagged == 0 else f'{flagged} flagged: read both before either is posted'))
        return 1 if flagged else 0

    candidate = sys.stdin.read(MAX_INPUT_BYTES)
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
