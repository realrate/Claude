"""
RealRate radial mindmap — universal generator
Usage:
  python gen_mindmap.py              # TriLinc Global Impact Fund (default)
  python gen_mindmap.py trilinc      # TriLinc Global Impact Fund
  python gen_mindmap.py strata       # Strata Critical Medical Inc
  python gen_mindmap.py hp           # HP Inc.
  python gen_mindmap.py angi         # Angi Inc.
  python gen_mindmap.py nvidia       # Nvidia Corp.
  python gen_mindmap.py harley       # Harley Davidson INC
"""
import sys, math, base64, re, requests, urllib3, time, os
from pathlib import Path
from PIL import Image as _PIL
from playwright.sync_api import sync_playwright

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Company selection ──────────────────────────────────────────────────────────
COMPANY = sys.argv[1].lower() if len(sys.argv) > 1 else "trilinc"
if COMPANY not in ("trilinc", "strata", "hp", "angi", "nvidia", "tesla", "apple", "harley"):
    print(f"Unknown company '{COMPANY}'. Use: trilinc, strata, hp, angi, nvidia, tesla, apple, harley"); sys.exit(1)

# ── Constants ──────────────────────────────────────────────────────────────────
W, H = 1920, 1080
F  = "'Manrope',Segoe UI,Helvetica Neue,Arial,sans-serif"
BG = "#050B18"; GREY="#AFAFAF"; WH="#FFFFFF"
AMBER="#F59E0B"; CYAN="#3DBACD"; LIME="#86EF60"; SKY="#60A5FA"
EMER="#34D399"; PINK="#F472B6"; PURP="#A78BFA"; ORAN="#FB923C"
TBLUE="#2563EB"; TAQUA="#0891B2"
_ACCENT_BY_COMPANY = {
    "trilinc": EMER, "strata": SKY, "tesla": SKY, "angi": PINK,
    "nvidia": LIME, "harley": AMBER, "apple": ORAN,
}
ACCENT = _ACCENT_BY_COMPANY.get(COMPANY, CYAN)

CACHE_DIR = Path(__file__).parent / "img_cache"
CACHE_DIR.mkdir(exist_ok=True)

HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer":    "https://en.wikipedia.org/",
    "Accept":     "image/webp,image/jpeg,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Utilities ──────────────────────────────────────────────────────────────────
def verify_ranking_url(industry_slug, fallback_year):
    try:
        hdrs = {"User-Agent": HDRS["User-Agent"], "Accept-Language": "en-US,en;q=0.9"}
        r = requests.get("https://realrate.ai/rankings", timeout=20, headers=hdrs, verify=False)
        r.raise_for_status()
        hits = re.findall(r'/rankings/([\w]+)/(\d{4})', r.text)
        matches = [(slug, yr) for slug, yr in hits if industry_slug in slug]
        if matches:
            slug, yr = max(matches, key=lambda x: x[1])
            url = f"https://realrate.ai/rankings/{slug}/{yr}"
            print(f"  Ranking URL verified: {url}")
            return url
    except Exception as e:
        print(f"  Warning: rankings page fetch failed — {e}")
    fallback = f"https://realrate.ai/rankings/{industry_slug}/{fallback_year}"
    print(f"  Ranking URL (fallback): {fallback}")
    return fallback

def raster_mime(d):
    if d[:5] == 'iVBOR': return 'image/png'
    if d[:5] == 'UklGR': return 'image/webp'
    if d[:4] == '/9j/':  return 'image/jpeg'
    return None

def is_raster_b64(d):
    return raster_mime(d) is not None

def cache_path(url, suffix=".cache"):
    return CACHE_DIR / (base64.urlsafe_b64encode(url.encode()).decode()[:80] + suffix)

def fetch_b64(url):
    cf = cache_path(url)
    if cf.exists():
        d = cf.read_text()
        if is_raster_b64(d):
            return d
        print(f"  Cache invalid, re-fetching {url[-50:]}")
        cf.unlink()
    time.sleep(1.2)
    r = requests.get(url, timeout=30, headers=HDRS, verify=False)
    r.raise_for_status()
    d = base64.b64encode(r.content).decode()
    if not is_raster_b64(d):
        raise ValueError(f"Not a raster image: {url[-40:]}")
    cf.write_text(d)
    return d

def wiki_image_url(article_title, thumb_size=400):
    api = "https://en.wikipedia.org/w/api.php"
    params = {"action":"query","titles":article_title,"prop":"pageimages",
              "pithumbsize":thumb_size,"format":"json","formatversion":"2"}
    r = requests.get(api, params=params, headers=HDRS, verify=False, timeout=20)
    r.raise_for_status()
    pages = r.json().get("query",{}).get("pages",[])
    if pages and "thumbnail" in pages[0]:
        return pages[0]["thumbnail"]["source"]
    return None

def try_wiki(article_titles, label, size=400):
    for title in article_titles:
        try:
            time.sleep(1.2)
            url = wiki_image_url(title, size)
            if not url:
                print(f"  {label} '{title}' — no image found"); continue
            d = fetch_b64(url)
            print(f"  {label} OK  [{title}]"); return d
        except Exception as e:
            print(f"  {label} '{title}' fail: {e}")
    return None

def try_fetch(urls, label):
    for url in urls:
        try:
            d = fetch_b64(url); print(f"  {label} OK"); return d
        except Exception as e: print(f"  {label} ..{url[-40:]} fail: {e}")
    return None

# ── Ranking URL ────────────────────────────────────────────────────────────────
print("Verifying ranking URL…")
_ranking_cfg = {
    "trilinc": ("us_finance_services", "2025"),
    "strata":  ("us_air",              "2026"),
    "hp":      ("us_computers",        "2025"),
    "angi":    ("us_advertising",      "2025"),
    "nvidia":  ("us_semiconductors",   "2026"),
    "tesla":   ("us_motor",            "2026"),
    "apple":   ("us_computers",        "2025"),
    "harley":  ("us_motor",            "2026"),
}
RANKING_URL = verify_ranking_url(*_ranking_cfg[COMPANY])

# ── Assets ────────────────────────────────────────────────────────────────────
print("Fetching assets…")

RL_PATH = Path(__file__).parent.parent / "RealRate Logos" / "RealRate_logo_horizontal.png"
RL_D = base64.b64encode(RL_PATH.read_bytes()).decode() if RL_PATH.exists() else None
print("  RealRate logo:", "OK" if RL_D else "MISSING")

LOGO_SVG_D = None  # SVG logo data (base64) — used when PNG logo unavailable

if COMPANY == "trilinc":
    B1_D   = try_fetch(["https://www.trilincglobal.com/wp-content/uploads/2023/05/gloria-website-photo.jpg"],
                       "Gloria Nelund") or try_wiki(["Gloria Nelund","TriLinc Global Impact Fund"], "Gloria Nelund")
    B2_D   = try_wiki(["Sustainable Development Goals","Social finance","Microfinance"], "Fund Overview")
    B6_D   = try_wiki(["Developing country","Sub-Saharan Africa"], "Globe/Impact")
    LOGO_D = None

elif COMPANY == "strata":
    B1_D   = try_wiki(["Air ambulance","Air medical services","Medical evacuation"], "Air Medical")
    B2_D   = try_wiki(["Critical care medicine","Intensive care medicine","Emergency medical services"], "Company Overview")
    B6_D   = try_wiki(["Helicopter","Aviation medicine","Emergency medicine"], "Helicopter")
    LOGO_D = try_fetch(["https://www.realrate-archive.com/us_air/logos/0001779128_256x256.png"], "Strata logo")

elif COMPANY == "hp":
    B1_D   = try_wiki(["Enrique Lores","HP Inc."], "Enrique Lores")
    B2_D   = try_wiki(["HP Inc.","Hewlett-Packard"], "HP Overview")
    B6_D   = try_wiki(["AI PC","HP LaserJet","Personal computer"], "HP Strategy")
    LOGO_D = try_fetch(["https://www.realrate-archive.com/us_computers/logos/0000047217_256x256.png"], "HP logo")

elif COMPANY == "angi":
    B1_D   = try_wiki(["Jeff Kip","Angi Inc.","HomeAdvisor"], "Jeff Kip / Angi")
    B2_D   = try_wiki(["Angi Inc.","HomeAdvisor","Home services"], "Angi Overview")
    B6_D   = try_wiki(["Home improvement","Home repair","Handyman"], "Highlights")
    LOGO_D = try_fetch(["https://www.realrate-archive.com/us_advertising/logos/0001707092_256x256.png"], "Angi logo")

elif COMPANY == "nvidia":
    B1_D    = try_wiki(["Jensen Huang","Nvidia"], "Jensen Huang")
    B2_D    = try_wiki(["Nvidia","Nvidia Headquarters"], "Nvidia Overview")
    B6_D    = None   # AI Leadership uses svg_neural icon
    LOGO_D  = try_fetch([
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Nvidia_logo.svg/320px-Nvidia_logo.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Nvidia_logo.svg/640px-Nvidia_logo.svg.png",
    ], "Nvidia logo")
    NV_GPU_D = try_wiki(["Hopper (microarchitecture)","Blackwell (microarchitecture)","Nvidia GPU","GeForce RTX 4090"], "GPU chip image")
    NV_DC_D  = try_wiki(["Data center","Server room","Cloud computing"], "Data center image")

elif COMPANY == "tesla":
    B1_D    = try_wiki(["Elon Musk","Tesla Motors"], "Elon Musk")
    B2_D    = try_wiki(["Tesla Inc.","Tesla Gigafactory Shanghai","Tesla Model Y"], "Tesla Overview")
    B6_D    = try_wiki(["Tesla Cybertruck","Tesla Model Y","Tesla Model 3"], "Tesla Car")
    LOGO_D  = None
    svg_local = Path(__file__).parent / "Tesla Inc" / "tesla_t_logo.svg"
    svg_url   = "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg"
    svg_cf    = cache_path(svg_url, ".svgcache")
    if svg_local.exists():
        LOGO_SVG_D = base64.b64encode(svg_local.read_bytes()).decode()
        print("  Tesla SVG logo OK (local)")
    elif svg_cf.exists():
        LOGO_SVG_D = svg_cf.read_text(); print("  Tesla SVG logo OK (cached)")
    else:
        LOGO_D = try_fetch([
            "https://www.tesla.com/apple-touch-icon.png",
            "https://digitalassets.tesla.com/tesla-contents/image/upload/Logomark_Red_RGB.png",
            "https://logo.clearbit.com/tesla.com",
        ], "Tesla logo PNG")
        if not LOGO_D:
            try:
                time.sleep(1.2)
                r = requests.get(svg_url, timeout=30, headers=HDRS, verify=False)
                r.raise_for_status()
                if b'<svg' in r.content[:500] or b'<?xml' in r.content[:10]:
                    LOGO_SVG_D = base64.b64encode(r.content).decode()
                    svg_cf.write_text(LOGO_SVG_D)
                    svg_local.write_bytes(r.content)
                    print("  Tesla SVG logo OK")
                else:
                    print("  Tesla SVG logo: unexpected content")
            except Exception as e:
                print(f"  Tesla SVG logo fail: {e}")

elif COMPANY == "apple":
    B1_D   = try_wiki(["Tim Cook","Apple Inc."], "Tim Cook")
    B2_D   = try_wiki(["Apple Park","Apple Campus 2","Apple Inc."], "Apple Overview")
    B6_D   = try_wiki(["iPhone 16","Apple Vision Pro","MacBook Pro"], "Apple Products")
    LOGO_D = try_fetch([
        "https://www.realrate-archive.com/us_computers/logos/0000320193_256x256.png",
    ], "Apple logo")

elif COMPANY == "harley":
    B1_D   = try_wiki(["Jochen Zeitz","Harley-Davidson"], "Jochen Zeitz / Harley")
    B2_D   = try_wiki(["Harley-Davidson","Milwaukee Wisconsin"], "Harley Overview")
    B6_D   = try_wiki(["Harley-Davidson motorcycle","Softail","Harley-Davidson"], "Harley Motorcycle")
    LOGO_D = try_fetch(["https://www.realrate-archive.com/us_motor/logos/0000793952_256x256.png"], "Harley logo")

# ── SVG icon builders ──────────────────────────────────────────────────────────
def svg_globe(cx, cy, col):
    return (f'<circle cx="{cx}" cy="{cy}" r="18" fill="none" stroke="{col}" stroke-width="2" opacity=".9"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="8" ry="18" fill="none" stroke="{col}" stroke-width="1.3" opacity=".65"/>'
            f'<line x1="{cx-18}" y1="{cy}" x2="{cx+18}" y2="{cy}" stroke="{col}" stroke-width="1.3" opacity=".65"/>'
            f'<line x1="{cx}" y1="{cy-18}" x2="{cx}" y2="{cy+18}" stroke="{col}" stroke-width="1" opacity=".5"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="18" ry="8" fill="none" stroke="{col}" stroke-width="1" opacity=".5"/>')

def svg_leaf(cx, cy, col):
    return (f'<path d="M{cx},{cy-18} C{cx+18},{cy-18} {cx+18},{cy+10} {cx},{cy+18} C{cx-18},{cy+10} {cx-18},{cy-18} {cx},{cy-18}Z" fill="none" stroke="{col}" stroke-width="2" opacity=".88"/>'
            f'<line x1="{cx}" y1="{cy-18}" x2="{cx}" y2="{cy+18}" stroke="{col}" stroke-width="1.3" opacity=".7"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{cx+12}" y2="{cy-8}" stroke="{col}" stroke-width="1" opacity=".55"/>'
            f'<line x1="{cx}" y1="{cy+5}" x2="{cx+11}" y2="{cy}" stroke="{col}" stroke-width="1" opacity=".55"/>')

