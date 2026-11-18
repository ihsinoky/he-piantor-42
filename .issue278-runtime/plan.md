# Issue #278 — Flipped-installation USB routing study: PLAN + measured basis

## Premise (adopted record)
- Main Rev.10 flipped (components down), Wing links qualified flipped
  (Type D FFC, #275 Stage B audits). USB path is the named residual.
- J4 = Molex Pico-EZmate 781710004 on Main; Fly Daughterboard (Geon x
  Wolf) at the north wall; stock cable 170 mm EZmate<->EZmate (x2 owned).

## Measured basis (sources cited; numbers re-extracted in basis.py)
- Case/body frame = #264 bundle: fitlibF.bodies_at(17, -2.65)
  (plate top 10.90). Tray floor top Z1.60; flipped Main underside
  plane Z4.70 -> free span 3.10 mm. Main slab flipped about z 5.30.
- Flipped J4 plug (Stage B model, audit275.py): box centre
  (0, 19.18, 3.45), 5.0 x 3.5 x 1.30 -> z 2.80..4.10; hangs to Z2.80
  over plain floor = 1.20 mm clear of Z1.60. Plug's only Stage B
  contact = its own header envelope (engagement volume, expected).
  J4 header flipped: 1.55 tall -> bottom Z3.15, residual 1.55.
- Stage B attempted dress (FLY_FLIP, flat bundle 4.5 x 1.2): south
  exit, west loop at z 1.85, hop over left FFC sheet at y 1..-5
  (z 3.85). FAILED: hop transition vs left sheet 5.385 mm3;
  vs tray-left 501.788 mm3 (candidate channel W cut only partial);
  vs Fly-official 0.189; fold-back needs sub-1 mm bend radius
  (z-span 4.10 vs 2x1.2 strands + allowance). audit275-j4flip.json.
- D-046 pocket A (ADOPTED): x -6..+13, y 28..48, depth 1.0
  (cut z 0.60..1.60) -> tray web 0.60 mm nominal under pocket.
  Restores flipped power-field residual 0.60 -> 1.60.
  Flipped component hang-downs (Stage B body set): C26/27/28 2.5 mm
  -> bottom Z2.20; L1 2.1 -> Z2.60; FH12 2.0 -> Z2.70.
- Fly (official STEP, PMO measurements 2026-11-13): board
  23.57 x 8.30 x 1.59; holes dia 2.20 at (+-9.50, 0); USB-C mouth
  face at board +Y edge (Y +4.385, 0.235 proud), opening centre
  Z ~3.3; EZmate housing on BOTTOM face X -3.30..3.30,
  Y -3.39..1.14, hangs to Z -1.45; plug mates from below.
- Fly seat (adopted low-deck tree, issue-263 README): case bodies +
  Fly seat inherited from issue-261 tree = Delta+6-qualified
  arrangement shifted with the deck (s = -2.65); Fly bodies were in
  the #264/#275 audited sets, no contacts. D-037 seat (deck frame):
  board centre (0, -50.136) @17mm, PCB bottom Z10 (Delta=0 frame),
  USB mouth 0.30 mm inside outer wall, opening W16 open-top.
  Stock-cable Fly plug end in body set at (0, -48.6, 3.45).
  -> basis.py re-extracts exact bboxes from the flipped body set
  (Fly-*, EZmate-*, USB-reference-*, tray-*, flipped Main-study-*)
  instead of trusting the inherited numbers.
- Type D FFC sheets (flipped pose): CTRL_R plan, z flattened to
  underside mouth plane 2.95 (sheet_boxes over catmull(CTRL)).
- Cable model: flat pack 4.5 x 1.2 (4 discrete wires, #232 record:
  flat pack 14-wire 3/4/4/3 for GH; EZmate = 4 wires single row).
  Bend discipline: centreline R >= 5 mm in any plane (project
  harness models use R5 fillets, #232/#246); a z-transition of
  height h consumes >= 2R of run. Stage B fold-back rejection
  stands under this discipline.

## Audit method (repaired, per brief)
- build123d Shape.intersect (ShapeList-aware: sum piece volumes),
  every solid volume-validated (volume > 0), plus a positive
  self-test pair that MUST return > 0 before any result is read
  (method of .issue275gh-runtime/build_audit.py, Phase 2 GH check).
- Cable audited as ONE fused solid vs the full flipped body set
  (both Type D sheets fitted, Fly + USB bodies, trays with pocket A
  + family-specific case cuts modelled explicitly).

## Families (order: A/C share the depressed-corridor idea, run A
## first; B mirror check; D length check; E by measurement; F search)
A pocket extension / depressed corridor from J4 exit northward.
B east-side channel (mirror of failed west route).
C under-sheet crossing inside the channel corridor.
D south-margin loop (measure true path length vs 170 mm).
E Fly 180-degree seat rotation (mouth constraint, measured).
F alternative stock cable / pre-crimped leads (search evidence).

## Pass criteria (per brief)
Unexpected contacts = 0 (full flipped fitted audit, cable one
connected solid, plug envelopes in); length <= stock part; service
motion swept or sequenced with clearances; USB-C insertion
unaffected. Pass-with-case-change counts, quantified.

## PO note 2026-11-18 (relayed via PMO)
- The stock 170 mm EZmate<->EZmate cable is PHYSICALLY ON HAND
  (two Fly units, each shipped with its cable). Family F is a
  FALLBACK only - no procurement optimisation on the main line.
- Model assumptions that a real-part measurement could decide
  (to be named in the final report for a possible PO measurement):
  (1) flat bundle cross-section modelled 4.5 x 1.2 mm;
  (2) bend discipline R >= 5 mm centreline;
  (3) plug envelope modelled 5.0 x 3.5 x 1.30 mm (Stage B box).
