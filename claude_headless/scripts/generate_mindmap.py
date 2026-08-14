#!/usr/bin/env python3
"""
Practice build — RealRate Company Mindmap Generator.

Rebuilt from skills/mindmap.md (real repo), which hardcodes exactly 8
companies and pulls executive/office photos from Wikipedia via Playwright.
This version works for ANY company in the archive and uses only fields
already verified in this session (ECR, rank, report_text's strength/
weakness sentences, logo_url) — no scraped photos of real people, no
browser dependency. Rendered directly with Pillow, same cross-platform font
fallback proven in generate_infographic.py (the original's font loader only
checked Windows paths and silently degraded elsewhere).

Branches are adaptive: a company missing multi-year history just gets one
fewer branch, laid out evenly among however many qualify — same principle
as the report skills' adaptive sections, applied to a single image instead
of PDF pages.

Usage:
    python generate_mindmap.py <industry_slug> <rank_or_name> [--year YEAR]

Output:
    output/us_<slug>/mindmap/<company_slug>_<year>_mindmap.png
"""

import argparse
import datetime
import io
import math
import os
import re
import urllib.request
import json

import cairosvg
from PIL import Image, ImageDraw, ImageFont

SKILL_NAME = "mindmap"

CANVAS_W, CANVAS_H = 1920, 1080
NAVY = (0, 59, 87)
TEAL = (61, 186, 205)
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 245)
POSITIVE = (65, 148, 83)
NEGATIVE = (192, 74, 58)

BRANCH_COLORS = [
    (0, 74, 110), (0, 88, 132), (51, 137, 177),
    (52, 162, 179), (44, 139, 154), (61, 186, 205),
]

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


def resolve_company(data: dict, arg: str) -> dict:
    companies = sorted(data["company_details"], key=lambda c: c["rank"])
    if arg.isdigit():
        rank = int(arg)
        for c in companies:
            if c["rank"] == rank:
                return c
        raise SystemExit(f"No company at rank {rank}. This industry has {len(companies)} ranked companies.")
    matches = [c for c in companies if arg.lower() in c["name"].lower()]
    if not matches:
        available = "\n  ".join(f"#{c['rank']} {c['name']}" for c in companies)
        raise SystemExit(f"No company matching '{arg}'. Available:\n  {available}")
    return matches[0]


