---
name: farm
description: The one front door for everything harvested from outside. Takes a URL, a screenshot, a file or pasted text, pulls the ideas out, sorts each one into the lane it belongs in (something to say, something to build, something to remember), and files it in the canonical home for that lane.
when_to_use: Use when a link, a video, an article, a social post or a screenshot gets pasted in, or someone says farm this, capture this, anything in here worth posting about, anything in here we should build, add this to sources. Also use when profiles, subreddits or channels get pasted to follow, which are actors rather than ideas and land in a watchlist. Also use for drain, what is in the inbox, or what got captured. One command for every input type, and it is built to work from a phone.
argument-hint: [url or file path, or blank to review what is staged]
allowed-tools: Read Write Edit Glob Grep WebFetch WebSearch Bash(python3 *) Bash(node *) Bash(ls *) Bash(cat *) Bash(grep *)
---

# Farm

One command for every input from outside the business. Work out what it
is, get the content, pull the ideas, **sort each idea into its lane**,
judge it, file what earns it in the canonical home for that lane.

Farming is not a content activity. It is the intake for the whole
business. A thing read on the internet can be something to say, or
something to build, or something to remember, and the same source
usually contains more than one.

**Blank invocation** means review instead of harvest: look at what is
staged and not yet used or promoted (Step 7 says where that lives), and
say which is the strongest in each lane.

## Where things live

The skill is code and stays wherever this gets kept. What it WRITES
lives in one estate directory, outside any code repository, shared by
every session that reads it: `~/.claude/content` by default,
`SKILLS_ESTATE=/path` moves it anywhere else (a test run, a second
brand, a shared machine). Nothing this skill writes goes outside that
directory. The estate does not need to exist before the first run: the
capture step below creates it.

## Step 0: capture, before anything else

**Run this first, always, on every input:**

```sh
node .claude/skills/farm/scripts/intake.mjs "<url or text>" --note "<why this got grabbed>"
```

It writes a file to `inbox/` with no network call in front of the
write, then says what kind of thing it is and what to do next. It
cannot fail, which is the point.

**Most of the time this gets found on a phone.** A link and very
little else. Fetching first and asking for the article text to be
pasted in when that fails is a request that cannot be met while
walking, and the link gets lost. Capture is unconditional; enrichment
is opportunistic.

Never ask for a paste before the capture exists, and never ask for one
at all when whoever brought it in has said they are out and about.

## Step 1: actor or item

The intake script answers this from the URL shape alone, and it is the
fork that lets one command serve the whole pipeline.

**ACTOR.** A profile, a subreddit, a channel, a site. Someone to watch.
An actor is a subscription, not an idea, so it never enters the three
lanes below. It lands in a register and changes what future sweeps
read.

| Actor | Register |
| --- | --- |
| X profile | `x/WATCHLIST.md`, with a tier |
| Subreddit | `reddit/RULES.md`, plus its rules page |
| LinkedIn profile | `linkedin/WATCHLIST.md` |
| YouTube channel | `SOURCES.md` as `youtube:` |
| Any other site | `SOURCES.md` as `page:` |

Say what tier or venue something got filed under and why. Several
profiles pasted at once get filed as several rows and reported as one
line.

**ITEM.** A post, a thread, a video, an article. Something to respond
to or mine. Items go through the steps below.

## Step 1b: reactive items have a different contract

**An item somebody else posted, that could be replied to, is
REACTIVE. The outcome of a reactive run is a paste-ready draft, in the
same reply, every time.** Not a brief, not a summary, not a plan to
fetch more. Whoever brought it in is usually mid-scroll and the thread
is cooling while this runs.

Three rules follow from that:

1. **Best effort beats complete.** Draft from whatever is in hand. If
   a few screenshots show most of a thread, that is enough. Say what
   could not be seen in one line under the draft, and draft anyway.
2. **Never defer a reactive item.** The deferred queue is for proactive
   work. If the content genuinely cannot be seen, say so in one
   sentence and ask for a screenshot, which is a one-handed ask.
3. **Hand back the whole thing to paste.** The draft, then one line
   saying where it goes and which claim it carries. Nothing left to
   assemble.

