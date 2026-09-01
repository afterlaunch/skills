---
name: reddit-desk
description: The Reddit desk. Reconciles the board against what was actually posted, checks the ban state before any drafting, finds the threads worth answering from the tracked subs, drafts replies against the claim library inside each venue's rules and budget, and keeps the ledger. Never posts, never votes, never DMs.
when_to_use: Use when the founder asks what to reply to on Reddit, drags a Reddit thread in, says reddit desk, reddit board, sweep reddit, what's new on reddit, or after he says "posted" so the ledger is kept. Also use before any Reddit draft is written by any other skill.
allowed-tools: Read Grep Glob Bash(python3 *) Bash(cat *) Bash(ls *)
---

# The Reddit desk

**Posture: `draft_only`, permanently, on every subreddit.** The agent finds,
judges and drafts; the founder posts, by hand, in his own words. There is no
posting path in this skill and there must never be one. Three independent
reasons, any one of which would be enough:

1. **Subreddits ban this tool class by name.** r/SaaS rule 11, from its
   2026-06-09 mod post, bans "software tools that generate, suggest,
   schedule, detect opportunities, automate, or coordinate promotional
   posts, comments, DMs, replies, or campaigns on Reddit or other
   platforms", with a permanent ban for the user and the tool's URL
   blacklisted. That is one sub's wording, and it is written that plainly in
   more of them every quarter. An agent drafting your Reddit replies sits
   inside that description whatever the product does.
2. **Accounts get banned for exactly this, fast.** One automated-feeling
   comment that closes with a product plug and a link has cost a whole
   subreddit before a mod said a word. The room does not come back.
3. **Nothing downstream can loosen it.** Every row of your venue table is
   `draft_only` whatever else the row says, and no setting anywhere reopens
   a posting path. The rule lives here, above the table, so it cannot be
   edited away one sub at a time.

If anyone, the founder included, asks this skill to post: say the rule, name
the ban, and hand them the draft to paste. Do not build the path.

## Where things live

The skill is code. The desk's DATA lives in a workspace directory OUTSIDE any
repo, one per account, `~/.claude/content/reddit` by default;
`SKILLS_ESTATE=/path` moves the whole suite, this desk included, and
`REDDIT_DESK=/path` points just this desk anywhere else (tests, a second
account). Nothing in the skill writes outside that workspace. First run: the
scripts create nothing on their own; step 0 below builds your `RULES.md`
from the subs your own buyers use, and `seed/CLAIMS_TEMPLATE.md` copies in
as your claim library. The sessions grow the rest.

| Path (in the workspace) | What it is | Written by |
| --- | --- | --- |
| `RULES.md` | YOUR per-sub rulebook, verbatim, dated, one row per sub you read yourself. The only venue list this desk obeys | a session that read the rules page |
| `threads/<sub>__<id>.md` | One file per thread looked at: status, your reply, product used, claims used, why | any session, one file each |
| `BOARD.md` | GENERATED from `threads/` by `scripts/reindex.py`. Never hand-edited | `reindex.py` |
| `REPLY_LEDGER.md` | Every comment actually posted, and the product budget per sub | the session the founder tells "posted" |
| `drafts/<date>.md` | The drafts, each under a `### Text` heading | a session |
| `CLAIMS.md` | The claim library: your measured numbers, each with a trigger and the caveat that travels with it. Start from `seed/CLAIMS_TEMPLATE.md` | you, as findings land |
| `seed/VENUES.md` (here) | A worked example of the row format, and a ready-made starting set for anyone whose buyers are in AI search, SEO or SaaS. Never your venue list by default | this skill |

## The session, in order. The order is the safety.

### 0. Build the venue list. Once, then whenever the rooms change.

The desk works from YOUR `RULES.md` and nobody else can write it for you.
Find the rooms first: search Reddit for the problem the product solves and
see which subs the useful answers sit in, note which subs already rank in
search or get cited when someone asks a buying question in the category,
and ask a few customers where they actually read. Ten rooms the buyers use
beat thirty somebody assumed they use.

