# Knight attack critique, 2026-10-31 (blind)

Bar: a shipped FromSoftware knight attack (Dark Souls 3 / Elden Ring): a clear wind-up, weight committed through hips and feet, a fast readable strike, follow-through, a grounded recovery, a believable blade arc and no pops.

## How this was judged

- **Evidence used.** I used only the 16 mp4s in `Local/knight-review-20261028/attacks-20261031/media/`. I did not read any docs, plans or earlier critiques.
- **Frame format.** Every clip is 2430x810 at 30 fps with three 810-px panels. Panel 0 is the front view, panel 1 the side view and panel 2 the three-quarter view.
- **Contact sheets.** I tiled every second frame of every panel, with frame numbers burned in, and also took full-resolution close-up strips at the key moments.
- **Measurements.**
  - Blade centroid speed in px/frame. The blade is segmented by its brown hue (R−B > 18), separately in each panel.
  - Mean absolute difference between consecutive frames, per panel.
  - Exact-duplicate checks on raw RGB frames.
  - PSNR between the two HeavyAttack clips.
- **Frame numbers** are 0-based video frames.

## 1. Per-video table

### Current clips (`cur-*`, in-game play rate)

| Clip | Weight | Wind-up | Strike speed / readability | Follow-through / recovery | Blade arc | Contact / feet | Defects (frames) | Verdict | Biggest problem |
|---|---|---|---|---|---|---|---|---|---|
| **LightAttack** (29 f, 0.97 s) | Best of the current set: wide lunge with the rear leg extended and a slight hip drop | f0–8: blade cocked high behind. Short but present | f8–11, peak 94–143 px/f. Fast and readable horizontal sweep | Blade parks horizontal f12–18. **Recovery f19–22 sweeps the blade back up through the strike plane at 85–102 px/f, almost the strike's speed** | The recovery retraces the strike path in reverse | Feet planted, no step | f19–22: reverse whip-back reads as a second swing | **APPROACHES** | The recovery replays the strike backwards at strike speed, so every light attack looks like two swings |
| **LightAttackTwoHand** (37 f) | None: legs locked straight, torso upright, no hip drop through the whole clip | f0–10: blade laid back over the left side. Slow and shallow | f11–13 at 54–85 px/f, then a **stall at f14→15** (diff energy 0.2 vs 1.0–1.2; p2 speed 3 px/f), then it resumes at f16 | Blade frozen horizontal f16–22, then raised straight back to vertical f24–34 | A flat horizontal plane, then a reverse lift | Static stance, no weight shift | f15: mid-strike hitch. f16–22: dead hold. f24–34: reverse recovery | **FAILS** | A standing mannequin with a mid-swing hitch at f15 |
| **HeavyAttack** (43 f) | Upright and one-handed. Some hunch only after the hit (f20–28) | f4–14: blade raised sideways to shoulder height. Too small and quick for a heavy | f14–19, peak 114 px/f. Readable | Blade buried behind the body f20–28, then **a second full swing back across the body f28–41** to the low start guard | Two opposed arcs: strike, then backhand return | Feet barely move | f28–41: recovery reads as a second attack | **FAILS** | No heavy wind-up or weight, and the recovery is a second swing |
| **HeavyAttackAlternate** (43 f) | Same as HeavyAttack | Same | Same | Same | Same apart from blade roll in f5–19 | Same | **Effectively identical to HeavyAttack**: PSNR ≥ 48 dB on f1–4 and f20–43, and 35–42 dB only on f5–19 | **FAILS** | A player cannot tell it apart from HeavyAttack. The slot is a duplicate |
| **HeavyAttackTwoHand** (49 f) | Upright, with mild knee bend only f24–32 | f2–14: blade laid back horizontal. Clear | f14–16 at 82–95 px/f, then **dead stop f17–19** (0–2 px/f, diff 0.1) with the blade pointed at the camera | After the stop the blade *resumes* a slow sweep at ~25 px/f (f20–36), then rises to vertical (f38–46) | Strike, stop, then a second slow drift. No continuous follow-through | No step | f17–19: baked stop. f20–36: stop-then-continue drift | **FAILS** | The strike hits a wall at f17, then drifts on, which reads as a hitch rather than weight |
| **HeavyAttackTwoHandAlternate** (70 f) | Good low, wide lunge stance during the hit pose (f24–46) | f0–12, then a charge hold f12–19 (1–5 px/f). Acceptable | f19–24 at 77–83 px/f. Blade crosses chest height in front of the torso (f21) | **Frozen f25–46**: ≤ 5 px/f for 21 frames (0.7 s), with diff energy at the compression floor (0.2–0.3). Recovery f47–60 lifts the blade up through the face line | Single diagonal-down sweep | Feet planted. No settling motion in the hold | f25: hard stop. f25–46: statue hold | **FAILS** | A 0.7 s statue freeze after the hit, with no breath and no settle |
| **LightCombo** (101 f) | Upright, legs near-straight, shoulder-width for hits 1–2 | Hit 1 f0–8, hit 2 f18–22, hit 3 f32–46 (a 10-frame near-static hold at the shoulder) | Three hits with real peaks (98, 126, 151 px/f), but **each one stutters**. f12: speed 1–14 between 56–78 (changed pixels 8.7k vs 38–45k on the neighbours). f27: 5–10 between 75–126. **f53, f54 and f55 are pixel-identical** (max abs diff 0), a 3-frame freeze right at the hit-3 peak | Blade wobbles low f60–72, snaps to the chest f72–74, rises to vertical f76–82, then 17 frames of idle tail (f84–100) | Three different planes, which is good variety | No steps for any of the three hits | f12, f27: stop-start hitches. f53–55: exact frozen frames. f84–100: dead tail | **FAILS** | Every hit stutters, including a 3-frame freeze at hit 3, and the legs never commit |