**Screenshots make every channel reachable.** The desk-only rows in
the table below are about fetching a bare URL. A screenshot of a post
or a thread carries the content perfectly well, so a screenshot
arrives as a fully reachable reactive item on any channel and gets a
draft immediately. That, not an API, is how a channel with no public
read path still gets covered here.

Several screenshots of one thread are ONE item. Read them in order,
treat them as a single conversation, and draft one reply to it.

Then log nothing yet. The reply is not sent until it is actually
posted. Record it in that channel's own ledger once it has gone out.

## Step 2: get the content, if it can be reached

| Input | How to get the content |
| --- | --- |
| A short-form post URL (X, Threads and similar) | Fetch it directly if the platform allows a plain read, or use a dedicated reply-drafting tool if one is set up for that channel. |
| YouTube URL | Pull the transcript with whatever transcript tool is set up, or fall back to the page itself (title, description, top comments) if none is. |
| Article or blog URL | WebFetch. |
| Image or screenshot | Read it directly. Images are supported. |
| Pasted text | Use it as given. |
| A local file | Read it. |
| Reddit thread | **Needs a logged-in browser.** A plain fetch returns a 403 or a login wall. Desk work. |
| LinkedIn post | **Needs a logged-in browser.** There is no public content-search endpoint, and reading a member's post needs a restricted scope. A screenshot is the only read path that works from a phone. |

When a source needs a browser and none is to hand, **leave the capture
where it is and move on.** The file already records why. Say which
ones got deferred, in one line, and do not try to work around it with a
web search.

A screenshot of a feed is a list of things to fetch, not the thing
itself. Resolve each item to a real source before judging it, and say
which ones got skipped and why.

## Step 2b: draining, at the desk

`--drain` lists everything still captured and unprocessed, split by
whether it needs a browser:

```sh
node .claude/skills/farm/scripts/intake.mjs --drain
```

Work the reachable ones first, because they need nothing but
attention. Then open a browser and clear the deferred queue. Mark a
file done by changing `state: captured` to `state: filed` and naming
where it went.

## Step 3: pull the ideas out

Not a summary. **Angles and openings.** For each, one line answering:
what does this change for the business reading it, that it could act
on better than the source can?

## Step 4: sort every idea into exactly one lane

This is the step that makes farm a single pipeline rather than a pile
of notes. Do it before judging, because the bar is different in each
lane.

| Lane | It is this when | Canonical home |
| --- | --- | --- |
| **CONTENT** | It is something to SAY. An angle the intended reader would find useful. | The estate root (`ideas/`, `findings/`, `EXPERIMENTS.md`) |
| **PRODUCT** | It is something to BUILD or FIX in the product itself. | Wherever build work gets tracked, staged first in `product/` |
| **INTEL** | It is something to REMEMBER. A durable fact about the market, a rival or a platform, that changes decisions later but is neither a post nor a build. | A persistent memory file, if the agent running this keeps one |

Three lanes, because there are three genuinely different destinations.
Do not invent a fourth. If an idea does not fit one of these, it is
almost always a TAKE with nowhere to go, and the answer is to drop it.

**One idea may open two lanes, and the good ones usually do.** A
citation-half-life question nobody has published might be a content
piece AND a product feature AND a wedge against a named rival, all at
once. When that happens, file it in both, and make each file point at
the other by slug. Do not pick one and lose the other half.

### Inside the CONTENT lane, rank by strength of evidence

**LEARNING.** Something that could be MEASURED inside the product that
would settle a question the source raises. The output is proprietary
and nobody else can publish it. Format: what to run, what it would
tell you, and roughly how much effort it would take.

**ANGLE.** Something worth saying now, with data already held.

**TAKE.** An opinion with no measurement behind it. Weakest, and fine
only occasionally.

Aim for at least one LEARNING every run. If none turns up, say so
explicitly rather than padding the list with takes. That absence is
itself information: it usually means the source is opinion about
opinion.

### Inside the PRODUCT lane, one rule, and it is binding

