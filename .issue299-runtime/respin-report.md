# Issue #299 — GND respin round report (PO decisions 2026-11-21)

Branch `issue-299-wwing-gndfix`, on top of the GND-repair round
(boards `2f3371690`, report `834ddbf4e`). Base of record for the
original defect: `3fcad246f`. PO decisions executed: sensor pockets
= local pocket respin on the 16L pattern (option d); cap islands =
stitch vias + HALL_3V3 carve (option b); plus the PO-approved Wing
south-inner-corner trim from Issue #296 (δ=9.5 battery-bay ruling).

**Result: all four variants are at 79/79 pad-level GND on the saved
files, HALL_3V3 integrity 50/50 everywhere, corners trimmed, and the
full gate suite re-run. The set is ready for the Codex re-review.**

Final board SHA-256 (tree files on this branch):
- 16L `5a7003167b50b147ed0ecb7b6972c53f840556ffd3efd520e64d4cd6fffd711c`
- 16R `a2131e1aeb419367241915e0d33ec8e5a430e15f99279f7e28bd58536585a855`
- 17L `a6aa72a1df2848aa6ecd7e14645887bf59784d07af18a04ed75234b652907a03`
- 17R `f43b22869365a048d9f0433fab4b2401c43836a7d08bfb9206d312afaacdc840`

Checkpoint commits: 17R `a8c7ec796`, 16L `db88c6bf1`, 17L
`99acd1a39` + jog fix `1f654afee`, 16R `c6670066d`.

## 1. What was done per island

Method (the 16L pattern, generalised): a Ø0.60/0.30 GND stitch via
pair (via A on the pocket fragment, via B on the return pour) joined
by a 0.30 mm F.Cu track, with the HALL_3V3 zone fill treated as
carveable — after stitching, the HALL_3V3 zone is refilled and carves
clearance rings around the new GND copper, exactly as the as-designed
16L pocket via does. Sensors never moved; the TMAG land pattern is
untouched (Gate 1 field deviation 0.0000, Gate 2 errors []).

| Variant | Island | Fix | HALL carve |
|---|---|---|---|
| 17R | C_HC2 (cap) | stitch A(117.473,81.950) B(116.473,83.000), 0.30 track — the pre-staged design, verified then executed | −1.6626 mm² |
| 17R | U_HA2 (sensor) | stitch A(151.451,90.720) B(150.001,89.870), 0.30 straight track | −1.8867 mm² |
| 16R | U_HA2 (sensor) | stitch A(149.086,90.997) B(149.836,90.447), 0.30 track | −1.4369 mm² |
| 17L | U_HB5 (sensor) | stitch A(116.203,95.899) B(116.853,95.199), 0.30 track | (combined −5.6742) |
| 17L | C_HB5 (cap) | stitch A(116.212,98.560) B(117.362,98.510), 0.30 track | (combined) |
| 17L | U_HC5 (sensor) | RAW jog + stitch A(133.206,97.947) B(134.356,97.947), 0.30 track | (combined) |

Tooling note: the GND-only round's `stitch.py` searched only the 14
nearest via-B candidates; on 17R HA2 all 14 are F.Cu-unreachable
while a farther site routes at 0.30 mm (A* path length 1.25 mm).
`respin_stitch2.py` runs one A* per width with the full via-B
candidate union as the goal geometry; that placed every stitch
except HC5.

### 17L U_HC5 — the one true pocket respin

No via-A site exists for HC5 at the board's via size (exhaustive
tally ok=0 of 450). The pocket is pinched between the U_HC5.3
WING_EN pad and the F.Cu H_C5_RAW track: EN-pad corner to RAW
centreline is 0.617 mm in total, against 0.40 (pad floor) + 0.45
(track clearance incl. half-width) needed; the max-min bisector
bound is ≈0.28 mm, so smaller vias (0.40/0.35) fail too. The pocket
was respun properly: the F.Cu H_C5_RAW segment
(133.250,99.175)→(132.000,96.300) was jogged away from the pocket
(final route v3: →(132.900,98.420)→(132.100,97.900)→(131.900,97.400)
→(132.000,96.300), same net, same endpoint vias, w=0.10), opening 41
valid via-A sites; the stitch then placed as tabled above. The RAW
net grows ≈3 mm of slow analog routing; no other net was touched.

Jog v1 (north route) and v2 (east-first) both failed DRC — v1 passed
0.05 mm from the HALL_3V3 chain end (133.23,99.85), v2 crossed the
HALL vertical track body (133.856, 98.72..99.47). Both were caught
by kicad-cli DRC (shorting_items / tracks_crossing) before the files
were committed as final; v3 is verified clean by DRC and pairscan.
This is recorded as a producer-side miss: the hand clearance checks
for v1/v2 each overlooked one obstacle class.

## 2. Corner trim (Issue #296, PO-approved)

