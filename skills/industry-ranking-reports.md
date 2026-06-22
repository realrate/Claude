# /industry-ranking-reports — RealRate Ranking Report Toolkit

All-in-one toolkit for RealRate ranking reports. Supports three sub-commands:

**Usage:** `/industry-ranking-reports <sub-command> [args]`

---

## Sub-commands

### `new <dir-slug> <archive-slug> <display-name>`
Scaffold a new industry report directory and `generate_report.py`.

**Example:** `/industry-ranking-reports new "US Motors" us_motors "U.S. Motor Industry"`

**Steps:**
1. Fetch `https://www.realrate-archive.com/<archive-slug>/2025/website-ranking.json` to get the top-3 companies (name, ECR, company_id).
2. Determine the cover design for this industry from CLAUDE.md's "Per-industry variation" table. If not yet listed, use the next rotation entry from the "Company 3 graph rotation" list.
3. Write `report (2026)/<dir-slug>/generate_report.py` using the template below. Fill every `<PLACEHOLDER>` with real values from step 1–2.
4. Print a summary: top-3 companies with ECR and IDs, cover design applied, and the exact command to run the script.
5. Remind the user to fill in EFFECTS, FINANCIALS, HIST for earlier years, and article body text before running.

**Cover design rules (always enforce):**
- Never reuse the same background gradient or overlay as an existing industry — check CLAUDE.md's Per-industry variation table first.
- "Rankings YEAR" text must always be `C_WHITE` in dark mode — never teal.
- Download logos before calling `create_featured_images()` using `download_logos(IDS, "<archive-slug>", CHART_DIR)`.

**Template:**

