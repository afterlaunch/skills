# For any agent

One skill lives here: `skills/roughen/SKILL.md`. Read the whole file before
running it, and follow it literally. It audits a finished piece of prose for
the patterns that give machine writing away, fixes a model's words or flags a
person's, then runs a dice pass at the tolerances in
`skills/roughen/tolerances.json`.

The script at `skills/roughen/scripts/roughen.py` is optional and needs only
Python 3. Use `--report` to find without changing, and `--seed` so a run can be
repeated. Show the writer every change the dice made; any one may be refused.

Never add roughness by hand, never invent a fact to make a piece sound lived
in, and never rewrite words a person wrote themselves.
