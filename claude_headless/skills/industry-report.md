---
description: Generate a RealRate industry report PDF — an adaptive set of chart+interpretation sections covering rankings, distribution, trend, top-rated status, notable movers, and data caveats, built entirely from one live archive JSON response. Practice-built alongside skills/industry-ranking-reports.md, which targets a rr_shared.py module and docx/Chrome pipeline that don't exist in this repo.
argument-hint: [industry_slug] [year (optional)]
---

# Practice Skill — Industry Report

Generates a multi-page PDF industry report: a cover page plus one page per
section that actually has supporting data for this run — see "Sections are
adaptive" below. Every number and quote traces back to one archive response;
nothing is invented.

Design context: `claude_practice/context/industry-report-design.md` — read
it before adding a new section or changing what a chart shows. It documents
the verified data schema (which fields exist, what they mean, what's still
unverified) and the chart style rules.

## Arguments

- `$ARGUMENTS` parses as: `{industry_slug} [year]`
- `industry_slug` (required) — e.g. `air`, `software`, `hotels` (also
  accepts `us_air` / `us-air`)
- `year` (optional) — overrides which balance-sheet-year URL to fetch; the
  report always *displays* the marketing year from the payload's own `year`
  field, not the fetch year (see context file § Fields)

## Setup (first run only)

```bash
python3 -m venv "${CLAUDE_PROJECT_DIR}/claude_practice/.venv"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install --upgrade pip
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install Pillow cairosvg matplotlib
```

Skip if the venv already exists — shared with `top10-infographic`, which
uses the same Pillow/cairosvg but not matplotlib.

## Generate

```bash
cd "${CLAUDE_PROJECT_DIR}/claude_practice"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/python" \
  "${CLAUDE_PROJECT_DIR}/claude_practice/scripts/generate_industry_report.py" <industry_slug>
```

Pass `--year <year>` only if `$ARGUMENTS` explicitly names one.

## Sections are adaptive, not fixed

The script holds a `SECTION_REGISTRY` of 10 candidate sections. Each one
declares a `requires(data)` check against *this run's* actual archive
response; only sections that pass are rendered. A data-rich industry may
get all 10 pages, a sparse one fewer — the script prints exactly which
sections were included and which were skipped (and why, implicitly, via
the `requires` check that failed). Never edit a section to force it to
always appear — if the data doesn't support it, skipping is correct.

Current candidates, in render order: Industry Overview, Top 10 Rankings,
ECR Distribution, Top-Rated Snapshot, Multi-Year ECR Trend, Sector Leader
Profile, Notable Movers, Competitive Compression, Data Confidence &
Caveats, Takeaway & Full Ranking. Full requires/chart/text spec for each is
in `context/industry-report-design.md`.

Two sections (**Sector Leader Profile**, **Notable Movers**) quote
RealRate's own `report_text` / `scentences` fields verbatim rather than
generating interpretation — real analyst text beats invented prose. HTML
markup in those fields (e.g. literal `<br/>`) is stripped before quoting,
never rendered raw.

## Output contract

- `claude_practice/output/us_<slug>/industry-report/<slug>_<year>_report.pdf`

One file. Console output on run lists which sections were included vs.
skipped — check that before treating the PDF as complete; a section
missing because its data wasn't available is not a bug.

## Known unverified data

`trend`'s sign convention (positive = improved) has no field in the
payload that cross-checks it the way `ecr_records` confirmed the ECR
scale — the Data Confidence & Caveats page in every report says so
explicitly. Don't remove that page; it's the report's own disclosure, not
boilerplate.

## After generating

Report the output PDF path and the section include/skip list from the
script's stdout. Remind that `report_text`/`scentences` quotes are
RealRate's own generated text, not this skill's — attribute accordingly if
excerpted elsewhere.
