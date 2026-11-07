---
description: Run the full claude_practice pipeline for one industry in a single pass — top10 infographic, industry report, company report, mindmap, and top5 reveal GIF. Orchestrator, modeled on skills/auto-post-cycle.md (real repo), scoped down to what actually exists and runs in claude_practice.
arguments: industry_slug [company_rank_or_name] [year]
---

# Practice Skill — Auto Practice Cycle (Orchestrator)

Runs every skill built in `claude_practice/` for one industry, in order,
in a single pass. No dashboard upload, no Drive, no `ADMIN_SECRET` —
those are real-repo `auto-post-cycle.md` concerns that don't apply here;
this orchestrator only chains local script runs and reports what was
produced.

## Arguments

- `$ARGUMENTS` parses as: `{industry_slug} [company_rank_or_name] [year]`
- `industry_slug` (required) — e.g. `air`, `hotels` (also accepts `us_air` / `us-air`)
- `company_rank_or_name` (optional) — which company(s) to use for the two
  per-company skills (`company-report`, `mindmap`). **Defaults to `all`**
  — every company in the industry gets its own report and mindmap. Pass a
  rank number or name substring instead to scope to one company.
- `year` (optional) — overrides the balance-sheet-year URL fetched; every
  script independently resolves the correct marketing year from the
  payload regardless

Both per-company scripts accept `all` natively (they loop internally, one
process — not one invocation per company from this orchestrator), and
skip-and-continue past any single company's failure rather than aborting
the batch. On a large industry this step takes noticeably longer than the
other four combined (one causal-graph SVG fetch per company for
`company-report`) — that's expected, not a hang.

## Step 0 — Setup (first run only)

All five scripts share one venv. Create it if it doesn't already exist:

```bash
python3 -m venv "${CLAUDE_PROJECT_DIR}/claude_practice/.venv"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install --upgrade pip
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install Pillow cairosvg matplotlib
```

## Step 1 — Run each skill in order

Run from `claude_practice/` so relative output paths land correctly. If
any single step fails, report the error and continue with the remaining
steps — don't let one skill's failure block the others (same
error-handling principle as `skills/auto-post-cycle.md`).

```bash
cd "${CLAUDE_PROJECT_DIR}/claude_practice"
VENV="${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/python"
COMPANY="<company_rank_or_name, or 'all' if $ARGUMENTS didn't name one>"

"$VENV" scripts/generate_infographic.py <industry_slug>
"$VENV" scripts/generate_industry_report.py <industry_slug>
"$VENV" scripts/generate_company_report.py <industry_slug> "$COMPANY"
"$VENV" scripts/generate_mindmap.py <industry_slug> "$COMPANY"
"$VENV" scripts/generate_top5_reveal_gif.py <industry_slug>
```

Append `--year <year>` to each command only if `$ARGUMENTS` explicitly
named one.

## Step 2 — Summary

All five skills write into the same `output/us_<slug>/` folder, namespaced
by skill (`top10-infographic/`, `industry-report/`, `company-report/`,
`mindmap/`, `top5-reveal-gif/`) — same convention established across every
skill in this project. After running, list what actually landed there:

```bash
find "${CLAUDE_PROJECT_DIR}/claude_practice/output/us_<industry_slug>" -type f
```

Report:
- Each file produced, grouped by skill
- Section/branch/frame counts each script printed to stdout (industry-report
  and company-report report adaptive section counts; mindmap reports branch
  count) — these are meaningful, not just log noise; a lower-than-expected
  count means that skill's data wasn't fully available for this
  industry/company, not that something broke
- Any step that failed, with its error, so it can be re-run individually
  once fixed — don't silently omit a failed step from the summary

## Known caveats to mention in the summary

Carry forward from the individual skill files — don't re-verify these each
run, just note they apply:
- ECR figures assume `value × 100` and the marketing year from the
  payload's `year` field (see `context/infographic-design.md` § Resolved)
- The causal graph's own ECR (in `company-report`) may not match the
  headline ECR — see `context/company-report-design.md`. Confirmed on a
  full `us_air` `all` run: 5 of 10 companies showed a mismatch, so expect
  this on a meaningful fraction of any industry's companies, not just an
  isolated case
- `trend`'s sign convention is still unverified everywhere it appears
