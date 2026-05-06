"""
CampusClip Social Media Post Generator v3
Brand-accurate: matches the real CampusClip app design.
Dark blue UI, blue-purple gradient, white text.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# ── CampusClip Brand Colours (matched to actual app) ────────────────────────
BRAND_BLUE      = "#4B6EF5"   # primary blue-purple (buttons, logo, accents)
BRAND_BLUE_LITE = "#6B8EFF"   # lighter blue for secondary text on dark
BRAND_GRAD_A    = "#5B9EF8"   # logo gradient start (top-left, lighter blue)
BRAND_GRAD_B    = "#4040F2"   # logo gradient end   (bottom-right, deep blue-purple)
DARK_BG         = "#0A1628"   # app background (very dark blue)
DARK_BG2        = "#0D1F3C"   # slightly lighter dark blue (gradient target)
CARD_BG         = "#152248"   # card/panel background
CARD_BG2        = "#1E2F5A"   # lighter card
CREAM           = "#F0F4FF"   # light posts: very slight blue tint (not warm cream)
WHITE           = "#FFFFFF"
MUTED           = "#94A3B8"
SLATE           = "#64748B"
ORANGE          = "#F59E0B"   # target/goal accent (from grade ring)
CHARCOAL        = "#0D1535"   # dark text on light backgrounds

W, H  = 1080, 1080
PAD   = 88


# ── Utilities ────────────────────────────────────────────────────────────────

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def wrap(text, fnt, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def circle(base, cx, cy, r, color, alpha):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(ov)
    rc, gc, bc = hex_rgb(color)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(rc, gc, bc, alpha))
    return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")

def ring(base, cx, cy, r, color, alpha, width=3):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(ov)
    rc, gc, bc = hex_rgb(color)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(rc, gc, bc, alpha), width=width)
    return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")

def gradient(top, bottom, w=W, h=H):
    img = Image.new("RGB", (w, h))
    d   = ImageDraw.Draw(img)
    r0,g0,b0 = hex_rgb(top)
    r1,g1,b1 = hex_rgb(bottom)
    for y in range(h):
        t = y / h
        d.line([(0,y),(w,y)], fill=(int(r0+(r1-r0)*t), int(g0+(g1-g0)*t), int(b0+(b1-b0)*t)))
    return img

def diag_gradient(top_left, bottom_right, w=W, h=H):
    """Diagonal gradient (top-left corner to bottom-right corner)."""
    img = Image.new("RGB", (w, h))
    r0,g0,b0 = hex_rgb(top_left)
    r1,g1,b1 = hex_rgb(bottom_right)
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            t = (x/w + y/h) / 2
            pixels[x,y] = (int(r0+(r1-r0)*t), int(g0+(g1-g0)*t), int(b0+(b1-b0)*t))
    return img


# ── Logo ─────────────────────────────────────────────────────────────────────

def draw_logo_icon(draw, img, x, y, size=64):
    """
    Draws the CampusClip logo badge:
    - Blue gradient rounded square
    - White graduation cap (diamond mortarboard)
    - White envelope/chat shape below cap
    """
    # Gradient badge background
    badge = diag_gradient(BRAND_GRAD_A, BRAND_GRAD_B, size, size)
    mask  = Image.new("L", (size, size), 0)
    md    = ImageDraw.Draw(mask)
    r     = size // 5
    md.rounded_rectangle([0, 0, size, size], radius=r, fill=255)
    img.paste(badge, (x, y), mask)

    # Draw icon elements in white on top
    d = ImageDraw.Draw(img)
    pad   = int(size * 0.14)
    iw, ih = size - pad*2, size - pad*2
    ox, oy = x + pad, y + pad   # icon origin

    # Graduation cap — flat diamond (mortarboard top)
    cap_cx = ox + iw // 2
    cap_cy = oy + int(ih * 0.34)
    hw     = int(iw * 0.46)    # half-width of diamond
    hh     = int(ih * 0.15)    # half-height
    cap_pts = [
        (cap_cx,       cap_cy - hh),   # top
        (cap_cx + hw,  cap_cy),         # right
        (cap_cx,       cap_cy + hh),   # bottom
        (cap_cx - hw,  cap_cy),         # left
    ]
    d.polygon(cap_pts, fill=WHITE)

    # Cap tassel stem — small rect on right
    stem_x = cap_cx + hw - int(hw*0.18)
    stem_y = cap_cy
    d.rectangle([stem_x, stem_y, stem_x + int(hw*0.14), cap_cy + int(ih*0.18)], fill=WHITE)

    # Envelope / speech shape below cap
    env_x0 = ox + int(iw * 0.10)
    env_y0 = cap_cy + int(ih * 0.22)
    env_x1 = ox + int(iw * 0.90)
    env_y1 = oy + ih - int(ih * 0.04)
    env_r  = int((env_x1 - env_x0) * 0.18)
    d.rounded_rectangle([env_x0, env_y0, env_x1, env_y1], radius=env_r, fill=WHITE)

    # V notch on top of envelope (classic envelope fold)
    mid_x = (env_x0 + env_x1) // 2
    notch = [
        (env_x0, env_y0),
        (mid_x,  env_y0 + int((env_y1-env_y0)*0.38)),
        (env_x1, env_y0),
    ]
    # Draw notch in brand blue to cut into envelope
    r_b, g_b, b_b = hex_rgb(BRAND_GRAD_B)
    # approximate the badge colour at this position
    t_notch = ((env_x0 - x)/size + (env_y0 - y)/size) / 2
    r_bg = int(hex_rgb(BRAND_GRAD_A)[0] + (r_b - hex_rgb(BRAND_GRAD_A)[0]) * t_notch)
    g_bg = int(hex_rgb(BRAND_GRAD_A)[1] + (g_b - hex_rgb(BRAND_GRAD_A)[1]) * t_notch)
    b_bg = int(hex_rgb(BRAND_GRAD_A)[2] + (b_b - hex_rgb(BRAND_GRAD_A)[2]) * t_notch)
    d.polygon(notch, fill=(r_bg, g_bg, b_bg))


def draw_wordmark(draw, x, y, size=30, color=WHITE):
    """CampusClip text wordmark."""
    f = font(FONT_BOLD, size)
    draw.text((x, y), "CampusClip", font=f, fill=color, anchor="lm")


def branding(draw, img, x=None, y=None, theme="dark", icon_size=56):
    """Logo icon + wordmark."""
    bx = x if x is not None else PAD
    by = y if y is not None else H - 96
    draw_logo_icon(draw, img, bx, by, size=icon_size)
    wm_col = WHITE if theme == "dark" else BRAND_BLUE
    draw_wordmark(draw, bx + icon_size + 14, by + icon_size // 2, size=28, color=wm_col)


def save(img, filename):
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")


# ── App UI mockup helpers ────────────────────────────────────────────────────

def draw_app_card(draw, x, y, w, h, label, value, sublabel=""):
    """Mimics a CampusClip dashboard card."""
    r = 20
    # Card background with slight gradient feel
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=CARD_BG)
    draw.rounded_rectangle([x, y, x+w, y+4], radius=r, fill=BRAND_BLUE)  # top accent

    lf = font(FONT_REGULAR, 28)
    vf = font(FONT_BOLD, 52)
    sf = font(FONT_REGULAR, 24)

    draw.text((x + w//2, y + 44), label, font=lf, fill=MUTED, anchor="mm")
    draw.text((x + w//2, y + h//2 + 14), value, font=vf, fill=WHITE, anchor="mm")
    if sublabel:
        draw.text((x + w//2, y + h - 32), sublabel, font=sf, fill=BRAND_BLUE_LITE, anchor="mm")


def draw_stat_pill(draw, x, y, number, label):
    """Renders a stat like '10K+ Students'."""
    nf = font(FONT_BOLD,    52)
    lf = font(FONT_REGULAR, 28)
    draw.text((x, y),      number, font=nf, fill=WHITE)
    draw.text((x, y + 60), label,  font=lf, fill=MUTED)


def draw_donut(draw, cx, cy, r, pct, track_col, fill_col, label, sublabel):
    """Simple donut chart (like the grade rings in the app)."""
    # Track
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=track_col, width=14)
    # Arc
    start = -90
    end   = start + int(360 * pct)
    draw.arc([cx-r, cy-r, cx+r, cy+r], start=start, end=end, fill=fill_col, width=14)
    # Labels
    draw.text((cx, cy - 10), label,    font=font(FONT_BOLD, 38),    fill=WHITE,           anchor="mm")
    draw.text((cx, cy + 32), sublabel, font=font(FONT_REGULAR, 24), fill=BRAND_BLUE_LITE, anchor="mm")


# ════════════════════════════════════════════════════════════════════════════
# TEMPLATES
# ════════════════════════════════════════════════════════════════════════════

def hero_dark(filename, headline, body=None, cta=None, tag=None):
    """
    Dark blue gradient background (matches app bg).
    Large headline, decorative glow circles.
    """
    img = gradient(DARK_BG, DARK_BG2)
    # Glow circles matching app aesthetic
    img = circle(img, W - 60,  100,  380, BRAND_BLUE, 28)
    img = circle(img, 80,  H - 120, 280, BRAND_BLUE, 18)
    img = circle(img, W//2, H//2,   520, "#000820",  70)
    d   = ImageDraw.Draw(img)

    # Top accent bar (matches app's horizontal accent lines)
    d.rectangle([PAD, 64, PAD + 120, 70], fill=BRAND_BLUE)

    y = 118
    if tag:
        tf  = font(FONT_BOLD, 26)
        tw  = d.textbbox((0,0), tag, font=tf)[2] + 40
        d.rounded_rectangle([PAD, y, PAD+tw, y+44], radius=22, fill=BRAND_BLUE)
        d.text((PAD+20, y+22), tag, font=tf, fill=WHITE, anchor="lm")
        y += 64

    hf = font(FONT_BOLD, 108)
    for l in wrap(headline, hf, W - PAD*2, d)[:4]:
        d.text((PAD, y), l, font=hf, fill=WHITE)
        y += 122

    y += 16
    if body:
        bf = font(FONT_REGULAR, 42)
        for l in wrap(body, bf, W - PAD*2, d)[:7]:
            d.text((PAD, y), l, font=bf, fill=MUTED)
            y += 56

    if cta:
        cy  = H - 180
        cf  = font(FONT_BOLD, 30)
        cw  = d.textbbox((0,0), cta, font=cf)[2]
        # Gradient button (like the app's Sign In button)
        btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, cw+56, 56)
        bmask = Image.new("L", (cw+56, 56), 0)
        ImageDraw.Draw(bmask).rounded_rectangle([0,0,cw+56,56], radius=28, fill=255)
        img.paste(btn, (PAD, cy), bmask)
        d = ImageDraw.Draw(img)
        d.text((PAD+28, cy+28), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, img)
    save(img, filename)


def hero_light(filename, line1, line2=None, body=None, tag=None, cta=None):
    """
    Light blue-tinted background. Dark headline, blue accent second line.
    """
    img = Image.new("RGB", (W, H), CREAM)
    img = circle(img, W + 60,  -60,  460, BRAND_BLUE, 18)
    img = circle(img, -80, H + 80,  320, BRAND_BLUE, 10)
    d   = ImageDraw.Draw(img)

    # Left rule — blue
    d.rectangle([PAD, PAD, PAD + 6, H - PAD], fill="#D0D8FF")
    d.rectangle([PAD, PAD, PAD + 6, PAD + 220], fill=BRAND_BLUE)

    y = PAD + 20
    if tag:
        tf = font(FONT_BOLD, 26)
        tw = d.textbbox((0,0), tag, font=tf)[2] + 40
        d.rounded_rectangle([PAD+24, y, PAD+24+tw, y+44], radius=22, fill=BRAND_BLUE)
        d.text((PAD+44, y+22), tag, font=tf, fill=WHITE, anchor="lm")
        y += 68
    else:
        y += 30

    h1 = font(FONT_BOLD, 112)
    for l in wrap(line1, h1, W - PAD*2 - 30, d)[:3]:
        d.text((PAD+24, y), l, font=h1, fill=CHARCOAL)
        y += 126

    if line2:
        for l in wrap(line2, h1, W - PAD*2 - 30, d)[:2]:
            d.text((PAD+24, y), l, font=h1, fill=BRAND_BLUE)
            y += 126

    y += 8
    d.line([(PAD+24, y), (W-PAD, y)], fill="#C8D0F0", width=2)
    y += 32

    if body:
        bf = font(FONT_REGULAR, 40)
        for l in wrap(body, bf, W - PAD*2 - 30, d)[:6]:
            d.text((PAD+24, y), l, font=bf, fill=SLATE)
            y += 54

    if cta:
        cy  = H - 180
        cf  = font(FONT_BOLD, 28)
        cw  = d.textbbox((0,0), cta, font=cf)[2]
        btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, cw+48, 52)
        bmask = Image.new("L", (cw+48, 52), 0)
        ImageDraw.Draw(bmask).rounded_rectangle([0,0,cw+48,52], radius=26, fill=255)
        img.paste(btn, (PAD+24, cy), bmask)
        d = ImageDraw.Draw(img)
        d.text((PAD+48, cy+26), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, img, theme="light")
    save(img, filename)


def launch_hero(filename, headline, body):
    """
    Full brand gradient. Launch announcements.
    Matches the blue-purple gradient of the CampusClip brand.
    """
    img = diag_gradient(BRAND_GRAD_A, BRAND_GRAD_B)
    img = circle(img, W + 100, -100, 500, WHITE,   9)
    img = circle(img, -120, H + 120,  420, "#000830", 40)
    img = circle(img, W - 200, H - 200, 350, "#2020A0", 50)
    d   = ImageDraw.Draw(img)

    d.rectangle([PAD, 80, PAD + 200, 87], fill="#FFFFFF30")

    hf = font(FONT_BOLD, 148)
    y  = 140
    for l in wrap(headline, hf, W - PAD*2, d)[:2]:
        d.text((PAD, y), l, font=hf, fill=WHITE)
        y += 168

    y += 12
    d.rectangle([PAD, y, W-PAD, y+3], fill="#FFFFFF40")
    y += 40

    bf = font(FONT_REGULAR, 46)
    for l in wrap(body, bf, W - PAD*2, d)[:6]:
        d.text((PAD, y), l, font=bf, fill="#D8E4FF")
        y += 62

    cy  = H - 186
    cf  = font(FONT_BOLD, 32)
    cta = "download now — link in bio"
    cw  = d.textbbox((0,0), cta, font=cf)[2]
    d.rounded_rectangle([PAD, cy, PAD+cw+56, cy+60], radius=30, fill=WHITE)
    d.text((PAD+28, cy+30), cta, font=cf, fill=BRAND_GRAD_B, anchor="lm")

    branding(d, img)
    save(img, filename)


def split(filename, top_text, bottom_headline, bottom_body=None, cta=None):
    """
    Top: brand gradient block. Bottom: light blue-tinted.
    """
    img = Image.new("RGB", (W, H), CREAM)
    split_y = 400
    top_block = diag_gradient(BRAND_GRAD_A, BRAND_GRAD_B, W, split_y)
    img.paste(top_block, (0, 0))
    img = circle(img, W - 120, split_y, 190, BRAND_BLUE, 55)
    d   = ImageDraw.Draw(img)

    tf = font(FONT_BOLD, 84)
    tl = wrap(top_text, tf, W-PAD*2, d)
    ty = max(PAD, (split_y - len(tl[:3])*100)//2)
    for l in tl[:3]:
        d.text((PAD, ty), l, font=tf, fill=WHITE)
        ty += 100

    y = split_y + 60
    bh = font(FONT_BOLD, 70)
    for l in wrap(bottom_headline, bh, W-PAD*2, d)[:3]:
        d.text((PAD, y), l, font=bh, fill=CHARCOAL)
        y += 84
    y += 12

    if bottom_body:
        bf = font(FONT_REGULAR, 38)
        for l in wrap(bottom_body, bf, W-PAD*2, d)[:4]:
            d.text((PAD, y), l, font=bf, fill=SLATE)
            y += 52

    if cta:
        cy  = H - 168
        cf  = font(FONT_BOLD, 28)
        cw  = d.textbbox((0,0), cta, font=cf)[2]
        btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, cw+48, 52)
        bmask = Image.new("L", (cw+48, 52), 0)
        ImageDraw.Draw(bmask).rounded_rectangle([0,0,cw+48,52], radius=26, fill=255)
        img.paste(btn, (PAD, cy), bmask)
        d = ImageDraw.Draw(img)
        d.text((PAD+24, cy+26), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, img, theme="light")
    save(img, filename)


def quote_card(filename, quote, attribution, subtext=None):
    """
    Dark blue card — matches app's dark panel aesthetic.
    Large white quote text. Attribution in brand blue.
    """
    img = gradient(DARK_BG, DARK_BG2)
    img = circle(img, W//2, H//2, 480, BRAND_BLUE, 10)
    d   = ImageDraw.Draw(img)

    # Giant decorative quote mark
    d.text((PAD - 20, -70), "“", font=font(FONT_BOLD, 300), fill="#1A2E5A")

    # Attribution pill top-right
    af  = font(FONT_BOLD, 24)
    aw  = d.textbbox((0,0), attribution, font=af)[2]
    btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, aw+40, 44)
    bmask = Image.new("L", (aw+40, 44), 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0,0,aw+40,44], radius=22, fill=255)
    img.paste(btn, (W-PAD-aw-40, 56), bmask)
    d = ImageDraw.Draw(img)
    d.text((W-PAD-aw-20, 78), attribution, font=af, fill=WHITE, anchor="lm")

    qf     = font(FONT_BOLD, 72)
    qlines = wrap(quote, qf, W-PAD*2, d)
    total  = len(qlines[:5]) * 88
    y      = max(200, (H-total)//2 - 30)
    for l in qlines[:5]:
        d.text((PAD, y), l, font=qf, fill=WHITE)
        y += 88

    y += 24
    # Gradient accent bar
    bar = gradient(BRAND_GRAD_A, BRAND_GRAD_B, 100, 6)
    img.paste(bar, (PAD, y))
    d = ImageDraw.Draw(img)
    y += 34

    if subtext:
        sf = font(FONT_REGULAR, 36)
        for l in wrap(subtext, sf, W-PAD*2, d)[:3]:
            d.text((PAD, y), l, font=sf, fill=MUTED)
            y += 48

    branding(d, img)
    save(img, filename)


def big_number(filename, number, label, subtext, theme="dark"):
    """
    Huge centred number with concentric rings (like app's grade donuts).
    """
    if theme == "dark":
        img = gradient(DARK_BG, DARK_BG2)
        nc, lc, sc = WHITE, BRAND_BLUE_LITE, MUTED
    else:
        img = Image.new("RGB", (W, H), CREAM)
        nc, lc, sc = CHARCOAL, BRAND_BLUE, SLATE

    cx, cy_c = W//2, 410
    for r, a in [(300, 18), (230, 32), (158, 50)]:
        img = ring(img, cx, cy_c, r, BRAND_BLUE, a, width=3)

    d = ImageDraw.Draw(img)
    d.rectangle([PAD, 60, PAD+120, 68], fill=BRAND_BLUE)

    nf   = font(FONT_BOLD, 296)
    nbox = d.textbbox((0,0), str(number), font=nf)
    d.text((cx - (nbox[2]-nbox[0])//2, cy_c-182), str(number), font=nf, fill=nc)

    lf   = font(FONT_BOLD, 68)
    lbox = d.textbbox((0,0), label.upper(), font=lf)
    d.text((cx - (lbox[2]-lbox[0])//2, cy_c+158), label.upper(), font=lf, fill=lc)

    sf = font(FONT_REGULAR, 38)
    y  = cy_c + 270
    for l in wrap(subtext, sf, W-PAD*2-80, d)[:4]:
        bx = d.textbbox((0,0), l, font=sf)
        d.text((cx-(bx[2]-bx[0])//2, y), l, font=sf, fill=sc)
        y += 52

    branding(d, img, theme=theme)
    save(img, filename)


def dashboard_mockup(filename, headline, body, cta=None):
    """
    Renders a post that shows a CampusClip dashboard-style UI card.
    Great for showing the product's actual look.
    """
    img = gradient(DARK_BG, "#0F1F3A")
    img = circle(img, W - 80, 160, 340, BRAND_BLUE, 22)
    d   = ImageDraw.Draw(img)

    # Top bar
    d.rectangle([PAD, 64, PAD+120, 70], fill=BRAND_BLUE)

    y = 120
    hf = font(FONT_BOLD, 72)
    for l in wrap(headline, hf, W-PAD*2, d)[:2]:
        d.text((PAD, y), l, font=hf, fill=WHITE)
        y += 86
    y += 20

    # Mock grade card (like "Your Academic Performance" panel)
    card_x, card_y = PAD, y
    card_w, card_h = W - PAD*2, 220
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h],
                        radius=20, fill=CARD_BG)
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+5],
                        radius=20, fill=BRAND_BLUE)
    d.text((card_x+30, card_y+40), "Your Academic Performance",
           font=font(FONT_BOLD, 32), fill=WHITE)
    d.text((card_x+30, card_y+82), "Based on 4 active classes",
           font=font(FONT_REGULAR, 26), fill=MUTED)

    # Two donut rings (like the app)
    draw_donut(d, card_x + card_w - 220, card_y + card_h//2 + 10,
               64, 0.74, CARD_BG2, BRAND_BLUE, "74%", "CURRENT")
    draw_donut(d, card_x + card_w - 90,  card_y + card_h//2 + 10,
               64, 0.80, CARD_BG2, ORANGE,     "80%", "TARGET")

    y = card_y + card_h + 36

    # Two class cards
    cw2 = (W - PAD*2 - 16) // 2
    for i, (code, name) in enumerate([("MOS-2228B", "Managerial Accounting"),
                                       ("EC2156B",   "Labour Economics")]):
        cx2 = PAD + i*(cw2+16)
        d.rounded_rectangle([cx2, y, cx2+cw2, y+150], radius=16, fill=CARD_BG)
        d.rounded_rectangle([cx2, y, cx2+cw2, y+4],   radius=16, fill=BRAND_BLUE)
        d.text((cx2+16, y+22), code,  font=font(FONT_BOLD,    24), fill=BRAND_BLUE_LITE)
        nl = wrap(name, font(FONT_BOLD, 28), cw2-32, d)
        ny = y + 54
        for l in nl[:2]:
            d.text((cx2+16, ny), l, font=font(FONT_BOLD, 28), fill=WHITE)
            ny += 34
        d.text((cx2+cw2-16, y+110), "74%", font=font(FONT_BOLD, 34), fill=WHITE, anchor="rm")

    y += 170

    if body:
        bf = font(FONT_REGULAR, 38)
        for l in wrap(body, bf, W-PAD*2, d)[:3]:
            d.text((PAD, y), l, font=bf, fill=MUTED)
            y += 52

    if cta:
        cy2 = H - 180
        cf  = font(FONT_BOLD, 30)
        cw3 = d.textbbox((0,0), cta, font=cf)[2]
        btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, cw3+56, 56)
        bmask = Image.new("L", (cw3+56, 56), 0)
        ImageDraw.Draw(bmask).rounded_rectangle([0,0,cw3+56,56], radius=28, fill=255)
        img.paste(btn, (PAD, cy2), bmask)
        d = ImageDraw.Draw(img)
        d.text((PAD+28, cy2+28), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, img)
    save(img, filename)


def two_panel(filename, left_label, left_lines, right_label, right_lines):
    """
    Dark left (problem) / light right (solution).
    """
    img = Image.new("RGB", (W, H), WHITE)
    d   = ImageDraw.Draw(img)
    sx  = W // 2

    d.rectangle([0,  0, sx, H], fill=DARK_BG)
    d.rectangle([sx, 0, W,  H], fill=CREAM)
    img = circle(img, sx//2,      H//2, 220, BRAND_BLUE, 22)
    img = circle(img, sx+sx//2,   H//2, 220, BRAND_BLUE, 10)
    d   = ImageDraw.Draw(img)

    # Gradient centre divider
    for i in range(4):
        t  = i / 3
        rc = int(hex_rgb(BRAND_GRAD_A)[0]*(1-t) + hex_rgb(BRAND_GRAD_B)[0]*t)
        gc = int(hex_rgb(BRAND_GRAD_A)[1]*(1-t) + hex_rgb(BRAND_GRAD_B)[1]*t)
        bc = int(hex_rgb(BRAND_GRAD_A)[2]*(1-t) + hex_rgb(BRAND_GRAD_B)[2]*t)
        d.line([(sx-1+i, 0), (sx-1+i, H)], fill=(rc,gc,bc))

    ll = font(FONT_BOLD, 28)
    d.text((sx//2,    72), left_label,  font=ll, fill=MUTED,      anchor="mm")
    d.text((sx+sx//2, 72), right_label, font=ll, fill=BRAND_BLUE, anchor="mm")

    lif = font(FONT_REGULAR, 36)
    rif = font(FONT_BOLD,    36)
    ly = ry = 144

    for l in left_lines[:7]:
        bx = d.textbbox((0,0), l, font=lif)
        d.text((sx//2 - (bx[2]-bx[0])//2, ly), l, font=lif, fill="#7A8CA0")
        ly += 58

    for l in right_lines[:7]:
        bx = d.textbbox((0,0), l, font=rif)
        d.text((sx+sx//2 - (bx[2]-bx[0])//2, ry), l, font=rif, fill=CHARCOAL)
        ry += 58

    branding(d, img, theme="dark")
    save(img, filename)


def checklist(filename, title, items, cta=None):
    """
    Numbered checklist. Gradient left bar. Light blue background.
    """
    img = Image.new("RGB", (W, H), CREAM)
    img = circle(img, W+100, -100, 420, BRAND_BLUE, 14)

    # Gradient left strip
    strip = gradient(BRAND_GRAD_A, BRAND_GRAD_B, 14, H)
    img.paste(strip, (0, 0))
    d = ImageDraw.Draw(img)

    tf = font(FONT_BOLD, 66)
    y  = PAD
    for l in wrap(title, tf, W-PAD*2, d)[:2]:
        d.text((PAD+16, y), l, font=tf, fill=CHARCOAL)
        y += 80
    y += 10
    d.rectangle([PAD+16, y, W-PAD, y+3], fill="#C8D0F0")
    y += 28

    nf  = font(FONT_BOLD,    36)
    itf = font(FONT_REGULAR, 40)
    for i, item in enumerate(items[:7]):
        nx = PAD + 16
        # Gradient circle for number
        circ = diag_gradient(BRAND_GRAD_A, BRAND_GRAD_B, 54, 54)
        cmask = Image.new("L", (54,54), 0)
        ImageDraw.Draw(cmask).ellipse([0,0,54,54], fill=255)
        img.paste(circ, (nx, y), cmask)
        d = ImageDraw.Draw(img)
        d.text((nx+27, y+27), str(i+1), font=nf, fill=WHITE, anchor="mm")

        il = wrap(item, itf, W-PAD*2-76, d)
        for j, l in enumerate(il[:2]):
            d.text((nx+68, y+j*46), l, font=itf, fill=CHARCOAL)
        y += max(68, len(il)*46) + 18

    if cta:
        cy  = H - 164
        cf  = font(FONT_BOLD, 28)
        cw  = d.textbbox((0,0), cta, font=cf)[2]
        btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, cw+48, 52)
        bmask = Image.new("L", (cw+48, 52), 0)
        ImageDraw.Draw(bmask).rounded_rectangle([0,0,cw+48,52], radius=26, fill=255)
        img.paste(btn, (PAD+16, cy), bmask)
        d = ImageDraw.Draw(img)
        d.text((PAD+40, cy+26), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, img, theme="light")
    save(img, filename)


def statement_dark(filename, without_text, with_text):
    """
    Without / With two-half format. Dark, branded.
    """
    img = gradient(DARK_BG, DARK_BG2)
    img = circle(img, W//2, H//2, 460, BRAND_BLUE, 10)
    d   = ImageDraw.Draw(img)

    # Gradient divider
    bar = gradient(BRAND_GRAD_A, BRAND_GRAD_B, W, 6)
    img.paste(bar, (0, H//2 - 3))
    d = ImageDraw.Draw(img)

    lf = font(FONT_BOLD, 26)
    d.rounded_rectangle([PAD, 52, PAD+200, 96], radius=20, fill=CARD_BG)
    d.text((PAD+100, 74), "WITHOUT  ✗", font=lf, fill=MUTED, anchor="mm")

    btn = gradient(BRAND_GRAD_A, BRAND_GRAD_B, 160, 44)
    bmask = Image.new("L", (160,44), 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0,0,160,44], radius=22, fill=255)
    img.paste(btn, (PAD, H//2+24), bmask)
    d = ImageDraw.Draw(img)
    d.text((PAD+80, H//2+46), "WITH  ✓", font=lf, fill=WHITE, anchor="mm")

    wf = font(FONT_REGULAR, 44)
    wy = 112
    for l in wrap(without_text, wf, W-PAD*2, d)[:4]:
        d.text((PAD, wy), l, font=wf, fill="#5A6A80")
        wy += 60

    wf2 = font(FONT_BOLD, 46)
    wy2 = H//2 + 82
    for l in wrap(with_text, wf2, W-PAD*2, d)[:4]:
        d.text((PAD, wy2), l, font=wf2, fill=WHITE)
        wy2 += 64

    branding(d, img)
    save(img, filename)


# ════════════════════════════════════════════════════════════════════════════
# GENERATE ALL POSTS
# ════════════════════════════════════════════════════════════════════════════

print("\n🎨  CampusClip v3 — brand-accurate posts...\n")

print("── August Pre-Launch ──")

hero_light(
    "aug01_6apps.png",
    "you have 6 apps open",
    "and still don't know when your midterm is.",
    body="canvas. google cal. your notes app. the group chat. instagram dms. another group chat.\n\nwe made an app for this.",
    tag="coming August 19 · Western",
    cta="follow so you don't miss it"
)

statement_dark(
    "aug04_groupchat.png",
    '"wait when is the project due"\n"idk check canvas"\n"canvas doesn\'t have it"\n"which syllabus"\n\nthis is every Western class group chat.',
    'CampusClip replaces this with a class feed — your dates, your grades, your classmates. one place.'
)

quote_card(
    "aug05_quote.png",
    "my whole university life was just there",
    "Beta user · Western",
    "She scanned her syllabus. Joined her classes. Saw her classmates. Checked her grade. One app. CampusClip launches August 19th."
)

big_number(
    "aug07_25days.png",
    25, "days",
    "The students who download CampusClip in the first week are going to have a very different year. Western University · August 19, 2026.",
    theme="light"
)

two_panel(
    "aug08_returning.png",
    "last September",
    ["6 apps", "3 group chats", "no idea what's due", "grades calculated by hand", "never found a study group", "always one step behind"],
    "this September",
    ["CampusClip", "one app", "semester organised day one", "grade calculated automatically", "classmates already there", "you're ready"]
)

hero_dark(
    "aug11_onestepbehind.png",
    '"I stopped feeling one step behind"',
    body="that's the goal. not to hack your study habits. just to not feel scattered.\n\nCampusClip. launching at Western August 19th.",
    cta="follow for updates"
)

big_number(
    "aug14_18days.png",
    18, "days",
    "then it all starts — new classes, new syllabuses, new group chats. this year is different. CampusClip launches at Western from day one.",
    theme="dark"
)

print("\n── Final Countdown ──")

big_number(
    "aug15_4days.png",
    4, "days",
    "CampusClip launches at Western on August 19th. one app for your classes, your grades, and your classmates.",
    theme="dark"
)

quote_card(
    "aug17_wishihadit.png",
    "I wish I had this in first year",
    "Western · Beta",
    "not in a productivity-hack way. in a 'my whole semester is just there' way. drops tomorrow."
)

hero_dark(
    "aug18_tomorrow.png",
    "tomorrow.",
    body="CampusClip is live at Western University tomorrow.\n\ndownload it. add your classes. photograph your syllabus.\n\nyour September just got easier."
)

print("\n── Launch Day ──")

launch_hero(
    "aug19_launch.png",
    "it's live.",
    "CampusClip is now available at Western University.\n\ndownload it. photograph your syllabus. join your classes.\n\nyour classmates are already in there."
)

dashboard_mockup(
    "aug20_day2.png",
    "this is what your semester looks like in CampusClip.",
    "your grades. your classes. your classmates. all in one place.",
    cta="link in bio"
)

print("\n── Launch Aftermath ──")

hero_dark(
    "aug22_3daysin.png",
    "3 days in.",
    body="[X] Western students have already uploaded their syllabus.\n[X] class pages are live.\n\nyour classmates are in there. the longer you wait, the more you miss.",
    cta="link in bio"
)

hero_light(
    "aug24_gradetracker.png",
    "do you know what grade you need",
    "on your final exam?",
    body="not an estimate. the exact number — based on your syllabus weights and marks so far.\n\nCampusClip calculates it automatically from day one.",
    cta="link in bio"
)

split(
    "aug25_orientation.png",
    "orientation week.",
    "know your classmates before you walk in.",
    bottom_body="join your class feeds on CampusClip and you already know who's in your PSYCH 1000 before the first lecture.",
    cta="link in bio"
)

hero_light(
    "aug27_classmate.png",
    "somewhere in your lecture is your best study partner.",
    body="you won't find them on Canvas. you won't find them on Instagram.\n\nor you could just open CampusClip, join the class, and see everyone already in there.",
    cta="link in bio"
)

checklist(
    "aug28_checklist.png",
    "your first week checklist",
    [
        "Download CampusClip before first class",
        "Add all your courses (takes 60 seconds)",
        "Photograph every syllabus as you get it",
        "Join your class feeds — find your classmates",
        "Browse campus clubs and events",
        "Set your grade targets for each course",
    ]
)

hero_light(
    "aug29_weekend.png",
    "enjoy this weekend.",
    body="next weekend you'll be back at Western, pretending you don't have three syllabuses to read.\n\nwe'll be there when you're ready.",
    cta="download takes 20 seconds"
)

big_number(
    "aug30_twosleeps.png",
    2, "sleeps",
    "do one thing tonight: download CampusClip. you can do the rest when your syllabus is in your hand.",
    theme="dark"
)

hero_dark(
    "aug31_tomorrow.png",
    "tomorrow it starts.",
    body="new classes. new syllabuses. new people in your lectures.\n\nthis year you don't figure it out by week 6.\n\ndownload CampusClip tonight. walk in tomorrow ready.",
    cta="link in bio"
)

print("\n── September Week 1 ──")

launch_hero(
    "sep01_firstday.png",
    "first day.",
    "you're going to get 4 syllabuses today.\n\nphotograph each one in CampusClip the moment you get it.\n\nby tonight, your entire semester is organised."
)

hero_light(
    "sep03_studygroup.png",
    "been in class three days and still don't know anyone's name?",
    body="CampusClip fixes this.\n\njoin your class and your classmates are right there — no awkward Instagram search, no waiting for someone to make a group chat.",
    cta="link in bio"
)

two_panel(
    "sep04_week1meme.png",
    "without CampusClip",
    ["6 apps open", "3 group chats", "no idea what's due", "calculating grades by hand", "never found a study group"],
    "with CampusClip",
    ["one app", "class feed built in", "every due date visible", "grade auto-calculated", "study group sorted week 1"]
)

hero_light(
    "sep05_weekend.png",
    "you survived week one.",
    body="while you're recovering this weekend, your CampusClip is sitting there with your entire semester already organised.\n\nno Sunday anxiety about what's due Monday.",
    cta="link in bio if you haven't yet"
)

split(
    "sep07_week2.png",
    "week 2.",
    "your classmates who scanned their syllabus already know every due date and exactly what grade they need.",
    bottom_body="are you one of them?",
    cta="still not too late → link in bio"
)

print("\n── September Week 2 ──")

hero_light(
    "sep08_clubs.png",
    "clubs at Western don't come to you.",
    body="orientation week is basically the only time they're visible.\n\nCampusClip shows you what's on campus, what they're about, and when they're meeting.",
    cta="link in bio"
)

statement_dark(
    "sep09_groupchatgrief.png",
    '"someone add me to the group chat"\n47 messages about when to meet\nassignment reminder buried in memes\n"wait that was due TODAY"',
    'CampusClip replaces this with a class feed that has your dates, your classmates, and no chaos.'
)

hero_dark(
    "sep11_gradecheck.png",
    "do you know your actual grade right now?",
    body="not what Canvas shows. your actual weighted grade based on every assignment you've gotten back.\n\nif the answer is no — that's what CampusClip solves.",
    cta="link in bio"
)

split(
    "sep14_twoweeks.png",
    "two weeks in.",
    "if you feel scattered, it's fixable.",
    bottom_body="scan your syllabuses. it's genuinely not too late to get your semester under control.",
    cta="link in bio"
)

print("\n── September Week 3 ──")

hero_light(
    "sep15_firstassignment.png",
    "your first assignment is coming.",
    body="do you know exactly what it's worth?\nwhat you need to stay on track for your target grade?\nwho in your class you can study with?\n\nCampusClip has all three.",
    cta="link in bio"
)

statement_dark(
    "sep16_assignmentmeme.png",
    'notes in one app. rubric on Canvas. study group across 3 iMessage threads. grade calculator open in another tab.',
    'CampusClip. your notes, your grade, your class, your due dates — all in one place. link in bio.'
)

checklist(
    "sep17_gradetracker_how.png",
    "how the grade tracker works",
    [
        "photograph syllabus → grade weights auto-populate",
        "enter your mark as you get each assignment back",
        "CampusClip calculates your weighted grade live",
        "set a target — see what you need on every assessment",
        "always know where you stand. no December surprises.",
    ],
    cta="link in bio"
)

dashboard_mockup(
    "sep18_weekendreminder.png",
    "your assignments due next week are already in CampusClip.",
    "no Sunday-night panic. just open the app. you already know.",
    cta="link in bio"
)

split(
    "sep21_threeweeks.png",
    "three weeks in.",
    "if you're on top of it — tell your friends.",
    bottom_body="someone in your class is struggling. send them this. one app. 15 minutes. semester organised.",
    cta="link in bio"
)

print("\n── September Week 4 (Midterms) ──")

hero_dark(
    "sep22_midtermscoming.png",
    "midterms are coming.",
    body="in 2–3 weeks most Western students will be scrambling to figure out their grade.\n\nthe students who set up CampusClip in week 1 already know all of this. they've known since September 1st.",
    cta="link in bio · still helps"
)

checklist(
    "sep23_midtermprep.png",
    "midterm prep in CampusClip",
    [
        "Check your exact current grade in grade tracker",
        "Check the midterm weight — is it 20%? 35%?",
        "Check what score you need to hit your target",
        "Post in class feed — find a study group now",
        "Check what else is due the same week",
    ],
    cta="link in bio"
)

hero_light(
    "sep24_studygroup.png",
    "the best study groups don't form in week 6.",
    body="they form in week 2.\n\nif you haven't found yours yet — go to your class page right now. post 'anyone want to study for the midterm.'\n\nsomeone will respond.",
    cta="link in bio"
)

two_panel(
    "sep25_midtermmeme.png",
    "without CampusClip",
    ['"which syllabus"', "grade unknown", "midterm weight unknown", "studying alone", "going in blind"],
    "with CampusClip",
    ["open app", "current grade: 74%", "midterm is 30%", "need 68% to hit B+", "study group found"]
)

hero_dark(
    "sep28_midtermweek.png",
    "midterm week.",
    body="you either know your numbers or you don't.\n\nfor everyone who knows: you're ready.\n\nfor everyone who doesn't: CampusClip is still here. at least go in knowing what you need.",
    cta="link in bio"
)

hero_dark(
    "sep30_onemonth.png",
    "one month in.",
    body="your grades calculated. your semester organised. your class connected — since day one.\n\nif you still haven't: October is a great time to start. the second half is harder.",
    cta="link in bio"
)

count = len(os.listdir(OUTPUT_DIR))
print(f"\n✅  Done — {count} posts saved to launch/posts/")
