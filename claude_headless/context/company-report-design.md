# Context — Company Report Design & Data Schema

Backs `skills/company-report.md`. Companion to `industry-report-design.md` —
same verification discipline, same adaptive-section principle, one level
deeper: a single company within an industry instead of the industry as a
whole.

---

## Data source

Same endpoint as the industry report — one company's entry inside
`company_details` carries everything, plus one extra live SVG fetch for the
causal graph:

```
GET https://www.realrate-archive.com/us_<slug>/<balance_sheet_year>/website-ranking.json
GET <that company's graph_url>   (a second live fetch, SVG)
```

### Per-company fields used (verified 2026-08-14 against `us_air` / Strata Critical Medical Inc)

| Field | Shape | Notes |
|---|---|---|
| `graph_url` | URL to SVG | RealRate's own causal "Influence Model Explanation" graph — a Graphviz-rendered DAG of balance-sheet variables flowing into ECR. Plain SVG 1.1 (paths, text, polygons) — renders cleanly with `cairosvg`, no exotic features. Render it as-is; don't redraw or reinterpret the diagram. |
| `report_url` | URL to PDF | RealRate's own full company report — link to it in the Takeaway section, don't try to fetch/embed it |
| `report_text` | str | Same field used in the industry report's leader section — quote verbatim |
| `table_records` | `{year: {input_variables: {...}, output_variables: {...}}}` | Per-year balance sheet figures as comma-formatted strings, e.g. `"126,192"`. **No unit is specified anywhere in the payload** — don't assume thousands/millions, see "Unresolved" below |
| `company_id` | str | Key into `ecr_records[year]` for this company's own multi-year ECR history |

### CONFIRMED DISCREPANCY — two different ECR values for the same company/year
The causal graph SVG has its own `EconomicCapitalRatio` node with a literal
percentage label (e.g. `"54.3%"`) baked into the graph's `<text>` elements.
This **does not match** `company_details.value * 100` for the same
company, same industry, same year (verified: 123.5% vs. 54.3% for the same
company/id/year). Both numbers come directly from RealRate — this isn't a
computation error on this skill's part.

**Do not silently pick one.** The company report:
1. States the headline ECR from `company_details.value * 100` (same
   source used everywhere else in this repo's skills, so it stays
   consistent across deliverables)
2. Separately states whatever the causal graph's own node says, labeled as
   "per the causal graph" — extracted from the SVG's text nodes (see
   `parse_graph_ecr()` in the script), not re-derived
3. Flags the mismatch explicitly in the Data Confidence & Caveats section
   — never averaged, never "corrected" to make them agree

### Unresolved: financial figure units
`table_records` values like `"126,192"` have no unit label anywhere in the
payload (no "$K" / "$M" / currency marker). `industry_box` (industry-level
aggregate) does use suffixed units ("110 B"), but that's a different field
serving a different purpose — don't assume the same scale applies here.
Chart axis is labeled "Reported value (unit not specified in payload)"
rather than guessing.

---

## Causal graph SVG parsing

The graph's node structure (Graphviz output) splits a label across
multiple `<text>` elements inside one `<g class="node">...<title>NodeName
</title>...</g>` block. To find the model's own stated ECR:

1. Locate the block whose `<title>` is exactly `EconomicCapitalRatio` (no
   spaces — Graphviz strips them from titles even though the visible
   label has them)
2. Within that block, the last `<text>...>` matching `-?\d+\.?\d*%` is the
   value

Same technique generalizes to reading any other node's percentage if a
future section needs it (e.g. `EconomicCapitalRatiobeforeLimitedLiability`,
which this graph shows as a distinct intermediate value, one more sign
these are genuinely different quantities, not rounding drift).

---

## Sections are adaptive (same principle as industry-report-design.md)

| Candidate | Requires | Chart | Text source |
|---|---|---|---|
| Company Overview | always (once a company resolves) | — (stat cards) | `name`, `rank`, `value`, `top_rated`, `trend` |
| Causal ECR Graph | `graph_url` fetches successfully | the real SVG, rasterized | graph's own node values + discrepancy note |
| Strengths & Weaknesses | `report_text` non-empty | — | `report_text`, quoted verbatim |
| Balance Sheet Snapshot | `table_records` has ≥ 1 year | bar chart, latest year's `output_variables` | computed, unit caveat included |
| Multi-Year ECR History | this `company_id` appears in `ecr_records` for ≥ 3 years | line chart | computed |
| Peer Comparison | `company_details` has ≥ 2 companies | bar: this company vs. industry avg vs. #1 | computed |
| Data Confidence & Caveats | always | — | ECR discrepancy, unit caveat, `trend` caveat |
| Takeaway & Full Report | always | — | synthesis + `report_url` + ranking URL |

## Chart style, page layout, what never appears
Same as `industry-report-design.md` — white/light background only, navy
text (`#003b57`), primary `#00679B` / secondary `#3DBACD`, no hashtags, no
emojis, never "we".