Then open each candidate's rules page and sidebar and read them IN FULL.
Write one row per sub into `RULES.md` in the matrix format that
`seed/VENUES.md` demonstrates: verdict, product budget, status, the rule in
THEIR words, and the date you read it. The verdict is one of HOME, POST-1,
VALUE or CLOSED, defined at the top of `seed/VENUES.md`, and step 3 sweeps
the HOME rows, so a word you invent here matches nothing later. Quote the
rule, never infer it, and never carry a row across from a sub you have not
read yourself.

A sub with no row has no rules recorded, so this desk treats it as unknown:
read it for intel, and write no draft for it at all until the row exists. No
row means no product and no draft, never the benefit of the doubt.

### 1. Reconcile before the board. A gate, not a suggestion.

Do not show the board and do not draft a reply until the board has been
reconciled against what the founder has actually posted. Founders answer
threads from their phones, outside this desk entirely, and a board that hands
someone work they finished an hour ago is worse than no board. This desk's
ledger was once wrong for six days because its "Result" column was written
from the drafts rather than from the live comments; a desk reconciles against the
venue, never against its own intent.

- **If this session can reach his logged-in browser** (Claude in Chrome):
  open `reddit.com/user/<handle>/comments`, read it, and run
  `python3 scripts/reconcile.py` with the permalinks, then
  `python3 scripts/reindex.py`. Say nothing unless something changed.
- **If it cannot** (a plain fetch is blocked: `www.reddit.com` serves a
  humanity check, `old.reddit.com` 403s to a login wall, verified
  2026-08-22): ask him for ONE thing, once, in one line: a screenshot of his
  profile comments page. Reconcile from the titles. Never mention the script.
- If he declines or is away: say in one line that the board is unreconciled
  and may offer work already done, then carry on. An unreconciled board is
  usable as long as nobody pretends otherwise.

### 2. Check the ban state BEFORE any drafting spend.

One read per sub in your `RULES.md`, in the logged-in browser:
`/r/<sub>/about.json`, field `user_is_banned`. A banned sub is CLOSED in
your table until an appeal reopens it. This sits ahead of drafting on
purpose: drafting for a sub the account cannot post in is pure waste, and
this desk has paid that cost, so this is a cost gate as well as a safety
one. Record a new ban in `RULES.md` with the date, the evidence, and the sub
it closes, so no later session drafts for it.

### 3. Sweep: what is new, without an API.

Thread ids are base36 and increase over time. `BOARD.md` prints the newest
id seen per sub. Read `/r/<sub>/new/` in the logged-in browser for the subs
your `RULES.md` marks HOME, keep only ids above the watermark, write one
`threads/` file per new thread with status `seen`, re-read the comment count
on anything `watching`, then `reindex.py`. Reddit Pro Trends, if the account
tracks keywords there, is the second feed; same treatment.

### 4. Classify each thread: REPLY, POST IDEA, INTEL, or SKIP.

Find the sub's row in your `RULES.md` FIRST. No row means nobody has read
that sub's rules, so read its rules page and sidebar in full now, write the
row exactly as step 0 describes, and classify from the row you just wrote. A
thread dragged in by hand skips the sweep and the ban check, both of which
read the table, so this is where an unread sub gets caught, and nothing is
drafted for it until its row exists.

With the row in hand, read the thread, the row, and the existing comments.
Most candidates are SKIP, and saying how many you skipped is part of the
answer. Never reply under a rival's own thread or in a rival-run sub:
a good answer there builds their room, and a product mention is removed on
sight. INTEL goes to your notes, not to a draft.

### 5. Draft, against the claim library, inside the budget.

