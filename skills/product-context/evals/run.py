#!/usr/bin/env python3
"""product-context evals: this skill is one plain-text file, so its evals are
structural and publication lints over that file. Pure, offline, no network.

    python3 evals/run.py        # exit 0 = every eval passes
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / 'SKILL.md'
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = '') -> None:
    print(('PASS' if ok else 'FAIL'), name, detail if not ok else '')
    if not ok:
        FAILURES.append(name)


def main() -> int:
    text = SKILL.read_text(encoding='utf-8')

    check('frontmatter has name/description/when_to_use',
          all(re.search(rf'^{f}:', text, re.M) for f in ('name', 'description', 'when_to_use')))

    for heading in ('ask, do not guess', 'What the file answers',
                    'Where the file lives', 'How the other skills use it',
                    'With AfterLaunch connected', 'What this skill cannot do'):
        check(f'section present: {heading}', heading in text)

    # The nine questions are the substance; a short list is the failure mode.
    # Counted INSIDE its own section, because the two-pass method above it is
    # also a numbered list and a document-wide count conflates them.
    section = text.split('## What the file answers', 1)[1].split('\n## ', 1)[0]
    numbered = re.findall(r'^\d+\. \*\*', section, re.M)
    check('the file answers nine questions', len(numbered) == 9, f'found {len(numbered)}')

    # The honesty mechanic must survive any future edit.
    check('unverified fields stay marked rather than filled', 'UNKNOWN' in text)
    check('never invents a claim', 'Never write a claim into this file' in text)

    # House rules.
    check('no em-dash', '—' not in text)
    check('no exclamation mark', '!' not in text)
    check('no americanised -ize spellings',
          not re.search(r'\b\w+iz(e|ed|es|ing|ation)\b', text))

    # THE PUBLICATION RULE. Nothing of ours travels: no costs, no product
    # metrics, no internals, no personal identity. The denylist is assembled
    # from fragments so this published file never contains what it blocks.
    money = '|'.join(['co' + 'st', 'pri' + 'cing', 'sp' + 'end', 'cre' + 'dits', r'\$'])
    check('no cost or pricing language', not re.search(money, text, re.I))
    metrics = '|'.join(['our cor' + 'pus', 'we mea' + 'sured', 'citation r' + 'ate', 'mention r' + 'ate'])
    check('no product metrics of ours', not re.search(metrics, text, re.I))
    internals = '|'.join(['supa' + 'base', 'inn' + 'gest', 'enroll' + 'ment', 'servi' + 'ce_role', 'schema'])
    check('no internal architecture', not re.search(internals, text, re.I))
    private = '|'.join(['shr' + 'eyas', 'caffeine' + 'mojo'])
    check('no personal identity', not re.search(private, text, re.I))
    check('no credential-shaped strings',
          not re.search(r'(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|Bearer [A-Za-z0-9._-]{10,})', text))
    check('no home paths', not re.search(r'/Users/[a-z]|~/\.claude/content', text))

    # The write surface: this skill only ever reads, plus one optional record.
    verbs = set(re.findall(r'`(get_\w+|list_\w+|\w+_move|\w+_draft|record_insight)`', text))
    check('no verb beyond the declared surface',
          verbs <= {'get_snapshot', 'list_kb_pages', 'get_kb_page', 'record_insight'},
          str(verbs))
    check('never ships a move', 'ship_move' not in text)

    check('no scripts directory', not (SKILL.parent / 'scripts').exists())

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
