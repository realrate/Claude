#!/usr/bin/env python3
"""
Practice build — RealRate Industry Report Generator.

Pipeline (same three-stage shape as generate_infographic.py):
  1. FETCH    — one live JSON response carries everything this skill needs
  2. ANALYZE  — turn raw fields into numbers/text per candidate section
  3. RENDER   — one PDF page per section that qualifies (chart + interpretation)

Sections are ADAPTIVE, not a fixed count — see context/industry-report-design.md
§ "Sections are adaptive, not fixed". Each entry in SECTION_REGISTRY declares
its own `requires(data)` check; only sections whose required data is actually
present for this run are rendered. Don't assert what the data doesn't support.

Usage:
    python generate_industry_report.py <industry_slug> [--year YEAR]

Output:
    output/us_<slug>/industry-report/<slug>_<year>_report.pdf
"""

import argparse
import datetime
import io
import os
import re
import textwrap
import urllib.request
import json

import cairosvg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

SKILL_NAME = "industry-report"

# context/industry-report-design.md § Chart style
NAVY = "#003b57"
PRIMARY = "#00679B"
SECONDARY = "#3DBACD"
POSITIVE = "#419453"
NEGATIVE = "#C04A3A"
BG = "#f5f5f5"

LOGO_SVG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "context", "RealRate_logo_horizontal.svg"
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


# --- Stage 1: FETCH ----------------------------------------------------------

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
    """Same walk-back pattern as generate_infographic.py."""
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


# --- Shared helpers -----------------------------------------------------------

def ecr_pct(value: float) -> float:
    """company_details[i].value is a raw ratio — confirmed bug fix, see
    infographic-design.md § Resolved. ecr_records' own `ecr` field is
    already on this scale and needs no conversion."""
    return value * 100


def companies_sorted(data: dict) -> list:
    return sorted(data["company_details"], key=lambda c: c["rank"])


def parse_money(s: str) -> float | None:
    """'110 B' -> 110.0 (billions). Returns None if unparseable."""
    s = s.strip()
    mult = {"T": 1000.0, "B": 1.0, "M": 1 / 1000.0, "K": 1 / 1_000_000.0}
    for suffix, factor in mult.items():
        if s.endswith(suffix):
            try:
                return float(s[:-1].strip().replace(",", "")) * factor
            except ValueError:
                return None
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def clean_archive_text(s: str) -> str:
    """report_text/scentences come from the archive with raw HTML markup
    (e.g. literal '<br/>') — strip tags rather than quoting them verbatim."""
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def wrapped_text(ax, text: str, width: int = 86, fontsize: int = 11.5):
    ax.axis("off")
    # Text is already wrapped by textwrap.fill below — matplotlib's own
    # wrap=True would re-wrap on top of that using axes pixel width, which
    # conflicts with the character-width wrap and orphans stray words.
    wrapped = "\n".join(textwrap.fill(p, width) for p in text.split("\n\n"))
    ax.text(0, 1, wrapped, transform=ax.transAxes, va="top", ha="left",
            fontsize=fontsize, color=NAVY, linespacing=1.6)


def style_axes(ax):
    ax.set_facecolor(BG)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=NAVY, labelsize=9)
    ax.xaxis.label.set_color(NAVY)
    ax.yaxis.label.set_color(NAVY)


# --- Stage 2: candidate sections (requires / chart / text) --------------------

def sec_industry_overview_requires(data):
    return bool(data.get("industry_box"))


def sec_industry_overview_chart(ax, data):
    style_axes(ax)
    labels, values = [], []
    for label, raw in data["industry_box"]:
        v = parse_money(raw)
        if v is not None:
            labels.append(f"{label}\n({raw})")
            values.append(v)
    if not values:
        ax.axis("off")
        return
    ax.bar(labels, values, color=PRIMARY)
    ax.set_ylabel("$ Billions")


def sec_industry_overview_text(data):
    label = data.get("industry_label", "This industry")
    n = data.get("num_companies", len(data["company_details"]))
    fields = ", ".join(f"{k} of {v}" for k, v in data["industry_box"])
    return (
        f"{label} currently tracks {n} companies in RealRate's archive. "
        f"Aggregate figures across the tracked companies: {fields}. "
        f"These are archive-reported totals, not RealRate's own estimate — "
        f"verify against realrate-archive.com before publishing."
    )


def sec_top10_requires(data):
    return len(data["company_details"]) > 0


