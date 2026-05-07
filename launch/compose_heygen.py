#!/usr/bin/env python3
"""
compose_heygen.py  —  overlays app screenshots in a phone frame
onto a HeyGen avatar video.

Usage:
  python3 compose_heygen.py <avatar_video.mp4> <output.mp4> \
      <screen_name>:<start>-<end> [<screen_name>:<start>-<end> ...]

Example:
  python3 compose_heygen.py hg01.mp4 hg01_final.mp4 \
      dashboard:0-5 class:5-12 clubs:12-20

Available screen names:
  dashboard, class, clubs, club_page, feed, calendar, search, profile
"""
import sys, subprocess, urllib.request, tempfile, os
from pathlib import Path

RAW = (
    "https://raw.githubusercontent.com/JamesYoung111/marketingskills/"
    "main/launch/app-screenshots"
)
SCREENS = {
    "dashboard": f"{RAW}/IMG_1617.jpeg",
    "class":     f"{RAW}/IMG_1618.jpeg",
    "clubs":     f"{RAW}/IMG_1619.jpeg",
    "club_page": f"{RAW}/IMG_1620.jpeg",
    "feed":      f"{RAW}/IMG_1621.jpeg",
    "calendar":  f"{RAW}/IMG_1622.jpeg",
    "search":    f"{RAW}/IMG_1623.jpeg",
    "profile":   f"{RAW}/IMG_1624.jpeg",
}

# Phone mockup position — bottom-right inset on 1080x1920 frame
PH_W   = 300    # phone width  (pixels)
PH_H   = 600    # phone height
PH_X   = 750    # x offset from left
PH_Y   = 1240   # y offset from top
BORDER = 10     # white bezel thickness


def fetch(url, path):
    if not Path(path).exists():
        urllib.request.urlretrieve(url, path)


def compose(avatar_path, output_path, scenes):
    """
    scenes: list of (screen_name, start_sec, end_sec)
    """
    with tempfile.TemporaryDirectory() as tmp:
        # Download all needed screenshots
        screen_files = {}
        for name, _, _ in scenes:
            p = f"{tmp}/{name}.jpg"
            fetch(SCREENS[name], p)
            screen_files[name] = p

        # Scale each screenshot to the inner phone screen area
        inner_w = PH_W - BORDER * 2
        inner_h = PH_H - BORDER * 2
        scaled = {}
        for name, path in screen_files.items():
            out = f"{tmp}/{name}_scaled.png"
            subprocess.run([
                "ffmpeg", "-y", "-i", path,
                "-vf", f"scale={inner_w}:{inner_h}:force_original_aspect_ratio=decrease,"
                       f"pad={inner_w}:{inner_h}:(ow-iw)/2:(oh-ih)/2",
                out,
            ], capture_output=True, check=True)
            scaled[name] = out

        # Build filter_complex
        # Input 0 = avatar video
        # Inputs 1..N = one scaled screenshot per unique screen
        unique = list(dict.fromkeys(n for n, _, _ in scenes))
        idx = {name: i + 1 for i, name in enumerate(unique)}

        parts = []

        # Start from avatar
        parts.append("[0:v]setsar=1[base]")

        prev = "base"
        for i, (name, t_in, t_out) in enumerate(scenes):
            si = idx[name]
            enable = f"'between(t,{t_in},{t_out})'"

            # White border box drawn onto previous stream
            box_label = f"box{i}"
            parts.append(
                f"[{prev}]drawbox="
                f"x={PH_X - BORDER}:y={PH_Y - BORDER}:"
                f"w={PH_W}:h={PH_H}:"
                f"color=white:t=fill:enable={enable}[{box_label}]"
            )

            # Overlay screenshot inside the white box
            out_label = f"v{i}"
            parts.append(
                f"[{box_label}][{si}:v]overlay="
                f"x={PH_X}:y={PH_Y}:enable={enable}[{out_label}]"
            )
            prev = out_label

        # Build the full command
        extra_inputs = []
        for name in unique:
            extra_inputs += ["-loop", "1", "-i", scaled[name]]

        cmd = [
            "ffmpeg", "-y",
            "-i", avatar_path,
            *extra_inputs,
            "-filter_complex", ";".join(parts),
            "-map", f"[{prev}]",
            "-map", "0:a?",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest",
            output_path,
        ]

        print("  compositing phone mockup...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            print(f"  ffmpeg stderr:\n{r.stderr[-2000:]}", flush=True)
            raise RuntimeError("compose failed")
        print(f"  -> {output_path}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    avatar  = sys.argv[1]
    output  = sys.argv[2]
    raw_scenes = sys.argv[3:]

    scenes = []
    for s in raw_scenes:
        # format: screen_name:start-end  e.g. dashboard:0-5
        name, times = s.split(":")
        start, end = times.split("-")
        scenes.append((name, float(start), float(end)))

    compose(avatar, output, scenes)