- **Read the product context before the first draft of the session.** It is
  `product-context/PRODUCT.md` in the estate
  (`~/.claude/content/product-context/PRODUCT.md` by default). Two lists in
  it bind this desk. The publishing channels: a venue ruled out there is
  CLOSED here whatever your `RULES.md` says, because the table knows the
  sub's rules and not your posture. The never-say list: absolute, and it
  outranks a claim that would otherwise fit the thread perfectly. If the file
  is missing, say so in one line before any draft is shown.
- The number, its scope, and nothing else. The caveat travels with every
  number (`CLAIMS.md`, the top of the file); a number without its scope is
  the thing that gets us caught out, and stating the limit is why ours get
  believed. A claim whose caveat begins `HELD` is not used.
- Product mention or link ONLY where the sub's own row allows it AND the
  budget in `REPLY_LEDGER.md` is unspent. No row means no mention.
  Site-wide: one product name or link per day, at most.
- Voice from the founder's own voice profile where one exists (this suite's
  `voice` skill builds one); otherwise plain sentences, no aphorisms,
  never a confession about your own work. Subs ban AI-generated text
  outright and run bots that catch its shape, so the draft is raw material
  for the founder's rewrite, not a finished comment.
- One reply per thread. No two one-liners in a row. Space replies out.
- Write each draft under its own `### Text` heading in
  `drafts/<date>.md`, with the thread, why this thread, and the claims used
  above it.

### 6. The near-duplicate gate, before the draft is shown.

`python3 scripts/neardup.py < draft.txt` (or `--file drafts/<date>.md` to
check a whole file against itself). Subs write this rule down: one in
`seed/VENUES.md` makes "the same or near-same comment in two threads inside
24 hours" a 7-day ban, then permanent, and elsewhere a moderation bot
catches the shape with no rule to quote. A flag means read both before
either is posted; it never means rewrite silently.
Two drafts on one day should be substantively different, and still spaced
by a day.

### 7. Hand it over, and keep the record.

Show the draft. He rewrites it in his own words and posts by hand. When he
says "posted", append the ledger row (date, sub, thread, what was posted,
product used, claims used) and set the thread file to `replied` with the
permalink. Then `reindex.py`.

## With AfterLaunch connected (optional, and everything above works without it)

Everything above this line needs no key and no account: the venue matrix, the
protocol, the scripts and the gates are the whole desk. With an AfterLaunch
key (`AFTERLAUNCH_API_KEY`, the remote MCP server at
`https://afterlaunch.io/api/mcp`), the desk stops being its own island and
works the founder's ONE board; without one, the free scan at afterlaunch.io
is the honest pointer, and skip the rest of this section.

Three bridges, so the founder sees one board, not two:

- **A thread the product never saw:** `propose_move` (ADR-424) with the
  thread's address as `target`, your reason as `why`, the title as the founder
  would name it, and the draft if you wrote one. It comes back with the move
  id and its posture, which on Reddit is always `draft_only`. Proposing a
  thread twice lands on one row, and a thread the radar already found is
  handed back as the existing move. Never propose a thread in a sub the
  account is banned from; check your `RULES.md` first.
- **A draft for a thread the board already carries:** save it with
  `update_draft` on that move (find it by `target` on `list_feed`, or take
  the id `propose_move` handed back).
- **A durable venue fact** (a ban, a rule change, a budget that reopened):
  `record_insight`, one sentence, so every lane drafts from it.

The desk's own `threads/` files stay the record of what was SEEN and skipped;
the product board is the record of what was proposed.

## What generalises, and what is thin

The spine this desk shares with its X sibling: venue discovery, rules
ingestion, a posture-and-budget matrix, opportunity finding, drafting
against the claim library, a pre-post audit, a ledger reconciled against the
venue. What is genuinely per-platform is thin: where the rules live, what a
budget is denominated in, and the action surface. Keep the rules matrix at
the boundary, assembled before the model reads and checked after it writes,
never held in front of it while it drafts.