def sec_top10_chart(ax, data):
    style_axes(ax)
    companies = companies_sorted(data)[:10]
    names = [c["name"][:16] for c in companies]
    values = [ecr_pct(c["value"]) for c in companies]
    avg = sum(ecr_pct(c["value"]) for c in companies_sorted(data)) / len(data["company_details"])
    colors = [SECONDARY if c.get("top_rated") else PRIMARY for c in companies]
    ax.barh(names[::-1], values[::-1], color=colors[::-1])
    ax.axvline(avg, color=NEGATIVE, linestyle="--", linewidth=1.2, label=f"Average {avg:.1f}%")
    ax.set_xlabel("ECR %")
    ax.legend(loc="lower right", fontsize=8, frameon=False)


def sec_top10_text(data):
    companies = companies_sorted(data)
    top10 = companies[:10]
    leader = top10[0]
    avg = sum(ecr_pct(c["value"]) for c in companies) / len(companies)
    gap = ecr_pct(leader["value"]) - avg
    top_rated = sum(1 for c in top10 if c.get("top_rated"))
    return (
        f"{leader['name']} leads with an ECR of {ecr_pct(leader['value']):.1f}%, "
        f"{gap:.1f} points above the {len(companies)}-company average of {avg:.1f}%. "
        f"{top_rated} of the top {len(top10)} hold Top-Rated status this cycle."
    )


def sec_distribution_requires(data):
    return len(data["company_details"]) >= 3


def sec_distribution_chart(ax, data):
    style_axes(ax)
    values = [ecr_pct(c["value"]) for c in data["company_details"]]
    ax.hist(values, bins=min(10, len(values)), color=PRIMARY, edgecolor="white")
    ax.set_xlabel("ECR %")
    ax.set_ylabel("Companies")


def sec_distribution_text(data):
    values = [ecr_pct(c["value"]) for c in data["company_details"]]
    n = len(values)
    mean = sum(values) / n
    std = (sum((v - mean) ** 2 for v in values) / n) ** 0.5
    rating = dict(data.get("rating_box", []))
    best_worst = rating.get("Best, worst rating", "")
    return (
        f"Across {n} tracked companies, ECR ranges from {min(values):.1f}% to "
        f"{max(values):.1f}%, averaging {mean:.1f}% with a standard deviation of "
        f"{std:.1f} points. RealRate's own summary reports best/worst rating as "
        f"{best_worst or 'not available in this response'}."
    )


def sec_top_rated_requires(data):
    return bool(data.get("rating_box"))


def sec_top_rated_chart(ax, data):
    rating = dict(data.get("rating_box", []))
    raw = rating.get("Top rated", "")
    try:
        n, total = [int(x.strip()) for x in raw.split("of")]
    except Exception:
        ax.axis("off")
        return
    ax.pie([n, max(total - n, 0)], labels=["Top-Rated", "Not Top-Rated"],
           colors=[SECONDARY, "#cfd8dc"], autopct="%1.0f%%",
           textprops={"color": NAVY, "fontsize": 10},
           wedgeprops={"width": 0.45})


def sec_top_rated_text(data):
    rating = dict(data.get("rating_box", []))
    raw = rating.get("Top rated", "unknown")
    names = [c["name"] for c in data["company_details"] if c.get("top_rated")]
    named = ", ".join(names) if names else "none listed in this response"
    return f"{raw} companies hold Top-Rated status this cycle: {named}."


def sec_trend_requires(data):
    records = data.get("ecr_records", {})
    qualifying_years = [y for y, cos in records.items() if len(cos) >= 3]
    return len(qualifying_years) >= 3


def _trend_series(data):
    records = data.get("ecr_records", {})
    series = []
    for year in sorted(records.keys()):
        cos = records[year]
        if len(cos) < 3:
            continue
        vals = [float(v["ecr"]) for v in cos.values()]
        series.append((int(year), sum(vals) / len(vals)))
    return series


def sec_trend_chart(ax, data):
    style_axes(ax)
    series = _trend_series(data)
    years = [y for y, _ in series]
    avgs = [v for _, v in series]
    ax.plot(years, avgs, color=PRIMARY, marker="o", linewidth=2)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_xlabel("Year")
    ax.set_ylabel("Industry Avg ECR %")


def sec_trend_text(data):
    series = _trend_series(data)
    first_year, first_avg = series[0]
    last_year, last_avg = series[-1]
    direction = "risen" if last_avg > first_avg else "fallen" if last_avg < first_avg else "held steady"
    return (
        f"Industry-average ECR has {direction} from {first_avg:.1f}% in {first_year} "
        f"to {last_avg:.1f}% in {last_year}, across {len(series)} years with sufficient "
        f"company coverage (3+ reporting companies) to be meaningful."
    )


def sec_leader_requires(data):
    leader = companies_sorted(data)[0]
    return bool(leader.get("report_text"))


