# Issue #296 — hinge + latch round (A) and centre-slope removal (B): plan

PO decisions 2026-11-22, one round, branch `issue-296-stageb` from tip
`22012ff1b` (south unification). Previous worker died at the output cap
before committing; this plan starts fresh from the clean branch.

## (A) Hinge + latch — spec of record

Idea 2 in `~/workspace/goals/he-piantor-42-keyboard-pmo/files/
case296-swap-ideas-opus-2026-11-22.md` (read 2026-11-22). Premise
change, recorded: the shelf no longer comes off for a battery swap; it
stays attached and OPENS. This supersedes the removal half of the
2026-11-21 lid-integral decision; the lid stays integral with the
north band (one part) either way. Target: swap 20 actions → ~12,
tool-less.

### Placement decision — hinge axis on the shelf's SOUTH edge

The dispatch brief's headline says "hinge along the shelf's north
edge", but the spec of record argues, with geometry, that the axis
must sit on the shelf's **south edge**, and this round follows the
spec of record (deviation recorded here and in the final report):

- A north-edge axis lands 1–2 mm inside the flush north face and
  collides head-on with the flush-face invariant; letting the north
  skirt's lower end swing clear would require the axis at the skirt's
  north-bottom corner — on the outer face — destroying the flush
  design.
- With a south-edge axis the north skirt escapes outward exactly as
  in idea 1's geometry, and the closed shelf stays byte-identical in
  outline.

Consequences accepted with the spec: the opened shelf stands as a
~64 mm wall on the SOUTH side of the bay (between user and bay); its
top reaches Z ≈ 86; a stopper is mandatory so it cannot fall past
~95° onto the keytops; the middle cell (free end south) extracts
beside the standing shelf's root — extraction clearance is a measured
gate below, not an assumption.

### Design elements (per spec of record)

- Hinge knuckles ×2 on the shelf south edge, candidates X ±40
  (just outside the bay, inside the Wings) or X ±100 — pick by
  measured clearance to plate opening and Wing outline.
- Pin Ø2, **non-magnetic** (SUS316 or brass) — ferromagnetic pin /
  latch spring near the Wing Hall sensors is prohibited.
- Full-circumference knuckles + pin (no C-snap living knuckles:
  creep under constant opening stress).
- Hinge holes slotted in Y (+0.3): closed-state positioning is by
  the north sandwich (skirt/wall), not by the hinge, so the ±0.20
  print tolerance does not force the sandwich.
- Tray side: hinge bosses ×2 + latch receiver ×1. Existing 4
  heat-set inserts become unused (disposition recorded at build).
- Latch: ONE slide latch at X +85 on the shelf top, flush with the
  top face, captive slider (cannot fall out), single-motion finger
  release. The 4 countersunk screw holes (X ±55/±85, Y −60.37) are
  abolished. Pry notches: disposition at build (expected: retired —
  the latch + hinge replaces the pry action; record either way).
- Stopper: shelf opening limited to ≤ ~95–100° by a positive stop
  (tray-side or shelf-side), so the shelf cannot fall onto the caps.
- Durability: weekly opening ≈ 50/year (spec says ~100 cycles/yr is
  negligible wear for Ø2 metal pin + PETG full knuckles). Record
  knuckle wall thicknesses, pin retention (end caps / peened /
  captive groove), latch engagement depth with numbers.

### Measured gates for (A)

1. Hinge candidate sites: distance from plate opening edges and
   Wing outlines at X ±40 and X ±100 (boss footprint must not force
   a plate change without recording it).
2. Open state: all 3 cells extract on their established motions
   (slide 2.0 toward spring end, tip 35°, lift) vs the OPEN shelf —
   report real clearances, esp. the middle cell vs the standing
   shelf's inner face.
3. Arc sweep: shelf rotation sampled over the full arc vs keycaps
   (unpressed AND pressed), trackpad island, Fly + plugged USB-C
   plug envelope at the north face, desk plane, case itself —
   0.000 everywhere or stop and report the collision with numbers.
4. Closed state: shelf geometry identical to current (flush north
   deviation 0.000, band 22.00, cap gap 1.30 nominal, mating gaps
   as built); full interference suite re-run — 0.000 except the
   accepted artifacts (J_WING envelope 42.380/side, Ø44 probe disc).

## (B) Centre slope removed — PO verbatim

「中央の傾斜は無しで。無駄に複雑になるだけだ」

The shell-central slope sheet (22.00 → 10.90 over Y −0.37..20,
28.6°) is deleted; the centre field steps straight down (cliff)
from the shelf's south edge to the 10.90 plate-height field. This
supersedes the slope element of the 2026-11-21 profile (the PO's
original text allowed a cliff; this makes the cliff the design).
Consequences to handle and record:

- DLED light pipe at (−4, +13) now meets a flat 10.90 top —
  re-trim its length; verify pipe vs shell = 0.000.
- The shelf's south edge at centre now meets the vertical step
  (the slope's top edge was the meeting line; the step face takes
  its place).
- SW1 boss/plunger at (−15.5, +64.50) is south of the slope zone —
  re-verify anyway (plunger vs shell 0.000).
- Trackpad seat (Ø44.6 recess, floor 11.10) unchanged.

## Invariants (both parts)

Outline 310.04 × 146.07; Z ≤ 22.00; north face flush deviation
0.000; south unification as built at `22012ff1b`; antenna band
11.8 deep, cavity empty; Wing/plate positions; battery removal
sweeps and power-board fixing unchanged in the closed state.

## Stages

1. This plan (commit).
2. Measure: hinge sites, latch site, slope-zone geometry, current
   shelf/tray interfaces (script + numbers file).
3. Build (B) slope removal + light-pipe re-trim (smaller, lands
   first; checkpoint commit).
4. Build (A) hinge + latch + stopper; screws/inserts abolished
   (checkpoint commit).
5. Verify: closed suite + arc sweep + open-state extraction
   (script, numbers in the addendum).
6. Records: case-3d.md addendum (premise change, design numbers,
   open angle, sweep results, new swap step list + action count,
   slope disposition, durability), renders (closed top + new
   open-state view), Issue #296 comment, GOAL.md line, push.
