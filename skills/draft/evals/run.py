#!/usr/bin/env python3
"""draft evals: structural, house-style and publication-safety lints over
the skill's own markdown files. Pure, offline, no network, no dependency
beyond the standard library.

    python3 evals/run.py        # exit 0 = every eval passes
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ['SKILL.md', 'STYLE.md', 'HOOKS.md', 'FORMATS.md']
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = '') -> None:
    print(('PASS' if ok else 'FAIL'), name, detail if not ok else '')
    if not ok:
        FAILURES.append(name)


def main() -> int:
    texts = {f: (ROOT / f).read_text(encoding='utf-8') for f in FILES}
    skill = texts['SKILL.md']
    everything = '\n'.join(texts.values())

    # Frontmatter and the sections the skill promises.
    check('frontmatter has name/description/when_to_use/allowed-tools',
          all(re.search(rf'^{f}:', skill, re.M)
              for f in ('name', 'description', 'when_to_use', 'allowed-tools')))
    for heading in ('Read first', 'Where things live', 'The sequence',
                    'Getting real material', 'Establishing your own voice',
                    'With AfterLaunch connected', 'What this cannot do alone'):
        check(f'section present: {heading}', heading in skill)

    # House style, across every file this skill ships.
    for name, text in texts.items():
        check(f'no em-dash in {name}', '—' not in text)
        check(f'no exclamation mark in {name}',
              '!' not in text.replace('exclamation', ''))
        # American -ize spellings fail, with one documented exception: a
        # banned-vocabulary list is allowed to name the American spelling
        # of a word it is banning, since that is data, not house style.
        allowed_ize = {'utilize', 'utilizes', 'utilizing', 'utilized',
                       'revolutionize', 'revolutionizes', 'revolutionizing'}
        hits = [w for w in re.findall(r'\b\w+iz(?:e|ed|es|ing|ation)\b', text, re.I)
                if w.lower() not in allowed_ize]
        check(f'no americanised -ize spellings in {name}', not hits, str(hits))

    # Never ships one finished post: three hooks, a draft per platform.
    check('promises three hooks', 'three hook' in skill.lower() or 'Three hooks' in skill)
    check('never one finished post', 'one finished post' in skill.lower())

    # The workspace path is configurable, and the skill does not hardcode
    # a bare, unnamespaced estate path left over from an internal version.
    check('workspace path is configurable via env var', 'SKILLS_ESTATE' in skill)
    check('no bare unnamespaced content-estate path',
          not re.search(r'~/\.claude/content/(?!draft|voice)', everything))
    home_path = '/' + 'Users/[a-z]'
    check('no literal filesystem home path', not re.search(home_path, everything, re.I))

    # The connected surface is exactly the two honest verbs named for this
    # skill; nothing that ships, ranks or remembers on its own.
    verbs = set(re.findall(
        r'`(get_move|update_draft|list_feed|record_insight|propose_move|ship_move)`',
        everything))
    check('ship_move never appears', 'ship_move' not in everything)
    check('connected verbs are exactly get_move and update_draft',
          verbs == {'get_move', 'update_draft'}, str(verbs))

    # Publication rule: no per-call outlay or unit-economics language
    # (ours or anyone else's), no schema/service names, no founder
    # identity. The denylist is assembled from fragments so this file
    # never itself contains the strings it exists to keep out of the
    # published skill.
    money = ['co' + 'st', 'pri' + 'ce', 'sp' + 'end', 'cred' + 'it']
    for word in money:
        check(f'no "{word}"-shaped language', not re.search(word, everything, re.I))
    schema = ['engine_' + 'rollup', 'competitor_' + 'mentions', 'snapshots.ai_' + 'scan']
    for word in schema:
        check(f'no internal schema name "{word}"', word not in everything)
    private = '|'.join(['shr' + 'eyas', 'caffeine' + 'mojo', 'after' + 'launchapp+'])
    check('no founder name or personal handle', not re.search(private, everything, re.I))

    # No executable surface: this skill is pure method, no scripts.
    check('no scripts directory', not (ROOT / 'scripts').exists())

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
