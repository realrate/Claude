# Mind Map Claude — Generator Guide

## Standing Rule

**`gen_mindmap.py` is the universal generator — all companies are CLI arguments.** To add a new company, add an `elif COMPANY == "companyname":` block inside `gen_mindmap.py`. Never create a new separate script.

---

## Scripts & Companies

| Script | Companies |
|---|---|
| `gen_mindmap.py` | trilinc · strata · hp · angi · nvidia |
| `gen_mindmap_apple.py` | apple (standalone) |

**Archive slugs per company:**

| Company | Archive path | Rankings slug |
|---|---|---|
| trilinc | `us_finance_services/2025/` | `us_finance_services/2026` |
| strata | `us_air/2025/` | `us_air/2026` |
| hp | `us_computers/2025/` | `us_computers/2025` |
| angi | `us_advertising/2025/` | `us_advertising/2026` |
| nvidia | `us_semiconductors/2025/` | `us_semiconductors/2026` |
| apple | `us_computers/2025/` | `us_computers/2025` |

---

## How to Run

```
python gen_mindmap.py              # TriLinc Global (default)
python gen_mindmap.py trilinc
python gen_mindmap.py strata
python gen_mindmap.py hp
python gen_mindmap.py angi
python gen_mindmap.py nvidia
python gen_mindmap_apple.py
```

**Outputs** — each company writes to its own subfolder (except trilinc, which writes to root):

| File | Size | Purpose |
|---|---|---|
| `[company]-mindmap.png` | 1920×1080 | Full-res original |
| `[company]-mindmap-linkedin.png` | 1200×628 | LinkedIn post image |
| `[company]-linkedin-post.txt` | — | Caption + publishing notes |

Subfolders: `Strata Critical Medical/` · `HP Inc/` · `Angi Inc/` · `Nvidia Corp/`

**Dependencies:** `requests`, `playwright`, `Pillow`
Install Playwright browser once: `playwright install chromium`

---

## ECR & Financial Data — Always Fetch From Archive

**Rule: never hardcode or recall ECR values from memory. Always fetch live from the archive first.**

**Apple** — `https://realrate-archive.com/us_computers/2025/website-ranking.json`
- ECR Score: 430% · Industry Rank: #1 of 17 · Status: Top-Rated
- Revenue FY2025: $416B (+6% YoY) · Net Income: $112B · Operating margin: 32%
- Cash & Securities: $162B · R&D: $34.6B · Market cap: $3.0 Trillion

**TriLinc Global** — `https://realrate-archive.com/us_finance_services/2025/website-ranking.json`
- ECR Score: 124% · Industry Rank: #1 of 4 · Status: Top-Rated
- Total Assets: $282.8M · Stockholders' Equity: $272.6M · Liabilities: $10.2M
- Equity-to-Assets ratio: 96.4% · Net Income: –$8.5M
- ECR drivers: Equity +57pp · Revenue –17pp · 46pp above industry avg (78%)

**HP Inc.** — `https://realrate-archive.com/us_computers/2025/website-ranking.json`
- ECR Score: 258% · Industry Rank: #9 of 17 · Status: Rated
- Revenue FY2024: $53.6B · Net Income: $2.8B · Operating margin: 7.1%
- Total Assets: $39.9B · Stockholders' Equity: –$1.3B (deficit) · Liabilities: $41.2B
- Cash: $3.25B · Long-term Debt: $8.3B · R&D: $1.64B
- Segments: Personal Systems ~$34.4B (64%) · Printing ~$19.1B (36%)
- CEO: Enrique Lores (since Nov 2019) · Est. 1939 · HPQ · Logo CIK: 0000047217

**Strata Critical Medical** — `https://realrate-archive.com/us_air/2025/website-ranking.json`
- ECR Score: 123% · Industry Rank: #1 of 4 · Status: Top-Rated
- Total Assets: $325.5M · Stockholders' Equity: $279.1M · Liabilities: $46.4M
- Revenue: $197.1M (FY2025) · Net Income: +$41.3M · First profitable year
- ECR drivers: Operating Expenses +46pp · Other Expenses –81pp · 54pp above industry avg (69%)

