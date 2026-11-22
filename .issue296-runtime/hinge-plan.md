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

## Stage-2 measurements (probe_hinge.py / probe_hinge2.py, 2026-11-22)

- Shelf south edge: only the lid (|X| ≤ 30.25) reaches Y −0.57.
  Plateau edges: X ±40 → −10.219; ±60 → −29.849; ±100 → −33.313.
  → A straight hinge axis can only sit on the lid edge line; the
  spec's ±40/±100 knuckle candidates cannot reach it (arms would
  sweep the caps/plate). Knuckles go on the lid edge (deviation
  from the spec's candidate sites, forced by these numbers).
- No cap solids at |X| < 32 → the open shelf's sweep zone over the
  centre field is cap-free.
- Latch zone: plate-right north edge Y −57.2 (X76) .. −58.75 (X89);
  tray top = 10.90 across X 75..89, Y −63..−59 (except the existing
  insert hole). Latch line set at Y −61.00 so the collar (Ø4.4,
  south extent −58.8) clears the plate edge (≥0.45 at X 85.8).

## Design of record for this round (numbers)

- **Axis** A = (Y −0.57, Z 19.30) — the lid's south edge line;
  knuckle/boss wrap radius 2.70 (top exactly 22.00). Pin Ø2.0,
  non-magnetic (SUS316/brass); holes Ø2.1 (boss round; shelf
  knuckle slotted +0.3 in Y per spec).
- **Per side** (mirrored): tray boss segments X 14..18 and 25..28 —
  post (Y −2.37..−0.37, Z 4.0..19.3, on the bay south wall) + wrap
  cylinder + pin hole (outer boss blind, floor X 27.8). Shelf
  knuckle X 18.3..24.7 (0.3 side play). Shelf notches at the boss
  spans (X ±0.3): lid-edge notch Y −3.5..+2.4, Z 15.0..22.3; skirt
  notch Y −2.67..−0.17, Z 10.9..15.6.
- **Pin** per side: shaft X 13.4..27.6, head flange Ø3.4 at
  X 12.6..13.4; inserted from the centre (bay side) outward after
  plate assembly; captive between head and blind hole.
- **Stopper**: radial lug on the inner boss wrap, centre at
  rel (dy +1.55, dz −2.94) (world angle −60°), tip r ≈ 3.4; it is
  contacted by the shelf notch's south wall at θ ≈ 95°. Contact
  angle tuned numerically in verification (target 95 ± 1°).
- **Latch** (right side only, per spec): line Y −61.00. Slider
  (new part) X 72..92, Y −61.3..−55.7, Z 19.8..22.0 in a groove
  cut into the plateau top (groove X 67.7..96.3, Y −61.8..−55.2);
  stem X 81..83, Y −62..−60, Z 10.0..19.8 through a web slot
  (X 76.2..87.8, Y −62.2..−59.8); collar Ø4.4 at (82, −61),
  Z 9.30..10.00. Receiver (tray): pocket X 75..89, Y −63.3..−58.7,
  Z 9.25..10.00; entries Ø5.0 elongated +0.3 north at (78.2, −61)
  and (85.8, −61), Z 10.00..10.95; neck X 80.2..83.8,
  Y −62.15..−59.85, Z 10.00..10.95. Locked = slider centred
  (stem in the neck, collar trapped under the tray top); release
  = slide ±3.8 to either entry. Centring: PETG flexure fingers at
  both slider ends (arm 10 × 1.1 × 1.8, end-wall ramps 20°,
  max deflection 1.38, strain ≈ 2.3%, unloaded at centre).
- **Abolished**: the 4 plateau screw holes + countersinks, the 4
  tray insert holes, the pry notches. The −85 tray boss stays as
  plain geometry; the +85 boss hosts the receiver.
- **(B)**: profile cut flat at 10.90 for Y ≥ −0.37 (trackpad disc
  exempt); slope sheet replaced by a flat sheet (Z 8.90..10.90,
  same footprint machinery) restoring any deleted skin; DLED pipe
  top 14.71 → 10.90.

## As-built revision (2026-11-22, after probe_hinge3 + follow-up probes)

The per-side boss placement above (X 14..18 / 25..28 on the bay
south wall) proved impossible: the Wing boards' south edges
cross the wall band (Y −2.37..−0.37, Z 4.70..5.90) at every
|X| ≥ 11.14 — measured intersections of the planned posts with
the Wing bodies: 9.47 mm³ (X 14..18) and 7.20 mm³ (X 25..28),
both sides; a trimmed post would be severed by the board. The
shell-central does not reach the hinge line either at those X
(its north edge recedes to Y 22.71 at X16, 29.64 at X20). The
design was therefore re-placed, same axis A and radius:

- **Hinge groups central**, on the wall span |X| ≤ 10.90 (top
  15.15, board-free): per side boss X ±(0.5..4.0), shelf knuckle
  ±(4.3..8.6), boss ±(8.9..10.9) — posts Y −2.37..−0.37,
  Z 4.0..19.3 on the wall (infill carries both boss1s + boss2
  right; tray-left carries boss2 left). Shelf notches at the boss
  spans widened ±0.3: ±(0.2..4.3) and ±(8.6..11.2), same notch
  boxes as above.
- **Two pins**, one per side, each inserted from the bay centre
  outward (as the spec requires): Ø2.0, shaft from the boss1
  inner face (|X| 0.5) to tip |X| 10.80 in the boss2 blind hole
  (floor 10.85), head flange Ø3.4 × 0.4 at the centre
  (X 0.1..0.5 / −0.5..−0.1 — the 1.0 centre gap takes both
  flanges side by side); captive between head and blind floor.
  (A single centre-spanning pin measured 0.628 mm³ into the
  lid's south edge at the centre gap — the axis lies on the
  edge line — hence two pins. Boss1 notches start at X 0.0 so
  the heads sit inside them.)
- **Stopper**: the wrap-lug idea died with the boss placement
  (at the boss spans the shelf is notched away — nothing sweeps
  toward a lug). Built instead: a post on the shell-central,
  X −0.45..+0.45, Y +1.88..+3.38, top Z 19.10 — the standing
  shelf's lid top edge lands on it. (A first site at
  X −2.6..−0.8 measured 0.255 mm³ into the west boss1 wrap —
  the post moved to the 1.0 gap between the wraps.) It stands
  on the shell (top 10.90); the Main board is below the shell
  there. Contact angle sweep-verified (target ~95°).
- **Centring**: one PETG finger under the slider (arm ~7 long ×
  0.6 thick, tooth dropping into a dip in the groove floor) —
  unloaded in the dip at centre (locked), max deflection 0.75,
  strain ≈ 1.3%, return force ≈ 0.5 N vs the 0.29k mm³ slider.
  (Replaces the two end-fingers + ramps of the earlier sketch:
  same function, one feature, no groove-end geometry.)
- **Verification fixes (first verify run)**: slider collar top
  10.30 → 10.00 with the stem extended down to Z 9.60 (the
  collar's top sliver measured 1.601 mm³ into the tray beside
  the neck); the (B) flat sheet overlapped tray-left's top by
  3.993 mm³ at the shell's north-west (the south-tip pair
  measured 0.000) — the shell is now trimmed by the final
  trays/infill at the end of the build. The closed cell sweeps
  reproduced the recorded baseline exactly (175.8 / 176.8 /
  175.8 mm³ = each cell's own spring-fin working space).

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
