# Issue #278 — Flipped-installation USB routing study

**Verdict: the flipped USB path CLOSES.** Family A passes with a case
change (configuration "A2"): the stock 170 mm EZmate cable dresses from
the flipped Main J4 to the Fly Daughterboard through a shallow route
channel cut into the right tray, passing *under* both Type D FFC sheets.
Full fitted audit in flipped pose: **unexpected contacts = 0**, cable
centreline **168.64 mm ≤ 170 mm**. All other families fail or are not
needed; the binding numbers are below.

Basis state: origin/main = D-047 (Main Rev.10 symmetric, Wing Rev.6,
low-deck production case with the D-046 flip pocket A; FPC final).
Worker: Muse (Wonder). Date: 2026-11-18.

---

## 1. Measured basis (extracted, not assumed)

Body set: the #264/#275 fitted bundle (`fitlibF.bodies_at(17, -2.65)`,
343 bodies after exclusions) with Main-attached bodies flipped about
Z = 5.30, Type D FFC sheets as fused solids (z 2.825..3.075), ZIF
envelopes rebuilt per the #275 audit, and case pocket A applied
(X -6..+13, Y 28..48, floor cut to Z 0.60). All 345 solids
volume-validated > 0. The normal-pose cable model `Fly-170mm` is
excluded (it is the same physical cable in the other pose; Stage B's
4.157 mm³ "hit" against it was a modelling artefact).

- **Flipped J4**: on the case axis at (0, 20); header envelope
  x -4.325..4.325, y 16.455..23.714, z 2.6..4.7. Plug envelope
  5.0 x 3.5 x 1.30 at centre (0, 19.18, 3.45), z 2.80..4.10; hangs to
  Z 2.80, i.e. clear of every fixed body except its own header
  (engagement 35.4-36.5 mm³, expected).
- **Fly seat — verified in the adopted low-deck production tree**:
  board centre (0, -50.136) at 17 mm pitch (the D-037 seat carried
  over), board z 4.70..6.29 in the deck frame (s = -2.65); EZmate
  housing on the bottom face, x -3.3..3.3, y -51.28..-46.75,
  z 3.25..4.70; Fly plug envelope identical to the J4 plug at
  (0, -49.02, 3.45). USB-C mouth at the north wall opening (W16,
  mouth 0.30 mm inside the wall).
- **Cable model**: flat pack 4.5 x 1.2 mm (4 discrete wires, #232
  record), bend discipline centreline R >= 5 mm; plugs as above.
  Dress length is the Catmull-Rom centreline between plug centres.
- **Under-board field**: free span under the flipped Main is 3.10 mm
  (underside Z 4.70). Binding hang-downs near the corridor: flipped
  ZIF envelopes bottom Z 2.70; C26/27/28 study envelopes bottom
  Z 1.70 (west, x -12.5..-1.7, y 33.8..47.0 — inside pocket A plan);
  L1 envelope bottom Z 2.40 (x -4.2..1.2, y 29.2..33.8). Case joint
  screw posts (x 13..17, y -10..-6 and y 53..57; x -2..2 ditto) span
  z -4.6..5.0 and must be dodged in plan. Main H1 screw at (0, 9.27)
  spans the full z range.
- **Tray surface along any J4->Fly path**: NOT the Z 1.60 of the Wing
  bay. Probes (1x1 mm columns) on the route points read tray material
  up to **Z ≈ 2.0**, and **Z 3.0** at the pocket-A east rim (14, 47).
  This is why shallow reliefs fail (family A iterations below).
- **Bundle quirk (recorded)**: `tray-left` in this bundle is a
  fragment compound (7 solids, 7.4 mm³, z <= 0.4). It is
  bbox-disjoint from every cable in this study (cable z >= 1.30), so
  no gate number depends on it. See §2 for the intersect artefact it
  caused in an early self-test.

## 2. Method and verification

