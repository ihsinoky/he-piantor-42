# Wireless Matrix evaluation board (Issue #288) — fabrication and assembly review requirements

**DRAFT / NOT FOR ORDER.** Review package for Issue #288. No order, charge or
manufacturing release. Use only `../wmatrix.kicad_pcb` from this Issue #288
directory with this note.
Qualified board SHA-256:
`5baf83c84f938b4acd787bd2694bd3b6434984dcc2c31410396b3081a113d6e7`.
See `../REPORT.md`, `../verification-s2.json`, `../rail-droop-s2.json`,
`../drc-s2.json`, `../erc-s2.json` and `../via-audit-s2/`.

- One **128 x 80 mm**, **two copper layer**, **1.2 mm** finished board
  (outline inherited unchanged from Matrix Rev.3). Signal traces **0.10 mm**,
  power traces (HALL_3V3 / GND / VIN / VIN_SRC / HALL_3V3_SRC) **0.30 mm**,
  copper clearance **0.10 mm**. No rule relaxation. Nominal copper 35 um (1 oz).
- **POFV (epoxy fill / copper cap) is NOT required.** No via overlaps a
  **different-net** pad: the independent via-pad audit (389 vias x 263 copper
  pads, analytic signed distance, KiCad native collision crosscheck) gives a
  different-net minimum of **0.1002 mm**, at/above the 0.10 mm floor
  (tightest site: GND via at KiCad (120.15, 123.55) vs U_MUXC pin 11).
  14 via sites sit between 0.1002 and 0.125 mm; all are listed in
  `../via-audit-s2/via-pad-diffnet.json`. Supply ordinary plated through
  vias, **389 sites, diameter 0.60 mm / drill 0.30 mm**, mask tenting on
  both sides. Do not add fill/cap processing.
- Same-net via-on-pad junctions exist by construction (e.g. stitching vias
  stacked on test-point pads and on the J_BATT pad). These are electrical
  junctions of one net, not clearance cases; they are not to be filled.
  Test-point pads remain probeable (the via barrel occupies part of the
  1.2 mm pad; the annulus stays exposed under tenting — confirm at DFM if
  probing access is critical).
- Four **NPTH diameter 2.2 mm** mounting holes at the Rev.3 positions;
  5 x 5 mm no-net copper reservations at the corners retained on both
  layers. NPTH holes are not filled/plated.
- `gerber/`: full layer set plus separate PTH/NPTH drills from
  `wmatrix.kicad_pcb` (kicad-cli), absolute mm coordinates.
- Assembly is **top side only, 54 placed parts / 12 exact MPN groups**
  (`BOM-jlcpcb.csv`): 18x TMAG5253BA3IQDMRR (**C22401868**, X2SON-4,
  TI DMR land pattern), 3x TMUX1208PWR (C494728), 21x 100 nF 0603
  (C45000), 2x 10 uF 0805 (C15850), AP2112K-3.3TRG1 (C51118), AO3401A
  (C15127), TYPE-C-31-M-12 (C165948), KT-0805G LED (C2297), UNI-ROYAL
  0603 resistors (C21189/C21190/C23186/C25804). No substitutions.
- **Hand-fit after PCBA (excluded from BOM/CPL):** the Seeed XIAO
  nRF52840 module (U_XIAO, fitted into the soldered socket footprint —
  the module itself is NOT placed by PCBA) and the battery connector
  J_BATT (JST B2B-XH-A (LF)(SN), 2-pin XH; its LCSC code could not be
  verified at package time, so it is hand-soldered rather than listed
  with an unverified code). 25 test points and the 4 mounting NPTH are
  excluded from BOM/CPL per project convention.
- CPL (`CPL-jlcpcb-gerber-frame.csv`) is in the **gerber frame**:
  Mid X = KiCad X, Mid Y = **-KiCad Y** (Y up), 6-decimal mm, Layer top,
  Rotation = KiCad orientation degrees unchanged. Compare
  assembler-library rotations/centroids against the board at DFM,
  particularly the X2SON-4 sensors (pin 1 = VCC, north-west in board
  orientation) and the USB-C connector.
- The XIAO socket's antenna end faces the south board edge; the silk
  antenna keep-out zone (no copper on either layer under the module's
  antenna end) must remain empty — it is already empty in the artwork.
- Use nonmagnetic sensor-adjacent fixtures. Sensor evaluation
  measurements, X2SON yield check and final manufacturer DFM remain
  separate work (D-049 conditions).

The artwork alone omits assembly lists and this process note. Use this
complete package; never apply this note to Matrix Rev.3/Rev.4 artwork.
No manufacturer preview, purchase or charge has been requested by this task.
