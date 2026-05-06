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
import os, sys, time, urllib.request, base64, subprocess
from pathlib import Path
import replicate

BATCH = sys.argv[1] if len(sys.argv) > 1 else "images"

Path("ai-images").mkdir(exist_ok=True)
Path("ai-videos").mkdir(exist_ok=True)

SCREENSHOTS_DIR = Path("app-screenshots")

# Screenshots are on main branch with iPhone default names (IMG_XXXX.jpeg).
# This map translates our logical names to the actual uploaded filenames.
GITHUB_RAW = (
    "https://raw.githubusercontent.com/JamesYoung111/marketingskills/"
    "main/launch/app-screenshots"
)
SCREENSHOT_MAP = {
    "screenshot_01_dashboard.png":    "IMG_1617.jpeg",
    "screenshot_02_class_detail.png": "IMG_1618.jpeg",
    "screenshot_03_clubs.png":        "IMG_1619.jpeg",
    "screenshot_04_club_page.png":    "IMG_1620.jpeg",
    "screenshot_05_feed.png":         "IMG_1621.jpeg",
    "screenshot_06_calendar.png":     "IMG_1622.jpeg",
    "screenshot_07_search.png":       "IMG_1623.jpeg",
    "screenshot_08_profile.png":      "IMG_1624.jpeg",
}

def screenshot_url(logical_name):
    """Return GitHub raw URL using actual uploaded filename."""
    actual = SCREENSHOT_MAP.get(logical_name, logical_name)
    return f"{GITHUB_RAW}/{actual}"

def screenshot_exists(logical_name):
    actual = SCREENSHOT_MAP.get(logical_name, logical_name)
    return (SCREENSHOTS_DIR / actual).exists()

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


def frames_to_video(frame_files, output_path, fps=24, dur=2.8, fade=0.45):
    """Assemble PNG frames into a 9:16 MP4 with crossfade transitions via ffmpeg."""
    n = len(frame_files)
    scale = (
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
        f"fps={fps}"
    )
    parts = [f"[{i}:v]{scale}[v{i}]" for i in range(n)]
    prev = "[v0]"
    for i in range(1, n):
        offset = round(dur * i - fade * i, 3)
        label = "[out]" if i == n - 1 else f"[xf{i}]"
        parts.append(f"{prev}[v{i}]xfade=transition=fade:duration={fade}:offset={offset}{label}")
        prev = f"[xf{i}]"
    if n == 1:
        parts.append("[v0]copy[out]")

    inputs = []
    for fp in frame_files:
        inputs += ["-loop", "1", "-t", str(dur + 1), "-i", str(fp)]

    total = round(dur * n - fade * (n - 1), 2)
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", "; ".join(parts),
        "-map", "[out]",
        "-t", str(total),
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  ffmpeg error:\n{r.stderr[-1200:]}", flush=True)
        raise RuntimeError("ffmpeg assembly failed")
    print(f"  assembled {n} frames -> {output_path} ({total:.1f}s)", flush=True)


def gen_video_slideshow(item, pause=10):
    """Generate a video: 3 FLUX keyframes + ffmpeg crossfade assembly."""
    out_mp4 = item["file"]
    frames = item.get("frames", [])
    if not frames:
        print(f"  no frames defined for {out_mp4}", flush=True)
        return
    print(f"\nGenerating slideshow: {out_mp4} ({len(frames)} frames)", flush=True)
    tmp = []
    try:
        for idx, frame in enumerate(frames):
            fp = out_mp4.replace(".mp4", f"_tmp{idx}.png")
            print(f"  FLUX frame {idx+1}/{len(frames)}", flush=True)
            out = run_with_retry("black-forest-labs/flux-1.1-pro", {
                "prompt": frame["prompt"],
                "aspect_ratio": "9:16",
                "output_format": "png",
                "output_quality": 100,
                "safety_tolerance": 2,
                "prompt_upsampling": True,
            })
            download(str(out), fp)
            add_branding_overlay(fp, item.get("feature", "CampusClip"), item.get("headline", ""))
            tmp.append(fp)
            time.sleep(pause)
        frames_to_video(tmp, out_mp4)
        Path(out_mp4.replace(".mp4", ".txt")).write_text(item.get("caption", ""))
    finally:
        for fp in tmp:
            Path(fp).unlink(missing_ok=True)


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

