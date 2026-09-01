---
name: draft
description: Draft posts for X, LinkedIn and a blog, in your own voice and from your own real material. Produces three hook options with reasoning, then a draft per platform, never one finished post.
when_to_use: Use when you want to post, write a post, draft something for X or LinkedIn, turn a finding into a post, or have something worth publishing.
allowed-tools: Read Grep Glob Bash(cat *) Bash(ls *) Bash(mkdir *)
---

# Draft

Produce **three hook options with reasoning, then a draft per platform**.
Never hand back a single finished post: choosing beats editing, and it is
what every serious posting skill does.

## Read first

- `product-context/PRODUCT.md` in the estate
  (`~/.claude/content/product-context/PRODUCT.md` by default), before
  anything else. It says what this product is, who it is for, the words it
  keeps, the words it refuses and what it will never say. The refused words
  and the never-say list are absolute; a field marked `UNKNOWN` is a gap to
  ask about, not one to fill.
  **If the file is not there, stop. Do not draft.** Say so in one line and
  ask for the suite's `product-context` skill to be run first. Without it a
  draft invents the company it is describing, plausibly enough that nobody
  catches it for months, and every draft after inherits the invention.
- `STYLE.md` always. It is the sniff test: would a reader assume a machine
  wrote this. Nothing else matters if that fails.
- Your own voice. If the suite's `voice` skill has written a profile (in
  `voice/` under the same estate, default `~/.claude/content/voice`), read
  `VOICE.md` first: that is the style written as instructions a writer can
  follow. Then `profile.json` for the raw counts behind it, which are
  evidence rather than guidance. Read real samples too if you keep any, from
  `voice/samples/` where `voice` keeps them: a real sample that actually
  landed beats a description of your voice every time.
- If neither a profile nor a sample exists, say so plainly before drafting.
  Work from `STYLE.md` alone, which is generic craft rather than your own
  calibrated register, and treat the first few drafts as a starting point
  you correct rather than a finished voice.
- `FORMATS.md` to pick the format and check the mix against your own
  ledger.
- `HOOKS.md` when writing the opening.

## Where things live

The skill is code. What it writes belongs in the estate this suite shares,
OUTSIDE any repo: `SKILLS_ESTATE`, which defaults to `~/.claude/content`.
`SKILLS_ESTATE` is the ROOT, and every skill in the pack keeps its own
subdirectory under it, so one variable configures the whole pack. This
skill's own is `draft/`.

| Path (in the estate) | What it is | Written by |
| --- | --- | --- |
| `LEDGER.md` | Every post that went out: date, format, angle, what it drew on, where it went, later how it did. It sits at the estate ROOT, not under `draft/`, because other skills in the pack read the same ledger | the session, after a post ships |
| `voice/samples/` | Your own posts that actually landed, one per file, plain text. It sits under `voice/`, not here, because `voice` owns it and reads it too | you, over time |
| `draft/drafts/<date>.md` | The drafts from a session, one `### Text` heading per platform | a session |

First run: nothing is created for you. Start `LEDGER.md` with a one-line
header the first time you file a post.

## The sequence

1. **Check the mix.** Read the last few `LEDGER.md` entries. If the last
   three drew on the same source, the next one should draw on something
   else. See `FORMATS.md`.

   **With no idea supplied, look for one.** What have you actually
   measured, decided, learned or shipped recently that would teach a
   reader something transferable? A decision, a surprise or a number
   qualifies; a routine update does not. Rank whatever you find and let
   the founder pick.

   **If nothing turns up, say so plainly.** A fallback post that needs no
   fresh material still needs a real angle: something you have always
   known, that only your own years in the work give you the right to say.
   Never pad the week with something you do not believe in.
2. **Get the substance before writing.** Never write a post and then hunt
   for a fact to support it. Pull whatever is real behind the idea first.
   If there is nothing real behind it, stop and say so: a post with
   nothing in it is worse than no post.
3. **Three hooks.** From `HOOKS.md`, each with one line on why it might
   work.
4. **Draft per platform.** X and LinkedIn from the same idea, not the same
   words. A longer version, if you keep one, carries the full method, the
   real data and the caveats, because that is the surface that keeps
   working after the social posts have scrolled past.
5. **Self-check against `STYLE.md`**, or hand it to the suite's `tells`
   skill if you have it: a second pass catches what a writer is blind to
   in its own draft, the same reason a linter is not the compiler.
