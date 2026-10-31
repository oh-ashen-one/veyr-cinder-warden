#!/bin/bash
# Knight attack fix round A1 (2026-10-31): render the after-* review jobs (attacks_a1.py jobs) through the shared GPU slot,
# then encode before/after/stacked mp4s. Usage: render_attacks_a1.sh LABELSUFFIX [CLIP ...]
# Exit 75 from capture = slot busy/skipped (not a crash): wait 300 s and retry (max 4). Never overrides the gate.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$ROOT"
K=tools/art/knight_complete; R=Local/knight-review-20261028/attacks-a1-20261031; mkdir -p "$R/logs"
X="${1:-pilot}"; shift || true
python3 $K/attacks_a1.py jobs "$@" || exit 1
for attempt in 0 1 2 3 4; do
  "$HOME/.cache/gpu-slot/bin/gpu_slot.sh" capture --label "knight-a1-$X" --timeout 7200 -- \
    blender --background --factory-startup --python $K/render_review.py -- "$R/jobs.json" "$R" >> "$R/logs/render-$X.log" 2>&1
  rc=$?
  if [ $rc -eq 75 ] && [ $attempt -lt 4 ]; then echo "slot busy (75), retry in 300 s"; "$HOME/.cache/gpu-slot/bin/gpu_slot.sh" status | head -4; sleep 300; continue; fi
  break
done
[ $rc -ne 0 ] && { echo "RENDER FAILED (exit $rc), see $R/logs/render-$X.log"; tail -8 "$R/logs/render-$X.log"; exit 1; }
grep '^RENDERED\|^SKIP' "$R/logs/render-$X.log" | tail -10
python3 $K/attacks_a1.py encode "$@" || exit 1
echo DONE
