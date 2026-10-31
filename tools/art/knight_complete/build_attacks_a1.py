#!/usr/bin/env python3
"""Knight attack fix round A1 (2026-10-31): author the A1 attack clips in plain CPython/numpy (no Blender, no GPU).

  python3 build_attacks_a1.py [CLIP ...] [--force] [--preview DIR]

Targets: docs/knight-complete-20261028/attacks-20261031/critique-attacks.md (top-3 fixes and pass tests).
Source-first: the Mixamo clips (already retargeted + normalized in Local/CustomuseAssets/Attacks20261031/knight, see
mixamo-retarget-manifest.json) and the current runtime clips stay the motion base. Allowed corrections only: retime and
trim, settle/blend into the game's ready pose (the approved idle frame 0 of that grip), foot plants and lifted steps
(planned contacts, two-bone leg IK, hips shift/drop for reach), the runtime v17 weapon fit (grip) and blade ground
clearance, Hermite bridges over baked stops, a moving settle in place of a statue hold.

Outputs: Local/CustomuseAssets/AttacksA1-20261031/knight/<Clip>_A1.glb (+ .json sidecar). The template for each GLB is
the slot's current runtime GLB, so node list, skin and mesh variant are unchanged; only the animation is replaced.
Everything is authored at 60 Hz in clip seconds; the gameplay rate is in the sidecar (rate = clip s per real s)."""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d, minimum_filter1d, maximum_filter1d
from scipy.spatial.transform import Rotation, Slerp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a1_core as c  # noqa: E402
import r5_core  # noqa: E402

ROOT = c.ROOT
OUT = ROOT / "Local/CustomuseAssets/AttacksA1-20261031/knight"
MIX = ROOT / "Local/CustomuseAssets/Attacks20261031/knight"
RT = json.loads((ROOT / "docs/knight-complete-20261028/attacks-20261031/runtime-attacks.json").read_text())
RUNTIME = {r["clip"]: r for r in RT["clips"]}
HZ = 120
CMR = c.CM                     # game cm per rig m
LEGS = ("Left", "Right")


# ------------------------------------------------------------------------------------------------ helpers
def g2b(v):                    # glTF -> Blender coordinates (x, -z, y)
    v = np.asarray(v); return np.stack([v[..., 0], -v[..., 2], v[..., 1]], -1)


def b2g(v):
    v = np.asarray(v); return np.stack([v[..., 0], v[..., 2], -v[..., 1]], -1)


def idle_pose(grip):
    k = c.Clip(c.IDLE[grip]); return k, k.sample([0.0])


def pchip_map(keys, smooth_s=.05):
    """Monotone time map out_t -> src_t: piecewise linear through (out, src) keys, with the playback speed (its slope)
    gaussian-smoothed over smooth_s so speed changes ease instead of stepping. Returns a callable."""
    k = np.array(keys, float); tt = np.linspace(k[0, 0], k[-1, 0], int((k[-1, 0] - k[0, 0]) * 1000) + 1)
    sp = np.gradient(np.interp(tt, k[:, 0], k[:, 1]), tt)
    sp = gaussian_filter1d(sp, smooth_s * 1000, mode="nearest")
    ss = k[0, 1] + np.concatenate([[0], np.cumsum((sp[1:] + sp[:-1]) / 2 * np.diff(tt))])
    return lambda x: np.interp(x, tt, ss)


def yaw_mat(deg):
    return Rotation.from_euler("y", deg, degrees=True).as_matrix()   # glTF Y up


