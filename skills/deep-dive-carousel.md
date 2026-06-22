# Generate Industry Deep Dive Carousel

Generate a complete Industry Deep Dive Carousel for a given industry and year. Produces all required output files: interactive HTML, print HTML, PDF, animated GIF, and LinkedIn post.

## Usage

```
/deep-dive-carousel [industry name] [year]
```

Example: `/deep-dive-carousel "US Software" 2026`

---

## Step 0 — Read context files

Before doing anything else, read all of these:

- `C:\Users\shaky\Downloads\RealRate claude\RealRate\Industry Deep Dive Carousel\CLAUDE.md`
- `C:\Users\shaky\Downloads\RealRate claude\RealRate\Industry Deep Dive Carousel\deep-dive-template.md`
- `C:\Users\shaky\Downloads\RealRate claude\RealRate\context\brand-context.md`
- `C:\Users\shaky\Downloads\RealRate claude\RealRate\context\brand-voice.md`

---

## Step 1 — Verify the industry URL slug

Fetch `https://realrate.ai/rankings` and confirm the exact slug for this industry. Never guess the slug from the industry name. Record it as `[slug]`.

Known slugs for reference (always verify live):
- US Food → `us_food`
- US Financial Services → `us_finance_services`
- US Brokers → `us_brokers`
- US Motor → `us_motor`
- US Software → `us_software`

---

## Step 2 — Pull data from the live rankings page

Fetch `https://realrate.ai/rankings/[slug]/[year]` and extract:

- Top 10 companies with ECR scores and Top-Rated status
- Industry average ECR (current year)
- Total companies ranked
- Total Top-Rated companies
- Greatest strength driver + point contribution for each Top-5 company

---

## Step 3 — Pull data from the archive

Fetch `https://www.realrate-archive.com/[slug]/[year-1]/` (archive year = ranking year − 1).

Extract for each company in the Top 10:
- Year-over-year rank change
- ECR for ranks 6–10 (calculated as: `effect × 100 + industry_average` from the causal graph JSON at `graphs/[CIK].json`)
- Prior year industry average ECR
- Biggest mover (largest rank change up or down)
- One "surprise" company (well-known name whose ECR contradicts expectations)
- Bottom-tier fragility: dominant weakness driver, % of companies affected, average ECR gap

---

## Step 4 — Choose the industry colour scheme

Pick a colour palette distinct from all previously used schemes. Update `:root` CSS variables and the cover/Slide 7/Slide 10 gradients accordingly. The colour table in `CLAUDE.md` lists existing schemes — do not reuse them.

Example palette variables to set:
```css
--cover-bg-start, --cover-bg-end  /* cover gradient */
--blue-dark                        /* primary dark */
--blue-light                       /* accent / highlight */
--accent                           /* gold / warm accent */
--stripe-angle                     /* diagonal stripe °  */
```

---

## Step 5 — Source company logos (Top 10)

For each of the Top 10 companies, obtain an SVG logo using this priority order:

1. **Wikimedia Commons** — query the API: `commons.wikimedia.org/w/api.php?action=query&titles=File:[Name]_logo.svg&prop=imageinfo&iiprop=url&format=json`
2. **Company website** — scrape homepage for SVG logo tag
3. **Wordmark SVG fallback** — generate manually:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 40">
  <rect width="220" height="40" fill="none"/>
  <text x="8" y="28" font-family="Arial, sans-serif" font-size="22" font-weight="900" fill="#111">CompanyName</text>
</svg>
```

Save each SVG as `[company-slug]-logo.svg` inside the industry subfolder.

Also download PNG thumbnails (for the GIF generator) from:
`https://en.wikipedia.org/w/index.php?title=Special:Redirect/file/[File].svg&width=320`
Save as `[company-slug]-logo.png`.

---

## Step 6 — Create the industry subfolder

```
Industry Deep Dive Carousel/[Industry Name]/
```

All output files go inside this subfolder. Never write files loose in the root carousel folder.

