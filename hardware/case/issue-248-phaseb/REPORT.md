# Round 17 — Feed 3-point chain + case-change slack storage: feed NOT converged (joint optimisation wall reproduced in 5 runs; incumbent unchanged); slack storage CLOSED at proof standard across all remaining families; case delta EMPTY; gates 1/3 still FAIL

## Feed — 3-point chain (corridor -> ORG -> M1 -> M2 -> M3 -> P -> G -> ep)

Machinery: `sources/round17/opt_feed17.py` = round-16 repaired
machinery generalised to 9 vars/strand (126 total). FD gradcheck over
all 126 vars PASSED (the only mismatches are the objective's own
+-10000 gradient clip, inherited from round 16). Fitted verdicts by
`sources/round17/probe17.py` (strict build, no point-dropping,
plain-Common counts; WW counts are lower bounds per the round-10
blind-spot finding).

Validation probes (both pitches, 28 wires each):
- Incumbent (round-14 taut feed, 2-point): builds 28/28;
  WW 6 / WF 108 @17mm, WW 6 / WF 118 @16mm; longest finished
  102.3 mm. (Round 15's audit of the same feed read WW 2 / WF 94/106
  under its builder; the numbers here are this round's probe
  standard, applied uniformly to every state below.)
- geom3 init (the optimiser's geometric start): strict build FAILS
  on all sampled pins (segment-6 'R5 straight too short', need
  5.58-5.77 mm in the M3->P->G region). The screen's starting point
  is not a fitted object.

Stage-1 curriculum runs (bodies: C5 envelopes + Wing PCBs + plates):
1. taut14 warm start, wmul 1.0, 6 chunks: loss 357,917 -> 47,370;
   screen min body -0.62 (plate), min WW pair 0.425.
2. geom init, wmul 1.0, 8 chunks: loss -> 38,900; min body -0.694,
   stuck at strand 9, sample (24.1, -10.5, 12.9) vs plate-right;
   min WW 0.503.
3. Bounded run (chain Z <= 11.4, X <= 40.5 - plate penetration
   impossible for chain points and, Z being linear on segments, for
   samples), wmul 2.0, 8 chunks: min body -0.25 (strand 1 vs
   wing_right at (25.9, 17.3, 8.3)), min WW 0.368. FITTED PROBE of
   this best screen state: WW 21 / WF 55 @17mm, WW 21 / WF 59
   @16mm, and 18 of 56 wires UNBUILDABLE (R5 straights 4.66-9.40 mm
   at segments 4/6/7). Screen-feasible is not fitted-feasible.
4. WW-weighted continuation (wmulw 4.0): degraded (min body -0.585,
   min WW 0.149) - stopped.
5. Tight-hinge continuation (HB 0.85 / HW 1.15): same wall at
   chunk 2 (min body -0.585, min WW 0.153) - stopped.

Stages 2/3 NOT run: stage 1 is a relaxation of stages 2/3 (fewer
bodies); no stage-1 state was both fitted-buildable and better than
the incumbent, so the curriculum has nothing to promote. The
binding constraint is the round-16 one, now confirmed for the
3-point topology: the feed must thread the C5/plate/PCB slot while
holding chain separation into the on-axis approach, and joint
L-BFGS-B on this VM converges to screen states whose fitted builds
fail or score worse than the incumbent. Incumbent unchanged:
round-14 taut feed. Untried lever (named, not attempted at scale):
per-strand Gauss-Seidel repair with strict-build fitted acceptance
per move.

## Slack storage — every remaining family closed

Requirement: exactly +30.20 mm fitted per strand, stored
fitted-clean, releasing toward the Wing-side GH. Case-change
authority (PO 2026-11-16) was available for grooves/pockets/bosses.

1. Closed loops (discs/reels). Any closed curve with bend radius
   >= 5 has length >= 2*pi*5 = 31.42 (total curvature 2*pi), so a
   closed loop cannot account exactly +30.20. Independently, the
   dress-disc grid (144 configs/strand, exact oracle, tray treated
   as carveable) shows a three-way pincer: neighbour separation
   1.25*|n_x| >= 1.05 needs |n_x| >= 0.84; body clearance md >= 0.72;
   desk clearance (feet plane -6.0; groove floor = zmin - 0.8;
   floor skin 1.2) needs zmin >= -4.0. ZERO of 14 strands has a
   config meeting all three (the only strands passing md+nx,
   5-8 at beta=20, have zmin -4.19 -> protrusion 6.19 > 6.0).
   Rounds 14-16 had already closed circular storage at
   optimisation standard; this closes the exact-length identity.
2. Secant loops (chord entry/exit on a segment). Entry deflection
   at the near intersection is 180 - acos(h/R) degrees > 90 for
   every h < R (134.6 deg at h = 3.5): R5 trim 11.97 mm against
   <= ~7 mm of available straight. Unbuildable by arithmetic.
3. Point detours. Corridor detour DET (fx-7, -31.5, 1.8): corner
   deflections 125 deg (corridor) / 155 deg (DET). Strict build
   fails; the standard split_corners chamfer amputates DET from
   (21.85, -31.5, 1.8) to ~(23.9, -27.4, 2.8), destroying the
   stored length it was meant to create (proto v2 build log,
   .issue248-runtime/round17/proto1.log).
4. Bights (arc hairpin hosted on a segment). Footprint along the
   host = junction trims 2*5*tan(gamma/2) + arc extent 2R*sin(gamma)
   + leg progress >= ~19-20 mm for gamma in [70, 90] deg. The
   dress segment is 15.2 mm. A bight spanning dress+climb reaches
   Delta ~ 9.4; plus the best buildable climb bulge ~ +4.5;
   total ~ 14 << 30.20.
5. Climb bulges / westward detours. Delta <= ~6.3 per bulge at
   buildable deflections. Steeper variants hit splice-1
   (X -10.5..17.5, Y -16..0, Z -3..1.2) and the joint-screw boxes
   (X 13..17, Y -10..-6, Z -4.6..5.0) for strands 11-14, or the
   Wing PCB (climb-disc probe: -0.595 at (fx, -14.1, 7.9)).
6. Rectangular detours (4x 90 deg). Every leg needs >= 10 mm
   (two R5 trims). Forward variant: Delta = 2a, so a = 15.1 puts
   the spur end at (fx, -2.0, -1.8), crossing splice-1 / joint
   screws for strands 11-14. Backward variant rejoins behind its
   own start (self-crossing).
7. Host-segment alternatives. Climb discs pierce the Wing PCB
   (round-11 column-scan class evidence); B0->B1 is 3.9 mm;
   eastward detours exist only for strand 1 (outlet fan).

Conclusion: under the frozen set (boards/plates byte-unchanged,
deck Z13.55, R >= 5, OD1 lanes at 1.25 mm, desk plane -6.0), no
storage mechanism accounts +30.20 mm fitted-clean per strand.
The binding constraints are wire geometry and fixed-body
geography, not case volume - the PO's case-change authority does
not rescue it. CASE DELTA = NONE: no case solid is modified by
this round, so gates 4/5/7/8 inherit round-16 status (their space
is untouched).

## Gate table (incumbent candidate: round-14 taut feed, no storage)

| Gate | 17mm | 16mm | Note |
|---|---|---|---|
| 1 fitted collisions | FAIL (WW 6, WF 108) | FAIL (WW 6, WF 118) | probe17 standard; WW = lower bound |
| 2 finished <= 200 mm | PASS (102.3) | PASS (102.3) | budget not binding |
| 3 unplug-first service | FAIL | FAIL | no fitted-clean stored slack exists |
| 4 Fly 170 | PASS (inherited) | PASS (inherited) | no case change |
| 5 USB insertion | PASS (inherited) | PASS (inherited) | no case change |
| 6 keycap clearance | OPEN | OPEN | Junana physical measurement, PO-side |
| 7 manufacturing | PASS (inherited) | PASS (inherited) | no changed parts |
| 8 preview STEP | PASS (inherited) | PASS (inherited) | no changed parts |

The 2 known POM-spacer FF residuals are inside the gate-1 WF
counts above (not separately waived this round).

## Unfreeze ledger

Consumed: route envelope only (feed chain points inside the
existing volume; the design_r15 skeleton from round 15 stands).
NOT consumed: the PO-authorised case change for storage (no case
solid modified - no design survived to need it); POM skin notch;
neck tray cut. Retainers remain at (+-8, -30). Boards and
aluminium plates byte-unchanged. Deck Z13.55 / plateau Z24.65
(provisional, Junana q = 1.50) unchanged.

## Comparison

- Round 16: feed machinery repaired; joint optimisation plateaued
  at fitted WF 72-74 with a 2-point chain. Round 17: 3-point
  chain, five stage-1 runs, same wall; the best screen state is
  fitted-worse and partly unbuildable.
- Round 14: incumbent feed produced (WW-cleanest fitted feed of
  the study; still WF 108/118 under this round's probe).
- Rounds 14-16 closed circular slack storage at optimisation
  standard. Round 17 closes secant loops, point detours, bights,
  bulges and rectangular detours at proof/arithmetic standard,
  plus the exact-length identity for closed loops.

## Remaining blockers (PO-level)

1. Feed: WF 0 not reached by joint optimisation in rounds 15-17
   (three machinery generations). Untried: per-strand
   fitted-acceptance repair; or a hand-designed feed corridor
   from the fitted hit map (round-9 method) carrying the
   round-14 assignment.
2. Slack: +30.20 mm is proven unreachable under the current
   frozen set. Gate 3 can only close via a PO change: (a) reduce
   the qualified reserve (the physical extraction need is ~6 mm
   plus handling; the largest storage this round's arithmetic
   admits is ~14 mm via dress+climb bight + climb bulge, at
   trim-feasibility bounds, not fitted-built), (b) relax R >= 5
   for the storage section only, (c) revisit the interconnect /
   service concept (round-13 candidate C), or (d) close the
   low-deck study in favour of D-041 (Delta+6), whose 30.2 mm
   reserve is already qualified.
3. Junana measurement (PO-side) still blocks the final plateau
   height; plateau stays provisional.

# Round 16 — Curriculum feed optimisation + continuous slack placement: optimisation machinery REPAIRED (3 defects); feed NOT converged (topology-bound); continuous slack placement NOT converged (capacity); gates 1/3 still FAIL

## Feed — machinery diagnosis and repair (the round's durable result)

Rounds 15-16's optimiser stalls were traced to three defects in the
screen objective, each proven before repair:

1. **Sample birth/death cliffs.** `var_samples` used
   n = ceil(len/1.5) per segment; counts changed as segments moved,
   making the objective discontinuous. FD gradient check (all 84 vars,
   stage-1 state): var 18 FD = -2.24e7 vs analytic -2.04.
   FIX: sample counts frozen from the init state (`SEG_N`).
2. **Kinked trim penalty.** The capped cot-form trim penalty's FD
   gradient exploded near sharp corners. FIX: smooth deflection-angle
   fillet tangents t = R*tan(defl/2) over the chain
   [corridor, ORG, M1, M2, P, G, ep] (G corner included).
3. **Medial-ridge gradient flips.** The exact signed distance is
   non-differentiable on medial surfaces; the returned witness flips
   and the analytic gradient points the wrong way. Proven at strand-1
   sample 56 vs plate-right: d = -0.750 (the exact plate mid-plane),
   FD -211.1 vs analytic +211.1 per pitch (x2 pitches = the whole
   844.4 discrepancy on var 11). FIX: soft-min signed distance over
   the body's two closest faces (tau = 0.08; clearance underestimated
   by <= 0.055 mm, i.e. conservative).

After repair: FD gradcheck is clean apart from the explained ridge
variable (pre-fix); L-BFGS-B chunks complete 30/30 iterations in
~40 s (previously ABNORMAL stalls of 130-160 s) with monotone loss.

## Feed — stage-1 curriculum results (fitted counts are the verdict)

Stage 1 = 24 bodies (C5 switch envelopes + Wing PCBs + plates).
Warm starts and methods tried, all on the design_r15 skeleton:

| attempt | screen result | fitted (17mm) |
|---|---|---|
| L-BFGS-B from taut14 (broken obj) | 101,658 -> ~19,450, ABNORMAL stalls | - |
| Adam lr 0.08 from taut14 | oscillates (loss rose), killed | - |
| geometric init (broken obj) | WW valley, converged 210,137, body -1.53 | - |
| Gauss-Seidel sweeps from taut14 | joint loss 338,860 -> 68,784, body -2.41 | INVALID: 6 strands unbuildable (R5 trims) |
| joint polish from GS state (smooth obj) | 72,301 -> 54,605 plateau, body -0.75, WW 0.23 | WW 46 pairs, WF 72 hits, 6 unbuildable |
| joint from taut14 (smooth obj) | 338,307 -> 58,961 plateau, body -0.61, WW 0.41 | WW 70 pairs, WF 74 hits, 2 unbuildable |

Stages 2/3 were NOT run: stage 1 is a relaxation of the full body
set, and it does not converge for this topology, which settles the
harder stages. Target WF 0 with WW <= 2 NOT achieved. The incumbents
are unchanged: **round-14 taut feed remains the best fitted feed**
(true WW 2/pitch, WF 94 @17mm / 106 @16mm, buildable, longest
102.20 mm); round-15 taut: WW 6, WF 108/118. Screen loss and fitted
WW anti-correlate in the optimised states because R5 fillet corner
cutting moves fitted wires off the screened polylines. Binding
constraint: the two-point (M1/M2) feed topology on the design_r15
skeleton cannot simultaneously clear the stage-1 bodies and hold
1.35 mm chain separation; a third intermediate point or a new
skeleton is a design change, not an optimisation setting.

## Slack — continuous placement (place16.py)

Formulation: 14 design rings x (cx, cy, Z, R, entry angle a0, sweep
theta), R in [5.0, 9.6] (a near-full loop at R~5 stores +30.2 mm in a
~11 mm footprint vs 18.4 mm for the round-15 R9.2 disk), full-circle
clearance vs the exact oracle at both pitches, ring-ring and
ring-vs-fixed-route hinges, arc-extra target ~29 mm (phase-B fans +
theta re-solve would close the exact +30.20 accounting). Runs:
greedy grid init + joint L-BFGS-B (4 chunks, exact distance), a
6-chunk continuation, then a soft-distance run. **NOT converged:**
best min body distance across all runs -1.01 mm; the soft-distance
run converges (normal termination) to a local optimum with one ring
sample 1.96 mm inside switch-envelope-R_R1_C5 at (40.3, 19.3, 10.5)
and min ring pair 0.362 mm. `opt_fans16.py` / `build16.py` were
written but not run - there is no placement to build on.

This joins round 15's gridded evidence (feasible bands Z 3.9-6.75
dense + sparse northern pockets 9.2-11.5; three assignment solvers
failed; capacity ~5 bands x ~5 disks < 28 at R 7.5-9.2). The
continuous search removes the grid quantisation caveat but reaches
the same wall: at >= 1.05 mm clearance with same-band separation
>= 2R+1, the frozen bay volume does not host 28 storage rings.
Not a proof over every conceivable storage shape (non-circular
coils and partial-arc shapes were not exhaustively searched); the
reel/disk family is closed at optimisation standard, as were round
14's hairpins and round 15's assignment. Storage would need case
free volume the frozen geometry does not provide (step-4 / PO
territory).

## Gate table (both pitches, inherited where marked)

| gate | result |
|---|---|
| 1 fitted collision | FAIL - no new fitted candidate; incumbents stand (R14 taut: WW 2 true, WF 94/106; 2 known POM FF residuals) |
| 2 finished length | PASS (inherited; taut longest 102.3 mm, ~132 with a loop - budget not binding) |
| 3 unplug-first service | FAIL - no fitted-clean stored loop exists (placement not converged); motion steps not qualified |
| 4 Fly 170 / 5 USB / 7 manufacturing / 8 preview | PASS (inherited, unchanged) |
| 6 keycap clearance | OPEN (Junana physical measurement, PO-side) |

## Unfreeze ledger (round 16)

Consumed this round: NOTHING new. Step 1 (route envelope) stands as
consumed in round 15 (design_r15 rise skeleton). No fixed-body
change of any kind; the pre-authorised neck tray cut was not used;
the POM notch (step 3) was not used; steps 2 and 4 untouched.
Boards, plates, GH + D-024, wire spec, deck Z13.55, plateau Z24.65
(provisional), seam rule, blisters, M2x10, retainers (+/-8,-30),
R>=5: all unchanged. F-015: D-037 classification preserved.

## Remaining blockers

1. Feed topology: fitted-clean feed needs a third intermediate
   point per chain or a new rise/feed skeleton (design decision).
   The repaired machinery (fixed sample counts, smooth trim,
   soft-min distance) is in `sources/round16/` and removes the
   solver-stall class for any successor round.
2. Slack storage capacity in the frozen bay volume: reel/disk
   family closed at screen + optimisation standard (rounds 14-16).
   A case-geometry change for storage is step-4/PO territory.
3. Junana cap physical measurement (PO-side) still open; plateau
   Z24.65 remains provisional.

# Round 15 — Body-aware routing: exact machinery VALIDATED; feed not converged; slack-disk placement infeasible in the discretised space; gates 1/3 still FAIL

## Exact-distance optimiser — built and validated (task 1, machinery)

- `exact_oracle.py`: exact signed point-to-solid distance. PLANE/CYLINDER
  faces are evaluated analytically from the face's own BRep (trimmed-region
  ray casting in UV); other faces use per-face DistShapeShape with AABB
  pruning; sign from the BRepClass3d classifier. VERIFIED against raw
  DistShapeShape on 60 random points x 190 bodies (both pitches, route
  region): max |difference| = 0.0 everywhere
  (`.issue248-runtime/round15/oracle_verify.json`). Face census:
  PLANE 10696, BSPLINE 1344, CYLINDER 489.
- Hit-map validation PASSED: the round-14 taut candidate's fitted
  wire-fixed hit map is reproduced exactly by path sampling against the
  oracle — 17mm 94/94 hits, 16mm 106/106; 149 zero-volume near pairs at
  17mm, none falsely flagged. The round-14 wire-wire crossings localise
  to centreline min distance 0.732 mm (both pairs, tail/P region).
- Analytic gradients FD-checked (max err 0.004-0.005) for both the feed
  and reel optimisers.
- TWO screen-blindness defects found and fixed, both inherited from the
  round-14 methodology: (1) sampling at 6 points/segment is blind to
  shallow crossings on long segments — an earlier screen-"clean" feed
  state fitted to 84 wire-wire overlap pairs; round 15 samples at
  <= 1.5 mm spacing everywhere and adds an R5 trim-margin penalty so
  fitted fillets cannot cut across neighbours. (2) `routes_round14.wire()`
  silently DROPS feed points (indices 5, then 4, then 4+5) when the R5
  builder asserts — a fitted "candidate" built through it is not always
  the designed chain. All round-15 fitted probes build STRICTLY
  (assert = recorded strand failure; none occurred).

## Rise skeleton — round-14 rise proven inside the switch envelopes; design_r15 (unfreeze step 1)

Exact distances of the round-14 rise tops: strand 1 sits INSIDE
switch-envelope R0_C5 at both pitches (-0.563 @17mm, -0.975 @16mm);
strand 2 +0.062/-0.350; strand 3 +0.687/+0.275. A Z-scan over
Z 7.6-11.6 at the strand-1/2 lanes has max clearance 0.0 — no vertical
window exists for a 1.0 mm wire there (the envelope sits on the Wing
PCB). The round-14 fitted audit agrees: strand 01 x R0_C5 = 12.09 mm3
(17mm) is its largest single wire-fixed hit.
`design_r15.py` moves the rise tops north and down the (Y,Z) scan
(worst case over both pitches): strands 1-9 Y=-11, Z=10.3 (clearance
1.67-1.75); strand 10 Y=-12, Z=9.9 (1.51); strands 11-14 Y=-13, Z=8.2
(0.82-1.35). Corridor (fx, -18, 5.1), P/G/ep stations unchanged.
This is a route-envelope change only (unfreeze step 1); no fixed body
was touched.

## Taut candidate fitted verdict (design_r15 skeleton + round-14 feed, strict build)

| pitch | wire-wire pairs | wire-fixed hits | longest finished |
|---|---|---|---|
| 17mm | 6 (max 0.75 mm3) | 108 | 102.3 mm |
| 16mm | 6 | 118 | 102.3 mm |

vs round 14 (WW 2, WF 94/106, longest 102.20): the skeleton change
ALONE does not improve the fitted candidate — round-14's body-blind
feed still ploughs the C5 column and plates from the new rise tops
(strand 01 x R0_C5 = 12.11 mm3 persists via the feed segment, not the
rise). The feed must be re-optimised against the exact oracle; that
optimisation (below) did not converge this round.

## Exact feed optimisation — progress, NOT converged

Dense-sampling run (warm start, hinge targets 1.30 WW / 1.15 body,
R5 trim-margin penalty): loss 853,660 -> 164,950 in chunk 0
(40 iterations), then L-BFGS-B stalls (ABNORMAL termination, nit 0 on
chunks 1-3). Fitted probe of the chunk-0 state (17mm): wire-wire
42 pairs (volumes 0.02-2.80 mm3), wire-fixed 100 hits (28 of them
Main-GH DRAWING-BOUND grazes <= 0.006 mm3), longest finished
117.45 mm. Better than the pre-round-15 screen-blind state on every
axis, far from fitted-clean. The machinery is validated; the run is
compute-bound on this VM (1.5 shared CPUs; one objective evaluation
costs seconds at dense sampling) and the hinge landscape stalls the
solver. No silent relaxation was applied.

## Slack reel — shared axis proven impossible; per-strand placement infeasible in the discretised space (task 2)

- Round 14's shared axis C=(0,5) is PROVEN impossible for two sides:
  the mirror construction pairs left pin 15-p with right pin p at the
  same ladder Z and the same radius, and the two 270-degree sweeps
  overlap volumetrically on the north and south bands.
- Shared-axis centre scans (20 + 25 centres, R 6.5-9.2, all ladder
  levels): worst clearance -0.59..-1.8 everywhere. Blockers rotate:
  tray bosses (low), Wing slab Z 7.35-8.55 (mid), switch envelopes
  (east), plates (over key fields), slope cheeks/ceiling (north).
- Per-strand disk placement instead: two exact scans found
  130 feasible (centre, Z) at R=9.2 (coarse grid) and 289 feasible
  (centre, Z, R in {7.5, 9.2}) on the fine grid (Z step 0.95 from 3.9;
  centres on a 2 mm grid; clearance >= 0.55 vs all fixed bodies, both
  pitches; feasible bands Z 3.9-6.75 dense, 9.2-11.5 sparse northern
  pockets, 12.35+ none).
- The 28-disk assignment (conflict: |dZ| < 1.05 AND centre distance
  < R1+R2+1.0) was attacked with three solvers and NOT solved:
  static-order DFS (exhausted), MRV DFS x2 (900 s caps, ~300k nodes
  each), min-conflicts local search (200 restarts x 400 steps; best
  total conflict count 16, plateaued). Capacity estimate agrees:
  ~5 usable Z bands x ~5 disks/band < 28 once same-band separation
  (16.0-19.4 mm) is enforced in the two pocket regions.
