---
name: realrate-bizdev-cycle
description: Automates the full RealRate bizdev content cycle for a new industry ranking — fetches data from realrate-archive.com, generates all LinkedIn content (ranking carousel, seal post, 4 insight images, deep dive PDF), writes the DOCX/PDF article, drafts Instantly email sequences, LinkedIn outreach messages, and Pingen mail. Use whenever someone says "new cycle", "run the cycle for [industry]", "generate content for [industry]", "industry launch", or any task from the Bizdev Industry Task Template. Also use when working on RealRate LinkedIn posts, articles, outreach campaigns, or any bizdev automation for realrate.ai.
---

# RealRate Bizdev Cycle — Automation Engine

This skill automates the full bizdev content cycle for a new industry ranking. Given an industry slug and year, it fetches data, selects angles, and generates all deliverables.

## Input Required

Ask the user for:
1. **Industry slug** (e.g., `us_food`, `us_advertising`, `us_computers`, `us_recreation`)
2. **Marketing year** (e.g., 2026) — balance sheet year = marketing year - 1

## Data Source

All ranking data comes from `realrate-archive.com`. Read `references/data-api.md` for the full API reference.

Quick reference:
```
# Main ranking data (JSON)
https://www.realrate-archive.com/{industry_slug}/{balance_sheet_year}/website-ranking.json

# SVG graphs for companies
https://www.realrate-archive.com/{industry_slug}/{balance_sheet_year}/graphs/IME_{company_id}.svg
https://www.realrate-archive.com/{industry_slug}/{balance_sheet_year}/plot_over_time/{company_id}_strength_weakness.svg
https://www.realrate-archive.com/{industry_slug}/{balance_sheet_year}/backtesting_correlation/regression_{company_id}.svg

# Industry-level graphs
https://www.realrate-archive.com/{industry_slug}/{balance_sheet_year}/feature_importance/feature_importance.svg
https://www.realrate-archive.com/{industry_slug}/{balance_sheet_year}/backtesting_correlation/regression_{balance_sheet_year}.svg

# Historical data (prior years)
https://www.realrate-archive.com/{industry_slug}/{year}/website-ranking.json
```

## Step 1: Fetch & Analyze Data

1. Fetch `website-ranking.json` for the current balance sheet year
2. Extract: full ranking, ECR values, company_details, effects, strengths/weaknesses, report_text
3. Fetch prior years (at least 2-3) for historical comparison
4. Compute: market average ECR, YoY changes, top movers, biggest surprises

## Step 2: Select Angles

Based on data analysis, select the best angle for each content piece. Record selections in the output directory.

### Insight 1 — Company Editorial (Day +2)
Pick ONE based on data:
| Angle | Use when |
|---|---|
| **Reputable, Not Top-Rated** | A well-known company failed to reach Top-Rated |
| **Unknown, Top-Rated** | A lesser-known company made Top-Rated ahead of recognized names |
| **The Surprise** | Any non-obvious finding that defies expectation |

### Insight 2 — Industry YoY Shift (Day +4)
| Option | Use when |
|---|---|
| **Industry-Wide** | Sector-level ECR shift is the headline |
| **Company-Level** | A specific company's YoY shift is more compelling |

### Insight 3 — Rotating Angle (Day +6)
Must NOT repeat the last 2 cycles. Check `references/angle-rotation-log.md` before selecting.
| Angle | Use when |
|---|---|
| **The Industry Blind Spot** | One weakness driver across most companies |
| **The Market vs The Balance Sheet** | High market rating but low ECR, or vice versa |
| **The Methodology Moment** | Build credibility around ECR methodology |
| **The Investor Signal** | Industry health matters for investors/partners |
| **The Macro Lens** | Macro trend visibly affects the industry |

### Insight 4 — NTR Rotating (Day +8)
| Angle | Use when |
|---|---|
| **Almost There** | Company just below threshold — one driver is the gap |
| **The One Thing** | Single weakness pulling ECR below threshold |
| **The Fallen** | Company lost Top-Rated status from a prior year |
| **The Sector Drag** | Multiple companies in same sub-sector failing |
| **Close But Not Rated** | Strong traditional metrics but ECR threshold not met |
| **The Due Diligence Gap** | NTR status matters for investors/partners |

### Article angle
Read `references/article-angles.md` for full guidance. Default to "Ranking Interpretation" unless data strongly supports another angle.