def foot_track(plan, times, idle_M, side):
    """plan: list of plants (t0, t1, (dx, dy) Blender game-cm offset from the idle ankle, yaw deg, lift_cm of the step INTO
    this plant). Returns ankle [F,3] (glTF rig m), rotation [F,3,3], lifted mask."""
    base = idle_M[:3, 3]; R0 = idle_M[:3, :3] / np.linalg.norm(idle_M[:3, :3], axis=0)
    def spot(p):
        dx, dy = p[2]; return base + b2g(np.array([dx, dy, 0.0])) / CMR
    A = np.zeros((len(times), 3)); Rm = np.zeros((len(times), 3, 3)); lifted = np.zeros(len(times), bool)
    for i, t in enumerate(times):
        cur = None
        for j, p in enumerate(plan):
            if p[0] <= t <= p[1] or (j == 0 and t < p[0]) or (j == len(plan) - 1 and t > p[1]):
                cur = ("plant", p); break
            if j + 1 < len(plan) and p[1] < t < plan[j + 1][0]:
                cur = ("step", p, plan[j + 1]); break
        if cur[0] == "plant":
            A[i] = spot(cur[1]); Rm[i] = yaw_mat(cur[1][3]) @ R0
        else:
            a, b = cur[1], cur[2]; u = (t - a[1]) / (b[0] - a[1])
            h, z = r5_core.step_shape(u, .12, .88, b[4])
            A[i] = spot(a) * (1 - h) + spot(b) * h + np.array([0, z / CMR, 0])
            ra = Rotation.from_matrix(yaw_mat(a[3]) @ R0); rb = Rotation.from_matrix(yaw_mat(b[3]) @ R0)
            Rm[i] = Slerp([0, 1], Rotation.concatenate([ra, rb]))([h]).as_matrix()[0]
            lifted[i] = z > .5
    return A, Rm, lifted


def leg_lengths(clip, pose):
    W = c.fk(clip, c.single(pose, 0)); out = {}
    for s in LEGS:
        H = W[s + "UpLeg"][0, :3, 3]; K = W[s + "Leg"][0, :3, 3]; A = W[s + "Foot"][0, :3, 3]
        out[s] = (np.linalg.norm(K - H), np.linalg.norm(A - K))
    return out


def fit_body_to_feet(clip, pose, targets, reach=.975, smooth_s=.06, drop_extra=None, shift=0.0):
    """Keep the source hips path (optionally shifted by `shift` x the change of the feet midpoint, source-blended ->
    planned), drop the hips where an ankle target is out of reach, then two-bone IK both legs onto the targets."""
    F = c.frames(pose); W = c.fk(clip, pose)
    mid_b = (W["LeftFoot"][:, :3, 3] + W["RightFoot"][:, :3, 3]) / 2
    mid_p = (targets["Left"][0] + targets["Right"][0]) / 2
    D = (mid_p - mid_b) * shift; D[:, 1] = 0
    D = gaussian_filter1d(D, smooth_s * HZ, axis=0, mode="nearest")
    pose["Hips"][0] += D                       # Hips parent is VeyrRoot (identity): local == world
    W = c.fk(clip, pose); L = leg_lengths(clip, pose)
    drop = np.zeros(F)
    for s in LEGS:
        H = W[s + "UpLeg"][:, :3, 3]; T = targets[s][0]; a, b = L[s]; r = (a + b) * reach
        d = T - H; horiz = np.linalg.norm(d[:, [0, 2]], axis=1); vert = -d[:, 1]
        need = np.sqrt(np.maximum(r * r - horiz ** 2, 0)); short = np.maximum(vert - need, 0)
        short[horiz > r] = vert[horiz > r]           # cannot reach at all: drop to the target height (IK clamps)
        drop = np.maximum(drop, short)
    if drop_extra is not None:
        drop = drop + drop_extra
    k = max(1, int(smooth_s * HZ))
    drop = gaussian_filter1d(maximum_filter1d(drop, 2 * k + 1), k, mode="nearest")
    pose["Hips"][0][:, 1] -= drop
    for s in LEGS:
        T, Rm, _ = targets[s]
        c.plant_leg(clip, pose, s, T, Rm, np.ones(F, bool))
    return D, drop


