# Issue #278 IMPLEMENTATION plan — A2 route channel into the production case tree

PO decision: D-051 (docs/decisions.md on this branch) — A2 channel adopted;
implementation is PMO-GO work on branch issue-278-flip-usb.
Study being implemented: `.issue278-runtime/flip-usb.md` / `flip-usb.json`.

## How pocket A was implemented in #275 (the convention to mirror)

- The production tree `hardware/case/issue-263-lowdeck-production/` is a
  DELTA RECORD: tray geometry stays sourced from the #261 tree
  (`hardware/case/issue-261-lowdeck-full/`); deltas are adopted as
  quantified cuts in its README ("cut exactly those volumes when the
  trays are next generated"), each backed by a computation log copied
  into `audit-rerun/`.
- Pocket A precedent: script `case-pocket-275.py` (in the #275 runtime,
  mainsym worktree) measured the pocket box against the audit body set
  (fitlibF.bodies_at(pitch, -2.65)): removes exactly 380.00 mm3 of tray,
  touches no other body, remaining web recorded. Log:
  `audit-rerun/case-pocket-275.log`. README section: "Issue #275 round
  (2026-11-18)" with the quantified box (case X -6..+13, Y 28..48,
  floor Z0.60) and the production note.
- The #275 fitted audits (audit275.py, mainsym runtime) run on
  fitlibF.bodies_at(17, -2.65) with trays pre-cut by the formed FFC
  channel solids (audit_static.channel_solid); flipped mode adds
  pocket A. Production copies: `audit-rerun/audit275-{normal,flipped}.json`.
- The #278 study body set (bodies_cache/, 343 bodies) is that same
  fitted bundle at pitch 17 with Main flipped and pocket A applied.

## What the A2 channel is (study geometry, to be landed exactly)

- Cutter (final_audit.py construction, verbatim): segment boxes along
  Catmull-Rom (n_per=14) of the A1F centreline control points
  (local_lib.A1F), each Pos(mid.x, mid.y, 2.30) * Rot(yaw) *
  Box(len+1.2, 7.5, 2.20) → z band 1.20..3.40, width 7.5, fused.
  Gross cutter volume 2661.4 mm3.
- Cut from tray-right / tray-left: removed **931.3 / 0.0 mm3** (study).
  Floor Z1.20; joins pocket A on its east side; web below Z1.20
  untouched (thicker than pocket A's 0.60 mm web); no boss/screw
  feature broken; FFC formed-channel floor locally notched <=7.5 mm
  at 2-3 crossings (a consequence of the same cutter, to be counted).

## Implementation steps

1. `case-channel-a2.py` (flipped, via local_lib + bodies_cache):
   - Positive controls: synthetic pair = 13.5; A0 dress vs unmodified
     tray-right = 321.58 (study values; cache fidelity + Common path).
   - BASELINE (invariant 1): gate the A2 dress cable (LL.cable_solid(
     A1F), length must read 168.64) against the UNMODIFIED cached set
     → expect a tray-right hit; this is the contact the channel must
     remove, so the delta is attributable.
   - Cutter checks: cutter ∩ every non-tray body = 0 (boss/screw/
     splice-plate safety, direct); cutter ∩ pocket-A box > 0 and
     distance 0 (joining); cutter gross volume = 2661.4.
   - Apply cut; removed must read 931.3 (tray-right) / 0.0 (tray-left);
     removed-solid zmin >= 1.20 (floor; web below untouched).
   - FLIPPED GATE (invariant 3): cable vs modified set → unexpected
     hits = {} ; engagement = {Main-study-J4 35.417, Fly housing
     1.552, EZmate-Fly-plug 22.73} (study values); sheet extrema
     right 0.314 / left 5.29; service sweeps (plug boxes translated
     -2.0 z, study construction) → no hits outside OWN.
2. `case-channel-a2-normal.py` (normal pose, mirroring audit275.py
   'normal' verbatim method: BRepAlgoAPI_Common gate1 + shapely
   tray_disposition; body set = fitlibF.bodies_at(17,-2.65) from the
   raise worktree lib + this worktree's issue-261 audit_static;
   trays formed-channel-cut; wing + Main ZIF envelopes added):
   - BASELINE reproduction first: must match production
     `audit-rerun/audit275-normal.json` (right gate1 {}, left
     {Main-study-C23: 0.488} — the known build watch item; tray vols
     {tray-left: 290.409} both sides; plan outside corridor 0.0).
     Mismatch → stop and diagnose, do not improvise.
   - Apply the same A2 cutter to tray-right/tray-left; record removed;
     re-run: gate1 unchanged, plan outside corridor 0.0, tray vols
     may only shrink; report the delta.
   - Count FFC formed-channel crossings: disjoint pieces of
     cutter ∩ channel_solid(CTRL_R) / (CTRL_L) (expect 2-3 total).
3. Production record (mirroring pocket A):
   - Logs → `hardware/case/issue-263-lowdeck-production/audit-rerun/
     case-channel-a2-278.log` (+ normal log), gate JSONs →
     `audit278-a2impl-flipped.json`, `audit278-a2impl-normal.json`.
   - README: new section "Issue #278 round (2026-11-19) — A2 route
     channel adopted (D-051)" after the #275 section, pocket-A style:
     quantified cut, joining, web note, notch disclosure, both-pose
     audit results, D-051 build-time confirmation note.
4. `.issue278-runtime/a2-implementation.md` + `a2-implementation.json`:
   what was cut where, both poses' verdicts with control results,
   deviations from study geometry (must be none; any forced deviation
   = STOP and report as blocker).

## Environments / runtimes

- Python: ~/workspace/tools/cad-venv/bin/python (build123d), as the
  study scripts ran. Scripts run in background with logs (flipped
  gate took ~40 min wall in the study; fitlibF build ~10 min).
- bodies_cache/ (51 MB) stays on disk, never committed.
