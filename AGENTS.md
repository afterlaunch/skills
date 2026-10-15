# For any agent

Every skill in this repository is a folder under `skills/` with a `SKILL.md`
you follow literally. Read the whole file before running one.

## roughen

`skills/roughen/SKILL.md` audits a finished piece of prose for the patterns
that give machine writing away, fixes a model's words or flags a person's,
then runs a dice pass at the tolerances in `skills/roughen/tolerances.json`.
The script at `skills/roughen/scripts/roughen.py` is optional and needs only
Python 3. Use `--report` to find without changing, and `--seed` so a run can
be repeated. Show the writer every change the dice made; any one may be
refused. Never add roughness by hand, never invent a fact to make a piece
sound lived in, and never rewrite words a person wrote themselves.
