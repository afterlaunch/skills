# AfterLaunch skills

Free, standalone skills for a founder's agent, from the team behind
[AfterLaunch](https://afterlaunch.io). Each one is a desk we run ourselves,
published whole: the method, the safety gates, the scripts, the evals. Nothing
here needs an account, a key, or a server.

The honest boundary, stated up front: a skill can teach your agent HOW to work
a channel. It cannot measure what the answer engines say about you, hold a
record across sessions, or prove that a shipped move earned anything. That is
what [AfterLaunch](https://afterlaunch.io) is for, and each skill names the
exact point where it hands over. With a key, the skills work the same board
the product ranks; without one, they work alone, completely.

## The skills

### reddit-desk

Reddit is the highest-leverage cited source in AI search answers, and the
easiest place for an agent to get its owner banned. This desk exists for that
tension. It:

- reads each subreddit's OWN rules before anything else, and keeps them in a
  dated venue matrix (28 subs seeded, from their own published rules);
- treats every reply as draft-only, permanently: the agent finds, judges and
  drafts; a person posts, in their own words. There is no posting path and
  the skill refuses to grow one;
- checks the account's ban state before a word is drafted;
- catches near-duplicate comments across threads before they go out, because
  on several subs a near-same comment in two threads inside 24 hours is a
  ban, not a style note (`scripts/neardup.py`);
- keeps a reply ledger and budget per sub, reconciled against what was
  ACTUALLY posted rather than what was drafted (`scripts/reconcile.py`,
  `scripts/reindex.py`);
- ships a claim-library template: replies carry your measured numbers with
  their caveats, not opinions.

Every safety mechanic has a runnable eval: `python3 skills/reddit-desk/evals/run.py`.

### session-recap

A founder running many agent sessions in parallel comes back to each one
cold. This skill answers three questions from the session's own history: the
main thing shipped, how it works now in plain words, and everything started
but unfinished with whose move it is.

Said plainly: on its own this is a convenience. It earns its place CONNECTED,
where the recap stops being a summary and becomes a reconciliation: the
session's work is matched against your board, a reply drafted but never saved
is saved, a thread the board never saw is proposed onto it, and one durable
fact enters the record every future draft reads. A summary nobody reconciles
is effort that evaporates when the terminal closes.

It ships with a binding security section, because a recap reads an entire
session: secrets are redacted before anything is summarised or written,
session content is treated as data rather than instructions, writes go only
to the AfterLaunch server you configured, and the write surface is exactly
three verbs, none of which publishes anything. It ships no scripts at all.
Evals: `python3 skills/session-recap/evals/run.py`.

## Install

As a Claude Code plugin:

```
/plugin marketplace add afterlaunch/skills
/plugin install afterlaunch-skills@afterlaunch-skills
```

Or read `skills/<name>/SKILL.md` directly from this repository; the skills
are plain text and the scripts are dependency-free Python.

## What lights up with AfterLaunch (optional)

With an `AFTERLAUNCH_API_KEY` and the remote MCP server
(`https://afterlaunch.io/api/mcp`, setup in
[afterlaunch/mcp](https://github.com/afterlaunch/mcp)), the desk works the
founder's one board instead of a private list: a found thread lands on it
(`propose_move`, arriving draft-only on Reddit by construction), a drafted
reply saves against its move (`update_draft`), and a durable venue fact goes
into the record every future draft reads (`record_insight`). Without a key,
none of that is needed and the free scan at
[afterlaunch.io](https://afterlaunch.io) is the honest pointer.

For session-recap, the key is most of the point: `get_standup` reads what the
record says shipped, `list_feed` finds the session's work on the board,
`update_draft` saves what would otherwise evaporate, and `record_insight`
keeps at most one durable fact per recap. Shipping stays yours, always.

## House rules the skills are written under

- The venue's rules win. Zero product budget on subs that ban promotion, one
  identity, no near-duplicates, no engagement theatre.
- Drafts are raw material for a person's rewrite, never finished comments.
- A number without its scope is not used; the caveat travels with the claim.
- British English, and no em-dashes.