Repaired audit method (per the #248 lesson): boolean Common via
`Shape.intersect` (ShapeList-aware, volumes summed over pieces);
every solid volume-validated; gates run over the full fitted body set
with a bbox prefilter; own-engagement pairs (J4 header, Fly EZmate
housing, the body-set plug model) reported separately, never counted
as hits.

Positive controls (both exact):
- synthetic box pair, known overlap 13.5 mm³ -> measured 13.5;
- route A0 cable vs tray-right, computed from the STEP body cache ->
  **321.58 mm³, identical to the in-process value** (cache fidelity
  and the Common path both exercised on a genuine overlapping pair).

Correction of an earlier reading: the basis self-test "plug vs
tray-left = 22.75 mm³" was a **fail-open intersect artefact** —
`Shape.intersect` against the disjoint fragment compound `tray-left`
returns the first operand (the plug's own volume, 22.75) at any z
offset (verified in-process at dz 0 / -1.6 and z-centre 1.85, all
22.75, against a body whose zmax is 0.4). It was never evidence of
contact, and no family verdict uses it. The service sweeps in §4 were
re-checked with this in mind: they exclude own terms and their zero
results are against Solids, with the plug's swept volume
bbox-overlapping the trays — the readings stand (see §4 note).

## 3. Family verdicts

### A. Pocket extension / route channel — **PASS WITH CASE CHANGE**

Three iterations, all fully audited:

| variant | case change | length | unexpected contacts |
|---|---|---|---|
| A0 | none (ride on tray surface, pack z 1.60..2.80) | 148.5* | tray-right 321.58; joint-screw-1 post graze 0.162; ZIF-main-right graze 0.302 |
| A1 | shallow channel 0.35 deep (floor Z 1.25), same plan fixed vs posts/ZIF | 168.64 | tray-right **296.58** (channel too shallow — tray top is ~2.0, §1) |
| **A2** | **route channel, floor Z 1.20** | **168.64** | **none (0)** |

*A0's centreline was also 21.5 mm short of consuming the 170 mm
cable; A1/A2's dress adds a south serpentine under the Main plus two
S-bends in the north lane to land at 168.64 mm.

**A2 case change (the PO adoption item)**: a channel **7.5 mm wide**
following the route centreline (§4), cut from the local tray surface
(~Z 2.0, 3.0 at the pocket rim) down to a **floor at Z 1.20**;
**931.3 mm³ removed, all from tray-right** (tray-left 0.0). The
channel runs from the J4 exit apron into pocket A's east side, so it
reads as an extension of the adopted pocket. Remaining web under the
channel floor: the tray section below Z 1.20 is untouched — thicker
than pocket A's adopted 0.60 mm web. The channel does not break into
any boss/screw feature: the plan dodges both joint-screw posts and
the H1 screw (A1-fixed/A2 audits: zero hits on all screw/post
bodies), and the splice plate (top Z 1.20) is a separate body,
untouched, locally forming the channel floor with the cable 0.10 mm
above it. Disclosure: where the channel crosses the FFC formed
channels (2-3 points), the FFC channel floor is locally lowered to
Z 1.20 in a <=7.5 mm notch; the FFC sheet (z 2.825..3.075) bridges
the notch and is otherwise unaffected (gate: cable vs sheets = 0;
sheet support elsewhere unchanged).

### B. East-side channel (mirror of the failed west route) — **FAIL**

The Stage B west construction mirrored to the east (floor-level loop
in a 1.0-deep east channel, hop *over* the right FFC sheet at
y 1..-5): **FFC-sheet-right contact 3.215 mm³** at the hop transition,
plus tray-right 165.25 mm³ outside its channel. There is **no
east/west asymmetry to exploit**: the Type D sheets are exact mirror
images (inner edges at x = ±2.059), J4 and the Fly are on-axis, and
the hop failure reproduces in mirror (west 5.385 mm³ in Stage B vs
east 3.215 mm³ here — same mechanism, the sheet's fold-flat zone
leaves no transition window on either side). What differs in the
passing A2 is not the side but the crossing mode: *under* the sheet
(family C), never over it.

### C. Under-sheet crossing — **PASS (mechanism; used by A2)**

Straight test segment crossing under the sheets inside the tray
corridor, repaired-Common volume 0 at both levels; extrema distance:
- at tray-surface level (pack top Z 2.80): **0.025 mm** to the right
  sheet, 0.032 mm to the left — geometrically real but marginless;
- at A2 channel level (pack top Z 2.50): **0.325 mm** both sides.

Service interaction: the FFC is peel/lift serviced. In A2 the EZmate
cable lies in its own channel *below* the sheet's plane, so lifting a
sheet up and out is unobstructed by the cable. Removing the EZmate
cable is a slide-out along its channel (§4), not a vertical lift, so
the crossings never trap it. The crossing survives the sheet's
service motion.

### D. South-margin loop — **FAIL**

Best construction (exit south, dress to the true south margin at
y ≈ 72-74.5, return north on a lane west of the flipped ZIF
envelope): **centreline 191.72 mm > 170 mm stock — binding**. The
same construction also contacts both east joint-screw posts
(2.413 mm³ each, at y -10..-6 and y 53..57 on the return lane) and
tray-right 465.15 mm³. The Stage B estimate ("loop adds ~30 mm,
170 mm has the length") is **not confirmed**: measured, the
south-margin dress needs ~192 mm. Family F's 300 mm assembly could
fix the length but not the screw-post contacts, and the family is
dominated by A2 in any case.

### E. Fly orientation (rotate seat 180°) — **FAIL (cannot rotate)**

The Fly's mounting is symmetric (holes at ±9.50 mm, EZmate housing
centred at x -3.3..3.3), so the board would physically sit rotated —
but its USB-C mouth face is on the board's north edge, 0.30 mm
inside the north wall's W16 opening; rotating 180° puts the mouth
8.30 mm south of the opening, facing the case interior, and no
USB-C plug could ever reach it. One measured sentence: **the mouth
must stay at the wall, the wall opening is only on the north side,
so the seat cannot rotate.**

### F. Alternative stock cable — **NOT NEEDED (fallback recorded)**

Per the PO note, the 170 mm cable is on hand (x2) and family A2
closes with it, so F is a fallback only. Recorded for completeness
(search-result crawls, 2026-11-18, not live-checked): Molex
**36920-0403** Pico-EZmate 4-circuit assembly **300 mm** (DigiKey
stock 2,659, $3.66) and **36920-0402** **150 mm** (stock 4,359,
$3.48); pre-crimped leads **79758-1010** (300 mm, 28AWG, stock
6,581, $1.47) with housings **78172-0004** ($0.19). The 300 mm
assembly is the part that would reopen family D's length problem;
no family needs it.

## 4. The passing configuration (A2) in full

**Route** (case frame, mm; centreline control points, pack 4.5 x 1.2,
running level z-centre 1.90 in the channel, plugs at z-centre 3.45):

```
(0,19.18) J4 plug -> exit south, descend (0,22.5) (1.5,25.5) (4,28)
-> south serpentine under the flipped Main, east side:
   (11,32) (16.5,38) (17,44) U-turn (14.5,50) (9,48)
   north lane x=6.5: (6.5,41) (6.5,30) (7.5,22)
-> north lane x=10.5: (10.5,14) (10.5,5)
-> east S-bend (clears joint-screw-1 post at x 13..17, y -10..-6 in
   plan by passing east of its post circle): (20,-3) (20,-9)
-> (10.5,-15) west S-bend: (2,-21) (2,-27) (10.5,-33)
-> Fly return: (8,-39) (5.5,-44.5) rise (1,-46.6) (0,-48)
-> (0,-49.02) Fly plug
```

Centreline length **168.64 mm** (stock 170; the residual ~1.4 mm is
absorbed by the dress's natural bow — the cable is not tensioned).
Minimum bend radius in the dress: the serpentine U-turns run at
R ≈ 5.25-5.5 mm centreline, inside the modelled R >= 5 discipline.

**Audit result (full flipped fitted set, 343 bodies)**: unexpected
contacts **0**; engagement only with the J4 header (35.42 mm³), the
Fly EZmate housing (1.55 mm³) and the body-set plug model
(22.73 mm³) — all mating interfaces. Minimum distance from the
dressed cable to the right FFC sheet, measured by extrema on the
final solid: **0.314 mm** (left sheet 5.29 mm; gate sheet volume = 0;
family C's straight-crossing figure at the same z-stack is 0.325). USB-C insertion bodies were in the gate set:
0 contacts — insertion at the Fly is unaffected.

**Case change**: as §3-A2 (channel 7.5 wide, floor Z 1.20,
931.3 mm³ from tray-right, joining pocket A). No other case change.
No board change. Cable: the on-hand stock 170 mm part.

**Service sequence** (flipped pose):
1. Unplug either end by a straight downward pull: a 2.0 mm downward
   sweep of each plug box clears every fixed body in the model
   (swept-volume test, both ends, hits = none) — no board lift is
   needed for the EZmate plugs themselves. (The FFC ZIF actuators
   still need the board lift already established for flipped
   installation in #275; that is unchanged.)
2. Slide the cable out along its open-top channel toward the Fly
   (south) end; the under-sheet crossings are passed by sliding.
3. Refit in reverse: dress the cable in the channel, plug the Fly
   end, plug J4 last.

## 5. Real-cable measurements that would firm this up

The PO owns the physical cable; three modelled values decide the
margins above, and a measurement replaces each assumption:

1. **Flat-bundle thickness** (modelled 1.2 mm) — sets the
   under-sheet clearance in A2 1:1 (modelled 0.325 mm at channel
   level). Measure the 4-wire pack with calipers at a mid-span.
2. **Plug envelope** (modelled 5.0 x 3.5 x 1.30 mm, from the #275
   audit model, not a datasheet) — height decides the J4/Fly
   hang-down clearance (modelled: plug bottom Z 2.80 vs channel
   floor 1.20 and tray features).
3. **Minimum comfortable bend radius** of the real bundle (modelled
   discipline R >= 5 mm centreline; the dress's tightest U-turns
   are R ≈ 5.25-5.5 mm) — bend the pack 180° around the smallest
   radius former that does not kink or stress the wires and measure
   the former.

Cable length tolerance (170 mm nominal) is the fourth: the dress
consumes 168.64 mm of centreline, so a cable at the short end of
its tolerance still fits; a long-tolerance cable's extra length
absorbs as bow in the serpentine.

## 6. Files

- `.issue278-runtime/plan.md` — plan + measured basis extract
- `.issue278-runtime/basis.py`, `basis.json` — basis extraction
  (345 solids validated; bbox dump)
- `.issue278-runtime/route_audit.py` — run 1 (A0, D, C, sweeps, B/A1
  bodies; B and A1 gates completed in run 2 after a service restart)
- `.issue278-runtime/route_audit2.py` — run 2 (B gate; A1-fixed gate)
- `.issue278-runtime/decisive.py` — tray-left artefact resolution
- `.issue278-runtime/diag2.py`, `diag_tray.json` — tray-top
  diagnostic (intersection slices + probes)
- `.issue278-runtime/final_audit.py` — A2 final audit (positive
  controls + channel + full gate)
- `.issue278-runtime/audit278.json` — all gate numbers (machine
  readable; mirrored in flip-usb.json)
- `.issue278-runtime/bodies_cache/` — STEP cache of the 343-body
  fitted set (51 MB, on disk only, not committed)
- Logs: `basis.log`, `route_audit.log`, `route_audit2.log`,
  `diag2.log`, `decisive.log`, `final_audit.log`
