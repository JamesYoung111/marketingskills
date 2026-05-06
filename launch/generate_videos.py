#!/usr/bin/env python3
"""
CampusClip Video Generator
Produces animated MP4s for TikTok, Instagram Reels, and Stories.
Output: launch/videos/  (9:16, 1080x1920)
"""

import os, math, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS  = 24

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# ── Brand palette ─────────────────────────────────────────────────────────────
DARK_BG   = (10,  22,  40)
CARD_BG   = (21,  34,  72)
GRAD_A    = np.array([91,  158, 248], dtype=np.float32)   # #5B9EF8
GRAD_B    = np.array([64,  64,  242], dtype=np.float32)   # #4040F2
GRAD_A_T  = (91,  158, 248)
GRAD_B_T  = (64,  64,  242)
MID_BLUE  = (77,  111, 245)
ORANGE    = (245, 158, 11)
WHITE     = (255, 255, 255)
OFF_WHITE = (210, 228, 255)
DIM_BLUE  = (120, 150, 220)

OUT = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(OUT, exist_ok=True)


# ── Easing ────────────────────────────────────────────────────────────────────
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def prog(t, start, end):
    if end <= start: return 1.0
    return max(0.0, min(1.0, (t - start) / (end - start)))


# ── Gradient builders (numpy, fast) ───────────────────────────────────────────
_X = np.linspace(0, 1, W, dtype=np.float32)
_Y = np.linspace(0, 1, H, dtype=np.float32)
_XX, _YY = np.meshgrid(_X, _Y)
_DIAG = (_XX + _YY) / 2   # shape (H, W)


def gradient_bg(offset=0.0, dark_mix=0.0):
    t = np.clip(_DIAG + offset, 0, 1)[:, :, np.newaxis]
    rgb = GRAD_A * (1 - t) + GRAD_B * t
    if dark_mix > 0:
        dark = np.array(DARK_BG, dtype=np.float32)
        rgb = rgb * (1 - dark_mix) + dark * dark_mix
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))


def dark_glow_bg(glow_strength=0.4):
    arr = np.full((H, W, 3), DARK_BG, dtype=np.float32)
    r = np.sqrt((_XX - 0.5) ** 2 + (_YY - 0.5) ** 2 * 0.6)
    glow = np.clip(1 - r * 1.5, 0, 1) * glow_strength
    glow = glow[:, :, np.newaxis]
    glow_color = np.array(MID_BLUE, dtype=np.float32)
    arr = arr * (1 - glow) + glow_color * glow
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def split_bg(top_frac=0.45):
    """Gradient top half, dark bottom half."""
    arr = np.full((H, W, 3), DARK_BG, dtype=np.float32)
    top_h = int(H * top_frac)
    t = np.clip(_DIAG[:top_h], 0, 1)[:, :, np.newaxis]
    grad_top = GRAD_A * (1 - t) + GRAD_B * t
    arr[:top_h] = grad_top
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ── Font & text helpers ───────────────────────────────────────────────────────
def fnt(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def text_size(text, size, bold=True):
    f = fnt(size, bold)
    dummy = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(dummy)
    bb = d.textbbox((0, 0), text, font=f)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_centered(img, text, cy, size, color, bold=True, opacity=1.0, wrap_px=940):
    """Render centered, word-wrapped text onto img (RGBA or RGB)."""
    f = fnt(size, bold)
    # Word-wrap to fit wrap_px
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        tw, _ = text_size(test, size, bold)
        if tw > wrap_px and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))

    line_h = size + int(size * 0.2)
    total_h = len(lines) * line_h
    base_y = cy - total_h // 2

    for i, line in enumerate(lines):
        tw, _ = text_size(line, size, bold)
        x = (W - tw) // 2
        y = base_y + i * line_h
        if opacity < 0.999 or isinstance(img, Image.Image) and img.mode == "RGBA":
            if img.mode != "RGBA":
                img_rgba = img.convert("RGBA")
            else:
                img_rgba = img
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            a = int(opacity * 255)
            ld.text((x, y), line, font=f, fill=(*color, a))
            img_rgba.alpha_composite(layer)
            if img.mode != "RGBA":
                img.paste(img_rgba.convert("RGB"))
        else:
            d = ImageDraw.Draw(img)
            d.text((x, y), line, font=f, fill=color)

    return img


