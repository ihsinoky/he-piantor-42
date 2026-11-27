# Issue #299 — GND repair round report

Branch `issue-299-wwing-gndfix`, base `3fcad246f`, repair checkpoint
`2f3371690`. All measurements on the SAVED files, reloaded fresh.

## Verdict

| Variant | Base (checker) | Final (checker) | State |
|---|---|---|---|
| 16L | 76/79 | **79/79** | REPAIRED |
| 16R | 77/79 | 77/79 | U_HA2 island NOT repairable in envelope — dispositioned |
| 17L | 74/79 | 74/79 | HB5/HC5/C_HB5 islands NOT repairable in envelope — dispositioned |
| 17R | 75/79 | 76/79 | C_HB3 REPAIRED; U_HA2 + C_HC2 dispositioned |

Acceptance 1 (pad-level connectivity) is met for 16L only.
Acceptance 2 remainder is itemised below with pad-level proof.
Acceptance 3 (gates 1/2/4/6/7/8 unchanged) and the change envelope
(only GND copper changed; non-GND geometry identical) are met for
all four variants. **The unrepaired islands are a genuine
in-envelope impossibility, proven below — they need a PO decision
(option (b) or pocket respin, §5), not more worker rounds.**

## 1. Checker and negative control

`gndcheck.py` (this runtime dir) walks the saved copper — zone fills
as saved + tracks + vias + pads, both layers, vias joining layers —
and reports which GND pads sit in the J_WING return component.
Negative control on the base commit's boards reproduces the Codex
review's M6 table EXACTLY (same counts, same pad sets):

- 16L base 76/79, off: C_HB2.2, U_HB2.2, U_HB2.5
- 16R base 77/79, off: U_HA2.2, U_HA2.5
- 17L base 74/79, off: C_HB5.2, U_HB5.2, U_HB5.5, U_HC5.2, U_HC5.5
- 17R base 75/79, off: C_HB3.2, C_HC2.2, U_HA2.2, U_HA2.5

## 2. What was repaired

### 16L — zone refill, min-thickness only (79/79)

The HB2 island already contained a stitch (GND via (67.361,91.050) →
F.Cu track → via (68.486,92.425)) whose far via lands back on the
island's own fill lobe — a stitch that starts and ends on the same
fragment. No B.Cu bridge exists (pocket sealed, §4) and no F.Cu
track route exists (grid A* from the stitch stub to return F.Cu
copper / new via-B: no path at widths 0.30/0.20/0.10).

Repair: refill of the GND zone with **min_thickness 0.30 → 0.05,
clearance unchanged 0.15**. The fill now keeps a neck of ≈0.248 mm
(erosion-waist measurement at U_HB2.2) through a 0.545 mm corridor
that the 0.30 min-thickness rule previously pruned. GND fill area
8709.26 → 8752.03 mm² (+42.77, −0.0003 removed — the growth is the
same pruning released board-wide; all of it GND fill at the
unchanged 0.15 moat). The zone parameter change is part of the
delivered file, so any future refill reproduces this fill — it is
not a stale-fill landmine. DRC: unconnected 1 → 0, copper_sliver
2 → 2, silk_over_copper 22 → 22, shorting 0. Census: object counts
identical; non-GND geometry diff = 0; GND diff = the one B.Cu zone
fill polygon set.

### 17R — one B.Cu bridge track (C_HB3)

Added exactly one GND track, B.Cu, width 0.25:
(84.6687, 82.9995) → (84.6687, 83.7995). Census: non-GND diff = 0;
GND diff = this track only. DRC unconnected 3 → 2 (the remaining 2
items are the HA2 and C_HC2 islands, §5). Pair scan: no new
sub-0.100 pair (B.Cu worst stays 0.100, 0 pairs below).

### 16R, 17L — files unchanged

Byte-identical to base (census 0/0 in both buckets; git diff empty).

## 3. Invariant verification (all variants)

Diff census vs `3fcad246f` (`census.py`): object counts identical
everywhere (16L 1148 trk/231 via, 16R 1138/251, 17L 1227/226,
17R 1127→1128 trk/251; 110 footprints, 278 pads, 7 zones, 329
drawings each). Non-GND geometry multiset diff = **0** on all four.

Different-net pair scan (`pairscan.py`, exact geometry, threshold
0.105), B.Cu pairs below 0.100, base → final: 16L 0 → 0 (worst
0.100), 16R 9 → 9 (worst 0.082892 — the recorded 0.0829 caveat,
unchanged), 17L 9 → 9 (worst 0.091075, recorded class 0.0904–0.0994
unchanged), 17R 0 → 0 (worst 0.100). No caveat worsened.

Gates re-run on the final files (original Stage-2 scripts):
G1 field deviation 0.0000 mm (21 sites ×4); G2 assignment errors []
×4; G4 via-pad minima 0.100 / 0.1016 / 0.100 / 0.1052 — exactly the
recorded floors, not reduced; G6 pin census diffs {} ×4; G7 parity
224 = 224 ×4, no mismatches; G8 outline 329/329 edges, 46/46 holes
equal ×4.

DRC (kicad-cli, --severity-all, in-tree with project rules):
shorting 0 on all four, base and final. Final class counts —
16L: sliver 2, silk 22, unconnected 0. 16R: clearance 10, sliver 1,
silk 22, hole_to_hole 3, track_dangling 21, via_dangling 9,
unconnected 1 (the HA2 island). 17L: clearance 7, sliver 1, silk
22, hole_to_hole 3, track_dangling 30, via_dangling 16,
unconnected 3 (the three islands). 17R: sliver 1, silk 22,
hole_to_hole 8, via_dangling 10, track_dangling 14, unconnected 2.
Unchanged variants match their base counts class-for-class; the
changed variants differ only in the unconnected counts above.
ERC: 0 errors on all four schematics (43 warnings; schematics
untouched).