def ground_clearance(clip, pose, clearance_cm=3.0, smooth_s=.05):
    """Rotate the right hand (with the socket following via the grip) about a horizontal axis through the palm so the
    lowest sword point stays >= clearance; the correction angle is max-filtered + smoothed so it eases in/out."""
    W = c.fk(clip, pose); F = c.frames(pose); pts = c._PTS[::12]
    need = np.zeros(F); axes = np.zeros((F, 3))
    for i in range(F):
        M = W["WeaponSocket"][i]; hand = W["RightHand"][i, :3, 3]
        P = (M[:3, :3] @ pts.T).T + M[:3, 3]
        blade = M[:3, :3] @ np.array([0, 1.0, 0]); blade /= np.linalg.norm(blade)
        ax = np.cross(blade, np.array([0, 1.0, 0]))
        if np.linalg.norm(ax) < 1e-6:
            continue
        ax /= np.linalg.norm(ax); axes[i] = ax
        lo = P[:, 1].min() * CMR
        if lo >= clearance_cm:
            continue
        for deg in np.arange(.5, 60, .5):
            R = Rotation.from_rotvec(ax * math.radians(deg)).as_matrix()
            if (((R @ (P - hand).T).T + hand)[:, 1].min() * CMR) >= clearance_cm:
                need[i] = deg; break
    if need.max() == 0:
        return 0.0
    k = int(smooth_s * HZ)
    ang = gaussian_filter1d(maximum_filter1d(need, 2 * k + 1), k, mode="nearest")
    ax_s = gaussian_filter1d(axes, k, axis=0, mode="nearest")
    newH = W["RightHand"].copy()
    for i in range(F):
        if ang[i] < 1e-3:
            continue
        ax = ax_s[i] / max(np.linalg.norm(ax_s[i]), 1e-9); R = Rotation.from_rotvec(ax * math.radians(ang[i])).as_matrix()
        M = newH[i]; sc = np.linalg.norm(M[:3, :3], axis=0); M[:3, :3] = R @ M[:3, :3]
    c.set_world(clip, pose, W, "RightHand", newH)
    return float(need.max())


def attach_socket(clip, pose, G):
    """WeaponSocket world = RightHand world @ G[f] (G [F,4,4] or [4,4])."""
    W = c.fk(clip, pose); G = np.broadcast_to(G, (c.frames(pose), 4, 4))
    c.set_world(clip, pose, W, "WeaponSocket", W["RightHand"] @ G)


def grip_blend(Ga, Gb, w):
    ta = Ga[:3, 3]; tb = Gb[:3, 3]; sa = np.linalg.norm(Ga[:3, :3], axis=0); sb = np.linalg.norm(Gb[:3, :3], axis=0)
    qa = Rotation.from_matrix(Ga[:3, :3] / sa).as_quat(); qb = Rotation.from_matrix(Gb[:3, :3] / sb).as_quat()
    q = c.qslerp(np.tile(qa, (len(w), 1)), np.tile(qb, (len(w), 1)), w); out = np.tile(np.eye(4), (len(w), 1, 1))
    out[:, :3, :3] = Rotation.from_quat(q).as_matrix() * (sa + (sb - sa) * w[:, None])[:, None, :]
    out[:, :3, 3] = ta + (tb - ta) * w[:, None]
    return out


def grip_of(path, t=0.0):
    k = c.Clip(path); W = c.fk(k, k.sample([t])); return (np.linalg.inv(W["RightHand"]) @ W["WeaponSocket"])[0]


