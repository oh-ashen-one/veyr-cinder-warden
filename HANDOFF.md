# HANDOFF — dragon-boss-fight (Can It Code north-star pass)

Date: 2026-10-28 · Branch: `claude-code-enhancements` · Host: Studio (midirstudio) · Status: **WIP, pipeline proven, runtime compile-only; switching to laptop**

## What this is

Replicating Can It Code's boss-fight process (YouTube `z1mgtUvTdqg`, Patreon source pack) on our Veyr dragon so we can
compare it with what we had. The shared-brain package `boss-fight-blueprint` (merged, agents-md PR #27) is the
reusable design; this branch is its first application. Decisions confirmed by Hari: creature motion may come from
AI video of our own rig through video2rig (the explicit exception to source-first animation; the knight stays on
sourced clips); MiniMax H3 Max at 768p was the first provider, Seedance 2.5 approved on 2026-10-28 evening after
MiniMax oversized the wings; one clip at a time, review before the next; merge of PR #27 approved and done; after
that "do whatever you want on your own". Hari approved the idle and roar on 2026-10-28 evening (laptop review); see Owner verdict below.

## Owner verdict (2026-10-28 evening, laptop)

Hari watched the before/after page served locally on the laptop (`Local/ab-idle-20261028/serve`, the Studio server
pid 53126 and its tailnet publish were stopped). Idle and roar approved with no change requests. He asked that the
shared brain and all future sessions use this method; promoted in agents-md PR #32 (video2rig = creature default).
The laptop clone is `~/dev/dragon-boss-fight`; only the `serve/` folder and `rangeserver.py` were copied, the full
Local/ bundle is not restored here yet.

## Repo / branch map

| Repo | Checkout (Studio) | Branch |
|---|---|---|
| oh-ashen-one/dragon-boss-fight (public, renamed from veyr-cinder-warden today) | `/Users/midir/dragon-boss-fight` | `claude-code-enhancements` (off `main` 0755faf, Hari created main from Codex's v030) |
| oh-ashen-one/video2rig (public fork of canitcode/video2rig, AGPL) | `/Users/midir/video2rig` | `mac-mps` (Apple Silicon port + `twins` and `limbs` creature.json settings) |
| oh-ashen-one/agents-md (private shared brain) | `/Users/midir/agents-md` | `main` has the package; draft PRs #30 (sync rebuild fix) and #31 (lessons) await Hari's merge |
| oh-ashen-one/veyr-animation-sources (private backups) | none | release `v2r-dragon-20261028` = this thread's Local/ artifacts |

Other sessions' checkouts on the Studio, do not touch: `/Users/midir/veyr-review-fable-20261021` (holds the dragon
rig source `Local/Blender/dragon-v1-20261021/Dragon_Rig_v008_weightfix.blend` and the hand-keyed idle), Codex's
dated `codex/*` branches. The Patreon pack is at `~/Downloads/BossFight-Unreal-Project` on the Studio only; never
put it in a repo.

## Where things stand

**Owner playtest backlog (2026-10-31):** `BACKLOG.md` on branch `fable/knight-complete-20261028` (worktree `~/veyr-knight-20261028`). Dragon items there: idle wings cramped against the body, a playthrough replay showing every dragon move, fight capped at 2.5 min (MaxHealth 2800 now), camera shake/fight feel (none in code), music/SFX.

**Dragon fix round 2 (2026-10-29, Studio, branch `claude-code-enhancements`, not pushed):**
- Nine v4 Actions built from the round-2 critique (`Local/video2rig/dragon/Dragon_<Move>_sd_v2r_v4.blend`, Actions
  `roar_v4`, `collapse_v4`, `bite_v4`, `land2_v4`, `rise_v4`, `air_hover_v4`, `air_land_v4`, `takeoff3_v4`,
  `air_fire_down_v4`); scripts in `tools/dragon_refine/v4/`. Move data (`Data/dragon/`) rebuilt from them; movedata tests OK.
- Measured on a CPU raster with the critic's definitions (no GPU render possible: foreign trainer at 100 %):
  `Local/dragon-review-20261029/measure_v4.json`. 27 of 31 table rows pass; fails: wing-body correlation at lag 0-4
  (all airborne, |r| 0.29-0.45; best at negative lag), takeoff last-24 centroid 0.14 BH, raw hover last-8 span, fire-down
  span drift 7.3 %. Per-item table: `docs/canitcode-enhancements.md`, section "Fix round 2".
- **Next:** run the render queue when the GPU is quiet: `tools/dragon_refine/v4/run_queue_v4.sh`
  (reads `Local/dragon-review-20261029/queue_v4.txt`, gpu_slot capture, adds the "Round 2 fix" cards to the review page),
  then a blind re-critique on the renders.

**Session end 2026-10-29 (laptop orchestrator, owner continuing on the Studio):**
- Dragon: 12 clips through video2rig (8 ground + 4 airborne), all on this branch (head c7056e0 before this note).
  Review page `Local/dragon-review-20261029/serve/index.html` (airborne section at `#airborne`). Open dragon items:
  air_land touchdown is authored not fitted, takeoff3 overshoots the hover by ~50 cm, a lying-start "rise" clip is a
  known gap, and a dragon fix round 2 (re-critique of round 1) has not been run.
- Knight: branch `fable/knight-complete-20261028` (worktree `/Users/midir/veyr-knight-20261028` on the Studio), read its
  own HANDOFF.md. Round 2 is built, packaged and pushed; the blind critic says round 2 is **not shippable** (blinks are
  a sprint loop, sprint-strafe waist twist, roll-attack exit slide, loop seams; sword and skate fixes unproven because
  no engine blends were rendered). Critique: `Local/knight-review-20261028/critique-round2.md` in that worktree.
  Its ranked fix list is the round-3 plan. Gates: 5 of 6 pass; integration fails on `locked_blink_left` only because
  the GPU is pinned by other sessions (12 fps, 0.4 s frames miss the 0.16 s hidden window). A frame-rate-independent
  gate (reads the game's own blink record) was in progress when the session ended; see the knight HANDOFF.
- Shared brain: agents-md PRs #30, #31, #32 (video2rig as the creature default) are open and need the owner's merge.
- Higgsfield: this session spent 589.5 credits on 15 Seedance clips; balance about 575.


- Pipeline works on this Mac end to end: start picture → clip → check → fit → review → Blender Action → scripted
  refinement → blind A/B. Clip to Action takes about four minutes once a reader exists.
- Idle: refined video2rig idle beats the hand-keyed idle in a blind A/B (47 vs 41); both still fail the shipped bar.
- Roar: landed on Seedance with a half-open-wings prompt (the rig's wings are fanned at rest; 1.27x span is the
  physical limit). Two usable Actions: `Dragon_Idle_v2r_v2.blend`, `Dragon_Roar_sd_v2r_v2.blend`.
- Move data measured from those Actions into `Data/dragon/*.json`; C++ loader and bone hurt capsules compile
  (UBT, editor and Shipping) but nothing is verified in PIE.
- Spend: 107.5 Higgsfield credits (3 MiniMax at 12.5, 2 Seedance at 35).

## Dragon clips 2026-10-29 (Seedance 2.5 move set, Studio)

Nine first-take clips plus two regenerations went through the pipeline overnight. Full numbers per clip are in
`docs/canitcode-enhancements.md` (Clip ledger rows and the section "Remaining clips (2026-10-28/29)").

**Fitted, refined, rendered** (Actions in `Local/video2rig/dragon/*.blend`, all 24 fps; scripts in `refine/`, gitignored):

| Move | Blend / Action | Frames | End | Check body / limbs | Fit miss, outline front / side |
| --- | --- | --- | --- | --- | --- |
| idle (earlier) | `Dragon_Idle_v2r_v2` / `idle_v2` | 90 | loop | 0.58% / 0.59% | 1.73 px, 0.81 / 0.90 |
| roar (earlier) | `Dragon_Roar_sd_v2r_v2` / `roar_sd_v2` | 121 | live, no return | 1.13% / 0.65% | 3.30 px, 0.76 / 0.85 |
| collapse | `Dragon_Collapse_sd_v2r_v2` / `collapse_v2` | 145 | lying flat | 1.17% / 0.77% | 4.72 px, 0.75 / 0.83 |
| death | `Dragon_Death_sd_v2r_v2` / `death_v2` | 169 | on the right flank | 0.93% / 1.36% | 7.07 px, 0.71 / 0.82 (weakest) |
| bite | `Dragon_Bite_sd_v2r_v2` / `bite_v2` | 121 | stance (closed onto frame 0) | 0.92% / 1.22% | 3.76 px, 0.78 / 0.80 |
| claw_swipe | `Dragon_ClawSwipe_sd_v2r_v2` / `claw_swipe_v2` | 121 | stance | 0.81% / 0.74% | 2.63 px, 0.77 / 0.88 (reader-78) |
| stagger | `Dragon_Stagger_sd_v2r_v2` / `stagger_v2` | 121 | stance | 0.85% / 1.17% | 4.49 px, 0.77 / 0.82 |
| land (land2 clip) | `Dragon_Land2_sd_v2r_v2` / `land2_v2` | 118 | stance | 0.86% / 0.88% | 2.83 px, 0.79 / 0.87 |
| rise | `Dragon_Rise_sd_v2r_v2` / `rise_v2` | 121 | stance | 1.17% / 0.99% | 3.07 px, 0.81 / 0.84 |
| idle_look | `Dragon_IdleLook_sd_v2r_v2` / `idle_look_v2` | 193 | loop | 1.02% / 0.91% | 2.00 px, 0.84 / 0.92 (best) |
| idle layered | `Dragon_IdleLayered_sd_v2r_v2` / `idle_layered_v2` | 193 | loop | (idle_v2 body + look head) | |

Keep all three idles (`idle_v2`, `idle_look_v2`, `idle_layered_v2`); the layered one has the look clip's 46 deg of head yaw on idle_v2's breathing, tail
and wings (measured table in the doc). Hari's call on which is the shipped idle.

**Failed the check, not fitted** (check FAIL is regenerated, never fitted): `land` 1.76% (body disagreement between the panels; fail line 1.5%),
`takeoff` 2.14%, `takeoff2` 2.41% (a lower rise in the prompt made it worse). Land passed once the hop was pinned low in the prompt (land2, 0.86%), but
the generator still hops 0.59 body heights. Finding: airborne moves need a flying start picture and a reader trained on it; likely cause (untested) is that
the start picture and reader assume feet on a floor.

**What the refinement does** (`refine/move/refine_move.py`, `refine/collapse/refine_fall.py` for collapse and death): trims a still tail, blends the end
onto frame 0 for moves that return to stance (24 to 36 frames), clamps wings to 1.27x of the frame-0 lateral extent (never needed tonight: raw peaks were
1.00 to 1.24x), lifts a wing root or the body when the fit goes under the floor, smooths tail spikes, plants feet by temporary IK bake only while grounded
(`ground=auto`) or the whole clip (`ground=all`). Collapse and death also relay the tail and clear the floor. Footage frame rate: claw_swipe and rise came
as 30 fps content with every 5th frame dropped (the tool detects and resamples to 24).

**Move data**: `Data/dragon/*.json` rebuilt for every Action with `tools/movedata/run_veyr.sh` (the runner now lists all Actions; `BLENDER_CAP=2` when a
render is running); 3 unit tests pass. Landing shock (land2): feet down frames 84 to 86, shock recorded at 3.583 s (7.24 m/s foot). Collapse: chest hits
at 3.167 s (10.9 m/s). Still nothing verified in PIE.

**Review page**: `Local/dragon-review-20261029/serve/index.html` (per move: Seedance source, hand-keyed before where one exists, raw fit, refined, three
angles; idle_v2 vs idle_look_v2 vs idle_layered in one row). `rangeserver.py` beside it (Safari needs byte ranges); no server is running. Renders live
in `Local/ab-idle-20261028/video/clip_<label>_{front,left,threequarter}.mp4` (labels CO, DE, BI, CS, ST, RI, LA, IL; 0 = raw fit, 1 = refined; IL2 = layered;
H* = hand-keyed before from the review checkout, read-only).

**Credits** (Higgsfield balance 1241.64 to 792.14): 449.5 spent this session on 11 renders = 9 first takes (379.5) + land2 + takeoff2 (35 each, both
5 s). 5 s clips cost 35; the 6, 7 and 8 s clips (collapse, death, idle_look) cost about 8.07 credits per second, derived (48.4 / 56.5 / 64.6; verify
against the transaction list). The failed first land and takeoff cost 35 each and produced no Action. Branch total with the earlier 107.5: 557.0.

**Fix round 1 (v3 Actions)**: from the blind critique (`Local/dragon-review-20261029/critique.md`). Eight new Actions, v2 untouched: `roar_sd_v3`, `collapse_v3`,
`death_v3`, `bite_v3`, `claw_swipe_v3`, `stagger_v3`, `land2_v3`, `rise_v3` (`Dragon_<Move>_sd_v2r_v3.blend`). Shared stance = idle_v2 frame 0 (frame 0 and last frame overlap
1.000, feet 0 mm off); claw and rise keyed at container time (no 4-frame stutter); land2 on a ballistic arc with touchdown at frames 74 to 75; stagger recoil at frame 2 with a
3 cm catch-step lift; roar flared to 1.20x idle (not the 1.25x target) with a tremor; bite jaw 38 deg; death holds from 110; collapse wing swept and folded. Numbers per fix:
`docs/canitcode-enhancements.md`, section "Fix round 1". Scripts in `Local/video2rig/dragon/refine/v3/` (gitignored). `tools/movedata/run_veyr.sh` now builds from the v3
Actions (roar ends on the stance: seam 0.00x); `Data/dragon/*.json` rebuilt; 3 tests pass.

**Airborne reader (trained)**: sibling project `Local/video2rig/dragon-air/` (hover start picture `start/start.png`, ground picture `start-ground/start.png`, perspective lens 50, same
cameras; Higgsfield media ids hover 3d674b17-e4f8-4a0b-b90c-a6edb3f55476, ground 2e796531-c58c-4f75-b7c0-762510fb5bc1), reader trained (9000 steps, 172 min total, held-out median front 7.31 px / side 6.68 px; `reader/reader.pt`) on the fork branch
`air-reader` (`~/video2rig-air`, opt-in `air` key in creature.json). Prompts: `dragon-air/clips/air_fire_down|air_land|air_hover|takeoff3.prompt.txt`.

**Airborne clips**: `air_hover`, `air_land`, `takeoff3`, `air_fire_down` fitted with the airborne reader and refined (`Dragon_AirHover|AirLand|AirTakeoff|AirFireDown_sd_v2r_v3.blend`,
Actions `air_hover_v3`, `air_land_v3`, `takeoff3_v3`, `air_fire_down_v3`). Checks are WARN (no panel check with perspective cameras); fits: 2.57, 4.84, 5.53, 4.31 px median. The landing and take-off fits
are weak (outline 0.61 to 0.71): air_land's touchdown is authored, takeoff3 overshoots the hover by 50 cm. Details: `docs/canitcode-enhancements.md` "Airborne clips". Move data has the four air moves
(`floor_metrics_valid: false`; fire_down window 3.333 to 6.667 s).

**Next steps**
1. Flying start picture for takeoff and land: render the start picture with the body off the floor (and a reader trained on it, about 3 h of MPS), then
   regenerate takeoff and a real tall hop. Until then takeoff, fly-hover stay on the hand-keyed Blender versions in the review checkout.
2. A lying-start clip for rise: the rise clip starts standing, 21 cm (mean vertex shift, rig scale) from the collapse's last frame; the engine would have to
   do the get-up. Generate a clip whose first frame is the collapse's end pose (needs its own start picture).
3. Owner review of the page, then pick the idle; then the engine session (bind capsules with the Customuse content, import Actions, blend collapse to rise, fix the
   18 cm rest-pose float in the import offset).
4. Death needs a second look (median miss 7.07 px, twist 51.7 deg on a foreleg, a leg dips 1.85 cm under the floor in transit); stagger's catch-step and the
   claw swipe's 7.8 cm of head overreach past the straight-neck figure are noted in the doc and uncorrected.

### 2026-10-29 evening (orchestrator, Fable 5.1): coupling convention fixed, rise-from-lying prompt drafted, renders still waiting on the GPU

- `tools/dragon_refine/v4/metrics_v4.py`: the wing/body coupling check scored the lag with the sign reversed. `lag_corr` pairs wing-tip velocity at t+l with body
  acceleration at t, so l < 0 is "wing leads body" (the physical order and the critic's "lag 0 to 4 frames"); the old 0..4 window measured body-leads-wing. The pass now uses
  `corr_wingleads0to4` (|r|, lead 0 to 4 frames); the old keys stay in `measure_v4.json` for comparison. Re-measured on CPU: takeoff3_v4 0.45 -> 0.59 (lead 3),
  air_hover_v4 0.37 -> 0.45 (lead 4), air_fire_down_v4 0.29 -> 0.42 (lead 3), air_land_v4 0.33 (lead 0). All still under 0.6: no pass flips; the 27 of 31 count stands.
  Sign is negative throughout, as expected (downstroke lifts the body), so the critic's criterion is magnitude.
- Rise from lying: prompt drafted at `Local/video2rig/dragon/clips/rise_lying.prompt.txt` (first frame = collapse end pose: flat on the belly, chin on the floor, wings
  half-folded; get-up forelegs first, shake, settle to the standing stance). Still needed, in order: a start picture rendered from `Dragon_Collapse_sd_v2r_v4.blend`'s last
  frame (Blender counts as a GPU client, so it waits with the renders), one Seedance 2.5 clip (decline the preset recommendation), reader on the lying start (~3 h MPS), fit, refine.
- `run_queue_v4.sh` renders, the roar membrane check and the blind re-critique are still waiting: another session's video2rig reader trainer has held the GPU at 97-100 % all afternoon.
  Owner instruction: do not override the gpu_slot utilization gate; wait for a quiet GPU or an explicit go.
- From the Hulk session (2026-10-29 evening): upstream video2rig `reader/fit.py` lock_feet adds the floor-relative rest height to an absolute height (fix c60a645 on `brute-lockfeet-floor`, not yet on `mac-mps`). Checked for the dragon: `rig/mesh.npz` rest-mesh minimum along up is 0.0000 in armature space and `dragon-air/creature.json` pins `floor: 0.0`, so the bug is a no-op here (consistent with no "end of range"/leg-fold warnings in our fits); no refit, no cherry-pick needed unless the floor changes. Two upstream-tutorial tips adopted for the next clips: prompts carry "Shot at a very fast shutter speed: no motion blur at all, every frame is sharp" (added to `rise_lying.prompt.txt`), and the lying-start reader should start from the ground reader with `prepare --init <reader.pt>` (far fewer steps than the ~3 h from scratch).
- gpu_slot gotcha: any python whose command line contains "video2rig" (even a data path) is counted as an ML GPU client. Run CPU measurements with a command line that avoids
  the word (cd into the work dir and pass `.`), or the machine-wide foreign-client cap is consumed by a CPU script.

## What happened this session

- `docs/canitcode-enhancements.md`: plan, gap analysis, rule checks, clip ledger, every A/B and fit number, the
  wing finding, provider costs (commits dc71d2c … 0ae3440).
- `tools/movedata/` + `Data/dragon/`: measured moves, capsules, tempo, sounds (3aa61c3, 6124a05).
- `Unreal/Veyr/Source/Veyr/VeyrMoveData.*`, `VeyrDragonMoveData.cpp`, hooks in `VeyrDragon.*`: data-driven
  windows and capsules, console commands `veyr.MoveData.Dump/Draw/Play`, `veyr.MoveData.HurtBlocksPawn` (6334c7b).
- Fork `video2rig` `mac-mps`: device helper (cuda/mps/cpu), MPS resize workaround, `twins`, `limbs`, docs/MACOS.md.
- Shared brain: `boss-fight-blueprint` package (teardowns, inventory, Apple Silicon reference, Veyr lessons log),
  routing row, creature exception, search keywords; merged as a675572.

## Verification done

- `brain doctor` after the merge: revision a675572, freshness verified, no issues; `brain resolve
  boss-fight-blueprint` and `brain search boss fight` rank the package first.
- `video2rig check` on idle 0.58%, roar_sd2 1.13% (fail line 1.5%); fits with warnings none.
- Two blind Opus critics (videos only); numbers in docs and `Local/ab-idle-20261028/critique*.md`.
- UBT `Build.sh VeyrEditor Mac Development` and Shipping: `Result: Succeeded`, no new warnings.
- `tools/movedata/test_build_moves.py`: 3 passed. Bundle sha256 recorded in the release's SHA256SUMS.

## Not done / explicitly out of scope

- No PIE or packaged run of the data-driven dragon. This clone has no `Content/Characters/Customuse` (native
  character content is not in git; it is in Codex's checkout and the private backups), so capsules cannot bind here.
- Owner verdict received 2026-10-28 evening: idle and roar APPROVED ("much better", roar "so, so good"). Next clips unblocked.
- Idle gap: no head intent (one breathing sine); needs an 8 s clip or a second "look" clip layered in Blender.
- Roar: does not return to stance (engine blend into idle needed); tail whip still a spike; v3 hand-flare end pose
  differs from start.
- First post-merge shared-brain release lacks search keywords until PR #30 merges and a `brain sync --force
  --strict` runs; mandatory routing row works regardless.
- Remaining clips (claw swipe, bite, stagger, collapse, death, takeoff, land), the brain by reach, fight-feel
  system, lab flags, Niagara, Lumen/VSM defaults: not started.
- `Local/ab-idle-20261028/frames/` (PNG frame sets) and `Local/video2rig/dragon/reader/renders/` were left out of
  the bundle; they regenerate.

## Next steps

1. On the laptop: restore the bundle (below), then `brain sync --force --strict` once PR #30 is merged.
2. Done: owner approved idle and roar. Shared-brain PR #32 (plus #30, #31) makes video2rig the creature default; Hari merges.
3. Engine session on the Studio with the native content: bind capsules (`veyr.MoveData.Draw 1`), import the two
   Actions, rerun the collision and stance trials, fix the 18 cm rest-pose float in the import offset.
4. Next clip (claw swipe) on Seedance with the gesture described inside the rig's reach; same check/fit/refine/A/B.
5. Promote `Local/video2rig/dragon/refine/` scripts into `tools/` or the fork so the refinement is reusable.

## Key files

- `docs/canitcode-enhancements.md` — the full record: plan, ledger, numbers, lessons, provider finding.
- `tools/movedata/README.md` — move-data schema, units, commands, thresholds.
- `Data/dragon/moves.json`, `boxes.json` — measured windows and capsules at game scale (x21.56).
- `Unreal/Veyr/Source/Veyr/VeyrMoveData.h` — loader structs mirroring the blueprint's contract.
- `Local/video2rig/dragon/creature.json` — root, facing, hinges, `twins`, `limbs`, wing wrist range (restored from bundle).
- `Local/video2rig/dragon/clips/*.prompt.txt` and `*.json` — prompts and provenance per clip.
- `Local/ab-idle-20261028/critique.md`, `critique-round2.md` — blind critic reports; `private/mapping.json` — labels.

## How to run it

```bash
# restore artifacts (laptop): private release asset, ~540 MB
cd ~/dragon-boss-fight && mkdir -p Local && cd Local
gh release download v2r-dragon-20261028 -R oh-ashen-one/veyr-animation-sources -p 'veyr-v2r-dragon-20261028.tar.gz' -p SHA256SUMS
shasum -a 256 -c SHA256SUMS && mkdir -p restore && tar -xzf veyr-v2r-dragon-20261028.tar.gz -C restore
mkdir -p video2rig ab-idle-20261028 && mv restore/dragon video2rig/dragon && mv restore/ab-idle/* ab-idle-20261028/ && mv restore/movedata movedata

# video2rig fork (Apple Silicon)
git clone -b mac-mps https://github.com/oh-ashen-one/video2rig.git ~/video2rig && cd ~/video2rig
python3.12 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt torch torchvision
export V2R_BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
P=~/dragon-boss-fight/Local/video2rig/dragon
.venv/bin/python -m video2rig check "$P" roar_sd2 && .venv/bin/python -m video2rig run "$P" roar_sd2 && .venv/bin/python -m video2rig review "$P" roar_sd2

# move data (headless Blender) and tests
cd ~/dragon-boss-fight && bash tools/movedata/run_veyr.sh && python3 -m unittest tools/movedata/test_build_moves.py

# Unreal compile only (Studio)
"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" VeyrEditor Mac Development -Project=/Users/midir/dragon-boss-fight/Unreal/Veyr/Veyr.uproject -NoUBA -NoXGE -NoFASTBuild -NoSNDBS -MaxParallelActions=4 -WaitMutex
```

## Running processes / infra

- Nothing running on the Studio for this thread as of 2026-10-29 07:30: the old page server (pid 53126) and
  `tailscale serve --tcp 8790` were turned off on 2026-10-28 evening at the owner's request. No engines, no LaunchAgents.
- Other sessions' processes were on the Studio GPU all night (an Unreal Editor under `/Users/Shared/Epic` and Markhor
  Meadow video2rig jobs); device utilisation read 100%. They are not ours; do not touch them.
- The review pages are served on the **laptop** only: dragon `Local/dragon-review-20261029/serve` on port 8790,
  knight `Local/knight-review-20261028/serve` on port 8791 (`python3 rangeserver.py serve <port>`), with the Chrome
  lazy-load patch applied. Both folders are rsync copies of the Studio ones; the Studio copies are the source.

## Picking this up on the other machine

- Branch is pushed to: `origin/claude-code-enhancements` — `git clone -b claude-code-enhancements https://github.com/oh-ashen-one/dragon-boss-fight.git ~/dragon-boss-fight`
- Written on: Studio
- **Local-only, did NOT travel:** the Patreon pack (`~/Downloads/BossFight-Unreal-Project`), the teardown notes
  (`~/canitcode-teardown/`, their content is in the shared-brain package), review frames and reader renders
  (regenerable), the Downloads copies of the videos.
- **Needs rebuilding there:** `~/video2rig/.venv` (torch with MPS), Blender 5.2, ffmpeg; Unreal 5.8 if compiling.
- **Must already exist there:** `gh` auth for oh-ashen-one, Higgsfield MCP for clips, shared brain installed
  (`brain doctor`).
- **Studio-only:** engine sessions with the native Customuse content, GPU-heavy reader training (laptop MPS works but
  slower), the served page.

## Secrets

- None new. Higgsfield is through the MCP connector; no keys in files. `VEYR_BLENDER_OWNER`/`VEYR_BLENDER_WORK`
  are names used by older Blender MCP tooling, not needed for this thread.

## Gotchas

- Generators draw gestures the rig cannot do (wings 2x span); describe moves inside the rig's measured reach.
  `check` does not catch a part that grows; eyeball the peak frame against the start picture.
- Changing the start picture, rig or model means a new reader (about 3 h on the Studio's MPS).
- Tripo rig: Left/Right limb names mean front/hind; wing PosZ sits at -Y; no root motion on `tripo::Root`
  (body travels on `tripo::Spine_0`); rest pose floats 18 cm at game scale.
- Blender scripts must run `--background --factory-startup` or the MCP add-on registers itself into exports.
- Python's stock `http.server` cannot serve byte ranges: Safari will not play the videos; use `rangeserver.py`.
- The Studio's Tailscale app only passes ports published with `tailscale serve`.
- The always-on shared rules file sits at 11,997 of 12,000 bytes; any new route needs a trim first.
- Do not rename rig bones to fix tools: the Unreal skeleton and trained readers are keyed to the names.

## Resume command

```
work out of ~/dragon-boss-fight on branch claude-code-enhancements, read HANDOFF.md, restore the v2r-dragon-20261028 bundle into Local/, pick up at next steps
```

### 2026-10-30 03:05 UTC (orchestrator, Fable 5.1): fix-round-2 renders done, critic and lying start picture running

- GPU handed over by the Hulk session (midir-60) at 02:37 UTC. `tools/dragon_refine/v4/run_queue_v4.sh` rendered all nine v4 Actions (AH4, TK4, AL4, FD4, RS4, CO4, RI4, BI4, LA4; `Local/dragon-review-20261029/queue_v4.log`, one Blender at a time through `gpu_slot.sh capture`, exit 0) and rebuilt the review page (`serve/index.html`, "Round 2 fix" column, lazy-load kept; served on port 8790).
- Running: blind re-critique of fix round 2 on the ground clips plus the first critique of the four airborne clips (opus-critic, videos only, magnitude coupling criterion with the wing leading 0-4 frames) -> `Local/dragon-review-20261029/critique-round3.md`; the lying start picture for the rise clip (sonnet-builder: collapse v4 end pose rendered with the ground cameras via `render_start_air.py --cameras-from`, into `Local/video2rig/dragon-lying/start/`, note in `docs/dragon-lying-start-20261030.md`).
- 03:15 UTC: lying start picture rendered (`Local/video2rig/dragon-lying/start/start.png`, collapse_v4 frame 144 with the ground cameras, lowest vertex 1.5 mm above the floor, far wing tip touches the side panel edge; `docs/dragon-lying-start-20261030.md`). One Seedance 2.5 clip generated from it (`Local/video2rig/dragon/clips/rise_lying.mp4` + `.json`, 6 s, 145 frames at 24 fps, 720p, job 461da1de..., 42 credits quoted; the MCP's "IN THE DARK" preset recommendation was declined with declined_preset_id 24bae836-2c4a-48e0-89b6-49fcc0b21612). Eyeballed: lies still ~3 s, pushes up forelegs first, hind legs, head shake with wings raised (span briefly wider than the prompt allowed, frames ~100-115), settles to stance by frame 143. Copied into `Local/video2rig/dragon-lying/clips/`. `video2rig check`/fit need the project's own reader: `python -m video2rig.reader.prepare Local/video2rig/dragon-lying --blend <model.blend> --init Local/video2rig/dragon/reader/reader.pt` (~3 h MPS, Blender pose renders inside) is queued AFTER Markhor's two readers AND the Hulk dense reader (owner's overnight training order relayed by midir-60 at 03:40 UTC: Markhor R1 -> Markhor R2 -> Hulk dense reader ~2 h -> this dragon reader ~3 h; trainings back to back, never alongside engine launches); start it only on midir-60's "Hulk reader done" message and announce to both before starting (likely ~10:00 UTC or later). Then check, run, review, refine, A/B on the page.
- 03:25 UTC: blind critique of fix round 2 + first airborne critique: `docs/dragon-critique-round3-20261030.md` (copy of `Local/dragon-review-20261029/critique-round3.md`). Shippable: bite BI4, land2 LA4, hover AH4, takeoff3 TK4, fire-down FD4. Not: air_land AL4 (one-frame 0.22 BH teleport at 63->64, soft landing, frozen end), rise RI4 (floating get-up blend, pop at 43->44), collapse CO4 (end pose 0.69 of standing height vs source 0.47, tented/rigid wing), roar RS4 (halves differ 10 %, span 1.26x vs source 1.10x, regular 4-frame buzz). Orchestrator sign-off: roar target becomes the approved source's 1.10-1.15x span (overrides round 2's 1.22x). Fix round 3 (v5 Actions) running on opus-builder: AL4, RI4, CO4, RS4 + cheap polish, re-measure the five shippable ones (no regressions), queue_v5 renders through the gated queue, "Round 3 fix" column, movedata rebuild + tests, hover loop marked 0-129.
- 04:40 UTC: fix round 3 (v5 Actions) authored and measured on the CPU by opus-builder (`docs/canitcode-enhancements.md` "Fix round 3", `Local/dragon-review-20261029/measure_v5.json`, blends `Local/video2rig/dragon/Dragon_{Roar,Collapse,Rise,AirLand,Bite}_sd_v2r_v5.blend`, scripts `tools/dragon_refine/v4/{refine_v5,lib_v5,measure_v5,metrics_v5,build_review_page_v5}.py`, `run_v5.sh`, `run_queue_v5.sh`): air_land v5 passes all targets (frame-63 pop gone, braking span +33 %, drop 0.361 BH, end matches stance), rise v5 passes (no pop at 43, two feet down every frame, breathing 0-7), roar v5 passes the source-matched targets (span 1.136x, halves 3.2 % apart, irregular tremor), bite v5 (twitch gone, 3/4 wing hook fixed); collapse v5 front height 0.531 raw (~0.506 to the critic) still a hair above 0.50 (wings on the flanks fixed); land2 keeps v4 (v5 hop hit but foot jump worsened), hover/fire-down/takeoff keep v4 (hover/fire-down v5 refines never started). Hover loop marked frames 0-129 in `Data/dragon/moves.json`; `tools/movedata/annotate_air.py` now takes the touchdown frame from the sampled action; tests 3 OK.
- NOT DONE (GPU pinned at 97-100 % by the other sessions' reader trainings from 01:05 ET, owner's overnight order): the v5 review renders (`tools/dragon_refine/v4/run_queue_v5.sh`, queue `Local/dragon-review-20261029/queue_v5.txt`: AL5, RI5, CO5, RS5, BI5 all pending, done labels are skipped on re-run; then `build_review_page_v5.py` adds the "Round 3 fix" column) and the move-data rebuild (`bash tools/movedata/run_veyr.sh` with `BLENDER_CAP=2`, then `python3 -m unittest tools/movedata/test_build_moves.py`; `Data/dragon/` is still v4 apart from the hover loop range), then the hover and fire-down v5 refines, then a blind critique of the v5 column. Run these when util drops (between or after the trainers).
- Next, in order: (1) v5 renders + move data + tests as above; (2) blind critique of the v5 column (critic's thresholds in `docs/dragon-critique-round3-20261030.md`); (3) dragon lying reader (`python -m video2rig.reader.prepare Local/video2rig/dragon-lying --blend <model.blend> --init Local/video2rig/dragon/reader/reader.pt`, ~3 h MPS) only after Markhor's "both readers done" message (order: Hulk dense reader 01:05 ET -> Markhor R1 -> Markhor R2 -> this), then `check`, `run`, `review`, refine of `rise_lying`, A/B against the authored rise v5. Engine-done messages were sent to midir-5b and midir-60 at 04:30 UTC.
- 15:30 UTC (owner rule relayed by the Hulk session, midir-60): a fidelity gate is not a quality gate. The Hulk run passed every video2rig gate for 18 h and shipped clips the owner called "nothing". Applies here before any further video2rig spend: (1) before scaling past a pilot clip, put the take beside the clip it replaces (close-up, same angle) and ask whether a human would call it visibly better; (2) if the first blind comparison is ties or marginal, STOP and report "ceiling is low" with the levers (provider, start picture, timing freedom, exaggeration), even if the goal says not to stop; (3) "tie ships" means "same ships", never the bar for an upgrade run. For this project: the rise_lying Seedance clip and any reader-trained refine ship only if the blind A/B against authored rise v5 says visibly better; the ~3 h lying-reader training is justified only by that take looking better than rise v5 first (judge the clip against the v5 render before training, not after). Memory: `feedback_fidelity_gate_not_quality_gate.md`.
- 16:25 UTC (12:25 ET): Markhor (midir-5b) schedule: its first reader done ~13:45 ET, second (chop) ~16:15 ET; it messages on each event and on any stall. GPU is at the 3-client cap (Markhor trainer + two short Hulk jobs). Holding every launch of mine (v5 renders, movedata, trainer) until the "both readers done" message. Before the lying reader: CPU-only side-by-side of the raw rise_lying clip vs the rise v5 render; skip the 3 h training and tell both sessions if it is not visibly better.
- 16:50 UTC (12:50 ET): owner relay via Markhor: keep a localhost progress page open in Chrome and message all sessions on milestones. Progress page `Local/progress-20261030/index.html` served on port 8796 (`python3 progress-20261030/rangeserver.py progress-20261030 8796` from `Local/`), opened in a new Chrome window with 8790 and 8795; URL sent to midir-5b (Markhor), midir-60 (Hulk), midir-d3 (Invincible). Update the page at each milestone.
- 17:40 UTC (13:40 ET): owner relay via Markhor: progress pages must be visual, no text. Page on 8796 rebuilt: GPU/CPU gauges, who is on the GPU, pipeline graphic (stage states derived from files: queue_v5_done.txt, serve/*_r3_*.mp4, Data/dragon/moves.json mtime, flags/), rise-from-lying start picture + Seedance clip + rise v5 slot, per-move rows source / old rig / round 2 / round 3 (videos cross-origin from 8790, fit-frame strips mirrored into m/), knight r4h vs r5 and r2 vs r3 pairs (8795, 8792). Feed: `Local/progress-20261030/status_loop.py` (nohup, 15 s; page polls 10 s). Manual stage flags: touch `Local/progress-20261030/flags/{movedata,crit4,ab,gpu_go}`; `flags/note.txt` shows a short line under the banner. Peer pages: Markhor 8092, Hulk 8777/progress.html, Invincible 8810.
- 20:35 UTC (16:35 ET): GPU turn opened on Markhor's "both readers done" (16:09 ET). Round-3 renders done (AL5, RI5, CO5, RS5, BI5; the bite queue line had lost its leading slash, rewritten) and the "Round 3 fix" column written on 8790. Move data rebuilt from the v5 Actions (`Data/dragon/moves.json`, `boxes.json`; roar 121, collapse 157, bite 93, rise 150, air_land 145 frames; hover loop 0-129), tests 3 OK. Side-by-side of the raw Seedance rise_lying clip vs the rise v5 render (`Local/progress-20261030/m/rise_ab.mp4`): blind Opus critic says the AI clip is CLEARLY better (four readable beats: still, laboured push, wing-flare stand, settle; v5 reads as a continuous float with a spliced rear) and the gain from re-authoring is clear, with two conditions (trim the opening hold to 1-1.5 s, make the settle loop into idle). `docs/dragon-rise-ab-20261030.md`. So the lying reader runs. Lying project prepared: `Local/video2rig/dragon-lying/model.blend` (collapse_v4 frame 144 baked as the current pose, animation cleared) and `rig/` (export_rig.py); launch script (util preflight, 6000 steps from `dragon/reader/reader.pt`) waits for Markhor's second "capture done" (≤16:50) and Hulk's "baseline captures done" (≤17:15), then Invincible trains, then Hulk captures.
- 20:40 UTC (16:40 ET): lying-start reader STARTED (pid in `Local/video2rig/dragon-lying/prepare.log`; `python -m video2rig.reader.prepare Local/video2rig/dragon-lying --blend Local/video2rig/dragon-lying/model.blend --init Local/video2rig/dragon/reader/reader.pt --steps 6000`, launched after a 3-reading util preflight at 26-30 %, one MPS client). ETA ~18:30-18:45 ET. Announced to midir-60 and midir-d3; order after it: Invincible training, then Hulk build + captures; Markhor is completely done (16:35). Fix round 4 (v6) critique in `docs/dragon-critique-round4-20261030.md` (rise, bite ship; air_land wing snap, collapse height, roar lopsided wings fail); v6 scripts being written on the CPU, Blender authoring + renders after the reader (`run_queue_v6.sh`, then movedata if the v6 moves pass).
- 21:05 UTC (17:05 ET): fix round 4 (v6) scaffold pushed by opus-builder (414f130): `tools/dragon_refine/v4/{refine_v6,measure_v6}.py`, `run_author_v6.sh` (one gated Blender at a time; measures, promotes passing moves to `Dragon_<Move>_sd_v2r_v6.blend`, comments failing ones out of `queue_v6.txt`), `run_queue_v6.sh`, docs "Fix round 4". measure_v6 is recalibrated to the critic's render readings (v5's raster had the wrong definitions for roar halves and bite near-wing). Only one air_land trial was built before the reader started: fold 22 %/frame (target ≤12 %), hold life and tail whip pass, contact drop regressed (0.076 vs 0.3 in 6 frames); next settings `fold_new_b=116 fold_lin=0.8`, fold a frame or two earlier. Roar/collapse/bite v6 not authored. Resume after the GPU is free (after Invincible's training and Hulk's captures): `tools/dragon_refine/v4/run_author_v6.sh air_land roar collapse bite` (then the FORCE/OPTS line in the docs for air_land), then `run_queue_v6.sh`, then run_veyr.sh for moves that pass.
- 22:15 UTC (18:15 ET): lying-start reader DONE in 89 min (poses 269 s, renders 103 s, training 4980 s / 6000 steps): held out median 6.4 px front / 5.16 px side (p90 38.6 / 31.5), off-bone points 7.4 / 7.3 px; `Local/video2rig/dragon-lying/reader/reader.pt`, `reader-train.json`, `prepare-clock.json`. GPU handed to Invincible at 18:10 ET (its training pid in its own HANDOFF, ~2.5-3 h), Hulk after it. `video2rig check dragon-lying rise_lying --cpu`: body 0.0062, limbs 0.0201 of the height (panel disagreement warning on the limbs), confidence 0.62. `run --cpu` + `review --cpu` running on the CPU (`Local/video2rig/dragon-lying/run_rise_lying.log`, `review_rise_lying.log`, output in `work/rise_lying/`).
- 22:30 UTC (18:30 ET): `video2rig run --cpu` on rise_lying with the lying reader (106 s on the CPU): outline match 0.774 front / 0.807 side, worst frames 104-120 (the wing-spread shake), max twist VeyrWingPosZRoot 59.9°, biggest jump 17.8° at frame 134 (wing fold), 0 frames under the floor, `tripo::0_Right_Limb_2` at its joint limit for 119 frames; `work/rise_lying/{fit.npz,report.json,review.mp4}`. Review film read: the rig reproduces the clip's beats (still 0-72, push-up 80-100, wing-spread shake 107-128, settle 134-145); the shake wings are spread flat/sideways where the video has them raised and back, the rest tracks. Film on the dashboard (8796, "reader fit on the clip"). Next (needs Blender through gpu_slot, so after Invincible + Hulk): refine rise_lying in Blender as `Dragon_RiseLying_sd_v2r_v1.blend` (wing cleanup frames 100-134, hind-limb limit, foot lock, trim the opening hold to ~1-1.5 s, settle into the idle pose for a clean handoff), render it for the page, A/B against rise v5 (critic conditions in `docs/dragon-rise-ab-20261030.md`), then movedata if it wins. Then v6 authoring + renders (`run_author_v6.sh`, `run_queue_v6.sh`).

- 22:55 UTC (18:55 ET, Sonnet 5.5 builder for the orchestrator): rise_lying refine AUTHORED, NO Blender started (GPU pinned by another session). `tools/dragon_refine/v4/`: `lib_rise_lying.py` (numpy stages + CPU skinner, `info`/`dry`/`dump` commands), `prep_wings_rl.py` (CPU silhouette solve of wings 100-134 against the clip masks, twist cap 25), `refine_rise_lying.py` (Blender: import via video2rig import_motion, trim to hold_s=1.25 from raw frame 44 with 6-frame ease from the collapse end pose, wings cleaned, hind knee off its limit, IK foot lock, 8/16-frame blend into idle_v2 frame 0, last frame pinned), `measure_rise_lying.py`, `run_rise_lying.sh`, `run_queue_rl.sh`, `build_review_page_rl.py`; doc "Rise from lying" in docs/canitcode-enhancements.md. CPU-verified: wings (twist 59.9 -> 22.5 deg, step 17.8 -> 8 deg, outline match in the wing window 0.68/0.65 -> 0.75/0.69, `Local/video2rig/dragon-lying/refine_rl/wings_rl.json`), trim (101 frames, hold 1.46 s), end == idle (0.3 mm), CPU skinner == video2rig skin (1e-8 m) and == Blender idle dump (0.3 mm). UNTESTED: everything inside Blender (import, Clip write, IK foot lock, end pin, blender-vs-CPU skin check, dump), the render queue, the page card. Resume once the GPU is free: `tools/dragon_refine/v4/run_rise_lying.sh` (`FORCE_RENDER=1` renders even if a measure check fails; `foot_lock=0` if the IK step misbehaves; log `Local/video2rig/dragon-lying/refine_rl/log_refine.txt`).
- 2026-10-31 02:55 EDT (Opus 5.5 after the owner's model switch; midir-60 coordinates overnight): **Rise from lying v1 refined, rendered, on the page** (`Local/video2rig/dragon/Dragon_RiseLying_sd_v2r_v1.blend`, Action rise_lying_v1, 113 frames / 4.7 s; label RL1, "Rise from lying" card on 8790). All 8 measure checks pass (no pops, body/feet on the floor, 1.5 s hold, wing twist ≤25°, wing step ≤8°, last frame = idle_v2 frame 0, wing-window silhouette better than the raw fit). Final blind call (one Opus critic, same camera vs authored rise v5): clearly better than v5, but NOT SHIPPABLE on (1) dead stop at the end, (2) floating near front foot 64-82, (3) near wing jutting forward like a spear 60-90. Fixed since: (1) tail ease (last 10 frames retimed to 22, ease-out) + 12/24-frame blend into idle; floor lift clears the feet and has a 5.5 mm target (the Blender vs CPU skinning gap is ~4-6 mm). Blender foot lock is OFF (`foot_lock=0`): with the retimed tail it sank a front foot 2 cm; without it the feet stay within 1 mm. Wing solve also off (`wing_src=none`): the heuristic clean passes every check and looks the same. **Open:** (3) the forward near wing is in the raw fit itself; it needs hand-keying in Blender (frames ~60-90 of rise_lying_v1), then a re-check. Not yet in move data (rise stays v5 until the owner accepts RL1). Run: `FORCE_RENDER=1 tools/dragon_refine/v4/run_rise_lying.sh floor=0.0055 foot_lock=0 wing_src=none`.
- Fix round 4 (v6) authored: **bite v6 passes and ships** (near wing ≥0.7, v5 checks kept; rendered BI6, move data rebuilt, tests OK). roar v6 fixed the halves/span but brought back a buzz, collapse v6 still lies too high (hips), air_land v6 fold still 22 %/frame: those three keep v5 (`Local/dragon-review-20261029/measure_v6.json`).
