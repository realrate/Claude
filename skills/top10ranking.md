# RealRate Top 10 Infographic Generator

Generates a **1200 × 1500 px portrait LinkedIn infographic** from live data at `realrate-archive.com`, plus a matching LinkedIn caption `.txt`.

Script: `generate_infographic.py`

---

## Quick start

```bash
python generate_infographic.py <industry_slug>
```

Output: `output/<slug>_<year>.png` and `output/linkedin_<slug>_<year>.txt`

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

## Infographic design

### Canvas
- **Size**: 1200 × 1500 px (portrait, LinkedIn-optimised)
- **Layout**: 2-column × 5-row ranking cards, header, footer

### Per-industry color rebrand
Every industry gets a distinct background, accent color, card gradient, and bold background pattern. The accent (`I_NEON`) drives all colored elements: borders, glow, icon, subtitle, ECR values, badges, footer.

| Industry | Accent | Background | Pattern |
|---|---|---|---|
| Motor | Racing blue `(30,160,255)` | Carbon black-blue | Speed streaks, speedometer arc |
| Air | Sky blue `(55,210,255)` | Midnight sky | Contrails, horizon arcs, compass rose |
| Software | Matrix green `(0,255,120)` | Dark matrix | Network graph, code rain |
| Computers | Electric indigo `(80,160,255)` | Dark indigo | PCB traces, chip diagram |
| Finance | Gold `(240,168,32)` | Dark amber | Candlestick charts, trend lines |
| Health/Pharma | Medical teal `(0,230,185)` | Dark teal | ECG line, molecular lattice |
| Energy/Petrol | Flame orange `(255,120,0)` | Oil black | Radial streaks, lightning bolt |
| Food | Leaf green `(95,220,45)` | Dark forest | Organic waves, honeycomb |

Background patterns use **bold alpha** (~3× original) so they're clearly visible.

### Header
- Left: RealRate logo with neon glow halo
- Center: Title (extrabold white) + subtitle (`I_NEON` accent)
- Right: Industry icon (142 px, `I_NEON` accent, with glow halo)
  - **Motor icon**: F1 steering wheel — double ring, thick spokes, grip notches, filled hub

### Ranking cards
- **Top 3**: deep industry-colored gradient + neon accent border + left glow bar
- **Top-rated rank 4+**: dark glassmorphism + multi-layer neon glow border
- **Standard**: dark glassmorphism + dim border
- Each card: rank badge (accent fill), company name, `ECR X%` (bright label + white value), trend arrow ↑↓–, `★ TOP RATED` pill when applicable

### Color variables in `generate()`
| Variable | Purpose |
|---|---|
| `I_NEON` | Primary accent — borders, icon, subtitle, all glow elements |
| `I_NEON_BRIGHT` | Icon & subtitle bright rendering (= `I_NEON`) |
| `I_NEON_HI` | ECR % value (`I_NEON + 85` per channel) |
| `I_MUTED` | ECR label `(210,225,238,240)` — neutral bright white |
| `I_ACCENT` | Rank badge fill, TOP RATED pill gradient |
| `I_DIM` | Standard card border |
| `I_DARK` | Badge outline / pill gradient end |

---

## LinkedIn caption (auto-generated)

Written to `output/linkedin_<slug>_<year>.txt` alongside every PNG.

### Format
```
🏆 TOP 10 US [INDUSTRY] COMPANIES [YEAR]
RealRate Financial Strength Rankings using Artificial Intelligence

[2-sentence industry hook]

At RealRate, our explainable AI framework quantifies financial resilience through ECR...

Market average ECR: X%

🥇 #1 Company — ECR: X%  TOP RATED
[2-sentence description: ECR vs average + trend]

🥈 #2 Company — ECR: X%  TOP RATED
[2-sentence description]

🥉 #3 Company — ECR: X%  TOP RATED
[2-sentence description]

#4 Company — ECR: X%  TOP RATED
[1-sentence description: ECR vs average only]

Also in the ranking:
#N Company (X%) | ...

[Engagement question]

Full ranking + individual company reports:
🔗 https://realrate.ai/rankings/us_[industry]/[year]

#Finance #AI #Investing #RealRate ... [industry hashtags]
```

### Description rules
- **Top 3 (rank 1–3)**: 2 sentences — ECR position vs sector average + trend
- **Top-rated rank 4+**: 1 sentence — ECR position only
- **Non-top-rated**: no description, listed under "Also in the ranking"
- No `★` icon in caption labels (only on the infographic badge)

### Year logic
- **Title + filename + URL**: `datetime.date.today().year` (current calendar year)
- **Archive fetch**: uses latest year from the archive directory listing

---

## Logo fixes

**Manual override** — drop a PNG at `assets/logos/<company_name_lowercase_underscores>.png`
Example: `Visteon CORP` → `assets/logos/visteon_corp.png`

**Domain hint** — add to `_DOMAIN_HINTS` in `generate_infographic.py`, then delete the cached file in `assets/logos/`.

**White/light logo detection** — `_logo_is_light()` auto-detects logos where ≥60% of visible pixels have brightness >200 and renders them on a near-black `(18,18,18)` box instead of white.

Current domain overrides:

| Company | Domain |
|---------|--------|
| Bristow Group Inc | `bristowgroup.com` |
| Allegiant Travel CO | `allegiantair.com` |
| Strata Critical Medical Inc | `stratacritical.com` |
| Abrdn (all ETF trusts) | `abrdn.com` |

---

## JSON field reference

| Field | Meaning |
|-------|---------|
| `name` | Company name |
| `rank` | Integer rank |
| `value` | ECR as decimal (e.g. `1.88` = 188%) |
| `trend` | Rank change (positive = rising) |
| `top_rated` | Boolean — show TOP RATED badge if true |
| `logo_url_256x256` | Direct archive logo URL (tried first in logo pipeline) |
