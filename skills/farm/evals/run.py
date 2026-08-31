#!/usr/bin/env python3
"""farm evals: structural and publication lints over the published
SKILL.md. Pure, offline, no network.

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
    # A markdown line wrap can split a phrase across two lines; flatten
    # whitespace once for any check that reads as a sentence rather than a
    # single token or heading.
    flat = re.sub(r'\s+', ' ', text)

    # Frontmatter and the sections the skill promises.
    check('frontmatter has name/description/when_to_use/allowed-tools',
          all(re.search(rf'^{f}:', text, re.M)
              for f in ('name', 'description', 'when_to_use', 'allowed-tools')))
    for heading in ('Where things live', 'Step 0: capture', 'Step 1: actor or item',
                    'Step 4: sort every idea into exactly one lane', 'Step 5: the judge',
                    'Step 7: file it', 'With AfterLaunch connected', 'What this cannot do alone',
                    'House rules', 'Next'):
        check(f'section present: {heading}', heading in text)

    # The estate is configurable, and the default is stated as the current
    # default, matching the parameterise-the-estate pattern reddit-desk set
    # with REDDIT_DESK.
    check('estate is configurable via SKILLS_ESTATE', 'SKILLS_ESTATE' in text)
    check('default estate is stated (~/.claude/content)', '~/.claude/content' in text)

    # House style: no em-dash, no exclamation mark, British spellings only.
    check('no em-dash', '—' not in text)
    check('no exclamation mark', '!' not in text)
    check('no americanised -ize spellings',
          not re.search(r'\b\w+iz(e|ed|es|ing|ation)\b', text))

    # The honest limit: it names what it cannot do alone (ask the engines,
    # rank, prove), and says so explicitly rather than only implying it.
    for phrase in ('cannot ask the engines', 'cannot rank', 'cannot prove'):
        check(f'honest limit names: {phrase}', phrase in flat)

    # The write surface is exactly the declared verbs, and never ship_move.
    verbs = set(re.findall(r'`(\w+_move|\w+_draft|record_insight|get_\w+|list_\w+|ship_move)`', text))
    check('ship_move never appears', 'ship_move' not in text)
    check('no verb beyond the declared surface',
          verbs <= {'record_insight', 'get_standup'})

    # Publication rule (docs/plans/DESK_CATALOGUE.md section 4b): no costs,
    # no product metrics, nothing reverse-engineerable, no founder identity.
    # Denylists assembled from fragments so this published file never
    # itself contains the strings it exists to keep out of the world.
    check('no cost or spend figures',
          not re.search('|'.join([r'\$\d', r'\bUSD\b', 'per[- ]call ' + 'co' + 'st',
                                'sp' + 'end cap', 'cre' + 'dit(s)? (cost|price)'] + ['half a ' + 'penny']), text, re.I))
    check('no product metrics (customer/scan/citation counts)',
          not re.search(r'\b\d+([,.]\d+)?\s*(' + '|'.join(['cust' + 'omers', 'sc' + 'ans',
              'cita' + 'tions', 'men' + 'tions', 'enroll' + 'ments']) + r')\b', text, re.I))
    check('no internal doc cross-references (BACKLOG.md, MEMORY.md, root CLAUDE.md, monorepo)',
          not re.search(r'\bBACKLOG\.md\b|\bMEMORY\.md\b|root `?CLAUDE\.md`?|\bmonorepo\b|\bworktrees?\b', text, re.I))
    check('no reference to unpublished sibling skills by internal path',
          not re.search(r'\.claude/skills/(x-intel|yt|reddit-desk|post)/', text))
    check('no credential-shaped strings',
          not re.search(r'(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|Bearer [A-Za-z0-9._-]{10,}|al_[A-Za-z0-9]{16,})', text))
    check('no home paths beyond the documented default estate',
          not re.search(r'/Users/[a-z]', text))
    # The denylist is assembled from fragments so this published file never
    # itself contains the strings it exists to keep out.
    private = '|'.join(['shr' + 'eyas', 'caffeine' + 'mojo', 'after' + 'launchapp+'])
    check('no founder name or personal handle',
          not re.search(private, text, re.I))

    # The script this skill ships (intake.mjs) must itself respect the same
    # estate override, or the prose above would describe behaviour the code
    # does not have.
    script = SKILL.parent / 'scripts' / 'intake.mjs'
    check('scripts/intake.mjs exists', script.exists())
    if script.exists():
        code = script.read_text(encoding='utf-8')
        check('intake.mjs reads SKILLS_ESTATE before falling back to the default',
              'process.env.SKILLS_ESTATE' in code)
        check('intake.mjs default estate matches the documented one (~/.claude/content)',
              "'.claude', 'content'" in code)
        check('intake.mjs has no dangling reference to an unpublished sibling skill',
              not re.search(r'\.claude/skills/(x-intel|yt)/', code))

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
