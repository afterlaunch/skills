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

    # THE SKILL MUST TEACH A READER TO BUILD THEIR OWN VENUE LIST. The desk
    # shipped once with no discovery step at all: it told a new reader to copy
    # the seed in as their RULES.md and swept on, so anyone whose buyers are
    # not in the seed's rooms inherited a rulebook for somebody else's market
    # (founder, 2026-09-02). Three checks, and each is worth reading for what
    # it does NOT do. The first two are presence tests: a section teaching
    # venue discovery exists, it comes before the ban check, and it says an
    # unrecorded sub gets no draft. Presence alone is weak, and QA proved it:
    # a mutant that put the old copy-the-seed instruction BACK while keeping
    # the discovery section passed both of them clear (2026-09-02). So the
    # third asserts the ABSENCE of the defect itself, and it is the one that
    # actually pins the bug. Wording is not the invariant either way: a real
    # rewrite of the section still passes all three.
    skill = (SKILL / 'SKILL.md').read_text()
    bodies = re.split(r'^### .*$', skill, flags=re.M)[1:]

    def first(pred) -> int:
        return next((i for i, b in enumerate(bodies) if pred(b)), -1)

    ban = first(lambda b: 'user_is_banned' in b)
    discovery = first(lambda b: (
        'RULES.md' in b
        and re.search(r'\brules page\b', b, re.I)
        and re.search(r'\brow\b', b, re.I)
        and re.search(r'buyers|customers', b, re.I)
    ))
    check('the session starts by discovering YOUR venues, before the ban check',
          0 <= discovery < ban, f'discovery={discovery} ban={ban}')
    check('a sub with no row is unknown, and gets no draft',
          discovery >= 0 and re.search(r'no row', bodies[discovery], re.I) is not None
          and re.search(r'unknown', bodies[discovery], re.I) is not None,
          bodies[discovery] if discovery >= 0 else '')

    # And the rule is enforced where an unswept thread arrives, not only
    # asserted in step 0. A thread handed straight to the desk misses the
    # sweep and the ban check, which both read the table, so classification
    # is the last gate before a draft. The property is that the classify step
    # reads the table and says what happens when the row is missing; whether
    # it stops there or writes the row in place is a wording choice, and this
    # deliberately does not pin which.
    classify = first(lambda b: 'SKIP' in b and 'INTEL' in b)
    check('classification itself gates on the row, so a hand-dragged thread cannot slip past',
          classify >= 0 and 'RULES.md' in bodies[classify]
          and re.search(r'no row', bodies[classify], re.I) is not None,
          bodies[classify] if classify >= 0 else '')

    # TRAIN 3 ITEM 13: THE CLAIM LIBRARY LIVES IN THE RECORD. The desk is the
    # thing that measures; until now it was also the only thing holding the
    # measurements, in a file its X sibling kept a second, unsynced copy of.
    # Connected, `get_claims` is the library and `CLAIMS.md` is the cache of
    # what was read. Scoped to the DRAFT step body, so a mention anywhere else
    # in the file cannot satisfy a rule about where the drafter is standing.
    draft_step = first(lambda b: 'CLAIMS.md' in b and 'REPLY_LEDGER.md' in b)
    check('the draft step is the one that holds the claim rule', draft_step >= 0)
    dbody = re.sub(r'\s+', ' ', bodies[draft_step] if draft_step >= 0 else '')

    # FIRST, and first is the whole point: a draft written before the library
    # is read is a draft written against a stale local copy. QA proved the
    # byte offset alone is not that invariant (finding 4, 2026-09-02): it
    # reworded the bullet to "call get_claims AFTER the replies are written"
    # without moving a byte, and the offset check passed clear. So the
    # IMPERATIVE is asserted against the bullet's own text first, and the
    # position is kept as a second line rather than the only one.
    m = re.search(r'- \*\*Read the claim library[^\n]*\n(?:  [^\n]*\n)*',
                  bodies[draft_step] if draft_step >= 0 else '')
    bullet = re.sub(r'\s+', ' ', m.group(0) if m else '')
    check('the claim bullet itself puts get_claims before the first draft',
          'get_claims' in bullet and 'before the first draft' in bullet, bullet)
    check('and the bullet still sits ahead of the drafting rule in the step',
          -1 < dbody.find('get_claims') < dbody.find('The number, its scope'))
    # And it degrades to the file, which is what a reader with no key has.
    check('CLAIMS.md is the offline fallback and the cache of what was read',
          'CLAIMS.md` is the library on its own' in dbody
          and 'cache of what was read' in dbody)
    # A held claim is skipped whichever way it arrives. The two shapes are the
    # verb's `held` flag and the file's `HELD` caveat, and they mean one thing.
    check('a held claim from the record is skipped exactly as a HELD caveat is',
          re.search(r'`held` is true is skipped', dbody) is not None
          and 'HELD' in dbody)
    # The desk measures, so the desk feeds the library rather than hoarding it.
    check('a claim settled in the session is offered back to the record',
          'record_claim' in dbody)

    # The defect in its own words: the seed standing in as the rulebook. Read
    # as a target, not a verb list, because "use|copy" plus two filenames also
    # matches the honest sentences that teach the row FORMAT, and a guard that
    # fails on good writing is one somebody edits out in a hurry. A negated
    # sentence ("never copy a row from the seed into RULES.md") is a
    # prohibition, so it is skipped by the same reasoning.
    adopt = re.compile(
        r'VENUES\.md[^.]{0,80}\b(as|becomes)\b[^.]{0,40}`?(your |the )?`?RULES\.md'
        r'|VENUES\.md[^.]{0,100}RULES\.md[^.]{0,25}starting point'
        r'|VENUES\.md[^.]{0,60}\bas\b[^.]{0,30}(your |the )?(rulebook|venue list|rules file)'
        r'|(cop\w+|adopt\w*|reus\w+)[^.]{0,60}VENUES\.md[^.]{0,60}\b(to|as|into|for)\b'
        r'[^.]{0,30}`?(your |the )?`?RULES\.md',
        re.I)
    hits = [m for m in adopt.finditer(skill)
            if not re.search(r"\b(never|not|don't)\b", skill[max(0, m.start() - 45):m.start()], re.I)]
    check('the skill never tells a reader to adopt the seed as their RULES.md',
          not hits, hits[0].group(0) if hits else '')

    # And the seed must not present itself as the map. Same defect, other end:
    # a file that reads like the definitive venue list is one a reader adopts
    # whole. Its preamble has to name itself an example and a starting set,
    # and send a reader whose market is elsewhere to find their own rooms.
    preamble = venues.split('| Sub |')[0]
    check('the seed presents itself as an example and a starting set, not the map',
          all(re.search(pat, preamble, re.I) for pat in
              [r'\bexample\b', r'starting set', r'your own']), preamble)

    for name in ['SKILL.md', 'seed/VENUES.md', 'seed/CLAIMS_TEMPLATE.md']:
        text = (SKILL / name).read_text()
        check(f'no em-dash in {name}', '\u2014' not in text, '')

    check('the skill never posts (the words are present, all three)',
          skill.count('draft_only') >= 3 and 'never be one' in skill, '')

    print('---')
    print('CLEAR' if not FAILURES else f'{len(FAILURES)} FAILED: {FAILURES}')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
