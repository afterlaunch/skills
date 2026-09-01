# AfterLaunch skills

Growth skills for AI visibility and SEO, from the team building
[AfterLaunch](https://afterlaunch.io), the organic growth engine.

What they do: get you posting useful things regularly, in your own voice, so
the gaps in how AI answers and search find you start closing. Free, MIT, and
useful on their own. Better pointed at [AfterLaunch](https://afterlaunch.io).

Seven so far. More over time.

## Start here: product-context

Writes `product-context/PRODUCT.md`. What you sell, who for, what you can
prove, the words you keep and the words you refuse. Everything else reads it.
Skip it and an agent invents your company off your landing page, and every
draft after that inherits the invention.

You do not start from a blank page. The free Growth Snapshot at
[afterlaunch.io](https://afterlaunch.io) reads your site and fills most of it
in, then this walks you through fixing what it got wrong.

## farm

Farming ideas. Everything you come across in a day goes in one door, and gets
sorted into something to say, something to build, or something to remember.
When you want to post, it looks across everything you kept and hands you an
idea instead of a blank page.

Nobody runs out of things to post. They run out of things they wrote down.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/farm-dark.svg">
  <img alt="The farm: one door in, three lanes out" src="assets/farm-light.svg">
</picture>

## The other five

**`voice`** shows you two sentences, you pick the closer one. Out comes a
profile the drafting skills obey.

**`draft`** three hooks with the reasoning, then one draft per platform.

**`tells`** the de-slop pass. One register of what gives machine writing away,
quoting the line that failed. Worth running on things you wrote yourself.

**`reddit-desk`** reads 28 subreddits' own rules before writing a word. Nine
of them ban naming your product outright. It checks whether you are banned
there, keeps a budget per sub for how often you may mention yourself, and
refuses a reply too close to one you already left, because on some subs a
near-duplicate inside twenty-four hours costs a seven day ban and then a
permanent one. It never posts.

**`session-recap`** what you shipped, how it works in plain words, what you
left unfinished.

Four of them read `product-context/PRODUCT.md`. `draft` stops rather than
guess when it is missing.

## Connectors

Most places have no usable write path for one person, so the road is an agent
driving a browser you are already signed into. The skill carries the brief,
not the automation: your agent drives, and we hold no credentials for anyone.
No browser agent, and the skill hands you the finished post and the URL to
paste it into.

It fills the composer and stops before submit. You press the button. That one
does not change.

## Install

These are instructions, not software. There is nothing to build and nothing
to depend on, so pick whichever of these three you are.

**Hand this to your agent.** Claude Code, Codex, Cursor, Copilot, Gemini CLI,
Windsurf, Aider, or anything else that can run a command. Paste this:

```
Clone https://github.com/afterlaunch/skills. Read skills/product-context/SKILL.md
and follow it to build my product context. Every skill is a folder under skills/
with a SKILL.md you follow literally, so read the whole file before running one.
Then tell me which skill to run next and why.
```

That is the entire installation.

**On Claude Code there is a shortcut:**

```
/plugin marketplace add afterlaunch/skills
/plugin install afterlaunch-skills@afterlaunch-skills
```

**No terminal at all?** Open any `SKILL.md` on this page, copy the whole file,
paste it into ChatGPT, Claude, Gemini or whatever you use, and say follow this.
Everything works as plain instructions. The Reddit desk is the only skill with
scripts, and they are optional.

Whichever way you came in, run `product-context` first. The skills share one
directory: `SKILLS_ESTATE` points at it, and defaults to `~/.claude/content`.

Every skill ships a runnable offline eval, if you want to check it yourself:

```
for s in skills/*/; do python3 "$s/evals/run.py"; done
```

## With AfterLaunch

The skills do the making. [AfterLaunch](https://afterlaunch.io) does the
knowing: what the engines say about you, what moved since last week, what to
do next, and whether it worked.

A skill runs once and forgets. Set `AFTERLAUNCH_API_KEY`, add the MCP server
(setup in [afterlaunch/mcp](https://github.com/afterlaunch/mcp)), and these
work your ranked board instead of a local folder. A thread they find lands on
it, a draft saves against its move, and what you learn about a venue stays for
every later draft. Shipping stays a human decision.

Without a key they run the same way against files on your machine.

## House rules

- The venue's rules win. Zero product budget where promotion is banned.
- Drafts are raw material for your rewrite, never finished comments.
- A number without its scope is not used. The caveat travels with the claim.
- British English, and no em-dashes.
