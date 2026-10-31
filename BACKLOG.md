# Veyr backlog (owner playtest feedback, 2026-10-31)

Owner played the v030t Shipping build (`Builds/Unreal-Mac-20261031T171249Z`) on 2026-10-31 and said it is "looking much
better now". These are his notes for the next session, in his order, with the facts checked in code on the same day.
Start with `HANDOFF.md`, then pick items here. Each item needs a before/after the owner can watch (bare page: video plus
BEFORE/AFTER label, no text walls) and a blind Opus critic before it is called done.

## 1. Knight running feels blocky, not like a sprint
- Owner: "the running still feels a bit blocky. It doesn't feel like you're actually sprinting, and it doesn't seem too fluid."
- Runtime run clips: Run / RunAlternate / RunTwoHand (approved Fab run v18 family, see `docs/knight-complete-20261028/local-assets-provenance.json`), RunStop join 0.30 s.
- Look at: sprint speed vs clip stride (foot slide), Shift-sprint state (separate sprint clip or only a rate bump?), lean/acceleration, camera FOV/lag at sprint, run-start/stop blends. Source-first: Mixamo/Fab sprint candidates before any authoring.

## 2. Dragon idle: wings cramped against the body
- Owner: "In the idle animation for the dragon, his wings are super cramped against his body."
- Idle is owner-approved (2026-10-28) but the folded wings now read wrong in play. Fix as a wing-spread layer or a new idle take; keep the breathing. Dragon tooling: `~/dragon-boss-fight` branch `claude-code-enhancements`, `tools/dragon_refine/`, move data `tools/movedata/run_veyr.sh`.

## 3. Playthrough that shows every dragon animation
- Owner: "I don't think I saw all of the animations the dragon had. We need a playthrough where you get to see each individual part as it goes."
- Build a scripted replay mode (like `VeyrReplay` lockon/blendproof) that walks the dragon through every move and state in order: Fire, FlyAway (takeoff, hover, fire-down, air-land), ClawSwipe, BackStomp, TailSmack, Bite, Buckle, Collapse, Exposed, Rise, Dead, plus idle, walk/turns, roar. Record it as one video with a small move-name caption and serve it on a bare page.

## 4. Fight too long: 2.5 minutes max
- Owner: "The dragon has too much health, and it takes forever to kill him. It should be a 2.5-minute boss fight max."
- Now: `AVeyrDragon::MaxHealth = 2800` (`Unreal/Veyr/Source/Veyr/VeyrDragon.h:115`). Knight damage 28 / 62 per light hit (1H / 2H), heavy 43.4 / 96.1 (see `docs/handoffs/HANDOFF-codex-v030-chain-20261028.md`). 2800 HP is about 100 one-hand light hits.
- Tune health (and/or damage, stagger/exposed multipliers) so a competent player wins in at most 150 s; measure with the `victory` replay and an owner playtest. Update the gates that assume the old fight length.

## 5. Knight drinking-cup (heal) animation is bad
- Owner: "For the player, the drinking cup animation is really bad."
- Heal clip + `ApprovedHealCup` prop in `VeyrKnight.cpp`. Source-first: find a drink/potion motion (Mixamo "drinking", Fab), retarget, fit the cup to the hand, keep heal timing and stamina rules.

## 6. Music and sound effects for the whole game
- Owner: "We have fish audio and the Higgsfield MCP, and we need to add background music and sound effects to the entire thing."
- Now: `VeyrAudio.cpp` plays raw PCM from `Unreal/Veyr/Content/Audio/Overhaul/` (Music, Ambience, Blink, Break, Breath, Contact, Fire, Footstep, ...) through procedural sound waves. Treat it as placeholder.
- Generate a boss theme (intro / loop / final phase / victory) and per-action SFX (sword swings light/heavy, hits on scales, blink whoosh, roll, footsteps on stone, armour clank, heal gulp, dragon roar/bite/stomp/wingbeats/fire/landing, UI). Owner tools: Fish Audio and the Higgsfield MCP (audio generation). Spend: one generation at a time, review, then the next (`feedback_generate_one_at_a_time`); log every spend. Mix so combat feedback is never masked by music.

## 7. Camera shake and fight feel (missing)
- Owner: from the video2rig/Unreal reference repo "When the dragon was hit, landed really hard, or during the boss fight, it shook the camera. Do we also have that or not? I don't think we have that."
- Checked 2026-10-31: **we do not have it.** No camera shake, hit-stop or flinch anywhere in `Unreal/Veyr/Source/Veyr/` (grep for CameraShake/Shake: no matches).
- Reference: shared-brain `boss-fight-blueprint` (fight-feel system: hit-stop, shake by weight, flinch, hit flash, weapon trail, dust tiers) and its `references/hero-runtime.md` (`UWardenCombatFx`, blow weights, hit-stop times, shake amplitudes). Resolve with `~/.config/devin/brain/bin/brain resolve boss-fight-blueprint`.
- Add: shake on dragon landings, stomps, tail hits, roar, heavy knight hits and knight damage, scaled by weight and distance; short hit-stop on connects; keep it subtle and add a settings toggle.

## 8. Knight attacks are boring: source better ones
- Owner: "the attack animations for the knight are pretty boring. Let's go on like Fab ... and look for some two-handed heavy attacks, jumping attacks, and better attacks as well."
- State: v030t took five round-A1 winners (`docs/knight-complete-20261028/attacks-20261031/ab-a1.md`); blind critic says none ship. The two-hand attacks are arm-only because every local Mixamo source is one-handed.
- Do: search Fab (free listings only), Mixamo (Great Sword pack; the owner asked on 2026-10-31 to go and source these, downloads use his own Mixamo/Fab login in Chrome), and the wider free sources in the `animation-sourcing` playbook for two-handed greatsword heavies, jumping/leaping attacks, running attacks and stronger light chains. Stage candidates on a bare localhost page for the owner to pick (source-then-pick), then retarget, fit the blade, set damage windows, blind A/B, import as the next KnightB version.
- Also still open from A1: recoveries that retrace the strike or hold still; LightAttack wind-up as fast as the strike; LightCombo blade dips below the floor; two-hand thrust freeze; one-hand light-light-heavy chain now 3.95 s (was 3.28 s).

## Also open from earlier passes
- Owner approval of the shadow-dash blink and v030t attacks (he has played it).
- Engine crossfade foot skating (`docs/knight-complete-20261028/blendproof-footgate-diagnosis.md` section 5).
- Dragon: rise-from-lying v1 near wing needs hand-keying (frames ~60-90); roar/collapse/air_land v6 retries (see `~/dragon-boss-fight` HANDOFF).
