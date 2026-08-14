# Context — Infographic Design Tokens

Scoped subset of `context/design-system.md`, containing only what the Top 10
infographic generator needs. A full skill would load the whole design system;
this practice copy keeps only what one script actually consumes, so the link
between "context fact" and "line of code" stays visible.

Note this deliverable is a **Pillow-rendered PNG**, not an HTML→Puppeteer
export like the rest of the design system assumes — so it uses its own canvas
size (1200×1500, portrait) rather than the standard 1200×1200 square.

---

## Canvas
- **Size:** 1200×1500px (portrait — taller than the standard square post to
  fit a 10-row list plus header)
- **Margin:** 50px all sides

## Colors (from `context/design-system.md`)
| Role | Hex | RGB |
|---|---|---|
| Deep Navy — background | `#003b57` | `(0, 59, 87)` |
| Primary teal — accent/wordmark | `#3DBACD` | `(61, 186, 205)` |
| White — primary text | `#ffffff` | `(255, 255, 255)` |
| Off-White — secondary text/stats | `#f5f5f5` | `(245, 245, 245)` |
| Light Grey — flat/neutral trend | `#e8e8e8` | `(232, 232, 232)` |
| Strong Positive — trend up | `#419453` | `(65, 148, 83)` |
| Strong Negative — trend down | `#C04A3A` | `(192, 74, 58)` |

**Rotating accent pool** (blue family only, per the design system's "Dark
Backgrounds" table) — one is picked deterministically per industry slug so the
same industry always gets the same accent:
| Hex | Name |
|---|---|
| `#004a6e` | Navy Blue |
| `#005884` | Dark Blue |
| `#3389b1` | Medium Blue |
| `#34a2b3` | Blue Teal |
| `#2c8b9a` | Dark Teal |

## Logo (from `context/design-system.md` § Logo)
- Dark background → render `context/RealRate_logo_light.svg` at **44px
  height**, top-left, 50px margin — rasterized via `cairosvg`, not
  approximated with drawn text. Use the file's own colors as authored (a
  blue mark, white lettering, a teal mark) — they are intentional, not a
  placeholder to recolor.
- This was originally implemented as hand-drawn "Real"/"Rate" text, which
  silently drifted from the actual brand asset — a reminder that "see
  design-system.md" in a code comment isn't enough; the code has to actually
  load the file the context names.

## Typography
Real skill files call for Manrope, but that's a *web font* — this script
renders with Pillow directly (no browser), so it falls back to whatever
system font is available (DejaVu Sans / Liberation Sans / Arial). This is a
known gap versus the brand spec, not a deliberate substitution.

| Element | Size | Weight |
|---|---|---|
| Logo | 44px height | — (rendered from SVG, not a font) |
| "TOP 10" badge | 22px | bold |
| Title | 54px | bold |
| Subtitle | 24px | regular |
| Rank number | 30px | bold |
| Company name | 28px | bold |
| Stat value (ECR) | 30px | bold |
| Tagline | 18px | regular |

## What never appears on the image
- Hashtags
- Emojis
- Red/green anywhere except the trend arrow (`.change-positive` / `.change-negative` equivalents)

## Caption rules (applies to the matching .txt file, not the image)
- No hashtags
- Max 2 emoji (this skill uses 0)
- Never "we" — always "RealRate"
- Ends with `Full ranking: https://realrate.ai/rankings/us_<slug>/<year>`

## Resolved — ECR scale and year (verified against the live archive)
Two assumptions this skill originally carried as unverified turned out to be
wrong when checked against `ecr_records` and `rating_box` in the raw
`website-ranking.json` payload:

- **ECR scale:** `company_details[i].value` is a raw ratio, not a percent —
  display it as `value * 100`. Confirmed by cross-referencing the same
  company_id's entry in `ecr_records[year]`, which reports ECR on a 0–100+
  scale directly (e.g. `value: 1.2349...` == `ecr_records: "123"`), and by
  `rating_box`'s `"Best, worst rating": "123%, 24.3%"`.
- **Year:** the URL path uses the *balance sheet year* (e.g. `.../2025/...`),
  but the payload's own `year` field (and `url_segment`, e.g.
  `"2026-us-air"`) is the *marketing year* — that's what belongs in the
  title, filename, and `realrate.ai/rankings/...` URL, not the fetch-URL
  year.

`trend`'s sign convention (positive = improved) is still unverified — no
field in the payload cross-checks it the way `ecr_records` did for value.
Standing rule still applies to anything not explicitly confirmed here — see
`CLAUDE.md` → "Always verify ECR data."