- Therefore NO fitted slack loop exists this round and gate 3 cannot
  be qualified. Search-space caveats (state, do not overclaim):
  centres/Z/R are grid-quantised as above; entry/exit directions and
  the 270-degree sweep are inherited from round 14; off-grid centres,
  intermediate radii, or different entry angles were not searched.
  Reel fan optimisation (`opt_reel3.py`, built and gradient-verified)
  had no placement to optimise around and was not run to a build.

## Gate table (round 15)

| gate | 17mm | 16mm | basis |
|---|---|---|---|
| 1 fitted collision | FAIL: WW 6 pairs, WF 108 hits (+2 known POM residuals, FF, reported as before) | FAIL: WW 6, WF 118 (+2 POM) | strict fitted probe of the taut candidate above |
| 2 finished <= 200 | PASS for the taut route: longest 102.3, margin 97.7 (a +30.2 loop would put it at ~132, still <= 200 — but no loop exists) | same | builder lengths |
| 3 unplug-first service | FAIL: no fitted-clean stored loop (placement infeasible, above); motion steps not qualified | FAIL | reel evidence |
| 4 Fly | PASS (inherited) | PASS (inherited) | fixed assembly unchanged this round |
| 5 USB | PASS (inherited) | PASS (inherited) | fixed assembly unchanged |
| 6 caps | OPEN (inherited; Junana physical measurement still PO-side) | OPEN | — |
| 7 manufacturing 19/19 + envelopes | PASS (inherited) | PASS (inherited) | fixed assembly unchanged |
| 8 preview STEP | PASS (inherited) | PASS (inherited) | no new assembly produced (no complete candidate) |

## Unfreeze ledger

Consumed: step 1 (route envelope) — the design_r15 rise skeleton
(rise-top Y/Z only; corridor, stations, tails unchanged). NOT used:
the neck tray cut; no fixed-body change of any kind was made in
round 15. Steps 2-4 untouched. Boards, plates, GH/D-024, wire spec,
deck Z13.55, plateau Z24.65 (provisional), seam rule, blisters,
M2x10, retainers (+/-8,-30), R>=5 certification: all unchanged.

## Remaining blockers

1. Feed convergence: exact machinery validated, but the dense
   objective needs either a faster host, a reduced/curriculum body
   set, or a sturdier solver schedule (softened-hinge continuation)
   to reach fitted-clean. Current best fitted state: taut candidate
   above (WW 6 / WF 108 @17mm).
2. Slack storage: per-strand 270-degree disks do not pack in the
   discretised placement space (3 solver failures + capacity bound).
   Unexplored continuations: continuous (off-grid) placement
   optimisation; smaller radii via a larger joint-loss budget in the
   fans; different entry/exit angles; or a different storage concept
   — the last two change the round-14 reel assumptions and the
   service concept itself is PO territory (step 4) if case geometry
   must move.
3. Junana cap physical measurement (PO-side) still open; plateau
   Z24.65 remains provisional.


# Round 14 — Candidate A build round: fan closed at screen level; slack loop NOT fitted-qualified; gate 3 FAIL

## Requirement change (PO decision, 2026-11-15)

Candidate A (no-reserve + unplug-first service) is adopted as the build
direction. Gate 3 is REDEFINED: the connected 30.20 mm slide-service
requirement is DELETED and replaced by UNPLUG-FIRST SERVICE:
(1) remove the raised shells, (2) extract the Wing-side GH plug
(~6 mm along its axis, fed by +30.2 mm of harness slack dressed as an
open loop in the bay), (3) lift the Wing out. The new gate 3 qualifies
this procedure: the stored loop geometry must be fitted-clean, and each
motion step collision-free by exact Common at sampled positions.
All other gates unchanged.

## Fan convergence (task 1) — SOLVED at screen level; fitted-clean NOT achieved

Construction (right side; left mirrored): Wing outlets → uniform
translation of the outlet row to the western corridor (fx = 28.85 −
1.25i, Y −18, Z 5.1; parallel segments, 1.25 mm spacing preserved —
this is round 13's A6 corridor/rise, whose corridor and rise are
fitted-clean; A6's failure was its EASTERN fan, which is discarded) →
rise at the corridor lane X = fx to round 9's zf ladder → optimised
two-point feed (per-strand M1/M2, L-BFGS-B; hinge 1.3 mm on all
cross-strand centreline sample pairs incl. the fixed west transit and
the P/G/ep tail; ceiling constraint; approach-angle penalty at P) →
P = G + 6a ON the connector axis (a = (0.866, −0.5, 0); the inlet-row
offset is exactly perpendicular to a, 1.25 mm) → G → ep (round 9 tail
stations verbatim).

Screen result (both the design feed and its mirror): min centreline
pair distance 1.25 mm (= the row spacing itself; binding pair is the
adjacent rise-top origins), optimiser loss 2.13. Round 13's open
problem — the western-corridor fan convergence — is closed at screen
level. Two fitted-level facts temper this:

- The feed optimiser is blind to fixed bodies. The fitted audit of the
  assembled taut candidate finds the feed crossing fixed bodies
  (see gate 1 below). A body-aware variant (fixed-solid surface-sample
  distance penalty, 104,058 samples) was built and audited; it was
  WORSE on every axis (132 hits, 26 wire–wire pairs, 371 mm³
  wire–fixed volume) and is rejected; its numbers are recorded in the
  round-14 runtime logs.
- Fitted wire–wire overlaps of the taut candidate: 2 pairs per pitch
  (left 04×05 and right 10×11, 0.211 mm³ each, audit.py volumes;
  repaired-audit true count: see gate table).

## Slack loop (task 2) — NOT closed; three mechanisms, proof-standard evidence

The +30.2 mm per-strand slack was attempted three ways:

1. Discrete vertical hairpin loops (corridor / rise / feed zones):
   REFUTED by fixed-body geography — the plate (Z 12.05–13.55) and the
   northern sensor row block the corridor/rise zones; at the feed, a
   uniform-family hairpin's descent crosses neighbours (optimiser min
   pair 0.51–0.54). Plan-view coils cannot tile at 1.25 mm strand
   spacing (10 mm loop footprint).
2. Distributed detour in the feed: at polyline level PERFECT (min pair
   1.25, +30.14…30.21 mm on all 14 strands). FITTED realisation fails:
   R5 fillet corner losses consume ≈13 mm of the detour (fitted gain
   ≈17 of 30.2 mm at blend α = 1); extrapolating α to recover the
   length destroys the geometry of the high-offset strands, and
   raising the polyline target to 44.2 mm collapses the screen
   (min pair 0.32 body-blind, 0.73 body-aware with strand 1 at +19.6).
3. Slack reel (the mechanism taken furthest): each strand's slack is
   one horizontal 270° turn around a shared vertical axis at bay
   centre C = (0, 5), at its own Z (ladder 4.6 + 1.12i), radius
   bisected per strand so the ANALYTIC slack (fitted path minus taut
   path, with exact R5 corner-loss corrections at the two miter-modelled
   reel joints) is exactly +30.20 mm. Strand-level results: pins 1–2
   BUILD (R 7.64 / 7.38; fitted stored 166.04 / 176.87; finished
   173.34 / 184.17 mm — within the 200 mm budget); wire–wire fitted
   overlaps among built wires: none. BUT pins 3–14 FAIL to build
   ("R5 straight too short", needs 2.93–6.95 mm, in the reel fan
   segments), and the two built wires FAIL fitted probes vs fixed
   bodies (pin 1: wing_right 3.875, tray-left 3.021, tray-right 2.414,
   R0_C5 envelope 3.026 mm³; pin 2: wing_right 5.256, R0_C5 8.310,
   tray-left 3.065, tray-right 2.849 mm³) — the reel fans were
   optimised against route samples only, never against fixed bodies.

Named remaining path (not attempted; next round): body-aware fan
optimisation with EXACT BRep distance penalties (the sampled-surface
penalty used this round demonstrably under-resolves the large flat
bodies), applied to BOTH the main feed and the reel fans, or a manual
corridor design driven by the fitted hit map.

## Gate table — taut route candidate (the route WITHOUT slack)

## Gate table — taut route candidate (the route WITHOUT slack)

17 mm: gate 1 fitted audit COMPLETE, 0 errors — 98 unexpected hits:
wire–wire 2, wire–fixed 94, fixed–fixed 2 (the known POM skin
residuals, 0.040770 mm³ ×2, carried since round 5). REPAIRED audit
(audit_repair.py, clipped-Common over every zero-volume pair):
TRUE wire–wire hits = 2 (Wire-left-04 × Wire-left-05 and
Wire-right-10 × Wire-right-11, 0.211 mm³ each, full-Common), 0
zero-volume touches, 0 errors. Wire–fixed hits by body: wing_left /
wing_right 12 each, switch envelopes R1_C5 7 and R0_C5 6 per side,
plate-left / plate-right 7 each, tray-left / tray-right 5 each,
underside U_MUX_B 5 per side.
16 mm: fitted audit COMPLETE, 0 errors — 110 unexpected hits:
wire–wire 2, wire–fixed 106, fixed–fixed 2 (same POM residuals).
REPAIRED audit: TRUE wire–wire hits = 2 (same pairs, 0.211 mm³
each), 0 touches, 0 errors.
Gate 1 verdict: FAIL (target 0 unexpected) — on wire–fixed crossings
and 2 residual wire–wire pairs; the strand–strand problem itself is
fitted-solved (110 → 2 true crossings vs round 9).
Gate 2 (route only): longest finished 102.20 mm (pin 1; tails
3.90 + 3.40 included), margin 97.80 mm — PASS with wide margin.
For the full candidate (route + loop) gate 2 is not evaluable: no
fitted loop exists. Budget is not the binding constraint (route +
30.2 mm ≈ 132 mm « 200 mm; the two built reel strands finished at
173.34 / 184.17 mm).

- Gate 3 (unplug-first service): FAIL. No fitted-clean stored loop
  exists (above), so the motion steps were not run. The service
  procedure itself is documented below for the builder; it is NOT
  qualified.
- Gates 4–8: inherited from round 9 — the fixed assembly is
  byte-identical to round 5/round 9 (assembly index fixed-scope check:
  all fixed operands hash-matched), and gates 4 (Fly), 5 (USB),
  6 (swept caps), 7 (manufacturing), 8 (preview STEP) are properties
  of the fixed bodies. Gate 6 keeps its inherited OPEN flag: the
  Junana cap physical test has not been performed (PO-side).

## Service procedure (builder document — NOT qualified, gate 3 FAIL)

1. Remove the raised shells (bay cover and raised shell parts).
2. At each Wing-side GH connector, draw the stored slack loop out of
   the bay and extract the plug ≈6 mm along its axis; the +30.2 mm
   loop feeds the extraction.
3. Lift the Wing out.
Reassembly is the reverse. This procedure is specified by the PO
decision of 2026-11-15; round 14 did not qualify it (no fitted-clean
stored loop; motion states not run).

## Unfreeze ledger

None consumed. The pre-authorised neck tray cut (step 1) was NOT used;
no step-2 items were used. All fixed bodies remain byte-identical to
round 5.

## Comparison vs round 9

Round 9 candidate: true 110 strand crossings (repaired audit), longest
finished 198.366 mm, gates 2/4/5/6/7/8 PASS under the OLD gate set.
Round 14 taut route: screen min pair 1.25 (round 9's feed family was
its crossing source); fitted wire–wire TRUE count 2 per pitch (repaired audit) — but the
feed crosses fixed bodies where round 9's wires score 0, and the
candidate carries NO service slack, so it does not satisfy the new
gate 3 at all. Round 14 does not supersede round 9 as a buildable
candidate; it closes the fan-convergence sub-problem at screen level
and maps the slack problem's remaining lever precisely.

# Issue #248 Phase B — Round 13

## Mandate — service-mechanism / interconnect change study (PO authorization 2026-11-15)

Rounds 8–12 closed the sliding-reserve problem from three sides (assignment
floor 110 true; vertical family by proof; flat order-preserving turn by
proof). The PO authorized studying changes **outside the frozen set**: the
service mechanism and the interconnect itself. This round is a STUDY: no
frozen tree, board, or decision was modified. Screens/probes live in
`sources/round13/` and `.issue248-runtime/round13/`. All gate-1 screens use
the centreline screen of rounds 5–12 plus exact-Common probes against the
frozen round-9 solids (17 mm, right side; probe pipeline validated by a
positive control: wire-vs-itself Common = 72.68 mm³ ≈ its swept volume).

## Candidate A — no reserve, unplug-first service

Route: Wing outlets → corridor → fan/rise → round 9's on-axis G approach →
Main inlets. No reversal anywhere, so no re-sort is needed.

**Centreline screen (variant A6 — best of eight constructions A1–A8):**
inversions **0 at every Y cut** (−32/−27/−21/−12/0); longest polyline
93.42 mm, **100.72 mm incl. tails**; a harness built with the full +30.2 mm
of slack is ≈131 mm, 69 mm under the 200 cap. Only **4 pairs < 1.0 mm**,
all in the feed family round 9 already carries (pins 10–14 G-station
pass-bys, 0.54–0.61 mm; round 9's fitted tail count for this family was 9).
The reserve knot (45 screen pairs / 110 true) is **gone by construction**.

**Fixed-body probe (exact Common, A6 wires 1–7 vs all frozen solids): FAIL
for the A6 geometry as drawn.** The eastern fan ladder (fx to 28.85, bow to
38.85) trespasses on the Wing's east column: `wing_right` PCB corner
2.14 mm³, `switch-envelope-R_R0_C5` up to 12.50 mm³, `R_R1_C5` up to
10.66 mm³, `underside-right-U_MUX_B` ≈0.03 mm³ (round 9's own wires score
0.0 against the same solids). The mirror construction A8 (round 9's proven
western feed + one diagonal replacing the reserve) fails the centreline
screen instead: **49 pairs < 1.0, min 0.0** — the diagonal family collapses
at the shared fan stations. **The open design problem for A is the fan**:
converging 14 strands from the 16.25 mm outlet row into the western feed
inside the corridor's Z band (3.6–5.75 mm, capped above by the Wing
underside sensor bounds). It is bounded and has named levers (Z-laddered
diagonals, Y-staggered fan stations, longer convergence over the corridor);
crucially it is **not** subject to the proven funnel bound — only 14 passes
cross the neck, and round 12 showed that plane essentially free for a wide
row. A build round must close it under the fitted audit.

**Service story (replaces the slide reserve):** (1) remove the central
shell and north strips (removable parts; no Wing stack disturbance);
(2) with the bay open, unplug the Wing GH from the bay side — extraction
travel ≈6 mm along the axis; the harness is built +30.2 mm over the
installed path and the excess is dressed as one gentle open loop in the
bay's free volume (not a routed pack), feeding ≥16 mm to the Wing end
(6 extraction + ~10 handling); (3) the Wing lifts vertically out of its
pocket with the harness detached. **Requirement change for PO:** gate 3's
connected slide-service (30.20 mm release while mated) is deleted and
replaced by unplug-first service; Wing GH mating cycles become the service
budget (low-frequency service; GH-class rating). Tray pack channels become
vestigial; boards, plates, GH, pin maps untouched.

## Candidate B — serpentine (S-fold) service loop in the bay — KILLED at screen

Construction: candidate A's route with an own-plane S-fold (two R5 arcs,
shared tangent, upper leg at zf+10) inserted in the rise→bow leg — two
reversals restore end order; X order is never disturbed. Arithmetic passes:
release ≈32.0 mm ≥ 30.2; longest 125.41 mm polyline, 132.71 incl. tails;
crown centreline max Z21.41 vs plateau underside 22.56. **Screen fails:
21 pairs < 1.0 mm, min 0.08** (pairs 11/13, 12/14) — each strand's exit leg
must cross every intermediate strand's fold plane, and the neighbours' arc
crowns sit exactly in the exit legs' Z band. Alternative placements are
proof-blocked: under the Wing = round 11's PCB pierce; under Main the
headroom is 5.35 mm < the 10 mm fold height; downstream of G there is no
run left. The kill is structural to folding inside a shared corridor with
diagonal exits, not a tuning miss. B was the only candidate preserving
connected slide-service; none survives.

## Candidate C — mid-harness connector split (on candidate A's route)

Concept: a small carrier PCB (~34×16 mm, 2-layer) in the bay NE of Main
carrying two SM14B-GHS-TB (C265343) back-to-back, pin n→n straight through
(D-024 invariant); both sub-harnesses end in GHR-14V-S plugs. Electrical
(B2/B3 framework): the split adds per line +2 mated GH pairs + 2 crimps +
a short trace ≈ **+86 mΩ loop worst case** (30 mΩ contact class, ×7/6
return factor), +44 mΩ typical → Vfar 4.792958 V degrades by ≤10.9 mV to
≈**4.782 V, margin ≈182 mV** to the 4.60 V target. **PASS.** Service:
shells off → unplug at the split (open bay access) → Wing-side sub-harness
comes away in hand for its own GH unplug and Wing lift-out; no dressed
slack loop needed. Cost delta ≈ **+$6–12/unit class** (carrier PCB,
2 headers, 2 housings, 28 extra crimps, +1 harness assembly). Unfreezes
only the harness definition (D-033 becomes two sub-harnesses + carrier)
plus a small carrier-retention feature in the bay. It does **not** solve
candidate A's fan problem (same route); it buys service modularity
(Wing swap without disturbing the Main-side dressing; bench-testable
sub-harnesses) at extra cost and a new failure point (two more mated
pairs in the power path). Build scope if adopted: A build round + carrier
PCB design/retention + harness re-specification.

## Candidate D — FFC / custom FPC

