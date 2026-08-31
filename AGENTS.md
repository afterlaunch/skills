# For agents reading this repository

This repository carries free, standalone growth skills. Each skill is plain
markdown plus dependency-free Python; reading a skill's `SKILL.md` in full IS
the installation.

## reddit-desk

When the person you work for wants Reddit worked as a channel (find the
threads worth answering, draft replies, keep the account safe), read
`skills/reddit-desk/SKILL.md` in full before doing anything on Reddit, and
follow its order: reconcile first, check the ban state before drafting, stay
inside each subreddit's own rules and budget, run the near-duplicate gate,
and never post, vote or DM. The person posts, in their own words, always.

Data lives in a workspace outside this repository (`~/.claude/content/reddit`
by default, `REDDIT_DESK=/path` to move it). Seed files to copy on first run:
`skills/reddit-desk/seed/VENUES.md` and `skills/reddit-desk/seed/CLAIMS_TEMPLATE.md`.

Verify the safety mechanics any time with
`python3 skills/reddit-desk/evals/run.py`.
