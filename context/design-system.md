# RealRate — Design System

Visual specs for all LinkedIn posts. Load this file when building any HTML post.

---

## Canvas
- **Size:** 1200×1200px
- **Margin:** 50px all sides — all content and logo stay within this boundary
- **Font:** Manrope (Google Fonts) — weights 300, 400, 500, 600, 700, 800
- **Export:** `node export.mjs` — Puppeteer at deviceScaleFactor 2 → PNG

---

## Colors

### Dark Backgrounds (approved)
| Hex | Name |
|---|---|
| `#003b57` | Deep Navy — primary |
| `#004a6e` | Navy Blue |
| `#005884` | Dark Blue |
| `#3389b1` | Medium Blue |
| `#34a2b3` | Blue Teal |
| `#2c8b9a` | Dark Teal |
| `#0a1628` | Dark Navy (legacy) |
| `#00679B` | Brand Blue (legacy) |

### Light Backgrounds (approved)
| Hex | Name | Use |
|---|---|---|
| `#f5f5f5` | Light Grey | Data viz, light slides |
| `#e8e8e8` | Off-White | Light variant |
| `#ffffff` | White | Data viz only |

### Brand Colors
| Role | Hex |
|---|---|
| Primary teal | `#3DBACD` |
| Primary blue | `#00679B` |
| Black | `#000000` |
| Grey | `#AFAFAF` |

### Semantic / Delta Colors
| Meaning | Hex |
|---|---|
| Strong Positive | `#419453` |
| Light Positive | `#86CC82` |
| Strong Negative | `#C04A3A` |
| Light Negative | `#F08F82` |
| Neutral | `#E8E8E8` |

**Delta rule:** Any ECR change or pp shift must use semantic color — never neutral/white. Apply via CSS:
```css
.change-negative { color: #C04A3A; }
.change-positive { color: #419453; }
```

### Accent Rule
One accent per design. Never mix across background types:
| Background | Accent colors |
|---|---|
| Dark | `#f5f5f5` · `#e8e8e8` |
| Light | `#3DBACD` · `#00679B` |

---

## Logo
- **Dark background** → `RealRate_logo_light.svg` (white), any corner at 50px margin
- **Light background** → `RealRate_logo_horizontal.svg` (colored), any corner at 50px margin
- Choose corner with most available space and least content collision

---

## Typography Scale

| Element | Size | Weight | Notes |
|---|---|---|---|
| Logo | 44px height | — | |
| Industry tag | 20px | 700 | Uppercase, letter-spaced, white |
| Post label badge | 25px | 700 | `#3DBACD` bg · `#003b57` text · `border-radius: 6px` · `padding: 10px 22px` · `align-self: flex-start` |
| Title | 64–72px | 800 | Uppercase, `letter-spacing: -2px` |
| Subtitle | 30px | 400 | `#ffffff` · `line-height: 1.45` |
| Company rank | 30px | 700 | Uppercase · `#ffffff` |
| Body / Description | 25–30px | 400 | `#ffffff` |
| Stat labels | 35px | 700 | Uppercase · `white-space: nowrap` · `letter-spacing: 0.5px` · `#ffffff` |
| Stat values (ECR) | 50–56px | 800 | `#f5f5f5` or white |
| Stat driver name | 32px | 700 | White |
| Stat driver gain | 28px | 600 | `#e8e8e8` |
| Tagline | 20px | 400 | `rgba(255,255,255,0.24)` · `position: absolute; bottom: 50px; left: 50px` |

---

## Layout Patterns

| ID | Name | Description | Best for |
|---|---|---|---|
| L1 | Circle Photo — Bottom Left | Dark BG; large circular B&W photo bottom-left; title large right | Cover posts, announcements |
| L2 | Vertical Split | Colored left panel ~55%; B&W photo right ~45% | Thought leadership, insight posts |
| L3 | Geometric Teal | Teal area; dark angular shapes one corner | Brand storytelling |
| L4 | Circle Photo — Corner | Dark BG; circular photo clipped top-right; bold title bottom-left | Ranking posts, insight 1 |
| L5 | Ring Photo | Dark BG; large ring right with photo inside; text left | Deep dives, feature posts |

