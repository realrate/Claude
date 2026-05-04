# Post Design SOP — RealRate LinkedIn Visual Posts

## Purpose
This SOP governs the creation of HTML-based visual posts for RealRate's LinkedIn channel. It defines the production workflow, file conventions, and quality checks for each approved post type.

---

## General Production Rules (All Post Types)

### Canvas
- **Size:** 1200×1200px square
- **Margin:** 50px all sides — all content and the logo must stay within this boundary
- **Font:** Manrope (Google Fonts) — weights 300, 400, 500, 600, 700, 800
- **Export:** Puppeteer via `export.mjs` at deviceScaleFactor 2 → PNG

### Color System

**Dark Backgrounds**
| Hex | Name |
|---|---|
| `#003b57` | Deep Navy (primary) |
| `#004a6e` | Navy Blue |
| `#005884` | Dark Blue |
| `#3389b1` | Medium Blue |
| `#34a2b3` | Blue Teal |
| `#2c8b9a` | Dark Teal |
| `#0a1628` | Dark Navy (legacy) |
| `#00679B` | Brand Blue (legacy) |

**Light Backgrounds**
| Hex | Name | Use |
|---|---|---|
| `#f5f5f5` | Light Grey | Data viz posts |
| `#e8e8e8` | Off-White | Light variant |
| `#ffffff` | White | Data viz only |

**Default text color:** White (`#ffffff`) on all dark backgrounds. Dark navy (`#003b57`) on light backgrounds.

### Accent Color Rule

Accent assignment by background type — never mix across types in one design:

| Background | Use these accent colors |
|---|---|
| Any **dark** background | `#f5f5f5` · `#e8e8e8` |
| Any **light** background | `#3DBACD` · `#00679B` |

One accent per design. Never use `#3DBACD` and `#00679B` both as text/UI highlights in the same post.

### Logo Rule

- **Dark backgrounds** → `RealRate_logo_light.svg` (white text), no wrap needed, top-left at 50px margin
- **Light backgrounds** → `RealRate_logo_horizontal.svg` (colored), no wrap needed, top-left at 50px margin

### What Never Appears
- Red or green — except when explicitly indicating a real financial loss (red) or gain (green) in ECR/metric data only
- Hashtags anywhere on images
- Tagline `"Powered by RealRate: Using Explainable Financial AI"` in captions — image only
- External company logo URLs — always inline SVG or letter initials
- Background pills or badge boxes on text labels

### Typography Scale

| Element | Size | Weight |
|---|---|---|
| Title | 50–64px | 700–800 (bold) |
| Subtitle | 30–53px | 400–500 |
| Heading | 35–40px | 400–500 (regular) |
| Subheading / Body | 25–30px | 400 (regular) |
| Stat values (large) | 48–64px | 800 |
| Stat labels | 13–16px | 700, uppercase, letter-spaced |
| Footer / Tagline | 16–20px | 400 |

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

## Post Type: The Surprise

### When to Use
One post per ranking cycle when a Surprise scenario is clearly supported by the data. Can be published as Insight 1 (Day +2) or Insight 2 (Day +5) depending on the strength of the finding — see `ranking-publication-protocol.md → Day +2 Decision Rule`.

One post type. The title and story angle depend on what the data shows — pick the angle that fits:

| Angle | Trigger | Title |
|---|---|---|
| **The Confirmation** | Well-known company at/near the top — the structural WHY is non-obvious | `THE CONFIRMATION` or `WHAT THE DATA REVEALS` |
| **Reputation Doesn't Rate** | Well-known company ranked significantly lower than their profile suggests | `REPUTATION DOESN'T RATE` |
| **The Unknown Leader** | Lesser-known company ranked ahead of recognized industry names | `THE UNKNOWN LEADER` |

### Data to Verify Before Starting (from realrate-archive.com)

**All angles:**
- [ ] Company name (exact)
- [ ] Current rank and ECR score (%)
- [ ] Industry average ECR (%)
- [ ] Total companies ranked

**The Confirmation and The Unknown Leader — strength driver:**
- [ ] Greatest strength driver name + contribution (pp)

**Reputation Doesn't Rate — weakness driver:**
- [ ] Greatest weakness driver name + contribution (pp)
- [ ] Number of companies ranked ahead of the subject company

**The Unknown Leader — comparison company:**
- [ ] At least one well-known company the subject outranks: name, rank, ECR (%)

### Layout Options

**Option 1 — Single Company (all variants)**
Follows the Biggest Mover structure adapted for the angle. Post label, title, subtitle, rank or ECR highlight, company header, description, stats bar.

```
┌─────────────────────────────────────────┐
│ [Logo]              [Industry Tag]       │
│                                         │
│ [POST LABEL]                            │
│ [TITLE — ALL CAPS, ~90–118px]           │
│ [one-liner subtitle — 19px, muted]      │
│                                         │
│          [spacer — flex:1]              │
│                                         │
│ [Company logo box + Company Name]        │
│ [Description — 23px, muted]             │
│                                         │
│ ECR SCORE | KEY DRIVER | INDUSTRY AVG.  │
│                                         │
│ Powered by RealRate: Using Explainable… │
└─────────────────────────────────────────┘
       [arc or geometric square decoration]