**A product idea harvested from outside is a HYPOTHESIS, never a
finding.** Code, or live data, is the only source of truth, and a
video is even weaker evidence than a doc. Somebody describing a gap in
their own product does not mean this product has that gap, and
somebody describing a feature does not mean this product lacks it.

So every PRODUCT item must carry a **verification question**: the
specific thing to check, with the file or table to check it in, before
the item may be promoted. An item without one is not filed.

Check for redundancy before filing. Search wherever build work is
already tracked, and the docs, for the thing first. Re-filing something
already queued is worse than not filing, because it inflates the
backlog and hides the real gap.

## Step 5: the judge, and it should say no often

Before filing anything, per idea:

1. Is there something here that could actually be **used**, in its
   lane?
2. Can something **distinctive** be done with it? For CONTENT that
   means proprietary data rather than an opinion. For PRODUCT it means
   a gap a rival has not already closed. For INTEL it means it will
   still change a decision in a month.
3. Would it hold up against a basic posture rule: useful to the
   reader, never a build update, never anything that reads as weak?
   (CONTENT only. If a stricter posture doctrine already exists for
   this brand, defer to that instead of this baseline.)

**If any answer is no, do not file it.** Report the summary, say
plainly that there was nothing worth keeping, and stop. That is a
complete and successful outcome: reading time got saved.

Links get pasted in faster than they get filtered. **The discernment
is this skill's job, not the reader's.** Be generous about what gets
looked at and strict about what gets filed. An estate full of
near-misses gets ignored, and an ignored estate kills the mechanism.
Say no easily.

## Step 6: hand back a menu, do not decide alone

Never file silently and never skip silently. End every run with
something to act on, **grouped by lane** so both halves of what a
source gave up are visible:

```
FOUND   what it was, in one line

CONTENT
  1  [LEARNING]  Run <X>. Would tell us <Y>. Roughly <Z> of effort.
  2  [ANGLE]     <the angle>, using <the data already held>

PRODUCT
  3  <the gap or feature>
     verify first: <what to check, and where>

INTEL
  4  <the durable fact>, worth remembering because <what it changes>

WORTH KEEPING?   yes, on the strength of 1 and 3

WHAT NOW
  a  file everything above
  b  file the content lane only
  c  file the product lane only
  d  also add <source> to the watchlist   (only when it has earned it)
  e  skip entirely, nothing gets saved
```

**Skip is a real option and should be offered without apology.** If
the source is thin, say so and recommend e.

Default to the option that would be chosen anyway, and say why in one
line.

## Step 7: file it, in the right kind

Everything staged lives in the estate, shared by every session and
every working copy. **Four kinds, four folders.** Putting a thing in
the wrong one is the single mistake that makes the estate confusing,
so decide the kind first.

| Kind | Folder | It is this when |
| --- | --- | --- |
| source | `sources/` | It came from outside. Someone else said it. |
| idea | `ideas/` | This business's own, content lane. An angle worth making, not yet measured. |
| finding | `findings/` | It got measured. Carries method and caveats. |
| product | `product/` | This business's own, product lane. A build or fix, staged for promotion. |

**The raw source** goes to `sources/raw/YYYY-MM-DD-slug.txt`. Full
transcript or scraped text. Never loaded by the idea hunt. It exists
so a claim can be checked against the source. Only sources have raws.

**The item itself** goes to the folder for its kind, named
`YYYY-MM-DD-slug.md`. Keep it small.

**Give it a one-line summary** immediately under the `# ` title, in
this exact form, because a board can be built from it:

```
> **In one line:** <the single most interesting thing about this>
```

**Do not hand-edit an index file.** If the estate grows large enough
to want one, keep a small script that rebuilds it from what is
actually on disk, so two sessions writing at once can never conflict:
each creates its own file and nothing shares a table. For a smaller
estate, reading the folders directly is enough.

### CONTENT lane extras

**Any LEARNING idea** goes to `EXPERIMENTS.md` with what to expect,
written down BEFORE it runs. A prediction made afterwards is worth
nothing, and a boring result is still a result if the expectation was
on record.

