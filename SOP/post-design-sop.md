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

- **Dark backgrounds** → `RealRate_logo_light.svg` (white text), no wrap needed, any corner at 50px margin
- **Light backgrounds** → `RealRate_logo_horizontal.svg` (colored), no wrap needed, any corner at 50px margin

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

## Post Type: Insight 1 — Company Editorial

### When to Use
One post per ranking cycle. Angle chosen based on what the data most clearly supports.

| Angle | Trigger |
|---|---|
| **Reputable, Not Top-Rated** | A well-known company failed to reach Top-Rated — ECR contradicts their reputation |
| **Unknown, Top-Rated** | A lesser-known company made Top-Rated ahead of recognized names |
| **The Surprise** | Any non-obvious finding about a ranked company — score, driver, position, or trajectory |

### Data to Verify (from realrate-archive.com)
- [ ] Company name (exact spelling)
- [ ] Current rank and total companies ranked
- [ ] ECR score (%)
- [ ] Industry average ECR (%)
- [ ] Strength driver + contribution (pp) — Unknown Top-Rated, The Surprise
- [ ] Weakness driver + contribution (pp) — Reputable Not Top-Rated
- [ ] Comparison company name, rank, ECR (%) — Unknown Top-Rated if using two-company layout

### Layout

```
┌─────────────────────────────────────────┐
│ [Logo — any corner]   [Industry Tag]    │
│                                         │
│ [RANKING INSIGHT · YEAR]                │
│ [TITLE — free-form, 50–64px, bold]      │
│ [Subtitle — 30px, muted]                │
│                                         │
│          [spacer — flex:1]              │
│                                         │
│ [Company logo box + Company Name]        │
│ [Rank + ECR — key data point]           │
│ [Description — 25–30px, muted]          │
│                                         │
│ ECR SCORE | KEY DRIVER | INDUSTRY AVG.  │
│                                         │
│ Powered by RealRate: Using Explainable… │
└─────────────────────────────────────────┘
```

Two-company comparison layout available for Unknown Top-Rated — ECR values as visual hero.

### Title Rule
Free-form. Written for the specific company and data. Professional, direct, one hook-line. Not the angle name.

### QA Checklist
- [ ] ECR values verified against realrate-archive.com
- [ ] Company name exact spelling confirmed
- [ ] Angle selected and documented
- [ ] For Reputable Not Top-Rated: caption includes ECR clarifying line
- [ ] One accent color only
- [ ] Industry tag white, not accent
- [ ] Industry Avg. white, not muted
- [ ] Tagline present, 16–20px
- [ ] Exported at 1200×1200px

### Caption Rule — Reputable Not Top-Rated + all Insight 4 posts
Must include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### File Naming
`insight1_[companyslug].html` / `.png`

---

## Post Type: Insight 2 — Industry YoY Shift

### When to Use
One carousel per ranking cycle. Compares ECR performance vs prior 1–2 years. Max 3 slides. Two options — use whichever the data supports.

| Option | When to use |
|---|---|
| **Industry-Wide** | The sector shift is the headline — average ECR movement, companies moving up or down |
| **Company-Level** | A well-known company's YoY shift is the story, supported by industry context |

### Slide Structure

**Slide 1 — The Shift**
Headline number leads. Industry ECR avg then vs now, or company ECR then vs now. The change in points is the visual hero.

**Slide 2 — What Drove It**
The key structural reason behind the shift. One clear finding.

**Slide 3 — The Context** *(only if it adds meaningful information)*
Where the industry sits relative to others, or what the shift signals for the next cycle.

### Data to Verify (from realrate-archive.com)
- [ ] Industry ECR average — current year
- [ ] Industry ECR average — prior 1 or 2 years
- [ ] ECR change (pp) — current minus prior
- [ ] Key driver of shift
- [ ] # companies ranked — current vs prior (if changed)
- [ ] Company name, ECR current + prior, rank current + prior — Company-Level option only

### QA Checklist
- [ ] All ECR values verified against archive
- [ ] No more than 3 slides
- [ ] Each slide has one clear message — no overloading
- [ ] Slide numbering visible (e.g. 1/3, 2/3)
- [ ] Consistent background and typography across all slides
- [ ] Tagline on every slide
- [ ] Exported at 1200×1200px

### File Naming
`insight2_slide[1-3]_[industryslug].html` / `.png`

---

## Post Type: Insight 3 — Rotating Angle

### When to Use
One post per ranking cycle. Rotate through the angle bank — pick the one most supported by the current data and least recently used.

