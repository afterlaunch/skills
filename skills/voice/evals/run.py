#!/usr/bin/env python3
"""voice evals: this skill is plain text and one JSON template, so its
evals are structural and publication lints over SKILL.md. Pure, offline,
no network.

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

    # Frontmatter and the sections the skill promises.
    check('frontmatter has name/description/when_to_use',
          all(re.search(rf'^{f}:', text, re.M) for f in ('name', 'description', 'when_to_use')))
    for heading in ('Where things live', 'How a round runs', 'Reading the answers',
                    'What gets written', 'The honest limit', 'With AfterLaunch connected',
                    'House rules', 'Next'):
        check(f'section present: {heading}', heading in text)

    # The estate is configurable, and the default is stated as the current
    # default (this skill's own directory), matching the parameterise-the-
    # estate pattern reddit-desk set with REDDIT_DESK.
    check('estate is configurable via SKILLS_ESTATE', 'SKILLS_ESTATE' in text)
    # THE HANDOFF. `draft` reads the profile from voice/ under the shared
    # estate, so a voice written anywhere else is a voice no draft ever uses.
    # Two builders disagreed about this path and it would have shipped broken,
    # so the contract is pinned here rather than trusted.
    check('writes into the shared estate, where draft reads it',
          'voice/' in text and '~/.claude/content' in text)

    # House style: no em-dash, no exclamation mark, British spellings only.
    check('no em-dash', '—' not in text)
    check('no exclamation mark', '!' not in text)
    check('no americanised -ize spellings',
          not re.search(r'\b\w+iz(e|ed|es|ing|ation)\b', text))

    # The honest limit: it names what it cannot do alone (ask the engines,
    # rank, prove), and says so explicitly rather than only implying it.
    # Whitespace (including a markdown line wrap) is collapsed first so a
    # phrase split across two wrapped lines still matches.
    flat = re.sub(r'\s+', ' ', text)
    for phrase in ('cannot ask the engines', 'cannot rank', 'cannot prove'):
        check(f'honest limit names: {phrase}', phrase in flat)

    # The write surface is exactly the declared verbs, and never ship_move.
    verbs = set(re.findall(r'`(\w+_move|\w+_draft|record_insight|get_\w+|list_\w+|ship_move)`', text))
    check('ship_move never appears', 'ship_move' not in text)
    check('no verb beyond the declared surface',
          verbs <= {'update_draft', 'get_move', 'list_feed'})

    # Publication rule (docs/plans/DESK_CATALOGUE.md section 4b): no costs,
    # no product metrics, nothing reverse-engineerable, no founder identity.
    # Denylists assembled from fragments so this published file never
    # itself contains the strings it exists to keep out of the world.
    check('no cost or spend figures',
          not re.search('|'.join([r'\$\d', r'\bUSD\b', 'per[- ]call ' + 'co' + 'st',
                                'sp' + 'end cap', 'cre' + 'dit(s)? (cost|price)']), text, re.I))
    check('no product metrics (customer/scan/citation counts)',
          not re.search(r'\b\d+([,.]\d+)?\s*(' + '|'.join(['cust' + 'omers', 'sc' + 'ans',
              'cita' + 'tions', 'men' + 'tions', 'enroll' + 'ments']) + r')\b', text, re.I))
    check('no credential-shaped strings',
          not re.search(r'(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|Bearer [A-Za-z0-9._-]{10,}|al_[A-Za-z0-9]{16,})', text))
    check('no home paths or local estates other than the documented default',
          not re.search(r'/Users/[a-z]', text))
    # The denylist is assembled from fragments so this published file never
    # itself contains the strings it exists to keep out.
    private = '|'.join(['shr' + 'eyas', 'caffeine' + 'mojo', 'after' + 'launchapp+'])
    check('no founder name or personal handle',
          not re.search(private, text, re.I))
    # No cross-reference to an internal, unpublished sibling skill's doctrine
    # file: the old post-voice wrote into ../post/VOICE.md, which does not
    # exist in a standalone publish of this skill alone.
    check('no dangling cross-reference to an unpublished sibling skill',
          '../post/' not in text)

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
