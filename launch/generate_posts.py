"""
CampusClip Social Media Post Generator v2
Professional-grade 1080x1080 Instagram posts.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_BOLD    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Brand palette
CREAM   = "#F7F4EF"
NAVY    = "#0D1117"
PURPLE  = "#6C63FF"
PURPLE2 = "#8B85FF"
PURPLE3 = "#4B44CC"
WHITE   = "#FFFFFF"
CHARCOAL= "#1C1C2E"
SLATE   = "#64748B"
MUTED   = "#94A3B8"

W, H   = 1080, 1080
PAD    = 88


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
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(rc, gc, bc, alpha))
    return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")

def ring(base, cx, cy, r, color, alpha, width=4):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d  = ImageDraw.Draw(ov)
    rc, gc, bc = hex_rgb(color)
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=(rc, gc, bc, alpha), width=width)
    return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")

def gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    d   = ImageDraw.Draw(img)
    r0, g0, b0 = hex_rgb(top)
    r1, g1, b1 = hex_rgb(bottom)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)],
               fill=(int(r0+(r1-r0)*t), int(g0+(g1-g0)*t), int(b0+(b1-b0)*t)))
    return img

def logo(draw, x, y, theme="dark"):
    sz = 60
    draw.rounded_rectangle([x, y, x+sz, y+sz], radius=14, fill=PURPLE)
    draw.text((x+sz//2, y+sz//2), "CC",
              font=font(FONT_BOLD, 24), fill=WHITE, anchor="mm")
    wm_col = WHITE if theme == "dark" else CHARCOAL
    draw.text((x+sz+14, y+sz//2), "CampusClip",
              font=font(FONT_BOLD, 28), fill=wm_col, anchor="lm")

def branding(draw, theme="dark"):
    logo(draw, PAD, H - 96, theme)

def save(img, filename):
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")


# ── Template 1: HERO LIGHT ───────────────────────────────────────────────────
# Cream bg · giant headline · purple accent word option · circles for depth

def hero_light(filename, line1, line2=None, body=None, tag=None, cta=None):
    img = Image.new("RGB", (W, H), CREAM)
    img = circle(img, W + 60,  -60,  440, PURPLE, 22)
    img = circle(img, -80, H + 80,  300, PURPLE, 12)
    d   = ImageDraw.Draw(img)

    # Left rule
    d.rectangle([PAD, PAD, PAD + 6, H - PAD], fill="#E2DEFF")
    d.rectangle([PAD, PAD, PAD + 6, PAD + 200], fill=PURPLE)

    y = PAD + 20
    if tag:
        tf = font(FONT_BOLD, 26)
        tw = d.textbbox((0,0), tag, font=tf)[2] + 40
        d.rounded_rectangle([PAD+24, y, PAD+24+tw, y+44], radius=22, fill=PURPLE)
        d.text((PAD+44, y+22), tag, font=tf, fill=WHITE, anchor="lm")
        y += 68
    else:
        y += 30

    # Line 1 — charcoal
    h1 = font(FONT_BOLD, 116)
    for l in wrap(line1, h1, W - PAD*2 - 30, d)[:3]:
        d.text((PAD+24, y), l, font=h1, fill=CHARCOAL)
        y += 130

    # Line 2 — purple (optional emphasis)
    if line2:
        h2 = font(FONT_BOLD, 116)
        for l in wrap(line2, h2, W - PAD*2 - 30, d)[:2]:
            d.text((PAD+24, y), l, font=h2, fill=PURPLE)
            y += 130

    y += 10
    d.line([(PAD+24, y), (W - PAD, y)], fill="#D0CAFF", width=2)
    y += 32

    if body:
        bf = font(FONT_REGULAR, 40)
        for l in wrap(body, bf, W - PAD*2 - 30, d)[:6]:
            d.text((PAD+24, y), l, font=bf, fill=SLATE)
            y += 54

    if cta:
        cy = H - 176
        cf = font(FONT_BOLD, 28)
        cw = d.textbbox((0,0), cta, font=cf)[2]
        d.rounded_rectangle([PAD+24, cy, PAD+24+cw+48, cy+52],
                             radius=26, fill=PURPLE)
        d.text((PAD+48, cy+26), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, "light")
    save(img, filename)


# ── Template 2: HERO DARK ────────────────────────────────────────────────────
# Deep navy gradient · glowing purple circles · white headline · muted body

def hero_dark(filename, headline, body=None, cta=None):
    img = gradient(NAVY, "#070C12")
    img = circle(img, W - 80,  160, 360, PURPLE, 30)
    img = circle(img, 120, H - 180, 260, PURPLE, 18)
    d   = ImageDraw.Draw(img)

    d.rectangle([PAD, 64, PAD + 100, 72], fill=PURPLE)

    y = 120
    hf = font(FONT_BOLD, 110)
    for l in wrap(headline, hf, W - PAD*2, d)[:4]:
        d.text((PAD, y), l, font=hf, fill=WHITE)
        y += 124

    y += 16
    if body:
        bf = font(FONT_REGULAR, 42)
        for l in wrap(body, bf, W - PAD*2, d)[:7]:
            d.text((PAD, y), l, font=bf, fill=MUTED)
            y += 56

    if cta:
        cy = H - 176
        cf = font(FONT_BOLD, 30)
        cw = d.textbbox((0,0), cta, font=cf)[2]
        d.rounded_rectangle([PAD, cy, PAD+cw+56, cy+56], radius=28, fill=PURPLE)
        d.text((PAD+28, cy+28), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, "dark")
    save(img, filename)


# ── Template 3: SPLIT ────────────────────────────────────────────────────────
# Purple top block · cream bottom · bold contrast layout

def split(filename, top_text, bottom_headline, bottom_body=None, cta=None):
    img = Image.new("RGB", (W, H), CREAM)
    d   = ImageDraw.Draw(img)
    split_y = 400
    d.rectangle([0, 0, W, split_y], fill=PURPLE3)
    img = circle(img, W - 100, split_y, 200, PURPLE, 60)
    d   = ImageDraw.Draw(img)

    tf = font(FONT_BOLD, 86)
    tlines = wrap(top_text, tf, W - PAD*2, d)
    ty = max(PAD, (split_y - len(tlines[:3])*102)//2)
    for l in tlines[:3]:
        d.text((PAD, ty), l, font=tf, fill=WHITE)
        ty += 102

    y = split_y + 56
    bh = font(FONT_BOLD, 72)
    for l in wrap(bottom_headline, bh, W - PAD*2, d)[:3]:
        d.text((PAD, y), l, font=bh, fill=CHARCOAL)
        y += 86
    y += 12

    if bottom_body:
        bf = font(FONT_REGULAR, 38)
        for l in wrap(bottom_body, bf, W - PAD*2, d)[:4]:
            d.text((PAD, y), l, font=bf, fill=SLATE)
            y += 52

    if cta:
        cy = H - 168
        cf = font(FONT_BOLD, 28)
        cw = d.textbbox((0,0), cta, font=cf)[2]
        d.rounded_rectangle([PAD, cy, PAD+cw+48, cy+52], radius=26, fill=CHARCOAL)
        d.text((PAD+24, cy+26), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, "light")
    save(img, filename)


# ── Template 4: QUOTE CARD ───────────────────────────────────────────────────
# Oversized decorative quote mark · centered text · attribution bar

def quote_card(filename, quote, attribution, subtext=None):
    img = Image.new("RGB", (W, H), "#FAFAF7")
    img = circle(img, W//2, H//2, 460, PURPLE, 7)
    d   = ImageDraw.Draw(img)

    # Giant background quote mark
    d.text((PAD - 24, -80), "“",
           font=font(FONT_BOLD, 300), fill="#EAE5FF")

    # Attribution pill top-right
    af  = font(FONT_BOLD, 24)
    aw  = d.textbbox((0,0), attribution, font=af)[2]
    d.rounded_rectangle([W-PAD-aw-40, 56, W-PAD, 100], radius=20, fill=PURPLE)
    d.text((W-PAD-aw-20, 78), attribution, font=af, fill=WHITE, anchor="lm")

    # Quote
    qf    = font(FONT_BOLD, 74)
    qlines= wrap(quote, qf, W - PAD*2, d)
    total = len(qlines[:5]) * 90
    y     = max(200, (H - total)//2 - 30)
    for l in qlines[:5]:
        d.text((PAD, y), l, font=qf, fill=CHARCOAL)
        y += 90

    y += 24
    d.rectangle([PAD, y, PAD + 80, y + 6], fill=PURPLE)
    y += 34

    if subtext:
        sf = font(FONT_REGULAR, 36)
        for l in wrap(subtext, sf, W - PAD*2, d)[:3]:
            d.text((PAD, y), l, font=sf, fill=SLATE)
            y += 48

    branding(d, "light")
    save(img, filename)


# ── Template 5: BIG NUMBER ───────────────────────────────────────────────────
# Huge centred number · concentric rings for depth · top/dark themes

def big_number(filename, number, label, subtext, theme="dark"):
    if theme == "dark":
        img = gradient(NAVY, "#060C14")
        nc, lc, sc = WHITE,   PURPLE2, MUTED
        rc = PURPLE
    else:
        img = Image.new("RGB", (W, H), CREAM)
        nc, lc, sc = CHARCOAL, PURPLE,  SLATE
        rc = PURPLE

    cx, cy_c = W//2, 420
    for r, a in [(290, 20), (220, 35), (150, 55)]:
        img = ring(img, cx, cy_c, r, rc, a, width=3)

    d = ImageDraw.Draw(img)
    d.rectangle([PAD, 60, PAD + 100, 68], fill=rc)

    nf   = font(FONT_BOLD, 300)
    nbox = d.textbbox((0,0), str(number), font=nf)
    d.text((cx - (nbox[2]-nbox[0])//2, cy_c - 185), str(number), font=nf, fill=nc)

    lf   = font(FONT_BOLD, 70)
    lbox = d.textbbox((0,0), label.upper(), font=lf)
    d.text((cx - (lbox[2]-lbox[0])//2, cy_c + 160), label.upper(), font=lf, fill=lc)

    sf = font(FONT_REGULAR, 38)
    y  = cy_c + 280
    for l in wrap(subtext, sf, W - PAD*2 - 80, d)[:4]:
        bbox = d.textbbox((0,0), l, font=sf)
        d.text((cx - (bbox[2]-bbox[0])//2, y), l, font=sf, fill=sc)
        y += 52

    branding(d, theme)
    save(img, filename)


# ── Template 6: LAUNCH HERO ─────────────────────────────────────────────────
# Full purple gradient · giant headline · white CTA button

def launch_hero(filename, headline, body):
    img = gradient("#5540F0", "#9060F8")
    img = circle(img, W + 100, -100, 500, WHITE,   10)
    img = circle(img, -120, H + 120,  400, "#000000", 18)
    img = circle(img, W//2, H//2,     600, "#3020CC", 55)
    d   = ImageDraw.Draw(img)

    d.rectangle([PAD, 80, PAD + 180, 88], fill="#FFFFFF33")

    hf = font(FONT_BOLD, 150)
    y  = 140
    for l in wrap(headline, hf, W - PAD*2, d)[:2]:
        d.text((PAD, y), l, font=hf, fill=WHITE)
        y += 170

    y += 16
    d.rectangle([PAD, y, W - PAD, y + 3], fill="#FFFFFF44")
    y += 40

    bf = font(FONT_REGULAR, 46)
    for l in wrap(body, bf, W - PAD*2, d)[:6]:
        d.text((PAD, y), l, font=bf, fill="#DDD4FF")
        y += 60

    cy  = H - 180
    cf  = font(FONT_BOLD, 32)
    cta = "download now — link in bio"
    cw  = d.textbbox((0,0), cta, font=cf)[2]
    d.rounded_rectangle([PAD, cy, PAD+cw+56, cy+60], radius=30, fill=WHITE)
    d.text((PAD+28, cy+30), cta, font=cf, fill=PURPLE, anchor="lm")

    branding(d, "dark")
    save(img, filename)


# ── Template 7: TWO PANEL (meme / comparison) ────────────────────────────────
# Dark left / cream right split — problem vs solution

def two_panel(filename, left_label, left_lines, right_label, right_lines):
    img = Image.new("RGB", (W, H), WHITE)
    d   = ImageDraw.Draw(img)
    sx  = W // 2

    d.rectangle([0,  0, sx, H], fill="#10131A")
    d.rectangle([sx, 0, W,  H], fill=CREAM)
    img = circle(img, sx//2,       H//2, 220, PURPLE, 25)
    img = circle(img, sx + sx//2,  H//2, 220, PURPLE, 12)
    d   = ImageDraw.Draw(img)
    d.rectangle([sx-2, 0, sx+2, H], fill=PURPLE)

    ll  = font(FONT_BOLD, 28)
    d.text((sx//2, 76), left_label,  font=ll, fill=MUTED,   anchor="mm")
    d.text((sx+sx//2, 76), right_label, font=ll, fill=PURPLE, anchor="mm")

    lif = font(FONT_REGULAR, 36)
    rif = font(FONT_BOLD,    36)
    ly = ry = 150

    for l in left_lines[:7]:
        bbox = d.textbbox((0,0), l, font=lif)
        lw   = bbox[2]-bbox[0]
        d.text((sx//2 - lw//2, ly), l, font=lif, fill="#94A3B8")
        ly += 58

    for l in right_lines[:7]:
        bbox = d.textbbox((0,0), l, font=rif)
        rw   = bbox[2]-bbox[0]
        d.text((sx+sx//2 - rw//2, ry), l, font=rif, fill=CHARCOAL)
        ry += 58

    branding(d, "dark")
    save(img, filename)


# ── Template 8: CHECKLIST ───────────────────────────────────────────────────
# Numbered circles · thick left rule · clean cream background

def checklist(filename, title, items, cta=None):
    img = Image.new("RGB", (W, H), CREAM)
    img = circle(img, W + 100, -100, 420, PURPLE, 14)
    d   = ImageDraw.Draw(img)

    d.rectangle([0, 0, 14, H], fill=PURPLE)

    tf = font(FONT_BOLD, 68)
    y  = PAD
    for l in wrap(title, tf, W - PAD*2, d)[:2]:
        d.text((PAD + 14, y), l, font=tf, fill=CHARCOAL)
        y += 82
    y += 10
    d.rectangle([PAD+14, y, W-PAD, y+3], fill="#DDD8F0")
    y += 28

    nf  = font(FONT_BOLD,    36)
    itf = font(FONT_REGULAR, 40)
    for i, item in enumerate(items[:7]):
        nx = PAD + 14
        d.ellipse([nx, y, nx+52, y+52], fill=PURPLE)
        d.text((nx+26, y+26), str(i+1), font=nf, fill=WHITE, anchor="mm")
        ilines = wrap(item, itf, W - PAD*2 - 76, d)
        for j, l in enumerate(ilines[:2]):
            d.text((nx+66, y + j*46), l, font=itf, fill=CHARCOAL)
        y += max(68, len(ilines)*46) + 18

    if cta:
        cy  = H - 164
        cf  = font(FONT_BOLD, 28)
        cw  = d.textbbox((0,0), cta, font=cf)[2]
        d.rounded_rectangle([PAD+14, cy, PAD+14+cw+48, cy+52], radius=26, fill=PURPLE)
        d.text((PAD+38, cy+26), cta, font=cf, fill=WHITE, anchor="lm")

    branding(d, "light")
    save(img, filename)


# ── Template 9: STATEMENT DARK (meme-style) ─────────────────────────────────
# Without/With — two halves, looks intentionally designed

def statement_dark(filename, without_text, with_text):
    img = gradient(NAVY, "#0A0F18")
    img = circle(img, W//2, H//2 - 4, 460, PURPLE, 12)
    d   = ImageDraw.Draw(img)

    # Divider
    d.rectangle([0, H//2 - 3, W, H//2 + 3], fill=PURPLE)

    # Labels
    lf = font(FONT_BOLD, 26)
    d.rounded_rectangle([PAD, 52, PAD+180, 94], radius=20, fill="#FFFFFF12")
    d.text((PAD+90, 73), "WITHOUT  ✗", font=lf, fill=MUTED, anchor="mm")

    d.rounded_rectangle([PAD, H//2+24, PAD+160, H//2+66], radius=20, fill=PURPLE)
    d.text((PAD+80, H//2+45), "WITH  ✓", font=lf, fill=WHITE, anchor="mm")

    wf = font(FONT_REGULAR, 46)
    wy = 110
    for l in wrap(without_text, wf, W - PAD*2, d)[:4]:
        d.text((PAD, wy), l, font=wf, fill="#7A8CA0")
        wy += 62

    wf2 = font(FONT_BOLD, 48)
    wy2 = H//2 + 82
    for l in wrap(with_text, wf2, W - PAD*2, d)[:4]:
        d.text((PAD, wy2), l, font=wf2, fill=WHITE)
        wy2 += 66

    branding(d, "dark")
    save(img, filename)


# ════════════════════════════════════════════════════════════════════════════
# GENERATE ALL POSTS
# ════════════════════════════════════════════════════════════════════════════

print("\n🎨  CampusClip — generating v2 posts...\n")

# ── August Pre-Launch ────────────────────────────────────────────────────────

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
    'CampusClip replaces this with a class feed that has your dates, your grades, and your classmates — all in one place.'
)

quote_card(
    "aug05_quote.png",
    "my whole university life was just there",
    "Beta user · Western",
    "She scanned her syllabus. Joined her classes. Saw her classmates. Checked her grade. One app. CampusClip launches at Western August 19th."
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
    ["6 apps", "3 group chats", "no idea what's due", "calculating grades manually", "never found a study group", "always one step behind"],
    "this September",
    ["CampusClip", "one app", "semester organised day one", "grade calculated automatically", "classmates already there", "you're ready"]
)

hero_light(
    "aug11_onestepbehind.png",
    '"I stopped feeling",\none step behind"',
    body="that's the goal. not to be more productive. not to hack your study habits. just to not feel scattered.\n\nCampusClip. launching at Western August 19th.",
    cta="follow for updates"
)

big_number(
    "aug14_18days.png",
    18, "days",
    "then it all starts — new classes, new syllabuses, new group chats you'll never find what you need in. this year is different.",
    theme="dark"
)

# ── Final Countdown ──────────────────────────────────────────────────────────

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
    "Western student · Beta",
    "not in a productivity-hack way. in a 'my whole semester is just there' way. drops tomorrow."
)

hero_dark(
    "aug18_tomorrow.png",
    "tomorrow.",
    body="CampusClip is live at Western University tomorrow.\n\ndownload it. add your classes. photograph your syllabus.\n\nyour September just got easier."
)

# ── Launch Day ───────────────────────────────────────────────────────────────

print("\n── Launch Day ──")

launch_hero(
    "aug19_launch.png",
    "it's live.",
    "CampusClip is now available at Western University.\n\ndownload it. photograph your syllabus. join your classes.\n\nyour classmates are already in there."
)

hero_dark(
    "aug20_day2.png",
    "your classmates are already in there.",
    body="[X] Western students in the first 24 hours.\n[X] class pages live.\n[X] syllabuses uploaded.\n\nstill not on it?",
    cta="link in bio"
)

# ── Launch Aftermath ─────────────────────────────────────────────────────────

print("\n── Launch Aftermath ──")

hero_dark(
    "aug22_3daysin.png",
    "3 days in.",
    body="[X] Western students have already uploaded their syllabus.\n[X] class pages are live.\n\nthe longer you wait, the more you miss.",
    cta="link in bio"
)

hero_light(
    "aug24_gradetracker.png",
    "do you know what grade you need",
    "on your final exam?",
    body="not an estimate. the exact number — based on your syllabus weights and marks so far.\n\nCampusClip calculates it automatically. you'll never go into an exam not knowing what you need.",
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
    body="new classes. new syllabuses. new people in your lectures you've never met.\n\nthis year you don't have to figure it out by week 6.\n\ndownload CampusClip tonight. walk in tomorrow ready.",
    cta="link in bio"
)

# ── September Week 1 ─────────────────────────────────────────────────────────

print("\n── September Week 1 ──")

launch_hero(
    "sep01_firstday.png",
    "first day.",
    "you're going to get 4 syllabuses today.\n\nphotograph each one in CampusClip the moment you get it.\n\nby tonight, your entire semester is organised."
)

hero_light(
    "sep03_studygroup.png",
    "been in class three weeks and still don't know anyone's name?",
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
    "your classmates who scanned their syllabus already know every due date, every exam, and exactly what grade they need.",
    bottom_body="are you one of them?",
    cta="still not too late → link in bio"
)

# ── September Week 2 ─────────────────────────────────────────────────────────

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
    body="not what Canvas shows. your actual weighted grade based on the assignments you've gotten back.\n\nif the answer is no — that's the problem CampusClip solves.",
    cta="link in bio"
)

split(
    "sep14_twoweeks.png",
    "two weeks in.",
    "if you feel scattered, it's fixable.",
    bottom_body="scan your syllabuses. it's genuinely not too late to get your semester under control.",
    cta="link in bio"
)

# ── September Week 3 ─────────────────────────────────────────────────────────

print("\n── September Week 3 ──")

hero_light(
    "sep15_firstassignment.png",
    "your first assignment is coming.",
    body="do you know exactly what it's worth?\nwhat you need to stay on track for your target grade?\nwho in your class you can study with before it's due?\n\nCampusClip has all three.",
    cta="link in bio"
)

statement_dark(
    "sep16_assignmentmeme.png",
    'notes in one app. rubric on Canvas. study group across 3 iMessage threads. grade calculator open in another tab.',
    'CampusClip. one app. your notes, your grade, your class, your due dates — all in one place. link in bio.'
)

checklist(
    "sep17_gradetracker_how.png",
    "how the grade tracker works",
    [
        "photograph syllabus → weights auto-populate",
        "enter your mark as you get each assignment back",
        "CampusClip calculates your weighted grade live",
        "set a target — see what you need on every assessment",
        "always know where you stand. no December surprises.",
    ],
    cta="link in bio"
)

hero_light(
    "sep18_weekendreminder.png",
    "weekend reminder:",
    body="the assignments due next week are already in your CampusClip calendar.\n\nno Sunday-night panic trying to remember what's coming up.\n\njust open the app. you already know.",
    cta="link in bio if you want this"
)

split(
    "sep21_threeweeks.png",
    "three weeks in.",
    "if you're on top of it — tell your friends.",
    bottom_body="someone in your class is struggling. send them this. CampusClip. one app. 15 minutes. your whole semester gets organised.",
    cta="link in bio"
)

# ── September Week 4 — Midterms ───────────────────────────────────────────────

print("\n── September Week 4 (Midterms) ──")

hero_dark(
    "sep22_midtermscoming.png",
    "midterms are coming.",
    body="in 2–3 weeks most Western students will be scrambling to figure out their grade and what they need to score.\n\nthe students who set up CampusClip in week 1 already know all of this. they've known since September 1st.",
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
        "Check what else is due the same week as your midterm",
    ],
    cta="link in bio"
)

hero_light(
    "sep24_studygroup.png",
    "the best study groups don't form in week 6.",
    body="they form in week 2.\n\nif you haven't found yours yet — go to your class page right now. post 'anyone want to study for the midterm.'\n\nsomeone will respond.",
    cta="link in bio"
)

statement_dark(
    "sep25_midtermmeme.png",
    '"do you know what the midterm is worth"\n"no idea check the syllabus"\n"which syllabus"\ncalculating grade manually in notes app',
    'CampusClip users: open app → grade tracker → midterm is 30% → you need 68% → done. link in bio.'
)

hero_dark(
    "sep28_midtermweek.png",
    "midterm week.",
    body="you either know your numbers or you don't.\n\nfor everyone who knows: you're ready.\n\nfor everyone who doesn't: CampusClip is still here. at least go into your midterms knowing what you need.",
    cta="link in bio"
)

hero_dark(
    "sep30_onemonth.png",
    "one month in.",
    body="if you've been on CampusClip since September 1 — your grades have been calculated, your semester organised, your class connected.\n\nif you still haven't: October is a great time to start. the second half is harder.",
    cta="link in bio"
)

count = len(os.listdir(OUTPUT_DIR))
print(f"\n✅  Done — {count} posts saved to launch/posts/")
