"""Read-only UE 5.8 commandlet: dump the runtime knight definition's clip table (no saves, no imports).

Run (headless, through the GPU slot like every editor launch):
  gpu_slot.sh capture --label knight-dump -- UnrealEditor <uproject> -run=pythonscript
    -script=<absolute path to this file> -nullrhi -unattended -NoZenAutoLaunch -notraceserver
Writes Local/CustomuseImports/runtime-clips-<stamp>.json and logs VEYR_RUNTIME_CLIPS_DUMPED <path>.
Used before the v030t attack import to copy the inherited weapon/mesh bindings of the replaced attack clips."""
import datetime
import json
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = "/Game/Characters/Customuse/RuntimePolish/DA_Knight"
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = ROOT / ("Local/CustomuseImports/runtime-clips-%s.json" % stamp)


def path(obj):
    return obj.get_path_name() if obj else None


try:
    d = unreal.load_asset(RUNTIME)
    rec = {"definition": RUNTIME, "source": unreal.EditorAssetLibrary.get_metadata_tag(d, "VeyrPolishSourceDefinition"),
           "previous": unreal.EditorAssetLibrary.get_metadata_tag(d, "VeyrPreviousSourceDefinition"),
           "skeletalMesh": path(d.skeletal_mesh), "clips": {}}
    for k, c in d.clips.items():
        roots = list(c.root_translation_samples_cm)
        rec["clips"][str(k)] = {
            "sequence": path(c.sequence), "playLength": float(c.sequence.get_play_length()) if c.sequence else None,
            "meshOverride": path(c.mesh_override), "weapon": path(c.weapon_mesh),
            "gameplayPlayRate": float(c.gameplay_play_rate), "start": float(c.start_seconds), "end": float(c.end_seconds),
            "impact": float(c.impact_seconds), "loop": bool(c.loop),
            "damageWindows": [[float(w.x), float(w.y)] for w in c.damage_windows],
            "nominalSpeed": float(c.nominal_speed_cm_per_second), "rootMotionRemoved": bool(c.root_motion_removed),
            "rootSampleRate": float(c.root_sample_rate), "rootSamples": len(roots),
            "rootFirstLast": [[roots[0].x, roots[0].y, roots[0].z], [roots[-1].x, roots[-1].y, roots[-1].z]] if roots else [],
            "approvedSourceFile": c.approved_source_file, "approvedSourceSHA256": c.approved_source_sha256}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    unreal.log("VEYR_RUNTIME_CLIPS_DUMPED " + str(OUT))
except Exception as error:
    unreal.log_error("VEYR_RUNTIME_CLIPS_FAILED " + str(error))
    raise
