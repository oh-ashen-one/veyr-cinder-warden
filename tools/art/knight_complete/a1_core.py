"""Knight attack fix round A1 (2026-10-31): pure numpy core (no Blender) shared by build_attacks_a1.py and
measure_attacks_a1.py.

* Clip: vectorised sampler of a canonical KnightB GLB (56 nodes, LINEAR channels) -> per-bone local T/Q/S at any times.
* Pose arrays: dict bone -> (T [F,3], Q [F,4] xyzw, S [F,3]); fk() -> world 4x4 [F,4,4] per bone (glTF space, Y up,
  knight forward = +Z, knight's left = +X; Blender = C @ glTF, verified identical bone frames with the glTF importer).
* write_glb(): the template GLB with its animation replaced by the given local channels (structure, skin and mesh kept).
* Review cameras: exact replica of render_review.py (hips-follow focus, ortho 3.2 m over 810 px, CANON_FWD from the
  approved 1H idle frame 0) so analytic blade speeds are in the critic's px/frame.
Game cm = rig m x 240."""
import copy, hashlib, json, struct, sys
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art/integration"))
from normalize_approved import GLB, Writer, decompose  # noqa: E402

CM = 240.0
FPS = 30
C = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)   # glTF -> Blender
KNIGHT = ROOT / "Local/CustomuseAssets/Polish20261025/knight"
IDLE = {"one": KNIGHT / "IdleOneHand_Blender_v2r4.glb", "two": KNIGHT / "IdleTwoHand_Blender_v2r4.glb"}
SWORD = ROOT / "Local/polish-review-20261025/BoatGreatsword_OneHand_v4.glb"


def qnorm(q):
    return q / np.linalg.norm(q, axis=-1, keepdims=True)


def qslerp(a, b, w):
    """Row-wise slerp of quaternion arrays a, b [F,4] by weights w [F] (shortest path)."""
    a = np.atleast_2d(a); b = np.atleast_2d(b).copy(); w = np.broadcast_to(np.asarray(w, float), (max(len(a), len(b)),))
    a = np.broadcast_to(a, (len(w), 4)); b = np.broadcast_to(b, (len(w), 4)).copy()
    d = np.sum(a * b, axis=1); b[d < 0] *= -1; d = np.abs(d)
    out = np.empty_like(a)
    lin = d > .9995
    out[lin] = a[lin] + (b[lin] - a[lin]) * w[lin, None]
    th = np.arccos(np.clip(d[~lin], -1, 1)); s = np.sin(th)
    out[~lin] = (np.sin((1 - w[~lin]) * th) / s)[:, None] * a[~lin] + (np.sin(w[~lin] * th) / s)[:, None] * b[~lin]
    return qnorm(out)


def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def smoother(x):
    x = np.clip(x, 0, 1); return x * x * x * (x * (6 * x - 15) + 10)


class Clip:
    def __init__(self, path):
        self.path = Path(path); self.g = GLB(path); g = self.g.g
        self.nodes = [n.get("name") for n in g["nodes"]]
        self.parent = {i: p for i, p in self.g.parents.items()}
        self.bones = [n for n in self.nodes if n not in ("Body",)]
        self.order = self._topo()
        a = g["animations"][0]; self.ch = {}
        for c in a["channels"]:
            sm = a["samplers"][c["sampler"]]
            self.ch[(self.nodes[c["target"]["node"]], c["target"]["path"])] = (self.g.accessor(sm["input"]).ravel().astype(float),
                                                                                 self.g.accessor(sm["output"]).astype(float))
        self.duration = max(v[0][-1] for v in self.ch.values())
        self.sha = self.g.sha

    def _topo(self):
        out, seen = [], set()
        def visit(i):
            if i in seen:
                return
            if i in self.parent:
                visit(self.parent[i])
            seen.add(i); out.append(i)
        for i in range(len(self.nodes)):
            visit(i)
        return [self.nodes[i] for i in out if self.nodes[i] != "Body"]

    def rest(self, name):
        n = self.g.g["nodes"][self.nodes.index(name)]
        return (np.array(n.get("translation", [0, 0, 0]), float), np.array(n.get("rotation", [0, 0, 0, 1]), float),
                np.array(n.get("scale", [1, 1, 1]), float))

    def sample(self, times):
        """Local channels at clip times (clamped to [0, duration])."""
        times = np.clip(np.asarray(times, float), 0, self.duration); F = len(times); pose = {}
        for b in self.order:
            rt, rq, rs = self.rest(b)
            T = np.tile(rt, (F, 1)); Q = np.tile(rq, (F, 1)); S = np.tile(rs, (F, 1))
            if (b, "translation") in self.ch:
                k, v = self.ch[(b, "translation")]; T = np.stack([np.interp(times, k, v[:, i]) for i in range(3)], 1)
            if (b, "scale") in self.ch:
                k, v = self.ch[(b, "scale")]; S = np.stack([np.interp(times, k, v[:, i]) for i in range(3)], 1)
            if (b, "rotation") in self.ch:
                k, v = self.ch[(b, "rotation")]; v = v.copy()
                for i in range(1, len(v)):
                    if v[i] @ v[i - 1] < 0:
                        v[i] *= -1
                if len(k) == 1:
                    Q = np.tile(v[0], (F, 1))
                else:
                    Q = Slerp(k, Rotation.from_quat(v))(np.clip(times, k[0], k[-1])).as_quat()
            pose[b] = [T, Q, S]
        return pose

    def parent_name(self, b):
        i = self.nodes.index(b)
        return self.nodes[self.parent[i]] if i in self.parent else None


