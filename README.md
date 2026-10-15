# roughen

Make machine-written prose read as if a person typed it.

Two moves, in this order. Take out what a model reaches for: the vocabulary,
the "not X but Y" reversals, the one-line closers, the staged run-ups, the
dashes, the invisible characters that survive copy and paste. Then put back,
at random and at tolerances you set, the small roughness a person leaves
behind: a dropped apostrophe here, a lowercase start there, once in a while a
typo. Rolled by dice, never written by rule, because a rule is a pattern and a
pattern is a new tell.

It is one skill: a markdown file an agent follows, with a register of the tells
inside it, and one optional script that does the parts a model cannot do
honestly (regex and random numbers).

## Install

These are instructions, not software. Pick whichever of these you are.

**Hand this to your agent.** Claude Code, Codex, Cursor, Copilot, Gemini CLI,
Windsurf, Aider, anything that can run a command. Paste this:

```
Clone https://github.com/afterlaunch/roughen and read skills/roughen/SKILL.md
in full. Follow it literally on the next piece of writing I give you.
```

**On Claude Code there is a shortcut:**

```
/plugin marketplace add afterlaunch/roughen
/plugin install roughen@roughen
```

**No terminal at all?** Open `skills/roughen/SKILL.md` on this page, copy the
whole file, paste it into ChatGPT, Claude, Gemini or whatever you use, and say
follow this. Everything works as plain instructions. The script is optional.

## Run

Give the agent a finished piece of writing and say roughen this. It will:

1. Run the mechanical pass, which finds dashes, banned words and phrases,
   invisible characters, hashtag walls and paragraphs that run too long.
2. Read the piece against the register and flag every tell, quoting the line
   and offering one fix each.
3. Fix the piece if a model wrote it. If you wrote it, it only suggests: your
   own casing, punctuation and roughness are your voice, not tells.
4. Roll the dice, show you every change, and let you refuse any one of them.
5. Read it back for rhythm.

The script on its own:

```
python3 skills/roughen/scripts/roughen.py draft.md --report      # find, change nothing
python3 skills/roughen/scripts/roughen.py draft.md --seed 7       # clean, then roll
python3 skills/roughen/scripts/roughen.py draft.md --no-roughen   # clean only
pbpaste | python3 skills/roughen/scripts/roughen.py - --seed 7
```

Standard library Python, no network, nothing to install.

## The dice

Every knob lives in `skills/roughen/tolerances.json`. Set one to 0 and that
pass is off. Same seed, same draft, same result.

| Knob | Default | What it does |
| --- | --- | --- |
| `apostrophe_drop` | 0.33 | each contraction apostrophe has this chance of going ("dont", "youll") |
| `lowercase` | 0.16 | each ordinary sentence-opening word, and the pronoun I, has this chance of losing its capital |
| `typo_chance` | 0.2 | the chance the whole piece gets one typo, two adjacent letters swapped in an ordinary word |
| `max_sentences_per_paragraph` | 4 | report only: longer paragraphs are flagged for you to split |

The dice never touch numbers or the words beside them, names, links, email
addresses, handles, hashtags, code, anything in quotation marks, or the first
line of the piece.

## What it will not do

It will not invent a fact, a feeling or a reaction to make a piece sound lived
in. It will not rewrite a person's own words. It will not add roughness by hand;
only the dice may, and only at your tolerances.

And it cannot tell you whether the result reads better to a real reader. That
needs a reader.

## Check it yourself

```
python3 skills/roughen/evals/run.py
```

Offline, standard library, exits 0 when every check passes.

## Attribution

The five strongest entries in the register are adapted from
[blader/humanizer](https://github.com/blader/humanizer) (MIT), and the
invisible-character pass follows
[Jakeschincariol/linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill)
(MIT). Notices in `THIRD_PARTY.md`. Published by the team behind
[AfterLaunch](https://afterlaunch.io). MIT.
