# Issue #299 Stage 2 — Wireless Wing: schematic + layout report

Four variants (16L, 16R, 17L, 17R), each a native KiCad schematic + board
derived from its Wing Rev.6 donor: 21× TMAG5253BA3 channels (the #288 block
verbatim: VCC ∥ 100 nF, OUT direct to the MUX S pin, EP→GND), 3× TMUX1208PWR
with the Rev.6 address map, all TMAG EN pins on the existing WING_EN net,
rail net renamed HALL_3V3 from FH12 pin 1. The TMAG land is the single shared
footprint `wwing.pretty/TMAG5253BA3_X2SON-4.kicad_mod` (byte-identical to the
#288 land, md5 642faa960c1220ade09ac96f3c2434d9), so a D-049 yield-driven
land change touches one file for all variants.

Gate scripts: `.issue299-runtime/s2_gates.py` (gates 1/2/4/6/8),
`s2_gate5.py` (rail graph), `s2_gate7.py` (netlist parity). Per-variant raw
outputs in `.issue299-runtime/gates-<VAR>.jsonl`.

## Gate summary

| Gate | 16L | 16R | 17L | 17R |
|---|---|---|---|---|
| 1. Sensor field deviation vs Rev.6 | 0.0000 mm | — (layout blocked, see §16R) | | |
| 2. Placed-pad assignment errors | 0 | — | | |
| 3. ERC errors / DRC (see per-variant notes) | 0 / dispositioned | **BLOCKED — gate 3 cannot pass** | | |
| 4. Via–pad different-net min (floor 0.10 / target 0.125) | 0.100 mm | — | | |
| 5. Far-sensor VCC typ / max (study 3.276 / 3.253 V) | 3.2765 / 3.2549 V | — | | |
| 6. Flip-install pad-net diffs | 0 | — | | |
| 7. Schematic↔board parity (nodes) | 224 = 224, 0 diffs | — | | |
| 8. Outline / mounting deltas vs Rev.6 | 0 (329 = 329 items, 46 holes) | — | | |

## 16L

- **Gate 1:** worst deviation 0.0000 mm over 21 sites; rotations identical
  (18× 0°, U_HA6 +5°, U_HB6 −10°, U_HC6 −25°).
- **Gate 2:** 0 errors over 21 sites × 5 pads (net map + placed pad offsets
  through the flip/rotation transform vs the footprint definition).
  Negative control: in a scratch copy, moving U_HB2 pad 3 by +0.5 mm makes
  the gate report exactly that pad (expected offset (0.25, −0.70), got
  (0.75, −0.70)); a whole-footprint 180° rotation is caught by gate 1's
  rotation comparison. The real board reports 0.
- **Gate 3:** ERC 0 errors. 43 warnings, all `footprint_link_issues` = exactly
  the 43 donor-embedded components (24 C + 3 MUX + 1 FH12 + 15 TP) whose
  FPIDs carry empty library nicknames — inherited Rev.6 state; the 21 TMAGs
  resolve through the `wwing` library. DRC final state:
  `copper_sliver ×2, silk_over_copper ×22`, unconnected ×1 — all dispositioned
  below; zero clearance / shorting / hole / edge / dangling items.
  - *silk_over_copper ×22:* 21 are the TMAG pin-1 marker of the adopted #288
    footprint itself (present identically on the qualified Matrix board);
    1 is donor-inherited (the Rev.6 donor's own baseline has exactly 1).
  - *copper_sliver ×2 (1 F.Cu, 1 B.Cu):* kicad-cli 9.0.9 exports no item
    geometry for this class; a filled-outline area scan finds no outline
    < 0.20 mm² — these are thin necks inside fractured pour outlines.
    Warning class, pour-fill origin; the affected nets are proven connected
    by the unconnected list.
  - *unconnected ×1 — GND pour fragment at (140.71, 41.21), NE of U_MUX_C:*
    a component-free B.Cu pour fragment sealed off by added tracks. Proven
    pad-free: the only unconnected pair is zone↔zone at the same anchor and
    no GND pad appears in any unconnected pair — every GND pad connects via
    the main pour. Two stitch attempts were made and removed (they added
    worse violations than they cured). No functional impact; recorded here
    rather than dispositioned silently.
  - One stacked exact-duplicate GND F.Cu track pair at (121.80, 29.73)
    remains — electrically identical copper, invisible to DRC, not a defect.
- **Gate 4:** min via–pad different-net distance 0.100 mm — exactly at the
  0.10 floor, below the 0.125 target. Tightest item: H_C4_RAW via at
  (83.486, 96.406) vs U_HC4 pad 5 (EP, GND). Measured with KiCad's own
  effective pad shapes. Same class as the qualified boards (wireless Matrix
  0.1002 mm, wireless Main 0.100 mm).
- **Gate 5:** placed-copper resistive graph (154 clusters, 256 edges; track
  R = 0.491 mΩ/sq × L/w, vias 1 mΩ, F.Cu pour as ideal union). Wing-side
  drop to the far sensor (U_HB5): 0.604 mV typ / 1.159 mV max — better than
  the Stage-1 lumped allowance (1.37 / 2.63 mV). With the study's upstream
  chain (0.417 Ω): far VCC **3.2765 V typ (Δ +0.5 mV vs study)** /
  **3.2549 V max (Δ +1.9 mV)**.
- **Gate 6:** J_WING pad→net map (15 pins incl. MP) identical to the Rev.6
  donor — 0 diffs; the flipped-pose EN0/EN1 swap is absorbed on Main, as
  designed (D-024 link).
- **Gate 7:** netlist parity full: 224 = 224 nodes, 64 = 64 refs, 0 missing /
  extra / mismatched; the only schematic-side NC nodes are the 7 by-design
  ones (J_WING MP, MUX VSS + S8 ×3).
- **Gate 8:** Edge.Cuts item sets identical (329 = 329, 0 only-built /
  0 only-donor); 46 NPTH positions equal.

## 16R — BLOCKED (gate 3 cannot pass; stopped per the gate-failure rule)

The 16R board builds through the standard pipeline (donor swap, collision
repair, escape+A* routing, finisher) and converges everywhere **except the
U_HC1 site cage**, where three nets remain unconnectable and shorted. This
is a measured geometric seal, not a routing-effort gap: both A* routers
(corridor and the finisher's escape) fail on the cage, and ~35 hand-designed
polylines were placed and DRC-checked; every one violates a measured
constraint itemised below. Per the Stage-2 instructions the variant is
stopped here rather than dispositioned around.

Final DRC state (after reverting the last cage attempts; the two clean
out-of-cage bridges — HC5 HALL_3V3 and the HALL-C trunk hop — are in):
`clearance ×21, shorting_items ×5, tracks_crossing ×1, hole_to_hole ×3,
copper_edge_clearance ×2, items_not_allowed ×2, solder_mask_bridge ×2,
copper_sliver ×1, silk_over_copper ×22, track_dangling ×31,
via_dangling ×12`, **unconnected ×9** — of which 8 are the HC1 cage and its
EN feed (below) and 1 is a pad-free GND zone↔zone fragment at (157.1, 50.8),
the same dispositionable class as 16L's fragment.

### The HC1 cage (U_HC1 centre (68.89, 65.59), rot 0°)

Pads: 1 HALL (68.64, 66.29), 2 GND (68.64, 64.89), 3 EN (69.14, 64.89),
4 RAW (69.14, 66.29), 5 EP (68.89, 65.59) rect x[68.49, 69.29] y[65.29, 65.89].
C_HC1 at (68.89, 69.09). Three nets must braid through a ≈1.5 × 2.5 mm box:
HALL's east feed (junction (68.15, 67.68) → trunk west end (70.00, 64.10)),
RAW's north run (pad 4 → trunk via (69.60, 62.90)), EN's south run
(pad 3 → south tree via (69.80, 68.23)). Binding constraints, all measured
from placed data:

- **B east is walled by the HALL chain itself.** Route2's fan discs at
  (69.40, 66.73) / (69.52, 66.68) and the P-chain
  (69.52, 66.60) → (69.55, 66.23) → (69.56, 66.02) → (69.59, 65.62) →
  (70.10, 65.20) → (70.45, 65.15) → (70.45, 64.55) hug the EP; RAW's pad-4
  exit passes 0.171 mm from piece (69.59, 65.62)→(70.10, 65.20)'s *body*
  (endpoint-to-body, the binding measure) against the 0.20 mm floor.
- **B west/north is walled by the GND via at (69.00, 65.55)** (route2,
  B↔F): its centreline exclusion (0.30 via radius + 0.05 track half +
  0.10 clearance = 0.45) overlaps the HALL chain's exclusion at every
  latitude of the dip channel (at y 65.40 the two exclusions leave
  x [69.424, 69.386] — negative width).
- **F north is walled by the GND F chain** (69.11, 64.01) → (69.74, 64.38)
  → (69.86, 64.88) together with H_C3_RAW's F diagonal
  (70.30, 64.48) → (69.05, 63.23); the only F gap computes to ≤ 0.02 mm.
- **F east/south is walled by H_C3_RAW's F verticals at x 70.30**
  (y [64.48, 66.98] and y [67.23, 79.48]) and the GND via bubble at
  (69.86, 67.13) (track-centreline exclusion 0.45): at y 67.50 the free
  channel between the via bubble and the C3 band is x [70.116, 70.10] —
  negative width.
- **Every layer crossing needs a 0.60 mm via** (exclusion Ø 0.90 for
  centreline-to-centre); no point inside the cage satisfies all
  exclusions simultaneously — candidate via points were computed at
  (69.80, 65.70) (0.21 mm from the HALL chain body — shorts, confirmed by
  DRC), (70.60, 68.10) (reaches the C3 vertical — shorts, confirmed),
  (70.75, 65.55), (69.35, 64.70), (69.50, 64.20) (0.04 mm from the GND F
  chain), all failing by measurement.

Remaining unconnected pairs (all cage-caused): H_C1_RAW pad-side stub
(69.25, 66.10) ↔ trunk piece (69.86, 65.62); WING_EN F trunk (69.80, 68.23)
↔ B tree (70.80, 77.73); WING_EN HB6 pad 3 (69.90, 115.68) ↔ stub
(51.04, 122.26) (the HC6↔HB6 hop — corridor-reachable in isolation but its
path crosses the cage's EN feed); WING_EN HA1 pad 3 (101.14, 58.30) ↔ HA3
stub (101.14, 74.30) (A-column thicket — corridor A* fails; independent of
the cage but unbridged); leftover EN F stubs at (70.85, 66.15) / (70.95,
66.15) ↔ B stub (70.85, 64.85) (route2/finisher debris inside the cage);
H_C2_RAW (98.90, 58.50) ↔ (100.80, 57.80) (HA1-area GND mesh — corridor
A* fails on the clean board).

**What would unblock 16R:** a local re-route of the whole HC1
neighbourhood (delete route2's copper in x[66, 73] y[61, 71] for
HALL / H_C1_RAW / WING_EN and re-place as one coherent design, moving the
GND via at (69.00, 65.55) and the HALL fan geometry) — a design change to
route2's local topology, outside this stage's bridging scope; or accepting
a 4-layer / smaller-via stackup for this variant. The 16R tree in this PR
is the pipeline output with the cage left open, DRC as above; the
schematic was not generated and gates 1/2/4–8 were not run, because gate 3
cannot pass.

## 17L

(pending)

## 17R

(pending)

## Notes for Stage 3 (not part of this stage)

- Wing adoption and ordering wait for D-049's two conditions, discharged via
  the #288 Matrix board (Stage-1 gate note).
- The wireless FFC lane acceptance (≤ 0.30 Ω/lane) is a build-guide action.
- TMAG5253BA3 (LCSC C22401868) stock pacing for the full 20-board run is a
  Stage-3 re-check item (Stage-1 availability note).