def frames(pose):
    return len(next(iter(pose.values()))[0])


def trs_mat(T, Q, S):
    M = np.zeros((len(T), 4, 4)); M[:, :3, :3] = Rotation.from_quat(Q).as_matrix() * S[:, None, :]; M[:, :3, 3] = T; M[:, 3, 3] = 1
    return M


def fk(clip, pose):
    W = {}
    for b in clip.order:
        L = trs_mat(*pose[b]); p = clip.parent_name(b)
        W[b] = W[p] @ L if p in W else L
    return W


def set_world(clip, pose, W, b, M, mask=None):
    """Write world matrices M [F,4,4] for bone b into pose (local channels), given current world dict W (parents valid)."""
    p = clip.parent_name(b)
    L = np.linalg.inv(W[p]) @ M if p in W else M
    T, Q, S = [], [], []
    for m in L:
        t, q, s = decompose(m); T.append(t); Q.append(q); S.append(s)
    T, Q, S = np.array(T), np.array(Q), np.array(S)
    if mask is None:
        mask = np.ones(len(T), bool)
    pose[b][0][mask] = T[mask]; pose[b][1][mask] = Q[mask]; pose[b][2][mask] = S[mask]


def copy_pose(pose):
    return {b: [x.copy() for x in v] for b, v in pose.items()}


def concat(*poses):
    return {b: [np.concatenate([p[b][i] for p in poses]) for i in range(3)] for b in poses[0]}


def blend(a, b, w, bones=None):
    """Per-frame local blend a->b with weights w [F] (a, b same frame count; a single-frame pose broadcasts)."""
    out = {}
    w = np.asarray(w, float)
    for n in a:
        if bones is not None and n not in bones:
            out[n] = [x.copy() for x in a[n]]; continue
        ta, qa, sa = a[n]; tb, qb, sb = b[n]
        F = len(w)
        ta = np.broadcast_to(ta, (F, 3)); tb = np.broadcast_to(tb, (F, 3)); sa = np.broadcast_to(sa, (F, 3)); sb = np.broadcast_to(sb, (F, 3))
        out[n] = [ta + (tb - ta) * w[:, None], qslerp(np.broadcast_to(qa, (F, 4)), np.broadcast_to(qb, (F, 4)), w), sa + (sb - sa) * w[:, None]]
    return out


def single(pose, i):
    return {b: [x[i:i + 1].copy() for x in v] for b, v in pose.items()}


def repeat(pose1, F):
    return {b: [np.repeat(x, F, 0) for x in v] for b, v in pose1.items()}


# ------------------------------------------------------------------------------------------------ IK
def two_bone(H, K, A, T, pole_hint):
    """Analytic two-bone IK: returns new knee position K2 so |K2-H|=|K-H|, |T-K2|=|A-K|, bending toward pole_hint."""
    a = np.linalg.norm(K - H); b = np.linalg.norm(A - K)
    d = np.clip(np.linalg.norm(T - H), 1e-5, (a + b) * .9995)
    u = (T - H) / max(np.linalg.norm(T - H), 1e-9)
    v = pole_hint - u * (pole_hint @ u); v /= max(np.linalg.norm(v), 1e-9)
    ca = np.clip((a * a + d * d - b * b) / (2 * a * d), -1, 1)
    return H + a * (ca * u + np.sqrt(max(0, 1 - ca * ca)) * v)


