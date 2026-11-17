# Issue #264 plan — stock FFC, folded, for the adopted FPC architecture

## Goal
Verdict: can a stock (ready-made) FFC, folded to the bent plan path with a
3D-printed folding jig, realise the D-042 configuration (plate 10.90) in
place of the custom FPC? Paper electrical guarantee stays open by PO
acceptance; closure is by post-purchase measurement (procedure is a
deliverable).

## Stages
0. Read references (excerpts): #261 REPORT (adopted config, route geometry,
   placement spec, audit machinery), #248 round-13 Candidate D (why stock
   FFC was killed), B3 FH12/FFC survey data.
1. Cable selection: specific stock FFC (14 cond, 0.5 mm pitch, FH12-class
   contact zone). Seed: Molex 152660149 (152 mm). Survey length variants /
   same-family alternatives. Contact-side arrangement, stiffener, price.
   Check against #261 connector poses; flag any board-side delta
   (top/bottom contact variant) explicitly.
2. Fold plan: map straight cable onto #261 bent plan path. Fold positions,
   angles, mountain/valley, contact-face bookkeeping along the cable
   (both ends must mate). Absorb excess length inside audited geometry.
3. Folding jig design: printed former, fold edges at design radius,
   guides/stops, folding procedure, PETG / Ender-3 envelope. Audit uses
   jig radii + fold positions with stated placement tolerance (±0.5 mm
   class) as allowance or sensitivity run.
4. Fitted audit at plate 10.90 (inherit #261/#248 machinery): folded cable
   as solids (doubled thickness at overlaps, radius bends, tails in ZIFs)
   vs full fixed-body set. Gates 1, 3, 4/5 (inheritance), 7 (incl. jig).
   If 10.90 fails: +0.5 mm steps, report lowest passing height.
5. Electrical: Vfar @127 mA/Wing on (i) B3 assumed 0.035 mm² lanes,
   (ii) pessimistic case (0.026 mm² or maker's max R). Physical closure:
   post-purchase measurement procedure (lanes, 2-wire vs 4-wire,
   multimeter class, acceptance threshold in Ω mapping to Vfar ≥ 4.60 V).
6. Cost: stock cable + jig vs custom FPC ($50–150/iteration), per
   keyboard and per iteration.
7. REPORT.md in hardware/case/issue-264-stockffc/ + draft D-042
   cable-clause amendment text (REPORT only).

## Rules
- Scratch only in .issue264-runtime/. CAD python: cad-venv.
- Small response segments; read back ≤~30 lines at a time.
- Checkpoint commit after each stage. Do NOT push.
