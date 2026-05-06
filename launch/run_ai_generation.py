#!/usr/bin/env python3
"""
CampusClip AI Content Generator — called by GitHub Actions.
Usage: python3 run_ai_generation.py [images|lifestyle|product|emotional|all]
"""
import os, sys, urllib.request
from pathlib import Path
import replicate

BATCH = sys.argv[1] if len(sys.argv) > 1 else "images"

Path("ai-images").mkdir(exist_ok=True)
Path("ai-videos").mkdir(exist_ok=True)

def download(url, path):
    urllib.request.urlretrieve(str(url), path)
    print(f"  saved -> {path}", flush=True)

STYLE = (
    "cinematic lighting, shot on iPhone 16 Pro, ultra-detailed, "
    "8K resolution, social media ad quality, vibrant colors, "
    "professional photography, sharp focus, natural skin tones"
)

IMAGES = [
    {
        "file": "ai-images/img_01_library.png",
        "caption": "Study smarter, not harder 📚",
        "prompt": "Three diverse university students at a modern library table laughing at a smartphone showing a blue grade-tracking app. Western University hoodies, warm amber lighting, open MacBooks, autumn leaves through floor-to-ceiling windows. Shot on Sony A7IV, f/1.8, golden hour, hyperrealistic, Vogue editorial quality, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_02_syllabus_scan.png",
        "caption": "Every deadline. Auto-saved. 🗓️",
        "prompt": "Extreme close-up of elegant hands holding iPhone 16 Pro, screen shows a blue glassmorphism app scanning a university syllabus PDF with animated progress bar. Shallow depth of field, bokeh wooden desk background, ceramic espresso cup, morning light streaming through window. Product photography, hyperrealistic, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_03_grade_celebration.png",
        "caption": "That feeling when the grade hits different ✨",
        "prompt": "A joyful 21-year-old female student mid-laugh, eyes closed, fist pumped, sitting on sunlit university steps. Phone shows 91 percent Excellent in a blue gradient app. Golden hour backlight creates a halo effect, autumn leaves falling, Western University stone architecture. Candid lifestyle photography, hyperrealistic, 8K, shot on Leica. " + STYLE,
    },
    {
        "file": "ai-images/img_04_flatlay.png",
        "caption": "Your semester starter pack 🎓",
        "prompt": "Overhead flatlay: iPhone showing a beautiful blue gradient student app, open MacBook Pro, matcha latte with latte art, fresh white AirPods, Muji pens, leather notebook with sticky notes, university planner. Marble white desk, perfect lighting, Instagram aesthetic, hyperrealistic, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_05_night_dorm.png",
        "caption": "Deadlines don't sneak up anymore 🌙",
        "prompt": "University student in cozy dorm room at 11pm, warm fairy lights and Edison bulb glow, phone screen emitting soft blue light showing deadline alerts, textbooks open, half-eaten snack. Cinematic chiaroscuro lighting, moody intimate atmosphere. Shot on Canon R5, hyperrealistic, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_06_campus_walk.png",
        "caption": "Campus life, one app 🍂",
        "prompt": "Stylish male student mid-stride on a stunning autumn university campus path, laughing while checking phone, fallen maple leaves swirling. Gothic stone buildings, vibrant orange-red foliage, cinematic depth. Shot from slightly low angle, f/2.0, bokeh background, golden hour, hyperrealistic, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_07_study_group.png",
        "caption": "Your whole class, connected 🤝",
        "prompt": "Four diverse students in a warmly-lit campus cafe, all reacting with delight to something on one phone screen. Latte cups, MacBooks, authentic laughter, casual streetwear. Warm Edison bulb ambience, exposed brick, hyperrealistic candid photography, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_08_phone_hero.png",
        "caption": "Meet your campus companion 📱",
        "prompt": "iPhone 16 Pro in titanium finish floating at an angle against deep midnight blue background with subtle particle bokeh, screen showing a stunning blue gradient app with three animated circular grade rings 87 percent 72 percent 91 percent and glassmorphism cards. Dramatic rim lighting, caustic light reflections on desk surface. Apple-style product photography, hyperrealistic, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_09_relief_moment.png",
        "caption": "No more deadline panic. Ever. 😮‍💨",
        "prompt": "Split scene: left half moody red tones showing a stressed student with scattered papers, red notification alerts, overwhelmed expression; right half calm blue tones, same student relaxed and smiling at organized app screen. Perfect symmetry, graphic editorial style, hyperrealistic, 8K. " + STYLE,
    },
    {
        "file": "ai-images/img_10_graduation.png",
        "caption": "Organised students graduate differently 🎓",
        "prompt": "University graduate in cap and gown, holding diploma triumphantly overhead, brilliant smile, campus quad in golden hour, confetti mid-air. Phone in other hand shows 3.9 GPA Congratulations blue notification. Cinematic aspiration, emotional, shot on RED camera, hyperrealistic, 8K. " + STYLE,
    },
]