### Mixamo candidates (`mix-*`, source rate 1.0, plain attachment)

All nine start in a one-handed, blade-on-right-shoulder pose that differs from the game's two-hand vertical ready pose. That is a blend cost, not a pop. None shows a mid-clip hitch: there are no duplicate frames and no speed collapses inside a swing.

| Clip | Weight | Wind-up | Strike speed / readability | Follow-through / recovery | Blade arc | Contact / feet | Defects (frames) | Verdict | Biggest problem |
|---|---|---|---|---|---|---|---|---|---|
| **Attack1** (71 f, 2.37 s) | Heavy landing into a kneel. Fully committed | Very long (f0–32). The blade disappears behind the back during the leap (front view f16–30, blade area under 100 px) | Overhead slam f34–37 at 105–121 px/f. Very readable | Kneel with the blade on the ground f38–54, rise f56–70. **The clip ends mid-rise** (blade still travelling up at f70) | Clean vertical overhead plane | **Leaves the ground for about 0.6 s (f16–33), with the feet roughly half a body-height up** | f16–30: blade hidden in the front view. f70: unsettled end | **APPROACHES** (as a jump attack) | A half-body-height leap is a superhero move for an 8-ft plate knight. It only fits a jump or charged-heavy slot |
| **Attack2** (40 f) | Light: a spin with the **rear leg kicked off the floor f17–21** | f4–14: full body spin (back to camera f10–14) | f16–20 at 128–178 px/f. Fast | Ends crouched and mid-motion at f39 | Wide horizontal. The blade face crosses the torso f7–11 | One-leg skip | f17–21: airborne rear leg. f39: unsettled end | **FAILS** | Reads as a nimble swordsman's spin, not 8 ft of armour |
| **Attack3** (53 f) | **The best weight in the whole set**: strong hip coil, then a deep wide crouch f24–42 | f0–18: turns its back to the target, a clear coil | f21–26 at 105–151 px/f, then a second low sweep f39–46 at 40–52 px/f | Recovery cut off: at f52 the blade is still rising diagonally | Big continuous horizontal arc, then a low return | Deep, grounded stance. No visible foot skate on the sheets | f52: unsettled end. One-handed throughout | **APPROACHES** | Ends mid-motion, so it needs a settle tail. It is also two hits, not one |
| **Attack4** (31 f) | Upright | — | **No strike**: the blade twirls overhead (f6–18, peak 75–89 px/f) and returns to the shoulder | — | Helicopter loop over the head | Static | Whole clip | **FAILS** | It is a flourish, not an attack |
| **Slash1** (46 f) | **Real committed lunge**: big forward step and front-knee load f14–22 (side view) | f0–16: overhead lasso twirl of the blade. Readable but not FromSoft-like | f17–21 at 109–177 px/f. Diagonal-down cut, very readable | Blade carries through and drags low behind f24–30, then rises to shoulder rest f32–44. Settled end | One continuous arc, no reversal | Front foot plants and the rear leg extends. Grounded | f8–16: twirl wind-up. f24–30: blade nearly invisible in the front view (area 40–50 px) | **APPROACHES** | The twirl wind-up is busier than a FromSoft light. Everything after f16 is the right idea |
| **Slash2** (107 f, 3.57 s) | Mixed: good stepping in hits 1–3, then **a split-leg spinning leap f54–70** | Several | Peaks of 113–174 px/f on 4 or more hits, plus a slam at f72–76 | Kneel f76–92, rise f94–106. Ends mid-raise | Varied planes | Airborne split-leg spin | f54–70: acrobatics | **FAILS** | The spinning split-leap is anime choreography, out of character for the knight |
| **Slash3** (48 f) | Weak: legs nearly straight through the strike (f20–26). The coil is good (back to camera f14–18) | f0–18, clear | f22–26 at 91–134 px/f, a readable horizontal sweep | **Rebounds upward into an arm-straight vertical raise overhead f30–36**, then to the shoulder | The sweep is followed by an upward flourish | Upright | f30–36: flourish | **FAILS** | The follow-through goes *up* into a pose instead of loading the body down |
| **Slash4** (70 f) | Heavy slam and kneel | f14–40: spin with a **leg raised horizontal (front view f22–28)** and a hop | Overhead slam f40–42 at 122–155 px/f, with a clean impact stop at f43 | Kneel f42–58, rise f60–68. Ends unsettled | Vertical slam plane | Hop and crane-kick leg | f22–28: kick pose. f68: unsettled end | **FAILS** | The kick-spin wind-up undercuts an otherwise good slam |
| **Slash5** (42 f) | Locked in a deep crouch/kneel from start to end | f6–16, overhead | f17–19 at 105–140 px/f | Low drag, returns to the same crouch | Horizontal | **Never stands up** | Whole clip | **FAILS** | It is a kneeling attack and cannot chain from a standing ready pose |

