#!/usr/bin/env python3
"""KnightB v030t: the five attack-round A1 winners (ab-a1.md) on top of the v030s runtime.

Imported: LightAttack (Mixamo Slash1), HeavyAttack (Mixamo Attack3), HeavyAttackAlternate (Mixamo Attack1),
HeavyAttackTwoHand (bridged v2r3) and LightCombo (bridged v5), from Local/CustomuseAssets/AttacksA1-20261031/knight.
Kept as they are (inherited by reference, never touched): LightAttackTwoHand and HeavyAttackTwoHandAlternate
(A1 tie / A1 worse) and every other clip of the v030s runtime definition.

Each clip takes rate, damage windows, impact time and duration from its A1 sidecar, cross-checked against the
'timing' section of docs/knight-complete-20261028/data/attacks-a1-metrics.json (the numbers in plan-a1.md).
Weapon prop and mesh override are copied from the clip it replaces, read from the runtime definition by
dump_runtime_clips.py (pass that dump with --dump), so only the motion and its timing change.

Usage: prepare_attacks_a1_plan.py --dump <runtime-clips-*.json>   write plan + manifest (refuses to overwrite)
       prepare_attacks_a1_plan.py --activate                     point active-plans.json at it after a hash check
"""
import copy, hashlib, json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art/integration")); sys.path.insert(0, str(ROOT / "tools/art/knight_complete"))
A1 = ROOT / "Local/CustomuseAssets/AttacksA1-20261031/knight"; BASE = ROOT / "Local/CustomuseAssets/Polish20261025"
OUT = ROOT / "Local/CustomuseAssets/KnightAttacksA1-v030t"; PLAN = BASE / "knight-v030t/import-plan-KnightB.json"
PREV = BASE / "knight-v030s/import-plan-KnightB.json"
DOC = ROOT / "docs/knight-complete-20261028/data/import-plan-KnightB-v030t.json"
METRICS = ROOT / "docs/knight-complete-20261028/data/attacks-a1-metrics.json"
TAKE = ["LightAttack", "HeavyAttack", "HeavyAttackAlternate", "HeavyAttackTwoHand", "LightCombo"]
KEEP = ["LightAttackTwoHand", "HeavyAttackTwoHandAlternate"]
# Source GLB of each mesh variant the replaced clips use (the files those native variants were imported from).
VARIANT_FILES = {
    "knight_571e0abbfde2720e": ROOT / "Local/CustomuseAssets/Sourced20261025b/knight/Mixamo_Walk_v17.glb",
    "knight_6d3b4c55bd8c3fa0": BASE / "idle-joins/knight/HeavyAttackOneHand_Blender_v4r3.glb",
    "knight_2bb061d3dbf92c62": BASE / "idle-joins/knight/IdleOneHand_Blender_v2r4.glb",
    "knight_9eeb95137c66d34d": BASE / "idle-joins/knight/Heal_Blender_v4.glb",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def package(path):
    return path.split(".")[0] if path else None


if "--activate" in sys.argv:
    rec = json.loads((OUT / "knight-manifest.json").read_text())
    if rec["planSHA256"] != sha(PLAN):
        raise SystemExit("plan hash differs from the manifest; refusing to activate")
    active = BASE / "active-plans.json"; prior = json.loads(active.read_text())
    prior["KnightB"] = {"path": str(PLAN), "sha256": sha(PLAN)}
    active.write_text(json.dumps(prior, indent=2) + "\n"); print("PLAN_ACTIVE", PLAN); sys.exit(0)

DUMP = Path(sys.argv[sys.argv.index("--dump") + 1]).resolve(); dump = json.loads(DUMP.read_text())
if PLAN.exists():
    raise FileExistsError(PLAN)
old = json.loads(PREV.read_text())
assert dump["source"] == "/Game/Characters/Customuse/KnightB/v030s/DA_KnightB", dump["source"]
assert not {c["name"] for c in old["clips"]} & set(TAKE + KEEP), "v030s plan must not own any attack clip"
timing = json.loads(METRICS.read_text())["timing"]

from normalize_sourced import GLB  # noqa: E402
from normalize_approved import mesh_variant  # noqa: E402
sys.path.insert(0, str(ROOT / "tools/unreal")); import import_customuse  # noqa: E402
canonical = GLB(old["rig"]["file"])
plan = copy.deepcopy(old)
plan.update(version="v030t", replace_runtime_source="/Game/Characters/Customuse/KnightB/v030s/DA_KnightB",
            purpose="Knight attack round A1 (2026-10-31): the five blind-A/B winners (LightAttack Slash1, HeavyAttack Attack3, "
                    "HeavyAttackAlternate Attack1 hop-slam, bridged HeavyAttackTwoHand and LightCombo) with their new rates, damage "
                    "windows and impact times; LightAttackTwoHand and HeavyAttackTwoHandAlternate kept; other clips inherited from v030s.")
plan["clips"] = []; plan["mesh_variants"] = {}; plan["existing_mesh_variants"] = {}
plan["existing_props"] = dict(old.get("existing_props", {})); rows = []
(OUT / "knight").mkdir(parents=True, exist_ok=True)
for key in TAKE:
    src = A1 / (key + "_A1.glb"); meta = json.loads(src.with_suffix(".json").read_text()); t = timing[key]["after"]
    assert sha(src) == meta["sha256"] == t["sha256"], key
    windows = [[float(a), float(b)] for a, b in meta["damageWindowsClipSeconds"]]
    assert windows == t["damageClipSeconds"] and abs(meta["gameplayPlayRate"] - t["rate"]) < 1e-9, key
    assert abs(meta["duration"] - t["clipSeconds"]) < 1e-3, (key, meta["duration"], t["clipSeconds"])
    impact = meta.get("impactClipSeconds")
    assert impact == t.get("impactClipSeconds"), key
    if impact is not None:
        assert any(a <= impact <= b for a, b in windows), (key, impact, windows)
    assert all(0 <= a < b <= meta["duration"] for a, b in windows), key
    inherited = dump["clips"][key]
    vname = package(inherited["meshOverride"]).split("/")[-2]; assert vname in VARIANT_FILES, (key, vname)
    weapon_asset = package(inherited["weapon"]); weapon_base = weapon_asset.split("/")[-1] + ".glb"
    weapon_version = weapon_asset.split("/")[-4]
    alias = "%s#%s" % (weapon_base, weapon_version)          # importer only uses the key to find the existing prop
    plan["existing_props"][alias] = weapon_asset
    # The A1 GLBs keep their template's mesh, skin order and node layout (build_attacks_a1.py writes them on the
    # runtime template, which v026/v027 imported as-is), so they are byte-copied, not re-normalized: normalize_file
    # would remap the skin to the canonical joint order and no longer match the inherited native mesh variant.
    dst = OUT / "knight" / src.name
    if not dst.exists():
        shutil.copyfile(src, dst)
    assert sha(dst) == meta["sha256"], key
    got = "knight_" + mesh_variant(GLB(dst))[:16]
    assert got == vname, (key, "A1 mesh variant", got, "inherited override", vname)
    n = round(meta["duration"] * meta["sampleRate"])
    row = {"file": str(dst), "sha256": meta["sha256"], "sourceSHA256": meta["sha256"], "duration": GLB(dst).duration(),
           "rootSampleRate": n / meta["duration"], "rootTranslationSamplesCm": [[0.0, 0.0, 0.0]] * (n + 1), "bRootMotionRemoved": False,
           "mesh_variant": got, "canonicalReconstructionMaxMatrixError": 0.0}
    assert abs(row["duration"] - meta["duration"]) < 1e-4, (key, row["duration"], meta["duration"])
    vfile = VARIANT_FILES[vname]
    plan["mesh_variants"][vname] = {"file": str(vfile), "sha256": sha(vfile)}
    plan["existing_mesh_variants"][vname] = package(inherited["meshOverride"])
    rows.append({**row, "key": key, "source": str(src), "inherited": inherited})
    plan["clips"].append({"name": key, "file": row["file"], "sha256": row["sha256"], "mesh_variant": vname, "start_seconds": 0,
        "end_seconds": -1, "loop": False, "gameplay_play_rate": meta["gameplayPlayRate"], "nominal_speed_cm_per_second": 0.0,
        "damage_windows": windows, "impact_seconds": impact if impact is not None else -1, "weapon_file": alias,
        "root_motion_policy": "preserve", "root_motion_removed": False, "root_sample_rate": row["rootSampleRate"],
        "root_translation_samples_cm": row["rootTranslationSamplesCm"], "root_yaw_samples_degrees": [],
        "source_duration": row["duration"], "approved_source_file": src.name, "approved_source_sha256": row["sourceSHA256"]})
    print("PLANNED", key, vname, "rate", meta["gameplayPlayRate"], "dur", round(row["duration"], 4), "windows", windows,
          "impact", impact, "weapon", weapon_asset, "copied", Path(row["file"]).name, flush=True)
for vname, v in plan["mesh_variants"].items():
    assert v["sha256"] == sha(v["file"])
plan["integration_notes"] = dict(plan.get("integration_notes", {}), knightAttacksA1={
    "decisions": "docs/knight-complete-20261028/attacks-20261031/ab-a1.md", "plan": "docs/knight-complete-20261028/attacks-20261031/plan-a1.md",
    "imported": TAKE, "keptAsIs": KEEP, "inheritedByReference": "every clip not listed, from v030s",
    "weaponAndMeshOverride": "copied from the replaced runtime clip (dump %s); existing_props keys '<file>#<version>' are lookup aliases" % DUMP.relative_to(ROOT),
    "builder": "tools/art/knight_complete/build_attacks_a1.py (A1 GLBs), prepare_attacks_a1_plan.py (this plan)"})
PLAN.parent.mkdir(parents=True, exist_ok=True); PLAN.write_text(json.dumps(plan, indent=2) + "\n")
canon = import_customuse.inspect_glb(plan["rig"])
for c in plan["clips"]:
    v = plan["mesh_variants"].get(c["mesh_variant"])
    import_customuse.compatible(import_customuse.inspect_glb(v) if v else canon, import_customuse.inspect_glb(c))
DOC.write_text(PLAN.read_text())
(OUT / "knight-manifest.json").write_text(json.dumps({"version": "v030t", "plan": str(PLAN), "planSHA256": sha(PLAN), "clips": rows}, indent=2) + "\n")
print("PLAN_WRITTEN (not activated; run with --activate before the import commandlet)", PLAN, sha(PLAN))
