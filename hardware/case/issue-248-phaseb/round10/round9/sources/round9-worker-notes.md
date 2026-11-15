# Round 9 design notes
Axis (right side): a = (sin120, cos120, 0) = (0.866025, -0.5, 0); ep_i + L*a = point on connector axis line.
Row offset per pin step (right): d = (-0.625, -1.082532, 0), |d| = 1.25, d . a = 0 (row perp to axis).
=> Axis vertical planes (contain a and Z through ep_i) are parallel, spaced exactly 1.25 mm.
=> Any path inside its own plane keeps >= 1.25 mm from neighbours' in-plane paths (plane-distance bound).
=> Tail design: get each strand into its plane at E_i = ep_i + s_i*a + (0,0,hE); then straight E_i -> ep_i lies in-plane. DONE.
Open problem = fan-out a3' -> E_i in shared space (straight fan fails: E row is anti-parallel to feed dir, E_j lies near strand i's straight path).
Old tail (R8) pin1: a3'(7.625,-7,10.5) a4(19.625,8,10.5) ap(32.03,42.84,10.65) ep(25.97,46.34,10.65); lengths 19.21+36.99+7 = 63.2.
Length budget: R8 longest finished 195.205 (routed 187.9). New tail must stay ~<= old + 4.
Feed Y-span is ~48 mm fixed (fan Y-7 to Main Y~41). Straight a3'->E is shorter than old 2-seg path (triangle inequality).

## AUDIT BLIND SPOT (verified on round-8 assembly, 17mm)
Pair Wire-right-01/05: audit exact_results volume = 0.0 (not a contact), BUT:
- real path wires intersect (BRepExtrema wire-wire distance ~1e-14) at (17.62,-11.93,4.54)
- point classifier: that point is IN both solids
- box-clipped (3mm box) Common of the two solids = 2.456 mm3 overlap
=> Direct full-solid BRepAlgoAPI_Common (audit's common_record, OBB+parallel) silently returns 0
   for some long swept wire solids. Gate-1 counts in ALL rounds are potential undercounts.
=> Round 9 acceptance must ALSO satisfy the centreline screen (min distance >= 1.0 + margin, ALL pairs),
   not only the pipeline audit. Report this finding prominently.

## Screen facts (right side, centreline.py)
R8: 57 pairs <1.05. By segment pair: (3,7)=19 neck in/out, (3,3)=8 inbound convergence,
(7,7)=9 outbound divergence, (8,8)=2 rise, (9,9)=1, (10,10)=18 approach tail.
R9 tail (stagger s_i = L + k*(i-6.5), L=7, k=-0.9, hE=1): tail pairs -> 2 (early feed, Y 2..10).
Remaining upstream after tail fix: (3,7)=24, (3,3)=14, (7,7)=12, (7,8)=1, (8,8)=1 = 52.
Plan: early rise (a2.z = z_f) for (3,7); re-optimise sigmaB/sigmaF/sigmaZ for (3,3)/(7,7) with tail fixed.

## Stage 1 design (LOCKED, committed de96cfe)
- after = [a0,a1,a2,a3',G,ep], G = ep + s*a + 0.35z on the strand's own connector-axis
  line; s = 7.0 - 0.9*(pin-6.5), floored for pins 11-14 at 5.0+0.15*(pin-10)
  (their unfloored slant < R5 trim at G: pin14 slant 1.52 vs trim 4.42 -> s=5.45).
- An F point NE of G was tried and REJECTED: feed pairs exploded (9,9)=23 vs 3.
  (First F attempt SW of G was a hairpin - travel reversal at G; do not repeat.)
- Pipeline make_routes: 28/28 sweeps valid, service identity exact, longest
  finished 197.848 (margin 2.152), min radius 5.
- Screen (centreline, R8 before): 54 pairs <1.0 = neck (3,7)21+(3,3)13+(7,7)7(+2)
  + feed (9,9) 11. Closest-point seg labels shift between variants; totals stable.

## Neck knot - structural evidence (for REPORT)
- Assignment-only searches floor at ~54 screen pairs: R8's own 550+1900-iter
  search -> 55; this round's greedy -> 54; sorted/identity constructions 83-88.
- Station moves do not break the floor: a2y in {-18..-12}, two-stage descent,
  staggered pack entry (stag_in 0/0.75/1.5), staggered a1y: all 54.
- Knot location: pack-entry corner (X 10-14, Y -20..-13) + descent funnel.
  Funnel bound: at Y=-14 cut the 14 inbound strands pass a ~3.2 x 2.2 mm window
  (X spread ~3.2, Z spread ~2.2) -> mean lattice spacing ~0.76 < 1.0.
- Gate argument: outbound must cross the inbound wall; over-pass slot under the
  Wing edge is Z 6.41..6.85 (single layer); gate frontage ~3 mm in X.
- Service model forces after[1] north of Y~-5 (first fixed station), so the
  outbound cannot loop south first (tested reasoning, not implemented).
- Audit blind spot (verified): R8 audit 46 right-side pairs is a STRICT SUBSET
  of screen 57; 11 pairs/side are real crossings the boolean Common reports as
  0.0 (pair 01/05 proven 2.456 mm3 by clipped common). True R8 crossings >= 114
  both sides vs audit 92. Round-9 acceptance must read screen + audit together.

## PO unfreeze instruction (2026-11-15, mid-round)
If on-axis round cannot reach zero crossings: unfreeze in order (1) tray/shell
local channel geometry, (2) shell reliefs/blister + POM H3/H1 notch exception.
Ledger required per item used. Still frozen: boards, plates, GH/pin maps, wire
spec, deck 13.55, plateau 24.65, seam rule.
Variants screened under this instruction:
- Widened pack lattice (5-4-5, dx 1.2, dz 1.5, origin (9.9,4.35)): seed 69 pairs,
  longest finished 215.1 -> REJECTED (turn radii grow; length-poisoned; px max
  already at the radius>=5 cap 12.458 vs current 12.36, cannot widen east).
- Two-layer outbound (group B climbs to Z 6.6 on seg 7): 54-91 pairs, all
  groupings >= baseline -> REJECTED (climb braids (7,7)).