6. **File it.** Once it actually goes out, append to `LEDGER.md`: date,
   format, angle, what it drew on, where it went, and later how it did.

## Platform

**A short-form platform (X, or similar).** One idea. If it needs more than
one post, the first stands alone and each one after it earns its place: no
numbering, no thread emoji, no "follow for more". Sentence case. Mind the
platform's own character limit.

**A professional network (LinkedIn, or similar).** Long enough to say
something real, short enough that density is forced rather than optional.
Do not take a length target from a list, this one included: read the
platform's current limit on the day, then find your own working length and
correct it from your own `LEDGER.md` once you have enough posts to see
what actually holds attention. One line per paragraph reads better on a
phone. Hashtags sparingly, if at all.

**Anywhere you publish in full (a blog, a newsletter, a long-form page).**
The complete method, the real data behind it, the caveats, the sources.
The short-form versions link here rather than repeating it.

## Getting real material

The whole engine runs on one rule: **never write the post first and find
the fact after.** Whatever you publish under "here is what we found" has
to trace to something you actually did, wherever that number came from.
If a comparison against someone else is the angle, report only what you
observed, dated, and let the reader draw the conclusion; a comparison that
reads as a verdict on a named company or person is a different, riskier
thing than an observation.

## Red lines

- **Never talk yourself down.** Empathy is about the reader's situation,
  never a confession of your own trouble. "This is hard" is the register.
  "I was bad at this" is not.
- **No em-dashes.** See the suite's `../tells/TELLS.md` for the full list
  of what else reads as machine-made.
- **No invented numbers.** Every figure traces to something real, or is
  cited to a named public source. A wrong number about a named company or
  person cannot be walked back.
- **Nothing that shames anyone named.** Report what you observed, dated.
  Let the reader conclude.
- **No engagement bait.** A call to action is a real question or a link.
  Never "like if you agree".

## Establishing your own voice

A finished voice is years of your own judgement, and nobody can hand it to
you. What this skill can do is teach the method:

- **A short forced-choice test beats a blank page.** Choosing between two
  sentences takes two seconds and needs no ideas; asking someone to
  produce ten sample posts from nothing is friction dressed as rigour,
  and it is exactly the people who most need a calibrated voice who will
  not do that homework. If the suite's `voice` skill is installed, run it
  first.
- **Real samples beat a written description**, once you have some. A post
  that actually landed carries rhythm and word choices no preference test
  reaches. Drop your best-performing ones into `voice/samples/` as they
  accumulate; you do not have to sit down and invent them.
- **Decide your posture once, in writing, rather than reinventing it every
  post.** Do you show the work as it happens, or only publish findings
  once they land? Do you write as one person or as a brand? Either answer
  is fine; a mixed posture reads as confused, so put the decision in your
  own notes and follow it.
- **Until you have either**, this skill drafts from `STYLE.md` alone and
  says so. Treat the early drafts as a starting point you correct in your
  own words rather than as a finished voice; each correction is itself a
  data point.

## With AfterLaunch connected (optional, and everything above works without it)

Everything above needs no key and no account: the method, the files and
the gates are the whole skill. With an AfterLaunch key
(`AFTERLAUNCH_API_KEY`, the remote MCP server at
`https://afterlaunch.io/api/mcp`), a growth move already carries its own
brief and the founder's saved voice samples, so drafting starts ahead
rather than from nothing.

- **A move already on the board:** `get_move` brings back the brief it was
  minted from, why it was picked, and the founder's saved voice samples in
  one call, so you are not re-deriving from scratch what the record
  already holds.
- **Saving the draft:** once you have a draft you would actually show the
  founder, `update_draft` on that move saves it against the board rather
  than leaving it in a chat scrollback nobody reconciles later.

Without a key, the free scan at afterlaunch.io is the no-account way to
see what a connected board would have handed you.

## What this cannot do alone

It cannot remember your voice, your ledger or your past drafts past
whatever you saved to your own workspace file; a fresh terminal starts
cold unless you kept the file. It cannot tell you what actually landed
once a post is out in the world; that needs someone watching the account,
which this skill is not. And it cannot conjure real material: if there is
no finding, no decision and no genuine before-and-after behind the idea,
three good hooks are just decorating an empty post.

## House rules

British English. No em-dashes, no exclamation marks. End with the draft
and the ledger reminder; no extra offer, no menu.