## Step 3: Generate All Deliverables

Output directory: `report ({marketing_year})/US {Industry}/`

### 3A. Article Report (DOCX + PDF)

Use the `generate_report.py` pattern from `C:\Users\User\Downloads\Ranking Reports claude\Ranking Reports claude\`.

The script generates:
- **Matplotlib charts**: top 5 ECR bar chart, ECR history line chart, per-company effects charts, market stats chart
- **SVG downloads + PNG conversion** via Playwright for causal graphs, strength/weakness plots, regression plots, feature importance
- **Featured images** (1080x1080, dark + light variants) via PIL
- **DOCX article** (~1600 words, journalistic style, all charts embedded)
- **PDF conversion** via Word COM / docx2pdf / LibreOffice
- **LinkedIn post text**, website titles, meta descriptions

Key data structures to populate from the JSON:
```python
RANKING_{year} = [{"rank": N, "name": "...", "ecr": N}, ...]  # top 5
MARKET_AVG = N  # from report_text
HIST = {year: (company1_ecr, company2_ecr, company3_ecr, market_avg), ...}
EFFECTS = {"Company": {"Variable": value_pp, ...}, ...}
ECR_ABOVE = {"Company": N, ...}  # how far above market avg
REPORT_TEXT = {"Company": "summary string", ...}
FINANCIALS = {"Company": {"Assets": N, "Liabilities": N, ...}, ...}  # USD millions
FEAT_IMP = {"Variable": importance_pct, ...}  # from feature_importance
IDS = {"Company Name": "company_id", ...}  # for SVG URLs
```

## Content Principle: Caption + Visual Complement Each Other

Every LinkedIn post has two components that work together but never repeat:
1. **Visual** (image or carousel PDF) — shows the data, numbers, charts, comparisons
2. **Caption** — provides context, narrative, and commentary the visual cannot convey

**Rules for all posts:**
- Caption and visual must cover the same topic but from different angles — never restate what's visible in the image
- If the image shows "ECR 221%", the caption should explain what that means, not repeat "221%"
- Tone: **professional, authoritative, trustworthy** — no hype, no clickbait, no emojis in images
- Visual design: **premium, clean, professional** — correct RealRate logo, corporate colors, generous whitespace, no clutter
- Always use the correct logo variant: white horizontal on dark backgrounds, standard on light backgrounds

---

### 3B. Top 10 Ranking Infographic (2160x2160 image + caption)

Day 0 hero post — the main ranking announcement.

**VISUAL — `top10_ranking.png`:**

Premium infographic showing the top 10 companies by ECR. Must feel institutional-grade, like a financial report cover.

Layout (top → bottom):
| Zone | Content |
|---|---|
| Header | RealRate logo centered + teal accent stripe |
| Title | "TOP 10 US [INDUSTRY] COMPANIES RANKING [YEAR]" |
| Subtitle | "Most Financially Resilient Companies" |
| Ranking bars | 10 horizontal bars — ECR value, company name, rank badge |
| Info strip | "Annual Rankings · N Companies · Balance Sheet Year YYYY" |
| Footer | Dark background + "RealRate — Explainable Financial AI" |

Design specs:
- Canvas: 2160x2160 px (high-res for LinkedIn)
- Top 3 bars: `#00679B` (dark blue) with gold/silver/bronze rank badges
- Bars 4-10: `#AFAFAF` (grey)
- Market average line: `#3DBACD` dashed
- ECR labels: bold, right of each bar (e.g., "221%")
- Company logos: fetch from archive JSON `logo_url` field
- White border frame: 7px
- Clean spacing between bars — never cramped

**CAPTION — `linkedin_post.txt`:**

The caption provides the narrative the infographic cannot — why these rankings matter, what surprised, and what the reader should pay attention to. Never list the same numbers already visible in the image.

