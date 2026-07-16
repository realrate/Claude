---
name: top10ranking
description: Generate a RealRate "Top 10" ranking LinkedIn post for an industry — a 1200x1500 infographic PNG plus a matching LinkedIn caption .txt, pulled live from realrate-archive.com. Use whenever asked to create/generate a top 10 ranking, industry ranking post, or LinkedIn infographic for an industry (e.g. "make the top 10 software ranking post", "generate this year's motor industry ranking", "do the air rankings"), even if only the industry is named.
version: 1.0.0
---

# RealRate Top 10 Ranking Generator

Generates a 1200x1500 px portrait LinkedIn infographic plus a matching LinkedIn caption for a
RealRate industry "Top 10" ranking, using live data fetched from realrate-archive.com.

This skill is fully self-contained: the generator script, Manrope fonts, and a fallback
RealRate logo all live inside this skill folder (`scripts/`, `assets/`). It does not read or
depend on any other file in the surrounding repo — you can copy this `top10ranking/` folder
into any project's `.claude/skills/` directory and it works standalone. The full source of
`scripts/generate_infographic.py` is also embedded verbatim at the bottom of this file, so
this single `top10ranking.md` document fully describes and contains everything the skill does.

## Setup (first run only)

```bash
pip install -r "${CLAUDE_PROJECT_DIR}/.claude/skills/top10ranking/requirements.txt"
```

## Generate a ranking

```bash
python "${CLAUDE_PROJECT_DIR}/.claude/skills/top10ranking/scripts/generate_infographic.py" <industry_slug>
```

This produces both output files together — never generate just the PNG or just the caption:

- `${CLAUDE_PROJECT_DIR}/output/<slug>_<year>.png` — the infographic
- `${CLAUDE_PROJECT_DIR}/output/linkedin_<slug>_<year>.txt` — the matching LinkedIn caption

Output always lands in `output/` at the root of whichever project the skill is run from
(`$CLAUDE_PROJECT_DIR`, falling back to the current working directory) — never inside this
skill folder.

If the user names an industry (e.g. "motor", "software", "air"), map it to the closest slug
below and run the command. If it's ambiguous, ask which slug before running.

## Available slugs

`air` · `motor` · `software` · `computers` · `finance_services` · `food` · `health_services` ·
`advertising` · `semiconductors` · `programming` · `petrol` · `mining` · `construction` ·
`realestate` · `hotels` · `consulting` · `data_processing` · `brokers` · `savings` ·
`life` · `non_life` · `pharma` · `chemicals` · `state_banks` · `medicinal_products` · `recreation`

## Behavior notes

- Data source is archive-first: the script fetches live from realrate-archive.com. Cards show
  ECR%, a ★ TOP RATED badge where applicable, and trend arrows.
- Ranking links in the caption always use the `us_` prefix: `https://realrate.ai/rankings/us_<industry>/<year>`.
- Every industry gets a unique blue-tone accent and themed background pattern — accent colors
  must stay in the blue family even when the pattern differs per industry.
- Title, filename, and ranking URL use the current calendar year; the archive fetch itself uses
  the latest year available in the archive listing.
- Fonts and the RealRate logo fallback are bundled in `assets/` — no network access is required
  for those. Company logos are still fetched live per-run (Clearbit, logo.dev, Wikipedia, etc.)
  and cached under `assets/logos/` inside this skill folder between runs.

## After generating

Report the output file paths and confirm both the PNG and the caption .txt were created.

## Full script source (`scripts/generate_infographic.py`)

The script bundled at `scripts/generate_infographic.py` (used by the command above) is
reproduced verbatim below, so this skill's full behavior is documented in one place.