def svg_handshake(cx, cy, col):
    return (f'<path d="M{cx-16},{cy+4} L{cx-6},{cy-4} L{cx+2},{cy-4} L{cx+16},{cy+4}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".88"/>'
            f'<path d="M{cx-8},{cy-4} L{cx-4},{cy-14} L{cx+4},{cy-14} L{cx+8},{cy-4}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".75"/>'
            f'<circle cx="{cx-14}" cy="{cy+8}" r="4" fill="none" stroke="{col}" stroke-width="1.5" opacity=".7"/>'
            f'<circle cx="{cx+14}" cy="{cy+8}" r="4" fill="none" stroke="{col}" stroke-width="1.5" opacity=".7"/>')

def svg_helicopter(cx, cy, col):
    return (f'<ellipse cx="{cx}" cy="{cy+4}" rx="14" ry="7" fill="none" stroke="{col}" stroke-width="2" opacity=".88"/>'
            f'<line x1="{cx-20}" y1="{cy-8}" x2="{cx+20}" y2="{cy-8}" stroke="{col}" stroke-width="2.5" stroke-linecap="round" opacity=".9"/>'
            f'<path d="M{cx+14},{cy+4} L{cx+22},{cy-2}" fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round" opacity=".75"/>'
            f'<line x1="{cx+20}" y1="{cy-5}" x2="{cx+20}" y2="{cy+1}" stroke="{col}" stroke-width="1.8" stroke-linecap="round" opacity=".75"/>'
            f'<line x1="{cx-8}" y1="{cy+11}" x2="{cx+8}" y2="{cy+11}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".7"/>'
            f'<line x1="{cx-6}" y1="{cy+8}" x2="{cx-6}" y2="{cy+11}" stroke="{col}" stroke-width="1.5" opacity=".6"/>'
            f'<line x1="{cx+6}" y1="{cy+8}" x2="{cx+6}" y2="{cy+11}" stroke="{col}" stroke-width="1.5" opacity=".6"/>'
            f'<line x1="{cx-3}" y1="{cy+1}" x2="{cx+3}" y2="{cy+1}" stroke="#EF4444" stroke-width="2.2" stroke-linecap="round" opacity=".9"/>'
            f'<line x1="{cx}" y1="{cy-2}" x2="{cx}" y2="{cy+4}" stroke="#EF4444" stroke-width="2.2" stroke-linecap="round" opacity=".9"/>')

def svg_cross(cx, cy, col):
    return (f'<rect x="{cx-4}" y="{cy-14}" width="8" height="28" rx="2" fill="{col}" opacity=".85"/>'
            f'<rect x="{cx-14}" y="{cy-4}" width="28" height="8" rx="2" fill="{col}" opacity=".85"/>')

def svg_growth(cx, cy, col):
    return (f'<polyline points="{cx-18},{cy+12} {cx-10},{cy+4} {cx-2},{cy+8} {cx+8},{cy-8} {cx+18},{cy-8}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'
            f'<polyline points="{cx+11},{cy-8} {cx+18},{cy-8} {cx+18},{cy-1}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'
            f'<line x1="{cx-18}" y1="{cy+16}" x2="{cx+18}" y2="{cy+16}" stroke="{col}" stroke-width="1.2" opacity=".5"/>')

def svg_house(cx, cy, col):
    return (f'<path d="M{cx-22},{cy-2} L{cx},{cy-20} L{cx+22},{cy-2}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'
            f'<path d="M{cx-16},{cy-2} L{cx-16},{cy+14} L{cx+16},{cy+14} L{cx+16},{cy-2}" fill="none" stroke="{col}" stroke-width="2" opacity=".85"/>'
            f'<rect x="{cx-6}" y="{cy+3}" width="12" height="11" rx="2" fill="none" stroke="{col}" stroke-width="1.5" opacity=".75"/>')

def svg_wrench(cx, cy, col):
    return (f'<path d="M{cx+8},{cy-14} L{cx+14},{cy-8} L{cx-6},{cy+12} L{cx-12},{cy+6} Z" fill="none" stroke="{col}" stroke-width="2" opacity=".85"/>'
            f'<circle cx="{cx+11}" cy="{cy-11}" r="5" fill="none" stroke="{col}" stroke-width="1.8" opacity=".82"/>'
            f'<circle cx="{cx-9}" cy="{cy+9}" r="4" fill="none" stroke="{col}" stroke-width="1.8" opacity=".78"/>')

def svg_chip(cx, cy, col):
    return (
        f'<rect x="{cx-13}" y="{cy-13}" width="26" height="26" rx="3" fill="none" stroke="{col}" stroke-width="2" opacity=".9"/>'
        f'<rect x="{cx-7}" y="{cy-7}" width="14" height="14" rx="2" fill="none" stroke="{col}" stroke-width="1.5" opacity=".7"/>'
        f'<line x1="{cx-13}" y1="{cy-7}" x2="{cx-19}" y2="{cy-7}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx-13}" y1="{cy+7}" x2="{cx-19}" y2="{cy+7}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx+13}" y1="{cy-7}" x2="{cx+19}" y2="{cy-7}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx+13}" y1="{cy+7}" x2="{cx+19}" y2="{cy+7}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx-7}" y1="{cy-13}" x2="{cx-7}" y2="{cy-19}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx+7}" y1="{cy-13}" x2="{cx+7}" y2="{cy-19}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx-7}" y1="{cy+13}" x2="{cx-7}" y2="{cy+19}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
        f'<line x1="{cx+7}" y1="{cy+13}" x2="{cx+7}" y2="{cy+19}" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>'
    )

def svg_neural(cx, cy, col):
    inp = [(cx-17, cy-10), (cx-17, cy), (cx-17, cy+10)]
    hid = [(cx, cy-7), (cx, cy+7)]
    out = [(cx+17, cy)]
    svg = ""
    for ix,iy in inp:
        for hx,hy in hid:
            svg += f'<line x1="{ix}" y1="{iy}" x2="{hx}" y2="{hy}" stroke="{col}" stroke-width="0.9" opacity=".42"/>'
    for hx,hy in hid:
        for ox,oy in out:
            svg += f'<line x1="{hx}" y1="{hy}" x2="{ox}" y2="{oy}" stroke="{col}" stroke-width="0.9" opacity=".42"/>'
    for nx,ny in inp:
        svg += f'<circle cx="{nx}" cy="{ny}" r="3.5" fill="{col}" opacity=".65"/>'
    for nx,ny in hid:
        svg += f'<circle cx="{nx}" cy="{ny}" r="4" fill="{col}" opacity=".85"/>'
    for nx,ny in out:
        svg += f'<circle cx="{nx}" cy="{ny}" r="5" fill="{col}" opacity="1"/>'
    return svg

def svg_trend(cx, cy, col, label="ECR"):
    return (f'<polyline points="{cx-18},{cy+10} {cx-10},{cy} {cx-2},{cy+6} {cx+8},{cy-10} {cx+18},{cy-10}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'
            f'<polyline points="{cx+12},{cy-10} {cx+18},{cy-10} {cx+18},{cy-4}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'
            f'<text x="{cx}" y="{cy+24}" font-family="Manrope,sans-serif" font-size="13" font-weight="700" fill="{col}" text-anchor="middle" opacity=".8">{label}</text>')

def svg_car(cx, cy, col):
    return (
        f'<rect x="{cx-20}" y="{cy-2}" width="40" height="13" rx="4" fill="none" stroke="{col}" stroke-width="2" opacity=".88"/>'
        f'<path d="M{cx-14},{cy-2} L{cx-10},{cy-14} L{cx+10},{cy-14} L{cx+14},{cy-2}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>'
        f'<circle cx="{cx-11}" cy="{cy+11}" r="5" fill="none" stroke="{col}" stroke-width="1.8" opacity=".9"/>'
        f'<circle cx="{cx+11}" cy="{cy+11}" r="5" fill="none" stroke="{col}" stroke-width="1.8" opacity=".9"/>'
        f'<line x1="{cx-5}" y1="{cy-2}" x2="{cx+5}" y2="{cy-2}" stroke="{col}" stroke-width="1.2" stroke-linecap="round" opacity=".5"/>'
    )

def svg_bolt(cx, cy, col):
    return (
        f'<path d="M{cx+5},{cy-16} L{cx-8},{cy+2} L{cx+2},{cy+2} L{cx-5},{cy+16} L{cx+8},{cy-2} L{cx-2},{cy-2} Z" '
        f'fill="{col}" opacity=".88"/>'
    )

def svg_motorcycle(cx, cy, col):
    return (
        f'<circle cx="{cx-10}" cy="{cy+8}" r="6" fill="none" stroke="{col}" stroke-width="2" opacity=".9"/>'
        f'<circle cx="{cx+10}" cy="{cy+8}" r="6" fill="none" stroke="{col}" stroke-width="2" opacity=".9"/>'
        f'<path d="M{cx-16},{cy+6} L{cx-4},{cy-8} L{cx+4},{cy-8} L{cx+10},{cy+2}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".88"/>'
        f'<path d="M{cx+4},{cy-8} L{cx+16},{cy-10}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" opacity=".75"/>'
        f'<path d="M{cx-6},{cy-8} L{cx-2},{cy-14} L{cx+2},{cy-14}" fill="none" stroke="{col}" stroke-width="1.5" stroke-linecap="round" opacity=".7"/>'
        f'<line x1="{cx-10}" y1="{cy+2}" x2="{cx+10}" y2="{cy+2}" stroke="{col}" stroke-width="1.2" stroke-opacity=".4"/>'
    )

# ── Reusable SVG component builders ───────────────────────────────────────────
def ecr_gauge(cx, cy, ecr_val, ecr_max, status, col=None):
    arc_r = 36
    c = col or LIME
    ea = (-math.pi/2) + 2*math.pi*min(ecr_val/ecr_max, 0.95)
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{arc_r}" fill="none" stroke="{c}" stroke-width="4" stroke-opacity=".15"/>'
        f'<path d="M{cx},{cy-arc_r} A{arc_r},{arc_r} 0 1,1 {cx+arc_r*math.cos(ea):.1f},{cy+arc_r*math.sin(ea):.1f}" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round" opacity=".82"/>'
        f'<text x="{cx}" y="{cy-7}" font-family="{F}" font-size="14" font-weight="700" fill="{c}" text-anchor="middle" opacity=".95" letter-spacing="1">ECR</text>'
        f'<text x="{cx}" y="{cy+12}" font-family="{F}" font-size="22" font-weight="800" fill="{WH}" text-anchor="middle">{ecr_val}%</text>'
        f'<text x="{cx}" y="{cy+27}" font-family="{F}" font-size="13" font-weight="700" fill="{c}" text-anchor="middle" opacity=".88">{status}</text>'
    )

def balance_sheet_svg(cx, cy, assets_label):
    return (
        f'<text x="{cx}" y="{cy-18}" font-family="{F}" font-size="14" font-weight="700" fill="{SKY}" text-anchor="middle" opacity=".95" letter-spacing="1">BALANCE SHEET</text>'
        + "".join(f'<rect x="{cx-22+i*11}" y="{cy+10-h}" width="8" height="{h}" rx="2" fill="{SKY}" opacity="{0.38+i*0.12}"/>' for i,h in enumerate([24,28,8,12,6]))
        + f'<text x="{cx}" y="{cy+28}" font-family="{F}" font-size="14" font-weight="700" fill="{SKY}" text-anchor="middle" opacity=".88">{assets_label}</text>'
    )

def pie_svg(cx, cy, r, segments, center_label, fsize=13):
    sa = -math.pi/2
    svg = ""
    for pct, sc in segments:
        sw = 2*math.pi*pct/100; ea = sa+sw
        x1 = cx+r*math.cos(sa); y1 = cy+r*math.sin(sa)
        x2 = cx+r*math.cos(ea); y2 = cy+r*math.sin(ea)
        svg += f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {1 if pct>50 else 0},1 {x2:.1f},{y2:.1f} Z" fill="{sc}" opacity=".68"/>'
        sa = ea
    svg += f'<circle cx="{cx}" cy="{cy}" r="16" fill="url(#gEmr)"/>'
    svg += f'<text x="{cx}" y="{cy+5}" font-family="{F}" font-size="{fsize}" fill="{EMER}" text-anchor="middle" font-weight="700">{center_label}</text>'
    return svg

def ecr_drivers_svg(cx, cy, plus_label, minus_label, ecr_pct, status, col=None):
    c = col or EMER
    return (
        f'<text x="{cx}" y="{cy-22}" font-family="{F}" font-size="12" font-weight="700" fill="{c}" text-anchor="middle" opacity=".95" letter-spacing="1">ECR DRIVERS</text>'
        f'<rect x="{cx-32}" y="{cy-9}" width="24" height="10" rx="2" fill="{LIME}" opacity=".78"/>'
        f'<text x="{cx-20}" y="{cy}" font-family="{F}" font-size="12" font-weight="800" fill="#050B18" text-anchor="middle">{plus_label}</text>'
        f'<rect x="{cx+8}" y="{cy-9}" width="24" height="10" rx="2" fill="#EF4444" opacity=".72"/>'
        f'<text x="{cx+20}" y="{cy}" font-family="{F}" font-size="12" font-weight="800" fill="{WH}" text-anchor="middle">{minus_label}</text>'
        f'<text x="{cx}" y="{cy+18}" font-family="{F}" font-size="22" font-weight="800" fill="{WH}" text-anchor="middle">{ecr_pct}</text>'
        f'<text x="{cx}" y="{cy+32}" font-family="{F}" font-size="12" font-weight="700" fill="{c}" text-anchor="middle" opacity=".88">{status}</text>'
    )

# ── Shared helpers ─────────────────────────────────────────────────────────────
def cedge(cx,cy,r,tx,ty):
    angle = math.atan2(ty-cy, tx-cx)
    return int(cx+r*math.cos(angle)), int(cy+r*math.sin(angle))

