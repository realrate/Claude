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

## Delta / Change Value Color Rule

Any ECR change, pp shift, or directional delta displayed on a post must use semantic color:

| Direction | Color | Hex |
|---|---|---|
| Negative change (decline) | Strong Negative red | `#C04A3A` |
| Positive change (growth) | Strong Positive green | `#419453` |

Apply via CSS class — add `.change-negative` or `.change-positive` to the delta element. These classes must be defined in every insight post that shows a change value:

```css
.change-negative { color: #C04A3A; }
.change-positive { color: #419453; }
```

Never use neutral/white (`#e8e8e8`, `#f5f5f5`) for a delta value — the direction must be visually clear.

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

## Insight 1 — Company Editorial

One post per ranking cycle. Angle and title chosen based on what the data shows — pick whichever scenario is most clearly supported.

### Angles

| Angle | When to use |
|---|---|
| **Reputable, Not Top-Rated** | A well-known company failed to reach Top-Rated. Their ECR tells a different story than their reputation |
| **Unknown, Top-Rated** | A lesser-known company made Top-Rated ahead of recognized names in the same industry |
| **The Surprise** | Any non-obvious finding about a ranked company — score, driver, position, or trajectory |

### Title Rule
Free-form. Written based on the specific company and what the data shows. Must be professional, direct, one clear hook, specific to this company and data.

### Layout — Single Post (L4 approved · approved May 2026)

```
┌─────────────────────────────────────────┐
│ [Logo 44px]         [Industry Tag 20px] │  ← top bar
│                   ╭──────────────╮      │
│ [POST LABEL BADGE] │  circular    │      │  ← teal badge · photo
│ [TITLE 64–72px]    │  photo       │      │    clipped top-right
│ [Subtitle 30px]    │  top-right   │      │
│                    ╰──────────────╯      │
│  [title section flex:1 — vertically     │
│   centered in available space]          │
│                                         │
│ [Company logo in white box]             │  ← bottom section
│ [Rank 30px · muted]                    │    margin-bottom: 70px
│ [Description 25–30px · muted]          │
│ ─────────────────────────────          │
│ ECR SCORE | KEY DRIVER | INDUSTRY AVG. │  ← stat labels 35px
│ [56px]    | [32px  +28pp] | [50px]    │
│                                         │
│ Powered by RealRate…  [absolute bottom] │  ← tagline 20px
└─────────────────────────────────────────┘
```

**Flex structure:**
- `body`: `display: flex; flex-direction: column; position: relative; padding: 50px`
- `title-section`: `flex: 1; display: flex; flex-direction: column; justify-content: center`
- `bottom-section`: `flex-shrink: 0; margin-bottom: 70px`
- `tagline`: `position: absolute; bottom: 50px; left: 50px`

**Post label badge:**
- `background: #3DBACD; color: #003b57; border-radius: 6px; padding: 10px 22px; align-self: flex-start`

**Company logo box:**
- White rounded box — `background: #fff; border-radius: 12px; padding: 12px 22px; display: inline-flex`
- Actual company logo image inside (height 44px, width auto)

Two-company comparison layout available for Unknown, Top-Rated — ECR values as visual hero.

### Data Fields Required

| Field | Angles |
|---|---|
| Company name (exact) | All |
| Current rank | All |
| ECR score (%) | All |
| Industry average ECR (%) | All |
| Strength driver + contribution (pp) | Unknown Top-Rated, The Surprise |
| Weakness driver + contribution (pp) | Reputable Not Top-Rated |
| Comparison company: name, rank, ECR (%) | Unknown Top-Rated (optional) |

### Caption Rule — Reputable, Not Top-Rated
Must include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### Caption Structure — Insight 1 (approved)

**Formula:** Methodology hook → Data reveal → ECR definition reminder → Key driver → Benchmark comparison → Ranking URL

**Opening hook template (Option B — methodology-first):**
> "[What ECR measures] and [what it is not] are different things. RealRate's ECR isolates one — how structurally sound a company's finances are. In [year], that lens produced a clear result."

**Full structure:**
1. Hook — position the methodology before the finding (2–3 sentences)
2. Company name + rank (exact)
3. ECR definition reminder — one line, three "Not X" statements
4. Key driver + pp contribution
5. Industry average ECR vs company ECR (gap in points)
6. Ranking URL

### File Naming
`insight1_[companyslug].html` / `.png`

---

## Insight 2 — Industry YoY Shift

Up to 3 slides. Compares ECR performance vs the prior 1–2 years. Two options — use whichever is supported by the data.

### Options

| Option | When to use |
|---|---|
| **Industry-Wide** | The sector is the story — how the average ECR moved, how many companies shifted, what changed overall |
| **Company-Level** | A well-known company's YoY shift is the headline, supported by broader industry context |