def rot_between(u, v):
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v); c = np.cross(u, v); s = np.linalg.norm(c); d = u @ v
    if s < 1e-9:
        return np.eye(3)
    k = c / s; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    ang = np.arctan2(s, d)
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


def plant_leg(clip, pose, side, target_ankle, target_foot_rot, mask):
    """Two-bone IK of UpLeg/Leg so the ankle (Foot origin) reaches target_ankle [F,3] and the Foot world rotation
    = target_foot_rot [F,3,3], for frames in mask. Knee plane taken from the current knee (no pole flips)."""
    W = fk(clip, pose); up, lg, ft = side + "UpLeg", side + "Leg", side + "Foot"
    newU = W[up].copy(); newL = W[lg].copy(); newF = W[ft].copy()
    for i in np.where(mask)[0]:
        H = W[up][i, :3, 3]; K = W[lg][i, :3, 3]; A = W[ft][i, :3, 3]; T = target_ankle[i]
        mid = (H + A) / 2; hint = K - mid
        if np.linalg.norm(hint) < 1e-4:
            hint = np.array([0, 0, 1.0])
        K2 = two_bone(H, K, A, T, hint)
        R1 = rot_between(K - H, K2 - H)
        U = W[up][i].copy(); U[:3, :3] = R1 @ U[:3, :3]; newU[i] = U
        # Leg world: its head moves to K2, rotate so (A'-K2) aims at T
        Lw = W[lg][i].copy(); Lw[:3, :3] = R1 @ Lw[:3, :3]; Lw[:3, 3] = K2
        A1 = K2 + R1 @ (A - K)
        R2 = rot_between(A1 - K2, T - K2); Lw[:3, :3] = R2 @ Lw[:3, :3]; newL[i] = Lw
        Fw = W[ft][i].copy(); sc = np.linalg.norm(Fw[:3, :3], axis=0); Fw[:3, :3] = target_foot_rot[i] * sc; Fw[:3, 3] = T; newF[i] = Fw
    set_world(clip, pose, W, up, newU, mask); W = fk(clip, pose)
    set_world(clip, pose, W, lg, newL, mask); W = fk(clip, pose)
    set_world(clip, pose, W, ft, newF, mask)