**Angi Inc.** — `https://realrate-archive.com/us_advertising/2025/website-ranking.json`
- ECR Score: 157% · Industry Rank: #1 of 4 · Status: Top-Rated
- Total Assets: $1.68B · Stockholders' Equity: $1.46B · Liabilities: $222.4M
- Revenue: $1.03B · Net Income: +$43.8M · Equity-to-Assets ratio: 86.7%
- ECR drivers: Stockholders' Equity +68pp · Marketing & Selling Expenses –22pp · 78pp above industry avg (80%)
- CEO: Jeff Kip · NASDAQ: ANGI · Est. 1995 · Denver, CO · IAC subsidiary
- Brands: Angi (formerly Angie's List) · HomeAdvisor · Handy · ~4,500 employees

**Nvidia Corp.** — `https://realrate-archive.com/us_semiconductors/2025/website-ranking.json`
- ECR Score: 351% · Industry Rank: #8 of 44 · Status: Top-Rated
- Revenue FY2025: $130.5B (+114% YoY) · Net Income: $72.9B · R&D: $12.9B
- Total Assets: $111.6B · Stockholders' Equity: $79.3B · Liabilities: $32.3B
- ECR drivers: Net Income +94pp · Stockholders' Equity –56pp · 98pp above industry avg (253%)
- CEO: Jensen Huang (co-founder, since 1993) · NASDAQ: NVDA · Est. 1993 · Santa Clara, CA
- Segments: Data Center ~$115.2B (88%) · Gaming ~$11.4B (9%) · Other ~$3.9B (3%)
- ECR trajectory: 242→254→223→299→351% (2021–2025) · CIK: 0001045810

**Archive is internal only — never share the URL publicly.**

---

## Shared Canvas & Layout

All `gen_mindmap.py` companies use the same layout constants:

```
Canvas:       W=1920, H=1080
Hub centre:   HCX=940, HCY=494  (rect HX=700, HY=348, HW=480, HH=292)
Hub radius:   HR=200
Render:       Playwright device_scale_factor=2 → 3840×2160 → Pillow LANCZOS → 1920×1080
LinkedIn crop: crop_y=8 (top-biased)
```

**Branch circle positions (all companies):**

| Role | Colour | cx, cy, r |
|---|---|---|
| B1 — CEO / Leader | AMBER #F59E0B | 640, 300, 82 |
| B7 — History / Journey | PURP #A78BFA | 600, 600, 68 |
| B2 — Company Overview | CYAN #3DBACD | 940, 130, 64 |
| B3 — Industry Position | LIME #86EF60 | 1400, 200, 64 |
| B4 — Financial Health | SKY #60A5FA | 1480, 430, 62 |
| B5 — Segments / Strategy | EMER #34D399 | 1390, 720, 62 |
| B6 — Highlights / Focus | ORAN #FB923C | 920, 820, 62 |

**Decorative circle positions (all companies):**

| Role | cx, cy, r |
|---|---|
| D1 — bottom-left | 700, 820, 44 |
| D2 — bottom-right | 1155, 770, 44 |
| D3 — mid-left | 220, 623, 44 |
| D4 — top-right | 1170, 185, 44 |

**Accent colour per company:** EMER (trilinc) · SKY (strata) · CYAN (hp) · PINK (angi) · LIME (nvidia)

**Image caching:** all fetched images are base64-cached in `img_cache/`. Delete a `.cache` file to force re-fetch.

---

## LinkedIn Posts

Generated automatically on every run — paste-ready, no edits needed.

Rules:
- Never tag companies in the caption — always in first pinned comment
- Max 5 hashtags, always include `#RealRate`
- Every post must include: `Powered by RealRate: Using Explainable Financial AI`
- Link only to `realrate.ai/rankings/[slug]/[year]` — never to the archive
- Ranking URL is fetched live on every run; falls back to the slug in `_ranking_cfg`

To update caption copy, edit the `CAPTION` f-string in the relevant `elif COMPANY == "..."` block near the bottom of `gen_mindmap.py`.

---

## Key Links

| | URL |
|---|---|
| Archive (internal only) | https://realrate-archive.com |
| Rankings | https://realrate.ai/rankings |
| Methodology | https://realrate.ai/methodology |
