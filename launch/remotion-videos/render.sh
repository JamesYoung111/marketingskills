#!/usr/bin/env bash
set -e
OUT="../videos-v2"
mkdir -p "$OUT"

render() {
  echo "Rendering $1 ($2s)..."
  npx remotion render src/index.ts "$1" "$OUT/$1.mp4" \
    --codec=h264 --crf=18 --log=quiet
  echo "  ✓ $1.mp4"
}

render LaunchHero  30
render StatReveal  18
render FeatureReel 30
render BeforeAfter 21
render GradeTracker 18

echo ""
echo "Done! Videos saved to $OUT/"
ls -lh "$OUT/"