---

## Step 7 — Generate the interactive HTML

File: `[Industry Name]/[industry-slug]-[year].html`

**Spec:** 540×675px interactive preview · 10 slides · slide navigation dots.

Follow all design rules from `CLAUDE.md`:

- **Cover (Slide 1):** Two rows of 5 cards (Top 10). Rank colours: gold/silver/bronze/#4–5 blue-light/#6–10 blue-light. Stats bar: companies · avg ECR · Top-Rated count. RealRate logo in white pill top-center.
- **Slide 2 — Industry at a Glance:** Key stats, YoY ECR change, avg ECR bar fill proportional to ECR on a 600% scale.
- **Slide 3 — All Top-Rated:** Rows #1–#5 with driver chip; rows #6+ without. Compress rows if 9+ companies (`gap: 5px`, `padding: 8px 12px`).
- **Slide 4 — Biggest Mover:** Rank before/after, ECR, key driver with point contribution.
- **Slide 5 — The Surprise:** Company, rank, ECR, market assumption vs. data reality, structural explanation.
- **Slide 6 — Warning Signal:** Aggregate only — no company names. Red accent treatment.
- **Slide 7 — What Separates Top-Rated:** Three driver-grounded factors. Dark background.
- **Slide 8 — What This Means For You:** CFO / Investor / Risk Officer rows.
- **Slide 9 — Methodology:** Standard RealRate ECR explanation — no customisation.
- **Slide 10 — CTA:** Dark background. Ranking URL verified against live page.

Font: Manrope throughout. No emojis on any slide. Footer on every slide except Slide 9 (use `realrate.ai/methodology` instead).

RealRate logo path in interactive HTML: `../../RealRate Logos/RealRate_logo_horizontal.png`

---

## Step 8 — Generate the print HTML

File: `[Industry Name]/[industry-slug]-[year]-print.html`

**Spec:** 1080×1350px design · zoom 1.111 → 1200×1500px output · all font sizes doubled vs. interactive.

Required print CSS:
```css
@page { size: 1200px 1500px; margin: 0; }
body  { width: 1080px; margin: 0; zoom: 1.11111; }
.slide { width: 1080px; height: 1350px; page-break-after: always; }
.slide:last-child { page-break-after: avoid; }
.slide-body { flex: 1; display: flex; flex-direction: column; padding: 20px 52px; justify-content: center; }
.cover-inner { justify-content: space-between; }
.cover-h-rule { display: none; }
```

**All logos must be base64 data URIs in the print HTML** — never relative paths (Chrome headless runs from C:\Temp\ so relative paths produce a blank PDF). Apply base64 replacement immediately after writing the file:

```powershell
$rr = "data:image/png;base64," + [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\shaky\Downloads\RealRate claude\RealRate\RealRate Logos\RealRate_logo_horizontal.png"))
# repeat for each company SVG
$html = $html -replace 'src="\.\.\/\.\.\/RealRate Logos\/RealRate_logo_horizontal\.png"', "src=""$rr"""
Set-Content "[Industry Name]\[industry]-[year]-print.html" $html -Encoding UTF8
```

Company logo CSS: `filter: brightness(0) invert(1)` on `.co5-logo img` and `.co-rest-logo img`.

---

## Step 9 — Generate the PDF

Copy the print HTML to `C:\Temp\` first (paths with spaces silently fail in Chrome headless):

```powershell
Copy-Item "[Industry Name]\[industry-slug]-[year]-print.html" "C:\Temp\rr_print.html" -Force

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
Start-Process $chrome -ArgumentList @(
    "--headless=new","--disable-gpu","--no-margins",
    "--user-data-dir=$env:TEMP\chrome_rr",
    "--print-to-pdf=C:\Temp\rr_out.pdf",
    "--print-to-pdf-no-header",
    "file:///C:/Temp/rr_print.html"
) -Wait
Start-Sleep -Seconds 8