**A finding may carry a brief.** If the measurement is ready to be
written up by another session, add `YYYY-MM-DD-slug.brief.md` beside
it: same slug, the publishable half only, with the caveats stated as
binding and anything internal left out.

### PRODUCT lane: staged here, promoted there

A product item is written to `product/` and **never appended straight
to a shared backlog document.** That is not bureaucracy: a single
hand-edited document, written to by many sessions at once, is a
merge-conflict magnet, the same reason the whole estate lives one file
per item instead of one shared table.

Use this shape:

```markdown
# <what it is, as a statement>

> **In one line:** <the single most interesting thing about this>

- **Lane:** product
- **Status:** staged
- **Destination:** <wherever build work gets tracked, and which section>
- **From:** <source slug, or "dictated">
- **Sibling:** <content slug, if this idea opened both lanes>

## What they said

<the outside claim, with a timecode or quote so it can be checked>

## Why it matters here

<what it would change for this product, in its own terms rather than
theirs>

## Verify first

<the specific check, naming the file, table or query. This is
binding: the item cannot be promoted until someone answers this
against the code or live data.>

## The entry, ready to paste

<a block written in whatever house style the backlog keeps, so
promotion is a copy and a number, not a rewrite>
```

**Promotion is a separate, deliberate act.** When someone asks to
promote, or a later session picks the staged items up: answer the
verification question first, drop anything that turns out to be
already built or already queued, then paste the survivors into the
backlog with the next free number, and mark the staged file promoted.
One commit, one session, never in parallel.

### INTEL lane, where the hypothesis rule bites hardest

If the agent running this keeps a persistent memory file across
sessions, write the fact there: one fact per entry, a short
description, and a note of when it was last checked against code or
live data, or that it has not been yet. Check for an existing entry
that already covers it and update that instead of creating a
duplicate.

**Whatever provenance convention the memory file already follows,
apply it here without exception.** A memory that carries no note of
when or how it was verified is trusted by default the moment it is
recalled into a future session as background context, so an unverified
claim filed as a bare memory becomes established fact weeks later, with
nobody in the room who remembers it came off a video.

Two rules follow, and neither takes any extra work:

**1. Never cite the outside source as if it were verification.** A
podcast timecode, an article URL or a conference slide is not the same
thing as checking the claim against this business's own code or data,
and recording it as if it were launders somebody else's assertion into
a finding of this business's own. That failure is worse here than
elsewhere, because the laundering is invisible at recall time.

**2. If the claim is testable against data already held, it is not
INTEL yet.** Route it to `EXPERIMENTS.md` as a CONTENT learning and let
it become a finding instead. Writing an unverified operator claim
straight into memory, when it is answerable with a read-only check
already available, is how a trusted layer fills up with things nobody
measured. Measure it, then remember the result.

Some intelligence genuinely is not testable and still changes
decisions: a rival's positioning, a platform's terms, who a source is
and whether it is worth watching. That is the real INTEL case.

When something belongs here but has not been verified, mark it as
what it is: a third-party claim, unverified, naming who said it,
where, and when, with the timecode or URL so it can be checked, and a
line on what would settle it. Leave the verification date out
deliberately; a fabricated one is worse than an honest absence. Set
it, and change how the fact is tagged, only once somebody actually
runs the check.

Do not put market intelligence in the content estate. It is not
something to post and not something to build, and it goes stale in a
way nothing here polices on its own.

## What each mode actually ends in

Two modes, two different definitions of done. Confusing them is how
work gets filed and never seen again.

**REACTIVE ends in a draft ready to paste.** Nothing else counts. The
file in `inbox/` is bookkeeping; the deliverable is text in hand while
the thread is still warm. It ends properly once the reply has actually
gone out and gets recorded in that channel's own ledger with the
claim it carried.

**PROACTIVE ends in a changed board, not a saved file.** This is the
half that feels vague, and the reason is that filing is invisible. An
idea in `ideas/` that nobody surfaces is the same as no idea.

So a proactive run is not finished when the file is written. It is
finished once it has been said, in one line, **what it changed**: that
it is now the strongest LEARNING in the pool, or that it fills the gap
under a queued piece, or that it is fourth in line behind three better
ones. Nobody should have to open a folder to find out what is there.