## 2. Slot-by-slot: would a mix clip be visibly better?

| Game slot | Current verdict | Best candidate | Visibly better? | Reason |
|---|---|---|---|---|
| LightAttack | APPROACHES | **mix-Slash1** | **Yes** | Slash1 has a real step, a loaded front knee and one continuous arc that carries through and settles at the shoulder. The current clip whips the blade back along the strike path at f19–22, which players read as a double swing. Slash1 needs a rate of about 1.3–1.5 to feel light, and a blend from the two-hand ready pose |
| LightAttackTwoHand | FAILS | **Keep current** | No | All nine mix clips strike one-handed with the left arm flying free, so none is a two-hand grip. Putting a one-hand clip in a two-hand slot swaps one visible fault for another. Repair the current clip instead (fixes 1 and 2 below) |
| HeavyAttack | FAILS | **mix-Attack3** | **Yes** | Attack3 has a strong coil, a 151 px/f sweep and a deep committed crouch, which is the weightiest motion in either set. It has to be cut, or given a settle, after f46, because it ends mid-motion at f52 |
| HeavyAttackAlternate | FAILS (duplicate of HeavyAttack) | **mix-Attack1** | **Yes** | Anything distinct beats a pixel-near duplicate, and Attack1 has the clearest heavy telegraph: a long overhead wind-up, a ground impact and a kneel recovery. Caveat: the 0.6 s leap is out of tone for a standing heavy. Accept it only if this slot is a jump or charged heavy. Otherwise keep current and author a distinct alternate |
| HeavyAttackTwoHand | FAILS | **Keep current** | No | No mix clip delivers a two-handed horizontal heavy. Attack1's overhead grip is two-handed, but it is already the better use for the alternate slot, and its leap is the same tone problem. Repair the stop at f17–19 |
| HeavyAttackTwoHandAlternate | FAILS | **Keep current** | No | Its lunge stance is good. Its fault is the 0.7 s freeze at f25–46, which is fixable. Slash4 is the only other slam candidate, and its crane-kick wind-up is worse to a player than the current freeze |
| LightCombo | FAILS | **Keep current** | No (tie at best) | Slash2 removes the stutters, but adds a spinning split-leap (f54–70) that a player will notice more and that breaks the knight. Fix the current clip's hitches instead |

