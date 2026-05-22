# RealRate Infographic Generator — Claude Notes

## Improvements (2026-05-15)

### Archive-first data source (no spreadsheets)
1. **`load_from_archive(slug)`** — fetches live from `https://realrate-archive.com/us_{slug}/{latest_year}/website-ranking.json`. Parses `company_details` array. SSL uses `verify=False` (self-signed cert on archive host).
2. **`_archive_get(url)`** — dedicated HTTP helper for realrate-archive.com that suppresses InsecureRequestWarning and skips cert verification.
3. **CLI: industry slug mode** — `python generate_infographic.py <slug>` auto-detects latest year from archive directory listing, sets title and output filename automatically.
4. **27 industry slugs supported** — see full list in command syntax section.
5. **`prefer_archive=True`** — when loading from JSON, `logo_url_256x256` from the JSON is tried first (before Clearbit/logo.dev/etc.), then falls back to normal pipeline.

### Card design — ECR, TOP RATED, trend
6. **ECR displayed on every card** — muted "ECR" label + bright cyan percentage (44pt extrabold).
7. **Trend arrow inline** — `↑` green / `↓` red / `–` grey, sourced from `trend` field.
8. **TOP RATED badge** — inline pill after trend arrow; 30pt bold, 44px tall, ACCENT→DARK_BLUE gradient fill with ACCENT border. Shown only when `top_rated=True` in JSON.

### Year logic
9. **Title always uses current calendar year** (`datetime.date.today().year`), regardless of which data year was fetched from the archive.

## What this project does

Generates a **2160 × 2160 px LinkedIn-ready PNG infographic** fetched live from `realrate-archive.com`.
Script: `generate_infographic.py`

## Command syntax (preferred — no spreadsheet needed)

```
python generate_infographic.py <industry_slug> [title] [subtitle] [output.png]
```

Automatically fetches the latest year's ranking from realrate-archive.com, shows ECR%, TOP RATED badge (★), and trend arrows (↑↓–) on every card.

## How to generate all industries

```bash
python generate_infographic.py air
python generate_infographic.py motor
python generate_infographic.py software
python generate_infographic.py computers
python generate_infographic.py finance_services
python generate_infographic.py food
python generate_infographic.py health_services
python generate_infographic.py advertising
python generate_infographic.py semiconductors
python generate_infographic.py programming
python generate_infographic.py petrol
```

Output lands in `output/<slug>_<year>.png` automatically.

## Available industry slugs

`air` · `motor` · `software` · `computers` · `finance_services` · `food` · `health_services` ·
`advertising` · `semiconductors` · `programming` · `petrol` · `mining` · `construction` ·
`realestate` · `hotels` · `consulting` · `data_processing` · `brokers` · `savings` ·
`life` · `non_life` · `pharma` · `chemicals` · `state_banks` · `medicinal_products` · `recreation`

## Command syntax (legacy — spreadsheet)

```
python generate_infographic.py <spreadsheet.xlsx> [title] [subtitle] [output.png]
```

Output lands in `output/`.

## Spreadsheets

| File | Title used | Output |
|------|-----------|--------|
| `Spreadsheets/us motor 2025-09 ranking (1).xlsx` | TOP 10 US MOTOR COMPANIES 2025 | `output/motor_2025.png` |
| `Spreadsheets/us software 2025-09 ranking.xlsx` | TOP 10 US SOFTWARE COMPANIES 2025 | `output/software_2025.png` |
| `Spreadsheets/us computers 2026-04 ranking.xlsx` | TOP 10 US COMPUTER COMPANIES 2026 | `output/computers_2026.png` |
| `Spreadsheets/us finance services 2026-04 ranking.xlsx` | TOP 10 US FINANCE SERVICES COMPANIES 2026 | `output/finance_services_2026.png` |
| `Spreadsheets/us food 2026-04 ranking.xlsx` | TOP 10 US FOOD COMPANIES 2026 | `output/food_2026.png` |
| `Spreadsheets/us air 2026-04 ranking.xlsx` | TOP 10 US AIR COMPANIES 2026 | `output/air_2026.png` |

## Dependencies

Install with:
```bash
pip install -r requirements.txt
```

Key packages: `Pillow>=10.0.0`, `pandas>=2.0.0`, `openpyxl>=3.1.0`, `xlrd>=2.0.1`, `requests>=2.31.0`

- `.xlsx` / `.xlsm` → `engine="openpyxl"`
- `.xls` → `engine="xlrd"` (different engine — do not mix up)

## Manual logo override

If a logo can't be fetched automatically, drop a PNG at:
```
assets/logos/<company_name_lowercase_underscores>.png
```
Example: `Visteon CORP` → `assets/logos/visteon_corp.png`

