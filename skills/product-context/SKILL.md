---
name: product-context
description: Build the one file every other skill reads first: what this product is in the words a customer would use, who it is for, what it can prove, the vocabulary it keeps and refuses. Interviews rather than guesses, and marks anything it could not verify.
when_to_use: Use before any drafting skill runs for the first time, when the founder says set up my context, product context, who are we, my brand file, or when a draft comes back generic and the cause is that nothing told the agent what this business actually is. Also use to refresh the file after a positioning change.
---

# Product context

Every skill in this pack reads one file before it does anything. Without it
an agent writes plausible marketing for a company it has invented from your
landing page, and every draft after that inherits the invention. This skill
builds that file.

It is the least glamorous thing here and it is the one that decides whether
everything else is any good.

## The rule that makes this worth doing: ask, do not guess

An agent handed a website can produce a confident description of a business
in seconds, and it will be wrong in ways nobody catches for months, because
the wrong parts read fine. So this skill works in two passes and the second
one is not optional.

1. **Read what exists.** The site, the docs, the README, anything the
   founder points at. Extract only what is actually stated.
2. **Ask about the rest, then mark what is still unknown.** Every field you
   could not verify gets asked as a question, in one batch, in plain terms.
   Anything the founder does not answer stays in the file marked `UNKNOWN`
   rather than filled with something reasonable. A blank the drafting skills
   can see is safe. An invention they cannot see is not.

Never write a claim into this file that nobody said out loud.

## What the file answers

Nine questions, in this order. The order matters: the later ones are only
answerable once the earlier ones are honest.

1. **What is it, in the words a customer would use.** Not the category you
   would like to be in. If your customers say "a tool that tells me why my
   site is slow", write that, not "a performance observability platform".
2. **Who is it for, specifically enough to exclude people.** A description
   that excludes nobody is not a description. Name who this is not for.
3. **What did they use before.** The status quo you are displacing, whether
   that is a competitor, a spreadsheet, an agency or nothing at all.
4. **What can you prove.** Anything you can point at: a number you measured,
   a customer who will say it out loud, a public result. Each one gets the
   caveat that travels with it. This is what stops replies being opinions.
   The `claims` skill owns the detail; this file holds the pointer.
5. **What are you claiming that you cannot yet prove.** Being explicit here
   is what keeps it out of the copy by accident.
6. **The words you keep.** The five or ten terms you want to own, spelled
   the way you spell them.
7. **The words you refuse.** The category words, cliches and competitor
   framings you will not use, with a one-line reason each. This list does
   more work than the one above.
8. **Where you publish, and where you do not.** Channels you are actually
   present on, plus the ones you have deliberately ruled out, so no skill
   proposes them again.
9. **What you will never say.** Hard lines: claims you will not make,
   comparisons you will not draw, things that are legally or personally off
   limits. Every drafting skill treats this as absolute.

## Where the file lives

One file, `PRODUCT.md`, in `product-context/` under the estate this pack
shares: `SKILLS_ESTATE`, which defaults to `~/.claude/content`. On a default
install that is `~/.claude/content/product-context/PRODUCT.md`. Create the
directory if it is not there.

The exact path is the whole handoff, so it is worth being boring about. Every
skill below reads that string and no other. A context file written anywhere
else is a context file nothing ever opens, and the drafts go back to being
generic without anyone being told why.

Treat the file as private working material, not as a public document. It
holds things you have not published and possibly things you never will.
Nothing in this pack sends it anywhere.

## How the other skills use it

Each of these opens `product-context/PRODUCT.md` at that path by name.

- `voice` reads it before calibrating, so the forced choices are about your
  register rather than about writing in general.
- `draft` reads it first, always, and refuses to write generic copy when the
  file is missing: it asks you to run this instead.
- `tells` reads the refused-words list and treats each one as a check.
- The desks read the publishing channels and the never-say list before
  anything is drafted for a venue.

A field marked `UNKNOWN` propagates honestly: a skill that needs it says so
rather than filling the gap.

## With AfterLaunch connected (optional, and everything above works without it)

Everything above needs no key and no account. With one, the interesting
thing is that most of this file already exists, because the product read
your site and extracted the business context to write from.

- `get_snapshot` returns the extracted context: what the product understood
  your business to be. Read it first and use it as the draft answer to
  questions one, two and three, then correct it. Correcting a wrong
  extraction is faster and more accurate than starting from nothing.
- `list_kb_pages` and `get_kb_page` return the record's own pages on
  positioning, the audience and the competitive set, which answer the middle
  questions with something you have already reviewed.
- `record_insight` sends a durable correction back the other way. If the
  extraction had you wrong and you fix it here, record the correction in one
  sentence so every future draft reads the corrected version rather than
  re-learning it each time.

Without a key, the interview is the whole method and it takes about the same
time as a coffee.

## What this skill cannot do

It cannot check whether any of this is true in the market. It cannot ask an
answer engine what it thinks your product is, hold this file steady across
sessions on its own, or tell you whether your positioning is working. It
writes down what you know. Measuring whether the world agrees is a different
job and it needs something with a meter and a memory.

## House rules

British English. No em-dashes, no exclamation marks. Plain words over
category language, in this file above all: a context file written in
marketing prose teaches every downstream skill to write marketing prose.
