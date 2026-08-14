---
description: Generate a RealRate company report PDF — an adaptive set of chart+interpretation sections for one company within an industry, including RealRate's own causal ECR graph rendered from its source SVG. Companion to skills/industry-report.md, same adaptive-section architecture one level deeper.
argument-hint: [industry_slug] [rank_or_company_name] [year (optional)]
---

# Practice Skill — Company Report

Generates a multi-page PDF report for a single company: cover page plus
whichever candidate sections have supporting data for this company this
run. Same principle as `skills/industry-report.md` — sections are adaptive,
not a fixed count.

Design context: `claude_practice/context/company-report-design.md` — read
it before touching anything here. It documents the verified schema, how the
causal graph SVG is parsed, and a **confirmed discrepancy** you need to
know about before extending this skill.

## The discrepancy this skill surfaces, not hides

For the same company/year, `company_details.value × 100` and the causal
graph's own `EconomicCapitalRatio` node report *different* ECR values
(verified: 123.5% vs. 54.3% for Strata Critical Medical Inc, `us_air`,
2025). Both come directly from RealRate. This skill states both, labeled by
source, in the Causal ECR Graph and Caveats sections — it does not average
them, does not pick one as "correct," and does not hide the mismatch.
If you extend this skill, preserve that behavior; resolving the
discrepancy is a question for RealRate's data team, not something to guess
at in a chart script.

## Arguments

- `$ARGUMENTS` parses as: `{industry_slug} {rank_or_name} [year]`
- `industry_slug` (required) — e.g. `air` (also accepts `us_air` / `us-air`)
- `rank_or_name` (required) — a rank number (`1` = industry leader), a
  case-insensitive substring of the company name (e.g. `strata`), or
  **`all`** to generate one report per company in the industry (loops
  internally — one process, not one invocation per company; a failure on
  one company is logged and skipped, not fatal to the rest)
- `year` (optional) — overrides the balance-sheet-year URL fetched; the
  report always displays the marketing year from the payload's `year` field

## Setup (first run only)

Shares the venv with `top10-infographic` / `industry-report` — same
dependencies:

```bash
python3 -m venv "${CLAUDE_PROJECT_DIR}/claude_practice/.venv"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install --upgrade pip
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install Pillow cairosvg matplotlib
```

## Generate

```bash
cd "${CLAUDE_PROJECT_DIR}/claude_practice"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/python" \
  "${CLAUDE_PROJECT_DIR}/claude_practice/scripts/generate_company_report.py" <industry_slug> <rank_or_name>
```

Pass `--year <year>` only if `$ARGUMENTS` explicitly names one. If the
company name doesn't match, the script lists every ranked company in that
industry with its rank — don't guess a company_id, re-run with the printed
name instead. Pass `all` in place of `<rank_or_name>` to generate a report
for every company in the industry in one run.

## Sections are adaptive

Candidates, in render order: Company Overview, Causal ECR Graph, Strengths
& Weaknesses, Balance Sheet Snapshot, Multi-Year ECR History, Peer
Comparison, Data Confidence & Caveats, Takeaway & Full Report. Full
requires/chart/text spec is in `context/company-report-design.md`. A
company missing `report_text`, a fetchable `graph_url`, or 3+ years of
`ecr_records` history gets correspondingly fewer pages — that's correct
behavior, not a bug to patch around.

Two sections quote RealRate's own text verbatim rather than generating
interpretation: **Strengths & Weaknesses** (`report_text`) and the
discrepancy note in **Causal ECR Graph**. HTML markup (literal `<br/>`) is
stripped before quoting, per the same `clean_archive_text()` helper used in
the industry report.

## Output contract

- `claude_practice/output/us_<slug>/company-report/<company_slug>_<year>_report.pdf`
- With `all`: one such file per company, same folder, all in one run

Console output on run lists included vs. skipped sections per company, and
prints an explicit `NOTE:` line if the causal-graph/headline ECR mismatch
applies to that company — check that before treating any PDF as complete.
With `all`, a per-company `FAILED` line (with the error) plus a final
`Done: N/M reports generated` count replaces the single-run summary —
check that count, not just that the command exited, since individual
company failures don't stop the batch.

## Known unresolved data issues (don't silently fix these)

- Causal graph ECR vs. headline ECR mismatch (see above)
- Balance sheet figures in `table_records` have no stated unit — charted as
  relative magnitudes, axis labeled accordingly, never assumed to be
  thousands/millions/dollars
- `trend` sign convention still unverified (carried from the infographic
  and industry-report skills)

## After generating

Report the output PDF path, the section include/skip list, and — if
present — the causal-graph/headline ECR mismatch note from stdout.