## Domain hints

When a company gets the wrong logo or no logo, add its domain to `_DOMAIN_HINTS` in `generate_infographic.py` and delete the bad cached file in `assets/logos/`. Domain hints bypass the Clearbit autocomplete lookup and force all icon sources to use the correct domain.

**Always add a domain hint when a logo fails or is wrong.** Delete the bad cache first so the pipeline re-fetches cleanly.

Current overrides beyond the defaults:

| Company | Domain |
|---------|--------|
| Bristow Group Inc | `bristowgroup.com` |
| Allegiant Travel CO | `allegiantair.com` |
| Strata Critical Medical Inc | `stratacritical.com` |

## Improvements (2026-04-30)

### Visual design — industry backgrounds & icons
1. **Three-tone blue palettes** — `_draw_industry_background` now uses a per-industry triplet `(a1, a2, a3)` instead of a single accent colour. Minor grid lines use the deep tone (`a2`), major grid and corner brackets use the primary (`a1`), reference lines use the highlight (`a3`). All industry-specific geometry distributes colour across the three tones for visual depth.
2. **All accents now strictly blue-tone** — finance (was green), food (was orange), energy (was orange), computers (was purple) all corrected to blue variants. Per-industry palette:
   - motor: `(0,200,255)` / `(0,100,200)` / `(150,230,255)`
   - software: `(60,130,255)` / `(0,60,180)` / `(115,185,255)`
   - computers: `(110,160,255)` / `(55,100,220)` / `(185,215,255)`
   - finance: `(0,130,200)` / `(0,55,150)` / `(85,190,240)`
   - health: `(0,205,225)` / `(0,120,185)` / `(145,235,250)`
   - energy: `(30,90,210)` / `(0,35,155)` / `(85,155,255)`
   - food: `(80,190,255)` / `(25,115,210)` / `(165,225,255)`
   - air: `(0,170,255)` / `(0,75,190)` / `(125,215,255)`
3. **Air industry added** — new `"air"` industry type throughout:
   - `_INDUSTRY_KEYWORDS` — keywords: air, airline, aviation, airways, aircraft, airport, flight, aerospace, jetblue, southwest, delta, frontier, allegiant, bristow, saker, wheels up, sun country, united airlines, american airlines, spirit, alaska, hawaiian.
   - `_ibg` base colour: `(3, 8, 30)` deep sky navy.
   - `_draw_industry_background` — aviation theme: Earth-curvature horizon arcs (3 layered), dashed flight-level altitude bands (6 rows), 5 Bézier contrail paths, compass/heading rose watermark (lower-right), scattered aircraft-position dots.
   - `_draw_industry_icon` — top-down airplane silhouette: tapered fuselage (nose up), swept-back main wings, horizontal tail stabilisers. Multi-pass neon glow same as all other icons.
4. **Industry icon correctness** — icons are always drawn for the detected industry. Air uses airplane, not the generic bar chart or health ECG.

### US Air ranking added
5. **`Spreadsheets/us air 2026-04 ranking.xlsx`** — built from `https://realrate-archive.com/us_air/2025/website-ranking.json`; includes Rank, Company, CIK, currentReport columns for archive logo resolution.
6. **`output/air_2026.png`** and **`output/linkedin_air_2026.txt`** — TOP 10 US AIR COMPANIES 2026, market average ECR 69%.

| File | Title used | Output |
|------|-----------|--------|
| `Spreadsheets/us air 2026-04 ranking.xlsx` | TOP 10 US AIR COMPANIES 2026 | `output/air_2026.png` |

### Command
```bash
python generate_infographic.py "Spreadsheets/us air 2026-04 ranking.xlsx" "TOP 10 US AIR COMPANIES 2026" "RealRate Financial Health Ranking based on Economic Capital Ratio" "output/air_2026.png"
```

## Improvements (2026-04-27)

### Logo box rendering
1. **Smooth logo box corners** — `paste_logo_container` now uses a single supersampled AA mask (4× resolution, downscaled with LANCZOS) shared by both the white background and the logo clip. Previously the background was drawn with PIL's built-in `rounded_rectangle` (no AA), leaving pixel-stepped corners visible around the border. Both background and logo are now clipped to the same smooth mask.
2. **Logo priority reversed** — RealRate archive moved from first-priority to last-resort fallback. Live sources (Clearbit → logo.dev → Brandfetch → Uplead → favicon → website → Wikipedia → Wikimedia) are tried first; archive is used only if all fail.
3. **Federated Hermes domain hint added** — `"federated hermes": "federatedhermes.com"` added to `_DOMAIN_HINTS` to prevent the wrong Hermes Investment logo being fetched.

