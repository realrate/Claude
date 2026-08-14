#!/usr/bin/env python3
"""
Practice build — RealRate Top 10 Ranking Infographic Generator.

Learning copy of infographics/generate_infographic.py, rebuilt to make the
link between "design context" and "rendering code" explicit. Every constant
below traces back to a line in claude_practice/context/infographic-design.md
— that's the pattern to notice: a script should never invent a color or size,
it should cite where the number came from.

Pipeline (three stages, same shape as every skill in this repo):
  1. FETCH  — pull live data from an external source (no local business logic)
  2. RENDER — turn that data + the design context into a PNG (Pillow, no browser)
  3. CAPTION — turn the same data into the LinkedIn caption text

Usage:
    python generate_infographic.py <industry_slug> [--year YEAR]

Output (written to ./output/, created if missing):
    output/<slug>_<year>.png
    output/linkedin_<slug>_<year>.txt

OPEN QUESTION (see context/infographic-design.md → "Known open question"):
this treats the archive's `value` field as already being an ECR percentage,
and `trend` as a signed delta. Unverified — check before publishing.
"""

import argparse
import datetime
import io
import os
import urllib.request
import json

import cairosvg
from PIL import Image, ImageDraw, ImageFont

# context/design-system.md § Logo: "Dark background -> RealRate_logo_light.svg
# (white), any corner at 50px margin". Resolve relative to this file, not cwd,
# so the script works no matter where it's invoked from.
LOGO_SVG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "context", "RealRate_logo_light.svg"
)
LOGO_HEIGHT_PX = 44  # context/infographic-design.md § Typography -> Logo

# --- Canvas — context/infographic-design.md § Canvas -----------------------
CANVAS_W, CANVAS_H = 1200, 1500
MARGIN = 50

# --- Colors — context/infographic-design.md § Colors ------------------------
NAVY = (0, 59, 87)           # #003b57 — background
TEAL = (61, 186, 205)        # #3DBACD — wordmark/accent
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 245)  # #f5f5f5 — secondary text/stats
LIGHT_GREY = (232, 232, 232)  # #e8e8e8 — flat trend
POSITIVE = (65, 148, 83)     # #419453 — trend up
NEGATIVE = (192, 74, 58)     # #C04A3A — trend down

# Rotating blue-family accent pool — context/infographic-design.md § rotating accent pool
ACCENT_POOL = [
    (0, 74, 110),    # Navy Blue
    (0, 88, 132),    # Dark Blue
    (51, 137, 177),  # Medium Blue
    (52, 162, 179),  # Blue Teal
    (44, 139, 154),  # Dark Teal
]

TAGLINE = "Powered by RealRate: Using Explainable Financial AI"

# Matches this script's skill file name — used to namespace output by skill,
# same convention as skills/auto-post-cycle.md's output/{industry}/{task}/ layout.
SKILL_NAME = "top10-infographic"

INDUSTRY_SLUGS = {
    "air": "Air", "motor": "Motor", "software": "Software", "computers": "Computers",
    "finance_services": "Finance Services", "food": "Food", "health_services": "Health Services",
    "advertising": "Advertising", "semiconductors": "Semiconductors", "programming": "Programming",
    "petrol": "Petrol", "mining": "Mining", "construction": "Construction",
    "realestate": "Real Estate", "hotels": "Hotels", "consulting": "Consulting",
    "data_processing": "Data Processing", "brokers": "Brokers", "savings": "Savings",
    "life": "Life Insurance", "non_life": "Non-Life Insurance", "pharma": "Pharma",
    "chemicals": "Chemicals", "state_banks": "State Banks",
    "medicinal_products": "Medicinal Products", "recreation": "Recreation",
}


# --- Stage 1: FETCH ----------------------------------------------------------

def fetch_ranking_data(slug: str, year: int | None):
    """Try the given year, then walk backwards a few years, until a valid
    response with company_details is found. Returns (data, year_used)."""
    candidates = [year] if year else [datetime.date.today().year - i for i in range(0, 4)]
    tried = []
    for y in candidates:
        url = f"https://www.realrate-archive.com/us_{slug}/{y}/website-ranking.json"
        tried.append(url)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RealRate-Infographic-Practice/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    continue
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("company_details"):
                    return data, y
        except Exception:
            continue
    raise RuntimeError(
        f"Could not fetch ranking data for slug '{slug}'. Tried:\n  " + "\n  ".join(tried)
    )


