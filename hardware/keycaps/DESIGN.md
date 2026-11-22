# Keycap design — he-piantor-42 (Issue #296, PO 2026-11-22)

Parametric FDM keycap replacing the assumed commercial cap (Junana /
MT165 class, 16.5 mm ±0.25 ASSUMED, physical measurement an open
print gate). Model: `keycap.py` (build123d); verification:
`verify_keycaps.py` (full output in
`.issue296-keycaps-runtime/verify-out.txt`). All 42 keys are 1u —
verified from the case's caps.json (42 polygons, every one a
16.5 × 16.5 square at its own angle).

## Interface (from the record, with sources)

- Switch: **Gateron Magnetic Jade Pro HE, KS-20TF10B045NW-Y106**
  (D-003; specification §3.1). Drawing SPEC-KS-20T-041 (repo copy
  `hardware/kicad/qualification/issue-194-wing-rev2/sources/
  jade-pro.pdf` p.7):
  - Stem cross **4.00 ± 0.05 × 4.00 ± 0.05**, arms **1.30 ± 0.04**
    (N–S arm, thickness in X) and **1.10 ± 0.04** (E–W arm, in Y).
    The 1.30/1.10 axis assignment is read from the drawing's
    dimension-line placement; the fit coupon carries the same
    orientation, so the print gate arbitrates it on a real stem.
  - Travel **3.5 ± 0.2** (drawing; wider than the spec's ±0.1 — used
    for all interference checks, following issue-150's precedent).
  - Housing body 14.00 ± 0.05; plate seat 5.00 ± 0.05 above PCB top.
- Case frame (Issue #296): plate top = case Z 10.90. Below, "local"
  z is measured from the plate top.

### Finding F1 — the record's stem-tip height is 0.50 low
Phase A / Issue #255 derived stem tip = plate + 9.60 as
11.10 + 3.50 − 5.00, equating the stem protrusion with the travel
and the 11.10 dimension with the stem-block top. Pixel measurement
of the signed drawing (300 dpi; scale cross-checked on two
dimensioned spans in the same view, 30.1 px/mm) gives: protrusion
above the stem block 3.46 ≈ 3.50, but the block top sits at
PCB + 11.63 — the 11.10 dimension ends at the cover ledge, 0.53
below the block top. **Stem tip = plate + 10.10 ± 0.15.** This
design uses the drawing value. Propagation: a cap with the record's
assumed q = 1.50 would top at case Z 22.50, not 22.00; Issue #255's
keytop arithmetic inherits the same 0.50. Flagged for the PMO;
nothing else in this design depends on the record's value.

## Design (local frame: plate top z = 0)

Pitch-dependent dimensions are marked †. W = pitch − 0.50 (nominal
cap-to-cap gap 0.50, D-002's rationale).

| Parameter | 17 mm (primary) | 16 mm | Basis |
|---|---|---|---|
| Outer width W † | 16.50 | 15.50 | pitch − 0.50 |
| Skirt wall † | **1.03** | **0.53** | (W − cavity 14.45)/2 |
| Cap top z | 11.10 | 11.10 | case Z 22.00 datum preserved |
| Skirt bottom z | 4.40 | 4.40 | travel max 3.7 + flange 0.50 + 0.20 |
| Total height | 6.70 | 6.70 | |
| Volume | 590.7 mm³ | 393.2 mm³ | from the solid |

Fixed by the switch: cavity width 14.45 (housing max 14.05 +
0.20/side for seating play + print tolerance), cavity corner R1.0
(diagonal clearance +0.283 against an R1.0 housing corner, +0.076
against R0.5 — the corner radii, not the sides, set the diagonal);
cavity ceiling z 10.00 (ledge 6.10 + travel 3.7 + 0.20); socket
ceiling z 10.15 (stem tip 10.10 + 0.05); top wall 0.95 at the rim,
0.75 at the dish centre.

Top surface: shallow cylindrical dish, depth 0.20, axis ∥ local Y
(the finger travels along the column), 0.30 chamfer on the top
perimeter, plan corner radius R2.0, vertical skirt — the plan
outline stays inside the 16.5 square the case verified. Legends:
**blank** (legend process is a separate open item).

### Socket + fit strategy (coupon-calibrated)
Socket cross opening 4.24 (arm-tip clearance ≥ 0.095/side against
the max stem 4.05). Arm slots are biased −0.02 from the arm
nominals; at `socket_offset` = 0 the fit against the drawing's arm
ranges straddles zero (+0.06 interference vs the thinnest arm,
−0.02 clearance vs the thickest) — by design, because a nominal-only
design cannot guarantee a friction fit: stem tolerance ±0.04
against FDM ±0.20. The deliverable therefore includes a **fit
coupon** (`socket-coupon.step/stl`): five socket blocks at offsets
−0.05 … +0.15 (groove-count indexed), printed in the production
PETG/settings; the offset that seats fully by hand and pulls off
with a puller becomes the production `socket_offset`.

### The boss enters the switch's stem bore (named assumption)
Socket boss: 5.60 square, bottom at z 8.10 → cross engagement
2.00. At full press the boss bottom reaches z 4.40, i.e. **1.70
below the cover ledge plane**: it is designed to enter the cover's
stem bore, as all MX caps do (without bore entry the maximum
possible engagement on this switch is 4.00 − 3.7 − 0.15 = 0.15 mm —
no MX cap could work, yet specification §3.2 designates one as the
reference part). Required bore ≥ 5.90 wide × ≥ 1.70 deep below the
ledge. The bore is not dimensioned on the drawing → print-gate
check (below). Solid check: against the housing envelope **with**
the bore, cap intersection is **0.000 at rest and at full press**;
against a solid ledge (no bore) it is exactly the boss-tip volume,
**37.861 mm³** — that is the amount of the fit riding on this
assumption, stated rather than hidden.

## Verification results (verify_keycaps.py)
- Single solids; bbox and section confirm W, cavity 14.45, wall
  1.025 (17 mm) / 0.525 (16 mm).
- Plan view at the real caps.json poses (rotation convention
  asserted by full point-set match against caps.json's polygons):
  **cap-to-cap min distance 0.500** (nominal, same pair as the
  record's square caps); **outermost |X| = 150.269** ≤ the record's
  151.001 (shelf end 152.30 keeps ≥ 2.03 at the ends).
- Shelf stack-up re-run with the designed cap: northern growth term
  0.141 (record's assumed cap: 0.176 by the same method) → worst-case
  remainder **+0.409** vs the record's +0.35. The case's other terms
  (play 0.15, shelf tol 0.20, placement 0.30, plate 0.10) unchanged.
- Cap-to-cap tolerance stack: nominal 0.50; worst-case −0.20
  (touch possible only at the extreme corner of print tol ±0.20 +
  play 0.15 + centre offset 0.10 all adverse at once); RSS-typical
  +0.09. Same budget style as issue-150's acceptance arithmetic.
- Bottom-out (descent 3.7, drawing worst): cap vs plate 0.000
  (skirt bottom ends 0.70 above the plate); cap vs housing envelope
  0.000 with the bore (above); cap top case Z 22.00 rest / 18.30
  pressed — the case's Z22.00 datum is preserved exactly. (The
  case's own pressed model used 3.0 travel; this design uses the
  drawing's 3.5 ± 0.2 throughout.)

## Manufacturability (FDM PETG)
Print upright (skirt down). Dish prints as the last layers (0.12
layer height at the top recommended; ironing optional). Cavity
ceiling bridges ≈ 4.4 mm per side from skirt wall to boss; socket
ceiling bridges 4.24 mm — both bridgeable in PETG; no other
overhangs; skirt walls vertical. Assumed print tolerance ±0.20 XY /
±0.10 Z (the case's own FDM PETG assumption). Skirt wall 1.03 at
17 mm ≈ 2–3 perimeters @0.4 nozzle.

**16 mm variant: regenerates and gaps correctly (0.500 nominal on a
16 mm grid), but its skirt wall is 0.525 — below the 0.80 FDM
floor.** It is a prototype-only part (0.25 mm nozzle or resin) as
designed. This is a measured input to the still-open pitch decision
(D-015), alongside issue-150's finding that the switch envelope
itself leaves ≈ 0 at 16 mm under tolerance. The 17 mm variant has
no such deficit.

## Print gate (PO-side; replaces the Junana measurement gate)
Print the coupon + one 17 mm cap; on a real Jade Pro:
(a) pick `socket_offset` (seats by hand, pulls off with a puller,
no cracks) and confirm the cross orientation; (b) boss enters the
cover bore over the full travel with no contact (paper-drag at
bottom-out); (c) printed width within ±0.20 of 16.50.

## Open items
- Pitch decision (D-015) still open — this design is parametric in
  it; the 16 mm wall deficit above is one of its inputs.
- Legends: blank by design; legend process undecided.
- F1 (stem tip 10.10 vs record 9.60): PMO to disposition — the
  case's cap placement and #255's keytop figures carry the 0.50.
- Bore geometry undimensioned on the drawing → print gate (b).
