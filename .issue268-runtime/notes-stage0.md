# Issue #268 — stage 0 notes (baseline + design decisions)

## Rev.3 baseline (measured from board/m1-matrix18.kicad_pcb)
- 2 layers, outline bbox x 35.975..164.025, y 59.975..140.025 (128.05 x 80.05 mm), 65 footprints.
- Rules: min track 0.10, min clearance 0.10, min via dia 0.60.
- J_WING = JST BM14B-GHS-TBT top-entry GH (BOM C265384), F.Cu at (100,133) rot 0.
  Pads along X at y=133, pin1 x=108.125 -> pin14 x=91.875 (pitch 1.25). MP pads (90.025/109.975, 136.35), no net.
- Pad->net = D-024 canonical: 1 HALL_5V, 2 GND, 3 MUX_A0, 4 GND, 5 MUX_A1, 6 MUX_A2,
  7 WING_EN, 8 GND, 9 MUX_OUT_A, 10 GND, 11 MUX_OUT_B, 12 GND, 13 MUX_OUT_C, 14 GND.
- No native KiCad schematic exists for the Matrix (JITX-generated board; Rev.3 tree has none)
  -> ERC gap is inherited; state it in REPORT.
- Local lib: Wing129 -> ../PCBA.pretty (connector.kicad_mod = the GH footprint).

## Wing Rev.5 arriving-order assignment (verified from built board wing-rev5-17mm-left/routed.kicad_pcb)
- J_WING = FH12 on B.Cu (layer 2); pad n -> D-024 signal n (identical table to Matrix Rev.3 above).
- Main Rev.8 J2/J3: F.Cu, pad n <- signal (15-n) (reversal absorbed at Main, D-043). J2 pad1=GND, pad14=HALL_5V.

## FH12 footprint (corrected, from issue-263-implementation/connector/)
- Signal pads 0.30 x 1.30 (land length corrected per CL586-0533-0), pitch 0.5,
  local frame: origin at pad-row centre, +X toward pin 14, mouth toward +Y,
  pads at local y=-1.00, MP pads 0.90x1.30 at (+/-4.70, +1.20), NC.
- Housing depth: catalog bottom-contact 5.6 (pads.json's 6.4 is pre-correction lineage; envelope only).

## Rev.4 design decisions
- FH12 mounted on B.Cu (same as Wing Rev.5), anchor at old GH site: footprint origin (100,133),
  mouth facing +Y (south edge at y=140.025; housing front reaches ~137.6, on-board).
- Pad-1 side: pad 1 at +X (east), pad row descending toward -X, matching the old GH layout AND
  the Wing mouth-frame chirality: u=(pad1->pad14)=(-1,0), m=(mouth)=(0,+1), f=-Z (B.Cu)
  -> (u x m).f = +1, same as Wing Rev.5 (measured u=(-0.866,0.5), m~(0.5,0.866), f=-Z -> +1).
  Main J2 (F.Cu) chirality will be computed in the verification script for the connection check.
- Pad nets: pad n <- D-024 signal n (unchanged from Rev.3). MP pads: no net (as Rev.3).
- Re-route connector neighbourhood only; disclose copper-diff extent by measurement.

## Manufacturing package (per PMO additional requirement, 2026-11-17)
- JLCPCB-ready, NOT KiCad-native: BOM.csv in project format (Comment,Designator,Footprint,LCSC Part #)
  with real LCSC codes carried from the Rev.3 BOM; only J_WING line changes:
  FH12-14S-0.5SH(55) with placeholder C-HIROSE-FH12-14S (do NOT invent a code).
- CPL-jlcpcb-gerber-frame.csv (Designator,Mid X,Mid Y,Layer,Rotation), gerber frame =
  KiCad frame via (X, -Y); Matrix offset vs KiCad-frame CPL = (+36.000000, -140.000000) (PR #220 method,
  Rev.3 NOTES). All rows except J_WING carry over; J_WING row recomputed (bottom layer, body centroid =
  housing centre, local +1.40 from pad-row origin, documented like the Rev.3 GH centroid note).
- Include CPL-jlcpcb-gerber-frame-NOTES.md + quote-handoff.md (Rev.6 exemplar) in the package.
- FABRICATION.md marked DRAFT / NOT FOR ORDER.