# ── Video slideshows — 3 FLUX keyframes per video, assembled by ffmpeg ────────
# Each video = 3 frames × 2.8s + crossfades ≈ 8 seconds total
LIFESTYLE_VIDEOS = [
    {
        "file": "ai-videos/v01_grade_tracker.mp4",
        "feature": "Grade Tracker", "headline": "Watch your GPA climb.",
        "caption": "Set your goal. Watch your GPA climb 📊",
        "frames": [
            {"prompt": "iPhone 16 Pro floating against deep navy background, screen showing CampusClip app: dark navy, graduation-cap blue logo, 'Your Academic Performance' card with grey ring '0% CURRENT AVERAGE' and orange ring '80% TARGET GOAL', two class cards MOS-2228B and EC2156B below. Apple product photography, electric blue rim light. " + STYLE},
            {"prompt": "Extreme macro close-up of phone screen showing CampusClip grade tracker: two circular rings side by side, grey ring labeled 'CURRENT AVERAGE 0%' and glowing orange ring '80% TARGET GOAL', dark navy background, graduation-cap CampusClip logo at top. Soft screen glow, caustic light. " + STYLE},
            {"prompt": "Joyful 21-year-old student on sunny campus steps holding iPhone, screen shows CampusClip grade tracker with rings and '3.7 GPA' in blue gradient text, bright smile, Western University stone architecture background, golden hour. " + STYLE},
        ],
    },
    {
        "file": "ai-videos/v02_deadline_calendar.mp4",
        "feature": "Deadline Calendar", "headline": "Track your academic journey.",
        "caption": "Every deadline. Every time. Never missed. 🗓️",
        "frames": [
            {"prompt": "iPhone screen showing CampusClip calendar app: 'April 2026' header, 'Track your academic journey' subtitle, monthly grid with small blue dots on assignment days, today (April 2) highlighted with blue rounded square, orange dot below. Deep navy app background. Product shot. " + STYLE},
            {"prompt": "Close-up of phone showing CampusClip calendar event card: 'Group Case Assignment' in bold white, 'MOS-2228B' course code, clock icon '8:00 PM', orange dot indicator, dark navy glassmorphism card. Student desk, warm lamp light. " + STYLE},
            {"prompt": "Student at organized desk at night checking phone showing CampusClip calendar, all assignments listed with blue checkmarks and upcoming deadlines. Fairy lights, warm cozy dorm room, relieved expression. " + STYLE},
        ],
    },
    {
        "file": "ai-videos/v03_campus_community.mp4",
        "feature": "Explore & Clubs", "headline": "Discover your campus community.",
        "caption": "Trending students. Popular clubs. All at Western. 🔍",
        "frames": [
            {"prompt": "iPhone screen showing CampusClip Explore page: teal compass icon, 'Explore' header, 'Discover your campus community' in green, search bar, 'Trending Students' section with 2x2 grid of student profile cards. Dark navy app background. " + STYLE},
            {"prompt": "iPhone screen showing CampusClip Clubs page: 'My Clubs' section with Investment Club (Admin badge) and Sigma Chi ΣX (3 members), 'Discover Clubs' section with Western Finance Club showing orange 'Join' button. Blue gradient 'Create Club' button at top. " + STYLE},
            {"prompt": "Four diverse Western University students gathered excitedly around one iPhone in a campus cafe, screen showing CampusClip clubs page, pointing at Investment Club and Sigma Chi entries, genuine laughter, warm Edison bulb lighting. " + STYLE},
        ],
    },
]

