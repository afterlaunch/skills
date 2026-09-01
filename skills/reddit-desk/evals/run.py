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
        ws = Path(td) / 'desk'
        (ws / 'drafts').mkdir(parents=True)
        # The shape SKILL.md actually prescribes: "Write each draft under its
        # own '### Text' heading in drafts/<date>.md", at the top level of the
        # file, with NO enclosing '## ' section. This fixture used to wrap the
        # draft in one, so the eval gave positive confidence on the one shape
        # that worked while the shape readers are TOLD to write read as zero
        # drafts and the gate reported a clear file it had never opened
        # (QA, 2026-09-01). The heading suffix stays: it is the exact form that
        # slipped past the parser once before.
        (ws / 'drafts' / '2026-01-01.md').write_text(
            '# 2026-01-01 drafts\n\nThread: r/example, "a thread"\n'
            'Why this thread: they asked how to measure.\nClaims used: C1.\n\n'
            '### Text as loaded (v2)\n\n' + DRAFT + '\n\n---\n'
        )
        # The nested shape stays pinned beside it, because the estate carries
        # files where a '### Text' block does sit under a '## ' section, and a
        # fix for the top-level shape must not be bought with that one.
        (ws / 'drafts' / '2026-01-04.md').write_text(
            '# 2026-01-04 drafts\n\n## Draft A. r/example, "a thread"\n\n'
            'Claims used: C1.\n\n### Text\n\n' + DRAFT + '\n\n---\n'
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
        check('a draft written as SKILL.md prescribes, at the top level, is read',
              '1 drafts read' in r.stdout, r.stdout)

        r = neardup(ws, '--file', str(ws / 'drafts' / '2026-01-04.md'))
        check('a suffix-free ### Text block nested under a ## section is read too',
              '1 drafts read' in r.stdout, r.stdout)

        # The property rather than the parse. Two near-same comments in one
        # file written exactly as prescribed are the 7-day-ban shape, and this
        # is what the gate is FOR: it must flag them, not report a clear file
        # it never opened. Its own workspace, so the corpus above cannot make
        # it pass for the wrong reason.
        ws2 = Path(td) / 'prescribed'
        (ws2 / 'drafts').mkdir(parents=True)
        (ws2 / 'drafts' / '2026-01-01.md').write_text(
            '# 2026-01-01 drafts\n\nThread: r/example, "one thread"\nClaims used: C1.\n\n'
            '### Text\n\n' + DRAFT + '\n\n---\n\n'
            'Thread: r/example, "another thread"\nClaims used: C1.\n\n'
            '### Text\n\n' + DRAFT + '\n'
        )
        r = neardup(ws2, '--file', str(ws2 / 'drafts' / '2026-01-01.md'))
        check('two near-same drafts in a prescribed-format file FLAG, never clear',
              r.returncode == 1 and 'NEAR-DUPLICATE' in r.stdout, r.stdout + r.stderr)

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

    # THE DOCUMENTED FIRST RUN, on an estate that does not exist yet:
    # reconcile then reindex, with no comment history to paste. It used to end
    # in a traceback, so the desk's own prescribed opening move failed for
    # every new reader. Both halves are pinned here.
    def desk(estate: Path):
        env = {k: v for k, v in os.environ.items() if k != 'REDDIT_DESK'}
        env['SKILLS_ESTATE'] = str(estate)

        def run(script: str, *args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(SKILL / 'scripts' / script), *args],
                env=env, input='', capture_output=True, text=True,
            )
        return run

    with tempfile.TemporaryDirectory() as td:
        estate = Path(td) / 'estate'  # deliberately never created
        run = desk(estate)

        r = run('reconcile.py')
        check('first run: reconcile on a fresh estate does not traceback',
              'Traceback' not in r.stderr, r.stderr)
        r = run('reindex.py')
        check('first run: reindex on a fresh estate does not traceback',
              r.returncode == 0 and 'Traceback' not in r.stderr, r.stderr + r.stdout)
        check('first run: an empty board is written anyway',
              (estate / 'reddit' / 'BOARD.md').is_file())

        # --file is a READ, and it is contained to the workspace. A reader
        # that opens any absolute path on the machine is a wider surface than
        # a desk needs, and a missing path answers in a line, not a traceback.
        r = run('neardup.py', '--file', '/etc/passwd')
        check('neardup refuses a file outside the workspace',
              r.returncode == 2 and 'refused' in r.stderr, r.stderr)
        r = run('neardup.py', '--file', str(estate / 'reddit' / 'drafts' / 'absent.md'))
        check('neardup fails politely on a missing file',
              r.returncode == 2 and 'Traceback' not in r.stderr, r.stderr)

    with tempfile.TemporaryDirectory() as td:
        # A permalink on an estate whose PARENT does not exist either: the
        # directory has to be made with its parents or this crashes.
        estate = Path(td) / 'estate'
        r = desk(estate)('reconcile.py',
                         'https://reddit.com/r/example/comments/1abc/x/comment/p123/')
        check('first run: a permalink files a thread on a fresh estate',
              r.returncode == 0 and 'Traceback' not in r.stderr, r.stderr + r.stdout)

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
        check(f'no em-dash in {name}', '\u2014' not in text, '')

    text = (SKILL / 'SKILL.md').read_text()
    check('the skill never posts (the words are present, all three)',
          text.count('draft_only') >= 3 and 'never be one' in text, '')

    print('---')
    print('CLEAR' if not FAILURES else f'{len(FAILURES)} FAILED: {FAILURES}')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