Notch = the Z-check §6 clip bbox (asm pre-shift X 6.36..12.75,
Y −6.68..−3.09) expanded by 0.25 mm, cut into the single Edge.Cuts
segment crossing it; removed 14.515 mm² per variant. Per-variant
asm transforms were fitted and validated before cutting (17L:
exact mirror of 17R, Hausdorff 0.0000; 16L: exact mirror of 16R,
0.0000; 16R: J_WING anchored at 17R's asm J_WING position, west
tip X=1.00 matches). Emptiness verified per variant on the actual
removed polygon: no pads/tracks/vias in any of the four. The zone
fills DO blanket the corner (12.17 mm² each on 17R) — "empty" in
the Z-check meant no discrete copper — so both zones were refilled
after the cut and recede from the new edge by their 0.15 clearance
(fill delta −15.4249 mm² each, all four variants; containment
0.0000 mm² outside the new outline on both layers).

Rim-roll re-verification (zcheck8 envelope replicated exactly:
slide 2.0, tip 35°, rim pivot): trimmed outlines intersect the
sweep at **0.000 mm³ on all four variants**. Control with the same
machinery on the untrimmed outlines gives 4.487 mm³ (nonzero, so
the check is live; the Z-check's 10.4 figure came from the
case-study brep solid, not the as-fabricated KiCad outline — the
trim clears both, since it removes the entire clip-bbox region,
a superset of either intersection).

## 3. Verification (all on the saved tree files)

- **Pad-level GND checker**: 79/79 ×4. Negative control on the
  `3fcad246f` bases still reproduces the review's island lists
  exactly (16L 76, 16R 77, 17L 74, 17R 75 with the same pads).
- **HALL_3V3 pad-level integrity** (netcheck.py, root = J_WING pin
  1): 50/50 ×4, before and after every carve.
- **Gates** (original Stage-2 scripts): G1 field deviation 0.0000
  (21 sites ×4); G2 errors [] ×4; G4 via-pad minima
  0.100 / 0.1016 / 0.100 / 0.1052 — exactly the recorded floors;
  G6 pin census diffs {} ×4; G7 parity 224 = 224 ×4, no mismatches.
- **Gate 5 (rail) re-run on the carved finals**: far-VCC typ
  3.2765 / 3.2768 / 3.2763 / 3.2763 V and max-case 3.2549 / 3.2555 /
  3.2545 / 3.2545 V (16L/16R/17L/17R) vs the Stage-2 study
  3.276 / 3.253 V — deltas ≤ +2.5 mV, budget class unchanged.
- **Gate 8**: outline 334 built vs 329 donor edges; the only-built
  set is exactly the 6 trim segments and the only-donor set exactly
  the 1 replaced segment, per variant; holes 46/46 equal ×4.
- **Census vs pre-respin (`2f3371690`)**: every difference is
  itemised — GND additions are exactly the stitches (vias/tracks
  listed with coordinates in the census output); the only non-GND
  track change anywhere is the 17L RAW jog (−1 segment, +4
  segments); footprints/pads identical. Fill changes (filldiff.py
  symmetric difference) are confined to the trim corner (15.425 mm²)
  and the stitch carve rings (1.44–1.89 mm² each); the remaining
  symdiff parts are area-0.000 refill tessellation hairlines.
- **Pairscan (B.Cu, sub-0.100)**: pair lists for 16R and 17L are
  identical base→final (worst 0.082892 and 0.091075, 17L's extra
  pairs 0.098958 / 0.099503 unchanged — not nudged, per the brief's
  disposition rule); counts unchanged on 16L/17R. No caveat
  worsened, no new sub-0.100 pair.
- **DRC (kicad-cli, --severity-all, full project copies)**:
  shorting_items 0 ×4; **unconnected_items 0 ×4** (KiCad's own
  refilled connectivity now agrees the islands are gone);
  tracks_crossing 0 ×4. Class counts otherwise match the repair
  round's finals, except 17L clearance 7→8: the extra item is a
  pre-existing 0.098958 pair (C_HA2.1 pad vs GND track), measured
  geometrically identical in base and final and present in both
  pairscan lists — DRC's refill grouping surfaces it only in the
  final run. ERC 0 errors ×4 (schematics untouched).
- **Project-file guard** (AGENTS.md lesson from the power-board
  Stage 2): after every scripted save cycle, the respin copies'
  `.kicad_pro` files were diffed against the tree — only the
  `.kicad_pcb` ever differed; no `.kicad_pro` was rewritten.

### Refill lessons (tooling, for the record)

1. Zone refills only reproduce inside the full project directory
   (`.kicad_pro` present); a bare `.kicad_pcb` refill silently
   changes fill areas (up to −251 mm² observed). All respin work
   was done in full copies under `scratch/respin/<V>/`.
2. `ZONE_FILLER.Fill()` with several zones — as a list or in a
   per-zone loop within one process — silently skipped the GND
   zone after a trim (HALL receded, GND did not; containment check
   caught 12.17 mm² of GND fill outside the new outline). Proven
   route: one zone per process (`refill_one.py`).

## 4. What remains

- Codex re-review of this fixed set (measure-first protocol), then
  PR topology for PR #300, then Stage 3 (manufacturing package +
  quote) — TMAG stock permitting. Wing adoption remains gated on
  D-049's two conditions (evaluation-board measurement + X2SON
  yield via the wireless Matrix), unchanged by this round.
- 17L's two extra sub-0.100 pairs stay dispositioned as recorded;
  16R's reversed duplicate WING_EN segment pair was left as
  instructed (same-net duplicate copper, pre-existing).