### LinkedIn post format
4. **Methodology block replaced** — old four-line verbatim block removed. Now uses a fixed two-paragraph block starting *"At RealRate, we go beyond correlation."*
5. **Hook rule updated** — two sentences required; must be fresh and industry-specific every post, never reused.
6. **CTA rule updated** — engagement CTA must be unique per post; no repeated phrasing.
7. **Hashtags reduced to 8** — down from 10–12. Fixed set: `#Finance #AI #Investing #RealRate #FinancialHealth #FinancialAnalysis` + one industry tag + one company name.
8. **Finance services post added** — `output/linkedin_finance_services_2026.txt` and `output/finance_services_2026.png`.

## Design & code improvements (2026-04-23)

### Visual design
1. **Header height** increased 380 → 440 px; `HEADER_GAP` 80 → 70 px.
2. **Title** — extrabold, allows up to 2 lines so font stays large (starts at 128 pt, shrinks by 4 until ≤ 2 lines fit). Each line individually centred in the text zone.
3. **Subtitle** — medium weight, 52 pt, NEON_CYAN, sits 68 px below the title block.
4. **Title centering fixed** — `title_cx` was centred on the full 2040 px header width; now correctly centred on the text zone between the RealRate logo and the industry icon.
5. **Hex grid upgraded** — `_draw_hex_grid` now records all vertex positions and draws a glowing dot at every intersection (dot alpha = 5× edge alpha). Edge opacity bumped from 7–8 → 18 across all industry grids.
6. **Dot grid added** — replaces the invisible 1 px crosshatch lines. 2 px dots every 108 px + 4 px accent dots every 324 px, both in the industry's signature colour.
7. **Random background** — all fixed `random.seed(N)` calls replaced with `random.seed()` so the background elements (streaks, nodes, circuit traces, etc.) are unique on every run.

### Bugs fixed
1. **`_download_ttf` woff2 bug** — modern browser UA caused Google Fonts to return woff2 URLs; PIL can't load woff2. Fixed by using a legacy IE UA for the CSS fetch so Google returns TTF. Regex tightened to `\.ttf` only.
2. **`_try_website_logo` data: URIs** — inline `data:image/…` base64 URIs were being passed to `_get()` as HTTP URLs. Added early `continue` for `data:` URLs.
3. **`word_wrap` width measurement** — used `bb[2]` (right edge) instead of `bb[2] - bb[0]` (actual rendered width), causing text to wrap a few pixels too early.
4. **Dead functions removed** — `_glass_card` and `_draw_3d_sphere` were defined but never called; both deleted.

## Improvements (2026-04-21)

1. **RealRate archive as first-priority logo source** — `_try_realrate_archive` added; tries `https://www.realrate-archive.com/[industry]/logos/[CIK]_256x256.png` before any third-party service. Most reliable source since it holds the verified logo for every ranked company.
2. **CIK + currentReport read from spreadsheet** — `load_spreadsheet` now reads the `CIK` and `currentReport` columns and derives `archive_logo_url` automatically (regex extracts the `[host]/[industry]/` base from the report URL, then appends `logos/[CIK]_256x256.png`).
3. **`get_company_logo` signature extended** — accepts `archive_logo_url=` param; archive is tried immediately after the cache check, before domain resolution and all other sources.
4. **IBM logo fixed** — third-party favicon services were returning a wrong bee icon for `ibm.com`; correct logo now sourced from RealRate archive (`assets/logos/international_business_machines.png`).
5. **Arista Networks logo fixed** — Uplead returned a 33px-tall strip (below 64px threshold); correct 256×256 logo now sourced from RealRate archive (`assets/logos/arista_networks_inc.png`).
6. **Wetouch Technology logo added** — not available on any third-party service; logo sourced from RealRate archive (`assets/logos/wetouch_technology_inc.png`).

## Bugs fixed & improvements (2026-03-24 session 2)

