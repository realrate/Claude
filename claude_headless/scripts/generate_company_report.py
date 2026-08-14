#!/usr/bin/env python3
"""
Practice build — RealRate Company Report Generator.

Same three-stage pipeline and adaptive-section pattern as
generate_industry_report.py, one level deeper: a single company within an
industry. See context/company-report-design.md before changing anything —
in particular the CONFIRMED DISCREPANCY between company_details.value and
the causal graph's own stated ECR. Both are real RealRate outputs; this
script reports both rather than picking one.

Usage:
    python generate_company_report.py <industry_slug> <rank_or_name> [--year YEAR]

Output:
    output/us_<slug>/company-report/<company_slug>_<year>_report.pdf
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

SKILL_NAME = "company-report"

NAVY = "#003b57"
PRIMARY = "#00679B"
SECONDARY = "#3DBACD"
POSITIVE = "#419453"
NEGATIVE = "#C04A3A"
BG = "#f5f5f5"

RR_LOGO_SVG_PATH = os.path.join(
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
            if resp.status != 200:
                return None
            return resp.read().decode("utf-8")
    except Exception:
        return None


# --- Shared helpers -----------------------------------------------------------

def ecr_pct(value: float) -> float:
    return value * 100


def parse_number(s: str) -> float | None:
    """table_records figures are comma-formatted with no unit, e.g. '126,192'."""
    try:
        return float(s.replace(",", "").replace("%", ""))
    except (ValueError, AttributeError):
        return None


def clean_archive_text(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_graph_ecr(svg_text: str, node_title: str = "EconomicCapitalRatio") -> float | None:
    """Graphviz splits a node's visible label across multiple <text>
    elements inside one <g class="node">...<title>NAME</title>...</g>
    block (titles have spaces stripped even though labels don't) — find
    that block, then the last percentage-shaped <text> inside it. See
    context/company-report-design.md § Causal graph SVG parsing."""
    pattern = re.compile(
        r"<title>" + re.escape(node_title) + r"</title>(.*?)</g>", re.DOTALL
    )
    match = pattern.search(svg_text)
    if not match:
        return None
    texts = re.findall(r">([^<]+)</text>", match.group(1))
    for t in reversed(texts):
        t = t.strip()
        if re.match(r"^-?\d+\.?\d*%$", t):
            return float(t.rstrip("%"))
    return None


def wrapped_text(ax, text: str, width: int = 86, fontsize: int = 11.5):
    ax.axis("off")
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


def load_svg_array(svg_text_or_path: str, height_px: int = 90, is_url_content=False):
    if is_url_content:
        png_bytes = cairosvg.svg2png(bytestring=svg_text_or_path.encode("utf-8"), output_height=height_px)
    else:
        png_bytes = cairosvg.svg2png(url=svg_text_or_path, output_height=height_px)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


# --- Stage 2: candidate sections ----------------------------------------------

def sec_overview_requires(data, company, extra):
    return True


def sec_overview_chart(ax, data, company, extra):
    ax.axis("off")
    logo_svg = extra.get("company_logo_svg")
    if logo_svg:
        try:
            logo = load_svg_array(logo_svg, height_px=110, is_url_content=True)
            inset = ax.inset_axes([0.35, 0.15, 0.3, 0.75])
            inset.imshow(logo)
            inset.axis("off")
        except Exception:
            pass


def sec_overview_text(data, company, extra):
    avg = sum(ecr_pct(c["value"]) for c in data["company_details"]) / len(data["company_details"])
    ecr = ecr_pct(company["value"])
    status = "Top-Rated" if company.get("top_rated") else "Not Top-Rated"
    trend = company.get("trend")
    trend_word = "improved" if (trend and trend > 0) else "declined" if (trend and trend < 0) else "held flat"
    return (
        f"{company['name']} ranks #{company['rank']} of {len(data['company_details'])} in "
        f"{data.get('industry_label', 'this industry')} for {data.get('year')}, with an ECR "
        f"of {ecr:.1f}% against an industry average of {avg:.1f}%. Status: {status}. "
        f"Trend this cycle: {trend_word} (sign convention unverified — see Caveats)."
    )


def sec_causal_requires(data, company, extra):
    return extra.get("causal_svg") is not None


def sec_causal_chart(ax, data, company, extra):
    ax.axis("off")
    try:
        img = load_svg_array(extra["causal_svg"], height_px=500, is_url_content=True)
        inset = ax.inset_axes([0.5 - 0.35, 0.0, 0.7, 1.0])
        inset.imshow(img)
        inset.axis("off")
    except Exception:
        ax.text(0.5, 0.5, "Graph failed to render", ha="center", transform=ax.transAxes)


def sec_causal_text(data, company, extra):
    headline = ecr_pct(company["value"])
    graph_ecr = extra.get("graph_ecr")
    base = (
        f"RealRate's own causal graph for {company['name']} — each edge is that "
        f"variable's percentage-point contribution to Economic Capital Ratio."
    )
    if graph_ecr is not None and abs(graph_ecr - headline) > 0.5:
        return base + (
            f"\n\nDiscrepancy: the graph's own ECR node reads {graph_ecr:.1f}%, while the "
            f"headline figure used elsewhere in this report is {headline:.1f}% "
            f"(company_details.value × 100). Both come directly from RealRate for the same "
            f"company and year — this report does not attempt to reconcile them. Verify "
            f"which applies before using either externally."
        )
    return base


def sec_strengths_requires(data, company, extra):
    return bool(company.get("report_text"))


def sec_strengths_chart(ax, data, company, extra):
    ax.axis("off")


def sec_strengths_text(data, company, extra):
    quote = clean_archive_text(company["report_text"])
    if len(quote) > 700:
        quote = quote[:700].rsplit(".", 1)[0] + "."
    return f'RealRate\'s own analysis of {company["name"]}:\n\n"{quote}"'


def sec_balance_sheet_requires(data, company, extra):
    return bool(company.get("table_records"))


def _latest_year_vars(company):
    years = sorted(company["table_records"].keys())
    latest = years[-1]
    return latest, company["table_records"][latest].get("output_variables", {})


def sec_balance_sheet_chart(ax, data, company, extra):
    style_axes(ax)
    _, out_vars = _latest_year_vars(company)
    labels, values = [], []
    for label, raw in out_vars.items():
        if "%" in raw:
            continue
        v = parse_number(raw)
        if v is not None:
            labels.append(label)
            values.append(v)
    if not values:
        ax.axis("off")
        return
    ax.barh(labels, values, color=PRIMARY)
    ax.set_xlabel("Reported value (unit not specified in payload)")


def sec_balance_sheet_text(data, company, extra):
    latest, out_vars = _latest_year_vars(company)
    return (
        f"Balance sheet output figures for fiscal year {latest}, as reported by RealRate's "
        f"archive. No currency unit is specified in the payload (not thousands, millions, "
        f"or dollars explicitly) — treat magnitudes as relative to each other within this "
        f"chart, not as absolute dollar figures, until confirmed against the source report: "
        f"{company.get('report_url', 'not available')}."
    )


def sec_ecr_history_requires(data, company, extra):
    records = data.get("ecr_records", {})
    cid = company["company_id"]
    years_present = [y for y, cos in records.items() if cid in cos]
    return len(years_present) >= 3


def _company_ecr_series(data, company):
    records = data.get("ecr_records", {})
    cid = company["company_id"]
    series = [(int(y), float(records[y][cid]["ecr"])) for y in sorted(records.keys()) if cid in records[y]]
    return series


def sec_ecr_history_chart(ax, data, company, extra):
    style_axes(ax)
    series = _company_ecr_series(data, company)
    years = [y for y, _ in series]
    vals = [v for _, v in series]
    ax.plot(years, vals, color=PRIMARY, marker="o", linewidth=2)
    ax.set_xticks(years)
    ax.set_xlabel("Year")
    ax.set_ylabel("ECR %")


def sec_ecr_history_text(data, company, extra):
    series = _company_ecr_series(data, company)
    first_year, first_val = series[0]
    last_year, last_val = series[-1]
    direction = "risen" if last_val > first_val else "fallen" if last_val < first_val else "held steady"
    return (
        f"{company['name']}'s ECR has {direction} from {first_val:.1f}% in {first_year} to "
        f"{last_val:.1f}% in {last_year}, across {len(series)} years on record."
    )


def sec_peer_requires(data, company, extra):
    return len(data["company_details"]) >= 2


def sec_peer_chart(ax, data, company, extra):
    style_axes(ax)
    companies = sorted(data["company_details"], key=lambda c: c["rank"])
    avg = sum(ecr_pct(c["value"]) for c in companies) / len(companies)
    leader = companies[0]
    labels = ["Industry Average", company["name"][:20]]
    values = [avg, ecr_pct(company["value"])]
    colors = [SECONDARY, PRIMARY]
    if leader["company_id"] != company["company_id"]:
        labels.append(f"#1 {leader['name'][:20]}")
        values.append(ecr_pct(leader["value"]))
        colors.append("#0a4a6e")
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("ECR %")


def sec_peer_text(data, company, extra):
    companies = sorted(data["company_details"], key=lambda c: c["rank"])
    avg = sum(ecr_pct(c["value"]) for c in companies) / len(companies)
    gap = ecr_pct(company["value"]) - avg
    direction = "above" if gap >= 0 else "below"
    return (
        f"{company['name']} sits {abs(gap):.1f} points {direction} the "
        f"{len(companies)}-company industry average of {avg:.1f}%, at rank "
        f"#{company['rank']}."
    )


def sec_caveats_requires(data, company, extra):
    return True


def sec_caveats_chart(ax, data, company, extra):
    ax.axis("off")
    rows = [
        ("ECR scale (value × 100)", "Confirmed", POSITIVE),
        ("Marketing year vs. balance sheet year", "Confirmed", POSITIVE),
        ("trend sign convention", "Unverified", NEGATIVE),
        ("Causal graph ECR vs. headline ECR", "Confirmed mismatch", NEGATIVE),
        ("Balance sheet figure units", "Unspecified in payload", NEGATIVE),
    ]
    for i, (label, status, color) in enumerate(rows):
        y = 0.82 - i * 0.18
        ax.text(0.02, y, label, fontsize=10.5, color=NAVY, transform=ax.transAxes)
        ax.text(0.62, y, status, fontsize=10.5, color=color, weight="bold", transform=ax.transAxes)


def sec_caveats_text(data, company, extra):
    return (
        "This report states only what has been checked against live archive responses "
        "for this company. The causal-graph/headline ECR mismatch and the unlabeled "
        "balance-sheet units are not resolved here — they're surfaced so a human can "
        "check them, per this project's standing rule to verify data before publishing."
    )


def sec_takeaway_requires(data, company, extra):
    return True


def sec_takeaway_chart(ax, data, company, extra):
    ax.axis("off")


def sec_takeaway_text(data, company, extra):
    industry_id = data.get("industry_id", "")
    year = data.get("year")
    report_url = company.get("report_url", "not available")
    return (
        f"{company['name']} — RealRate rank #{company['rank']} in "
        f"{data.get('industry_label', 'this industry')}, {year} marketing cycle.\n\n"
        f"RealRate's full company report: {report_url}\n\n"
        f"Full industry ranking: https://realrate.ai/rankings/{industry_id}/{year}"
    )


SECTION_REGISTRY = [
    {"title": "Company Overview", "requires": sec_overview_requires,
     "chart": sec_overview_chart, "text": sec_overview_text},
    {"title": "Causal ECR Graph", "requires": sec_causal_requires,
     "chart": sec_causal_chart, "text": sec_causal_text},
    {"title": "Strengths & Weaknesses", "requires": sec_strengths_requires,
     "chart": sec_strengths_chart, "text": sec_strengths_text},
    {"title": "Balance Sheet Snapshot", "requires": sec_balance_sheet_requires,
     "chart": sec_balance_sheet_chart, "text": sec_balance_sheet_text},
    {"title": "Multi-Year ECR History", "requires": sec_ecr_history_requires,
     "chart": sec_ecr_history_chart, "text": sec_ecr_history_text},
    {"title": "Peer Comparison", "requires": sec_peer_requires,
     "chart": sec_peer_chart, "text": sec_peer_text},
    {"title": "Data Confidence & Caveats", "requires": sec_caveats_requires,
     "chart": sec_caveats_chart, "text": sec_caveats_text},
    {"title": "Takeaway & Full Report", "requires": sec_takeaway_requires,
     "chart": sec_takeaway_chart, "text": sec_takeaway_text},
]


# --- Stage 3: RENDER -----------------------------------------------------------

def render_cover(pdf: PdfPages, company: dict, industry_display: str, year: int, num_sections: int):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    logo = load_svg_array(RR_LOGO_SVG_PATH, height_px=80)
    logo_ax = fig.add_axes([0.5 - 0.16, 0.74, 0.32, 0.32 * logo.height / logo.width])
    logo_ax.imshow(logo)
    logo_ax.axis("off")

    fig.text(0.5, 0.62, company["name"], ha="center", fontsize=24, weight="bold", color=NAVY,
              wrap=True)
    fig.text(0.5, 0.56, "COMPANY REPORT", ha="center", fontsize=20, weight="bold", color=SECONDARY)
    fig.text(0.5, 0.50, f"US {industry_display.upper()}  ·  {year} Marketing Cycle  ·  "
                         f"{num_sections} sections", ha="center", fontsize=12, color=NAVY)
    fig.text(0.5, 0.08, "Powered by RealRate: Using Explainable Financial AI",
              ha="center", fontsize=10, color="#888888")
    fig.text(0.5, 0.05, f"Generated {datetime.date.today().isoformat()}",
              ha="center", fontsize=9, color="#aaaaaa")
    pdf.savefig(fig)
    plt.close(fig)


def render_section(pdf: PdfPages, index: int, total: int, title: str, chart_fn, text: str,
                    data: dict, company: dict, extra: dict):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    fig.text(0.08, 0.95, f"{index:02d} / {total:02d}", fontsize=10, color=SECONDARY, weight="bold")
    fig.text(0.08, 0.91, title, fontsize=20, weight="bold", color=NAVY)

    ax_chart = fig.add_axes([0.24, 0.46, 0.66, 0.40])
    chart_fn(ax_chart, data, company, extra)

    ax_text = fig.add_axes([0.08, 0.06, 0.84, 0.32])
    wrapped_text(ax_text, text)

    pdf.savefig(fig)
    plt.close(fig)


def generate_for_company(data: dict, company: dict, slug: str, industry_display: str, year: int) -> str:
    """Builds one company's PDF and returns its path. Isolated from main()
    so `company == "all"` can call this once per company in a loop without
    duplicating the render pipeline."""
    extra = {"graph_ecr": None, "causal_svg": None, "company_logo_svg": None}
    causal_svg = fetch_svg(company["graph_url"]) if company.get("graph_url") else None
    if causal_svg:
        extra["causal_svg"] = causal_svg
        extra["graph_ecr"] = parse_graph_ecr(causal_svg)
    if company.get("logo_url"):
        extra["company_logo_svg"] = fetch_svg(company["logo_url"])

    qualifying = [s for s in SECTION_REGISTRY if s["requires"](data, company, extra)]
    skipped = [s["title"] for s in SECTION_REGISTRY if s not in qualifying]

    company_slug = re.sub(r"[^a-z0-9]+", "_", company["name"].lower()).strip("_")
    out_dir = os.path.join(os.getcwd(), "output", f"us_{slug}", SKILL_NAME)
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, f"{company_slug}_{year}_report.pdf")

    with PdfPages(pdf_path) as pdf:
        render_cover(pdf, company, industry_display, year, len(qualifying))
        for i, section in enumerate(qualifying, start=1):
            text = section["text"](data, company, extra)
            render_section(pdf, i, len(qualifying), section["title"], section["chart"], text,
                            data, company, extra)

    print(f"Wrote {pdf_path}")
    print(f"  Sections included ({len(qualifying)}/{len(SECTION_REGISTRY)}): "
          + ", ".join(s["title"] for s in qualifying))
    if skipped:
        print(f"  Sections skipped (data not available this run): {', '.join(skipped)}")
    if extra["graph_ecr"] is not None and abs(extra["graph_ecr"] - ecr_pct(company["value"])) > 0.5:
        print(f"  NOTE: causal graph ECR ({extra['graph_ecr']:.1f}%) does not match headline "
              f"ECR ({ecr_pct(company['value']):.1f}%) — see Causal ECR Graph / Caveats sections.")
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Practice: generate a RealRate company report PDF.")
    parser.add_argument("industry", help="Industry slug or name, e.g. 'air' or 'US Air'")
    parser.add_argument("company", help="Company rank (e.g. '1'), a name substring (e.g. 'strata'), "
                                         "or 'all' to generate one report per company in the industry")
    parser.add_argument("--year", type=int, default=None, help="Override the archive year to fetch")
    args = parser.parse_args()

    slug = resolve_slug(args.industry)
    industry_display = INDUSTRY_SLUGS[slug]

    data = fetch_ranking_data(slug, args.year)
    year = data.get("year")

    if args.company.strip().lower() == "all":
        companies = sorted(data["company_details"], key=lambda c: c["rank"])
        print(f"Generating company reports for all {len(companies)} companies in {industry_display}...")
        failures = []
        for company in companies:
            try:
                generate_for_company(data, company, slug, industry_display, year)
            except Exception as e:
                print(f"  FAILED for {company['name']} (rank {company['rank']}): {e}")
                failures.append(company["name"])
        print(f"Done: {len(companies) - len(failures)}/{len(companies)} reports generated.")
        if failures:
            print(f"Failed: {', '.join(failures)}")
        return

    company = resolve_company(data, args.company)
    generate_for_company(data, company, slug, industry_display, year)


if __name__ == "__main__":
    main()
