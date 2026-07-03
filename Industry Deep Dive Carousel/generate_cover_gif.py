#!/usr/bin/env python3
"""
Template — Industry Deep Dive Carousel cover GIF (Top 5 revealing animation).
SCALE = 2  ->  1080x924 px  (LinkedIn native portrait quality)

Shared script for the deep-dive-carousel skill (Step 10). Lives at
Industry Deep Dive Carousel/generate_cover_gif.py — for each new industry,
edit the constants marked "EDIT" below in place, then run it. OUT_PATH
writes into that industry's own subfolder, so nothing here needs moving.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Resolution ────────────────────────────────────────────────────────────
SCALE = 2          # 1 = 540x675 preview | 2 = 1080x1350 LinkedIn quality
W     = 540 * SCALE

def s(v):
    """Scale a pixel / font-size value."""
    return int(v * SCALE)

# Derive canvas height from content — no dead space at bottom
# stats bar: C_Y(258) + C_H(110) + gap(16) + bar_h(62) = 446
# footer text y: 446 + 14 = 460, font height ~12, padding below 28
H = s(220 + 110 + 16 + 62 + 14 + 12 + 28)   # = s(462) = 924 px at SCALE 2

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))  # Industry Deep Dive Carousel/
# EDIT: point at the industry's own subfolder and output filename
OUT_PATH  = os.path.join(BASE_DIR, "[Industry Name]", "[industry-slug]-[year]-cover.gif")
LOGO_PATH = os.path.join(BASE_DIR, "..", "RealRate Logos", "RealRate_logo_horizontal.png")

# ── Palette ─────────────────────────────────────────────────────────────── EDIT
# Default RealRate blue palette — replace with the industry's chosen palette (Step 4 of the skill)
NAVY     = (0, 24, 41)       # cover bg dark #001829
GOLD     = (201, 168, 76)    # accent #C9A84C
GOLD_L   = (219, 191, 110)   # accent light
BLUE_L   = (61, 186, 205)    # blue light #3DBACD
BLUE_D   = (0, 103, 155)     # blue dark #00679B
GREEN_L  = (134, 204, 130)   # #86CC82 (ECR score colour — keep green across all palettes)
WHITE    = (255, 255, 255)
SILVER   = (208, 208, 208)
BRONZE   = (212, 149, 106)

def blend(c, a, bg=NAVY):
    """Pre-multiply alpha blend onto bg (a: 0-255)."""
    t = a / 255.0
    return tuple(int(ci * t + bi * (1 - t)) for ci, bi in zip(c, bg))

# ── Company data ─────────────────────────────────────────────────────────── EDIT
# Replace with the industry's actual Top 5 (name, ECR, Top-Rated status) from the live rankings page
TOP5 = [
    {"rank": 1, "lines": ["Company One"],   "ecr": "0%", "top_rated": True,
     "rank_c": GOLD_L,  "border_c": GOLD,    "b_a": 140, "bg_a": 25},
    {"rank": 2, "lines": ["Company Two"],   "ecr": "0%", "top_rated": True,
     "rank_c": SILVER,  "border_c": SILVER,  "b_a": 115, "bg_a": 17},
    {"rank": 3, "lines": ["Company Three"], "ecr": "0%", "top_rated": True,
     "rank_c": BRONZE,  "border_c": BRONZE,  "b_a": 115, "bg_a": 20},
    {"rank": 4, "lines": ["Company Four"],  "ecr": "0%", "top_rated": True,
     "rank_c": BLUE_L,  "border_c": BLUE_L,  "b_a": 76,  "bg_a": 15},
    {"rank": 5, "lines": ["Company Five"],  "ecr": "0%", "top_rated": True,
     "rank_c": BLUE_L,  "border_c": BLUE_L,  "b_a": 76,  "bg_a": 15},
]

# Reveal order: rank 5 first -> rank 1 last (indices into TOP5)
REVEAL_ORDER = [4, 3, 2, 1, 0]

# ── Card geometry ─────────────────────────────────────────────────────────
C_PAD = s(20)
C_GAP = s(6)
C_W   = (W - 2 * C_PAD - 4 * C_GAP) // 5
C_Y   = s(220)
C_H   = s(110)

def card_x(i):
    return C_PAD + i * (C_W + C_GAP)

# ── Font loader ───────────────────────────────────────────────────────────
def load_font(bold=False, black=False, size=12):
    if black:
        cands = [r"C:\Windows\Fonts\ariblk.ttf",
                 r"C:\Windows\Fonts\segoeuib.ttf",
                 r"C:\Windows\Fonts\arialbd.ttf"]
    elif bold:
        cands = [r"C:\Windows\Fonts\segoeuib.ttf",
                 r"C:\Windows\Fonts\arialbd.ttf"]
    else:
        cands = [r"C:\Windows\Fonts\segoeui.ttf",
                 r"C:\Windows\Fonts\arial.ttf"]
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()

fRank  = load_font(True,  False, s(7))
fName  = load_font(True,  False, s(7))
fEcr   = load_font(True,  False, s(13))
fBadge = load_font(True,  False, s(6))
fLabel = load_font(True,  False, s(8))
fTitle = load_font(False, True,  s(30))
fYear  = load_font(True,  False, s(13))
fStatN = load_font(True,  False, s(26))
fStatL = load_font(True,  False, s(8))
fFoot  = load_font(False, False, s(8))

# ── Company logo loader ───────────────────────────────────────────────────── EDIT
# Replace with the [company-slug]-logo.png filenames sourced in Step 5, ranks 1–5
_LOGO_FILES = {
    0: "company-one-logo.png",
    1: "company-two-logo.png",
    2: "company-three-logo.png",
    3: "company-four-logo.png",
    4: "company-five-logo.png",
}

def _load_logo(filename):
    """Load a PNG logo and convert all opaque pixels to white (CSS brightness(0) invert(1) equivalent)."""
    path = os.path.join(BASE_DIR, "[Industry Name]", filename)  # EDIT: match OUT_PATH's subfolder
    try:
        img  = Image.open(path).convert("RGBA")
        a    = img.split()[3]           # keep original alpha mask
        white = Image.new("RGBA", img.size, (255, 255, 255, 255))
        white.putalpha(a)
        return white
    except Exception:
        return None

def _fit_logo(logo, max_w, max_h):
    """Resize a logo RGBA image to fit inside max_w × max_h, preserving aspect ratio."""
    ratio = min(max_w / logo.width, max_h / logo.height)
    nw = max(1, int(logo.width  * ratio))
    nh = max(1, int(logo.height * ratio))
    return logo.resize((nw, nh), Image.LANCZOS)

# Pre-load and pre-fit all logos once at startup — avoids per-frame LANCZOS resizes in stamp_card()
_LB_W = C_W - s(16)
_LB_H = s(22)
LOGOS        = {i: _load_logo(f) for i, f in _LOGO_FILES.items()}
FITTED_LOGOS = {i: _fit_logo(logo, _LB_W, _LB_H) if logo is not None else None
                for i, logo in LOGOS.items()}

# ── Text helper ───────────────────────────────────────────────────────────
def tc(draw, text, cx, y, fnt, fill):
    """Draw text horizontally centred at cx, top at y."""
    bb = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (bb[2] - bb[0]) // 2, y), text, font=fnt, fill=fill)

# ── Build static base (background + UI, no company cards) ─────────────────
def make_base():
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)

    # Cover gradient top -> bottom — EDIT: match the industry's --cover-bg-start / --cover-bg-end (Step 4)
    GRAD_START = (0, 24, 41)   # #001829
    GRAD_END   = (0, 45, 78)   # #002d4e
    for y in range(H):
        t = y / H
        r = int(GRAD_START[0] * (1 - t) + GRAD_END[0] * t)
        g = int(GRAD_START[1] * (1 - t) + GRAD_END[1] * t)
        b = int(GRAD_START[2] * (1 - t) + GRAD_END[2] * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))

    # Very faint inner border
    bm = s(12)
    d.rectangle([bm, bm, W - bm - 1, H - bm - 1], outline=blend(WHITE, 18))

    # Gold L-corner marks
    M, ARM = s(12), s(24)
    for (ax, dx) in [(M, 1), (W - M, -1)]:
        for (ay, dy) in [(M, 1), (H - M, -1)]:
            d.line([(ax, ay), (ax + dx * ARM, ay)], fill=GOLD, width=s(2))
            d.line([(ax, ay), (ax, ay + dy * ARM)], fill=GOLD, width=s(2))

    # ── RealRate logo pill ───────────────────────────────────────────────
    pw, ph = s(160), s(40)
    px = (W - pw) // 2
    py = s(22)

    logo_ok = False
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        lh   = s(24)
        lw   = int(logo.width * lh / logo.height)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        lx   = px + (pw - lw) // 2
        ly   = py + (ph - lh) // 2
        img_rgba = img.convert("RGBA")
        d2 = ImageDraw.Draw(img_rgba)
        d2.rounded_rectangle([px, py, px + pw, py + ph], radius=s(6), fill=(255,255,255,255))
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        overlay.paste(logo, (lx, ly), logo)
        img = Image.alpha_composite(img_rgba, overlay).convert("RGB")
        logo_ok = True
    except Exception:
        pass

    d = ImageDraw.Draw(img)
    if not logo_ok:
        fL = load_font(True, False, s(15))
        tc(d, "RealRate", W // 2, py + s(11), fL, BLUE_D)

    # ── Title block ────────────────────────────────────────────────────── EDIT
    tc(d, "FINANCIAL HEALTH REPORT",  W // 2, s(76),  fLabel, GOLD)
    tc(d, "[INDUSTRY NAME]",          W // 2, s(94),  fTitle, WHITE)

    # Year bar: decorative lines + year number
    ybar = s(150)
    d.line([(s(40),  ybar), (s(208), ybar)], fill=blend(BLUE_L, 128))
    d.line([(s(332), ybar), (s(500), ybar)], fill=blend(BLUE_L, 128))
    tc(d, "[YEAR]", W // 2, s(142), fYear, BLUE_L)

    # Gold accent rule
    d.line([(W // 2 - s(20), s(155)), (W // 2 + s(20), s(155))],
           fill=GOLD, width=s(2))

    # Horizontal separator
    d.line([(s(25), s(168)), (W - s(25), s(168))], fill=blend(WHITE, 32))

    # Section label above cards
    tc(d, "TOP 5  .  FINANCIAL HEALTH RANKINGS",
       W // 2, s(180), fLabel, blend(WHITE, 110))

    # ── Stats bar ────────────────────────────────────────────────────────
    SY  = C_Y + C_H + s(16)
    SEY = SY + s(62)
    d.line([(0, SY - 1), (W, SY - 1)], fill=blend(WHITE, 22))
    d.line([(0, SEY),    (W, SEY)],    fill=blend(WHITE, 22))

    # EDIT: companies ranked · industry avg ECR · Top-Rated count (from Step 2 rankings pull)
    for i, (num, lbl) in enumerate([("0", "COMPANIES"), ("0%", "AVG ECR"), ("0", "TOP-RATED")]):
        cx_s = W // 6 + i * (W // 3)
        if i > 0:
            d.line([(cx_s - W // 6, SY), (cx_s - W // 6, SEY)], fill=blend(WHITE, 24))
        tc(d, num, cx_s, SY + s(8),  fStatN, WHITE)
        tc(d, lbl, cx_s, SY + s(42), fStatL, blend(WHITE, 97))

    # Footer
    tc(d, "Powered by RealRate  .  Using Explainable Financial AI",
       W // 2, SEY + s(14), fFoot, blend(WHITE, 75))

    return img

# ── Stamp one company card onto an existing image ─────────────────────────
def stamp_card(base, idx, y_off=0):
    co  = TOP5[idx]
    out = base.copy()
    d   = ImageDraw.Draw(out)
    x   = card_x(idx)
    y   = C_Y + y_off
    cx  = x + C_W // 2

    bg_c  = blend(co["border_c"], co["bg_a"])
    bdr_c = blend(co["border_c"], co["b_a"])

    # Gold outer glow ring for rank 1
    if co["rank"] == 1:
        d.rounded_rectangle([x - s(3), y - s(3), x + C_W + s(3), y + C_H + s(3)],
                            radius=s(10), outline=blend(GOLD, 80), width=s(3))

    d.rounded_rectangle([x, y, x + C_W, y + C_H],
                        radius=s(7), fill=bg_c, outline=bdr_c, width=s(2))

    # Rank label
    tc(d, f"#{co['rank']}", cx, y + s(7), fRank, co["rank_c"])

    # Company logo
    lb_y   = y + s(22)
    fitted = FITTED_LOGOS.get(idx)
    if fitted is not None:
        lx = x + s(8) + (_LB_W - fitted.width)  // 2
        ly = lb_y      + (_LB_H - fitted.height) // 2
        out.paste(fitted, (lx, ly), fitted)
    else:
        d.rectangle([x + s(8), lb_y, x + C_W - s(8), lb_y + _LB_H],
                    fill=blend(WHITE, 15))

    # Company name (two lines)
    ny = y + s(54)
    for line in co["lines"]:
        tc(d, line, cx, ny, fName, blend(WHITE, 224))
        ny += s(10)

    # ECR score
    tc(d, co["ecr"], cx, y + s(79), fEcr, GREEN_L)

    # "TOP-RATED" badge — only for top-rated companies
    if co.get("top_rated", True):
        bb = d.textbbox((0, 0), "TOP-RATED", font=fBadge)
        bw = bb[2] - bb[0]
        bx = cx - bw // 2 - s(4)
        by = y + C_H - s(14)
        d.rounded_rectangle([bx, by - s(2), bx + bw + s(8), by + s(9)],
                            radius=s(2), fill=blend(GREEN_L, 51))
        tc(d, "TOP-RATED", cx, by, fBadge, GREEN_L)

    return out

# ── Assemble animation frames ─────────────────────────────────────────────
def build_frames():
    base    = make_base()
    frames  = []
    durs    = []
    visible = []

    def render(new_idx=None, y_off=0):
        img = base.copy()
        for vi in visible:
            img = stamp_card(img, vi)
        if new_idx is not None:
            img = stamp_card(img, new_idx, y_off)
        return img

    # Intro: title + stats only
    for _ in range(4):
        frames.append(base.copy())
        durs.append(80)

    # Reveal each card: slide up then hold
    for card_idx in REVEAL_ORDER:
        for y_off in [s(45), s(25), s(8)]:
            frames.append(render(card_idx, y_off))
            durs.append(60)
        frames.append(render(card_idx, 0))
        durs.append(950 if card_idx == 0 else 480)
        visible.append(card_idx)

    # Final hold: all 5 visible
    frames.append(render())
    durs.append(2600)

    return frames, durs

# ── Main ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Canvas: {W}x{H} px  (SCALE={SCALE})")
    print("Building frames...")
    frames, durs = build_frames()
    print(f"  {len(frames)} frames")

    print("Quantizing to 256 colours...")
    pf = [f.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=0)
          for f in frames]

    print(f"Saving to: {OUT_PATH}")
    pf[0].save(
        OUT_PATH,
        save_all=True,
        append_images=pf[1:],
        duration=durs,
        loop=0,
    )

    kb = os.path.getsize(OUT_PATH) // 1024
    print(f"Done - {kb} KB  ({len(frames)} frames)")
