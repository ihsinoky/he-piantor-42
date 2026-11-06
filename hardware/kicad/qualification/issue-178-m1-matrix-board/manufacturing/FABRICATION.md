# M1 MATRIX18 — fabrication and assembly review requirements

Review data only. No order or charge has been placed. No manufacturing release.
Source: `../board/m1-matrix18.kicad_pcb`; read `../export-provenance.json` and
`../inspection/final/assessment.json` (independent all-net four-zero pass).

- One 128 x 80 mm board, two copper layers, 1.2 mm finished thickness.
- Signal 0.10 mm; HALL_5V/GND 0.30 mm; clearance 0.10 mm.
- 146 plated through vias, ALL diameter 0.60 / drill 0.30 mm; 4 NPTH holes,
  diameter 2.2 mm. All four holes reserve diameter 5 mm on both copper layers.
- **ALL 146 plated vias MUST be epoxy-filled and copper-capped/plated-over
  (POFV / IPC-4761 Type VII).** Do not supply hollow/tented-only via-in-pad.
  See `../all-vias.csv`, `../via-pcba-review.json`: 18 mounted centre-in-pad,
  7 mounted drill-edge overlaps, 4 mounted annulus-only, 2 bare-testpad overlaps,
  115 without pad overlap. The all-via treatment intentionally includes every
  site, so an unfilled edge case cannot be missed. Manufacturer must confirm
  this exact two-layer, 0.60/0.30 mm scope and process before a later release.
- KiCad 9 stores tenting, not filling/capping. Gerber/Excellon alone do not
  encode the required fill/cap process; this note controls it. Front mask covers
  free vias; openings at pads remain as plotted. Filling and capping must not
  alter the supplied copper/pad geometry, drill size or trace rules.
- Nominal copper 35 um (1 oz); nonmagnetic fasteners/fixture near sensors.
  Finish and stackup confirmation belong to the later manufacturer review.
  No claimed impedance or assembly-process acceptance is made here.
- `gerber/`: 7 artwork layers plus separate PTH/NPTH drills; absolute coordinates
  in mm; Gerber 4.6, drill decimal quantization 0.001 mm. `.gbrjob` is informative
  only (its size includes outline stroke; finish is not specified).
- `paste/`: front and bottom paste files for PCBA; 160 top pad apertures,
  bottom empty. 18 bare probe pads intentionally have no paste.
- `BOM.csv`: 4 exact MPN groups, 43 assembled components. No substitutions.
  18 Hall + 3 MUX + 21 100nF 0603 capacitors + 1 GH14 header.
  Copper testpads and NPTH holes are excluded from both BOM and CPL.
- `CPL.csv`: mm, top side, CCW rotation. Origin is the lower-left board edge:
  KiCad (36,140); X right, Y up. **GH14 uses its body centroid**, KiCad
  (100,135.325), CPL (64,4.675) mm, rather than its signal-row origin (100,133).
  Other bodies are centred on the inherited footprint origins.
- `assembly-top.svg/pdf`: actual pad numbers, pad-1 marks, body centroids and
  top-view package outlines. All design rotations are 0 degrees. Before later
  release, reconcile assembler-library rotations/centroids against this drawing,
  especially DRV5055 and GH14; no vendor preview is approved in this task.
- GH14 is BM14B-GHS-TBT(LF)(SN), C265384, top-entry 14-contact / 1.25 mm.
  Pin 1 is rightmost in the top view; reinforcement pads are mechanical NC.
- No switch mounting holes are assumed. An external nonmagnetic switch/magnet
  fixture is required, retaining sensor/target centres and board clearances.

Do not submit the artwork-only ZIP without these process requirements. The
full review package includes this note, all-via inventory, BOM/CPL and paste.
Stock, attrition, cost, Type VII process, orientation and final DFM remain to be
confirmed by the manufacturer when ordering is separately authorized.
