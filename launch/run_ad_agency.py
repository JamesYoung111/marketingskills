#!/usr/bin/env python3
"""
CampusClip Ad Agency Pipeline
Combines HeyGen (AI avatar + voiceover) + Runway ML (cinematic B-roll) + ffmpeg composite.

For each scene:
  1. HeyGen renders the avatar speaking that scene's script against a chroma-green background
  2. Runway renders cinematic campus B-roll for that scene
  3. ffmpeg composites: B-roll background + chroma-keyed avatar + phone mockup overlay

All scenes are concatenated into the final polished ad.

Usage:
  python3 run_ad_agency.py                   # generate all ads
  python3 run_ad_agency.py list              # list available ads
  python3 run_ad_agency.py aa01_grade_panic  # generate one specific ad
"""
import os, sys, json, time, subprocess, traceback
import urllib.request, urllib.error
from pathlib import Path

# ── Credentials ────────────────────────────────────────────────────────────────
HEYGEN_API_KEY   = os.environ.get("HEYGEN_API_KEY",   "")
RUNWAY_API_KEY   = os.environ.get("RUNWAY_API_KEY",   "")
HEYGEN_AVATAR_ID = os.environ.get("HEYGEN_AVATAR_ID", "Daisy-inskirt-20220818")
HEYGEN_VOICE_ID  = os.environ.get("HEYGEN_VOICE_ID",  "1bd001e7e50f421d891986aad5158bc8")

HEYGEN_BASE = "https://api.heygen.com"
RUNWAY_BASE = "https://api.dev.runwayml.com"

# ── Output directories ─────────────────────────────────────────────────────────
OUT_DIR = Path("ai-videos/ad-agency")
TMP_DIR = Path("ai-videos/ad-agency/tmp")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# ── App screenshots ────────────────────────────────────────────────────────────
RAW = (
    "https://raw.githubusercontent.com/JamesYoung111/marketingskills"
    "/main/launch/app-screenshots"
)
SCREENS = {
    "dashboard": f"{RAW}/IMG_1617.jpeg",
    "class":     f"{RAW}/IMG_1618.jpeg",
    "clubs":     f"{RAW}/IMG_1619.jpeg",
    "feed":      f"{RAW}/IMG_1621.jpeg",
    "calendar":  f"{RAW}/IMG_1622.jpeg",
    "search":    f"{RAW}/IMG_1623.jpeg",
}

# ── HeyGen API ─────────────────────────────────────────────────────────────────
def hg_request(method, endpoint, data=None, params=None):
    url = HEYGEN_BASE + endpoint
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers={
        "X-Api-Key":    HEYGEN_API_KEY,
        "Content-Type": "application/json",
        "Accept":       "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HeyGen {method} {endpoint} → {e.code}: {e.read().decode()}")

def heygen_submit(script):
    """Submit one HeyGen scene with green screen background, return video_id."""
    print(f"  [HeyGen] submitting ({len(script.split())} words)...", flush=True)
    resp = hg_request("POST", "/v2/video/generate", {
        "video_inputs": [{
            "character": {
                "type":         "avatar",
                "avatar_id":    HEYGEN_AVATAR_ID,
                "avatar_style": "normal",
            },
            "voice": {
                "type":       "text",
                "input_text": script,
                "voice_id":   HEYGEN_VOICE_ID,
                "speed":      1.0,
            },
            "background": {"type": "color", "value": "#00FF00"},
        }],
        "dimension": {"width": 1080, "height": 1920},
        "caption":   False,
        "title":     "CampusClip Ad Scene",
    })
    vid_id = resp["data"]["video_id"]
    print(f"  [HeyGen] queued video_id={vid_id}", flush=True)
    return vid_id

