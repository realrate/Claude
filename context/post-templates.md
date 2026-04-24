# Post Templates — RealRate Visual Design Context

This file is a reference for all approved post template specifications. Load it when generating any HTML visual post. For step-by-step production procedures, see `SOP/post-design-sop.md`.

---

## Approved Backgrounds
| Color | Hex | Notes |
|---|---|---|
| Dark Navy | `#0a1628` | Default — most posts |
| Dark Blue | `#00679B` | Alternate — carousel slides, NTR posts |
| Light Grey | `#f5f5f5` | Light section in split-band layouts only |
| Off-White | `#e8e8e8` | Light section variant |
| Medium Grey | `#8e96a2` | Insight posts — lighter, positive tone |

## Approved Split-Band Combinations
Split-band layout = solid color top section + light bottom section, divided by a `#3DBACD` 3px rule.

| Top (accent/header) | Bottom (content) | Use for |
|---|---|---|
| `#00679B` dark blue | `#f5f5f5` light grey | Carousel slides, NTR posts (default) |
| `#8e96a2` mid grey | `#f5f5f5` light grey | Insight posts — lighter, neutral tone |

---

## Accent Color Rule
One accent per design. Rotate across posts:
- `#3DBACD` — light teal (preferred on dark navy background)
- `#00679B` — dark blue (preferred when used as decoration, not text)

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

## Template: Not Top-Rated (NTR) — Gap Analysis
*(Pending approval — do not use until approved)*

---

## Template: Industry Driver Pattern Carousel (4 slides)
*(Pending approval — do not use until approved)*
