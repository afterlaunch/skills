#!/usr/bin/env python3
"""tells evals: structural, house-style, publication-safety and
register-substance lints over the skill's own markdown files. Pure,
offline, no network, no dependency beyond the standard library.

    python3 evals/run.py        # exit 0 = every eval passes
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ['SKILL.md', 'TELLS.md']
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = '') -> None:
    print(('PASS' if ok else 'FAIL'), name, detail if not ok else '')
    if not ok:
        FAILURES.append(name)


def main() -> int:
    texts = {f: (ROOT / f).read_text(encoding='utf-8') for f in FILES}
    skill = texts['SKILL.md']
    tells = texts['TELLS.md']
    everything = '\n'.join(texts.values())

    # Frontmatter and the sections the skill promises.
    check('frontmatter has name/description/when_to_use/allowed-tools',
          all(re.search(rf'^{f}:', skill, re.M)
              for f in ('name', 'description', 'when_to_use', 'allowed-tools')))
    for heading in ('What this catches that a green build does not',
                     'How to run it', 'For a draft post specifically',
                     'Three rules for the findings', 'Where things live',
                     'With AfterLaunch connected', 'What this cannot do alone'):
        check(f'section present: {heading}', heading in skill)
    for heading in ('Part 1: Prose', 'Part 2: Visual and layout',
                     'Part 3: Machine-checked', 'Vocabulary, zero tolerance',
                     'Constructions, zero tolerance'):
        check(f'register section present: {heading}', heading in tells)

    # This is a merge of two prior audits: it must do prose AND a built
    # surface, not just one.
    check('audits prose', 'prose' in skill.lower())
    check('audits a built surface', re.search(r'built (surface|interface)', skill.lower()) is not None)

    # House style, across every file this skill ships.
    for name, text in texts.items():
        check(f'no em-dash in {name}', '\u2014' not in text)
        check(f'no exclamation mark in {name}',
              '!' not in text.replace('exclamation', ''))
        # A banned-vocabulary register is allowed to name the American
        # spelling of a word it exists to ban; that is data, not a house
        # style violation. Everything else must stay British.
        allowed_ize = {'utilize', 'utilizes', 'utilizing', 'utilized',
                       'revolutionize', 'revolutionizes', 'revolutionizing'}
        hits = [w for w in re.findall(r'\b\w+iz(?:e|ed|es|ing|ation)\b', text, re.I)
                if w.lower() not in allowed_ize]
        check(f'no americanised -ize spellings in {name}', not hits, str(hits))

    # The register is the heart of the skill, and thin is the failure
    # mode. Count what actually reads as a distinct, checkable entry:
    # top-level bullets, plus the two comma-separated banned-word/phrase
    # lists, which are prose blocks rather than bullets.
    bullets = re.findall(r'^- ', tells, re.M)
    vocab_block = re.search(r'## Vocabulary, zero tolerance\n\n(.+?)\n\n##', tells, re.S)
    vocab_words = len(re.findall(r'[a-z][a-z -]*[a-z]', vocab_block.group(1))) if vocab_block else 0
    phrase_block = re.search(r'## Phrases\n\n(.+?)\n\n##', tells, re.S)
    phrases = len(re.findall(r'"[^"]+"', phrase_block.group(1))) if phrase_block else 0
    total_checks = len(bullets) + vocab_words + phrases
    check('register carries a substantial number of distinct checks',
          total_checks >= 60, str(total_checks))
    check('register has at least 20 named vocabulary entries', vocab_words >= 20, str(vocab_words))
    check('register has at least 10 named phrase entries', phrases >= 10, str(phrases))

    # Part 3 is meant to be machine-parseable and points at the reader's
    # own project, never at ours.
    check('Part 3 ships a parseable JSON rule block', '```json' in tells)
    check('Part 3 scope is a placeholder, not our own path',
          '<path to your own' in tells and 'apps' + '/web' not in tells)

    # The workspace path is configurable, and no bare unnamespaced
    # estate path or literal home path leaked in.
    check('workspace path is configurable via env var', 'SKILLS_ESTATE' in skill)
    # Namespaced means: the estate ROOT plus a skill's own subdirectory. Two
    # are legitimate here, this skill's own and product-context's, whose
    # refused-words list this audit checks against. Anything else under the
    # root is a leftover from an internal version.
    check('no bare unnamespaced content-estate path',
          not re.search(r'~/\.claude/content/(?!tells|product-context)', everything))

    # The refused words are half this audit's vocabulary, and the register
    # cannot carry them: they are per-business, not generic.
    check('checks the refused words from the product context file',
          '~/.claude/content/product-context/PRODUCT.md' in skill
          and 'refused' in skill.lower())
    home_path = '/' + 'Users/[a-z]'
    check('no literal filesystem home path', not re.search(home_path, everything, re.I))

    # The connected surface is exactly the one honest verb for this skill:
    # a fix goes back onto the board, nothing ships, nothing is minted.
    verbs = set(re.findall(
        r'`(get_move|update_draft|list_feed|record_insight|propose_move|ship_move)`',
        everything))
    check('ship_move never appears', 'ship_move' not in everything)
    check('connected verb is exactly update_draft', verbs == {'update_draft'}, str(verbs))

    # Publication rule: no per-call outlay or unit-economics language
    # (ours or anyone else's), no internal schema/architecture names, no
    # founder identity. The denylist is assembled from fragments so this
    # file never itself contains the strings it exists to keep out.
    money = ['co' + 'st', 'pri' + 'ce', 'sp' + 'end', 'cred' + 'it']
    for word in money:
        check(f'no "{word}"-shaped language', not re.search(word, everything, re.I))
    internal = ['V6 es' + 'tate', 'V5 fall' + 'back', 'stat ' + 'gate',
                'BACK' + 'LOG D23', 'ADR-' + '319']
    for word in internal:
        check(f'no internal architecture reference "{word}"', word not in everything)
    private = '|'.join(['shr' + 'eyas', 'caffeine' + 'mojo', 'after' + 'launchapp+'])
    check('no founder name or personal handle', not re.search(private, everything, re.I))

    # No executable surface beyond this eval itself: this skill is a
    # register plus a process, not a bundle of scripts.
    check('no scripts directory', not (ROOT / 'scripts').exists())

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