1. **`_try_uplead` placeholder rejection** — added solid-colour + min-64px check; previously let bad Uplead placeholders (e.g. Ameritek Ventures 4.4 KB blank) slip through and get cached.
2. **`_try_brandfetch` placeholder rejection** — same solid-colour + min-64px guard added (was missing).
3. **`_CACHE_REGEN_BELOW` lowered 180 → 64** — valid 96×96 favicons were being thrown away and re-fetched in an infinite loop because they fell below the old threshold.
4. **Ameritek Ventures icon** — manually fetched correct 96×96 icon from `ameritekventures.com/wp-content/uploads/2020/11/favicon_gLV_icon.ico` and saved to `assets/logos/ameritek_ventures_inc.png`.
5. **Logo pipeline reordered** — new priority: (1) icon APIs → (2) favicon → (3) website → (4) Wikipedia → (5) Wikimedia → (6) fallback vertical/horizontal from Wikipedia/Wikimedia with extra suffix queries. Website moved up before Wikipedia/Wikimedia so the direct source is tried first.
6. **Company-name verification in `_search_domain`** — Clearbit autocomplete results are now checked for ≥50 % key-word overlap with the query before the domain is accepted, preventing wrong-company logos.
7. **Wikipedia article title verification** — `_try_wikipedia_logo` now verifies the top search result title matches the company before using it.
8. **`_try_wikimedia_logo` file-title guard** — at least one key company-name word must appear in the Wikimedia file title before the image is downloaded.

## Improvements (2026-03-24)

1. **Parallel logo fetching** — `ThreadPoolExecutor(max_workers=4)` in `main()` reduces fetch time ~4×. All status prints go through `_log()` (thread-safe).
2. **`_get` retry** — retries once on `Timeout`; breaks immediately on 4xx so bad domains don't double-hit.
3. **Placeholder rejection** — `_try_clearbit_logo` and `_try_logodev` now reject sub-64px images and solid-colour placeholder returns.
4. **Protocol-relative URLs** — `_try_website_logo` correctly handles `//cdn.example.com/logo.png` by prepending only the scheme.
5. **`http` fallback restored** — removed unconditional `break` in `_try_website_logo` so the `http` scheme is tried when `https` yields no usable logo.
6. **Wikimedia name guard** — `_try_wikimedia_logo` now verifies at least one key company-name word appears in each candidate file title before downloading it.
7. **Numpy gradient** — `_draw_gradient_rect` replaces a per-column PIL draw loop with a vectorised numpy broadcast (~50–100× faster on 2160 px canvases).
8. **Named thresholds** — `_CACHE_REGEN_BELOW = 180` and `_ICON_EARLY_EXIT = 256` replace scattered magic numbers in `get_company_logo`.
9. **Header-row scan** — `load_spreadsheet` now scans rows 0–5 for the real header when row 0 looks like metadata.
10. **Smarter name-column detection** — falls back to any object column whose values average 1–8 words and are <30% numeric, avoiding date/memo columns.
11. **Dead `mkdir` removed** — removed redundant `ASSETS_DIR.mkdir` inside `get_realrate_logo` loop body.

## LinkedIn Description Generation

### What it does
Generates LinkedIn post `.txt` files for each industry ranking, saved to `output/`.

**Always generate both** — whenever a LinkedIn post is generated for any industry, also run `generate_infographic.py` to produce the matching PNG in the same response. Never deliver just the post without the image.

### Command
Run manually — no CLI flag. Write the files directly using the rules below.

### Rules
- **Title format:** `🏆 TOP 10 US [INDUSTRY] COMPANIES RANKING [CURRENT YEAR]` — trophy emoji, always current calendar year
- **Subtitle:** Fixed, always verbatim from realrate.ai/rankings: `RealRate Financial Strength Rankings using Artificial Intelligence`
- **Data source:** First fetch `https://realrate-archive.com/[industry]/` to find the latest year available (highest number in the directory listing), then fetch `https://realrate-archive.com/[industry]/[latest_year]/website-ranking.json` (use `curl -sk` to bypass SSL). ECR = `value` field × 100, rounded. Strength/weakness = `report_text` field (strip HTML tags). Use the latest year's ranking order for company listings.
- **Company scope wording:** Never say "US-listed". Use the industry-specific label: "US Motor companies", "US Software companies", etc.
- **Hook line:** Two sharp industry-specific sentences. End with: *"Here is who is built to last."* **Always write a fresh hook — never reuse or closely echo a previous post's hook.** The first sentence should be a specific, surprising insight about the industry's financial dynamics, not a generic opener.
- **Methodology block:** Fixed — use exactly this text every time:
  1. (blank line after hook)
  2. *"At RealRate, we go beyond correlation."*
  3. *"Our explainable AI framework reveals not just where each company stands, but why. Giving you a clear view of the underlying drivers of financial resilience, risk exposure, and long-term stability. At the core is Economic Capital Ratio (ECR) — a forward-looking metric that measures how efficiently a company converts its economic value into balance sheet strength, enabling true comparability across size and business models."*
