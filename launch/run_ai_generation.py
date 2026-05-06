#!/usr/bin/env python3
"""
CampusClip AI Content Generator — called by GitHub Actions.
Usage: python3 run_ai_generation.py [images|lifestyle|product|emotional|all]
"""
import os, sys, time, urllib.request
from pathlib import Path
import replicate

BATCH = sys.argv[1] if len(sys.argv) > 1 else "images"

Path("ai-images").mkdir(exist_ok=True)
Path("ai-videos").mkdir(exist_ok=True)

def download(url, path):
    urllib.request.urlretrieve(str(url), path)
    print(f"  saved -> {path}", flush=True)

def run_with_retry(model, input_data, retries=4):
    for attempt in range(retries):
        try:
            return replicate.run(model, input=input_data)
        except Exception as e:
            if "429" in str(e) or "throttled" in str(e).lower():
                wait = 60 * (attempt + 1)
                print(f"  Rate limited — waiting {wait}s before retry {attempt+1}/{retries}...", flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Failed after {retries} retries")


def add_branding_overlay(img_path, feature_name, headline, cta="Free Download · August 2026"):
    """Composite CampusClip branding onto a generated image using PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  PIL not available, skipping overlay", flush=True)
        return

    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Dark gradient at bottom third
    grad_h = int(h * 0.42)
    for i in range(grad_h):
        alpha = int(215 * (i / grad_h) ** 1.4)
        y = h - grad_h + i
        draw.rectangle([(0, y), (w, y + 1)], fill=(8, 18, 38, alpha))

    # Try system fonts, fallback gracefully
    def load_font(size, bold=True):
        candidates = [
            f"/usr/share/fonts/truetype/dejavu/DejaVuSans-{'Bold' if bold else ''}.ttf",
            f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    pad = int(w * 0.075)
    base_y = h - grad_h + int(grad_h * 0.12)

    # CampusClip wordmark — electric blue
    font_brand = load_font(int(w * 0.075))
    draw.text((pad, base_y), "CampusClip", fill=(91, 158, 248, 255), font=font_brand)

    # Feature name — white
    font_feature = load_font(int(w * 0.052))
    draw.text((pad, base_y + int(w * 0.095)), feature_name, fill=(255, 255, 255, 240), font=font_feature)

    # Headline — soft blue-white
    font_sub = load_font(int(w * 0.038), bold=False)
    draw.text((pad, base_y + int(w * 0.165)), headline, fill=(180, 205, 245, 210), font=font_sub)

    # CTA pill button
    btn_y = h - int(h * 0.085)
    btn_w = int(w * 0.72)
    btn_h = int(h * 0.062)
    draw.rounded_rectangle(
        [(pad, btn_y), (pad + btn_w, btn_y + btn_h)],
        radius=btn_h // 2,
        fill=(64, 64, 242, 220),
    )
    font_cta = load_font(int(w * 0.038))
    # Center text in button
    try:
        bbox = draw.textbbox((0, 0), cta, font=font_cta)
        txt_w = bbox[2] - bbox[0]
    except Exception:
        txt_w = len(cta) * int(w * 0.022)
    draw.text(
        (pad + (btn_w - txt_w) // 2, btn_y + (btn_h - int(w * 0.045)) // 2),
        cta, fill=(255, 255, 255, 255), font=font_cta,
    )

    img = Image.alpha_composite(img, overlay).convert("RGB")
    img.save(img_path, quality=97)
    print(f"  branding overlay composited -> {img_path}", flush=True)


# ── Prompt style suffix ───────────────────────────────────────────────────────
STYLE = (
    "cinematic lighting, ultra-detailed, 8K resolution, "
    "social media ad quality, vibrant colors, professional photography, "
    "sharp focus, hyperrealistic"
)

# ── Image prompts ─────────────────────────────────────────────────────────────
# Every prompt shows CampusClip's actual UI on the phone screen.
IMAGES = [
    {
        "file": "ai-images/img_01_grade_rings.png",
        "feature": "Grade Tracker",
        "headline": "Watch your GPA update live.",
        "caption": "Know your grade before it's too late 📊",
        "prompt": (
            "Extreme close-up of an iPhone 16 Pro screen held by a student, the screen shows the "
            "CampusClip grade tracker app: dark navy background, three glowing circular progress "
            "rings — the first labeled 'CS 2211' filled 87% in electric blue, the second 'MATH 1600' "
            "at 72% in amber orange, the third 'BIOL 1290' at 91% in teal, the word 'CampusClip' "
            "in white text at the top of the screen, and a glassmorphism card showing 'Current GPA 3.7'. "
            "Shallow depth of field, university library bokeh in background, warm amber lighting. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_02_syllabus_scan.png",
        "feature": "Syllabus Scanner",
        "headline": "Drop your PDF. Every deadline saved.",
        "caption": "Every deadline. Auto-saved. 🗓️",
        "prompt": (
            "Close-up of iPhone screen showing the CampusClip app's syllabus scanner feature: "
            "a university course syllabus PDF is displayed, an animated blue progress bar sweeps "
            "across the screen, bold text reads 'Found 12 deadlines' in white, below it a clean "
            "checklist of assignments auto-populates — 'Essay #1 · Oct 14', 'Midterm · Oct 21', "
            "'Lab Report · Nov 3' — each with a blue checkbox. 'CampusClip' logo visible top-left "
            "in the app. Hands holding phone over textbooks, morning light, marble desk. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_03_deadline_alert.png",
        "feature": "Deadline Calendar",
        "headline": "3 days early. Every time.",
        "caption": "Deadlines don't sneak up anymore 🔔",
        "prompt": (
            "iPhone screen glowing in a cozy university dorm room at night, showing a CampusClip "
            "push notification: a glassmorphism card with the CampusClip logo and the text "
            "'CS 2211 Essay due in 3 days — you're on track ✓' in white on dark navy background, "
            "with a blue gradient accent. Student hand reaching for the phone, warm fairy lights "
            "and Edison bulbs in background, cozy moody atmosphere. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_04_class_community.png",
        "feature": "Class Communities",
        "headline": "Your whole class. One place.",
        "caption": "Your whole class, connected 🤝",
        "prompt": (
            "iPhone showing the CampusClip 'Class Communities' feature: a chat interface for "
            "'CS 2211 — Computer Science' with student message bubbles, one message reading "
            "'Does anyone have notes from lecture 5?', another replying 'Posted in files! 📎', "
            "a shared document thumbnail, emoji reactions, and a pinned study poll. "
            "CampusClip logo at top of screen. Four diverse students huddle around the phone "
            "in a warmly-lit campus cafe, reacting with genuine excitement. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_05_events_feed.png",
        "feature": "Events & Clubs",
        "headline": "Everything at Western. In one feed.",
        "caption": "Campus life, one app 🎉",
        "prompt": (
            "iPhone screen showing the CampusClip Events & Clubs feed: a beautiful scrollable "
            "list of campus events with colorful thumbnails — 'Engineering Networking Night 🔧', "
            "'Pre-Med Study Group 🩺', 'Western Career Fair 💼', 'Club Crawl 🎉' — each card "
            "with a vivid image, date chip, and blue 'RSVP' button. CampusClip header at top. "
            "Stylish student walking through autumn Western University campus holding phone, "
            "gothic stone buildings, golden hour maple leaves. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_06_hero_dashboard.png",
        "feature": "All-In-One Campus App",
        "headline": "Your campus, organised.",
        "caption": "Meet your campus companion 📱",
        "prompt": (
            "iPhone 16 Pro in titanium finish floating at a slight angle, screen showing the "
            "CampusClip home dashboard: dark navy background with five glassmorphism feature "
            "tiles arranged in a grid — '📚 Syllabus Scanner', '📊 Grade Tracker', "
            "'📅 Deadlines', '🏫 Communities', '🎉 Events' — each tile with a blue gradient "
            "icon, the 'CampusClip' wordmark in large white text at the top with a blue gradient "
            "logo mark. Dramatic product photography, midnight blue background, subtle particle "
            "bokeh, Apple-style rim lighting. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_07_before_after.png",
        "feature": "Stop the Chaos",
        "headline": "Everything changes when you're organised.",
        "caption": "No more deadline panic. Ever. 😮‍💨",
        "prompt": (
            "Perfect split-screen image: LEFT HALF — moody red-orange tones, stressed student "
            "at cluttered desk buried in scattered papers and sticky notes, red alert notifications "
            "on phone, overwhelmed expression, messy background; RIGHT HALF — calm cool blue tones, "
            "same student relaxed and smiling, phone showing CampusClip clean deadline list with "
            "blue checkmarks and 'All on track ✓' in white text, organized clean desk. "
            "Graphic editorial style, perfect symmetry, hyperrealistic, 8K. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_08_study_success.png",
        "feature": "Grade Tracker",
        "headline": "See every mark. Know every grade.",
        "caption": "That feeling when the grade hits different ✨",
        "prompt": (
            "Joyful 21-year-old female student mid-celebration on sunlit university steps, "
            "eyes wide with delight, fist pumped in the air. Her phone screen clearly shows "
            "the CampusClip grade tracker app: a large '91%' in blue gradient text, 'BIOL 1290 — Excellent' "
            "below it, a glowing circular ring at 91% fill. Golden hour backlight, autumn leaves "
            "falling, Western University stone architecture. Candid lifestyle, hyperrealistic, 8K. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_09_study_flatlay.png",
        "feature": "The Student Starter Pack",
        "headline": "One app. Your whole semester.",
        "caption": "Your semester starter pack 🎓",
        "prompt": (
            "Perfectly styled overhead flatlay on a white marble desk: iPhone prominently "
            "centered showing CampusClip app with blue gradient interface and the text "
            "'CampusClip — 5 deadlines this week', open MacBook Pro showing class notes, "
            "matcha latte with latte art, fresh white AirPods, Muji pens, leather notebook "
            "with 'CS 2211' tab. Magazine quality Instagram aesthetic, soft natural light, "
            "hyperrealistic, 8K. "
            + STYLE
        ),
    },
    {
        "file": "ai-images/img_10_gpa_graduation.png",
        "feature": "Organised Students Graduate Differently",
        "headline": "Start organised. Graduate proud.",
        "caption": "Organised students graduate differently 🎓",
        "prompt": (
            "University graduate in cap and gown holding diploma triumphantly overhead, "
            "brilliant smile, campus quad in golden hour, confetti mid-air. "
            "Phone in other hand clearly shows the CampusClip app: "
            "'Final GPA: 3.9 — Congratulations! 🎉' in large white text on dark navy background "
            "with blue gradient celebration animation. Cinematic aspiration, emotional, "
            "shot on RED camera, hyperrealistic, 8K. "
            + STYLE
        ),
    },
]

# ── Video prompts ─────────────────────────────────────────────────────────────
LIFESTYLE_VIDEOS = [
    {
        "file": "ai-videos/v01_campus_check.mp4",
        "caption": "Check your deadlines before your next class 📱",
        "duration": 5,
        "prompt": (
            "Cinematic tracking shot alongside a confident stylish student walking through "
            "a stunning autumn university campus at golden hour. She glances at her iPhone "
            "showing the CampusClip app — the screen shows a blue deadline list with green "
            "checkmarks. Camera slowly orbits her as she smiles at the screen. Maple leaves "
            "falling, gothic stone buildings, anamorphic bokeh, 24fps cinematic, like an Apple ad."
        ),
    },
    {
        "file": "ai-videos/v02_library_syllabus.mp4",
        "caption": "Scan your syllabus. Never miss a thing 📚",
        "duration": 5,
        "prompt": (
            "Slow dolly shot through a beautiful university library. We see a student hold up "
            "their iPhone camera to their printed syllabus. On the phone screen the CampusClip "
            "app shows a blue progress bar scanning the document, then a satisfying animation "
            "as 12 deadlines appear in a clean checklist. Student exhales with visible relief "
            "and smiles. Warm golden library light, cinematic, smooth camera motion."
        ),
    },
    {
        "file": "ai-videos/v03_group_reaction.mp4",
        "caption": "Your class is already on CampusClip 🤝",
        "duration": 5,
        "prompt": (
            "Four diverse university students burst into surprised laughter around a cafe table. "
            "One shows their phone to the group — the screen shows CampusClip class community chat "
            "with messages and shared notes from their CS class. Others lean in, reacting with "
            "genuine delight. Camera slowly orbits the group. Warm cafe Edison lighting, "
            "authentic candid energy, cinematic 35mm shallow depth of field."
        ),
    },
]

PRODUCT_VIDEOS = [
    {
        "file": "ai-videos/v04_syllabus_demo.mp4",
        "caption": "Your syllabus → every deadline in 30 seconds 📲",
        "duration": 5,
        "prompt": (
            "Elegant screen-recording style close-up of an iPhone showing the CampusClip app. "
            "A finger taps 'Scan Syllabus', the camera opens, a university course syllabus PDF "
            "appears, a blue progress bar sweeps across with a satisfying animation, then a "
            "clean list of deadlines populates: 'Essay #1 · Oct 14', 'Midterm · Oct 21'. "
            "Each item has a blue checkbox. CampusClip logo visible at top. "
            "Camera slowly pulls back to reveal phone on marble desk. Apple product aesthetic."
        ),
    },
    {
        "file": "ai-videos/v05_grade_tracker_demo.mp4",
        "caption": "Watch your GPA update in real time 📊",
        "duration": 5,
        "prompt": (
            "Macro close-up of iPhone screen showing CampusClip grade tracker. Three circular "
            "progress rings animate from 0% filling smoothly up to 87%, 72%, and 91% with "
            "glowing blue, orange, and teal arcs. Below each ring the course code appears. "
            "A GPA counter ticks upward from 2.9 to 3.7 with smooth easing. Screen shows "
            "'CampusClip' wordmark at top on dark navy background. Satisfying, clean animation, "
            "Apple UI aesthetic. Camera slowly zooms in on the screen."
        ),
    },
    {
        "file": "ai-videos/v06_notification.mp4",
        "caption": "3 days early. Every assignment. 🔔",
        "duration": 5,
        "prompt": (
            "Close-up of a student nightstand in the early morning. Phone screen gently lights up "
            "with a CampusClip notification card: blue gradient background, white text reads "
            "'CS 2211 Essay due in 3 days — You're on track ✓ · CampusClip'. "
            "A student hand slowly reaches over and picks up the phone, we see their sleepy face "
            "relax into a relieved smile in soft morning light. "
            "Camera slowly rises from nightstand level to eye level. Warm, intimate, cinematic."
        ),
    },
]

EMOTIONAL_VIDEOS = [
    {
        "file": "ai-videos/v07_transformation.mp4",
        "caption": "Everything changes when you're organised 🙌",
        "duration": 5,
        "prompt": (
            "A transformation story: student sitting at a chaotic desk covered in scattered papers, "
            "highlighted calendar, multiple missed notifications — stressed and overwhelmed. "
            "The scene dissolves to the same student at a clean desk, calm and confident, "
            "holding their phone showing the CampusClip deadline list with blue checkmarks and "
            "'All assignments on track'. Whole room mood shifts from anxious red tones to calm "
            "cool blue. Cinematic cross-dissolve, emotional, like a meditation app ad."
        ),
    },
    {
        "file": "ai-videos/v08_campus_confidence.mp4",
        "caption": "Your campus. Your app. Your era. 🍂",
        "duration": 10,
        "prompt": (
            "Stylish female student walking confidently through a stunning autumn Western University "
            "campus, gothic stone buildings in golden background, maple leaves falling. Camera tracks "
            "alongside at shoulder level. She checks her iPhone — screen shows CampusClip home "
            "dashboard with 'No deadlines due today ✓' in blue. She smiles and walks taller. "
            "Slow motion moments mixed with real-time. Cinematic, aspirational, iPhone commercial feel. "
            "24fps, anamorphic bokeh."
        ),
    },
    {
        "file": "ai-videos/v09_graduation.mp4",
        "caption": "Organised students graduate differently 🎓",
        "duration": 10,
        "prompt": (
            "Emotional slow-motion of a university graduation ceremony. Graduate walks across stage, "
            "receives diploma, turns and raises it overhead — pure joy. In their other hand, phone "
            "shows CampusClip: 'Final GPA 3.9 — Congratulations! 🎉' on a blue gradient card. "
            "Crowd cheers in slow motion, confetti falls through golden sunlight, caps fly. "
            "Camera cuts between the diploma moment and the glowing phone screen. "
            "Cinematic, emotional, swelling energy, like a university commercial."
        ),
    },
]


def gen_image(item, pause=12):
    print(f"\nGenerating image: {item['file']}", flush=True)
    out = run_with_retry(
        "black-forest-labs/flux-1.1-pro",
        {
            "prompt": item["prompt"],
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 100,
            "safety_tolerance": 2,
            "prompt_upsampling": True,
        }
    )
    download(str(out), item["file"])
    # Composite CampusClip branding on top
    add_branding_overlay(
        item["file"],
        feature_name=item.get("feature", "CampusClip"),
        headline=item.get("headline", ""),
    )
    Path(item["file"].replace(".png", ".txt")).write_text(item.get("caption", ""))
    print(f"  waiting {pause}s to respect rate limit...", flush=True)
    time.sleep(pause)


def gen_video(item, pause=15):
    print(f"\nGenerating video: {item['file']} ({item.get('duration', 5)}s)", flush=True)
    out = run_with_retry(
        "kwaivgi/kling-v1-6-pro",
        {
            "prompt": item["prompt"],
            "duration": item.get("duration", 5),
            "aspect_ratio": "9:16",
            "cfg_scale": 0.5,
        }
    )
    url = str(out) if isinstance(out, str) else str(list(out)[0])
    download(url, item["file"])
    Path(item["file"].replace(".mp4", ".txt")).write_text(item.get("caption", ""))
    print(f"  waiting {pause}s to respect rate limit...", flush=True)
    time.sleep(pause)


batches = {
    "images":    (IMAGES, []),
    "lifestyle": ([], LIFESTYLE_VIDEOS),
    "product":   ([], PRODUCT_VIDEOS),
    "emotional": ([], EMOTIONAL_VIDEOS),
    "all":       (IMAGES, LIFESTYLE_VIDEOS + PRODUCT_VIDEOS + EMOTIONAL_VIDEOS),
}

imgs, vids = batches.get(BATCH, (IMAGES, []))

if imgs:
    print(f"\n{'='*50}\nGenerating {len(imgs)} images\n{'='*50}", flush=True)
    for item in imgs:
        try:
            gen_image(item)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)

if vids:
    print(f"\n{'='*50}\nGenerating {len(vids)} video clips\n{'='*50}", flush=True)
    for item in vids:
        try:
            gen_video(item)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)

print("\nDone!", flush=True)
