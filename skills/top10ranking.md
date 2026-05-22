# RealRate Top 10 Infographic Generator

Generates a **2160 × 2160 px LinkedIn-ready PNG** from live data at `realrate-archive.com`.
Script: `generate_infographic.py`

---

## Quick start

```bash
python generate_infographic.py <industry_slug>
```

Output: `output/<slug>_<year>.png`

## Available slugs

`air` · `motor` · `software` · `computers` · `finance_services` · `food` · `health_services` ·
`advertising` · `semiconductors` · `programming` · `petrol` · `mining` · `construction` ·
`realestate` · `hotels` · `consulting` · `data_processing` · `brokers` · `savings` ·
`life` · `non_life` · `pharma` · `chemicals` · `state_banks` · `medicinal_products` · `recreation`

## Dependencies

```bash
pip install -r requirements.txt
```

Key: `Pillow>=10.0.0`, `pandas>=2.0.0`, `openpyxl>=3.1.0`, `xlrd>=2.0.1`, `requests>=2.31.0`

---

## Logo fixes

**Manual override** — drop a PNG at `assets/logos/<company_name_lowercase_underscores>.png`
Example: `Visteon CORP` → `assets/logos/visteon_corp.png`

**Domain hint** — add to `_DOMAIN_HINTS` in `generate_infographic.py`, then delete the bad cached file in `assets/logos/`. Use this whenever a logo is wrong or missing.

Current domain overrides:

| Company | Domain |
|---------|--------|
| Bristow Group Inc | `bristowgroup.com` |
| Allegiant Travel CO | `allegiantair.com` |
| Strata Critical Medical Inc | `stratacritical.com` |

---

## LinkedIn post generation

**Always generate both** — whenever you write a LinkedIn post, also run `generate_infographic.py` to produce the matching PNG.

### Rules

- **Title:** `🏆 TOP 10 US [INDUSTRY] COMPANIES RANKING [CURRENT YEAR]`
- **Subtitle:** `RealRate Financial Strength Rankings using Artificial Intelligence`
- **Data:** Fetch `https://realrate-archive.com/us_{slug}/{latest_year}/website-ranking.json` (use `curl -sk`). ECR = `value` × 100, rounded. Latest year = highest number in the directory listing.
- **Company scope:** Never say "US-listed". Use "US Motor companies", "US Software companies", etc.
- **Hook:** Two sharp, industry-specific sentences ending with *"Here is who is built to last."* Fresh every post — never reuse or echo a previous hook. First sentence must be a specific, surprising insight, not a generic opener.
- **Methodology block** (fixed, verbatim every time):
  > At RealRate, we go beyond correlation.
  > Our explainable AI framework reveals not just where each company stands, but why. Giving you a clear view of the underlying drivers of financial resilience, risk exposure, and long-term stability. At the core is Economic Capital Ratio (ECR) — a forward-looking metric that measures how efficiently a company converts its economic value into balance sheet strength, enabling true comparability across size and business models.
- **Market average:** One line after methodology block: `Market average ECR: X%`
- **Top 3:** Medal emoji + rank + name + ECR% + 2–3 tight sentences (strength driver, pp above market, rank trend, punchy "so what").
- **Ranks 4–10:** `#4 Name (X%) | #5 Name (X%) | … | #10 Name (X%)`
- **CTA:** One punchy, industry-specific question. Never reuse. No generic filler.
- **Link:** `🔗 https://realrate.ai/rankings/[industry]/[current year]`
- **Hashtags:** Exactly 8. Always: `#Finance #AI #Investing #RealRate #FinancialHealth #FinancialAnalysis` + 1 industry tag + 1 company name from top 3. Never use: `#Technology #Innovation #StockMarket #USStocks #TopRated #CloudComputing #Cybersecurity`

### Post template

```
🏆 TOP 10 US [INDUSTRY] COMPANIES RANKING [YEAR]
RealRate Financial Strength Rankings using Artificial Intelligence

[Hook — two sentences, industry-specific, ends with "Here is who is built to last."]

At RealRate, we go beyond correlation.
Our explainable AI framework reveals not just where each company stands, but why. Giving you a clear view of the underlying drivers of financial resilience, risk exposure, and long-term stability. At the core is Economic Capital Ratio (ECR) — a forward-looking metric that measures how efficiently a company converts its economic value into balance sheet strength, enabling true comparability across size and business models.

Market average ECR: X%

🥇 #1 [Company] — ECR: [X]%
[2–3 sentences.]

🥈 #2 [Company] — ECR: [X]%
[2–3 sentences.]

🥉 #3 [Company] — ECR: [X]%
[2–3 sentences.]

Also in the top 10:
#4 [Name] ([X]%) | #5 [Name] ([X]%) | #6 [Name] ([X]%) | #7 [Name] ([X]%) | #8 [Name] ([X]%) | #9 [Name] ([X]%) | #10 [Name] ([X]%)

[Fresh CTA]

Full ranking + individual company reports:
🔗 https://realrate.ai/rankings/[industry]/[current year]

#Finance #AI #Investing #RealRate #FinancialHealth #FinancialAnalysis #[IndustryTag] #[CompanyName]
```

### JSON field reference

| Field | Meaning |
|-------|---------|
| `name` | Company name |
| `rank` | Integer rank |
| `value` | ECR as decimal (e.g. `0.85` = 85%) |
| `trend` | Rank change (positive = rising) |
| `top_rated` | Boolean — show TOP RATED badge if true |
| `report_text` | HTML narrative — strip `<br/>` tags before use |