def ico(kind,x,y,col):
    cx,cy=x+10,y+10
    if kind=="clock":
        return (f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="{col}" stroke-width="1.6" opacity=".85"/>'
                f'<line x1="{cx}" y1="{cy-4}" x2="{cx}" y2="{cy}" stroke="{col}" stroke-width="1.6" stroke-linecap="round" opacity=".85"/>'
                f'<line x1="{cx}" y1="{cy}" x2="{cx+4}" y2="{cy+3}" stroke="{col}" stroke-width="1.6" stroke-linecap="round" opacity=".85"/>')
    if kind=="star":
        pts=[]
        for i in range(10):
            a_=math.pi*i/5-math.pi/2; r_=8 if i%2==0 else 3.5
            pts.append(f"{cx+r_*math.cos(a_):.1f},{cy+r_*math.sin(a_):.1f}")
        return f'<polygon points="{" ".join(pts)}" fill="{col}" opacity=".8"/>'
    if kind=="chart":
        bars=[(x,y+12,3,8),(x+4,y+6,3,14),(x+8,y+2,3,18),(x+12,y+7,3,13),(x+16,y+4,3,16)]
        return "".join(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="1" fill="{col}" opacity=".8"/>' for bx,by,bw,bh in bars)
    if kind=="trending":
        return (f'<polyline points="{x+1},{y+16} {x+6},{y+10} {x+11},{y+13} {x+16},{y+4} {x+19},{y+4}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>'
                f'<polyline points="{x+14},{y+4} {x+19},{y+4} {x+19},{y+9}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>')
    if kind=="globe":
        return (f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="{col}" stroke-width="1.5" opacity=".82"/>'
                f'<ellipse cx="{cx}" cy="{cy}" rx="4" ry="8" fill="none" stroke="{col}" stroke-width="1" opacity=".68"/>'
                f'<line x1="{x+2}" y1="{cy}" x2="{x+18}" y2="{cy}" stroke="{col}" stroke-width="1" opacity=".68"/>')
    if kind=="building":
        return (f'<rect x="{x+3}" y="{y+3}" width="14" height="15" rx="1" fill="none" stroke="{col}" stroke-width="1.5" opacity=".8"/>'
                f'<rect x="{x+7}" y="{y+10}" width="3" height="8" rx=".5" fill="{col}" opacity=".7"/>'
                f'<rect x="{x+11}" y="{y+10}" width="3" height="8" rx=".5" fill="{col}" opacity=".7"/>'
                f'<line x1="{x+3}" y1="{y+9}" x2="{x+17}" y2="{y+9}" stroke="{col}" stroke-width="1" opacity=".55"/>')
    if kind=="dollar":
        return f'<text x="{x+3}" y="{y+17}" font-family="{F}" font-size="20" font-weight="800" fill="{col}" opacity=".75">$</text>'
    if kind=="leaf":
        return (f'<path d="M{cx},{cy-8} C{cx+8},{cy-8} {cx+8},{cy+5} {cx},{cy+8} C{cx-8},{cy+5} {cx-8},{cy-8} {cx},{cy-8}Z" fill="none" stroke="{col}" stroke-width="1.6" opacity=".85"/>'
                f'<line x1="{cx}" y1="{cy-8}" x2="{cx}" y2="{cy+8}" stroke="{col}" stroke-width="1.3" opacity=".7"/>')
    if kind=="news":
        return (f'<rect x="{x+1}" y="{y+1}" width="18" height="16" rx="2" fill="none" stroke="{col}" stroke-width="1.5" opacity=".78"/>'
                f'<line x1="{x+4}" y1="{y+7}" x2="{x+16}" y2="{y+7}" stroke="{col}" stroke-width="1.3" opacity=".75"/>'
                f'<line x1="{x+4}" y1="{y+11}" x2="{x+14}" y2="{y+11}" stroke="{col}" stroke-width="1.3" opacity=".75"/>')
    if kind=="people":
        return (f'<circle cx="{cx-5}" cy="{cy-5}" r="4" fill="none" stroke="{col}" stroke-width="1.5" opacity=".82"/>'
                f'<path d="M{cx-13},{cy+8} Q{cx-5},{cy+2} {cx+3},{cy+8}" fill="none" stroke="{col}" stroke-width="1.5" opacity=".75"/>'
                f'<circle cx="{cx+5}" cy="{cy-5}" r="4" fill="none" stroke="{col}" stroke-width="1.5" opacity=".82"/>'
                f'<path d="M{cx-3},{cy+8} Q{cx+5},{cy+2} {cx+13},{cy+8}" fill="none" stroke="{col}" stroke-width="1.5" opacity=".75"/>')
    return ""

# ══════════════════════════════════════════════════════════════════════════════
def build():
    p=[]; a=p.append

    HX,HY,HW,HH = 700,348,480,292
    HCX,HCY = HX+HW//2, HY+HH//2   # 940, 494

    # Branch circles
    B1_CX,B1_CY,B1_R = 640,300,82   # AMBER
    B7_CX,B7_CY,B7_R = 600,600,68   # PURP
    B2_CX,B2_CY,B2_R = 940,130,64   # CYAN
    B3_CX,B3_CY,B3_R = 1400,200,64  # LIME
    B4_CX,B4_CY,B4_R = 1480,430,62  # SKY
    B5_CX,B5_CY,B5_R = 1390,720,62  # EMER
    B6_CX,B6_CY,B6_R = 920,820,62   # ORAN

    # Decorative circles
    D1_CX,D1_CY,D1_R = 700,  820, 44
    D2_CX,D2_CY,D2_R = 1155, 770, 44
    D3_CX,D3_CY,D3_R = 220,  623, 44
    D4_CX,D4_CY,D4_R = 1170, 185, 44

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="none">')
    a('<defs>')
    a(f'''
  <radialGradient id="bg"  cx="50%" cy="45%" r="60%"><stop offset="0%" stop-color="#0D1F3E"/><stop offset="100%" stop-color="{BG}"/></radialGradient>
  <radialGradient id="hGl" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{ACCENT}" stop-opacity=".18"/><stop offset="65%" stop-color="{ACCENT}" stop-opacity=".04"/><stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gHub"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0E2040"/><stop offset="100%" stop-color="#060C1A"/></linearGradient>
  <linearGradient id="gAmb"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1C1100"/><stop offset="100%" stop-color="#0D0800"/></linearGradient>
  <linearGradient id="gCyn"  x1="100%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#001A20"/><stop offset="100%" stop-color="#000E14"/></linearGradient>
  <linearGradient id="gLme"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0A1800"/><stop offset="100%" stop-color="#060C00"/></linearGradient>
  <linearGradient id="gSky"  x1="100%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#001428"/><stop offset="100%" stop-color="#000A18"/></linearGradient>
  <linearGradient id="gEmr"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#001C12"/><stop offset="100%" stop-color="#000C08"/></linearGradient>
  <linearGradient id="gPnk"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1C0016"/><stop offset="100%" stop-color="#0D000C"/></linearGradient>
  <linearGradient id="gPrp"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0E0620"/><stop offset="100%" stop-color="#07030E"/></linearGradient>
  <linearGradient id="gOrn"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#3A1200"/><stop offset="100%" stop-color="#1A0800"/></linearGradient>
  <linearGradient id="gMH"   x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1A0038"/><stop offset="100%" stop-color="{PURP}"/></linearGradient>
  <linearGradient id="gTBlu"  x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#001040"/><stop offset="100%" stop-color="#000820"/></linearGradient>
  <linearGradient id="gTAqua" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#001D2E"/><stop offset="100%" stop-color="#000F1A"/></linearGradient>
  <linearGradient id="branchGrad" x1="{HX}" y1="{HY}" x2="{HX+HW}" y2="{HY}" gradientUnits="userSpaceOnUse">
    <stop offset="0%"   stop-color="{AMBER}"/>
    <stop offset="15%"  stop-color="{PURP}"/>
    <stop offset="29%"  stop-color="{CYAN}"/>
    <stop offset="50%"  stop-color="{ACCENT}"/>
    <stop offset="71%"  stop-color="{LIME}"/>
    <stop offset="85%"  stop-color="{SKY}"/>
    <stop offset="100%" stop-color="{ORAN}"/>
  </linearGradient>
  <clipPath id="b1Clip"><circle cx="{B1_CX}" cy="{B1_CY}" r="{B1_R}"/></clipPath>
  <clipPath id="b2Clip"><circle cx="{B2_CX}" cy="{B2_CY}" r="{B2_R}"/></clipPath>
  <clipPath id="b6Clip"><circle cx="{B6_CX}" cy="{B6_CY}" r="{B6_R}"/></clipPath>
  <clipPath id="b7Clip"><circle cx="{B7_CX}" cy="{B7_CY}" r="{B7_R}"/></clipPath>
  <clipPath id="d1Clip"><circle cx="{D1_CX}" cy="{D1_CY}" r="{D1_R}"/></clipPath>
  <clipPath id="d2Clip"><circle cx="{D2_CX}" cy="{D2_CY}" r="{D2_R}"/></clipPath>
  <clipPath id="d3Clip"><circle cx="{D3_CX}" cy="{D3_CY}" r="{D3_R}"/></clipPath>
  <clipPath id="d4Clip"><circle cx="{D4_CX}" cy="{D4_CY}" r="{D4_R}"/></clipPath>
  <filter id="g5"     x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur in="SourceGraphic" stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="halo"   x="-120%" y="-120%" width="340%" height="340%"><feGaussianBlur in="SourceGraphic" stdDeviation="24"/></filter>
  <filter id="halo2"  x="-60%"  y="-60%"  width="220%" height="220%"><feGaussianBlur in="SourceGraphic" stdDeviation="11"/></filter>
  <filter id="borderGlow" x="-18%" y="-25%" width="136%" height="150%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="14" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="gHubGlow" cx="50%" cy="44%" r="58%"><stop offset="0%" stop-color="{ACCENT}" stop-opacity=".22"/><stop offset="50%" stop-color="{ACCENT}" stop-opacity=".06"/><stop offset="100%" stop-color="{BG}" stop-opacity="0"/></radialGradient>
  <clipPath id="hubClip"><circle cx="{HCX}" cy="{HCY}" r="200"/></clipPath>
  <filter id="innerGlow" x="0%" y="0%" width="100%" height="100%"><feGaussianBlur in="SourceGraphic" stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="b"/></feMerge></filter>
    ''')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    GRID = 240
    for gy in range(0, H+1, GRID):
        a(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" stroke="{ACCENT}" stroke-width="0.7" stroke-opacity=".18"/>')
    for gx in range(0, W+1, GRID):
        a(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" stroke="{ACCENT}" stroke-width="0.7" stroke-opacity=".18"/>')
    for gy in range(0, H+1, GRID):
        for gx in range(0, W+1, GRID):
            a(f'<circle cx="{gx}" cy="{gy}" r="3" fill="{ACCENT}" opacity=".45"/>')

    a(f'<ellipse cx="{HCX}" cy="{HCY}" rx="560" ry="370" fill="url(#hGl)"/>')

    for dx,dy,dr,dc,dop in [
        (188,748,3,AMBER,.28),(312,82,2,ACCENT,.24),(1722,142,3,PURP,.24),(1632,952,2,ACCENT,.27),
        (858,50,2,LIME,.2),(1098,1030,2,PURP,.2),(502,515,1.5,ACCENT,.14),(1438,575,1.5,AMBER,.14),
        (658,988,2,ACCENT,.17),(1288,76,2,LIME,.17),(448,298,1.5,CYAN,.11),(1564,385,1.5,SKY,.11)]:
        a(f'<circle cx="{dx}" cy="{dy}" r="{dr}" fill="{dc}" opacity="{dop}"/>')

    def t(x,y,s,sz=13,col=WH,anch="start",wt="400",op=1,sp="0"):
        a(f'<text x="{x}" y="{y}" font-family="{F}" font-size="{sz}" font-weight="{wt}" '
          f'fill="{col}" text-anchor="{anch}" opacity="{op}" letter-spacing="{sp}">{s}</text>')

    def mline(x1,y1,cp1x,cp1y,cp2x,cp2y,x2,y2,col):
        q=f"M{x1},{y1} C{cp1x},{cp1y} {cp2x},{cp2y} {x2},{y2}"
        a(f'<path d="{q}" fill="none" stroke="{col}" stroke-width="48" stroke-opacity=".042" stroke-linecap="round"/>')
        a(f'<path d="{q}" fill="none" stroke="{col}" stroke-width="18" stroke-opacity=".16" stroke-linecap="round"/>')
        a(f'<path d="{q}" fill="none" stroke="{col}" stroke-width="3.8" stroke-opacity="1" stroke-linecap="round"/>')
        a(f'<circle cx="{x1}" cy="{y1}" r="7" fill="{col}" opacity=".92" filter="url(#g5)"/>')
        a(f'<circle cx="{x2}" cy="{y2}" r="5" fill="{col}" opacity=".6"/>')

    def sline(x1,y1,cpx,cpy,x2,y2,col):
        q=f"M{x1},{y1} Q{cpx},{cpy} {x2},{y2}"
        a(f'<path d="{q}" fill="none" stroke="{col}" stroke-width="12" stroke-opacity=".07" stroke-linecap="round"/>')
        a(f'<path d="{q}" fill="none" stroke="{col}" stroke-width="2.2" stroke-opacity=".82" stroke-linecap="round"/>')
        a(f'<circle cx="{x2}" cy="{y2}" r="3.5" fill="{col}" opacity=".52"/>')

    def white_box(x, y, w, h, col=None, op=.35):
        c = col or ACCENT
        a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="white" opacity=".97"/>')
        a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{c}" stroke-width=".5" stroke-opacity="{op}"/>')

    def hub_logo_png(x, y, data, size=64, box=72):
        white_box(x, y, box, box, op=.3)
        if data:
            pad = (box - size) // 2
            a(f'<image href="data:{raster_mime(data)};base64,{data}" x="{x+pad}" y="{y+pad}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet"/>')
        return bool(data)

    def draw_circle(cx, cy, r, col, grad, label, *,
                    img=None, clip_id=None, svg_icon=None, inner_svg=None, fallback="?"):
        a(f'<circle cx="{cx}" cy="{cy}" r="{r+16}" fill="{col}" opacity=".05" filter="url(#halo2)"/>')
        a(f'<circle cx="{cx}" cy="{cy}" r="{r+6}" fill="none" stroke="{col}" stroke-width="1.2" stroke-opacity=".28" stroke-dasharray="5,4"/>')
        a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{grad})"/>')
        if inner_svg:
            a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="2.5" stroke-opacity=".7"/>')
            a(inner_svg)
        else:
            if img:
                a(f'<image href="data:{raster_mime(img)};base64,{img}" x="{cx-r}" y="{cy-r}" width="{r*2}" height="{r*2}" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMid slice"/>')
            elif svg_icon:
                a(svg_icon)
            else:
                t(cx, cy+8, fallback, 32, WH, "middle", "800")
            a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="2.8" stroke-opacity=".72"/>')
        lw = max(220, len(label)*12+22)
        a(f'<rect x="{cx-lw//2}" y="{cy+r+7}" width="{lw}" height="40" rx="10" fill="url(#{grad})" stroke="{col}" stroke-width=".9" stroke-opacity=".52"/>')
        t(cx, cy+r+35, label, 20, col, "middle", "800", sp=".5")

    def snode(nx,ny,nw,nh,col,grad,line1,line2="",icon_kind=""):
        a(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10" fill="url(#{grad})" stroke="{col}" stroke-width=".9" stroke-opacity=".42"/>')
        a(f'<rect x="{nx}" y="{ny+7}" width="3" height="{nh-14}" rx="1.5" fill="{col}" opacity=".8"/>')
        if icon_kind:
            ix=nx+nw-30; iy=ny+(nh-22)//2
            a(f'<rect x="{ix-4}" y="{iy-4}" width="30" height="30" rx="6" fill="{col}" fill-opacity=".08"/>')
            a(ico(icon_kind,ix,iy,col))
        tx=nx+14; tw=nw-16-(46 if icon_kind else 0)
        a(f'<svg x="{tx}" y="{ny}" width="{tw}" height="{nh}" overflow="hidden">')
        if line2:
            a(f'<text x="0" y="{nh//2-7}" font-family="{F}" font-size="22" font-weight="800" fill="{WH}" opacity="1">{line1}</text>')
            a(f'<text x="0" y="{nh//2+18}" font-family="{F}" font-size="18" font-weight="600" fill="{col}" opacity=".96">{line2}</text>')
        else:
            a(f'<text x="0" y="{nh//2+8}" font-family="{F}" font-size="22" font-weight="800" fill="{WH}" opacity="1">{line1}</text>')
        a('</svg>')

    # ── MAIN LINES ────────────────────────────────────────────────────────────
    ex1,ey1 = cedge(B1_CX,B1_CY,B1_R, 772,385)
    mline(772,385, 720,360, 680,335, ex1,ey1, AMBER)
    ex2,ey2 = cedge(B2_CX,B2_CY,B2_R, 940,294)
    mline(940,294, 938,260, 940,220, ex2,ey2, CYAN)
    ex3,ey3 = cedge(B3_CX,B3_CY,B3_R, 1108,385)
    mline(1108,385, 1200,310, 1340,244, ex3,ey3, LIME)
    ex4,ey4 = cedge(B4_CX,B4_CY,B4_R, 1138,473)
    mline(1138,473, 1265,462, 1398,446, ex4,ey4, SKY)
    ex5,ey5 = cedge(B5_CX,B5_CY,B5_R, 1098,592)
    mline(1098,592, 1218,635, 1328,675, ex5,ey5, EMER)
    ex6,ey6 = cedge(B6_CX,B6_CY,B6_R, 933,694)
    mline(933,694, 930,742, 924,778, ex6,ey6, ORAN)
    ex7,ey7 = cedge(B7_CX,B7_CY,B7_R, 749,554)
    mline(749,554, 690,565, 634,578, ex7,ey7, PURP)

    # ── SUB LINES ─────────────────────────────────────────────────────────────
    s1_ce = cedge(B1_CX,B1_CY,B1_R, 225,147)
    sline(*s1_ce, 450,220, 225,147, AMBER)
    s2_ce = cedge(B1_CX,B1_CY,B1_R, 225,283)
    sline(*s2_ce, 450,296, 225,283, AMBER)
    s3_ce = cedge(B1_CX,B1_CY,B1_R, 225,479)
    sline(*s3_ce, 450,430, 225,479, AMBER)

    ap1_ce = cedge(B2_CX,B2_CY,B2_R, 665,57)
    sline(*ap1_ce, 810,92, 665,57, CYAN)
    ap2_ce = cedge(B2_CX,B2_CY,B2_R, 1225,57)
    sline(*ap2_ce, 1160,90, 1225,57, CYAN)

    in1_ce = cedge(B3_CX,B3_CY,B3_R, 1689,51)
    sline(*in1_ce, 1500,126, 1689,51, LIME)
    in2_ce = cedge(B3_CX,B3_CY,B3_R, 1689,147)
    sline(*in2_ce, 1500,174, 1689,147, LIME)

    fn1_ce = cedge(B4_CX,B4_CY,B4_R, 1735,291)
    sline(*fn1_ce, 1558,362, 1735,291, SKY)
    fn2_ce = cedge(B4_CX,B4_CY,B4_R, 1735,387)
    sline(*fn2_ce, 1558,416, 1735,387, SKY)
    fn3_ce = cedge(B4_CX,B4_CY,B4_R, 1735,483)
    sline(*fn3_ce, 1558,460, 1735,483, SKY)

    b5_1ce = cedge(B5_CX,B5_CY,B5_R, 1682,663)
    sline(*b5_1ce, 1464,692, 1682,663, EMER)
    b5_2ce = cedge(B5_CX,B5_CY,B5_R, 1622,759)
    sline(*b5_2ce, 1464,730, 1622,759, EMER)
    b5_3ce = cedge(B5_CX,B5_CY,B5_R, 1682,855)
    sline(*b5_3ce, 1464,788, 1682,855, EMER)

    b6_1ce = cedge(B6_CX,B6_CY,B6_R, 720,983)
    sline(*b6_1ce, 820,940, 720,983, ORAN)
    b6_2ce = cedge(B6_CX,B6_CY,B6_R, 1110,983)
    sline(*b6_2ce, 960,942, 1110,983, ORAN)
    b6_3ce = cedge(B6_CX,B6_CY,B6_R, 1500,983)
    sline(*b6_3ce, 1062,942, 1500,983, ORAN)

    b7_1ce = cedge(B7_CX,B7_CY,B7_R, 215,768)
    sline(*b7_1ce, 430,680, 215,768, PURP)
    b7_2ce = cedge(B7_CX,B7_CY,B7_R, 215,864)
    sline(*b7_2ce, 430,762, 215,864, PURP)
    b7_3ce = cedge(B7_CX,B7_CY,B7_R, 215,960)
    sline(*b7_3ce, 430,842, 215,960, PURP)

    # ══════════════════════════════════════════════════════════════════════════
    # COMPANY-SPECIFIC BRANCH CONTENT
    # ══════════════════════════════════════════════════════════════════════════
    if COMPANY == "trilinc":

        # B1 — GLORIA NELUND
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Gloria Nelund  ·  CEO", img=B1_D, clip_id="b1Clip")
        snode(15,104, 420,86,AMBER,"gAmb","CEO, Founder &amp; President","Chief Compliance Officer · TriLinc","star")
        snode(15,240, 420,86,AMBER,"gAmb","Deutsche Bank: CEO US Private Wealth","Managed $50B · World's 5th largest bank","chart")
        snode(15,436, 420,86,AMBER,"gAmb","Founded TriLinc 2008","40+ years in international asset management","trending")

        # B2 — FUND OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","FUND OVERVIEW", img=B2_D, clip_id="b2Clip", fallback="FO")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: 2008  ·  Delaware, USA","Ticker: TRLC  ·  Public offering closed 2017","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~$1.4B AUM  ·  TriLinc Global Advisors","Female-founded  ·  -owned  ·  -led","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,124,150,"TOP-RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 124%  ·  Top-Rated  ·  RealRate","#1 of 4 US Finance Services companies","star")
        snode(1474,104, 430,86,LIME,"gLme","46pp above industry avg (78%)","Highest ECR in US Finance Services 2025","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$282.8M"))
        snode(1560,248, 350,86,SKY,"gSky","Total Assets: $282.8M","Stockholders&apos; Equity: $272.6M","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Liabilities: $10.2M","Equity-to-Assets ratio: 96.4%","chart")
        snode(1560,440, 350,86,SKY,"gSky","Net Income: –$8.5M","ECR driver: Equity +57pp · Revenue –17pp","trending")

        # B5 — INVESTMENT STRATEGY
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","INVESTMENT STRATEGY",
            inner_svg=pie_svg(B5_CX,B5_CY,32,[(40,LIME),(30,CYAN),(20,AMBER),(10,EMER)],"SME"))
        snode(1462,620, 440,86,EMER,"gEmr","Direct loans  ·  Loan participations","Trade finance  ·  Convertible debt","dollar")
        snode(1462,716, 440,86,EMER,"gEmr","Target: SMEs with &lt;500 employees","Developing economies  ·  local sub-advisors","globe")
        snode(1462,812, 440,86,EMER,"gEmr","Structured credit  ·  Preferred equity","Growth-stage businesses  ·  4 continents","chart")

        # B6 — IMPACT FOCUS
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","IMPACT FOCUS",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_leaf(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","Building Sustainable Communities","Education · Energy · Housing · Health","leaf")
        snode(920,940, 380,86,ORAN,"gOrn","Strengthening the Workforce","Job creation · Equality · Capacity building","people")
        snode(1310,940,380,86,ORAN,"gOrn","Financial inclusion  ·  Food security","Measurable social impact metrics tracked","globe")

        # B7 — MISSION & HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Mission &amp; History",
            svg_icon=svg_handshake(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","2008: Founded  ·  Delaware, USA","Female-founded  ·  -owned  ·  -led fund","clock")
        snode(15,821, 400,86,PURP,"gPrp","2017: Public offering closed","TRLC listed  ·  OTC Pink Markets","trending")
        snode(15,917, 400,86,PURP,"gPrp","2025: #1 US Finance Services · RealRate","Named Top Real Leader of Impact Investing","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, ORAN,"gOrn","Global Reach",
            img=B6_D, clip_id="d1Clip", svg_icon=svg_globe(D1_CX,D1_CY,ORAN))
        draw_circle(D2_CX,D2_CY,D2_R, EMER,"gEmr","Sub-Advisors",
            svg_icon=svg_handshake(D2_CX,D2_CY,EMER))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"ECR +46pp"))
        draw_circle(D4_CX,D4_CY,D4_R, CYAN,"gCyn","$1.4B AUM", fallback=" ")
        t(D4_CX, D4_CY-6, "$1.4B", 22, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "AUM", 16, CYAN, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "124%", "#1 / 4", "Top-Rated"

    elif COMPANY == "strata":

        # B1 — AIR MEDICAL SERVICES
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Air Medical Services",
            img=B1_D, clip_id="b1Clip", svg_icon=svg_helicopter(B1_CX,B1_CY,AMBER))
        snode(15,104, 420,86,AMBER,"gAmb","Air Medical Transport  ·  Critical Care","Emergency Response Services","star")
        snode(15,240, 420,86,AMBER,"gAmb","OTC-listed  ·  CIK: 0001779128  ·  Delaware","Air ambulance services  ·  US market","building")
        snode(15,436, 420,86,AMBER,"gAmb","Critical airborne medical transport","Serving patients across US air network","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="CO")
        snode(460,14, 410,86,CYAN,"gCyn","Air Medical Transport  ·  Critical Care","Emergency Response  ·  Delaware, USA","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","CIK: 0001779128  ·  OTC-listed  ·  STCM","US Air Industry  ·  Publicly reporting","news")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,123,150,"TOP-RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 123%  ·  Top-Rated  ·  RealRate","#1 of 4 US Air companies","star")
        snode(1474,104, 430,86,LIME,"gLme","54pp above industry avg (69%)","Highest ECR in US Air 2025","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$325.5M"))
        snode(1560,248, 350,86,SKY,"gSky","Total Assets: $325.5M","Stockholders&apos; Equity: $279.1M","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Liabilities: $46.4M","Revenue: $197.1M (FY2025)","chart")
        snode(1560,440, 350,86,SKY,"gSky","Net Income: +$41.3M","First profitable year in company history","trending")

        # B5 — ECR ANALYSIS
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","ECR ANALYSIS",
            inner_svg=ecr_drivers_svg(B5_CX,B5_CY,"+46pp","–81pp","123%","TOP-RATED"))
        snode(1462,620, 440,86,EMER,"gEmr","Greatest Strength: Operating Expenses","+46pp contribution to ECR","chart")
        snode(1462,716, 440,86,EMER,"gEmr","Greatest Weakness: Other Expenses","–81pp drag on ECR","trending")
        snode(1462,812, 440,86,EMER,"gEmr","ECR: 123%  ·  54pp above industry avg","Market average: 69%","star")

        # B6 — 2025 HIGHLIGHTS
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","2025 HIGHLIGHTS",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_helicopter(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","FY2025 Revenue: $197.1M","Net Income: +$41.3M (first profitable)","dollar")
        snode(920,940, 380,86,ORAN,"gOrn","Equity: $279.1M  ·  Assets: $325.5M","Equity-to-Assets ratio: 85.8%","chart")
        snode(1310,940,380,86,ORAN,"gOrn","ECR trajectory: 87→92→73→90→123%","Consistent upward ECR momentum","trending")

        # B7 — GROWTH JOURNEY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Growth Journey",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","2021: Revenue $50.5M  ·  Net Income –$40.1M","Rapid expansion phase begins","clock")
        snode(15,821, 400,86,PURP,"gPrp","2022–2024: Revenue $146M → $249M","~4× growth in 3 years","trending")
        snode(15,917, 400,86,PURP,"gPrp","2025: ECR 123%  ·  #1 US Air  ·  RealRate","First profitable year in history","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, AMBER,"gAmb","Air Fleet",
            img=B6_D, clip_id="d1Clip", svg_icon=svg_helicopter(D1_CX,D1_CY,AMBER))
        draw_circle(D2_CX,D2_CY,D2_R, CYAN,"gCyn","Medical Care",
            svg_icon=svg_cross(D2_CX,D2_CY,CYAN))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"→ 123%"))
        draw_circle(D4_CX,D4_CY,D4_R, SKY,"gSky","Revenue", fallback=" ")
        t(D4_CX, D4_CY-6,  "$197M", 22, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "FY2025", 16, SKY, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "123%", "#1 / 4", "Top-Rated"

    elif COMPANY == "hp":

        # B1 — ENRIQUE LORES
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Enrique Lores  ·  CEO", img=B1_D, clip_id="b1Clip")
        snode(15,104, 420,86,AMBER,"gAmb","President &amp; CEO since November 2019","Joined HP in 1989  ·  35+ years with HP","star")
        snode(15,240, 420,86,AMBER,"gAmb","Led Imaging, Printing &amp; Solutions","MBA IESE  ·  Industrial Engineering","chart")
        snode(15,436, 420,86,AMBER,"gAmb","'Future Ready' transformation plan","AI PCs  ·  Subscriptions  ·  Cost efficiency","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="HP")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: 1939  ·  Palo Alto, California","Split from Hewlett-Packard: November 2015","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~58,000 employees worldwide","HQ: 1501 Page Mill Rd  ·  Palo Alto, CA","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,258,300,"RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 258%  ·  Rated  ·  RealRate","#9 of 17 US Computers companies","star")
        snode(1474,104, 430,86,LIME,"gLme","At the industry average (258%)","Balance sheet leverage offsets revenue strength","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$39.9B"))
        snode(1560,248, 350,86,SKY,"gSky","Revenue: $53.6B (FY2024)","Net Income: $2.8B  ·  EPS: $2.81","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Operating margin: 7.1%","R&amp;D investment: $1.64B","chart")
        snode(1560,440, 350,86,SKY,"gSky","Total Assets: $39.9B  ·  Cash: $3.25B","LT Debt: $8.3B  ·  Equity Deficit: –$1.3B","trending")

        # B5 — BUSINESS SEGMENTS
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","BUSINESS SEGMENTS",
            inner_svg=pie_svg(B5_CX,B5_CY,32,[(64.3,LIME),(35.7,CYAN)],"2 SEG",fsize=7))
        snode(1462,620, 440,86,EMER,"gEmr","Personal Systems: ~$34.4B  ·  64%","PCs  ·  Laptops  ·  Workstations  ·  Chromebooks","chart")
        snode(1462,716, 440,86,EMER,"gEmr","Printing: ~$19.1B  ·  36%","LaserJet  ·  OfficeJet  ·  Instant Ink  ·  Supplies","dollar")
        snode(1462,812, 440,86,EMER,"gEmr","Stockholders&apos; Equity: –$1.3B","Liabilities: $41.2B  ·  Buyback-driven balance sheet","trending")

        # B6 — STRATEGY & INNOVATION
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","STRATEGY &amp; INNOVATION",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_globe(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","AI PC leadership  ·  HP Omnibook Ultra","Neural Processing Unit  ·  Windows AI integration","trending")
        snode(920,940, 380,86,ORAN,"gOrn","HP+ Instant Ink subscription model","Recurring revenue  ·  Sustainability  ·  HP Planet Partners","leaf")
        snode(1310,940,380,86,ORAN,"gOrn","Poly collaboration hardware (acq. 2022)","Hybrid work solutions  ·  Video conferencing","globe")

        # B7 — COMPANY HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Company History",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","1939: Founded by Hewlett &amp; Packard","Palo Alto garage  ·  HP200A audio oscillator","clock")
        snode(15,821, 400,86,PURP,"gPrp","2015: HP splits into HP Inc. &amp; HPE","HP Inc. keeps HPQ  ·  PC &amp; Printer business","trending")
        snode(15,917, 400,86,PURP,"gPrp","FY2024: Revenue $53.6B  ·  ECR 258%  ·  RealRate","'Future Ready' AI transformation underway","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, ORAN,"gOrn","Global Reach",
            img=B6_D, clip_id="d1Clip", svg_icon=svg_globe(D1_CX,D1_CY,ORAN))
        draw_circle(D2_CX,D2_CY,D2_R, CYAN,"gCyn","Poly &amp; Collab",
            svg_icon=svg_handshake(D2_CX,D2_CY,CYAN))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"258%"))
        draw_circle(D4_CX,D4_CY,D4_R, SKY,"gSky","$53.6B", fallback=" ")
        t(D4_CX, D4_CY-6, "$53.6B", 19, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "Revenue", 14, SKY, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "258%", "#9 / 17", "Rated"

    elif COMPANY == "angi":

        # B1 — JEFF KIP / LEADERSHIP
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Jeff Kip  ·  CEO",
            img=B1_D, clip_id="b1Clip", svg_icon=svg_house(B1_CX,B1_CY,AMBER))
        snode(15,104, 420,86,AMBER,"gAmb","Chief Executive Officer, Angi Inc.","NASDAQ: ANGI  ·  Denver, Colorado","star")
        snode(15,240, 420,86,AMBER,"gAmb","IAC subsidiary  ·  ~4,500 employees","Brands: Angi  ·  HomeAdvisor  ·  Handy","building")
        snode(15,436, 420,86,AMBER,"gAmb","Platform transformation  ·  AI integration","Connecting homeowners with professionals","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="AN")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: 1995  ·  Denver, Colorado","Formed 2017 via HomeAdvisor &amp; Angie's List merger","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~4,500 employees worldwide","Ticker: ANGI  ·  NASDAQ  ·  IAC subsidiary","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,157,200,"TOP-RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 157%  ·  Top-Rated  ·  RealRate","#1 of 4 US Advertising companies","star")
        snode(1474,104, 430,86,LIME,"gLme","78pp above industry avg (80%)","Highest ECR in US Advertising 2025","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$1.68B"))
        snode(1560,248, 350,86,SKY,"gSky","Total Assets: $1.68B","Stockholders&apos; Equity: $1.46B","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Liabilities: $222.4M","Revenue: $1.03B","chart")
        snode(1560,440, 350,86,SKY,"gSky","Net Income: +$43.8M","Equity-to-Assets ratio: 86.7%","trending")

        # B5 — PLATFORM & BRANDS
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","PLATFORM &amp; BRANDS",
            inner_svg=pie_svg(B5_CX,B5_CY,32,[(50,LIME),(30,CYAN),(20,AMBER)],"3 BRANDS",fsize=6.5))
        snode(1462,620, 440,86,EMER,"gEmr","Angi (formerly Angie&apos;s List)","Homeowner marketplace  ·  Reviews  ·  Cost guides","globe")
        snode(1462,716, 440,86,EMER,"gEmr","HomeAdvisor  ·  Instant Pro Connect","Local professionals  ·  Project cost estimator","people")
        snode(1462,812, 440,86,EMER,"gEmr","Handy  ·  On-demand home services","Cleaning  ·  Assembly  ·  Moving  ·  Repairs","chart")

        # B6 — 2025 HIGHLIGHTS
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","2025 HIGHLIGHTS",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_house(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","Revenue: $1.03B  ·  Net Income: +$43.8M","ECR Strength: Equity +68pp","dollar")
        snode(920,940, 380,86,ORAN,"gOrn","Equity: $1.46B  ·  Assets: $1.68B","Equity-to-Assets ratio: 86.7%","chart")
        snode(1310,940,380,86,ORAN,"gOrn","ECR Weakness: Marketing Expenses –22pp","Industry avg: 80%  ·  78pp above average","trending")

        # B7 — COMPANY HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Company History",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","1995: Angie&apos;s List  ·  Columbus, Ohio","Crowd-sourced reviews for home contractors","clock")
        snode(15,821, 400,86,PURP,"gPrp","1998: ServiceMagic → HomeAdvisor (2012)","2017: ANGI Homeservices via merger","trending")
        snode(15,917, 400,86,PURP,"gPrp","2021: Rebranded to Angi Inc.  ·  NASDAQ","2025: #1 US Advertising  ·  RealRate","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, ORAN,"gOrn","Home Services",
            img=B6_D, clip_id="d1Clip", svg_icon=svg_house(D1_CX,D1_CY,ORAN))
        draw_circle(D2_CX,D2_CY,D2_R, CYAN,"gCyn","Pro Network",
            svg_icon=svg_handshake(D2_CX,D2_CY,CYAN))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"→ 157%"))
        draw_circle(D4_CX,D4_CY,D4_R, SKY,"gSky","$1.03B", fallback=" ")
        t(D4_CX, D4_CY-6,  "$1.03B", 20, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "Revenue", 14, SKY, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "157%", "#1 / 4", "Top-Rated"

    elif COMPANY == "nvidia":

        # B1 — JENSEN HUANG
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Jensen Huang  ·  CEO", img=B1_D, clip_id="b1Clip")
        snode(15,104, 420,86,AMBER,"gAmb","Co-Founder &amp; CEO since 1993  ·  NVDA","Pioneer of GPU computing  ·  CUDA architect","star")
        snode(15,240, 420,86,AMBER,"gAmb","Oregon State BSc EE  ·  Stanford MS EE","30+ years leading Nvidia as CEO","chart")
        snode(15,436, 420,86,AMBER,"gAmb","Led Nvidia from gaming GPUs to AI supercomputing","&quot;The most important chip company in the world&quot;","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="NV")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: April 5, 1993  ·  Santa Clara, CA","Founders: Huang  ·  Priem  ·  Malachowsky","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~36,000 employees worldwide","HQ: Endeavor Campus  ·  Santa Clara, CA","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,351,400,"TOP-RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 351%  ·  Top-Rated  ·  RealRate","#8 of 44 US Semiconductors companies","star")
        snode(1474,104, 430,86,LIME,"gLme","98pp above industry avg (253%)","Top-Rated in US Semiconductors 2025","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$111.6B"))
        snode(1560,248, 350,86,SKY,"gSky","Revenue: $130.5B (FY2025)","Net Income: $72.9B","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Total Assets: $111.6B","Stockholders&apos; Equity: $79.3B","chart")
        snode(1560,440, 350,86,SKY,"gSky","Liabilities: $32.3B","R&amp;D investment: $12.9B","trending")

        # B5 — BUSINESS SEGMENTS
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","BUSINESS SEGMENTS",
            inner_svg=pie_svg(B5_CX,B5_CY,32,[(88.3,LIME),(8.7,CYAN),(3.0,AMBER)],"DC 88%",fsize=6.5))
        snode(1462,620, 440,86,EMER,"gEmr","Data Center: ~$115.2B  ·  88%","AI training  ·  inference  ·  HPC  ·  NVLink","chart")
        snode(1462,716, 440,86,EMER,"gEmr","Gaming: ~$11.4B  ·  9%","GeForce RTX 50 series  ·  DLSS 4  ·  Ray Tracing","dollar")
        snode(1462,812, 440,86,EMER,"gEmr","Pro Viz  ·  Automotive  ·  OEM: ~$3.9B  ·  3%","DRIVE platform  ·  Omniverse  ·  Jetson","globe")

        # B6 — AI LEADERSHIP
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","AI LEADERSHIP",
            svg_icon=svg_neural(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","Blackwell GPU architecture launch 2025","B200  ·  GB200 NVL72  ·  AI superchip era","trending")
        snode(920,940, 380,86,ORAN,"gOrn","Revenue +114% YoY  ·  Net Income +145%","AI demand acceleration  ·  Data Center boom","chart")
        snode(1310,940,380,86,ORAN,"gOrn","CUDA platform  ·  3M+ developers","Software ecosystem moat  ·  AI standard","globe")

        # B7 — COMPANY HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Company History",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","1993: Founded  ·  Santa Clara, CA","Jensen Huang  ·  Priem  ·  Malachowsky","clock")
        snode(15,821, 400,86,PURP,"gPrp","1999: GeForce 256 — world&apos;s first GPU","2006: CUDA — AI computing foundation","trending")
        snode(15,917, 400,86,PURP,"gPrp","2025: ECR 351%  ·  #8 US Semiconductors  ·  RealRate","Revenue +114% YoY  ·  AI supercycle","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, ORAN,"gOrn","AI Chips",
            img=NV_GPU_D, clip_id="d1Clip", svg_icon=svg_chip(D1_CX,D1_CY,ORAN))
        draw_circle(D2_CX,D2_CY,D2_R, CYAN,"gCyn","Data Center",
            img=NV_DC_D, clip_id="d2Clip", svg_icon=svg_wrench(D2_CX,D2_CY,CYAN))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"→ 351%"))
        draw_circle(D4_CX,D4_CY,D4_R, SKY,"gSky","$130.5B", fallback=" ")
        t(D4_CX, D4_CY-6,  "$130.5B", 18, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "Revenue", 14, SKY, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "351%", "#8 / 44", "Top-Rated"

    elif COMPANY == "tesla":

        # B1 — ELON MUSK
        draw_circle(B1_CX,B1_CY,B1_R, TBLUE,"gTBlu","Elon Musk  ·  CEO", img=B1_D, clip_id="b1Clip")
        snode(15,104, 420,86,TBLUE,"gTBlu","Co-Founder &amp; CEO since 2008  ·  TSLA","SpaceX · xAI · Neuralink · The Boring Co","star")
        snode(15,240, 420,86,TBLUE,"gTBlu","BSc Physics &amp; Economics — Univ. Pennsylvania","Founded Zip2 (1995) · X.com → PayPal (1999)","chart")
        snode(15,436, 420,86,TBLUE,"gTBlu","Autonomous AI vision: FSD &amp; Robotaxi 2026","Tesla Bot (Optimus)  ·  AI Supercomputer: Dojo","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="TS")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: July 1, 2003  ·  San Carlos, CA","HQ: Austin, Texas (relocated 2021)  ·  NASDAQ: TSLA","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~125,665 employees worldwide","Gigafactories: Austin · Berlin · Shanghai · Fremont","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, SKY,"gSky","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,135,150,"TOP-RATED",col=SKY))
        snode(1474,  8, 430,86,SKY,"gSky","ECR: 135%  ·  Top-Rated  ·  RealRate","#9 of 38 US Motor companies","star")
        snode(1474,104, 430,86,SKY,"gSky","34pp above industry avg (102%)","9 of 38 US Motor companies Top-Rated","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$137.8B"))
        snode(1560,248, 350,86,SKY,"gSky","Revenue: $94.8B (FY2025)","Net Income: $3.9B  ·  R&amp;D: $6.4B","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Total Assets: $137.8B","Stockholders&apos; Equity: $82.9B","chart")
        snode(1560,440, 350,86,SKY,"gSky","Liabilities: $54.9B","Equity-to-Assets ratio: 60.2%","trending")

        # B5 — BUSINESS SEGMENTS
        draw_circle(B5_CX,B5_CY,B5_R, TAQUA,"gTAqua","BUSINESS SEGMENTS",
            inner_svg=pie_svg(B5_CX,B5_CY,32,[(81,SKY),(13,CYAN),(6,TBLUE)],"3 SEG",fsize=6.5))
        snode(1462,620, 440,86,TAQUA,"gTAqua","Automotive: ~$77.1B  ·  ~81%","Model 3/Y/S/X/Cybertruck  ·  FSD  ·  Robotaxi","trending")
        snode(1462,716, 440,86,TAQUA,"gTAqua","Energy Gen &amp; Storage: ~$11.6B  ·  ~13%","Powerwall  ·  Megapack  ·  Solar Roof","chart")
        snode(1462,812, 440,86,TAQUA,"gTAqua","Services &amp; Other: ~$6.1B  ·  ~6%","Supercharger  ·  Insurance  ·  Tesla Fleet","globe")

        # B6 — 2025 HIGHLIGHTS
        draw_circle(B6_CX,B6_CY,B6_R, TAQUA,"gTAqua","2025 HIGHLIGHTS",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_car(B6_CX,B6_CY,TAQUA))
        snode(530,940, 380,86,TAQUA,"gTAqua","Revenue: $94.8B  ·  Net Income: $3.9B","R&amp;D: $6.4B  ·  SG&amp;A: $5.8B  ·  Tesla IR 2025","dollar")
        snode(920,940, 380,86,TAQUA,"gTAqua","~1.79M vehicles delivered  ·  FY2025","Cybertruck ramp  ·  Model Y Juniper refresh","chart")
        snode(1310,940,380,86,TAQUA,"gTAqua","Optimus production starts  ·  FSD v13","Robotaxi pilot  ·  Austin, TX  ·  Tesla Shareholder","trending")

        # B7 — COMPANY HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Company History",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","2003: Founded  ·  San Carlos, California","Eberhard &amp; Tarpenning · Musk joins 2004","clock")
        snode(15,821, 400,86,PURP,"gPrp","2010: TSLA IPO · NASDAQ  ·  2012: Model S","First US EV company IPO since Ford (1956)","trending")
        snode(15,917, 400,86,PURP,"gPrp","2025: ECR 135%  ·  #9 US Motor  ·  RealRate","Revenue $94.8B  ·  Robotaxi &amp; Optimus era","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, TBLUE,"gTBlu","EV Pioneer",
            svg_icon=svg_car(D1_CX,D1_CY,TBLUE))
        draw_circle(D2_CX,D2_CY,D2_R, TAQUA,"gTAqua","Energy",
            svg_icon=svg_bolt(D2_CX,D2_CY,TAQUA))
        draw_circle(D3_CX,D3_CY,D3_R, SKY,"gSky","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,SKY,"→ 135%"))
        draw_circle(D4_CX,D4_CY,D4_R, CYAN,"gCyn","$94.8B", fallback=" ")
        t(D4_CX, D4_CY-6,  "$94.8B", 20, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "Revenue",  9, CYAN, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "135%", "#9 / 38", "Top-Rated"

    elif COMPANY == "apple":

        # B1 — TIM COOK
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Tim Cook  ·  CEO", img=B1_D, clip_id="b1Clip")
        snode(15,104, 420,86,AMBER,"gAmb","Chief Executive Officer since August 2011","Auburn BSc IE  ·  Duke MBA  ·  Former Apple COO","star")
        snode(15,240, 420,86,AMBER,"gAmb","Led services transformation &amp; Apple Silicon","$700B+ in share buybacks since 2012","chart")
        snode(15,436, 420,86,AMBER,"gAmb","Apple Intelligence  ·  Spatial Computing","Vision Pro  ·  AI integration across ecosystem","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="AP")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: April 1, 1976  ·  Cupertino, CA","Jobs  ·  Wozniak  ·  Wayne  ·  NASDAQ: AAPL","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~150,000 employees worldwide","Apple Park HQ  ·  Cupertino, California","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,430,500,"TOP-RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 430%  ·  Top-Rated  ·  RealRate","#1 of 17 US Computers companies","star")
        snode(1474,104, 430,86,LIME,"gLme","177pp above industry avg (253%)","Highest ECR in US Computers 2025","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$364.9B"))
        snode(1560,248, 350,86,SKY,"gSky","Revenue: $416B (FY2025)  +6% YoY","Net Income: $112B  ·  Op. Margin: 32%","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Total Assets: $364.9B","Cash &amp; Securities: $162B","chart")
        snode(1560,440, 350,86,SKY,"gSky","R&amp;D: $34.6B  ·  Market Cap: $3.0T","Stockholders&apos; Equity: $56.9B","trending")

        # B5 — BUSINESS SEGMENTS
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","BUSINESS SEGMENTS",
            inner_svg=pie_svg(B5_CX,B5_CY,32,[(48,ORAN),(23,LIME),(29,CYAN)],"3 SEG",fsize=6.5))
        snode(1462,620, 440,86,EMER,"gEmr","iPhone: ~$201B  ·  48%","iPhone 16 series  ·  Apple Intelligence  ·  5G","chart")
        snode(1462,716, 440,86,EMER,"gEmr","Services: ~$96B  ·  23%","App Store  ·  iCloud  ·  Apple TV+  ·  Apple Pay","dollar")
        snode(1462,812, 440,86,EMER,"gEmr","Mac  ·  iPad  ·  Wearables: ~$119B  ·  29%","Apple Silicon  ·  Vision Pro  ·  AirPods Pro","globe")

        # B6 — 2025 HIGHLIGHTS
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","2025 HIGHLIGHTS",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_chip(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","Revenue: $416B (+6% YoY)","Net Income: $112B  ·  Market Cap: $3.0T","dollar")
        snode(920,940, 380,86,ORAN,"gOrn","Apple Intelligence &amp; Siri AI overhaul","Vision Pro spatial computing  ·  M4 chip era","trending")
        snode(1310,940,380,86,ORAN,"gOrn","Services record: ~$96B revenue","App Store  ·  iCloud  ·  Subscription platform","chart")

        # B7 — COMPANY HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Company History",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","1976: Founded  ·  Cupertino, California","Jobs  ·  Wozniak  ·  Wayne  ·  Apple I computer","clock")
        snode(15,821, 400,86,PURP,"gPrp","1984: Macintosh  ·  2007: iPhone launched","2011: Tim Cook becomes CEO  ·  Post-Jobs era","trending")
        snode(15,917, 400,86,PURP,"gPrp","2025: ECR 430%  ·  #1 US Computers  ·  RealRate","Revenue $416B  ·  Market Cap $3.0T","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, ORAN,"gOrn","Products",
            img=B6_D, clip_id="d1Clip", svg_icon=svg_chip(D1_CX,D1_CY,ORAN))
        draw_circle(D2_CX,D2_CY,D2_R, CYAN,"gCyn","Ecosystem",
            svg_icon=svg_neural(D2_CX,D2_CY,CYAN))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"→ 430%"))
        draw_circle(D4_CX,D4_CY,D4_R, SKY,"gSky","$3.0T", fallback=" ")
        t(D4_CX, D4_CY-6,  "$3.0T", 22, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "Mkt Cap", 14, SKY, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "430%", "#1 / 17", "Top-Rated"

    elif COMPANY == "harley":

        # B1 — JOCHEN ZEITZ / CEO
        draw_circle(B1_CX,B1_CY,B1_R, AMBER,"gAmb","Jochen Zeitz  ·  CEO",
            img=B1_D, clip_id="b1Clip", svg_icon=svg_motorcycle(B1_CX,B1_CY,AMBER))
        snode(15,104, 420,86,AMBER,"gAmb","President &amp; CEO since February 2020","Architect of Hardwire 5-year strategy 2021–2025","star")
        snode(15,240, 420,86,AMBER,"gAmb","Former CEO of Puma AG  ·  Sustainability champion","Led HD&apos;s pivot to premium focus &amp; profitability","chart")
        snode(15,436, 420,86,AMBER,"gAmb","LiveWire EV spin-off 2022  ·  NYSE: LVWR","Selective market expansion  ·  Global brand depth","trending")

        # B2 — COMPANY OVERVIEW
        draw_circle(B2_CX,B2_CY,B2_R, CYAN,"gCyn","COMPANY OVERVIEW",
            img=B2_D, clip_id="b2Clip", fallback="HD")
        snode(460,14, 410,86,CYAN,"gCyn","Founded: 1903  ·  Milwaukee, Wisconsin","NYSE: HOG  ·  One of the world&apos;s oldest motorcycle brands","clock")
        snode(1010,14, 430,86,CYAN,"gCyn","~5,900 employees worldwide","HQ: 3700 W Juneau Ave  ·  Milwaukee, WI 53208","building")

        # B3 — INDUSTRY POSITION
        draw_circle(B3_CX,B3_CY,B3_R, LIME,"gLme","INDUSTRY POSITION",
            inner_svg=ecr_gauge(B3_CX,B3_CY,147,200,"TOP-RATED"))
        snode(1474,  8, 430,86,LIME,"gLme","ECR: 147%  ·  Top-Rated  ·  RealRate","#5 of 38 US Motor companies","star")
        snode(1474,104, 430,86,LIME,"gLme","45pp above industry avg (102%)","Top-Rated in US Motor 2026","chart")

        # B4 — FINANCIAL HEALTH
        draw_circle(B4_CX,B4_CY,B4_R, SKY,"gSky","FINANCIAL HEALTH",
            inner_svg=balance_sheet_svg(B4_CX,B4_CY,"$12.1B"))
        snode(1560,248, 350,86,SKY,"gSky","Revenue: $5.84B  ·  Net Income: $695M","Total Assets: $12.1B","dollar")
        snode(1560,344, 350,86,SKY,"gSky","Stockholders&apos; Equity: $3.25B","Liabilities: ~$8.85B","chart")
        snode(1560,440, 350,86,SKY,"gSky","ECR Strength: Stockholders&apos; Equity +30pp","ECR Weakness: Current Liabilities –18pp","trending")

        # B5 — ECR ANALYSIS
        draw_circle(B5_CX,B5_CY,B5_R, EMER,"gEmr","ECR ANALYSIS",
            inner_svg=ecr_drivers_svg(B5_CX,B5_CY,"+30pp","–18pp","147%","TOP-RATED"))
        snode(1462,620, 440,86,EMER,"gEmr","Greatest Strength: Stockholders&apos; Equity","+30pp contribution to ECR","chart")
        snode(1462,716, 440,86,EMER,"gEmr","Greatest Weakness: Liabilities, Current","–18pp drag on ECR","trending")
        snode(1462,812, 440,86,EMER,"gEmr","ECR: 147%  ·  45pp above industry avg","Market average: 102%  ·  #5 of 38 US Motor","star")

        # B6 — HARDWIRE STRATEGY / HIGHLIGHTS
        draw_circle(B6_CX,B6_CY,B6_R, ORAN,"gOrn","HARDWIRE STRATEGY",
            img=B6_D, clip_id="b6Clip", svg_icon=svg_motorcycle(B6_CX,B6_CY,ORAN))
        snode(530,940, 380,86,ORAN,"gOrn","Revenue: $5.84B  ·  Net Income: $695M","Premium motorcycle focus  ·  Selective market expansion","dollar")
        snode(920,940, 380,86,ORAN,"gOrn","HD Financial Services (HDFS)","Retail loans  ·  Wholesale financing  ·  Insurance","chart")
        snode(1310,940,380,86,ORAN,"gOrn","LiveWire (NYSE: LVWR)  ·  EV expansion","S2 Del Mar  ·  S2 Mulholland  ·  Electric future","trending")

        # B7 — COMPANY HISTORY
        draw_circle(B7_CX,B7_CY,B7_R, PURP,"gMH","Company History",
            svg_icon=svg_growth(B7_CX,B7_CY,PURP))
        snode(15,725, 400,86,PURP,"gPrp","1903: Founded  ·  Milwaukee, Wisconsin","William Harley &amp; Arthur Davidson  ·  Backyard workshop","clock")
        snode(15,821, 400,86,PURP,"gPrp","1969: AMF acquisition  ·  1981: Management buyout","120+ years of American motorcycle heritage","trending")
        snode(15,917, 400,86,PURP,"gPrp","2026: ECR 147%  ·  #5 US Motor  ·  RealRate","Hardwire strategy  ·  Premium focus  ·  EV expansion","star")

        # DECORATIVE
        draw_circle(D1_CX,D1_CY,D1_R, ORAN,"gOrn","Heritage",
            img=B6_D, clip_id="d1Clip", svg_icon=svg_motorcycle(D1_CX,D1_CY,ORAN))
        draw_circle(D2_CX,D2_CY,D2_R, CYAN,"gCyn","HDFS",
            svg_icon=svg_handshake(D2_CX,D2_CY,CYAN))
        draw_circle(D3_CX,D3_CY,D3_R, LIME,"gLme","ECR Trend",
            svg_icon=svg_trend(D3_CX,D3_CY,LIME,"→ 147%"))
        draw_circle(D4_CX,D4_CY,D4_R, SKY,"gSky","$5.84B", fallback=" ")
        t(D4_CX, D4_CY-6,  "$5.84B", 20, WH,  "middle", "800")
        t(D4_CX, D4_CY+12, "Revenue", 14, SKY, "middle", "700")

        ECR_VAL, RANK_VAL, STATUS_VAL = "147%", "#5 / 38", "Top-Rated"

    # ══════════════════════════════════════════════════════════════════════════
    # CENTER HUB
    # ══════════════════════════════════════════════════════════════════════════
    HR = 200

    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR+28}" fill="none" stroke="{ACCENT}" stroke-width="22" stroke-opacity=".06" filter="url(#halo)"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR+46}" fill="none" stroke="{ACCENT}" stroke-width="1" stroke-opacity=".12"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR+62}" fill="none" stroke="{ACCENT}" stroke-width=".6" stroke-opacity=".07"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR+10}" fill="none" stroke="url(#branchGrad)" stroke-width="26" stroke-opacity=".28" filter="url(#borderGlow)"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR+2}" fill="none" stroke="url(#branchGrad)" stroke-width="9" stroke-opacity=".68" filter="url(#borderGlow)"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR}" fill="url(#gHub)"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR}" fill="url(#gHubGlow)"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR-5}" fill="none" stroke="url(#branchGrad)" stroke-width="20" stroke-opacity=".38" clip-path="url(#hubClip)" filter="url(#innerGlow)"/>')
    a(f'<circle cx="{HCX}" cy="{HCY}" r="{HR}" fill="none" stroke="url(#branchGrad)" stroke-width="2.2" stroke-opacity=".92"/>')

    for ang_deg in [0, 90, 180, 270]:
        a1 = math.radians(ang_deg - 18); a2 = math.radians(ang_deg + 18)
        ri = HR - 8
        a(f'<path d="M{HCX+ri*math.cos(a1):.1f},{HCY+ri*math.sin(a1):.1f} A{ri},{ri} 0 0,1 {HCX+ri*math.cos(a2):.1f},{HCY+ri*math.sin(a2):.1f}" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" opacity=".88"/>')

    for i in range(8):
        ang = math.radians(i * 45)
        a(f'<line x1="{HCX+HR*math.cos(ang):.1f}" y1="{HCY+HR*math.sin(ang):.1f}" x2="{HCX+(HR-7)*math.cos(ang):.1f}" y2="{HCY+(HR-7)*math.sin(ang):.1f}" stroke="{ACCENT}" stroke-width="1.2" opacity=".5"/>')

    # ── Hub Row 1: RealRate logo (centered, top) ─────────────────────────────
    rl_w, rl_h = 220, 52
    rl_x, rl_y = HCX - rl_w // 2, HY + 10
    white_box(rl_x, rl_y, rl_w, rl_h)
    if RL_D:
        a(f'<image href="data:image/png;base64,{RL_D}" x="{rl_x+3}" y="{rl_y+3}" width="{rl_w-6}" height="{rl_h-6}" preserveAspectRatio="xMidYMid meet"/>')

    a(f'<line x1="{HCX-155}" y1="{HY+68}" x2="{HCX+155}" y2="{HY+68}" stroke="{ACCENT}" stroke-width=".5" stroke-opacity=".22"/>')

    # ── Hub Row 2: Company logo (centered, 72×72) stacked above company name ──
    lg_bw, lg_bh = 72, 72
    lg_bx = HCX - lg_bw // 2   # centered
    lg_by = HY + 76             # top of logo box

    if COMPANY == "trilinc":
        white_box(lg_bx, lg_by, lg_bw, lg_bh, op=.3)
        a(f'<svg x="{lg_bx+4}" y="{lg_by+4}" width="64" height="64" viewBox="0 0 40 40">'
          f'<path d="M20,4 C32,4 36,16 36,24 C36,32 28,38 20,38 C12,38 4,32 4,24 C4,16 8,4 20,4Z" fill="none" stroke="{ACCENT}" stroke-width="2" opacity=".9"/>'
          f'<line x1="20" y1="4" x2="20" y2="38" stroke="{ACCENT}" stroke-width="1.5" opacity=".7"/>'
          f'<line x1="20" y1="20" x2="32" y2="14" stroke="{ACCENT}" stroke-width="1" opacity=".55"/>'
          f'<line x1="20" y1="26" x2="31" y2="22" stroke="{ACCENT}" stroke-width="1" opacity=".55"/>'
          f'</svg>')
        t(HCX, HY+170, "TriLinc Global", 36, WH, "middle", "800")
        t(HCX, HY+170, "Impact Investing  ·  SME Lending  ·  Developing Economies", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "TRLC  ·  Est. 2008  ·  Delaware, USA", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "strata":
        if not hub_logo_png(lg_bx, lg_by, LOGO_D):
            a(f'<svg x="{lg_bx+4}" y="{lg_by+4}" width="64" height="64" viewBox="0 0 40 40">'
              f'<ellipse cx="18" cy="22" rx="12" ry="7" fill="none" stroke="{ACCENT}" stroke-width="2"/>'
              f'<line x1="4" y1="14" x2="34" y2="14" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round"/>'
              f'<path d="M30,22 L38,17" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round"/>'
              f'<line x1="36" y1="15" x2="36" y2="20" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round"/>'
              f'<line x1="10" y1="29" x2="26" y2="29" stroke="{ACCENT}" stroke-width="1.5" stroke-linecap="round"/>'
              f'<line x1="13" y1="26" x2="13" y2="29" stroke="{ACCENT}" stroke-width="1.5"/>'
              f'<line x1="23" y1="26" x2="23" y2="29" stroke="{ACCENT}" stroke-width="1.5"/>'
              f'<line x1="15" y1="20" x2="21" y2="20" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round"/>'
              f'<line x1="18" y1="17" x2="18" y2="23" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round"/>'
              f'</svg>')
        t(HCX, HY+164, "Strata Critical", 28, WH, "middle", "800")
        t(HCX, HY+192, "Medical",          28, WH, "middle", "800")
        t(HCX, HY+170, "Air Medical Transport  ·  Critical Care  ·  Emergency Response", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "CIK: 0001779128  ·  OTC-listed  ·  Delaware, USA", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "hp":
        if not hub_logo_png(lg_bx, lg_by, LOGO_D):
            a(f'<svg x="{lg_bx+4}" y="{lg_by+4}" width="64" height="64" viewBox="0 0 40 40">'
              f'<rect x="4" y="6" width="32" height="21" rx="2" fill="none" stroke="{ACCENT}" stroke-width="2" opacity=".9"/>'
              f'<rect x="8" y="10" width="24" height="14" rx="1" fill="{ACCENT}" opacity=".12"/>'
              f'<line x1="0" y1="29" x2="40" y2="29" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" opacity=".9"/>'
              f'<rect x="15" y="27" width="10" height="2" rx="1" fill="{ACCENT}" opacity=".6"/>'
              f'</svg>')
        t(HCX, HY+170, "HP Inc.", 46, WH, "middle", "800")
        t(HCX, HY+170, "Personal Systems  ·  Printing  ·  Technology", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "Est. 1939  ·  HPQ  ·  Palo Alto, California", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "angi":
        t(HCX, HY+130, "Angi Inc.", 52, WH, "middle", "800")
        t(HCX, HY+170, "Home Services  ·  Marketplace  ·  Reviews", 18, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "ANGI  ·  NASDAQ  ·  Est. 1995  ·  Denver, CO", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "nvidia":
        hub_logo_png(lg_bx, lg_by, LOGO_D)
        t(HCX, HY+170, "Nvidia Corp.", 38, WH, "middle", "800")
        t(HCX, HY+170, "AI Computing  ·  GPU Architecture  ·  Data Center", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "NVDA  ·  Est. 1993  ·  Santa Clara, California", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "apple":
        if not hub_logo_png(lg_bx, lg_by, LOGO_D):
            a(f'<svg x="{lg_bx+4}" y="{lg_by+4}" width="64" height="64" viewBox="0 0 40 40">'
              f'<path d="M20,7 C23,7 26,9 27,12 C30,10 34,11 34,16 C34,24 28,33 23,35 C21.5,35.5 18.5,35.5 17,35 C12,33 6,24 6,16 C6,11 10,10 13,12 C14,9 17,7 20,7Z" fill="none" stroke="{ACCENT}" stroke-width="2" opacity=".9"/>'
              f'<path d="M20,5 C22,5 22.5,7 22,7" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linecap="round" opacity=".75"/>'
              f'</svg>')
        t(HCX, HY+170, "Apple Inc.", 46, WH, "middle", "800")
        t(HCX, HY+170, "iPhone  ·  Mac  ·  Services  ·  Apple Intelligence", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "AAPL  ·  Est. 1976  ·  Cupertino, California", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "tesla":
        # Logo LEFT, name RIGHT in the same row
        tl_cy  = HY + 112            # row vertical center
        tl_bx  = HCX - 150          # logo box left edge (x=790)
        tl_by  = tl_cy - lg_bw // 2 # logo box top
        white_box(tl_bx, tl_by, lg_bw, lg_bh, op=.3)
        if LOGO_SVG_D:
            _svg = base64.b64decode(LOGO_SVG_D).decode('utf-8')
            _svg = _svg.replace('viewBox="0 0 278.67201 360.43799"', 'viewBox="0 15 278.67201 237"')
            _svg_enc = base64.b64encode(_svg.encode('utf-8')).decode()
            a(f'<image href="data:image/svg+xml;base64,{_svg_enc}" x="{tl_bx+8}" y="{tl_by+8}" width="56" height="48" preserveAspectRatio="xMidYMid meet"/>')
        elif LOGO_D:
            a(f'<image href="data:{raster_mime(LOGO_D)};base64,{LOGO_D}" x="{tl_bx+4}" y="{tl_by+4}" width="64" height="64" preserveAspectRatio="xMidYMid meet"/>')
        _nx = (tl_bx + lg_bw + 12 + HCX + 155) // 2   # center of right zone ≈ 984
        t(_nx, tl_cy + 14, "Tesla Inc.", 40, WH, "middle", "800")
        t(HCX, HY+170, "Electric Vehicles  ·  Energy Storage  ·  AI Robotics", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "TSLA  ·  NASDAQ  ·  Est. 2003  ·  Austin, Texas", 18, GREY, "middle", "500", sp=".3")

    elif COMPANY == "harley":
        if not hub_logo_png(lg_bx, lg_by, LOGO_D):
            a(f'<svg x="{lg_bx+4}" y="{lg_by+4}" width="64" height="64" viewBox="0 0 40 40">'
              f'<path d="M20,4 L34,12 L34,28 L20,36 L6,28 L6,12 Z" fill="none" stroke="{ACCENT}" stroke-width="2" opacity=".9"/>'
              f'<text x="20" y="26" font-family="Arial" font-size="9" font-weight="800" fill="{ACCENT}" text-anchor="middle" opacity=".9">H-D</text>'
              f'</svg>')
        t(HCX, HY+170, "Harley Davidson INC", 34, WH, "middle", "800")
        t(HCX, HY+170, "Motorcycles  ·  Financial Services  ·  LiveWire EV", 17, GREY, "middle", "500", op=.88, sp=".4")
        t(HCX, HY+184, "HOG  ·  NYSE  ·  Est. 1903  ·  Milwaukee, Wisconsin", 18, GREY, "middle", "500", sp=".3")

    a(f'<line x1="{HCX-155}" y1="{HY+156}" x2="{HCX+155}" y2="{HY+156}" stroke="{ACCENT}" stroke-width=".5" stroke-opacity=".22"/>')
    a(f'<line x1="{HCX-155}" y1="{HY+192}" x2="{HCX+155}" y2="{HY+192}" stroke="{ACCENT}" stroke-width=".5" stroke-opacity=".22"/>')

    def badge(bx,by,bw,bh,c,label,val,fsz=24):
        a(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="{c}" fill-opacity=".09" stroke="{c}" stroke-width=".8" stroke-opacity=".4"/>')
        t(bx+bw//2, by+16, label, 16, c, "middle", wt="700", sp="1.1")
        t(bx+bw//2, by+40, val,  fsz,  WH, "middle", "800")

    # Badges centred at HCX; span 336px → fits inside circle at this y (r=200, d≈104)
    by_,bh_ = HY+200, 50
    badge(HCX-168, by_, 100, bh_, CYAN,  "ECR SCORE",    ECR_VAL,    28)
    badge(HCX-60,  by_, 120, bh_, AMBER, "INDUSTRY RANK",RANK_VAL,   24)
    badge(HCX+68,  by_, 100, bh_, LIME,  "STATUS",       STATUS_VAL, 18)

    a(f'<line x1="80" y1="1054" x2="{W-80}" y2="1054" stroke="{ACCENT}" stroke-width=".4" stroke-opacity=".13"/>')
    t(W//2,1070,"Powered by RealRate: Using Explainable Financial AI  ·  realrate.ai  ·  ECR Data from RealRate",
      20,"#A8D8FF","middle",op=.9,sp=".6")

    a('</svg>'); return '\n'.join(p)

html = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">'
        f'<style>*{{margin:0;padding:0;overflow:hidden;background:{BG}}}</style>'
        f'</head><body>{build()}</body></html>')

# ── Output paths ───────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
_subdirs = {
    "trilinc": None,
    "strata":  "Strata Critical Medical",
    "hp":      "HP Inc",
    "angi":    "Angi Inc",
    "nvidia":  "Nvidia Corp",
    "tesla":   "Tesla Inc",
    "apple":   "Apple Inc",
    "harley":  "Harley Davidson INC",
}
_subdir = _subdirs[COMPANY]
OUT_DIR = HERE / _subdir if _subdir else HERE
if _subdir:
    OUT_DIR.mkdir(exist_ok=True)
OUT       = str(OUT_DIR / f"{COMPANY}-mindmap.png")
POST_PATH = str(OUT_DIR / f"{COMPANY}-linkedin-post.txt")

# ── Render ─────────────────────────────────────────────────────────────────────
print("Rendering…")
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
    pg.set_content(html, timeout=60000)
    try:
        pg.wait_for_load_state("networkidle", timeout=45000)
    except Exception:
        pass
    pg.wait_for_timeout(2500)
    HI_OUT = OUT.replace(".png", "_2x.png")
    pg.screenshot(path=HI_OUT, clip={"x": 0, "y": 0, "width": W, "height": H})
    br.close()

img_out = _PIL.open(HI_OUT).resize((W, H), _PIL.LANCZOS)
img_out.save(OUT, "PNG", optimize=True)
os.remove(HI_OUT)
print(f"Done (1920×1080): {OUT}")

# ── LinkedIn post ──────────────────────────────────────────────────────────────
if COMPANY == "trilinc":
    CAPTION = f"""\
TriLinc Global Impact Fund ranks #1 in US Finance Services. ECR: 124%.

46 percentage points above the industry average of 78%. Top-Rated by RealRate's independent, explainable financial AI.

THE FUND
Founded 2008 · Delaware, USA · Ticker: TRLC · ~$1.4B AUM
Female-founded · Female-owned · Female-led

LEADERSHIP
Gloria Nelund — Founder, Chief Executive Officer & Chief Compliance Officer
Former CEO, US Private Wealth at Deutsche Bank — oversaw $50 billion in assets under management
Over 40 years of experience in international asset management

FINANCIAL HEALTH
Total Assets: $282.8M · Stockholders' Equity: $272.6M · Liabilities: $10.2M
Equity-to-Assets Ratio: 96.4% · Net Income: –$8.5M
Primary ECR Drivers: Equity +57pp · Revenue –17pp

INVESTMENT STRATEGY
Direct loans · Trade finance · Structured credit · Preferred equity
SMEs with fewer than 500 employees · Developing economies · Local sub-advisors · 4 continents

IMPACT
Sustainable community development · Workforce capacity building · Financial inclusion · Food security
Sectors: Education · Energy · Housing · Health

2008: Founded | 2017: TRLC listed on OTC Pink Markets | 2025: Ranked #1 in US Finance Services

Powered by RealRate: Using Explainable Financial AI

Full US Finance Services ranking: {RANKING_URL}

#RealRate #ImpactInvesting #ESG #SMELending #FinancialHealth"""

elif COMPANY == "hp":
    CAPTION = f"""\
HP Inc. ranks #9 in US Computers. ECR: 258%.

At the industry average of 258%. Rated by RealRate's independent, explainable financial AI.

THE COMPANY
Personal computing and printing technology leader · Palo Alto, California
Founded 1939 · Spun off from Hewlett-Packard November 2015 · Ticker: HPQ
~58,000 employees worldwide

LEADERSHIP
Enrique Lores — President & Chief Executive Officer
Joined HP in 1989 · Led Imaging, Printing & Solutions before becoming CEO November 2019
"Future Ready" transformation — restructuring for AI-era growth and subscription revenue

FINANCIAL HEALTH
Revenue: $53.6B (FY2024) · Net Income: $2.8B · Operating margin: 7.1%
Total Assets: $39.9B · Stockholders' Equity: –$1.3B (deficit from cumulative buybacks)
Cash: $3.25B · Long-term Debt: $8.3B · R&D: $1.64B

BUSINESS SEGMENTS
Personal Systems: ~$34.4B (64%) — PCs, laptops, workstations, Chromebooks
Printing: ~$19.1B (36%) — LaserJet, OfficeJet, Instant Ink supplies
Poly collaboration hardware — acquired 2022 · hybrid work solutions

HISTORY
1939: William Hewlett & Dave Packard found the company in a Palo Alto garage
2015: Hewlett-Packard splits into HP Inc. (HPQ) and Hewlett Packard Enterprise (HPE)
FY2024: $53.6B revenue · ECR 258% · AI PC transformation underway

Powered by RealRate: Using Explainable Financial AI

Full US Computers ranking: {RANKING_URL}

#RealRate #HPInc #AIComputer #FinancialHealth #TechIndustry"""

elif COMPANY == "strata":
    CAPTION = f"""\
Strata Critical Medical ranks #1 in US Air. ECR: 123%.

54 percentage points above the industry average of 69%. Top-Rated by RealRate's independent, explainable financial AI.

THE COMPANY
Air Medical Transport · Critical Care · Emergency Response · Delaware, USA
CIK: 0001779128 · OTC-listed · STCM · Publicly reporting

FINANCIAL HEALTH
Total Assets: $325.5M · Stockholders' Equity: $279.1M · Liabilities: $46.4M
Revenue: $197.1M (FY2025) · Net Income: +$41.3M
First profitable year in company history

ECR DRIVERS
Greatest Strength: Operating Expenses — +46pp contribution to ECR
Greatest Weakness: Other Expenses — –81pp drag on ECR

GROWTH JOURNEY
2021: Revenue $50.5M · Net Income –$40.1M — Rapid expansion phase begins
2022–2024: Revenue grew from $146M to $249M — approximately 4× growth in 3 years
2025: ECR 123% · #1 US Air · RealRate — First profitable year in history

Powered by RealRate: Using Explainable Financial AI

Full US Air ranking: {RANKING_URL}

#RealRate #AirMedical #CriticalCare #FinancialHealth #Healthcare"""

elif COMPANY == "nvidia":
    CAPTION = f"""\
Nvidia Corp. ranks #8 in US Semiconductors. ECR: 351%.

98 percentage points above the industry average of 253%. Top-Rated by RealRate's independent, explainable financial AI.

THE COMPANY
AI computing and GPU technology leader · Santa Clara, California
Founded April 5, 1993 · NASDAQ: NVDA · ~36,000 employees worldwide

LEADERSHIP
Jensen Huang — Co-Founder & Chief Executive Officer
Oregon State BSc Electrical Engineering · Stanford MS Electrical Engineering
Led Nvidia from gaming graphics chipmaker to the world's AI computing infrastructure provider

FINANCIAL HEALTH
Revenue: $130.5B (FY2025) · Net Income: $72.9B
Total Assets: $111.6B · Stockholders' Equity: $79.3B · Liabilities: $32.3B
R&D investment: $12.9B

ECR DRIVERS
Greatest Strength: Net Income — +94pp contribution to ECR
Greatest Weakness: Stockholders' Equity — –56pp drag on ECR

BUSINESS SEGMENTS
Data Center: ~$115.2B (88%) — H100, H200, Blackwell B200, GB200 NVL72, NVLink, InfiniBand
Gaming: ~$11.4B (9%) — GeForce RTX 50 series · DLSS 4 · Ray Tracing
Professional Visualization · Automotive · OEM: ~$3.9B (3%) — DRIVE platform · Omniverse · Jetson

HISTORY
1993: Jensen Huang, Curtis Priem & Chris Malachowsky found Nvidia in Santa Clara
1999: GeForce 256 — world's first GPU | 2006: CUDA platform — AI computing foundation
2025: ECR 351% · #8 US Semiconductors · Revenue +114% YoY · RealRate

Powered by RealRate: Using Explainable Financial AI

Full US Semiconductors ranking: {RANKING_URL}

#RealRate #Nvidia #AIComputing #GPUs #FinancialHealth"""

elif COMPANY == "tesla":
    CAPTION = f"""\
Tesla Inc ranks #9 in US Motor. ECR: 135%.

34 percentage points above the industry average of 102%. Top-Rated by RealRate's independent, explainable financial AI.

THE COMPANY
Electric vehicles, energy storage, and AI company · Austin, Texas
Founded July 1, 2003 · NASDAQ: TSLA
~125,665 employees worldwide

LEADERSHIP
Elon Musk — Co-Founder & Chief Executive Officer (since 2008)
Also CEO of SpaceX, xAI, Neuralink & The Boring Company
Driving Tesla's transition from EV maker to full-stack AI and robotics company

FINANCIAL HEALTH
Revenue: $94.8B (FY2025) · Net Income: $3.9B · R&D: $6.4B
Total Assets: $137.8B · Stockholders' Equity: $82.9B · Liabilities: $54.9B
Equity-to-Assets Ratio: 60.2%

ECR DRIVERS
Greatest Strength: Cost of Goods and Services Sold — +36pp contribution to ECR
Greatest Weakness: Other Expenses — –27pp drag on ECR

BUSINESS SEGMENTS
Automotive: ~81% — Model 3/Y/S/X/Cybertruck · Full Self-Driving · Robotaxi
Energy Generation & Storage: ~13% — Powerwall · Megapack · Solar Roof
Services & Other: ~6% — Supercharger network · Insurance · Tesla Fleet

HISTORY
2003: Tesla Motors founded by Martin Eberhard & Marc Tarpenning · San Carlos, California
2008: Elon Musk becomes CEO · First Roadster delivered | 2010: TSLA IPO on NASDAQ
2025: ECR 135% · #9 US Motor · Top-Rated · Revenue $94.8B · Robotaxi & Optimus era

Powered by RealRate: Using Explainable Financial AI

Full US Motor ranking: {RANKING_URL}

#RealRate #Tesla #ElectricVehicles #FinancialHealth #EV"""

elif COMPANY == "angi":
    CAPTION = f"""\
Angi Inc. ranks #1 in US Advertising. ECR: 157%.

78 percentage points above the industry average of 80%. Top-Rated by RealRate's independent, explainable financial AI.

THE COMPANY
Online home services marketplace · Denver, Colorado
Founded 1995 · NASDAQ: ANGI · IAC subsidiary
~4,500 employees worldwide

LEADERSHIP
Jeff Kip — Chief Executive Officer
Brands: Angi (formerly Angie's List) · HomeAdvisor · Handy
Connecting homeowners with local service professionals across the United States

FINANCIAL HEALTH
Total Assets: $1.68B · Stockholders' Equity: $1.46B · Liabilities: $222.4M
Revenue: $1.03B · Net Income: +$43.8M
Equity-to-Assets Ratio: 86.7%

ECR DRIVERS
Greatest Strength: Stockholders' Equity — +68pp contribution to ECR
Greatest Weakness: Marketing & Selling Expenses — –22pp drag on ECR

PLATFORM
Angi: Homeowner marketplace · Crowd-sourced reviews · Cost guides
HomeAdvisor: Instant Pro Connect · Local professionals · Project matching
Handy: On-demand home services · Cleaning · Assembly · Moving · Repairs

HISTORY
1995: Angie's List founded in Columbus, Ohio — review platform for home service contractors
1998: ServiceMagic founded, rebranded HomeAdvisor in 2012
2017: ANGI Homeservices formed via HomeAdvisor & Angie's List merger | 2021: Rebranded to Angi Inc.
2025: ECR 157% · #1 US Advertising · RealRate

Powered by RealRate: Using Explainable Financial AI

Full US Advertising ranking: {RANKING_URL}

#RealRate #HomeServices #AngiInc #FinancialHealth #Marketplace"""

elif COMPANY == "harley":
    CAPTION = f"""\
Harley Davidson INC ranks #5 in US Motor. ECR: 147%.

45 percentage points above the industry average of 102%. Top-Rated by RealRate's independent, explainable financial AI.

THE COMPANY
Iconic American motorcycle brand · Milwaukee, Wisconsin
Founded 1903 · NYSE: HOG · ~5,900 employees worldwide
Brands: Harley-Davidson · LiveWire · Harley-Davidson Financial Services (HDFS)

LEADERSHIP
Jochen Zeitz — President & Chief Executive Officer
Former CEO of Puma AG · Architect of the "Hardwire" 2021–2025 strategic plan
Focus on premium motorcycles, selective market expansion, and EV platform development

FINANCIAL HEALTH
Revenue: $5.84B · Net Income: $695M
Total Assets: $12.1B · Stockholders' Equity: $3.25B · Liabilities: ~$8.85B

ECR DRIVERS
Greatest Strength: Stockholders' Equity — +30pp contribution to ECR
Greatest Weakness: Liabilities, Current — –18pp drag on ECR

BUSINESS
Motorcycles & Related Products: Touring, Softail, Sportster, Adventure, Electric
Financial Services (HDFS): Retail loans, wholesale financing, insurance, licensing
LiveWire (NYSE: LVWR): Dedicated EV motorcycle brand, spun off 2022

HISTORY
1903: William Harley & Arthur Davidson build first motorcycle in Milwaukee backyard
1969: AMF acquisition | 1981: Management buyout — independence restored
2021: Hardwire strategy launched | 2022: LiveWire EV brand spun off
2026: ECR 147% · #5 US Motor · Top-Rated · RealRate

Powered by RealRate: Using Explainable Financial AI

Full US Motor ranking: {RANKING_URL}

#RealRate #HarleyDavidson #Motorcycles #FinancialHealth #EV"""

elif COMPANY == "apple":
    CAPTION = f"""\
Apple Inc. ranks #1 in US Computers. ECR: 430%.

177 percentage points above the industry average of 253%. Top-Rated by RealRate's independent, explainable financial AI.

THE COMPANY
World's most valuable technology company · Cupertino, California
Founded April 1, 1976 · NASDAQ: AAPL · ~150,000 employees worldwide

LEADERSHIP
Tim Cook — Chief Executive Officer
CEO since August 2011 · Auburn University BSc Industrial Engineering · Duke MBA
Led Apple's transformation from hardware maker to services, AI, and spatial computing company

FINANCIAL HEALTH
Revenue: $416B (FY2025) · +6% YoY · Net Income: $112B · Operating Margin: 32%
Total Assets: $364.9B · Stockholders' Equity: $56.9B
Cash & Securities: $162B · R&D investment: $34.6B · Market Cap: $3.0 Trillion

BUSINESS SEGMENTS
iPhone: ~$201B (48%) — iPhone 16 series · Apple Intelligence · 5G
Services: ~$96B (23%) — App Store · iCloud · Apple TV+ · Apple Pay · Apple Arcade
Mac · iPad · Wearables: ~$119B (29%) — Apple Silicon M4 · Vision Pro · AirPods Pro

HISTORY
1976: Steve Jobs, Steve Wozniak & Ronald Wayne found Apple · Cupertino, California
1984: Macintosh launched | 2007: iPhone changes mobile computing | 2011: Tim Cook becomes CEO
2025: ECR 430% · #1 US Computers · Revenue $416B · Market Cap $3.0 Trillion · RealRate

Powered by RealRate: Using Explainable Financial AI

Full US Computers ranking: {RANKING_URL}

#RealRate #Apple #iPhone #FinancialHealth #TechIndustry"""

with open(POST_PATH, "w", encoding="utf-8") as _f:
    _f.write(CAPTION + "\n")
print("LinkedIn post saved:", POST_PATH)
