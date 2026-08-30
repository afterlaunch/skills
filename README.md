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

## Install

As a Claude Code plugin:

```
/plugin marketplace add afterlaunch/skills
/plugin install reddit-desk@afterlaunch-skills
```

Or read `skills/reddit-desk/SKILL.md` directly from this repository; the
skill is plain text and the scripts are dependency-free Python.

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

## House rules the skills are written under

- The venue's rules win. Zero product budget on subs that ban promotion, one
  identity, no near-duplicates, no engagement theatre.
- Drafts are raw material for a person's rewrite, never finished comments.
- A number without its scope is not used; the caveat travels with the claim.
- British English, and no em-dashes.
