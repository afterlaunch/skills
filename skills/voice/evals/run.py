#!/usr/bin/env python3
"""voice evals: this skill is plain text and one JSON template, so most of
its evals are structural and publication lints over SKILL.md. The last block
is different: it EXECUTES the round procedure the prose states, because the
one thing prose cannot show is whether the rule it describes terminates.
Pure, offline, no network.

    python3 evals/run.py        # exit 0 = every eval passes
"""
from __future__ import annotations

import random
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / 'SKILL.md'
AXES = Path(__file__).resolve().parent.parent / 'AXES.md'
FAILURES: list[str] = []

NUMBER_WORDS = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6,
                'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11}


def check(name: str, ok: bool, detail: str = '') -> None:
    print(('PASS' if ok else 'FAIL'), name, detail if not ok else '')
    if not ok:
        FAILURES.append(name)


def as_number(token: str) -> int | None:
    """A count the skill states in prose, as a digit or as a word."""
    token = token.lower()
    return int(token) if token.isdigit() else NUMBER_WORDS.get(token)


def settle_bars(segment: str) -> list[int | None]:
    """Every settle bar stated in one segment of the skill, as numbers.

    Read out rather than matched. A substring check for the bar passes on a
    segment whose own clause now says something else, as long as a NEIGHBOUR
    still carries the number the check was looking for, which is the mutant
    QA landed: the LEAN clause moved from six to five and every check stayed
    green on the six in the VARIES clause beside it.
    """
    return [as_number(m.group(1))
            for m in re.finditer(r'([A-Za-z]+|\d+) or more observations', segment)]


def outcome(pair: tuple[int, int], bar: int) -> str:
    """One axis read the way the skill reads it: open, then LEAN or VARIES."""
    a, b = pair
    if a + b < bar:
        return 'open'
    return 'lean' if max(a, b) >= 2 * min(a, b) else 'varies'


def simulate(answer, axis_ids: list[str], bar: int, limit: int | None = None):
    """Execute step 2 as written, and report where it stops.

    Nothing here is invented. The first pass takes the axes in AXES.md order;
    after it, the next pair goes to the unsettled axis with the MOST
    observations, ties to the split closest to even, ties on that to AXES.md
    order; an axis retires at the bar either way. `answer` returns True for
    pole a, and is the only thing a respondent controls.
    """
    counts: dict[str, list[int]] = {axis: [0, 0] for axis in axis_ids}
    # Retirement flows through the ONE reading of an axis, so a rule where an
    # outcome fails to retire shows up here as a round that does not stop
    # rather than as a round that stops and quietly leaves axes open. The cap
    # is what turns that into a failed check instead of a hung eval.
    cap = limit if limit is not None else len(axis_ids) * max(bar, 1) * 4

    def open_axes() -> list[str]:
        return [x for x in axis_ids if outcome(tuple(counts[x]), bar) == 'open']

    asked = 0
    while asked < cap:
        remaining = open_axes()
        if asked >= len(axis_ids) and not remaining:
            break
        if asked < len(axis_ids):
            axis = axis_ids[asked]
        else:
            axis = min(remaining, key=lambda x: (-sum(counts[x]),
                                                 abs(counts[x][0] - counts[x][1]),
                                                 axis_ids.index(x)))
        counts[axis][0 if answer(axis, tuple(counts[axis])) else 1] += 1
        asked += 1
    return asked, {x: outcome(tuple(counts[x]), bar) for x in axis_ids}


