# Post Templates — RealRate Visual Design Context

This file is a reference for all approved post template specifications. Load it when generating any HTML visual post. For step-by-step production procedures, see `SOP/post-design-sop.md`.

---

## Canvas

- **Size:** 1200×1200px (all social posts)
- **Margin:** 50px all sides — content and logo stay within this boundary
- **Export:** Puppeteer via `export.mjs` at deviceScaleFactor 2 → PNG

## Approved Dark Backgrounds

| Hex | Name | Notes |
|---|---|---|
| `#003b57` | Deep Navy | Primary — most posts |
| `#004a6e` | Navy Blue | Alternate |
| `#005884` | Dark Blue | Alternate |
| `#3389b1` | Medium Blue | Lighter dark BG |
| `#34a2b3` | Blue Teal | Lighter dark BG |
| `#2c8b9a` | Dark Teal | Alternate |
| `#0a1628` | Dark Navy (legacy) | Still approved |
| `#00679B` | Brand Blue (legacy) | Still approved |

## Approved Light Backgrounds

| Hex | Name | Notes |
|---|---|---|
| `#f5f5f5` | Light Grey | Data viz posts, light slides |
| `#e8e8e8` | Off-White | Light section variant |
| `#ffffff` | White | Data viz only |

## Accent Color Rule

Accent assignment is based on background type — never mix:

| Background | Accent colors |
|---|---|
| **Dark** (any dark BG above) | `#f5f5f5` · `#e8e8e8` |
| **Light** (any light BG above) | `#3DBACD` · `#00679B` |

One accent per design. Never use both `#3DBACD` and `#00679B` as text/UI accents in the same post.

## Layout Patterns — Approved 2026

Visual references in `Design References/Social Media/`.

| ID | Pattern | Description |
|---|---|---|
| L1 | Circle Photo — Bottom Left | Dark BG; large circular B&W photo bottom-left; title large right; subtitle + body stacked right |
| L2 | Vertical Split | Colored left panel (~55%) text; B&W photo right panel (~45%) |
| L3 | Geometric Teal | Teal main area; dark angular geometric shapes one corner; text on teal |
| L4 | Circle Photo — Corner | Dark BG; circular masked photo top-right; large bold title bottom-left |
| L5 | Ring Photo | Dark BG; large ring/donut with photo inside right; text left |

## Data Visualization Layout

- **Background:** `#f5f5f5` or `#ffffff` only
- **Text:** Dark navy (`#003b57`)
- **Primary series (US):** `#00679B` bars
- **Secondary series (EU):** `#3DBACD` bars
- **Style:** Horizontal bars, no gridlines, percentage labels right of bar

---

## Template: Biggest Mover Insight Post ✅ Approved 2026-04-23

### Identity
- **Post type label:** `[YEAR] RANKING INSIGHT`
- **Title:** `BIGGEST MOVER`
- **Subtitle:** `The company that gained the most ECR points year on year.`

### Fixed Layout (top → bottom)
1. Top bar: logo (white SVG, no box) · industry tag (white)
2. Post label (accent color, 17px)
3. Title — ALL CAPS, 118px, weight 800
4. One-liner subtitle — 19px, muted white
5. `flex: 1` spacer
6. Rank row — old rank (muted) · ↑ · new rank (white, large)
7. Company header — logo in white 64px rounded box + company name 54px white bold
8. Description — 23px muted, max-width 540px
9. Stats bar — ECR Score (accent) | Key Driver (white + accent gain) | Industry Avg. (white)
10. Tagline — 16px, very muted