```python
"""
RealRate Ranking Report Generator — <DISPLAY_NAME> 2026
Marketing year 2026 / Balance sheet year 2025

Outputs:
  report (2026)/<DIR_SLUG>/
    <SAFE_NAME>_Rankings_2026.docx
    <SAFE_NAME>_Rankings_2026.pdf
    featured_image_dark.png
    featured_image_light.png
    website_title.txt
    linkedin_post.txt
    titles.md
"""

import math
import os
import random
import sys
from PIL import Image, ImageDraw

# Script lives in report (2026)/<DIR_SLUG>/ — project root is 3 levels up
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from rr_shared import (
    LIGHT_BLUE, DARK_BLUE, GREY, C_TEAL, C_WHITE, GOLD, SILVER, BRONZE,
    apply_style, save_chart,
    chart_top_n, chart_ecr_history, chart_effects, chart_market_stats,
    convert_svgs_to_png, download_svg, download_logos,
    add_heading, add_body, add_interpretation,
    add_caption, add_png, add_svg, add_divider, set_doc_margins,
    generate_pdf, save_text_files,
    pil_fnt, pil_paste, pil_rr_rect, pil_dtxt, pil_initials_badge,
)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT         = _ROOT
REPORT_DIR   = os.path.join(ROOT, "report (2026)")
INDUSTRY_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR    = os.path.join(INDUSTRY_DIR, "charts")
LOGOS_DIR    = os.path.join(ROOT, "RealRate Logos")
os.makedirs(CHART_DIR, exist_ok=True)

# ── Archive ────────────────────────────────────────────────────────────────────
BASE_URL = "https://www.realrate-archive.com/<ARCHIVE_SLUG>/2025"
IDS = {
    "<CO1_NAME>": "<CO1_ID>",
    "<CO2_NAME>": "<CO2_ID>",
    "<CO3_NAME>": "<CO3_ID>",
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA — balance sheet year 2025 / marketing year 2026
# Source: https://www.realrate-archive.com/<ARCHIVE_SLUG>/2025/website-ranking.json
#         https://www.realrate-archive.com/<ARCHIVE_SLUG>/qa/
# ══════════════════════════════════════════════════════════════════════════════
RANKING_2026 = [
    {"rank": 1, "name": "<CO1_NAME>", "ecr": <CO1_ECR>},
    {"rank": 2, "name": "<CO2_NAME>", "ecr": <CO2_ECR>},
    {"rank": 3, "name": "<CO3_NAME>", "ecr": <CO3_ECR>},
    # TODO: add more notable companies from the JSON
]
MARKET_AVG = <MARKET_AVG>  # TODO: compute from JSON ecr values

HIST = {
    # TODO: populate from earlier JSON years
    2026: (<CO1_ECR>, <CO2_ECR>, <CO3_ECR>, <MARKET_AVG>),
}

EFFECTS = {
    # TODO: populate from shrinked_graph_json / table_records in JSON
    "<CO1_NAME>": {},
    "<CO2_NAME>": {},
    "<CO3_NAME>": {},
}
ECR_ABOVE = {
    "<CO1_NAME>": <CO1_ECR> - <MARKET_AVG>,
    "<CO2_NAME>": <CO2_ECR> - <MARKET_AVG>,
    "<CO3_NAME>": <CO3_ECR> - <MARKET_AVG>,
}

FINANCIALS = {
    # TODO: populate from output_variables in JSON
}

ECR_HIST_SERIES = [
    (0, "<CO1_NAME>", LIGHT_BLUE, "-",  "o"),
    (1, "<CO2_NAME>", DARK_BLUE,  "-",  "s"),
    (2, "<CO3_NAME>", "#555555",  "-",  "^"),
    (3, "Market Average", GREY,   "--", "none"),
]

MKT_YEARS = [2024, 2025, 2026]
MKT_AVGS  = [<MARKET_AVG>, <MARKET_AVG>, <MARKET_AVG>]  # TODO: fill historical avgs

FEAT_IMP = {}  # TODO: populate from feature_importance JSON or SVG


# ══════════════════════════════════════════════════════════════════════════════
# FEATURED IMAGE — <DISPLAY_NAME> design (1080×1080)
# TODO: implement industry-specific background, overlay, and motif
# per the cover design rules in CLAUDE.md
# ══════════════════════════════════════════════════════════════════════════════
def create_featured_images():
    W, H = 1080, 1080
    co_logos = download_logos(IDS, "<ARCHIVE_SLUG>", CHART_DIR)

    def make(dark):
        cv = Image.new("RGBA", (W, H))
        dr = ImageDraw.Draw(cv)

        if dark:
            for y in range(H):
                t = y / H
                dr.line([(0, y), (W, y)], fill=(
                    int(10 + 5 * t), int(8 + 5 * t), int(28 + 10 * t)))
            txt      = C_WHITE
            name_col = C_WHITE
            card_bg  = (12, 10, 35, 225)
            card_brd = C_TEAL
            foot_bg  = (3, 2, 10)
            rr_file  = "RealRate_logo_horizontal_white.png"
        else:
            for y in range(H):
                t = y / H
                dr.line([(0, y), (W, y)],
                        fill=(int(245 - 20 * t), int(246 - 14 * t), int(255 - 15 * t)))
            txt      = (10, 8, 45)
            name_col = (10, 8, 45)
            card_bg  = (255, 255, 255, 255)
            card_brd = C_TEAL
            foot_bg  = (0, 103, 155)
            rr_file  = "RealRate_logo_horizontal.png"

        dr.rectangle([0, 0, W, 10], fill=C_TEAL)

        lbw, lbh = 300, 72
        lbx = (W - lbw) // 2
        lby = 24
        if not dark:
            pil_rr_rect(dr, [lbx - 18, lby - 10, lbx + lbw + 18, lby + lbh + 10],
                        r=14, fill=(255, 255, 255, 210))
        pil_paste(cv, os.path.join(LOGOS_DIR, rr_file), lbx, lby, lbw, lbh)
        dr = ImageDraw.Draw(cv)

        pil_dtxt(dr, (W // 2, 200), "<DISPLAY_NAME>", txt, pil_fnt("bold", 70))
        pil_dtxt(dr, (W // 2, 295), "Rankings 2026",
                 C_WHITE if dark else (0, 103, 155), pil_fnt("bold", 62))
        pil_dtxt(dr, (W // 2, 370), "Most Financially Resilient Companies",
                 txt, pil_fnt("italic", 28))
        dr.rectangle([90, 408, W - 90, 413], fill=C_TEAL)

        CW, CH = 240, 240
        GAP    = 40
        x0     = (W - 3 * CW - 2 * GAP) // 2
        y0     = 436
        for i, (co, medal) in enumerate(zip(IDS.keys(), [GOLD, SILVER, BRONZE])):
            cx   = x0 + i * (CW + GAP)
            card = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
            cd   = ImageDraw.Draw(card)
            pil_rr_rect(cd, [0, 0, CW, CH], r=22, fill=card_bg)
            pil_rr_rect(cd, [0, 0, CW, CH], r=22, fill=None,
                        outline=(*card_brd, 200), lw=3)

            lp = co_logos.get(co)
            logo_shown = False
            if lp and os.path.exists(lp):
                try:
                    logo = Image.open(lp).convert("RGBA")
                    logo.thumbnail((CW - 36, CH - 36), Image.LANCZOS)
                    if dark:
                        pad = 8
                        lx  = (CW - logo.width) // 2
                        ly  = (CH - logo.height) // 2
                        pil_rr_rect(cd, [lx - pad, ly - pad,
                                         lx + logo.width + pad, ly + logo.height + pad],
                                    r=10, fill=(255, 255, 255, 230))
                    card.paste(logo, ((CW - logo.width) // 2, (CH - logo.height) // 2), logo)
                    logo_shown = True
                except Exception as e:
                    print(f"  logo paste error {co}: {e}")

            if not logo_shown:
                initials = "".join(w[0] for w in co.split() if w[0].isupper())[:3]
                pil_initials_badge(cd, CW // 2, CH // 2, 72, initials, pil_fnt)

            cv.paste(card, (cx, y0), card)

            mr  = 26
            mx2 = cx + CW - mr - 4
            my2 = y0 + mr + 4
            ov  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od  = ImageDraw.Draw(ov)
            od.ellipse([mx2 - mr - 4, my2 - mr - 4, mx2 + mr + 4, my2 + mr + 4],
                       fill=(255, 255, 255, 180))
            od.ellipse([mx2 - mr, my2 - mr, mx2 + mr, my2 + mr], fill=(*medal, 255))
            pil_dtxt(od, (mx2, my2), str(i + 1), C_WHITE, pil_fnt("bold", 28))
            cv = Image.alpha_composite(cv, ov)
            dr = ImageDraw.Draw(cv)

            pil_dtxt(dr, (cx + CW // 2, y0 + CH + 22), co,
                     name_col, pil_fnt("bold", 18))
            pil_dtxt(dr, (cx + CW // 2, y0 + CH + 46),
                     f"ECR {RANKING_2026[i]['ecr']}%",
                     C_TEAL if dark else (0, 103, 155), pil_fnt("bold", 16))

        info_y = y0 + CH + 72
        dr.line([(90, info_y), (W - 90, info_y)], fill=C_TEAL, width=1)
        pil_dtxt(dr, (W // 2, info_y + 26),
                 "Annual Rankings  ·  Balance Sheet Year 2025",
                 txt, pil_fnt("reg", 17))

        fy = H - 148
        dr.rectangle([0, fy, W, H], fill=foot_bg)
        dr.rectangle([0, fy, W, fy + 6], fill=C_TEAL)
        pil_dtxt(dr, (W // 2, fy + 76),
                 "RealRate  —  Explainable Financial AI", C_WHITE, pil_fnt("bold", 26))

        bw = 7
        for rect in [(0, 0, W, bw), (0, H - bw, W, H), (0, 0, bw, H), (W - bw, 0, W, H)]:
            dr.rectangle(rect, fill=C_WHITE)
        return cv

    paths = []
    for dark, suffix in [(True, "dark"), (False, "light")]:
        img  = make(dark)
        path = os.path.join(INDUSTRY_DIR, f"featured_image_{suffix}.png")
        img.convert("RGB").save(path)
        print(f"  Featured image ({suffix}): {os.path.basename(path)}")
        paths.append(path)
    return paths[0], paths[1]


# ══════════════════════════════════════════════════════════════════════════════
# BUILD CHARTS
# ══════════════════════════════════════════════════════════════════════════════
print("Building charts…")
p_top = chart_top_n(
    RANKING_2026, MARKET_AVG,
    "<DISPLAY_NAME> 2026 — Selected Rankings by ECR",
    CHART_DIR, "top_ranking.png", top3=3,
)
p_hist = chart_ecr_history(
    HIST, ECR_HIST_SERIES,
    "ECR Evolution — Top-3 Companies, Marketing Years 2024–2026",
    CHART_DIR,
)
p_mkt = chart_market_stats(
    MKT_YEARS, MKT_AVGS,
    "<DISPLAY_NAME> — Market Average ECR by Year",
    CHART_DIR,
)
eff_charts = {co: chart_effects(co, EFFECTS[co], ECR_ABOVE[co], CHART_DIR) for co in IDS}

# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD LOGOS + FEATURED IMAGES
# ══════════════════════════════════════════════════════════════════════════════
print("\nDownloading company logos…")
download_logos(IDS, "<ARCHIVE_SLUG>", CHART_DIR)
p_feat_dark, p_feat_light = create_featured_images()

# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD SVGs
# Graph assignment (per CLAUDE.md rotation):
#   Co1 → Causal ECR graph (IME_{cid}.svg)
#   Co2 → Strengths & Weaknesses over time ({cid}_strength_weakness.svg)
#   Co3 → <GRAPH3_TYPE> (per rotation in CLAUDE.md)
# Industry: feature_importance.svg, regression_2025.svg
# ══════════════════════════════════════════════════════════════════════════════
print("\nDownloading SVGs…")
causal_svg, sw_svg, co3_svg = {}, {}, {}
for co, cid in IDS.items():
    causal_svg[co] = download_svg(f"{BASE_URL}/graphs/IME_{cid}.svg",
                                  f"causal_{cid}.svg", CHART_DIR)
    sw_svg[co]     = download_svg(
        f"{BASE_URL}/plot_over_time/{cid}_strength_weakness.svg",
        f"sw_{cid}.svg", CHART_DIR)
    co3_svg[co]    = download_svg(
        f"{BASE_URL}/backtesting_correlation/regression_{cid}.svg",
        f"reg_{cid}.svg", CHART_DIR)

feat_imp_svg = download_svg(
    f"{BASE_URL}/feature_importance/feature_importance.svg",
    "feat_importance.svg", CHART_DIR)
reg_ind_svg  = download_svg(
    f"{BASE_URL}/backtesting_correlation/regression_2025.svg",
    "reg_industry.svg", CHART_DIR)

print("\nConverting SVGs to PNG…")
causal  = convert_svgs_to_png(causal_svg)
sw_plot = convert_svgs_to_png(sw_svg)
co3     = convert_svgs_to_png(co3_svg)
misc    = convert_svgs_to_png({"feat_imp": feat_imp_svg, "reg_ind": reg_ind_svg})
feat_imp_png = misc["feat_imp"]
reg_ind_png  = misc["reg_ind"]

# ══════════════════════════════════════════════════════════════════════════════
# BUILD DOCX
# ══════════════════════════════════════════════════════════════════════════════
print("\nBuilding DOCX…")
doc = Document()
set_doc_margins(doc)

if p_feat_dark and os.path.exists(p_feat_dark):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(p_feat_dark, width=Inches(6.2))
    doc.add_paragraph()

ARTICLE_TITLE = "<DISPLAY_NAME> Rankings 2026: TODO"
SUBTITLE      = "TODO subtitle"

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = tp.add_run(ARTICLE_TITLE)
tr.font.size = Pt(21); tr.bold = True
tr.font.color.rgb = RGBColor(0x01, 0x67, 0x9b)

sp = doc.add_paragraph()
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sp.add_run(SUBTITLE)
sr.font.size = Pt(13); sr.italic = True
sr.font.color.rgb = RGBColor(0x3e, 0xba, 0xcd)

add_divider(doc)
doc.add_paragraph()

add_heading(doc, "Introduction", 1)
add_body(doc, "TODO: write introduction paragraph.")

add_heading(doc, "2026 Rankings at a Glance", 1)
add_body(doc, "TODO: write rankings overview.")
add_png(doc, p_top, "Figure 1 — <DISPLAY_NAME> 2026: Selected rankings by ECR. Source: RealRate Archive.")

# TODO: add company profiles, industry analysis, market stats, notable movers, takeaway

# ══════════════════════════════════════════════════════════════════════════════
# SAVE DOCX
# ══════════════════════════════════════════════════════════════════════════════
docx_path = os.path.join(INDUSTRY_DIR, "<SAFE_NAME>_Rankings_2026.docx")
doc.save(docx_path)
print(f"\nDOCX saved: {docx_path}")

WEBSITE_TITLE       = "<DISPLAY_NAME> Rankings 2026: TODO"
WEBSITE_META_TITLE  = "<DISPLAY_NAME> Rankings 2026 | RealRate ECR Analysis"
WEBSITE_META_DESC   = "TODO meta description."
WEBSITE_DECK        = "TODO deck."
WEBSITE_HIGHLIGHTED = "TODO highlighted paragraph."
LINKEDIN_POST       = "TODO LinkedIn post."
TITLES_MD = f"""# Title & Copy Variants — <DISPLAY_NAME> Rankings 2026\n\n## DOCX / PDF\n**Title:** {ARTICLE_TITLE}\n**Subtitle:** {SUBTITLE}\n"""

save_text_files(
    INDUSTRY_DIR,
    title=WEBSITE_TITLE, meta_title=WEBSITE_META_TITLE,
    meta_desc=WEBSITE_META_DESC, deck=WEBSITE_DECK,
    highlighted_desc=WEBSITE_HIGHLIGHTED, url_slug="/<ARCHIVE_SLUG>-rankings-2026",
    linkedin_post=LINKEDIN_POST, titles_md=TITLES_MD,
)

print("\nGenerating PDF…")
generate_pdf(docx_path, os.path.join(INDUSTRY_DIR, "<SAFE_NAME>_Rankings_2026.pdf"))
print("\nDone. Output folder:", INDUSTRY_DIR)
```

