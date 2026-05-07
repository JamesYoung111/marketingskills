#!/usr/bin/env python3
"""
CampusClip Ad Agency Pipeline — Free Edition
  Avatar + voiceover : Hedra  (hedra.com — Creator plan $10/month)
  Cinematic B-roll   : Kling  via PiAPI (piapi.ai — free credits on signup)

Layout per scene (1080x1920):
  ┌──────────────────┐
  │  Kling B-roll    │  top 55 %  (1080 x 1056)
  ├──────────────────┤
  │  Hedra avatar    │  bottom 45 %  (1080 x 864, face/shoulders cropped)
  │            [📱]  │  phone mockup bottom-right
  └──────────────────┘

Setup (env vars):
  HEDRA_API_KEY     — hedra.com/api-profile  (requires Creator plan)
  PIAPI_KEY         — piapi.ai workspace     (free credits on signup)
  HEDRA_AVATAR_URL  — public URL to a portrait JPG used as the avatar face

Usage:
  python3 run_ad_agency.py list
  python3 run_ad_agency.py reel1_the_problem
  python3 run_ad_agency.py all
"""
import os, sys, json, time, subprocess, traceback
import urllib.request, urllib.error
from pathlib import Path

# ── Credentials ────────────────────────────────────────────────────────────────
HEDRA_API_KEY    = os.environ.get("HEDRA_API_KEY",    "")
PIAPI_KEY        = os.environ.get("PIAPI_KEY",        "")
HEDRA_AVATAR_URL = os.environ.get("HEDRA_AVATAR_URL", "")

HEDRA_BASE = "https://api.hedra.com/web-app/public"
PIAPI_BASE = "https://api.piapi.ai"

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

