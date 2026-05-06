#!/usr/bin/env python3
"""
CampusClip AI Content Generator — called by GitHub Actions.
Usage: python3 run_ai_generation.py [images|lifestyle|product|emotional|all]

App UI reference (from real screenshots):
- Background: deep navy blue (#0A1628)
- Header: CampusClip graduation-cap logo (blue square, rounded) + white wordmark
  Bell, mail, profile avatar icons top-right
- Academic Performance card: light blue glassmorphism card, two circular rings
  (grey ring = current %, orange gradient ring = target %)
- Class cards: rounded corners, lighter navy, course-code badge top-left,
  bold course name, professor name, email, Grade + N/A pill bottom-right
- Bottom nav: Dashboard | Feed | Calendar | Clubs | Search | Profile (6 tabs, icon+label)
- Clubs: blue/purple gradient "Create Club" button, orange "Join" buttons
- Feed: social post cards with like/comment counts
"""
import os, sys, time, urllib.request, base64
from pathlib import Path
import replicate

BATCH = sys.argv[1] if len(sys.argv) > 1 else "images"

Path("ai-images").mkdir(exist_ok=True)
Path("ai-videos").mkdir(exist_ok=True)

SCREENSHOTS_DIR = Path("app-screenshots")
GITHUB_RAW = (
    "https://raw.githubusercontent.com/JamesYoung111/marketingskills/"
    "claude/group-skills-employees-9rORY/launch/app-screenshots"
)

def screenshot_url(filename):
    """Return GitHub raw URL for a screenshot (used as Kling start_image)."""
    return f"{GITHUB_RAW}/{filename}"

