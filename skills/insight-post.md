# Skill — Insight Post (Types 1–4)

## Load
- `context/brand-core.md`
- `context/brand-voice.md`
- `context/design-system.md`

---

## Post Types
| Type | Format | Timing in cycle |
|---|---|---|
| Insight 1 — Company Editorial | Single image | Day +2 |
| Insight 2 — Industry YoY Shift | Carousel up to 3 slides | Day +4 |
| Insight 3 — Rotating Angle | Single image | Day +6 |
| Insight 4 — NTR Rotating | Single image | Day +8 |

---

## Steps
1. Identify which insight type and select angle from the angle bank below
2. Verify all ECR data at realrate-archive.com (use data checklist below)
3. Build HTML following design-system.md specs (L4 layout for Insight 1; L2 for Insight 2)
4. Apply `.change-negative` / `.change-positive` to all delta values
5. Write caption using approved structure below
6. Export: `node export.mjs`
7. QA against checklist

---

## Insight 1 — Company Editorial

### Angle Bank
| Angle | When to use |
|---|---|
| **Reputable, Not Top-Rated** | A well-known company failed to reach Top-Rated — ECR contradicts their reputation |
| **Unknown, Top-Rated** | A lesser-known company made Top-Rated ahead of recognised names |
| **The Surprise** | Any non-obvious finding — score, position, driver, or trajectory that defies expectation |

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
4. `Full ranking: realrate.ai/rankings/[industry]/[year]`

**Mandatory on Reputable Not Top-Rated:** *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### QA Checklist
- [ ] ECR values verified
- [ ] Company name exact spelling confirmed
- [ ] One accent color only
- [ ] Delta values use `.change-negative` / `.change-positive`
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
4. `Full ranking: realrate.ai/rankings/[industry]/[year]`

### QA Checklist
- [ ] All ECR values verified
- [ ] Max 3 slides, each with one clear message
- [ ] Slide numbering visible on every slide
- [ ] Consistent background and typography across slides
- [ ] Delta values use `.change-negative` / `.change-positive`
- [ ] Tagline on every slide

### File Naming
`insight2_slide[1-3]_[industryslug].html` / `.png`

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

Must not have been used in the prior 2 ranking cycles.

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

**Mandatory on all NTR posts:** *"ECR measures balance sheet strength, not revenue performance or market reputation."*

### File Naming
`insight4_[angle-slug]_[companyslug].html` / `.png`