### Angle Bank

| Angle | Story |
|---|---|
| **The Industry Blind Spot** | One weakness driver appearing across most companies in the industry — a structural drag most haven't addressed |
| **The Market vs The Balance Sheet** | A company the market rates highly has a low ECR, or vice versa — perception vs structural health |
| **The Industry Trend** | How industry ECR has shifted over 2–3 years — getting stronger or weaker, and what's behind it |
| **The Methodology Moment** | What ECR measures that other ratings don't — one clear explanation that builds trust in the ranking |
| **The Investor Signal** | Is this industry financially healthy right now? Safe, risky, stable, fragile — the ECR answers it |
| **The Macro Lens** | An industry under pressure from a continuous trend — war, sanctions, tariffs, rate cycles — what the balance sheets show that headlines don't |

### Data to Verify (by angle)

| Angle | Key Data Needed |
|---|---|
| Industry Blind Spot | Most common weakness driver + % of companies affected |
| Market vs Balance Sheet | Company market cap/valuation + ECR score + industry avg ECR |
| Industry Trend | Industry ECR avg across 2–3 years |
| Methodology Moment | No specific data required |
| Investor Signal | ECR avg, % Top-Rated, highest vs lowest ECR in industry |
| Macro Lens | ECR avg current vs prior; affected companies; external event context |

### Title Rule
Free-form. Match the angle and the specific data. Professional, direct, hook-driven.

### QA Checklist
- [ ] Angle selected and not used in the previous 2 ranking publications
- [ ] All ECR values verified against archive
- [ ] External claims (market data, macro events) sourced from trusted public sources
- [ ] One accent color only
- [ ] Tagline present
- [ ] Exported at 1200×1200px

### File Naming
`insight3_[angle-slug]_[industryslug].html` / `.png`
e.g. `insight3_blindspot_uscomputers.html`, `insight3_macro_usfinance.html`

---

## Post Type: Insight 4 — Non-Top-Rated (NTR) Rotating

### When to Use
One post per ranking cycle. Rotate through the angle bank — pick the one most clearly supported by the data.

### Angle Bank

| Angle | Story |
|---|---|
| **Almost There** | A company sitting just below the Top-Rated threshold. One driver is the specific difference |
| **The One Thing** | A single weakness driver is pulling ECR below threshold — remove it and they'd qualify |
| **The Fallen** | A company that held Top-Rated in a prior year and has since dropped — what changed |
| **The Sector Drag** | Multiple companies in the same sub-sector all failing to reach Top-Rated — company problem or structural issue |
| **Close But Not Rated** | Performs well by traditional metrics — revenue, market cap, brand — but ECR threshold not met |
| **The Due Diligence Gap** | Why NTR status matters for investors, counterparties, and partners — anchored on a real company |

### Data to Verify (from realrate-archive.com)

| Field | Notes |
|---|---|
| Company name (exact) | Verified |
| Current rank (e.g. #34 of 43) | Verified |
| ECR score (%) | Verified |
| Industry average ECR (%) | Verified |
| Top-Rated threshold ECR (%) | Almost There, The One Thing, Close But Not Rated |
| Gap to threshold (pp) | Almost There |
| Key weakness driver + contribution (pp) | All except The Due Diligence Gap |
| Prior year rank + ECR | The Fallen |
| # companies in sub-sector below threshold | The Sector Drag |

### Title Rule
Free-form. Reflects the specific angle and company — not the angle name. Professional, direct, hook-driven.

### QA Checklist
- [ ] All ECR values verified against archive
- [ ] Company name exact spelling confirmed
- [ ] Angle selected — documented in file notes
- [ ] Caption includes ECR clarifying line (mandatory for all NTR posts)
- [ ] For The Fallen: prior year data verified
- [ ] For Almost There: gap to threshold calculated and verified
- [ ] One accent color only
- [ ] Tagline present
- [ ] Exported at 1200×1200px

### Caption Rule — All NTR Posts (non-negotiable)
Must include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### File Naming
`insight4_[angle-slug]_[companyslug].html` / `.png`
e.g. `insight4_fallen_kraftheinz.html`, `insight4_almostthere_apollo.html`

---

## Export Instructions

```bash
# From the post's folder directory
node export.mjs
# Exports all HTML files in folder to PNG at 1080×1080, deviceScaleFactor 2
```

Puppeteer path: `/Users/amnehqaljawi/.npm-global/lib/node_modules/puppeteer`