# ------------------------------------------------------------------------------------------------ output
def write_glb(template, pose, times, out, name):
    """Template GLB (same canonical node list) with one animation of the given local channels at `times`."""
    src = GLB(template); w = Writer(src.g, src.binary); g = w.g
    # drop the old animation's data: rebuild the buffer from the non-animation accessors
    keep_acc = set()
    used = set(i for a in g.get("animations", []) for s in a["samplers"] for i in (s["input"], s["output"]))
    w2 = Writer({k: v for k, v in g.items() if k not in ("animations", "accessors", "bufferViews", "buffers")}, b"")
    w2.g["accessors"] = []; w2.g["bufferViews"] = []; remap = {}
    for i, a in enumerate(g["accessors"]):
        if i in used:
            continue
        arr = src.accessor(i)
        comp = a["componentType"]
        if a.get("normalized"):
            info = np.iinfo({5121: np.uint8, 5123: np.uint16, 5120: np.int8, 5122: np.int16}[comp]); arr = np.round(arr * info.max)
        j = w2.add(arr, a["type"], comp, bounds="min" in a)
        if a.get("normalized"):
            w2.g["accessors"][j]["normalized"] = True
        remap[i] = j
    def fix(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("POSITION", "NORMAL", "TANGENT", "indices", "inverseBindMatrices") or k.startswith(("TEXCOORD_", "JOINTS_", "WEIGHTS_", "COLOR_")):
                    if isinstance(v, int):
                        o[k] = remap[v]; continue
                fix(v)
        elif isinstance(o, list):
            for v in o:
                fix(v)
    for key in ("meshes", "skins"):
        if key in w2.g:
            fix(w2.g[key])
    # images stored in bufferViews
    for im in w2.g.get("images", []):
        if "bufferView" in im:
            v = g["bufferViews"][im["bufferView"]]; raw = bytes(src.binary[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]])
            w2.binary.extend(b"\0" * (-len(w2.binary) % 4)); off = len(w2.binary); w2.binary.extend(raw)
            im["bufferView"] = len(w2.g["bufferViews"]); w2.g["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(raw)})
    ids = {n.get("name"): i for i, n in enumerate(w2.g["nodes"])}
    anim = {"name": name, "samplers": [], "channels": []}
    tacc = w2.add(np.asarray(times, float), "SCALAR", bounds=True)
    for b in [n for n in ids if n in pose]:
        T, Q, S = pose[b]; Q = Q.copy()
        for i in range(1, len(Q)):
            if Q[i] @ Q[i - 1] < 0:
                Q[i] *= -1
        for path, vals, typ in (("translation", T, "VEC3"), ("rotation", Q, "VEC4"), ("scale", S, "VEC3")):
            si = len(anim["samplers"]); anim["samplers"].append({"input": tacc, "output": w2.add(vals, typ), "interpolation": "LINEAR"})
            anim["channels"].append({"sampler": si, "target": {"node": ids[b], "path": path}})
    w2.g["animations"] = [anim]
    sha = w2.write(out)
    return sha


# ------------------------------------------------------------------------------------------------ sword + cameras
def sword_points():
    raw = SWORD.read_bytes(); n = struct.unpack_from("<I", raw, 12)[0]; doc = json.loads(raw[20:20 + n]); blob = raw[28 + n:]
    a = doc["accessors"][doc["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]; v = doc["bufferViews"][a["bufferView"]]
    off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    pts = np.frombuffer(blob, dtype="<f4", count=3 * a["count"], offset=off).reshape(-1, 3).astype(float)
    return pts


_PTS = sword_points()
BLADE = _PTS[_PTS[:, 1] > .55]           # blade body (as build_round5); centroid = brown-hue blade the critic segments
BLADE_C = BLADE.mean(0)
TIP = np.array([0, 2.35, 0])


def blade_world(W, local=None):
    """World (Blender space) positions [F,3] of a socket-local point (default: blade centroid)."""
    p = BLADE_C if local is None else np.asarray(local, float)
    M = C[None] @ W["WeaponSocket"]
    return (M[:, :3, :3] @ p + M[:, :3, 3])


def canon_fwd():
    idle = Clip(IDLE["one"]); W = fk(idle, idle.sample([0.0]))
    toes = (W["LeftToeBase"][0, :3, 3] + W["RightToeBase"][0, :3, 3]) / 2; heels = (W["LeftFoot"][0, :3, 3] + W["RightFoot"][0, :3, 3]) / 2
    f = (C[:3, :3] @ (toes - heels)); f[2] = 0
    return f / np.linalg.norm(f)


FWD = canon_fwd()
RIGHT = np.array([FWD[1], -FWD[0], 0.0])
VIEWS = {"front": FWD * 3 + np.array([0, 0, .4]), "side": RIGHT * 3 + np.array([0, 0, .4]), "threequarter": FWD * 3 + RIGHT * 2 + np.array([0, 0, .5])}
ORTHO, RES = 3.2, 810


def cam_axes(off):
    d = -off / np.linalg.norm(off)                 # view direction (camera -Z)
    up0 = np.array([0, 0, 1.0])
    r = np.cross(d, up0); r /= np.linalg.norm(r)
    u = np.cross(r, d)
    return r, u


def project(Wb, hips_b):
    """Blender-space points [F,3] -> {view: [F,2] px} with the hips-follow camera (focus = hips x,y, z .5)."""
    focus = np.c_[hips_b[:, 0], hips_b[:, 1], np.full(len(hips_b), .5)]
    out = {}
    for v, off in VIEWS.items():
        r, u = cam_axes(off); d = Wb - focus
        out[v] = np.c_[d @ r, d @ u] / ORTHO * RES
    return out


def hips_b(W):
    return (C[None] @ W["Hips"])[:, :3, 3]


def render_times(duration, rate, start=0.0, end=None):
    """render_review 'even' sampling: n = round(span*30), n+1 frames ending on `end`."""
    end = duration if end is None else end
    n = max(1, int(round((end - start) / rate * FPS)))
    return start + np.arange(n + 1) * (end - start) / n


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