def resolve_slug(arg: str) -> str:
    if arg in INDUSTRY_SLUGS:
        return arg
    lowered = arg.lower().replace(" ", "_").replace("-", "_")
    if lowered.startswith("us_"):
        lowered = lowered[3:]
    if lowered in INDUSTRY_SLUGS:
        return lowered
    for slug, name in INDUSTRY_SLUGS.items():
        if arg.lower() == name.lower():
            return slug
    raise SystemExit(
        f"Unknown industry '{arg}'. Available slugs: {', '.join(sorted(INDUSTRY_SLUGS))}"
    )


# --- Shared formatting helpers ----------------------------------------------

def format_ecr(value: float) -> str:
    """`value` in company_details is a raw ratio, not a percentage — confirmed
    against the archive's own `ecr_records`/`rating_box` fields, which show
    the same company's ECR on a 0-100+ scale (e.g. 1.2349... == 123.5%)."""
    return f"{value * 100:.1f}%"


def trend_arrow(trend) -> tuple[str, tuple]:
    if trend is None or trend == 0:
        return "–", LIGHT_GREY
    if trend > 0:
        return "▲", POSITIVE
    return "▼", NEGATIVE


def initials(name: str) -> str:
    parts = [p for p in name.replace(",", " ").split() if p]
    letters = [p[0].upper() for p in parts if p[0].isalpha()]
    return "".join(letters[:2]) if letters else "?"


def industry_accent(slug: str):
    """Deterministic by slug, so the same industry always renders with the
    same accent color across runs — see design-system.md's accent rule."""
    return ACCENT_POOL[sum(slug.encode()) % len(ACCENT_POOL)]