def respondents(axis_ids: list[str]) -> dict:
    """Five ways of answering, each deterministic, none of them co-operative.

    The adversary is the interesting one: it answers to keep every split as
    even as it can, which under a lean-only settle rule holds each axis one
    short of settling for as long as it likes. It is the shape that did not
    terminate, and it is here so the claim that it now does is run rather than
    asserted.
    """
    counter = {'n': 0}
    biased = set(axis_ids[:6])

    def alternating(axis, pair):
        counter['n'] += 1
        return counter['n'] % 2 == 1

    rng = random.Random(11)
    return {
        'always the same pole': lambda axis, pair: True,
        'strict alternation': alternating,
        'seeded random, even odds': lambda axis, pair: rng.random() < 0.5,
        'three in four on six axes, even on five':
            lambda axis, pair: ((pair[0] + pair[1]) % 4 != 3 if axis in biased
                                else (pair[0] + pair[1]) % 2 == 0),
        'adversary holding every split even': lambda axis, pair: pair[0] <= pair[1],
    }


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
    verbs = set(re.findall(r'`(\w+_move|\w+_draft|record_insight|get_\w+|list_\w+|set_\w+|ship_move)`', text))
    check('ship_move never appears', 'ship_move' not in text)
    check('no verb beyond the declared surface',
          verbs <= {'update_draft', 'get_move', 'list_feed', 'get_kb_page',
                    'get_voice_profile', 'record_insight', 'set_voice_axes'})

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


    # --- Train 3 item 14: active selection, and a stopping rule. ---------

    # A pair buys less per judgement than a rating scale does, so the cost of
    # this mechanic is the NUMBER of judgements, and choosing the next pair is
    # the only thing that pays it back. The three parts are pinned separately
    # because a mutant that keeps the settled threshold while dropping the
    # selection rule reads perfectly well and measures the wrong axes forever.
    rounds_start = text.find('## How a round runs')
    rounds_end = text.find('## Reading the answers', rounds_start + 1)
    check('the round procedure is present and bounded',
          rounds_start != -1 and rounds_end > rounds_start)
    rounds = re.sub(r'\s+', ' ',
                    text[rounds_start:rounds_end] if rounds_end > rounds_start >= 0 else '')

    # SETTLED HAS TWO OUTCOMES, AND BOTH RETIRE THE AXIS. This is what makes
    # the stop reachable at all: under a lean-only rule an axis nobody leans on
    # is asked forever, so the round never ends. A VARIES outcome is the
    # deletion that fixes it, and the Reading section already blessed "varies"
    # as a real answer. That termination claim used to be a sentence in this
    # comment quoting an item number nobody could re-run. It is now the
    # simulator at the foot of this file, which executes the rule as written
    # against five respondents and fails if any of them does not stop.
    check('an axis settles two ways, a LEAN or VARIES, and both retire it',
          'LEAN' in rounds and 'VARIES' in rounds
          and re.search(r'both retire it', rounds) is not None)
    # EACH CLAUSE IS READ ON ITS OWN, then the numbers are compared. The two
    # clauses state the same bar twice, so the mutation that matters is one of
    # them moving, and that is invisible to any check that only asks whether
    # the segment contains a six somewhere.
    i_lean = rounds.find('a LEAN')
    i_varies = rounds.find('VARIES', i_lean + 1)
    lean_clause = rounds[i_lean:i_varies] if -1 < i_lean < i_varies else ''
    varies_clause = (rounds[i_varies:rounds.find('.', i_varies) + 1]
                     if i_varies != -1 else '')
    lean_bars = settle_bars(lean_clause)
    varies_bars = settle_bars(varies_clause)
    check('the LEAN clause states its own settle bar',
          len(lean_bars) == 1 and lean_bars[0] is not None, f'got {lean_bars}')
    check('the VARIES clause states its own settle bar',
          len(varies_bars) == 1 and varies_bars[0] is not None, f'got {varies_bars}')
    # The lean bar as a formula, not as words. "Two to one" reads as a ratio
    # nobody computes the same way twice at 6-3.
    check('the lean bar is stated as a formula, inside the LEAN clause',
          'majority >= 2 x minority' in lean_clause)
    check('a settled axis of either kind stops being offered',
          'stops being offered' in rounds)
    # It is a starting rule, not a result. No round has ever been run, so a six
    # presented as a finding would be a fabricated number in a published file.
    check('the six is marked a starting rule to be tuned, not a finding',
          'starting rule to be tuned' in rounds and 'not a measured finding' in rounds)

    # THE FIRST PASS IS LOAD-BEARING: every axis is asked once before any is
    # asked twice, so a round always has a reading on all eleven.
    check('the first pass covers every axis once before any repeat',
          re.search(r'first pass covers all eleven axes once', rounds) is not None)
    # And in a stated order, so two runs of a first sitting ask the same eleven
    # items in the same sequence rather than whatever order the reader imagines.
    check('the first pass takes the axes in AXES.md order',
          re.search(r'first pass covers all eleven axes once, in `AXES\.md`\s*order',
                    rounds) is not None)
    # NEAREST-FIRST, NOT FEWEST-FIRST. Fewest-first spreads answers thin and
    # maximises time to the first settled axis, which starves the write-back:
    # under it the first lean lands around item 57 and the founder sees nothing
    # in the round he is actually in. Nearest-first settles one by item 16.
    check('after the first pass the next pair goes to the axis with the MOST observations',
          re.search(r'unsettled axis with the MOST observations', rounds) is not None
          and 'nearest to settling' in rounds)
    # Asserted POSITIVELY. The old form checked only that the words "fewest
    # observations" were absent, which a rule deleted altogether also satisfies,
    # so the check that was meant to pin the selection criterion passed on a
    # skill that no longer had one.
    check('the selection rule names MOST observations as the criterion',
          re.search(r'the unsettled axis with the MOST observations, because it is '
                    r'the one\s*nearest to settling', rounds) is not None
          and re.search(r'fewest observations', rounds, re.I) is None)
    check('ties go to the split closest to even, then AXES.md order',
          re.search(r'\btie', rounds, re.I) is not None
          and 'closest to even' in rounds and '`AXES.md` order' in rounds)

    # THE STOP, all three ways it can happen. The bound is what guarantees
    # termination even when the axes themselves misbehave.
    check('the round ends when every axis is settled, at the bound, or when the user stops',
          'every axis is settled' in rounds and 'the user stops' in rounds
          and 'at the bound' in rounds)
    check('the bound is about twenty pairs first, twelve later',
          re.search(r'about twenty pairs on a first run and twelve on\s*a later one', rounds)
          is not None)
    check('the round says how many axes are still open, and offers the exit',
          'how many axes are still open' in rounds)
    # RULING 5: two status reports, not four. Step 6 above, and the
    # end-of-round summary below. Step 7 must not restate it.
    check('the status report is not restated inside the numbered steps',
          'which axes are settled and which are not' not in rounds)

    # ONE threshold, used twice. The write-up bar used to be four out of five,
    # a second and looser reading of the same word, so an axis could be
    # written as an instruction while the round still counted it unsettled.
    reading = re.sub(r'\s+', ' ',
                     text[text.find('## Reading the answers'):text.find('## What gets written')])
    reading_bars = settle_bars(reading)
    check('the write-up bar is the same two outcomes, on the same formula',
          'LEAN' in reading and 'VARIES' in reading
          and 'majority >= 2 x minority' in reading)
    # The formula alone was all this used to assert, so the Reading section
    # could state a different count from the round procedure and stay green.
    # An axis written up as an instruction on five observations while the round
    # still counts it open is the drift the single bar exists to prevent.
    check('the Reading section states the bar for both outcomes, not just the formula',
          len(reading_bars) == 2 and all(b is not None for b in reading_bars),
          f'got {reading_bars}')

    # THE END-OF-ROUND SUMMARY, the second and last status report. Three
    # states, because an axis that came out varies is answered, not pending,
    # and lumping it with the open ones is what the old wording did.
    written = re.sub(r'\s+', ' ',
                     text[text.find('## What gets written'):text.find('## The honest limit')])
    check('the end-of-round summary names lean, varies and open separately',
          'settled with a lean' in written and 'came out varies' in written
          and 'still open' in written)

    # --- Train 3 / D7: the settled axes write back to the fact. ----------

    wb_start = text.find('- **Write the settled leans back')
    wb_end = text.find('- **A draft already sitting', wb_start + 1)
    check('the axes write-back bullet is present and bounded',
          wb_start != -1 and wb_end > wb_start)
    wb = re.sub(r'\s+', ' ', text[wb_start:wb_end] if wb_end > wb_start >= 0 else '')

    check('the round writes the calibrated axes back with set_voice_axes',
          'set_voice_axes' in wb)
    # THE SCALE. strength is the share of the observations that fell on the
    # leaning side, so an even split is 0.5 and the server refuses anything
    # under it. Which values are reachable is then a CONSEQUENCE of the settle
    # bar rather than a free choice, so they are checked as arithmetic: every
    # value stated has to be its own split rounded to two decimals, and every
    # split has to total the same bar. The example this replaced (six of eight)
    # was not reachable at all, because an axis retires as its sixth
    # observation lands, and an unreachable example is a worked instruction to
    # send a number the scale cannot produce.
    check('the write-back carries a lean and a strength',
          '`lean`' in wb and '`strength`' in wb
          and re.search(r'share of[^.]{0,40}observations that fell on the lean', wb)
          is not None)
    check('strength is bounded, an even split at 0.5 and everything one way at 1',
          '0.5 is an even split' in wb and 'Nothing below 0.5 or above 1' in wb)
    splits = [(float(v), as_number(n), as_number(d))
              for v, n, d in re.findall(r'([01](?:\.\d+)?) \((\w+) of (\w+)\)', wb)]
    check('the write-back states the reachable strengths, each one its own split',
          len(splits) == 3
          and all(n and d and round(n / d, 2) == v for v, n, d in splits)
          and sorted(v for v, _, _ in splits) == [0.67, 0.83, 1.0],
          f'got {splits}')
    check('every reachable strength sits above an even split and at most 1',
          bool(splits) and all(0.5 < v <= 1 for v, _, _ in splits))
    wb_bars = sorted({d for _, _, d in splits})
    check('the splits in the write-back all total one bar',
          len(wb_bars) == 1 and wb_bars[0] is not None, f'got {wb_bars}')
    # AND THE FOUR PLACES AGREE. The skill states its settle bar in four
    # clauses that have to be one number: a reader implementing any one of them
    # implements all four. This is the check the substring form could not make,
    # because "is six in here somewhere" is true of a segment whose own clause
    # now says five.
    stated_bars = lean_bars + varies_bars + reading_bars + wb_bars
    check('every settle bar the skill states is the same number',
          None not in stated_bars and len(set(stated_bars)) == 1,
          f'got {stated_bars} (LEAN, VARIES, Reading, write-back)')
    # SETTLED ONLY. This is the mutation that would otherwise ship silently:
    # sending every axis writes a confident position for axes measured once,
    # and the fact the product drafts from would carry noise as instruction.
    # LEANS ONLY. A varies axis is a measured answer but not a position, and
    # writing it as one would teach the product a direction nobody picked.
    check('only leans are sent; a varies axis and an open axis are not',
          'LEAN' in wb and re.search(r'VARIES is not sent', wb) is not None
          and 'neither is an axis still open' in wb)
    # And a round that settled nothing makes no call at all, rather than an
    # empty one. The founder is told in a line; silence would read as a bug.
    check('no lean this round means the verb is not called at all',
          re.search(r'no axis settled with a lean this\s*round, do not call the verb at all', wb)
          is not None and 'say so in one line' in wb)
    check('the ids come from AXES.md rather than being invented per round',
          'AXES.md' in wb)
    # It writes the founder's own register. A calibrated lean filed against the
    # brand would teach the website's voice from the founder's own picks.
    check('the axes write-back is the personal register, never the brand',
          "own register and never the brand's" in wb)
    # Both degradations, named where the caller is standing. Asserted as the
    # SENTENCE, not as two words that happen to co-occur: "the verb is absent
    # and the insights are not sent either" contains both and says the
    # opposite. The spans between the anchors cannot cross a full stop and
    # cannot contain a negation, so an inverted clause fails.
    unnegated = r'(?:(?!\b(?:not|never|no|without|unless|cannot)\b)[^.])*'
    check('an absent verb degrades to the insights, said plainly',
          re.search(r'If the verb is absent,' + unnegated + r'say so plainly:'
                    + unnegated + r'the voice insights above carry the round', wb)
          is not None)
    # RULING 5: ONE rate_limited statement, covering every write to the record,
    # stated once. It used to be said twice in near-identical words, which is
    # the shape that drifts apart on the next edit.
    check('rate_limited is handled once, for any write, in the connected section',
          connected.count('`rate_limited`') == 1
          and 'any write to\n  the record'.replace('\n  ', ' ') in connected
          and 'local profile still holds' in connected)

    # And with no key at all there is one home, stated as such.
    check('without a key, profile.json is the only home the round has',
          '`profile.json` is the only home' in re.sub(r'\s+', ' ', text))

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
    ids = re.findall(r'^\|\s*\d+\s*\|\s*`([a-z_]+)`\s*\|', axes_text, re.M)
    check('AXES.md gives every axis a stable id, which is what set_voice_axes writes',
          sorted(ids) == sorted([
              'sentence_length', 'register', 'address', 'certainty',
              'technical_density', 'self_reference', 'formality',
              'opening', 'evidence_order', 'closing', 'humour']),
          f'got {ids}')

    labels = ' '.join(groups).lower()
    for word, why in (('precedent', 'register and stance family'),
                      ('rhetorical', 'craft family'),
                      ('unvalidated', 'the unvalidated axis')):
        check(f'AXES.md labels {why}', word in labels)

    # --- The round, executed. --------------------------------------------

    # A round that does not stop is the failure this procedure was rewritten to
    # fix, and prose cannot show termination. So the rule is run: the real axis
    # list in its real order, the bar the skill itself states, and five
    # respondents who between them cover the unanimous case, the even case, the
    # random case, the mixed case and the adversarial one.
    bar = wb_bars[0] if len(wb_bars) == 1 and wb_bars[0] else 0
    expected = len(ids) * bar
    for name, answer in respondents(ids).items():
        asked, outcomes = simulate(answer, ids, bar)
        check(f'the round terminates with every axis settled: {name}',
              bar > 0 and asked == expected
              and all(o != 'open' for o in outcomes.values()),
              f'stopped at {asked} of {expected}, outcomes {outcomes}')
        # And the first sitting is worth sitting through: the bound cuts the
        # round off long before every axis is settled, so something has to have
        # closed by then or the founder answers twenty pairs for nothing.
        sat, partial = simulate(answer, ids, bar, limit=20)
        check(f'a first sitting bounded at twenty pairs settles an axis: {name}',
              sat == 20 and any(o != 'open' for o in partial.values()),
              f'{sat} items, outcomes {partial}')
    check('eleven axes at the stated bar is a round of 66 items',
          expected == 66, f'got {len(ids)} axes at a bar of {bar}, so {expected}')

    print(('OK' if not FAILURES else 'FAILED'), f'({len(FAILURES)} failures)')
    return 1 if FAILURES else 0


if __name__ == '__main__':
    sys.exit(main())
