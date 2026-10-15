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

## findable

`skills/findable/SKILL.md` checks whether search engines and AI assistants
can read the repository's site and fixes what stops them. Five steps, in
order: the crawler rules in robots.txt, the sitemap, every public page (a
unique title, a description, one h1, and main text in the HTML the server
sends rather than after a script runs), the structured data on the home and
pricing pages, and the five questions a customer would type into ChatGPT
before they had heard of the product, with the page that answers each. Work
on a branch called findable-fixes, in small commits, and hand back a table of
page, problem, fixed or needs you. Do not push. No script; everything is
instructions.