def sec_leader_chart(ax, data):
    style_axes(ax)
    companies = companies_sorted(data)
    leader = companies[0]
    avg = sum(ecr_pct(c["value"]) for c in companies) / len(companies)
    ax.bar(["Industry Average", leader["name"][:24]],
           [avg, ecr_pct(leader["value"])], color=[SECONDARY, PRIMARY])
    ax.set_ylabel("ECR %")


def sec_leader_text(data):
    leader = companies_sorted(data)[0]
    quote = clean_archive_text(leader["report_text"])
    if len(quote) > 500:
        quote = quote[:500].rsplit(".", 1)[0] + "."
    return f'RealRate\'s own analysis of {leader["name"]}:\n\n"{quote}"'


def sec_movers_requires(data):
    return bool(data.get("scentences"))


def sec_movers_chart(ax, data):
    style_axes(ax)
    companies = {c["name"]: c for c in data["company_details"]}
    mentioned = [c for name, c in companies.items()
                 if any(name in s for s in data["scentences"])]
    if not mentioned:
        ax.axis("off")
        return
    names = [c["name"][:16] for c in mentioned]
    values = [ecr_pct(c["value"]) for c in mentioned]
    colors = [POSITIVE if c.get("trend", 0) and c["trend"] > 0 else NEGATIVE for c in mentioned]
    ax.barh(names, values, color=colors)
    ax.set_xlabel("ECR %")


def sec_movers_text(data):
    return "RealRate's own notes on notable movement this cycle:\n\n" + "\n\n".join(
        f"• {clean_archive_text(s)}" for s in data["scentences"]
    )


def sec_compression_requires(data):
    return len(data["company_details"]) >= 5


def sec_compression_chart(ax, data):
    style_axes(ax)
    companies = companies_sorted(data)
    tail = companies[5:10] if len(companies) > 5 else companies[-5:]
    names = [c["name"][:20] for c in tail]
    values = [ecr_pct(c["value"]) for c in tail]
    ax.bar(names, values, color=PRIMARY)
    ax.set_ylabel("ECR %")
    ax.tick_params(axis="x", rotation=30)


def sec_compression_text(data):
    companies = companies_sorted(data)
    tail = companies[5:10] if len(companies) > 5 else companies[-5:]
    values = [ecr_pct(c["value"]) for c in tail]
    spread = max(values) - min(values) if values else 0
    return (
        f"Ranks {tail[0]['rank']}–{tail[-1]['rank']} span only {spread:.1f} ECR points "
        f"({min(values):.1f}% to {max(values):.1f}%) — a tight cluster where small "
        f"balance-sheet shifts could reorder several positions next cycle."
    )


def sec_caveats_requires(data):
    return True


def sec_caveats_chart(ax, data):
    ax.axis("off")
    rows = [
        ("ECR scale (value × 100)", "Confirmed", POSITIVE),
        ("Marketing year vs. balance sheet year", "Confirmed", POSITIVE),
        ("trend sign convention", "Unverified", NEGATIVE),
        ("report_text / scentences wording", "Verbatim from archive", PRIMARY),
    ]
    for i, (label, status, color) in enumerate(rows):
        y = 0.8 - i * 0.22
        ax.text(0.02, y, label, fontsize=11, color=NAVY, transform=ax.transAxes)
        ax.text(0.62, y, status, fontsize=11, color=color, weight="bold", transform=ax.transAxes)


def sec_caveats_text(data):
    return (
        "This report only states what has been checked against the live archive "
        "response. Fields marked \"Unverified\" above are used as-is from the API "
        "without independent confirmation — treat them as provisional. Per this "
        "project's standing rule, verify all figures at realrate-archive.com before "
        "using this report externally."
    )


def sec_takeaway_requires(data):
    return True


def sec_takeaway_chart(ax, data):
    ax.axis("off")


def sec_takeaway_text(data):
    label = data.get("industry_label", "this industry")
    year = data.get("year")
    # `industry_id` is already the full slug (e.g. "us_air") — confirmed
    # live. Don't reconstruct it from url_segment, which is
    # "<year>-us-<slug>" and produces a doubled "us_us-<slug>" prefix if
    # concatenated with another "us_".
    industry_id = data.get("industry_id", "")
    n = data.get("num_companies", len(data["company_details"]))
    return (
        f"RealRate tracked {n} {label} companies for the {year} marketing cycle, "
        f"ranking each by Economic Capital Ratio — a measure of balance-sheet "
        f"resilience independent of size or reputation.\n\n"
        f"Full ranking: https://realrate.ai/rankings/{industry_id}/{year}"
    )