def screenshot_exists(filename):
    return (SCREENSHOTS_DIR / filename).exists()

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
    grad_h = int(h * 0.40)
    for i in range(grad_h):
        alpha = int(210 * (i / grad_h) ** 1.3)
        y = h - grad_h + i
        draw.rectangle([(0, y), (w, y + 1)], fill=(8, 18, 38, alpha))

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
    base_y = h - grad_h + int(grad_h * 0.1)

    font_brand   = load_font(int(w * 0.075))
    font_feature = load_font(int(w * 0.052))
    font_sub     = load_font(int(w * 0.038), bold=False)
    font_cta     = load_font(int(w * 0.038))

    # CampusClip wordmark — electric blue
    draw.text((pad, base_y), "CampusClip", fill=(91, 158, 248, 255), font=font_brand)

    # Feature name
    draw.text((pad, base_y + int(w * 0.095)), feature_name, fill=(255, 255, 255, 240), font=font_feature)

    # Headline
    draw.text((pad, base_y + int(w * 0.160)), headline, fill=(180, 205, 245, 210), font=font_sub)

    # CTA pill button
    btn_y = h - int(h * 0.085)
    btn_w = int(w * 0.72)
    btn_h = int(h * 0.060)
    draw.rounded_rectangle([(pad, btn_y), (pad + btn_w, btn_y + btn_h)], radius=btn_h // 2, fill=(64, 64, 242, 220))
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


# ── Style suffix ──────────────────────────────────────────────────────────────
STYLE = (
    "cinematic lighting, ultra-detailed, 8K resolution, "
    "social media ad quality, vibrant colors, professional photography, "
    "sharp focus, hyperrealistic"
)

# ── Real UI description (consistent across prompts) ───────────────────────────
APP_UI = (
    "The phone screen shows the real CampusClip app: deep navy blue background (#0A1628), "
    "header bar with a blue square graduation-cap logo and white 'CampusClip' wordmark on the left, "
    "bell and mail icons and a circular profile avatar on the right. "
    "Bottom navigation bar with six labeled tabs: Dashboard, Feed, Calendar, Clubs, Search, Profile. "
)

DASHBOARD_UI = (
    APP_UI +
    "The main screen shows 'Your Academic Performance' on a lighter navy glassmorphism card "
    "with two circular ring charts — a grey ring showing '0% CURRENT AVERAGE' and an orange "
    "gradient ring showing '80% TARGET GOAL'. Below that, 'My Classes' section with two cards: "
    "one labeled 'MOS-2228B Introduction to Managerial Accounting, Robert Pilling, CPA, CA' "
    "and one 'EC2156B Economics of Trade Unions and Labour, Evan Sauve'. "
    "Each card has a course-code badge, Grade label, and N/A pill button. "
)

CLASS_UI = (
    APP_UI +
    "The screen shows a class detail page for 'Introduction to Managerial Accounting — MOS-2228B'. "
    "Three metric tiles show CURRENT 0% Overall, TARGET 80% Goal (green), REQUIRED 80% Edit (orange). "
    "Tab bar with Assignments (active, blue), Chat, Classmates tabs. "
    "Below that, an Exams section with 'Final Exam' card showing 'Date is passed' purple badge, "
    "weight 40%, and a green Pending status bar. "
)

CLUBS_UI = (
    APP_UI +
    "The Clubs screen has a blue-to-purple gradient '+ Create Club' button at the top. "
    "'My Clubs' section lists Investment Club (Admin crown badge, 1 member) and "
    "Sigma Chi with ΣX logo (Member badge, 3 members). "
    "'Discover Clubs' section shows Western Finance Club (5 members, orange Join button) "
    "and other clubs with Follow and orange Join buttons. "
)

FEED_UI = (
    APP_UI +
    "The Feed screen shows social post cards from clubs: Sigma Chi posted with the ΣX logo, "
    "'less than a minute ago', 'Private' purple badge, post text and an attached image. "
    "Below the image are like (heart) and comment icons with counts. "
    "Investment Club post visible below saying 'Hello'. "
)

CALENDAR_UI = (
    APP_UI +
    "The Calendar screen shows 'April 2026' in large bold white text, subtitle 'Track your academic journey' "
    "in lighter blue. Navigation arrows and 'Today' button in the top right. "
    "A full monthly calendar grid (SUN through SAT columns), today (April 2, Thursday) highlighted "
    "with a blue rounded square and an orange dot below it. Other days have small blue dots indicating events. "
    "Below the calendar: 'APRIL 2026' label, 'Apr 2, 2026' in very large bold white text, "
    "and an event card showing 'Group Case Assignment' with an orange dot, 'MOS-2228B' course code, "
    "and a clock icon with '8:00 PM'. "
)

SEARCH_UI = (
    APP_UI +
    "The Search/Explore screen: teal compass icon and bold 'Explore' header, "
    "subtitle 'Discover your campus community' in green. "
    "A search bar 'Search students' and 'Select School' dropdown below. "
    "'Trending Students' section with a trending arrow icon, 'View more' in green: "
    "a 2x2 grid of student cards — James Young @jamesyoung11, chandni solanki @Student, "
    "Chandni Solanki @sdsdsdsd, Adrian Berezin @Drin — each with profile photo and username. "
    "'Popular Clubs' section below with pink icon: Harry's Sports Club (sports) and Sig Chi at Western (ΣX teal logo). "
)

PROFILE_UI = (
    APP_UI +
    "The Profile screen shows a student profile card: circular 'J' avatar, 'James Young' bold name, "
    "'@jamessyoung93' handle, '3 posts  •  0 followers  •  1 following' stats row, "
    "'2nd Year  •  BMOS - Finance' and 'Western University' below. "
    "'Edit Profile' and friend-add icon buttons. "
    "Tab bar: Posts (active, blue background), Classes, Clubs. "
    "Below: empty state with grid icon and 'No posts yet — Share your first post to get started!' "
)


# ── Image prompts — all 8 real screens represented ───────────────────────────
IMAGES = [
    {
        "file": "ai-images/img_01_dashboard_hero.png",
        "feature": "Grade Tracker",
        "headline": "Your academic performance. At a glance.",
        "caption": "Know your grades in real time 📊",
        "prompt": (
            "Extreme close-up hero product shot of an iPhone 16 Pro tilted at a slight angle, "
            "screen precisely showing the CampusClip app dashboard: " + DASHBOARD_UI +
            "Beautiful bokeh university library in the background, warm amber light streaming "
            "through tall windows. Apple product photography aesthetic. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_02_grade_rings_glow.png",
        "feature": "Academic Performance",
        "headline": "Set your target. Track every mark.",
        "caption": "Your goals on one screen 🎯",
        "prompt": (
            "Dramatic macro close-up of an iPhone screen showing the CampusClip "
            "Academic Performance card: deep navy blue (#0A1628) background, "
            "two large circular ring charts side by side — "
            "left ring is grey showing '0%' with green label 'CURRENT AVERAGE' below, "
            "right ring is orange gradient showing '80%' with label 'TARGET GOAL'. "
            "Both rings have a subtle neon glow. CampusClip graduation-cap logo at top of screen. "
            "Soft specular highlight on screen glass. Student hands barely visible at edges, "
            "cozy warm desk lamp bokeh behind. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_03_calendar_deadline.png",
        "feature": "Deadline Calendar",
        "headline": "Track your academic journey.",
        "caption": "Every deadline. Every time. Never missed. 🗓️",
        "prompt": (
            "Close-up of iPhone screen held by a student, showing: " + CALENDAR_UI +
            "The calendar is crisp and sharp. Student sitting at a wooden university desk, "
            "textbooks open beside them, warm study lamp light, "
            "late afternoon golden light through window. Authentic, candid. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_04_calendar_lifestyle.png",
        "feature": "Deadline Calendar",
        "headline": "April 2026. Every deadline. Covered.",
        "caption": "Deadlines don't sneak up anymore 🔔",
        "prompt": (
            "iPhone 16 Pro floating at a dynamic angle, screen showing: " + CALENDAR_UI +
            "Deep navy blue background with soft blue particle bokeh. "
            "Orange and blue accent lighting matching the calendar's event dots. "
            "Apple-style dramatic product photography, rim lighting. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_05_explore_community.png",
        "feature": "Explore",
        "headline": "Discover your campus community.",
        "caption": "Trending students. Popular clubs. All at Western. 🔍",
        "prompt": (
            "iPhone screen held in a student's hand, showing: " + SEARCH_UI +
            "The teal Explore compass icon and green subtitle are vivid. "
            "Student walking through a busy campus quad, "
            "other students visible in the background. Candid, dynamic lifestyle shot. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_06_clubs_screen.png",
        "feature": "Clubs & Communities",
        "headline": "Investment Club. Sigma Chi. Find yours.",
        "caption": "Every Western club. One place. 🏫",
        "prompt": (
            "iPhone 16 Pro floating at an angle, screen showing: " + CLUBS_UI +
            "Deep midnight blue background, subtle purple bokeh, "
            "orange accent lighting matching the Join buttons, "
            "blue accent matching the Create Club gradient. Apple-style product photography. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_07_profile_identity.png",
        "feature": "Your Student Profile",
        "headline": "2nd Year. BMOS - Finance. Western University.",
        "caption": "Made for Western students. By Western students. 🎓",
        "prompt": (
            "iPhone screen showing: " + PROFILE_UI +
            "The profile card is beautifully lit. Student holding phone confidently, "
            "standing outside Western University's iconic University College building, "
            "gothic stone architecture, warm afternoon light. "
            "Pride in their identity as a Western student. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_08_hero_product.png",
        "feature": "CampusClip",
        "headline": "One app. Your whole campus.",
        "caption": "Everything Western. One app. Free. 📱",
        "prompt": (
            "iPhone 16 Pro in titanium finish floating against deep navy blue background, "
            "screen showing the CampusClip dashboard: " + DASHBOARD_UI +
            "Dramatic Apple product photography, electric blue rim light from left, "
            "subtle orange rim light from right matching the target ring, "
            "background has soft particle bokeh. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_09_before_after.png",
        "feature": "Stop the Chaos",
        "headline": "Before CampusClip. After CampusClip.",
        "caption": "No more deadline panic. Ever. 😮‍💨",
        "prompt": (
            "Perfect editorial split-screen composition: "
            "LEFT HALF — moody red-orange tones, stressed student at chaotic desk, "
            "scattered papers, crossed-out planner, multiple missed assignment alerts, "
            "overwhelmed expression. "
            "RIGHT HALF — calm navy blue tones, same student relaxed and smiling, "
            "iPhone showing CampusClip dashboard with the Academic Performance rings "
            "and organised class cards. Clean desk. "
            "Perfect symmetry. Graphic editorial style. " + STYLE
        ),
    },
    {
        "file": "ai-images/img_10_success.png",
        "feature": "Organised Students Succeed",
        "headline": "Start organised. Graduate proud.",
        "caption": "Organised students graduate differently 🎓",
        "prompt": (
            "University graduate in cap and gown holding diploma triumphantly overhead, "
            "brilliant smile, campus quad in golden hour, confetti mid-air. "
            "Phone in other hand showing CampusClip — the Academic Performance card "
            "with both rings now filled and glowing, a notification overlay reading "
            "'Dean's List — Congratulations 🎉' on the navy CampusClip interface. "
            "Cinematic, emotional, aspirational. " + STYLE
        ),
    },
]

# ── Video prompts — with start_image support ──────────────────────────────────
LIFESTYLE_VIDEOS = [
    {
        "file": "ai-videos/v01_dashboard_walkthrough.mp4",
        "caption": "Your academic life. One screen. 📱",
        "duration": 5,
        "start_image": "screenshot_01_dashboard.png",
        "prompt": (
            "Starting from the CampusClip dashboard on an iPhone — navy blue app with "
            "graduation-cap logo, two circular grade rings (grey CURRENT AVERAGE, orange TARGET GOAL), "
            "and class cards for MOS-2228B and EC2156B below. "
            "A student's thumb scrolls down slowly. Camera gradually pulls back to reveal "
            "a stylish student sitting on campus steps checking their grades. "
            "Warm golden hour light, cinematic, like an Apple ad."
        ),
    },
    {
        "file": "ai-videos/v02_calendar_reveal.mp4",
        "caption": "Every deadline. Automatically tracked. 🗓️",
        "duration": 5,
        "start_image": "screenshot_06_calendar.png",
        "prompt": (
            "Starting from the CampusClip Calendar screen — 'April 2026, Track your academic journey', "
            "monthly calendar with blue dot indicators on assignment days, "
            "today (April 2) highlighted with blue rounded square and orange dot. "
            "Below the calendar: 'Group Case Assignment — MOS-2228B — 8:00 PM' event card. "
            "A finger taps April 15 (a day with a blue dot) — a new event card slides up smoothly. "
            "Student at desk, relieved expression. Cinematic, satisfying UI animation."
        ),
    },
    {
        "file": "ai-videos/v03_explore_community.mp4",
        "caption": "Discover your campus community 🔍",
        "duration": 5,
        "start_image": "screenshot_07_search.png",
        "prompt": (
            "Starting from the CampusClip Explore screen — teal compass icon, "
            "'Discover your campus community' in green, Trending Students grid showing "
            "James Young @jamesyoung11 and others, Popular Clubs below with Harry's Sports Club "
            "and Sig Chi at Western. "
            "A finger scrolls down through Trending Students, then taps Sig Chi at Western. "
            "Camera pulls back to reveal a student on campus, smiling as they explore. "
            "Vibrant, social, community energy. Cinematic."
        ),
    },
]

PRODUCT_VIDEOS = [
    {
        "file": "ai-videos/v04_grade_rings_animate.mp4",
        "caption": "Set your goal. Watch your grades climb 📊",
        "duration": 5,
        "start_image": "screenshot_01_dashboard.png",
        "prompt": (
            "Extreme macro close-up of iPhone screen showing the CampusClip Academic Performance card. "
            "The grey 'CURRENT AVERAGE' ring starts at 0% and animates clockwise, filling to 87% in blue. "
            "The percentage number ticks upward: 0%... 34%... 67%... 87%. "
            "The orange 'TARGET GOAL' ring pulses with a warm glow. "
            "Deeply satisfying animation, dark navy background, screen fills the frame entirely. "
            "Apple product aesthetic, cinematic macro lens, soft screen reflection."
        ),
    },
    {
        "file": "ai-videos/v05_calendar_deadline_demo.mp4",
        "caption": "Never miss a deadline again 🔔",
        "duration": 5,
        "start_image": "screenshot_06_calendar.png",
        "prompt": (
            "Close-up of iPhone screen showing CampusClip Calendar — April 2026 grid, "
            "blue dot indicators on assignment days, today highlighted. "
            "Below: 'Group Case Assignment • MOS-2228B • 8:00 PM' event card with orange dot. "
            "A phone notification slides down from top: '⏰ Assignment due tomorrow — MOS-2228B'. "
            "Student hand visible picking up phone from nightstand, soft morning light. "
            "Satisfying, reassuring, cinematic."
        ),
    },
    {
        "file": "ai-videos/v06_join_club.mp4",
        "caption": "Your club is waiting. Tap to join. 🤝",
        "duration": 5,
        "start_image": "screenshot_03_clubs.png",
        "prompt": (
            "iPhone screen showing CampusClip Clubs page with Investment Club, Sigma Chi ΣX, "
            "and Discover Clubs section with Western Finance Club and orange 'Join' button. "
            "A finger taps the orange 'Join' button — it flashes with a satisfying animation, "
            "Western Finance Club slides up to 'My Clubs' with a smooth transition. "
            "Student smiles in background bokeh, warm cafe lighting. Cinematic product demo."
        ),
    },
]

EMOTIONAL_VIDEOS = [
    {
        "file": "ai-videos/v07_transformation.mp4",
        "caption": "Everything changes when you're organised 🙌",
        "duration": 5,
        "prompt": (
            "Emotional transformation story. Scene 1: stressed student at chaotic desk, "
            "scattered papers, multiple missed deadlines, overwhelmed expression, red alarm. "
            "Cut to: the same student calm, phone showing CampusClip dashboard — "
            "navy blue app with two organised circular rings, class cards neatly listed. "
            "Their posture relaxes, they smile. Room mood shifts from harsh to warm blue. "
            "Cinematic cross-dissolve, like a productivity app commercial."
        ),
    },
    {
        "file": "ai-videos/v08_campus_confidence.mp4",
        "caption": "Your campus. Your app. Your era. 🍂",
        "duration": 10,
        "start_image": "screenshot_01_dashboard.png",
        "prompt": (
            "Stylish student walking confidently through Western University campus in autumn. "
            "Gothic stone buildings, maple leaves falling in golden hour. "
            "She glances at iPhone showing CampusClip dashboard — the Academic Performance card "
            "shows rings, her classes listed clearly. She smiles and walks taller. "
            "Camera tracks alongside at shoulder level, slow-motion moments. "
            "Cinematic, aspirational, iPhone commercial feel. 24fps, anamorphic bokeh."
        ),
    },
    {
        "file": "ai-videos/v09_graduation.mp4",
        "caption": "Organised students graduate differently 🎓",
        "duration": 10,
        "prompt": (
            "Emotional slow-motion university graduation. Graduate walks across stage, "
            "receives diploma, raises it overhead — pure joy, crowd cheers. "
            "Cut to: phone showing CampusClip — 'CURRENT AVERAGE' ring now filled and glowing, "
            "'Congratulations — Dean's List 🎉' notification on navy background with the "
            "CampusClip graduation-cap logo. "
            "Confetti falls in golden sunlight, caps fly. Cinematic, emotional, swelling energy."
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

    input_data = {
        "prompt": item["prompt"],
        "duration": item.get("duration", 5),
        "aspect_ratio": "9:16",
        "cfg_scale": 0.5,
    }

    # Use real screenshot as starting frame if available
    screenshot_file = item.get("start_image")
    if screenshot_file and screenshot_exists(screenshot_file):
        img_url = screenshot_url(screenshot_file)
        input_data["start_image"] = img_url
        print(f"  using start_image: {img_url}", flush=True)
    elif screenshot_file:
        print(f"  note: {screenshot_file} not found in app-screenshots/ — generating without start frame", flush=True)

    out = run_with_retry("kwaivgi/kling-v1-6-pro", input_data)
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
