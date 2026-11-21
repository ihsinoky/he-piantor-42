# Issue #296 — Wireless case design, Stage B: 2D approval package (D-062 + δ=9.5)

Status: FOR PO 2D APPROVAL. No 3D modelling started (project gate).
Figures: `case296b-2d-topview.png`, `case296b-2d-sections.png` (goal files/).
Frame: asm frame of the study lineage — X centred on the case (+east),
Y +south; case outer north Y=−64.37, outer south Y=+81.70; Z = case Z
(case bottom 0, keytop datum 22.00 provisional per Junana gate).
Scripts/artifacts: `.issue296-runtime/extract_main.py`,
`pilotb-coords.json`, `wing-conn.json`, `wing17r-outline-asm.json`,
`measures.json`, `figures.py`.

## Settled inputs consumed

- D-062 (centre 3-cell) + its 2026-11-21 amendment: δ=9.5/side by plate
  tip notch only; Wing boards unchanged; outline 310 × 146.1; FFC
  channel 11.5.
- Boards of record: wireless Main origin/main SHA `75db72bc…` (D-063);
  wireless Wing Stage-2 set, PR #300 tree @ `3fcad246f`; power board
  Stage 1 (Issue #303, PR #304 tree / design note).

## Item 1 — Outline and Wing poses

- Outline **310 × 146.1**: width = D-062 amendment (319 − 2×4.5);
  depth per item 9 below. South edge straightened (going-forward
  outline): Main south edge (asm Y +67.90, board file) → case edge
  **13.80** (south-notch study figure 13.802).
- Wing poses: baseline geometry17 fit (rotation ∓29.996°, verified this
  run: the 17R Edge.Cuts outline transformed by the recorded fit gives
  bbox X 1.0..142.244 / Y −61.601..77.380 — exactly the Stage 1 record)
  shifted outward by δ=9.5. Wing outer corner reaches |X| 151.74,
  inside the 155 half-width.
- **Plate tip notch** (from the wing-shape study, option A): plate
  inner straight edge at |X| 22.70 (= 13.2 + 9.5); the tip diagonal is
  truncated at the study's cut line |X| **22.47**; removed tip triangle
  ≈100 mm²/side (study estimate from the inner-edge profile); nearest
  switch-hole wall keeps its 2.75 mm land (study measurement — the
  notch zone contains no switch or screw holes). Board inner edge at
  |X| 22.50 (= 13.0 + 9.5) is the δ=9.5 clearance driver on the board
  side (study ladder: slab 9.2 < 9.5 ✓).

## Item 2 — Centre bay and power board Stage-2 input

- **Floor: case Z −0.65, levelled.** The block footprint contains the
  old Fly-pocket floor and the old cable-channel wall pair (both top
  4.70) and local bosses (top 2.85) — all removed by levelling; both
  mouldings belong to features this configuration deletes (centre
  study §1). Unlevelled stack = cover at exactly 22.00 (zero margin,
  the known trap); levelled stack below.
- **Stack (levelled):** floor −0.65 → power board 0.8 (top +0.15) →
  cell top **14.65** → cover top **16.65** → **5.35 mm margin** to the
  22.00 datum. No zero-margin item in the stack.
- **Block:** envelope 48.5 × 56.0, north-anchored: X ±24.25,
  Y −62.37..−6.37; cell centres X −15/0/+15, Y −34.37; contact faces
  ±26.00 from cell centres (power board Stage 1 datum).
- **Bay cavity:** 56.5 (X) × 60.0 (Y): inner faces X ±28.25,
  Y −62.37..+2.37; walls 2.0 → bay footprint 60.5 × 64.0 in the case.
- **Power board outline (Stage-2 input, this package's output):**
  **52.5 (X) × 58.0 (Y)**, datum = board north edge on the bay inner
  north face (Y −62.37), board X centred on 0 → board spans
  X ±26.25, Y −62.37..−4.37. Clearances: 2.0/side in X, 2.0 south,
  0 north (datum face; fixing method is a Stage-2/case detail).
  Board thickness 0.8 (D-059 construction (a) lineage, Stage 1 input 6).
- **Cover:** re-formed roof over the block, top 16.65 (0.5 gap +
  1.5 shell over cell top 14.65, centre study §5); spine insert pair
  moves to the block corners in the re-form (D-062 consequence 2).

## Item 3 — Fly (right) and USB

- Fly centre at **dx = +38** (the D-062 minimum; band +38..+44),
  Y −50.14 (17-pitch seat record). At δ=9.5 the Wing's north corner
  approaches 4.5 mm closer than in the δ=14 study assembly; the study's
  residual Wing sliver (22–51 mm³ at δ=14) grows slightly — same
  local-relief class (pocket moulding + corner relief), no hard
  blocker identified; **the exact sliver volume at δ=9.5 is not
  re-measured in this package (2D stage)** — flagged for the 3D stage.
- USB opening on the **north gable wall**: at |X|=38 the gable falls
  ≈1.8 mm south of the centre line (centre study §4) → Fly sits 1.8 mm
  north of the flat-wall datum OR the opening gets a short tunnel;
  either is a case detail, recorded here as the two options.
- Plate graze: USB shell top 9.60 vs plate underside 9.40 = 0.2 mm
  graze → local notch in the plate north rim (study), right side is
  the smaller graze.
- **EZmate route re-measured at δ=9.5:** polyline J4 plug (0, +19.2) →
  (35.75, −6.0) east of the block → Fly plug (38, −49.0): centreline
  **86.8 mm**, ≈**99.8 mm** with the study's 15% service allowance —
  inside the stock 170 mm cable with ~70 mm to spare (route crosses
  the FFC channel band north-east of Main; stacking with the FFC is a
  routing detail carried from the centre study).

## Item 4 — FFC channel 11.5 and the FFC/FPC follow-up

- Channel (perpendicular gap Main diagonal ↔ Wing inner edge) =
  **11.5 mm** at δ=9.5 (D-062 amendment; = 2.00 + 9.5).
- Connector-centre spans re-measured from the board files: Main J3
  asm (+24.255, +45.222) ↔ Wing 17R J_WING asm (+36.502, −38.906) =
  **85.01 mm**; left pair mirror = **85.01 mm**. (16 mm variants: the
  channel width applies by the same δ definition; their
  connector-centre distance was not extracted in this package —
  recorded as unverified, expected same class by the shared link
  design.)
- **Follow-up FFC-1 (named, precise):** the D-042 stock folded-FFC
  qualification (152 mm ribbon, 5-fold, ≤0.30 Ω/lane acceptance per
  build-guide F-1) was premised on the 2.00 mm hop and does **not**
  carry to an 85 mm centre-distance link in an 11.5 mm channel.
  Re-selection task: per-side straight FFC (100 mm class) or the
  D-042 custom-FPC fallback, Type per installed pose, with the lane
  acceptance (≤0.30 Ω/lane) and a channel bend check re-run. Owner:
  Issue #296 follow-up; blocks the Wing order configuration, not
  this 2D gate.

## Item 5 — JBATT route

- Power board J1 (GH, Stage 1 decision: GH–GH cable, same part/pinout
  as Main JBATT) at the board's south edge; route polyline
  (17, −4.37) → (30, +10) → (24, +60) → JBATT plug asm
  **(+24.0, +67.898)** (Pilot B, board file): centreline **77.6 mm**,
  ≈**89 mm** with 15% allowance → the Stage 1 ~100 mm cable class is
  confirmed with margin. (Centre study estimate was ~100 mm at δ=14;
  the δ=9.5 geometry shortens it slightly.)

## Item 6 — Trackpad island and antenna band

- Island Ø44 at shell (0, 48), surface Z12.70 (D-053): north rim
  Y +26.0 vs block south face −6.37 → **32.37 mm** clear (unchanged
  by δ, which is an E-W quantity). South rim Y +70.0 vs case south
  edge +81.70 ✓.
- Antenna south PETG band: Main south edge → straightened edge =
  13.80; less the 2.0 south wall → **11.8 mm clear PETG zone**; case
  rule carried from Stage 1: no screws, inserts, shielding or other
  metal features inside this band.

## Item 7 — Placements (Pilot B coordinates; see pilotb-report.md)

Exact case-frame (asm) coordinates from the wireless Main board file
(SHA 75db72bc…), transform X = bx−100, Y = by−66.602, validated on
JBATT (record +24.0/+67.9 ✓) and the Main south edge (67.900 ✓):

- **JBATT** board (124.0, 134.5) → asm **(+24.0, +67.898)**; pads
  pin1 VBAT+ / pin2 GND.
- **DLED** board (96.0, 83.0) → asm **(−4.0, +16.398)**, 0603,
  pads LED_A/GND. **Light pipe: KEEP the Stage 1 proposal** — Ø2 pipe
  from (−4.0, +16.398) to the shell-central spine surface; the point
  sits on the spine north slope, 31.9 mm from the island centre
  (outside the Ø44 island), visible-while-typing class as proposed.
- **SW1** board (84.5, 134.5) → asm **(−15.5, +67.898)** — **on
  Main's south edge, not in the centre bay** as the Stage 1 note
  assumed. **Plunger proposal: KEEP, relocated** — Ø3 plunger hole
  through shell-central's south slope directly above
  (−15.5, +67.898) (25.2 mm from the island centre — outside the
  island, on the slope). Board implication stands and is sharper:
  SW1's footprint is a generic `TACT` placeholder and the part is
  DNP/hand-fit in the adopted configuration — a fitted tact switch
  (or a defined case switch + test pads) must be settled at the next
  Main respin; the case cannot invent access to an unfitted land.
- **Slide switch (power):** off-board per power board Stage 1.
  Case position (this package): **inner face of the bay east wall**
  (X +28.25), centred Y −34.37, actuator at Z ≈8 facing the bay;
  wires ≈35 mm down the wall to the power board's J2 loop pads at
  its south-east. SS-12D10 class (≥0.5 A) per Stage 1.

## Item 8 — Main fixing and tray centre joint

- Tray halves met at X +3.5; at δ=9.5 the half edges land at
  X −6.0 (left half) and +13.0 (right half) → **centre floor infill
  spans X −6.0..+13.0 (19.0 wide), full length** of the separation.
- Main's outer washer sites are board-fixed at X ±(29.6..34.1),
  Y 62.2..66.7 (Stage 1/centre-study record) — the tray-half bosses
  that used to sit under them move ±9.5 away with the halves, so
  **fixing bosses are re-formed in the infill / new tray geometry at
  the board's washer coordinates** (D-062 consequence 4). Spine edge
  joints are redesigned with the infill (same consequence).

## Item 9 — Outline-depth reconciliation (145.6 vs 146.1)

**146.1 is correct.** The production record (D-042 low-deck tree)
gives outline depth 146.1, and it closes arithmetically in the asm
frame: outer north −64.37 (= inner −62.37 + 2.0 wall, centre study)
+ outer south +81.702 (= Main south edge 67.900 + 13.802
straightening, south-notch study) = **146.07 ≈ 146.1**. The 145.6
figure appears only in the arrangement study's base (its "+17 →
291 × 162.6" implies a 145.6 base) — a 0.5 mm datum difference in
that study's north reference, never reconciled there. All Stage B
figures use 146.1.

## Power board Stage-2 checklist (Issue #303 design note) — answers

1. δ proven = 9.5 → bay inner width/depth: cavity 56.5 × 60.0;
   board outline 52.5 × 58.0 with datum (item 2). Block need
   48.5 × 56.0 + margins ✓ (2.0/side X, 2.0 south, datum north).
2. Levelled floor Z = **−0.65** (case Z). Board fixing
   method/positions: NOT settled in this package (2D stage) —
   Stage-2/case detail, flagged.
3. Cable exit: J1 on the board south edge, route to JBATT asm
   (+24.0, +67.898), ≈100 mm class GH–GH (item 5); the route stays
   east of Main's north tab and does not cross the FFC channel stack
   at board level (it crosses the EZmate band only, item 3 note).
4. Switch position: bay east wall inner face, Y −34.37, Z ≈8
   (item 7) → J2 wire ≈35 mm.
5. Contact walls: bay end walls are 2.0 thick; the Keystone 209
   clips need **1.52–1.78 mm** — the wall inner faces at the six
   contact sites (Y −60.37 / −8.37 lines, X −15/0/+15) must present
   a 1.52–1.78 mm clip land (local thinning of the 2.0 wall or a
   board-edge doubler): recorded as a case-side requirement for
   the 3D stage.
6. Board thickness 0.8 confirmed as the package's stack basis
   (item 2). PCBA vs hand-solder of F1/J1 remains an order-stage
   choice (Stage 1 note).

## Zero-margin / unverified register

- Zero-margin items: **none in the adopted stack** (cover margin
  5.35). The unlevelled-floor trap (cover at exactly 22.00) is
  designed out by mandatory levelling, not carried.
- Thin margins flagged: plate notch land to nearest switch hole
  2.75 mm (study); EZmate plate graze 0.2 (relieved by the rim
  notch, item 3); FFC channel graze class at δ=9.5 is the study's
  0.5 mm³-class board graze at δ=9.0 disappearing at 9.5 (wing9
  proof) — design δ carries +0.5 over the 9.0 graze point per the
  D-062 amendment's assembly-margin instruction.
- Unverified in this package: Fly/Wing sliver volume at δ=9.5
  (item 3, 3D stage); 16 mm FFC centre distance (item 4); board
  fixing method (checklist 2).

## Addendum (2026-11-21) — v2 figures redrawn from real geometry

PO rejected the v1 figures as schematic ("draw the actual outline").
`case296b-topview-v2.png` / `case296b-sections-v2.png` (goal files/)
replace them as the approval figures; every Stage B number above is
unchanged except the flagged item below. Scripts:
`.issue296-runtime/extract_v2.py`, `extract_main_v2.py`,
`render_v2.py`; extracted data `geom_v2.json`,
`main-outline-asm.json`.

Geometry source per drawn shape:
- Case silhouette + section profiles: geometry17 BREP bodies
  (issue-232-final 17mm assembly body set,
  `he-piantor-raise/.issue248-runtime/phaseb/geometry17/`): tray-left /
  tray-right / shell-central / strip-left / strip-right, halves shifted
  ±9.5 in X (δ=9.5). Top view = all edges projected; sections = slab
  intersects at Y=−34.37 (A) and X=0 (B), faces on the cut plane.
- Switch plates: plate-left / plate-right top-face outer wires from
  the same body set, shifted ±9.5, tip notch applied as the
  wing-shape study defines it (clip at |X|=22.47; removed tip shown
  red-dashed).
- Main outline: Edge.Cuts of the D-063 board file (SHA 75db72bc…),
  14 segments chained into the true trapezoid loop.
- Wing outlines: `wing17r-outline-asm.json` (17R Edge.Cuts at the
  recorded fit, δ=0 pose) shifted +9.5; left mirrored.
- Fly: Fly-official-00 body edges, translated to centre (38, −50.14).
- Cells: true AA cylinder projection (Ø14.5 × 50.5 total) at the
  Stage B centres; sections show the true circle (A) / axial
  rectangle (B). Power board, bay walls and the battery cover are
  Stage B-defined outlines/profiles (no solid exists yet) drawn at
  the note's dimensions; the centre-north case edge is re-formed to
  −64.37 across the bay span per item 1/2 (the existing gable valley
  at the centre is superseded there).

### ⚠ FLAGGED CONFLICT — Pilot B asm transform Y offset is wrong by 3.398 mm

Pilot B (item 7) used Y = by − 66.602. The board file's mounting
holes against the case assembly's washer bodies (geometry17) prove
the offset is **−70.000**: board H2 (68.11, 134.4) / H3 (131.89,
134.4) → washer centres asm (∓31.89, 64.40); H1 (100, 79.27) →
(0, 9.27) = washer-main-H1 centre. All three anchors agree at
−70.000 exactly (X = bx − 100 confirmed likewise). Consequences:
- The v2 Main outline is drawn with the corrected transform; its
  south edge lands at asm **+67.90**, exactly as items 1/6/9 state —
  those numbers stand (the antenna band 13.80 / PETG 11.8 stand).
- Item 7's asm Y coordinates are all 3.398 too far south. Corrected:
  **JBATT (+24.0, +64.50), DLED (−4.0, +13.00), SW1 (−15.5, +64.50)**.
  The light-pipe and plunger positions in item 7 move 3.40 north
  with them (same relative placement logic).
- Item 5's JBATT route shortens by ≈3.4 (≈86 mm with allowance);
  the ~100 mm cable class conclusion is unchanged.
- pilotb-coords.json / pilotb-report.md carry the old offset and
  need a correction pass (PMO to disposition; not silently edited
  here beyond this flag).

## PMO disposition of the Pilot B transform flag (2026-11-21)

ACCEPTED. The corrected asm transform (Y offset -70.000, anchored on
board mounting holes H1/H2/H3 against the case washer centres, three
anchors in agreement) supersedes the Pilot B two-anchor value
(-66.602). Corrected case-frame coordinates: JBATT (+24.0, +64.50),
DLED (-4.0, +13.00), SW1 (-15.5, +64.50) - all 3.40mm further north
than the Pilot B report stated. The light-pipe and plunger positions
move with them; the JBATT cable route becomes ~86mm (the ~100mm-class
conclusion stands). Stage B headline numbers are unaffected (Main
south edge +67.90 and the 13.80 antenna band hold under the corrected
transform). pilotb-coords.json / pilotb-report.md remain as originally
written; this disposition is the correction of record for their
coordinate values, and the review ledger entries R-294-44..47 inherit
it.
