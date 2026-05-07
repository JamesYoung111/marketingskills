#!/usr/bin/env python3
"""
CampusClip HeyGen Video Generator
Usage: python3 run_heygen.py [list-avatars|list-voices|generate]
"""
import os, sys, json, time, urllib.request, urllib.error
from pathlib import Path

API_KEY  = os.environ.get("HEYGEN_API_KEY", "")
BASE_URL = "https://api.heygen.com"
OUT_DIR  = Path("ai-videos/heygen")
OUT_DIR.mkdir(parents=True, exist_ok=True)

RAW = (
    "https://raw.githubusercontent.com/JamesYoung111/marketingskills/"
    "main/launch/app-screenshots"
)
SCREENS = {
    "dashboard":   f"{RAW}/IMG_1617.jpeg",
    "class":       f"{RAW}/IMG_1618.jpeg",
    "clubs":       f"{RAW}/IMG_1619.jpeg",
    "feed":        f"{RAW}/IMG_1621.jpeg",
    "calendar":    f"{RAW}/IMG_1622.jpeg",
    "search":      f"{RAW}/IMG_1623.jpeg",
}

# ── API helpers ───────────────────────────────────────────────────────────────

def api(method, endpoint, data=None, params=None):
    url = BASE_URL + endpoint
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers={
        "X-Api-Key":     API_KEY,
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HeyGen API {e.code}: {body}")

def download(url, path):
    urllib.request.urlretrieve(url, str(path))
    print(f"  saved -> {path}", flush=True)

# ── Avatar / voice discovery ──────────────────────────────────────────────────

def list_avatars():
    resp = api("GET", "/v2/avatars")
    avatars = resp.get("data", {}).get("avatars", [])
    print(f"\n{'='*60}\n{len(avatars)} avatars available\n{'='*60}")
    for a in avatars:
        print(f"  id={a['avatar_id']:<40} name={a.get('avatar_name','')}")
    return avatars

def list_voices():
    resp = api("GET", "/v2/voices")
    voices = resp.get("data", {}).get("voices", [])
    print(f"\n{'='*60}\n{len(voices)} voices available\n{'='*60}")
    en = [v for v in voices if v.get("language", "").startswith("en")]
    for v in en[:40]:
        print(f"  id={v['voice_id']:<40} name={v.get('name',''):<24} gender={v.get('gender','')}")
    return voices

# ── Video generation ──────────────────────────────────────────────────────────

def make_video(name, script, avatar_id, voice_id, bg_url=None):
    print(f"\nGenerating: {name}", flush=True)
    background = (
        {"type": "image", "url": bg_url}
        if bg_url else
        {"type": "color", "value": "#0A1628"}
    )
    payload = {
        "video_inputs": [{
            "character": {
                "type":         "avatar",
                "avatar_id":    avatar_id,
                "avatar_style": "normal",
            },
            "voice": {
                "type":       "text",
                "input_text": script,
                "voice_id":   voice_id,
                "speed":      1.0,
            },
            "background": background,
        }],
        "dimension":  {"width": 1080, "height": 1920},
        "caption":    True,
        "title":      name,
    }
    resp = api("POST", "/v2/video/generate", payload)
    video_id = resp["data"]["video_id"]
    print(f"  queued video_id={video_id}", flush=True)
    return video_id

def wait_for_video(video_id, timeout=600):
    print(f"  waiting for render...", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = api("GET", "/v1/video_status.get", params={"video_id": video_id})
        status = resp["data"]["status"]
        print(f"  status: {status}", flush=True)
        if status == "completed":
            return resp["data"]["video_url"]
        if status == "failed":
            raise RuntimeError(f"HeyGen render failed: {resp['data'].get('error')}")
        time.sleep(15)
    raise RuntimeError(f"Timeout waiting for {video_id}")

# ── Scripts ───────────────────────────────────────────────────────────────────

VIDEOS = [
    {
        "name":       "hg01_grade_tracker",
        "background": SCREENS["dashboard"],
        "script": (
            "If you're at Western and still using a spreadsheet to track your grades, "
            "you are wasting so much time. "
            "CampusClip tracks everything automatically. "
            "Every assignment, every weight, every deadline — "
            "and you can see your GPA update in real time. "
            "It is completely free for Western students. "
            "Download coming August 2026."
        ),
    },
    {
        "name":       "hg02_transformation",
        "background": SCREENS["class"],
        "script": (
            "First year I genuinely did not know my grade in three of my five classes "
            "until the week before finals. "
            "Canvas shows marks but never your actual average. "
            "I was calculating everything in the hallway before every single exam. "
            "CampusClip changed that completely. "
            "You set your target GPA, enter your marks as you get them, "
            "and it tells you exactly what you need on every upcoming test. "
            "No spreadsheet. No guessing. "
            "Built specifically for Western — your actual courses, your actual clubs. "
            "Free. August 2026."
        ),
    },
    {
        "name":       "hg03_peer_rec",
        "background": SCREENS["dashboard"],
        "script": (
            "If you're starting at Western in September, "
            "download CampusClip before you go. "
            "It tracks your grades automatically, "
            "shows you every club on campus, "
            "and syncs all your deadlines with your courses. "
            "It is the one app I wish I had in first year. "
            "Free for Western students. August 2026."
        ),
    },
    {
        "name":       "hg04_campus_life",
        "background": SCREENS["feed"],
        "script": (
            "There is so much happening at Western and it is all scattered — "
            "Instagram, GroupMe, email from the prof. You miss stuff constantly. "
            "CampusClip puts your classes, your clubs, and your deadlines "
            "all in one feed. "
            "If something is happening at Western, it is in the app. "
            "Free. August 2026. Follow at campusclipapp."
        ),
    },
    {
        "name":       "hg05_clubs",
        "background": SCREENS["clubs"],
        "script": (
            "How many clubs at Western do you actually know about? "
            "There are over two hundred. "
            "Most people join two in first year and never find the rest. "
            "CampusClip has every Western club in one place. "
            "You can browse, follow, and join — "
            "and their posts show up right in your feed "
            "next to your class deadlines. "
            "Launching August 2026. Free for Western students."
        ),
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────

MODE = sys.argv[1] if len(sys.argv) > 1 else "generate"

# Defaults — override via env vars HEYGEN_AVATAR_ID and HEYGEN_VOICE_ID
AVATAR_ID = os.environ.get("HEYGEN_AVATAR_ID", "Daisy-inskirt-20220818")
VOICE_ID  = os.environ.get("HEYGEN_VOICE_ID",  "1bd001e7e50f421d891986aad5158bc8")

if MODE == "list-avatars":
    list_avatars()

elif MODE == "list-voices":
    list_voices()

elif MODE == "generate":
    if not API_KEY:
        print("ERROR: HEYGEN_API_KEY not set", flush=True)
        sys.exit(1)

    print(f"[HEYGEN] avatar={AVATAR_ID}  voice={VOICE_ID}", flush=True)

    for vid in VIDEOS:
        try:
            video_id = make_video(
                vid["name"], vid["script"],
                AVATAR_ID, VOICE_ID,
                vid.get("background"),
            )
            url = wait_for_video(video_id)
            out = OUT_DIR / f"{vid['name']}.mp4"
            download(url, out)
        except Exception as e:
            import traceback
            print(f"  ERROR {vid['name']}: {e}", flush=True)
            traceback.print_exc()

    print("\nDone!", flush=True)

else:
    print(f"Unknown mode: {MODE}. Use list-avatars, list-voices, or generate.")
    sys.exit(1)