PRODUCT_VIDEOS = [
    {
        "file": "ai-videos/v04_app_demo.mp4",
        "feature": "All-In-One App", "headline": "One app. Your whole campus.",
        "caption": "Dashboard. Calendar. Clubs. Feed. One app. 📱",
        "frames": [
            {"prompt": "iPhone 16 Pro in titanium finish on dark marble surface, screen showing CampusClip home dashboard: navy background, graduation-cap logo, Academic Performance rings, class cards. Dramatic side lighting, Apple product photography. " + STYLE},
            {"prompt": "iPhone screen split view showing CampusClip navigation: Dashboard tab active with grade rings, then Calendar tab showing April 2026 grid, then Clubs tab with Investment Club. Bottom nav bar with all 6 tabs visible. Macro lens. " + STYLE},
            {"prompt": "Student in Western University library sitting at wooden table, MacBook open, iPhone showing CampusClip dashboard — grade rings visible on screen. Warm amber light through tall windows, golden hour study session. " + STYLE},
        ],
    },
    {
        "file": "ai-videos/v05_feed_social.mp4",
        "feature": "Campus Feed", "headline": "Everything happening at Western.",
        "caption": "Your campus feed. Always live. 🏠",
        "frames": [
            {"prompt": "iPhone screen showing CampusClip Feed: social post cards from Sigma Chi (ΣX logo, 'less than a minute ago', 'Private' purple badge), post with image, like (heart) and comment icons below. Investment Club post below. Dark navy app background. " + STYLE},
            {"prompt": "Close-up of iPhone showing CampusClip club post: Sigma Chi fraternity post with attached sports graphic, 'Private' badge, engagement icons. Student thumb scrolling, warm afternoon light. " + STYLE},
            {"prompt": "Student on campus bench in afternoon sun, smiling while scrolling through CampusClip feed on iPhone showing club posts and campus updates, other students and autumn trees in background. Candid, authentic lifestyle. " + STYLE},
        ],
    },
    {
        "file": "ai-videos/v06_profile_class.mp4",
        "feature": "Your Student Profile", "headline": "2nd Year. BMOS - Finance. Western.",
        "caption": "Your classes. Your clubs. Your profile. 🎓",
        "frames": [
            {"prompt": "iPhone screen showing CampusClip Profile: 'James Young' @jamessyoung93, circular J avatar, '3 posts • 0 followers • 1 following', '2nd Year • BMOS - Finance', 'Western University', Posts/Classes/Clubs tab bar (Posts active). " + STYLE},
            {"prompt": "iPhone screen showing CampusClip class detail for 'Introduction to Managerial Accounting MOS-2228B': three metric tiles CURRENT 0%, TARGET 80% (green), REQUIRED 80% (orange), Assignments/Chat/Classmates tab bar. " + STYLE},
            {"prompt": "Confident 2nd-year finance student at Western University standing outside Ivey Business School building, holding iPhone showing CampusClip profile, proud expression, professional look. Golden afternoon light. " + STYLE},
        ],
    },
]

