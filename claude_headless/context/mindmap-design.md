# Context — Mindmap Design & Data Schema

Backs `skills/mindmap.md`. This is a **deliberate redesign**, not a port,
of the real repo's `skills/mindmap.md` — read "Why redesigned" before
changing anything here.

---

## Why redesigned, not ported

The real skill hardcodes exactly 8 named companies and pulls executive/
office photos live from Wikipedia via `wiki_image_url()`, rendered through
Playwright + headless Chromium. Three problems with porting that as-is:

1. **Not generic** — adding company #9 means hand-editing two `elif`
   blocks in a 1873-line file with real financial figures typed in by
   hand, which is exactly the "don't hardcode data" mistake this whole
   practice project has been correcting.
2. **External, fragile dependency** — Wikipedia's API can rate-limit, an
   article can be renamed, an image can be removed; none of that is
   under this project's control and none of it is archive data RealRate
   can stand behind.
3. **Heavier runtime** — Playwright + a Chromium download is a lot of
   weight for a company card, when every other skill in `claude_practice`
   already renders adequately with Pillow + cairosvg.

This version works for **any company already in the live archive**, built
only from fields verified elsewhere in this project (see
`company-report-design.md`), rendered directly with Pillow — same
cross-platform font loader as `generate_infographic.py`.

---

## Branch data sources (all previously verified fields)

| Branch | Data source | Always present? |
|---|---|---|
| Industry Position | `rank`, `num_companies`/`len(company_details)`, `industry_label` | Yes |
| Financial Health | `value * 100`, industry average | Yes |
| Greatest Strength | `report_text`, regex-extracted | Only if `report_text` present and matches the template |
| Greatest Weakness | `report_text`, regex-extracted | Only if `report_text` present and matches the template |
| Multi-Year Trend | `ecr_records[year][company_id]` across years | Only if ≥ 2 years on record for this company |
| Rating Status | `top_rated` | Yes |

Branch count is therefore **adaptive, 4–6** — same principle as the report
skills, applied to a single image instead of PDF pages.

## `report_text` extraction — a confirmed regex bug and its fix

`report_text` follows one consistent template across every company checked
this session:

> "...The greatest strength of **{name}** ... is the variable **{X}**,
> increasing the Economic Capital Ratio by **{N}%** points.The greatest
> weakness of **{name}** is the variable **{Y}**, reducing the Economic
> Capital Ratio by **{M}%** points..."

A first attempt used a bare pattern `variable (.+?), increasing...` /
`variable (.+?), reducing...`. Because `re.search` locks onto the
**first** literal "variable" in the text (the strength sentence) and the
non-greedy `.+?` only stops at the *next* matching suffix — for the
weakness pattern, that meant it swallowed the entire strength sentence in
between, producing a paragraph-long "variable name" that overflowed the
branch circle onto the canvas edge.

**Fix:** anchor each pattern to its own sentence — `greatest strength of
.+? is the variable (.+?), increasing...` / `greatest weakness of .+? is
the variable (.+?), reducing...` — so each regex only searches within its
own sentence. See `parse_strength_weakness()` in the script.

**Defense in depth:** `draw_centered_text()` still truncates any line
wider than its circle regardless of source, since a future template change
in the archive's `report_text` wording could reintroduce the same failure
mode silently. The hub company name is exempted from truncation and
shrinks its font instead — a company's own name is the one label that
should never become "Strata Critica…".

---

## Layout
- Canvas 1920×1080, deep navy background (`#003b57`) — same brand dark
  background as the Top 10 infographic
- Hub: 380px circle, center, RealRate logo (`RealRate_logo_light.svg`,
  same asset/technique as `top10-infographic`) + company name + ECR/rank
  badge line
- Branches: evenly spaced around the hub at fixed radius, count = however
  many candidates qualified (4–6), each a 300px filled circle in a
  blue-family accent color, connected to the hub by a teal line
- No red/green — this is a dark-background asset, so semantic delta
  colors don't apply here (see `design-system.md`'s accent rule: dark
  backgrounds use light/teal accents only)

## What never appears
No hashtags, no emojis, never "we", no photos of real people (see "Why
redesigned" above) — RealRate's own logo and real company data only.
