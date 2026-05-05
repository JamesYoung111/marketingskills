"""
CampusClip Social Media Post Generator
Generates Instagram-ready 1080x1080 PNG images for each post.
"""

from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

# ── Paths ──────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Brand colours ──────────────────────────────────────────────────────────
BG_LIGHT    = "#F5F3EE"   # warm off-white
BG_DARK     = "#1A1A2E"   # deep navy (for launch / countdown posts)
BG_PURPLE   = "#5B5EA6"   # CampusClip brand purple
ACCENT      = "#6C63FF"   # vivid purple accent
TEXT_DARK   = "#1A1A2E"
TEXT_LIGHT  = "#FFFFFF"
TEXT_MUTED  = "#6B7280"
CHIP_BG     = "#EEF2FF"
CHIP_TEXT   = "#4F46E5"

W, H = 1080, 1080

# ── Helpers ────────────────────────────────────────────────────────────────

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_logo_badge(draw, img, x, y, size=56):
    """Draw a simple CampusClip logo badge (purple rounded square + CC text)."""
    badge_w, badge_h = size, size
    draw_rounded_rect(draw, [x, y, x+badge_w, y+badge_h], radius=14, fill=ACCENT)
    font = load_font(FONT_BOLD, size // 3)
    draw.text((x + size//2, y + size//2), "CC", font=font, fill=TEXT_LIGHT, anchor="mm")

def draw_wordmark(draw, x, y, size=32):
    """Draw 'CampusClip' wordmark next to badge."""
    font = load_font(FONT_BOLD, size)
    draw.text((x, y), "CampusClip", font=font, fill=ACCENT, anchor="lm")

def add_branding(draw, img, theme="light", bottom=True):
    """Add logo + wordmark to image."""
    if bottom:
        bx, by = 60, H - 90
    else:
        bx, by = 60, 48
    text_color = TEXT_LIGHT if theme == "dark" else TEXT_DARK
    draw_rounded_rect(draw, [bx - 12, by - 12, bx + 56 + 180, by + 68], radius=12,
                      fill=("#ffffff22" if theme == "dark" else "#00000010"))
    draw_logo_badge(draw, img, bx, by, size=56)
    wm_font = load_font(FONT_BOLD, 28)
    draw.text((bx + 68, by + 28), "CampusClip", font=wm_font, fill=ACCENT, anchor="lm")

def add_tag(draw, text, x, y, bg=CHIP_BG, fg=CHIP_TEXT):
    font = load_font(FONT_BOLD, 24)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    pad = 20
    draw_rounded_rect(draw, [x, y, x + tw + pad*2, y + 44], radius=22, fill=bg)
    draw.text((x + pad, y + 22), text, font=font, fill=fg, anchor="lm")

# ── Gradient background helper ─────────────────────────────────────────────

def make_gradient_bg(color_top, color_bottom):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    r0,g0,b0 = tuple(int(color_top.lstrip('#')[i:i+2],16) for i in (0,2,4))
    r1,g1,b1 = tuple(int(color_bottom.lstrip('#')[i:i+2],16) for i in (0,2,4))
    for y in range(H):
        t = y / H
        r = int(r0 + (r1-r0)*t)
        g = int(g0 + (g1-g0)*t)
        b = int(b0 + (b1-b0)*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

# ── Post templates ─────────────────────────────────────────────────────────

def post_light(filename, headline, body, tag=None, cta="link in bio"):
    """Warm off-white background post (awareness / relatable)."""
    img = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(img)

    # Subtle top stripe
    for y in range(8):
        draw.line([(0,y),(W,y)], fill=ACCENT)

    # Tag chip (optional)
    ty = 100
    if tag:
        add_tag(draw, tag, 60, ty)
        ty += 70

    # Headline
    h_font = load_font(FONT_BOLD, 72)
    lines = wrap_text(headline, h_font, W - 120, draw)
    y = ty + 20
    for line in lines[:4]:
        draw.text((60, y), line, font=h_font, fill=TEXT_DARK)
        y += 84

    # Divider
    y += 10
    draw.line([(60, y), (W-60, y)], fill=ACCENT, width=4)
    y += 30

    # Body
    b_font = load_font(FONT_REGULAR, 40)
    b_lines = wrap_text(body, b_font, W - 120, draw)
    for line in b_lines[:8]:
        draw.text((60, y), line, font=b_font, fill=TEXT_MUTED)
        y += 52

    # CTA pill
    if cta:
        cy = H - 180
        cta_font = load_font(FONT_BOLD, 30)
        bbox = draw.textbbox((0,0), cta, font=cta_font)
        cw = bbox[2]-bbox[0]
        draw_rounded_rect(draw, [60, cy, 60+cw+48, cy+52], radius=26, fill=ACCENT)
        draw.text((84, cy+26), cta, font=cta_font, fill=TEXT_LIGHT, anchor="lm")

    add_branding(draw, img, theme="light")
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

def post_dark(filename, headline, body, tag=None, cta="link in bio"):
    """Deep navy dark post (launch / countdown)."""
    img = make_gradient_bg("#1A1A2E", "#0F0F1A")
    draw = ImageDraw.Draw(img)

    # Top accent line
    draw_rounded_rect(draw, [60, 60, 180, 68], radius=4, fill=ACCENT)

    ty = 120
    if tag:
        add_tag(draw, tag, 60, ty, bg="#ffffff22", fg=TEXT_LIGHT)
        ty += 70

    h_font = load_font(FONT_BOLD, 80)
    lines = wrap_text(headline, h_font, W - 120, draw)
    y = ty + 20
    for line in lines[:3]:
        draw.text((60, y), line, font=h_font, fill=TEXT_LIGHT)
        y += 96

    y += 16
    b_font = load_font(FONT_REGULAR, 42)
    b_lines = wrap_text(body, b_font, W - 120, draw)
    for line in b_lines[:7]:
        draw.text((60, y), line, font=b_font, fill="#CBD5E1")
        y += 56

    if cta:
        cy = H - 180
        cta_font = load_font(FONT_BOLD, 30)
        bbox = draw.textbbox((0,0), cta, font=cta_font)
        cw = bbox[2]-bbox[0]
        draw_rounded_rect(draw, [60, cy, 60+cw+48, cy+52], radius=26, fill=ACCENT)
        draw.text((84, cy+26), cta, font=cta_font, fill=TEXT_LIGHT, anchor="lm")

    add_branding(draw, img, theme="dark")
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

def post_meme(filename, top_text, bottom_text):
    """Two-panel meme style."""
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Top half
    draw_rounded_rect(draw, [40, 40, W-40, H//2-20], radius=24, fill=CHIP_BG)
    t_font = load_font(FONT_BOLD, 52)
    t_lines = wrap_text(top_text, t_font, W-160, draw)
    ty = 120
    for line in t_lines[:5]:
        draw.text((W//2, ty), line, font=t_font, fill=TEXT_DARK, anchor="mm")
        ty += 66

    # Bottom half
    draw_rounded_rect(draw, [40, H//2+20, W-40, H-140], radius=24, fill="#EEF2FF")
    b_font = load_font(FONT_BOLD, 52)
    b_lines = wrap_text(bottom_text, b_font, W-160, draw)
    by = H//2 + 100
    for line in b_lines[:5]:
        draw.text((W//2, by), line, font=b_font, fill=ACCENT, anchor="mm")
        by += 66

    add_branding(draw, img, theme="light")
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

def post_quote(filename, quote, attribution, subtext=""):
    """Large quote card — testimonial style."""
    img = make_gradient_bg("#F9F7FF", "#EEF2FF")
    draw = ImageDraw.Draw(img)

    # Big quotation mark
    qfont = load_font(FONT_BOLD, 200)
    draw.text((50, 20), "“", font=qfont, fill="#DDD8FF")

    # Quote text
    q_font = load_font(FONT_BOLD, 64)
    lines = wrap_text(quote, q_font, W - 120, draw)
    y = 220
    for line in lines[:5]:
        draw.text((60, y), line, font=q_font, fill=TEXT_DARK)
        y += 80

    # Attribution
    y += 20
    draw.line([(60, y), (200, y)], fill=ACCENT, width=3)
    y += 20
    a_font = load_font(FONT_BOLD, 34)
    draw.text((60, y), attribution, font=a_font, fill=ACCENT)

    if subtext:
        y += 50
        s_font = load_font(FONT_REGULAR, 36)
        s_lines = wrap_text(subtext, s_font, W-120, draw)
        for line in s_lines[:4]:
            draw.text((60, y), line, font=s_font, fill=TEXT_MUTED)
            y += 48

    add_branding(draw, img, theme="light")
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

def post_countdown(filename, number, unit, subtext, theme="dark"):
    """Big countdown number post."""
    if theme == "dark":
        img = make_gradient_bg("#1A1A2E", "#0F0F1A")
        draw = ImageDraw.Draw(img)
        num_color = TEXT_LIGHT
        sub_color = "#CBD5E1"
    else:
        img = Image.new("RGB", (W, H), BG_LIGHT)
        draw = ImageDraw.Draw(img)
        num_color = TEXT_DARK
        sub_color = TEXT_MUTED

    # Accent strip
    draw_rounded_rect(draw, [60, 60, 180, 70], radius=4, fill=ACCENT)

    # Big number
    n_font = load_font(FONT_BOLD, 260)
    draw.text((W//2, 420), str(number), font=n_font, fill=ACCENT, anchor="mm")

    # Unit
    u_font = load_font(FONT_BOLD, 72)
    draw.text((W//2, 580), unit.upper(), font=u_font, fill=num_color, anchor="mm")

    # Subtext
    s_font = load_font(FONT_REGULAR, 40)
    s_lines = wrap_text(subtext, s_font, W-180, draw)
    y = 680
    for line in s_lines[:5]:
        draw.text((W//2, y), line, font=s_font, fill=sub_color, anchor="mm")
        y += 52

    add_branding(draw, img, theme=theme)
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

def post_launch(filename, headline, body):
    """High-energy launch day post."""
    img = make_gradient_bg("#4F46E5", "#7C3AED")
    draw = ImageDraw.Draw(img)

    # Glow circles (decorative)
    for cx, cy, r, a in [(900,150,300,30),(150,900,200,20)]:
        overlay = Image.new("RGBA", (W,H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(255,255,255,a))
        img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
        draw = ImageDraw.Draw(img)

    h_font = load_font(FONT_BOLD, 100)
    lines = wrap_text(headline, h_font, W-120, draw)
    y = 180
    for line in lines[:3]:
        draw.text((60, y), line, font=h_font, fill=TEXT_LIGHT)
        y += 116

    y += 16
    b_font = load_font(FONT_REGULAR, 44)
    b_lines = wrap_text(body, b_font, W-120, draw)
    for line in b_lines[:7]:
        draw.text((60, y), line, font=b_font, fill="#E0E7FF")
        y += 58

    # CTA
    cy2 = H - 180
    cta_font = load_font(FONT_BOLD, 32)
    cta = "link in bio ↓"
    bbox = draw.textbbox((0,0), cta, font=cta_font)
    cw = bbox[2]-bbox[0]
    draw_rounded_rect(draw, [60, cy2, 60+cw+48, cy2+56], radius=28, fill="#FFFFFF")
    draw.text((84, cy2+28), cta, font=cta_font, fill=ACCENT, anchor="lm")

    add_branding(draw, img, theme="dark")
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

def post_checklist(filename, title, items, cta="link in bio"):
    """Checklist style carousel slide (renders as single summary card)."""
    img = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, [0, 0, W, 12], radius=0, fill=ACCENT)

    t_font = load_font(FONT_BOLD, 58)
    t_lines = wrap_text(title, t_font, W-120, draw)
    y = 80
    for line in t_lines[:2]:
        draw.text((60, y), line, font=t_font, fill=TEXT_DARK)
        y += 72

    y += 20
    i_font = load_font(FONT_REGULAR, 38)
    b_font = load_font(FONT_BOLD, 38)
    for item in items[:8]:
        # Tick circle
        draw.ellipse([60, y, 100, y+40], outline=ACCENT, width=3)
        draw.text((80, y+20), "✓", font=load_font(FONT_BOLD, 28), fill=ACCENT, anchor="mm")
        i_lines = wrap_text(item, i_font, W-180, draw)
        for j, line in enumerate(i_lines[:2]):
            draw.text((120, y + j*44), line, font=i_font, fill=TEXT_DARK)
        y += max(52, len(i_lines)*44 + 12)

    if cta:
        cy = H - 160
        cta_font = load_font(FONT_BOLD, 30)
        bbox = draw.textbbox((0,0), cta, font=cta_font)
        cw = bbox[2]-bbox[0]
        draw_rounded_rect(draw, [60, cy, 60+cw+48, cy+52], radius=26, fill=ACCENT)
        draw.text((84, cy+26), cta, font=cta_font, fill=TEXT_LIGHT, anchor="lm")

    add_branding(draw, img, theme="light")
    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  ✓ {filename}")

# ── Generate all posts ─────────────────────────────────────────────────────

print("\n🎨 Generating CampusClip Instagram posts...\n")

# === AUGUST PRE-LAUNCH ===

print("── August Pre-Launch ──")

post_light(
    "aug01_6apps.png",
    "you have 6 apps open and still don't know when your midterm is",
    "canvas. google cal. your notes app. the group chat you're searching through. instagram dms. another group chat.\n\nwe made an app for this.",
    tag="coming September",
    cta="follow so you don't miss it"
)

post_light(
    "aug04_groupchat.png",
    "the group chat is not a calendar",
    '"wait when is the project due"\n"idk check canvas"\n"canvas doesn\'t have it"\n"wasn\'t it in the syllabus"\n"which syllabus"\n\nthis is a problem we\'re fixing.',
    tag="CampusClip · September · Western"
)

post_quote(
    "aug05_quote.png",
    "my whole university life was just there",
    "Beta user, Western University",
    "She scanned her syllabus. Joined her classes. Saw her classmates. Checked her grade. All in one place. CampusClip launches at Western this September."
)

post_light(
    "aug11_onestepbehind.png",
    '"I stopped feeling one step behind"',
    "that's the goal. not to be more productive. not to optimise your study habits. just to not feel scattered.\n\nCampusClip. launching at Western this September.",
    cta="follow for updates"
)

post_countdown(
    "aug07_25days.png",
    25, "days",
    "The students who download CampusClip in the first week are going to have a very different year. Western University · September 2026.",
    theme="light"
)

post_meme(
    "aug08_returning.png",
    "returning to Western ✓",
    "going back to your 6-app situation ✗\n\nCampusClip. September. Western."
)

post_countdown(
    "aug14_18days.png",
    18, "days",
    "then it all starts — new classes, new syllabuses, new group chats. this year is different. CampusClip launches at Western from day one.",
    theme="dark"
)

# === COUNTDOWN ===

print("\n── Final Countdown ──")

post_countdown(
    "aug15_4days.png",
    4, "days",
    "CampusClip launches at Western on August 19th. if you're a Western student, this is the one app you want on your phone before September.",
    theme="dark"
)

post_light(
    "aug17_wishihadit.png",
    '"I wish I had this in first year"',
    "not in a productivity-hack way. in a 'my whole semester is just there' way.\n\ndrops tomorrow.",
    cta="follow now"
)

post_dark(
    "aug18_tomorrow.png",
    "tomorrow.",
    "CampusClip is live at Western University tomorrow.\n\ndownload it. add your classes. photograph your syllabus.\n\nyour September just got easier.\n\n🔔 turn on notifications.",
    cta=""
)

# === LAUNCH DAY ===

print("\n── Launch Day ──")

post_launch(
    "aug19_launch.png",
    "it's live.",
    "CampusClip is now available at Western University.\n\ndownload it. photograph your syllabus. join your classes.\n\nyour classmates are already in there."
)

post_dark(
    "aug20_day2.png",
    "yesterday [X] Western students decided to stop feeling scattered.",
    "your class is in here. your semester is organised. your grade is calculated.\n\nstill not on it?",
    cta="link in bio"
)

# === LAUNCH AFTERMATH ===

print("\n── Launch Aftermath ──")

post_dark(
    "aug22_3daysin.png",
    "3 days in.",
    "[X] Western students have already uploaded their syllabus.\n[X] class pages are live.\n\nyour classmates are in there. the longer you wait, the more you miss.",
    cta="link in bio"
)

post_light(
    "aug24_gradetracker.png",
    "do you actually know what grade you need on your final exam?",
    "not an estimate. the exact number.\n\nCampusClip calculates it automatically based on your syllabus weights and marks so far.\n\nyou'll never go into an exam not knowing what you need. ever.",
    cta="link in bio"
)

post_meme(
    "aug25_orientation.png",
    "me at orientation without CampusClip:\n6 apps open, no idea what's happening",
    "me at orientation with CampusClip:\ncalm. organised. already found two clubs.\n\nlink in bio → right panel"
)

post_light(
    "aug27_classmate.png",
    "somewhere in your lecture there's a person who would be your best study partner.",
    "you won't find them on Canvas.\nyou won't find them on Instagram.\nyou'd have to sit next to them three times before you'd even ask their name.\n\nor you could just open CampusClip, join the class, and see everyone in there already.",
    cta="link in bio"
)

post_checklist(
    "aug28_checklist.png",
    "your first week of semester checklist",
    [
        "Download CampusClip before first class",
        "Add all your courses (60 seconds)",
        "Photograph every syllabus as you get it",
        "Join your class feeds — find your classmates",
        "Browse campus clubs and events",
        "Set your grade targets for each course",
    ]
)

post_light(
    "aug29_weekend.png",
    "enjoy this weekend.",
    "next weekend you'll be back at Western, pretending you don't have three syllabuses to read.\n\nwe'll be there when you're ready.",
    cta="downloads take 20 seconds"
)

post_countdown(
    "aug30_twosleeps.png",
    2, "sleeps",
    "do one thing today: download CampusClip. that's it.\nyou can do the rest when your syllabus is in your hand.",
    theme="dark"
)

post_dark(
    "aug31_tomorrow.png",
    "tomorrow it starts.",
    "new classes. new syllabuses. new people in your lectures you've never met.\n\nthis year you don't have to figure it out by week 6.\n\ndownload CampusClip tonight. walk in tomorrow ready.",
    cta="link in bio"
)

# === SEPTEMBER ===

print("\n── September: Week 1 ──")

post_launch(
    "sep01_firstday.png",
    "first day.",
    "you're going to get 4 syllabuses today.\n\nphotograph each one in CampusClip the moment you get it.\n\nby tonight, your entire semester is organised."
)

post_light(
    "sep03_studygroup.png",
    "raise your hand if you've been in a class for three weeks and still don't know anyone's name.",
    "CampusClip fixes this.\n\njoin your class in the app and your classmates are right there — no awkward Instagram search, no waiting until someone makes a group chat.\n\nyour study group is in there. go find them.",
    cta="link in bio"
)

post_meme(
    "sep04_week1meme.png",
    "without CampusClip:\n6 apps · 3 group chats · no idea what's due · already behind",
    "with CampusClip:\none app · semester organised · know my classmates · know my grade targets"
)

post_light(
    "sep05_weekend.png",
    "surviving your first week of semester deserves recognition.",
    "while you're recovering this weekend, your CampusClip is sitting there with your entire semester already organised.\n\nno Sunday anxiety about what's due Monday.\n\nyou're welcome 🎓",
    cta="link in bio if you haven't downloaded yet"
)

post_light(
    "sep07_week2.png",
    "week 2.",
    "by now you've seen your syllabuses. you know what this semester looks like.\n\nthe students who scanned theirs into CampusClip already know every due date, every exam, and exactly what grade they need on each one.\n\nare you one of them?",
    cta="still not too late → link in bio"
)

print("\n── September: Week 2 ──")

post_light(
    "sep08_clubs.png",
    "clubs at Western don't come to you.",
    "you have to find them — and orientation week is basically the only time they're visible.\n\nCampusClip shows you what clubs are on campus, what they're about, and when they're meeting.\n\nno more missing the thing you would have actually loved.",
    cta="link in bio"
)

post_meme(
    "sep09_groupchatgrief.png",
    "the four stages of group chat grief:\n1. 'someone add me'\n2. 47 messages about when to meet\n3. assignment reminder buried in memes",
    '4. "wait that was due TODAY"\n\nCampusClip replaces this with a class feed that actually works.'
)

post_light(
    "sep11_gradecheck.png",
    "quick question:",
    "right now, today, do you know your weighted grade in each of your classes?\n\nnot what Canvas shows. your actual grade based on the assignments you've gotten back.\n\nif the answer is no — that's the problem CampusClip solves.",
    cta="link in bio"
)

post_light(
    "sep14_twoweeks.png",
    "two weeks in.",
    "if you feel organised: good. you're ahead.\n\nif you feel scattered: download CampusClip. scan your syllabuses. it's genuinely not too late to fix this.",
    cta="link in bio"
)

print("\n── September: Week 3 ──")

post_light(
    "sep15_firstassignment.png",
    "the first assignment of the semester is coming.",
    "do you know exactly what it's worth?\nexactly what you need to get to stay on track for your target grade?\nwho in your class you can study with before it's due?\n\nCampusClip has all three.",
    cta="link in bio"
)

post_meme(
    "sep16_assignmentmeme.png",
    "the assignment is due in 3 days.\nnotes in one app. rubric on Canvas.\nstudy group in 3 different iMessage threads.",
    "or:\n\nCampusClip.\n\nlink in bio."
)

post_checklist(
    "sep17_gradetracker_how.png",
    "how CampusClip's grade tracker works",
    [
        "photograph your syllabus → weights auto-populate",
        "enter your mark as you get assignments back",
        "CampusClip calculates your weighted grade",
        "set a target grade — see what you need on every assessment",
        "always know where you stand. no surprises in December.",
    ],
    cta="link in bio"
)

post_light(
    "sep18_weekendreminder.png",
    "weekend reminder:",
    "the assignments you have due next week are already in your CampusClip calendar.\n\nno Sunday-night panic trying to remember what's coming up.\n\njust open the app. you already know.",
    cta="link in bio if you want this for your semester"
)

post_light(
    "sep21_threeweeks.png",
    "three weeks in.",
    "by now you either feel on top of your semester or you don't.\n\nif you don't: the problem is solvable. one app. 15 minutes. your whole semester gets organised.\n\nif you do: tell your friends. someone in your class needs this.",
    cta="link in bio"
)

print("\n── September: Week 4 (Midterms) ──")

post_dark(
    "sep22_midtermscoming.png",
    "midterms are coming.",
    "in 2–3 weeks most Western students will be in full panic mode — scrambling to figure out their grade, what they need to score, and whether they have time to bring it up.\n\nthe students who set up CampusClip in week 1 already know all of this. they've known since September 1st.",
    cta="link in bio · still helps"
)

post_checklist(
    "sep23_midtermprep.png",
    "midterm prep in CampusClip",
    [
        "Check grade tracker — your exact current grade",
        "Check midterm weight — is it 20%? 35%? Changes everything",
        "Check what you need to score to hit your target",
        "Post in class feed — find a study group now",
        "Check what else is due same week as your midterm",
    ],
    cta="link in bio — midterm command centre"
)

post_light(
    "sep24_studygroup.png",
    "the best study groups don't form in week 6.",
    "they form in week 2.\n\nthe students who joined their class feeds on CampusClip early already have their study groups sorted.\n\nif you haven't found yours yet — go to your class page right now. post 'anyone want to study for the midterm.'\n\nsomeone will respond.",
    cta="link in bio"
)

post_meme(
    "sep25_midtermmeme.png",
    "week 4 without CampusClip:\n'do you know what the midterm is worth'\n'no idea check the syllabus'\n'which syllabus'",
    "week 4 with CampusClip:\nopen app → grade tracker → midterm is 30% → you need 68% → close app"
)

post_dark(
    "sep28_midtermweek.png",
    "midterm week.",
    "you either know your numbers or you don't.\n\nfor everyone who knows: good luck. you're ready.\n\nfor everyone who doesn't: CampusClip is still here. at least go into your midterms knowing what you need.\n\nit's better than going in blind.",
    cta="link in bio"
)

post_dark(
    "sep30_onemonth.png",
    "one month in.",
    "if you've been on CampusClip since September 1 — you've had your grades calculated, your classes organised, and your semester in one place.\n\nif you still haven't: October is a great time to start. the second half of the semester is harder.\n\nyou've still got time.",
    cta="link in bio"
)

print(f"\n✅ Done! {len(os.listdir(OUTPUT_DIR))} posts saved to launch/posts/")
print(f"   Open the folder: {OUTPUT_DIR}")
