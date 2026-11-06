# Matrix Rev.3 — fabrication and assembly review requirements

Review package for Issue #182. No order, charge or manufacturing release.
Use only `../board/m1-matrix18.kicad_pcb` from this Rev.3 directory with this note.
Qualified board SHA-256:
`7ad3c6e67aed41f882b87f38f7ea8f812805e56837bf15a1d21dc2479060b8db`.
See `../verification.json`, `../inspection/final/assessment.json`,
`../inspection/final/via-pad-audit.json` and `../all-vias.csv`.

- **POFV (epoxy fill and copper cap / plated-over via) is NOT required.**
  The Matrix Rev.2 requirement to fill/cap all 146 vias is withdrawn for this
  Rev.3 package: none of the 158 vias overlaps any component pad, including
  bare testpads, NC lands and GH14 reinforcement lands. Every via's outer
  copper annulus is at least **0.107462501 mm** from the nearest pad copper,
  exceeding the unchanged **0.10 mm** requirement. All 28,124 via/pad pairs
  were independently checked, with KiCad native-shape collision crosschecks.
  There are no pad-overlapping vias requiring filling or capping.
- Supply ordinary plated through vias, **158 sites, diameter 0.60 mm /
  drill 0.30 mm**, with the inherited mask tenting on both sides. Do not add
  fill/cap processing. KiCad/Gerber do not encode a filling process; this
  note explicitly replaces Rev.2's process request for this package only.
  Main board D-022 and the historical Rev.2 package are unaffected.
- One **128 x 80 mm**, **two copper layer**, **1.2 mm** finished board.
  Signal traces **0.10 mm**, HALL_5V/GND traces **0.30 mm**, copper clearance
  **0.10 mm**. No rule relaxation. Nominal copper 35 um (1 oz).
- Four **NPTH diameter 2.2 mm** mounting holes; **diameter 5 mm copper
  reservations** retained on both layers. NPTH holes are not filled/plated.
- `gerber/`: seven artwork layers, separate PTH/NPTH drills; absolute mm
  coordinates, Gerber 4.6, drill decimal resolution 0.001 mm. `.gbrjob` is
  informative only (its size includes outline stroke; finish is unspecified).
  Parsed copper, pad, outline and drill geometry matches the supplied PCB.
- `paste/`: 160 front apertures, empty bottom paste; all 18 bare testpads
  intentionally have no paste. All assembly is on the top side.
- `BOM.csv` and `CPL.csv` were regenerated from Rev.3 and are byte-identical
  to Rev.2, so the Rev.2 assembly lists are reusable. There are 43 assembled
  components / 4 exact MPN groups: 18 Hall sensors, 3 MUX, 21 capacitors,
  1 GH14 header. Testpads and NPTH holes are excluded; no substitutions.
- CPL is in mm, top side, CCW rotations. Origin is the lower-left board edge,
  KiCad (36,140), X right / Y up. GH14 uses its body centroid (100,135.325),
  CPL (64,4.675) mm, rather than the signal-row origin (100,133).
- GH14 is BM14B-GHS-TBT(LF)(SN), C265384, top-entry 14-contact / 1.25 mm;
  pad 1 is rightmost in top view; reinforcement lands remain NC.
- `assembly-top.svg/pdf/png` identifies pad numbers, pad 1 and body centroids.
  Compare assembler-library rotations/centroids to this drawing, particularly
  DRV5055 and GH14, at a separately authorized manufacturing review.
- Placement, outline, interface, net assignments, artwork and paste membership
  are unchanged from Rev.2. The inherited `M1 MATRIX18 / ISSUE178` silk label
  is retained because this revision changes only traces/vias. Package path,
  board hash and this process note identify the Rev.3 fabrication data.
- Use nonmagnetic sensor-adjacent fixtures. External switch/magnet fixture,
  magnetic/ADC measurements and final manufacturer DFM remain separate work.

The artwork ZIP alone omits assembly lists, paste and this process note. Use
this complete Rev.3 review package; never apply this note to Rev.2 artwork.
No manufacturer preview, purchase or charge has been requested by this task.
