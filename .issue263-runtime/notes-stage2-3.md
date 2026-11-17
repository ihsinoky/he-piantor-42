# Issue #263 — stage 2/3 working notes (worker)

## Stage 2 — Wing Rev.5

- Build: Rev.4 routed boards, J_WING GH -> FH12 at the GH site,
  pad-row aligned, then shifted +2.95 mm along the mouth direction so
  the housing envelope centre matches the #261 spec exactly.
  Verified in case frame (pose-verification.json): envelope centre
  (+/-27.0, -37.5) EXACT, mouth (+/-27.0, -34.3) vs spec slot -34.2.
- FH12 footprint frame error found and fixed during the round: the
  first build had the mouth facing AWAY from Main (local frame
  mirrored vs the GH convention). Footprint local Y mirrored
  (mouth +Y, pads at rear -Y), Wing shifted to envelope spec, Main
  yaw corrected (KiCad orientation = #261 case yaw in file frame).
- MP fitting pads: first placement overlapped signal pads 1/14
  (DRC); moved to housing front corners (+/-4.70, +1.20); later
  shrunk 1.20x1.60 -> 0.90x1.30 to clear an inherited H_A2_RAW track
  on 17L. Geometry remains a catalog reconstruction — verify against
  Hirose drawing CL586-0533-0 before order release.
- Flow per variant: KRT route (D-021 opts) -> diagnose (power width
  normalisation + HALL_5V F.Cu / GND B.Cu pours) -> plane-repair ->
  cleanup -> audit (refill + native DRC + physical qualify).
  Escalation 'board' re-routes tried for all four variants.
- Result: every variant ends with exactly ONE unconnected item —
  one J_WING GND pad's pour island pinched off by neighbouring
  fanout tracks (17R: pad 4, island 0.65 mm2, too small for a
  0.60/0.30 via hop; plane-repair A* reports NO PATH; the neck is
  set by the zone min-thickness 0.30 / clearance 0.15 rules, not
  relaxed). No wrong-net contacts anywhere. Via-pad minima:
  16L 0.1013, 16R 0.1072, 17L 0.1252, 17R 0.1301 (floor 0.10 PASS;
  0.125 target met by 17mm pair only). Width floors PASS.
  Native Wing ERC: unavailable (inherited — no native Wing
  schematic), stated not waived.

## Stage 3 — Main Rev.8

- Assignment: pad n <- D-024 signal (15-n) on both J2/J3; schematic
  net labels on J2/J3 swapped pairwise to match; ERC 0 after swap.
- Assignment verification: position-space composition through the
  #264 five-fold transport (recomputed from its headings) PASSES
  for both sides and both pitches (assignment-verification.json);
  net sets equal Rev.7 per connector.
- Build defect found+fixed: Rev.7 kept copper (V5V2) passed under
  the FH12 fitting pads -> shorts. build-main now removes any kept
  track/via colliding with the new pads (+0.10 mm) before routing
  (2 V5V2 segments among them); shorts gone after re-route.
- SPEC CONFLICT (for PMO/PO): the #261 J2 pose puts ZIF pads
  12/13/14 at copper-to-edge clearance 0.173 / 0.000 / 0.000 mm
  against the Rev.7 outline's west hypotenuse (rule 0.200 mm).
  Rev.7's J2 sat ~5 mm further east and was clear. A pose shift
  large enough to restore 0.2 mm moves the FFC landing laterally
  ~0.49 mm per 0.5 mm shift — a full lane at 0.5 mm pitch — so it
  cannot be absorbed silently; the case entry slot is also cut for
  the spec mouth. Options: (a) shift pose + re-cut slot + accept
  lane offset (not viable), (b) extend the Main outline westward
  near J2 (case pocket check needed), (c) accept reduced edge
  clearance as a disclosed exception (pads 13/14 at 0.000 = copper
  at the edge — NOT recommended), (d) rotate J2 a few degrees
  about its centre so the pad row's west end lifts off the edge
  (mouth heading changes; FPC approach heading was 43 deg class —
  a small rotation may be absorbable by the fold plan's first
  segment; needs #264 model re-run). PMO decision needed; the
  board was qualified in the spec pose meanwhile.
- Copper-diff locality vs Rev.7: 895 of 1167/826 track objects
  differ; changed-copper bbox 41.6 x 40.8 mm around the two sites —
  NOT a local change (same lesson as Rev.7's: a connector swap on
  this board is a re-route, disclosed as such).
- Via-pad min 0.1596 mm PASS (>=0.125 target).
