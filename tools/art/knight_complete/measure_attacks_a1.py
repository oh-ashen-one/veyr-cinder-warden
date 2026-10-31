#!/usr/bin/env python3
"""Knight attack fix round A1 (2026-10-31): pass-test metrics (plain CPython/numpy + OpenCV, no Blender, no GPU).

  measure_attacks_a1.py metrics OUT.json            analytic metrics, before (runtime) and after (A1) of every clip
  measure_attacks_a1.py video MEDIA_DIR OUT.json    critic-replica video metrics on before-/after-<Clip>.mp4
  measure_attacks_a1.py preview OUT.png CLIP ...    stick-figure front/side strips (before above after), every 2nd frame

Analytic metrics sample each GLB exactly like render_review.py (even sampling at the gameplay rate, 30 fps) and project
the blade centroid with the review cameras (hips-follow focus, ortho 3.2 m over 810 px), so speeds are in the critic's
px/frame (max over the three panels). Frames are 0-based rendered frames.

Pass tests (critique-attacks.md):
  stops      inside the active swing (first frame >= 10 px/f .. last damage window end + 4 f): no run of >= 2 consecutive
             frames < 3 px/f, and no identical consecutive poses (max joint/blade move < 0.05 game cm)
  freeze     anywhere before the last 4 frames: no run of >= 6 frames < 1 px/f (statue holds)
  recovery   (last damage window end + 4 f .. end): peak <= 40 % of the strike peak, and the recovery does not retrace the
             strike: the blade tip's azimuth around the hips over the strike (peak +-3 f) vs the azimuth the recovery sweeps
             BACK while the tip is inside the strike's height band (+-30 cm); retraceFraction = back / strike, pass < 0.25
  hipsDrop   heavy slots: hips height drop in the strike window vs frame 0 (game cm) and in side-view px; pass >= 10 cm
  readyPose  frame 0 and last frame vs the ready pose (approved idle frame 0 of the grip): max of hips, head, hands,
             feet distance (game cm), pass <= 3 cm; the blade tip distance is reported separately (grip fit)
  footSkate  per foot: max horizontal speed (game cm per rendered frame) of the planted contact (toe if the toe is down,
             else the ankle) while it is planted (toe z < 6 cm or ankle within 4 cm of its lowest); pass <= 1.5
  grip       max change of the RightHand->WeaponSocket transform over the clip (game cm / deg); one-hand pass <= 0.5 cm
  ground     lowest sword point over the clip (game cm); pass >= 0"""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a1_core as c  # noqa: E402

ROOT = c.ROOT
CM = c.CM
RT = {r["clip"]: r for r in json.loads((ROOT / "docs/knight-complete-20261028/attacks-20261031/runtime-attacks.json").read_text())["clips"]}
A1 = ROOT / "Local/CustomuseAssets/AttacksA1-20261031/knight"
GRIP = {"LightAttack": "one", "HeavyAttack": "one", "HeavyAttackAlternate": "one", "LightAttackTwoHand": "two",
        "HeavyAttackTwoHand": "two", "HeavyAttackTwoHandAlternate": "two", "LightCombo": "two"}
HEAVY = {"HeavyAttack", "HeavyAttackAlternate", "HeavyAttackTwoHand", "HeavyAttackTwoHandAlternate"}
KEYJ = ["Hips", "Head", "LeftHand", "RightHand", "LeftFoot", "RightFoot"]


def runs(mask):
    out, i = [], 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j + 1 < len(mask) and mask[j + 1]:
                j += 1
            out.append((i, j)); i = j + 1
        else:
            i += 1
    return out


def sample(glb, rate):
    k = c.Clip(glb); t = c.render_times(k.duration, rate); P = k.sample(t); W = c.fk(k, P)
    return k, t, W


def ready_world(grip):
    k = c.Clip(c.IDLE[grip]); return c.fk(k, k.sample([0.0]))


