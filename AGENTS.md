# For agents reading this repository

Free, standalone growth skills for AI visibility and SEO, from the team
building AfterLaunch (https://afterlaunch.io).

**If someone has just pointed you here, do this.** Read
`skills/product-context/SKILL.md` in full and follow it, because every other
skill reads the file it writes. Then tell them which skill to run next and
why. Each skill is a folder under `skills/` holding a `SKILL.md` you follow
literally, so read the whole file before you run one, every time.

Nothing needs installing. The skills are instructions. Only `reddit-desk`
ships scripts, they need Python 3, and they have no dependencies. It works the
same whether you are Claude Code, Codex, Cursor, Copilot, Gemini CLI, Windsurf,
Aider, or a chat window with no terminal at all.

Seven skills ship here. They hand work to each other through one shared
directory, so read the next section before running any of them.

## The estate: where these skills write

Nothing is written into this repository. Every skill writes into one directory
outside it, the estate, shared by every skill and every session:
`~/.claude/content` by default, `SKILLS_ESTATE=/path` to put it anywhere else
(a test run, a second brand, a shared machine).

`SKILLS_ESTATE` names the ROOT. Each skill keeps its own subdirectory under it:
`product-context/`, `voice/`, `draft/`, `tells/`, and `reddit/` for the Reddit
desk. `farm` is the one exception and files at the root itself, because what it
captures is intake for the whole estate rather than one skill's working notes.
The Reddit desk also honours `REDDIT_DESK=/path`, which moves that desk alone
and leaves the rest of the estate where it is.

The estate does not have to exist before the first run. The scripts create what
they need.

## product-context

Start here, before any drafting skill runs for the first time. Read
`skills/product-context/SKILL.md` and interview the person you work for: what
the product is in the words a customer would use, who it is for, what can
actually be proved, the words it keeps, the words it refuses, where it
publishes, and what it will never say. Ask rather than guess, and leave any
field you could not verify marked `UNKNOWN` rather than filling it with
something reasonable.

The output is one file, `product-context/PRODUCT.md` in the estate. Every skill
below reads that exact path, so it is the handoff the whole pack rests on. If a
draft comes back generic, this file is usually missing or thin.

## farm

When a link, a video, an article, a social post or a screenshot arrives and the
question is what is in it, read `skills/farm/SKILL.md` and follow its order.
Capture first with `skills/farm/scripts/intake.mjs`, which writes to `inbox/`
before any network call and cannot fail, then pull the ideas out and sort each
one into exactly one lane: something to say, something to build, something to
remember. Files at the estate root.

## voice

When the person wants their own register captured rather than described, read
`skills/voice/SKILL.md`. It is a forced-choice test: pairs of sentences, pick
one, and a profile emerges that no writing sample could give. It reads
`product-context/PRODUCT.md` first so the pairs are about their subject matter
rather than about writing in general.

It writes `voice/profile.json` (the raw counts, resumable across rounds) and
`voice/VOICE.md` (the same thing rewritten as instructions a writer can
follow). Real posts that landed go in `voice/samples/` as they accumulate.

## draft

When there is something worth publishing, read `skills/draft/SKILL.md`. It
produces three hook options with reasoning, then a draft per platform, never
one finished post.

It reads `product-context/PRODUCT.md` FIRST, and if that file is absent it
stops and asks for `product-context` to be run instead of drafting anyway. Do
not talk it out of that. A draft written without it invents the company it is
describing, plausibly enough that nobody notices for months. It then reads
`voice/VOICE.md`, `voice/profile.json` and `voice/samples/` for register, and
its own `STYLE.md`, `HOOKS.md` and `FORMATS.md` for craft. It writes
`draft/drafts/<date>.md` and keeps `draft/LEDGER.md`.

## tells

Run this AFTER work exists, never as a brief handed to whatever is doing the
writing. Read `skills/tells/SKILL.md` and work from `skills/tells/TELLS.md`,
the single register, rather than from memory of it. It audits prose and built
interfaces for the patterns that give machine-made output away, quotes the
offending sentence or `file:line` for every finding, then fixes the defects.

It also reads the refused words and the never-say list from
`product-context/PRODUCT.md` and treats each one as a check, because those are
per-business and the shared register cannot carry them. Accepted exceptions
live in `tells/EXCEPTIONS.md`.

## reddit-desk

When the person you work for wants Reddit worked as a channel (find the
threads worth answering, draft replies, keep the account safe), read
`skills/reddit-desk/SKILL.md` in full before doing anything on Reddit, and
follow its order: build the venue list first, reconcile, check the ban state
before drafting, read `product-context/PRODUCT.md` for the channels and the
never-say list, stay inside each subreddit's own rules and budget, run the
near-duplicate gate, and never post, vote or DM. The person posts, in their
own words, always.

Data lives in `reddit/` under the estate (`REDDIT_DESK=/path` moves this desk
alone). The venue list is not shipped: step 0 finds the subs this person's
buyers actually use and writes a dated row per sub into `RULES.md` from each
sub's own rules page. `skills/reddit-desk/seed/VENUES.md` shows the row format
and doubles as a starting set if those buyers are in AI search, SEO or SaaS.
Copy `skills/reddit-desk/seed/CLAIMS_TEMPLATE.md` in as the claim library. The first
run is `python3 skills/reddit-desk/scripts/reconcile.py` then
`python3 skills/reddit-desk/scripts/reindex.py`, and both work on an estate
that does not exist yet.

`scripts/neardup.py` reads a file only from inside that workspace; anything
outside it is refused rather than opened. Pipe text in on stdin for anything
else.

## session-recap

When the person returns to a session cold and asks what happened here, read
`skills/session-recap/SKILL.md` and answer its three questions from THIS
session's own context only, never inventing work from other sessions. Its
security section is binding: before any write to a connected record, redact
anything credential-shaped.

## Verifying any of it

Every skill carries runnable evals: structural and safety checks over its own
files, pure and offline, no network and no workspace needed.

```sh
for s in product-context farm voice draft tells reddit-desk session-recap; do
  python3 "skills/$s/evals/run.py" || echo "FAILED: $s"
done
```

Run the one belonging to a skill you have edited before trusting the edit.