```

**Option 2 — Two-Company Comparison (The Unknown Leader preferred, Reputation Doesn't Rate optional)**
Side-by-side or stacked layout contrasting two companies. ECR values are the visual hero.

```
┌─────────────────────────────────────────┐
│ [Logo]              [Industry Tag]       │
│                                         │
│ [POST LABEL]                            │
│ [TITLE — ALL CAPS]                      │
│                                         │
│  [Company A logo + name]   vs           │
│  ECR: [X]%  Rank #[N]                  │
│  ─────────────────────────              │
│  [Company B logo + name]                │
│  ECR: [Y]%  Rank #[M]                  │
│                                         │
│ [One-line structural explanation]        │
│                                         │
│ Powered by RealRate: Using Explainable… │
└─────────────────────────────────────────┘
```

**Option 3 — Causal Graph (any angle)**
Replace or supplement the stats bar with the causal graph showing driver contributions to ECR. Particularly effective for Reputation Doesn't Rate (shows the specific driver pulling ECR down) and The Confirmation (shows the specific driver anchoring the top position). Use the existing causal graph design from prior posts or redesign for the specific data — either is approved. The core requirement: the graph must show the causal link from driver name to ECR contribution, not just the final score.

All titles: ALL CAPS, 90–118px, weight 800.

### Section-by-Section Rules

**Post Label**
- Text: `[YEAR] Ranking Insight`
- Color: accent color (`#3DBACD`)
- Size: 17px, 700 weight, uppercase, letter-spaced 3px

**One-Liner Subtitle**
- The Confirmation: `The structural driver behind their top ranking — and why it matters.`
- Reputation Doesn't Rate: `ECR measures balance sheet strength, not market presence.`
- The Unknown Leader: `A company you haven't heard of. A ranking that tells a different story.`
- Size: 19px, 400 weight, `rgba(255,255,255,0.5)`, max-width ~520px

**Company Header**
- Logo box: 64×64px white rounded box (`border-radius: 14px`), inline SVG inside
  - No SVG: use 2-letter initials, `#00679B` text on white bg, 26px bold
- Company name: white, 54px, 800 weight, gap 18px from logo box
- The Unknown Leader (Option 2 layout): show both companies — use a smaller logo/name pair for the comparison company

**Stats Bar (Option 1 layout)**
- Three columns, separated by `1px solid rgba(255,255,255,0.14)`
- Column 1 — ECR Score: label 13px muted · value accent color, 48px, 800 weight
- Column 2 — Key Driver: label 13px muted · driver name white 38px bold + contribution accent 34px
  - Reputation Doesn't Rate: label as `GREATEST WEAKNESS` in same style; value reflects the drag on ECR
- Column 3 — Industry Avg.: label 13px muted · value white 44px, 800 weight

**Caption Rule — Reputation Doesn't Rate (non-negotiable)**
Must include this line verbatim in caption: *"ECR measures balance sheet strength, not revenue performance or market reputation."* Prevents the post from being read as a brand attack.

### QA Checklist
- [ ] ECR values verified against realrate-archive.com
- [ ] Company name(s) exact spelling confirmed
- [ ] Angle selected (The Confirmation / Reputation Doesn't Rate / The Unknown Leader)
- [ ] Title matches the selected angle
- [ ] For Reputation Doesn't Rate: clarifying line present in caption draft
- [ ] For The Unknown Leader: comparison company data verified
- [ ] Only one accent color used for text elements
- [ ] Industry tag is white (not accent color)
- [ ] Industry Avg. value is white (not muted)
- [ ] No red or green unless indicating actual financial data loss or gain in a metric
- [ ] Tagline present, correct text, 16px
- [ ] Exported at 1080×1080px

### File Naming
`insight1_surprise_[companyslug].html` / `.png` — when used as Insight 1
`insight2_surprise_[companyslug].html` / `.png` — when used as Insight 2

e.g. `insight1_surprise_kraftheinz.html`, `insight2_surprise_freshpet.html`

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
