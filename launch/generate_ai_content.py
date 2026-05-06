#!/usr/bin/env python3
"""
CampusClip AI Content Generator
Uses Replicate API to generate professional Instagram images and video clips.

Setup:
  export REPLICATE_API_TOKEN=r8_xxxxxxxxxxxx
  python3 generate_ai_content.py

Models used:
  Images : black-forest-labs/flux-1.1-pro  (~$0.004/image, 1080x1920)
  Video  : kwaivgi/kling-v1-5              (~$0.04/clip,  5s, 720p)
"""

import os, sys, json, time, urllib.request
from pathlib import Path

try:
    import replicate
except ImportError:
    print("Installing replicate..."); os.system("pip install replicate -q")
    import replicate

TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
if not TOKEN:
    print("\n─── SETUP REQUIRED ─────────────────────────────────────────────")
    print("1. Go to: https://replicate.com/signin")
    print("2. Sign up (free — includes $5 credit)")
    print("3. Go to: https://replicate.com/account/api-tokens")
    print("4. Copy your token, then run:")
    print('\n   export REPLICATE_API_TOKEN="r8_your_token_here"')
    print("   python3 generate_ai_content.py\n")
    sys.exit(1)

OUT_IMG = Path("ai-images")
OUT_VID = Path("ai-videos")
OUT_IMG.mkdir(exist_ok=True)
OUT_VID.mkdir(exist_ok=True)

# ── Style anchor (appended to every prompt) ───────────────────────────────────
STYLE = (
    "cinematic lighting, shot on iPhone 16 Pro, ultra-detailed, "
    "8K resolution, social media ad quality, vibrant colors, "
    "professional photography, sharp focus, natural skin tones"
)

BRAND_CONTEXT = (
    "CampusClip app UI visible on phone screen showing blue gradient interface, "
    "Western University campus setting"
)

