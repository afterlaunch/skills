#!/usr/bin/env python3
"""The desk's evals: runnable proof that the safety mechanics work, in the
guard-test culture the skills programme demands (a skill without evals is a
blog post). Pure, offline, no network, no workspace needed: fixtures only.

    python3 evals/run.py        # exit 0 = every eval passes
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = '') -> None:
    print(('PASS' if ok else 'FAIL'), name, detail if not ok else '')
    if not ok:
        FAILURES.append(name)


def neardup(workspace: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SKILL / 'scripts' / 'neardup.py'), '--hours', '100000', *args],
        env={**os.environ, 'REDDIT_DESK': str(workspace)},
        capture_output=True,
        text=True,
    )


DRAFT = (
    'Before you buy a tool, measure the baseline by hand for a fortnight. '
    'Pick ten to fifteen questions a customer would ask, run each a few times '
    'per engine, and log three things: named, linked, and who got the link '
    'instead. Split it by engine, because a blended score hides the spread, '
    'and read the four-week line rather than the daily one.'
)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        (ws / 'drafts').mkdir()
        # Both draft shapes the estate has really carried: a '### Text' block
        # (suffix included, the exact form that once slipped past the parser)
        # and a lettered blockquote section.
        (ws / 'drafts' / '2026-01-01.md').write_text(
            '# drafts\n\n## Draft A\n\n### Text as loaded (v2)\n\n' + DRAFT + '\n\n---\n'
        )
        (ws / 'drafts' / '2026-01-02.md').write_text(
            '# drafts\n\n## B. r/example, "a thread"\n\nClaims used: C1.\n\n'
            + ''.join('> ' + line + '\n' for line in DRAFT.split('. '))
        )
        # A section that only QUOTES somebody (a sub rule): never a draft.
        (ws / 'drafts' / '2026-01-03.md').write_text(
            '# notes\n\n## Why a message, not a post\n\n> '
            + 'It is simple to email the mods and ask permission to post about your product, '
            'and without permission it is spam, so include content useful on its own.\n'
        )

        r = neardup(ws, '--file', str(ws / 'drafts' / '2026-01-01.md'))
        check('suffixed ### Text heading is read as a draft', '1 drafts read' in r.stdout, r.stdout)

        r = subprocess.run(
            [sys.executable, str(SKILL / 'scripts' / 'neardup.py'), '--hours', '100000'],
            env={**os.environ, 'REDDIT_DESK': str(ws)},
            input=DRAFT,
            capture_output=True,
            text=True,
        )
        check('a near-same comment across threads FLAGS (the 7-day-ban shape)',
              r.returncode == 1 and 'NEAR-DUPLICATE' in r.stdout, r.stdout)

        r = subprocess.run(
            [sys.executable, str(SKILL / 'scripts' / 'neardup.py'), '--hours', '100000'],
            env={**os.environ, 'REDDIT_DESK': str(ws)},
            input='A genuinely different comment about pricing pages and churn, with none of the earlier claim.',
            capture_output=True,
            text=True,
        )
        check('a genuinely different comment clears', r.returncode == 0, r.stdout)

        r = neardup(ws, '--file', str(ws / 'drafts' / '2026-01-03.md'))
        check('a quoted sub rule is not read as our draft', '0 drafts read' in r.stdout, r.stdout)

    # The venue matrix: every row carries a dated read and a reason; no
    # account-specific state ships in the seed; house style holds.
    venues = (SKILL / 'seed' / 'VENUES.md').read_text()
    rows = [l for l in venues.splitlines() if l.startswith('| r/')]
    check('venue matrix has rows', len(rows) >= 20, str(len(rows)))
    dated = [l for l in rows if re.search(r'\| \d{4}-\d{2}-\d{2} \|$', l)]
    check('every venue row carries the date its rules were read', len(dated) == len(rows),
          f'{len(dated)}/{len(rows)}')
    check('no account state in the seed (bans and reopen dates live in YOUR RULES.md)',
          'BANNED 20' not in venues and 'reopens 20' not in venues, '')

    for name in ['SKILL.md', 'seed/VENUES.md', 'seed/CLAIMS_TEMPLATE.md']:
        text = (SKILL / name).read_text()
        check(f'no em-dash in {name}', '—' not in text, '')

    text = (SKILL / 'SKILL.md').read_text()
    check('the skill never posts (the words are present, all three)',
          text.count('draft_only') >= 3 and 'never be one' in text, '')

    print('---')
    print('CLEAR' if not FAILURES else f'{len(FAILURES)} FAILED: {FAILURES}')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
