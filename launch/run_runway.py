#!/usr/bin/env python3
"""
CampusClip Runway ML Video Ad Generator
Generates lifestyle B-roll via Runway Gen-3, then composites the real
CampusClip app screenshot in a phone frame overlay.

Usage: python3 run_runway.py [generate|test]
"""
import os, sys, json, time, subprocess, urllib.request, urllib.error, traceback
from pathlib import Path

API_KEY  = os.environ.get("RUNWAY_API_KEY", "")
BASE_URL = "https://api.dev.runwayml.com"
HEADERS  = {
    "Authorization":  f"Bearer {API_KEY}",
    "X-Runway-Version": "2024-11-06",
    "Content-Type":   "application/json",
    "Accept":         "application/json",
}

RAW = (
    "https://raw.githubusercontent.com/JamesYoung111/marketingskills/"
    "main/launch/app-screenshots"
)
SCREENS = {
    "dashboard": f"{RAW}/IMG_1617.jpeg",
    "class":     f"{RAW}/IMG_1618.jpeg",
    "clubs":     f"{RAW}/IMG_1619.jpeg",
    "feed":      f"{RAW}/IMG_1621.jpeg",
    "calendar":  f"{RAW}/IMG_1622.jpeg",
    "search":    f"{RAW}/IMG_1623.jpeg",
    "profile":   f"{RAW}/IMG_1624.jpeg",
}

OUT_DIR = Path("ai-videos/runway")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = Path("ai-videos/runway/tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)

# ── API ───────────────────────────────────────────────────────────────────────

def api_post(endpoint, data):
    body = json.dumps(data).encode()
    req  = urllib.request.Request(
        BASE_URL + endpoint, data=body,
        headers=HEADERS, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Runway POST {endpoint} → {e.code}: {e.read().decode()}")

def api_get(endpoint):
    req = urllib.request.Request(BASE_URL + endpoint, headers=HEADERS, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Runway GET {endpoint} → {e.code}: {e.read().decode()}")

def download(url, path):
    urllib.request.urlretrieve(url, str(path))
    print(f"    saved -> {path}", flush=True)

# ── Runway clip generation ─────────────────────────────────────────────────────

def generate_clip(prompt, duration=5, idx=0):
    """Submit a text-to-video task, wait for completion, return local path."""
    print(f"  clip {idx+1}: submitting to Runway...", flush=True)
    print(f"    prompt: {prompt[:80]}...", flush=True)

    resp = api_post("/v1/text_to_video", {
        "promptText": prompt,
        "model":      "gen3a_turbo",
        "duration":   duration,
        "ratio":      "720:1280",
        "watermark":  False,
    })
    task_id = resp.get("id") or resp.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task ID in response: {resp}")
    print(f"    task_id={task_id}", flush=True)

    # Poll
    deadline = time.time() + 600
    while time.time() < deadline:
        status_resp = api_get(f"/v1/tasks/{task_id}")
        status = status_resp.get("status", "")
        print(f"    status: {status}", flush=True)
        if status == "SUCCEEDED":
            outputs = status_resp.get("output", [])
            if not outputs:
                raise RuntimeError("SUCCEEDED but no output URLs")
            url = outputs[0]
            out = TMP_DIR / f"clip_{idx:02d}.mp4"
            download(url, out)
            return str(out)
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(
                f"Task {status}: {status_resp.get('failure', status_resp.get('error', ''))}"
            )
        time.sleep(15)
    raise RuntimeError(f"Timeout waiting for task {task_id}")

# ── Phone mockup overlay ───────────────────────────────────────────────────────

# Position of phone inset in the 1080x1920 output frame
PH_W, PH_H = 280, 560
PH_X, PH_Y = 760, 1280   # bottom-right area
BORDER      = 10

def overlay_phone(bg_clip, screen_name, output):
    """Composite CampusClip screenshot in phone frame on top of B-roll clip."""
    screen_path = TMP_DIR / f"{screen_name}.jpg"
    if not screen_path.exists():
        urllib.request.urlretrieve(SCREENS[screen_name], str(screen_path))

    inner_w = PH_W - BORDER * 2
    inner_h = PH_H - BORDER * 2

    # Scale screenshot to inner phone area
    scaled = TMP_DIR / f"{screen_name}_scaled.png"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(screen_path),
        "-vf", f"scale={inner_w}:{inner_h}:"
               f"force_original_aspect_ratio=decrease,"
               f"pad={inner_w}:{inner_h}:(ow-iw)/2:(oh-ih)/2",
        str(scaled),
    ], capture_output=True, check=True)

    # Composite: white bezel box + screenshot on top of B-roll
    fc = (
        # Scale B-roll to 1080x1920
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1[bg];"
        # White bezel
        f"[bg]drawbox="
        f"x={PH_X-BORDER}:y={PH_Y-BORDER}:w={PH_W}:h={PH_H}:"
        f"color=white:t=fill[boxed];"
        # Screenshot overlay
        f"[boxed][1:v]overlay=x={PH_X}:y={PH_Y}[out]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", bg_clip,
        "-loop", "1", "-i", str(scaled),
        "-filter_complex", fc,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest",
        output,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"    ffmpeg error:\n{r.stderr[-1500:]}", flush=True)
        raise RuntimeError("overlay_phone failed")
    print(f"    composited -> {output}", flush=True)

# ── Clip assembly ─────────────────────────────────────────────────────────────

def concat_clips(clip_paths, output):
    """Concatenate clips into final video."""
    list_file = TMP_DIR / "concat.txt"
    list_file.write_text("\n".join(f"file '{Path(p).resolve()}'" for p in clip_paths))
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        output,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"  ffmpeg concat error:\n{r.stderr[-1500:]}", flush=True)
        raise RuntimeError("concat failed")
    print(f"  final -> {output}", flush=True)