def draw_left(img, text, x, cy, size, color, bold=True, opacity=1.0):
    f = fnt(size, bold)
    if opacity < 0.999:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((x, cy), text, font=f, fill=(*color, int(opacity * 255)))
        if img.mode != "RGBA":
            tmp = img.convert("RGBA")
            tmp.alpha_composite(layer)
            img.paste(tmp.convert("RGB"))
        else:
            img.alpha_composite(layer)
    else:
        d = ImageDraw.Draw(img)
        d.text((x, cy), text, font=f, fill=color)


# ── Shape helpers ─────────────────────────────────────────────────────────────
def pill_gradient(w, h):
    """Returns (img, mask) for a gradient-filled pill."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for i in range(w):
        t = i / max(w - 1, 1)
        c = tuple(int(GRAD_A[j] + (GRAD_B[j] - GRAD_A[j]) * t) for j in range(3))
        d.line([(i, 0), (i, h)], fill=c)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, w, h], radius=h // 2, fill=255)
    return img, mask


def paste_pill(bg, cx, cy, w, h, label, label_size=38):
    pill, mask = pill_gradient(w, h)
    x, y = cx - w // 2, cy - h // 2
    bg.paste(pill, (x, y), mask=mask)
    draw_centered(bg, label, cy, label_size, WHITE, bold=True)


def draw_logo(bg, cx, cy, size=90):
    """Gradient badge + white graduation cap + white envelope."""
    s = size
    badge = Image.new("RGB", (s, s))
    bd = ImageDraw.Draw(badge)
    for i in range(s):
        t = i / max(s - 1, 1)
        c = tuple(int(GRAD_A[j] + (GRAD_B[j] - GRAD_A[j]) * t) for j in range(3))
        bd.line([(0, i), (s, i)], fill=c)
    badge_mask = Image.new("L", (s, s), 0)
    bm = ImageDraw.Draw(badge_mask)
    bm.rounded_rectangle([0, 0, s, s], radius=s // 5, fill=255)
    bx, by = cx - s // 2, cy - s // 2
    bg.paste(badge, (bx, by), mask=badge_mask)

    draw = ImageDraw.Draw(bg)
    cap_cx, cap_cy = cx, cy - s // 9
    hw, hh = s // 3, s // 7
    draw.polygon([
        (cap_cx, cap_cy - hh),
        (cap_cx + hw, cap_cy),
        (cap_cx, cap_cy + hh),
        (cap_cx - hw, cap_cy),
    ], fill=WHITE)

    env_x = cx - s // 4
    env_y = cy + s // 9
    env_w = s // 2
    env_h = s // 3
    draw.rounded_rectangle([env_x, env_y, env_x + env_w, env_y + env_h], radius=3, fill=WHITE)
    mid = tuple(int((GRAD_A[j] + GRAD_B[j]) / 2) for j in range(3))
    draw.polygon([
        (env_x, env_y),
        (env_x + env_w // 2, env_y + env_h // 2),
        (env_x + env_w, env_y),
    ], fill=mid)


def draw_card(draw, x, y, w, h, radius=24, color=CARD_BG, alpha=200):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=color)


def draw_checkmark(draw, cx, cy, r, color):
    d = r * 0.6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    draw.line([(cx - d * 0.5, cy), (cx - d * 0.1, cy + d * 0.4),
               (cx + d * 0.5, cy - d * 0.3)], fill=WHITE, width=max(2, int(r * 0.25)))


def make_video(filename, make_frame_fn, duration):
    path = os.path.join(OUT, filename)
    clip = VideoClip(make_frame_fn, duration=duration)
    clip.write_videofile(path, fps=FPS, codec="libx264",
                         audio=False, logger=None,
                         ffmpeg_params=["-crf", "20", "-preset", "fast"])
    print(f"  ✓ {filename}")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 1 — Launch Hero  (30s)
# Hook: "Your campus. Organised." → features reveal → CTA
# ══════════════════════════════════════════════════════════════════════════════
def make_launch_hero():
    features = [
        ("📚", "Syllabus Scanner"),
        ("📊", "Grade Tracker"),
        ("🏫", "Class Communities"),
        ("📅", "Deadline Calendar"),
        ("🎉", "Events & Clubs"),
    ]

    def frame(t):
        # Background slowly shifts gradient offset
        offset = math.sin(t * 0.4) * 0.1
        bg = gradient_bg(offset=offset, dark_mix=0.15)

        # ─ Logo (fades in 0→1s) ─
        logo_alpha = ease_out(prog(t, 0.0, 0.8))
        if logo_alpha > 0.01:
            draw_logo(bg, W // 2, 280, size=100)
            draw_centered(bg, "CampusClip", 400, 52, WHITE, opacity=logo_alpha)
            draw_centered(bg, "Western University", 465, 30, OFF_WHITE, bold=False, opacity=logo_alpha * 0.8)

        # ─ Main hook (slides up 1→2.5s) ─
        hook_p = ease_out(prog(t, 1.0, 2.5))
        if hook_p > 0.01:
            y_off = int(60 * (1 - hook_p))
            # Draw big headline
            draw_centered(bg, "Your campus.", 700 - y_off, 96, WHITE, opacity=hook_p)
            draw_centered(bg, "Organised.", 810 - y_off, 96, WHITE, opacity=hook_p)

        # ─ Tagline (fades 2.5→3.5s) ─
        tag_p = ease_out(prog(t, 2.5, 3.5))
        if tag_p > 0.01:
            draw_centered(bg, "The all-in-one platform for Western students",
                          930, 34, OFF_WHITE, bold=False, opacity=tag_p)

        # ─ Features appear one by one (4→18s) ─
        if t > 4.0:
            draw = ImageDraw.Draw(bg)
            feat_start_y = 1000
            feat_spacing = 110
            for i, (icon, label) in enumerate(features):
                feat_t_start = 4.0 + i * 2.2
                feat_p = ease_out(prog(t, feat_t_start, feat_t_start + 0.9))
                if feat_p < 0.01:
                    continue
                fy = feat_start_y + i * feat_spacing
                x_off = int(40 * (1 - feat_p))
                # Card bg
                card_a = int(feat_p * 180)
                card_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                cd = ImageDraw.Draw(card_img)
                cd.rounded_rectangle([80 + x_off, fy, W - 80 + x_off, fy + 88],
                                     radius=20, fill=(*CARD_BG, card_a))
                bg.paste(card_img.convert("RGB"), mask=card_img.split()[3])

                # Icon circle
                draw.ellipse([105 + x_off, fy + 16, 161 + x_off, fy + 72],
                             fill=MID_BLUE)
                icon_f = fnt(28)
                ib = ImageDraw.Draw(bg).textbbox((0, 0), icon, font=icon_f)
                draw_left(bg, icon, 116 + x_off, fy + 24, 28, WHITE, opacity=feat_p)
                draw_left(bg, label, 180 + x_off, fy + 24, 34, WHITE, bold=True, opacity=feat_p)

        # ─ CTA (fades 20→21.5s) ─
        cta_p = ease_out(prog(t, 20.0, 21.5))
        if cta_p > 0.01:
            paste_pill(bg, W // 2, 1800, 560, 88, "Download Free — August 2026", label_size=34)

        return np.array(bg)

    make_video("01_launch_hero.mp4", frame, 30)


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 2 — Syllabus Scan Demo  (20s)
# Hook → phone mockup → grade tracker reveal → CTA
# ══════════════════════════════════════════════════════════════════════════════
def make_syllabus_demo():
    PHONE_W, PHONE_H = 480, 780
    PHONE_X = (W - PHONE_W) // 2
    PHONE_Y = 580

    def draw_phone_frame(bg):
        draw = ImageDraw.Draw(bg)
        draw.rounded_rectangle([PHONE_X - 10, PHONE_Y - 10,
                                 PHONE_X + PHONE_W + 10, PHONE_Y + PHONE_H + 10],
                                radius=48, fill=(30, 45, 75))
        draw.rounded_rectangle([PHONE_X, PHONE_Y, PHONE_X + PHONE_W, PHONE_Y + PHONE_H],
                                radius=38, fill=DARK_BG)

    def draw_scan_progress(bg, scan_pct):
        draw = ImageDraw.Draw(bg)
        # "Scanning syllabus" header
        draw_centered(bg, "Scanning Syllabus...", PHONE_Y + 60, 28, OFF_WHITE)
        # Progress bar
        bar_x, bar_y = PHONE_X + 40, PHONE_Y + 120
        bar_w, bar_h = PHONE_W - 80, 10
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                                radius=5, fill=CARD_BG)
        fill_w = int(bar_w * scan_pct)
        if fill_w > 0:
            draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
                                    radius=5, fill=GRAD_A_T)
        pct_text = f"{int(scan_pct * 100)}%"
        draw_centered(bg, pct_text, PHONE_Y + 160, 36, WHITE)

        # Scrolling "document lines"
        for row in range(8):
            line_y = PHONE_Y + 220 + row * 44
            opacity = max(0, 1 - abs(row - 3) / 4) * min(1, scan_pct * 2)
            line_w = int((PHONE_W - 80) * (0.6 + (row % 3) * 0.15))
            line_col = int(opacity * 80)
            draw.rounded_rectangle([PHONE_X + 40, line_y, PHONE_X + 40 + line_w, line_y + 8],
                                    radius=4, fill=(line_col, line_col + 30, line_col + 80))

    def draw_results(bg, appear_p):
        draw = ImageDraw.Draw(bg)
        draw_centered(bg, "✓ Done! Found:", PHONE_Y + 50, 28, GRAD_A_T)

        items = [
            ("12", "Assignments"),
            ("3",  "Midterms"),
            ("1",  "Final Exam"),
            ("6",  "Projects"),
        ]
        for i, (num, label) in enumerate(items):
            p = ease_out(prog(appear_p, i * 0.15, i * 0.15 + 0.5))
            iy = PHONE_Y + 140 + i * 130
            card_a = int(p * 200)
            c_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            cd = ImageDraw.Draw(c_img)
            cx1 = PHONE_X + 30
            cd.rounded_rectangle([cx1, iy, cx1 + PHONE_W - 60, iy + 100],
                                  radius=16, fill=(*CARD_BG, card_a))
            bg.paste(c_img.convert("RGB"), mask=c_img.split()[3])
            draw_centered(bg, num, iy + 30, 42, GRAD_A_T, opacity=p)
            draw_centered(bg, label, iy + 75, 22, OFF_WHITE, bold=False, opacity=p)

    def frame(t):
        bg = dark_glow_bg(glow_strength=0.5)

        # ─ Hook text (0→3s) ─
        hook_p = ease_out(prog(t, 0.0, 1.0))
        fade_out = 1 - ease_in_out(prog(t, 2.5, 3.5))
        h_op = hook_p * fade_out

        if h_op > 0.01:
            draw_centered(bg, "scan your syllabus", 350, 76, WHITE, opacity=h_op)
            draw_centered(bg, "in 30 seconds.", 460, 76, WHITE, opacity=h_op)
            draw_centered(bg, "Every deadline. Auto-added.", 570, 38,
                          OFF_WHITE, bold=False, opacity=h_op * 0.85)

        # ─ Phone appears (3→5s) ─
        phone_p = ease_out(prog(t, 3.0, 4.5))
        if phone_p > 0.01:
            draw_phone_frame(bg)

            if t < 11.0:
                # Scanning animation (4→11s)
                scan_raw = prog(t, 4.0, 10.0)
                scan_p = ease_in_out(scan_raw) * phone_p
                draw_scan_progress(bg, scan_p)
            else:
                # Results (11→18s)
                res_p = ease_out(prog(t, 11.0, 13.0))
                draw_results(bg, res_p)

        # ─ Sub-text (12→15s) ─
        sub_p = ease_out(prog(t, 12.0, 13.5))
        if sub_p > 0.01:
            draw_centered(bg, "All added to your deadline calendar", 1450, 34,
                          OFF_WHITE, bold=False, opacity=sub_p)
            draw_centered(bg, "automatically.", 1500, 34,
                          OFF_WHITE, bold=False, opacity=sub_p)

        # ─ CTA (17→20s) ─
        cta_p = ease_out(prog(t, 17.0, 18.5))
        if cta_p > 0.01:
            paste_pill(bg, W // 2, 1800, 520, 88, "Try CampusClip Free →", label_size=36)

        # Logo in corner
        draw_logo(bg, W - 90, 80, size=70)

        return np.array(bg)

    make_video("02_syllabus_demo.mp4", frame, 20)


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 3 — Stat Reveal  (15s)
# "70% of students miss a deadline" counter → solution reveal
# ══════════════════════════════════════════════════════════════════════════════
def make_stat_reveal():
    def frame(t):
        bg = dark_glow_bg(glow_strength=0.6)
        draw = ImageDraw.Draw(bg)

        # ─ Set-up line (0→1.5s) ─
        setup_p = ease_out(prog(t, 0.0, 1.2))
        fade_setup = 1 - ease_in_out(prog(t, 5.0, 6.5))
        if setup_p * fade_setup > 0.01:
            draw_centered(bg, "Real talk.", 400, 68, OFF_WHITE, opacity=setup_p * fade_setup)

        # ─ Stat number counts up (1.5→5s) ─
        stat_p = prog(t, 1.5, 5.0)
        fade_stat = 1 - ease_in_out(prog(t, 6.0, 7.0))
        if stat_p > 0 and fade_stat > 0:
            num = int(ease_in_out(stat_p) * 70)
            num_text = f"{num}%"
            draw_centered(bg, num_text, 850, 240, WHITE, opacity=fade_stat)
            label_p = ease_out(prog(t, 2.5, 3.5))
            if label_p > 0.01:
                draw_centered(bg, "of Western students", 1040, 46,
                              OFF_WHITE, bold=False, opacity=label_p * fade_stat)
                draw_centered(bg, "miss at least one deadline per semester",
                              1110, 40, DIM_BLUE, bold=False, opacity=label_p * fade_stat)

        # ─ Divider (5s) ─
        div_p = ease_out(prog(t, 5.0, 6.0))
        if div_p > 0.01:
            div_w = int(400 * div_p)
            x0 = W // 2 - div_w // 2
            draw.rounded_rectangle([x0, 900, x0 + div_w, 906], radius=3, fill=GRAD_A_T)

        # ─ Solution (7→12s) ─
        sol_p = ease_out(prog(t, 7.0, 8.5))
        if sol_p > 0.01:
            draw_centered(bg, "CampusClip sees every", 500, 68, WHITE, opacity=sol_p)
            draw_centered(bg, "deadline before you do.", 590, 68, WHITE, opacity=sol_p)

        sol2_p = ease_out(prog(t, 8.5, 10.0))
        if sol2_p > 0.01:
            items = ["Auto-parsed from your syllabus",
                     "Synced to your calendar",
                     "Smart reminders, 3 days early"]
            for i, item in enumerate(items):
                ip = ease_out(prog(t, 8.5 + i * 0.6, 9.0 + i * 0.6))
                check_x = 160
                check_y = 720 + i * 100
                if ip > 0.01:
                    draw_checkmark(draw, check_x, check_y + 20, 22, GRAD_A_T)
                    draw_left(bg, item, check_x + 50, check_y, 34, OFF_WHITE, opacity=ip)

        # ─ CTA (12→15s) ─
        cta_p = ease_out(prog(t, 12.0, 13.5))
        if cta_p > 0.01:
            paste_pill(bg, W // 2, 1800, 560, 88, "Never miss a deadline →", label_size=36)

        draw_logo(bg, W - 90, 80, size=70)
        return np.array(bg)

    make_video("03_stat_reveal.mp4", frame, 15)


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 4 — Feature Reel  (25s)
# 5 features, each gets 4s — fast-cut energy
# ══════════════════════════════════════════════════════════════════════════════
def make_feature_reel():
    sections = [
        ("Syllabus Scanner",    "Drop your PDF. Every deadline auto-imported.",
         GRAD_A_T,   0.0),
        ("Grade Tracker",       "Know exactly where you stand in every class.",
         GRAD_B_T,   4.5),
        ("Class Communities",   "Study groups that actually exist.",
         MID_BLUE,   9.0),
        ("Events & Clubs",      "Everything happening on campus, in one place.",
         GRAD_A_T,   13.5),
        ("Deadline Calendar",   "24-hr warnings. Never surprised. Ever.",
         ORANGE,     18.0),
    ]

    def frame(t):
        # Find current section
        cur_sec = None
        for (title, body, accent, start) in reversed(sections):
            if t >= start:
                cur_sec = (title, body, accent, start)
                break

        if cur_sec is None:
            cur_sec = sections[0]

        title, body, accent, start = cur_sec
        sec_t = t - start
        sec_dur = 4.5

        # Transition offset for gradient
        sec_idx = next(i for i, s in enumerate(sections) if s[3] == start)
        bg_offset = sec_idx * 0.2 + math.sin(sec_t * 0.8) * 0.05
        bg = gradient_bg(offset=bg_offset, dark_mix=0.2)
        draw = ImageDraw.Draw(bg)

        # ─ Progress dots ─
        for i in range(len(sections)):
            dot_x = W // 2 - (len(sections) - 1) * 30 + i * 60
            dot_y = 200
            if i == sec_idx:
                draw.ellipse([dot_x - 10, dot_y - 6, dot_x + 10, dot_y + 6],
                             fill=WHITE)
            else:
                draw.ellipse([dot_x - 6, dot_y - 6, dot_x + 6, dot_y + 6],
                             fill=(100, 130, 200))

        # ─ Accent bar ─
        bar_p = ease_out(prog(sec_t, 0.0, 0.5))
        bar_w = int(180 * bar_p)
        draw.rounded_rectangle([W//2 - bar_w//2, 660, W//2 + bar_w//2, 672],
                                radius=3, fill=accent)

        # ─ Title slides up ─
        title_p = ease_out(prog(sec_t, 0.1, 0.7))
        fade_out = 1 - ease_in_out(prog(sec_t, sec_dur - 0.8, sec_dur - 0.2))
        op = title_p * fade_out
        if op > 0.01:
            draw_centered(bg, title, 780, 86, WHITE, opacity=op)

        # ─ Body fades in ─
        body_p = ease_out(prog(sec_t, 0.5, 1.2))
        if body_p * fade_out > 0.01:
            draw_centered(bg, body, 900, 42, OFF_WHITE, bold=False,
                          opacity=body_p * fade_out)

        # ─ Section number ─
        draw_left(bg, f"{sec_idx + 1}/{len(sections)}", 80, 180, 28, DIM_BLUE, bold=False)

        # Logo
        draw_logo(bg, W - 90, 80, size=70)

        # ─ Final CTA (23→25s) ─
        if t > 23.0:
            cta_p = ease_out(prog(t, 23.0, 24.0))
            paste_pill(bg, W // 2, 1800, 580, 88, "All this. Free. August 2026.", label_size=36)
            draw_centered(bg, "CampusClip", 1700, 38, WHITE, opacity=cta_p)

        return np.array(bg)

    make_video("04_feature_reel.mp4", frame, 25)


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 5 — Before/After  (18s)
# "Before CampusClip" chaos vs "After" clarity
# ══════════════════════════════════════════════════════════════════════════════
def make_before_after():
    before_chaos = [
        "Missed the lab quiz 😭",
        "When was the midterm again?",
        "I have 3 things due tomorrow??",
        "Which prof posted the notes?",
        "Did I submit that?",
    ]
    after_wins = [
        "Deadline calendar auto-filled ✓",
        "Smart reminders 3 days early ✓",
        "One app. Every class. ✓",
        "Notes synced to community ✓",
        "Grade on track: 87% ✓",
    ]

    def frame(t):
        bg = dark_glow_bg(glow_strength=0.5)
        draw = ImageDraw.Draw(bg)

        phase = "before" if t < 8.5 else "transition" if t < 10.5 else "after"

        if phase in ("before", "transition"):
            fade_out = 1 - ease_in_out(prog(t, 8.0, 10.5))

            header_p = ease_out(prog(t, 0.0, 1.0)) * fade_out
            draw_centered(bg, "Sound familiar? 😬", 300, 62, WHITE, opacity=header_p)
            draw_centered(bg, "Every semester...", 380, 38,
                          DIM_BLUE, bold=False, opacity=header_p * 0.8)

            for i, text in enumerate(before_chaos):
                ip = ease_out(prog(t, 0.5 + i * 0.9, 1.3 + i * 0.9)) * fade_out
                if ip < 0.01:
                    continue
                y = 520 + i * 140
                x_off = int(50 * (1 - ip))
                c_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                cd = ImageDraw.Draw(c_img)
                cd.rounded_rectangle([60 + x_off, y, W - 60 + x_off, y + 100],
                                     radius=18, fill=(120, 30, 40, int(ip * 180)))
                bg.paste(c_img.convert("RGB"), mask=c_img.split()[3])
                draw_centered(bg, text, y + 30, 34, WHITE, opacity=ip)

        if phase in ("transition", "after"):
            t2 = t - 10.5
            pop_p = ease_out(prog(t, 10.5, 11.8))
            if pop_p > 0.01:
                draw_centered(bg, "There's a better way.", 460, 76, WHITE, opacity=pop_p)
                draw_centered(bg, "CampusClip changes everything.", 560, 42,
                              OFF_WHITE, bold=False, opacity=pop_p * 0.9)

            for i, text in enumerate(after_wins):
                ip = ease_out(prog(t, 11.5 + i * 0.7, 12.3 + i * 0.7))
                if ip < 0.01:
                    continue
                y = 700 + i * 140
                c_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                cd = ImageDraw.Draw(c_img)
                cd.rounded_rectangle([60, y, W - 60, y + 100], radius=18,
                                     fill=(*CARD_BG, int(ip * 200)))
                bg.paste(c_img.convert("RGB"), mask=c_img.split()[3])
                draw_checkmark(draw, 120, y + 50, 22, GRAD_A_T)
                draw_left(bg, text, 160, y + 25, 34, WHITE, bold=True, opacity=ip)

        # CTA (16→18s)
        cta_p = ease_out(prog(t, 16.0, 17.2))
        if cta_p > 0.01:
            paste_pill(bg, W // 2, 1800, 560, 88, "Download Free — Aug 2026", label_size=36)

        draw_logo(bg, W - 90, 80, size=70)
        return np.array(bg)

    make_video("05_before_after.mp4", frame, 18)


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO 6 — Grade Tracker  (15s)
# Animated grade ring counting up
# ══════════════════════════════════════════════════════════════════════════════
def make_grade_tracker():
    def draw_ring(bg, cx, cy, r, pct, track_col, fill_col, num_str, label):
        draw = ImageDraw.Draw(bg)
        thick = 28
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=270, fill=track_col, width=thick)
        sweep = pct * 360
        if sweep > 0.5:
            draw.arc([cx - r, cy - r, cx + r, cy + r],
                     start=-90, end=-90 + sweep, fill=fill_col, width=thick)
        draw_centered(bg, num_str, cy - 10, 56, WHITE)
        draw_centered(bg, label, cy + 55, 24, DIM_BLUE, bold=False)

    def frame(t):
        bg = gradient_bg(dark_mix=0.5)
        draw = ImageDraw.Draw(bg)

        hook_p = ease_out(prog(t, 0.0, 1.0))
        fade = 1 - ease_in_out(prog(t, 3.5, 4.5))
        if hook_p * fade > 0.01:
            draw_centered(bg, "Know your grade.", 350, 80, WHITE, opacity=hook_p * fade)
            draw_centered(bg, "Before it's too late.", 450, 80, WHITE, opacity=hook_p * fade)

        # Grade rings appear
        ring_p = ease_out(prog(t, 4.0, 6.5))
        courses = [
            ("CS 2211",  0.87, GRAD_A_T,  "87%"),
            ("MATH 1600", 0.72, ORANGE,    "72%"),
            ("BIOL 1290", 0.91, GRAD_B_T,  "91%"),
        ]
        ring_r = 110
        ring_spacing = 320
        start_x = W // 2 - ring_spacing
        ring_y = 900

        for i, (course, target_pct, color, label) in enumerate(courses):
            ip = ease_out(prog(t, 4.0 + i * 0.8, 5.5 + i * 0.8))
            if ip < 0.01:
                continue
            cx = start_x + i * ring_spacing
            pct = ease_in_out(min(ip * 1.3, 1.0)) * target_pct
            num_disp = f"{int(pct * 100)}%"
            draw_ring(bg, cx, ring_y, ring_r, pct, CARD_BG, color, num_disp, course)

        # GPA reveal
        gpa_p = ease_out(prog(t, 8.0, 9.5))
        if gpa_p > 0.01:
            gpa_val = ease_in_out(prog(t, 8.0, 10.5)) * 3.7
            draw_centered(bg, f"GPA: {gpa_val:.1f}", 1140, 72, WHITE, opacity=gpa_p)
            draw_centered(bg, "Updated after every grade entry",
                          1230, 32, DIM_BLUE, bold=False, opacity=gpa_p * 0.8)

        # CTA
        cta_p = ease_out(prog(t, 12.0, 13.2))
        if cta_p > 0.01:
            paste_pill(bg, W // 2, 1800, 560, 88, "Track Your GPA Free →", label_size=36)

        draw_logo(bg, W - 90, 80, size=70)
        return np.array(bg)

    make_video("06_grade_tracker.mp4", frame, 15)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("CampusClip Video Generator")
    print(f"Output → {OUT}/\n")

    videos = [
        ("01_launch_hero.mp4    30s  Launch announcement",    make_launch_hero),
        ("02_syllabus_demo.mp4  20s  Syllabus scan walkthru", make_syllabus_demo),
        ("03_stat_reveal.mp4    15s  '70% miss a deadline'",  make_stat_reveal),
        ("04_feature_reel.mp4   25s  5-feature fast reel",    make_feature_reel),
        ("05_before_after.mp4   18s  Before/After CampusClip",make_before_after),
        ("06_grade_tracker.mp4  15s  Animated grade rings",   make_grade_tracker),
    ]

    for desc, fn in videos:
        print(f"Rendering {desc} ...")
        fn()

    print(f"\nDone! 6 videos saved to {OUT}/")
    print("Specs: 1080×1920 (9:16) · H.264 · 24fps · no audio")
    print("\nNext step: add a trending audio track in CapCut before posting.")
