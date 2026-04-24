# Post Design SOP — RealRate LinkedIn Visual Posts

## Purpose
This SOP governs the creation of HTML-based visual posts for RealRate's LinkedIn channel. It defines the production workflow, file conventions, and quality checks for each approved post type.

---

## General Production Rules (All Post Types)

### Canvas
- **Size:** 1080×1080px square
- **Font:** Manrope (Google Fonts) — weights 300, 400, 500, 600, 700, 800
- **Export:** Puppeteer via `export.mjs` at deviceScaleFactor 2 → PNG

### Color System
| Token | Hex | Use |
|---|---|---|
| Dark Navy | `#0a1628` | Approved background |
| Dark Blue | `#00679B` | Approved background + decoration |
| Light Teal | `#3DBACD` | Accent — labels, highlights, key numbers |
| White | `#ffffff` | Primary text, logos, key values |
| Mid Grey | `rgba(255,255,255,0.5–0.6)` | Descriptions, secondary text |
| Muted Grey | `rgba(255,255,255,0.28–0.38)` | Labels, taglines, dimmed values |
| Mid Grey | `#8e96a2` | Approved background — insight posts, lighter positive tone |
| Light BG | `#f5f5f5` / `#e8e8e8` | Split-band light section |

**Approved split-band combinations** (top accent + light bottom, divided by `#3DBACD` 3px rule):
- `#00679B` + `#f5f5f5` — default (carousel, NTR posts)
- `#8e96a2` + `#f5f5f5` — insight posts, lighter neutral tone

### Single-Accent Rule
Each design uses **one accent color** for text/UI elements — either `#3DBACD` or `#00679B`. Rotate between posts. Never use both as text highlights in the same design.

### What Never Appears
- Red or green — except when explicitly indicating a real financial loss (red) or gain (green), and only in the ECR/metric data itself
- Background data number textures
- Hashtags anywhere on images
- Tagline `"Powered by RealRate: Using Explainable Financial AI"` in captions — image only
- External company logo URLs — always inline SVG or letter initials

### Typography Scale
| Element | Size | Weight |
|---|---|---|
| Post title (short) | 90–120px | 800 |
| Post title (long) | 75–90px | 800 |
| Post label / tagline | 16–19px | 600–700 |
| Section headers | 28–44px | 700–800 |
| Body / description | 19–24px | 400–500 |
| Stat labels | 11–13px | 700, uppercase, letter-spaced |

---

## Post Type: Biggest Mover Insight

### When to Use
One post per ranking publication. Published as a standalone insight — the company with the highest ECR point gain year on year.

### Data to Verify Before Starting
From https://www.realrate-archive.com (internal only):
- [ ] Company name (exact)
- [ ] Prior year rank
- [ ] Current year rank
- [ ] ECR prior year (%)
- [ ] ECR current year (%)
- [ ] ECR point gain (current minus prior)
- [ ] Greatest strength driver name + contribution (pp)
- [ ] Industry average ECR (%)
- [ ] Ranking context: `[Industry] · [Year]`

### Layout Specification (Fixed Order)

```
┌─────────────────────────────────────────┐
│ [Logo]              [Industry Tag]       │  ← top bar
│                                         │
│ [POST LABEL]                            │  ← 80px below top bar
│ [TITLE — ALL CAPS, ~118px]              │
│ [one-liner subtitle — 19px, muted]      │
│                                         │
│          [spacer — flex:1]              │
│                                         │
│ [#old ↑ #new]                           │  ← rank row
│ [🍎 Company Name]                       │  ← logo box + name
│ [Description — 23px, muted]             │
│                                         │
│ ECR SCORE | KEY DRIVER | INDUSTRY AVG.  │  ← stats bar
│ [430%]    | [Net Income +245pp] | [258%]│
│                                         │
│ Powered by RealRate: Using Explainable… │  ← tagline
└─────────────────────────────────────────┘
       [arc decoration — bottom right]
```

### Section-by-Section Rules

**Top Bar**
- Logo: RealRate white SVG, no border box, height 38px
- Industry tag: white, 16px, 700 weight, uppercase, letter-spaced 2.5px

