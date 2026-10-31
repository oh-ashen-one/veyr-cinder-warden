#!/usr/bin/env python3
"""Attack review set (2026-10-31): current runtime attacks vs licensed Mixamo sword-and-shield candidates on the KnightB rig.

  attacks_20261031.py normalize   structural normalization (normalize_sourced.normalize_file, motion untouched) of the nine
                                  retargeted exports -> Local/CustomuseAssets/Attacks20261031/knight/ + manifest.json
  attacks_20261031.py jobs        writes Local/knight-review-20261028/attacks-20261031/jobs.json (render_review.py format)
  attacks_20261031.py encode      frames -> media/<label>.mp4 (front | side | three-quarter hstack, all-intra) + index.html
Framing = round 5 RollAttack framing (810 px per view, ortho 3.2 rig m, 0.95 game cm/px) so a full blade swing stays in frame,
in place, hips camera, display mesh = the round-5 mesh variant. cur-* play at the in-game rate from docs/.../runtime-attacks.json;
mix-* play at the source rate 1.0 (no gameplay rate has been chosen for candidates)."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art/integration"))
from normalize_approved import GLB  # noqa: E402
from normalize_sourced import normalize_file  # noqa: E402
BASE = ROOT / "Local/CustomuseAssets/Polish20261025"
OUT = ROOT / "Local/CustomuseAssets/Attacks20261031"
REV = ROOT / "Local/knight-review-20261028/attacks-20261031"
EXPORTS = ROOT / "Local/FabRigTesting/Exports"
MIX = [("Attack1", "sword and shield attack.fbx"), ("Attack2", "sword and shield attack (2).fbx"), ("Attack3", "sword and shield attack (3).fbx"),
       ("Attack4", "sword and shield attack (4).fbx"), ("Slash1", "sword and shield slash.fbx"), ("Slash2", "sword and shield slash (2).fbx"),
       ("Slash3", "sword and shield slash (3).fbx"), ("Slash4", "sword and shield slash (4).fbx"), ("Slash5", "sword and shield slash (5).fbx")]
FRAME = {"res": 810, "ortho": 3.2}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def normalize():
    plan = json.loads((BASE / "knight-v030s/import-plan-KnightB.json").read_text())
    canonical = GLB(plan["rig"]["file"]); rows = []
    for key, fbx in MIX:
        f = EXPORTS / ("Mixamo_SS_%s_v1.glb" % key); meta = json.loads(f.with_suffix(".json").read_text()); assert sha(f) == meta["sha256"], key
        out = OUT / "knight" / ("Mixamo_SS_%s_v1.glb" % key)
        if out.exists():
            print("SKIP existing", out.name); continue
        row = normalize_file(f, canonical, out, meta["fps"], None)
        rows.append({"name": key, "source": meta["source"], "sourceFBX": fbx, "provider": "mixamo (free, downloaded earlier)", "retargetExport": str(f.relative_to(ROOT)),
                     "retargetExportSHA256": meta["sha256"], "file": str(out.relative_to(ROOT)), "sha256": row["sha256"], "duration": row["duration"],
                     "maxReconstructionError": row.get("canonicalReconstructionMaxMatrixError"), "handAuthoredMotion": False})
        print("NORMALIZED", key, row["duration"], row.get("canonicalReconstructionMaxMatrixError"), flush=True)
    if rows:
        (OUT / "manifest.json").write_text(json.dumps({"date": "2026-10-31", "note": "plain retarget (retarget.py run(), in place, WeaponSocket on the right hand with the approved walk grip); no weapon fit, no blade arc",
                                                       "clips": rows}, indent=1) + "\n")


def jobs():
    plan = json.loads((BASE / "knight-v030p/import-plan-KnightB.json").read_text())
    display = str(Path(plan["mesh_variants"]["knight_571e0abbfde2720e"]["file"]).relative_to(ROOT))
    rt = json.loads((ROOT / "docs/knight-complete-20261028/attacks-20261031/runtime-attacks.json").read_text())
    out = []
    for c in rt["clips"]:
        d = GLB(ROOT / c["glb"]).duration()
        out.append(dict({"label": "cur-" + c["clip"], "display": display, "blend": .1, "hold": 0, "segments": [
            {"glb": c["glb"], "start": 0, "end": d, "rate": c["gameplayPlayRate"], "loop": False, "even": True}]}, **FRAME))
    for key, _ in MIX:
        p = "Local/CustomuseAssets/Attacks20261031/knight/Mixamo_SS_%s_v1.glb" % key; d = GLB(ROOT / p).duration()
        out.append(dict({"label": "mix-" + key, "display": display, "blend": .1, "hold": 0, "segments": [
            {"glb": p, "start": 0, "end": d, "rate": 1.0, "loop": False, "even": True}]}, **FRAME))
    REV.mkdir(parents=True, exist_ok=True)
    (REV / "jobs.json").write_text(json.dumps(out, indent=1) + "\n"); print(len(out), "jobs")


def encode():
    media = REV / "media"; media.mkdir(parents=True, exist_ok=True); labels = [j["label"] for j in json.loads((REV / "jobs.json").read_text())]
    done = []
    for lab in labels:
        fr = REV / "frames" / lab; views = [v for v in ("front", "side", "threequarter") if (fr / (v + "_0000.png")).exists()]
        if len(views) != 3:
            print("NO FRAMES", lab); continue
        out = media / (lab + ".mp4")
        if not out.exists():
            cmd = ["ffmpeg", "-loglevel", "error", "-y"]
            for v in views:
                cmd += ["-framerate", "30", "-i", str(fr / (v + "_%04d.png"))]
            cmd += ["-filter_complex", "[0][1][2]hstack=inputs=3", "-c:v", "libx264", "-crf", "12", "-g", "1", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-r", "30", str(out)]
            subprocess.run(cmd, check=True)
        done.append(lab); print("ENCODED", out.name, out.stat().st_size)
    html = ["<!doctype html><meta charset=utf-8><title>attacks</title><style>body{background:#111;color:#eee;font:16px -apple-system,Helvetica,sans-serif;margin:24px}"
            "h2{font-weight:600;font-size:16px;margin:22px 0 6px}video{width:100%;max-width:1600px;background:#000;border-radius:8px;display:block}</style>"]
    for lab in done:
        html.append('<h2>%s</h2><video src="%s.mp4" controls loop muted playsinline preload="metadata"></video>' % (lab, lab))
    (media / "index.html").write_text("\n".join(html) + "\n"); print("index.html", len(done), "videos")


{"normalize": normalize, "jobs": jobs, "encode": encode}[sys.argv[1]]()