## 3. Top three fixes, ranked by how much a player would notice

1. **Remove the baked stops and freezes in the current clips.** Pass test: inside any active swing, no run of 2 or more consecutive frames below 3 px/frame of blade centroid speed, and no pixel-identical consecutive frames.
   - **LightCombo:** f53–55 are byte-identical; f12 and f27 are stop-starts.
   - **LightAttackTwoHand:** f15 stall.
   - **HeavyAttackTwoHand:** f17–19 dead stop.
   - **HeavyAttackTwoHandAlternate:** f25–46 statue. Replace the 21-frame freeze with a decaying settle that has continuous low motion: a breath, a hip settle and a blade sag.
2. **Stop the recoveries from replaying the strike in reverse.** Pass test: the recovery peak blade speed is no more than 40 % of the strike peak, and the recovery path differs from the strike path.
   - **LightAttack:** f19–22 runs at 85–102 px/f against a 94–143 px/f strike, along the same plane. Swap in mix-Slash1, or re-author the recovery so the blade continues through, decelerates low, and returns to guard on a different path.
   - **HeavyAttack:** f28–41 is a second full swing. Same fix.
   - **LightAttackTwoHand:** f24–34. Same fix.
3. **Make the heavy slots look heavy and distinct.**
   - **HeavyAttack:** replace it with mix-Attack3, cut or settled after f46.
   - **HeavyAttackAlternate:** it must stop being the same clip (PSNR ≥ 48 dB over 60 % of its frames). Use mix-Attack1 if a leap is acceptable; otherwise author a distinct overhead slam.
   - **Pass test:** the pelvis drops visibly during the strike in the side view, and the two heavy slots differ by under 30 dB PSNR on most frames.

## Secondary issues

- **Unsettled ends.** Every candidate that would be adopted (Slash1 excepted) ends mid-motion: Attack1 f70, Attack3 f52, Slash4 f68, Attack2 f39. Each needs a settle-to-guard tail or a blend-out window.
- **Ready-pose mismatch.** The mix clips start from a one-hand shoulder rest, while the game's ready pose is two-handed with the blade vertical at the chest. Expect a visible blend at the attack start until the idle and the attack start pose are reconciled.
- **Blade occlusion.** The blade goes nearly invisible in the front view during Attack1 f16–30 and Slash1 f24–30. That is fine for gameplay framing, but check it in the game camera.
- **Not measured.** Foot sliding was not measured per foot. No gross skate is visible on the sheets. Hand–hilt slips could not be confirmed or ruled out at this capture resolution, because the character is about 240 px tall. Missing evidence: a close-up hand camera is needed before grip quality can be signed off.

## Overall verdict

**FAILS the FromSoftware bar.** No clip in either set ships. The current set's dominant faults are baked hitches and freezes, and recoveries that replay the strike backwards. Three mix swaps would be visible upgrades to a player: Slash1 for LightAttack, Attack3 for HeavyAttack, and Attack1 for HeavyAttackAlternate (if a leap is acceptable). The four two-hand and combo slots must be repaired in place, because no mix candidate fits them.