# ── Image prompts ─────────────────────────────────────────────────────────────
IMAGE_PROMPTS = [
    {
        "filename": "01_student_library.png",
        "prompt": (
            "A diverse group of three university students sitting at a modern library table, "
            "laughing and looking at a smartphone showing a blue app with grade rings and deadlines. "
            "One student wearing a Western University hoodie. "
            "Warm ambient library lighting, bookshelves in background, "
            "open laptops on table, autumn vibes through window. "
            f"{STYLE}"
        ),
        "caption": "Study smarter, not harder 📚",
    },
    {
        "filename": "02_scan_syllabus.png",
        "prompt": (
            "Close-up of a university student's hands holding a white iPhone, "
            "phone screen showing a blue-gradient app scanning a printed course syllabus PDF. "
            "Student sitting at a wooden desk, coffee cup nearby, campus notebook visible. "
            "Clean natural window light, shallow depth of field, bokeh background. "
            f"{STYLE}"
        ),
        "caption": "30 seconds and every deadline is saved 🗓️",
    },
    {
        "filename": "03_celebration_grades.png",
        "prompt": (
            "Happy 20-year-old female university student looking at her phone, "
            "big genuine smile, fist pump gesture, sitting outside on university campus steps. "
            "Phone screen shows '91% — Great job!' in a blue gradient app. "
            "Golden hour sunlight, leafy campus background, casual student fashion. "
            f"{STYLE}"
        ),
        "caption": "That feeling when the grade hits different ✨",
    },
    {
        "filename": "04_campus_social.png",
        "prompt": (
            "Overhead flat lay shot of a MacBook, iPhone showing blue social app feed, "
            "university branded items (pencils, notebook, stickers), iced coffee, "
            "airpods, on a light wood desk. Aesthetic student workspace. "
            "Vibrant pastel accents, Instagram-worthy composition. "
            f"{STYLE}"
        ),
        "caption": "Your new semester starter pack 🎓",
    },
    {
        "filename": "05_night_study.png",
        "prompt": (
            "University student studying late at night in dorm room, "
            "phone propped up showing deadline alerts glowing in blue, "
            "fairy lights in background, textbooks stacked, laptop open, "
            "cozy warm lamp light contrasting with cool phone screen glow. "
            "Moody cinematic atmosphere, intimate dorm room setting. "
            f"{STYLE}"
        ),
        "caption": "Deadlines don't sneak up on you anymore 🌙",
    },
    {
        "filename": "06_campus_walk.png",
        "prompt": (
            "Stylish university student walking across a beautiful autumn campus, "
            "checking phone while walking, phone screen visible showing CampusClip app events feed. "
            "Red and orange maple leaves, gothic university architecture in background, "
            "blue sky, natural movement, lifestyle photography feel. "
            f"{STYLE}"
        ),
        "caption": "Campus life, all in one place 🍂",
    },
    {
        "filename": "07_friend_group.png",
        "prompt": (
            "Four diverse university students in a campus café, "
            "all looking at one student's phone screen that shows a blue group chat and event feed. "
            "Everyone laughing and reacting, casual outfits, coffee cups, "
            "warm café lighting, brick walls, authentic candid moment feel. "
            f"{STYLE}"
        ),
        "caption": "Your whole class on one app 🤝",
    },
    {
        "filename": "08_app_mockup_hero.png",
        "prompt": (
            "Ultra-realistic iPhone 16 Pro mockup floating in mid-air against a deep navy blue background, "
            "phone screen showing a beautiful blue gradient app with circular grade rings (87%, 72%, 91%), "
            "glassmorphism cards, clean sans-serif typography. "
            "Dramatic studio lighting from above, subtle lens flare, "
            "phone casting a soft blue glow shadow below it. "
            "Product photography style, advertising campaign quality. "
            f"{STYLE}"
        ),
        "caption": "Meet your new campus companion 📱",
    },
    {
        "filename": "09_deadline_panic_to_calm.png",
        "prompt": (
            "Split composition: left side shows scattered paper, stressed student, alarm clocks, "
            "red urgent notifications; right side shows same student now calm and smiling, "
            "organized phone app showing all deadlines sorted with checkmarks, blue peaceful tones. "
            "Bold visual contrast between chaos and calm. "
            "Modern graphic design meets photography, editorial style. "
            f"{STYLE}"
        ),
        "caption": "Before vs After CampusClip 🔄",
    },
    {
        "filename": "10_graduation_future.png",
        "prompt": (
            "University student in graduation cap and gown, holding diploma, "
            "triumphant expression, beautiful campus in golden hour background, "
            "confetti falling, holding phone showing CampusClip with '4.0 GPA achieved' notification. "
            "Aspirational, emotional, cinematic graduation photo. "
            "Warm golden tones, celebratory atmosphere. "
            f"{STYLE}"
        ),
        "caption": "This is what organised looks like 🎓",
    },
]

# ── Video prompts ─────────────────────────────────────────────────────────────
VIDEO_PROMPTS = [
    {
        "filename": "v01_scan_demo.mp4",
        "prompt": (
            "University student picks up printed syllabus document and holds it in front of phone camera. "
            "Phone screen shows scanning animation with blue progress bar filling up, "
            "then displays organized list of dates and deadlines with checkmarks appearing. "
            "Clean, satisfying UI animation. Modern aesthetic, natural lighting, "
            "shallow depth of field, cinematic movement."
        ),
        "duration": 5,
    },
    {
        "filename": "v02_grade_reveal.png",
        "prompt": (
            "Close up of phone screen showing grade tracker app, "
            "numbers animating and counting upward in blue gradient, "
            "GPA ticking from 3.2 to 3.8, circular progress rings filling with glowing blue light. "
            "Phone slowly pulls back to reveal student smiling in campus café. "
            "Satisfying, clean, motivational mood."
        ),
        "duration": 5,
    },
    {
        "filename": "v03_campus_lifestyle.mp4",
        "prompt": (
            "Montage-style: student walking through autumn university campus, "
            "checking phone app while walking, close-up of app screen showing events feed, "
            "cuts to student joining study group on campus, "
            "all connected by seamless blue app interface overlays. "
            "Dynamic, energetic, modern lifestyle feel. "
            "Golden hour lighting, fast-paced but smooth editing rhythm."
        ),
        "duration": 5,
    },
]


