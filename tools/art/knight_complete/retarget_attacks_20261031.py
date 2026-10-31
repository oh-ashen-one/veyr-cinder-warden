"""Headless Blender: retarget the nine licensed Mixamo sword-and-shield attack/slash FBX files onto the KnightB rig
(2026-10-31). Same path as the earlier rounds (tools/art/blender/fab_rig_testing/retarget.py, run(): rest-pose calibrated FK
retarget, in place, WeaponSocket carried on the right hand with the approved walk grip) and NO hand-authored motion: no weapon
fit, no blade arc. retarget.py's own 5-frame evidence renders are switched off (this stage never renders).
  taskpolicy -b blender --background --factory-startup --python retarget_attacks_20261031.py -- [NAME ...]
Exports land in Local/FabRigTesting/Exports/<NAME>.glb|json|blend (one Blender process, never overwrites)."""
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
FAB = HERE.parent / "blender/fab_rig_testing"
SRC = "Local/FabRigTesting/Source/Mixamo/"
JOBS = [  # (name, fbx)
    ("Mixamo_SS_Attack1_v1", "sword and shield attack.fbx"),
    ("Mixamo_SS_Attack2_v1", "sword and shield attack (2).fbx"),
    ("Mixamo_SS_Attack3_v1", "sword and shield attack (3).fbx"),
    ("Mixamo_SS_Attack4_v1", "sword and shield attack (4).fbx"),
    ("Mixamo_SS_Slash1_v1", "sword and shield slash.fbx"),
    ("Mixamo_SS_Slash2_v1", "sword and shield slash (2).fbx"),
    ("Mixamo_SS_Slash3_v1", "sword and shield slash (3).fbx"),
    ("Mixamo_SS_Slash4_v1", "sword and shield slash (4).fbx"),
    ("Mixamo_SS_Slash5_v1", "sword and shield slash (5).fbx"),
]
only = set(sys.argv[sys.argv.index("--") + 1:]) if "--" in sys.argv else set()
g = {"__file__": str(FAB / "retarget.py")}
exec(compile((FAB / "retarget.py").read_text(), str(FAB / "retarget.py"), "exec"), g)
g["render"] = lambda *a, **k: None  # no evidence renders from this stage
root = g["ROOT"]
for name, fbx in JOBS:
    if only and name not in only:
        continue
    if (g["OUT"] / "Exports" / (name + ".glb")).exists():
        print("SKIP existing", name, flush=True)
        continue
    bpy.context.scene["session_owner"] = g["OWNER"]
    g["run"](root / SRC / fbx, "mixamo", name, False, False)
    print("RETARGETED", name, flush=True)
