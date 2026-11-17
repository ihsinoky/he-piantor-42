# Issue 264 — stage 0/1 notes (cable selection + face bookkeeping)

## Connector variant fact (decides the face bookkeeping)
- Hirose FH12-14S-0.5SH(55) [#261 selection] is the BOTTOM-contact variant
  (TME listing: "bottom contacts; ZIF"; Hirose code: the "A" suffix variant
  FH12A-... is the top-contact type). (55) = gold plating. Height 2.0 mm,
  FPC adaptive thickness 0.30±0.05 mm, 0.5 A/contact, 50 mOhm, 20 cycles.
- Bottom-contact: contact springs sit in the housing's lower part; the cable's
  conductive face must point TOWARD the PCB-side the springs face.
  - Main Rev.8: ZIF top-mounted, bottom-contact -> springs face DOWN -> cable
    contacts face world DOWN at the Main tail.
  - Wing Rev.5: ZIF underside-mounted (connector rotated 180 deg about the
    travel axis) -> springs face world UP -> cable contacts face world UP at
    the Wing tail.
  - Required net face change Wing->Main: UP -> DOWN = ODD number of folds.

## Selected cable (seed confirmed)
- Molex Premo-Flex FFC 152660149: 14 circuits, 0.50 mm pitch, Type A
  (same-side contacts), length 152.00 mm, cable thickness 0.27 mm, tin
  plating, 0.5 A/contact, Active. Same-family Type A lengths: 102 (15266-0145),
  127, 152 (152660149), 203 (15266-0153). Type D (opposite-side) exists as the
  parity escape hatch if the fold count were even.
- Fold plan has FIVE folds (odd) -> Type A delivers UP at Wing, DOWN at Main:
  CONSISTENT with FH12-14S-0.5SH(55) at all four sites. NO board-side delta.
- Conductor transport (reflection across each fold line, computed):
  net mapping is a REVERSAL k -> 15-k on BOTH sides. Absorbed by the #263
  respin exactly as #261 already assigns pin order at the footprints to the
  arriving lane order; binding note for #263: with this cable, the Main
  footprint assigns D-024 signal k to the position the Wing delivers as 15-k.
- Length budget: fixed parts T0->B 39.1 + S2->T1 42.5 = 81.6 mm; the middle
  (B->S1 run + S-pair leg) absorbs the rest: leg2 = 19.6..27.6 mm for cable
  lengths 148..156 (152 nominal -> 23.6). S2/V7/final fixed from the Main end;
  S1 floats +-2 mm (jig slider detents per measured cable length).
- Audit model allowances: sheet width 9.6 (real ~9.0 + placement), thickness
  0.32 (real 0.27), fold patches +0.30 below, sensitivity run: S1 +2.3 mm,
  width 10.4, patch 0.35.

## Path revision after audit run 1 (2026-11-17)
- Run 1 (right side valid): U_MUX_C graze 0.0233 mm3 REAL (repair estimator is
  an exact partitioned Common): the sheet's east edge rises with the climb
  while passing ~3 mm from the MUX envelope corner in plan. Fix: climb delayed
  3 mm north (flat to y=-19, climb y -19..-11) - no climb under the MUX field.
- Main ZIF hits 2.81 mm3: modelling artefact of the inherited envelope (its
  slot cut was a mouth notch; #261's sheet stopped at the mouth). Real FH12
  slot runs the connector depth -> slot cut deepened to full depth, both ZIFs.
- Stack run shifted +0.6 mm outboard (S1 x 14.08, S2 x 13.00, V7 x 14.41) for
  Main-study-C23 clearance (its top z 7.55 vs leg3 z band 7.38..7.70).
- Left-side mirror bug found and fixed (double negation on S1 points).
- Final length budget (sharp-corner polyline): total 153.2 mm at S1 y=24.4;
  absorber slope ~2 mm per 1 mm of S1 travel -> S1 detents y = 21.8 (cable
  148) .. 25.8 (cable 156), nominal 23.8 for a 152.0 mm unit.