### Typography
| Element | Size | Weight | Color |
|---|---|---|---|
| Industry tag | 16px | 700 | `#ffffff` |
| Post label | 17px | 700 | Accent |
| Title | 118px | 800 | `#ffffff` |
| Subtitle | 19px | 400 | `rgba(255,255,255,0.5)` |
| Old rank | 38px | 800 | `rgba(255,255,255,0.28)` |
| New rank | 76px | 800 | `#ffffff` |
| Company name | 54px | 800 | `#ffffff` |
| Description | 23px | 400 | `rgba(255,255,255,0.6)` |
| Stat label | 13px | 700 | `rgba(255,255,255,0.38)` |
| ECR score | 48px | 800 | Accent |
| Key driver name | 38px | 700 | `#ffffff` |
| Key driver gain | 34px | 600 | Accent |
| Industry avg. | 44px | 800 | `#ffffff` |
| Tagline | 16px | 400 | `rgba(255,255,255,0.28)` |

### Decoration Options (pick one)
**Arc (default):**
```css
.deco-arc {
  position: absolute;
  width: 680px; height: 680px;
  border-radius: 50%;
  border: 110px solid #3DBACD; /* or current accent */
  bottom: -210px; right: -210px;
  opacity: 0.55;
}
```

**Geometric squares (alternate):**
3–4 solid accent-color squares, sizes 40–90px, opacity 0.12–0.28, clustered at corner.

### Data Fields Required
| Field | Example |
|---|---|
| Industry + Year | `US Computers · 2026` |
| Company name | `Apple Inc` |
| Prior year rank | `#2` |
| Current year rank | `#1` |
| ECR prior year | `394%` |
| ECR current year | `430%` |
| Key driver name | `Net Income` |
| Key driver contribution | `+245pp` |
| Industry average ECR | `258%` |

### Reference File
`posts/us_computers_2026/insight1_apple.html` — canonical approved example

---

## Template: The Surprise Insight Post
*(Definition approved — visual design pending first approved production)*

### Identity
- **Post type label:** `[YEAR] RANKING INSIGHT`
- **Title by variant:**
  - Variant A (Confirmation): `THE CONFIRMATION` or `WHAT THE DATA REVEALS`
  - Variant B (Reputation Doesn't Rate): `REPUTATION DOESN'T RATE`
  - Variant C (Unknown Leader): `THE UNKNOWN LEADER`

### Angle Selection — Pick Based on What the Data Shows

One post. The title and story direction depend on what the data supports.

| Angle | When to use | Title |
|---|---|---|
| **The Confirmation** | Well-known brand ranked high as expected — the structural WHY is non-obvious | `THE CONFIRMATION` or `WHAT THE DATA REVEALS` |
| **Reputation Doesn't Rate** | Well-known brand ranked significantly lower than their public profile suggests | `REPUTATION DOESN'T RATE` |
| **The Unknown Leader** | Obscure company ranked ahead of recognized industry giants | `THE UNKNOWN LEADER` |

### Priority Rule
- Reputation Doesn't Rate and The Unknown Leader: eligible for Insight 1 (Day +2)
- The Confirmation: eligible for Insight 2 (Day +5)
- See `ranking-publication-protocol.md → Day +2 Decision Rule` for full logic

### Layout Options
- **Option 1 — Single company:** follows Biggest Mover structure adapted for the angle (all angles)
- **Option 2 — Two-company comparison:** side-by-side ECR contrast (The Unknown Leader preferred, Reputation Doesn't Rate optional)
- **Option 3 — Causal graph:** replaces or supplements stats bar — shows driver → ECR causation. Can use existing graph design or a redesigned version. Approved for all angles.

### Data Fields Required

| Field | Angles |
|---|---|
| Company name (exact) | All |
| Current rank | All |
| ECR score (%) | All |
| Industry average ECR (%) | All |
| Greatest strength driver + contribution (pp) | The Confirmation, The Unknown Leader |
| Greatest weakness driver + contribution (pp) | Reputation Doesn't Rate |
| Comparison company: name, rank, ECR (%) | The Unknown Leader |

### Caption Rule — Reputation Doesn't Rate Only
Must include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### Reference File
*(None yet — pending first approved production)*

---

## Template: Not Top-Rated (NTR) — Gap Analysis
*(Pending approval — do not use until approved)*

---

## Template: Industry Driver Pattern Carousel (4 slides)
*(Pending approval — do not use until approved)*