def analyze(clip, glb, rate, windows):
    k, t, W = sample(glb, rate); F = len(t)
    B = c.blade_world(W); Hb = c.hips_b(W); P = c.project(B, Hb)
    sp = {v: np.r_[0, np.linalg.norm(np.diff(P[v], axis=0), axis=1)] for v in P}
    speed = np.max(np.stack(list(sp.values())), 0)
    fr = lambda s: s / rate * c.FPS                                   # clip seconds -> rendered frame
    win = [(fr(a), fr(b)) for a, b in windows]
    first = int(np.argmax(speed >= 10)); last_dmg = int(math.ceil(win[-1][1])); rec0 = min(F - 1, last_dmg + 4)
    strike_mask = np.zeros(F, bool)
    for a, b in win:
        strike_mask[max(0, int(math.floor(a)) - 2):min(F, int(math.ceil(b)) + 3)] = True
    strike_peak = float(speed[strike_mask].max())
    # identical consecutive poses (joints + blade tip), game cm
    pts = np.stack([(c.C[None] @ W[j])[:, :3, 3] for j in KEYJ] + [c.blade_world(W, c.TIP), B], 1) * CM
    move = np.r_[np.inf, np.abs(np.diff(pts, axis=0)).max(axis=(1, 2))]
    active = np.zeros(F, bool); active[first:rec0 + 1] = True
    slow_runs = [(int(a), int(b)) for a, b in runs((speed < 3) & active) if b - a + 1 >= 2 and a > 0]
    ident = [int(i) for i in np.where((move < .05) & active)[0]]
    freeze_runs = [(int(a), int(b)) for a, b in runs(speed < 1) if b - a + 1 >= 6 and a > 0 and b < F - 4]
    # recovery
    rec = np.arange(rec0, F); rec_peak = float(speed[rec].max()) if len(rec) else 0.0
    # retrace: azimuth sweep of the blade tip around the hips (hips-follow camera space). The strike sweeps the azimuth
    # one way; a recovery that sweeps it back at the strike's heights replays the strike backwards.
    Tip = c.blade_world(W, c.TIP); rel = Tip - np.c_[Hb[:, :2], Hb[:, 2] * 0]
    az = np.unwrap(np.arctan2(rel[:, 1], rel[:, 0])); el = rel[:, 2] * CM
    sidx = np.where(strike_mask)[0]
    pk = int(sidx[np.argmax(speed[sidx])]); a_lo = max(sidx[0], pk - 3); a_hi = min(sidx[-1], pk + 3)
    strike_sweep = float(az[a_hi] - az[a_lo]); sgn = np.sign(strike_sweep) or 1.0
    band = (el[a_lo:a_hi + 1].min() - 30, el[a_lo:a_hi + 1].max() + 30)
    back = 0.0
    for i in range(max(rec0, 1), F):
        d = (az[i] - az[i - 1]) * sgn
        if d < 0 and band[0] <= el[i] <= band[1] and band[0] <= el[i - 1] <= band[1]:
            back += -d
    retrace = back / max(abs(strike_sweep), 1e-6)
    moving = [i for i in range(rec0, F) if speed[i] >= .15 * strike_peak]
    # hips drop
    hz = Hb[:, 2] * CM
    sw = np.where(strike_mask)[0]
    drop = float(hz[0] - hz[sw].min()); drop_px = drop / CM / c.ORTHO * c.RES
    # ready pose
    R = ready_world(GRIP[clip]); idle_pts = np.stack([(c.C @ R[j][0])[:3, 3] for j in KEYJ] + [c.blade_world(R, c.TIP)[0]], 0) * CM
    def dist(i, blade=False):
        d = np.linalg.norm(pts[i, :len(KEYJ) + 1] - idle_pts, axis=1)
        return float(d[len(KEYJ)] if blade else d[:len(KEYJ)].max())
    # foot skate
    skate = {}
    for s in ("Left", "Right"):
        toe = (c.C[None] @ W[s + "ToeBase"])[:, :3, 3] * CM; ank = (c.C[None] @ W[s + "Foot"])[:, :3, 3] * CM
        toe_down = toe[:, 2] < 6; heel_down = ank[:, 2] < ank[:, 2].min() + 4
        worst = 0.0; worst_f = None
        for i in range(1, F):
            for ok, p in ((toe_down, toe), (heel_down, ank)):
                if ok[i] and ok[i - 1]:
                    v = float(np.linalg.norm(p[i, :2] - p[i - 1, :2]))
                    if v > worst:
                        worst, worst_f = v, i
        skate[s] = {"maxPlantedSlideCmPerFrame": round(worst, 2), "frame": worst_f}
    # grip
    G = np.linalg.inv(W["RightHand"]) @ W["WeaponSocket"]
    gt = float(np.linalg.norm((W["RightHand"][:, :3, :3] @ (G[:, :3, 3] - G[0, :3, 3])[..., None])[..., 0], axis=1).max() * CM)
    rel = [Rotation.from_matrix(G[i, :3, :3] / np.linalg.norm(G[i, :3, :3], axis=0)) * Rotation.from_matrix(G[0, :3, :3] / np.linalg.norm(G[0, :3, :3], axis=0)).inv() for i in range(F)]
    gr = float(max(r.magnitude() for r in rel) * 180 / math.pi)
    # ground
    M = c.C[None] @ W["WeaponSocket"]; sw_pts = np.einsum("fij,pj->fpi", M[:, :3, :3], c._PTS[::12]) + M[:, None, :3, 3]
    ground = float(sw_pts[:, :, 2].min() * CM)
    res = {
        "glb": str(Path(glb).relative_to(ROOT)), "sha256": c.sha256(glb), "rate": rate, "frames": F, "damageFrames": [[round(a, 1), round(b, 1)] for a, b in win],
        "bladeSpeedPxPerFrame": [round(float(x), 1) for x in speed],
        "activeSwingFrames": [first, rec0], "strikePeakPx": round(strike_peak, 1), "strikePeakFrame": int(sidx[np.argmax(speed[sidx])]),
        "stops": {"slowRuns": slow_runs, "identicalFrames": ident, "pass": not slow_runs and not ident},
        "freeze": {"runsBelow1px": freeze_runs, "pass": not freeze_runs},
        "recovery": {"frames": [int(rec0), F - 1], "peakPx": round(rec_peak, 1), "peakOverStrike": round(rec_peak / max(strike_peak, 1e-9), 3),
                     "retraceFraction": round(retrace, 3), "strikeSweepDeg": round(abs(strike_sweep) * 180 / math.pi, 1),
                     "reverseSweepInStrikeBandDeg": round(back * 180 / math.pi, 1), "strikeTipHeightBandCm": [round(band[0], 1), round(band[1], 1)],
                     "pass": rec_peak <= .4 * strike_peak and retrace < .25},
        "hipsDrop": {"cm": round(drop, 1), "sideViewPx": round(drop_px, 1), "hipsStartCm": round(float(hz[0]), 1), "pass": drop >= 10 if clip in HEAVY else None},
        "readyPose": {"startCm": round(dist(0), 1), "endCm": round(dist(F - 1), 1), "bladeTipStartCm": round(dist(0, True), 1),
                      "bladeTipEndCm": round(dist(F - 1, True), 1), "pass": dist(0) <= 3 and dist(F - 1) <= 3},
        "footSkate": dict(skate, **{"pass": all(v["maxPlantedSlideCmPerFrame"] <= 1.5 for v in skate.values())}),
        "grip": {"maxShiftCm": round(gt, 2), "maxRotDeg": round(gr, 2), "pass": gt <= .5 and gr <= 1.0 if GRIP[clip] == "one" else None},
        "groundMinCm": round(ground, 1), "groundPass": ground >= 0,
    }
    return res