### Slide Structure (max 3 slides)

**Slide 1 — The Shift**
Lead with the headline number. Industry ECR avg then vs now, or company ECR then vs now. The change in points is the visual hero.

**Slide 2 — What Drove It**
The key structural reason behind the shift. One clear finding from the data.

**Slide 3 — The Context** *(use only if it adds meaningful information)*
Where this industry sits relative to others, or what the shift signals for the next cycle.

### Data Fields Required

| Field | Notes |
|---|---|
| Industry name | Exact |
| Current year ECR average (%) | Verified against archive |
| Prior year ECR average (%) | 1 or 2 years back |
| ECR change (pp) | Current minus prior |
| # companies ranked (current vs prior) | If changed |
| Key driver of shift | From archive |
| Company name + ECR current + prior (%) | Company-Level option only |
| Company rank current + prior | Company-Level option only |

### File Naming
`insight2_slide[1-3]_[industryslug].html` / `.png`

---

## Insight 3 — Rotating Angle

One post per ranking cycle. Angle rotates across publications — pick the one most supported by the current data and least recently used.

### Angle Bank

| Angle | Story |
|---|---|
| **The Industry Blind Spot** | One weakness driver appears across most companies in the industry — a structural drag most haven't addressed |
| **The Market vs The Balance Sheet** | A company the market rates highly has a low ECR — or vice versa. Market perception vs structural financial health |
| **The Industry Trend** | How industry ECR has shifted over 2–3 years. Getting stronger or weaker — and what's behind it |
| **The Methodology Moment** | What ECR measures that other ratings don't. One clear explanation that builds trust in the ranking |
| **The Investor Signal** | Is this industry financially healthy right now? Safe, risky, stable, fragile — the ECR answers it for investors and business partners |
| **The Macro Lens** | An industry under pressure from a continuous trend — war, sanctions, tariffs, rate cycles. What the balance sheets show that headlines don't |

### Title Rule
Free-form. Match the angle and the specific data. Professional, direct, hook-driven.

### Data Fields Required (by angle)

| Angle | Key Data |
|---|---|
| Industry Blind Spot | Most common weakness driver + % of companies affected |
| Market vs Balance Sheet | Company market cap/valuation + ECR + industry avg ECR |
| Industry Trend | Industry ECR avg across 2–3 years |
| Methodology Moment | No specific data required |
| Investor Signal | ECR avg, % Top-Rated, highest vs lowest ECR in industry |
| Macro Lens | ECR avg current vs prior; companies most affected; external event context |

### File Naming
`insight3_[angle-slug]_[industryslug].html` / `.png`
e.g. `insight3_blindspot_uscomputers.html`, `insight3_macro_usfinance.html`

---

## Insight 4 — Non-Top-Rated (NTR) Rotating

One post per ranking cycle. Angle rotates — pick the one most clearly supported by the data.

### Angle Bank

| Angle | Story |
|---|---|
| **Almost There** | A company sitting just below the Top-Rated threshold. One driver is the difference — and it's specific |
| **The One Thing** | A single weakness driver is pulling ECR below threshold. Remove it and they'd qualify |
| **The Fallen** | A company that held Top-Rated in a prior year and has since dropped. What changed in the balance sheet |
| **The Sector Drag** | Multiple companies in the same sub-sector all failing to reach Top-Rated. Company problem or structural industry issue |
| **Close But Not Rated** | Performs well by traditional metrics — revenue, market cap, brand. ECR threshold not met |
| **The Due Diligence Gap** | Why NTR status matters for investors, counterparties, and business partners — anchored on a real company |

### Title Rule
Free-form. The title reflects the specific angle and company — not the angle name itself. Professional, direct, hook-driven.

### Layout — Single Post

```
┌─────────────────────────────────────────┐
│ [Logo]              [Industry Tag]       │
│                                         │
│ [RANKING INSIGHT · YEAR]                │
│ [TITLE — free-form, 50–64px, bold]      │
│ [Subtitle — 30px, muted]                │
│                                         │
│          [spacer — flex:1]              │
│                                         │
│ [Company logo box + Company Name]        │
│ [Rank — e.g. #34 of 43]                │
│ [Description — 25–30px, muted]          │
│                                         │
│ ECR SCORE | KEY WEAKNESS | INDUSTRY AVG.│
│                                         │
│ Powered by RealRate: Using Explainable… │
└─────────────────────────────────────────┘
```

### Data Fields Required

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

### Caption Rule — All NTR Posts
Must include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### File Naming
`insight4_[angle-slug]_[companyslug].html` / `.png`
e.g. `insight4_fallen_kraftheinz.html`, `insight4_almostthere_apollo.html`