**Stock FFC (Molex 152660149 + FH12) — killed.** The cable is straight;
the route is bent in plan (fan shift, bow lean, NE flights), and a straight
chord crosses unscreened volumes. Its lane resistance is unspecified
(B3), so the electrical claim cannot be closed (on B3's assumed
0.035 mm² lanes it would pass: loop ≈203 mΩ vs the incumbent 187.350 mΩ,
ΔVfar ≈ −2 mV; FH12's 0.5 A/contact > 127 mA on the HALL_5V lane). The
Wing-side FH12 actuator sits under the Wing PCB in the 5.35 mm cavity —
in-situ actuation is not demonstrated. **Custom FPC — viable but
dominated.** Patterned to candidate A's plan shape, its lanes never
converge (0.5 mm pitch printed), so the fan problem dissolves by
construction, and service works (unplug the Main-end ZIF in the open bay,
lift Wing + FPC out together, bench-open the Wing ZIF). But it respins
**both boards (Main Rev.8 / Wing Rev.5)**, reopening the adopted D-040 /
D-039 baselines with full requalification and new manufacturing packages —
round #250 showed how fragile Main's power copper is under connector
changes — plus FPC prototype cost class ($50–150+/iteration) and a
20-cycle ZIF rating. Largest backtracking and highest cost of the set.

## Comparison (PO priorities: cost, low backtracking, freedom, speed)

| Candidate | Knot dissolved? | Service | Electrical | Unfreezes | Cost delta |
|---|---|---|---|---|---|
| A no-reserve | Yes (screen: 4 feed pairs left; fan = build-round problem) | Unplug-first (requirement change) | Unchanged (PASS) | Service requirement (gate 3); case reserve geometry | ≈0 (deletes features) |
| B S-fold | **Killed at screen** (21 pairs, min 0.08) | Would have preserved slide-service | Unchanged | — | — |
| C split | Inherits A | Unplug at split (requirement change) | PASS (Vfar ≈4.782, margin 182 mV) | Harness definition (D-033) | +$6–12/unit class |
| D stock FFC | **Killed** (straight vs bent path; actuator access) | — | Unclosable (lane R unspecified) | Both boards | — |
| D custom FPC | Yes, by construction | Unplug Main ZIF + lift-out | PASS on assumed lanes | **Both boards (Rev.8/Rev.5), D-039/D-040 reopened** | Highest (FPC + respins) |

## Recommendation

**Adopt candidate A** and take it to a build round. It is the cheapest
option (it deletes parts), reopens no adopted baseline (boards, D-024,
D-039, D-040 untouched; the #248 case is still a study), and its one open
problem — the western-corridor fan — is a bounded routing task under the
fitted audit, not a proven bound. Candidate C is the fallback if PO values
service modularity over the added cost and failure point; it shares A's
build round. **Requirement change A (and C) asks of PO:** delete gate 3's
connected 30.20 mm slide-service and replace it with unplug-first service
(Wing GH extraction ≈6 mm + lift-out, fed by +30.2 mm of dressed harness
slack in the bay). If connected slide-service is non-negotiable, no
candidate in this study survives, and the low-deck case should be closed
in favour of the adopted Δ+6 design (D-041).

## Remaining blockers

1. Candidate A build round: western-corridor fan convergence (screen
   evidence above), feed-tail tuning (4-pair family), fitted-audit gates
   1–8, service-procedure qualification (extraction access, slack-loop
   dressing, GH cycle budget).
2. Physical Junana cap measurement — still open, PO-side; plateau Z24.65
   remains provisional.

---
# Issue #248 Phase B — Round 12

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Verdict — the flat order-preserving fan turn is impossible; no candidate built

PO's round-12 mandate (flat reserve, order-preserving fan-shaped turn, neck
channel reshape under unfreeze steps 1–2, OD1 gates standing) was screened.
The screen fails at the turn, with proof-standard evidence in three
independent forms. The neck, by contrast, turns out to be essentially free —
the round-9 window was route-imposed, not solid-imposed (see ledger).

### Proof 1 — planar U-turns of a parallel row necessarily reverse order

For two same-direction semicircular U-turns (radii r, r+Δρ; centres offset
d, entry pitch p=1.25), non-crossing requires nesting, d ≤ |Δρ|. The centre
offset obeys |ΔC| = |p − Δρ| (for the order-preserving sign of Δρ), so
nesting requires |Δρ| ≥ |p − Δρ|, i.e. Δρ ≥ p/2 = 0.625 — which forces the
exit pitch p − 2Δρ ≤ 0. Hence any family of pairwise-disjoint planar
semicircular U-turns exits in reversed (or degenerate) order; an
order-preserving (inversions = 0) flat 180° turn of the 14-strand row does
not exist. The only escapes are turn reversal (round-9 family), Z-separation
(round-11 family, closed by proof in round 11), or crossings.

### Proof 2 — numeric scan of the mandated fan family

Fan as mandated (two R5 quarter arcs + straight per strand, Y-stagger g,
west shift 10+L, Z-ramp exit 5.1→4.0), new zone only (Wing outlet to the
round-9 after[2] handoff), centreline all-pairs, right side:

| g | L | min distance | pairs < 1.0 (of 91) |
|---|---|---|---|
| 1.05 | 0 | 0.000 | 61 |
| 1.05 | 4 | 0.000 | 64 |
| 1.50 | 0 | 0.000 | 55 |
| 1.50 | 4 | 0.000 | 66 |
| 2.00 | 0 | 0.000 | 75 |
| 2.00 | 4 | 0.000 | 81 |
| 2.50 | 0 | 0.000 | 78 |
| 2.50 | 4 | 0.000 | 76 |

Worst pair throughout: pins 2–3, arc2–arc2 — the equal-R5 arc intersection
predicted analytically (intersection at ≈139° lies on both arc2 spans for
g=1.05). Clearing arc2–arc2 needs g ≳ 6, i.e. a 78 mm stagger band; the
available band is ≲36 mm and is further capped at the east edge by the
U_HC1 underside bound (X 32.3–36.9, Y −4.18..0.46, Z 3.95–7.35): strands
1–2 cannot run the Z5.1 row north of Y ≈ −4.7. Length was not the fan's
problem (v1 finished max 180.265 mm); topology is.

### Proof 3 — the wide-row concentric fallback fails on radius and length

Single-centre concentric turn of the uncompressed row (the only disjoint
planar family): centre inside the row span leaves 8 strands with radius
< 5 (R ≥ 5 violated); centre outside the span (XC = 13.875, min radius
exactly 5.0) gives pin 1 an arc of π·21.25 = 66.76 mm and a finished
length of 220.54 mm > 200. The round-9 funnel existed precisely to buy
turn-radius economy (pack span 3.03 → radii 5.03–8.06); a wide row cannot
afford a disjoint planar turn.

### Neck ledger — the window was route-imposed; almost nothing to reshape

Exact-Common band probes against the frozen round-9 solids (17 mm;
probe validated on a sanity band, wing_right 600.0 mm³):

- Neck row band (Y −16..−12 across the Y=−14 cut, X 17.9–36.1,
  Z 4.55–5.65): only **tray-right 0.016 mm³**. A single local tray cut of
  ~0.02 mm³ class (unfreeze step 1) would clear the wide channel at the
  neck plane.
- Corridor band (Y −24.5..2.5, same X/Z): tray-right 0.297 mm³;
  underside-right-U_HC1 10.758 mm³ (the fixed sensor bound above — not
  reshapable, it caps the northern reach instead).
- Turn/outbound bands (X 3–37) contain tray-right 32.699 / 43.116 mm³ —
  these volumes sit in the western pack/splice region the wide route does
  not use; band-level presence only, not path-resolved.

Fixed-body changes consumed: **none** (no build). POM notch: not consumed.
The reshaped channel the mandate priced is therefore nearly free — but it
cannot rescue the design, because the binding constraint is the turn,
upstream of the neck.

### Gate table — round 12

Screen stage only; build stage not entered (screen not clean). Gates 1–8
not run. Baseline unchanged: round-9 candidate, true strand–strand 110
(repaired audit), gates 2/4/5/6/7/8 PASS, longest finished 198.366 mm.

### Remaining blockers / what a successor must satisfy

The reserve problem is now closed from three sides: assignment-only
(rounds 8–9, floor 110 true), vertical (round 11, proof), flat
order-preserving (this round, proof + scan). Any successor must either
(a) accept turn reversal and re-sort the outbound family across a
Z-separated wide frontage — noting the re-sort then faces the same
funnel economics in reverse plus round 9's compressed after[2] handoff
(pitch 0.26–0.36, inherited with the frozen G feed) — or (b) change the
service mechanism or interconnect, which is outside the frozen set and a
PO decision. The neck is not the constraint; the turn is.

# Issue #248 Phase B — Round 11

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Verdict — Concept C is refuted at the build stage; no candidate built

Round 11 was tasked to build round 10's winning reserve, Concept C
(own-plane vertical hairpin), grafted with round 9's a3'/a4 bow feed.
The junction screen's fixed-body half fails decisively before any
build: the hairpin's own centreline passes through frozen fixed
solids, and an exhaustive column scan proves no placement of an
own-plane vertical hairpin exists in this case geometry. No round-11
candidate was built, so gates 2–8 have nothing to run on; the latest
buildable candidate remains round 9 (true strand–strand count 110,
repaired audit). Round 10's Concept C ranking is superseded: its
concept screen was centreline strand–strand plus AABB flag counts,
and the flags it recorded (wing_right 154, plate-right 42,
switch-envelope 276 sample points) were never resolved by exact
Common. Resolved here, they are real material.

### Evidence 1 — concept C centrelines inside fixed solids (exact Common)

Round 10's own `concept_C` centrelines for strands 1, 7 and 14 were
tested point by point (0.8 mm probe box, exact `BRepAlgoAPI_Common`)
against the frozen round-9 fixed solids. A hit means the centreline
itself is strictly inside a fixed solid — a certain gate-1 contact,
independent of wire radius. Full log:
`sources/round11/probe_cl.log`.

- Leg 1 (the Z5.1 run south in its own plane) enters
  `underside-right-U_HC1` (13 points, strand 1, Y −4.0…−1.8): the
  corridor datum is only clear north of the Wing's southern Hall
  sensors; round 9 turned west by Y −13.5, Concept C runs to Y +10.
  Strand 14's leg 1 also enters `tray-right` (2 points, Y −8.5…−7.8).
- Both hairpin arcs pierce `wing_right` (12 points on every probed
  strand: the up-arc bulge at Y 14.5/Z 8.0, the down-arc and exit
  rise at Y −6.7…5.0, Z 7.1…8.4) — the Wing PCB (Z 7.35–8.55) spans
  the hairpin's whole Y band at the outlet planes.
- The up-arc enters `switch-envelope-R_R1_C5` (20 points, strand 1)
  and `plate-right` (3–5 points per strand, Z 11.8–13.9).
- The crown leg at Z 15.1 sits inside `switch-envelope-R_R0_C5`
  (21 points strand 1, 14 points strand 7, Y −2…+7.5). The flagged
  build check "crowns vs slope underside" is moot: the crowns never
  reach the slope, they land in the R0 cap envelope. The "crown
  slide corridor" check is moot for the same reason.
- The exit rise enters `underside-right-C_HC1` (2 points, strand 1).
- Only the two endpoint hits (`J_WING`, Main GH bound) are the
  strands' own classified terminations.

### Evidence 2 — column scan: no clear rise exists at any outlet plane

For planes x0 = 35.125 (pin 1), 27.625 (pin 7), 18.875 (pin 14),
every Y from −34 to +32 (1 mm steps) was probed at eight Z levels
(5.1, 6.6, 8.0, 9.5, 11.0, 12.8, 14.0, 15.1) by exact Common against
all fixed solids. **Zero of 67 Y rows is clear through the full
column at any of the three planes.** Blocker counts (blocked probe
points per solid): pin 1 — wing_right 67, switch-envelope-R_R0_C5
93, plate-right 45, R_R1_C5 37, U_HC1 10; pin 7 — wing_right 67,
plate-right 60, R_R0_C5 47, U_MUX_B 7; pin 14 — wing_right 66,
plate-right 64, shell-central 10, U_MUX_C 7. The Wing PCB alone
blocks the Z 8.0 level at 66–67 of 67 rows per plane. Grid saved in
`sources/round11/column-scan.json`, log alongside.

### Evidence 3 — the crown height is forced, so there is no lower variant

An in-plane (Y–Z) 180° reversal with bend radius ≥ 5 mm has a
perpendicular extent of at least 2R = 10 mm. From the corridor datum
Z 5.1 the crown of any own-plane vertical hairpin is therefore at
Z ≥ 15.1 — exactly as round 10 drew it — and the rise must pierce
the Wing PCB sheet (Z 7.35–8.55) that the scan shows present at
essentially every Y. Tilting the turn out of plane is a different
concept (it spends X, where the neighbouring planes are 1.25 mm
away). A crown below the aluminium plate is equally impossible:
plate underside Z 12.05 leaves 6.45 mm above the corridor datum,
less than the 10 mm any R5 reversal needs. The vertical-hairpin
reserve family is closed in this case geometry, not just round 10's
instance of it.

### Gate table — round 11

| Gate | Result |
|---|---|
| 1 fitted collision | FAIL at screen stage vs fixed bodies (Evidence 1–2); no fitted candidate exists to audit |
| 2–8 | Not run — no buildable candidate |

Comparison: round 9 candidate (built, repaired audit): strand–strand
110 true, gates 2/4/5/6/7/8 PASS, service motion 0 hits. Round 10:
no build (concept study). Round 11: no build (Concept C refuted).
The reserve neck knot from round 9 remains the open problem.

### Unfreeze ledger

None consumed. No fixed body was modified, no tray/shell channel
geometry changed, the POM notch is untouched, and no board, plate,
connector or harness parameter moved. Round 10 was frozen before
the screen work (`round10/` + `round10-sha256.json`, 3679 files).

### Remaining blockers / what a successor must satisfy

- Any reserve must fit under the plate (crown ≤ Z 11.55) or inside
  a genuine plate/PCB aperture column; Evidence 2 shows no such
  column exists in the outlet planes, and the 10 mm reversal bound
  rules out a vertical hairpin under the plate anywhere.
- The strand–strand knot therefore has to be attacked in the flat
  reserve family (round 9's pack topology, true count 110) or by a
  new concept that spends its reversal width in Y at corridor
  height, not in Z. That choice is a PMO/PO decision; this round
  only closes the vertical-hairpin branch with evidence.

---

# Issue #248 Phase B — Round 10

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Stage A — audit repair and true strand–strand counts

Round 9 proved the pipeline fitted audit's per-pair `BRepAlgoAPI_Common`
silently returns zero volume for some long swept wire solids, so every
round's strand–strand count was a lower bound. Round 10 repairs the
instrument (`audit_repair.py`) and re-audits the frozen round-8 and
round-9 candidates. No geometry was changed in Stage A.

### Method

For every wire–wire pair (182 same-side pairs per pitch; cross-side
pairs are AABB-clear, verified from the index bounds):

1. The round's own full-Common volume is kept where it is positive
   (identical geometry and settings — the repair adds a fallback, it
   does not recompute what already worked).
2. Where the full Common reported zero, an exact solid–solid minimum
   distance (`BRepExtrema_DistShapeShape`) is computed. Overlapping
   solids have distance exactly 0, so distance > 1e-3 mm proves the
   pair disjoint at solid level.
3. Where distance ≤ 1e-3 mm, the overlap volume is measured by a
   partitioned clipped Common: the AABB-intersection box (padded
   0.6 mm) is partitioned into ≤4 mm cells and the Common volume is
   summed cell by cell. Common distributes over a partition of one
   operand, so the sum is the pair's total overlap volume; the short
   clipped operands avoid the long-solid failure mode.

A pair is a hit iff its resolved volume exceeds the pipeline threshold
1e-6 mm³. Zero-volume tangential touches are recorded separately
(none occurred).

### Validation

- The known witness reproduces: round-8 pair Wire-right-01/05, audit
  0.0 mm³, resolves to distance 0.0 and a clipped-Common overlap of
  **2.582 mm³**. (Round 9's manual single-box clip measured 2.456 mm³;
  the partitioned clip measures the pair's total overlap, hence the
  slightly larger value. Same pair, same crossing, in both candidates —
  it sits in the neck geometry rounds 8/9 share.)
- The repaired totals land exactly on round 9's screen-derived lower
  bounds (≥114 and ≥110), and every pair the centreline screen flagged
  is resolved at solid level — no screen-flagged pair is left on the
  audit's word alone.

### Corrected counts (strand–strand hits, both pitches identical)

| Candidate | Pipeline audit | Repaired (true) | Found by fallback |
|---|---:|---:|---:|
| Round 8 | 92 | **114** | 22 |
| Round 9 | 74 | **110** | 36 |

Rounds 3–7 strand–strand counts remain lower bounds (not re-audited;
their candidates are superseded). All future gate-1 certifications must
use the repaired audit (full Common + distance/clipped-Common fallback).

### Fixed-body categories — spot check

Question: did the blind spot also hide fixed-body overlaps (the audit
reported many fixed categories clean on the same Common machinery)?
Method (`spotcheck_fixed.py`, round-9 assemblies): every zero-volume
exact pair involving a wire or the Fly cable (518 pairs at 17 mm,
530 at 16 mm), plus
the 50 fixed–fixed pairs with the largest AABB-overlap volumes, were
re-resolved independently — exact solid distance where tractable,
partitioned clipped Common for the Fly/shell pairs (where distance
extrema are pathologically slow), 3-slab partitioned Common for the
fixed sample.

Result: **no hidden fixed-body overlap anywhere.** At 16 mm the full
selection completed — 580 pairs checked, 0 flagged, 0 errors. At
17 mm, 318 of 568 pairs were resolved before the check was bounded
(all of the largest-AABB-overlap fixed pairs among them): 0 hits,
0 errors, and every pair that required a volume resolution measured
exactly 0.0 mm³. The blind spot is specific to the long swept wire
solids; the audit's fixed-body zeros stand. (The unresolved 17 mm
remainder is the same pair categories the completed 16 mm run covers
in full; the partial 17 mm results are preserved in
`sources/round10/spotcheck-fixed-17mm-partial.json`.)

## Stage B — reserve concept study

The binding blocker after round 9 is the reserve neck knot: at the
Y=−14 cut the 14 inbound strands pass a ≈3.2 × 2.2 mm window (mean
lattice spacing ≈0.76 mm < 1.0 mm OD), and the outbound family must
cross the inbound wall through a single-layer over-pass slot. Three
concepts were evaluated at centreline level (right side; the design is
mirror-symmetric). All keep round 9's on-axis Main approach, the Wing
outlet side, deck Z13.55, plateau Z24.65 and the seam rule. Screens use
the round-9 centreline model (R5 fillets, sampled centrelines);
"clean" means zero pairs below 1.05 mm over all 91 same-side pairs.

### Concept A — nested flat U-turn reserve relocated to the bay

Strands fan west during the rise into 14 lanes (X 2.0–15.25, spacing
1.019 mm — already below the 1.05 design margin) at Z 10.3, run north
and make nested 180° flat U-turns (centre X 20.25, radii 5.0–18.25,
staggered entries), return south at Z 11.6 and deliver diagonally to
the round-9 G stations.

- Screen: **91 of 91 pairs below 1.0 mm**; longest finished
  **206.0 mm — fails gate 2**.
- Binding constraints (two, independent): (1) a flat U-turn reverses
  the row order, and the G row has the outlet's order, so the delivery
  diagonals must cross wholesale — the knot is not removed, it is
  moved to the delivery; (2) length: the north run + arc + return
  geometry pushes the longest strand past 200 mm even before the
  delivery weave. Service also degrades: with the turn at the north
  end and one fixed station (G) north of it, no rigid slide of the
  reserve yields the Δ=30.20 mm identity (the two legs change length
  in opposite senses under any single translation).
- Fixed-body changes: the tray pack channels become unused; no new
  parts. Rejected on screen + length + service.

### Concept B — split reserve, two 7-strand packs

Analytic evaluation only (not screened to a candidate). Splitting the
pack into two 7-strand windows of the present size relaxes the window
arithmetic from mean spacing 0.76 mm to ≈1.00 mm
(√(3.2·2.2/7) ≈ 1.003 mm) — exactly the wire OD, with zero margin,
before the diagonal convergence into each window is counted. Each
group's outbound must still cross its own inbound wall through the
same single-layer slot type, and the east pack's lanes (px ≥ 14.5)
force turn centre ≥ 22.5 for R ≥ 5, putting its outbound lanes at
X 27.5–30.5 across the first pack's outbound corridor. The funnel
bound is halved in density but not removed, and no assignment freedom
remains to absorb it. Rejected on arithmetic; ranked last.

### Concept C — own-plane vertical hairpin reserve (ranked first)

Each strand keeps its outlet X plane for the whole journey (planes
spaced 1.25 mm — the connector pitch — so no funnel exists anywhere).
From the corridor (Z 5.1) it runs south in-plane to Y=10, makes a
vertical hairpin (two R5 arcs in its own Y–Z plane, crown Z 15.1,
south leg 12 mm at crown height), returns north at Z 5.1, rises
in-plane to the fan layer and delivers to the round-9 G stations.
The reserve is the hairpin: stored slack is the loop; release is a
15.1 mm northward crown translation plus loop flattening (motion
audit is a build-stage item, see below).

- Screen (base C): **16 pairs below 1.0 mm, all of them in the
  G-entry feed zone** (Y 29–40, Z ≈ 11.0). Zero close pairs in the
  corridor, hairpin and rise zones; lateral order equals the outlet
  order at every Y cut (inversions vs outlet: 0 at all cuts — the
  reserve generates no disorder at all, unlike the pack's 33–84).
- Longest finished **166.7 mm** — 33.3 mm of headroom, the largest of
  any candidate in any round.
- Variants: C2 (two-level Z-staggered G entry, ±1.3 mm) → **10
  pairs**; C3 (plane entry extended 10 mm along the axis) → 8 pairs
  but its stations for pins 1–3 sit at X ≈ 42–45, outside the shell
  (X ≤ 41.0) — infeasible as drawn.
- Tightest cut: the corridor/hairpin zone itself — 1.25 mm plane
  spacing at every cut, ≥ 1.0 mm with the full design margin. The
  funnel bound is removed by construction, not relaxed.
- Binding constraint (what keeps the screen from clean): the feed
  into the on-axis G stations. The G row is offset anti-parallel to
  the fan-in travel, so straight or staggered fan-in lines compress
  against the adjacent axis planes near G (the round-8 approach-tail
  family, one stage earlier). Round 9 solved this exact interface
  with its a3′/a4 bow feed; a build round for C must graft that feed
  (delivering strands to a3′ instead of G) and re-screen the one new
  junction — the hairpin exit's return to a3′ crosses the corridor
  wall, and must be shown to cross it in the Z window the current
  outbound uses (Z ≈ 4.5–5.4 under the Wing edge is occupied by the
  corridor legs themselves in C, so the crossing geometry differs
  from round 9's and is the build round's first screen).
- Fixed-body changes (reserve region only): tray pack channels and
  the neck grooves become unused (channels may be left as-is —
  vestigial, no cost); no tray or shell geometry change is required
  by the screened geometry. Two clearance questions are flagged for
  exact build-stage checks, not resolved by AABB flags: (i) hairpin
  crowns (top Z 15.6, Y −7…15) against the slope underside —
  centreline arithmetic gives ≥ 3.1 mm at Y ≤ 15, shrinking
  northward; (ii) the crown slide corridor (crown translated
  −15.1 mm in Y) against the right Wing's plate/north-strip zone.
  The POM H3/H1 notch (unfreeze step 2) is not consumed by this
  concept.
- Manufacturing impact: none on boards, plates or shell moulds; the
  harness dressing procedure changes (loops dressed in-plane instead
  of a pack) — a service-note change, not a part change.

### Ranking (PO priorities: cost, low backtracking, freedom, speed)

1. **C** — removes the funnel by construction, keeps every frozen
   item, has 33 mm of length headroom to spend on the feed graft, and
   leaves the pack design recoverable (channels unused, not deleted).
   Its open item is one known interface (the G feed), already solved
   once in round 9 in a neighbouring geometry.
2. **A** — relocates the reserve but re-creates the knot at the
   delivery, fails length, and weakens the service mechanism. More
   change, worse result.
3. **B** — least change, but the arithmetic caps it at ≈1.00 mm mean
   spacing with zero margin; it cannot be certified clean.

No concept's centreline screen is fully clean, so per the round-10
mandate no build was started. The path to a buildable candidate is
Concept C plus the round-9 feed graft, screened first at the
hairpin-exit → a3′ junction.

## Remaining blockers

1. Gate 1 / gate 3 (unchanged candidates): the reserve neck knot —
   now measured with the repaired audit at **110 true strand
   crossings** for the round-9 candidate. Resolution path: Concept C
   build round with the round-9 feed graft (Stage B above).
2. Physical Junana cap measurement — still open, PO-side; plateau
   Z24.65 remains provisional.

---
# Issue #248 Phase B — Round 9

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Mandate

Round 9 implements the station change round 8 named as its way out and the PO
approved: the Main-side approach is rebuilt so each strand aligns onto **its own
connector-axis line** at a pre-approach station in the bay volume NE of Main,
then runs its final approach **parallel to the connector axis** into the GH
inlet. Round 8's assignment discipline (physical traversal order from the
verified native pin map) and the frozen round-5 assembly are retained; all
fixed bodies remain byte-identical (`17mm/round9-fixed-scope.json`,
`16mm/round9-fixed-scope.json`: `all_fixed_byte_identical: true`). The POM
H3/H1 skin residuals (0.040770 mm³ each) are retained and reported. F-015 keeps
its D-037 classification.

Mid-round, the PO authorized progressive unfreezing if zero crossings proved
unreachable: (1) tray/shell local wiring-channel geometry, then (2) local shell
reliefs/blister adjustments and the POM H3/H1 skin notch as a named exception.
The unfreeze ledger is at the end of this section. Still frozen throughout:
Main Rev.7 / Wing Rev.4 boards, aluminium plates, GH connector and pin maps,
harness wire spec, deck Z13.55, plateau Z24.65, the seam rule.

## Station geometry — why it removes the round-8 bound

Round 8 proved the old approach tail collapses because the inter-strand offset
vector rotates into near-anti-parallelism with the approach travel direction
(max achievable adjacent-pair distances 0.756–0.993 mm < 1.0 mm). The new
approach never lets the offset rotate: each strand's final approach runs inside
its own **axis-parallel vertical plane**. The Main J2/J3 row direction
d = (−0.625, −1.082532, 0) is exactly perpendicular to the connector axis
a = (0.866025, −0.5, 0) (d·a = 0), so the 14 axis planes are parallel and
spaced exactly **1.25 mm** (the connector pitch). A strand inside its own plane
is ≥1.25 mm from any in-plane path of its neighbours; crossings can then only
be generated before the planes are entered, not inside the approach.

Per strand (right side; left mirrored): after the retained R8 bow point
a4 = (fx+12, 8, z_f), the strand flies to the alignment station
**G = ep + s·a + 0.35ẑ** on its own axis line, with staggered entry distance
s = 7.0 − 0.9·(pin − 6.5) mm (inner pins enter closer, outer pins farther out),
then runs G → ep parallel to the axis. Pins 11–14 carry a floor
s ≥ 5.0 + 0.15·(pin − 10): unfloored, their G→ep slant (down to 1.52 mm) is
shorter than the R5 fillet trim at G (4.42 mm) and the route does not build.
Per-stage order is the endpoint order by construction at G and ep (the planes
are entered in row order); the screen's remaining close pairs sit upstream of
the feed, not in the approach (below).

Result on the tail: fitted-audit contacts with bounds centre Y>15 fall from
**52 (round 8) to 9 (round 9, 17 mm)**. The residual tail pairs are early-feed
expansion pairs, not approach pairs.

## Stage 1 — centreline screen

The centreline screen (round-5-exact model, right side) for the swept
candidate: **55 same-side pairs below 1.0 mm** (round 8 candidate: 57 by the
same screen; round 5: 85), longest finished **198.366 mm**. Composition:
descent/outbound knot at the pack-entry corner (segments 3/7, 3/3, 7/7) ≈ 45,
feed/approach ≈ 8–11 depending on variant bookkeeping, rise ≈ 2. A direct
a3′→G feed (no bow point) was screened first (54 pairs) but the fitted audit
showed it clipping the centre POM spacers (H2/H4) and the tray neck wall
(12 wire–fixed contacts, 17 mm); retaining round 8's a4 bow point removes all
12 at a cost of +0.52 mm on the longest conductor.

## Audit blind spot — the gate-1 counts of ALL rounds are undercounts

While verifying the screen against the round-8 audit, a defect in the
pipeline's fitted audit was found and proven: its per-pair
`BRepAlgoAPI_Common` silently returns zero volume for some long swept wire
solids. On the round-8 assembly (17 mm, right side), the audit's 46 wire–wire
pairs are a **strict subset** of the centreline screen's 57 sub-1.0 mm pairs;
the 11 missing pairs are real crossings — pair Wire-right-01/05, recorded as
0.0 mm³ by the audit, has a wire–wire distance of ~1e-14 mm at
(17.62, −11.93, 4.54), a point-classifier hit inside both solids, and a
box-clipped Common volume of **2.456 mm³**. All four OBB/parallel Common
configurations return zero for this pair while returning the correct
9.683 mm³ for pair 03/04. The defect persists unchanged on this round's
candidate: right side screen 55 pairs vs audit 36 pairs — again a strict
subset, 19 pairs audit-blind, so round 9's true strand crossings number
≥110 across both sides against the audited 74. Consequences: (a) round 8's
true strand crossings number ≥114 across both sides, not the audited 92;
(b) round 9's gate-1 acceptance is therefore read from screen + audit
together — the screen is the complete instrument for strand pairs, the audit
for everything else; (c) the pipeline audit needs a clipped-Common or
distance-based fallback for wire pairs before any future round's gate 1 can
be certified by the audit alone.

## The remaining blocker — the reserve neck knot (upstream of the feed)

Zero crossings is **not** reached. The remaining strand crossings are
generated in the reserve neck — the descent funnel into the pack and the
outbound diagonal crossing it — upstream of everything this round changed:

- Two independent assignment optimizers floor at the same place: round 8's
  550-iteration greedy + 1,900-iteration annealing reached 55 screen pairs;
  this round's searches reach 54–55. Sorted and identity constructions give
  83–88. The floor is structural, not a search failure.
- Station moves do not break it: fan-in station Y ∈ {−18, −16, −14, −12},
  two-stage descent, staggered pack entry (0 / 0.75 / 1.5 mm per pin),
  staggered return start — all leave the count at 54.
- Funnel bound: at the Y=−14 cut the 14 inbound strands pass a window of
  ≈3.2 mm (X, set by the pack width) × ≈2.2 mm (Z) — mean lattice spacing
  ≈0.76 mm < 1.0 mm before the outbound family crosses the same corner.
- Gate bound: the outbound family must cross the inbound wall in plan. The
  only over-pass slot is under the Wing PCB edge (inbound top 5.41 + 1.0 ≤ Z ≤
  6.85 under-Wing centre limit) — a single wire layer over a ≈3 mm frontage
  at the pack-entry corner (X 10–13); 14 strands cannot pass it in one layer.
  A two-layer split (half the outbound climbing to Z 6.6 on the diagonal) was
  screened: 54–91 pairs, all groupings ≥ baseline — the climbs braid.
- The service model forbids the south loop: the stored/released length
  identity (Δ = 30.20 mm exactly) requires the first fixed station north of
  the released tangent (Y ≲ −5), so the outbound cannot first run south and
  loop around the pack's south end.
- Widening the pack/channel (unfreeze step 1) is length-poisoned: a 5-4-5
  lattice (dx 1.2, dz 1.5) screens at 69 pairs with longest finished
  215.1 mm > 200; and the pack cannot widen east at all — max px 12.36 is
  already at the turn-radius ≥5 cap (px ≤ 12.458).

What would have to change is outside the still-frozen set and this round's
unfreeze authorization: a different reserve concept (e.g. single-row pack
travel with a widened neck channel AND a length budget recovered elsewhere),
or a connector/interconnect change. The binding constraint is the pack-entry
funnel + wall-crossing gate, proven above; it is not the Main approach, which
this round fixed.

## Stage 2 — sweep and eight-gate audit, both pitches

| Gate | 17 mm | 16 mm |
|---|---|---|
| 1 Exhaustive fitted collision | **FAIL** — 76 contacts: 74 strand–strand + 2 POM residuals; 0 wire–fixed; 0 Boolean errors | **FAIL** — 76 contacts: 74 strand–strand + 2 POM residuals; 0 wire–fixed; 0 Boolean errors |
| 2 Finished ≤200 mm | PASS — longest 198.366 mm, margin 1.634 mm | PASS — longest 198.366 mm, margin 1.634 mm |
| 3 Accessible ~30.20 mm service | **FAIL by fitted collisions only** — motion clear; service sweep 0 hits both sides | **FAIL by fitted collisions only** — motion clear; service sweep 0 hits both sides |
| 4 Fly 170.000 / R5 / gap 0.30 | PASS — 0 fitted contacts | PASS — 0 fitted contacts |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps | PASS — physical Junana skirt test OPEN | PASS — physical Junana skirt test OPEN |
| 7 Manufacturing + envelopes | PASS — export verification PASS; retention load path complete; required-skin conflicts = the 2 known POM residuals only | PASS — export verification PASS; retention load path complete; required-skin conflicts = the 2 known POM residuals only |
| 8 Fitted preview STEP | PASS | PASS |

Collision counts by category (unexpected contacts, exhaustive fitted audit):

| Round | Strand–strand | Wire–fixed | Other fixed | Longest finished | Note |
|---|---:|---:|---:|---:|---|
| 5 | 163 | 0 | 2 POM | 196.87 PASS | frozen base |
| 8 | 92 (audit; ≥114 true, see blind spot) | 0 | 2 POM | 195.205 PASS | assignment only |
| 9 | 74 | 0 | 2 POM | 198.366 PASS | on-axis approach; tail-zone 52 → 9 |

## Unfreeze ledger (PO authorization 2026-11-15)

| Step | Item | Used? | Evidence / effect |
|---|---|---|---|
| 1 | Tray/shell local wiring-channel geometry (widened pack channel for a 5-4-5 lattice) | **Evaluated, not consumed** | Screened: 69 pairs, longest finished 215.1 mm — fails gate 2 and does not reach zero; eastward widening impossible (turn-radius cap). No tray/shell geometry was changed; byte-identical checks stand unqualified. |
| 2 | POM H3/H1 skin notch (0.040770 mm³ ×2) as named exception | **Not consumed** | The notch would clear only the 2 fixed–fixed residuals; gate 1's binding failure is the strand–strand neck knot, which the notch cannot unblock. Residuals remain reported, per the pre-unfreeze discipline. |
| 2 | Local shell reliefs / blister adjustments | **Not needed** | The rebuilt approach fits the existing shell volume; no wire–shell contacts in either pitch audit. |

No fixed body was modified in round 9. All byte-identical results above are
therefore unqualified.

## Remaining blockers

1. Gate 1 / gate 3: the reserve neck knot (see above) — strand–strand
   crossings generated in the descent funnel and wall crossing, upstream of
   the fixed approach. Binding constraint named with proof; resolution needs
   a reserve-concept change outside the frozen set.
2. Physical Junana cap measurement (q, installed skirt, swept width) — still
   open, PO-side; plateau Z24.65 remains provisional.
3. The pipeline audit's wire-pair Common blind spot must be repaired (or a
   distance/clipped-Common fallback added) before gate 1 can be certified by
   the audit alone in any future round.