## 4. Why the remaining islands cannot be repaired in-envelope

Anatomy (measured per island; scripts `freetest.py`, `diag.py`,
`pocket.py`, `stitch.py`, `refill_test.py` in this runtime dir):

- Each island is a sensor or bypass-cap pocket: a small B.Cu fill
  fragment ringed by its own EN / RAW / HALL_3V3 tracks and pads.
  All ring slots are < 0.30 mm (best: 0.28 mm between the TMAG
  VCC/OUT pads), and a 0.10 mm track at the 0.100 floor needs a
  0.30 mm slot. Exact free-space connectivity (`freetest.py`,
  shapely, width 0.10, 12 mm margin) proves every island except
  17R C_HB3 is **sealed on B.Cu**.
- The F.Cu above every pocket is covered by the HALL_3V3 zone fill
  (distance 0.0). A Ø0.60/0.30 stitch via (the board's only via
  size) must keep 0.100 from that fill; sampled exhaustively
  (0.05 grid over island + margin, `diag.py`): via-A valid sites =
  **0** for 16R HA2 (477 raw), 17L HB5 (802), 17L HC5 (450),
  17L C_HB5 (1291), 17R HA2 (789), 17R C_HC2 (1406) — every site
  rejected on F.Cu-other-net. (16L HB2 is the exception that proves
  the rule: its pocket via was placed before the fill existed, so
  the fill has a cutout there.)
- Refill experiments: GND zone at clearance 0.10 / min-thickness
  0.05 (moats below the as-designed 0.15) still leaves 16R HA2,
  17L HB5/HC5/C_HB5, 17R HA2/C_HC2 disconnected (waist 0.000);
  the only sub-0.30 slots would admit ≤0.08 mm hair necks, which
  are below the 0.10 minimum feature and were rejected as
  checker-gaming, not repair.

## 5. Dispositions and the decision needed

Unrepaired, with pads (all are the checker lists in §1 minus the
repaired ones): **16R U_HA2.2/.5; 17L U_HB5.2/.5, U_HC5.2/.5,
C_HB5.2; 17R U_HA2.2/.5, C_HC2.2.** Fabricated as-is, those sensor
channels (HA2 on 16R/17R, HB5/HC5 on 17L) and bypass returns have
no ground return — dead channels. These boards must not be
ordered in this state.

Options, priced:

- **(b) Authorise a bounded HALL_3V3 change**: place stitch vias
  over the pockets, then refill ONLY the HALL_3V3 zone so it carves
  clearance rings around the new GND copper. Pre-staged on 17R in
  scratch (NOT in the tree): C_HC2 stitched (via A (117.473,
  81.950), via B (116.473, 83.000), F.Cu track 0.30 wide), HALL_3V3
  refilled → checker 77/79; HALL_3V3 F.Cu fill area 9192.402 →
  9190.740 mm² (−1.662 mm², rings only). So (b) is **proven for
  cap islands**. For the sensor pockets it is necessary but not
  sufficient: with the fill carved, 180 valid via-A sites exist
  over 17R HA2, but no F.Cu egress route was found by grid A*
  (nearest return F.Cu copper 35.4 mm away; via-B + track egress
  is a hand-routing task). Expect (b) + hand egress per sensor
  pocket, or combine with (d).
- **(d) Pocket respin**: re-place the pocket fanout with the GND
  via inside the pocket from the start (the 16L pattern) — a
  local Stage-2 redo for 5 pockets across 3 boards; largest
  rework, cleanest result.

## 6. Secondary items

- 17L's two extra sub-0.100 pairs — reproduced exactly by
  `pairscan.py`: 0.098958 (B.Cu, C_HA2.1 HALL_3V3 pad vs GND track
  (48.6,92.15)→(48.8,95.275)) and 0.099503 (B.Cu, GND track
  (80.746,81.889)→(80.496,82.139) vs HALL_3V3 track). **Dispositioned,
  not nudged**: the deficits are 0.0011 / 0.0005 mm, inside the
  recorded 0.0904–0.0994 caveat class (whose worst they do not
  change); both involve GND tracks, so a fix is a GND-only nudge —
  but 17L is otherwise byte-unchanged pending the §5 decision, and
  a respin/(b) round will rework this area anyway. Recorded here
  so the next round closes them.
- 16R's reversed duplicate WING_EN segment pair: out of envelope
  per the brief — left untouched, noted (same-net duplicate copper;
  it inflates the 16R clearance-pair count 10 object pairs → 9
  physical).

## 7. Deliverables in this round

- Boards: 16L + 17R repaired (checkpoint `2f3371690`); 16R + 17L
  unchanged. Branch `issue-299-wwing-gndfix` pushed.
- This report; REPORT.md addendum in the tree; Issue #299 comment;
  GOAL.md line.
- Tooling (this runtime dir): `gndcheck.py` (acceptance checker),
  `census.py`, `pairscan.py`, `survey2.py`, `freetest.py`,
  `route.py`, `stitch.py`, `diag.py`, `pocket.py`, `refill_test.py`,
  `neckfind.py`, `gndfix-plan.md`.