def download_file(url: str, path: Path):
    """Download a file from URL and save it."""
    with urllib.request.urlopen(url) as r, open(path, "wb") as f:
        f.write(r.read())


def generate_image(prompt_data: dict, idx: int, total: int) -> str:
    print(f"\n[{idx}/{total}] Generating: {prompt_data['filename']}")
    print(f"  Prompt: {prompt_data['prompt'][:80]}...")

    output = replicate.run(
        "black-forest-labs/flux-1.1-pro",
        input={
            "prompt": prompt_data["prompt"],
            "aspect_ratio": "9:16",          # 1080x1920 for Stories/Reels
            "output_format": "png",
            "output_quality": 100,
            "safety_tolerance": 2,
            "prompt_upsampling": True,
        }
    )

    out_path = OUT_IMG / prompt_data["filename"]
    url = str(output)
    download_file(url, out_path)
    print(f"  ✓ Saved → {out_path}")

    # Save caption alongside
    cap_path = out_path.with_suffix(".txt")
    cap_path.write_text(prompt_data.get("caption", ""))

    return str(out_path)


def generate_video(prompt_data: dict, idx: int, total: int) -> str:
    print(f"\n[{idx}/{total}] Generating video: {prompt_data['filename']}")
    print(f"  Prompt: {prompt_data['prompt'][:80]}...")

    output = replicate.run(
        "kwaivgi/kling-v1-5",
        input={
            "prompt": prompt_data["prompt"],
            "duration": prompt_data.get("duration", 5),
            "aspect_ratio": "9:16",
            "cfg_scale": 0.5,
        }
    )

    out_path = OUT_VID / prompt_data["filename"]
    url = str(output) if isinstance(output, str) else str(list(output)[0])
    download_file(url, out_path)
    print(f"  ✓ Saved → {out_path}")
    return str(out_path)


def main():
    print("=" * 60)
    print("CampusClip AI Content Generator")
    print(f"Model: FLUX 1.1 Pro (images) + Kling v1.5 (video)")
    print(f"Output: {OUT_IMG}/ and {OUT_VID}/")
    print("=" * 60)

    # Ask what to generate
    print("\nWhat do you want to generate?")
    print("  1. Images only  (10 posts, ~$0.04 total)")
    print("  2. Videos only  (3 clips, ~$0.12 total)")
    print("  3. Both         (~$0.16 total)")
    choice = input("\nEnter 1, 2, or 3 [default: 1]: ").strip() or "1"

    results = []

    if choice in ("1", "3"):
        print(f"\n─── Generating {len(IMAGE_PROMPTS)} images ───")
        for i, p in enumerate(IMAGE_PROMPTS, 1):
            try:
                path = generate_image(p, i, len(IMAGE_PROMPTS))
                results.append({"type": "image", "path": path, "caption": p.get("caption", "")})
            except Exception as e:
                print(f"  ✗ Error: {e}")

    if choice in ("2", "3"):
        print(f"\n─── Generating {len(VIDEO_PROMPTS)} video clips ───")
        for i, p in enumerate(VIDEO_PROMPTS, 1):
            try:
                path = generate_video(p, i, len(VIDEO_PROMPTS))
                results.append({"type": "video", "path": path})
            except Exception as e:
                print(f"  ✗ Error: {e}")

    # Save manifest
    manifest = OUT_IMG / "manifest.json"
    manifest.write_text(json.dumps(results, indent=2))

    print(f"\n{'=' * 60}")
    print(f"Done! Generated {len(results)} assets.")
    print(f"Images → {OUT_IMG}/")
    print(f"Videos → {OUT_VID}/")
    print(f"Manifest → {manifest}")
    print("\nCaption files saved as .txt alongside each image.")
    print("Ready to upload to Instagram / TikTok directly.")


if __name__ == "__main__":
    main()