def heygen_wait(vid_id, out_path, timeout=900):
    """Poll HeyGen until done, download to out_path."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = hg_request("GET", "/v1/video_status.get", params={"video_id": vid_id})
        status = resp["data"]["status"]
        print(f"  [HeyGen] status: {status}", flush=True)
        if status == "completed":
            urllib.request.urlretrieve(resp["data"]["video_url"], str(out_path))
            print(f"  [HeyGen] saved → {out_path}", flush=True)
            return
        if status == "failed":
            raise RuntimeError(f"HeyGen failed: {resp['data'].get('error')}")
        time.sleep(20)
    raise RuntimeError(f"HeyGen timeout for {vid_id}")

# ── Runway API ─────────────────────────────────────────────────────────────────
def rw_headers():
    return {
        "Authorization":    f"Bearer {RUNWAY_API_KEY}",
        "X-Runway-Version": "2024-11-06",
        "Content-Type":     "application/json",
        "Accept":           "application/json",
    }

def rw_post(endpoint, data):
    req = urllib.request.Request(
        RUNWAY_BASE + endpoint,
        data=json.dumps(data).encode(),
        headers=rw_headers(), method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Runway POST {endpoint} → {e.code}: {e.read().decode()}")

def rw_get(endpoint):
    req = urllib.request.Request(RUNWAY_BASE + endpoint, headers=rw_headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Runway GET {endpoint} → {e.code}: {e.read().decode()}")

def runway_generate_clip(prompt, out_path, duration=5, timeout=600):
    """Submit Runway text-to-video, poll until done, download to out_path."""
    print(f"  [Runway] submitting clip...", flush=True)
    print(f"  [Runway] prompt: {prompt[:90]}", flush=True)
    resp = rw_post("/v1/text_to_video", {
        "promptText": prompt,
        "model":      "gen3a_turbo",
        "duration":   duration,
        "ratio":      "720:1280",
        "watermark":  False,
    })
    task_id = resp.get("id") or resp.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task ID in Runway response: {resp}")
    print(f"  [Runway] task_id={task_id}", flush=True)

    deadline = time.time() + timeout
    while time.time() < deadline:
        s = rw_get(f"/v1/tasks/{task_id}")
        status = s.get("status", "")
        print(f"  [Runway] status: {status}", flush=True)
        if status == "SUCCEEDED":
            url = (s.get("output") or [""])[0]
            if not url:
                raise RuntimeError("SUCCEEDED but no output URL")
            urllib.request.urlretrieve(url, str(out_path))
            print(f"  [Runway] saved → {out_path}", flush=True)
            return
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(
                f"Runway task {status}: {s.get('failure', s.get('error', ''))}"
            )
        time.sleep(15)
    raise RuntimeError(f"Runway timeout for task {task_id}")

# ── ffmpeg compositing ─────────────────────────────────────────────────────────
# Phone mockup dimensions and position (bottom-right, 1080x1920 frame)
PH_W, PH_H = 300, 600
PH_X, PH_Y = 760, 1280
BORDER      = 10

def get_screen_scaled(screen_name):
    """Download app screenshot and scale it to fit the phone's inner area."""
    src = TMP_DIR / f"screen_{screen_name}.jpg"
    dst = TMP_DIR / f"screen_{screen_name}_scaled.png"
    if not dst.exists():
        if not src.exists():
            urllib.request.urlretrieve(SCREENS[screen_name], str(src))
            print(f"  [assets] downloaded {screen_name} screenshot", flush=True)
        inner_w = PH_W - BORDER * 2
        inner_h = PH_H - BORDER * 2
        subprocess.run([
            "ffmpeg", "-y", "-i", str(src),
            "-vf", (
                f"scale={inner_w}:{inner_h}:force_original_aspect_ratio=decrease,"
                f"pad={inner_w}:{inner_h}:(ow-iw)/2:(oh-ih)/2"
            ),
            str(dst),
        ], capture_output=True, check=True)
    return dst

