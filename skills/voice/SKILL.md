---
name: voice
description: Calibrate the writing voice with a short forced-choice test. Shows pairs of sentences and asks which is closer to your brand, then turns the answers into a voice profile every posting skill reads.
when_to_use: Use on first setup of a posting workflow, when someone says calibrate my voice, run the voice test, set up posting, tune the voice, or the drafts do not sound right. Also use after a run of posts to nudge the profile rather than rebuild it. Anyone forking this skill runs it first.
argument-hint: [blank for a normal round, or "full" for a first calibration]
allowed-tools: Read Write Edit Glob AskUserQuestion Bash(cat *) Bash(ls *)
---

# Voice calibration

A forced-choice test, not a writing exercise.

**Why this way.** Asking someone to produce ten sample posts is
friction dressed up as rigour. Most people cannot think of what to
write on the spot, the samples overfit to whatever mood they were in,
and the people who most need a calibrated voice are exactly the ones
who will not do the homework. Then the drafts read generic and the
tool gets blamed.

Picking between two sentences takes two seconds and needs no ideas. Do
enough of them and a position emerges that no single sample could
give.

## Where things live

Two files, in the estate this suite shares: `voice/` under
`SKILLS_ESTATE`, which defaults to `~/.claude/content`. Create the
directory if it is not there.

The location matters more than it looks. `draft` reads the profile from
exactly this path, so a voice written somewhere else is a voice no draft
ever uses. One estate, configured once, is the whole convention: every
skill in the suite reads and writes its own subdirectory of it.

| File | What it is | Written by |
| --- | --- | --- |
| `profile.json` | The raw state: per axis, the observation count and the split, plus the date of each round. Resumable by design. | every round |
| `VOICE.md` | The style section rewritten as instructions a writer can follow. Written once there is enough to say something, not before. | every round with enough observations to update |

## How a round runs

Read the product context before the first pair. It is
`product-context/PRODUCT.md` in the same estate
(`~/.claude/content/product-context/PRODUCT.md` by default) and it says what
this business is, who it is for, and which words it keeps and refuses. The
pairs are then drawn from your own subject matter rather than from writing
in general, and a refused word never turns up in a sentence you are asked to
prefer, which would teach the profile the opposite of what you decided. If
the file is not there, say so in one line and calibrate anyway: the test
still works, the pairs are just blunter.

1. **Read `profile.json`** if it exists. This is resumable: a round
   adds to what is there rather than starting again.
2. **Choose which axes to test.** Read `AXES.md`. On a first run, cover
   all ten. On a later run, put the questions toward the axes with the
   fewest answers or the least agreement, because those are the ones
   still moving.
3. **Write the items fresh.** Do not reuse pairs from a previous round;
   repeating an item measures memory rather than taste. Follow the
   item-writing rules in `AXES.md`: one axis varying, everything else
   held still, both options obeying whatever hard style rules already
   exist for this brand (a banned-word list, a formatting rule,
   contractions on or off).
4. **Ask in rounds of four** using AskUserQuestion. Each question is
   one pair, the two options are the two poles, and the axis is never
   named. Naming it invites a theory about oneself instead of a
   reaction.
5. **Score.** Each answer is one observation on one axis. Store the
   count and the split.
6. **Stop at about twenty items** on a first run, twelve on a later
   one. Long tests get abandoned halfway and half a test is worse than
   none.
7. **Write the profile**, then say what changed.

## Reading the answers

Per axis: how many observations, and how lopsided.

- **Four or more one way out of five or more** is a real position.
  Write it as an instruction.
- **A near-even split** is not indecision, it is context-dependence.
  Write it as "varies", and the writer should take its cue from the
  format rather than from the profile.
- **Fewer than three observations** is not a reading. Say so and
  prompt another round rather than inventing a position.

Never present a thin result as settled. A confident profile built on
four answers is worse than an honest "not enough yet", because
everything downstream trusts this file.

## What gets written

**`profile.json`**, updated every round with the new counts and split
per axis, plus the round's date. This is what makes the next run a
nudge rather than a rebuild.

**`VOICE.md`**, rewritten as instructions a writer can follow. Not
"sentence length: 0.7 toward short" but "Keep sentences short. One
clause, usually." Include the axes that came out even, marked as
varying, because knowing what is NOT fixed is useful too.

Then say plainly which axes are solid, which are still moving, and
how many rounds it would take to firm them up.

## The honest limit, and what to do about it

**This measures taste, not habit.** It captures what someone thinks
sounds like them, which is not always how they actually write. Real
samples carry rhythm, tics and word choices no preference test can
reach.

So the two methods are complements, not rivals, and the order
matters:

- **The test first**, because it works immediately and needs nothing.
- **Samples later**, gathered from posts that actually went out and
  landed. Keep those in a `samples/` folder next to `VOICE.md`.

That turns samples from homework into a byproduct. Nobody has to sit
down and invent them; they accumulate from doing the thing anyway.
Re-run this test after a stretch of posting and the profile firms up
from both directions at once.

That is also the edge of what this skill can do alone. It cannot ask
the engines whether writing in this voice earns more attention than
the alternative would; it cannot rank one calibrated axis against a
real result; and it cannot prove a post performed because it matched
the profile. All three need a measurement this test does not have.

## With AfterLaunch connected (optional, and the test works the same without it)

The calibration itself needs no key: the pairs, the scoring and the
profile it writes are the whole test. With an AfterLaunch key
(`AFTERLAUNCH_API_KEY`, the remote MCP server at
`https://afterlaunch.io/api/mcp`), the profile stops being a file only
this skill reads:

- **A draft already sitting on the board can be rewritten against the
  fresh profile and saved back.** Find it with `list_feed` or
  `get_move`, rewrite the copy against whatever this round changed,
  and save it with `update_draft`. The voice just calibrated then
  travels with every move that already has a draft, not only the ones
  written after this round.

Without a key, `VOICE.md` travels only as far as whatever reads that
file by hand. The free scan at afterlaunch.io is the honest pointer
otherwise, and skip the rest of this section.

## House rules

British English. No em-dashes, no exclamation marks, no Americanised
-ize spellings. Every test item obeys these too: they are hard rules
this skill already follows, not something the calibration measures.

## Next

Once the profile exists, drafting is the next step, wherever drafts
get written. If the drafts still feel off after a few posts, run this
again: it will put the questions toward whatever is still unsettled.
