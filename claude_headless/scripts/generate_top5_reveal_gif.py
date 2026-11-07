#!/usr/bin/env python3
"""
Practice build — RealRate Top 5 Reveal GIF Generator.

Ported from "Industry Deep Dive Carousel/generate_cover_gif.py" (real
repo), which is Pillow-only (good — no browser dependency) but its
load_font() only tries Windows font paths (C:\\Windows\\Fonts\\...) and
silently falls back to Pillow's low-quality bitmap default everywhere
else. This version reuses the cross-platform font-fallback chain already
proven in generate_infographic.py.

Also generalized: the original is a hand-edited template (every constant
marked "# EDIT", meant to be edited in place per industry and left
edited). This version is CLI-driven like every other skill in this
project — no manual editing required to run it for a different industry.

Animates a rank-5-to-rank-1 reveal (suspense builds toward the leader),
holds on the final frame, then loops.

Usage:
    python generate_top5_reveal_gif.py <industry_slug> [--year YEAR]

Output:
    output/us_<slug>/top5-reveal-gif/<slug>_<year>_top5.gif
"""

import argparse
import datetime
import io
import os
import urllib.request
import json

import cairosvg
from PIL import Image, ImageDraw, ImageFont

SKILL_NAME = "top5-reveal-gif"

CANVAS_W, CANVAS_H = 1080, 1080
MARGIN = 60

NAVY = (0, 59, 87)
TEAL = (61, 186, 205)
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 245)
GOLD = (212, 175, 55)
SILVER = (192, 192, 192)
BRONZE = (176, 118, 62)
RANK_COLORS = {1: GOLD, 2: SILVER, 3: BRONZE}
DEFAULT_RANK_COLOR = (0, 88, 132)

RR_LOGO_SVG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "context", "RealRate_logo_light.svg"
)

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


# --- FETCH ---------------------------------------------------------------------

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
    raise SystemExit(f"Unknown industry '{arg}'. Available slugs: {', '.join(sorted(INDUSTRY_SLUGS))}")


def fetch_ranking_data(slug: str, year: int | None):
    candidates = [year] if year else [datetime.date.today().year - i for i in range(0, 4)]
    tried = []
    for y in candidates:
        url = f"https://www.realrate-archive.com/us_{slug}/{y}/website-ranking.json"
        tried.append(url)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RealRate-Report-Practice/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    continue
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("company_details"):
                    return data
        except Exception:
            continue
    raise RuntimeError(f"Could not fetch ranking data for slug '{slug}'. Tried:\n  " + "\n  ".join(tried))


def ecr_pct(value: float) -> float:
    return value * 100


def initials(name: str) -> str:
    parts = [p for p in name.replace(",", " ").split() if p]
    letters = [p[0].upper() for p in parts if p[0].isalpha()]
    return "".join(letters[:2]) if letters else "?"


# --- RENDER ---------------------------------------------------------------------

def _load_font(size: int, bold: bool = False):
    """Cross-platform fallback chain — the original script this was ported
    from only checked C:\\Windows\\Fonts\\... paths."""
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


def load_logo(height_px: int = 60) -> Image.Image:
    png_bytes = cairosvg.svg2png(url=RR_LOGO_SVG_PATH, output_height=height_px)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def build_base(display_name: str, year: int) -> Image.Image:
    base = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    draw = ImageDraw.Draw(base)

    logo = load_logo(48)
    base.paste(logo, (MARGIN, MARGIN), logo)

    f_title = _load_font(46, bold=True)
    f_sub = _load_font(24, bold=False)
    draw.text((MARGIN, MARGIN + 80), f"US {display_name.upper()}", font=f_title, fill=WHITE)
    draw.text((MARGIN, MARGIN + 136), f"TOP 5 · {year}", font=f_title, fill=TEAL)
    draw.text((MARGIN, MARGIN + 196), "Ranked by Economic Capital Ratio", font=f_sub, fill=OFF_WHITE)
    return base


def draw_row(draw: ImageDraw.ImageDraw, company: dict, row_index: int, top_y: int, row_h: int):
    ry = top_y + row_index * row_h
    row_mid = ry + row_h / 2
    rank = company["rank"]
    color = RANK_COLORS.get(rank, DEFAULT_RANK_COLOR)

    f_rank = _load_font(28, bold=True)
    f_name = _load_font(26, bold=True)
    f_stat = _load_font(30, bold=True)
    f_badge = _load_font(16, bold=True)

    av_cx, av_r = MARGIN + 90, 30
    draw.ellipse([av_cx - av_r, row_mid - av_r, av_cx + av_r, row_mid + av_r], fill=color)
    rank_text = str(rank)
    rw = draw.textlength(rank_text, font=f_rank)
    draw.text((av_cx - rw / 2, row_mid - 17), rank_text, font=f_rank, fill=WHITE if rank > 3 else NAVY)

    name_x = av_cx + av_r + 24
    name = company["name"]
    max_name_w = 480
    while draw.textlength(name, font=f_name) > max_name_w and len(name) > 3:
        name = name[:-2] + "…"
    draw.text((name_x, row_mid - 16), name, font=f_name, fill=WHITE)

    if company.get("top_rated"):
        draw.text((name_x, row_mid + 14), "★ TOP RATED", font=f_badge, fill=TEAL)

    stat_text = f"{ecr_pct(company['value']):.1f}%"
    sw = draw.textlength(stat_text, font=f_stat)
    draw.text((CANVAS_W - MARGIN - sw, row_mid - 18), stat_text, font=f_stat, fill=OFF_WHITE)


def build_frames(data: dict, display_name: str, year: int) -> list:
    companies = sorted(data["company_details"], key=lambda c: c["rank"])[:5]
    base = build_base(display_name, year)

    list_top = MARGIN + 260
    row_h = 130
    reveal_order = list(reversed(companies))  # rank 5 first, rank 1 last

    frames = []
    revealed = []
    for company in reveal_order:
        revealed.append(company)
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        # Draw already-revealed rows in their final rank position, so a
        # newly revealed row appears in place rather than the list
        # reshuffling frame to frame.
        for c in revealed:
            row_index = c["rank"] - 1
            draw_row(draw, c, row_index, list_top, row_h)
        frames.append(frame)

    return frames


def main():
    parser = argparse.ArgumentParser(description="Practice: generate a RealRate Top 5 reveal GIF.")
    parser.add_argument("industry", help="Industry slug or name, e.g. 'air' or 'US Air'")
    parser.add_argument("--year", type=int, default=None, help="Override the archive year to fetch")
    args = parser.parse_args()

    slug = resolve_slug(args.industry)
    display_name = INDUSTRY_SLUGS[slug]

    data = fetch_ranking_data(slug, args.year)
    year = data.get("year")

    frames = build_frames(data, display_name, year)

    out_dir = os.path.join(os.getcwd(), "output", f"us_{slug}", SKILL_NAME)
    os.makedirs(out_dir, exist_ok=True)
    gif_path = os.path.join(out_dir, f"{slug}_{year}_top5.gif")

    # Per-frame duration (not duplicate frames) to hold on the final
    # state — Pillow's GIF writer collapses pixel-identical consecutive
    # frames even with optimize=False, so duplicating frames to create a
    # "hold" silently produces a shorter GIF than intended. A duration
    # list is the correct way to make one frame linger.
    durations = [700] * (len(frames) - 1) + [3000]
    frames[0].save(
        gif_path, format="GIF", save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=False,
    )
    print(f"Wrote {gif_path}")
    print(f"Frames: {len(frames)} (5 reveal steps, final frame held for {durations[-1]}ms)")


if __name__ == "__main__":
    main()