# ------------------------------------------------------------------------------------------------ Mixamo compositions
def compose_mixamo(spec):
    """Source body (retimed) blended in from / out to the ready pose, planned feet, v17 grip, ground clearance."""
    src = c.Clip(MIX / ("Mixamo_SS_%s_v1.glb" % spec["source"]))
    idle_clip, I = idle_pose(spec["grip"])
    T_end = spec["duration"]; F = int(round(T_end * HZ)) + 1; t = np.linspace(0, T_end, F)
    tmap = pchip_map(spec["timemap"]); st = np.clip(tmap(t), 0, src.duration)
    P = src.sample(st)
    # body weight: 0 = ready pose, 1 = source
    w = np.ones(F)
    a, b = spec["blend_in"]; w = np.minimum(w, c.smoother((t - a) / (b - a)) if b > a else 1)
    a, b = spec["blend_out"]; w = np.minimum(w, 1 - c.smoother((t - a) / (b - a)))
    w = np.clip(w, 0, 1)
    # per-bone weight overrides (e.g. the sword arm leaves the ready pose later / returns earlier)
    pose = c.blend(c.repeat(I, F), P, w)
    for bones, (a2, b2, a3, b3) in spec.get("arm_blend", []):
        w2 = np.minimum(c.smoother((t - a2) / (b2 - a2)), 1 - c.smoother((t - a3) / (b3 - a3)))
        part = c.blend(c.repeat(I, F), P, w2, bones=set(bones))
        for n in bones:
            pose[n] = part[n]
    if spec.get("hips_scale"):
        # jump height: hips height above the take-off -> landing line scaled by k inside [a, b] (root trajectory correction)
        a, b, k = spec["hips_scale"]; y = pose["Hips"][0][:, 1]
        ia, ib = int(np.searchsorted(t, a)), int(np.searchsorted(t, b))
        base = np.interp(t, [t[ia], t[ib]], [y[ia], y[ib]])
        inside = (t >= t[ia]) & (t <= t[ib])
        pose["Hips"][0][inside, 1] = base[inside] + k * (y[inside] - base[inside])
    Wi = c.fk(idle_clip, I)
    targets = {s: foot_track(spec["feet"][s], t, Wi[s + "Foot"][0], s) for s in LEGS}
    D, drop = fit_body_to_feet(src, pose, targets, drop_extra=spec.get("drop_extra", lambda tt: 0)(t), shift=spec.get("shift", 0.0))
    # weapon: ready-pose grip at the ends, runtime v17 grip in the attack (same weapon fit as LightAttack v17)
    # constant grip for the whole clip (no hand slide along the handle); the game's grip lock covers the crossfade
    G = grip_of(ROOT / RUNTIME["LightAttack"]["glb"]) if spec.get("grip_fit", "v17") == "v17" else grip_of(c.IDLE[spec["grip"]])
    attach_socket(src, pose, G)
    clear = ground_clearance(src, pose)
    attach_socket(src, pose, G)
    info = {"sourceClipSeconds": [float(st[0]), float(st[-1])], "hipsShiftMaxCm": float(np.abs(D).max() * CMR),
            "hipsDropMaxCm": float(drop.max() * CMR), "groundClearanceMaxDeg": clear}
    return src, pose, t, info


# ------------------------------------------------------------------------------------------------ repairs of runtime clips
def hermite_bridge(clip, pose, t, t0, t1, new_len=None, tangent_scale=1.0):
    """Replace the motion inside [t0, t1] by a cubic Hermite bridge between the poses at t0 and t1, using the clip's own
    velocities there (a baked stop/hitch becomes one continuous move). new_len (s) re-times the bridge; the rest of the
    clip after t1 shifts accordingly. Works on the local channels; returns the new pose and times."""
    i0 = int(np.searchsorted(t, t0)); i1 = int(np.searchsorted(t, t1))
    dt = t[1] - t[0]; L_old = t[i1] - t[i0]; L_new = L_old if new_len is None else new_len
    n_new = max(2, int(round(L_new / dt)))
    s = np.linspace(0, 1, n_new + 1)[1:-1]
    h00 = 2 * s ** 3 - 3 * s ** 2 + 1; h10 = s ** 3 - 2 * s ** 2 + s; h01 = -2 * s ** 3 + 3 * s ** 2; h11 = s ** 3 - s ** 2
    out = {}
    for b, (T, Q, S) in pose.items():
        Qc = Q.copy()
        for i in range(1, len(Qc)):
            if Qc[i] @ Qc[i - 1] < 0:
                Qc[i] *= -1
        def bridge(X):
            v0 = (X[i0] - X[i0 - 2]) / (2 * dt); v1 = (X[i1 + 2] - X[i1]) / (2 * dt)
            m0 = v0 * L_new * tangent_scale; m1 = v1 * L_new * tangent_scale
            mid = h00[:, None] * X[i0] + h10[:, None] * m0 + h01[:, None] * X[i1] + h11[:, None] * m1
            return np.concatenate([X[:i0 + 1], mid, X[i1:]])
        out[b] = [bridge(T), c.qnorm(bridge(Qc)), bridge(S)]
    F = len(out["Hips"][0]); t_new = np.arange(F) * dt
    return out, t_new


def resample(clip, path_or_pose, times):
    return clip.sample(times)



# ------------------------------------------------------------------------------------------------ retime repairs
def motion_arc(clip, pose):
    """Cumulative motion of the pose (rig m): weighted blade centroid, blade tip, hands, hips and head world paths."""
    W = c.fk(clip, pose)
    P = [c.blade_world(W), c.blade_world(W, c.TIP)] + [(c.C[None] @ W[b])[:, :3, 3] for b in ("LeftHand", "RightHand", "Hips", "Head")]
    wts = [3.0, 1.0, .25, .25, .25, .25]          # blade-dominated: the bridge evens out what the eye tracks
    step = sum(w * np.r_[0, np.linalg.norm(np.diff(p, axis=0), axis=1)] for w, p in zip(wts, P)) + 1e-7
    return np.cumsum(step)