def after_meta(clip):
    m = json.loads((A1 / (clip + "_A1.json")).read_text()); return m


def metrics(out):
    data = {"date": "2026-10-31", "method": __doc__.split("Pass tests")[0].strip(), "clips": {}}
    for clip, r in RT.items():
        row = {"before": analyze(clip, ROOT / r["glb"], r["gameplayPlayRate"], r["damageWindowsClipSeconds"])}
        if (A1 / (clip + "_A1.glb")).exists():
            m = after_meta(clip)
            row["after"] = analyze(clip, A1 / (clip + "_A1.glb"), m["gameplayPlayRate"], m["damageWindowsClipSeconds"])
        data["clips"][clip] = row
        b = row["before"]; a = row.get("after")
        def line(x):
            return ("strike %5.0f rec %.2f retr %.2f stops %s ident %d freeze %s drop %5.1f ready %4.1f/%4.1f skate %4.1f/%4.1f grip %.2f/%.1f ground %5.1f" % (
                x["strikePeakPx"], x["recovery"]["peakOverStrike"], x["recovery"]["retraceFraction"], x["stops"]["slowRuns"], len(x["stops"]["identicalFrames"]),
                x["freeze"]["runsBelow1px"], x["hipsDrop"]["cm"], x["readyPose"]["startCm"], x["readyPose"]["endCm"], x["footSkate"]["Left"]["maxPlantedSlideCmPerFrame"],
                x["footSkate"]["Right"]["maxPlantedSlideCmPerFrame"], x["grip"]["maxShiftCm"], x["grip"]["maxRotDeg"], x["groundMinCm"]))
        print("%-28s BEFORE %s" % (clip, line(b)))
        if a:
            print("%-28s AFTER  %s" % ("", line(a)))
    Path(out).write_text(json.dumps(data, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n")


# ------------------------------------------------------------------------------------------------ stick preview
BONES = [("Hips", "Spine"), ("Spine", "Spine1"), ("Spine1", "Spine2"), ("Spine2", "Neck"), ("Neck", "Head"),
         ("Spine2", "LeftShoulder"), ("LeftShoulder", "LeftArm"), ("LeftArm", "LeftForeArm"), ("LeftForeArm", "LeftHand"),
         ("Spine2", "RightShoulder"), ("RightShoulder", "RightArm"), ("RightArm", "RightForeArm"), ("RightForeArm", "RightHand"),
         ("Hips", "LeftUpLeg"), ("LeftUpLeg", "LeftLeg"), ("LeftLeg", "LeftFoot"), ("LeftFoot", "LeftToeBase"),
         ("Hips", "RightUpLeg"), ("RightUpLeg", "RightLeg"), ("RightLeg", "RightFoot"), ("RightFoot", "RightToeBase")]


def preview(out, items, step=2, views=("front", "side"), cell=200, per_line=16):
    """Stick figures (white spine, blue left, red right limbs, orange blade points), hips-follow review cameras.
    Each item gets len(views) strips per line of `per_line` frames, wrapped."""
    from PIL import Image, ImageDraw
    rows = []
    for glb, rate, label in items:
        k, t, W = sample(glb, rate); rows.append((W, label, len(t)))
    nmax = max(r[2] for r in rows); lines = (len(range(0, nmax, step)) + per_line - 1) // per_line
    H = lines * len(rows) * len(views)
    img = Image.new("RGB", (per_line * cell, H * cell), (20, 22, 26)); d = ImageDraw.Draw(img)
    sc = cell / 810 * 1.3
    for ri, (W, label, n) in enumerate(rows):
        hb = c.hips_b(W)
        for vi, v in enumerate(views):
            for ci, f in enumerate(range(0, n, step)):
                line, col_i = divmod(ci, per_line)
                y0 = ((line * len(rows) + ri) * len(views) + vi) * cell; x0 = col_i * cell
                def pj(p):
                    q = c.project(p[None], hb[f:f + 1])[v][0]; return (x0 + cell / 2 + q[0] * sc, y0 + cell * .70 - q[1] * sc)
                gy = c.project(np.array([[hb[f, 0], hb[f, 1], 0.0]]), hb[f:f + 1])[v][0][1]
                d.line([(x0, y0 + cell * .70 - gy * sc), (x0 + cell, y0 + cell * .70 - gy * sc)], fill=(60, 60, 60))
                M = (c.C @ W["WeaponSocket"][f]); bl = (M[:3, :3] @ c.BLADE[::25].T).T + M[:3, 3]
                for p in bl:
                    x, y = pj(p); d.point((x, y), fill=(200, 130, 60))
                for a, b in BONES:
                    pa = (c.C @ W[a][f])[:3, 3]; pb = (c.C @ W[b][f])[:3, 3]
                    col = (120, 170, 255) if "Left" in b else (255, 140, 140) if "Right" in b else (220, 220, 220)
                    d.line([pj(pa), pj(pb)], fill=col, width=2)
                d.text((x0 + 3, y0 + 2), "%s %s f%d" % (label, v[0], f), fill=(200, 200, 200))
    img.save(out)



# ------------------------------------------------------------------------------------------------ critic-replica video metrics
def video_metrics(mp4):
    """Critic method on the review mp4 (2430x810, three 810-px panels): blade = pixels with R - B > 18; per panel the
    blade-pixel centroid speed (px/frame), max over panels; exact-duplicate consecutive frames (max abs diff 0)."""
    import cv2
    cap = cv2.VideoCapture(str(mp4)); prev = None; cents = []; dup = []; i = 0; areas = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        fr = fr.astype(np.int16); row = []; ar = []
        for p in range(3):
            pan = fr[:, p * 810:(p + 1) * 810]; m = (pan[:, :, 2] - pan[:, :, 0]) > 18
            ys, xs = np.nonzero(m); ar.append(int(m.sum()))
            row.append((xs.mean(), ys.mean()) if len(xs) > 30 else (np.nan, np.nan))
        cents.append(row); areas.append(ar)
        if prev is not None and np.abs(fr - prev).max() == 0:
            dup.append(i)
        prev = fr; i += 1
    C = np.array(cents, float)
    sp = np.r_[np.zeros((1, 3)), np.linalg.norm(np.diff(C, axis=0), axis=2)]
    speed = np.nanmax(np.where(np.isnan(sp), -1, sp), axis=1); speed[speed < 0] = np.nan
    return {"frames": i, "bladeSpeedPxPerFrame": [None if np.isnan(x) else round(float(x), 1) for x in speed], "identicalFrames": dup,
            "bladeAreaPx": areas}


def video(media, out):
    data = {"date": "2026-10-31", "method": video_metrics.__doc__, "clips": {}}
    for clip in RT:
        row = {}
        for side in ("before", "after"):
            f = Path(media) / ("%s-%s.mp4" % (side, clip))
            if not f.exists():
                continue
            v = video_metrics(f); sp = np.array([np.nan if x is None else x for x in v["bladeSpeedPxPerFrame"]])
            meta = RT[clip] if side == "before" else after_meta(clip)
            rate = meta["gameplayPlayRate"]; wins = meta["damageWindowsClipSeconds"]
            fr = lambda x: x / rate * c.FPS
            first = int(np.nanargmax(sp >= 10)); rec0 = min(len(sp) - 1, int(math.ceil(fr(wins[-1][1]))) + 4)
            strike = np.zeros(len(sp), bool)
            for a, b in wins:
                strike[max(0, int(fr(a)) - 2):int(math.ceil(fr(b))) + 3] = True
            pk = float(np.nanmax(sp[strike])); rp = float(np.nanmax(sp[rec0:])) if rec0 < len(sp) else 0.0
            act = np.zeros(len(sp), bool); act[first:rec0 + 1] = True
            slow = [(int(a), int(b)) for a, b in runs((np.nan_to_num(sp, nan=99) < 3) & act) if b - a + 1 >= 2]
            v.update({"strikePeakPx": pk, "recoveryPeakPx": rp, "recoveryOverStrike": round(rp / pk, 3), "activeSwingFrames": [first, rec0],
                      "slowRunsInSwing": slow, "pass": {"stops": not slow and not [d for d in v["identicalFrames"] if act[d]], "recovery40": rp <= .4 * pk}})
            v.pop("bladeAreaPx"); row[side] = v
            print("%-28s %-6s frames %3d strike %5.0f rec/strike %.2f slow %s dup %s" % (clip, side, v["frames"], pk, rp / pk, slow, v["identicalFrames"]))
        data["clips"][clip] = row
    Path(out).write_text(json.dumps(data, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "metrics":
        metrics(sys.argv[2])
    elif mode == "video":
        video(sys.argv[2], sys.argv[3])
    elif mode == "preview":
        items = []
        for clip in sys.argv[3:]:
            if ".glb" in clip:
                rate = float(clip.split("@")[1]) if "@" in clip else 1.0
                items.append((Path(clip.split("@")[0]), rate, Path(clip.split("@")[0]).stem[:14])); continue
            r = RT[clip]; items.append((ROOT / r["glb"], r["gameplayPlayRate"], "B " + clip))
            if (A1 / (clip + "_A1.glb")).exists():
                items.append((A1 / (clip + "_A1.glb"), after_meta(clip)["gameplayPlayRate"], "A " + clip))
        preview(sys.argv[2], items)
