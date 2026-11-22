# Keycap design — plan note (Issue #296 umbrella, PO 2026-11-22「キーキャップも設計してね」)

Branch `issue-296-keycaps` from `issue-296-stageb` @ `644f9434f` (case
groove/lap round is in flight on the case worktree — untouched).
New models under `hardware/keycaps/` (build123d). This note is written
BEFORE modelling; all interface values below are extracted from the
record, with sources. One genuine discrepancy was found (item F1) —
it is designed around conservatively and reported, not hidden.

## 1. Interface extracted from the record

### Switch (design reference)
- **Gateron Magnetic Jade Pro HE, KS-20TF10B045NW-Y106** — D-003
  (provisional baseline), docs/specification.md §3.1: full-height HE,
  MX-style keycap stem, total travel 3.5 ± 0.1 (spec) / **3.5 ± 0.2**
  (signed drawing SPEC-KS-20T-041 — the wider value is used for
  interference, per docs/issue-150-case-stage1.md).
- Manufacturer drawing (repo copy:
  `hardware/kicad/qualification/issue-194-wing-rev2/sources/jade-pro.pdf`
  p.7; PNG read in `hardware/case/issue-150-stage1/sources/`):
  - **Stem cross: overall 4.00 ± 0.05 × 4.00 ± 0.05; arm thicknesses
    1.30 ± 0.04 (arm running N–S, thickness in X) and 1.10 ± 0.04
    (arm running E–W, thickness in Y)** — dimensioned on the sheet.
  - Housing body 14.00 ± 0.05; top-view outline 15.40 × 15.10 (the
    lower flange/clip outline at plate level, front view); bottom
    outlines 15.00 ± 0.5 / 14.70 ± 0.5 (below plate).
  - Housing height 11.10 (dimensioned to the cover ledge); plate seat
    5.00 ± 0.05 above PCB top; below-PCB protrusion 2.70 ± 0.1.
- Z stack (case frame, Issue #296): plate top = case Z 10.90; PCB top
  = plate − 5.00. Local frame below: plate top = 0 → housing ledge
  +6.10, stem block top +6.63 (measured, see F1), stem tip +10.10 (F1).

### F1 — DISCREPANCY: stem-tip height (record 9.60 vs drawing 10.10)
Phase A / Issue #255 derived "stem tip = plate + 9.60" as
11.10 + 3.50 (travel) − 5.00. Pixel measurement of the signed drawing
(300 dpi render; scale cross-checked on two independent dimensioned
spans in the same view: 11.10 → 334 px, 5.00 → 151 px, both
30.1 px/mm) gives: stem protrusion above its mounting block
= 3.46 ≈ 3.50 (the T.T. value), block top = PCB + 11.63 (the 11.10
dimension ends at the cover ledge, 0.53 below the block top), hence
**stem tip = PCB + 15.09 = plate + 10.09 ≈ 10.10 ± 0.15**.
The record's 9.60 understates the tip by ≈ 0.50. Consequences:
(a) a cap with the record's assumed q = 1.50 (Junana assumption,
unmeasured) would top at case Z 22.50, not 22.00; (b) Issue #255's
keytop arithmetic inherits the same 0.50. This design uses the
drawing value (primary source) and sizes the top wall for it; the
finding goes to the PMO in the final summary. The print gate
(§5) re-verifies against a real switch.

### Layout / pitch
- 42 keys, **all 1u** — verified from the case's caps.json: 21 + 21
  cap polygons, every one a 16.5 × 16.5 square at its own angle
  (fields at ±30°, thumbs at 25°/40°/55°). No wide keys exist.
- Pitch: **OPEN** (D-015 reopens D-002: candidates 17.0 / 16.5 /
  16.0). The built case + caps.json are the 17.0 class. Per brief:
  primary variant = 17 mm pitch, second variant = 16 mm pitch,
  regenerated from parameters. (16.5 pitch would take width 16.0 —
  same parameter, not a separate deliverable.)
