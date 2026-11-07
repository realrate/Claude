# Context — Industry Report Design & Data Schema

Backs `skills/industry-report.md`. Unlike `infographic-design.md` (a trimmed
subset of `design-system.md`), this file documents a **data schema**
discovered by inspecting the live archive response directly — the real
skill's own docs (`skills/industry-ranking-reports.md`) reference fields
this session couldn't confirm exist (`shrinked_graph_json`,
`feature_distribution_plot` as chartable data, etc.) or a shared module
(`rr_shared.py`) that isn't in the repo. Everything below was checked
against a live response before being written down — see "Verified against"
notes.

---

## Data source

One endpoint carries everything this skill needs — no per-company SVG
scraping required:

```
GET https://www.realrate-archive.com/us_<slug>/<balance_sheet_year>/website-ranking.json
```

Same walk-back-from-current-year fetch pattern as `top10-infographic`
(see `scripts/generate_infographic.py::fetch_ranking_data`).

### Fields, and what they actually are (verified 2026-08-14 against `us_air`)

| Field | Shape | What it is |
|---|---|---|
| `year` | int | **Marketing year** (e.g. `2026`) — display this, not the year in the fetch URL, which is the balance sheet year. Matches `url_segment` (e.g. `"2026-us-air"`). |
| `industry_label` | str | Human-readable industry name (e.g. `"Aviation"`) |
| `num_companies` | int | Total companies tracked in this industry |
| `industry_box` | list of `[label, value]` pairs | Aggregate financials, e.g. `[["Revenues","110 B"],...]` — pre-formatted strings, not raw numbers |
| `rating_box` | list of `[label, value]` pairs | `[["Top rated","2 of 10"],["Best, worst rating","123 %, 24.3 %"]]` |
| `company_details` | list of company dicts | `name`, `rank`, `top_rated`, `trend`, `value` (raw ratio — display as `value * 100`, confirmed bug, see `infographic-design.md` § Resolved), `report_text` (RealRate's own written strength/weakness summary — quote verbatim, don't rewrite), `company_id` |
| `ecr_records` | `{year: {company_id: {rank, ecr}}}` | Multi-year history for every tracked company. `ecr` is already on the 0–100+ percent scale as a string (no ×100 needed here, unlike `company_details.value`) — coverage varies by company and by industry, don't assume every year is populated |
| `scentences` | list of str | RealRate's own generated analyst sentences about rank movement and standout comparisons — use verbatim, don't paraphrase. Can be empty. |

### Known unverified field
`trend`'s sign convention (positive = improved) has no cross-checkable field
in this payload the way `value` did — carry it as unverified.

---

## Sections are adaptive, not fixed

Earlier draft of this skill assumed a fixed list of exactly 10 sections,
each hard-bound to a specific field. That breaks the moment an industry's
data doesn't match the shape `us_air` happened to have — e.g. `scentences`
empty, `ecr_records` covering only 2 years, or `report_text` missing for
smaller industries.

Instead, `generate_industry_report.py` holds a **registry of candidate
sections** (see script's `SECTION_REGISTRY`). Each candidate declares:
- a title and a chart function
- a `requires(data)` check — a short predicate over the fetched JSON
- a `build(data)` function that returns the interpretation text

The script runs every candidate's `requires()` check against *this run's*
actual data and includes only the ones that pass, in a fixed priority
order. The number of pages in the output PDF is however many candidates
qualified — not a number decided in advance. A data-rich industry might get
9–10 sections; a sparse one might get 5. This is the same principle as the
"Known open question" pattern used throughout this repo: don't assert
something the data doesn't actually support.

### Current candidate pool (priority order; add more by extending `SECTION_REGISTRY`)

| Candidate | Requires | Chart | Text source |
|---|---|---|---|
| Industry Overview | `industry_box` non-empty | stat cards (no chart) | `industry_box`, `industry_label`, `num_companies` |
| Top 10 Rankings | `company_details` non-empty | bar vs. average line | computed |
| ECR Distribution | ≥ 3 companies in `company_details` | histogram | computed mean/std/min/max + `rating_box` |
| Top-Rated Snapshot | `rating_box` present | donut | `rating_box` "N of M" |
| Multi-Year ECR Trend | `ecr_records` has ≥ 3 years with ≥ 3 companies each | line, industry avg by year | `ecr_records` |
| Sector Leader Profile | rank-1 company has non-empty `report_text` | single bar, leader vs. avg | leader's `report_text`, quoted |
| Notable Movers | `scentences` non-empty | rank-change bar (from `scentences` companies matched to `company_details`) | `scentences`, quoted verbatim |
| Competitive Compression | ≥ 5 companies in `company_details` | range plot, ranks 6–N | computed spread |
| Data Confidence & Caveats | always | — (confirmed/unverified table) | carried from `infographic-design.md`'s resolved bugs |
| Takeaway & Full Ranking | always | — | synthesis + CTA link |

---

## Chart style (from `context/design-system.md` § Data Visualization Posts)
- Background: white or `#f5f5f5` — **never dark**, unlike the infographic
- Text: dark navy `#003b57`
- Primary series: `#00679B`
- Secondary series: `#3DBACD`
- Delta colors: positive `#419453`, negative `#C04A3A`
- No gridlines, no decorative background — data only

## Page layout
- **Cover** (unnumbered): logo on light background (`RealRate_logo_horizontal.svg`
  per design-system.md's light-background rule — different asset than the
  infographic's dark-background logo), industry name, marketing year,
  generation date, tagline.
- Each qualifying section is one PDF page: title, one chart (or stat cards
  for chart-less sections), one interpretation paragraph.
- All pages assembled into a single PDF via
  `matplotlib.backends.backend_pdf.PdfPages` — no docx, no headless browser.

## What never appears
Same standing rules as everywhere else in this repo: no hashtags, no
emojis, never "we" (always "RealRate"), full ranking URL uses the
**marketing year**: `https://realrate.ai/rankings/us_<slug>/<year>`.