EMOTIONAL_VIDEOS = [
    {
        "file": "ai-videos/v07_transformation.mp4",
        "feature": "Stop the Chaos", "headline": "Before CampusClip. After CampusClip.",
        "caption": "Everything changes when you're organised 🙌",
        "frames": [
            {"prompt": "Stressed university student at chaotic desk: scattered papers, crossed-out paper planner, multiple missed deadline sticky notes everywhere, empty coffee cups, overwhelmed expression, red-orange harsh lighting. " + STYLE},
            {"prompt": "iPhone screen showing CampusClip dashboard: all deadlines organized in calendar, class cards MOS-2228B and EC2156B with upcoming assignments listed, grade rings showing progress. Clean navy interface. Calm, organized. " + STYLE},
            {"prompt": "Same student now calm and confident at clean organized desk, holding phone showing CampusClip, satisfied smile, all deadlines sorted. Warm blue soft lighting, plants, tidy space. Complete transformation. " + STYLE},
        ],
    },
    {
        "file": "ai-videos/v08_campus_era.mp4",
        "feature": "CampusClip", "headline": "Your campus. Your app. Your era.",
        "caption": "Your campus. Your app. Your era. 🍂",
        "frames": [
            {"prompt": "Stylish female student in Western University hoodie walking confidently through stunning autumn campus path, maple leaves falling around her, gothic University College stone building in background, golden hour. " + STYLE},
            {"prompt": "Close-up of student's iPhone showing CampusClip dashboard: performance rings, class cards, calendar with no overdue deadlines. She's holding it and smiling. Bokeh campus background. " + STYLE},
            {"prompt": "Wide shot of Western University campus at golden hour: students walking across scenic campus quad, autumn red and orange trees, gothic stone buildings, beautiful and vibrant university atmosphere. " + STYLE},
        ],
    },
    {
        "file": "ai-videos/v09_graduation.mp4",
        "feature": "Organised Students Graduate Differently", "headline": "Start organised. Graduate proud.",
        "caption": "Organised students graduate differently 🎓",
        "frames": [
            {"prompt": "Student using CampusClip on campus — phone shows grade tracker with 3.9 GPA, both rings filled, all classes on track. Confident expression, autumn campus, backpack on. The journey begins. " + STYLE},
            {"prompt": "University graduation ceremony: graduate in cap and gown walking across stage, receiving diploma from dean, crowd cheering, confetti falling, brilliant smile, campus quad in golden sunlight. " + STYLE},
            {"prompt": "Graduate holding diploma triumphantly overhead, cap and gown, campus quad, confetti mid-air, phone in other hand showing CampusClip with 'Final GPA 3.9 — Congratulations! 🎉' notification. Cinematic, emotional, golden hour. " + STYLE},
        ],
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
    duration = item.get("duration", 5)
    print(f"\nGenerating video: {item['file']} ({duration}s)", flush=True)

    # Try to attach a real app screenshot as the first frame
    first_frame_url = None
    screenshot_file = item.get("start_image")
    if screenshot_file:
        candidate = screenshot_url(screenshot_file)
        try:
            urllib.request.urlopen(candidate, timeout=8)
            first_frame_url = candidate
            print(f"  first_frame: {first_frame_url}", flush=True)
        except Exception as e:
            print(f"  first_frame URL unreachable ({e}), skipping", flush=True)

    # Models to try in order — minimax is free-tier accessible, Kling as fallback
    def minimax_input():
        d = {"prompt": item["prompt"], "duration": duration, "aspect_ratio": "9:16"}
        if first_frame_url:
            d["first_frame_image"] = first_frame_url
        return d

    def kling_input(model_ver):
        d = {"prompt": item["prompt"], "duration": str(duration),
             "aspect_ratio": "9:16", "cfg_scale": 0.5}
        if first_frame_url:
            d["start_image"] = first_frame_url
        return d

    candidates = [
        ("minimax/video-01",         minimax_input()),
        ("minimax/video-01-live",     minimax_input()),
        ("kwaivgi/kling-v1-6-pro",   kling_input("v1-6-pro")),
        ("kwaivgi/kling-v1.6-pro",   kling_input("v1.6-pro")),
    ]

    out = None
    last_error = None
    for model_id, model_input in candidates:
        try:
            print(f"  trying {model_id} ...", flush=True)
            out = run_with_retry(model_id, model_input)
            print(f"  ✓ success with {model_id}", flush=True)
            break
        except Exception as e:
            last_error = e
            print(f"  ✗ {model_id} failed: {e}", flush=True)

    if out is None:
        raise RuntimeError(f"All video models failed. Last error: {last_error}")

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
            gen_video_slideshow(item)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)

print("\nDone!", flush=True)