def arc_profile(u, a, b):
    """Normalised progress p(u), p(0)=0, p(1)=1, with p'(0)=a and p'(1)=b approximately and p' >= 0 everywhere (no
    overshoot, so no plateau): speed v(u) = monotone power blend between a and b when 1 lies between them, else a
    linear blend plus a sin bump scaled to the right area (floored at 2 % of the mean)."""
    fine = np.linspace(0, 1, 2001)
    lo, hi = min(a, b), max(a, b)
    if lo < 1 < hi and abs(a - b) > 1e-6:
        m = (1 - b) / (a - b) if a > b else (1 - a) / (b - a)
        k = max(1 / m - 1, 1e-3)
        v = b + (a - b) * (1 - fine) ** k if a > b else a + (b - a) * fine ** k
    else:
        cbump = (1 - (a + b) / 2) / (2 / np.pi)
        v = a * (1 - fine) + b * fine + cbump * np.sin(np.pi * fine)
        v = np.maximum(v, .02)
    p = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(fine))]); p /= p[-1]
    return np.interp(u, fine, p)


def bridge_map(src_t, arc, windows):
    """Monotone retime out -> src that removes stalls: inside each window (a, b, new_len or None, end_speed_scale) the
    source is replayed at a speed that goes smoothly (cubic Hermite in arc length) from the clip's own speed at a to its
    speed at b, so held / stalled source time is skipped. Outside the windows the source plays 1:1 (shifted).
    Returns (out_times, src_times) sampled at HZ."""
    dt = 1.0 / HZ; out_src = []; t = src_t[0]
    sA = lambda x: np.interp(x, src_t, arc)
    def speed(x, h=1.5 / 30):
        return (sA(x + h) - sA(x - h)) / (2 * h)
    cur = src_t[0]
    for a, b, new_len, vb_scale in windows:
        # 1:1 up to a
        n = int(round((a - cur) / dt)); out_src += list(cur + np.arange(n) * dt); cur = a
        s0, s1 = sA(a), sA(b); va, vb = speed(a), speed(b) * vb_scale
        L = new_len if new_len else max(2 * dt, 2 * (s1 - s0) / max(va + vb, 1e-6))
        n = max(2, int(round(L / dt))); L = n * dt; u = np.arange(n) / n
        s_out = s0 + (s1 - s0) * arc_profile(u, va * L / max(s1 - s0, 1e-9), vb * L / max(s1 - s0, 1e-9))
        # invert arc length (strictly increasing helper)
        fine = np.linspace(a, b, 4000); sf = sA(fine) + 1e-9 * np.arange(4000)
        out_src += list(np.interp(s_out, sf, fine)); cur = b
    n = int(round((src_t[-1] - cur) / dt)); out_src += list(cur + np.arange(n + 1) * dt)
    src = np.clip(np.array(out_src), src_t[0], src_t[-1])
    return np.arange(len(src)) * dt, src


def repair(spec, name):
    """Current runtime clip, re-timed through bridge_map (stalls and statue holds removed), optional additive settle,
    optional end trim. Feet re-planted on the clip's own frame-0 / ready stance where they are planted."""
    rt = RUNTIME[name]; clip = c.Clip(ROOT / rt["glb"])
    dense = np.linspace(0, clip.duration, int(round(clip.duration * 300)) + 1)
    arc = motion_arc(clip, clip.sample(dense))
    win = [(a / 30 * rt["gameplayPlayRate"], b / 30 * rt["gameplayPlayRate"], (L / 30 * rt["gameplayPlayRate"]) if L else None, vs) for a, b, L, vs in spec["bridges"]]
    out_t, src_t = bridge_map(dense, arc, win)
    if spec.get("trim_end"):
        keep = src_t <= spec["trim_end"] + 1e-9; out_t, src_t = out_t[keep], src_t[keep]
    pose = clip.sample(src_t)
    for fn in spec.get("additive", []):
        fn(clip, pose, out_t, src_t)
    # feet: keep every frame where the source foot is planted exactly at its plant spot (removes interpolation drift)
    def to_out(x):
        return float(np.interp(x, src_t, out_t))
    meta = {"timeMapOutToSrc": [[round(float(a), 4), round(float(b), 4)] for a, b in zip(out_t[::12], src_t[::12])],
            "damageWindowsClipSeconds": [[round(to_out(a), 3), round(to_out(b), 3)] for a, b in rt["damageWindowsClipSeconds"]]}
    return clip, pose, out_t, meta


