# AfterLaunch skills

Free skills for your AI agent, one folder each under `skills/`, added one at
a time and only once they have earned it. Each is a markdown file an agent
follows, with an optional script for the parts a model cannot do honestly.
MIT.

The page that hands them over, with the most useful open-source skills from
other people beside ours: https://afterlaunch.io/tools/skills

## What is here

| Skill | What it does |
| --- | --- |
| [`roughen`](skills/roughen/SKILL.md) | Makes machine-written prose read as if a person typed it. Audits a finished piece against one register of the patterns that give AI writing away, fixes a model's words and only flags a person's, then rolls dice at tolerances you set to put back a little of the roughness a person leaves behind. |

## Install

These are instructions, not software. Pick whichever of these you are.

**Hand this to your agent.** Claude Code, Codex, Cursor, Copilot, Gemini CLI,
Windsurf, Aider, anything that can run a command. Paste this:

```
Clone https://github.com/afterlaunch/skills and read skills/roughen/SKILL.md
in full. Keep it as a skill you follow when the task fits.
```

**On Claude Code there is a shortcut:**

```
/plugin marketplace add afterlaunch/skills
/plugin install afterlaunch-skills@afterlaunch-skills
```

**No terminal at all?** Open any `SKILL.md` on this page, copy the whole file,
paste it into ChatGPT, Claude, Gemini or whatever you use, and say follow
this. Everything works as plain instructions. The scripts are optional.

Nothing here writes into your instruction files or runs code from a URL. Your
agent clones a repository you can read first.

## Roughen, in short

Two moves, in this order. Take out what a model reaches for: the vocabulary,
the "not X but Y" reversals, the one-line closers, the staged run-ups, the
dashes, the invisible characters that survive copy and paste. Then put back,
at random and at tolerances you set, the small roughness a person leaves
behind: a dropped apostrophe here, a lowercase start there, once in a while a
typo. Rolled by dice, never written by rule, because a rule is a pattern and a
pattern is a new tell.

The script on its own:

```
python3 skills/roughen/scripts/roughen.py draft.md --report      # find, change nothing
python3 skills/roughen/scripts/roughen.py draft.md --seed 7       # clean, then roll
python3 skills/roughen/scripts/roughen.py draft.md --no-roughen   # clean only
```

Every knob lives in `skills/roughen/tolerances.json`. Same seed, same draft,
same result. The dice never touch numbers or the words beside them, names,
links, email addresses, handles, hashtags, code, anything in quotation marks,
or the first line of the piece.

## Check it yourself

```
python3 skills/roughen/evals/run.py
```

Offline, standard library, exits 0 when every check passes.

## Attribution

The five strongest entries in roughen's register are adapted from
[blader/humanizer](https://github.com/blader/humanizer) (MIT), and its
invisible-character pass follows
[Jakeschincariol/linkedin-agent-skill](https://github.com/Jakeschincariol/linkedin-agent-skill)
(MIT). Notices in `THIRD_PARTY.md`. Published by the team behind
[AfterLaunch](https://afterlaunch.io). MIT.
