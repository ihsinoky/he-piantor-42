# Wireless Wing boards (Issue #299) — fabrication and assembly review requirements

**DRAFT / NOT FOR ORDER.** Review package for Issue #299. No order, charge or
manufacturing release. Use only the four `../<variant>/wwing-<variant>.kicad_pcb`
files listed below with this note.
Qualified board SHA-256 (verified 2026-11-21, before package generation;
identical to the independent Codex re-review's M1 table):

- 16L: `5a7003167b50b147ed0ecb7b6972c53f840556ffd3efd520e64d4cd6fffd711c`
- 16R: `d7ec349e6b2aa4eeb2a711b8dc85ed4ffe28185cf1cb297ab62cabbacd69de44` (Fly notch, 2026-11-21 — see REPORT.md addendum)
- 17L: `a6aa72a1df2848aa6ecd7e14645887bf59784d07af18a04ed75234b652907a03`
- 17R: `5e62589c6cbb51521ebb6b6077e94833c63d644bc5db12aeb9bc8b934743572a` (Fly notch, 2026-11-21 — see REPORT.md addendum)

See `../REPORT.md` (including the GND repair/respin addenda and the
Stage-3 errata) for the full gate record.

- Four variants of one design: **16L / 16R** outline 117.3 × 118.43 mm,
  **17L / 17R** outline 123.3 × 122.43 mm (Edge.Cuts bounding box, KiCad
  frame, after the Issue #296 south-inner-corner trim). Each is a
  **two copper layer**, **1.2 mm** finished board. Signal traces
  **0.10 mm**, power traces (HALL_3V3 / GND) **0.30 mm**, copper
  clearance **0.10 mm**. No rule relaxation. Nominal copper 35 µm (1 oz).
- **POFV (epoxy fill / copper cap) is NOT required.** No via overlaps a
  **different-net** pad: the independent re-review's different-net census
  gives via–pad minima of **0.100 / 0.1016 / 0.100 / 0.1052 mm**
  (16L / 16R / 17L / 17R), all at/above the 0.10 mm floor. Supply
  ordinary plated through vias, diameter **0.60 mm / drill 0.30 mm**
  (via counts: 231 / 253 / 232 / 255 per variant), mask tenting on both
  sides. Same-net via-on-pad junctions exist by construction (GND
  stitch vias of the respin round); these are electrical junctions of
  one net, not clearance cases, and are not to be filled.
- **46 NPTH per board**: 42 × diameter **1.7 mm** + 4 × diameter
  **2.2 mm**, at the Rev.6 donor positions. NPTH holes are not
  filled/plated.
- `gerber/<variant>/`: full layer set plus drill file from the qualified
  board file above (kicad-cli), absolute mm coordinates;
  `wwing-<variant>-gerber.zip` bundles the same set per variant.
- Assembly is **bottom side only, as drawn** (the boards install
  flipped; every placed part sits on the B.Cu face), **49 placed parts /
  4 exact MPN groups** (`BOM-jlcpcb.csv`, identical for all four
  variants): 21× TMAG5253BA3IQDMRR (**C22401868**, X2SON-4, TI DMR
  land pattern), 3× TMUX1208PWR (C494728), 24× GRM188R71C104KA01D
  100 nF 0603 (C45000), 1× FH12-14S-0.5SH(55) (C5378715). No
  substitutions — in particular order the TMAG by its literal part
  number: the **BA3** sensitivity grade is required (the BA1/BA2/BA4
  siblings sit on adjacent LCSC codes).
- **Excluded from BOM/CPL:** the 15 test-point pads and the 46 NPTH
  hole footprints per board, per project convention. No hand-fit parts.
- CPL (`CPL-jlcpcb-gerber-frame-<variant>.csv`) is in the **gerber
  frame**: Mid X = KiCad X, Mid Y = **−KiCad Y** (Y up), 6-decimal mm,
  Layer **bottom**, Rotation = KiCad orientation degrees unchanged.
  Compare assembler-library rotations/centroids against the board at
  DFM — particularly the X2SON-4 sensors (pin 1 = VCC) and the FH12
  bottom-contact connector on the bottom face.
- **DFM watch items (disclosed, not waived).** Different-net copper
  pairs below the 0.10 mm clearance rule exist on two variants, all in
  the recorded route2 graze class: **16R — 10 pairs, worst
  0.082886 mm** (B.Cu GND track vs WING_EN track); **17L — 9 pairs,
  worst 0.090410 mm** (B.Cu GND track vs H_C2_RAW track), remainder
  0.0985–0.0995 mm. 16L and 17R have none. Via–pad minima on 16L and
  17L sit exactly at the 0.10 mm floor. These items are PO judgment
  items at the adoption gate; flag them for manufacturer DFM
  confirmation at order preparation.
- **Rail figures are model outputs.** The far-sensor VCC values in
  `../REPORT.md` Gate 5 come from a resistive-graph solver whose
  stated 1 mΩ via term never applies (see the Stage-3 errata in
  `../REPORT.md`); treat the values as the model's reported output,
  not as a measured guarantee.
- Availability re-check (2026-11-21, public web sources, no login):
  TMAG5253BA3IQDMRR LCSC **InStock** at $0.4214; numeric JLCPCB stock
  is not exposed publicly (jlcsearch index lists the part with no
  stock figure) — the last numeric observations are **2,981 pcs**
  (JLCPCB quote screen, 2026-11-19) and 1,126 pcs (Stage 1, same
  day). One full 4-variant set needs **84** TMAG; the full 20-board
  run needs **420** (10× = 4,200), so the sensor remains the pacing
  item, below the 10× rule on the last numeric observations.
  TMUX1208PWR LCSC **InStock** $0.3008 (12 per set / 60 per run).
  FH12-14S-0.5SH(55) LCSC **InStock** $0.5203 (4 per set / 20 per
  run; last numeric 3,907 pcs, 2026-11-17). Re-confirm numeric stock
  on the JLCPCB side at order preparation.
- Use nonmagnetic sensor-adjacent fixtures. Wing adoption and ordering
  wait for D-049's two conditions, discharged via the #288 Matrix
  board (measured travel curve + noise, and X2SON assembly yield) —
  a PO decision separate from this package.

The artwork alone omits assembly lists and this process note. Use this
complete package; never apply this note to Wing Rev.6 (wired) artwork.
No manufacturer preview, purchase or charge has been requested by this task.