**Post Label**
- Text: `[YEAR] Ranking Insight`
- Color: accent color (`#3DBACD`)
- Size: 17px, 700 weight, uppercase, letter-spaced 3px
- Margin-top: 80px from top bar

**Title**
- Text: `BIGGEST MOVER` (always all caps)
- Size: ~118px, 800 weight, line-height 0.9, letter-spacing -3px
- Margin-top: 14px from label

**One-Liner Subtitle**
- Text: `The company that gained the most ECR points year on year.`
- Size: 19px, 400 weight, color `rgba(255,255,255,0.5)`
- Margin-top: 18px from title, max-width ~520px

**Spacer**
- `flex: 1` — this creates the breathing room; never fill it with content

**Rank Row**
- Old rank: `rgba(255,255,255,0.28)`, 38px, 800 weight
- Arrow ↑: same muted color
- New rank: white, 76px, 800 weight
- Display inline, aligned to baseline

**Company Header**
- Logo box: 64×64px white rounded box (`border-radius: 14px`), inline SVG inside
  - If no SVG available: use 2-letter initials, `#00679B` text on white bg, 26px bold
- Company name: white, 54px, 800 weight — placed to the right of logo box, gap 18px
- Margin-bottom: 18px

**Description**
- Format: `ECR climbed from [X]% to [Y]% — overtaking last year's leader. One driver explains the move.`
- Size: 23px, 400 weight, `rgba(255,255,255,0.6)`, line-height 1.5, max-width 540px
- Adapt wording if company was already #1 prior year (e.g. "extending its lead")

**Stats Bar**
- Three columns, separated by `1px solid rgba(255,255,255,0.14)`, padding/margin 44px each
- Column 1 — ECR Score: label 13px muted · value accent color, 48px, 800 weight
- Column 2 — Key Driver: label 13px muted · driver name white 38px bold + gain accent color 34px
- Column 3 — Industry Avg.: label 13px muted · value **white** 44px, 800 weight
- Margin-bottom: 28px

**Tagline**
- Text: `Powered by RealRate: Using Explainable Financial AI`
- Size: 16px, 400 weight, `rgba(255,255,255,0.28)`

### Decoration (Creative Variation Allowed)

**Primary option — Arc (default):**
- Large partial ring, bottom-right, clipped by overflow:hidden
- Size: ~680×680px, border ~110px, positioned ~-210px from bottom and right
- Color: accent color at 55% opacity
- Never combine with geometric squares

**Alternate option — Geometric Squares (Reference #7 style):**
- 3–4 solid `#3DBACD` squares at varying sizes (40–90px) and opacities (0.12–0.28)
- Cluster at top-right or bottom-right corner
- Never combine with arc

**Optional subtle radial gradient on body:**
```css
background-image:
  radial-gradient(ellipse 700px 500px at 105% -5%, rgba(0,103,155,0.22) 0%, transparent 65%),
  radial-gradient(ellipse 400px 400px at -5% 105%, rgba(61,186,205,0.07) 0%, transparent 65%);
```

### QA Checklist
- [ ] ECR values verified against realrate-archive.com
- [ ] Company name exact spelling confirmed
- [ ] Only one accent color used for text elements
- [ ] Industry tag is white (not accent color)
- [ ] Industry Avg. value is white (not muted)
- [ ] Apple logo (or other company logo) visible in white rounded box
- [ ] No red or green in the design
- [ ] Tagline present, correct text, 16px
- [ ] Exported at 1080×1080px

### File Naming
`insight1_[companyslug].html` / `.png`
e.g. `insight1_apple.html`, `insight1_apple.png`

---

## Post Type: Not Top-Rated (NTR) — Gap Analysis
*(Template pending full approval)*

---

## Post Type: Industry Driver Pattern Carousel
*(4-slide carousel — template pending full approval)*

---

## Export Instructions

```bash
# From the post's folder directory
node export.mjs
# Exports all HTML files in folder to PNG at 1080×1080, deviceScaleFactor 2
```

Puppeteer path: `/Users/amnehqaljawi/.npm-global/lib/node_modules/puppeteer`