def _load_font(size: int, bold: bool = False):
    """Design system specifies Manrope, but that's a web font loaded via
    Puppeteer for HTML posts. This script renders directly with Pillow (no
    browser), so it falls back to whatever system sans-serif is installed."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# --- Stage 2: RENDER ---------------------------------------------------------

def load_logo(height_px: int = LOGO_HEIGHT_PX) -> Image.Image:
    """Rasterize the real brand SVG at the spec'd height, colors as-authored
    in the file (do not recolor — the mark/lettering colors are intentional,
    not a guess)."""
    png_bytes = cairosvg.svg2png(url=LOGO_SVG_PATH, output_height=height_px)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def draw_pattern(draw: ImageDraw.ImageDraw, accent):
    """Subtle diagonal-stripe accent pattern confined to the top-right quadrant."""
    step = 46
    overlay_color = accent + (60,)  # low-opacity RGBA
    for x in range(CANVAS_W - 420, CANVAS_W + 300, step):
        draw.line([(x, 0), (x - 420, 420)], fill=overlay_color, width=10)


def render_image(slug: str, display_name: str, year: int, top10: list, avg_ecr: float, out_path: str):
    base = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    accent = industry_accent(slug)
    draw_pattern(ImageDraw.Draw(overlay), accent)
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(base)

    f_badge = _load_font(22, bold=True)
    f_title = _load_font(54, bold=True)
    f_subtitle = _load_font(24, bold=False)
    f_rank = _load_font(30, bold=True)
    f_name = _load_font(28, bold=True)
    f_avatar = _load_font(22, bold=True)
    f_stat = _load_font(30, bold=True)
    f_tag = _load_font(18, bold=False)

    # Logo (top-left, 50px margin) — the real brand asset, not hand-drawn text
    logo = load_logo()
    base.paste(logo, (MARGIN, MARGIN), logo)

    # "TOP 10" badge (top-right)
    badge_text = "TOP 10"
    bw = draw.textlength(badge_text, font=f_badge) + 44
    bh = 46
    bx0, by0 = CANVAS_W - MARGIN - bw, MARGIN
    draw.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=8, fill=TEAL)
    draw.text((bx0 + 22, by0 + 11), badge_text, font=f_badge, fill=NAVY)

    # Title
    title_text = f"US {display_name.upper()}"
    title_y = MARGIN + 90
    draw.text((MARGIN, title_y), title_text, font=f_title, fill=WHITE)
    draw.text((MARGIN, title_y + 66), "TOP 10 RANKING", font=f_title, fill=TEAL)

    # Subtitle
    subtitle = f"{year} ECR Ranking  ·  Industry Average {format_ecr(avg_ecr)}"
    draw.text((MARGIN, title_y + 150), subtitle, font=f_subtitle, fill=OFF_WHITE)

    # Ranked rows
    list_top = title_y + 210
    list_bottom = CANVAS_H - 110
    row_h = (list_bottom - list_top) / 10

    for i, company in enumerate(top10):
        ry = list_top + i * row_h
        row_mid = ry + row_h / 2

        draw.text((MARGIN, row_mid - 18), f"{i + 1:02d}", font=f_rank, fill=OFF_WHITE)

        av_cx, av_r = MARGIN + 90, 26
        draw.ellipse([av_cx - av_r, row_mid - av_r, av_cx + av_r, row_mid + av_r], fill=accent)
        init = initials(company["name"])
        iw = draw.textlength(init, font=f_avatar)
        draw.text((av_cx - iw / 2, row_mid - 13), init, font=f_avatar, fill=WHITE)

        name_x = av_cx + av_r + 24
        name = company["name"]
        max_name_w = 480
        while draw.textlength(name, font=f_name) > max_name_w and len(name) > 3:
            name = name[:-2] + "…"
        draw.text((name_x, row_mid - 17), name, font=f_name, fill=WHITE)

        if company.get("top_rated"):
            draw.text((name_x, row_mid + 12), "★ TOP RATED", font=f_tag, fill=TEAL)

        stat_text = format_ecr(company["value"])
        sw = draw.textlength(stat_text, font=f_stat)
        arrow, arrow_color = trend_arrow(company.get("trend"))
        stat_x = CANVAS_W - MARGIN - sw
        draw.text((stat_x, row_mid - 18), stat_text, font=f_stat, fill=OFF_WHITE)
        draw.text((stat_x - 34, row_mid - 15), arrow, font=f_name, fill=arrow_color)

        if i < 9:
            draw.line([(MARGIN, ry + row_h), (CANVAS_W - MARGIN, ry + row_h)], fill=(255, 255, 255, 20), width=1)

    draw.text((MARGIN, CANVAS_H - MARGIN - 20), TAGLINE, font=f_tag, fill=WHITE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base.save(out_path, "PNG")


# --- Stage 3: CAPTION ---------------------------------------------------------

def build_caption(slug: str, display_name: str, year: int, top10: list, avg_ecr: float) -> str:
    """Caption rules — context/infographic-design.md § Caption rules."""
    leader = top10[0]
    gap = (leader["value"] - avg_ecr) * 100  # same raw-ratio-to-percent fix as format_ecr()
    top_rated_count = sum(1 for c in top10 if c.get("top_rated"))

    lines = [
        "RealRate's ECR isolates how structurally sound a company's finances are, "
        "independent of size or reputation.",
        "",
        f"In RealRate's {year} Top 10 ranking for {display_name}, {leader['name']} "
        f"leads at {format_ecr(leader['value'])} ECR — "
        f"{gap:.1f} points above the industry average of {format_ecr(avg_ecr)}.",
        "",
        f"{top_rated_count} of the top 10 hold Top-Rated status this cycle.",
        "",
        f"Full ranking: https://realrate.ai/rankings/us_{slug}/{year}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Practice: generate a RealRate Top 10 ranking infographic.")
    parser.add_argument("industry", help="Industry slug or name, e.g. 'software' or 'US Software'")
    parser.add_argument("--year", type=int, default=None, help="Override the archive year to fetch")
    args = parser.parse_args()

    slug = resolve_slug(args.industry)
    display_name = INDUSTRY_SLUGS[slug]

    data, fetch_year = fetch_ranking_data(slug, args.year)
    # The URL path uses the balance sheet year (`fetch_year`), but the JSON's
    # own `year` field is the marketing year (matches `url_segment`, e.g.
    # "2026-us-air") — that's what belongs in the title/filename/ranking URL,
    # confirmed by comparing both against the live archive.
    year = data.get("year", fetch_year)
    companies = sorted(data["company_details"], key=lambda c: c["rank"])
    top10 = companies[:10]
    avg_ecr = sum(c["value"] for c in companies) / len(companies)

    industry_folder = f"us_{slug}"
    out_dir = os.path.join(os.getcwd(), "output", industry_folder, SKILL_NAME)
    png_path = os.path.join(out_dir, f"{slug}_{year}.png")
    txt_path = os.path.join(out_dir, f"linkedin_{slug}_{year}.txt")

    render_image(slug, display_name, year, top10, avg_ecr, png_path)
    with open(txt_path, "w") as f:
        f.write(build_caption(slug, display_name, year, top10, avg_ecr))

    print(f"Wrote {png_path}")
    print(f"Wrote {txt_path}")


if __name__ == "__main__":
    main()