def fetch_svg(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RealRate-Report-Practice/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8") if resp.status == 200 else None
    except Exception:
        return None


# --- ANALYZE ---------------------------------------------------------------------

def ecr_pct(value: float) -> float:
    return value * 100


def clean_archive_text(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_strength_weakness(report_text: str):
    """report_text follows a consistent template across every company
    checked this session — see context/mindmap-design.md. Returns
    (strength_var, strength_pts, weakness_var, weakness_pts), any of which
    may be None if the pattern isn't found (best-effort, not guaranteed).

    Anchored on "greatest strength/weakness of ... is the variable" rather
    than a bare "variable (.+?)," — the bare form's non-greedy match still
    locks onto the FIRST "variable" in the text (the strength sentence) and
    swallows everything up to the second occurrence of the target keyword,
    producing a paragraph-long "variable name" for the weakness case."""
    text = clean_archive_text(report_text)
    s_match = re.search(
        r"greatest strength of .+? is the variable (.+?), increasing the Economic Capital Ratio by (\d+)%", text)
    w_match = re.search(
        r"greatest weakness of .+? is the variable (.+?), reducing the Economic Capital Ratio by (\d+)%", text)
    strength = (s_match.group(1), int(s_match.group(2))) if s_match else (None, None)
    weakness = (w_match.group(1), int(w_match.group(2))) if w_match else (None, None)
    return strength[0], strength[1], weakness[0], weakness[1]


def build_branches(data: dict, company: dict) -> list:
    """Each branch is (label, [text lines], color). Adaptive — a branch is
    only included if its underlying data is actually present."""
    companies = sorted(data["company_details"], key=lambda c: c["rank"])
    avg = sum(ecr_pct(c["value"]) for c in companies) / len(companies)
    ecr = ecr_pct(company["value"])
    branches = []

    branches.append((
        "Industry Position",
        [f"Rank #{company['rank']} of {len(companies)}", data.get("industry_label", "")],
    ))

    gap = ecr - avg
    branches.append((
        "Financial Health",
        [f"ECR {ecr:.1f}%", f"{abs(gap):.1f} pts {'above' if gap >= 0 else 'below'} avg"],
    ))

    if company.get("report_text"):
        s_var, s_pts, w_var, w_pts = parse_strength_weakness(company["report_text"])
        if s_var:
            branches.append(("Greatest Strength", [s_var, f"+{s_pts} pts to ECR"]))
        if w_var:
            branches.append(("Greatest Weakness", [w_var, f"-{w_pts} pts to ECR"]))

    records = data.get("ecr_records", {})
    cid = company["company_id"]
    years_present = sorted(y for y in records if cid in records[y])
    if len(years_present) >= 2:
        first, last = years_present[0], years_present[-1]
        first_v = float(records[first][cid]["ecr"])
        last_v = float(records[last][cid]["ecr"])
        direction = "up" if last_v > first_v else "down" if last_v < first_v else "flat"
        branches.append(("Multi-Year Trend", [f"{first}→{last}: {direction}", f"{first_v:.0f}% → {last_v:.0f}%"]))

    status = "Top-Rated" if company.get("top_rated") else "Not Top-Rated"
    branches.append(("Rating Status", [status, f"{company.get('year', data.get('year'))} cycle"]))

    return branches


# --- RENDER ---------------------------------------------------------------------

def _load_font(size: int, bold: bool = False):
    """Same cross-platform fallback chain as generate_infographic.py — the
    original mindmap script only checked Windows font paths."""
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


def load_logo(svg_path_or_content: str, height_px: int, is_content=False) -> Image.Image:
    if is_content:
        png_bytes = cairosvg.svg2png(bytestring=svg_path_or_content.encode("utf-8"), output_height=height_px)
    else:
        png_bytes = cairosvg.svg2png(url=svg_path_or_content, output_height=height_px)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def draw_centered_text(draw, cx, cy, lines, font, fill, max_width=340):
    """max_width guards against a bad upstream parse (e.g. a regex capture
    swallowing a whole sentence) turning one branch into unreadable
    canvas-wide text — truncate rather than let it overflow silently."""
    total_h = len(lines) * (font.size + 6)
    y = cy - total_h / 2
    for line in lines:
        while draw.textlength(line, font=font) > max_width and len(line) > 3:
            line = line[:-4] + "…"
        w = draw.textlength(line, font=font)
        draw.text((cx - w / 2, y), line, font=font, fill=fill)
        y += font.size + 6


def render_mindmap(data: dict, company: dict, out_path: str):
    branches = build_branches(data, company)
    n = len(branches)

    base = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    draw = ImageDraw.Draw(base)

    hub_cx, hub_cy, hub_r = CANVAS_W // 2, CANVAS_H // 2, 190
    branch_r = 420
    branch_radius = 150

    f_label = _load_font(22, bold=True)
    f_line = _load_font(20, bold=False)
    f_badge = _load_font(20, bold=True)

    # Shrink the hub name to fit rather than truncate — a company name is
    # the one label a reader most needs intact.
    f_name = _load_font(34, bold=True)
    while draw.textlength(company["name"], font=f_name) > hub_r * 1.7 and f_name.size > 18:
        f_name = _load_font(f_name.size - 2, bold=True)

    # Connector lines (drawn first, under everything)
    positions = []
    for i in range(n):
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        bx = hub_cx + branch_r * math.cos(angle)
        by = hub_cy + branch_r * math.sin(angle)
        positions.append((bx, by))
        draw.line([(hub_cx, hub_cy), (bx, by)], fill=(*TEAL, 255), width=3)

    # Branch circles + labels
    for (label, lines), (bx, by), color in zip(branches, positions, BRANCH_COLORS * 2):
        draw.ellipse([bx - branch_radius, by - branch_radius, bx + branch_radius, by + branch_radius],
                     fill=color, outline=WHITE, width=2)
        draw_centered_text(draw, bx, by - 20, [label], f_label, TEAL)
        draw_centered_text(draw, bx, by + 15, lines, f_line, WHITE)

    # Hub (drawn last, on top of connector lines)
    draw.ellipse([hub_cx - hub_r, hub_cy - hub_r, hub_cx + hub_r, hub_cy + hub_r],
                 fill=NAVY, outline=TEAL, width=4)

    logo = load_logo(RR_LOGO_SVG_PATH, height_px=36)
    base.paste(logo, (hub_cx - logo.width // 2, hub_cy - hub_r + 24), logo)

    draw_centered_text(draw, hub_cx, hub_cy - 20, [company["name"]], f_name, WHITE, max_width=hub_r * 1.8)

    ecr = ecr_pct(company["value"])
    badge_text = f"ECR {ecr:.1f}%   ·   Rank #{company['rank']}"
    bw = draw.textlength(badge_text, font=f_badge)
    draw.text((hub_cx - bw / 2, hub_cy + 40), badge_text, font=f_badge, fill=OFF_WHITE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base.save(out_path, "PNG")


def generate_for_company(data: dict, company: dict, slug: str, year: int) -> str:
    company_slug = re.sub(r"[^a-z0-9]+", "_", company["name"].lower()).strip("_")
    out_dir = os.path.join(os.getcwd(), "output", f"us_{slug}", SKILL_NAME)
    out_path = os.path.join(out_dir, f"{company_slug}_{year}_mindmap.png")

    render_mindmap(data, company, out_path)
    print(f"Wrote {out_path}")
    print(f"  Branches included: {len(build_branches(data, company))} (adaptive — depends on available data)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Practice: generate a RealRate company mindmap PNG.")
    parser.add_argument("industry", help="Industry slug or name, e.g. 'air' or 'US Air'")
    parser.add_argument("company", help="Company rank (e.g. '1'), a name substring, or 'all' to "
                                         "generate one mindmap per company in the industry")
    parser.add_argument("--year", type=int, default=None, help="Override the archive year to fetch")
    args = parser.parse_args()

    slug = resolve_slug(args.industry)
    data = fetch_ranking_data(slug, args.year)
    year = data.get("year")

    if args.company.strip().lower() == "all":
        companies = sorted(data["company_details"], key=lambda c: c["rank"])
        print(f"Generating mindmaps for all {len(companies)} companies...")
        failures = []
        for company in companies:
            try:
                generate_for_company(data, company, slug, year)
            except Exception as e:
                print(f"  FAILED for {company['name']} (rank {company['rank']}): {e}")
                failures.append(company["name"])
        print(f"Done: {len(companies) - len(failures)}/{len(companies)} mindmaps generated.")
        if failures:
            print(f"Failed: {', '.join(failures)}")
        return

    company = resolve_company(data, args.company)
    generate_for_company(data, company, slug, year)


if __name__ == "__main__":
    main()