def composite_scene(runway_clip, heygen_clip, screen_name, out):
    """
    Composite three layers into one scene clip:
      [0] Runway B-roll   → full-screen background (loops to fill avatar duration)
      [1] HeyGen avatar   → chroma-keyed (green removed) and overlaid on background
      [2] App screenshot  → composited in a white phone bezel, bottom-right corner
    Audio comes from the HeyGen clip (the voiceover).
    """
    screen_scaled = get_screen_scaled(screen_name)

    fc = (
        # Runway: scale to 1080x1920, darken slightly so avatar pops
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,"
        f"eq=brightness=-0.05:saturation=1.2[bg];"

        # HeyGen: scale to 1080x1920, chroma-key the green screen
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,"
        f"chromakey=green:0.3:0.05,format=yuva420p[avatar];"

        # Overlay avatar on B-roll background
        f"[bg][avatar]overlay=0:0:format=auto[base];"

        # White phone bezel
        f"[base]drawbox="
        f"x={PH_X - BORDER}:y={PH_Y - BORDER}:w={PH_W}:h={PH_H}:"
        f"color=white:t=fill[boxed];"

        # App screenshot inside bezel
        f"[boxed][2:v]overlay=x={PH_X}:y={PH_Y}[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(runway_clip),    # [0] B-roll, looped
        "-i", str(heygen_clip),                           # [1] avatar + audio
        "-loop", "1", "-i", str(screen_scaled),          # [2] screenshot
        "-filter_complex", fc,
        "-map", "[out]",
        "-map", "1:a?",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100",
        "-r", "24",
        "-shortest",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if r.returncode != 0:
        print(f"  [ffmpeg] stderr:\n{r.stderr[-2000:]}", flush=True)
        raise RuntimeError("composite_scene failed")
    print(f"  [ffmpeg] composited → {out}", flush=True)

def concat_clips(paths, out):
    """Concatenate all composited scene clips into the final ad."""
    list_file = TMP_DIR / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{Path(p).resolve()}'" for p in paths)
    )
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100",
        str(out),
    ], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  [ffmpeg] concat error:\n{r.stderr[-1000:]}", flush=True)
        raise RuntimeError("concat failed")
    print(f"  [ffmpeg] final → {out}", flush=True)

# ── Ad definitions ─────────────────────────────────────────────────────────────
STYLE = (
    "cinematic vertical 9:16, shallow depth of field, golden hour lighting, "
    "authentic, real university students, no text overlays, no logos, "
    "professional advertisement quality"
)
CAMPUS = (
    "Western University Ontario Canada, gothic stone buildings, "
    "autumn maple trees red and orange"
)

