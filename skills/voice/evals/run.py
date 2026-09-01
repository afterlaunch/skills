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
AXES = Path(__file__).resolve().parent.parent / 'AXES.md'
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

    # The calibration reads the product context before the first pair, so the
    # pairs are about this business rather than about writing in general.
    check('reads the product context before calibrating',
          '~/.claude/content/product-context/PRODUCT.md' in text)

    # House style: no em-dash, no exclamation mark, British spellings only.
    check('no em-dash', '\u2014' not in text)
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
          verbs <= {'update_draft', 'get_move', 'list_feed', 'get_kb_page',
                    'get_voice_profile', 'record_insight'})

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

    # --- Train 1: two voices, and the record is home. -------------------

    # THE OPENING (research dossier section 9, founder-accepted verbatim). The
    # user meets the two-voice idea here first, so the paragraph is pinned
    # rather than paraphrased. Flattened, so re-wrapping the markdown is a
    # good change that must not fail this.
    opening = (
        'There are two voices here. Your brand has one, and it is on your '
        'website, so we have already read it. You have one too, and it is '
        'different: it is how you write when it is you talking, on LinkedIn, '
        'on X, in a Reddit reply. The website cannot teach us that one. You '
        'can, in about two minutes, by picking between pairs of sentences '
        'until it is clear which way you lean. Pages and listings get the '
        'brand voice. Anything posted as you gets yours.')
    offline = (
        'There are two voices here. Your brand has one, and it is on your '
        'website. You have one too, and it is different: it is how you write '
        'when it is you talking, on LinkedIn, on X, in a Reddit reply. The '
        'website cannot teach us that one. You can, in about two minutes, by '
        'picking between pairs of sentences until it is clear which way you '
        'lean.')
    flat_all = re.sub(r'[\s>]+', ' ', text)
    check('first-run opening paragraph present verbatim', opening in flat_all)
    # With no key nothing read the site, so the offline variant drops the
    # clause claiming we did and the two sentences about which surface gets
    # which voice, because there is no brand register to give them.
    check('offline variant of the opening present', offline in flat_all)
    # The one word the dossier found the confusion living in.
    check('states the rule: the site register is the brand\'s, never "your voice"',
          'Never call the brand register "your voice"' in re.sub(r'\s+', ' ', text))

    # The connected section is sliced out once and the next three checks run
    # against that slice only, so a phrase in the offline half cannot satisfy
    # a rule about the connected half.
    start = text.find('## With AfterLaunch connected')
    end = text.find('## House rules', start + 1)
    check('connected section is present and bounded', start != -1 and end > start)
    connected = re.sub(r'\s+', ' ', text[start:end] if start != -1 and end > start else '')

    # THE WRITE-BACK. Every lean goes back to the record as a voice insight,
    # one per axis. Without this the calibration dies in the terminal.
    check('connected section sends every lean back as a voice insight',
          'record_insight' in connected and 'kind `voice`' in connected)
    check('the write-back is one insight per axis',
          re.search(r'per axis', connected) is not None)
    check('a thin axis is not sent',
          'too few observations' in connected and 'not sent' in connected)
    # The record supersedes by the text, so a count in the sentence means no
    # two rounds ever collapse onto each other.
    check('the insight sentence is stable per axis and lean',
          'stable for the same axis and the same lean' in connected)
    # THE TWO REGISTERS. Both are read before the first pair, each asked for by
    # name, so the user sees the brand's voice and whatever the record already
    # believes about their own before picking anything. Reading one register
    # and calling it the voice is the confusion this whole train exists to end.
    check('connected section reads the brand register before the first pair',
          'get_voice_profile' in connected and 'register `brand`' in connected)
    check('connected section reads the personal register too',
          'register `personal`' in connected)
    # An account with no uploaded writing answers has_profile false, which is an
    # answer and not an error, so the skill has to say so plainly rather than
    # show an empty box or invent a personal voice from the site.
    check('connected section handles an empty personal register honestly',
          '`has_profile` is false' in connected
          and 'no personal voice is on record yet' in connected)

    # TIER ONE VERIFIES ITSELF. A deployment that validates loosely ignores an
    # unknown argument instead of rejecting it, so the register-set call can
    # come back holding the current row. Comparing the returned field to the
    # one asked for is what stops a brand row being labelled personal.
    # Scoped to has_profile true, because a register with no row honestly
    # answers has_profile false with a null register, and reading that null as
    # an ignored parameter would drop a tier and swallow the "no personal voice
    # on record yet" message this train exists to deliver.
    asked = connected.find('only where `has_profile` came back true')
    check('tier one checks the returned register equals the one asked for',
          asked != -1 and '`register` field equals the one you asked for' in connected
          and 'label by the field that came back' in connected
          and 'the parameter was ignored' in connected)
    check('the tier-one self-check is scoped to a profile that exists',
          'A false `has_profile` returns a null register' in connected
          and 'not an ignored parameter' in connected)

    # THE THREE TIERS, in order. Tier 2 is an older deployment whose tool takes
    # no register; tier 3 is a deployment with no such tool at all. Each is
    # labelled, so no tier ever shows a register the user cannot name.
    rejected = connected.find('rejected because the tool does not take a register')
    absent = connected.find('tool is absent entirely')
    page = connected.find('about-my-voice')
    check('connected section degrades when the register parameter is rejected',
          rejected != -1 and 'no parameter' in connected
          and '`register` field in the response' in connected)
    check('connected section keeps the rendered page as the last tier',
          absent != -1 and page > absent and 'get_kb_page' in connected
          and 'fall back' in connected)
    # The page carries two labelled sections as of this train, so the last tier
    # labels by heading and only calls the whole page the brand's when it is the
    # old single-section shape.
    check('the last tier labels by the page sections, not the whole page',
          "\"Your brand's voice, read from your site\"" in connected
          and '"Your voice, from your writing"' in connected
          and 'single-section' in connected)
    check('the tiers are ordered: self-check, register rejected, tool absent',
          -1 < asked < rejected < absent)
    check('every tier is labelled with the register it is showing',
          'label' in connected and 'which register' in connected)

    # WHICH REGISTER THE ROUND WRITES. The leans go back as the founder's own
    # voice. A lean filed against the brand register would teach the website's
    # voice from the founder's picks, which is the inverse of the point.
    check('connected section says the leans it sends back are personal',
          'personal register' in connected and "never the brand's" in connected)

    # THE HOME. Connected, the record is the master copy and the local files
    # are a cache. Anything that reinstates the local model as the home is the
    # bug this train exists to fix.
    check('connected section names the record as home',
          'the record is home' in connected.lower())
    check('connected section calls the local files a cache',
          'cache' in connected)

    # THE AXES. Eleven, in exactly three labelled groups, because the groups
    # are what stop an unvalidated lean being read as a finding.
    axes_text = AXES.read_text(encoding='utf-8')
    groups: dict[str, list[int]] = {}
    heading = None
    for line in axes_text.splitlines():
        if line.startswith('## '):
            heading = line[3:].strip()
        row = re.match(r'\|\s*(\d+)\s*\|', line)
        if row and heading:
            groups.setdefault(heading, []).append(int(row.group(1)))
    numbered = sorted(n for ids in groups.values() for n in ids)
    check('AXES.md numbers eleven axes, 1 to 11, once each',
          numbered == list(range(1, 12)), f'got {numbered}')
    check('AXES.md sorts them into exactly three labelled groups',
          len(groups) == 3, f'got {sorted(groups)}')
    labels = ' '.join(groups).lower()
    for word, why in (('precedent', 'register and stance family'),
                      ('rhetorical', 'craft family'),
                      ('unvalidated', 'the unvalidated axis')):
        check(f'AXES.md labels {why}', word in labels)

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
