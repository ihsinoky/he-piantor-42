# Frontier study plan — how low can the deck go (Issue #248)

Parameter: plate top Z = B + 6.20; shift s = plateZ - 13.55 (s=0 -> B=7.35).
Coarse heights (plate Z): 13.55, 15.0, 16.2, 17.5, 19.0, 20.5, 22.2.
Refinement: bisect lowest passing bracket at ~0.5mm steps, max 3 heights.
Final lowest-passing height: FULL audit (gates 1-5 fitted, 7, 8; gate 6 OPEN).

## Body set per height (from cached(pitch) B=7.35 set, classified by bounds)
- stack bodies (Wing/Main PCB+components, plates, envelopes, POM, screws): shift +s in Z
- floor bodies (floor slab, feet): unshifted
- trays: floor band unshifted + upper band shifted +s, fused (walls/bosses extend)
- shells/strips: rebuild roof from plan height field at new Z (plateau=plate+11.10),
  walls extended to seat; validate method at s=0 vs cached shell (volume/bounds)
- Fly + its seat/cable: classify by bounds; cable storage re-checked at final height

## Route per height
- seed: round-18 repaired feed point lists (sources/round18/results/score_pass2.json),
  rigid +s shift; repair vs the height's body set (round-18 per-strand fitted
  Gauss-Seidel, fitlib adapted to arbitrary body set)
- UNIFORM BUDGET per height: repair passes 0+1 (single-point, then +shift moves),
  both pitches at frontier bracket + final; coarse sweep 17mm primary,
  16mm at the two heights bracketing the frontier + final
- verdicts: repaired audit (fitlib18 standard: plain Common WF + repaired WW)

## Slack / service per height
- round-18 bulge method on repaired feed, direction set extended with downward
  directions (deepened cavity); max-Delta per strand, exact accounting
- stored assembly fitted audit (gate-1 stored count)
- gate 3: step-2 extraction arithmetic per strand (need stored >= span growth
  ~5.67mm for 6mm extraction); steps 1/3 spot-checked at final height
- connected 30.2: record max storable Delta; if >=30.2 fitted-clean + motion
  spot check -> qualifiable (expected only near 22.2; #246 design is the
  qualified fallback at 22.2, different case architecture)

## Deliverable
REPORT.md new top section "Frontier study": table per height (B, plate Z,
plateau Z, gate1 WW/WF, longest, slack min/typical, gate3, service type,
pass/fail), lowest passing height + full audit, what fails 0.5-1.0 below,
trade-off statement, case-delta ledger per height. Checkpoint after EACH height.