def settle_additive(a, b, depth_cm=3.0, spine_deg=2.5):
    """Moving settle over out-time [a, b]: the hips sink depth_cm and come back (one smooth bump, early peak) and the
    chest breathes (Spine1 pitch bump); the feet are re-planted on their previous world positions."""
    def fn(clip, pose, out_t, src_t):
        u = np.clip((out_t - a) / (b - a), 0, 1); bump = np.sin(np.pi * u ** .7) * (u > 0) * (u < 1)
        W0 = c.fk(clip, pose)
        targets = {s_: (W0[s_ + "Foot"][:, :3, 3].copy(), W0[s_ + "Foot"][:, :3, :3] / np.linalg.norm(W0[s_ + "Foot"][:, :3, :3], axis=1, keepdims=True)) for s_ in LEGS}
        pose["Hips"][0][:, 1] -= bump * depth_cm / CMR
        q = Rotation.from_quat(pose["Spine1"][1]); pose["Spine1"][1] = (q * Rotation.from_euler("x", (bump * spine_deg)[:, None], degrees=True)).as_quat()
        m = bump > 1e-4
        for s_ in LEGS:
            R = W0[s_ + "Foot"][:, :3, :3]; R = R / np.linalg.norm(R, axis=0, keepdims=True)
            c.plant_leg(clip, pose, s_, targets[s_][0], R, m)
    return fn

# ------------------------------------------------------------------------------------------------ clip specs
SPECS = {
    # Slash1 (= the same Mixamo 'sword and shield slash' the runtime v17 was fitted from), with the SOURCE blade path
    # instead of v17's hand-keyed arc (whose return keys re-trace the strike), v17's grip, planned feet.
    "LightAttack": dict(
        kind="mixamo", source="Slash1", grip="one", rate=1.35, duration=1.44, shift=1.0,
        # src 0-.52 (the overhead lasso twirl) is cut: the blend from the ready pose into the cocked pose (src .52-.565)
        # is the wind-up, a single raise; strike src .57-.70; follow-through; the source's low return; settle
        timemap=[(0, .52), (.36, .565), (1.055, 1.22), (1.44, 1.30)],
        blend_in=(0.0, .36), blend_out=(.96, 1.44),
        feet={"Left": [(0, .04, (0, 0), 0, 0), (.30, 1.00, (6, -86), -10, 12), (1.28, 9, (0, 0), 0, 10)],
              "Right": [(0, 9, (0, 0), 0, 0)]},
        damage_src=(.575, .76), impact_src=.60),
    # Attack3: coil, big horizontal sweep, deep crouch, the source's own low return sweep (slowed to 0.75x) and a
    # grounded settle from src 1.48 (f44, blade forward-right at hip height) into the ready pose; src f45-52 cut.
    "HeavyAttack": dict(
        kind="mixamo", source="Attack3", grip="one", rate=1.1, duration=2.00, shift=1.0,
        timemap=[(0, .20), (.25, .30), (1.15, 1.20), (1.52, 1.48), (2.00, 1.52)],
        blend_in=(0.0, .26), blend_out=(1.48, 2.00),
        feet={"Left": [(0, .18, (0, 0), 0, 0), (.50, .70, (-21, 74), 0, 12), (1.00, 1.55, (-18, -64), -10, 12), (1.85, 9, (0, 0), 0, 12)],
              "Right": [(0, 9, (0, 0), 0, 0)]},
        damage_src=(.70, .88), impact_src=.767),
    # Attack1 (overhead jump slam + kneel) made into a short hop-slam: anticipation crouch from the ready pose, the
    # rise of the leap played 2.2x and its height scaled to 0.35 (hips +~40 cm instead of +112 cm), the descent and slam
    # at 1.25x, the kneel and rise at source speed, then a settle with two steps back to the ready stance.
    "HeavyAttackAlternate": dict(
        kind="mixamo", source="Attack1", grip="one", rate=1.15, duration=2.20, shift=1.0, hips_scale=(.30, .82, .35),
        timemap=[(0, .28), (.30, .36), (.52, .84), (.82, 1.22), (1.30, 1.70), (1.86, 2.30), (2.20, 2.33)],
        blend_in=(0.0, .30), blend_out=(1.70, 2.20),
        feet={"Left": [(0, .32, (0, 0), 0, 0), (.80, 1.45, (-2, -113), -10, 30), (1.75, 9, (0, 0), 0, 12)],
              "Right": [(0, .30, (0, 0), 0, 0), (.78, 1.60, (-7, -34), 10, 30), (1.88, 9, (0, 0), 0, 12)]},
        damage_src=(1.08, 1.27), impact_src=1.18),
    # ---- repairs of the current runtime clips (rate 1.0; bridge windows in the critic's rendered frames):
    # (a, b, new length in frames or None = from the edge speeds, end-speed scale)
    "LightCombo": dict(kind="repair", bridges=[(10, 14, None, 1.0), (25, 29, None, 1.0), (51, 57, None, 1.0), (83, 100, 9, 0.0)]),
    "LightAttackTwoHand": dict(kind="repair", bridges=[(13, 23, None, 1.0), (23, 36, 17, 0.0)]),
    "HeavyAttackTwoHand": dict(kind="repair", bridges=[(16, 33, None, 1.0), (33, 48, 21, 0.0)]),
    "HeavyAttackTwoHandAlternate": dict(kind="repair", bridges=[(23, 62, 30, 1.0)], settle=(24, 54, 3.0, 2.5)),
}


