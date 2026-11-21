# Stage B plan (Issue #296, 2026-11-21)

Inputs settled: D-062 centre 3-cell + amendment δ=9.5 (plate tip notch only,
Wing boards unchanged), outline 310 × 146.1, FFC channel 11.5.

## Frame
asm frame (all studies): X centred on case, +X east; Y +south, block
Y −62.37..−6.37; case outer north Y=−64.37 (inner −62.37 + wall 2.0),
south Y=+81.70 (= Main south edge 67.90 + 13.802 straightening).
Depth check: 64.37+81.70 = 146.07 ≈ 146.1 (see item 9 reconciliation).
Main board→asm: X = bx−100, Y = by−66.602 (anchors: JBATT (124,134.5)→
(+24.0,+67.9) centre study; Main south edge 67.900 = south-notch record).

## Steps
1. Pilot B extraction FIRST (feeds item 7): parse wmain.kicad_pcb on
   origin/main (SHA check 75db72bc) for JBATT / DLED / SW1 exact
   footprints + nets; validate transform on anchors (JBATT, south edge,
   J4 tab tip). Write pilotb-coords.json.
2. Measurements script (python, matplotlib only for figures; numbers
   from board files + study artifacts): Wing pose at δ=9.5 (shift +9.5
   from geometry17 baseline fit), FFC connector-centre spans (Main
   J2/J3 from board file; Wing J_WING from PR #300 tree @3fcad246f),
   EZmate route at Fly dx=+38 (min) — re-run polyline via study waypoints
   scaled to δ=9.5; JBATT route polyline.
3. Figures: topview (full + bay zoom + FFC zoom) → case296b-2d-topview.png;
   sections (N-S at X=+7.5 through block; E-W through bay; south band
   detail) → case296b-2d-sections.png. Goal files dir.
4. Design note .issue296-runtime/case-2d-stageb.md, items 1–9 of brief,
   every dimension sourced; power-board Stage-2 checklist answered
   (bay inner dims, floor Z −0.65, board outline/datum, cable exit,
   switch position, wall thickness 1.52–1.78 at contact sites).
5. Pilot B ledger entries in docs/review-ledger.md (new Pilot B section)
   + pilotb-report.md (procedure §6 shape, reconciliation arithmetic).
6. Issue #296 comment; GOAL.md line; checkpoint commits + push.