Structure:
- Medal emojis + 2-3 narrative sentences for top 3 (not just restating rank + ECR)
- Pipe-separated ranks 4-10 (brief)
- Fixed methodology block (always included verbatim)
- Industry-specific hook (never recycled between industries)
- Fresh CTA tied to the industry
- Exactly 8 hashtags: 6 standard (#Finance, #AI, #Investing, #RealRate, #FinancialHealth, #FinancialAnalysis) + 1 industry tag + 1 company name from top 3

---

### 3C. Insight 1 — Company Editorial (1080x1080 image + caption)

**VISUAL — `linkedin_editorial_image.png`:**

Use the `linkedin_editorial_*.py` pattern. Premium single image — dark navy gradient background. The image presents the data story at a glance.

Elements:
- RealRate logo (top-left, white horizontal)
- Industry tag (top-right, subtle)
- Main headline: company name + angle-specific hook (large, bold, white)
- ECR stat card: company ECR, market avg, rank, difference in pp — clean data layout
- Footer with RealRate tagline
- Teal accent stripe, diagonal line texture, angular accent polygons for depth

**CAPTION — `linkedin_editorial_caption.txt`:**

The caption tells the story behind the data shown in the image — methodology context, industry implications, what this means for stakeholders. Never restate the exact numbers already displayed.

Structure:
1. Hook — methodology positions the finding (not the number)
2. "In RealRate's recent financial assessment for the [industry] ranking, [Company] ranks #[N]."
3. One punchy insight line — what this reveals about the industry
4. `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

If angle is "Reputable Not Top-Rated", caption MUST include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

---

### 3D. Insight 2 — YoY Shift (carousel PDF + caption)

**VISUAL — `carousel_insight2.pdf`:**

Use the `linkedin_carousel_*.py` pattern. 1080x1350 per slide, up to 3 slides. Each slide delivers one clear data message — no text walls.

- **Slide 1** (light bg): The headline number — ECR change in pp, from/to years + values. Big, bold, impossible to miss.
- **Slide 2** (dark bg): What drove the shift — the key structural driver, shown with a visual comparison or data bar
- **Slide 3** (light bg, optional): The context — only if it adds genuinely new information

Design: alternating light/dark backgrounds, consistent header with logo + industry tag, slide numbers visible, generous padding.

**CAPTION — `carousel_insight2_caption.txt`:**

The caption adds the commentary and interpretation the slides cannot — why this shift matters, what it signals for the sector, what readers should watch next. Never restate figures visible on the slides.

End with: `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

---

### 3E. Insight 3 — Rotating Angle (1080x1080 image + caption)

**VISUAL — `linkedin_insight3_image.png`:**

Use the `linkedin_insight3_*.py` pattern. Dark charcoal gradient background. The image highlights the key data point for the selected angle — make it the visual hero. Clean, minimal, one clear message per image.

Elements: RealRate logo, industry tag, headline text for the angle, supporting data visualization (bar, comparison, or stat card), footer.

**CAPTION — `linkedin_insight3_caption.txt`:**

The caption provides the analytical narrative — why this pattern matters, what it means for the industry, the implication for financial decision-makers. The image shows the data; the caption explains the significance.

End with: `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

---

### 3F. Insight 4 — NTR Rotating (1080x1080 image + caption)

**VISUAL — `linkedin_insight4_image.png`:**

Use the `linkedin_insight4_*.py` pattern. Warm dark gradient background. Focus on the specific NTR company — show their ECR, the threshold, and the gap. Make the "almost but not quite" tension visual.

**CAPTION — `linkedin_insight4_caption.txt`:**

The caption contextualizes why NTR status matters — for investors, for counterparties, for the company itself. The image shows the data gap; the caption explains the real-world implications.

Caption MUST include: *"ECR measures balance sheet strength, not revenue performance or market reputation."*

End with: `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

---

### 3G. Deep Dive (carousel PDF + caption, 1080x1350, 10 slides)

**VISUAL — `carousel_deepdive.pdf`:**

Use the `linkedin_deepdive_*.py` pattern. Premium 10-slide document carousel. Alternating dark/light slides for visual rhythm. Each slide delivers one focused insight — no overcrowding.

| Slide | Background | Content |
|---|---|---|
| 1 (Cover) | Dark | "[Industry] Financial Health Report [Year] — What the Data Reveals" |
| 2 | Light | Industry snapshot: companies ranked, avg ECR, top-rated count |
| 3 | Dark | Top-rated companies with ECR numbers + shared dominant driver |
| 4 | Light | Insight 1 highlight — most compelling company story |
| 5 | Dark | The surprise — ECR contradicts assumptions |
| 6 | Light | Warning signal — bottom tier fragility pattern |
| 7 | Dark | What separates top-rated from the rest |
| 8 | Light | What this means for CFO/risk officer/investor |
| 9 | Dark | Methodology note — how ECR works |
| 10 | Light | CTA — "View the full ranking at realrate.ai" |

Design: consistent header/footer across all slides, slide numbers, RealRate logo on every slide, generous whitespace, data visualizations where possible (not just text).

Also export individual PNGs for flexibility.

**CAPTION — `deepdive_caption.txt`:**

Short, punchy — the deep dive itself is the content. The caption frames what the reader is about to see and why it's worth their time. Do not summarize the slides — let the document speak for itself.

End with: `Full ranking: https://realrate.ai/rankings/[industry_slug]/[year]`

### 3H. Instantly Outreach (API-automated)

Full automation via Instantly API (`https://api.instantly.ai/api/v2`). Requires API key — ask user if not already stored.

#### Step 1: Build target company lists from ranking data

From the fetched `website-ranking.json`, split all ranked companies into two ICPs:
- **ICP 1 — Top Rated**: companies above the Top-Rated ECR threshold
- **ICP 2 — Non Top Rated**: companies below the threshold

For each company, define target roles:
| ICP | Target roles |
|---|---|
| ICP 1 (Top Rated) | CEO, CFO, Head of Communications, Head of IR |
| ICP 2 (Non Top Rated) | CFO, VP Finance, Head of Risk, Treasurer |

#### Step 2: Find leads via Instantly Lead Finder API

Use the Lead Finder endpoint to search for contacts at each target company:
```python
POST https://api.instantly.ai/api/v2/lead-finder/search
Headers: {"Authorization": "Bearer {api_key}"}
Body: {
    "company_name": "Lifeway Foods",
    "job_titles": ["CFO", "Chief Financial Officer", "VP Finance"],
    "limit": 5
}
```

Collect verified email addresses. Save lead lists as CSV backup:
- `{industry}_leads_icp1.csv` — columns: email, first_name, last_name, company, title, ecr, rank
- `{industry}_leads_icp2.csv`

#### Step 3: Create campaigns

```python
POST https://api.instantly.ai/api/v2/campaigns
Body: {
    "name": "RealRate {Industry} {Year} — ICP 1 Top Rated",
    "sending_accounts": [...]  # ask user which sending accounts to use
}
```

Create two campaigns: one for ICP 1, one for ICP 2.

#### Step 4: Write email sequences

**ICP 1 — Top Rated Companies:**
Lead with financial transparency as a trust signal. Offer: seal + free evaluation + benchmarking.

**ICP 2 — Non Top Rated Companies:**
Lead with gap between perceived and actual financial health. Offer: consulting + improvement path.

| Email | Timing | Goal |
|---|---|---|
| 1 | Day 1 | Open + first impression — data-led hook |
| 2 | Day 3-4 | Build interest — different angle |
| 3 | Day 7-8 | Social proof — testimonial or finding |
| 4 | Day 12-14 | Soft CTA — low-pressure call offer |
| 5 | Day 20-22 | Final touch — keep door open |

Per-email structure:
- **Subject:** Short, specific, curiosity-driven — no clickbait. A/B test 2 variants.
- **Opening:** Personalized — reference their ECR rank, industry position, or a specific data point
- **Body:** Pain point → RealRate value prop → one verifiable claim
- **CTA:** One clear action per email

Add sequences to campaigns via API:
```python
POST https://api.instantly.ai/api/v2/campaigns/{campaign_id}/sequences
```

#### Step 5: Add leads to campaigns

```python
POST https://api.instantly.ai/api/v2/leads
Body: {
    "campaign_id": "...",
    "leads": [
        {"email": "...", "first_name": "...", "last_name": "...", "company": "...",
         "custom_variables": {"ecr": "221%", "rank": "1", "industry": "US Food"}}
    ]
}
```

Custom variables enable personalization in email templates (e.g., `{{ecr}}`, `{{rank}}`).

#### Step 6: Launch campaigns

**Do NOT auto-launch.** Present the user with a summary:
- Campaign names
- Number of leads per campaign
- Email sequence preview
- Sending account(s)

Ask for confirmation before launching. Launch 100 leads first — monitor 5-7 days before scaling.

```python
POST https://api.instantly.ai/api/v2/campaigns/{campaign_id}/activate
```

#### Target Metrics
| Metric | Target |
|---|---|
| Bounce Rate | ~5%, max 10% |
| Open Rate | 40-60% |
| Reply Rate | ~6% |
| Interested Rate | ~1% |
| Call Booked Rate | 0.66% |

Save email sequence text to `{industry}_instantly_icp1.txt` and `{industry}_instantly_icp2.txt` as backup.

### 3I. Seal Post Image (1080x1080)

Generate a post showing company logos with the RealRate Top-Rated seal. Layout:
- Dark or light background (match the featured image style)
- RealRate Top-Rated seal badge prominently displayed
- Grid of top-rated company logos
- Industry name + year

**Output:** `seal_post.png` + caption. Tags go in first pinned comment, not caption.

### 3J. LinkedIn Outreach Messages

Draft 4 message templates:
1. **Connection request** — personalized, no pitch (1-2 lines)
2. **Message 1** — insight + genuine question about their work
3. **Message 2** — different angle, new data point
4. **Message 3** — soft close, offer value

Save to `{industry}_linkedin_outreach.txt`.


## Design System (all visuals)

### Corporate Colors
```python
LIGHT_BLUE = "#3DBACD"   # Primary — teal accents, highlights
DARK_BLUE  = "#00679B"   # Primary — headers, chart titles
BLACK      = "#000000"   # Text, axes
GREY       = "#AFAFAF"   # Grid lines, secondary text
POS_COLOR  = "#5BB37F"   # Positive ECR effects (green)
NEG_COLOR  = "#C04A3A"   # Negative ECR effects (red)
```

### Fonts
- Primary: Arial (Bold, Regular, Italic)
- Path: `C:/Windows/Fonts/Arialbd.ttf`, `Arial.ttf`, `Ariali.ttf`

### Image Dimensions
- Single image posts: **1080x1080** (1:1)
- Carousel slides: **1080x1350** (4:5)

### Common Elements
- Top teal accent stripe: 8-10px
- White border frame: 7px all edges
- RealRate logo: white version on dark bg, standard on light bg
- Diagonal line overlay: `(255,255,255,4-7)` for subtle texture
- Angular teal accent polygons for depth

### Logos
Located at: `RealRate Logos/`
- `RealRate_logo_horizontal.png` (dark text, for light backgrounds)
- `RealRate_logo_horizontal_white.png` (white text, for dark backgrounds)

## Step 4: Post-Generation Checklist

After all files are generated:
- [ ] Verify all ECR values against the JSON source
- [ ] Check all company names are spelled correctly
- [ ] Confirm featured images have logos rendering properly
- [ ] Review captions for mandatory phrases (NTR disclaimer, ranking URL)
- [ ] Log which angles were used for this cycle

## Output Summary

When done, present the user with a summary of all generated files:
```
report ({year})/US {Industry}/
├── US_{Industry}_Rankings_{year}.docx          # Article report
├── US_{Industry}_Rankings_{year}.pdf
├── featured_image_dark.png                     # Article featured images
├── featured_image_light.png
├── top10_ranking.png                           # Day 0 — Top 10 infographic (2160x2160)
├── linkedin_post.txt                           # Day 0 — Ranking post caption
├── seal_post.png                               # Day 0-1 — Seal post image
├── seal_post_caption.txt
├── linkedin_editorial_image.png                # Day +2 — Insight 1 image + caption
├── linkedin_editorial_caption.txt
├── carousel_insight2.pdf                       # Day +4 — Insight 2 carousel + caption
├── carousel_insight2_caption.txt
├── linkedin_insight3_image.png                 # Day +6 — Insight 3 image + caption
├── linkedin_insight3_caption.txt
├── linkedin_insight4_image.png                 # Day +8 — Insight 4 image + caption
├── linkedin_insight4_caption.txt
├── carousel_deepdive.pdf                       # Day +10 — Deep dive carousel + caption
├── deepdive_caption.txt
├── website_title.txt                           # SEO titles + meta
├── titles.md                                   # All title variants
├── {industry}_leads_icp1.csv                   # Lead lists (backup)
├── {industry}_leads_icp2.csv
├── {industry}_instantly_icp1.txt               # Email sequences (backup)
├── {industry}_instantly_icp2.txt
└── {industry}_linkedin_outreach.txt            # LinkedIn DM templates
```

Each LinkedIn post = **1 image/PDF + 1 caption**.

Then tell the user: "All deliverables generated. Review the outputs, then publish in order: Day 0 ranking carousel + seal → Day +2 Insight 1 → Day +4 Insight 2 → Day +6 Insight 3 → Day +8 Insight 4 → Day +10-12 Deep Dive. Launch Instantly campaigns after Day 0."