---

# Issue #248 Phase B — Round 8

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Mandate and transferred discipline

Round 8 changes ONLY strand routing on the frozen round-5 assembly (operands recovered by serialized hash; `17mm/round8-fixed-scope.json` and `16mm/round8-fixed-scope.json` both report `all_fixed_byte_identical: true`). Fixed bodies, shells, trays, retainers (±8,−30), blisters (GH ceiling/top Z13.20/15.20; Fly Z13.25/15.25), M2×10, deck Z13.55, plateau Z24.65, the seam rule, and the byte-unchanged boards/plates are untouched. The POM H3/H1 skin residuals (0.040770 mm³ each) are retained and reported, not fixed. F-015's invalid Fly solid 42 keeps its D-037 classification (preserved, labelled, not a design contact).

The working discipline is transferred from Wing Rev.2 (Issue #194 / PR #195, D-032). There, the asymmetric DRV5055 footprint mirrors when rotated, and D-032 resolves it by deriving order from the actual physical presentation — "Native bottom transformations preserve the physical pin map. Calibrate active point to land origin … using TI Rev.C Figure 6-5 and the body-centered Wing land" — instead of forcing the nominal order. Transferred here: reserve lanes and downstream fan positions are assigned strictly by the physical traversal order of the verified native pin map (round-7 Stage 0: the endpoint permutation in assembly frames is the identity; disorder is generated inside the route), never by nominal index order. Round 8 therefore re-assigns, per pin, which reserve pack position, which return-fan x, and which fan z the strand takes, keeping every round-5 station coordinate, the concentric reserve, and the 30.20 mm service slide.

## Stage 1 — centreline design and screen

A centreline model reproducing round 5 exactly (max routed 189.566 vs 189.569 mm; 85 sub-1.05 pairs per side, matching Stage 0's 1001-sample screen) was used to search the three assignments (pack σB, fan-x σF, fan-z σZ) in two fan-rise modes (rise late at the fan, rise early during the return). A traversal-order construction, greedy local search (550+ iterations/mode), and simulated annealing (1,900 iterations, violating-pair-focused proposals) all converge to the same floor: the best assignment found leaves **55 of 91 same-side pairs below 1.0 mm centreline distance on the right** (round 5: 85), with screen max finished 195.20 mm. Per-stage pin orders read at route waypoints (global X, ties by Z; the method reproduces Stage 0's round-5 Δ values 33 / 84 / 40 / 61 exactly):

| Stage | R5 Δinv vs prev | R8 Δinv vs prev | R5 inv vs outlet | R8 inv vs outlet |
|---|---:|---:|---:|---:|
| outlet | 0 | 0 | 0 | 0 |
| corridor | 0 | 0 | 0 | 0 |
| reserve_in | 33 | 32 | 33 | 32 |
| reserve_out | 84 | 84 | 51 | 52 |
| fan_in (rise base) | 40 | 48 | 57 | 12 |
| rise_top | 4 | 2 | 61 | 10 |
| fan_out | 0 | 0 | 61 | 10 |
| Main_row | 61 | 10 | 0 | 0 |

The fan now delivers strands in near-endpoint order (inversions vs outlet 57–61 → 10–12). The reserve readings are dominated by the 2D pack and the U-turn's lateral-normal sign change, as Stage 0 warned; projected inversions are not themselves contacts. The candidate was swept because its remaining close pairs are located (below) and bounded, not because the screen is clean.

### Binding constraint: the Main approach tail

For adjacent pin pairs, the maximum centreline distance achievable on the round-5 approach tail (fan4 station (fx+12, 8, z_f) → approach point at 7.00 mm on the connector axis → endpoint, R5 fillets) was computed exhaustively over the full round-5 fan grid (every fx × z_f combination for both strands, independently per pair):

| Adjacent pair | 1–2 | 2–3 | 5–6 | 6–7 | 9–10 | 10–11 | 13–14 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Max achievable min-distance (mm) | 0.756 | 0.779 | 0.859 | 0.890 | 0.993 | 1.032 | 1.167 |

Five of seven tested adjacent pairs cannot reach the 1.0 mm OD1 clearance under ANY assignment within the round-5 stations, even with mutually incompatible per-pair optima. Cause: the inter-strand offset vector rotates from the fan4 spacing direction to the Main row direction (−0.625,−1.083,0), which is nearly anti-parallel to the approach travel direction, collapsing the perpendicular distance. A staggered axis-join tail was also screened analytically and rejected on length (join points at s≈16.6 mm push the longest finished conductor past 200 mm). **Zero strand crossings is therefore not achievable by assignment inside the frozen round-5 fan/approach envelope.** What would have to change is a station change, outside this round's mandate: relocate the pre-approach station onto the connector-axis lines (needs shell/bay space north-east of Main beyond the current fan envelope), or widen the reserve neck channel so the pack can travel as a single row (a fixed-body change), or change the interconnect concept.

## Stage 2 — sweep and eight-gate audit, both pitches

The candidate (routes-round8.json; pack/fan assignments in its provenance) was assembled on the frozen operands and audited with the unchanged pipeline. `routes.py` now holds the round-8 module, following the round-7 pattern (round-7 module preserved as routes_round7.py); metrology keeps the round-5 fan construction (`fixed_parts=None`).

| Gate | 17 mm | 16 mm |
|---|---|---|
| 1 Exhaustive fitted collision | **FAIL** — 94 contacts: 92 strand–strand + 2 POM residuals; 0 Boolean errors; 66,795 pairs, 1,417 exact candidates (17 mm) | **FAIL** — 94 contacts: 92 strand–strand + 2 POM residuals; 0 Boolean errors |
| 2 Finished ≤200 mm | PASS — longest 195.205 mm, margin 4.795 mm (tails 3.90 + 3.40) | PASS — longest 195.205 mm, margin 4.795 mm |
| 3 Accessible ~30.20 mm service | **FAIL by fitted collisions only** — motion clear; service sweep 0 hits on both sides | **FAIL by fitted collisions only** — motion clear; service sweep 0 hits on both sides |
| 4 Fly 170.000 / R5 / gap 0.30 | PASS — 0 fitted contacts | PASS — 0 fitted contacts |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps | PASS — certified minimum after 0.50 allowance 0.577 mm; physical Junana skirt test OPEN | PASS — physical Junana skirt test OPEN |
| 7 Manufacturing 19/19 + envelopes | PASS — required skin PASS; stack/palm/floor invariants PASS | PASS |
| 8 Fitted preview STEP | PASS — 366/366 constituents reloaded | PASS |

Collision counts by category, rounds 3–6 vs 8 (unexpected contacts, exhaustive fitted audit):

| Round | Strand–strand | Other | Longest finished | Note |
|---|---:|---:|---:|---|
| 3 | 52 | 28 fixed | — | built on the reversed right-Wing pin map (invalid premise) |
| 4 | part of 141 total | — | — | corrected pin map, fan topology regressed |
| 5 | 163 | 2 POM residuals | 196.87 PASS | frozen base of rounds 7–8 |
| 6 | part of 206 total | — | 204.51 FAIL | permutation applied at terminations only |
| **8** | **92** | **2 POM residuals** | **195.21 PASS** | assignment by physical traversal order; −44% strand contacts vs round 5, best length margin of any full-audit round |

## Verdict

Round 8 is the strongest routing candidate so far — strand contacts cut from 163 to 92, length margin improved to 4.795 mm, service motion and all non-collision gates pass at both pitches, and the fan-stage order is nearly the endpoint order — but gate 1 still fails, so the candidate is **not adoptable** and no service certification is granted. The remaining contacts are concentrated where the analysis says they must be: the Main approach tail, whose station geometry caps five adjacent pairs below OD1 clearance for any assignment. Further assignment search inside the frozen round-5 envelopes is not expected to close gate 1; the next step is a PO decision on changing the approach/fan stations (envelope change), the neck channel (fixed-body change), or the interconnect concept.


# Issue #248 Phase B — Round 7

**PROVISIONAL on plateau Z24.65 / q=1.50. NOT RELEASED.**

## Stage 0 — before conductor solids

Copilot’s full second opinion was read first and copied to [sources/second-opinion-copilot-round7.md](sources/second-opinion-copilot-round7.md). Current Issue comments are preserved in sources/issue248-round7.json. Its suggestions are hypotheses, not measured CAD results. BASE is exclusively frozen round5/. Frozen round6/ and round6-sha256.json preserve the preceding full package; rounds 3–5 are untouched. All round-5 BRep operands were recovered by exact serialized hashes into runtime/round7/frozen-operands; no STEP recovery or fixed-body repair is needed.

### 1. Native maps and centreline inversion analysis

Both native J2/J3 rows have increasing pin number in local u. Their assembly poses differ: the global Main row vector per pin is (−0.625,+1.082532,0) on the left and (−0.625,−1.082532,0) on the right. Wing global X also decreases with pin on BOTH sides. Thus global-X endpoint permutation is the identity (0 inversions), not reversal (91). Substituting Main local u for assembly X produces the advisor’s erroneous reversal conclusion. Main exit tangents are mirrored; projecting onto the endpoint lateral normals (+0.5,−0.866025,0) left / (+0.5,+0.866025,0) right gives the same endpoint order as the Wing normal (+1,0,0). This does not prove that an arbitrary intervening 3D route needs no frame rotation: the route’s transported frame must be checked.

The declared stage ranks below use increasing assembly X, ties within 1e−8 mm resolved by Z then cavity. Tied X groups and every coordinate are disclosed in stage0-round7.json. The bundle has multiple Z rows: a projected inversion is NOT itself proof of a physical collision. The reserve is a travel-direction reversal: its local lateral normal changes sign. Do not add its projected inversions to an axial-twist budget. The actual round-5 traversal has its rise AFTER the reserve, contrary to the upstream-rise assumption in the advice.

| Stage in traversal order | Left order | Δ inversions | Right order | Δ inversions |
|---|---|---:|---|---:|
| outlet | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 |
| corridor | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 0 |
| reserve_in | 4,11,7,14,3,10,6,13,2,9,5,12,1,8 | 40 | 14,7,10,3,13,6,9,2,12,5,8,1,11,4 | 33 |
| reserve_out | 1,8,5,12,2,9,6,13,3,10,7,14,4,11 | 84 | 11,4,8,1,12,5,9,2,13,6,10,3,14,7 | 84 |
| rise_base | 5,10,1,6,11,2,7,12,3,8,13,4,9,14 | 37 | 1,11,6,2,12,7,3,13,8,4,14,9,5,10 | 40 |
| rise_top | 5,10,6,1,11,7,2,12,8,3,13,9,4,14 | 4 | 1,6,11,2,7,12,3,8,13,4,9,14,5,10 | 4 |
| fan | 5,10,6,1,11,7,2,12,8,3,13,9,4,14 | 0 | 1,6,11,2,7,12,3,8,13,4,9,14,5,10 | 0 |
| Main_row | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 57 | 14,13,12,11,10,9,8,7,6,5,4,3,2,1 | 61 |

The independent 1001-point-per-strand baseline centreline screen finds 85 same-side pairs below OD1 on each side. It is a cheap screen, not the exact contact count: frozen round-5 exact audit reports 163 strand pairs total. Contact witnesses in stage0-round7.json locate them along the actual paths. Native endpoints remain bound to immutable pinmap-round4.json / round5/pinmap-round5.json.

### 2. Fixed-body twist envelope

stage0-envelope-17.json and stage0-envelope-16.json contain exact distances from existing fixed solids to 36 zero-thickness circular cross-sections per pitch. No new solid is generated for this screen. Full 14-wide diameter14.65 mm fails all 18 tested sections in both pitches. Half-width diameter7.30 mm clears 10/18 sections: six lie in the existing POST-reserve rise and four at X±5/Y−22 or−12/Z5.8. These are necessary cross-section clearances only; the best tempting upstream station has only 0.15 mm distance to the fixed tray floor. At the actual low reserve leg X±10.85 all tested half-ribbon sections are blocked by Wing/tray geometry. The X±5/Y−7 sections are tray-blocked. The full-station interval, inlet approaches, two half-ribbon coexistence, and service boundaries must be checked; cross-section PASS is not an envelope PASS.

### 3. Analytic lengths and curvature

Unchanged sourced tails are Wing3.90 + Main3.40 =7.30 mm. For a constant-rate half-turn at radius r and axial run L, length is sqrt(L²+(πr)²) and curvature radius is (r²+(L/π)²)/r. Entrance/exit angular-rate blending adds constraints. At r6.825/L20 the edge-wire excess is 9.32 mm, refuting the quoted ≈0.5 mm. Adding a full-width helix to equal-length round-5 axial runs exceeds 200 mm at every tested L12.727–30 (longest201.01–206.34 mm), even before blends. This is a screen of this replacement scheme, not a lower bound on all possible reroutes. The half-width replacement screen is length-plausible (197.05–197.53 mm); it does not include the 7+7 group exchange.

Two independent 7-wire flips give [7…1,14…8], not [14…1]; 49 cross-group inversions remain. Therefore the proposed two half-ribbons require an additional group-exchange construction or a jointly rotating packed section. A pure helix also has non-axial endpoint tangents unless its angular rate is blended to zero.

A 14-radius coplanar nested U has13×1.05=13.65 mm spread and π×13.65=42.882740 mm outer-minus-inner length. This verifies the advisor’s differential, but DOES NOT establish length impossibility: longer base wires can take shorter radii and a full path must be evaluated. Z-spread is tested as the requested fallback, retaining the existing fourteen low-pack reserve lanes and all fixed case/channel geometry. A true transported ribbon through the return hairpin needs a frame alignment of about50°, not an assumed180°. The first centreline prototype (central return R7.15) was rejected before solids after sampled edge curvature R4.795; its source/log remain in runtime. The next prototype enlarges only routing curvature, not any fixed body. Length and R≥5 screens remain binding.

Stage-0 verdict: **(a) pure-reversal claim REFUTED in verified assembly endpoint frames; (b) zero-contact claim UNPROVEN and not implied by a reversal count; (c) radial length differential VERIFIED, universal length-unaffordability NOT PROVED.** No strand solids may be swept until a complete candidate passes analytic length and bend screening.

### Complete candidate screen before solids

The stacked low/high two-row crossing prototype was rejected without sweeping: longest finished200.260842 mm; released return fillets have negative tangent slack on all14 strands (−1.250446…−0.077952 mm). It also retains60 sampled close pairs at the Main fan. The radius certificate exposed a separate sampling hazard in the R8.2 return candidate: pin2’s continuous lower bound4.973302 mm invalidated its sampled R5.086848 result. That candidate was rejected. See sources/round7/rejected-r8p2-curve-certificates.json.

The selected **diagnostic** fallback uses R8.5 central return bends and the original14 reserve lanes, with Z spread before inlet compression and an ordered transported return. It has a complete finished upper bound186.056270 mm (13.943730 mm margin), including unchanged7.30 mm tails. The14 non-rational spline curves are certified continuously by converting to Bezier patches and bounding |v×a| / |v|³ using Bernstein control-vector convex hulls, with adaptive subdivision. Lowest certified spline radius5.276689 mm; the overall minimum is the unchanged inner reserve radius5.035 mm. Independent per-patch quadrature agrees with kernel spline lengths within2.1e−13 mm. These tests precede ALL new conductor solids. See curve-certificates-round7.json and curve_certificate_round7.py.

This fallback is not asserted contact-free: the cheap screen still has79 close same-side pairs, notably where the inlet diagonal meets the low return and at the Main fan. It is carried through the required full audit to expose actual fixed-body, strand and service blockers. No dedicated180° twist was installed: the verified endpoint frames do not require the advisor’s asserted permutation, the full-width station fails its envelope, no complete upstream7+7 station was qualified, and the post-reserve rise cannot silently be called upstream. The fallback is explicitly a nested horizontal U with existing Z-spread, followed by an ordered return hairpin; it is a failed routing trial unless the independent gates establish otherwise. It does not fulfil an exactly-one-twist construction.

## Build and complete eight-gate audit

IN PROGRESS. No new routing PASS or reuse of round-6 geometry is claimed. POM-left-H3 / POM-right-H1 remain unauthorized required-skin blockers, with no exception. Prior complete results follow unchanged.

---

# Issue #248 Phase B — Round 6

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

## Round 6 results

Assignment correction inside the frozen round-3 final framework. Failed gates remain binding; no production release or exception is claimed.

| Gate | 17 mm | 16 mm |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Finished conductors ≤200 mm | FAIL | FAIL |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | PASS | PASS |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | PASS | PASS |
| 7 Print envelopes and manufacturing data | PASS | PASS |
| 8 Fitted preview STEP | PASS | PASS |

### Frozen base, physical assignment and exact deviation scope

The latest PO direction was read with `gh issue view 248 --comments` and is preserved in sources/issue248-round6.json. The entire round-5 package and report are frozen in round5/ with round5-sha256.json; all earlier evidence remains unchanged. Checkpoint 84be3a5 froze round 5 before work began.

BASE is the FINAL round-3 assembly whose 17 mm audit has 80 contacts and whose longest finished conductor is 198.400068 mm. Its stored/released turn-tangent datums are Y10.0/Y−5.1, reserve centre X±17.40, and travel 15.10 mm (connected reserve 30.20 mm). The tuning-round Y17.1/Y2.0 datums are not used. No reserve, lane pack, pack spacing/height, shell, strip, retainer (±8,−30), hardware, tray channel or tray seating relief is redesigned.

The frozen round-3 strand geometry DOES exist as parametric paths in round3/routes-round3.json and round3/routes.py, consistent with the frozen measurements. No paths are fitted from solids. Each corrected conductor retains the entire path belonging to its physical Wing outlet, including every inlet waypoint, low-pack radius/height, reserve turn and return-fan waypoint through the last interior vertex. Only the final two Main approach waypoints are taken from the frozen path that terminates at the corrected same-numbered Main cavity. right Wing pin1 is X35.125, pin14 X18.875; left pin1 is X−18.875. Native KiCad pads/nets independently verify all 28 endpoints in pinmap-round6.json against immutable pinmap-round4.json / pinmap-round5.json. Conductor names now denote corrected physical cavity numbers. Named-pair deltas therefore include renumbering; assignment-geometry-comparison.json supplies the physical-strand correspondence, so a renamed pair alone is not a cleared physical contact.

The complete deviation register is assignment-deviations-round6.json plus per-pitch assignment-geometry-comparison.json (including all 28 exact length changes), naming all 28 conductors (right pin and its mirrored left pin), original physical lane, old/new Main approach coordinates, unchanged waypoint indices and affected geometry. For each strand: after vertices5/6 change; edges4→5 and5→6 and R5 fillets at vertices4/5 regenerate; the tangent trim at unchanged vertex4 on edge3→4 consequently changes. Vertex4 itself does not move. All indices are zero-based. Entire inlet/reserve geometry and preceding fan vertices remain exactly unchanged. routes-round6.json is checked against the frozen arrays by verify_round6_framework.py; there is no route optimizer or extra clearance cut.

Frozen solid recovery uses content-addressed byte-identical BReps for 338 fixed constituents, including boards, plates, Fly, strips, retainers and hardware. Only central shell and two tray serialized BReps were absent from scratch; these three operands are read from their immutable final round-3 manufacturing STEP exports without healing. Their representation roundtrip volume/bounds changes are recorded individually in frozen-framework-recovery.json. This is solid recovery, not path reconstruction or a new shape design. The first partial 17 mm attempt exposed whole-assembly reserialization by the legacy boss-repair writer; it was stopped after a bounded chunk, retained under .issue248-runtime/round6/rejected-operand-reserialization/, and replaced with a writer that changes only tray-left. Its partial pair results are not reused. Independent final scope checks reject any change beyond the strand edits and carried tray-left repair.

CARRIED manufacturing-data repair: fresh analytic OD7 tray-left splice boss at X0/Y55 with original Ø1.7 pilot; explicit X−4…4/Y51…59/Z1.8…5.8 cleanup, native floor patch restored through Z1.6…2.0. splice-boss-rebuild.json records exact before/after volume and floor preservation. No other tray relief is cut, including no continuous-service or corrected-route channel enlargement. Required skin, source floor, full E supports, palm band and stack checks remain unchanged.

The two-waypoint termination correction exceeds the finished-length limit. The >200 mm route is preserved for an exact audit and a failed gate; no routing shortening, tail reduction, reserve shift or waiver is substituted. Binding thresholds remain deck Z13.55, plateau Z24.65/q1.50 provisional, seam ownership and 2.00 mm skin, byte-unchanged board/plate design inputs, GH/Fly blisters, M2×10, fourteen OD1/R≥5 strands per side, finished ≤200 mm including unchanged 3.90/3.40 mm tails, Fly 170/R5/0.30 gap, and 1e−6 mm³ collision threshold.

### Round 6 — 17 mm

Exhaustive audit: 366 physical constituents, 66795 unordered pairs; 65277 AABB exclusions, 132 explicit own mates, 1386 exact Commons, 0 Boolean errors. Every pair is re-enumerated. Exact Common results replay only for byte-identical frozen operands with identical names/indices; all changed-operand candidates recompute in bounded processes (80 new Commons per process). audit-E-restoration-reuse.json is independently checked; all gates bind to current assembly-index.json.

| Collision category | Round 3 | Round 4 | Round 5 | Round 6 |
|---|---:|---:|---:|---:|
| E screws / conductors | 0 | 2 | 0 | 0 |
| Fly-170mm / conductors | 0 | 4 | 0 | 0 |
| Fly-170mm / trays | 0 | 1 | 0 | 0 |
| POM-left-H3 / shell-central | 1 | 1 | 1 | 1 |
| POM-left-H4 / conductors | 0 | 1 | 0 | 0 |
| POM-right-H1 / shell-central | 1 | 1 | 1 | 1 |
| POM-right-H2 / conductors | 0 | 1 | 0 | 0 |
| Wing underside bounds / conductors | 0 | 12 | 0 | 0 |
| aluminium plates / conductors | 10 | 22 | 0 | 10 |
| conductors / conductors | 52 | 23 | 163 | 174 |
| conductors / joint-screw-1-12_0 | 0 | 1 | 0 | 0 |
| conductors / main | 2 | 0 | 0 | 2 |
| conductors / shell-central | 0 | 16 | 0 | 0 |
| conductors / strip-left | 0 | 9 | 0 | 0 |
| conductors / strip-right | 0 | 9 | 0 | 0 |
| conductors / switch-envelope-L_R0_C5 | 0 | 1 | 0 | 0 |
| conductors / switch-envelope-R_R0_C5 | 0 | 1 | 0 | 0 |
| conductors / trays | 0 | 10 | 0 | 4 |
| conductors / wing_left | 7 | 12 | 0 | 7 |
| conductors / wing_right | 7 | 12 | 0 | 7 |
| strip-left / trays | 0 | 1 | 0 | 0 |
| strip-right / trays | 0 | 1 | 0 | 0 |
| **Total** | **80** | **141** | **165** | **206** |

Named pairs, exact volumes and bounds: [17mm/audit.json](17mm/audit.json), collision-map.json and round6-comparison.json.

| Side | Longest strand | Routed mm | Finished mm | Margin to 200 mm | Connected reserve mm | Min bend mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 10 | 197.210171 | 204.510171 | -4.510171 | 30.200000 | 5.000000 |
| right | 05 | 197.210171 | 204.510171 | -4.510171 | 30.200000 | 5.000000 |

All over-limit strands: left-10: 204.510171 mm, left-14: 200.496278 mm, right-01: 200.496278 mm, right-05: 204.510171 mm. Finished lengths include unchanged tail-source.json tails. All R5 stored/released tangent slack is measured in length-fly.json; the dressed 164.8 mm figure remains reference only.

Fly: 170.000000000 mm, R5, roof gap 0.300000 mm; 0 fitted contacts. USB continuous 30 mm insertion: PASS. Certified cap envelope: PASS; physical q/skirt/full-press remains OPEN.

Service motion with Main/removable caps removed and Wing hardware fitted:

- left: 8 contacts (4 tray, 4 own fixed fan), 0 Boolean errors; 30.200000 mm release.
  - strand 01 / tray-left: 0.000292079 mm³.
  - strand 05 / tray-left: 0.000328737 mm³.
  - strand 06 / tray-left: 0.006182203 mm³.
  - strand 13 / tray-left: 0.018565946 mm³.
  - strand 08 / Wire-left-08-fixed-upper-fan: 0.647478711 mm³.
  - strand 09 / Wire-left-08-fixed-upper-fan: 1.893580431 mm³.
  - strand 10 / Wire-left-08-fixed-upper-fan: 0.000010086 mm³.
  - strand 11 / Wire-left-08-fixed-upper-fan: 0.037500277 mm³.
- right: 8 contacts (4 tray, 4 own fixed fan), 0 Boolean errors; 30.200000 mm release.
  - strand 02 / tray-right: 1.447755172 mm³.
  - strand 09 / tray-right: 0.474144643 mm³.
  - strand 10 / tray-right: 0.000328737 mm³.
  - strand 14 / tray-right: 0.000292079 mm³.
  - strand 04 / Wire-right-07-fixed-upper-fan: 0.037500277 mm³.
  - strand 05 / Wire-right-07-fixed-upper-fan: 0.000010086 mm³.
  - strand 06 / Wire-right-07-fixed-upper-fan: 1.893580448 mm³.
  - strand 07 / Wire-right-07-fixed-upper-fan: 0.647478672 mm³.

Geometric service motion: **FAIL**. Accessible service: **FAIL**. All intermediate translations plus 0.020 mm allowance are checked against fixed bodies and own fixed fans. Round 3 broadly excluded its own harness; the stronger carried round-4/5 check also audits fixed inlet/upper fan pieces, so any additional own-fan contacts are explicitly distinguished from the inherited tray grazes. Inherited strand crossings are independently disqualifying; no assertion of mutually separated round-3 turns is used. Fitted channels are frozen, so inherited motion grazes are retained rather than relieved.

Manufacturing: **PASS**, 19/19 independent STEP/STL reloads; exact edge incidence, degenerates, volume and print envelopes unchanged. Required skin PASS; source floor/stack/palm PASS; full E support/M2×10 PASS; retention probes PASS.

| Part | STEP valid | Solids | Nonmanifold edges | Degenerates | Verdict |
|---|---|---:|---:|---:|---|
| splice-1 | True | 1 | 0 | 0 | PASS |
| splice-2 | True | 1 | 0 | 0 | PASS |
| post-left-R1 | True | 1 | 0 | 0 | PASS |
| post-left-R2 | True | 1 | 0 | 0 | PASS |
| post-left-R3 | True | 1 | 0 | 0 | PASS |
| post-left-R4 | True | 1 | 0 | 0 | PASS |
| post-left-R5 | True | 1 | 0 | 0 | PASS |
| post-left-R6 | True | 1 | 0 | 0 | PASS |
| tray-left | True | 1 | 0 | 0 | PASS |
| post-right-R1 | True | 1 | 0 | 0 | PASS |
| post-right-R2 | True | 1 | 0 | 0 | PASS |
| post-right-R3 | True | 1 | 0 | 0 | PASS |
| post-right-R4 | True | 1 | 0 | 0 | PASS |
| post-right-R5 | True | 1 | 0 | 0 | PASS |
| post-right-R6 | True | 1 | 0 | 0 | PASS |
| tray-right | True | 1 | 0 | 0 | PASS |
| strip-left | True | 1 | 0 | 0 | PASS |
| strip-right | True | 1 | 0 | 0 | PASS |
| shell-central | True | 1 | 0 | 0 | PASS |

Inherited POM residuals remain **unauthorized blockers**:

| Fixed body | Required roof | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770488 |
| POM-right-H1 | low_south | 0.040770024 |

F-015/D-037: the invalid Fly-official-42-instance-42 is accepted only as the inherited source-model defect when its serialized operand hash exactly matches frozen round 3. It is neither healed nor exempted from contacts. All actual contacts remain audited.

Failed gates and blockers:

- **1 Exhaustive fitted collision**: 206 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid design constituents: none; F-015/D-037 preserved source defects: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **2 Finished conductors ≤200 mm**: Longest finished upper bound 204.510171 mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.
- **3 Accessible ~30 mm service**: Motion blocked; fitted collisions additionally prevent accessible certification.

Frozen recovery details:

- tray-left: frozen STEP representation roundtrip volume delta 7.82165443525e-09 mm³; maximum bounds delta 2.13162820728e-14 mm; no healing.
- tray-right: frozen STEP representation roundtrip volume delta -8.75334080774e-07 mm³; maximum bounds delta 4.88498130835e-15 mm; no healing.
- shell-central: frozen STEP representation roundtrip volume delta -7.47604644857e-10 mm³; maximum bounds delta 1.45909950788e-11 mm; no healing.
- carried tray-left analytic boss junction repair: volume change -15.921584297 mm³; required local floor missing 0.000000000 mm³.

### Round 6 — 16 mm

Exhaustive audit: 366 physical constituents, 66795 unordered pairs; 65267 AABB exclusions, 132 explicit own mates, 1396 exact Commons, 0 Boolean errors. Every pair is re-enumerated. Exact Common results replay only for byte-identical frozen operands with identical names/indices; all changed-operand candidates recompute in bounded processes (80 new Commons per process). audit-E-restoration-reuse.json is independently checked; all gates bind to current assembly-index.json.

| Collision category | Round 3 | Round 4 | Round 5 | Round 6 |
|---|---:|---:|---:|---:|
| E screws / conductors | 0 | 2 | 0 | 0 |
| Fly-170mm / conductors | 0 | 4 | 0 | 0 |
| Fly-170mm / trays | 0 | 1 | 0 | 0 |
| POM-left-H3 / shell-central | 1 | 1 | 1 | 1 |
| POM-left-H4 / conductors | 0 | 1 | 0 | 0 |
| POM-right-H1 / shell-central | 1 | 1 | 1 | 1 |
| POM-right-H2 / conductors | 0 | 1 | 0 | 0 |
| Wing underside bounds / conductors | 0 | 12 | 0 | 0 |
| aluminium plates / conductors | 10 | 22 | 0 | 10 |
| conductors / conductors | 52 | 23 | 163 | 174 |
| conductors / joint-screw-1-12_0 | 0 | 1 | 0 | 0 |
| conductors / main | 2 | 0 | 0 | 2 |
| conductors / shell-central | 0 | 16 | 0 | 0 |
| conductors / strip-left | 0 | 9 | 0 | 0 |
| conductors / strip-right | 0 | 9 | 0 | 0 |
| conductors / switch-envelope-L_R0_C5 | 1 | 1 | 0 | 1 |
| conductors / switch-envelope-L_R1_C5 | 2 | 0 | 0 | 2 |
| conductors / switch-envelope-R_R0_C5 | 1 | 1 | 0 | 1 |
| conductors / switch-envelope-R_R1_C5 | 2 | 0 | 0 | 2 |
| conductors / trays | 0 | 10 | 0 | 4 |
| conductors / wing_left | 7 | 12 | 0 | 7 |
| conductors / wing_right | 7 | 12 | 0 | 7 |
| strip-left / trays | 0 | 1 | 0 | 0 |
| strip-right / trays | 0 | 1 | 0 | 0 |
| **Total** | **86** | **141** | **165** | **212** |

Named pairs, exact volumes and bounds: [16mm/audit.json](16mm/audit.json), collision-map.json and round6-comparison.json.

| Side | Longest strand | Routed mm | Finished mm | Margin to 200 mm | Connected reserve mm | Min bend mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 10 | 197.210171 | 204.510171 | -4.510171 | 30.200000 | 5.000000 |
| right | 05 | 197.210171 | 204.510171 | -4.510171 | 30.200000 | 5.000000 |

All over-limit strands: left-10: 204.510171 mm, left-14: 200.496278 mm, right-01: 200.496278 mm, right-05: 204.510171 mm. Finished lengths include unchanged tail-source.json tails. All R5 stored/released tangent slack is measured in length-fly.json; the dressed 164.8 mm figure remains reference only.

Fly: 170.000000000 mm, R5, roof gap 0.300000 mm; 0 fitted contacts. USB continuous 30 mm insertion: PASS. Certified cap envelope: PASS; physical q/skirt/full-press remains OPEN.

Service motion with Main/removable caps removed and Wing hardware fitted:

- left: 8 contacts (4 tray, 4 own fixed fan), 0 Boolean errors; 30.200000 mm release.
  - strand 01 / tray-left: 0.000292079 mm³.
  - strand 05 / tray-left: 0.000328737 mm³.
  - strand 06 / tray-left: 0.006182203 mm³.
  - strand 13 / tray-left: 0.018565946 mm³.
  - strand 08 / Wire-left-08-fixed-upper-fan: 0.647478711 mm³.
  - strand 09 / Wire-left-08-fixed-upper-fan: 1.893580431 mm³.
  - strand 10 / Wire-left-08-fixed-upper-fan: 0.000010086 mm³.
  - strand 11 / Wire-left-08-fixed-upper-fan: 0.037500277 mm³.
- right: 8 contacts (4 tray, 4 own fixed fan), 0 Boolean errors; 30.200000 mm release.
  - strand 02 / tray-right: 1.447755172 mm³.
  - strand 09 / tray-right: 0.474144643 mm³.
  - strand 10 / tray-right: 0.000328737 mm³.
  - strand 14 / tray-right: 0.000292079 mm³.
  - strand 04 / Wire-right-07-fixed-upper-fan: 0.037500277 mm³.
  - strand 05 / Wire-right-07-fixed-upper-fan: 0.000010086 mm³.
  - strand 06 / Wire-right-07-fixed-upper-fan: 1.893580448 mm³.
  - strand 07 / Wire-right-07-fixed-upper-fan: 0.647478672 mm³.

Geometric service motion: **FAIL**. Accessible service: **FAIL**. All intermediate translations plus 0.020 mm allowance are checked against fixed bodies and own fixed fans. Round 3 broadly excluded its own harness; the stronger carried round-4/5 check also audits fixed inlet/upper fan pieces, so any additional own-fan contacts are explicitly distinguished from the inherited tray grazes. Inherited strand crossings are independently disqualifying; no assertion of mutually separated round-3 turns is used. Fitted channels are frozen, so inherited motion grazes are retained rather than relieved.

Manufacturing: **PASS**, 19/19 independent STEP/STL reloads; exact edge incidence, degenerates, volume and print envelopes unchanged. Required skin PASS; source floor/stack/palm PASS; full E support/M2×10 PASS; retention probes PASS.

| Part | STEP valid | Solids | Nonmanifold edges | Degenerates | Verdict |
|---|---|---:|---:|---:|---|
| splice-1 | True | 1 | 0 | 0 | PASS |
| splice-2 | True | 1 | 0 | 0 | PASS |
| post-left-R1 | True | 1 | 0 | 0 | PASS |
| post-left-R2 | True | 1 | 0 | 0 | PASS |
| post-left-R3 | True | 1 | 0 | 0 | PASS |
| post-left-R4 | True | 1 | 0 | 0 | PASS |
| post-left-R5 | True | 1 | 0 | 0 | PASS |
| post-left-R6 | True | 1 | 0 | 0 | PASS |
| tray-left | True | 1 | 0 | 0 | PASS |
| post-right-R1 | True | 1 | 0 | 0 | PASS |
| post-right-R2 | True | 1 | 0 | 0 | PASS |
| post-right-R3 | True | 1 | 0 | 0 | PASS |
| post-right-R4 | True | 1 | 0 | 0 | PASS |
| post-right-R5 | True | 1 | 0 | 0 | PASS |
| post-right-R6 | True | 1 | 0 | 0 | PASS |
| tray-right | True | 1 | 0 | 0 | PASS |
| strip-left | True | 1 | 0 | 0 | PASS |
| strip-right | True | 1 | 0 | 0 | PASS |
| shell-central | True | 1 | 0 | 0 | PASS |

Inherited POM residuals remain **unauthorized blockers**:

| Fixed body | Required roof | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770468 |
| POM-right-H1 | low_south | 0.040770032 |

F-015/D-037: the invalid Fly-official-42-instance-42 is accepted only as the inherited source-model defect when its serialized operand hash exactly matches frozen round 3. It is neither healed nor exempted from contacts. All actual contacts remain audited.

Failed gates and blockers:

- **1 Exhaustive fitted collision**: 212 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid design constituents: none; F-015/D-037 preserved source defects: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **2 Finished conductors ≤200 mm**: Longest finished upper bound 204.510171 mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.
- **3 Accessible ~30 mm service**: Motion blocked; fitted collisions additionally prevent accessible certification.

Frozen recovery details:

- tray-left: frozen STEP representation roundtrip volume delta 7.07223080099e-09 mm³; maximum bounds delta 1.06581410364e-14 mm; no healing.
- tray-right: frozen STEP representation roundtrip volume delta -7.56204826757e-07 mm³; maximum bounds delta 1.7763568394e-15 mm; no healing.
- shell-central: frozen STEP representation roundtrip volume delta -2.21552909352e-09 mm³; maximum bounds delta 1.45981005062e-11 mm; no healing.
- carried tray-left analytic boss junction repair: volume change -15.921584291 mm³; required local floor missing 0.000000000 mm³.

## Round 6 reproduction and integrity

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` with the retained CAD environment and runtime source BRep caches. Content-addressed recovery is checked against the frozen index before any substitution. Each pitch is sequential; exact all-pair work is bounded at 80 new operations and service motion runs per side. All eight gates, independent STEP/STL reloads, contact witnesses, seam/material/retention checks and final package verifier rerun. verify_round6_framework.py enforces frozen arrays and fixed-operand scope; verify_package.py additionally checks all five prior frozen evidence sets, native endpoint binding, current hashes, complete pair arithmetic and per-gate binding. Scratch stays under .issue248-runtime; checkpoints are committed through .issue248-runtime/git. No silent relaxation or physical release.

---

# Issue #248 Phase B — Round 5

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

## Round 5 results

The corrected-map reconstruction remains a failed routing candidate. All contacts and current blockers are retained below; no production release is claimed.

| Gate | 17 mm | 16 mm |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Finished conductors ≤200 mm | PASS | PASS |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | PASS | PASS |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | PASS | PASS |
| 7 Print envelopes and manufacturing data | PASS | PASS |
| 8 Fitted preview STEP | PASS | PASS |

### Reconstruction and physical correspondence

PO direction was reread with `gh issue view 248 --comments`; the snapshot is in sources/issue248-round5.json. Round 4 evidence, route inputs, build sources and both manufacturing packages are frozen in [round4/](round4/REPORT.md) with round4-sha256.json; all earlier frozen evidence is retained.

The preserved evidence contains two different reserve datums: tuning-round uses stored/released Y17.1/Y2.0, while the final round-3 assembly uses Y10.0/Y−5.1 and a 198.400068 mm maximum finished conductor. This reconstruction follows the explicit round-5 Y17.1/Y2.0 instruction. These are the original tuning datum names: the horizontal turn tangent lies 6.55 mm north of the datum and the crown depends on each concentric radius. No prior length or clearance verdict is copied.

derive_routes_round5.py reconstructs the separated outlet lanes through the Wing north corridor, low fan into the neck and horizontal concentric R≥5 reserve. Every strand is reassigned using the corrected native correspondence: right Wing pin1 X35.125, pin14 X18.875, with each Wing cavity connected to the same numbered Main cavity. The reserve centre X17.40 is re-derived as the midpoint of the frozen round-3 inlet/return turn endpoints. The low pack follows physical Wing lane order and the upper return fan follows corrected Main cavity order. Its staggered rows use Z9.59/10.50/11.41 and 1.05 mm lateral pitch; the fan plane has nominal 0.14 mm board clearance and 0.14 mm plate clearance for OD1. Actual transition contacts still require the exact audit. A higher fan candidate was rejected after exact plate contacts, and its partial audit is retained under .issue248-runtime/round5/. A subsequent X13.55 tuning-centre candidate completed a 202-contact fitted audit and failed left service with fourteen fixed-support contacts; it was rejected after comparison with the final round-3 X17.40 centre. Its full fitted audit, left motion evidence and source geometry inputs remain in .issue248-runtime/round5/rejected-tuning-centre/ and Git checkpoints. The current result below uses the reconstructed round-3 centre and a fresh complete audit. pinmap-round4.json remains immutable; verify_pinmap.py independently parses native pad coordinates/nets before any route sweeps and binds all 28 endpoints to routes-round5.json through pinmap-round5.json. Every OD1 conductor is swept again and independently checked against analytic length and volume.

The round-4 tilted reserve and shell-retainer relocation are discarded. The round-3 unrelieved OD6 floor-rooted pillars, inserts, screws, capture tabs and retainer positions (±8,−30) are restored. The stronger round-4 load-path and insert-fit probes are retained as checks. Round-3 tray seating relief is rebuilt from the actual shell. Conservative tray channels include fitted route projections and the entire continuous horizontal-turn translation, buffered 0.87 mm above Z2; the source floor, E support/root, stack and palm checks remain binding. No round-4 shell-rib routing cuts are applied.

The tray-left splice boss remains a fresh analytic OD7 boss with the original Ø1.7 pilot. Round 5 replaces the boss/floor junction in the explicit X−4…4/Y51…59/Z1.8…5.8 mm cleanup box, restoring the original floor patch from Z1.6 through Z2 before recutting the pilot. Material outside the fresh OD7 boss above Z2 in that local box is removed and its measured volume change is recorded in splice-boss-rebuild.json. This removes the Z2/Z2.000001 boundary implicated in the round-4 17 mm STL failure. The final floor and mesh verdicts are measured below; there is no mesh welding or incidence tolerance change.

Binding inputs remain deck Z13.55, provisional plateau Z24.65/q1.50, shell ownership stopping at aluminium plate boundaries, 2.00 mm normal skin, byte-unchanged boards/aluminium manufacturing inputs, GH ceiling/top Z13.20/15.20, Fly Z13.25/15.25, M2×10, fourteen OD1 strands per side, R≥5, ≤200 mm finished including tail-source.json tails, connected reserve 30.20 mm, Fly 170/R5/0.30 mm roof gap and continuous USB/service checks. The 1e−6 mm³ contact threshold and all manufacturing checks are unchanged.

### Round 5 — 17 mm

Exhaustive audit: 366 constituents, 66795 unordered pairs; 65240 AABB exclusions, 132 explicit own mates, 1423 exact Commons, 0 Boolean errors. Every gate binds to the current assembly-index.json; bounded audit processes checkpoint at 80 new exact operations.

| Collision category | Round 3 | Round 4 | Round 5 |
|---|---:|---:|---:|
| E screws / conductors | 0 | 2 | 0 |
| Fly-170mm / conductors | 0 | 4 | 0 |
| Fly-170mm / trays | 0 | 1 | 0 |
| POM-left-H3 / shell-central | 1 | 1 | 1 |
| POM-left-H4 / conductors | 0 | 1 | 0 |
| POM-right-H1 / shell-central | 1 | 1 | 1 |
| POM-right-H2 / conductors | 0 | 1 | 0 |
| Wing underside bounds / conductors | 0 | 12 | 0 |
| aluminium plates / conductors | 10 | 22 | 0 |
| conductors / conductors | 52 | 23 | 163 |
| conductors / joint-screw-1-12_0 | 0 | 1 | 0 |
| conductors / main | 2 | 0 | 0 |
| conductors / shell-central | 0 | 16 | 0 |
| conductors / strip-left | 0 | 9 | 0 |
| conductors / strip-right | 0 | 9 | 0 |
| conductors / switch-envelope-L_R0_C5 | 0 | 1 | 0 |
| conductors / switch-envelope-R_R0_C5 | 0 | 1 | 0 |
| conductors / trays | 0 | 10 | 0 |
| conductors / wing_left | 7 | 12 | 0 |
| conductors / wing_right | 7 | 12 | 0 |
| strip-left / trays | 0 | 1 | 0 |
| strip-right / trays | 0 | 1 | 0 |
| **Total** | **80** | **141** | **165** |

Full named pairs, exact volumes and bounds are in [17mm/audit.json](17mm/audit.json) and collision-map.json; round5-comparison.json binds the category counts and cleared/new named pairs to both frozen baseline audits.

| Side | Routed max mm | Finished max mm | Margin to 200 mm | Connected reserve mm | Minimum bend mm |
|---|---:|---:|---:|---:|---:|
| left | 189.569042 | 196.869042 | 3.130958 | 30.200000 | 5.000000 |
| right | 189.569042 | 196.869042 | 3.130958 | 30.200000 | 5.000000 |

Finished lengths include the unchanged 3.90 mm Wing and 3.40 mm Main bounds from tail-source.json. The 164.8 mm dressed value remains reference only.

Fly: 170.000000000 mm, R5, roof gap 0.300000 mm; 0 fitted contacts. USB continuous 30 mm insertion: PASS. Certified cap envelope: PASS; physical q/skirt/full-press remains OPEN.

Continuous service motion, with Main and removable shell caps removed and Wing hardware fitted:

- left: 0 contacts (0 tray, 0 own fixed fan), 0 Boolean errors; 30.200000 mm connected release.
- right: 0 contacts (0 tray, 0 own fixed fan), 0 Boolean errors; 30.200000 mm connected release.

Service geometric motion: **PASS**. Accessible service: **FAIL**. Full motion contacts are in service.json; fitted crossings remain independently disqualifying. The envelope includes all intermediate translations plus 0.020 mm allowance. Moving turns are also checked against fixed own-harness fan pieces.

Retention exact probes:

- left: PASS; missing vertical load-path volume 0.000000000 mm³, insert fit 7.539822369/7.539822369 mm³, pillar/shell Common 0.000000000 mm³.
- right: PASS; missing vertical load-path volume 0.000000000 mm³, insert fit 7.539822369/7.539822369 mm³, pillar/shell Common 0.000000000 mm³.

Manufacturing verdict: **PASS**, 19/19 independent STEP/STL reloads. Required skin PASS; source floor, stack and palm PASS; full E support and M2×10 engagement PASS.

| Part | STEP valid | Solids | Nonmanifold STL edges | Degenerate triangles | Verdict |
|---|---|---:|---:|---:|---|
| splice-1 | True | 1 | 0 | 0 | PASS |
| splice-2 | True | 1 | 0 | 0 | PASS |
| post-left-R1 | True | 1 | 0 | 0 | PASS |
| post-left-R2 | True | 1 | 0 | 0 | PASS |
| post-left-R3 | True | 1 | 0 | 0 | PASS |
| post-left-R4 | True | 1 | 0 | 0 | PASS |
| post-left-R5 | True | 1 | 0 | 0 | PASS |
| post-left-R6 | True | 1 | 0 | 0 | PASS |
| tray-left | True | 1 | 0 | 0 | PASS |
| post-right-R1 | True | 1 | 0 | 0 | PASS |
| post-right-R2 | True | 1 | 0 | 0 | PASS |
| post-right-R3 | True | 1 | 0 | 0 | PASS |
| post-right-R4 | True | 1 | 0 | 0 | PASS |
| post-right-R5 | True | 1 | 0 | 0 | PASS |
| post-right-R6 | True | 1 | 0 | 0 | PASS |
| tray-right | True | 1 | 0 | 0 | PASS |
| strip-left | True | 1 | 0 | 0 | PASS |
| strip-right | True | 1 | 0 | 0 | PASS |
| shell-central | True | 1 | 0 | 0 | PASS |

POM required-skin residuals remain **unauthorized blockers**, not exceptions:

| Fixed body | Required roof | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770488 |
| POM-right-H1 | low_south | 0.040770024 |

The inherited invalid Fly-official-42-instance-42 remains reported as F-015 / D-037 only when its serialized operand hash exactly matches frozen round 3. Its invalid faces and all real contact pairs remain audited. It is preserved, labelled and never healed or treated as a new design defect.

Failed gates and current blockers:

- **1 Exhaustive fitted collision**: 165 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid design constituents: none; F-015/D-037 preserved source defects: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **3 Accessible ~30 mm service**: Motion clear; fitted collisions additionally prevent accessible certification.

### Round 5 — 16 mm

Exhaustive audit: 366 constituents, 66795 unordered pairs; 65228 AABB exclusions, 132 explicit own mates, 1435 exact Commons, 0 Boolean errors. Every gate binds to the current assembly-index.json; bounded audit processes checkpoint at 80 new exact operations.

| Collision category | Round 3 | Round 4 | Round 5 |
|---|---:|---:|---:|
| E screws / conductors | 0 | 2 | 0 |
| Fly-170mm / conductors | 0 | 4 | 0 |
| Fly-170mm / trays | 0 | 1 | 0 |
| POM-left-H3 / shell-central | 1 | 1 | 1 |
| POM-left-H4 / conductors | 0 | 1 | 0 |
| POM-right-H1 / shell-central | 1 | 1 | 1 |
| POM-right-H2 / conductors | 0 | 1 | 0 |
| Wing underside bounds / conductors | 0 | 12 | 0 |
| aluminium plates / conductors | 10 | 22 | 0 |
| conductors / conductors | 52 | 23 | 163 |
| conductors / joint-screw-1-12_0 | 0 | 1 | 0 |
| conductors / main | 2 | 0 | 0 |
| conductors / shell-central | 0 | 16 | 0 |
| conductors / strip-left | 0 | 9 | 0 |
| conductors / strip-right | 0 | 9 | 0 |
| conductors / switch-envelope-L_R0_C5 | 1 | 1 | 0 |
| conductors / switch-envelope-L_R1_C5 | 2 | 0 | 0 |
| conductors / switch-envelope-R_R0_C5 | 1 | 1 | 0 |
| conductors / switch-envelope-R_R1_C5 | 2 | 0 | 0 |
| conductors / trays | 0 | 10 | 0 |
| conductors / wing_left | 7 | 12 | 0 |
| conductors / wing_right | 7 | 12 | 0 |
| strip-left / trays | 0 | 1 | 0 |
| strip-right / trays | 0 | 1 | 0 |
| **Total** | **86** | **141** | **165** |

Full named pairs, exact volumes and bounds are in [16mm/audit.json](16mm/audit.json) and collision-map.json; round5-comparison.json binds the category counts and cleared/new named pairs to both frozen baseline audits.

| Side | Routed max mm | Finished max mm | Margin to 200 mm | Connected reserve mm | Minimum bend mm |
|---|---:|---:|---:|---:|---:|
| left | 189.569042 | 196.869042 | 3.130958 | 30.200000 | 5.000000 |
| right | 189.569042 | 196.869042 | 3.130958 | 30.200000 | 5.000000 |

Finished lengths include the unchanged 3.90 mm Wing and 3.40 mm Main bounds from tail-source.json. The 164.8 mm dressed value remains reference only.

Fly: 170.000000000 mm, R5, roof gap 0.300000 mm; 0 fitted contacts. USB continuous 30 mm insertion: PASS. Certified cap envelope: PASS; physical q/skirt/full-press remains OPEN.

Continuous service motion, with Main and removable shell caps removed and Wing hardware fitted:

- left: 0 contacts (0 tray, 0 own fixed fan), 0 Boolean errors; 30.200000 mm connected release.
- right: 0 contacts (0 tray, 0 own fixed fan), 0 Boolean errors; 30.200000 mm connected release.

Service geometric motion: **PASS**. Accessible service: **FAIL**. Full motion contacts are in service.json; fitted crossings remain independently disqualifying. The envelope includes all intermediate translations plus 0.020 mm allowance. Moving turns are also checked against fixed own-harness fan pieces.

Retention exact probes:

- left: PASS; missing vertical load-path volume 0.000000000 mm³, insert fit 7.539822369/7.539822369 mm³, pillar/shell Common 0.000000000 mm³.
- right: PASS; missing vertical load-path volume 0.000000000 mm³, insert fit 7.539822369/7.539822369 mm³, pillar/shell Common 0.000000000 mm³.

Manufacturing verdict: **PASS**, 19/19 independent STEP/STL reloads. Required skin PASS; source floor, stack and palm PASS; full E support and M2×10 engagement PASS.

| Part | STEP valid | Solids | Nonmanifold STL edges | Degenerate triangles | Verdict |
|---|---|---:|---:|---:|---|
| splice-1 | True | 1 | 0 | 0 | PASS |
| splice-2 | True | 1 | 0 | 0 | PASS |
| post-left-R1 | True | 1 | 0 | 0 | PASS |
| post-left-R2 | True | 1 | 0 | 0 | PASS |
| post-left-R3 | True | 1 | 0 | 0 | PASS |
| post-left-R4 | True | 1 | 0 | 0 | PASS |
| post-left-R5 | True | 1 | 0 | 0 | PASS |
| post-left-R6 | True | 1 | 0 | 0 | PASS |
| tray-left | True | 1 | 0 | 0 | PASS |
| post-right-R1 | True | 1 | 0 | 0 | PASS |
| post-right-R2 | True | 1 | 0 | 0 | PASS |
| post-right-R3 | True | 1 | 0 | 0 | PASS |
| post-right-R4 | True | 1 | 0 | 0 | PASS |
| post-right-R5 | True | 1 | 0 | 0 | PASS |
| post-right-R6 | True | 1 | 0 | 0 | PASS |
| tray-right | True | 1 | 0 | 0 | PASS |
| strip-left | True | 1 | 0 | 0 | PASS |
| strip-right | True | 1 | 0 | 0 | PASS |
| shell-central | True | 1 | 0 | 0 | PASS |

POM required-skin residuals remain **unauthorized blockers**, not exceptions:

| Fixed body | Required roof | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770468 |
| POM-right-H1 | low_south | 0.040770032 |

The inherited invalid Fly-official-42-instance-42 remains reported as F-015 / D-037 only when its serialized operand hash exactly matches frozen round 3. Its invalid faces and all real contact pairs remain audited. It is preserved, labelled and never healed or treated as a new design defect.

Failed gates and current blockers:

- **1 Exhaustive fitted collision**: 165 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid design constituents: none; F-015/D-037 preserved source defects: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **3 Accessible ~30 mm service**: Motion clear; fitted collisions additionally prevent accessible certification.

## Interrupted round 5 WIP disposition

Continuation started at 041d12a through GIT_DIR=.issue248-runtime/git. Checkpoint 40dc5d2 preserves three byte-identical 16 mm evidence archives: round3-comparison.json and tray-step-diagnostics.json under the old 79e78de44d6e geometry prefix, and inner-wall-passages.json under dd58205322c0. These are historical evidence, not current gate inputs. The interrupted round5_report.py disclosure of the failed routing candidate was retained. No WIP was discarded. The 16 mm exact-pair checkpoint contained 901 results and matched the current assembly-index hash; only missing pairs were computed in bounded chunks. Completed 17 mm metrology/manufacturing evidence was retained only after its geometry binding was checked. Both per-side service records and their aggregate are checked against current geometry by the final package verifier.

## Round 5 reproduction and preservation

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16`. Native endpoint verification runs before CAD route generation. CAD scratch and bounded all-pair checkpoints remain in .issue248-runtime; length, USB and invariants run separately, and continuous service runs in separate processes per side. Every required gate, independent STEP/STL reload, fitted preview, cap/collision witness and full package verifier is rerun. verify_package.py checks all four frozen evidence sets, current input/artifact hashes, native endpoint correspondence and complete pair/gate arithmetic. Checkpoints are committed through .issue248-runtime/git. No physical release is claimed.

---

# Issue #248 Phase B — Round 4

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

## Round 4 results

The structural reserve redesign is audited but **not collision-free**: both pitches retain 141 fitted contacts. Exact blockers are reported below; no all-clear or production release is claimed.

| Gate | 17 mm | 16 mm |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Finished conductors ≤200 mm | PASS | PASS |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | FAIL | FAIL |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | PASS | PASS |
| 7 Print envelopes and manufacturing data | FAIL | PASS |
| 8 Fitted preview STEP | PASS | PASS |

### Fan and height-transition design

The inherited route index paired the right Wing outlet at X18.875 with Main pin1. The #235 placement certificate puts **right Wing pin1 at X35.125 and pin14 at X18.875** (left pin1 X−18.875). Main local pin1 is u=−8.125. D-024 requires 1→1 through 14→14. Thus the inherited geometric index reversed the Wing cavity order; an analysis based on that index alone incorrectly suggests a required full endpoint reversal. Round 4 corrects the physical correspondence and independently verifies all 28 numbered endpoints against native pad coordinates/nets in pinmap-round4.json. No net assignment or PCB is changed. Round 3 additionally used non-monotone low-pack radii/heights and independently rising return legs through the low inlet fan; those caused 52 exact strand contacts. Its 1071 local waypoint variants are not reused.

Round 4 replaces the low horizontal U plus independent return-rise topology with a **north-facing tilted concentric reserve that performs the height transition itself**. The inlet pack is specified in physical low-plane X/Z coordinates at 1.10 mm hexagonal spacing. For two turn centerlines, distance² is at least (Δradius)²+(Δnormal offset)², since their additional angular term is nonnegative; this lower bound is 1.10² mm² for the closest pair, giving 0.10 mm OD1 surface separation throughout their common translation. See fan-structure-proof.json. An orthonormal transform gives each strand a radius and normal-plane offset. Distinct turns on parallel planes have real normal separation; turns in a common plane have radial separation. Their swept conductor clearance is checked exactly along with the fans. The upper fan leaves the reserve above the low inlet instead of threading a rising return through it. This construction separates the reserve/height transition; it does not exempt any fan contact the exact audit still finds.

The two shell retainers move from (±8,−30) to (±4,−10) to release the north service corridor. The OD6 pillars retain OD3.2×4 inserts, shell screws, counterbores and engagement. Their lower-front relief clears the existing splice hardware; an independent exact Ø0.9 vertical material probe tests the rear load path at (x,y−2), in addition to the insert fit and point witnesses. The selected candidate fails this stronger check despite passing point samples; the missing material and incomplete press fit are retained as service/retention blockers. The roof is rebuilt with the two functional holes at the new sites; all remaining required skin, unchanged plate-boundary ownership and retention material are independently checked. This does not alter the low-south footprint, exterior or POM stack. See routing-structure-round4.json, routes-round4.json and per-pitch retention-check.json.

Proposed underside-rib passages are clipped below the independent required-skin volumes and then checked for connectivity. The selected-route cuts would disconnect skin-bearing material on all three 17 mm shell pieces, so those passages are rejected and the original single-solid parts are retained. Per-pitch inner-wall-passages.json records each blocked cut; ensuing wire/shell contacts remain failed. Complete nominal roofs and blister caps remain intact, and the exact skin check still binds. The tray reservation includes the full translated turn projection as well as the fitted route. Its 0.87 mm projected clearance is conservative case-only removal above Z2; original source floors, full E thread-bearing support and shell pillars remain restored and separately audited. No board, plate, cap, strand OD, bend threshold, reserve or tail allowance is reduced.

### Round 4 — 17 mm

Exhaustive audit: 366 physical constituents, 66795 unordered pairs; 64983 AABB exclusions, 160 explicit own mates, 1652 exact Commons, 0 Boolean errors. Threshold remains 1e−6 mm³. Heavy exact passes checkpoint every 80 new operations and restart the CAD process. Every gate is bound to the current assembly-index.json.

| Collision category | Round 3 | Round 4 |
|---|---:|---:|
| E screws / conductors | 0 | 2 |
| Fly-170mm / conductors | 0 | 4 |
| Fly-170mm / trays | 0 | 1 |
| POM-left-H3 / shell-central | 1 | 1 |
| POM-left-H4 / conductors | 0 | 1 |
| POM-right-H1 / shell-central | 1 | 1 |
| POM-right-H2 / conductors | 0 | 1 |
| Wing underside bounds / conductors | 0 | 12 |
| aluminium plates / conductors | 10 | 22 |
| conductors / conductors | 52 | 23 |
| conductors / joint-screw-1-12_0 | 0 | 1 |
| conductors / main | 2 | 0 |
| conductors / shell-central | 0 | 16 |
| conductors / strip-left | 0 | 9 |
| conductors / strip-right | 0 | 9 |
| conductors / switch-envelope-L_R0_C5 | 0 | 1 |
| conductors / switch-envelope-R_R0_C5 | 0 | 1 |
| conductors / trays | 0 | 10 |
| conductors / wing_left | 7 | 12 |
| conductors / wing_right | 7 | 12 |
| strip-left / trays | 0 | 1 |
| strip-right / trays | 0 | 1 |

Total unexpected contacts: **80 → 141**. Complete named pairs, volumes and witnesses are in [17mm/audit.json](17mm/audit.json) and collision-map.json.

| Side | Routed max mm | Finished max including 7.30 mm tails | Connected reserve mm | Min bend mm |
|---|---:|---:|---:|---:|
| left | 192.501349 | 199.801349 | 30.200000 | 5.000000 |
| right | 192.501349 | 199.801349 | 30.200000 | 5.000000 |

Fly: 170.000000000 mm, R5, roof gap 0.300000 mm. USB continuous 30 mm insertion: PASS. Certified caps: PASS; physical q/skirt/full-press remains OPEN.

Continuous service motion (caps and Main removed; Wing hardware fitted):

- left: 24 contacts (0 tray; 24 own fixed fan), 0 errors, 30.200000 mm connected release.
- right: 24 contacts (0 tray; 24 own fixed fan), 0 errors, 30.200000 mm connected release.

Retention probes: left: missing load path 2.569140932 mm³, insert fit 6.883509834/7.539822369 mm³; right: missing load path 2.569140932 mm³, insert fit 6.883509834/7.539822369 mm³

Geometric motion: **FAIL**. Accessible reserve certification: **FAIL**; fitted contacts remain independently binding.

Manufacturing: **18/19** independent STEP/STL reloads pass. Tray-left: STEP valid=True. The X0/Y55 splice boss was rebuilt with fresh analytic OD7 topology and Ø1.7 pilot; 0.001 mm radial cleanup above the Z2 source-floor boundary and 0.20 mm floor overlap are recorded in splice-boss-rebuild.json. Source floor, palm, board/plate stack and E support checks remain binding.

The inherited invalid Fly-official-42-instance-42 is **preserved and labelled as the known F-015 / D-037 source model defect**, contingent on an exact serialized operand hash match against frozen round 3. Its eight invalid faces remain reported. It is not a new design-contact count and is not discarded, healed or used to excuse any real Common. Every actual contact involving that body still fails normally.

**Unresolved required-skin POM blockers (no exception authorized):**

| Fixed body | Roof region | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770488 |
| POM-right-H1 | low_south | 0.040770024 |

Tray-left STL remains blocked by eight exact edge-incidence failures at the rebuilt boss/floor boundary; see [tray-left-diagnostics.json](17mm/tray-left-diagnostics.json) for endpoints and operand hashes. STEP reload itself passes. The cleanup boundary was aligned to Z2; this closes the 16 mm export but does not eliminate the 17 mm mesh residual. No vertex welding, omitted triangles or relaxed mesh test is used.

No low-south footprint/exterior/stack exception or thinner skin is introduced to eliminate these residuals.

Failed gates and their current blockers:

- **1 Exhaustive fitted collision**: 141 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid design constituents: none; F-015/D-037 preserved source defects: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **3 Accessible ~30 mm service**: Motion blocked; fitted collisions additionally prevent accessible certification.
- **4 Connected Fly 170 / R5 / roof gap**: 170.000000000 mm, R5; true roof gap 0.300000 mm; 5 fitted contacts.
- **7 Print envelopes and manufacturing data**: tray-left: STEP valid=True, 1 solids, 8 nonmanifold edges, volume delta 6.38829079e-09 mm³ Required skin PASS; stack/palm/floor invariants PASS.

### Round 4 — 16 mm

Exhaustive audit: 366 physical constituents, 66795 unordered pairs; 64967 AABB exclusions, 160 explicit own mates, 1668 exact Commons, 0 Boolean errors. Threshold remains 1e−6 mm³. Heavy exact passes checkpoint every 80 new operations and restart the CAD process. Every gate is bound to the current assembly-index.json.

| Collision category | Round 3 | Round 4 |
|---|---:|---:|
| E screws / conductors | 0 | 2 |
| Fly-170mm / conductors | 0 | 4 |
| Fly-170mm / trays | 0 | 1 |
| POM-left-H3 / shell-central | 1 | 1 |
| POM-left-H4 / conductors | 0 | 1 |
| POM-right-H1 / shell-central | 1 | 1 |
| POM-right-H2 / conductors | 0 | 1 |
| Wing underside bounds / conductors | 0 | 12 |
| aluminium plates / conductors | 10 | 22 |
| conductors / conductors | 52 | 23 |
| conductors / joint-screw-1-12_0 | 0 | 1 |
| conductors / main | 2 | 0 |
| conductors / shell-central | 0 | 16 |
| conductors / strip-left | 0 | 9 |
| conductors / strip-right | 0 | 9 |
| conductors / switch-envelope-L_R0_C5 | 1 | 1 |
| conductors / switch-envelope-L_R1_C5 | 2 | 0 |
| conductors / switch-envelope-R_R0_C5 | 1 | 1 |
| conductors / switch-envelope-R_R1_C5 | 2 | 0 |
| conductors / trays | 0 | 10 |
| conductors / wing_left | 7 | 12 |
| conductors / wing_right | 7 | 12 |
| strip-left / trays | 0 | 1 |
| strip-right / trays | 0 | 1 |

Total unexpected contacts: **86 → 141**. Complete named pairs, volumes and witnesses are in [16mm/audit.json](16mm/audit.json) and collision-map.json.

| Side | Routed max mm | Finished max including 7.30 mm tails | Connected reserve mm | Min bend mm |
|---|---:|---:|---:|---:|
| left | 192.501349 | 199.801349 | 30.200000 | 5.000000 |
| right | 192.501349 | 199.801349 | 30.200000 | 5.000000 |

Fly: 170.000000000 mm, R5, roof gap 0.300000 mm. USB continuous 30 mm insertion: PASS. Certified caps: PASS; physical q/skirt/full-press remains OPEN.

Continuous service motion (caps and Main removed; Wing hardware fitted):

- left: 24 contacts (0 tray; 24 own fixed fan), 0 errors, 30.200000 mm connected release.
- right: 24 contacts (0 tray; 24 own fixed fan), 0 errors, 30.200000 mm connected release.

Retention probes: left: missing load path 2.569140932 mm³, insert fit 6.883509834/7.539822369 mm³; right: missing load path 2.569140932 mm³, insert fit 6.883509834/7.539822369 mm³

Geometric motion: **FAIL**. Accessible reserve certification: **FAIL**; fitted contacts remain independently binding.

Manufacturing: **19/19** independent STEP/STL reloads pass. Tray-left: STEP valid=True. The X0/Y55 splice boss was rebuilt with fresh analytic OD7 topology and Ø1.7 pilot; 0.001 mm radial cleanup above the Z2 source-floor boundary and 0.20 mm floor overlap are recorded in splice-boss-rebuild.json. Source floor, palm, board/plate stack and E support checks remain binding.

The inherited invalid Fly-official-42-instance-42 is **preserved and labelled as the known F-015 / D-037 source model defect**, contingent on an exact serialized operand hash match against frozen round 3. Its eight invalid faces remain reported. It is not a new design-contact count and is not discarded, healed or used to excuse any real Common. Every actual contact involving that body still fails normally.

**Unresolved required-skin POM blockers (no exception authorized):**

| Fixed body | Roof region | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770468 |
| POM-right-H1 | low_south | 0.040770032 |

No low-south footprint/exterior/stack exception or thinner skin is introduced to eliminate these residuals.

Failed gates and their current blockers:

- **1 Exhaustive fitted collision**: 141 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid design constituents: none; F-015/D-037 preserved source defects: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **3 Accessible ~30 mm service**: Motion blocked; fitted collisions additionally prevent accessible certification.
- **4 Connected Fly 170 / R5 / roof gap**: 170.000000000 mm, R5; true roof gap 0.300000 mm; 5 fitted contacts.

## Interrupted round 4 WIP disposition

The continuation inventoried the alternate Git index and the disconnected-run log before any rebuild. Checkpoint 8e66419 retains the selected final-030 route, its native pin map, the stricter own-fixed-fan service audit, report explanation and independent verifier additions. Candidate screening was not accepted as a clearance verdict. Runtime optimization arrays/logs remain scratch; Python caches are excluded. A full source rebuild exposed route-isolated tray rim fragments; fd187a5 adds explicit mirrored bounds and volume limits for their removal, followed by unchanged floor, palm, skin, E-support and manufacturing gates. No arbitrary largest-solid filter or gate relaxation is used.

## Round 4 reproduction and preservation

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16`. All scratch stays in `.issue248-runtime/`; the all-pair stage restarts at bounded checkpoints and metrology runs length/USB/service/invariants in separate processes. The independent unchanged manufacturing verifier reloads all nineteen STEP/STL sets at both pitches. `verify_package.py` replays current all-pair coverage, acceptance classification, gate arithmetic, source/artifact hashes and all frozen evidence.

The complete prior report and round-3 artifacts are frozen in [round3/](round3/REPORT.md), with round3-sha256.json. First-candidate and tuning evidence remain frozen with their original manifests. Checkpoints are committed through `.issue248-runtime/git`. All physical validation remains provisional; no release is claimed.

---

# Issue #248 Phase B — Round 3 continuation

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

## Round 3 results

The plate-boundary seam rule supersedes the tuning round's shell/plate ownership. The entire preceding report is preserved below and its evidence is frozen in [tuning-round/](tuning-round/REPORT.md); first-candidate evidence is also retained. Current results below supersede earlier current-candidate statements. Restart WIP disposition is recorded in [ROUND3-WIP-INVENTORY.md](ROUND3-WIP-INVENTORY.md), checkpoint cdc2085.

| Gate | 17 mm | 16 mm |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Finished conductors ≤200 mm | PASS | PASS |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | PASS | PASS |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | PASS | PASS |
| 7 Print envelopes and manufacturing data | FAIL | FAIL |
| 8 Fitted preview STEP | PASS | PASS |

**Routing remains unresolved.** The finite local-repair screen examined 1071 admissible waypoint variants with R5, positive stored/released tangent slack, finished length including 7.30 mm tails ≤200 mm, and connected 30.20 mm reserve. The three shortlisted changes were individually tested by exact Common against the 16 mm fitted assembly: Wire-right-04: 8 contacts, Wire-right-08: 6 contacts, Wire-right-09: 9 contacts. All three remain blocked by fixed bodies and strands; the attempts also introduce tray/POM contacts. They are rejected and the frozen fitted round-3 route is retained. Full attempted waypoints, constraint checks and exact contacts are in [route-repair-attempts.json](route-repair-attempts.json). A separated fan/height-transition redesign is still required. This bounded unsuccessful search does not prove a compliant route impossible. No overlap exemption, thinner skin, shortened reserve or length waiver is used.

Deck Z13.55, slope lines, plateau Z24.65, 2.00 mm normal skin, unchanged boards/aluminium, M2×10 E screws, GH/Fly blister dimensions and Ø5.10 south openings remain binding. Tail-source.json supplies 3.40 mm/end plus the 0.50 mm Wing dress lead: 7.30 mm added to every routed conductor. The 164.8 mm value remains a reported reference. Physical Junana skirt/full-press and retention tests remain OPEN.

Tray route relief is an explicit conservative union of the projected conductor paths, buffered 0.87 mm and cut through their common height interval (clamped at Z2). This replaces overlapping per-strand Boolean tools; it may remove additional tray material within that reservation. The actual channel polygon and height are recorded in measurements.json. Initial floor restoration precedes splice remaking; the redundant post-pilot floor fuse is omitted because it produced invalid coincident topology. The final exact Common checks the complete original Z0…2 floor band, excluding only the authorized relocated pilot holes. Source floor, E thread-bearing support material and dedicated shell pillars are restored before the independent material, engagement, palm-band, fitted and print audits. Shell skin and aluminium are not cut by these channels.

### Round 3 — 17 mm

Exhaustive audit: 366 constituents, 66795 unordered pairs; 65281 AABB exclusions, 132 explicit own mates, 1382 exact Commons, 0 Boolean errors. Threshold stays 1e−6 mm³. All gates bind to assembly-index.json; no prior PASS certifies changed operands.

Final tray seating removes 53.262826830 mm³ only from trays north of the protected palm band. The two shell/tray contacts clear to zero Common. Shell, plate, POM and wire operands are byte-identical across that change. The full unordered-pair audit is re-enumerated; 998 exact current-round results are reused only when both serialized operand hashes, names and indices match. Every changed-tray pair is recomputed. The independent package verifier replays that proof; all service/material/export gates rerun on the new index. Seam proof rebinding likewise verifies every unchanged shell/plate operand. See tray-seating-relief.json and audit-E-restoration-reuse.json.

| Collision category | Tuning | Round 3 |
|---|---:|---:|
| E screws / conductors | 6 | 0 |
| E screws / shell-central | 2 | 0 |
| POM-left-H3 / shell-central | 1 | 1 |
| POM-right-H1 / shell-central | 1 | 1 |
| aluminium plates / conductors | 28 | 10 |
| aluminium plates / shell-central | 2 | 0 |
| conductors / conductors | 172 | 52 |
| conductors / main | 0 | 2 |
| conductors / shell-central | 28 | 0 |
| conductors / strip-left | 14 | 0 |
| conductors / strip-right | 14 | 0 |
| conductors / trays | 25 | 0 |
| conductors / wing_left | 0 | 7 |
| conductors / wing_right | 0 | 7 |
| shell-central / trays | 2 | 0 |

| Side | Longest finished mm | Routed mm | Connected reserve mm | Minimum radius mm |
|---|---:|---:|---:|---:|
| left | 198.400068 | 191.100068 | 30.200000 | 5.000000 |
| right | 198.400068 | 191.100068 | 30.200000 | 5.000000 |

Fly: 170.000000000 mm, R5, exact roof gap 0.300000 mm. USB sweep: PASS. Sourced tails and per-wire geometry are in [length-fly.json](17mm/length-fly.json).

**Seam geometry:** shell ownership ends at the full unchanged aluminium blank silhouette, including apertures; no shell is allowed inside plate apertures. Nominal horizontal gap and overlap are both 0 mm. Actual shell/plate Common maximum 0.000000000 mm³; ownership maximum 0.000000000 mm³. Full 2.00 mm normal skin check PASS; maximum missing required material 0.000000000 mm³. Slope vertical skin is 2.090056857 mm.

| Seam region | Length mm | Shell top minus plate top mm |
|---|---:|---|
| plateau | 3.651030 | 11.100000 … 11.100000 |
| slope | 84.475209 | 0.000000 … 11.100000 |
| low_south | 51.492992 | 0.000000 … 0.000000 |
| north_left | 172.333674 | 11.100000 … 11.100000 |
| north_right | 172.333674 | 11.100000 … 11.100000 |

Exact seam lines, trimmed boundary-distance witnesses (explicit [0, upper] intervals at ≤0.000001 mm for nominally coincident boundaries), and removed ownership regions are in [seam.json](17mm/seam.json). The central footprint is the component containing the declared bay datum (0,20); disconnected outer south perimeter regions are explicitly outside ownership, not discarded by volume ranking. No bridge crosses a well. Central shell: **1 solid(s)**. Single solid under the seam rule.


Fixed bodies intersecting the full required 2.00 mm skin (an underside pocket here removes required material):

| Fixed body | Roof region | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770488 |
| POM-right-H1 | low_south | 0.040770024 |

These residual contacts require a further explicit footprint, exterior or fixed-stack change. The seam rule is applied; no skin pocket or additional footprint exception is used to hide them.

Continuous service motion (caps and Main removed, Wing hardware fitted):

- left: 4 contacts, 0 errors; release 30.200000 mm.
- right: 4 contacts, 0 errors; release 30.200000 mm.

The remaining continuous-motion blockers are tray contacts (the fitted route itself has no tray contact); the translating reserve envelope is therefore not clear even after the caps/Main removal procedure:

- left strand 02 / tray-left: 0.018565946 mm³.
- left strand 09 / tray-left: 0.006182203 mm³.
- left strand 10 / tray-left: 0.000328737 mm³.
- left strand 14 / tray-left: 0.000292079 mm³.
- right strand 01 / tray-right: 0.000292079 mm³.
- right strand 05 / tray-right: 0.000328737 mm³.
- right strand 06 / tray-right: 0.474144643 mm³.
- right strand 13 / tray-right: 1.447755172 mm³.

Accessible service is NOT certified. The envelope covers every intermediate reserve-turn translation plus 0.020 mm allowance. Own moving harness is excluded as in the tuning method; fitted crossings remain independently disqualifying. See [service.json](17mm/service.json).

E screws full engagement/root: PASS. Board/plate stack, protected palm and complete source floor band: PASS. Certified cap check: PASS. Independent manufacturing reload: 18/19 parts; preview 366/366 constituents.

**17 mm central-shell manufacturing verdict: PASS** — STEP valid=True, 1 solid(s), 0 nonmanifold STL edges. This shell-specific verdict does not waive any other part's manufacturing failure.

Manufacturing blocker **tray-left**: independently reloaded STEP valid=False, 1 solid(s), STEP volume delta 7.82165444e-09 mm³; STL has 0 nonmanifold edges and 0 degenerate triangles. Source validity or a manifold STL cannot substitute for a valid STEP reload.

Rejected serialization repair attempts and the invalid splice-boss face are recorded in [tray-step-diagnostics.json](17mm/tray-step-diagnostics.json). No validity check is relaxed.

Inherited constituent **Fly-official-42-instance-42** is invalid: 8 invalid faces, bounds [[-4.470000100000003, -54.51392080832, 7.9499999999999975], [4.4700001000000045, -47.20892060831999, 12.250000100000001]]; diagnostic fix valid=False, volume delta 0.0 mm³. It remains a gate-1 blocker. Face areas/bounds are recorded in audit.json.

Remaining failed gates and evidence:

- **1 Exhaustive fitted collision**: 80 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid constituents: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **3 Accessible ~30 mm service**: Motion blocked; fitted collisions additionally prevent accessible certification.
- **7 Print envelopes and manufacturing data**: tray-left: STEP valid=False, 1 solids, 0 nonmanifold edges, volume delta 7.82165444e-09 mm³ Required skin PASS; stack/palm/floor invariants PASS.

Full named fitted blockers and intersection bounds are in audit.json / collision-map.json; exact roof blockers and shell separations are in tuning-blockers.json. A failed route is not proof that a compliant route is impossible.

### Round 3 — 16 mm

Exhaustive audit: 366 constituents, 66795 unordered pairs; 65267 AABB exclusions, 132 explicit own mates, 1396 exact Commons, 0 Boolean errors. Threshold stays 1e−6 mm³. All gates bind to assembly-index.json; no prior PASS certifies changed operands.

Final tray seating removes 41.340542540 mm³ only from trays north of the protected palm band. The two shell/tray contacts clear to zero Common. Shell, plate, POM and wire operands are byte-identical across that change. The full unordered-pair audit is re-enumerated; 1012 exact current-round results are reused only when both serialized operand hashes, names and indices match. Every changed-tray pair is recomputed. The independent package verifier replays that proof; all service/material/export gates rerun on the new index. Seam proof rebinding likewise verifies every unchanged shell/plate operand. See tray-seating-relief.json and audit-E-restoration-reuse.json.

| Collision category | Tuning | Round 3 |
|---|---:|---:|
| E screws / conductors | 6 | 0 |
| E screws / shell-central | 2 | 0 |
| POM-left-H3 / shell-central | 1 | 1 |
| POM-right-H1 / shell-central | 1 | 1 |
| aluminium plates / conductors | 28 | 10 |
| aluminium plates / shell-central | 4 | 0 |
| conductors / conductors | 172 | 52 |
| conductors / main | 0 | 2 |
| conductors / shell-central | 28 | 0 |
| conductors / strip-left | 14 | 0 |
| conductors / strip-right | 14 | 0 |
| conductors / switch-envelope-L_R0_C5 | 0 | 1 |
| conductors / switch-envelope-L_R1_C5 | 0 | 2 |
| conductors / switch-envelope-R_R0_C5 | 0 | 1 |
| conductors / switch-envelope-R_R1_C5 | 0 | 2 |
| conductors / trays | 25 | 0 |
| conductors / wing_left | 0 | 7 |
| conductors / wing_right | 0 | 7 |
| shell-central / trays | 4 | 0 |

| Side | Longest finished mm | Routed mm | Connected reserve mm | Minimum radius mm |
|---|---:|---:|---:|---:|
| left | 198.400068 | 191.100068 | 30.200000 | 5.000000 |
| right | 198.400068 | 191.100068 | 30.200000 | 5.000000 |

Fly: 170.000000000 mm, R5, exact roof gap 0.300000 mm. USB sweep: PASS. Sourced tails and per-wire geometry are in [length-fly.json](16mm/length-fly.json).

**Seam geometry:** shell ownership ends at the full unchanged aluminium blank silhouette, including apertures; no shell is allowed inside plate apertures. Nominal horizontal gap and overlap are both 0 mm. Actual shell/plate Common maximum 0.000000000 mm³; ownership maximum 0.000000000 mm³. Full 2.00 mm normal skin check PASS; maximum missing required material 0.000000000 mm³. Slope vertical skin is 2.090056857 mm.

| Seam region | Length mm | Shell top minus plate top mm |
|---|---:|---|
| slope | 84.475209 | 0.000000 … 11.100000 |
| low_south | 43.544804 | 0.000000 … 0.000000 |
| north_left | 164.588453 | 11.100000 … 11.100000 |
| north_right | 164.588453 | 11.100000 … 11.100000 |

Exact seam lines, trimmed boundary-distance witnesses (explicit [0, upper] intervals at ≤0.000001 mm for nominally coincident boundaries), and removed ownership regions are in [seam.json](16mm/seam.json). The central footprint is the component containing the declared bay datum (0,20); disconnected outer south perimeter regions are explicitly outside ownership, not discarded by volume ranking. No bridge crosses a well. Central shell: **1 solid(s)**. Single solid under the seam rule.


Fixed bodies intersecting the full required 2.00 mm skin (an underside pocket here removes required material):

| Fixed body | Roof region | Common mm³ |
|---|---|---:|
| POM-left-H3 | low_south | 0.040770468 |
| POM-right-H1 | low_south | 0.040770032 |

These residual contacts require a further explicit footprint, exterior or fixed-stack change. The seam rule is applied; no skin pocket or additional footprint exception is used to hide them.

Continuous service motion (caps and Main removed, Wing hardware fitted):

- left: 4 contacts, 0 errors; release 30.200000 mm.
- right: 4 contacts, 0 errors; release 30.200000 mm.

The remaining continuous-motion blockers are tray contacts (the fitted route itself has no tray contact); the translating reserve envelope is therefore not clear even after the caps/Main removal procedure:

- left strand 02 / tray-left: 0.018565946 mm³.
- left strand 09 / tray-left: 0.006182203 mm³.
- left strand 10 / tray-left: 0.000328737 mm³.
- left strand 14 / tray-left: 0.000292079 mm³.
- right strand 01 / tray-right: 0.000292079 mm³.
- right strand 05 / tray-right: 0.000328737 mm³.
- right strand 06 / tray-right: 0.474144643 mm³.
- right strand 13 / tray-right: 1.447755172 mm³.

Accessible service is NOT certified. The envelope covers every intermediate reserve-turn translation plus 0.020 mm allowance. Own moving harness is excluded as in the tuning method; fitted crossings remain independently disqualifying. See [service.json](16mm/service.json).

E screws full engagement/root: PASS. Board/plate stack, protected palm and complete source floor band: PASS. Certified cap check: PASS. Independent manufacturing reload: 18/19 parts; preview 366/366 constituents.

**16 mm central-shell manufacturing verdict: PASS** — STEP valid=True, 1 solid(s), 0 nonmanifold STL edges. This shell-specific verdict does not waive any other part's manufacturing failure.

Manufacturing blocker **tray-left**: independently reloaded STEP valid=False, 1 solid(s), STEP volume delta 7.0722308e-09 mm³; STL has 0 nonmanifold edges and 0 degenerate triangles. Source validity or a manifold STL cannot substitute for a valid STEP reload.

Rejected serialization repair attempts and the invalid splice-boss face are recorded in [tray-step-diagnostics.json](16mm/tray-step-diagnostics.json). No validity check is relaxed.

Inherited constituent **Fly-official-42-instance-42** is invalid: 8 invalid faces, bounds [[-4.470000100000003, -53.142736400370005, 7.9499999999999975], [4.4700001000000045, -45.837736200369996, 12.250000100000001]]; diagnostic fix valid=False, volume delta 0.0 mm³. It remains a gate-1 blocker. Face areas/bounds are recorded in audit.json.

Remaining failed gates and evidence:

- **1 Exhaustive fitted collision**: 86 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS. Invalid constituents: Fly-official-42-instance-42. Ownership PASS; plate seam contacts PASS; strand sweep checks 28/28.
- **3 Accessible ~30 mm service**: Motion blocked; fitted collisions additionally prevent accessible certification.
- **7 Print envelopes and manufacturing data**: tray-left: STEP valid=False, 1 solids, 0 nonmanifold edges, volume delta 7.0722308e-09 mm³ Required skin PASS; stack/palm/floor invariants PASS.

Full named fitted blockers and intersection bounds are in audit.json / collision-map.json; exact roof blockers and shell separations are in tuning-blockers.json. A failed route is not proof that a compliant route is impossible.

## Round 3 reproduction

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` with the retained CAD Python environment. All runtime scratch is in `.issue248-runtime/`. Every gate, independent STEP/STL reload, preview constituent count, collision witness and package hash/coverage check is rerun. Metrology runs length, USB, continuous service and invariants as separate processes; caps_only supplies the independent certified cap audit. This bounds memory and checkpoints completed sections without changing their geometric checks. Geometry ownership and full required skin are additionally checked by seam.py. Authorized openings are subtracted with the exact CAD cylinders: Ø5.10 south through-holes, Ø2.20 north through-holes and Ø4.00 north counterbores only over their top 1 mm. The preliminary inscribed-polygon masks falsely left circular slivers in the required material and are preserved under per-pitch evidence/; the collision/material thresholds are unchanged. No mesh welding, discarded in-footprint solid, changed collision threshold or strand-overlap exemption is used.

## Preserved tuning report (historical evidence)

# Issue #248 Phase B — tuning continuation

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

This tuning candidate closes only the gates shown as PASS. It does not complete the requested all-clear wiring/service design. The original first-candidate report and evidence remain byte-preserved in [first-candidate/](first-candidate/REPORT.md). PO comments were reread with `gh issue view 248 --comments`; the continuation snapshot is in sources/issue248-continuation.json.

| Gate | 17 mm primary | 16 mm verification |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Finished conductors ≤200 mm | PASS | PASS |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | PASS | PASS |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | PASS | PASS |
| 7 Print envelopes and manufacturing data | PASS | FAIL |
| 8 Fitted preview STEP | PASS | PASS |

## Kept and discarded interrupted work

See [WIP-INVENTORY.md](WIP-INVENTORY.md). Starting at 47f7dd5, uncommitted 17 mm hardware/geometry metadata, cap audit source, boundary regularization and hardware replacement code were inventoried and checkpointed early (aba62a9). M2×10 qualification and the cap audit were kept, rerun and extended to both pitches. The 17 mm shell boundary repair was kept and independently export-verified. Its intermediate two-solid diagnostic is superseded by final geometry diagnostics; the diagnostic is not a final claim. Experimental routes_tuning.py / transport.py remain as rejected development source, not fitted routes. Their fan crossings prevented adoption. Python caches were excluded. Runtime scratch and starting geometry snapshots remain in .issue248-runtime/tuning; no /tmp scratch was used.

Original E-boss regions were restored after a stricter engagement-material audit exposed damage from projected route cuts; the interrupted nominal-only engagement check was insufficient and is superseded. All changed-tray pair and service checks were rerun. The current `routes.py` replaces the early X±27/Y−24 merge with separated outlet lanes through the Wing north corridor, a lower fan into the neck, and concentric reserve turns. The long stored turn was moved from Y22.1 to Y17.1; its released reference is Y2.0, preserving 30.20 mm. This saves routed length. The final audit still rejects unresolved fan/upper-route and fixed-part contacts: no new route is described as qualified on length alone.

## Unchanged inputs and explicit deviations

Deck Z13.55; board undersides Z7.35; plateau Z24.65 provisional q=1.50; slope breaks Y1.935592550 / Y38.514430874; boards, aluminium plates and board/plate stack remain unchanged. Existing PCB and plate manufacturing files are byte-checked against inputs-sha256.json before report/manifests regenerate. Actual fitted invariants and the protected south palm band are recomputed. GH remains the connector. Fly remains one connected 170 mm R5 cable. No thinner skin, changed cap, raised deck or changed well is introduced.

Roofs use **2.00 mm normal thickness**; the slope's vertical thickness is 2.090056857 mm. Main GH blisters retain ceiling/top Z13.20/15.20; Fly Z13.25/15.25; Ø5.10 south openings and north shell retention remain. Case channels are cut only from trays, with the full source floor band restored through Z2 before remaking splice pilots. All local relief is recorded; no gate tolerance is enlarged. Detached north tongues are assigned by explicit geometric adjacency, never a largest-solid filter. The 16 mm south section is not deleted or bridged across a key well.

Length uses a **3.40 mm nominal internal wire upper bound per end**, plus the 0.50 mm Wing external dress lead, from the [JST GH manufacturer drawing](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), readable repository archival figure on printed page 2. Exact dress-plane definition and derivation are in [tail-source.json](tail-source.json): housing mouth to cut copper end; 5.70 housing axial length minus protected 2.30 mating section. Wing actual mouth is Y−35.45 (#235: header rear −42.60 + seated 7.15); this candidate starts at Y−34.95, so another 0.50 mm is explicitly included. Total unrouted bound is 7.30 mm (Wing 3.90 + Main 3.40). This assumes a correctly seated terminal whose nose does not protrude past the housing mating tip and a wire end that does not invade the mating section. It is a drawing-derived bound, not a measured crimp or a production tolerance guarantee. The 2.10 mm crimp-region and 1.50 mm strip dimensions are not misused as that tail. The 164.8 mm Phase A dressed budget is reported as a reference only. Physical mating, q/skirt/full-press, crimp inspection and retention testing remain OPEN.

## Remaining blockers and service procedure

Wiring remains a failed candidate wherever the exhaustive audit finds strand crossings or fixed-body contacts. Remove USB, shell screws, central cap and strips; disconnect Main GH/EZmate, remove Main and its own hardware, then translate the connected reserve turns north by 15.10 mm. Wing hardware remains fitted. The continuous audit tests that proposal; its blockers are retained in service.json. No accessible-service certification is granted while fitted collisions remain. A further separated fan/upper-path redesign is required; this run does not prove that redesign impossible.

There is also a direct fixed-input roof conflict: the required low skin and unchanged aluminium overlap in material. An underside pocket cannot preserve 2.00 mm skin there. At 16 mm, the settled central surface footprint has a disconnected south component separated by 0.200 mm; a single solid requires revised ownership/footprint or an authorized connection. These constraints are reported explicitly instead of deleting skin, plate or shell material. The full physical Junana skirt test remains OPEN at both pitches.

## 17 mm current evidence

- **1 Exhaustive fitted collision: FAIL.** 295 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS.
- **2 Finished conductors ≤200 mm: PASS.** Longest finished upper bound 197.822584 mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.
- **3 Accessible ~30 mm service: FAIL.** Motion blocked; fitted collisions additionally prevent accessible certification.
- **4 Connected Fly 170 / R5 / roof gap: PASS.** 170.000000000 mm, R5; true roof gap 0.300000 mm; 0 fitted contacts.
- **5 USB 30 mm insertion: PASS.** Three continuous 30 mm reservations recomputed.
- **6 Assumed swept caps after allowances: PASS.** Certified trimmed-face minimum after 0.50 mm allowance: 0.500000 mm; physical Junana skirt test OPEN.
- **7 Print envelopes and manufacturing data: PASS.** All nineteen STEP/STL sets independently reloaded with unchanged verifier.
- **8 Fitted preview STEP: PASS.** Preview reloaded 366 / 366 constituents.

| Side | Routed max mm | Finished bound mm | Margin to 200 mm | Finished dressed bound mm | Margin to 164.8 reference mm | Connected reserve mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |
| right | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |

The 164.8 mm value is a reported Phase A reference, not a binding gate. The 3.40 mm internal tails plus the 0.50 mm Wing dress lead are included in finished and dressed bounds. The 30.20 mm reserve is the difference between connected curves, not a detached length allowance. See [length-fly.json](17mm/length-fly.json).

Fitted audit: **366 constituents, 66795 unordered pairs**, 65084 AABB exclusions, 132 explicitly classified own mates, 1579 exact Commons, 0 operation errors. Intersection threshold remains 1e−6 mm³. [tuning-comparison.json](17mm/tuning-comparison.json) lists cleared, remaining and new named pairs against the first candidate. Both pitch geometries and all exact candidates were rerun in this tuning round. After E-boss restoration, results are replayed only when both serialized operand hashes, names and constituent indices are unchanged; every changed-tray pair is recomputed. audit-E-restoration-reuse.json binds this proof to preserved parent evidence; verify_package.py independently checks it. No first-candidate PASS is reused. Full names, Common volumes/bounds and all positive contacts are in [audit.json](17mm/audit.json) and [collision-map.json](17mm/collision-map.json). Inherited Fly source invalidities remain labelled.

- conductors / conductors: 172 contacts.
- aluminium plates / conductors: 28 contacts.
- conductors / shell-central: 28 contacts.
- conductors / trays: 25 contacts.
- conductors / strip-left: 14 contacts.
- conductors / strip-right: 14 contacts.
- E screws / conductors: 6 contacts.
- E screws / shell-central: 2 contacts.
- aluminium plates / shell-central: 2 contacts.
- shell-central / trays: 2 contacts.
- POM-left-H3 / shell-central: 1 contacts.
- POM-right-H1 / shell-central: 1 contacts.

Continuous service-motion results:

- left: 14 contacts, 0 errors; represented release 30.20 mm.
- right: 14 contacts, 0 errors; represented release 30.20 mm.

The swept envelope includes every intermediate translation of each concentric reserve U, plus a 0.020 mm excess. Wing stacks and the other harness remain fitted. Main and its removable hardware, shell caps and own moving harness are excluded as documented in service.json. The fixed legs shorten along their existing loci. A clear reserve-motion result alone cannot certify a harness with fitted fan/upper-route crossings. Individual own-harness motion was not promoted to service certification while those crossings remain. The new route clears every fixed Wing MUX bound (0 MUX contacts), but still has 172 strand/strand fitted contacts plus the fixed-body contacts listed above; it is not a successful separated-harness qualification.

Hardware: all eight **M2×10** E replacements PASS. Under-head Z13.85, tip Z3.85, boss top Z7.35: **3.50 mm nominal engagement**, full thread-bearing annulus verified by exact Common (major radius 1.00 / pilot radius 0.85 over Z3.85…7.35), tip **1.85 mm above floor top**, **≥1.20 mm root material** verified with material probes. Washer and head envelope are retained. Existing pilot depths remain recorded per seat. Replacement procurement must preserve the polymer-compatible thread and Ø3.4 ×1.3 mm head envelope; physical retention remains untested. [hardware-inventory.json](17mm/hardware-inventory.json) lists each seat. New north-head wall relief is below the plateau roof. A stricter engagement check rejected the routing cuts that left only 32.5% of the two north thread-bearing annuli. Exact original source boss material within a named Ø7 region was restored, preserving its pilots and the compressed stack; hardware-inventory.json now requires complete annulus and root material. This adds legitimate wire/boss contacts to the failed routing evidence, rather than weakening the supports. Required-skin contacts are not excused by it.

Certified local distances:

- cover-Main-spacer-2: distance 0.300000 mm; Common 0.000000000 mm³.
- cover-screw-2: distance 0.550000 mm; Common 0.000000000 mm³.
- cover-Main-spacer-3: distance 0.299999 mm; Common 0.000000000 mm³.
- cover-screw-3: distance 0.549999 mm; Common 0.000000000 mm³.
- Main-GH-left-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.
- Main-GH-right-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.

Caps: all 42 assumed 16×16 mm swept envelopes, Z13.95 to provisional Z24.65, checked against every actual central/strip solid. Common is below 1e−6 mm³ for every pair. The minimum exact trimmed-face distance is **1.000000 mm**, leaving **0.500000 mm** after the unchanged 0.50 mm allowance, against a 0.30 mm gate. Face pairs are excluded only by Euclidean AABB lower bounds; finite closest points and their actual face bounds are checked. This bypasses the defective whole-solid inside classifier. [cap-witnesses.json](17mm/cap-witnesses.json) records faces and points. Physical skirt/full-press test remains OPEN.

Required-skin blockers (independent intersection of the unchanged roof rule and fixed bodies):

- POM-left-H3 / required low_south roof: 3.653100 mm³.
- plate-left / required low_south roof: 1158.194242 mm³.
- plate-left / required slope roof: 175.400194 mm³.
- POM-right-H1 / required low_south roof: 3.653100 mm³.
- plate-right / required low_south roof: 1158.183766 mm³.
- plate-right / required slope roof: 175.400197 mm³.
- tray-left protected south palm band / required low_south roof: 89.482726 mm³.
- tray-right protected south palm band / required low_south roof: 84.196891 mm³.

These overlaps cannot be removed by underside relief while preserving a full 2.00 mm skin below the settled exterior at the same footprint. The low roof occupies Z11.55…13.55; the aluminium plate occupies Z12.05…13.55. Clearing it requires changed footprint/material ownership, stack or exterior. None is silently changed. Other remaining tray/hardware/strand contacts are still failed and enumerated, not claimed impossible merely because this candidate fails.

Central shell: **1 solids**. Boundary regularization cancels opposing internal planar sheets; volume preserved within 1e−6 mm³. All detached north tongues are explicitly assigned to an adjoining strip only after a valid volume-preserving single-solid union. Exact component separation and footprint component bounds are in [tuning-blockers.json](17mm/tuning-blockers.json). A disconnected south section is retained in STEP/STL and the print gate fails for it.

| Print | STEP solids | Nonmanifold STL edges | Export verification |
|---|---:|---:|---|
| splice-1 | 1 | 0 | PASS |
| splice-2 | 1 | 0 | PASS |
| post-left-R1 | 1 | 0 | PASS |
| post-left-R2 | 1 | 0 | PASS |
| post-left-R3 | 1 | 0 | PASS |
| post-left-R4 | 1 | 0 | PASS |
| post-left-R5 | 1 | 0 | PASS |
| post-left-R6 | 1 | 0 | PASS |
| tray-left | 1 | 0 | PASS |
| post-right-R1 | 1 | 0 | PASS |
| post-right-R2 | 1 | 0 | PASS |
| post-right-R3 | 1 | 0 | PASS |
| post-right-R4 | 1 | 0 | PASS |
| post-right-R5 | 1 | 0 | PASS |
| post-right-R6 | 1 | 0 | PASS |
| tray-right | 1 | 0 | PASS |
| strip-left | 1 | 0 | PASS |
| strip-right | 1 | 0 | PASS |
| shell-central | 1 | 0 | PASS |

The unchanged export checks include STEP validity, single solid, 220×220 mm XY envelope including 5 mm brim, height ≤250 mm, exact STL edge incidence, no degenerate triangles, volume error <0.001, hashes and preview inventory. No mesh welding or discarded solid is used. [export-verification.json](17mm/export-verification.json), manufacturing STEP/STL/SVG and dimension register correspond to this candidate.

Updated planning cost: 200.2 g nominal PETG; 250.3 g with waste; USD 7.81–15.91 case material/new hardware; 8.2–16.4 print hours. Including machine time and assembly, USD 36.02–52.33. Eight M2×10 replacements are newly included; these are assumptions, not quotes.

## 16 mm current evidence

- **1 Exhaustive fitted collision: FAIL.** 299 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS.
- **2 Finished conductors ≤200 mm: PASS.** Longest finished upper bound 197.822584 mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.
- **3 Accessible ~30 mm service: FAIL.** Motion blocked; fitted collisions additionally prevent accessible certification.
- **4 Connected Fly 170 / R5 / roof gap: PASS.** 170.000000000 mm, R5; true roof gap 0.300000 mm; 0 fitted contacts.
- **5 USB 30 mm insertion: PASS.** Three continuous 30 mm reservations recomputed.
- **6 Assumed swept caps after allowances: PASS.** Certified trimmed-face minimum after 0.50 mm allowance: 0.500000 mm; physical Junana skirt test OPEN.
- **7 Print envelopes and manufacturing data: FAIL.** shell-central: 2 solids, 0 nonmanifold edges
- **8 Fitted preview STEP: PASS.** Preview reloaded 367 / 367 constituents.

| Side | Routed max mm | Finished bound mm | Margin to 200 mm | Finished dressed bound mm | Margin to 164.8 reference mm | Connected reserve mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |
| right | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |

The 164.8 mm value is a reported Phase A reference, not a binding gate. The 3.40 mm internal tails plus the 0.50 mm Wing dress lead are included in finished and dressed bounds. The 30.20 mm reserve is the difference between connected curves, not a detached length allowance. See [length-fly.json](16mm/length-fly.json).

Fitted audit: **367 constituents, 67161 unordered pairs**, 65428 AABB exclusions, 133 explicitly classified own mates, 1600 exact Commons, 0 operation errors. Intersection threshold remains 1e−6 mm³. [tuning-comparison.json](16mm/tuning-comparison.json) lists cleared, remaining and new named pairs against the first candidate. Both pitch geometries and all exact candidates were rerun in this tuning round. After E-boss restoration, results are replayed only when both serialized operand hashes, names and constituent indices are unchanged; every changed-tray pair is recomputed. audit-E-restoration-reuse.json binds this proof to preserved parent evidence; verify_package.py independently checks it. No first-candidate PASS is reused. Full names, Common volumes/bounds and all positive contacts are in [audit.json](16mm/audit.json) and [collision-map.json](16mm/collision-map.json). Inherited Fly source invalidities remain labelled.

- conductors / conductors: 172 contacts.
- aluminium plates / conductors: 28 contacts.
- conductors / shell-central: 28 contacts.
- conductors / trays: 25 contacts.
- conductors / strip-left: 14 contacts.
- conductors / strip-right: 14 contacts.
- E screws / conductors: 6 contacts.
- aluminium plates / shell-central: 4 contacts.
- shell-central / trays: 4 contacts.
- E screws / shell-central: 2 contacts.
- POM-left-H3 / shell-central: 1 contacts.
- POM-right-H1 / shell-central: 1 contacts.

Continuous service-motion results:

- left: 14 contacts, 0 errors; represented release 30.20 mm.
- right: 14 contacts, 0 errors; represented release 30.20 mm.

The swept envelope includes every intermediate translation of each concentric reserve U, plus a 0.020 mm excess. Wing stacks and the other harness remain fitted. Main and its removable hardware, shell caps and own moving harness are excluded as documented in service.json. The fixed legs shorten along their existing loci. A clear reserve-motion result alone cannot certify a harness with fitted fan/upper-route crossings. Individual own-harness motion was not promoted to service certification while those crossings remain. The new route clears every fixed Wing MUX bound (0 MUX contacts), but still has 172 strand/strand fitted contacts plus the fixed-body contacts listed above; it is not a successful separated-harness qualification.

Hardware: all eight **M2×10** E replacements PASS. Under-head Z13.85, tip Z3.85, boss top Z7.35: **3.50 mm nominal engagement**, full thread-bearing annulus verified by exact Common (major radius 1.00 / pilot radius 0.85 over Z3.85…7.35), tip **1.85 mm above floor top**, **≥1.20 mm root material** verified with material probes. Washer and head envelope are retained. Existing pilot depths remain recorded per seat. Replacement procurement must preserve the polymer-compatible thread and Ø3.4 ×1.3 mm head envelope; physical retention remains untested. [hardware-inventory.json](16mm/hardware-inventory.json) lists each seat. New north-head wall relief is below the plateau roof. A stricter engagement check rejected the routing cuts that left only 32.5% of the two north thread-bearing annuli. Exact original source boss material within a named Ø7 region was restored, preserving its pilots and the compressed stack; hardware-inventory.json now requires complete annulus and root material. This adds legitimate wire/boss contacts to the failed routing evidence, rather than weakening the supports. Required-skin contacts are not excused by it.

Certified local distances:

- cover-Main-spacer-2: distance 0.300000 mm; Common 0.000000000 mm³.
- cover-screw-2: distance 0.550000 mm; Common 0.000000000 mm³.
- cover-Main-spacer-3: distance 0.299999 mm; Common 0.000000000 mm³.
- cover-screw-3: distance 0.549999 mm; Common 0.000000000 mm³.
- Main-GH-left-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.
- Main-GH-right-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.

Caps: all 42 assumed 16×16 mm swept envelopes, Z13.95 to provisional Z24.65, checked against every actual central/strip solid. Common is below 1e−6 mm³ for every pair. The minimum exact trimmed-face distance is **1.000000 mm**, leaving **0.500000 mm** after the unchanged 0.50 mm allowance, against a 0.30 mm gate. Face pairs are excluded only by Euclidean AABB lower bounds; finite closest points and their actual face bounds are checked. This bypasses the defective whole-solid inside classifier. [cap-witnesses.json](16mm/cap-witnesses.json) records faces and points. Physical skirt/full-press test remains OPEN.

Required-skin blockers (independent intersection of the unchanged roof rule and fixed bodies):

- POM-left-H3 / required low_south roof: 3.672595 mm³.
- plate-left / required low_south roof: 915.143479 mm³.
- plate-left / required slope roof: 160.260272 mm³.
- POM-right-H1 / required low_south roof: 3.672595 mm³.
- plate-right / required low_south roof: 915.139204 mm³.
- plate-right / required slope roof: 160.260276 mm³.
- tray-left protected south palm band / required low_south roof: 75.033093 mm³.
- tray-right protected south palm band / required low_south roof: 69.742299 mm³.

These overlaps cannot be removed by underside relief while preserving a full 2.00 mm skin below the settled exterior at the same footprint. The low roof occupies Z11.55…13.55; the aluminium plate occupies Z12.05…13.55. Clearing it requires changed footprint/material ownership, stack or exterior. None is silently changed. Other remaining tray/hardware/strand contacts are still failed and enumerated, not claimed impossible merely because this candidate fails.

Central shell: **2 solids**. Disconnected south surface footprint at 16 mm: a bridge would add exterior footprint or cross an excluded well. No bridge/deletion used. Exact component separation and footprint component bounds are in [tuning-blockers.json](16mm/tuning-blockers.json). A disconnected south section is retained in STEP/STL and the print gate fails for it.

| Print | STEP solids | Nonmanifold STL edges | Export verification |
|---|---:|---:|---|
| splice-1 | 1 | 0 | PASS |
| splice-2 | 1 | 0 | PASS |
| post-left-R1 | 1 | 0 | PASS |
| post-left-R2 | 1 | 0 | PASS |
| post-left-R3 | 1 | 0 | PASS |
| post-left-R4 | 1 | 0 | PASS |
| post-left-R5 | 1 | 0 | PASS |
| post-left-R6 | 1 | 0 | PASS |
| tray-left | 1 | 0 | PASS |
| post-right-R1 | 1 | 0 | PASS |
| post-right-R2 | 1 | 0 | PASS |
| post-right-R3 | 1 | 0 | PASS |
| post-right-R4 | 1 | 0 | PASS |
| post-right-R5 | 1 | 0 | PASS |
| post-right-R6 | 1 | 0 | PASS |
| tray-right | 1 | 0 | PASS |
| strip-left | 1 | 0 | PASS |
| strip-right | 1 | 0 | PASS |
| shell-central | 2 | 0 | FAIL |

The unchanged export checks include STEP validity, single solid, 220×220 mm XY envelope including 5 mm brim, height ≤250 mm, exact STL edge incidence, no degenerate triangles, volume error <0.001, hashes and preview inventory. No mesh welding or discarded solid is used. [export-verification.json](16mm/export-verification.json), manufacturing STEP/STL/SVG and dimension register correspond to this candidate.

Updated planning cost: 186.1 g nominal PETG; 232.6 g with waste; USD 7.45–15.38 case material/new hardware; 7.6–15.3 print hours. Including machine time and assembly, USD 35.08–50.64. Eight M2×10 replacements are newly included; these are assumptions, not quotes.

## Reproduction and integrity

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` from this worktree with the retained CAD Python environment. Each stage is separate; all scratch and audit checkpoints are under .issue248-runtime. Exact audit reuse is permitted only for the identical geometry index hash. This continuation rebuilds both pitches and reruns all eight gates, independent exports, witnesses and package checks. All 44 preserved first-candidate files are independently checked against the frozen 47f7dd5 hashes in first-candidate-sha256.json; new outputs describe the tuning candidate. Run `python3 hardware/case/issue-248-phaseb/verify_package.py` after report generation for input/artifact hashes and independent all-pair coverage. The package remains provisional and unreleased, with the explicitly failed gates above.

