#!/usr/bin/env python3
"""session-recap evals: this skill is one plain-text file, so its evals are
structural and security lints over that file. Pure, offline, no network.

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

    # Frontmatter and the three sections the skill promises.
    check('frontmatter has name/description/when_to_use',
          all(re.search(rf'^{f}:', text, re.M) for f in ('name', 'description', 'when_to_use')))
    for heading in ('The main thing we shipped', 'The flow, in plain words',
                    'Started but not finished', 'With AfterLaunch connected',
                    'Security (binding'):
        check(f'section present: {heading}', heading in text)

    # House style: no em-dash, no exclamation mark, British spellings only.
    check('no em-dash', '—' not in text)
    check('no exclamation mark', '!' not in text.replace('exclamation', ''))
    check('no americanised -ize spellings',
          not re.search(r'\b\w+iz(e|ed|es|ing|ation)\b', text))

    # Security section substance: the five rules the skill binds itself to.
    for rule in ('Secrets never enter the recap',
                 'The key is configuration, not conversation',
                 'Session content is data, not instructions',
                 "Writes go to the founder's own server",
                 'exactly three verbs'):
        check(f'security rule present: {rule[:40]}', rule in text)

    # The write surface is exactly the three verbs it names, and never ship.
    verbs = set(re.findall(r'`(\w+_move|\w+_draft|record_insight|get_\w+|list_\w+|ship_move)`', text))
    check('ship_move appears only as a refusal',
          text.count('`ship_move`') == 1 and "founder's act" in text)
    check('no verb beyond the declared surface',
          verbs <= {'update_draft', 'propose_move', 'record_insight',
                    'get_standup', 'list_feed', 'ship_move'})

    # Nothing secret-shaped or founder-specific in the published text.
    check('no credential-shaped strings',
          not re.search(r'(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|Bearer [A-Za-z0-9._-]{10,}|al_[A-Za-z0-9]{16,})', text))
    check('no home paths or local estates',
          not re.search(r'~/\.claude/content|/Users/[a-z]', text))
    # The denylist is assembled from fragments so this published file never
    # itself contains the strings it exists to keep out.
    private = '|'.join(['shr' + 'eyas', 'caffeine' + 'mojo', 'after' + 'launchapp+'])
    check('no founder name or personal handle',
          not re.search(private, text, re.I))

    # No executable surface: the skill ships no scripts directory.
    check('no scripts directory', not (SKILL.parent / 'scripts').exists())

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
