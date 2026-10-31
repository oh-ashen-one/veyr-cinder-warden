# Knight attacks, fix round A1 (2026-10-31)

Input: `critique-attacks.md` (critic, same folder) and `runtime-attacks.json` (which GLB each runtime attack plays).
Branch `fable/knight-complete-20261028`. Nothing was imported into Unreal; no Unreal process was launched.

Outputs (git-ignored `Local/`):

- GLBs + sidecar JSON (timing, time map, source sha): `Local/CustomuseAssets/AttacksA1-20261031/knight/<Clip>_A1.glb|json`
- Review media: `Local/knight-review-20261028/attacks-a1-20261031/media/` with `before-<Clip>.mp4` (byte copy of the
  attacks-20261031 `cur-<Clip>.mp4`), `after-<Clip>.mp4` (same three cameras, same framing), `ba-<Clip>.mp4`
  (BEFORE on top, AFTER below), `index.html`
- Numbers: `docs/knight-complete-20261028/data/attacks-a1-metrics.json` (analytic + critic-replica video metrics,
  old/new timing, HeavyAttackAlternate jump trace)

Scripts (`tools/art/knight_complete/`): `a1_core.py` (numpy GLB sampler, FK, IK, GLB writer),
`build_attacks_a1.py` (all clip specs; `python3 build_attacks_a1.py [Clip ...]`), `measure_attacks_a1.py`
(`metrics`, `video`, `preview`), `attacks_a1.py` (review jobs, encodes), `render_attacks_a1.sh` (renders through
`gpu_slot.sh capture --label knight-a1-<x>`).

Authoring is numpy only, keyed at 120 Hz on the runtime template rig (mesh preserved, node layout unchanged).
Source-first: every clip is a sourced Mixamo take or the current runtime clip. Changes are trim, retime, blends into
the ready pose, foot plants, leg IK, hips shift/drop, constant weapon grip and arc-length bridges. No whole motion
was hand-authored.

## Order and pilot gate

LightAttack and HeavyAttack were built and rendered first, next to the current clips, and compared close-up on
contact sheets of all three cameras. Items 3-5 were built only after that comparison.

## Per clip

Game seconds = clip seconds / gameplay rate. Damage windows are in clip seconds (what the DA stores) and in game seconds.

### LightAttack: Mixamo Slash1 with the v17 weapon fit

- Source `Local/CustomuseAssets/Attacks20261031/knight/Mixamo_SS_Slash1_v1.glb` (sha d277e5cca50e), the same
  Mixamo "sword and shield slash" take as v17. The hand-keyed v17 blade arc (its return retraced the strike) is not used.
- Trimmed to a single raise (source 0.52-1.30 s); smoothed piecewise-linear time map. Blend from the 1H idle frame 0
  over 0-0.36 s and back over 0.96-1.44 s. Left foot lunges forward 86 cm with a lifted step and steps back; right
  foot planted. Hips follow the feet midpoint. Weapon on the constant v17 grip (inv(RightHand) @ WeaponSocket of
  Mixamo_Attack_v17). Ground clearance 3 cm via hand rotation.
- Rate 1.6 -> 1.35. Duration 1.50 -> 1.44 clip s (0.94 -> 1.07 game s).
- Damage 0.45-0.72 clip (0.281-0.450 game) -> 0.347-0.567 clip (0.257-0.420 game). Impact 0.50 clip (0.313 game)
  -> 0.39 clip (0.289 game).

### HeavyAttack: Mixamo Attack3, grounded

- Source `Local/CustomuseAssets/Attacks20261031/knight/Mixamo_SS_Attack3_v1.glb` (sha dc9f983b8290). Coil, big horizontal sweep and follow-through kept at source
  pace; the post-swing part from source 1.48 s is compressed into a low, slow return and a settle into the ready pose.
- Left foot: step forward into the swing, back across, home. Right planted. Hips drop through the strike (feet IK).
- Rate 1.0 -> 1.1. Duration 1.40 -> 2.00 clip s (1.40 -> 1.82 game s).
- Damage 0.52-0.94 clip/game -> 0.65-0.83 clip (0.591-0.755 game). Impact 0.717 clip (0.652 game); old clip had no
  recorded impact time.

