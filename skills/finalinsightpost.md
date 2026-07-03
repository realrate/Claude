---
name: finalinsightpost
description: Generate a RealRate "Insight Post" (Types 1-4) — LinkedIn single-image or carousel graphics that report a company's or industry's ECR (Economic Capital Ratio) ranking result, plus a ready-to-post LinkedIn caption. Use when asked to create/generate an insight post, ECR ranking graphic, or LinkedIn insight carousel for a RealRate-ranked company or industry. Usage: /finalinsightpost <1|2|3|4> <industry> [company]
---

# Skill — RealRate Insight Post Generator

This skill does **not** assume any personal machine path and does
**not** require a sibling `RealRate Logos/` folder to already exist — the
RealRate logo is embedded as base64 below. It does not depend on any
insight-post-specific script or template file elsewhere in the repo (no
`export.py`, no `insight1-template.html`, etc.) — the four post-type
templates and the PNG/PDF export script are embedded in full below. It
*does* read the two files listed under Load — those live in this
repo's shared `context/` folder, are checked into git, and travel with
every clone, so they carry no personal-path risk. Do not read or
reference any other file in the repo (no other `context/*.md`, no other
skill's files, no absolute paths).

## Load

Read these before building any post — they are this repo's single
source of truth for brand tone and identity, shared across every
RealRate content type (not just insight posts):

- `context/brand-core.md` — company overview, tagline, colours, links
- `context/brand-voice.md` — tone rules, never-use phrases,
  content-accuracy rules, hashtag/link/tagging rules

(Paths are relative to this repo's root — `skills/` sits directly under
it, matching every other skill file in this folder.) These files are
the authority: if this repo's copy of `brand-voice.md` says something
different from the condensed "Brand rules" section below (e.g. hashtag
policy has changed over time), follow the loaded file, not the
fallback. If a user runs this skill from a copy of the repo where
`context/` was not included, fall back to the condensed "Brand rules"
section below and tell the user those two files were not found.

Do **not** load `context/design-system.md` — it documents an older,
superseded layout system (L1–L4 minimal-stat templates). The bento-grid
design system actually in use today is embedded in full in the "Design
System" section below; that section is the current authority for
layout, colour, and typography, not `context/design-system.md`.

## What this skill produces

A LinkedIn graphic reporting a RealRate ECR (Economic Capital Ratio)
ranking result, in one of four formats:

| Type | Format | Story |
|---|---|---|
| **Insight 1 — Company Editorial** | Single image, 1200×1200px | One company's ECR result vs. the industry average |
| **Insight 2 — Industry YoY Shift** | Carousel, up to 3 slides, 1200×1200px each | How an industry's average ECR moved year-over-year |
| **Insight 3 — Rotating Angle** | Single image, 1080×1350px | A rotating structural/methodology angle on an industry |
| **Insight 4 — NTR Rotating** | Single image, 1080×1350px | Why a company fell short of Top-Rated status |

Each run produces: the HTML source file(s), a PNG export at the correct
pixel dimensions (and an auto-merged PDF for Insight 2's 3 slides), and a
`linkedin-post.txt` caption file.

## How this skill works — step by step

1. **Ask the user (if not already given):** which insight type (1-4),
   which industry, which company (if type 1 or 4), which angle (if the
   angle bank offers a choice), and where the output should be written
   (default: current working directory). Never guess a company's ECR
   data — always get it from the user or the sources in step 3.

2. **Determine light/dark theme.** Insight posts must **alternate
   between light theme and dark theme every time, regardless of type**
   — never publish two posts of the same theme back-to-back. Look for
   the most recently created insight HTML file in the output location
   (or ask the user which one published last), read its
   `<html data-theme="...">` attribute, and use the opposite theme for
   this post. If this is the very first insight post ever generated in
   this location, default to **dark**.

3. **Verify the ECR data before building anything.** This skill has no
   built-in data source — RealRate's internal archive
   (`realrate-archive.com`) is only reachable to RealRate team members
   and is never to be shared publicly even when reachable. If you have
   access to it, verify every figure there. If you do not, or the user
   is external to RealRate, ask the user directly for the exact
   verified figures (ECR score, rank, industry average, driver
   contributions in pp) and do not fabricate or estimate any number.
   Separately, fetch `https://realrate.ai/rankings` (public site) to
   confirm the exact industry URL slug before using any
   `realrate.ai/rankings/[industry]/[year]` link — never guess the
   slug from the industry name (e.g. the slug is often `us_food`, not
   `us-food` or `food`).

4. **Pick an angle** from the angle bank for the chosen type (see
   Insight 1-4 sections below).

5. **Build the HTML file(s)** starting from the matching template in
   the Templates section below — copy it verbatim, then fill in every
   `[BRACKET]` placeholder with real, verified data. Follow the Design
   System section for all colour, layout, and typography rules. Give
   every post its own accent colour — do not reuse an accent already
   used by another post in the output location unless the user asks
   for visual consistency across a series.

6. **Use the embedded RealRate logo — never a relative file path.**
   Every `<img>` that shows the RealRate logo must use the exact data
   URI from the "Embedded Assets" section below as its `src`. Do not
   write `<img src="../../RealRate Logos/...">` — there is no
   guarantee that path exists on the machine this skill runs on.

7. **Company logos (Insight 1 and 4 only):** if you can obtain the
   company's official logo as a local file (transparent PNG, dark or
   coloured art — not white-on-transparent), save it next to the
   output HTML and reference it by bare filename (no relative path
   needed since it's alongside the file). Convert it to a base64 data
   URI instead if you want the HTML to be fully self-contained. If no
   logo is available, fall back to a Manrope text badge (see Company
   Logo Pill rules below) — never leave a broken image.

8. Apply `.change-negative` / `.change-positive` classes to every delta
   value (already defined in every template's CSS).

9. **Write the export script** by copying the Python source verbatim
   from the "Generator source" section below into a new file named
   `export_insight.py`, placed in the same directory as the HTML
   file(s) you just created (or the common parent directory if
   exporting several at once).

10. **Run it:**
    ```
    python export_insight.py [path/to/file1.html] [path/to/file2.html ...]
    ```
    (fall back to `python3` if `python` doesn't resolve). With no
    arguments it exports every `insight*.html` file found under the
    script's directory (recursively, skipping `*-template.html`). It
    auto-regenerates the Insight 2 carousel PDF (`[folder]-slides.pdf`)
    whenever it finds 2+ `insight2_slide*.png` files in the same
    folder.

11. **Delete `export_insight.py`** after the run (matching this
    skill's "don't leave a script behind" convention) unless the user
    wants to keep it for faster re-runs.

12. **Write the caption** to `linkedin-post.txt` next to the HTML/PNG
    using the approved caption structure for the chosen type (below).

13. **QA against the checklist** for the chosen type (below) before
    reporting the result.

14. Report the output file paths to the user. This skill only
    generates files — never open, upload, or post the image or
    caption anywhere.

---

## Brand rules (apply to every post, regardless of type)

`context/brand-voice.md` and `context/brand-core.md` (loaded per the
Load section above) are the authoritative source for these — the list
below is a condensed fallback for when those files aren't reachable,
kept in sync with them but not a substitute for reading the real files.

- **Never use** the phrases: "excited to share," "game-changing,"
  "revolutionary," "best-in-class" (without data).
- **Never link** to sales pages, pricing, or the internal archive in
  any public-facing caption or image — always link to
  `realrate.ai/rankings/[industry]/[year]` or `realrate.ai/methodology`.
- **Embed the full URL in the caption body** — never replace it with
  "link in first comment."
- **Never tag companies** in the caption text — company tags belong in
  the first pinned comment only (not produced by this skill; tell the
  user to add them).
- **Max 5 hashtags** per caption, always include `#RealRate`.
- **No emojis** on the image itself; **max 2 emojis** in the caption.
- **Every post must include** the tagline exactly as written:
  `Powered by RealRate: Using Explainable Financial AI` — it appears on
  the image (footer, every template already has it) and does not need
  to be repeated in the caption unless it reads naturally there.
- One accent colour only per post — never mix accent hues within a
  single post or across slides of the same Insight 2 carousel.

---

## Embedded Assets

### RealRate logo — base64 data URI

Use this exact string as the `src` of every RealRate logo `<img>` tag in
every template below. Do not truncate or re-encode it.

```
data:image/png;base64,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
```

Example usage (dark or light theme, 1200×1200 templates):
```html
<div class="logo-pill">
  <img src="data:image/png;base64,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" alt="RealRate">
</div>
```

(No `onerror` fallback is needed — a data URI cannot 404. Templates
below keep the `onerror` handler only as defense-in-depth; you may
remove it once the data URI is in place.)

---

## Insight 1 — Company Editorial

### Angle Bank
| Angle | When to use |
|---|---|
| **Reputable, Not Top-Rated** | A well-known company failed to reach Top-Rated — ECR contradicts their reputation |
| **Unknown, Top-Rated** | A lesser-known company made Top-Rated ahead of recognised names |
| **The Surprise** | Any non-obvious finding — score, position, driver, or trajectory that defies expectation |

**Default angle: The Surprise.** When generating a full 4-post cycle for
an industry, Insight 1 defaults to **The Surprise** — Insight 4 (NTR
Rotating) is already a "company missed Top-Rated" story, so opening the
cycle with "Reputable, Not Top-Rated" duplicates that framing. Only use
"Reputable, Not Top-Rated" or "Unknown, Top-Rated" instead of The
Surprise when explicitly requested, or when generating Insight 1 as a
standalone post outside a full cycle.

### Data to Verify
- [ ] Company name (exact spelling)
- [ ] Current rank and total companies ranked
- [ ] ECR score (%)
- [ ] Industry average ECR (%)
- [ ] Strength driver + contribution (pp) — Unknown Top-Rated, The Surprise
- [ ] Weakness driver + contribution (pp) — Reputable Not Top-Rated

### Caption Structure (approved)
1. Hook — methodology positions the finding: *"Balance sheet strength and market prominence are different things. RealRate's ECR isolates how structurally sound a company's finances are. In [year], that lens produced a clear result."*
2. "In RealRate's recent financial assessment for the [industry] ranking, [Company] ranks #[N]."
3. One punchy gap line — "Sitting [X] points above/below the industry average."
4. `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

**Mandatory on Reputable Not Top-Rated:** *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### QA Checklist
- [ ] ECR values verified with the user or the internal archive
- [ ] Company name exact spelling confirmed
- [ ] One accent color only
- [ ] Theme alternated from the previous insight post and `data-theme` set on `<html>`
- [ ] Delta values use `.change-negative` / `.change-positive`
- [ ] RealRate logo uses the embedded base64 data URI, not a relative path
- [ ] Tagline present on image
- [ ] Exported at 1200×1200px

### File Naming
`insight1_[companyslug].html` / `.png`

---

## Insight 2 — Industry YoY Shift

### Options
| Option | When to use |
|---|---|
| **Industry-Wide** | Sector average ECR movement is the story |
| **Company-Level** | A well-known company's YoY shift is the headline |

### Slide Structure (max 3 slides)
- **Slide 1 — The Shift:** Headline number leads. ECR avg then vs now. Change in points is the visual hero.
- **Slide 2 — What Drove It:** Key structural reason. One clear finding.
- **Slide 3 — The Context:** *(only if it adds meaningful information)*

### Data to Verify
- [ ] Industry ECR average — current year
- [ ] Industry ECR average — prior 1–2 years
- [ ] ECR change (pp)
- [ ] # companies ranked — current vs prior (if changed)
- [ ] Key driver of shift

### Caption Structure (approved)
Design carries the numbers. Caption adds context, commentary, and learnings — never restate figures visible on slides.
1. Open with the pattern, not the data point — e.g. *"Two years of stability. Then a shift."*
2. Explain why the pattern matters more than the single number
3. Commentary — what it means, what ECR captured, what the audience should be asking
4. `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

### QA Checklist
- [ ] All ECR values verified
- [ ] Max 3 slides, each with one clear message
- [ ] Slide numbering visible on every slide
- [ ] Consistent background and typography across slides
- [ ] Theme alternated from the previous insight post, same theme across all slides, `data-theme` set on `<html>`
- [ ] Delta values use `.change-negative` / `.change-positive`
- [ ] RealRate logo uses the embedded base64 data URI on every slide
- [ ] Tagline on every slide

### File Naming
`insight2_slide[1-3]_[industryslug].html` / `.png`, carousel PDF `[industryslug]-yoy-slides.pdf`

---

## Insight 3 — Rotating Angle

### Angle Bank
| Angle | Story |
|---|---|
| **The Industry Blind Spot** | One weakness driver appearing across most companies — a structural drag most haven't addressed |
| **The Market vs The Balance Sheet** | A company the market rates highly has a low ECR, or vice versa |
| **The Methodology Moment** | What ECR measures that other ratings don't |
| **The Investor Signal** | Is this industry financially healthy right now? ECR answers it |
| **The Macro Lens** | Industry under pressure from a macro trend — what the balance sheets show |

Must not have been used in the prior 2 ranking cycles for the same industry.

### QA Checklist
- [ ] Angle not reused from prior 2 cycles for this industry
- [ ] RealRate logo uses the embedded base64 data URI
- [ ] Delta values use `.change-negative` / `.change-positive`
- [ ] Exported at 1080×1350px

### File Naming
`insight3_[angle-slug]_[industryslug].html` / `.png`

---

## Insight 4 — Non-Top-Rated Rotating

### Angle Bank
| Angle | Story |
|---|---|
| **Almost There** | Company just below Top-Rated threshold — one driver is the gap |
| **The One Thing** | Single weakness driver pulling ECR below threshold |
| **The Fallen** | Company that held Top-Rated in prior year and has since dropped |
| **The Sector Drag** | Multiple companies in same sub-sector all failing to reach Top-Rated |
| **Close But Not Rated** | Looks strong by traditional metrics but ECR threshold not met |
| **The Due Diligence Gap** | Why NTR status matters for investors and partners |

**Mandatory on all NTR posts:** *"ECR measures balance sheet strength, not revenue performance or market reputation."* (already present in every template's `.disclaimer` element — never remove it.)

### QA Checklist
- [ ] Disclaimer line present and unedited
- [ ] RealRate logo uses the embedded base64 data URI
- [ ] Delta values use `.change-negative` / `.change-positive`
- [ ] Exported at 1080×1350px

### File Naming
`insight4_[angle-slug]_[companyslug].html` / `.png`

---

## Design System

### Theme Rotation — Light / Dark (Standing Rule)

Insight posts must **alternate between light theme and dark theme every time, regardless of type**. Never publish two posts of the same theme back-to-back — the rotation is across the whole output location, not per-type and not per-industry.

Every generated file must declare its theme on the root tag so this is a one-glance check next time:
```html
<html lang="en" data-width="1200" data-height="1200" data-theme="dark">   <!-- or data-theme="light" -->
```

Dark theme is the original spec documented throughout this Design System section (dark backgrounds, white text, coloured glows). Light theme uses the **same** bento-grid structure, corner brackets, icon strips, per-post accent colour, and typography scale — only the surface, text, border, and shadow tokens flip. Do not mix themes within a single post or across slides of the same Insight 2 carousel.

**Light theme background:**
```css
background:
  radial-gradient(ellipse 900px 800px at 0% 100%, rgba(accent,0.10) 0%, transparent 58%),
  radial-gradient(ellipse 500px 350px at 75% 5%,  rgba(accent,0.05) 0%, transparent 50%),
  linear-gradient(150deg, #FFFFFF 0%, #F7F8FB 45%, #F1F3F7 100%);
```
`body { margin:0; background:#fff; }` (in place of `#000` on dark theme).

**Light theme text colours:**
| Dark theme token | Light theme replacement |
|---|---|
| `--white: #ffffff` (headlines) | `--ink: #0F172A` |
| `rgba(255,255,255,0.88)` (body text) | `rgba(15,23,42,0.82)` |
| `rgba(255,255,255,0.72)` (secondary/labels) | `rgba(15,23,42,0.60)` |
| `rgba(255,255,255,0.65)` (tagline) | `rgba(15,23,42,0.55)` |

Accent-coloured text (ecr-value, driver-pts, etc.) uses the saturated `--accent`, not `--accent-lt` — `--accent-lt` is tuned for dark backgrounds and fails contrast on white. If `--accent` itself is too light, darken it ~15% toward black for AA contrast (`--accent-dk`).

**Light theme borders:**
| Dark theme | Light theme |
|---|---|
| `rgba(255,255,255,0.07)` (cell borders) | `rgba(15,23,42,0.08)` |
| `rgba(255,255,255,0.10)` (border-top accents) | `rgba(15,23,42,0.10)` |
| `rgba(255,255,255,0.03)` (subtle cell borders) | `rgba(15,23,42,0.05)` |

**Light theme cell fills:**
- Hero/accent cells: `linear-gradient(145deg, rgba(accent,0.14) 0%, rgba(accent,0.06) 55%, rgba(accent,0.02) 100%)` — roughly half the opacity used on dark theme
- Neutral cells: `rgba(15,23,42,0.03)` background in place of `rgba(0,0,0,0.40)`

**Glow → shadow:** dark theme's coloured `text-shadow` glows read as noisy haze on a white background. On light theme, replace with a soft neutral drop shadow:
```css
text-shadow: 0 2px 10px rgba(15,23,42,0.12);
```
Keep exactly one subtle accent-tinted shadow on the single largest hero number only (ECR score / stat hero), for brand identity: `0 0 40px rgba(accent,0.15), 0 2px 10px rgba(15,23,42,0.12)`.

**Corner brackets:** `--gold` stays unchanged on both themes — it is the one constant brand marker across every post.

**Logo pills (RealRate + company):** background stays white on both themes. On light theme, add `border: 1px solid rgba(15,23,42,0.08);` to `.logo-pill` and `.company-logo-pill` so the pill doesn't disappear into the white page.

**Icon chips / angle tag:** keep the `--accent` tinted background + border as on dark theme; verify accent text passes contrast against the lighter chip fill — use `--accent-dk` instead of `--accent-lt` if needed.

### Layout — Bento Grid

All insights use a **bento grid layout**: every data zone lives in a framed, bordered cell with `background + border + border-radius`. No free-floating numbers.

**Core principles:**
- **Size = importance**: the hero metric cell gets `flex:1` (or `grid-row: 1/-1`), supporting cells are fixed or smaller
- **Cell anatomy**: `label (small, uppercase, #ffffff or accent-lt)` → `value (large, accent or white, glowing)` → `sub-text (medium, ≥90% white)` — top to bottom inside every cell
- **Gutters as dividers**: gap between cells IS the visual separator — no thin 1px rules inside the grid
- **Accent via border-left**: hero and driver cells use `border-left: 4px solid var(--accent)` for colour identity

**Per post type:**
| Post | Hero zone | Structure |
|---|---|---|
| Type 1 (Company Editorial) | ECR+compare merged zone (fixed height 260px) | company-cell → ecr-compare-zone (grid 1fr 272px) → driver-grid |
| Type 2 Slide 1 (Year Split) | Year cells in `grid-template-columns: 1fr 80px 1fr` | year-bento → context-cell |
| Type 2 Slide 2 (Driver Cards) | Primary card `flex:1.4`, secondary `flex:1` | driver-stack → finding-cell |
| Type 2 Slide 3 (Context) | Rated cell spans `grid-column: 1/-1` in 3-col grid | stat-grid (asymmetric) → threshold-row → implication |
| Type 3 (Blind Spot / Data Table) | Bento stat cells (2-col) above data table | bento-stat-grid → table-wrap → avg-bar |
| Type 4 (NTR / Donut) | CSS Grid `300px 1fr` × 2 rows; donut `grid-row:1/-1` | hero-zone → data-strip → disclaimer |

### Header — Type 1 (Company Editorial)

Type 1 posts include **3 industry icon chips** in the header row (not 4), between the RealRate logo pill and the angle tag.

```css
.logo-pill { padding:16px 36px; border-radius:10px; }
.logo-pill img { height:50px; }
.angle-tag { font-size:18px; padding:14px 30px; border-radius:6px; letter-spacing:4px; }
.header-icon-chip { padding:12px 18px; gap:10px; border-radius:8px; }
.header-icon-chip svg { width:21px; height:21px; }
.header-icon-chip span { font-size:13px; letter-spacing:1.5px; }
```

### Company Cell — Type 1 (CRITICAL)

`.company-cell` **must always include `overflow:hidden`** to prevent the white logo pill background from bleeding through the rounded corners and creating a visible white bar below the cell:

```css
.company-cell {
  flex-shrink:0; overflow:hidden;   /* ← overflow:hidden is mandatory */
  background: linear-gradient(135deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.020) 100%);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:14px; padding:28px 34px; margin-bottom:12px;
}
```

### ECR + Compare Zone — Type 1

The ECR score and compare cells are merged into a single CSS grid zone (not separate elements):

```css
.ecr-compare-zone {
  display:grid; grid-template-columns:1fr 272px; gap:12px;
  flex:0 0 auto; height:260px; margin-bottom:12px;
}
/* Left: ecr-cell — right: compare-stack (flex column of 2 cmp-cells) */
```

### Icon Strip — Types 2, 3, 4 (Industry Posts)

Industry posts include a **horizontal icon strip** placed between the title/headline block and the main data grid.

```css
.icon-chip { padding:11px 20px; border-radius:8px; }
.icon-chip svg { width:20px; height:20px; }
.icon-chip span { font-size:13px; letter-spacing:2px; }
```

### Company Logo Pill — Type 1 (Company Editorial)

**Rule:** Always prefer the official company logo image in the pill —
`<img src="[logo-file or data URI]" alt="[Company]" onerror="this.outerHTML='[text-badge-fallback]'">`.
The pill background is white, so use a PNG where the logo is dark or
coloured on transparent (not white-on-transparent). Always include
`display:block` on the img via
`.company-logo-pill img { display:block; max-height:64px; max-width:160px; object-fit:contain; }`
— this removes the inline baseline gap. If no logo file exists yet, use
a text badge fallback until the logo is sourced:

```html
<div class="company-logo-pill">
  <div>
    <div class="company-badge-name">[SHORT NAME]</div>
    <div class="company-badge-sub">[SUFFIX]</div>
  </div>
</div>
```

### Colour Palette — Per Post

Each post has its own accent colour based on industry and topic. **Do not mix accents within a single post.** Pick a fresh hex pair for every new post — examples of hues already used across prior posts (avoid exact repeats unless intentionally matching a series): ice blue `#6B8CAE`, gold `#D4AA42`, teal `#2EC4DC`, royal blue `#2563EB`, steel orange `#F97316`, deep violet `#7C3AED`, dark purple `#6D28D9`, orange `#F97316`, amber `#F0A828`, deep orange `#EA580C`, blue `#3B82F6`, rust `#DC5F3C`, petrol teal `#0D9488`, bronze `#B5651D`, slate blue `#3E6182`, steel blue `#4A6FA5`, green `#22C55E`, rose `#F43F5E`, sky blue `#0EA5E9`.

**Always present across all posts:**
- `--gold` `#D4AA42` — corner bracket decoration
- `--green` `#5EC45A` / `--green-lt` `#90D48C` — Top-Rated cells
- `--red` `#E84836` / `--red-lt` `#FF8870` — weakness drivers, penalties

### White Borders on Warm Dark Backgrounds

On warm dark backgrounds (orange, amber, deep orange), white borders at low opacity appear much more visible than on cool dark backgrounds. **Rule for warm-background posts:**

- All `rgba(255,255,255,0.xx)` border values must be ≤ `0.05`
- Replace with accent-coloured borders where structure requires a visible divider
- Always include `body { margin:0; background:#000; }` after the CSS reset to prevent any white edge bleed in PNG exports

```css
/* Required in every HTML file */
html,body { width:1200px; height:1200px; overflow:hidden; font-family:'Manrope',sans-serif; }
body { margin:0; background:#000; }
```

### Cell Backgrounds

Hero/accent cells use **diagonal gradient fills**, never flat colours:
```css
background: linear-gradient(145deg, rgba(accent, 0.22) 0%, rgba(accent, 0.09) 55%, rgba(accent, 0.04) 100%);
```

Neutral dark cells (use on cool-background posts; reduce border opacity on warm backgrounds):
```css
background: rgba(0,0,0,0.40);
border: 1px solid rgba(255,255,255,0.07);   /* ≤0.05 on warm backgrounds */
border-top: 2px solid rgba(255,255,255,0.10); /* ≤0.06 on warm backgrounds */
```

### Glow on Hero Numbers

All large metric values carry a `text-shadow` glow matching the accent colour:
```css
/* ECR value (116px) */
text-shadow: 0 0 100px rgba(accent, 0.70), 0 2px 24px rgba(0,0,0,0.60);

/* Driver pts, compare gap, year value, stat value */
text-shadow: 0 0 40–60px rgba(accent, 0.45–0.55), 0 2px 16px rgba(0,0,0,0.50);
```

### Typography

- Font: **Manrope** (Google Fonts), weights 600 / 700 / 800 / 900
- ECR hero value: `font-size: 116px; font-weight: 900; letter-spacing: -5px`
- Company name: `font-size: 72–78px; font-weight: 900; letter-spacing: -2px`
- Industry label: `font-size: 34–38px; font-weight: 900; letter-spacing: 3px; text-transform: uppercase`
- Stat hero values: `font-size: 68–108px; font-weight: 900`
- Cell labels: `font-size: 13–16px; font-weight: 800; letter-spacing: 3–5px; text-transform: uppercase`
- Body/descriptor text: `font-size: 20–24px; font-weight: 600; color: #ffffff` — always use full white, never `rgba(white, <0.90)` on dark backgrounds

### Corner Brackets

All slides share identical gold corner brackets via `::after` pseudo-element (already included in every template below):
```css
.slide::after {
  content:''; position:absolute; inset:18px;
  background:
    linear-gradient(to right,  var(--gold) 52px, transparent 52px) top    left  /52px 2px no-repeat,
    linear-gradient(to bottom, var(--gold) 52px, transparent 52px) top    left  /2px 52px no-repeat,
    /* ... 6 more corners, see templates below */;
  z-index:1; pointer-events:none;
}
```

### Type 3 Data Table — Row Count Limit (CRITICAL)

If you build a Type 3 "data table" variant (`.table-wrap` → `.table-header` → `.table-body` → `.table-row`), it has a fixed vertical budget within the 1200×1200 canvas. `.table-row` must **never** include `min-height:0` — that lets flex rows shrink below their content height and overlap each other. Even with correct sizing, **the table body only reliably fits 3 data rows** at the established type scale (24px row-name / 18px row-ecr / 50px row-penalty) before the last row gets clipped by `.table-body`'s `overflow:hidden`. Always cap the table at **3 rows** (top 3 by magnitude) regardless of how many companies are actually affected — a bento-stat cell above the table can still state the true total (e.g. "9 of 23") even when only 3 rows are shown.

### Border Radius

All bento cells: `border-radius: 14px`
Smaller elements (tags, badges): `border-radius: 6–8px`
Round badges: `border-radius: 30px`

### Dark Purple — Highlighted Text Pattern (optional variant)

For deep purple posts (`--purple: #6D28D9`), use the **highlighted text** approach instead of the standard muted-opacity text style:

**Principle:** All text is pure `#ffffff`. Text "highlights" off the dark purple background via `text-shadow` glow — never reduced opacity below 0.90.

```css
:root {
  --purple: #6D28D9; --purple-mid: #7C3AED; --purple-lt: #C4B5FD;
  --violet: #8B5CF6; --violet-lt: #DDD6FE;
}

/* Background: two-point radial purple glow on near-black */
background:
  radial-gradient(ellipse 700px 500px at 75% 5%,  rgba(109,40,217,0.28) 0%, transparent 55%),
  radial-gradient(ellipse 400px 300px at 15% 85%, rgba(124,58,237,0.18) 0%, transparent 50%),
  linear-gradient(180deg, #0e0818 0%, #0b0614 55%, #080410 100%);

/* Cell fills: heavy purple (up to 0.40 opacity) */
background: linear-gradient(145deg, rgba(109,40,217,0.40) 0%, rgba(109,40,217,0.22) 60%, rgba(109,40,217,0.10) 100%);
border: 1px solid rgba(196,181,253,0.40);   /* lavender-tinted border */
border-top: 4px solid var(--violet-lt);

/* Hero numbers: white + purple glow */
color: #ffffff;
text-shadow: 0 0 80px rgba(196,181,253,0.90), 0 0 30px rgba(109,40,217,0.70), 0 2px 12px rgba(0,0,0,0.60);

/* Inline text highlights (em, key phrases): purple pill background */
background: linear-gradient(135deg, rgba(109,40,217,0.55) 0%, rgba(124,58,237,0.40) 100%);
border-radius: 6px; padding: 0 10px 2px;
text-shadow: 0 0 30px rgba(196,181,253,0.80);
box-shadow: 0 0 20px rgba(109,40,217,0.40);

/* Sub-row / secondary text: --violet-lt (#DDD6FE) keeps it purple-tinted but bright */
color: var(--violet-lt);
```

**Icon chips on dark purple posts:** heavier fill `rgba(109,40,217,0.30)` + lavender border `rgba(196,181,253,0.35)` + white text (not accent-coloured).

---

## Templates

Copy the relevant template verbatim into a new `.html` file, then fill
in every `[BRACKET]`. Every template's RealRate `<img>` tag is written
as `<img src="REALRATE_LOGO_DATA_URI" alt="RealRate">` — replace
`REALRATE_LOGO_DATA_URI` with the full data URI string from "Embedded
Assets" above before saving the file (do not leave the literal token in
the output).

### Insight 1 — Company Editorial template (1200×1200, dark theme default)

```html
<!DOCTYPE html>
<!--
  INSIGHT 1 — Company Editorial  |  Dark Bento Grid  |  1200×1200 px
  Angles: Reputable Not Top-Rated / Unknown Top-Rated / The Surprise
  FILL IN every [BRACKET] before exporting.
  Replace --accent / --accent-lt with a fresh hex pair (see Colour Palette above).
  If the angle is TOP-RATED, keep the <span class="rank-top-rated"> badge.
  If the angle is NOT TOP-RATED (reputable-not-top-rated), delete that badge,
  swap .gap-cell to red styling (see notes at the bottom of this template).
-->
<html lang="en" data-width="1200" data-height="1200" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <title>RealRate — Insight 1 — [COMPANY NAME]</title>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --accent:    #2EC4DC; --accent-lt:#80DCEC;
      --accent-30: rgba(46,196,220,0.30);
      --accent-18: rgba(46,196,220,0.18);
      --accent-10: rgba(46,196,220,0.10);
      --gold:    #D4AA42; --gold-lt:#F0CC68;
      --green:   #5EC45A; --green-lt:#90D48C;
      --red:     #E84836; --red-lt:#FF8870;
      --white:   #ffffff;
      --w70: rgba(255,255,255,0.70); --w50:rgba(255,255,255,0.50);
      --w45: rgba(255,255,255,0.45); --w22:rgba(255,255,255,0.05);
      --w14: rgba(255,255,255,0.04); --w08:rgba(255,255,255,0.03);
      --w06: rgba(255,255,255,0.03);
    }
    html,body { width:1200px; height:1200px; overflow:hidden; font-family:'Manrope',sans-serif; }
    body { margin:0; background:#000; }

    .slide {
      width:1200px; height:1200px;
      background:
        radial-gradient(ellipse 900px 800px at 0% 100%, rgba(46,196,220,0.18) 0%, transparent 58%),
        radial-gradient(ellipse 500px 350px at 75% 5%,  rgba(46,196,220,0.07) 0%, transparent 50%),
        linear-gradient(150deg, #071a20 0%, #0b1520 45%, #080e18 100%);
      display:flex; flex-direction:column; position:relative; overflow:hidden;
    }
    .slide::before {
      content:''; position:absolute; inset:0;
      background: repeating-linear-gradient(-45deg, transparent 0, transparent 40px, rgba(255,255,255,0.006) 40px, rgba(255,255,255,0.006) 41px);
      z-index:0; pointer-events:none;
    }
    .slide::after {
      content:''; position:absolute; inset:18px;
      background:
        linear-gradient(to right,  var(--gold) 52px, transparent 52px) top    left  /52px 2px no-repeat,
        linear-gradient(to bottom, var(--gold) 52px, transparent 52px) top    left  /2px 52px no-repeat,
        linear-gradient(to left,   var(--gold) 52px, transparent 52px) top    right /52px 2px no-repeat,
        linear-gradient(to bottom, var(--gold) 52px, transparent 52px) top    right /2px 52px no-repeat,
        linear-gradient(to right,  var(--gold) 52px, transparent 52px) bottom left  /52px 2px no-repeat,
        linear-gradient(to top,    var(--gold) 52px, transparent 52px) bottom left  /2px 52px no-repeat,
        linear-gradient(to left,   var(--gold) 52px, transparent 52px) bottom right /52px 2px no-repeat,
        linear-gradient(to top,    var(--gold) 52px, transparent 52px) bottom right /2px 52px no-repeat;
      z-index:1; pointer-events:none;
    }

    .inner { position:relative; z-index:2; display:flex; flex-direction:column; height:100%; padding:40px 58px; gap:0; }

    .header { display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
    .logo-pill { background:#fff; border-radius:10px; padding:16px 36px; display:inline-flex; align-items:center; }
    .logo-pill img { height:50px; display:block; }
    .angle-tag {
      font-size:18px; font-weight:800; letter-spacing:4px; text-transform:uppercase;
      color:var(--accent-lt); background:var(--accent-10); border:1px solid var(--accent-30);
      border-radius:6px; padding:14px 30px;
    }
    .h-rule { height:1px; background:linear-gradient(to right,var(--gold) 0%,rgba(212,170,66,0.20) 40%,transparent 100%); margin:18px 0; flex-shrink:0; }

    .header-icons { display:flex; gap:10px; align-items:center; }
    .header-icon-chip {
      display:inline-flex; align-items:center; gap:10px;
      padding:12px 18px; border-radius:8px;
      background:var(--accent-10); border:1px solid var(--accent-30);
    }
    .header-icon-chip svg {
      width:21px; height:21px; flex-shrink:0;
      stroke:var(--accent-lt); fill:none;
      stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round;
    }
    .header-icon-chip span { font-size:13px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:var(--accent-lt); white-space:nowrap; }

    .company-cell {
      flex-shrink:0; overflow:hidden;
      background: linear-gradient(135deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0.018) 100%);
      border:1px solid rgba(255,255,255,0.03);
      border-radius:14px; padding:28px 34px; margin-bottom:12px;
    }
    .industry-label { font-size:36px; font-weight:900; letter-spacing:3px; text-transform:uppercase; color:var(--accent-lt); margin-bottom:12px; text-shadow:0 0 50px var(--accent-30), 0 1px 8px rgba(0,0,0,0.55); }
    .company-header { display:flex; align-items:center; justify-content:space-between; gap:28px; }
    .company-info { display:flex; flex-direction:column; flex:1; min-width:0; }
    .company-name { font-size:76px; font-weight:900; color:var(--white); line-height:.93; letter-spacing:-2px; }
    .company-logo-pill {
      flex-shrink:0; display:flex; align-items:center; justify-content:center;
      background:rgba(255,255,255,0.96); border-radius:12px; padding:18px 32px;
      border:2px solid var(--accent-30);
      min-width:168px; min-height:100px;
    }
    .company-logo-pill img { display:block; max-height:64px; max-width:160px; object-fit:contain; }
    .company-badge-name { font-family:'Manrope',sans-serif; font-size:40px; font-weight:900; color:#0d1f2c; letter-spacing:-1px; line-height:1; text-align:center; }
    .company-badge-sub  { font-family:'Manrope',sans-serif; font-size:13px; font-weight:800; color:var(--accent); letter-spacing:4px; text-transform:uppercase; margin-top:7px; text-align:center; }
    .rank-row { display:flex; align-items:center; gap:18px; margin-top:16px; }
    .rank-badge {
      font-size:36px; font-weight:900; letter-spacing:-1px;
      color:var(--accent-lt);
      text-shadow:0 0 50px var(--accent-30), 0 1px 8px rgba(0,0,0,0.50);
    }
    .rank-top-rated {
      font-size:18px; font-weight:800; letter-spacing:3px; text-transform:uppercase;
      padding:10px 22px; border-radius:8px;
      border:2px solid var(--accent-30); color:var(--accent-lt);
      background:var(--accent-18);
      text-shadow:0 0 24px var(--accent-30);
    }
    .rank-of { font-size:20px; font-weight:600; color:rgba(255,255,255,0.72); align-self:flex-end; padding-bottom:6px; }

    .ecr-compare-zone {
      display:grid; grid-template-columns:1fr 272px; gap:12px;
      flex:0 0 auto; height:260px; margin-bottom:12px;
    }
    .ecr-cell {
      display:flex; flex-direction:column;
      align-items:flex-start; justify-content:center;
      background: linear-gradient(145deg, var(--accent-18) 0%, var(--accent-10) 55%, rgba(255,255,255,0.02) 100%);
      border:1px solid var(--accent-18); border-left:4px solid var(--accent);
      border-radius:14px; padding:26px 38px; gap:6px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 4px 32px rgba(0,0,0,0.30);
    }
    .ecr-label { font-size:16px; font-weight:800; letter-spacing:5px; text-transform:uppercase; color:var(--accent-lt); }
    .ecr-value {
      font-size:116px; font-weight:900; line-height:.9; letter-spacing:-5px; color:var(--accent-lt);
      text-shadow: 0 0 100px var(--accent-30), 0 2px 24px rgba(0,0,0,0.60);
    }
    .ecr-context { font-size:26px; font-weight:600; color:rgba(255,255,255,0.88); }

    .compare-stack { display:flex; flex-direction:column; gap:12px; }
    .cmp-cell {
      flex:1; display:flex; flex-direction:column; justify-content:center; gap:4px;
      padding:16px 22px; border-radius:14px;
      background:rgba(0,0,0,0.50); border:1px solid rgba(255,255,255,0.03); border-top:2px solid rgba(255,255,255,0.03);
    }
    .cmp-cell.gap-cell {
      background: linear-gradient(135deg, var(--accent-18) 0%, var(--accent-10) 100%);
      border:1px solid var(--accent-30); border-top:2px solid var(--accent);
    }
    .cmp-label { font-size:13px; font-weight:800; letter-spacing:3px; text-transform:uppercase; color:rgba(255,255,255,0.72); }
    .cmp-cell.gap-cell .cmp-label { color:var(--accent-lt); }
    .cmp-value { font-size:46px; font-weight:800; line-height:1; letter-spacing:-1.5px; color:var(--white); }
    .cmp-cell.gap-cell .cmp-value {
      color:var(--accent-lt); letter-spacing:-1px;
      text-shadow: 0 0 45px var(--accent-30);
    }
    .cmp-sub { font-size:17px; font-weight:600; color:rgba(255,255,255,0.72); }

    .driver-grid { display:flex; flex-direction:column; gap:10px; flex-shrink:0; }
    .driver-cell {
      display:flex; align-items:center; justify-content:space-between; gap:20px;
      padding:24px 30px; border-radius:14px;
    }
    .driver-cell.str {
      background: linear-gradient(135deg, rgba(10,50,70,0.70) 0%, rgba(6,36,52,0.50) 100%);
      border:1px solid var(--accent-18); border-left:4px solid var(--accent);
    }
    .driver-cell.wk {
      background: linear-gradient(135deg, rgba(130,40,30,0.60) 0%, rgba(100,28,20,0.42) 100%);
      border:1px solid rgba(255,136,112,0.20); border-left:4px solid var(--red);
    }
    .driver-left { display:flex; flex-direction:column; gap:5px; }
    .driver-type { font-size:14px; font-weight:800; letter-spacing:3px; text-transform:uppercase; color:rgba(255,255,255,0.72); }
    .driver-name { font-size:28px; font-weight:700; color:var(--white); line-height:1.1; }
    .driver-pts { font-size:52px; font-weight:800; letter-spacing:-1.5px; line-height:1; flex-shrink:0; }
    .driver-cell.str .driver-pts { color:var(--accent-lt); text-shadow: 0 0 40px var(--accent-30); }
    .driver-cell.wk  .driver-pts { color:var(--red-lt);    text-shadow: 0 0 40px rgba(255,136,112,0.40); }

    .footer { margin-top:16px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.05); display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
    .tagline { font-size:18px; font-weight:700; color:rgba(255,255,255,0.65); }
    .url     { font-size:18px; font-weight:700; color:var(--accent-lt); }
  </style>
</head>
<body>
<div class="slide"><div class="inner">

  <div class="header">
    <div class="logo-pill">
      <img src="REALRATE_LOGO_DATA_URI" alt="RealRate">
    </div>
    <!-- Exactly 3 chips: industry-specific / ECR Ranking (reuse) / Explainable AI (reuse) -->
    <div class="header-icons">
      <div class="header-icon-chip">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><line x1="12" y1="4" x2="12" y2="9.5"/><line x1="12" y1="14.5" x2="12" y2="20"/><line x1="4" y1="12" x2="9.5" y2="12"/><line x1="14.5" y1="12" x2="20" y2="12"/></svg>
        <span>[Industry Chip Label]</span>
      </div>
      <div class="header-icon-chip">
        <svg viewBox="0 0 24 24"><polyline points="3,17 8,11 13,14 20,5"/><polyline points="17,5 20,5 20,8"/></svg>
        <span>ECR Ranking</span>
      </div>
      <div class="header-icon-chip">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/><line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="14.83" y2="9.17"/><line x1="9.17" y1="14.83" x2="4.93" y2="19.07"/></svg>
        <span>Explainable AI</span>
      </div>
    </div>
    <!-- Angle tag: "Top-Rated" / "Not Top-Rated" / "The Surprise" -->
    <span class="angle-tag">[ANGLE TAG]</span>
  </div>

  <div class="h-rule"></div>

  <div class="company-cell">
    <div class="industry-label">[INDUSTRY NAME] &middot; [YEAR]</div>
    <div class="company-header">
      <div class="company-info">
        <div class="company-name">[COMPANY NAME]</div>
        <div class="rank-row">
          <span class="rank-badge">Rank #[N]</span>
          <!-- Include this span ONLY for Top-Rated angles -->
          <span class="rank-top-rated">&#9733;&thinsp;Top-Rated</span>
          <span class="rank-of">of [TOTAL] companies ranked</span>
        </div>
      </div>
      <div class="company-logo-pill">
        <img src="[company-logo-file or data URI]" alt="[COMPANY NAME]"
             onerror="this.outerHTML='<div><div class=company-badge-name>[SHORT NAME]</div><div class=company-badge-sub>[SUFFIX]</div></div>'">
      </div>
    </div>
  </div>

  <div class="ecr-compare-zone">
    <div class="ecr-cell">
      <div class="ecr-label">ECR Score</div>
      <div class="ecr-value">[XXX%]</div>
      <div class="ecr-context">Economic Capital Ratio</div>
    </div>
    <div class="compare-stack">
      <div class="cmp-cell">
        <div class="cmp-label">Industry Average</div>
        <div class="cmp-value">[XX%]</div>
        <div class="cmp-sub">[INDUSTRY NAME] &middot; [YEAR]</div>
      </div>
      <div class="cmp-cell gap-cell">
        <div class="cmp-label">Gap to Average</div>
        <!-- Use &#8593; (up arrow) if above average, &#8595; (down arrow) if below -->
        <div class="cmp-value">&#8593;&thinsp;+[X]pp</div>
        <div class="cmp-sub">above industry average</div>
      </div>
    </div>
  </div>

  <div class="driver-grid">
    <div class="driver-cell str">
      <div class="driver-left">
        <div class="driver-type">Top Strength Driver</div>
        <div class="driver-name">[Driver Name]</div>
      </div>
      <div class="driver-pts">+[X]pp</div>
    </div>
    <div class="driver-cell wk">
      <div class="driver-left">
        <div class="driver-type">Top Weakness Driver</div>
        <div class="driver-name">[Driver Name]</div>
      </div>
      <div class="driver-pts">&#8722;[X]pp</div>
    </div>
  </div>

  <div class="footer">
    <span class="tagline">Powered by RealRate: Using Explainable Financial AI</span>
    <span class="url">realrate.ai/rankings/[industry_slug]/[year]</span>
  </div>

</div></div>
</body>
</html>
```

**Reputable / Not Top-Rated variant** — key differences from the
template above:
1. Delete the `<span class="rank-top-rated">` badge entirely.
2. Change `.gap-cell` to red instead of accent:
   `border:1px solid rgba(232,72,54,0.38); border-top:2px solid var(--red);`
   `.cmp-value` gets `color:var(--red-lt);` with a red-tinted `text-shadow`.
3. Gap arrow becomes `&#8595;` (down) with "below industry average".
4. Mandatory caption line: *"ECR measures balance sheet strength, not
   revenue performance or market reputation."*

### Insight 2 — Industry YoY Shift template (1200×1200 per slide, 3 slides)

```html
<!DOCTYPE html>
<!--
  INSIGHT 2 — Industry YoY Shift  |  Dark Bento Grid  |  1200×1200 px per slide
  Options: Industry-Wide / Company-Level
  Max 3 slides: Slide 1 = The Shift | Slide 2 = What Drove It | Slide 3 = The Context
  FILL IN every [BRACKET]. Replace --accent/--accent-lt with a fresh hex pair.
  Delete Slide 3 entirely if it adds no meaningful information.
  Save each slide as its own file: insight2_slide[1-3]_[industryslug].html
-->
<html lang="en" data-width="1200" data-height="1200" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <title>RealRate — Insight 2 S1 — [INDUSTRY] YoY</title>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
    :root {
      --gold:    #D4AA42; --gold-lt:#F0CC68;
      --accent:  #F97316; --accent-lt:#FDBA74;
      --amber:   #F0A828; --amber-lt:#F8C458;
      --red:     #E84836; --red-lt:#FF8870;
      --green:   #5EC45A; --green-lt:#90D48C;
      --white:   #ffffff;
      --w70: rgba(255,255,255,0.70); --w50:rgba(255,255,255,0.50);
      --w45: rgba(255,255,255,0.45); --w22:rgba(255,255,255,0.05);
      --w14: rgba(255,255,255,0.04); --w08:rgba(255,255,255,0.03);
      --w06: rgba(255,255,255,0.03);
    }
    html,body { width:1200px; height:1200px; overflow:hidden; font-family:'Manrope',sans-serif; }
    body { margin:0; background:#000; }

    .slide {
      width:1200px; height:1200px;
      background:
        radial-gradient(ellipse 700px 500px at 50% 60%, rgba(249,115,22,0.07) 0%, transparent 60%),
        linear-gradient(170deg, #1c1008 0%, #120c05 50%, #0a0800 100%);
      display:flex; flex-direction:column; position:relative; overflow:hidden;
    }
    .slide::before {
      content:''; position:absolute; inset:0;
      background:
        repeating-linear-gradient(0deg, transparent 0, transparent 48px, rgba(255,255,255,0.007) 48px, rgba(255,255,255,0.007) 49px),
        repeating-linear-gradient(90deg, transparent 0, transparent 48px, rgba(255,255,255,0.007) 48px, rgba(255,255,255,0.007) 49px);
      z-index:0; pointer-events:none;
    }
    .slide::after {
      content:''; position:absolute; inset:18px;
      background:
        linear-gradient(to right,  var(--gold) 52px, transparent 52px) top    left  /52px 2px no-repeat,
        linear-gradient(to bottom, var(--gold) 52px, transparent 52px) top    left  /2px 52px no-repeat,
        linear-gradient(to left,   var(--gold) 52px, transparent 52px) top    right /52px 2px no-repeat,
        linear-gradient(to bottom, var(--gold) 52px, transparent 52px) top    right /2px 52px no-repeat,
        linear-gradient(to right,  var(--gold) 52px, transparent 52px) bottom left  /52px 2px no-repeat,
        linear-gradient(to top,    var(--gold) 52px, transparent 52px) bottom left  /2px 52px no-repeat,
        linear-gradient(to left,   var(--gold) 52px, transparent 52px) bottom right /52px 2px no-repeat,
        linear-gradient(to top,    var(--gold) 52px, transparent 52px) bottom right /2px 52px no-repeat;
      z-index:1; pointer-events:none;
    }

    .inner { position:relative; z-index:2; display:flex; flex-direction:column; height:100%; padding:40px 58px; gap:0; }

    .header { display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
    .logo-pill { background:#fff; border-radius:10px; padding:16px 36px; display:inline-flex; align-items:center; }
    .logo-pill img { height:50px; display:block; }
    .slide-tag {
      font-size:18px; font-weight:800; letter-spacing:4px; text-transform:uppercase;
      color:var(--amber-lt); background:rgba(240,168,40,0.12); border:1px solid rgba(240,168,40,0.32);
      border-radius:6px; padding:14px 30px;
    }
    .h-rule { height:1px; background:linear-gradient(to right,var(--gold) 0%,rgba(212,170,66,0.20) 40%,transparent 100%); margin:20px 0; flex-shrink:0; }

    .section-head { flex-shrink:0; margin-bottom:20px; }
    .industry-label { font-size:34px; font-weight:900; letter-spacing:3px; text-transform:uppercase; color:var(--accent-lt); margin-bottom:14px; text-shadow:0 0 50px rgba(253,186,116,0.75), 0 1px 8px rgba(0,0,0,0.55); }
    .section-title { font-size:46px; font-weight:900; color:var(--white); line-height:1.0; letter-spacing:-1px; }
    .section-sub { font-size:22px; font-weight:600; color:rgba(255,255,255,0.88); margin-top:10px; }

    .s-rule { height:1px; background:var(--w08); margin:20px 0; flex-shrink:0; }

    .icon-strip { display:flex; gap:10px; flex-shrink:0; margin-bottom:16px; }
    .icon-chip { display:inline-flex; align-items:center; gap:9px; padding:11px 20px; border-radius:8px; background:rgba(249,115,22,0.08); border:1px solid rgba(249,115,22,0.26); }
    .icon-chip svg { width:20px; height:20px; flex-shrink:0; stroke:var(--accent-lt); fill:none; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
    .icon-chip span { font-size:13px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:rgba(253,186,116,0.85); white-space:nowrap; }

    /* ═══ SLIDE 1 — BENTO YEAR COMPARISON ═══ */
    .year-bento {
      flex:1; display:grid;
      grid-template-columns:1fr 80px 1fr;
      align-items:stretch; gap:0;
      margin-bottom:14px;
    }
    .year-cell {
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      gap:14px; padding:40px 28px; border-radius:14px;
    }
    .year-cell.before {
      background: linear-gradient(145deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.020) 100%);
      border:1px solid rgba(255,255,255,0.03);
      border-top:2px solid rgba(249,115,22,0.12);
    }
    .year-cell.after {
      background: linear-gradient(145deg, rgba(232,72,54,0.16) 0%, rgba(232,72,54,0.06) 55%, rgba(232,72,54,0.02) 100%);
      border:1px solid rgba(232,72,54,0.20);
      border-top:4px solid var(--red);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .year-badge {
      font-size:19px; font-weight:800; letter-spacing:3px; text-transform:uppercase;
      padding:8px 22px; border-radius:30px;
    }
    .before .year-badge { color:var(--w50); background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.03); }
    .after  .year-badge { color:var(--red-lt); background:rgba(232,72,54,0.12); border:1px solid rgba(232,72,54,0.32); }
    .year-ecr-label { font-size:15px; font-weight:800; letter-spacing:4px; text-transform:uppercase; }
    .before .year-ecr-label { color:var(--w50); }
    .after  .year-ecr-label { color:rgba(255,136,112,0.70); }
    .year-value { font-size:88px; font-weight:900; line-height:.9; letter-spacing:-5px; }
    .before .year-value { color:var(--w45); }
    .after  .year-value { color:var(--red-lt); text-shadow: 0 0 80px rgba(232,72,54,0.55), 0 2px 20px rgba(0,0,0,0.50); }
    .year-sub { font-size:25px; font-weight:600; }
    .before .year-sub { color:var(--w45); }
    .after  .year-sub { color:var(--w70); }

    .year-arrow {
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      gap:10px; z-index:2;
    }
    .arrow-icon { font-size:40px; color:var(--amber-lt); text-shadow: 0 0 30px rgba(248,196,88,0.50); }
    .arrow-delta {
      font-size:26px; font-weight:800; color:var(--red-lt); letter-spacing:-0.5px;
      background:rgba(232,72,54,0.16); border:1px solid rgba(232,72,54,0.30);
      border-radius:6px; padding:7px 12px;
      text-shadow: 0 0 24px rgba(255,136,112,0.40);
    }

    .context-cell {
      flex-shrink:0;
      padding:22px 30px; border-radius:14px;
      background: linear-gradient(135deg, rgba(0,0,0,0.40) 0%, rgba(0,0,0,0.25) 100%);
      border:1px solid rgba(255,255,255,0.03); border-left:4px solid var(--amber);
    }
    .ctx-text { font-size:23px; font-weight:600; color:rgba(255,255,255,0.88); line-height:1.5; }
    .ctx-highlight { color:var(--amber-lt); font-weight:800; }

    /* ═══ SLIDE 2 — DRIVER STACK ═══ */
    .driver-stack { flex:1; display:flex; flex-direction:column; gap:12px; }
    .driver-card { display:flex; gap:0; border-radius:14px; overflow:hidden; }
    .driver-card.primary   { flex:1.4; border:1px solid rgba(240,168,40,0.28); box-shadow: 0 4px 24px rgba(0,0,0,0.30); }
    .driver-card.secondary { flex:1;   border:1px solid rgba(249,115,22,0.22); }
    .card-stripe { width:5px; flex-shrink:0; }
    .primary .card-stripe   { background: linear-gradient(to bottom, #F8C458, #E89020); }
    .secondary .card-stripe { background: linear-gradient(to bottom, var(--accent-lt), #c2410c); }
    .card-body { flex:1; padding:32px 36px; display:flex; flex-direction:column; gap:8px; justify-content:center; }
    .primary .card-body   { background: linear-gradient(145deg, rgba(240,168,40,0.14) 0%, rgba(240,168,40,0.06) 60%, rgba(240,168,40,0.02) 100%); }
    .secondary .card-body { background: linear-gradient(145deg, rgba(249,115,22,0.12) 0%, rgba(249,115,22,0.05) 60%, rgba(249,115,22,0.02) 100%); }
    .card-type { font-size:14px; font-weight:800; letter-spacing:3px; text-transform:uppercase; }
    .primary .card-type   { color:rgba(248,196,88,0.92); }
    .secondary .card-type { color:rgba(253,186,116,0.90); }
    .card-title { font-size:30px; font-weight:800; color:var(--white); line-height:1.1; }
    .card-desc { font-size:20px; font-weight:600; color:rgba(255,255,255,0.88); line-height:1.55; margin-top:4px; }
    .card-tag {
      display:inline-block; margin-top:10px;
      font-size:17px; font-weight:700; letter-spacing:0.5px;
      border-radius:5px; padding:6px 16px; width:fit-content;
    }
    .primary .card-tag   { color:var(--amber-lt); background:rgba(240,168,40,0.16); border:1px solid rgba(240,168,40,0.30); }
    .secondary .card-tag { color:var(--accent-lt); background:rgba(249,115,22,0.12); border:1px solid rgba(249,115,22,0.26); }

    .finding-cell {
      flex-shrink:0; margin-top:12px;
      padding:22px 30px; border-radius:14px;
      background: linear-gradient(135deg, rgba(0,0,0,0.40) 0%, rgba(0,0,0,0.25) 100%);
      border:1px solid rgba(255,255,255,0.03); border-left:4px solid var(--accent);
    }
    .finding-label { font-size:13px; font-weight:800; letter-spacing:3px; text-transform:uppercase; color:rgba(253,186,116,0.95); margin-bottom:8px; }
    .finding-text  { font-size:21px; font-weight:600; color:rgba(255,255,255,0.88); line-height:1.55; }

    /* ═══ SLIDE 3 — ASYMMETRIC STAT GRID ═══ */
    .stat-grid { display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; flex-shrink:0; }
    .stat-card { display:flex; flex-direction:column; gap:6px; padding:26px 26px; border-radius:14px; }
    .stat-card.rated {
      grid-column: 1 / -1;
      flex-direction:row; align-items:center; justify-content:space-between;
      padding:30px 44px;
      background: linear-gradient(145deg, rgba(94,196,90,0.22) 0%, rgba(94,196,90,0.10) 55%, rgba(94,196,90,0.04) 100%);
      border:1px solid rgba(94,196,90,0.28); border-top:4px solid var(--green);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 28px rgba(0,0,0,0.25);
    }
    .stat-card.ntr   { background: linear-gradient(145deg, rgba(240,168,40,0.16) 0%, rgba(240,168,40,0.06) 100%); border:1px solid rgba(240,168,40,0.26); border-top:3px solid var(--amber); }
    .stat-card.best  { background: linear-gradient(145deg, rgba(249,115,22,0.14) 0%, rgba(249,115,22,0.06) 100%); border:1px solid rgba(249,115,22,0.22); border-top:3px solid var(--accent); }
    .stat-card.worst { background: linear-gradient(145deg, rgba(255,136,112,0.14) 0%, rgba(255,136,112,0.06) 100%); border:1px solid rgba(255,136,112,0.22); border-top:3px solid var(--red-lt); }

    .sc-label { font-size:14px; font-weight:800; letter-spacing:3px; text-transform:uppercase; }
    .rated  .sc-label { color:rgba(144,212,140,0.95); }
    .ntr    .sc-label { color:rgba(248,196,88,0.92); }
    .best   .sc-label { color:rgba(253,186,116,0.92); }
    .worst  .sc-label { color:rgba(255,136,112,0.92); }

    .sc-value { font-size:68px; font-weight:900; line-height:.9; letter-spacing:-3px; }
    .rated  .sc-value { font-size:108px; letter-spacing:-4px; color:var(--green-lt); text-shadow: 0 0 80px rgba(94,196,90,0.60), 0 2px 20px rgba(0,0,0,0.50); }
    .ntr    .sc-value { color:var(--amber-lt); }
    .best   .sc-value { color:var(--accent-lt); }
    .worst  .sc-value { color:var(--red-lt); }

    .rated-right { display:flex; flex-direction:column; gap:6px; }
    .sc-sub { font-size:24px; font-weight:600; color:rgba(255,255,255,0.75); margin-top:4px; line-height:1.3; }

    .avg-row {
      flex-shrink:0; margin-top:12px;
      display:flex; align-items:center; justify-content:space-between;
      padding:20px 30px; border-radius:14px;
      background: linear-gradient(135deg, rgba(249,115,22,0.12) 0%, rgba(249,115,22,0.05) 100%);
      border:1px solid rgba(249,115,22,0.22);
    }
    .avg-label { font-size:18px; font-weight:800; letter-spacing:3px; text-transform:uppercase; color:rgba(255,255,255,0.75); }
    .avg-value { font-size:46px; font-weight:800; letter-spacing:-1px; color:var(--accent-lt); text-shadow: 0 0 40px rgba(249,115,22,0.45); }

    .implication {
      flex:1; margin-top:12px;
      padding:24px 30px; border-radius:14px;
      background: linear-gradient(135deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.20) 100%);
      border:1px solid rgba(255,255,255,0.03); border-left:4px solid var(--gold-lt);
      display:flex; flex-direction:column; justify-content:center; gap:10px;
    }
    .impl-label { font-size:13px; font-weight:800; letter-spacing:3px; text-transform:uppercase; color:rgba(240,204,104,0.95); }
    .impl-text  { font-size:22px; font-weight:600; color:rgba(255,255,255,0.88); line-height:1.6; }

    .footer { margin-top:14px; padding-top:14px; border-top:1px solid var(--w08); display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
    .tagline { font-size:18px; font-weight:700; color:rgba(255,255,255,0.65); }
    .url     { font-size:18px; font-weight:700; color:var(--accent-lt); }
  </style>
</head>
<body>

<!-- ═══ SLIDE 1 — THE SHIFT — save as insight2_slide1_[industryslug].html ═══ -->
<div class="slide"><div class="inner">

  <div class="header">
    <div class="logo-pill">
      <img src="REALRATE_LOGO_DATA_URI" alt="RealRate">
    </div>
    <span class="slide-tag">Industry Shift &middot; 1&thinsp;/&thinsp;3</span>
  </div>

  <div class="h-rule"></div>

  <div class="section-head">
    <div class="industry-label">[INDUSTRY NAME] &middot; Industry Average</div>
    <!-- Headline = the shift itself, e.g. "The sector average dropped. Not every company followed." -->
    <div class="section-title">[HEADLINE — the shift in one or two punchy lines]</div>
    <div class="section-sub">ECR industry average &middot; [PRIOR YEAR] vs [CURRENT YEAR]</div>
  </div>

  <div class="s-rule"></div>

  <!-- 4 chips: industry-specific / US Equities (reuse) / ECR Ranking (reuse) / Explainable AI (reuse) -->
  <div class="icon-strip">
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><line x1="12" y1="4" x2="12" y2="9.5"/><line x1="12" y1="14.5" x2="12" y2="20"/><line x1="4" y1="12" x2="9.5" y2="12"/><line x1="14.5" y1="12" x2="20" y2="12"/></svg>
      <span>[Industry Chip Label]</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="6" width="4" height="15" rx="1"/><rect x="17" y="9" width="4" height="12" rx="1"/></svg>
      <span>US Equities</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><polyline points="3,17 8,11 13,14 20,5"/><polyline points="17,5 20,5 20,8"/></svg>
      <span>ECR Ranking</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/><line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="14.83" y2="9.17"/><line x1="9.17" y1="14.83" x2="4.93" y2="19.07"/></svg>
      <span>Explainable AI</span>
    </div>
  </div>

  <div class="year-bento">
    <div class="year-cell before">
      <div class="year-badge">[PRIOR YEAR]</div>
      <div class="year-ecr-label">Industry Avg ECR</div>
      <div class="year-value">[XX%]</div>
      <div class="year-sub">Previous ranking</div>
    </div>
    <div class="year-arrow">
      <div class="arrow-icon">&#8594;</div>
      <!-- Use &#43; for an increase, &minus; for a decline -->
      <div class="arrow-delta">[&#43;/&minus;X]pp</div>
    </div>
    <!-- .after uses --red by default (decline styling). Swap rgba(232,72,54,*) → rgba matching --accent for a POSITIVE shift -->
    <div class="year-cell after">
      <div class="year-badge">[CURRENT YEAR]</div>
      <div class="year-ecr-label">Industry Avg ECR</div>
      <div class="year-value">[XX%]</div>
      <div class="year-sub">Current ranking</div>
    </div>
  </div>

  <div class="context-cell">
    <div class="ctx-text">
      A <span class="ctx-highlight">[&#43;/&minus;Xpp shift]</span> in the industry average across
      <span class="ctx-highlight">[N companies]</span> ranked in the [CURRENT YEAR] [INDUSTRY NAME] report.
    </div>
  </div>

  <div class="footer">
    <span class="tagline">Powered by RealRate: Using Explainable Financial AI</span>
    <span class="url">realrate.ai/rankings/[industry_slug]/[year]</span>
  </div>

</div></div>

</body>
</html>
```

**Slide 2 — What Drove It** (save as its own file, same `<head>` styles,
this `<body>` instead):

```html
<body>
<div class="slide"><div class="inner">

  <div class="header">
    <div class="logo-pill">
      <img src="REALRATE_LOGO_DATA_URI" alt="RealRate">
    </div>
    <span class="slide-tag">What Drove It &middot; 2&thinsp;/&thinsp;3</span>
  </div>

  <div class="h-rule"></div>

  <div class="section-head">
    <div class="industry-label">[INDUSTRY NAME] &middot; Industry Average</div>
    <div class="section-title">[One-line structural finding, e.g. "The fall wasn't just exits — it was erosion."]</div>
    <div class="section-sub">Two structural factors reshaped the sector average from [XX%] to [XX%]</div>
  </div>

  <div class="s-rule"></div>

  <div class="icon-strip">
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><line x1="12" y1="4" x2="12" y2="9.5"/><line x1="12" y1="14.5" x2="12" y2="20"/><line x1="4" y1="12" x2="9.5" y2="12"/><line x1="14.5" y1="12" x2="20" y2="12"/></svg>
      <span>[Industry Chip Label]</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="6" width="4" height="15" rx="1"/><rect x="17" y="9" width="4" height="12" rx="1"/></svg>
      <span>US Equities</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><polyline points="3,17 8,11 13,14 20,5"/><polyline points="17,5 20,5 20,8"/></svg>
      <span>ECR Ranking</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/><line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="14.83" y2="9.17"/><line x1="9.17" y1="14.83" x2="4.93" y2="19.07"/></svg>
      <span>Explainable AI</span>
    </div>
  </div>

  <div class="driver-stack">
    <div class="driver-card primary">
      <div class="card-stripe"></div>
      <div class="card-body">
        <div class="card-type">Primary Factor &middot; [Factor Category]</div>
        <div class="card-title">[Driver headline, e.g. "Balance Sheets Weakened, Not Just Exited"]</div>
        <div class="card-desc">[One to two sentences explaining what shifted and why it matters.]</div>
        <span class="card-tag">[Supporting stat, e.g. "43 companies compared · 28 of 43 declined"]</span>
      </div>
    </div>
    <div class="driver-card secondary">
      <div class="card-stripe"></div>
      <div class="card-body">
        <div class="card-type">Secondary Factor &middot; [Factor Category]</div>
        <div class="card-title">[Driver headline]</div>
        <div class="card-desc">[Supporting observation.]</div>
        <span class="card-tag">[Supporting stat]</span>
      </div>
    </div>
  </div>

  <div class="finding-cell">
    <div class="finding-label">Key Finding</div>
    <div class="finding-text">[One clear, specific takeaway. What ECR captured that other metrics missed.]</div>
  </div>

  <div class="footer">
    <span class="tagline">Powered by RealRate: Using Explainable Financial AI</span>
    <span class="url">realrate.ai/rankings/[industry_slug]/[year]</span>
  </div>

</div></div>
</body>
```

**Slide 3 — The Context** (optional — only if it adds meaning; same
`<head>`, this `<body>`):

```html
<body>
<div class="slide"><div class="inner">

  <div class="header">
    <div class="logo-pill">
      <img src="REALRATE_LOGO_DATA_URI" alt="RealRate">
    </div>
    <span class="slide-tag">The Context &middot; 3&thinsp;/&thinsp;3</span>
  </div>

  <div class="h-rule"></div>

  <div class="section-head">
    <div class="industry-label">[INDUSTRY NAME] &middot; [YEAR]</div>
    <div class="section-title">[Why this shift matters beyond the number]</div>
    <div class="section-sub">[One supporting line]</div>
  </div>

  <div class="s-rule"></div>

  <div class="icon-strip">
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><line x1="12" y1="4" x2="12" y2="9.5"/><line x1="12" y1="14.5" x2="12" y2="20"/><line x1="4" y1="12" x2="9.5" y2="12"/><line x1="14.5" y1="12" x2="20" y2="12"/></svg>
      <span>[Industry Chip Label]</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><rect x="3" y="12" width="4" height="9" rx="1"/><rect x="10" y="6" width="4" height="15" rx="1"/><rect x="17" y="9" width="4" height="12" rx="1"/></svg>
      <span>US Equities</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><polyline points="3,17 8,11 13,14 20,5"/><polyline points="17,5 20,5 20,8"/></svg>
      <span>ECR Ranking</span>
    </div>
    <div class="icon-chip">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/><line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="14.83" y2="9.17"/><line x1="9.17" y1="14.83" x2="4.93" y2="19.07"/></svg>
      <span>Explainable AI</span>
    </div>
  </div>

  <div class="stat-grid">
    <div class="stat-card rated">
      <div>
        <div class="sc-label">Top-Rated</div>
        <div class="sc-value">[N]</div>
      </div>
      <div class="rated-right">
        <div class="sc-sub">companies in<br>[INDUSTRY NAME] [YEAR]</div>
      </div>
    </div>
    <div class="stat-card ntr">
      <div class="sc-label">Non-Top-Rated</div>
      <div class="sc-value">[N]</div>
      <div class="sc-sub">of [TOTAL] companies</div>
    </div>
    <div class="stat-card best">
      <div class="sc-label">Best ECR</div>
      <div class="sc-value">[XXX%]</div>
      <div class="sc-sub">[Company] &middot; #1</div>
    </div>
    <div class="stat-card worst">
      <div class="sc-label">Worst ECR</div>
      <div class="sc-value">[X%]</div>
      <div class="sc-sub">Rank #[TOTAL]</div>
    </div>
  </div>

  <div class="avg-row">
    <span class="avg-label">Industry Average ECR</span>
    <span class="avg-value">[XX%] &middot; [N] Companies</span>
  </div>

  <div class="implication">
    <div class="impl-label">Implication</div>
    <div class="impl-text">[What an investor, analyst, or partner should take from this. One to two sentences.]</div>
  </div>

  <div class="footer">
    <span class="tagline">Powered by RealRate: Using Explainable Financial AI</span>
    <span class="url">realrate.ai/rankings/[industry_slug]/[year]</span>
  </div>

</div></div>
</body>
```

### Insight 3 — Rotating Angle template (1080×1350)

```html
<!DOCTYPE html>
<!--
  INSIGHT 3 — Rotating Angle  |  1080×1350 px (LinkedIn portrait)
  Angles: Industry Blind Spot / Market vs Balance Sheet / Methodology Moment /
          Investor Signal / Macro Lens
  FILL IN every [BRACKET]. Must not have been used in the prior 2 ranking cycles.
-->
<html lang="en" data-width="1080" data-height="1350" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <title>RealRate — Insight 3 — [ANGLE] — [INDUSTRY]</title>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --blue-dark:   #00679B;
      --blue-light:  #3DBACD;
      --bg:          #F5F5F5;
      --white:       #ffffff;
      --black:       #000000;
      --text-mid:    #4A4A4A;
      --text-soft:   #6A6A6A;
      --green:       #419453;
      --green-light: #86CC82;
      --red:         #C04A3A;
      --red-light:   #F08F82;
      --card-shadow: 0 2px 20px rgba(0,0,0,0.08);
    }

    html, body {
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      font-family: 'Manrope', sans-serif;
      background: var(--bg);
    }

    .slide {
      width: 1080px;
      height: 1350px;
      background: var(--bg);
      display: flex;
      flex-direction: column;
    }

    .accent-bar {
      height: 7px;
      background: linear-gradient(90deg, var(--blue-dark) 0%, var(--blue-light) 100%);
      flex-shrink: 0;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 36px 56px 30px;
      flex-shrink: 0;
      background: var(--white);
      border-bottom: 1px solid rgba(0,0,0,0.07);
    }
    .logo-wrap img { height: 30px; display: block; }
    .angle-tag {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--white);
      background: var(--blue-dark);
      border-radius: 4px;
      padding: 10px 22px;
    }

    .body {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 52px 56px 0;
    }

    .industry-label {
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--blue-light);
      margin-bottom: 20px;
      flex-shrink: 0;
    }

    .headline {
      font-size: 66px;
      font-weight: 800;
      color: var(--black);
      line-height: 1.04;
      letter-spacing: -1.5px;
      margin-bottom: 44px;
      flex-shrink: 0;
    }

    .panel-row {
      display: flex;
      gap: 16px;
      margin-bottom: 24px;
      flex: 1;
    }
    .card {
      background: var(--white);
      border-radius: 14px;
      padding: 30px 32px;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      gap: 8px;
      justify-content: center;
    }
    .card-full { flex: 1; }
    .card-label {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--text-soft);
    }
    .card-value {
      font-size: 68px;
      font-weight: 900;
      color: var(--blue-dark);
      line-height: 1;
      letter-spacing: -1.5px;
    }
    .card-sub {
      font-size: 17px;
      font-weight: 600;
      color: var(--text-soft);
      line-height: 1.4;
    }
    .card-dark {
      background: var(--blue-dark);
    }
    .card-dark .card-label { color: rgba(255,255,255,0.48); }
    .card-dark .card-value { color: var(--white); }
    .card-dark .card-sub   { color: rgba(255,255,255,0.55); }

    .driver-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex-shrink: 0;
      margin-bottom: 24px;
    }
    .dl-item {
      background: var(--white);
      border-radius: 12px;
      padding: 22px 30px;
      box-shadow: var(--card-shadow);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }
    .dl-item-left { display: flex; flex-direction: column; gap: 4px; }
    .dl-type { font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: var(--text-soft); }
    .dl-name { font-size: 24px; font-weight: 700; color: var(--black); }
    .dl-desc { font-size: 15px; font-weight: 500; color: var(--text-soft); }
    .dl-pts  { font-size: 44px; font-weight: 800; line-height: 1; flex-shrink: 0; }

    .change-positive { color: var(--green);  font-weight: 800; }
    .change-negative { color: var(--red);    font-weight: 800; }

    .insight-card {
      background: var(--white);
      border-radius: 14px;
      padding: 34px 38px;
      box-shadow: var(--card-shadow);
      border-left: 6px solid var(--blue-light);
      flex-shrink: 0;
      margin-bottom: 28px;
    }
    .insight-label {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--blue-dark);
      margin-bottom: 14px;
    }
    .insight-text {
      font-size: 29px;
      font-weight: 600;
      color: var(--text-mid);
      line-height: 1.5;
    }

    .footer {
      margin-top: auto;
      flex-shrink: 0;
      padding: 28px 56px;
      background: var(--white);
      border-top: 1px solid rgba(0,0,0,0.08);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .tagline { font-size: 16px; font-weight: 700; color: var(--text-soft); }
    .url     { font-size: 16px; font-weight: 700; color: var(--blue-dark); }
  </style>
</head>
<body>
<div class="slide">

  <div class="accent-bar"></div>

  <div class="header">
    <div class="logo-wrap">
      <img src="REALRATE_LOGO_DATA_URI" alt="RealRate">
    </div>
    <!--
      ANGLE TAG — choose one:
      "THE INDUSTRY BLIND SPOT" / "MARKET VS BALANCE SHEET" /
      "THE METHODOLOGY MOMENT" / "THE INVESTOR SIGNAL" / "THE MACRO LENS"
    -->
    <span class="angle-tag">[ANGLE TAG]</span>
  </div>

  <div class="body">

    <div class="industry-label">[INDUSTRY NAME] · [YEAR]</div>

    <!--
      Headline = the story the angle tells. Examples by angle:
        Blind Spot:          "One weakness driver appears in 7 of 10 companies."
        Market vs B/S:       "Highly rated by the market. Ranked 38th by ECR."
        Methodology Moment:  "Revenue is a performance signal. ECR is a stability signal."
        Investor Signal:     "Is this sector financially healthy? ECR gives a clear answer."
        Macro Lens:          "Rising rates met structural debt. ECR captured it first."
    -->
    <div class="headline">[HEADLINE — angle-specific story hook]</div>

    <!-- OPTION A: Two stat cards (Blind Spot, Investor Signal, Macro Lens) -->
    <div class="panel-row">
      <div class="card card-full">
        <div class="card-label">[STAT LABEL A]</div>
        <div class="card-value">[VALUE]</div>
        <div class="card-sub">[Brief context]</div>
      </div>
      <div class="card card-full card-dark">
        <div class="card-label">[STAT LABEL B]</div>
        <div class="card-value change-negative">[VALUE]</div>
        <div class="card-sub">[Brief context]</div>
      </div>
    </div>

    <!-- OPTION B: Driver list — use instead of OPTION A for the Blind Spot angle
    <div class="driver-list">
      <div class="dl-item">
        <div class="dl-item-left">
          <div class="dl-type">Weakness Driver · Most Common</div>
          <div class="dl-name">[Driver Name]</div>
          <div class="dl-desc">[Appears in X of Y companies]</div>
        </div>
        <div class="dl-pts change-negative">[−Xpp]</div>
      </div>
      <div class="dl-item">
        <div class="dl-item-left">
          <div class="dl-type">Weakness Driver · 2nd Most Common</div>
          <div class="dl-name">[Driver Name]</div>
          <div class="dl-desc">[Appears in X of Y companies]</div>
        </div>
        <div class="dl-pts change-negative">[−Xpp]</div>
      </div>
    </div>
    -->

    <div class="insight-card">
      <div class="insight-label">[INSIGHT LABEL — e.g. "What ECR Found" / "The Signal"]</div>
      <div class="insight-text">[One or two sentences. Specific, data-backed, no vague claims.]</div>
    </div>

  </div>

  <div class="footer">
    <span class="tagline">Powered by RealRate: Using Explainable Financial AI</span>
    <span class="url">realrate.ai/rankings/[industry_slug]/[year]</span>
  </div>

</div>
</body>
</html>
```

### Insight 4 — Non-Top-Rated Rotating template (1080×1350)

```html
<!DOCTYPE html>
<!--
  INSIGHT 4 — Non-Top-Rated (NTR) Rotating  |  1080×1350 px (LinkedIn portrait)
  Angles: Almost There / The One Thing / The Fallen / The Sector Drag /
          Close But Not Rated / The Due Diligence Gap
  FILL IN every [BRACKET]. MANDATORY DISCLAIMER already in footer — do not remove.
-->
<html lang="en" data-width="1080" data-height="1350" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <title>RealRate — Insight 4 — [ANGLE] — [COMPANY]</title>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --blue-dark:   #00679B;
      --blue-light:  #3DBACD;
      --bg:          #F5F5F5;
      --white:       #ffffff;
      --black:       #000000;
      --text-mid:    #4A4A4A;
      --text-soft:   #6A6A6A;
      --green:       #419453;
      --green-light: #86CC82;
      --red:         #C04A3A;
      --red-light:   #F08F82;
      --card-shadow: 0 2px 20px rgba(0,0,0,0.08);
    }

    html, body {
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      font-family: 'Manrope', sans-serif;
      background: var(--bg);
    }

    .slide {
      width: 1080px;
      height: 1350px;
      background: var(--bg);
      display: flex;
      flex-direction: column;
    }

    .accent-bar {
      height: 7px;
      background: linear-gradient(90deg, var(--red) 0%, var(--red-light) 100%);
      flex-shrink: 0;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 36px 56px 30px;
      flex-shrink: 0;
      background: var(--white);
      border-bottom: 1px solid rgba(0,0,0,0.07);
    }
    .logo-wrap img { height: 30px; display: block; }

    .angle-tag {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--white);
      background: var(--red);
      border-radius: 4px;
      padding: 10px 22px;
    }

    .body {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 44px 56px 28px;
    }

    .industry-label {
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--blue-light);
      margin-bottom: 20px;
    }

    .company-name {
      font-size: 84px;
      font-weight: 900;
      color: var(--black);
      line-height: 1.0;
      letter-spacing: -2px;
      margin-bottom: 20px;
    }

    .top-section { display: flex; flex-direction: column; margin-bottom: 44px; }

    .rank-row {
      display: flex;
      align-items: center;
      gap: 18px;
      margin-bottom: 44px;
      flex-shrink: 0;
    }
    .ntr-badge {
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(192,74,58,0.1);
      border: 1.5px solid rgba(192,74,58,0.35);
      border-radius: 5px;
      padding: 10px 22px;
    }
    .ntr-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--red);
      flex-shrink: 0;
    }
    .ntr-text {
      font-size: 17px;
      font-weight: 800;
      color: var(--red);
      letter-spacing: 0.5px;
    }
    .rank-context {
      font-size: 23px;
      font-weight: 600;
      color: var(--text-soft);
    }

    .ecr-section {
      display: flex;
      gap: 16px;
      flex: 1;
      margin-bottom: 20px;
    }

    .ecr-card {
      flex: 1;
      background: var(--blue-dark);
      border-radius: 14px;
      padding: 36px 40px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 10px;
    }
    .ecr-card-label {
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: rgba(255,255,255,0.55);
    }
    .ecr-value {
      font-size: 110px;
      font-weight: 900;
      line-height: 1;
      letter-spacing: -4px;
      color: var(--red-light);
    }
    .ecr-card-sub {
      font-size: 20px;
      font-weight: 600;
      color: rgba(255,255,255,0.55);
    }

    .threshold-card {
      width: 220px;
      flex-shrink: 0;
      background: var(--white);
      border-radius: 14px;
      padding: 36px 28px;
      align-self: stretch;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 10px;
      box-shadow: var(--card-shadow);
      border-top: 5px solid var(--green);
    }
    .threshold-label {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--text-soft);
    }
    .threshold-value {
      font-size: 56px;
      font-weight: 900;
      color: var(--green);
      line-height: 1;
      letter-spacing: -1px;
    }
    .threshold-desc {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-soft);
      line-height: 1.4;
    }

    .gap-pill {
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--white);
      border-radius: 8px;
      border-left: 5px solid var(--red);
      padding: 16px 24px;
      margin-bottom: 20px;
      flex-shrink: 0;
      box-shadow: var(--card-shadow);
    }
    .gap-text {
      font-size: 22px;
      font-weight: 700;
      color: var(--text-mid);
    }
    .change-negative { color: var(--red); font-weight: 800; }
    .change-positive { color: var(--green); font-weight: 800; }

    .driver-card {
      flex-shrink: 0;
      background: var(--white);
      border-radius: 14px;
      padding: 32px 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      box-shadow: var(--card-shadow);
      border-top: 5px solid var(--red);
    }
    .driver-left { display: flex; flex-direction: column; gap: 8px; }
    .driver-type {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--text-soft);
    }
    .driver-name {
      font-size: 32px;
      font-weight: 800;
      color: var(--black);
      line-height: 1.2;
    }
    .driver-desc {
      font-size: 17px;
      font-weight: 500;
      color: var(--text-soft);
      line-height: 1.4;
    }
    .driver-pts {
      font-size: 58px;
      font-weight: 900;
      line-height: 1;
      letter-spacing: -1px;
      flex-shrink: 0;
    }

    .footer {
      margin-top: auto;
      flex-shrink: 0;
      padding: 22px 56px 26px;
      background: var(--white);
      border-top: 1px solid rgba(0,0,0,0.08);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .disclaimer {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-soft);
      font-style: italic;
    }
    .footer-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .tagline { font-size: 15px; font-weight: 700; color: var(--text-soft); }
    .url     { font-size: 15px; font-weight: 700; color: var(--blue-dark); }
  </style>
</head>
<body>
<div class="slide">

  <div class="accent-bar"></div>

  <div class="header">
    <div class="logo-wrap">
      <img src="REALRATE_LOGO_DATA_URI" alt="RealRate">
    </div>
    <!--
      ANGLE TAG — choose one:
      "ALMOST THERE" / "THE ONE THING" / "THE FALLEN" /
      "THE SECTOR DRAG" / "CLOSE BUT NOT RATED" / "THE DUE DILIGENCE GAP"
    -->
    <span class="angle-tag">[ANGLE TAG]</span>
  </div>

  <div class="body">

    <div class="top-section">
    <div class="industry-label">[INDUSTRY NAME] · [YEAR]</div>

    <div class="company-name">[COMPANY NAME]</div>

    <div class="rank-row">
      <div class="ntr-badge">
        <div class="ntr-dot"></div>
        <span class="ntr-text">Non-Top-Rated</span>
      </div>
      <!--
        Adapt context to angle:
        "Almost There":    "Rank #N of N — [Xpp] from the Top-Rated threshold."
        "The Fallen":      "Top-Rated in [PRIOR YEAR]. Rank #N in [YEAR]."
        "Sector Drag":     "[N] companies in [sub-sector] below the Top-Rated threshold."
      -->
      <span class="rank-context">[RANK CONTEXT LINE]</span>
    </div>

    </div><!-- end .top-section -->

    <div class="ecr-section">
      <div class="ecr-card">
        <div class="ecr-card-label">ECR Score</div>
        <div class="ecr-value">[XX.X%]</div>
        <div class="ecr-card-sub">Economic Capital Ratio</div>
      </div>
      <div class="threshold-card">
        <div class="threshold-label">Top-Rated Threshold</div>
        <div class="threshold-value">[≥XX%]</div>
        <div class="threshold-desc">Minimum ECR for<br>Top-Rated status</div>
      </div>
    </div>

    <div class="gap-pill">
      <span class="gap-text"><span class="change-negative">[Xpp]</span> below the Top-Rated threshold</span>
    </div>

    <div class="driver-card">
      <div class="driver-left">
        <div class="driver-type">Key Weakness Driver</div>
        <div class="driver-name">[Driver Name]</div>
        <div class="driver-desc">[One sentence — what this driver measures and why it pulls ECR below threshold.]</div>
      </div>
      <div class="driver-pts change-negative">[−Xpp]</div>
    </div>

  </div>

  <!-- FOOTER — mandatory disclaimer, do not remove -->
  <div class="footer">
    <div class="disclaimer">ECR measures balance sheet strength, not revenue performance or market reputation.</div>
    <div class="footer-row">
      <span class="tagline">Powered by RealRate: Using Explainable Financial AI</span>
      <span class="url">realrate.ai/rankings/[industry_slug]/[year]</span>
    </div>
  </div>

</div>
</body>
</html>
```

---

## Generator source — PNG/PDF exporter (Python / Playwright)

Copy this verbatim into a new file named `export_insight.py`, placed
alongside the HTML file(s) to export. Do not retype or "improve" it
from memory.

First-run dependency:
```
pip install playwright Pillow
python -m playwright install chromium
```

```python
"""
export_insight.py — RealRate Insight Post PNG/PDF exporter (Python / Playwright)
Usage:
  python export_insight.py                              # exports all insight*.html in this folder (recursive)
  python export_insight.py insight1_companyslug.html     # exports one specific file
  python export_insight.py file1.html file2.html ...     # exports several specific files

Requires: pip install playwright Pillow && python -m playwright install chromium
Pillow is only needed for the auto Insight-2 carousel PDF merge.
"""

import sys
from collections import defaultdict
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent.resolve()


def export_file(page, html_path: Path):
    html = html_path.read_text(encoding="utf-8")
    page.set_content(html, wait_until="networkidle")

    w = page.evaluate("parseInt(document.documentElement.dataset.width  || '1200')")
    h = page.evaluate("parseInt(document.documentElement.dataset.height || '1200')")
    page.set_viewport_size({"width": w, "height": h})

    try:
        page.wait_for_function("document.fonts.ready", timeout=4000)
    except Exception:
        pass

    out_path = html_path.with_suffix(".png")
    page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": w, "height": h})
    kb = out_path.stat().st_size // 1024
    print(f"  OK  {out_path.name}  ({w}x{h}px)  {kb} KB")


def create_insight2_pdfs(files):
    """Combine insight2 slide PNGs into a single PDF per folder."""
    try:
        from PIL import Image
    except ImportError:
        print("  Note: install Pillow to enable PDF export  (pip install Pillow)")
        return

    groups = defaultdict(list)
    for f in files:
        if "insight2_slide" in f.name:
            groups[f.parent].append(f.with_suffix(".png"))

    for folder, pngs in groups.items():
        pngs = sorted(p for p in pngs if p.exists())
        if len(pngs) < 2:
            continue

        pdf_path = folder / f"{folder.name}-slides.pdf"
        imgs = [Image.open(str(p)).convert("RGB") for p in pngs]
        imgs[0].save(
            str(pdf_path),
            format="PDF",
            save_all=True,
            append_images=imgs[1:],
        )
        kb = pdf_path.stat().st_size // 1024
        print(f"  PDF  {pdf_path.name}  ({len(imgs)} slides, {kb} KB)")


def main():
    args = sys.argv[1:]

    if args:
        files = [SCRIPT_DIR / a for a in args]
    else:
        files = sorted(
            f for f in SCRIPT_DIR.glob("**/insight*.html")
            if not f.name.endswith("-template.html")
        )

    if not files:
        print("No insight HTML files found.")
        return

    print(f"Exporting {len(files)} file(s) at 1x resolution...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(device_scale_factor=1)
        page = context.new_page()
        for f in files:
            export_file(page, f)
        browser.close()

    create_insight2_pdfs(files)
    print("Done.")


if __name__ == "__main__":
    main()
```

Note: because every template above already embeds the RealRate logo as
a base64 data URI (rather than a relative file path), this exporter
does not need the path-substitution step that some other copies of
this exporter perform — the HTML is already fully self-contained
before it ever reaches Playwright.
