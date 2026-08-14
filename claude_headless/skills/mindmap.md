---
description: Generate a RealRate company mindmap PNG — a radial diagram of one company's ECR, rank, strengths/weaknesses, and trend. Redesigned from skills/mindmap.md (real repo), which hardcodes 8 named companies and scrapes Wikipedia photos via Playwright; this version works for any company in the live archive using only verified data fields.
argument-hint: [industry_slug] [rank_or_company_name] [year (optional)]
---

# Practice Skill — Company Mindmap

Generates a single 1920×1080 radial mindmap PNG for one company: a center
hub (name, ECR, rank) with branch circles for whatever data is actually
available — industry position, financial health, strengths/weaknesses
(quoted from RealRate's own `report_text`), multi-year trend, rating
status.

Design context: `claude_practice/context/mindmap-design.md` — **read the
"Why redesigned" section before assuming this should look like the real
repo's mindmap skill.** It documents a confirmed regex bug this session
found and fixed (a naive strength/weakness extraction pattern locked onto
the wrong sentence and produced a paragraph-long "variable name" that
overflowed the canvas) — the fix and the defense-in-depth truncation are
both load-bearing, not incidental.

## Arguments

- `$ARGUMENTS` parses as: `{industry_slug} {rank_or_name} [year]`
- `industry_slug` (required) — e.g. `air` (also accepts `us_air` / `us-air`)
- `rank_or_name` (required) — rank number (`1` = industry leader), a
  case-insensitive substring of the company name, or **`all`** to generate
  one mindmap per company in the industry (loops internally; one
  company's failure is logged and skipped, not fatal to the rest)
- `year` (optional) — overrides the balance-sheet-year URL fetched

## Setup (first run only)

Shares the venv with the other report skills:

```bash
python3 -m venv "${CLAUDE_PROJECT_DIR}/claude_practice/.venv"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install --upgrade pip
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/pip" install Pillow cairosvg
```

No Playwright, no browser install, no `matplotlib` — this skill only needs
what `top10-infographic` needs.

## Generate

```bash
cd "${CLAUDE_PROJECT_DIR}/claude_practice"
"${CLAUDE_PROJECT_DIR}/claude_practice/.venv/bin/python" \
  "${CLAUDE_PROJECT_DIR}/claude_practice/scripts/generate_mindmap.py" <industry_slug> <rank_or_name>
```

Pass `--year <year>` only if `$ARGUMENTS` explicitly names one. If the
company name doesn't match, the script lists every ranked company in that
industry — re-run with the printed name, don't guess a company_id. Pass
`all` in place of `<rank_or_name>` to generate a mindmap for every company
in the industry in one run.

## Branches are adaptive

4–6 branches depending on what this company's data actually supports —
see the table in `context/mindmap-design.md`. Console output on run states
the branch count. A company with no multi-year `ecr_records` history or no
parseable `report_text` gets fewer branches, laid out evenly among however
many qualify — that's correct behavior, not a bug to force back to 6.

## Output contract

- `claude_practice/output/us_<slug>/mindmap/<company_slug>_<year>_mindmap.png`
- With `all`: one PNG per company, same folder, plus a final
  `Done: N/M mindmaps generated` count on stdout — check that count before
  assuming every company got one

## Known limitation

`report_text`'s strength/weakness sentence template was verified across
four companies in `us_air` — if a different industry's wording deviates
from that template, `parse_strength_weakness()` returns `None` for the
unmatched part and that branch is silently skipped (adaptive, not a
crash), but it's worth spot-checking a new industry's first run to confirm
the branches you expect actually appeared.

## After generating

Report the output PNG path and the branch count from stdout.