### HeavyAttackAlternate: Mixamo Attack1, trimmed hop-slam

- Before: the same motion as HeavyAttack (v4r3 vs v4r5; analytic retrace 0.00 against itself, identical stops).
- Source `Local/CustomuseAssets/Attacks20261031/knight/Mixamo_SS_Attack1_v1.glb` (sha e46f90b64fde): overhead jump slam and kneel. Anticipation crouch from
  ready; leap rise played faster with its hips height scaled to 0.35 inside source 0.30-0.82 s; slam; kneel; rise; two
  steps back to the ready stance.
- Jump trace (rendered frames, game time): both feet off the ground f9-f20 (0.40 s), feet peak +37 cm, hips peak
  148 cm (idle 131); fall from the apex 0.6/1.8/5.0/10.6/18.7/30 cm over f15-f20 (free fall: 0.5/2.2/4.9/8.7/13.6/19.6).
  Kneel low point hips 47.7 cm, f29-31.
- Rate 1.0 -> 1.15. Duration 1.40 -> 2.20 clip s (1.40 -> 1.91 game s).
- Damage 0.52-0.94 -> 0.71-0.871 clip (0.617-0.757 game). Impact 0.79 clip (0.687 game).

### Repairs of the current runtime clips (rate 1.0, same source GLBs)

Bridges replace the named rendered-frame ranges with an arc-length retime (blade-weighted), monotone speed profile
from the edge speeds, so stalls and holds are skipped instead of interpolated.

| Clip | Source (runtime GLB, sha) | Bridges (frames a-b -> new length) | Duration clip s | Damage clip s |
| --- | --- | --- | --- | --- |
| LightCombo | LightCombo_Blender_v5 (ccea5025ebdf) | 10-14, 25-29, 51-57 (edge speed); 83-100 -> 9 f, ease out | 3.32 -> 2.908 | [.30,.50] [.767,1.033] [1.60,1.963] -> [.30,.475] [.742,.983] [1.55,1.813] |
| LightAttackTwoHand | LightAttackTwoHand_Compact_Blender_v2r3 (f7192952525c) | 13-23 (edge speed); 23-36 -> 17 f, ease out | 1.20 -> 1.175 | .35-.56 -> .35-.531 |
| HeavyAttackTwoHand | StrongAttackTwoHand_Sweep_Blender_v2r3 (823bae1b454e) | 16-33 (edge speed); 33-48 -> 21 f, ease out | 1.613 -> 1.592 | .43-.74 -> .43-.602 |
| HeavyAttackTwoHandAlternate | StrongAttackTwoHand_Thrust_Blender_v2r4 (c58950ffbb55) | 23-62 -> 30 f; additive settle f24-54 (hips dip 3 cm, Spine1 2.5 deg), feet replanted | 2.307 -> 2.008 | .70-.98 -> .70-.976 |

No recorded impact times exist for the repaired clips; the damage-window starts are unchanged except where a bridge
removed a stall inside the window (end moves earlier).

## Pass tests, before -> after

Analytic (FK of the GLB at the rendered times, `measure_attacks_a1.py metrics`). rec = recovery blade peak / strike
peak (pass <= 0.40); retr = reverse sweep in the strike height band / strike sweep (pass <= 0.25); stops = runs of >= 2
frames < 3 px/f inside the swing; drop = hips drop game cm; ready = body/feet distance to that grip's idle frame 0 at
start/end (cm); skate = max planted-foot slide cm/f (L/R); ground = lowest sword point game cm.

