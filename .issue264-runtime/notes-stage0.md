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