ADS = [
    # ── Reel 1: The Problem ───────────────────────────────────────────────────
    {
        "name": "reel1_the_problem",
        "scenes": [
            {
                "script": "You are wasting hours every week on this.",
                "runway": (
                    f"University student frantically switching between apps on laptop and phone, "
                    f"stressed, overwhelmed expression, multiple browser tabs open, dorm room, {STYLE}"
                ),
                "screen": "dashboard",
            },
            {
                "script": (
                    "Managing your classes, clubs, and campus life across five different apps — "
                    "manually entering everything yourself — is eating your time. "
                    "Every syllabus, every deadline, every club meeting — typed in by hand."
                ),
                "runway": (
                    f"Close-up of student's hands slowly typing a class schedule into Google Calendar, "
                    f"frustrated expression, switching between PDF syllabus and browser, late night, {STYLE}"
                ),
                "screen": "calendar",
            },
            {
                "script": (
                    "Upload your syllabus to CampusClip. "
                    "Your entire calendar populates in seconds. "
                    "Classes, clubs, events — one place."
                ),
                "runway": (
                    f"Student's face going from stressed to genuinely relieved and happy, "
                    f"looking at phone, warm light, relaxed shoulders, {STYLE}"
                ),
                "screen": "calendar",
            },
            {
                "script": "CampusClip. Coming to Western this August. Link in bio.",
                "runway": (
                    f"Beautiful {CAMPUS}, autumn leaves, students walking confidently, "
                    f"golden hour, cinematic wide shot, {STYLE}"
                ),
                "screen": "dashboard",
            },
        ],
    },
    # ── Reel 2: Seconds vs Hours ──────────────────────────────────────────────
    {
        "name": "reel2_seconds_vs_hours",
        "scenes": [
            {
                "script": "This takes three hours. This takes ten seconds.",
                "runway": (
                    f"Two university students side by side — one frustrated at laptop typing slowly, "
                    f"one relaxed holding phone smiling, contrasting expressions, campus library, {STYLE}"
                ),
                "screen": "class",
            },
            {
                "script": (
                    "Upload your syllabus, and CampusClip automatically builds your entire "
                    "academic schedule for you. No more copy-paste. No more missing deadlines."
                ),
                "runway": (
                    f"Student uploading a document on phone, then looking amazed as calendar fills up, "
                    f"satisfying reveal moment, bright study space, {STYLE}"
                ),
                "screen": "calendar",
            },
            {
                "script": (
                    "Your academics, your clubs, your campus events, your social feed — "
                    "all in one app."
                ),
                "runway": (
                    f"Student casually scrolling phone with a smile, relaxed on campus bench, "
                    f"{CAMPUS}, autumn, everything under control, {STYLE}"
                ),
                "screen": "feed",
            },
            {
                "script": "The future of student life at Western. Coming August 2026.",
                "runway": (
                    f"Cinematic drone shot over {CAMPUS}, golden afternoon light, "
                    f"students thriving, autumn colours, inspiring, {STYLE}"
                ),
                "screen": "dashboard",
            },
        ],
    },
    # ── Reel 3: One App ───────────────────────────────────────────────────────
    {
        "name": "reel3_one_app",
        "scenes": [
            {
                "script": "What if one app ran your entire university life?",
                "runway": (
                    f"University student looking at phone thoughtfully, curious expression, "
                    f"then face lighting up, {CAMPUS} background, {STYLE}"
                ),
                "screen": "dashboard",
            },
            {
                "script": (
                    "Your class schedule — auto-built from your syllabus. "
                    "Your assignments and deadlines — tracked automatically."
                ),
                "runway": (
                    f"Students in a lecture hall, organized and focused, professor at front, "
                    f"warm academic atmosphere, Western University, {STYLE}"
                ),
                "screen": "class",
            },
            {
                "script": (
                    "Your clubs and campus events all in one feed. "
                    "And your classmates — connected in one place."
                ),
                "runway": (
                    f"Students at a vibrant campus club fair, energetic, diverse groups, "
                    f"welcoming, {CAMPUS} outdoor space, autumn, {STYLE}"
                ),
                "screen": "clubs",
            },
            {
                "script": (
                    "One app. Your whole campus life. "
                    "CampusClip — launching at Western this August."
                ),
                "runway": (
                    f"Student relaxed on campus grass, laptop open, phone in hand, "
                    f"completely at ease, {CAMPUS} golden hour behind them, {STYLE}"
                ),
                "screen": "feed",
            },
        ],
    },
    # ── Legacy ads (kept for reference) ──────────────────────────────────────
    {
        "name": "aa01_grade_panic",
        "scenes": [
            {
                "script": (
                    "If you're at Western and still calculating your grade "
                    "in a spreadsheet — you are wasting so much time."
                ),
                "runway": (
                    f"University student stressed at laptop late at night, "
                    f"scattered notes and textbooks, dorm room blue glow, {STYLE}"
                ),
                "screen": "dashboard",
            },
            {
                "script": (
                    "CampusClip tracks every assignment, every weight, every deadline. "
                    "Your real GPA — updated automatically."
                ),
                "runway": (
                    f"Close-up of student's face changing from anxious to relieved, "
                    f"looking at phone, warm light, {STYLE}"
                ),
                "screen": "class",
            },
            {
                "script": (
                    "Free for Western students. Download coming August 2026. "
                    "Follow campusclipapp."
                ),
                "runway": (
                    f"Student walking confidently across {CAMPUS}, "
                    f"autumn morning golden light, happy expression, {STYLE}"
                ),
                "screen": "dashboard",
            },
        ],
    },
    {
        "name": "aa02_campus_life",
        "scenes": [
            {
                "script": (
                    "There is so much happening at Western, "
                    "and it's all scattered — Instagram, GroupMe, email from the prof. "
                    "You miss stuff constantly."
                ),
                "runway": (
                    f"Aerial view of {CAMPUS}, students walking on paths between "
                    f"buildings, autumn, stunning, {STYLE}"
                ),
                "screen": "feed",
            },
            {
                "script": (
                    "CampusClip puts your classes, your clubs, and all your deadlines "
                    "in one single feed. If something is happening at Western, "
                    "it's in the app."
                ),
                "runway": (
                    f"Two university students on campus bench laughing, looking at phones, "
                    f"{CAMPUS}, {STYLE}"
                ),
                "screen": "clubs",
            },
            {
                "script": (
                    "Free. August 2026. Follow at campusclipapp."
                ),
                "runway": (
                    f"Group of diverse university students at a campus social event, "
                    f"welcoming, inclusive, {CAMPUS}, {STYLE}"
                ),
                "screen": "search",
            },
        ],
    },
    {
        "name": "aa03_first_year",
        "scenes": [
            {
                "script": (
                    "If you're starting at Western in September, "
                    "download CampusClip before you go."
                ),
                "runway": (
                    f"New university student arriving on campus for the first time, "
                    f"looking around in awe, {CAMPUS}, September morning, backpack, {STYLE}"
                ),
                "screen": "dashboard",
            },
            {
                "script": (
                    "It tracks your grades automatically, "
                    "shows you every club on campus, "
                    "and syncs all your deadlines with your courses."
                ),
                "runway": (
                    f"University student joining a study group in the library, "
                    f"being welcomed warmly, amber lighting, bookshelves, {STYLE}"
                ),
                "screen": "clubs",
            },
            {
                "script": (
                    "It is the one app I wish I had in first year. "
                    "Free for Western students. August 2026."
                ),
                "runway": (
                    f"Student walking home at dusk, {CAMPUS} glowing behind them, "
                    f"confident stride, golden sunset, {STYLE}"
                ),
                "screen": "calendar",
            },
        ],
    },
]