| Clip | strike px/f | rec | retr | stops / ident / freeze | drop | ready | skate | ground |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LightAttack | 139 -> 203 | 0.75 -> 0.29 | 0.94 -> 0.22 | none -> none | 15.9 -> 36.0 | 64.2 -> 0.4 | 18.1/14.4 -> 0.0/0.0 | 43.8 -> 3.2 |
| HeavyAttack | 106 -> 220 | 0.46 -> 0.22 | 0.39 -> 0.20 | (23,26) -> none | 20.0 -> 44.5 | 0.0 -> 1.2 | 3.6/4.6 -> 0.0/0.1 | 33.0 -> 2.0 |
| HeavyAttackAlternate | 98 -> 174 | 0.49 -> 0.26 | (dup) -> 0.26 | (23,26) -> none | 20.0 -> 68.9 | 0.0 -> 0.9 | 3.6/4.6 -> 0.0/0.0 | 33.0 -> 1.2 |
| LightAttackTwoHand | 74 -> 72 | 0.45 -> 0.29 | 0.37 -> 0.18 | none -> none | 10.3 -> 10.0 | 0 -> 0 | 2.6/2.3 -> 1.9/2.2 | 132.6 -> 132.6 |
| HeavyAttackTwoHand | 109 -> 106 | 0.54 -> 0.44 | 0.29 -> 0.28 | (18,19), 1 ident -> none | 22.1 -> 22.1 | 0 -> 0 | 2.8/3.8 -> 2.8/3.8 | 45.4 -> 45.7 |
| HeavyAttackTwoHandAlternate | 89 -> 90 | 0.26 -> 0.14 | 0.21 -> 0.19 | (25,26),(32,34), freeze 33-43 -> none | 22.8 -> 25.4 | 0 -> 0 | 2.8/2.0 -> 2.6/2.0 | 71.8 -> 72.0 |
| LightCombo | 156 -> 161 | 0.41 -> 0.40 | 0.47 -> 0.40 | (54,55), 2 ident, freeze 91-96 -> none | 19.2 -> 19.2 | 0 -> 0 | 3.2/4.6 -> 2.4/4.6 | -46.3 -> -44.9 |

Critic-replica video metric (`measure_attacks_a1.py video`: blade pixels R-B > 18, centroid speed, max over panels):

| Clip | frames | strike px/f | rec/strike | slow runs | duplicates |
| --- | --- | --- | --- | --- | --- |
| LightAttack | 29 -> 33 | 143 -> 183 | 0.72 -> 0.49 | none | none |
| HeavyAttack | 43 -> 56 | 113 -> 156 | 0.44 -> 0.42 | none | none |
| HeavyAttackAlternate | 43 -> 58 | 80 -> 163 | 0.62 -> 0.32 | none | none |
| LightAttackTwoHand | 37 -> 36 | 84 -> 72 | 0.52 -> 0.42 | none | none |
| HeavyAttackTwoHand | 49 -> 49 | 96 -> 105 | 0.76 -> 0.55 | none | none |
| HeavyAttackTwoHandAlternate | 70 -> 61 | 84 -> 84 | 0.71 -> 0.46 | none | none |
| LightCombo | 101 -> 88 | 151 -> 155 | 0.81 -> 0.59 | (54,55) -> none | 54,55 -> none |

The video ratio counts all blade-pixel motion after the damage window (body turn and the blade's own follow-through
included), so it runs higher than the analytic blade-tip ratio.

## Open items (measured, not fixed in A1)

- HeavyAttackTwoHand recovery: analytic rec 0.44, retr 0.28 (both fail). The recovery window starts 4 frames after
  the damage end, which now falls inside the strike's own follow-through; the lift back to the vertical 2H ready pose
  still rises along the strike side.
- HeavyAttackAlternate retr 0.26 (limit 0.25).
- LightCombo rec 0.401 / retr 0.40 (fail) and the blade still goes 45 cm below the floor (unchanged source pose;
  not in the critic list for this round).
- Video rec/strike > 0.40 on LightAttack (0.49), HeavyAttack (0.42), LightAttackTwoHand (0.42), HeavyAttackTwoHand
  (0.55), HeavyAttackTwoHandAlternate (0.46), LightCombo (0.59).
- 2H repaired clips keep the source planted-foot slide (1.9-4.6 cm/f); repairs only retime.
- HeavyAttackTwoHandAlternate grip: hand-to-socket rotation changes up to 28 deg in the source thrust (30 deg before);
  inherited, not touched.
- LightAttack: the v17 grip sits ~10 game cm from the idle grip, so the blade tip is ~10 cm off the idle pose at
  frames 0 and end (body 0.4 cm); front view hides the blade behind the body f14-18.
- HeavyAttack and HeavyAttackAlternate are longer in game time (1.40 -> 1.82 and 1.91 s); the DA damage windows and
  any combo/cancel timings need the new values on import.