def build(name, preview=None, force=False):
    spec = SPECS[name]; OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / (name + "_A1.glb")
    if out.exists() and not force:
        print("EXISTS", out.name); return
    rmeta = {}
    if spec["kind"] == "mixamo":
        clip, pose, t, info = compose_mixamo(spec)
    else:
        if spec.get("settle"):
            a, b, d, sd = spec["settle"]; r = RUNTIME[name]["gameplayPlayRate"]
            spec = dict(spec, additive=[settle_additive(a / 30 * r, b / 30 * r, d, sd)])
        clip, pose, t, rmeta = repair(spec, name); info = {}
        spec = dict(spec, rate=RUNTIME[name]["gameplayPlayRate"]); spec.pop("additive", None)
    tmpl = ROOT / RUNTIME[name]["glb"]
    sha = c.write_glb(tmpl, pose, t, out, name + "_A1")
    tmap = pchip_map(spec["timemap"]) if "timemap" in spec else None
    info = dict(info, **rmeta)
    def out_t(src_t):          # invert the monotone time map numerically
        tt = np.linspace(0, spec["duration"], 4001); ss = tmap(tt); return float(tt[np.argmin(np.abs(ss - src_t))])
    meta = dict(name=name + "_A1", file=str(out.relative_to(ROOT)), sha256=sha, template=str(tmpl.relative_to(ROOT)),
                templateSHA256=c.sha256(tmpl), duration=float(t[-1]), sampleRate=HZ, gameplayPlayRate=spec["rate"], spec={k: v for k, v in spec.items()},
                **info)
    if tmap is None:
        meta["source"] = RUNTIME[name]["glb"]; meta["sourceSHA256"] = c.sha256(ROOT / RUNTIME[name]["glb"])
    if tmap is not None:
        meta["source"] = str((MIX / ("Mixamo_SS_%s_v1.glb" % spec["source"])).relative_to(ROOT))
        meta["sourceSHA256"] = c.sha256(MIX / ("Mixamo_SS_%s_v1.glb" % spec["source"]))
        meta["damageWindowsClipSeconds"] = [[round(out_t(spec["damage_src"][0]), 3), round(out_t(spec["damage_src"][1]), 3)]]
        meta["impactClipSeconds"] = round(out_t(spec["impact_src"]), 3)
    out.with_suffix(".json").write_text(json.dumps(meta, indent=1, default=str) + "\n")
    print("BUILT", out.name, round(float(t[-1]), 3), "s", json.dumps(info), "damage", meta.get("damageWindowsClipSeconds"), "impact", meta.get("impactClipSeconds"), flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for n in (args or list(SPECS)):
        build(n, force="--force" in sys.argv)