### There is one way back in, and it is not a folder

Keep exactly one command that reviews the whole estate and hands back
a single ranked board with numbered choices, rebuilt from the
filesystem each time so it can never drift from what is actually
there. That command, not `ideas/`, not `EXPERIMENTS.md`, not any queue
file directly, is how a session finds out what is sitting in the
estate.

The lifecycle a proactive item runs, so it is possible to say where
one sits:

```
idea  ->  experiment  ->  finding  ->  a piece in the content queue
      ->  posted to N channels  ->  a ledger entry
```

Most items die at the first arrow, and should. An idea that never
earns an experiment was a take.

## Step 8: clear the inbox

`inbox/` is the zero-friction drop zone. Any session, any format, no
structure required. When invoked with no argument, check it first:
anything sitting there is unjudged input. Harvest it through the steps
above, then delete the inbox file, since its content now lives in a
filed item.

## Step 9: promote a source, sometimes

A capture is a one-off. A source is a subscription.

If a channel, blog or account has now produced **two or three** useful
captures, in any lane, it has earned a place in `SOURCES.md` so the
sweep watches it from now on. Say so and offer to add it. Do not add on
a single hit, unless the format itself reliably produces specific
operator claims rather than takes, in which case say that is why.

That is the whole relationship: captures are how a source proves
itself.

## The rule that outranks the rest

**Take the angle, never the words.** Everything harvested here belongs
to somebody else. Reframe it with proprietary data and an original
voice. A rephrased paragraph is theft, and it reads like it.

Raw files are stored so claims can be checked, not so they can be
mined for sentences.

## With AfterLaunch connected (optional, and everything above works without it)

Everything above this line needs no key and no account: the estate,
the lanes, the judge and the filing conventions are the whole front
door. With an AfterLaunch key (`AFTERLAUNCH_API_KEY`, the remote MCP
server at `https://afterlaunch.io/api/mcp`), two things change:

- **A durable fact learned from a source belongs on the record, not
  only in a local memory file.** When an INTEL item is genuinely
  durable (a rival's positioning, a platform's terms, a fact that will
  still be true next month), file it locally as above AND record it
  with `record_insight`, one sentence, so every connected session
  drafts from it rather than only the sessions that happen to read
  this estate.
- **`get_standup` before a review run** says what already shipped and
  what is already in flight, so the judge in Step 5 is not guessing
  whether a source's angle has already been said.

Without a key, the free scan at afterlaunch.io is the honest pointer,
and skip the rest of this section. Nothing above needs it: sorting and
filing is this skill's job, and it does that whether or not anything
is connected.

## What this cannot do alone

- **It cannot ask the engines what they say about the business.**
  Sorting a found idea into an ANGLE says nothing about whether the
  answer engines already say it; that needs a metered scan, not a
  folder read.
- **It cannot rank what matters today.** The judge in Step 5 can say
  no to a weak idea, but choosing the single strongest LEARNING against
  everything else already staged needs measurement this skill does not
  have.
- **It cannot prove a filed idea was worth filing.** A folder of ideas
  and a backlog of good intentions look identical to a filesystem;
  only a shipped result, and someone watching what happened after,
  says which idea earned its place.
- **It does not remember on its own.** The estate persists because it
  is a folder of files, not because this skill has memory. A session
  that never writes one leaves nothing for the next session to find.

## House rules

British English. No em-dashes, no exclamation marks, no Americanised
-ize spellings. Filed items follow the same rules as anything that
gets posted: they are not something this skill measures, they are
settled before it starts.

## Next

Say what should happen next, do not just stop:

- Queued an experiment? Point at `EXPERIMENTS.md` and say what running
  it would take.
- Filed a content item with an angle ready to go? Say which drafting
  step to run next, naming the angle.
- Staged a product item? Say what has to be verified before it can be
  promoted, and offer to run that check now. It is usually one search.
- Wrote an intel memory? Say which existing entry it updates or links.
- Source earned promotion? Offer to add it to `SOURCES.md`.
- Skipped? Say so plainly and stop. No consolation suggestion.