# ── Main pipeline ──────────────────────────────────────────────────────────────
def generate_ad(ad):
    name   = ad["name"]
    scenes = ad["scenes"]
    print(f"\n{'='*60}\nGenerating: {name}  ({len(scenes)} scenes)\n{'='*60}", flush=True)

    if not HEYGEN_API_KEY:
        raise RuntimeError("HEYGEN_API_KEY not set")
    if not RUNWAY_API_KEY:
        raise RuntimeError("RUNWAY_API_KEY not set")

    composited = []
    for i, scene in enumerate(scenes):
        print(f"\n── Scene {i+1}/{len(scenes)} ──", flush=True)

        heygen_clip = TMP_DIR / f"{name}_hg_{i:02d}.mp4"
        runway_clip = TMP_DIR / f"{name}_rw_{i:02d}.mp4"
        comp_clip   = TMP_DIR / f"{name}_comp_{i:02d}.mp4"

        # Step A: HeyGen — avatar speaking this scene's script
        if heygen_clip.exists():
            print(f"  [HeyGen] using cached {heygen_clip.name}", flush=True)
        else:
            vid_id = heygen_submit(scene["script"])
            heygen_wait(vid_id, heygen_clip)

        # Step B: Runway — cinematic B-roll for this scene
        if runway_clip.exists():
            print(f"  [Runway] using cached {runway_clip.name}", flush=True)
        else:
            runway_generate_clip(scene["runway"], runway_clip, duration=5)

        # Step C: Composite HeyGen avatar over Runway B-roll + phone mockup
        composite_scene(runway_clip, heygen_clip, scene["screen"], comp_clip)
        composited.append(str(comp_clip))

    # Step D: Concatenate all composited scenes
    final = OUT_DIR / f"{name}.mp4"
    concat_clips(composited, final)
    print(f"\n✓  DONE → {final}", flush=True)


# ── Entry point ────────────────────────────────────────────────────────────────
MODE = sys.argv[1] if len(sys.argv) > 1 else "all"

if MODE == "list":
    print("\nAvailable ads:")
    for ad in ADS:
        words = sum(len(s["script"].split()) for s in ad["scenes"])
        print(f"  {ad['name']}  ({len(ad['scenes'])} scenes, ~{words} words)")
    sys.exit(0)

to_run = ADS if MODE == "all" else [a for a in ADS if a["name"] == MODE]
if not to_run:
    print(f"Unknown ad '{MODE}'. Run 'list' to see options.")
    sys.exit(1)

for ad in to_run:
    try:
        generate_ad(ad)
    except Exception as e:
        print(f"\nERROR in {ad['name']}: {e}", flush=True)
        traceback.print_exc()

print("\nAll done!", flush=True)
