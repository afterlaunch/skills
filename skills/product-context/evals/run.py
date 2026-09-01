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

    # THE HANDOFF. Every reader opens one exact string, so the file has to
    # name it. This is pinned rather than trusted because it is precisely
    # what went missing: the skill the pack calls "start here" described its
    # own location in prose, and no skill could act on the description.
    check('names the estate variable', 'SKILLS_ESTATE' in text)
    check('names the file and its directory concretely',
          '~/.claude/content/product-context/PRODUCT.md' in text)

    # The honesty mechanic must survive any future edit.
    check('unverified fields stay marked rather than filled', 'UNKNOWN' in text)
    check('never invents a claim', 'Never write a claim into this file' in text)

    # THE RECORD IS HOME. Connected, five of the nine questions arrive drafted
    # from the record and four are asked cold, but all nine still go to the
    # user. A vague connected section is the failure mode: it once said "use
    # the snapshot as the draft answer to questions one, two and three", which
    # named no page and no verb, so no reader could act on it. These checks
    # pin the parts that have to stay concrete.
    connected = text.split('## With AfterLaunch connected', 1)[1].split('\n## ', 1)[0]
    flat = re.sub(r'\s+', ' ', connected)

    for slug in ('about-my-business', 'my-audience', 'my-competitors', 'about-my-voice'):
        check(f'connected section names the page: {slug}', slug in connected)

    # The split is asserted as a PROPERTY, not as two hardcoded lists. Every
    # question is accounted for exactly once, and the declared drafted set has
    # to match the bullets that actually draft one. An earlier version listed
    # the numbers it expected, which passed a text that put question 4 in both
    # halves and a text that quietly dropped a bullet.
    def declared(label: str) -> set[int]:
        m = re.search(label + r', questions ([\d,\s]*\d+ and \d+)', flat)
        return {int(n) for n in re.findall(r'\d+', m.group(1))} if m else set()

    drafted, cold = declared('[Dd]rafted from the record'), declared('[Aa]sked cold')
    bulleted = {int(n) for n in re.findall(r'\*\*Question (\d+),', connected)}
    check('every question is drafted or asked cold, none both',
          drafted | cold == set(range(1, 10)) and not (drafted & cold),
          f'drafted={sorted(drafted)} cold={sorted(cold)}')
    check('the drafted questions are the ones with a bullet',
          bulleted == drafted and drafted, f'bullets={sorted(bulleted)}')
    check('the four asked cold are the four a site cannot know',
          cold == {4, 5, 8, 9}, str(sorted(cold)))

    # THE SEED GUARD. Showing a draft is only safe because an unconfirmed one
    # is never written down. Asserted as a property of ONE sentence: it has to
    # tie the marker to the act of persisting it, under a negation or a
    # condition. A proximity window over the word "confirm" was tried first
    # and failed both ways, passing a text whose guard had been deleted and an
    # unrelated UNKNOWN sentence added, and failing an honest reword to
    # "approve". Bold markers come out before the split so a sentence ending
    # inside them is not glued to the next one.
    sentences = re.split(r'(?<=\.)\s+', flat.replace('**', ''))
    PERSISTS = re.compile(r'PRODUCT\.md|written into|goes into|persist', re.I)
    CONDITION = re.compile(r'\b(never|not|until|unless)\b', re.I)
    check('an unconfirmed draft is never persisted',
          any('UNKNOWN' in s and PERSISTS.search(s) and CONDITION.search(s)
              for s in sentences))

    # Answers travel back, or the record stays wrong and every future draft
    # inherits it. The local file is the cache; the record is home.
    check('answers go back through the record', 'record_insight' in connected)
    check('the local file is named as a cache of the record',
          re.search(r'cache of (it|the record)', flat) is not None)

    # NEVER call the site-derived voice the user's own. The page is the BRAND's
    # voice, read from the website; conflating the two is the exact confusion
    # this pack exists to remove, and it lives in one word. Matched as a family
    # of phrasings, because a literal on one of them let "your own voice"
    # through.
    NEAR = 300
    OWNED = re.compile(r"your (own )?voice|the user'?s (own )?voice", re.I)
    for m in re.finditer('about-my-voice', text):
        window = text[max(0, m.start() - NEAR):m.end() + NEAR]
        check("the site-read voice is never called the user's own",
              not OWNED.search(window), window.strip()[:80])

    # House rules.
    check('no em-dash', '\u2014' not in text)
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
    # A path off one person's machine is both a leak and a bug for every
    # other reader, so it still fails. The pack's DOCUMENTED default estate is
    # not that: it is the one string every skill has to name for the handoff
    # to exist. Banning it is why this file once described its own location in
    # prose, which no reader could act on. So: strip the documented default
    # and anything under it, then any home path still standing is a real one.
    stripped = re.sub(r'~/\.claude/content(?:/[\w.-]+)*', '', text)
    check('no machine-specific home paths',
          not re.search(r'/Users/[a-z]|/home/[a-z]|~/', stripped))

    # THE WRITE SURFACE: three reads and one record, and nothing else exists.
    # Matched as ANY backticked snake_case token against an allowlist, rather
    # than as a list of verb shapes. The shape list let an invented page-write
    # verb through, which is precisely the verb a reader reaches for after
    # being told the pages are stale.
    ALLOWED = {'list_kb_pages', 'get_kb_page', 'get_snapshot', 'record_insight'}
    # A VERB, not any snake_case token: field and file names like author_kind
    # or product_context are honest prose and a guard that fails on them is a
    # guard that gets edited out under deadline. The prefixes are the ones a
    # reader could plausibly reach for, invented or real.
    PREFIXES = ('get_', 'list_', 'record_', 'set_', 'update_', 'create_',
                'delete_', 'ship_', 'skip_', 'propose_', 'refresh_', 'run_')
    tokens = set(re.findall(r'`([a-z][a-z0-9_]*)`', text))
    verbs = {v for v in tokens if '_' in v and v.startswith(PREFIXES)}
    check('no verb beyond the declared surface', verbs <= ALLOWED, str(verbs - ALLOWED))
    check('never ships a move', 'ship_move' not in text)
    # And say so out loud, so the reader does not go looking for the verb.
    check('says no tool writes a page',
          re.search(r'no tool writes a page', flat) is not None)

    check('no scripts directory', not (SKILL.parent / 'scripts').exists())

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
