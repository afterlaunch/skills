---
name: tells
description: Audit finished work, prose or a built interface, for the patterns that give machine-made output away. Reads one shared register, quotes the offending line or file:line for each check, then fixes what fails.
when_to_use: Use on any finished piece of writing or built page before it ships, when you ask does this look AI, or after a draft comes out of any other skill. Run it even on work written by hand.
allowed-tools: Read Grep Glob Bash Edit
---

# Tells

An audit, run **after** the work exists. Never a brief handed to whatever
is doing the writing or building.

That placement is not a style preference. Structure belongs at the
boundaries of a piece of work, not inside the act of making it: assemble
what you need before you start, check what you produced after you finish,
and put nothing in between. A model, or a person, handed a coverage
checklist while it writes tends to satisfy the checklist and lose the
actual point; a register run afterwards catches the same problems without
causing that one.

Read `TELLS.md` first. It is the single source; do not work from memory of
it.

Then read the words this business refuses. They live in
`product-context/PRODUCT.md` in the estate
(`~/.claude/content/product-context/PRODUCT.md` by default), in the refused
words list and the never-say list. Each entry is a check in this run,
exactly like a register entry: quote the line it turns up on and fix it. A
refused word is a defect even where the register would have let it through,
because the register is generic and that list is yours. If the file is not
there, say so once in the report: the audit is running without half its
vocabulary.

## What this catches that a green build does not

A build can enforce the mechanical subset of this register (Part 3 is
written as literal patterns for exactly that). This skill exists for the
rest: the judgement calls a regex cannot make.

- Does this grid have real visual variety, or six identical white cards?
- Is this the fourth section in a row with the same shape?
- Is that label earning its place, or is it on every section out of
  habit?
- Is that animation motivated, or is it motion for show?
- Does this read as written by someone, or assembled?

If a finding is mechanical and you had to notice it by hand, that is a
candidate for Part 3 of the register. Say so; do not silently rely on
having spotted it once and moving on.

## How to run it

**1. Identify the target and pick the halves that apply.** Prose, a built
surface, or both. A marketing page is both.

**2. Grep the mechanical entries yourself anyway**, whatever your own
build enforces. Cheap, and it front-loads the certain findings.

**3. Read the thing.** For a built surface this means rendering it, not
reading the source. Boot it, screenshot the real route at a real width,
look at it. A layout defect that passes every automated check is a real,
repeatable failure mode, not a hypothetical one: type-checking, linting, a
full test suite and a production build can all pass on a page where every
heading wraps one word per line.

**4. Report per finding**, most severe first:

- The tell, named from the register
- The evidence, quoted, with `file:line` or the offending sentence
- Whether it is a defect, a judgement call, or a collision with something
  you have already deliberately decided

**5. Fix the defects.** Do not just flag them.

## For a draft post specifically

The prose half of the register doubles as a pre-publish gate. Hard gates,
any one fails the draft:

1. **Em-dashes.** Zero.
2. **Banned vocabulary.** Zero instances from the register. One is enough
   to fail.
3. **Invented numbers.** Every figure must trace to something actually
   measured, or a named public source. If it cannot be traced, cut it.
4. **Self-denigration.** No confession of the writer's own failure or
   inadequacy dressed up as relatability.
5. **Claims about a named person or company.** An observation with a
   date, never a verdict.
6. **Engagement bait.** No "like if you agree", no question that exists
   only to farm replies.
7. **The four shapes.** No aphorisms, no "it's not X, it's Y", no pithy
   fragments for emphasis, no stacked fragments.
8. **Contractions.** Full forms in casual writing fail. "Wouldn't", not
   "would not".

Soft checks, report and suggest rather than block:

9. **Length.** Note the actual character count against whatever your
   target platform's natural read length is.
10. **Structural rhythm.** Flag uniform sentence length, rule-of-three
    lists, and the intro-body-summary-optimistic-close shape.
11. **Specificity.** Count adjectives doing no work; every one should be
    carrying a fact instead.
12. **The opening.** Does the first line stand alone and earn the second?
13. **Case and formatting.** Sentence case reads better than either
    shouting caps or affected lowercase; hashtags sparingly if the
    platform uses them at all.
14. **Mix.** If you are tracking a rolling ledger of what you have
    published, say whether this makes several of the same easy format in
    a row.

## Three rules for the findings

**A ratified decision beats this register.** Where you or your team have
already deliberately settled something, that decision wins and the
finding is closed as "collision, no action". If you hit a new one, write
it down once (in your own `EXCEPTIONS.md`, see below) rather than
re-litigating it every run.

**Separate defect from preference.** "This wraps a word per line" is a
defect. "I would not have used a serif" is not a finding at all. If you
cannot say what breaks, you have an opinion, not a finding.

**A green build is not evidence the page is right.** Gates prove the code
compiles. They prove nothing about what a reader actually sees.

## Where things live

The skill is code. Your own accepted exceptions live in the estate this
suite shares, OUTSIDE any repo: `SKILLS_ESTATE`, which defaults to
`~/.claude/content`. `SKILLS_ESTATE` is the ROOT, and every skill in the pack
keeps its own subdirectory under it, so one variable configures the whole
pack. This skill's own is `tells/`.

| Path (in the estate) | What it is |
| --- | --- |
| `tells/EXCEPTIONS.md` | One line per defect you have already reviewed and deliberately decided to keep. Checked before anything is flagged again |
| `product-context/PRODUCT.md` | Read, never written here. The refused words and the never-say list this run checks against |

First run: nothing is created for you, and the file is entirely optional.
A run with no `EXCEPTIONS.md` just has nothing to skip yet.

## Output

A short table: tell, verdict, evidence. Then the fixes applied. Then one
line on anything you could see was wrong but could not fix without
someone else's decision.

If nothing fails, say so plainly and stop. **Do not manufacture
findings.** A register with a quota becomes a machine for inventing work,
which is its own kind of machine-made output.

## With AfterLaunch connected (optional, and everything above works without it)

Everything above needs no key and no account: the register, the process
and the gates are the whole skill. With an AfterLaunch key
(`AFTERLAUNCH_API_KEY`, the remote MCP server at
`https://afterlaunch.io/api/mcp`), a fix applied to a draft that already
lives on the growth board should not stay only in your own file or your
own chat.

- **After a fix on a board draft:** `update_draft` on that move saves the
  corrected text where the founder will actually see it next, rather than
  leaving the good version sitting in this session's scrollback.

Without a key, the free scan at afterlaunch.io is the no-account way to
see what a connected board would carry.

## What this cannot do alone

It cannot remember which findings you have already accepted across a
fresh terminal, past whatever you wrote into your own `EXCEPTIONS.md`. It
cannot rank which piece of work is worth auditing first; that needs
someone deciding what matters today. And it cannot tell you whether the
fixed version actually reads better to a real reader; that needs an
actual reader, not a register.

## House rules

British English. No em-dashes, no exclamation marks. Do not manufacture
roughness or manufacture findings to look thorough; both are the same
mistake wearing different clothes.