# ── Ad definitions ────────────────────────────────────────────────────────────
# Each scene: prompt for Runway, which CampusClip screen to overlay, clip duration

STYLE = (
    "cinematic 35mm, shallow depth of field, golden hour lighting, "
    "authentic, candid, real students, professional ad quality, "
    "no text, no logos"
)

CAMPUS = (
    "Western University Ontario Canada, gothic stone buildings, "
    "autumn maple trees red and orange, beautiful campus"
)

ADS = [
    {
        "name": "rv01_grade_panic",
        "caption": "Stop guessing your grade. CampusClip tracks it automatically. Free for Western students. August 2026.",
        "scenes": [
            {
                "prompt": f"University student at desk late at night, stressed expression, scattered notes and textbooks, multiple browser tabs, blue laptop glow, dorm room, {STYLE}",
                "screen": "dashboard",
                "duration": 5,
            },
            {
                "prompt": f"Close-up of university student's face, expression changing from worried to relieved, warm light, looking at phone, {STYLE}",
                "screen": "class",
                "duration": 5,
            },
            {
                "prompt": f"University student walking confidently across campus, {CAMPUS}, backpack, autumn morning, golden light, {STYLE}",
                "screen": "dashboard",
                "duration": 5,
            },
            {
                "prompt": f"University student pumping fist in celebration, holding phone, big smile, campus background, {CAMPUS}, {STYLE}",
                "screen": "dashboard",
                "duration": 5,
            },
        ],
    },
    {
        "name": "rv02_western_life",
        "caption": "Your classes. Your clubs. Your campus. One app. Free for Western students. August 2026.",
        "scenes": [
            {
                "prompt": f"Aerial drone shot of {CAMPUS}, students walking on paths between buildings, autumn, stunning, {STYLE}",
                "screen": "search",
                "duration": 5,
            },
            {
                "prompt": f"University student joining a study group in the library, being welcomed, smiling, warm amber lighting, wooden tables, bookshelves, {STYLE}",
                "screen": "clubs",
                "duration": 5,
            },
            {
                "prompt": f"Two university students sitting on campus bench, autumn trees, both looking at phones, laughing together, {CAMPUS}, {STYLE}",
                "screen": "feed",
                "duration": 5,
            },
            {
                "prompt": f"University student rushing to class, checks phone, visibly relaxes, slows down, confident smile, {CAMPUS}, {STYLE}",
                "screen": "calendar",
                "duration": 5,
            },
            {
                "prompt": f"Group of diverse university students at campus social event, laughing, welcoming, inclusive energy, {CAMPUS} indoor event space, {STYLE}",
                "screen": "clubs",
                "duration": 5,
            },
        ],
    },
    {
        "name": "rv03_september",
        "caption": "Starting at Western this September? Download CampusClip. Free.",
        "scenes": [
            {
                "prompt": f"New university student arriving on campus for the first time, looking around in awe, {CAMPUS}, September morning, excited, backpack, {STYLE}",
                "screen": "dashboard",
                "duration": 5,
            },
            {
                "prompt": f"University student sitting alone at campus cafeteria, discovers something on their phone, expression brightening, {STYLE}",
                "screen": "clubs",
                "duration": 5,
            },
            {
                "prompt": f"University student joining a club meeting, welcomed by a group, handshakes, warm interior, students around a table, {STYLE}",
                "screen": "feed",
                "duration": 5,
            },
            {
                "prompt": f"University student walking home at dusk, {CAMPUS} beautiful behind them, confident stride, checking phone, golden sunset, {STYLE}",
                "screen": "dashboard",
                "duration": 5,
            },
        ],
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────

MODE = sys.argv[1] if len(sys.argv) > 1 else "generate"

if MODE == "test":
    print("[TEST] Checking Runway API connectivity...", flush=True)
    if not API_KEY:
        print("ERROR: RUNWAY_API_KEY not set", flush=True)
        sys.exit(1)
    # Try a minimal API call to verify auth
    try:
        resp = api_get("/v1/organizations")
        print(f"  Connected! Response keys: {list(resp.keys())}", flush=True)
    except Exception as e:
        print(f"  Connection test: {e}", flush=True)

elif MODE == "generate":
    if not API_KEY:
        print("ERROR: RUNWAY_API_KEY not set", flush=True)
        sys.exit(1)

    print(f"[STARTUP] Generating {len(ADS)} Runway ads", flush=True)

    for ad in ADS:
        print(f"\n{'='*55}\n{ad['name']}\n{'='*55}", flush=True)
        composited_clips = []
        try:
            for i, scene in enumerate(ad["scenes"]):
                # Generate B-roll clip
                raw_clip = generate_clip(scene["prompt"], scene["duration"], i)

                # Composite phone mockup
                composited = str(TMP_DIR / f"{ad['name']}_c{i:02d}.mp4")
                overlay_phone(raw_clip, scene["screen"], composited)
                composited_clips.append(composited)

            # Concatenate into final ad
            final = str(OUT_DIR / f"{ad['name']}.mp4")
            concat_clips(composited_clips, final)

            # Save caption
            Path(final.replace(".mp4", ".txt")).write_text(ad["caption"])
            print(f"  DONE: {final}", flush=True)

        except Exception as e:
            print(f"  ERROR {ad['name']}: {e}", flush=True)
            traceback.print_exc()

    print("\nAll done!", flush=True)

else:
    print(f"Unknown mode: {MODE}. Use generate or test.")
    sys.exit(1)