SECTION_REGISTRY = [
    {"title": "Industry Overview", "requires": sec_industry_overview_requires,
     "chart": sec_industry_overview_chart, "text": sec_industry_overview_text},
    {"title": "Top 10 Rankings", "requires": sec_top10_requires,
     "chart": sec_top10_chart, "text": sec_top10_text},
    {"title": "ECR Distribution", "requires": sec_distribution_requires,
     "chart": sec_distribution_chart, "text": sec_distribution_text},
    {"title": "Top-Rated Snapshot", "requires": sec_top_rated_requires,
     "chart": sec_top_rated_chart, "text": sec_top_rated_text},
    {"title": "Multi-Year ECR Trend", "requires": sec_trend_requires,
     "chart": sec_trend_chart, "text": sec_trend_text},
    {"title": "Sector Leader Profile", "requires": sec_leader_requires,
     "chart": sec_leader_chart, "text": sec_leader_text},
    {"title": "Notable Movers", "requires": sec_movers_requires,
     "chart": sec_movers_chart, "text": sec_movers_text},
    {"title": "Competitive Compression", "requires": sec_compression_requires,
     "chart": sec_compression_chart, "text": sec_compression_text},
    {"title": "Data Confidence & Caveats", "requires": sec_caveats_requires,
     "chart": sec_caveats_chart, "text": sec_caveats_text},
    {"title": "Takeaway & Full Ranking", "requires": sec_takeaway_requires,
     "chart": sec_takeaway_chart, "text": sec_takeaway_text},
]


# --- Stage 3: RENDER -----------------------------------------------------------

def load_logo_array(svg_path: str, height_px: int = 90):
    png_bytes = cairosvg.svg2png(url=svg_path, output_height=height_px)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def render_cover(pdf: PdfPages, display_name: str, year: int, num_sections: int):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    logo = load_logo_array(LOGO_SVG_PATH)
    logo_ax = fig.add_axes([0.5 - 0.18, 0.72, 0.36, 0.36 * logo.height / logo.width])
    logo_ax.imshow(logo)
    logo_ax.axis("off")

    fig.text(0.5, 0.6, f"US {display_name.upper()}", ha="center", fontsize=30,
              weight="bold", color=NAVY)
    fig.text(0.5, 0.55, "INDUSTRY REPORT", ha="center", fontsize=22,
              weight="bold", color=SECONDARY)
    fig.text(0.5, 0.49, f"{year} Marketing Cycle  ·  {num_sections} sections",
              ha="center", fontsize=13, color=NAVY)
    fig.text(0.5, 0.08, "Powered by RealRate: Using Explainable Financial AI",
              ha="center", fontsize=10, color="#888888")
    fig.text(0.5, 0.05, f"Generated {datetime.date.today().isoformat()}",
              ha="center", fontsize=9, color="#aaaaaa")
    pdf.savefig(fig)
    plt.close(fig)


def render_section(pdf: PdfPages, index: int, total: int, title: str, chart_fn, text: str, data: dict):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    fig.text(0.08, 0.95, f"{index:02d} / {total:02d}", fontsize=10, color=SECONDARY, weight="bold")
    fig.text(0.08, 0.91, title, fontsize=20, weight="bold", color=NAVY)

    # Left margin is wide enough for horizontal-bar y-tick labels (company
    # names) to not get clipped by the page edge — verified against actual
    # rendered output, not assumed.
    ax_chart = fig.add_axes([0.24, 0.46, 0.66, 0.40])
    chart_fn(ax_chart, data)

    ax_text = fig.add_axes([0.08, 0.06, 0.84, 0.32])
    wrapped_text(ax_text, text)

    pdf.savefig(fig)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Practice: generate a RealRate industry report PDF.")
    parser.add_argument("industry", help="Industry slug or name, e.g. 'air' or 'US Air'")
    parser.add_argument("--year", type=int, default=None, help="Override the archive year to fetch")
    args = parser.parse_args()

    slug = resolve_slug(args.industry)
    display_name = INDUSTRY_SLUGS[slug]

    data = fetch_ranking_data(slug, args.year)
    year = data.get("year")

    qualifying = [s for s in SECTION_REGISTRY if s["requires"](data)]
    skipped = [s["title"] for s in SECTION_REGISTRY if s not in qualifying]

    out_dir = os.path.join(os.getcwd(), "output", f"us_{slug}", SKILL_NAME)
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, f"{slug}_{year}_report.pdf")

    with PdfPages(pdf_path) as pdf:
        render_cover(pdf, display_name, year, len(qualifying))
        for i, section in enumerate(qualifying, start=1):
            text = section["text"](data)
            render_section(pdf, i, len(qualifying), section["title"], section["chart"], text, data)

    print(f"Wrote {pdf_path}")
    print(f"Sections included ({len(qualifying)}/{len(SECTION_REGISTRY)}): "
          + ", ".join(s["title"] for s in qualifying))
    if skipped:
        print(f"Sections skipped (data not available this run): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