- **Market average:** After the methodology block (before the top-3 entries), add one line: `Market average ECR: X%`. Derive X from the `value` field of the market-average entry in the JSON, or reverse-calculate from the per-company "X points above the market average" text (ECR − pp above = market avg). Round to the nearest whole percent.
- **Per-company entry (top 3):** rank + medal emoji (🥇🥈🥉), name, ECR%, 2–3 tight sentences — key strength driver with pp above market, rank trend if notable, one punchy "so what" insight.
- **Ranks 4–10:** Compact single line: `#4 Name (ECR%) | #5 Name (ECR%) | …`
- **Footer:** Engagement CTA then link. **The CTA must be different every post — never reuse the same line.** Write one punchy question or provocation that invites a reaction specific to this industry or ranking. No generic "drop a comment" filler. Examples of the tone (do not copy verbatim): *"Which name here would you have least expected at the top?"* / *"Does this ranking match what the market is pricing in?"* / *"Which of these would you hold through a downturn?"*
  ```
  [Fresh CTA — unique each post]

  Full ranking + individual company reports:
  🔗 https://realrate.ai/rankings/[industry]/[current year]
  ```
- **No** `realrate-archive.com` links anywhere in the output
- **Hashtags:** Exactly 8 tags. Always include: `#Finance` `#AI` `#Investing` `#RealRate` `#FinancialHealth` `#FinancialAnalysis`. Add one industry-specific tag (e.g. `#Computers`, `#FinanceServices`) and 1 recognisable company name from the top 3. Never use: `#Technology` `#Innovation` `#StockMarket` `#USStocks` `#TopRated` `#CloudComputing` `#Cybersecurity`

### Post template (canonical format)

```
🏆 TOP 10 US [INDUSTRY] COMPANIES RANKING [YEAR]
RealRate Financial Strength Rankings using Artificial Intelligence

[Hook — two sharp, industry-specific sentences, fresh each post. End with: "Here is who is built to last."]

At RealRate, we go beyond correlation.
Our explainable AI framework reveals not just where each company stands, but why. Giving you a clear view of the underlying drivers of financial resilience, risk exposure, and long-term stability. At the core is Economic Capital Ratio (ECR) — a forward-looking metric that measures how efficiently a company converts its economic value into balance sheet strength, enabling true comparability across size and business models.

Market average ECR: X%

🥇 #1 [Company] — ECR: [X]%
[2–3 tight sentences: key strength driver with pp above market, rank trend, punchy "so what".]

🥈 #2 [Company] — ECR: [X]%
[2–3 tight sentences.]

🥉 #3 [Company] — ECR: [X]%
[2–3 tight sentences.]

Also in the top 10:
#4 [Name] ([X]%) | #5 [Name] ([X]%) | #6 [Name] ([X]%) | #7 [Name] ([X]%) | #8 [Name] ([X]%) | #9 [Name] ([X]%) | #10 [Name] ([X]%)

[Fresh CTA — unique each post, never reused]

Full ranking + individual company reports:
🔗 https://realrate.ai/rankings/[industry]/[current year]

#Technology #Finance #AI #[IndustrySpecific] #Investing #RealRate #FinancialHealth #Innovation #[BroadIndustryTag] #FinancialAnalysis #[Company1] #[Company2]
```

### Output files
| Industry | File |
|----------|------|
| Motor | `output/linkedin_motor_YYYY.txt` |
| Software | `output/linkedin_software_YYYY.txt` |
| Computers | `output/linkedin_computers_YYYY.txt` |
| Finance Services | `output/linkedin_finance_services_YYYY.txt` |
| Food | `output/linkedin_food_YYYY.txt` |

### JSON field reference
- `name` — company name
- `rank` — integer rank
- `value` — ECR as decimal (e.g. 2.05 = 205%)
- `trend` — rank change (positive = rising)
- `report_text` — HTML strength/weakness narrative; strip `<br/>` tags before use
- `report_url` — PDF URL (used for archive only, not included in LinkedIn posts)

---

## Bugs fixed (2026-03-23)

1. **Dead variable** `query` in `_try_wikimedia_logo` — assigned but never used; removed.
2. **Redundant inner import** `from PIL import ImageFilter as _IF` inside `paste_logo_container` — removed, now uses module-level `ImageFilter`.
3. **Dead no-op arc** `gld.arc(..., fill=None)` in globe icon drawing — removed.
4. **`.xls` engine mismatch** — `openpyxl` doesn't support `.xls`; split into separate `xlrd` branch and added `xlrd>=2.0.1` to `requirements.txt`.
5. **Dead function** `smooth_circle` — defined but never called; removed.
6. **Redundant assignment** `domain = hint_domain or None` → simplified to `domain = hint_domain`.
7. **Extra blank lines** between top-level definitions trimmed to PEP 8 standard (2 lines).