---

### `run <industry-folder>`
Run the `generate_report.py` for an existing industry.

**Example:** `/industry-ranking-reports run "US Brokers"`

**Steps:**
1. Resolve the script path: `report (2026)/<industry-folder>/generate_report.py`. If it doesn't exist, list the available folders under `report (2026)/` and ask the user to pick one. Also accept a partial/case-insensitive match (e.g. `brokers` → `US Brokers`).
2. Run: `python "report (2026)/<industry-folder>/generate_report.py"`
3. On success: list the output files created (DOCX, PDF, featured images).
4. On failure: show the full traceback and diagnose the cause. If `ModuleNotFoundError: rr_shared`, check that the script is exactly 3 directory levels deep from the project root (`report (2026)/<Industry>/generate_report.py`).

---

### `fetch <archive-slug> [year]`
Fetch and summarize ranking data from the RealRate archive.

**Example:** `/industry-ranking-reports fetch us_food` or `/industry-ranking-reports fetch us_air 2024`

**Steps:**
1. Fetch `https://www.realrate-archive.com/<archive-slug>/<year>/website-ranking.json` (default year: `2025`).
2. Display:
   - **Top 10** — rank, name, ECR (`val`), company_id, rank change
   - **Market stats** — average, std dev, min, max ECR across all companies
   - **Notable movers** — companies that shifted ±5 positions or more
