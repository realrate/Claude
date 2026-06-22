# RealRate Ranking Report Generator

## Project Overview
This project generates illustrated, journalistic rating articles for various industries using RealRate data from https://www.realrate-archive.com/

## Project Layout

```
Ranking Reports claude/               ← project root
├── rr_shared.py                      ← shared utilities (colours, charts, DOCX, PIL)
├── convert_svgs.py                   ← batch SVG→PNG for all industries
├── CLAUDE.md
├── RealRate Logos/
└── report (2026)/                    ← all output; one folder per industry
    ├── US Food/
    │   ├── generate_report.py        ← run this to regenerate the report
    │   └── charts/
    ├── US Air/
    │   ├── generate_report.py
    │   └── charts/
    └── US {Industry}/                ← same structure for every industry
        ├── generate_report.py
        └── charts/
```

Each `generate_report.py` uses `sys.path.insert` to find `rr_shared.py` at the project root.
Run from **any directory**: `python "report (2026)/US Brokers/generate_report.py"`

### Path bootstrap for every new industry script

```python
import os, sys

# Script lives in report (2026)/{Industry Name}/ — project root is 3 levels up
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from rr_shared import ...

ROOT         = _ROOT
REPORT_DIR   = os.path.join(ROOT, "report (2026)")
INDUSTRY_DIR = os.path.dirname(os.path.abspath(__file__))   # this script's own folder
CHART_DIR    = os.path.join(INDUSTRY_DIR, "charts")
LOGOS_DIR    = os.path.join(ROOT, "RealRate Logos")
os.makedirs(CHART_DIR, exist_ok=True)
```

## How to Use
Run Claude Code in this directory and specify:
- `[ADD_INDUSTRY]` — the industry subdirectory slug (e.g., `motors`, `computers`, `software`, `food`, `petroleum`, `advertising`)
- `[ADD COUNTRY AND INDUSTRY]` — plain-English name for the intro paragraph (e.g., "US Motor Industry")

