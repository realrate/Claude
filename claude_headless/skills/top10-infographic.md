---
description: Generate a RealRate "Top 10" ranking LinkedIn infographic for an industry — a 1200x1500 PNG plus a matching caption .txt, pulled live from realrate-archive.com. Practice copy of skills/top10ranking.md.
argument-hint: [industry_slug] [year (optional)]
---

# Practice Skill — Top 10 Infographic

Generates a 1200×1500px portrait LinkedIn infographic plus a matching caption
for a RealRate industry "Top 10" ranking, using live data from
realrate-archive.com.

This is a **learning copy** — isolated in `claude_practice/`, does not touch
`skills/top10ranking.md` or `infographics/generate_infographic.py`.

Design context: `claude_practice/context/infographic-design.md` — read it
before changing any color, size, or copy rule below. Never hardcode a value
into the script that isn't traceable to that file.

**Unverified assumption** (see context file → "Known open question"): the
archive's `value` field is displayed directly as an ECR percentage. Sanity
check the numbers against realrate-archive.com before treating output as
publish-ready — this is a standing rule in the parent project's `CLAUDE.md`,
not optional here either.

## Arguments

- `$ARGUMENTS` parses as: `{industry_slug} [year]`
- `industry_slug` (required) — e.g. `air`, `software`, `hotels`
- `year` (optional) — if omitted, the script auto-detects the latest year
  with published data, walking backwards from the current calendar year

## Setup (first run only)

Create a virtual environment scoped to this practice folder (skip if it
already exists):

```bash
python3 -m venv "${CLAUDE_PROJECT_DIR}/claude_practice/.venv"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install --upgrade pip
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install Pillow cairosvg
```

`Pillow` renders the canvas; `cairosvg` rasterizes the real logo SVG named in
`context/design-system.md` so the image uses the actual brand asset instead
of a hand-drawn approximation. The archive fetch uses Python's built-in
`urllib`, no `requests`/`playwright` needed.

## Generate

Always run with the practice venv's Python:

```bash
cd "${CLAUDE_PROJECT_DIR}/claude_practice"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/python" \
  "${CLAUDE_PROJECT_DIR}/claude_practice/scripts/generate_infographic.py" <industry_slug>
```

Pass `--year <year>` only if `$ARGUMENTS` explicitly names one.

## Output contract

Output is namespaced by industry, then by skill — `output/us_<slug>/top10-infographic/`
— so multiple skills can later write into the same industry folder without
colliding, matching `skills/auto-post-cycle.md`'s `output/{industry}/{task}/`
convention. Running the script above always produces both files together —
never treat one as done without the other:

- `claude_practice/output/us_<slug>/top10-infographic/<slug>_<year>.png` — the infographic
- `claude_practice/output/us_<slug>/top10-infographic/linkedin_<slug>_<year>.txt` — the matching caption

## Available slugs

`air` · `motor` · `software` · `computers` · `finance_services` · `food` ·
`health_services` · `advertising` · `semiconductors` · `programming` ·
`petrol` · `mining` · `construction` · `realestate` · `hotels` ·
`consulting` · `data_processing` · `brokers` · `savings` · `life` ·
`non_life` · `pharma` · `chemicals` · `state_banks` ·
`medicinal_products` · `recreation`

## After generating

Report the output file paths, confirm both files were created, and remind
that the ECR numbers are unverified until checked against the archive.