3. For top-3 companies, show `company_details` summary and available graph URLs.
4. Cross-check top-3 names and ECR values against `https://www.realrate-archive.com/<archive-slug>/qa/`. Report any discrepancies.
5. If no year was specified, also probe `2024` and `2023` to report which years have data.

**Output format:**
```
── <archive-slug> / Balance Sheet Year <year> ──────────────

Top 10:
  #1  <name>  ECR <val>%  (id: <company_id>)  change: <rank_change>
  ...

Market stats:
  Average ECR:  <avg>%   Std dev: <std>%   Min / Max: <min>% / <max>%

Notable movers (±5 positions):
  <name>  <old_rank> → <new_rank>

Top-3 details:
  [1] <name>
      <company_details summary>
      Graphs: causal=<url>  sw=<url>  fd=<url>  reg=<url>

HTML cross-check: ✓ consistent  /  ✗ discrepancy: <details>

Available years: 2025 ✓  2024 ✓  2023 ✗
```

**Notes:**
- Only fetch from `https://www.realrate-archive.com/` — no other websites.
- ECR values in the JSON are stored under the `val` key per company entry.
- If the JSON returns 404, report it and suggest checking the slug spelling.

---

## Quick reference

| Sub-command | Args | Purpose |
|-------------|------|---------|
| `new` | `<dir-slug> <archive-slug> <display-name>` | Scaffold a new industry report |
| `run` | `<industry-folder>` | Run an existing report generator |
| `fetch` | `<archive-slug> [year]` | Fetch & summarize archive data |