```python
#!/usr/bin/env python3
"""
RealRate Infographic Generator
================================
Generates a 1200x1500 LinkedIn infographic from realrate-archive.com or a spreadsheet.

Usage (archive — preferred):
    python generate_infographic.py <industry_slug> [title] [subtitle] [output.png]
    python generate_infographic.py air
    python generate_infographic.py motor "TOP 10 US MOTOR COMPANIES 2025"

Usage (spreadsheet — legacy):
    python generate_infographic.py <spreadsheet.xlsx> [title] [subtitle] [output.png]

Available industry slugs: air, motor, software, computers, finance_services, food,
    health_services, advertising, semiconductors, programming, petrol, mining,
    construction, realestate, hotels, consulting, data_processing, brokers, savings,
    life, non_life, pharma, chemicals, state_banks, medicinal_products, recreation
"""

import datetime
import os
import sys
import io
import re
import math
import random
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import json
import requests

# Fix Unicode output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pandas as pd
from pathlib import Path
from contextlib import contextmanager
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Optional SVG support
try:
    import cairosvg
    HAS_CAIRO = True
except (ImportError, OSError):
    HAS_CAIRO = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    HAS_SVGLIB = True
except (ImportError, OSError, Exception):
    HAS_SVGLIB = False


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

IMG_W = 1200
IMG_H = 1500

PAD          = 33    # outer padding (px)
COL_GAP      = 22    # horizontal gap between two card columns
HEADER_H     = 290   # header card height
HEADER_GAP   = 46    # gap between header card and first card row
CARD_H       = 190   # height of each ranking card
CARD_GAP     = 18    # vertical gap between ranking cards
FOOTER_OFFSET= 28    # gap between last card and footer line

ACCENT_BAR_W = 7     # left accent stripe width inside card
RANK_R       = 26    # rank badge circle radius
LOGO_BOX_SZ  = 122   # logo container square size (px)
LOGO_BOX_R   = 13    # logo container corner radius
LOGO_MAX     = 113   # max logo dimension inside container
LOGO_PAD     = 4     # padding inside logo container

# ── Brand palette ─────────────────────────────────────────────────────────────
BG         = ( 10,  15,  30)   # Deep navy/dark background
WHITE      = (255, 255, 255)
DARK_BLUE  = (  0, 103, 155)   # #00679B
ACCENT     = ( 61, 186, 205)   # #3DBACD
NEON_CYAN  = (  0, 224, 255)   # Bright neon cyan
NEON_BLUE  = ( 60, 120, 255)   # Electric blue
CARD_BG    = ( 18,  26,  50)   # Card dark background
CARD_BG_LT = ( 25,  35,  65)   # Slightly lighter card bg
BORDER     = ( 40,  60, 100)   # Subtle blue-grey border
BLACK      = (  0,   0,   0)
GREY       = (140, 155, 180)   # Blue-tinted grey
DARK_GREY  = ( 74,  74,  74)   # #4A4A4A
GLOW_CYAN  = (  0, 200, 240)   # Glow color

# ── Paths ─────────────────────────────────────────────────────────────────────
# BASE_DIR is the skill's own root (this file lives in <skill_root>/scripts/), so all
# bundled assets (fonts, logo fallback) resolve from inside the skill — never from the
# caller's project. OUTPUT_DIR is the one exception: generated files land in the
# invoking project, not inside the skill folder.
BASE_DIR   = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()) / "output"

_ARCHIVE_BASE = "https://realrate-archive.com"

DEFAULT_SUBTITLE = "RealRate Financial Health Ranking based on Economic Capital Ratio"

_INDUSTRY_META = {
    "air":               ("TOP 10 US AIR COMPANIES",                "air"),
    "motor":             ("TOP 10 US MOTOR COMPANIES",              "motor"),
    "software":          ("TOP 10 US SOFTWARE COMPANIES",           "software"),
    "computers":         ("TOP 10 US COMPUTER COMPANIES",           "computers"),
    "finance_services":  ("TOP 10 US FINANCE SERVICES COMPANIES",   "finance_services"),
    "food":              ("TOP 10 US FOOD COMPANIES",               "food"),
    "health_services":   ("TOP 10 US HEALTH SERVICES COMPANIES",    "health_services"),
    "advertising":       ("TOP 10 US ADVERTISING COMPANIES",        "advertising"),
    "semiconductors":    ("TOP 10 US SEMICONDUCTOR COMPANIES",      "semiconductors"),
    "programming":       ("TOP 10 US PROGRAMMING COMPANIES",        "programming"),
    "petrol":            ("TOP 10 US PETROL COMPANIES",             "petrol"),
    "mining":            ("TOP 10 US MINING COMPANIES",             "mining"),
    "construction":      ("TOP 10 US CONSTRUCTION COMPANIES",       "construction"),
    "realestate":        ("TOP 10 US REAL ESTATE COMPANIES",        "realestate"),
    "hotels":            ("TOP 10 US HOTEL COMPANIES",              "hotels"),
    "consulting":        ("TOP 10 US CONSULTING COMPANIES",         "consulting"),
    "data_processing":   ("TOP 10 US DATA PROCESSING COMPANIES",    "data_processing"),
    "brokers":           ("TOP 10 US BROKERS",                      "brokers"),
    "savings":           ("TOP 10 US SAVINGS COMPANIES",            "savings"),
    "life":              ("TOP 10 US LIFE INSURANCE COMPANIES",     "life"),
    "non_life":          ("TOP 10 US NON-LIFE INSURANCE COMPANIES", "non_life"),
    "pharma":            ("TOP 10 US PHARMA COMPANIES",             "pharma"),
    "chemicals":         ("TOP 10 US CHEMICAL COMPANIES",           "chemicals"),
    "state_banks":       ("TOP 10 US STATE BANKS",                  "state_banks"),
    "medicinal_products":("TOP 10 US MEDICINAL PRODUCTS COMPANIES", "medicinal_products"),
    "recreation":        ("TOP 10 US RECREATION COMPANIES",         "recreation"),
    "spacs":             ("TOP 10 US SPACS",                        "spacs"),
}

REALRATE_SVG_URLS = [
    "https://realrate.ai/wp-content/uploads/2025/10/RealRate_logo_vertical.svg",
    "https://realrate.ai/wp-content/uploads/2025/10/RealRate_logo_horizontal.svg",
    "https://realrate.ai/wp-content/uploads/2025/10/RealRate_logo_light.svg",
]

FONT_VARIANTS = {
    "regular":   ("Manrope:wght@400", "manrope-400.ttf"),
    "medium":    ("Manrope:wght@500", "manrope-500.ttf"),
    "bold":      ("Manrope:wght@700", "manrope-700.ttf"),
    "extrabold": ("Manrope:wght@800", "manrope-800.ttf"),
}

WIN_FALLBACKS = {
    "regular":   [r"C:\Windows\Fonts\calibri.ttf",  r"C:\Windows\Fonts\arial.ttf"],
    "medium":    [r"C:\Windows\Fonts\calibri.ttf",  r"C:\Windows\Fonts\arial.ttf"],
    "bold":      [r"C:\Windows\Fonts\calibrib.ttf", r"C:\Windows\Fonts\arialbd.ttf"],
    "extrabold": [r"C:\Windows\Fonts\calibrib.ttf", r"C:\Windows\Fonts\arialbd.ttf"],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

_LOG_LOCK = threading.Lock()

def _log(msg: str, **kwargs) -> None:
    """Thread-safe print."""
    with _LOG_LOCK:
        print(msg, **kwargs)


# ══════════════════════════════════════════════════════════════════════════════
#  FONT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _download_ttf(family_spec: str, dest: Path) -> bool:
    """Download Manrope TTF via Google Fonts CSS."""
    css_url = f"https://fonts.googleapis.com/css2?family={family_spec}&display=swap"
    # A legacy user-agent causes Google Fonts to serve TTF instead of woff2,
    # which is required because PIL's ImageFont cannot load woff2 files.
    ttf_ua = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"}
    try:
        r = requests.get(css_url, headers=ttf_ua, timeout=12)
        r.raise_for_status()
        matches = re.findall(r"url\(([^)]+\.ttf)\)", r.text)
        if not matches:
            return False
        font_url = matches[0].strip("'\"")
        fr = requests.get(font_url, headers=HEADERS, timeout=15)
        fr.raise_for_status()
        dest.write_bytes(fr.content)
        return True
    except Exception as exc:
        print(f"    [warn] {exc}")
        return False


def ensure_fonts() -> dict:
    """Download Manrope variants; fall back to Windows system fonts."""
    font_dir = ASSETS_DIR / "fonts"
    font_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for key, (spec, fname) in FONT_VARIANTS.items():
        dest = font_dir / fname
        if not dest.exists():
            print(f"  Downloading Manrope {key} …")
            _download_ttf(spec, dest)
        if dest.exists():
            result[key] = dest
        else:
            for fb in WIN_FALLBACKS.get(key, []):
                if Path(fb).exists():
                    result[key] = Path(fb)
                    break
            else:
                result[key] = None
    return result


def pil_font(path, size: int) -> ImageFont.FreeTypeFont:
    if path and Path(path).exists():
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            pass
    return ImageFont.load_default()


# ══════════════════════════════════════════════════════════════════════════════
#  SVG → PIL
# ══════════════════════════════════════════════════════════════════════════════

@contextmanager
def _tmp_svg(data: bytes):
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        f.write(data)
        name = f.name
    try:
        yield name
    finally:
        try:
            os.unlink(name)
        except OSError:
            pass


def svg_to_pil(svg_bytes: bytes, width: int = 1024) -> "Image.Image | None":
    if HAS_CAIRO:
        try:
            png = cairosvg.svg2png(bytestring=svg_bytes, output_width=width)
            return Image.open(io.BytesIO(png)).convert("RGBA")
        except Exception as e:
            print(f"    [cairosvg] {e}")

    if HAS_SVGLIB:
        try:
            with _tmp_svg(svg_bytes) as tmp:
                drawing = svg2rlg(tmp)
                if drawing:
                    scale = width / drawing.width
                    drawing.width  = width
                    drawing.height = drawing.height * scale
                    drawing.transform = (scale, 0, 0, scale, 0, 0)
                    png_data = renderPM.drawToString(drawing, fmt="PNG")
                    return Image.open(io.BytesIO(png_data)).convert("RGBA")
        except Exception as e:
            print(f"    [svglib] {e}")

    return None


# ══════════════════════════════════════════════════════════════════════════════
#  LOGO FETCHING
# ══════════════════════════════════════════════════════════════════════════════

def _get(url: str, timeout: int = 14) -> "bytes | None":
    for attempt in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                return r.content
            if r.status_code < 500:
                break  # 4xx won't improve on retry
        except requests.exceptions.Timeout:
            pass  # retry once on timeout
        except Exception:
            break
    return None


def _archive_get(url: str, timeout: int = 20) -> "bytes | None":
    """GET for realrate-archive.com which uses a self-signed TLS certificate."""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass
    return None


def get_realrate_logo() -> "Image.Image | None":
    # The skill bundles its own fallback at assets/realrate_logo.png, so this
    # doubles as both the "already resolved" cache and the manually-placed override.
    cache = ASSETS_DIR / "realrate_logo.png"
    if cache.exists():
        try:
            return Image.open(cache).convert("RGBA")
        except Exception:
            pass

    # ── 1. Check for a logo placed under assets/ with a different extension ───
    for ext in ("png", "jpg", "jpeg", "svg"):
        manual = ASSETS_DIR / f"realrate_logo.{ext}"
        if manual.exists():
            if ext == "svg":
                img = svg_to_pil(manual.read_bytes(), 600)
            else:
                img = Image.open(manual).convert("RGBA")
            if img:
                img.save(cache)
                return img

    # ── 2. Download from realrate.ai ──────────────────────────────────────────
    print("  Fetching RealRate logo from realrate.ai …")
    for url in REALRATE_SVG_URLS:
        data = _get(url)
        if not data:
            continue
        if url.lower().endswith(".svg"):
            img = svg_to_pil(data, 600)
        else:
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
            except Exception:
                continue
        if img:
            img.save(cache)
            print(f"    ✓ {url.split('/')[-1]}")
            return img

    print("    ✗ Place realrate_logo.png (or .svg) in the assets/ folder manually.")
    return None


def _clean_company_name(name: str) -> str:
    """Strip legal suffixes, state codes, and normalise casing for better lookups."""
    # Common legal suffixes (order matters — longer first)
    suffixes = [
        r'\bHoldings\b', r'\bGroup\b', r'\bCorporation\b', r'\bIncorporated\b',
        r'\bLimited\b', r'\bCompany\b', r'\bEnterprises\b', r'\bInternational\b',
        r'\bTechnologies\b', r'\bSolutions\b',
        r'\bCORP\b', r'\bINC\b', r'\bLTD\b', r'\bLLC\b', r'\bLP\b',
        r'\bPLC\b', r'\bNV\b', r'\bSA\b', r'\bAG\b', r'\bSE\b',
        r'\bCO\b',
    ]
    cleaned = name
    for suf in suffixes:
        cleaned = re.sub(suf, '', cleaned, flags=re.IGNORECASE)
    # Remove trailing US state codes (1-2 uppercase letters at end, e.g. "DE", "MA")
    cleaned = re.sub(r'\s+[A-Z]{1,2}\s*$', '', cleaned.strip())
    # Collapse whitespace and strip
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


_NAME_STOP_WORDS = {
    'inc', 'corp', 'ltd', 'llc', 'co', 'lp', 'plc', 'nv', 'sa', 'ag', 'se',
    'the', 'and', 'of', 'technologies', 'technology', 'solutions', 'holdings',
    'group', 'international', 'enterprises', 'company', 'limited', 'incorporated',
    'corporation', 'software', 'systems', 'services', 'digital', 'media',
}


def _name_key_words(s: str) -> set:
    """Extract meaningful words from a company name for comparison."""
    words = set(re.sub(r'[^a-z0-9\s]', ' ', s.lower()).split())
    return {w for w in words if w not in _NAME_STOP_WORDS and len(w) > 1}


def _names_match(query: str, candidate: str, threshold: float = 0.5) -> bool:
    """Return True if candidate company name is a sufficient match for query."""
    q_words = _name_key_words(query)
    c_words = _name_key_words(candidate)
    if not q_words:
        return True
    return len(q_words & c_words) / len(q_words) >= threshold


def _search_domain(query: str) -> "str | None":
    """Look up a company domain via Clearbit autocomplete, verifying name match."""
    try:
        r = requests.get(
            "https://autocomplete.clearbit.com/v1/companies/suggest",
            params={"query": query}, timeout=8
        )
        if r.status_code == 200:
            hits = r.json()
            for hit in hits[:3]:
                if _names_match(query, hit.get("name", "")):
                    return hit["domain"]
    except Exception:
        pass
    return None


def _try_clearbit_logo(domain: str, cache: Path) -> "Image.Image | None":
    data = _get(f"https://logo.clearbit.com/{domain}?size=2048&format=png")
    if data and len(data) > 1500:
        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            if min(img.size) < 64:
                return None
            extrema = img.convert("RGB").getextrema()
            if all(lo == hi for lo, hi in extrema):
                return None  # solid-colour placeholder
            img.save(cache)
            return img
        except Exception:
            pass
    return None


_BAD_IMG_NAMES = {
    "commons-logo", "wikimedia", "edit-clear", "commons_logo",
    "mediawiki", "wikidata", "openstreetmap", "free_software",
    "question_mark", "replace_this", "missing",
}

def _try_wikipedia_logo(query: str, cache: Path) -> "Image.Image | None":
    """Fetch company logo from Wikipedia using Search + Images APIs."""
    # Step 1 — find the correct article title via Wikipedia search API
    try:
        sr = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": query,
                    "format": "json", "srlimit": 3},
            headers=HEADERS, timeout=8,
        )
        results = sr.json().get("query", {}).get("search", []) if sr.ok else []
        # Verify the top result actually matches the company before using it
        wiki_title = query
        for res in results[:3]:
            if _names_match(query, res["title"]):
                wiki_title = res["title"]
                break
    except Exception:
        wiki_title = query

    # Step 2 — list images on that article, filter for logo files
    try:
        ir = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "titles": wiki_title,
                    "prop": "images", "imlimit": "40", "format": "json"},
            headers=HEADERS, timeout=8,
        )
        if ir.ok:
            pages = ir.json().get("query", {}).get("pages", {})
            for page in pages.values():
                logo_files = [
                    img["title"] for img in page.get("images", [])
                    if "logo" in img["title"].lower()
                    and not any(b in img["title"].lower() for b in _BAD_IMG_NAMES)
                ]
                # Prefer vertical/stacked logos for crisp card display
                logo_files.sort(key=lambda t: (
                    0 if "vertical" in t.lower() else
                    1 if "stacked" in t.lower() else
                    2 if "wordmark" in t.lower() else 3
                ))
                for img_title in logo_files[:4]:
                    iinfo = requests.get(
                        "https://en.wikipedia.org/w/api.php",
                        params={"action": "query", "titles": img_title,
                                "prop": "imageinfo", "iiprop": "url",
                                "iiurlwidth": "1024", "format": "json"},
                        headers=HEADERS, timeout=8,
                    )
                    if not iinfo.ok:
                        continue
                    for ip in iinfo.json().get("query", {}).get("pages", {}).values():
                        ii = (ip.get("imageinfo") or [{}])[0]
                        orig_url = ii.get("url", "")
                        thumb_url = ii.get("thumburl") or orig_url
                        # Prefer SVG original for crisp rendering
                        if orig_url.lower().split("?")[0].endswith(".svg"):
                            svg_data = _get(orig_url)
                            if svg_data:
                                img = svg_to_pil(svg_data, 1024)
                                if img and min(img.size) >= 40:
                                    img.save(cache)
                                    return img
                        img_url = thumb_url
                        if not img_url:
                            continue
                        if any(b in img_url.lower() for b in _BAD_IMG_NAMES):
                            continue
                        data = _get(img_url)
                        if data and len(data) > 800:
                            try:
                                img = Image.open(io.BytesIO(data)).convert("RGBA")
                                if min(img.size) >= 40:
                                    img.save(cache)
                                    return img
                            except Exception:
                                pass
    except Exception:
        pass

    # Step 3 — HTML infobox fallback
    wiki_name = wiki_title.replace(" ", "_")
    html = _get(f"https://en.wikipedia.org/wiki/{wiki_name}", timeout=10)
    if html:
        text = html.decode("utf-8", errors="ignore")
        for pat in [
            r'<img[^>]+src="(//upload\.wikimedia\.org[^"]+(?:_logo|_Logo)[^"]*\.(?:png|svg\.png))"',
            r'<img[^>]+class="[^"]*infobox[^"]*"[^>]+src="(//upload\.wikimedia[^"]+)"',
        ]:
            for m in re.findall(pat, text):
                img_url = "https:" + m.split()[0]
                if any(b in img_url.lower() for b in _BAD_IMG_NAMES):
                    continue
                logo_data = _get(img_url)
                if logo_data:
                    try:
                        img = Image.open(io.BytesIO(logo_data)).convert("RGBA")
                        if min(img.size) >= 40:
                            img.save(cache)
                            return img
                    except Exception:
                        pass
    return None


def _try_logodev(domain: str, cache: Path) -> "Image.Image | None":
    data = _get(f"https://img.logo.dev/{domain}?token=pk_oIiuOc9PRGqFMJJdFJviqg&size=512&format=png")
    if data and len(data) > 500:
        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            if min(img.size) < 64:
                return None
            extrema = img.convert("RGB").getextrema()
            if all(lo == hi for lo, hi in extrema):
                return None  # solid-colour placeholder
            img.save(cache)
            return img
        except Exception:
            pass
    return None


def _try_brandfetch(domain: str, cache: Path) -> "Image.Image | None":
    """Try Brandfetch CDN for high-resolution logos."""
    for size in (512, 256):
        data = _get(f"https://cdn.brandfetch.io/{domain}/w/{size}/h/{size}")
        if data and len(data) > 1500:
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                if min(img.size) < 64:
                    continue
                extrema = img.convert("RGB").getextrema()
                if all(lo == hi for lo, hi in extrema):
                    continue  # solid-colour placeholder
                img.save(cache)
                return img
            except Exception:
                pass
    return None


def _try_uplead(domain: str, cache: Path) -> "Image.Image | None":
    """Try logo.uplead.com for high-quality company logos."""
    data = _get(f"https://logo.uplead.com/{domain}")
    if data and len(data) > 1500:
        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            if min(img.size) < 64:
                return None
            extrema = img.convert("RGB").getextrema()
            if all(lo == hi for lo, hi in extrema):
                return None  # solid-colour placeholder
            img.save(cache)
            return img
        except Exception:
            pass
    return None


def _try_realrate_archive(archive_logo_url: str, cache: Path) -> "Image.Image | None":
    """Fetch logo from RealRate archive by direct URL — most reliable for ranked companies."""
    data = _archive_get(archive_logo_url) if "realrate-archive.com" in archive_logo_url else _get(archive_logo_url)
    if data and len(data) > 500:
        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            if min(img.size) < 64:
                return None
            extrema = img.convert("RGB").getextrema()
            if all(lo == hi for lo, hi in extrema):
                return None
            img.save(cache)
            return img
        except Exception:
            pass
    return None


def _try_favicon(domain: str, cache: Path) -> "Image.Image | None":
    """Try multiple favicon services in descending quality order."""
    favicon_urls = [
        f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://{domain}&size=256",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
        f"https://icons.duckduckgo.com/ip3/{domain}.ico",
        f"https://{domain}/favicon.ico",
        f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
    ]
    best: "Image.Image | None" = None
    for url in favicon_urls:
        data = _get(url)
        if not data:
            continue
        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            if min(img.size) >= 64:
                if best is None or min(img.size) > min(best.size):
                    best = img
                    if min(img.size) >= 192:
                        break  # good enough
        except Exception:
            continue
    if best is not None:
        best.save(cache)
        return best
    return None


def _try_website_logo(domain: str, cache: Path) -> "Image.Image | None":
    """Last-resort: scrape homepage for vertical logo, then horizontal, then any logo img."""
    for scheme in ("https", "http"):
        html_data = _get(f"{scheme}://{domain}", timeout=10)
        if not html_data:
            continue
        text = html_data.decode("utf-8", errors="ignore")

        vertical, horizontal, other = [], [], []

        for m in re.findall(r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']', text, re.I):
            ml = m.lower()
            if "vertical" in ml:
                vertical.append(m)
            elif any(k in ml for k in ("horizontal", "wordmark", "wide")):
                horizontal.append(m)
            elif "logo" in ml:
                other.append(m)

        for m in re.findall(
            r'<img[^>]*(?:alt|class|id)=["\'][^"\']*vertical[^"\']*["\'][^>]*(?:src|data-src)=["\']([^"\']+)["\']',
            text, re.I):
            vertical.append(m)
        for m in re.findall(
            r'<img[^>]*(?:alt|class|id)=["\'][^"\']*(?:horizontal|wordmark)[^"\']*["\'][^>]*(?:src|data-src)=["\']([^"\']+)["\']',
            text, re.I):
            horizontal.append(m)
        for m in re.findall(
            r'<img[^>]*(?:alt|class|id)=["\'][^"\']*logo[^"\']*["\'][^>]*(?:src|data-src)=["\']([^"\']+)["\']',
            text, re.I):
            other.append(m)
        for m in re.findall(
            r'<link[^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
            text, re.I):
            other.append(m)

        for url in (vertical + horizontal + other):
            if url.startswith("data:"):
                continue
            if url.startswith("//"):
                url = f"{scheme}:{url}"
            elif url.startswith("/"):
                url = f"{scheme}://{domain}{url}"
            elif not url.startswith("http"):
                url = f"{scheme}://{domain}/{url}"
            if any(b in url.lower() for b in _BAD_IMG_NAMES):
                continue
            data = _get(url, timeout=8)
            if not data or len(data) < 800:
                continue
            try:
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                if min(img.size) >= 120:
                    img.save(cache)
                    return img
            except Exception:
                pass
    return None




_DOMAIN_HINTS = {
    "federal signal":        "federalsignal.com",
    "lci industries":        "lci1.com",
    "sps commerce":          "spscommerce.com",
    "progress software":     "progress.com",
    "grid dynamics":         "griddynamics.com",
    "harley-davidson":       "harley-davidson.com",
    "harley davidson":       "harley-davidson.com",
    "tesla":                 "tesla.com",
    "ameritek ventures":     "ameritekventures.com",
    "visteon":               "visteon.com",
    "leatt":                 "leatt.com",
    "gentex":                "gentex.com",
    "dorman products":       "dormanproducts.com",
    "appfolio":              "appfolio.com",
    "shopify":               "shopify.com",
    "intellicheck":          "intellicheck.com",
    "corecard":              "corecard.com",
    "destiny media":         "destinymedia.com",
    "federated hermes":      "federatedhermes.com",
    "bristow":               "bristowgroup.com",
    "allegiant":             "allegiantair.com",
    "strata critical":       "stratacritical.com",
    "angi inc":              "angi.com",
    "stran company":         "stranpromotional.com",
    "abrdn":                 "abrdn.com",
}


def _try_wikimedia_logo(name: str, cache: Path) -> "Image.Image | None":
    """Search Wikimedia Commons for a high-quality official company logo."""
    cleaned = _clean_company_name(name)
    name_words = _name_key_words(name)
    # Use full name queries only — single-word abbreviations cause wrong matches
    # Try vertical logo first, then general logo
    queries = list(dict.fromkeys([name, cleaned]))
    search_variants = []
    for q in queries:
        search_variants.append(f"{q} vertical logo")
        search_variants.append(f"{q} logo")
    for query_str in search_variants:
        try:
            params = {
                "action": "query",
                "generator": "search",
                "gsrnamespace": "6",
                "gsrsearch": query_str,
                "prop": "imageinfo",
                "iiprop": "url|size",
                "format": "json",
                "gsrlimit": "10",
            }
            r = requests.get(
                "https://commons.wikimedia.org/w/api.php",
                params=params, headers=HEADERS, timeout=12
            )
            if r.status_code != 200:
                continue
            pages = r.json().get("query", {}).get("pages", {})
            for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
                title = page.get("title", "").lower()
                # Skip Wikimedia/Commons own images and unrelated system images
                if any(b in title for b in _BAD_IMG_NAMES):
                    continue
                # Require at least one key company-name word in the file title
                if name_words and not any(w in title for w in name_words):
                    continue
                ii = (page.get("imageinfo") or [{}])[0]
                url = ii.get("url", "")
                if not url:
                    continue
                if any(b in url.lower() for b in _BAD_IMG_NAMES):
                    continue
                # Minimum size check from API metadata
                w = ii.get("width", 999)
                h = ii.get("height", 999)
                if w < 60 or h < 60:
                    continue
                ext = url.lower().split("?")[0].split(".")[-1]
                if ext not in ("png", "svg", "jpg", "jpeg"):
                    continue
                data = _get(url)
                if not data or len(data) < 800:
                    continue
                try:
                    if ext == "svg":
                        img = svg_to_pil(data, 512)
                    else:
                        img = Image.open(io.BytesIO(data)).convert("RGBA")
                    if img and min(img.size) > 60:
                        img.save(cache)
                        return img
                except Exception:
                    continue
        except Exception:
            pass
    return None


# Quality thresholds (px) for the logo pipeline
_ICON_QUALITY_MIN  = 128   # minimum usable icon size
_CACHE_REGEN_BELOW = 64    # re-fetch if cached logo is smaller than this
_ICON_EARLY_EXIT   = 256   # stop trying icon sources once one this large is found


def get_company_logo(name: str, hint_domain: str = None, archive_logo_url: str = None,
                     prefer_archive: bool = False) -> "Image.Image | None":
    logo_dir = ASSETS_DIR / "logos"
    logo_dir.mkdir(parents=True, exist_ok=True)
    safe  = re.sub(r"[^a-z0-9]", "_", name.lower())
    cache = logo_dir / f"{safe}.png"
    if cache.exists():
        try:
            img = Image.open(cache).convert("RGBA")
            # If cached logo is too small, delete and re-fetch at higher resolution
            if min(img.size) < _CACHE_REGEN_BELOW:
                cache.unlink(missing_ok=True)
            else:
                return img
        except Exception:
            pass

    # ── 0. Archive-preferred: try direct archive URL first (JSON mode) ─────────
    if prefer_archive and archive_logo_url:
        img = _try_realrate_archive(archive_logo_url, cache)
        if img:
            _log(f"  Logo → {name}: ✓ RealRate archive (direct)")
            return img

    cleaned = _clean_company_name(name)
    wiki_queries = list(dict.fromkeys([name, cleaned]))

    # ── 0b. Resolve domain ───────────────────────────────────────────────────
    domain = hint_domain
    if not domain:
        name_lower = name.lower()
        for hint_key, hint_val in _DOMAIN_HINTS.items():
            if hint_key in name_lower:
                domain = hint_val
                break
    if not domain:
        for q in [name, cleaned]:
            domain = _search_domain(q)
            if domain:
                break

    # ── 1. Try ALL icon sources; keep the highest-resolution result ──────────
    best_icon: "Image.Image | None" = None
    best_icon_size = 0
    best_icon_label = ""

    if domain:
        _tmp = logo_dir / f"{safe}_tmp.png"
        for try_fn, label in [
            (_try_clearbit_logo, f"Clearbit ({domain})"),
            (_try_logodev,       f"logo.dev ({domain})"),
            (_try_brandfetch,    f"Brandfetch ({domain})"),
            (_try_uplead,        f"Uplead ({domain})"),
        ]:
            img = try_fn(domain, _tmp)
            if img:
                sz = min(img.size)
                if sz > best_icon_size:
                    best_icon, best_icon_size, best_icon_label = img, sz, label
                if best_icon_size >= _ICON_EARLY_EXIT:
                    break  # high-res icon — no need to check further

        # Favicon as final icon fallback (only if still no good icon)
        if best_icon_size < _ICON_EARLY_EXIT:
            img = _try_favicon(domain, _tmp)
            if img:
                sz = min(img.size)
                if sz > best_icon_size:
                    best_icon, best_icon_size, best_icon_label = img, sz, f"favicon ({domain})"

        try:
            _tmp.unlink(missing_ok=True)
        except Exception:
            pass

    # ── 2. Any high-quality icon found → use it ─────────────────────────────
    if best_icon:
        best_icon.save(cache)
        _log(f"  Logo → {name}: ✓ {best_icon_label}")
        return best_icon

    # ── 3. Icon from website (direct source, fast) ────────────────────────────
    if domain:
        img = _try_website_logo(domain, cache)
        if img:
            _log(f"  Logo → {name}: ✓ website icon ({domain})")
            return img

    # ── 4. Icon from Wikipedia ────────────────────────────────────────────────
    for q in wiki_queries:
        img = _try_wikipedia_logo(q, cache)
        if img:
            _log(f"  Logo → {name}: ✓ Wikipedia ({q})")
            return img

    # ── 5. Icon from Wikimedia Commons ───────────────────────────────────────
    img = _try_wikimedia_logo(name, cache)
    if img:
        _log(f"  Logo → {name}: ✓ Wikimedia Commons")
        return img

    # ── 6. Fallback: official vertical/horizontal logo ────────────────────────
    #       Wikipedia / Wikimedia prefer vertical > stacked > wordmark logos
    extra_queries = []
    for suffix in [" Inc", " Corp", " Holdings", " Technologies", " Software"]:
        if suffix.lower() not in name.lower():
            extra_queries.append(cleaned + suffix)
    for q in extra_queries[:3]:
        img = _try_wikipedia_logo(q, cache)
        if img:
            _log(f"  Logo → {name}: ✓ Wikipedia vertical ({q})")
            return img

    img = _try_wikimedia_logo(cleaned, cache)
    if img:
        _log(f"  Logo → {name}: ✓ Wikimedia vertical ({cleaned})")
        return img

    # ── 7. RealRate archive — fallback for companies with no other source ─────
    if archive_logo_url and not prefer_archive:
        img = _try_realrate_archive(archive_logo_url, cache)
        if img:
            _log(f"  Logo → {name}: ✓ RealRate archive (fallback)")
            return img

    _log(f"  Logo → {name}: ✗ not found")
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  DRAWING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def shadow(base: Image.Image, x: int, y: int, w: int, h: int,
           radius: int = 20, blur: int = 14, off: int = 5, alpha: int = 35):
    bw = blur * 2
    layer = Image.new("RGBA", (w + bw * 2, h + bw * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([bw, bw, bw + w, bw + h], radius=radius, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer, (x - bw + off, y - bw + off))


def aa_border(canvas: Image.Image, x: int, y: int, w: int, h: int,
              radius: int, color: tuple, width: int = 3, scale: int = 4):
    """Draw an anti-aliased rounded-rectangle border using supersampling."""
    sw, sh = w * scale, h * scale
    layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    bw = width * scale
    # Draw a filled rounded rect then a smaller filled one on top to get border only
    ld.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=radius * scale, fill=color)
    inner_fill = (0, 0, 0, 0)
    ld.rounded_rectangle([bw, bw, sw - 1 - bw, sh - 1 - bw],
                         radius=max(1, (radius - width) * scale), fill=inner_fill)
    layer = layer.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(layer, (x, y))


def fit_image(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    w, h = img.size
    s = min(max_w / w, max_h / h)
    if s != 1.0:
        img = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    return img


def _logo_is_light(logo: Image.Image, threshold: int = 200, min_frac: float = 0.6) -> bool:
    """Return True if the majority of visible (non-transparent) pixels are light/white."""
    rgba = logo.convert("RGBA")
    arr = np.array(rgba)
    alpha = arr[:, :, 3]
    visible = alpha > 32
    if visible.sum() == 0:
        return False
    rgb = arr[:, :, :3][visible]
    brightness = rgb.mean(axis=1)
    return float((brightness > threshold).sum()) / len(brightness) >= min_frac


def paste_logo_container(canvas: Image.Image, logo: Image.Image,
                          x: int, y: int, size: int = LOGO_BOX_SZ,
                          radius: int = LOGO_BOX_R, pad: int = LOGO_PAD,
                          dark_mode: bool = False):
    shadow(canvas, x, y, size, size, radius=radius, alpha=20, blur=10, off=4)
    if _logo_is_light(logo):
        bg = (18, 18, 18)
        outline = (80, 80, 80)
    elif not dark_mode:
        bg = WHITE
        outline = BORDER
    else:
        bg = (240, 245, 250)
        outline = (50, 70, 110)

    # Single AA mask shared by both background and logo clip — one supersample pass
    SS = 4
    hi_mask = Image.new("L", (size * SS, size * SS), 0)
    ImageDraw.Draw(hi_mask).rounded_rectangle(
        [0, 0, size * SS - 1, size * SS - 1], radius=radius * SS, fill=255
    )
    clip_mask = hi_mask.resize((size, size), Image.LANCZOS)

    # AA background — apply clip_mask as alpha so corners are smooth
    bg_layer = Image.new("RGBA", (size, size), bg + (255,))
    bg_layer.putalpha(clip_mask)
    canvas.alpha_composite(bg_layer, (x, y))

    # Scale/fit the logo
    inner = size - pad * 2
    lw, lh = logo.size
    if max(lw, lh) < inner * 2:
        scale = max(2, (inner * 2) // max(lw, lh))
        logo = logo.resize((lw * scale, lh * scale), Image.LANCZOS)
    logo_fit = fit_image(logo, inner, inner)
    try:
        logo_fit = logo_fit.filter(ImageFilter.UnsharpMask(radius=1.5, percent=200, threshold=2))
    except Exception:
        pass
    lw, lh = logo_fit.size
    lx_off = (size - lw) // 2
    ly_off = (size - lh) // 2

    # Clip logo alpha to the same AA mask
    container = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rgba = logo_fit if logo_fit.mode == "RGBA" else logo_fit.convert("RGBA")
    container.alpha_composite(rgba, (lx_off, ly_off))
    r, g, b, a = container.split()
    clipped_a = Image.fromarray(
        np.minimum(np.array(a), np.array(clip_mask)).astype(np.uint8)
    )
    canvas.alpha_composite(Image.merge("RGBA", (r, g, b, clipped_a)), (x, y))

    aa_border(canvas, x, y, size, size, radius=radius, color=outline, width=2)


def word_wrap(text: str, font: ImageFont.FreeTypeFont,
              max_w: int, draw: ImageDraw.ImageDraw) -> list:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bb = draw.textbbox((0, 0), test, font=font)
        if (bb[2] - bb[0]) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


# ══════════════════════════════════════════════════════════════════════════════
#  INFOGRAPHIC GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def _draw_gradient_rect(canvas: Image.Image, x: int, y: int, w: int, h: int,
                         color1: tuple, color2: tuple, radius: int = 0,
                         direction: str = "horizontal"):
    """Draw a gradient-filled rounded rectangle (numpy-accelerated)."""
    steps = w if direction == "horizontal" else h
    t = np.linspace(0, 1, steps, dtype=np.float32)
    c1 = np.array([color1[i] if i < len(color1) else 255 for i in range(4)], dtype=np.float32)
    c2 = np.array([color2[i] if i < len(color2) else 255 for i in range(4)], dtype=np.float32)
    strip = c1 + (c2 - c1) * t[:, np.newaxis]
    strip[:, :3] += np.random.uniform(-0.5, 0.5, strip[:, :3].shape).astype(np.float32)
    strip = np.clip(strip, 0, 255).astype(np.uint8)
    arr = np.empty((h, w, 4), dtype=np.uint8)
    if direction == "horizontal":
        arr[:] = strip[np.newaxis, :, :]
    else:
        arr[:] = strip[:, np.newaxis, :]
    grad = Image.fromarray(arr, "RGBA")
    if radius > 0:
        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
        _, _, _, a_ch = grad.split()
        new_alpha = Image.new("L", (w, h), 0)
        new_alpha.paste(a_ch, mask=mask)
        grad.putalpha(new_alpha)
    canvas.alpha_composite(grad, (x, y))


def _draw_hex_grid(canvas: Image.Image, w: int, h: int, spacing: int = 80,
                    color: tuple = (255, 255, 255, 22)):
    """Draw a hexagonal grid overlay with glowing intersection dots."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = spacing // 2
    dx = int(r * 1.732)  # √3 * r
    dy = int(r * 1.5)
    vertices = set()
    for row in range(-1, h // dy + 2):
        for col in range(-1, w // dx + 2):
            cx = col * dx + (dx // 2 if row % 2 else 0)
            cy = row * dy
            pts = []
            for i in range(6):
                angle = math.pi / 180 * (60 * i + 30)
                px = cx + int(r * math.cos(angle))
                py = cy + int(r * math.sin(angle))
                pts.append((px, py))
                vertices.add((px, py))
            d.polygon(pts, outline=color)
    # Glowing dots at every hex vertex — gives the grid a premium circuit-board feel
    edge_a = color[3] if len(color) > 3 else 22
    dot_a = min(255, edge_a * 5)
    dot_col = color[:3] + (dot_a,)
    vr = max(2, spacing // 18)
    for vx, vy in vertices:
        if -vr <= vx <= w + vr and -vr <= vy <= h + vr:
            d.ellipse([vx - vr, vy - vr, vx + vr, vy + vr], fill=dot_col)
    canvas.alpha_composite(layer)



_INDUSTRY_BG = {
    "motor":     ( 4,  6, 14),   # carbon black with blue tint
    "software":  ( 2,  6, 20),   # deep navy
    "computers": ( 4,  5, 12),   # dark indigo
    "finance":   ( 8,  7,  3),   # dark amber
    "health":    ( 3, 12, 12),   # dark teal
    "energy":    (10,  5,  2),   # oil black
    "food":      ( 4, 10,  4),   # dark forest
    "air":       ( 3,  8, 20),   # midnight sky
    "generic":   ( 5,  9, 24),
}

_ABBREV_SKIP = {
    "inc", "corp", "co", "ltd", "llc", "plc", "group", "holdings",
    "the", "of", "and", "&", "technologies", "technology",
    "solutions", "services", "international", "global", "enterprises",
}

_INDUSTRY_PALETTE = {
    # (primary, deep, highlight) — bold, industry-specific hues
    "motor":     (( 30, 160, 255), ( 10,  80, 200), (160, 220, 255)),  # racing blue
    "software":  (( 60, 180, 255), ( 20,  90, 210), (180, 230, 255)),  # electric blue
    "computers": (( 80, 160, 255), ( 30,  80, 220), (190, 220, 255)),  # electric indigo
    "finance":   ((240, 168,  32), (160, 100,  12), (255, 225, 110)),  # gold
    "health":    ((  0, 230, 185), (  0, 145, 115), (160, 255, 235)),  # medical teal
    "energy":    ((255, 120,   0), (185,  70,   0), (255, 210,  90)),  # flame orange
    "food":      (( 95, 220,  45), ( 55, 145,  15), (195, 245, 130)),  # leaf green
    "air":       (( 55, 210, 255), ( 18, 120, 200), (195, 240, 255)),  # sky blue
}

# Per-industry full theme: neon accent, secondary accent, card/header gradients
_INDUSTRY_THEME = {
    "motor": {
        "neon":        ( 30, 160, 255),
        "accent":      ( 10,  95, 210),
        "card3_from":  (  8,  40,  95, 240),
        "card3_to":    (  3,  18,  50, 240),
        "header_from": ( 10,  25,  70, 244),
        "header_to":   (  4,  12,  35, 250),
        "dim_border":  ( 25,  70, 140),
    },
    "software": {
        "neon":        ( 60, 180, 255),
        "accent":      ( 20, 100, 220),
        "card3_from":  (  8,  35,  90, 240),
        "card3_to":    (  3,  14,  48, 240),
        "header_from": (  5,  20,  60, 244),
        "header_to":   (  2,   8,  30, 250),
        "dim_border":  ( 25,  70, 155),
    },
    "computers": {
        "neon":        ( 80, 160, 255),
        "accent":      ( 40, 100, 220),
        "card3_from":  ( 14,  32,  82, 240),
        "card3_to":    (  7,  16,  42, 240),
        "header_from": ( 12,  22,  55, 244),
        "header_to":   (  6,  10,  28, 250),
        "dim_border":  ( 30,  65, 140),
    },
    "finance": {
        "neon":        (240, 168,  32),
        "accent":      (175, 115,  15),
        "card3_from":  ( 65,  42,   6, 240),
        "card3_to":    ( 32,  20,   2, 240),
        "header_from": ( 25,  18,   5, 244),
        "header_to":   ( 12,   8,   2, 250),
        "dim_border":  (100,  70,  20),
    },
    "health": {
        "neon":        (  0, 230, 185),
        "accent":      (  0, 160, 125),
        "card3_from":  (  0,  55,  45, 240),
        "card3_to":    (  0,  28,  22, 240),
        "header_from": (  6,  28,  24, 244),
        "header_to":   (  3,  14,  12, 250),
        "dim_border":  ( 20,  90,  75),
    },
    "energy": {
        "neon":        (255, 120,   0),
        "accent":      (195,  78,   0),
        "card3_from":  ( 75,  28,   0, 240),
        "card3_to":    ( 38,  12,   0, 240),
        "header_from": ( 28,  12,   3, 244),
        "header_to":   ( 14,   5,   0, 250),
        "dim_border":  (100,  45,  10),
    },
    "food": {
        "neon":        ( 95, 220,  45),
        "accent":      ( 58, 155,  18),
        "card3_from":  ( 16,  55,   6, 240),
        "card3_to":    (  8,  28,   2, 240),
        "header_from": ( 10,  28,   8, 244),
        "header_to":   (  5,  14,   3, 250),
        "dim_border":  ( 30,  80,  20),
    },
    "air": {
        "neon":        ( 55, 210, 255),
        "accent":      ( 25, 145, 215),
        "card3_from":  (  0,  45,  95, 240),
        "card3_to":    (  0,  22,  50, 240),
        "header_from": (  8,  22,  65, 244),
        "header_to":   (  3,  10,  35, 250),
        "dim_border":  ( 28,  78, 130),
    },
    "generic": {
        "neon":        (  0, 224, 255),
        "accent":      ( 61, 186, 205),
        "card3_from":  (  0,  70, 120, 240),
        "card3_to":    ( 10,  40,  80, 240),
        "header_from": ( 18,  30,  65, 244),
        "header_to":   (  7,  14,  40, 250),
        "dim_border":  ( 55,  82, 138),
    },
}


def _draw_industry_background(canvas: Image.Image, W: int, H: int, industry: str):
    """Draw an industry-themed background with three-tone blue palettes."""

    a1, a2, a3 = _INDUSTRY_PALETTE.get(industry, ((50, 120, 210), (20, 70, 170), (105, 175, 240)))

    yy, xx = np.mgrid[0:H, 0:W]

    # ── 1. Overhead spotlight ─────────────────────────────────────────────────
    cx_g, cy_g = W // 2, int(H * 0.04)
    dist_g = np.sqrt(((xx - cx_g) / (W * 0.78))**2 + ((yy - cy_g) / (H * 1.05))**2)
    bright = np.clip((1.0 - dist_g) * 22, 0, 16).astype(np.float32)
    bright_u8 = bright.astype(np.uint8)
    bright_arr = np.zeros((H, W, 4), dtype=np.uint8)
    bright_arr[:, :, :3] = bright_u8[:, :, np.newaxis]
    bright_arr[:, :, 3] = bright_u8
    canvas.alpha_composite(Image.fromarray(bright_arr, "RGBA"))

    # ── 2. Vignette ───────────────────────────────────────────────────────────
    cx_v, cy_v = W // 2, H // 2
    dist_v = np.sqrt(((xx - cx_v) / (W * 0.55))**2 + ((yy - cy_v) / (H * 0.55))**2)
    vig_alpha = np.clip((dist_v - 0.30) * 100, 0, 72).astype(np.uint8)
    vig_arr = np.zeros((H, W, 4), dtype=np.uint8)
    vig_arr[:, :, 3] = vig_alpha
    canvas.alpha_composite(Image.fromarray(vig_arr, "RGBA"))

    # ── 3. Shared structural layer ────────────────────────────────────────────
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    step = 108

    # Ambient glow — highlight tone
    for rr in range(920, 0, -5):
        al = int(28 * (rr / 920))
        d.ellipse([W // 2 - rr, -420 - rr // 2, W // 2 + rr, -420 + rr // 2],
                  fill=a3 + (al,))

    # Corner brackets — primary
    arm = 95
    for (bx, by, sx, sy) in [(PAD+8, PAD+8, 1, 1), (W-PAD-8, PAD+8, -1, 1),
                               (PAD+8, H-PAD-8, 1, -1), (W-PAD-8, H-PAD-8, -1, -1)]:
        d.line([(bx, by), (bx + arm*sx, by)], fill=a1 + (120,), width=2)
        d.line([(bx, by), (bx, by + arm*sy)], fill=a1 + (120,), width=2)

    # Fine grid — minor: deep, major: primary
    for x in range(0, W + 1, step):
        d.line([(x, 0), (x, H)], fill=a2 + (20,), width=1)
    for y in range(0, H + 1, step):
        d.line([(0, y), (W, y)], fill=a2 + (20,), width=1)
    for x in range(0, W + 1, step * 4):
        d.line([(x, 0), (x, H)], fill=a1 + (42,), width=1)
    for y in range(0, H + 1, step * 4):
        d.line([(0, y), (W, y)], fill=a1 + (42,), width=1)

    # Horizontal data reference lines — highlight ticks, deep line
    for frac, al in [(0.22, 30), (0.40, 22), (0.58, 30), (0.76, 22), (0.90, 30)]:
        ly = int(H * frac)
        d.line([(PAD * 2, ly), (W - PAD * 2, ly)], fill=a3 + (al,), width=1)
        for tx in [W - PAD * 2 - 2, W // 2, PAD * 2 + 2]:
            d.line([(tx, ly - 5), (tx, ly + 5)], fill=a1 + (60,), width=1)

    # ── 4. Industry-specific thematic geometry ────────────────────────────────
    if industry == "air":
        # Earth-curvature horizon arcs — deep + highlight
        for ri, col, al in [(int(W*2.2), a2, 40), (int(W*2.05), a3, 26),
                             (int(W*1.90), a2, 18)]:
            hcx, hcy = W // 2, H + int(H * 0.28)
            d.arc([hcx - ri, hcy - ri, hcx + ri, hcy + ri],
                  start=210, end=330, fill=col + (al,), width=3)

        # Flight-level altitude bands — dashed highlight lines
        for frac in [0.20, 0.34, 0.48, 0.62, 0.76, 0.88]:
            fy = int(H * frac)
            for dash_x in range(PAD, W - PAD, 80):
                d.line([(dash_x, fy), (dash_x + 40, fy)],
                       fill=a3 + (32,), width=1)

        # Contrail Bézier paths across the sky
        trail_defs = [
            (0.04, 0.12, 0.96, 0.07, -0.04, a1, 40),
            (0.08, 0.30, 0.92, 0.22, -0.03, a2, 30),
            (0.00, 0.50, 0.88, 0.40,  0.03, a1, 26),
            (0.12, 0.68, 1.00, 0.58, -0.03, a3, 22),
            (0.20, 0.84, 0.80, 0.78,  0.02, a2, 18),
        ]
        for sx, sy, ex, ey, sag, col, al in trail_defs:
            x0, y0 = int(W*sx), int(H*sy)
            x1, y1 = int(W*ex), int(H*ey)
            mx = (x0 + x1) // 2
            my = (y0 + y1) // 2 + int(H * sag)
            trail_pts = []
            for t_i in range(51):
                t = t_i / 50
                bx_t = (1-t)**2*x0 + 2*(1-t)*t*mx + t**2*x1
                by_t = (1-t)**2*y0 + 2*(1-t)*t*my + t**2*y1
                trail_pts.append((int(bx_t), int(by_t)))
            for i in range(len(trail_pts) - 1):
                d.line([trail_pts[i], trail_pts[i+1]], fill=col + (al,), width=2)

        # Compass / heading rose watermark — lower-right
        rcx, rcy = int(W * 0.82), int(H * 0.82)
        rr_c = int(W * 0.15)
        d.ellipse([rcx - rr_c, rcy - rr_c, rcx + rr_c, rcy + rr_c],
                  outline=a2 + (50,), width=2)
        d.ellipse([rcx - int(rr_c*0.65), rcy - int(rr_c*0.65),
                   rcx + int(rr_c*0.65), rcy + int(rr_c*0.65)],
                  outline=a3 + (32,), width=1)
        for ang_deg in range(0, 360, 30):
            ang_r = math.radians(ang_deg)
            inner = int(rr_c * (0.72 if ang_deg % 90 == 0 else 0.83))
            tick_col = a1 if ang_deg % 90 == 0 else a2
            tick_al  = 75 if ang_deg % 90 == 0 else 45
            d.line([(rcx + int(inner * math.cos(ang_r)),
                     rcy + int(inner * math.sin(ang_r))),
                    (rcx + int(rr_c  * math.cos(ang_r)),
                     rcy + int(rr_c  * math.sin(ang_r)))],
                   fill=tick_col + (tick_al,), width=1)

        # Scattered aircraft-position dots — primary
        for _ in range(18):
            px = random.randint(PAD*2, W - PAD*2)
            py = random.randint(PAD*2, H - PAD*2)
            rd = random.randint(3, 7)
            d.ellipse([px-rd, py-rd, px+rd, py+rd],
                      fill=a1 + (random.randint(70, 140),))

    elif industry == "motor":
        # Speed streaks — primary + deep
        focal_x, focal_y = int(W * 0.06), int(H * 0.50)
        for _ in range(40):
            angle = math.radians(random.uniform(-38, 38))
            length = random.uniform(W * 0.55, W * 1.15)
            ex = focal_x + int(math.cos(angle) * length)
            ey = focal_y + int(math.sin(angle) * length)
            col = a1 if random.random() > 0.4 else a2
            d.line([(focal_x, focal_y), (ex, ey)],
                   fill=col + (random.randint(15, 50),),
                   width=random.choice([1, 1, 2, 2, 3]))
        # Speedometer arcs — three tones
        sr = int(W * 0.42)
        scx, scy = W - int(W * 0.08), H + int(H * 0.10)
        d.arc([scx - sr, scy - sr, scx + sr, scy + sr],
              start=200, end=340, fill=a1 + (65,), width=4)
        d.arc([scx - int(sr*0.82), scy - int(sr*0.82),
               scx + int(sr*0.82), scy + int(sr*0.82)],
              start=205, end=335, fill=a3 + (38,), width=2)
        d.arc([scx - int(sr*0.64), scy - int(sr*0.64),
               scx + int(sr*0.64), scy + int(sr*0.64)],
              start=210, end=330, fill=a2 + (26,), width=2)
        # Motion dashes — alternating primary / deep
        for i in range(12):
            bx = int(W * 0.04) + i * int(W * 0.082)
            by = int(H * 0.94)
            col = a1 if i % 2 == 0 else a2
            d.line([(bx, by), (bx + int(W * 0.048), by)],
                   fill=col + (75,), width=2)

    elif industry == "software":
        # Network graph — close edges primary, far edges deep, hot nodes highlight
        nodes = [(random.randint(PAD*2, W-PAD*2), random.randint(PAD*2, H-PAD*2))
                 for _ in range(24)]
        for i, (nx, ny) in enumerate(nodes):
            for j, (mx, my) in enumerate(nodes):
                if j <= i:
                    continue
                dist = math.hypot(nx-mx, ny-my)
                if dist < W * 0.36:
                    al = int(55 * (1 - dist / (W * 0.36)))
                    col = a1 if dist < W * 0.20 else a2
                    d.line([(nx, ny), (mx, my)], fill=col + (al,), width=1)
        for i, (nx, ny) in enumerate(nodes):
            rn = random.randint(4, 12)
            col = a3 if i < 4 else (a1 if i < 12 else a2)
            d.ellipse([nx-rn, ny-rn, nx+rn, ny+rn], fill=col + (130,))
        # Code-rain columns — alternating primary / deep
        for ci, col_x in enumerate(range(PAD, W-PAD, 86)):
            y = random.randint(0, H // 3)
            rc = a1 if ci % 2 == 0 else a2
            for _ in range(random.randint(4, 14)):
                d.ellipse([col_x-2, y-2, col_x+2, y+2], fill=rc + (28,))
                y += random.randint(26, 58)
                if y > H:
                    break

    elif industry == "computers":
        # PCB traces — deep lines, primary pads
        pads = [(random.randint(PAD*2, W-PAD*2), random.randint(PAD*2, H-PAD*2))
                for _ in range(24)]
        for i, (px, py) in enumerate(pads):
            ps = 10
            d.rectangle([px-ps, py-ps, px+ps, py+ps], outline=a1 + (120,), width=2)
            if i + 1 < len(pads):
                nx, ny = pads[i+1]
                mx = (px + nx) // 2
                d.line([(px, py), (mx, py)], fill=a2 + (55,), width=1)
                d.line([(mx, py), (mx, ny)], fill=a2 + (55,), width=1)
                d.line([(mx, ny), (nx, ny)], fill=a2 + (55,), width=1)
        # Processor chip — primary outer, highlight inner
        chip_cx, chip_cy = W // 2, H // 2
        chip_w, chip_h = int(W * 0.28), int(H * 0.28)
        d.rounded_rectangle([chip_cx-chip_w, chip_cy-chip_h,
                              chip_cx+chip_w, chip_cy+chip_h],
                             radius=20, outline=a1 + (45,), width=2)
        d.rounded_rectangle([chip_cx-int(chip_w*0.55), chip_cy-int(chip_h*0.55),
                              chip_cx+int(chip_w*0.55), chip_cy+int(chip_h*0.55)],
                             radius=12, outline=a3 + (30,), width=1)
        pin_count = 6
        for i in range(pin_count):
            t = (i + 1) / (pin_count + 1)
            lx = chip_cx - chip_w;  rx = chip_cx + chip_w
            y  = chip_cy - chip_h + int(chip_h * 2 * t)
            pc = a1 if i % 2 == 0 else a2
            d.line([(lx-30, y), (lx, y)], fill=pc + (60,), width=2)
            d.line([(rx, y), (rx+30, y)], fill=pc + (60,), width=2)
            x  = chip_cx - chip_w + int(chip_w * 2 * t)
            ty = chip_cy - chip_h;  bot_y = chip_cy + chip_h
            d.line([(x, ty-30), (x, ty)], fill=pc + (60,), width=2)
            d.line([(x, bot_y), (x, bot_y+30)], fill=pc + (60,), width=2)

    elif industry == "finance":
        # Candlesticks — primary up, deep down, highlight wick
        bar_count = 20
        bar_w = (W - PAD * 4) // bar_count
        base_y = int(H * 0.88)
        prev_close = random.uniform(0.3, 0.7)
        for i in range(bar_count):
            bx = PAD * 2 + i * bar_w
            open_v  = max(0.05, min(0.95, prev_close + random.uniform(-0.08, 0.08)))
            close_v = max(0.05, min(0.95, open_v  + random.uniform(-0.10, 0.10)))
            high_v  = max(0.05, min(0.95, max(open_v, close_v) + random.uniform(0.02, 0.08)))
            low_v   = max(0.05, min(0.95, min(open_v, close_v) - random.uniform(0.02, 0.08)))
            scale   = int(H * 0.30)
            oy     = base_y - int(open_v  * scale)
            cy_bar = base_y - int(close_v * scale)
            hy     = base_y - int(high_v  * scale)
            ly     = base_y - int(low_v   * scale)
            mid_x  = bx + bar_w // 2
            body_c = a1 if close_v >= open_v else a2
            d.line([(mid_x, hy), (mid_x, ly)], fill=a3 + (35,), width=1)
            d.rectangle([bx+2, min(oy, cy_bar), bx+bar_w-2, max(oy, cy_bar)],
                         fill=body_c + (50,))
            prev_close = close_v
        # Two trend lines — primary strong, highlight secondary
        pts = [(int(PAD*2 + i*(W-PAD*4)/14),
                int(H*0.76 - i*H*0.028 + random.uniform(-18, 18)))
               for i in range(15)]
        for i in range(len(pts) - 1):
            d.line([pts[i], pts[i+1]], fill=a1 + (75,), width=2)
        pts2 = [(int(PAD*2 + i*(W-PAD*4)/14),
                 int(H*0.82 - i*H*0.020 + random.uniform(-12, 12)))
                for i in range(15)]
        for i in range(len(pts2) - 1):
            d.line([pts2[i], pts2[i+1]], fill=a3 + (42,), width=1)

    elif industry == "food":
        # Organic waves — rotating through three tones
        wave_cols = [a1, a2, a3, a1, a2]
        for wave_idx in range(5):
            y_base = int(H * (0.18 + wave_idx * 0.16))
            amp    = random.randint(28, 80)
            freq   = random.uniform(1.4, 3.2)
            phase  = random.uniform(0, math.pi * 2)
            al     = random.randint(28, 55)
            col    = wave_cols[wave_idx]
            pts = [(x, y_base + int(amp * math.sin(freq * math.pi * x / W + phase)))
                   for x in range(0, W + 1, 6)]
            for i in range(len(pts) - 1):
                d.line([pts[i], pts[i+1]], fill=col + (al,), width=2)
        # Hexagonal honeycomb — alternating deep / highlight
        hx_r = 60; hx_dx = int(hx_r * math.sqrt(3)); hx_dy = hx_r * 2
        for row in range(-4, 5):
            for col_i in range(-6, 7):
                hcx = W//2 + col_i*hx_dx + (row % 2) * (hx_dx // 2)
                hcy = H//2 + row * int(hx_dy * 0.75)
                hc  = a2 if (row + col_i) % 2 == 0 else a3
                pts_hex = [(int(hcx + hx_r * math.cos(math.radians(60*k - 30))),
                             int(hcy + hx_r * math.sin(math.radians(60*k - 30))))
                            for k in range(6)]
                pts_hex.append(pts_hex[0])
                d.line(pts_hex, fill=hc + (30,), width=1)
        # Ripple rings — primary
        for ri in range(6, 0, -1):
            cr = ri * 80
            d.ellipse([W-PAD*2-cr, PAD*2-cr, W-PAD*2+cr, PAD*2+cr],
                      outline=a1 + (38,), width=2)

    elif industry == "health":
        # ECG line — primary
        ecg_y = int(H * 0.50)
        pts = []; x = PAD * 2; seg = 8
        while x < W - PAD * 2:
            pts.append((x, ecg_y))
            x += seg * 5
            if random.random() < 0.15 and x + seg * 12 < W - PAD * 2:
                for dx_off, dy_off in [(0, 0), (seg, -90), (seg*2, 60),
                                       (seg*3, -140), (seg*4, 40), (seg*5, 0)]:
                    pts.append((x + dx_off, ecg_y + dy_off))
                x += seg * 6
        for i in range(len(pts) - 1):
            d.line([pts[i], pts[i+1]], fill=a1 + (65,), width=3)
        # Molecular lattice — deep
        mol_r = 48; mol_dx = int(mol_r * math.sqrt(3)); mol_dy = mol_r * 2
        for row in range(-6, 7):
            for col_i in range(-7, 8):
                mcx = W//2 + col_i*mol_dx + (row % 2) * (mol_dx // 2)
                mcy = H//2 + row * int(mol_dy * 0.75)
                pts_mol = [(int(mcx + mol_r * math.cos(math.radians(60*k))),
                             int(mcy + mol_r * math.sin(math.radians(60*k))))
                            for k in range(6)]
                pts_mol.append(pts_mol[0])
                d.line(pts_mol, fill=a2 + (22,), width=1)
        # Atom circles — highlight
        for _ in range(8):
            ax = random.randint(PAD*3, W - PAD*3)
            ay = random.randint(PAD*3, H - PAD*3)
            ar = random.randint(30, 80)
            d.ellipse([ax-ar, ay-ar, ax+ar, ay+ar], outline=a3 + (42,), width=2)

    elif industry == "energy":
        # Radiating lines — alternating primary / deep
        src_x, src_y = W // 2, int(H * 0.88)
        for i_r in range(36):
            angle = math.radians(random.uniform(195, 345))
            length = random.uniform(H * 0.38, H * 1.05)
            ex = src_x + int(math.cos(angle) * length)
            ey = src_y + int(math.sin(angle) * length)
            col = a1 if i_r % 2 == 0 else a2
            d.line([(src_x, src_y), (ex, ey)],
                   fill=col + (random.randint(18, 55),), width=random.choice([1, 1, 2]))
        # Lightning bolt — primary
        lx, ly = int(W * 0.10), int(H * 0.10)
        bolt_scale = 110
        bolt = [(lx+bolt_scale*0.30, ly), (lx, ly+bolt_scale*0.50), (lx+bolt_scale*0.50, ly+bolt_scale*0.50),
                (lx+bolt_scale*0.20, ly+bolt_scale), (lx+bolt_scale*0.72, ly+bolt_scale*0.40),
                (lx+bolt_scale*0.42, ly+bolt_scale*0.40), (lx+bolt_scale*0.72, ly)]
        d.polygon([(int(bx), int(by)) for bx, by in bolt], fill=a1 + (55,), outline=a3 + (120,), width=2)
        # Electric arcs — deep and highlight alternating
        for ai_e in range(6):
            ax_e = random.randint(0, W); ay_e = random.randint(0, H // 2)
            ar_e = random.randint(int(W * 0.40), int(W * 0.92))
            sa_e = random.randint(100, 200)
            arc_col = a2 if ai_e % 2 == 0 else a3
            d.arc([ax_e-ar_e, ay_e-ar_e, ax_e+ar_e, ay_e+ar_e],
                  start=sa_e, end=sa_e + random.randint(30, 80),
                  fill=arc_col + (45,), width=3)

    else:
        # Generic: prestige arcs + diagonals using three tones
        r1 = int(W * 1.80)
        d.arc([W-r1, -r1//3, W+r1, r1+r1//3], start=158, end=228,
              fill=a1 + (35,), width=2)
        r2 = int(W * 1.28)
        d.arc([W-r2, -r2//4, W+r2, r2+r2//4], start=162, end=222,
              fill=a2 + (22,), width=1)
        d.line([(0, int(H*0.90)), (W, int(H*0.08))], fill=a1 + (28,), width=2)
        d.line([(0, 0), (W, H)], fill=a2 + (14,), width=1)
        d.line([(W, 0), (0, H)], fill=a3 + (14,), width=1)

    # ── Dot grid — small: deep, large accent: primary ─────────────────────────
    for gx in range(0, W + 1, step):
        for gy in range(0, H + 1, step):
            d.ellipse([gx-2, gy-2, gx+2, gy+2], fill=a2 + (110,))
    for gx in range(0, W + 1, step * 3):
        for gy in range(0, H + 1, step * 3):
            d.ellipse([gx-4, gy-4, gx+4, gy+4], fill=a1 + (180,))

    canvas.alpha_composite(layer)


_INDUSTRY_KEYWORDS = {
    "motor":     ["motor", "auto", "vehicle", "car", "truck", "transport", "automotive",
                  "mobility", "fleet", "harley", "tesla", "ford", "gm", "bmw", "dodge",
                  "visteon", "gentex", "dorman", "hyliion", "leatt", "lci"],
    "software":  ["software", "saas", "digital", "cloud", "cyber", "semiconductor",
                  "chip", "platform", "microsoft", "apple", "google", "oracle", "sap",
                  "salesforce", "adobe", "nvidia", "intel", "amd", "meta", "amazon"],
    "computers": ["computer", "hardware", "processor", "server", "storage", "display",
                  "printer", "peripheral", "dell", "hp", "lenovo", "acer", "asus",
                  "seagate", "western digital", "corsair", "logitech", "canon"],
    "finance":   ["bank", "financ", "credit", "capital", "invest", "insur", "asset",
                  "fund", "wealth", "trading", "exchange", "fintech", "jpmorgan", "wells",
                  "goldman", "morgan", "blackrock", "visa", "mastercard", "amex", "citi"],
    "health":    ["health", "pharma", "bio", "medical", "hospital", "clinic", "therapeut",
                  "drug", "life science", "pfizer", "johnson", "merck", "abbvie", "lilly",
                  "novartis", "roche", "medtronic", "abbott", "humana", "unitedhealth"],
    "energy":    ["energy", "oil", "gas", "power", "solar", "wind", "utility", "electric",
                  "renewable", "nuclear", "mining", "exxon", "chevron", "bp", "shell",
                  "nextera", "duke", "conoco", "halliburton", "schlumberger", "pioneer"],
    "food":      ["food", "beverage", "drink", "restaurant", "grocery", "nutrition",
                  "kraft", "nestle", "mcdonald", "starbucks", "pepsico", "coca", "tyson",
                  "general mills", "conagra", "mondelez", "kellogg", "campbell"],
    "air":       ["air", "airline", "aviation", "airways", "aircraft", "airport", "flight",
                  "aerospace", "jetblue", "southwest", "delta", "frontier", "allegiant",
                  "bristow", "saker", "wheels up", "sun country", "united airlines",
                  "american airlines", "spirit", "alaska", "hawaiian"],
}


def _detect_industry(title: str, companies: list = None) -> str:
    """Score industry from title + company names; return highest match."""
    corpus = title.lower()
    if companies:
        corpus += " " + " ".join(c["name"].lower() for c in companies)

    scores = {ind: 0 for ind in _INDUSTRY_KEYWORDS}
    for ind, kws in _INDUSTRY_KEYWORDS.items():
        for kw in kws:
            if kw in corpus:
                scores[ind] += 1

    best_ind  = max(scores, key=scores.get)
    best_score = scores[best_ind]
    return best_ind if best_score > 0 else "generic"


def _draw_industry_icon(canvas: Image.Image, cx: int, cy: int, size: int, industry: str,
                        icon_color: tuple = None):
    """Draw a neon industry icon with multi-layer glow, centered at (cx, cy)."""
    sc = 4
    sz = size * sc
    c  = sz // 2
    r  = int(sz * 0.38)
    lw = max(5, sz // 30)
    gw = lw * 3

    glow_shapes = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    crisp       = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_shapes)
    cd = ImageDraw.Draw(crisp)

    C  = (icon_color or NEON_CYAN)[:3]  # per-industry accent color
    cyan_g = C + (110,)         # glow fill — boosted for visibility
    cyan_b = C + (255,)         # crisp fill

    if industry == "motor":
        # Improved F1-style steering wheel — double ring, thick spokes, prominent hub
        # Outer ring
        gd.ellipse([c - r, c - r, c + r, c + r], outline=cyan_g, width=gw * 3)
        cd.ellipse([c - r, c - r, c + r, c + r], outline=cyan_b, width=lw + 5)
        # Inner grip ring
        ir = int(r * 0.76)
        gd.ellipse([c - ir, c - ir, c + ir, c + ir], outline=cyan_g, width=gw)
        cd.ellipse([c - ir, c - ir, c + ir, c + ir], outline=cyan_b, width=lw + 1)
        # Hub — filled circle
        hr = int(r * 0.22)
        gd.ellipse([c - hr, c - hr, c + hr, c + hr], fill=cyan_g)
        cd.ellipse([c - hr, c - hr, c + hr, c + hr], fill=cyan_b)
        # 3 spokes (hub → inner ring): top, lower-left, lower-right
        for ang_deg in [90, 210, 330]:
            ang = math.radians(ang_deg)
            x1 = int(c + hr * math.cos(ang))
            y1 = int(c - hr * math.sin(ang))
            x2 = int(c + ir * math.cos(ang))
            y2 = int(c - ir * math.sin(ang))
            gd.line([(x1, y1), (x2, y2)], fill=cyan_g, width=gw * 3)
            cd.line([(x1, y1), (x2, y2)], fill=cyan_b, width=lw + 3)
        # Grip notches on outer ring (6 small marks)
        for ang_deg in range(0, 360, 60):
            ang = math.radians(ang_deg)
            nx1 = int(c + (r - lw * 3) * math.cos(ang))
            ny1 = int(c - (r - lw * 3) * math.sin(ang))
            nx2 = int(c + (r + lw) * math.cos(ang))
            ny2 = int(c - (r + lw) * math.sin(ang))
            cd.line([(nx1, ny1), (nx2, ny2)], fill=cyan_b, width=lw)

    elif industry == "software":
        # Microchip: rounded body + pins
        chip = int(r * 0.56)
        pin  = int(r * 0.34)
        pg   = chip // 3
        cr_  = lw * 2
        gd.rounded_rectangle([c - chip, c - chip, c + chip, c + chip],
                              radius=cr_, outline=cyan_g, width=gw * 2)
        cd.rounded_rectangle([c - chip, c - chip, c + chip, c + chip],
                              radius=cr_, outline=cyan_b, width=lw + 2)
        for off in [-pg * 3 // 2, -pg // 2, pg // 2, pg * 3 // 2]:
            for (x1, y1, x2, y2) in [
                (c + off, c - chip,  c + off, c - chip - pin),
                (c + off, c + chip,  c + off, c + chip + pin),
                (c - chip, c + off,  c - chip - pin, c + off),
                (c + chip, c + off,  c + chip + pin, c + off),
            ]:
                gd.line([(x1, y1), (x2, y2)], fill=cyan_g, width=gw)
                cd.line([(x1, y1), (x2, y2)], fill=cyan_b, width=lw)
        nd = lw + 3
        cd.ellipse([c - nd, c - nd, c + nd, c + nd], fill=cyan_b)

    elif industry == "finance":
        # Classical bank: pediment + columns + base
        base_y = c + int(r * 0.84)
        step_y = c - int(r * 0.08)
        roof_y = c - int(r * 0.84)
        gd.line([(c - r, base_y), (c + r, base_y)], fill=cyan_g, width=gw * 3)
        cd.line([(c - r, base_y), (c + r, base_y)], fill=cyan_b, width=lw + 4)
        gd.line([(c - int(r*.84), step_y), (c + int(r*.84), step_y)],
                fill=cyan_g, width=gw * 2)
        cd.line([(c - int(r*.84), step_y), (c + int(r*.84), step_y)],
                fill=cyan_b, width=lw + 2)
        tri = [(c - int(r*.84)+lw, step_y), (c, roof_y), (c + int(r*.84)-lw, step_y)]
        gd.polygon(tri, outline=cyan_g, width=gw * 2)
        cd.polygon(tri, outline=cyan_b, width=lw + 1)
        col_top = step_y + lw * 2
        for col_x in [c - int(r*.54), c - int(r*.18), c + int(r*.18), c + int(r*.54)]:
            gd.line([(col_x, col_top), (col_x, base_y - lw * 2)], fill=cyan_g, width=gw)
            cd.line([(col_x, col_top), (col_x, base_y - lw * 2)], fill=cyan_b, width=lw)

    elif industry == "health":
        # ECG heartbeat line
        pts = [
            (c - r,           c),
            (c - int(r*.48),  c),
            (c - int(r*.24),  c - int(r*.18)),
            (c - int(r*.09),  c + int(r*.12)),
            (c,               c - int(r*.84)),
            (c + int(r*.12),  c + int(r*.54)),
            (c + int(r*.25),  c),
            (c + r,           c),
        ]
        for i in range(len(pts) - 1):
            gd.line([pts[i], pts[i+1]], fill=cyan_g, width=gw * 2)
            cd.line([pts[i], pts[i+1]], fill=cyan_b, width=lw + 2)

    elif industry == "energy":
        # Lightning bolt
        bolt = [
            (c + int(r*.20),  c - r),
            (c - int(r*.05),  c - int(r*.10)),
            (c + int(r*.30),  c - int(r*.05)),
            (c - int(r*.20),  c + r),
            (c + int(r*.05),  c + int(r*.10)),
            (c - int(r*.28),  c + int(r*.05)),
        ]
        gd.polygon(bolt, fill=cyan_g)
        cd.polygon(bolt, fill=cyan_b)
        gd.polygon(bolt, outline=C + (80,), width=gw)
        cd.polygon(bolt, outline=cyan_b, width=lw)

    elif industry == "computers":
        # Monitor: screen frame + stand + base
        sw = int(r * 1.16); sh = int(r * 0.80)
        st = c - int(r * 0.52); sb = st + sh
        sl = c - sw // 2;      sr = c + sw // 2
        gd.rounded_rectangle([sl, st, sr, sb], radius=lw * 2, outline=cyan_g, width=gw * 2)
        cd.rounded_rectangle([sl, st, sr, sb], radius=lw * 2, outline=cyan_b, width=lw + 2)
        std_b = c + int(r * 0.76)
        gd.line([(c, sb), (c, std_b)], fill=cyan_g, width=gw)
        cd.line([(c, sb), (c, std_b)], fill=cyan_b, width=lw + 1)
        bw_m = int(r * 0.62)
        gd.line([(c - bw_m, std_b), (c + bw_m, std_b)], fill=cyan_g, width=gw * 2)
        cd.line([(c - bw_m, std_b), (c + bw_m, std_b)], fill=cyan_b, width=lw + 2)

    elif industry == "food":
        # Fork — 3 rounded tines + thick handle
        fw = int(r * 0.10)
        tine_t = c - int(r * 0.82); tine_b = c - int(r * 0.12)
        for tx in [-int(r * 0.25), 0, int(r * 0.25)]:
            gd.rounded_rectangle([c + tx - fw, tine_t, c + tx + fw, tine_b],
                                  radius=fw, fill=cyan_g)
            cd.rounded_rectangle([c + tx - fw, tine_t, c + tx + fw, tine_b],
                                  radius=fw, fill=cyan_b)
        handle_t = c - int(r * 0.08); handle_b = c + int(r * 0.82)
        gd.rounded_rectangle([c - fw, handle_t, c + fw, handle_b],
                              radius=fw, fill=cyan_g)
        cd.rounded_rectangle([c - fw, handle_t, c + fw, handle_b],
                              radius=fw, fill=cyan_b)

    elif industry == "air":
        # Top-down airplane silhouette — nose pointing up
        # Fuselage body
        fus = [
            (c,                  c - r),
            (c + int(r * 0.13),  c - int(r * 0.55)),
            (c + int(r * 0.11),  c + int(r * 0.24)),
            (c + int(r * 0.07),  c + int(r * 0.62)),
            (c,                  c + int(r * 0.78)),
            (c - int(r * 0.07),  c + int(r * 0.62)),
            (c - int(r * 0.11),  c + int(r * 0.24)),
            (c - int(r * 0.13),  c - int(r * 0.55)),
        ]
        gd.polygon(fus, fill=cyan_g)
        cd.polygon(fus, fill=cyan_b)
        # Main swept wings
        for sx in [1, -1]:
            wing = [
                (c + sx * int(r * 0.10),  c - int(r * 0.10)),
                (c + sx * int(r * 0.95),  c + int(r * 0.42)),
                (c + sx * int(r * 0.78),  c + int(r * 0.54)),
                (c + sx * int(r * 0.09),  c + int(r * 0.20)),
            ]
            gd.polygon(wing, fill=cyan_g)
            cd.polygon(wing, fill=cyan_b)
        # Horizontal tail stabilisers
        for sx in [1, -1]:
            stab = [
                (c + sx * int(r * 0.07),  c + int(r * 0.52)),
                (c + sx * int(r * 0.44),  c + int(r * 0.62)),
                (c + sx * int(r * 0.38),  c + int(r * 0.72)),
                (c + sx * int(r * 0.06),  c + int(r * 0.68)),
            ]
            gd.polygon(stab, fill=cyan_g)
            cd.polygon(stab, fill=cyan_b)

    else:
        # Rising bar chart
        base_y = c + int(r * 0.84)
        bw = int(r * 0.25)
        for bx, bh in [(c - int(r*.54), int(r*.55)),
                       (c,              int(r*.84)),
                       (c + int(r*.54), int(r*.40))]:
            bar_top = base_y - bh
            gd.rectangle([bx - bw, bar_top, bx + bw, base_y], fill=cyan_g)
            cd.rectangle([bx - bw, bar_top, bx + bw, base_y],
                         fill=C + (80,), outline=cyan_b, width=lw)
        gd.line([(c - r, base_y + lw), (c + r, base_y + lw)], fill=cyan_g, width=gw * 2)
        cd.line([(c - r, base_y + lw), (c + r, base_y + lw)], fill=cyan_b, width=lw + 2)

    # ── Multi-pass glow composite ─────────────────────────────────────────────
    ic_color = C

    # Radial background halo
    halo = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    hd_i = ImageDraw.Draw(halo)
    halo_r = int(sz * 0.44)
    for i in range(halo_r, 0, -4):
        a = int(30 * (i / halo_r) ** 2)
        hd_i.ellipse([c - i, c - i, c + i, c + i], fill=ic_color + (a,))
    halo = halo.filter(ImageFilter.GaussianBlur(sz // 4))

    wide = glow_shapes.filter(ImageFilter.GaussianBlur(gw * 2.8))
    mid  = glow_shapes.filter(ImageFilter.GaussianBlur(gw * 1.3))

    result = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    result = Image.alpha_composite(result, halo)
    result = Image.alpha_composite(result, wide)
    result = Image.alpha_composite(result, mid)
    result = Image.alpha_composite(result, crisp)
    result = result.resize((size, size), Image.LANCZOS)
    canvas.alpha_composite(result, (cx - size // 2, cy - size // 2))



def generate(companies: list, title: str, subtitle: str,
             rr_logo: "Image.Image | None", fonts: dict, output_path: str):

    W, H = IMG_W, IMG_H
    content_w = W - PAD * 2
    card_w    = (content_w - COL_GAP) // 2

    def F(variant: str, size: int) -> ImageFont.FreeTypeFont:
        return pil_font(fonts.get(variant), size)

    # Font set (scaled for 1200×1500)
    f_subtitle   = F("medium",    29)
    f_company    = F("bold",      28)
    f_company_sm = F("bold",      21)
    f_rank       = F("extrabold", 33)
    f_ecr        = F("extrabold", 26)
    f_badge      = F("bold",      17)
    f_trend      = F("medium",    17)

    # ── Industry-aware canvas + themed background ────────────────────────────
    industry = _detect_industry(title, companies)
    _th      = _INDUSTRY_THEME.get(industry, _INDUSTRY_THEME["generic"])
    I_NEON   = _th["neon"]
    I_ACCENT = _th["accent"]
    I_DIM    = _th["dim_border"]
    I_C3F    = _th["card3_from"]
    I_C3T    = _th["card3_to"]
    I_HF     = _th["header_from"]
    I_HT     = _th["header_to"]
    # ECR label color — bright neutral white, always readable on dark cards
    I_MUTED  = (210, 225, 238, 240)
    # High-contrast accent for ECR value — neon hue boosted toward white
    I_NEON_HI     = tuple(min(255, c + 85) for c in I_NEON)   # ECR % value
    I_NEON_BRIGHT = I_NEON                                      # icon + subtitle: exact accent, max opacity
    # Dark version of accent for badge outlines / pill gradient end
    I_DARK   = tuple(max(0, c // 3) for c in I_ACCENT) + (255,)

    canvas = Image.new("RGBA", (W, H), _INDUSTRY_BG.get(industry, BG) + (255,))
    _draw_industry_background(canvas, W, H, industry)
    draw = ImageDraw.Draw(canvas)

    # ── HEADER ────────────────────────────────────────────────────────────────
    hx, hy = PAD, PAD
    hw, hh = content_w, HEADER_H

    # ── Header card ───────────────────────────────────────────────────────────
    shadow(canvas, hx, hy, hw, hh, radius=22, alpha=65, blur=34, off=12)
    _draw_gradient_rect(canvas, hx, hy, hw, hh,
                        I_HF, I_HT, radius=22, direction="vertical")
    # Teal glow: outer halo → mid bloom → tight inner, then crisp line
    glow_h = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd_h = ImageDraw.Draw(glow_h)
    # Outer soft halo
    gd_h.rounded_rectangle([hx - 14, hy - 14, hx + hw + 14, hy + hh + 14],
                            radius=36, outline=I_NEON + (40,), width=28)
    gd_h.rounded_rectangle([hx - 5, hy - 5, hx + hw + 5, hy + hh + 5],
                            radius=27, outline=I_NEON + (110,), width=12)
    gd_h.rounded_rectangle([hx - 1, hy - 1, hx + hw + 1, hy + hh + 1],
                            radius=23, outline=I_NEON + (200,), width=4)
    glow_h = glow_h.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(glow_h)
    draw = ImageDraw.Draw(canvas)
    aa_border(canvas, hx, hy, hw, hh, radius=22, color=I_NEON, width=3)

    # Glass specular — thin highlight at very top of header card
    _hgl = Image.new("RGBA", (hw - 44, 5), (0, 0, 0, 0))
    ImageDraw.Draw(_hgl).line([(0, 2), (hw - 44, 2)], fill=(255, 255, 255, 36), width=2)
    canvas.alpha_composite(_hgl, (hx + 22, hy))
    draw = ImageDraw.Draw(canvas)

    # ── Left zone: RealRate vertical logo ─────────────────────────────────────
    logo_zone_w = 167
    icon_zone_w = 162
    logo_pad    = 16
    icon_pad    = 16
    lz_x = hx + 14
    if rr_logo:
        rl = fit_image(rr_logo, logo_zone_w - 24, hh - 48)
        rl_x = lz_x + (logo_zone_w - 24 - rl.width) // 2
        rl_y = hy + (hh - rl.height) // 2
        logo_cx = rl_x + rl.width // 2
        logo_cy = rl_y + rl.height // 2
        # Radial glow behind logo — crop to logo area
        _lrx, _lry = rl.width // 2 + 28, rl.height // 2 + 28
        _lm = 90  # margin for GaussianBlur(28)
        _lw2, _lh2 = (_lrx + _lm) * 2, (_lry + _lm) * 2
        gl_logo = Image.new("RGBA", (_lw2, _lh2), (0, 0, 0, 0))
        _llcx, _llcy = _lw2 // 2, _lh2 // 2
        ImageDraw.Draw(gl_logo).ellipse(
            [_llcx - _lrx, _llcy - _lry, _llcx + _lrx, _llcy + _lry],
            fill=I_NEON + (55,))
        gl_logo = gl_logo.filter(ImageFilter.GaussianBlur(28))
        canvas.alpha_composite(gl_logo, (logo_cx - _llcx, logo_cy - _llcy))
        rgba_rl = rl if rl.mode == "RGBA" else rl.convert("RGBA")
        canvas.alpha_composite(rgba_rl, (rl_x, rl_y))
        draw = ImageDraw.Draw(canvas)
    else:
        draw.text((lz_x + 4, hy + hh // 2 - 21),
                  "RealRate", fill=I_NEON, font=F("extrabold", 31))

    # Vertical separator between logo zone and title zone
    sep_x = hx + logo_zone_w + logo_pad - 8
    draw.line([(sep_x, hy + 16), (sep_x, hy + hh - 16)], fill=(80, 110, 155, 70), width=1)

    # ── Center zone: Title + subtitle — centred on the text zone, not full header
    tw_center  = hw - logo_zone_w - logo_pad - icon_zone_w - icon_pad
    text_zone_x = hx + logo_zone_w + logo_pad          # left edge of text zone
    title_cx    = text_zone_x + tw_center // 2          # true centre of text zone

    # Title: allow up to 2 lines so font stays large
    title_fs = 72
    while title_fs > 34:
        f_title_lg = F("extrabold", title_fs)
        if len(word_wrap(title, f_title_lg, tw_center, draw)) <= 2:
            break
        title_fs -= 3
    f_title_lg = F("extrabold", title_fs)
    t_lines = word_wrap(title, f_title_lg, tw_center, draw)[:2]

    s_lines = word_wrap(subtitle, f_subtitle, tw_center, draw)[:2]

    # Measure title block
    t_bb     = draw.textbbox((0, 0), t_lines[0], font=f_title_lg)
    t_line_h = t_bb[3] - t_bb[1]
    t_line_gap   = int(t_line_h * 0.14)
    title_block_h = len(t_lines) * t_line_h + (len(t_lines) - 1) * t_line_gap

    sub_gap = 38
    sub_lh  = 34
    block_h = title_block_h + sub_gap + len(s_lines) * sub_lh

    # Vertically centre block in header
    title_y = hy + (hh - block_h) // 2

    # Title lines — extrabold white, each line centred individually
    for li, ln in enumerate(t_lines):
        bb = draw.textbbox((0, 0), ln, font=f_title_lg)
        tx = title_cx - (bb[2] - bb[0]) // 2 - bb[0]
        draw.text((tx, title_y + li * (t_line_h + t_line_gap)), ln,
                  fill=WHITE, font=f_title_lg)

    # Subtitle — medium weight, cyan, centred in text zone
    sub_y = title_y + title_block_h + sub_gap
    for i, ln in enumerate(s_lines):
        bb = draw.textbbox((0, 0), ln, font=f_subtitle)
        sx = title_cx - (bb[2] - bb[0]) // 2 - bb[0]
        draw.text((sx, sub_y + i * sub_lh), ln, fill=I_NEON_BRIGHT, font=f_subtitle)

    # ── Right zone: Industry neon icon ─────────────────────────────────────────
    icon_cx = hx + hw - icon_zone_w // 2
    icon_cy = hy + hh // 2
    _im = 56  # margin for GaussianBlur(18)
    _is = 148 + _im * 2
    _ic = _is // 2
    gl_icon = Image.new("RGBA", (_is, _is), (0, 0, 0, 0))
    ImageDraw.Draw(gl_icon).ellipse([_ic - 74, _ic - 74, _ic + 74, _ic + 74],
                                    fill=I_NEON_BRIGHT + (70,))
    gl_icon = gl_icon.filter(ImageFilter.GaussianBlur(20))
    canvas.alpha_composite(gl_icon, (icon_cx - _ic, icon_cy - _ic))
    _draw_industry_icon(canvas, icon_cx, icon_cy, 142, industry, icon_color=I_NEON_BRIGHT)
    draw = ImageDraw.Draw(canvas)

    # ── RANKING CARDS ─────────────────────────────────────────────────────────
    cards_y = hy + hh + HEADER_GAP

    for idx, co in enumerate(companies[:10]):
        col = idx // 5
        row = idx % 5
        cx  = PAD + col * (card_w + COL_GAP)
        cy  = cards_y + row * (CARD_H + CARD_GAP)

        rank = co["rank"]
        name = co["name"]
        logo = co.get("logo")
        is_top3 = rank <= 3

        # Card shadow — deep for strong elevation
        shadow(canvas, cx, cy, card_w, CARD_H, radius=18, alpha=55, blur=24, off=9)

        if is_top3:
            _draw_gradient_rect(canvas, cx, cy, card_w, CARD_H,
                                I_C3F, I_C3T, radius=18)
            draw = ImageDraw.Draw(canvas)
            aa_border(canvas, cx, cy, card_w, CARD_H, radius=18, color=I_NEON, width=3)
            name_color = WHITE
            # Left-edge neon glow bar
            gl_edge = Image.new("RGBA", (card_w, CARD_H), (0, 0, 0, 0))
            ImageDraw.Draw(gl_edge).rounded_rectangle(
                [1, 1, 5, CARD_H - 2], radius=3, fill=I_NEON + (100,))
            canvas.alpha_composite(gl_edge, (cx, cy))
            draw = ImageDraw.Draw(canvas)
            draw.rounded_rectangle([cx + 2, cy + 2, cx + 6, cy + CARD_H - 2],
                                   radius=3, fill=I_NEON)
        else:
            _draw_gradient_rect(canvas, cx, cy, card_w, CARD_H,
                                CARD_BG + (230,), CARD_BG_LT + (230,), radius=18,
                                direction="vertical")
            draw = ImageDraw.Draw(canvas)
            aa_border(canvas, cx, cy, card_w, CARD_H, radius=18, color=I_DIM, width=2)
            name_color = (240, 246, 255)

        # Neon glow border for TOP RATED non-top-3 cards
        if co.get("top_rated") and not is_top3:
            _gm = 16
            _gw, _gh = card_w + _gm * 2, CARD_H + _gm * 2
            _glow = Image.new("RGBA", (_gw, _gh), (0, 0, 0, 0))
            _gd = ImageDraw.Draw(_glow)
            _gd.rounded_rectangle([_gm - 8, _gm - 8, _gm + card_w + 8, _gm + CARD_H + 8],
                                  radius=26, outline=I_NEON + (28,), width=18)
            _gd.rounded_rectangle([_gm - 3, _gm - 3, _gm + card_w + 3, _gm + CARD_H + 3],
                                  radius=21, outline=I_NEON + (80,), width=9)
            _gd.rounded_rectangle([_gm, _gm, _gm + card_w, _gm + CARD_H],
                                  radius=18, outline=I_NEON + (150,), width=3)
            _glow = _glow.filter(ImageFilter.GaussianBlur(6))
            canvas.alpha_composite(_glow, (cx - _gm, cy - _gm))
            draw = ImageDraw.Draw(canvas)
            aa_border(canvas, cx, cy, card_w, CARD_H, radius=18, color=I_NEON, width=2)

        # Glass specular — thin bright line at card top (premium glass effect)
        _gl = Image.new("RGBA", (card_w - 24, 5), (0, 0, 0, 0))
        ImageDraw.Draw(_gl).line([(0, 2), (card_w - 24, 2)], fill=(255, 255, 255, 44), width=2)
        canvas.alpha_composite(_gl, (cx + 12, cy))
        draw = ImageDraw.Draw(canvas)

        # Accent bar (neon glow for top 3, subtle for others)
        bar_x = cx + 3
        bar_col = I_NEON if is_top3 else I_ACCENT
        draw.rounded_rectangle([bar_x, cy + 4, bar_x + ACCENT_BAR_W, cy + CARD_H - 4],
                               radius=4, fill=bar_col)

        # Rank badge
        circ_cx = bar_x + ACCENT_BAR_W + 10 + RANK_R
        circ_cy = cy + CARD_H // 2
        badge_col = I_ACCENT
        # Wide outer glow — crop to badge area to avoid full-canvas allocation
        _bm1 = 70  # margin for GaussianBlur(18)
        _bs1 = (RANK_R + 18 + _bm1) * 2
        _bc1 = _bs1 // 2
        gl_badge = Image.new("RGBA", (_bs1, _bs1), (0, 0, 0, 0))
        ImageDraw.Draw(gl_badge).ellipse(
            [_bc1 - RANK_R - 18, _bc1 - RANK_R - 18,
             _bc1 + RANK_R + 18, _bc1 + RANK_R + 18],
            fill=badge_col + (90,))
        gl_badge = gl_badge.filter(ImageFilter.GaussianBlur(18))
        canvas.alpha_composite(gl_badge, (circ_cx - _bc1, circ_cy - _bc1))
        # Tight inner glow — crop to badge area
        _bm2 = 30  # margin for GaussianBlur(7)
        _bs2 = (RANK_R + 4 + _bm2) * 2
        _bc2 = _bs2 // 2
        gl_badge2 = Image.new("RGBA", (_bs2, _bs2), (0, 0, 0, 0))
        ImageDraw.Draw(gl_badge2).ellipse(
            [_bc2 - RANK_R - 4, _bc2 - RANK_R - 4,
             _bc2 + RANK_R + 4, _bc2 + RANK_R + 4],
            fill=badge_col + (140,))
        gl_badge2 = gl_badge2.filter(ImageFilter.GaussianBlur(7))
        canvas.alpha_composite(gl_badge2, (circ_cx - _bc2, circ_cy - _bc2))
        # Solid #3DBACD filled circle + bright outline
        scale = 4
        sz = RANK_R * 2 * scale
        circ = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        cd = ImageDraw.Draw(circ)
        cd.ellipse([0, 0, sz - 1, sz - 1],
                   fill=badge_col + (255,), outline=I_DARK, width=scale * 2)
        circ = circ.resize((RANK_R * 2, RANK_R * 2), Image.LANCZOS)
        canvas.alpha_composite(circ, (circ_cx - RANK_R, circ_cy - RANK_R))
        draw = ImageDraw.Draw(canvas)
        bb = draw.textbbox((0, 0), str(rank), font=f_rank)
        rtx = circ_cx - (bb[2] - bb[0]) // 2 - bb[0]
        rty = circ_cy - (bb[3] - bb[1]) // 2 - bb[1]
        draw.text((rtx, rty), str(rank), fill=WHITE, font=f_rank)

        # Logo container (right) — white bg for readability
        lbx = cx + card_w - LOGO_BOX_SZ - 11
        lby = cy + (CARD_H - LOGO_BOX_SZ) // 2
        if logo:
            paste_logo_container(canvas, logo, lbx, lby, dark_mode=True)
            draw = ImageDraw.Draw(canvas)
        else:
            # Draw initials placeholder
            words = [w for w in re.split(r"[\s\-_]+", name) if w.lower() not in _ABBREV_SKIP and w]
            if words:
                # If first word is all-caps and short (like "BTCS"), use it directly
                if words[0].isupper() and len(words[0]) <= 5:
                    abbrev = words[0][:4]
                else:
                    abbrev = "".join(w[0].upper() for w in words[:3])
            else:
                abbrev = name[:2].upper()

            # Box background with gradient feel
            draw.rounded_rectangle([lbx, lby, lbx + LOGO_BOX_SZ, lby + LOGO_BOX_SZ],
                                   radius=LOGO_BOX_R, fill=(18, 30, 58))
            aa_border(canvas, lbx, lby, LOGO_BOX_SZ, LOGO_BOX_SZ, radius=LOGO_BOX_R,
                      color=I_NEON, width=2)
            # Subtle glow behind text — crop to logo box area
            _am = 60  # margin for GaussianBlur(18)
            _as = LOGO_BOX_SZ + _am * 2
            gl_ab = Image.new("RGBA", (_as, _as), (0, 0, 0, 0))
            ImageDraw.Draw(gl_ab).ellipse(
                [_am + 10, _am + 10, _am + LOGO_BOX_SZ - 10, _am + LOGO_BOX_SZ - 10],
                fill=I_NEON + (35,))
            gl_ab = gl_ab.filter(ImageFilter.GaussianBlur(18))
            canvas.alpha_composite(gl_ab, (lbx - _am, lby - _am))
            draw = ImageDraw.Draw(canvas)
            # Font size based on length
            ab_fs = 34 if len(abbrev) <= 2 else (28 if len(abbrev) == 3 else 21)
            f_ab = F("extrabold", ab_fs)
            ab_bb = draw.textbbox((0, 0), abbrev, font=f_ab)
            ab_x = lbx + (LOGO_BOX_SZ - (ab_bb[2] - ab_bb[0])) // 2 - ab_bb[0]
            ab_y = lby + (LOGO_BOX_SZ - (ab_bb[3] - ab_bb[1])) // 2 - ab_bb[1]
            draw.text((ab_x, ab_y), abbrev, fill=I_NEON, font=f_ab)

        # Company name + ECR + status block
        text_x      = circ_cx + RANK_R + 13
        text_zone_w = lbx - text_x - 10
        ecr         = co.get("ecr")
        is_top_rated = co.get("top_rated", False)
        trend_val   = co.get("trend", 0)

        fn = f_company
        lines = word_wrap(name, fn, text_zone_w, draw)
        if len(lines) > 2:
            fn = f_company_sm
            lines = word_wrap(name, fn, text_zone_w, draw)
        lines = lines[:2]

        name_lh      = 31
        name_block_h = len(lines) * name_lh - (name_lh - 27)

        if ecr is not None:
            ecr_gap   = 7
            sep_h     = 1
            sep_gap   = 6
            ecr_row_h = 29
            total_h   = name_block_h + ecr_gap + sep_h + sep_gap + ecr_row_h
        else:
            total_h = name_block_h

        start_y = cy + (CARD_H - total_h) // 2

        # Name lines
        for li, ln in enumerate(lines):
            draw.text((text_x, start_y + li * name_lh), ln, fill=name_color, font=fn)

        if ecr is not None:
            # Thin separator
            sep_y = start_y + name_block_h + ecr_gap
            draw.line([(text_x, sep_y), (text_x + text_zone_w - 10, sep_y)],
                      fill=(60, 90, 140, 90), width=1)

            # ECR row: muted label + cyan value + trend arrow
            ecr_y   = sep_y + sep_h + sep_gap
            lbl_str = "ECR"
            lbl_bb  = draw.textbbox((0, 0), lbl_str, font=f_ecr)
            lbl_w   = lbl_bb[2] - lbl_bb[0]
            val_str = f"  {ecr}%"
            val_bb  = draw.textbbox((0, 0), val_str, font=f_ecr)
            val_w   = val_bb[2] - val_bb[0]
            draw.text((text_x, ecr_y), lbl_str, fill=I_MUTED, font=f_ecr)
            draw.text((text_x + lbl_w, ecr_y), val_str, fill=I_NEON_HI, font=f_ecr)

            if trend_val > 0:
                trend_sym, trend_col = "↑", (80, 220, 130)
            elif trend_val < 0:
                trend_sym, trend_col = "↓", (220, 80, 80)
            else:
                trend_sym, trend_col = "–", (110, 130, 165)
            arrow_x = text_x + lbl_w + val_w + 8
            draw.text((arrow_x, ecr_y + 2), trend_sym, fill=trend_col, font=f_trend)
            cur_x = arrow_x + draw.textbbox((0, 0), trend_sym, font=f_trend)[2] + 9

            # TOP RATED pill — inline with ECR row
            if is_top_rated:
                badge_txt = "★  TOP RATED"
                btb       = draw.textbbox((0, 0), badge_txt, font=f_badge)
                badge_tw  = btb[2] - btb[0]
                badge_ph  = 24
                badge_pw  = badge_tw + 20
                badge_bx  = cur_x
                badge_by  = ecr_y + (ecr_row_h - badge_ph) // 2

                for px_i in range(badge_pw):
                    t   = px_i / max(badge_pw - 1, 1)
                    r_c = int(I_ACCENT[0] * (1 - t * 0.5) + I_DARK[0] * t * 0.5)
                    g_c = int(I_ACCENT[1] * (1 - t * 0.5) + I_DARK[1] * t * 0.5)
                    b_c = int(I_ACCENT[2] * (1 - t * 0.5) + I_DARK[2] * t * 0.5)
                    draw.line([(badge_bx + px_i, badge_by + 2),
                               (badge_bx + px_i, badge_by + badge_ph - 2)],
                              fill=(r_c, g_c, b_c, 210), width=1)
                aa_border(canvas, badge_bx, badge_by, badge_pw, badge_ph,
                          radius=badge_ph // 2, color=I_ACCENT + (200,), width=2)
                draw = ImageDraw.Draw(canvas)
                txt_x = badge_bx + (badge_pw - badge_tw) // 2 - btb[0]
                txt_y = badge_by + (badge_ph - (btb[3] - btb[1])) // 2 - btb[1]
                draw.text((txt_x, txt_y), badge_txt, fill=WHITE, font=f_badge)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    last_card_bottom = cards_y + 5 * (CARD_H + CARD_GAP) - CARD_GAP
    fy = last_card_bottom + FOOTER_OFFSET + 8

    # Glowing teal separator line — use a thin strip to avoid full-canvas allocation
    sep_y = fy - 10
    _sl_h = 36
    glow_line = Image.new("RGBA", (W - PAD * 2, _sl_h), (0, 0, 0, 0))
    ImageDraw.Draw(glow_line).line(
        [(0, _sl_h // 2), (W - PAD * 2, _sl_h // 2)], fill=I_NEON + (160,), width=10)
    glow_line = glow_line.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(glow_line, (PAD, sep_y - _sl_h // 2))
    draw = ImageDraw.Draw(canvas)
    draw.line([(PAD, sep_y), (W - PAD, sep_y)], fill=I_NEON + (220,), width=2)

    f_footer_lg = F("bold", 30)
    draw.text((PAD, fy), "RealRate - Explainable Financial AI",
              fill=I_NEON, font=f_footer_lg)

    # Globe icon + URL on the right
    f_url_lg = F("bold", 30)
    url_txt = "www.realrate.ai"
    url_bb = draw.textbbox((0, 0), url_txt, font=f_url_lg)
    url_w = url_bb[2] - url_bb[0]
    globe_r = 16
    gap = 8
    total_w = globe_r * 2 + gap + url_w
    gx = W - PAD - total_w          # globe centre x
    gy = fy + (url_bb[3] - url_bb[1]) // 2 + url_bb[1]  # vertically centred

    # Draw globe icon — use a small crop instead of full-canvas allocation
    _gm = 11  # margin for GaussianBlur(5)
    _gw = globe_r * 2 + _gm * 2
    _gh = globe_r * 2 + _gm * 2
    _go = (gx - _gm, gy - globe_r - _gm)
    gl_layer = Image.new("RGBA", (_gw, _gh), (0, 0, 0, 0))
    gld = ImageDraw.Draw(gl_layer)
    # Local coordinates: gx maps to _gm, gy maps to globe_r + _gm
    _lox, _loy = _gm, globe_r + _gm
    gld.ellipse([_lox, _loy - globe_r, _lox + globe_r * 2, _loy + globe_r],
                outline=I_NEON + (255,), width=3)
    gld.line([(_lox, _loy), (_lox + globe_r * 2, _loy)], fill=I_NEON + (255,), width=2)
    gld.arc([_lox + globe_r // 2, _loy - globe_r,
             _lox + globe_r * 3 // 2, _loy + globe_r],
            start=270, end=90, fill=I_NEON + (255,), width=2)
    gld.arc([_lox + globe_r // 2, _loy - globe_r,
             _lox + globe_r * 3 // 2, _loy + globe_r],
            start=90, end=270, fill=I_NEON + (255,), width=2)
    gl_glow = gl_layer.filter(ImageFilter.GaussianBlur(5))
    canvas.alpha_composite(gl_glow, _go)
    canvas.alpha_composite(gl_layer, _go)
    draw = ImageDraw.Draw(canvas)

    draw.text((gx + globe_r * 2 + gap, fy),
              url_txt, fill=I_NEON, font=f_url_lg)

    # ── Save ──────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG", dpi=(300, 300), optimize=False)
    print(f"\n  ✓ Saved → {output_path}")


# ══════════════════════════════════════════════════════════════════════════════
#  SPREADSHEET LOADER
# ══════════════════════════════════════════════════════════════════════════════

RANK_NAMES = {"rank", "ranking", "#", "position", "pos", "no.", "no", "place", "rk"}
NAME_NAMES = {"company", "name", "company name", "institution", "bank",
              "organization", "firm", "entity", "issuer", "bank name"}


def load_spreadsheet(path: str) -> list:
    p = Path(path)
    def _read_with_header_scan(read_fn, **kwargs):
        """Try row 0 first; scan rows 1-5 if no known header words are found."""
        df = read_fn(**kwargs)
        known = RANK_NAMES | NAME_NAMES
        if not any(str(c).strip().lower() in known for c in df.columns):
            for skip in range(1, 6):
                try:
                    df2 = read_fn(header=skip, **kwargs)
                    if any(str(c).strip().lower() in known for c in df2.columns):
                        return df2
                except Exception:
                    break
        return df

    if p.suffix.lower() in (".xlsx", ".xlsm"):
        df = _read_with_header_scan(pd.read_excel, io=p, engine="openpyxl")
    elif p.suffix.lower() == ".xls":
        df = _read_with_header_scan(pd.read_excel, io=p, engine="xlrd")
    elif p.suffix.lower() == ".csv":
        df = _read_with_header_scan(pd.read_csv, filepath_or_buffer=p)
    else:
        raise ValueError(f"Unsupported format: {p.suffix}")

    print(f"  File   : {p.name}")
    print(f"  Columns: {list(df.columns)}")

    rank_col = next((c for c in df.columns if str(c).strip().lower() in RANK_NAMES), None)
    name_col = next((c for c in df.columns if str(c).strip().lower() in NAME_NAMES), None)

    # Fallback: first mostly-numeric column for rank
    if rank_col is None:
        for c in df.columns:
            if pd.to_numeric(df[c], errors="coerce").notna().mean() > 0.7:
                rank_col = c
                break

    # Fallback: object column whose values look like company names
    # (1-8 avg words, not predominantly numeric)
    if name_col is None:
        for c in df.columns:
            if c == rank_col or df[c].dtype != object:
                continue
            sample = df[c].dropna().astype(str).head(10)
            if sample.empty:
                continue
            avg_words = sample.apply(lambda x: len(x.split())).mean()
            numeric_frac = pd.to_numeric(sample, errors="coerce").notna().mean()
            if 0.5 <= avg_words <= 8 and numeric_frac < 0.3:
                name_col = c
                break

    if not rank_col or not name_col:
        raise ValueError(
            "Cannot auto-detect rank/name columns. "
            "Rename your columns to 'Rank' and 'Company' and retry."
        )

    print(f"  Rank   : '{rank_col}'")
    print(f"  Name   : '{name_col}'")

    domain_col  = next((c for c in df.columns if str(c).strip().lower() == "domain"), None)
    cik_col     = next((c for c in df.columns if str(c).strip().lower() == "cik"), None)
    report_col  = next((c for c in df.columns
                        if str(c).strip().lower() in ("currentreport", "current_report")), None)

    df["_rank"] = pd.to_numeric(df[rank_col], errors="coerce")
    top10 = df[df["_rank"].between(1, 10)].sort_values("_rank").head(10)

    rows = []
    for _, r in top10.iterrows():
        entry = {"rank": int(r["_rank"]), "name": str(r[name_col]).strip()}

        if domain_col:
            raw = str(r.get(domain_col, "")).strip()
            if raw and raw.lower() not in ("nan", "none", ""):
                entry["domain"] = raw

        # Derive RealRate archive logo URL from CIK + currentReport base
        if cik_col and report_col:
            raw_cik = str(r.get(cik_col, "")).strip()
            raw_report = str(r.get(report_col, "")).strip()
            if raw_cik not in ("nan", "none", "") and raw_report not in ("nan", "none", ""):
                try:
                    cik_padded = str(int(float(raw_cik))).zfill(10)
                    m = re.match(r"(https?://[^/]+/[^/]+/)", raw_report)
                    if m:
                        archive_base = m.group(1)
                        entry["archive_logo_url"] = f"{archive_base}logos/{cik_padded}_256x256.png"
                except (ValueError, TypeError):
                    pass

        rows.append(entry)
    return rows


# ══════════════════════════════════════════════════════════════════════════════
#  ARCHIVE LOADER
# ══════════════════════════════════════════════════════════════════════════════

def load_from_archive(industry_slug: str, year: int = None) -> "tuple[list, int]":
    """Fetch top-10 ranking directly from realrate-archive.com JSON."""
    base = f"{_ARCHIVE_BASE}/us_{industry_slug}/"

    if year is None:
        raw = _archive_get(base)
        if not raw:
            raise RuntimeError(f"Cannot reach {base}")
        years = sorted(int(y) for y in re.findall(r'href="(\d{4})/"', raw.decode("utf-8", errors="ignore")))
        if not years:
            raise RuntimeError(f"No year directories at {base}")
        year = years[-1]
        print(f"  Latest year: {year}")

    json_url = f"{base}{year}/website-ranking.json"
    print(f"  Fetching {json_url} …")
    raw = _archive_get(json_url)
    if not raw:
        raise RuntimeError(f"Cannot fetch {json_url}")

    payload   = json.loads(raw.decode("utf-8"))
    entries   = payload.get("company_details", payload) if isinstance(payload, dict) else payload
    companies = []
    for entry in entries:
        rank = entry.get("rank")
        if not isinstance(rank, (int, float)) or int(rank) < 1 or int(rank) > 10:
            continue
        cid = str(entry.get("company_id", "")).strip().zfill(10)
        ecr_raw = entry.get("value", 0)
        logo_url = (entry.get("logo_url_256x256") or
                    f"{base}logos/{cid}_256x256.png")
        companies.append({
            "rank":             int(rank),
            "name":             entry["name"],
            "ecr":              round(float(ecr_raw) * 100),
            "top_rated":        bool(entry.get("top_rated", False)),
            "trend":            float(entry.get("trend", 0) or 0),
            "archive_logo_url": logo_url,
            "prefer_archive":   True,
        })

    companies.sort(key=lambda x: x["rank"])
    return companies[:10], year


# ══════════════════════════════════════════════════════════════════════════════
#  LINKEDIN CAPTION GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

_INDUSTRY_INTROS = {
    "air":              "Aviation is defined by thin margins, high capital intensity, and constant exposure to fuel price shocks — most carriers are one demand disruption away from a liquidity crisis. These rankings reveal which companies have built balance sheets strong enough to withstand the next one.",
    "motor":            "The auto industry faces accelerating pressure from EV transition costs, supply chain volatility, and shifting consumer demand. Here is how financial resilience stacks up across the sector.",
    "software":         "With growth multiples compressing and capital efficiency now a boardroom priority, software companies face a new financial discipline test. These are the firms with structural strength to outperform through the cycle.",
    "computers":        "Hardware margins remain under pressure from commoditisation and supply chain complexity. These rankings show which computer companies have built genuinely resilient balance sheets.",
    "finance_services": "Financial services firms face mounting pressure from credit normalisation and higher funding costs. ECR cuts through the complexity to reveal who is truly well-capitalised.",
    "food":             "Input cost volatility, shifting consumer preferences, and margin pressure continue to test food sector balance sheets. These are the companies demonstrating genuine financial resilience.",
    "health_services":  "Healthcare faces simultaneous pressure from reimbursement changes, labour costs, and demand uncertainty. ECR identifies which companies are structurally prepared.",
    "advertising":      "Ad markets are notoriously cyclical — financial stress compounds quickly in downturns. These rankings show which players have built the strongest foundations.",
    "semiconductors":   "Semiconductor cycles are among the most violent in any industry. These companies have the capital strength to navigate the inevitable next downturn.",
    "brokers":          "Broker-dealers face elevated market volatility and tightening regulatory capital requirements. ECR reveals who is genuinely well-positioned for what comes next.",
    "savings":          "Savings institutions navigate a challenging environment of rate sensitivity and deposit competition. These rankings identify the most financially resilient players.",
    "life":             "Life insurers carry long-duration liabilities that demand exceptional balance sheet discipline. ECR reveals which companies are truly positioned for the long term.",
    "non_life":         "Non-life insurers face rising claims costs and catastrophe exposure in a volatile market. These rankings show who has built the financial cushion to absorb the unexpected.",
    "pharma":           "Pharma balance sheets must absorb massive R&D costs, patent cliffs, and regulatory risk. These rankings identify the companies with the financial strength to keep innovating.",
    "chemicals":        "Chemical companies navigate volatile feedstock costs and cyclical demand. ECR reveals who has built genuine capital strength beyond the current cycle.",
    "state_banks":      "State banks carry unique balance sheet risks tied to credit quality and deposit funding. These rankings identify the financially strongest institutions in the sector.",
    "realestate":       "Real estate companies face rising financing costs and valuation pressure. ECR cuts through book-value uncertainty to show true financial resilience.",
    "hotels":           "The hotel sector continues to rebalance post-pandemic, with capital structure now a key differentiator. These rankings reveal the financially strongest operators.",
    "construction":     "Construction companies face margin pressure, project risk, and working capital intensity. ECR identifies which firms are built to last through the cycle.",
    "data_processing":  "Data processing companies operate at the intersection of tech investment cycles and enterprise spending. These rankings show who has the strongest financial foundation.",
    "consulting":       "Consulting firms face intense competition for talent and project wins. ECR reveals which companies have built the capital resilience to invest through downturns.",
    "mining":           "Mining companies face commodity price swings and capital-intensive operations. These rankings identify who is financially positioned to outperform across the cycle.",
    "petrol":           "Energy transition pressures and volatile commodity prices test petrol sector balance sheets. ECR reveals who has built genuine financial resilience.",
    "programming":      "Programming and IT services firms face pricing pressure and talent cost inflation. These rankings show who is financially equipped for long-term competition.",
    "medicinal_products": "Medicinal products companies navigate regulatory risk and R&D investment cycles. ECR identifies the companies with the financial strength to sustain innovation.",
    "recreation":       "Recreation companies face discretionary spending sensitivity and post-pandemic demand shifts. These rankings reveal who has built the strongest financial foundation.",
}

_INDUSTRY_HASHTAGS = {
    "air":              "#Aviation #Airlines #AirTravel",
    "motor":            "#Automotive #EV #CarIndustry",
    "software":         "#Software #Tech #SaaS #CloudComputing",
    "computers":        "#Technology #Hardware #Computing",
    "finance_services": "#Finance #Banking #FinancialServices",
    "food":             "#FoodIndustry #FMCG #FoodBusiness",
    "health_services":  "#Healthcare #HealthServices #MedicalIndustry",
    "advertising":      "#Advertising #Marketing #Media",
    "semiconductors":   "#Semiconductors #Chips #Technology",
    "brokers":          "#Brokerage #WealthManagement #Finance",
    "savings":          "#Banking #Savings #Finance",
    "life":             "#Insurance #LifeInsurance #Finance",
    "non_life":         "#Insurance #PropertyCasualty #Finance",
    "pharma":           "#Pharma #Biotech #Healthcare",
    "chemicals":        "#Chemicals #Materials #Industry",
    "state_banks":      "#Banking #Finance #StateBank",
    "realestate":       "#RealEstate #Property #REITs",
    "hotels":           "#Hospitality #Hotels #Travel",
    "construction":     "#Construction #Engineering #Infrastructure",
    "data_processing":  "#DataProcessing #Technology #DigitalTransformation",
    "consulting":       "#Consulting #ProfessionalServices #Business",
    "mining":           "#Mining #Resources #Commodities",
    "petrol":           "#Energy #OilAndGas #Petrol",
    "programming":      "#Programming #ITServices #Technology",
    "medicinal_products": "#MedicinalProducts #Pharma #Healthcare",
    "recreation":       "#Recreation #Leisure #ConsumerServices",
}

_MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}


def _top_rated_description(co: dict, avg_ecr: float, sentences: int = 2) -> str:
    ecr  = co.get("ecr", 0)
    diff = round(ecr - avg_ecr)
    trend = co.get("trend", 0)

    if diff >= 20:
        s1 = f"With an ECR of {ecr}%, this company sits {diff} points above the sector average — a standout level of financial resilience."
    elif diff >= 5:
        s1 = f"An ECR of {ecr}% places this company {diff} points above the sector average, reflecting a well-capitalised balance sheet."
    elif diff >= -5:
        s1 = f"At {ecr}% ECR — in line with the sector average — Top Rated status reflects consistent financial discipline rather than outsized leverage."
    else:
        s1 = f"At {ecr}% ECR, below the sector average by {abs(diff)} points, Top Rated status signals structural strengths the headline number alone understates."

    if sentences == 1:
        return s1

    if trend > 0.05:
        s2 = "A positive trend confirms building momentum and improving financial resilience year-on-year."
    elif trend < -0.05:
        s2 = "A declining trend is a watchpoint — whether this trajectory reverses will be the key story to follow."
    else:
        s2 = "Stable metrics year-on-year reflect consistent execution rather than one-off financial engineering."

    return f"{s1} {s2}"


def generate_linkedin_caption(companies: list, title: str, year: int,
                               industry_slug: str, output_path: str,
                               display_year: int = None) -> None:
    """Write a LinkedIn post .txt alongside the infographic."""
    if display_year is None:
        display_year = year
    avg_ecr = round(sum(c.get("ecr", 0) for c in companies) / len(companies)) if companies else 0

    intro = _INDUSTRY_INTROS.get(
        industry_slug,
        "Financial strength varies dramatically across this sector. ECR reveals which companies are truly built to last."
    )
    base_tags = "#Finance #AI #Investing #RealRate #FinancialHealth #FinancialAnalysis"
    ind_tags  = _INDUSTRY_HASHTAGS.get(industry_slug, "")
    hashtags  = f"{base_tags} {ind_tags}".strip() if ind_tags else base_tags

    top_rated = [c for c in companies if c.get("top_rated")]
    others    = [c for c in companies if not c.get("top_rated")]

    lines = []
    lines.append(f"🏆 {title}")
    lines.append("RealRate Financial Strength Rankings using Artificial Intelligence")
    lines.append("")
    lines.append(intro)
    lines.append("")
    lines.append(
        "At RealRate, our explainable AI framework quantifies financial resilience through ECR — "
        "Economic Capital Ratio — a forward-looking metric that enables true comparability across "
        "size and business models, revealing not just where each company stands, but why."
    )
    lines.append("")
    lines.append(f"Market average ECR: {avg_ecr}%")
    lines.append("")

    if top_rated:
        for co in top_rated:
            rank      = co["rank"]
            medal     = _MEDAL.get(rank, "")
            prefix    = f"{medal} #{rank}".strip() if medal else f"#{rank}"
            ecr       = co.get("ecr", "N/A")
            sentences = 2 if rank <= 3 else 1
            desc      = _top_rated_description(co, avg_ecr, sentences=sentences)
            lines.append(f"{prefix} {co['name']} — ECR: {ecr}%  TOP RATED")
            lines.append(desc)
            lines.append("")

    if others:
        other_parts = [f"#{c['rank']} {c['name']} ({c.get('ecr', 'N/A')}%)" for c in others]
        lines.append("Also in the ranking:")
        lines.append(" | ".join(other_parts))
        lines.append("")

    if len(companies) >= 2:
        c1, c2 = companies[0], companies[1]
        lines.append(
            f"Does {c1['name']} at #1 with {c1.get('ecr', '?')}% ECR match your expectations — "
            f"or does {c2['name']}'s position at #2 surprise you more?"
        )
    else:
        lines.append("Which company's position here surprises you most?")
    lines.append("")
    lines.append("Full ranking + individual company reports:")
    lines.append(f"🔗 https://realrate.ai/rankings/us_{industry_slug}/{display_year}")
    lines.append("")
    lines.append(hashtags)

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ LinkedIn caption → {output_path}")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("  RealRate Infographic Generator  |  1200x1500 PNG")
    print("=" * 60)

    first_arg = sys.argv[1]
    is_spreadsheet = Path(first_arg).suffix.lower() in (".xlsx", ".xlsm", ".xls", ".csv")

    if is_spreadsheet:
        # ── Legacy spreadsheet mode ───────────────────────────────────────────
        title    = sys.argv[2] if len(sys.argv) > 2 else "TOP 10 RANKING 2025"
        subtitle = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_SUBTITLE
        output   = sys.argv[4] if len(sys.argv) > 4 else str(OUTPUT_DIR / "infographic.png")

        print("\n[1/4] Reading spreadsheet …")
        companies = load_spreadsheet(first_arg)
        for c in companies:
            print(f"    #{c['rank']:2d}: {c['name']}")
    else:
        # ── Archive mode: industry slug ───────────────────────────────────────
        industry_slug = first_arg.lower().replace("-", "_")
        print(f"\n[1/4] Fetching '{industry_slug}' ranking from realrate-archive.com …")
        companies, year = load_from_archive(industry_slug)
        for c in companies:
            top_tag = " ★" if c.get("top_rated") else ""
            print(f"    #{c['rank']:2d}: {c['name']}  ECR={c['ecr']}%{top_tag}")

        meta         = _INDUSTRY_META.get(industry_slug,
                          (f"TOP 10 US {industry_slug.upper()} COMPANIES", industry_slug))
        current_year = datetime.date.today().year
        auto_title   = f"{meta[0]} {current_year}"
        auto_output  = str(OUTPUT_DIR / f"{meta[1]}_{current_year}.png")

        title    = sys.argv[2] if len(sys.argv) > 2 else auto_title
        subtitle = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_SUBTITLE
        output   = sys.argv[4] if len(sys.argv) > 4 else auto_output

    print("\n[2/4] Downloading Manrope fonts …")
    fonts = ensure_fonts()
    for k, v in fonts.items():
        print(f"    {k:12s}: {'✓' if v else '✗ system fallback'}")

    print("\n[3/4] Fetching RealRate brand logo …")
    rr_logo = get_realrate_logo()

    print("\n[4/4] Fetching company logos …")
    def _fetch_logo(co):
        co["logo"] = get_company_logo(
            co["name"],
            hint_domain=co.get("domain"),
            archive_logo_url=co.get("archive_logo_url"),
            prefer_archive=co.get("prefer_archive", False),
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_fetch_logo, co): co for co in companies}
        for fut in as_completed(futures):
            fut.result()

    print(f"\n[Rendering 1200×1500 PNG] …  title='{title}'")
    generate(companies, title, subtitle, rr_logo, fonts, output)

    if not is_spreadsheet:
        linkedin_output = str(OUTPUT_DIR / f"linkedin_{meta[1]}_{current_year}.txt")
        print("\n[Writing LinkedIn caption] …")
        generate_linkedin_caption(companies, title, year, industry_slug, linkedin_output,
                                   display_year=current_year)

    print("\nDone! Open:", output)


if __name__ == "__main__":
    main()
```
