#!/usr/bin/env python3
"""Knight attack fix round A1 (2026-10-31): review jobs and encodes (same three-panel cameras as attacks-20261031).

  attacks_a1.py jobs [CLIP ...]     Local/knight-review-20261028/attacks-a1-20261031/jobs.json (render_review.py format):
                                    after-<Clip> = A1 GLB at its gameplay rate; framing, display mesh, blend identical to
                                    the attacks-20261031 cur-* jobs (round-5 framing: 810 px per view, ortho 3.2)
  attacks_a1.py encode [CLIP ...]   media/before-<Clip>.mp4 (byte copy of attacks-20261031/media/cur-<Clip>.mp4),
                                    media/after-<Clip>.mp4 (front | side | three-quarter hstack, all-intra crf 12),
                                    media/ba-<Clip>.mp4 (BEFORE on top, AFTER below, each labeled in the top-left corner;
                                    the shorter clip holds its last frame), media/index.html
Render step (GPU, through the slot): render_attacks_a1.sh."""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "Local/knight-review-20261028/attacks-20261031"
REV = ROOT / "Local/knight-review-20261028/attacks-a1-20261031"
A1 = ROOT / "Local/CustomuseAssets/AttacksA1-20261031/knight"
ORDER = ["LightAttack", "HeavyAttack", "HeavyAttackAlternate", "LightAttackTwoHand", "HeavyAttackTwoHand",
         "HeavyAttackTwoHandAlternate", "LightCombo"]
FONT = "/System/Library/Fonts/Helvetica.ttc"


def jobs(clips):
    old = {j["label"]: j for j in json.loads((OLD / "jobs.json").read_text())}
    out = []
    for clip in clips:
        meta = json.loads((A1 / (clip + "_A1.json")).read_text()); ref = old["cur-" + clip]
        j = dict(ref, label="after-" + clip, segments=[{"glb": meta["file"], "start": 0, "end": meta["duration"], "rate": meta["gameplayPlayRate"],
                                                         "loop": False, "even": True}])
        out.append(j)
    REV.mkdir(parents=True, exist_ok=True)
    (REV / "jobs.json").write_text(json.dumps(out, indent=1) + "\n"); print(len(out), "jobs", [j["label"] for j in out])


def run(cmd):
    subprocess.run(cmd, check=True)


def encode(clips):
    media = REV / "media"; media.mkdir(parents=True, exist_ok=True)
    for clip in clips:
        fr = REV / "frames" / ("after-" + clip)
        if not (fr / "threequarter_0000.png").exists():
            print("NO FRAMES", clip); continue
        before = media / ("before-%s.mp4" % clip); after = media / ("after-%s.mp4" % clip); ba = media / ("ba-%s.mp4" % clip)
        shutil.copyfile(OLD / "media" / ("cur-%s.mp4" % clip), before)
        cmd = ["ffmpeg", "-loglevel", "error", "-y"]
        for v in ("front", "side", "threequarter"):
            cmd += ["-framerate", "30", "-i", str(fr / (v + "_%04d.png"))]
        cmd += ["-filter_complex", "[0][1][2]hstack=inputs=3", "-c:v", "libx264", "-crf", "12", "-g", "1", "-bf", "0", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", "-r", "30", str(after)]
        run(cmd)
        nb = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(before)],
                                capture_output=True, text=True).stdout.strip())
        na = len(list(fr.glob("front_*.png"))); n = max(na, nb)
        lab = "drawtext=fontfile=%s:text=%s:x=24:y=20:fontsize=44:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=10"
        fc = ("[0:v]tpad=stop_mode=clone:stop=%d,%s[b];[1:v]tpad=stop_mode=clone:stop=%d,%s[a];[b][a]vstack=inputs=2[v]"
              % (n - nb, lab % (FONT, "BEFORE"), n - na, lab % (FONT, "AFTER")))
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(before), "-i", str(after), "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n),
             "-c:v", "libx264", "-crf", "14", "-g", "1", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-r", "30", str(ba)])
        print("ENCODED", clip, "before", nb, "after", na, "frames", flush=True)
    done = [c for c in ORDER if (media / ("ba-%s.mp4" % c)).exists()]
    html = ["<!doctype html><meta charset=utf-8><title>knight attacks A1</title><style>body{background:#111;color:#eee;font:16px -apple-system,Helvetica,sans-serif;margin:24px}"
            "h2{font-weight:600;font-size:16px;margin:22px 0 6px}video{width:100%;max-width:1600px;background:#000;border-radius:8px;display:block}</style>"]
    for c in done:
        html.append('<h2>%s</h2><video src="ba-%s.mp4" controls loop muted playsinline preload="metadata"></video>' % (c, c))
    (media / "index.html").write_text("\n".join(html) + "\n"); print("index.html", len(done))


if __name__ == "__main__":
    mode = sys.argv[1]; clips = sys.argv[2:] or [c for c in ORDER if (A1 / (c + "_A1.glb")).exists()]
    {"jobs": jobs, "encode": encode}[mode](clips)
