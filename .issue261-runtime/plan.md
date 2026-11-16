# Issue #261 plan — low deck, all freezes lifted

## Invariants (function only)
42 keys, Hall (DRV5055-class), Wing x2 + Main, D-024 signal CONTENT
(5V common, addr common, 3 ADC common, EN independent x2, GND returns x6),
Vfar >= 4.60 V @ 127 mA/Wing, Wing removable by a defined procedure.
Pin ORDER at connectors is NOT invariant (both boards may respin).

## Verified failure modes to attack (from consolidated report)
1. Fan convergence in the bay -> wire-fixed contacts 65..96 best (#248/#258).
2. Neck funnel: 14 strands through ~3.2x2.2 mm window (round 9/12 proofs).
3. Planar U-turn reserve reverses order (round 12 topology proof);
   30.2 mm slack unprovable, ~14 mm also fails -> service must NOT rely
   on stored slack; unplug-first procedure is the sanctioned concept.
4. Carrier board becomes the largest fixed-body obstacle (#252).
5. Bend reach at silhouette: R5 climb needs ~4.9 mm, 4.86 available (#253 N2).
6. Stack: GH mated 4.35 binds plate 13.55; floor+gap compression only 0.60
   (#258); SH envelope 2.95 -> bound ladder in #255 (SH 11.55 w/ carrier
   premise; tie M2x10 next at 10.90).

## Stage 0 — screening (>=3 candidates)
(a) SH both boards, boards respun around pose, exits redesigned.
(b) Flat interconnect: ready FFC or custom FPC + ZIF, boards respun.
(c) N3 bay-facing GH + Wing outline tab (#258 residual cell).
(d) Own concept: pin-order co-design at BOTH ends (permutation-free fan)
    + widened neck/channel (case change) on the best connector from (a)/(c).
Per candidate: stack bound (real bounds ladder), fan screen (endpoint
permutation inversions + neck width needed vs available), service concept,
respin scope, supply screen (>=10x guideline; flag presale/obsolete).
Select: lowest plate bound among pass; tie -> fewer respins.
Write Stage 0 into REPORT.md, checkpoint BEFORE Stage 1.

## Stage 1 — build to audit at arithmetic-min plate height
Board candidates (KiCad, yardsticks, DRC/unrouted/ERC 0, via-pad >=0.10),
case geometry (low-deck language kept unless architecture requires change),
interconnect as fitted solids, repaired audit gates 1-8, Vfar extraction.
If min height fails: +0.5 mm steps to 16.2 max, report lowest passing.

## Machinery reuse
#248 phaseb sources (repaired audit, routing, frontier) in
he-piantor-raise worktree; KiCad runtime from sibling .issueXXX-runtime.
Scratch only in .issue261-runtime/. CAD python: cad-venv.
