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

## Two voices, and which one this trains

Open a first run with this, before anything else. Connected, verbatim:

> There are two voices here. Your brand has one, and it is on your
> website, so we have already read it. You have one too, and it is
> different: it is how you write when it is you talking, on LinkedIn, on
> X, in a Reddit reply. The website cannot teach us that one. You can, in
> about two minutes, by picking between pairs of sentences until it is
> clear which way you lean. Pages and listings get the brand voice.
> Anything posted as you gets yours.

With no key nothing has read the site and there is no brand register to
hand, so the clause saying we already have comes out, and so do the two
sentences about which surface gets which voice:

> There are two voices here. Your brand has one, and it is on your
> website. You have one too, and it is different: it is how you write
> when it is you talking, on LinkedIn, on X, in a Reddit reply. The
> website cannot teach us that one. You can, in about two minutes, by
> picking between pairs of sentences until it is clear which way you
> lean.

Then ask which voice this round calibrates, and default to theirs.

**Never call the brand register "your voice".** It came from the website,
so it is the brand's. That one word is where the confusion lives.

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

Connected, both files are a cache of what was sent to the record, not the
master copy. See the connected section below.

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
   all eleven. On a later run, put the questions toward the axes with
   the fewest answers or the least agreement, because those are the
   ones still moving. Note which family an axis belongs to: a lean in
   the unvalidated group is reported as unknown signal, not as a
   finding.
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
`https://afterlaunch.io/api/mcp`), the record is where the voice lives and
the local files become a copy of what was sent. A site read already gives
you the brand register; the personal one is what only this test can reach.

- **Read the brand register first, before the first pair.** Call
  `get_voice_profile` with register `brand`. It returns the structured
  voice the product itself drafts in, tone and phrases and sentence style
  and what it avoids. Show it labelled plainly as the brand's voice, read
  from the site, so the user sees the contrast before being asked to pick
  anything, which is what the opening above is for. On either call that
  sets a register, and only where `has_profile` came back true, check the
  `register` field equals the one you asked for: a mismatch means the
  parameter was ignored, so treat it as the tier below and label by the
  field that came back. A false `has_profile` returns a null register and
  is the honest empty answer, not an ignored parameter.
- **Then read the personal register, in the same breath.** Call
  `get_voice_profile` with register `personal`. If `has_profile` is true,
  show it labelled as the founder's own voice already on record, taken
  from writing they supplied, so what the record already believes about
  how they write is on the table before the first pair and they can say
  there and then if it is wrong. If `has_profile` is false, say plainly
  that no personal voice is on record yet and that this round is what
  starts it.
- **Degrade honestly, three tiers, and label every one of them.** If the
  call is rejected because the tool does not take a register, which means
  an older deployment, call `get_voice_profile` with no parameter, read
  the `register` field in the response if it is there, and label what you
  show by that. If the tool is absent entirely, fall back to
  `get_kb_page` with slug `about-my-voice`, the rendered page of the same
  thing, and label by its two section headings when the page carries them,
  "Your brand's voice, read from your site" and "Your voice, from your
  writing", calling the whole page the brand's only in the older
  single-section shape. Whichever tier you land on,
  the user always knows which register they are looking at.
- **What this round trains is the personal register.** The leans it sends
  back as voice insights below are the personal one, never the brand's.
- **Send every lean back after the round.** For each axis with enough
  observations to state a lean, one `record_insight` with kind `voice`:
  one plain sentence in the user's own terms and nothing else, for example
  "Voice leans to short clipped sentences over flowing ones." Between ten
  and five hundred characters. One insight per axis, not one for the whole
  round. An axis with too few observations to read is not a lean and is
  not sent.
  **Keep that sentence stable for the same axis and the same lean.** No
  counts, no dates, no round number. The record supersedes an insight by
  the text itself, so a stable sentence means a repeat round replaces the
  earlier note cleanly, while a sentence carrying "7 of 9 picks" never
  matches the next round and the contradictions pile up. Known limit: an
  axis that FLIPS leaves the old sentence standing, because it is
  different text. Say so when it happens rather than pretending the record
  is clean.
  There is a daily cap of 50 insights per product run. If a call comes
  back `rate_limited`, stop sending, say so plainly, and note that the
  local cache still holds the round.
- **A draft already sitting on the board can be rewritten against the
  fresh profile and saved back.** Find it with `list_feed` or `get_move`,
  rewrite the copy against whatever this round changed, and save it with
  `update_draft`. The voice just calibrated then travels with every move
  that already has a draft, not only the ones written after this round.

**Connected, the record is home.** `profile.json` and `VOICE.md` are a
cache of what was sent: readable from a terminal, and they survive a
dropped connection. They are not the master copy. A correction that never
reached the record is a correction the product does not have.

Without a key there is nothing to send to, so the local profile is the
whole model, exactly as it works today, and `VOICE.md` travels only as far
as whatever reads that file by hand. The free scan at afterlaunch.io is the
honest pointer otherwise, and skip the rest of this section.

## House rules

British English. No em-dashes, no exclamation marks, no Americanised
-ize spellings. Every test item obeys these too: they are hard rules
this skill already follows, not something the calibration measures.

## Next

Once the profile exists, drafting is the next step, wherever drafts
get written. If the drafts still feel off after a few posts, run this
again: it will put the questions toward whatever is still unsettled.