Claude will auto-resolve:
- `CURRENT_YEAR` → the current calendar year (today's date is available in context)
- `PREVIOUS_YEAR` → CURRENT_YEAR − 1 (balance sheet year used in the archive URLs)

## Article Generation Prompt

You are an experienced rating journalist, creating a [CURRENT_YEAR] rating article. You are being provided with the RealRate rating results on [CURRENT_YEAR] for the marketing year [CURRENT_YEAR].

**Background:**

Note that we use the "marketing year" ([CURRENT_YEAR]), while in our technical base data in https://realrate-archive.com/, we use the "balance sheet year" ([PREVIOUS_YEAR]). The reason is that the delay in publishing the annual reports is based on the balance sheet years. They are related like this: marketing year = balance sheet year + 1.

Never use any other websites, e.g., realrate.ai and other. Only fetch this website to get data: https://www.realrate-archive.com/

The ECR (Economic Capital Ratio) is the "final" variable in which we are interested. All "effects" are measured with respect to that final variable. The ECR is the economic value of the company divided by the sum of its assets in order to make big and small companies comparable.

---

### Data Sources

**Technical base data with sub-links:**

General archive: https://realrate-archive.com/

For this report, limit yourself to the following directory and its subdirectories:
`https://www.realrate-archive.com/[ADD_INDUSTRY]/`

**Subdirectory in HTML format:**
`https://www.realrate-archive.com/[ADD_INDUSTRY]/qa/`
Since this is in HTML, you will struggle to interpret the table correctly. Therefore, in case of any inconsistencies, use the following JSON data and not this HTML data.

**Subdirectory in JSON format** (balance sheet year [PREVIOUS_YEAR]):
`https://www.realrate-archive.com/[ADD_INDUSTRY]/[PREVIOUS_YEAR]/website-ranking.json`
Within that file, there is details about companies in `company_details` and the single companies can be differentiated by `company_id` or by `name`.

**Subdirectories in JSON format for earlier years** (replace YYYY with the corresponding balance sheet year):
`https://www.realrate-archive.com/[ADD_INDUSTRY]/YYYY/website-ranking.json`

There are also other industries available via INDUSTRY, but ignore those:
`https://www.realrate-archive.com/INDUSTRY/YYYY/website-ranking.json`

> When it comes to ECR and ranking position, only use numbers from https://realrate-archive.com/  
> Data from blog posts or press releases will be outdated since we are updating our rating model and recomputing the past.

Whenever using data from the HTML directory, first double-check your numbers by cross-checking with the JSON directories.

---

### Main Tasks

**1. HTML Ranking Extraction**
From `https://www.realrate-archive.com/[ADD_INDUSTRY]/qa/`:
- Extract the ranking "Ranks across the years" with company names, ranking positions, ECR values ("val"), and rank changes.
- Create an accurate graph for the first three companies, with names, ECR, and rank.
- Report if you were able to cross-check these HTML data with the JSON data.

**2. JSON Top-3 Graph**
From `https://www.realrate-archive.com/[ADD_INDUSTRY]/[PREVIOUS_YEAR]/website-ranking.json`:
- Output a graph with the top 3 companies for the most recent year, including name, ECR, and rank.
- Confirm that the data displayed is from the JSON source only.
- Compare information from Task 1 and Task 2 and check if they are consistent.

**3. Multi-Year Evolution**
- Gather data for all available years.
- For the top 3 companies, show their evolution over time with respect to rank and ECR.

**4. Company Details**
- Extract [PREVIOUS_YEAR] `company_details` in the JSON.
- Check the important information for the top 3 companies and add a short description.

**5. Causal Graphs**
- From the JSON, extract and open [PREVIOUS_YEAR] `graph_url` for the top 3 companies.
- Interpret the graphs semantically; if not readable, get from: `https://www.realrate-archive.com/[ADD_INDUSTRY]/[PREVIOUS_YEAR]/graphs/`
- If that doesn't work, extract `report_url` in JSON and interpret the graph image attached to it.
- Add a description.

> **ECR causality note:** Economic Capital is positively influenced by equity and profits. Equity = assets − liabilities. Profit = income − costs. Therefore: higher assets → positive; higher liabilities → negative; higher income → positive; higher costs → negative.

**6. Company-Specific Plots**
From the JSON file, for the top 3 companies:
- Extract [PREVIOUS_YEAR] `feature_distribution_plot`, `main_keyfigs_over_time_plot`, and `regression_plot`.
- Interpret these graphs semantically, insert them, and add a short description below each.

**7. Industry-Level Graphs**
Extract and open [PREVIOUS_YEAR] `feature_distribution`, `feature_importance`, and `backtesting_correlation` from:
`https://realrate-archive.com/[ADD_INDUSTRY]/[PREVIOUS_YEAR]/`
- For the overall companies, interpret these graphs semantically and add a short description below.

**8. Strengths & Weaknesses**
- Characterize the top 3 companies by strengths and weaknesses.
- Extract `report_url` and `report_text` from the JSON, explain it.
- Extract `strength_weakness_over_time_plot` from the JSON; interpret and add a description.
- Extract `table_records`, `input_variables`, and `output_variables` from the JSON and interpret them briefly.

**9. Notable Movers**
- Identify notable companies moving up or down significantly.

**10. Market Statistics**
- Prepare statistics for the total market: average ECR, standard deviation of ECR, average change of ECR, etc.

**11. Balance Sheet & P&L Characterization**
- Characterize the top 3 companies in terms of balance sheet (assets and liabilities) and profit & loss (revenues, costs, net income).
- See `input_variables` and `output_variables` (in million dollars) in the JSON directory.

**12. Effects Characterization**
- Characterize the top 3 companies in terms of their "effects."
- An effect is the amount by which the variable increases (positive) or decreases (negative) the final ECR by deviating from the industry average.
- See variables in `shrinked_graph_json` and `table_records` (in ECR percentage points) in the JSON directory.

**13. SVG Graph Interpretation**
- Read and extract all AI Prompts from: https://github.com/realrate/AI-Prompts/wiki/Graph-Interpretation-and-Prompts
- Interpret the uploaded SVG graphs, convert to PNG format, and embed/attach them in the DOCX file.
- Add a short description for the top 3 companies and the overall industry.

**Graph interpretation guidelines:**

Examine each SVG graph and provide:
- Its type and a one-sentence guide on how to read it.
- Key trends, patterns, comparisons, or outliers.
- A concise analysis of what the data shows or implies.

Specific instructions per graph type:

- **Feature Distribution (bar chart):** Identify features on the X-axis and their frequencies/counts on the Y-axis. Highlight the most and least common features, note outliers, and summarize what the distribution indicates about feature prevalence.
- **Feature Importance Graph:** Identify features on X-axis and importance scores on Y-axis. Highlight the most and least important features, note notable differences or patterns, and analyze which features most influence the model.
- **Regression / Backtesting Correlation (scatter/line plot):** Identify variables on X- and Y-axes. Describe trends, patterns, or outliers; note the strength and direction of correlations; summarize what the plot indicates about the relationship between variables.

> **Distinguishing industry vs. company-specific graphics:**
> - Feature distribution plot: industry-specific = no black arrow; company-specific = black arrow pointing to the specific company's effect.
> - Correlation plot: industry-specific = no red dot; company-specific = red dot highlighting the company's position.
> - Feature importance graph: only available as industry-specific.

**14. Causal Graph Interpretation**

You are given a causal graph of a company's ECR, which measures financial strength compared to the market average. Interpret and summarize the graph for non-technical people. Do not just list strengths and weaknesses — write a verbose text.

Structure:
- **About the company:** Short intro in plain words.
- **Financial Strength (ECR):** State how far above/below average.
- **Strengths:** List the biggest positive factors; explain how they flow into stronger ECR.
- **Weaknesses:** List the biggest negative factors; explain their impact.
- **Manager's Takeaway:** One-paragraph summary in plain business language.

Example paragraph:
> The relative strengths and weaknesses of [company] are analyzed with respect to the market average, including all of its competitors. We analyzed all variables having an effect on the Economic Capital Ratio. The greatest strength of [company] compared to the market average is the variable [strength], increasing the Economic Capital Ratio by xx% points. The greatest weakness of [company] is the variable [weakness], reducing the Economic Capital Ratio by xx% points. In total, the company's Economic Capital Ratio is xx% points above the market average.

**Causal graph special rules (for correct interpretation — do not narrate these rules in the article):**
- This graph is for a single company.
- It is about ECR (Economic Capital Ratio), representing financial strength.
- Nodes represent important financial variables.
- Node numbers do NOT represent absolute values — they represent **effects** (how this node changes ECR by being above or below the industry average).
- Do not talk about increase/decrease of variables, but instead that a variable is **better or worse than the benchmark average**.
- The last node, Economic Capital Ratio, shows by how much percentage points the ECR of this company is above or below the market average.
- Edges show causal relationships.
- Red or green paths show the causal chains leading to high or low financial strength.

---

### Final Article

Based on these data and preparations, write an interesting, illustrated, and visually appealing article on that industry. Follow these instructions:

- The article should cover the marketing year [CURRENT_YEAR], but just call it simply [CURRENT_YEAR].
- The output MUST contain relevant graphs.
- Focus on all the main tasks above.
- Also write descriptions of why these companies did well.
- The output format should be figures with descriptions. Confirm that figures have been directly included and attached.
- Gather all updated data from the HTML and JSON sources as outlined.
- Write a 50-word paragraph on the [ADD COUNTRY AND INDUSTRY] with the latest revenue figures. Include this paragraph in the appropriate place.
- **Limit the report to 1600 words.**
- Write in an experienced journalistic style, not too technical, targeting a general public audience.
- Write in US English.
- Please create the best title and subtitle.
- After completion, remove all citations, website sources, and links in the DOCX file.
- Send a downloadable DOCX file.

**Corporate color scheme for all graphs:**
- Background: white
- Grid lines: black
- RealRate light blue: `#3DBACD`
- RealRate dark blue: `#00679B`
- RealRate black: `#000000`
- RealRate grey: `#AFAFAF`
- Semantic positive: `#5BB37F`
- Semantic negative: `#C04A3A`

**Embed and insert all uploaded graphs in the DOCX.**

Do not ask any follow-up questions; fulfill the task as best as possible.

---

## generate_report.py — Featured Image Design (1080×1080)

The script produces two variants (`featured_image_dark.png`, `featured_image_light.png`) via PIL/Pillow.

### Layout (top → bottom)
| Zone | Y range | Content |
|------|---------|---------|
| Accent stripe | 0–10 | Solid `#3DBACD` |
| Logo | 22–98 | RealRate logo **centered** |
| Titles | 170–430 | Industry name · "Rankings YEAR" · subtitle · divider |
| Company cards | 444–680 | 3 × white rounded-rect with logo + gold/silver/bronze medal |
| Info strip | ~752 | Thin line + "Annual Rankings · N Companies · Balance Sheet Year YYYY" |
| Footer | H-152 → H | Dark background + teal top bar + bold tagline |
| Border | all edges | 7 px white frame |

### Logo treatment
- **Dark version:** `RealRate_logo_horizontal_white.png` pasted directly on background (no card)
- **Light version:** `RealRate_logo_horizontal.png` on a subtle semi-transparent white rounded card

### Background
- **Dark:** Multi-stop vertical gradient (deep navy → mid navy → very deep navy) + fine diagonal lines at α=7 + teal angular accent polygon bottom-right + counter-accent bottom-left
- **Light:** Near-white to very light steel-blue gradient + fine diagonal lines at α=5 + soft teal accent polygon

### Footer text
`RealRate  —  Explainable Financial AI` (bold, 26 pt, white)

### Company graph assignment
See [Cover Design Rules → Graph assignment per company](#cover-design-rules-apply-to-every-generate_report_industrypy) below for the full assignment table and Company 3 rotation.

> Note: `{cid}_main_keyfigs.svg` returns 404 on the current archive — use the assignment table instead.

---

## Cover Design Rules (apply to every generate_report_{industry}.py)

### Text contrast rule
- **"Rankings YEAR" text must always be `C_WHITE` in dark mode** — never use the accent/teal color (`C_TEAL`) as the text color, because if a pill or background uses the same teal fill it becomes invisible.
- Do not add a teal-filled pill behind "Rankings YEAR" in dark mode. Either use no pill, or use a dark semi-transparent overlay so white text remains readable.

### Per-industry variation (required — never reuse across industries)
Each `generate_report_{industry}.py` must define its own unique cover via a `make(dark)` function with:
- Different background gradient colors
- Different geometric overlay (diagonal lines vs orthogonal grid vs other pattern)
- Different industry-specific motif element
- Different accent polygon placement

| Industry | Dark background | Light background | Overlay | Motif |
|----------|----------------|-----------------|---------|-------|
| Food (`generate_report.py`) | Deep navy (`#04111E` → `#091F35` → `#020B15`) | Near-white steel-blue | Fine diagonal lines α=7 | Right-heavy accent polygons |
| Finance Services (`generate_report_finance_services.py`) | Deep teal-black (`#04161C` → `#062630` → `#030E12`) | Mint-green | Orthogonal grid 72px + rising stock ticker line | Left vertical accent bars |
| Air (`generate_report_air.py`) | Midnight blue-indigo (`#07091E` → `#0B1034` → `#040612`) | Sky blue (`#EDF6FF` → `#DCF0FF` → `#C8E8FF`) | Radar arcs from bottom-left corner + ascending contrail arc | Top-left + bottom-right corner accents |
| Brokers (`generate_report_brokers.py`) | Deep slate-indigo (`#0A0A1C` → `#100D2C` → `#05040E`) | Silver-pearl (`#F5F6FF` → `#E4E8FF`) | Candlestick bars (trading chart pattern) | Top-right + bottom-left corner accents + ascending trend line |
| Motors (`generate_report.py` in US Motors/) | Deep carbon-red (`#13080C` → `#1C0E12` → `#080509`) | Warm off-white (`#F5F0EC` → `#ECE6E0`) | Horizontal speed/motion lines + double racing stripe near bottom | Top-left + bottom-right corner accents |

### Company logos on cover cards (always required)
- Download logos BEFORE calling `create_featured_images()` so they appear on the cover.
- URL pattern: `https://www.realrate-archive.com/{industry}/logos/{cid}_256x256.png` (try `_256x256.png` first, then plain `.png`)
- If logo unavailable: initials badge fallback — teal circle, 3-letter initials, white bold text.
- In dark mode cards: add a white semi-transparent rounded backing behind the logo so it's visible against dark card backgrounds.

### Graph assignment per company (rotate per industry — never repeat)
| Company | Graph 1 | Graph 2 |
|---------|---------|---------|
| #1 | Causal ECR graph (`IME_{cid}.svg`) | ECR Drivers bar chart |
| #2 | Strengths & Weaknesses over time (`{cid}_strength_weakness.svg`) | ECR Drivers bar chart |
| #3 | **Varies by industry** (see below) | ECR Drivers bar chart |

**Company 3 graph rotation (alternates by industry creation order):**
- Odd-order industries (Food, Air, Motors…): Backtesting correlation scatter (`regression_{cid}.svg`, red dot = company)
- Even-order industries (Finance Services, Brokers…): Feature distribution plot (`feature_distribution_{cid}.svg`, black arrow = company)