### L1 — Circle Photo, Bottom Left
- **Background:** Deep navy (`#003b57`)
- **Photo element:** Large circle (B&W, desaturated) anchored bottom-left — partially bleeds off canvas
- **Logo:** White, any corner at 50px margin
- **Title:** Large bold white, centered-right — 50–64px
- **Subtitle / Body:** Stacked right side, white

### L2 — Vertical Split
- **Left panel (~55%):** Medium blue (`#3389b1`) — all text lives here
- **Right panel (~45%):** B&W photo, full-height
- **Logo:** White, any corner at 50px margin
- **Title:** Large bold white, left-aligned — 50–64px
- **Subtitle / Body:** Left panel, white, stacked below title

### L3 — Geometric Teal
- **Background:** Blue Teal (`#34a2b3`) main area
- **Geometric element:** Abstract angular/faceted dark blue shapes filling one corner quadrant (top-left) — mosaic effect against teal
- **Logo:** White, any corner at 50px margin (sits on geometric element area)
- **Title:** Large bold white on teal area — 50–64px
- **Subtitle / Body:** White on teal

### L4 — Circle Photo, Corner
- **Background:** Deep navy (`#003b57`)
- **Photo element:** Circular masked photo clipped to top-right corner — only partially visible (quarter circle)
- **Logo:** White, any corner at 50px margin
- **Title:** Large bold white, left-aligned bottom area — 50–64px
- **Subtitle / Body:** Below title, white, left-aligned

### L5 — Ring Photo
- **Background:** Deep navy (`#003b57`)
- **Photo element:** Large ring/donut shape right side — photo fills the ring, dark background through the center cutout; ring takes up ~45% of width
- **Logo:** White, any corner at 50px margin
- **Title:** Large bold white, left side — 50–64px
- **Subtitle / Body:** Left side, stacked below title, white

### Layout Rules (all patterns)
- Title section: `flex: 1; display: flex; flex-direction: column; justify-content: center`
- Bottom section: `flex-shrink: 0; margin-bottom: 70px`
- Tagline: `position: absolute; bottom: 50px; left: 50px`
- Company logo box: `background: #fff; border-radius: 12px; padding: 12px 22px; display: inline-flex` — logo inside at height 44px

---

## Data Visualization Posts
- **Background:** `#f5f5f5` or `#ffffff` only — never dark
- **Logo:** Colored (`RealRate_logo_horizontal.svg`), top-left
- **Text:** Dark navy `#003b57`
- **Primary series:** `#00679B` bars (US / main dataset)
- **Secondary series:** `#3DBACD` bars (Europe / secondary dataset)
- **Labels:** Right-aligned percentage values, dark navy
- **Section dividers:** Thin horizontal rules between groups where needed
- **Source line:** Bottom-left, small, grey — when citing external data
- **Style:** Horizontal bars, no gridlines, no background decoration

---

## What Never Appears on Images
- Hashtags
- Tagline in captions (image only)
- Emojis
- Red or green — except `.change-negative` / `.change-positive` on delta values
- External company logo URLs — always inline SVG or letter initials

---

## Design References (Competitor-Inspired)

### Deep Dive Cover Post → RapidRatings stat-led style
- Full-bleed B&W or desaturated industry photo as background
- Large partial arc/ring in `#00679B` — 40–50% of image, partially cropped at edges
- RealRate logo top-left, no wrap
- Lead stat bottom-left in oversized white type (e.g. "78%" or "43 companies")
- 1–2 lines white copy, CTA hook line in `#3DBACD`
- No boxes, no cards, no dividers — just layered type over image

### Top-Rated Seal Post → Moody's logo pairing style
- Background: flat `#00679B` — no gradients, no decorations
- RealRate logo left, company logo right — equal weight, centered
- No headline, no tagline, no badge — the pairing is the message
- Optional: one small line below in light opacity white, centered ("Top-Rated · US Computers 2026")

### General Insight Posts → Moody's geometric blocks style
- Background: flat `#00679B` or `#0a1628`
- Decorative squares: solid `#3DBACD` at `opacity: 0.25–0.35` — top-right corner + bottom edge, 2–4 squares, 60–120px
- Content type label in `#3DBACD` uppercase — matches squares
- Headline: white, 60–80px, dominant
- Never use arcs AND geometric squares in the same post — pick one

### NTR / Report Posts → RapidRatings split layout style
- Vertical two-panel: photo left with blue overlay, dark blue right with white headline
- More editorial/B2B — works well for CFO-targeted content