- Case cap assumptions being replaced: cap 16.5 × 16.5, size tol
  ±0.25/dimension (ASSUMED), seating play 0.15, Junana physical
  measurement = open print gate (case-3d.md P0/P1). Shelf↔cap nominal
  gap 1.30, worst-case remainder +0.35; shelf ends at outermost cap
  extent + 1.30 (outermost |X| = 151.001 from caps.json contours).

### Reference cap (specification §3.2)
16.5 × 16.5, MX cross stem; Beekeeb / Tai-Hao MT165-MX is the named
reference part. Issue #150's acceptance proposal for narrow caps:
underside must avoid the switch housing over the full stroke;
play budget 0.15/key + centre offset 0.10/side. Issue #150 open
item 1 (measure a real cap's MX fit / skirt) was never closed — the
socket fit therefore stays a print-gate verification (§5), with a
calibration coupon as part of the design.

## 2. Design (local frame: plate top z = 0, key centre origin)

Parametric in `hardware/keycaps/keycap.py` (build123d). Pitch-
dependent dimensions marked †; everything else is fixed by the
switch/case interfaces above.

| Parameter | 17 mm variant | 16 mm variant | Basis |
|---|---|---|---|
| Cap outer width W † | 16.50 | 15.50 | W = pitch − 0.50 nominal gap (D-002 rationale) |
| Nominal cap-to-cap gap † | 0.50 | 0.50 | D-002 |
| Skirt inner cavity width | 14.45 | 14.45 | housing body max 14.05 + 0.20/side (play + print tol) |
| **Skirt wall thickness †** | **1.03** | **0.53** | (W − 14.45)/2 — 16 mm is below the FDM wall floor (§4) |
| Cap top z | 11.10 | 11.10 | case datum: top plane stays at case Z 22.00 |
| Skirt bottom z | 4.40 | 4.40 | ≥ travel max 3.7 + flange top 0.50 + 0.20 |
| Cap total height | 6.70 | 6.70 | 11.10 − 4.40 |
| Cavity ceiling z | 10.00 | 10.00 | ≥ ledge 6.10 + travel 3.7 + 0.20 |
| Socket ceiling z | 10.15 | 10.15 | stem tip 10.10 (F1) + 0.05 |
| Top wall (rim / dish centre) | 0.95 / 0.75 | same | 11.10 − 10.15; dish 0.20 |
| Socket boss: outer / bottom z | 5.60 sq / 8.10 | same | engagement = tip − boss bottom = 2.00 |
| Socket cross opening | 4.24 × 4.24 | same | stem max 4.05 → ≈0.10/side tip clearance |
| Socket arm slots | 1.30-arm: 1.28 + off | 1.10-arm: 1.08 + off | nominal −0.02 interference bias; `socket_offset` calibrated by coupon (§5) |

Top surface: shallow cylindrical dish, depth 0.20, axis ∥ local Y
(finger travels along the column), 0.35 chamfer on the top perimeter,
corner radius R2.0 in plan, skirt walls vertical (max outline = the
16.5 square, so the cap stays inside the case's verified cap
envelope). Legends: **blank** — legend process is a separate open
item, not invented here.

### Boss / bore entry (named assumption, print-gate verified)
At full press (descent 3.7 worst) the socket boss bottom reaches
z = 4.40, i.e. 1.70 below the cover ledge plane (6.10): the boss is
designed to enter the switch cover's stem bore, as on all MX caps
(the stem bore is what makes MX cap engagement ≫ protrusion −
travel possible at all: without bore entry the maximum engagement
would be 4.00 − 3.7 − 0.15 = 0.15 mm, i.e. no commercial MX cap
could work on this switch — yet specification §3.2 designates one
as reference). Required bore: ≥ 5.90 wide × ≥ 1.70 deep below the
ledge. The bore is NOT dimensioned on the drawing → explicit
print-gate check against a real switch (§5). Fallback if the bore
refuses the boss: boss outer 5.20 / engagement 1.20 parameter set —
retention then still relies on bore entry, only shallower; if bore
entry itself fails, MX-cap compatibility (spec §3.2) is itself in
question and it goes back to the PO as a switch-truth finding.

## 3. Manufacturability (FDM, PETG — project context)
- Orientation: upright (skirt down, top up). Top dish prints as the
  last layers (0.12 layer height recommended at the top; ironing
  optional). Cavity ceiling is a horizontal bridge: spans from skirt
  wall to boss ≈ 4.4 mm per side — bridgeable in PETG. Socket cross
  ceiling bridges 4.24 mm. No other overhangs; skirt walls vertical.
- Assumed print tolerance: **± 0.20 mm XY** (the case's own FDM PETG
  assumption), Z ± 0.10. Small-hole shrinkage is handled by the
  coupon-calibrated `socket_offset`, not by a guessed constant.
- Walls: skirt 1.03 (≈ 2–3 perimeters @0.4 nozzle) at 17 mm;
  top wall 0.95 rim / 0.75 dish centre, printed last, fully dense.
- 16 mm variant wall 0.53 < 0.80 FDM floor → regenerates, but is a
  prototype-only/resin or 0.25-nozzle part. Recorded as a measured
  input to the open pitch decision, not silently passed.

## 4. Fit verification (to run, numbers not impressions)
`hardware/keycaps/verify_keycaps.py` (build123d solids + caps.json):
1. Stem fit: socket cross vs stem cross envelope (4.00 ± 0.05,
   arms 1.30 ± 0.04 / 1.10 ± 0.04) — clearance/interference table
   across the coupon offset range.
2. Cap-to-cap: min distance over all 42×41/2 pairs of the designed
   outline at caps.json poses, both pitches (16 mm poses = same
   centres scaled? NO — 16 mm poses do not exist as a layout; the
   16 mm check runs on the Matrix-style local grid: a 3×3 at 16 mm
   pitch, min pair gap; plus the tolerance stack: nominal 0.50,
   worst-case with print ±0.20, play 0.15, offset 0.10).
3. Cap vs case (17 mm, real poses): designed outline ⊆ 16.5 square
   → outermost |X| recomputed from the model outline; shelf stack
   re-run with designed size/tol replacing the ASSUMED ±0.25
   (growth term, remainder vs +0.35 baseline).
4. Bottom-out: cap solid at descent 3.7 vs plate (z 0), housing
   envelope (body 14.05 wide to ledge 6.10; flange outline at plate
   level), skirt bottom clearance; boss vs ledge plane (bore-entry
   depth 1.70, flagged as assumption §2).
5. Pressed/unpressed cap top: 22.00 / 18.30 (case Z) — top plane
   unchanged vs the case's verified assumption; note the case's own
   pressed model used 3.0 travel (theirs), this design uses the
   drawing's 3.5 ± 0.2.

## 5. Print gate (replaces the Junana measurement gate for this cap)
Print the coupon + one cap; on a real Jade Pro (or the Matrix
board): (a) socket seats fully by hand, pull-off with a puller, no
cracks — pick `socket_offset`; (b) boss enters the cover bore over
full travel with no contact (feeler/paper drag at bottom-out);
(c) printed width within ±0.20 of nominal. Gate stays PO-side.

## 6. Deliverables
- `hardware/keycaps/keycap.py` — parametric model (+ coupon),
  exports STEP/STL for both pitch variants.
- `hardware/keycaps/verify_keycaps.py` + results in the design note.
- `hardware/keycaps/DESIGN.md` — short design note (this plan's §1–§5
  finalised with measured results).
- Renders: single-cap close-up, a row on the Wing 17 pitch, caps-in-
  case top view (goal files dir).
- Issue #296 comment; GOAL.md one-liner; commits on this branch.