if (Test-Path "C:\Temp\rr_out.pdf") {
    Move-Item "C:\Temp\rr_out.pdf" "[Industry Name]\[industry-slug]-[year].pdf" -Force
    $i = Get-Item "[Industry Name]\[industry-slug]-[year].pdf"
    "PDF OK — $([math]::Round($i.Length/1KB,1)) KB"
} else { "PDF NOT found — check print HTML logos are base64" }
```

---

## Step 10 — Generate the animated cover GIF

Update `generate_cover_gif.py` with industry-specific constants:

| Constant | Value |
|---|---|
| `OUT_PATH` | `[Industry Name]/[industry-slug]-[year]-cover.gif` |
| `TOP5` | Top-5 company names, ECR scores, rank colours |
| `_LOGO_FILES` | PNG filenames for ranks 1–5 |
| `_load_logo()` path | `"[Industry Name]"` directory |
| `make_base()` gradient | Match the industry colour palette from Step 4 |
| `make_base()` stats | Companies count · avg ECR · Top-Rated count |
| `make_base()` title | `"[INDUSTRY NAME]"` (all caps) |

Then run:
```powershell
python "C:\Users\shaky\Downloads\RealRate claude\RealRate\Industry Deep Dive Carousel\generate_cover_gif.py"
```

Expected output: 1080×~924px · 25 frames · ~250–320 KB · reveals #5→#1.

---

## Step 11 — Write the LinkedIn post

File: `[Industry Name]/linkedin-post.txt`

Use this caption structure:

```
[N] [industry] companies ranked by financial health — not by [revenue / AUM / brand].

The #1 company isn't [expected well-known leader]. It's [actual #1] — with an ECR of [X%].

The top 10 companies that earned Top-Rated status in [year]:

1. [Company] — [X%] ECR
[One sentence: specific balance sheet reason.]
…(through #10)

The structural pattern across all [N] Top-Rated companies: [shared trait].

[Market contrast: "[Big name] — [scale claim] — ranks [N]th with an ECR of [X%]. Scale does not equal financial health."]

Industry average: [X]% — [up/down] [N] points year-over-year.
Only [N] of [total] companies earned Top-Rated status.

Full ranking: https://realrate.ai/rankings/[slug]/[year]

Powered by RealRate: Using Explainable Financial AI

#RealRate #[IndustryHashtag] #FinancialHealth #ExplainableAI #Investing
```

Caption rules:
- Hook must name a well-known company the reader would expect to rank #1 — then subvert it
- Top 10 listed (not all Top-Rated), one data-grounded sentence per company
- Full URL always in body — never "link in first comment"
- Market contrast sentence required
- Max 5 hashtags · always include `#RealRate` · no company tags in caption

First pinned comment:
```
Full [year] [Industry] ranking: https://realrate.ai/rankings/[slug]/[year]
[@Company1 @Company2 @Company3 @Company4 @Company5]
```

Publishing notes: Schedule for Day +9 or +10 of the ranking publication cycle. Never on a consecutive day after another ranking post.

---

## Step 12 — Final checklist

Confirm all outputs exist before reporting done:

- [ ] `[industry-slug]-[year].html` — interactive preview (540×675px)
- [ ] `[industry-slug]-[year]-print.html` — print source with base64 logos
- [ ] `[industry-slug]-[year].pdf` — PDF generated and size confirmed
- [ ] `[industry-slug]-[year]-cover.gif` — animated GIF generated
- [ ] `linkedin-post.txt` — caption + pinned comment + publishing notes
- [ ] `[company]-logo.svg` files for all Top 10 companies
- [ ] `[company]-logo.png` files for Top 5 companies (GIF generator)
- [ ] All ECR data verified against realrate-archive.com
- [ ] Industry URL slug verified by fetching realrate.ai/rankings — not guessed
- [ ] Colour scheme is distinct from all previously used industry palettes
- [ ] No emojis on any slide
- [ ] No company names on Slide 6 (Warning Signal)
- [ ] Tagline footer on every slide except Slide 9
