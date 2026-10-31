#!/bin/bash
# Attack review renders (2026-10-31): 7 current runtime attacks + 9 Mixamo candidates, round-5 framing, one mp4 each.
# Prereq: retarget_attacks_20261031.py (Blender, no render) and `attacks_20261031.py normalize` + `jobs`.
# The Blender render goes through the shared GPU slot (capture). Exit 75 = slot busy/skipped, not a crash: wait 300 s, retry (max 4).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$ROOT"
K=tools/art/knight_complete; R=Local/knight-review-20261028/attacks-20261031; mkdir -p "$R/logs"
for attempt in 0 1 2 3 4; do
  "$HOME/.cache/gpu-slot/bin/gpu_slot.sh" capture --label knight-attacks-render --timeout 7200 -- \
    blender --background --factory-startup --python $K/render_review.py -- "$R/jobs.json" "$R" >> "$R/logs/render.log" 2>&1
  rc=$?
  if [ $rc -eq 75 ] && [ $attempt -lt 4 ]; then echo "slot busy (75), retry in 300 s"; sleep 300; continue; fi
  break
done
[ $rc -ne 0 ] && { echo "RENDER FAILED (exit $rc), see $R/logs/render.log"; tail -8 "$R/logs/render.log"; exit 1; }
grep -c '^RENDERED' "$R/logs/render.log"
python3 $K/attacks_20261031.py encode || exit 1
echo DONE
