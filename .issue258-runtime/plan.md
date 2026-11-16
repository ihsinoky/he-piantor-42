# Issue #258 plan — no-carrier low-deck re-examination (completion study)

## Invariants
- NO carrier board. Direct GH Wing->Main harness only.
- Boards Main Rev.7 byte-unchanged. Wing Rev.4 except J_WING pose (Track 1).
- D-024 cavity order invariant; correspondence from physical presentation.
- Verdicts: fitted REPAIRED audit only (round18/frontier machinery).
- Uniform budget (stated): per track/pitch — seed construction + fitted
  repair passes 0+1 (single-point, then +shift moves), same class as
  frontier study; no extra heroics beyond the stated budget.

## Track 1 — N3 bay-facing J_WING
- Pose: J_WING rotated in place (t=0 class, #253 r2 finding) so mating
  axis points toward the bay (along north wall, E-W); pad row along the
  slanted inner edge per #253 §2.1 formulation.
- Step 1: build modified Wing inputs (pcbnew, #253 method) for 17R/17L
  primary; 16R/16L if pipeline holds. KRT re-route fanout, DRC verdicts.
  If fanout cannot close on ANY variant -> record, stop Track 1.
- Step 2: harness at plate Z13.55 in #248 fitted body set (frontier
  machinery, s=0 bodies + N3 outlet geometry adapted from #253 r2 route
  builder): exit along wall -> bay -> round-9 on-axis G tail.
  Gates: repaired audit (target 0; 2 known POM residuals only if
  inherited unchanged), length <=200, unplug-first service (slack +
  extraction/lift-out), Fly 170 + USB, print envelopes.

## Track 2 — thinned GH stack x direct route
- Stack (#255 GH subset, recomputed): floor 2.00->1.60 ribbed;
  connector GH 4.35 + allowance 0.50 + free gap 0.50->0.30
  -> B = 1.60+4.35+0.50+0.30 = 6.75; plate top = B+6.20 = 12.95;
  keytop = 12.95+11.10 = 24.05 (provisional q=1.50).
  Hall reservation 3.40->2.40 (bound 1.60+2.40+0.30=4.30 < B, non-binding,
  sensing geometry untouched). M2x10 tie bound 10.90 < 12.95 non-binding.
- Body set: frontier machinery with stack shift s=-0.60, floor band
  shifted -0.40 (floor top 1.60); trays fused per frontier method.
- Route: round-9 topology seed (round-18 repaired feed) rigid-shifted,
  fitted repair passes 0+1, both pitches. Connector pose: baseline
  Rev.4 south-facing (Track 1 pose only if its fanout closed AND it is
  the better audit — decide from Track 1 numbers).
- Question: does -0.60 stack change fan/neck outcome materially?

## Deliverable
- hardware/case/issue-258-direct-recheck/REPORT.md: Track 1 fanout +
  gate table @13.55; Track 2 stack table + gate table @12.95; closing
  coverage statement (all no-carrier combos, best fitted result each,
  anything <=16.2 unexamined?). Draft decision text in REPORT only.