LIFESTYLE_VIDEOS = [
    {
        "file": "ai-videos/v01_campus_golden_hour.mp4",
        "caption": "Western never looked this good 🌅",
        "duration": 5,
        "prompt": "Cinematic slow-motion shot of a beautiful university campus at golden hour. Students walking through fallen autumn leaves, soft bokeh lights, stone gothic architecture glowing warm amber. Camera slowly pushes forward at eye level. Film grain, anamorphic lens flare, 24fps cinematic. Dreamlike, aspirational, like an Apple ad.",
    },
    {
        "file": "ai-videos/v02_library_study.mp4",
        "caption": "This is your era 📚",
        "duration": 5,
        "prompt": "Slow dolly shot through a beautiful university library at golden hour. Students at wooden tables, soft warm light through tall windows, books and MacBooks open, one student smiles looking at phone screen. Camera glides smoothly past each study spot. Cinematic, warm, aspirational, like a Netflix opening scene.",
    },
    {
        "file": "ai-videos/v03_friend_energy.mp4",
        "caption": "Built for your campus 🎉",
        "duration": 5,
        "prompt": "A group of four diverse university students burst into laughter around a cafe table, one shows something on their phone to the others, genuine reactions of surprise and joy. Camera slowly orbits the group. Warm cafe lighting, dynamic energy, authentic candid feel. Shot on 35mm, shallow depth of field, cinematic.",
    },
]

PRODUCT_VIDEOS = [
    {
        "file": "ai-videos/v04_app_reveal.mp4",
        "caption": "30 seconds. Every deadline saved. 📲",
        "duration": 5,
        "prompt": "Elegant close-up of an iPhone screen showing a blue glassmorphism app interface. A finger taps to scan a document, a satisfying progress bar fills with blue light, then a list of organized deadlines appears with smooth checkmark animations. Camera slowly pulls back to reveal the phone resting on a marble desk. Product demo, Apple aesthetic, hyperrealistic, satisfying UX animation feel.",
    },
    {
        "file": "ai-videos/v05_grade_tracker.mp4",
        "caption": "Watch your GPA climb 📊",
        "duration": 5,
        "prompt": "Macro close-up of a phone screen: three circular grade ring charts animate from 0 percent filling up to 87 72 91 percent with glowing blue and orange arcs. GPA number counts upward from 2.9 to 3.8 with smooth easing. Screen has dark navy background with glassmorphism card elements. Satisfying, clean, the animation feels like Apple own UI. Camera slowly zooms in.",
    },
    {
        "file": "ai-videos/v06_notification_relief.mp4",
        "caption": "3 days early. Every time. 🔔",
        "duration": 5,
        "prompt": "Close up of a sleeping student nightstand. Phone screen lights up with a gentle blue notification: Assignment due in 3 days you are on track. Student hand reaches and picks up phone, we see their face relax into a smile in soft morning light. Cinematic, warm, intimate. Camera slowly rises from nightstand level to face level.",
    },
]

EMOTIONAL_VIDEOS = [
    {
        "file": "ai-videos/v07_transformation.mp4",
        "caption": "Everything changes when you're organised 🙌",
        "duration": 5,
        "prompt": "A transformation: student sitting at cluttered chaotic desk with scattered papers and empty coffee cups, looking stressed. Scene cross-dissolves to the same student at a clean organized desk, calm expression, phone showing a beautiful blue app, sunlight streaming in. The whole mood shifts from anxious to peaceful. Cinematic, emotional, like a meditation app ad.",
    },
    {
        "file": "ai-videos/v08_campus_walk_reel.mp4",
        "caption": "Your campus. Your app. Your era. 🍂",
        "duration": 10,
        "prompt": "Stylish female student walking confidently through a stunning autumn university campus. Camera tracks alongside at shoulder level. She glances at her phone with a satisfied smile, maple leaves falling around her, stone buildings in golden background. Slow motion at moments, then real-time. Cinematic, aspirational, like an iPhone commercial. 24fps, anamorphic bokeh.",
    },
    {
        "file": "ai-videos/v09_graduation_dream.mp4",
        "caption": "Organised students graduate differently 🎓",
        "duration": 10,
        "prompt": "Emotional slow-motion of a university graduation ceremony. Graduate walks across stage, receives diploma, turns and pumps fist, crowd cheers. Confetti falls in slow motion. Phone in hand shows 3.9 GPA Congratulations notification. Golden sunlight, caps flying through the air. Cinematic, emotional, swelling energy. Like a university commercial.",
    },
]

def gen_image(item):
    print(f"\nGenerating image: {item['file']}", flush=True)
    out = replicate.run(
        "black-forest-labs/flux-1.1-pro",
        input={
            "prompt": item["prompt"],
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 100,
            "safety_tolerance": 2,
            "prompt_upsampling": True,
        }
    )
    download(str(out), item["file"])
    Path(item["file"].replace(".png", ".txt")).write_text(item.get("caption", ""))

def gen_video(item):
    print(f"\nGenerating video: {item['file']} ({item.get('duration', 5)}s)", flush=True)
    out = replicate.run(
        "kwaivgi/kling-v1-6-pro",
        input={
            "prompt": item["prompt"],
            "duration": item.get("duration", 5),
            "aspect_ratio": "9:16",
            "cfg_scale": 0.5,
        }
    )
    url = str(out) if isinstance(out, str) else str(list(out)[0])
    download(url, item["file"])
    Path(item["file"].replace(".mp4", ".txt")).write_text(item.get("caption", ""))

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