# ── Hedra API ──────────────────────────────────────────────────────────────────
def hedra_req(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        HEDRA_BASE + path, data=data, method=method,
        headers={"x-api-key": HEDRA_API_KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Hedra {method} {path} → {e.code}: {e.read().decode()}")

def hedra_get_model_id():
    models = hedra_req("GET", "/models")
    if not models:
        raise RuntimeError("No Hedra models returned")
    print(f"  [Hedra] {len(models)} models available:", flush=True)
    for m in models:
        print(f"    id={m['id']} name={m.get('name','?')} type={m.get('type','?')}", flush=True)
    # Priority order: Hedra Character 3 > Hedra Character > Hedra Avatar > Hedra Omnia
    for priority in ["hedra character 3", "hedra character", "hedra avatar", "hedra omnia"]:
        for m in models:
            if priority in m.get("name", "").lower():
                print(f"  [Hedra] selected model: {m.get('name', m['id'])}", flush=True)
                return m["id"]
    raise RuntimeError(f"No Hedra avatar model found in {len(models)} models")

def hedra_get_voice_id():
    voices = hedra_req("GET", "/voices")
    if not voices:
        raise RuntimeError("No Hedra voices returned")
    print(f"  [Hedra] {len(voices)} voices available, using first: {voices[0].get('name', voices[0]['id'])}", flush=True)
    return voices[0]["id"]

def hedra_upload_avatar(image_path):
    """Create an image asset on Hedra and upload the file. Returns asset_id."""
    asset_id = hedra_req("POST", "/assets", {"name": "avatar.jpg", "type": "image"})["id"]
    with open(image_path, "rb") as f:
        img_data = f.read()
    boundary = "----campusclipboundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="avatar.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + img_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        HEDRA_BASE + f"/assets/{asset_id}/upload",
        data=body,
        headers={
            "x-api-key":    HEDRA_API_KEY,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    urllib.request.urlopen(req, timeout=60)
    return asset_id

def hedra_submit(script, model_id, voice_id, image_asset_id):
    resp = hedra_req("POST", "/generations", {
        "type":             "video",
        "ai_model_id":      model_id,
        "start_keyframe_id": image_asset_id,
        "generated_video_inputs": {
            "text_prompt":  "natural confident speaking, slight head movement",
            "resolution":   "720p",
            "aspect_ratio": "9:16",
        },
        "audio_generation": {
            "voice_id": voice_id,
            "text":     script,
        },
    })
    gen_id = resp["id"]
    print(f"  [Hedra] queued generation_id={gen_id}", flush=True)
    return gen_id

def hedra_wait(gen_id, out_path, timeout=900):
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = hedra_req("GET", f"/generations/{gen_id}/status")
        status = resp.get("status", "")
        print(f"  [Hedra] status: {status}", flush=True)
        if status == "complete":
            url = resp["download_url"]
            urllib.request.urlretrieve(url, str(out_path))
            print(f"  [Hedra] saved → {out_path}", flush=True)
            return
        if status == "error":
            raise RuntimeError(f"Hedra error: {resp.get('error_message')}")
        time.sleep(10)
    raise RuntimeError(f"Hedra timeout for {gen_id}")

# ── Kling via PiAPI ────────────────────────────────────────────────────────────
def piapi_req(method, path, body=None):
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        PIAPI_BASE + path, data=data, method=method,
        headers={"x-api-key": PIAPI_KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"PiAPI {method} {path} → {e.code}: {e.read().decode()}")

def kling_generate_clip(prompt, out_path, duration=5, timeout=600):
    print(f"  [Kling] submitting clip...", flush=True)
    print(f"  [Kling] prompt: {prompt[:90]}", flush=True)
    resp = piapi_req("POST", "/api/v1/task", {
        "model":     "kling",
        "task_type": "video_generation",
        "input": {
            "prompt":          prompt,
            "negative_prompt": "blurry, low quality, text overlay, logos, watermark",
            "duration":        duration,
            "aspect_ratio":    "9:16",
            "mode":            "std",
            "version":         "1.6",
        },
    })
    task_id = resp["data"]["task_id"]
    print(f"  [Kling] task_id={task_id}", flush=True)

    deadline = time.time() + timeout
    while time.time() < deadline:
        r      = piapi_req("GET", f"/api/v1/task/{task_id}")
        status = r["data"]["status"]
        print(f"  [Kling] status: {status}", flush=True)
        if status == "completed":
            url = r["data"]["output"]["works"][0]["video"]["resource_without_watermark"]
            urllib.request.urlretrieve(url, str(out_path))
            print(f"  [Kling] saved → {out_path}", flush=True)
            return
        if status == "failed":
            raise RuntimeError(f"Kling failed: {r['data'].get('error')}")
        time.sleep(15)
    raise RuntimeError(f"Kling timeout for task {task_id}")

# ── ffmpeg compositing ─────────────────────────────────────────────────────────
# Phone mockup — positioned in the bottom-right of the avatar section
PH_W, PH_H = 280, 560
PH_X, PH_Y = 780, 1330
BORDER      = 10

# Frame split: top 55% = Kling B-roll, bottom 45% = Hedra avatar
BROLL_H  = 1056   # 1920 * 0.55
AVATAR_H = 864    # 1920 * 0.45

def get_screen_scaled(screen_name):
    src = TMP_DIR / f"screen_{screen_name}.jpg"
    dst = TMP_DIR / f"screen_{screen_name}_scaled.png"
    if not dst.exists():
        if not src.exists():
            urllib.request.urlretrieve(SCREENS[screen_name], str(src))
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

def composite_scene(kling_clip, hedra_clip, screen_name, out):
    """
    [0] Kling B-roll  → top BROLL_H  pixels (loops to match avatar duration)
    [1] Hedra avatar  → bottom AVATAR_H pixels (face/shoulders crop from top)
    [2] App screenshot → phone mockup bottom-right of avatar section
    Audio from Hedra clip.
    """
    screen_scaled = get_screen_scaled(screen_name)

    fc = (
        # Kling: scale to 1080 x BROLL_H
        f"[0:v]scale=1080:{BROLL_H}:force_original_aspect_ratio=decrease,"
        f"pad=1080:{BROLL_H}:(ow-iw)/2:(oh-ih)/2,setsar=1[broll];"

        # Hedra: scale to 1080x1920 then crop the top AVATAR_H px (face area)
        f"[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,crop=1080:{AVATAR_H}:0:0,setsar=1[face];"

        # Stack B-roll (top) + avatar (bottom)
        f"[broll][face]vstack=inputs=2[stacked];"

        # White phone bezel
        f"[stacked]drawbox="
        f"x={PH_X - BORDER}:y={PH_Y - BORDER}:w={PH_W}:h={PH_H}:"
        f"color=white:t=fill[boxed];"

        # App screenshot overlay
        f"[boxed][2:v]overlay=x={PH_X}:y={PH_Y}[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(kling_clip),   # [0] B-roll, looped
        "-i", str(hedra_clip),                          # [1] avatar + audio
        "-loop", "1", "-i", str(screen_scaled),         # [2] screenshot
        "-filter_complex", fc,
        "-map", "[out]",
        "-map", "1:a?",
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100",
        "-r", "24", "-shortest",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if r.returncode != 0:
        print(f"  [ffmpeg] stderr:\n{r.stderr[-2000:]}", flush=True)
        raise RuntimeError("composite_scene failed")
    print(f"  [ffmpeg] composited → {out}", flush=True)

def concat_clips(paths, out):
    list_file = TMP_DIR / "concat.txt"
    list_file.write_text("\n".join(f"file '{Path(p).resolve()}'" for p in paths))
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
                "kling": (
                    f"University student frantically switching between apps on laptop and phone, "
                    f"stressed overwhelmed expression, multiple browser tabs, dorm room, {STYLE}"
                ),
                "screen": "dashboard",
            },
            {
                "script": (
                    "Managing your classes, clubs, and campus life across five different apps — "
                    "manually entering everything yourself — is eating your time. "
                    "Every syllabus, every deadline, every club meeting. Typed in by hand."
                ),
                "kling": (
                    f"Close-up of student's hands slowly typing schedule into Google Calendar, "
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
                "kling": (
                    f"Student's face going from stressed to genuinely relieved and happy, "
                    f"looking at phone, warm light, relaxed posture, {STYLE}"
                ),
                "screen": "calendar",
            },
            {
                "script": "CampusClip. Coming to Western this August. Link in bio.",
                "kling": (
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
                "kling": (
                    f"Two university students side by side — one frustrated at laptop typing slowly, "
                    f"one relaxed holding phone smiling, contrasting, campus library, {STYLE}"
                ),
                "screen": "class",
            },
            {
                "script": (
                    "Upload your syllabus, and CampusClip automatically builds your entire "
                    "academic schedule for you. No more copy-paste. No more missing deadlines."
                ),
                "kling": (
                    f"Student uploading a document on phone, then looking amazed as information "
                    f"fills the screen, satisfying reveal, bright study space, {STYLE}"
                ),
                "screen": "calendar",
            },
            {
                "script": (
                    "Your academics, your clubs, your campus events, your social feed — "
                    "all in one app."
                ),
                "kling": (
                    f"Student casually scrolling phone with a smile, relaxed on campus bench, "
                    f"{CAMPUS}, autumn, everything under control, {STYLE}"
                ),
                "screen": "feed",
            },
            {
                "script": "The future of student life at Western. Coming August 2026.",
                "kling": (
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
                "kling": (
                    f"University student looking at phone thoughtfully, curious expression, "
                    f"face lighting up, {CAMPUS} background, {STYLE}"
                ),
                "screen": "dashboard",
            },
            {
                "script": (
                    "Your class schedule — auto-built from your syllabus. "
                    "Your assignments and deadlines — tracked automatically."
                ),
                "kling": (
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
                "kling": (
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
                "kling": (
                    f"Student relaxed on campus grass, laptop open, phone in hand, "
                    f"completely at ease, {CAMPUS} golden hour, {STYLE}"
                ),
                "screen": "feed",
            },
        ],
    },
]

# ── Main pipeline ──────────────────────────────────────────────────────────────
def generate_ad(ad):
    name   = ad["name"]
    scenes = ad["scenes"]
    print(f"\n{'='*60}\nGenerating: {name}  ({len(scenes)} scenes)\n{'='*60}", flush=True)

    if not HEDRA_API_KEY:
        raise RuntimeError("HEDRA_API_KEY not set — get it from hedra.com/api-profile")
    if not PIAPI_KEY:
        raise RuntimeError("PIAPI_KEY not set — get it from piapi.ai workspace")
    if not HEDRA_AVATAR_URL:
        raise RuntimeError(
            "HEDRA_AVATAR_URL not set — provide a public URL to a portrait JPG "
            "(the face used for the avatar)"
        )

    # One-time setup: download avatar image, upload to Hedra, get model/voice IDs
    print("\n[Setup] Fetching Hedra model + voice + uploading avatar...", flush=True)
    model_id  = hedra_get_model_id()
    voice_id  = hedra_get_voice_id()
    avatar_img = TMP_DIR / "avatar.jpg"
    if not avatar_img.exists():
        urllib.request.urlretrieve(HEDRA_AVATAR_URL, str(avatar_img))
        print(f"  [Hedra] avatar image saved → {avatar_img}", flush=True)
    image_asset_id = hedra_upload_avatar(avatar_img)
    print(f"  [Hedra] model={model_id}  voice={voice_id}  image_asset={image_asset_id}", flush=True)

    composited = []
    for i, scene in enumerate(scenes):
        print(f"\n── Scene {i+1}/{len(scenes)} ──", flush=True)

        hedra_clip = TMP_DIR / f"{name}_hedra_{i:02d}.mp4"
        kling_clip = TMP_DIR / f"{name}_kling_{i:02d}.mp4"
        comp_clip  = TMP_DIR / f"{name}_comp_{i:02d}.mp4"

        # A: Hedra avatar speaking this scene's script
        if hedra_clip.exists():
            print(f"  [Hedra] using cached {hedra_clip.name}", flush=True)
        else:
            gen_id = hedra_submit(scene["script"], model_id, voice_id, image_asset_id)
            hedra_wait(gen_id, hedra_clip)

        # B: Kling cinematic B-roll for this scene
        if kling_clip.exists():
            print(f"  [Kling] using cached {kling_clip.name}", flush=True)
        else:
            kling_generate_clip(scene["kling"], kling_clip, duration=5)

        # C: Composite
        composite_scene(kling_clip, hedra_clip, scene["screen"], comp_clip)
        composited.append(str(comp_clip))

    # D: Concatenate all scenes
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
