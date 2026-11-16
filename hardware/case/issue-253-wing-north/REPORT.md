# Issue 253 — Wing PCB north extension study

PO proposal (2026-11-16): keeping the D-037 case outer silhouette,
the Wing PCB's north side should have room to grow; study extending
it northward and relocating J_WING onto the extension.

**Verdict (plain): the space exists and the PCB side works, but the
north extension does NOT make the low deck achievable on its own.**
Stage 0 confirms up to ≈3.9 mm (17 mm) / ≈3.0 mm (16 mm) of usable
extension over the connector tab. Stage 1 proves the north-facing
connector (option N2) re-routes on all four Wing variants with only
known local-repair residuals. Stage 2 finds the binding squeeze:
a north-facing GH plug's own length plus the R5 westward wire bend
consume the very rim land the extension creates — plug tip to outer
silhouette is 1.25–4.25 mm for extension E = 3.5–0.5 mm, against a
5.0 mm bend reach (4.57 mm with a 45° pre-bend) — and two fitted
constructions of the north-channel harness scored gate 1 =
300/312 and 272/284, far worse than the round-18 incumbent's
96/98 at the same deck. The low deck is not unlocked by this
direction alone; the follow-up it motivates is option N3
(bay-facing connector axis, §2.4), not more northward depth.

All measurements are from the #248 fitted body set (plate top
Z13.55, repaired-audit machinery); verdicts are fitted, not screens,
except where a section explicitly says "screen".

---

## 1. Stage 0 — premise verified by measurement

Method: ray sampling in −Y (assembly north) through the fitted
solids (`wing_*`, `tray-*`) at the PCB band (Z 7.95, mid-PCB) on a
4 mm X grid, both pitches and sides, plus full tray Y-intervals at
the connector tab (X = ±16/24/32/40, Z 5.0 and 7.95 — identical,
the rim land is solid from the floor band up through the PCB band).
Raw data: `stage0-measurements.json`, `stage0-wall.json`; sketch:
`stage0-sketch-left17.png`.

Findings:

- **Pocket clearance is 0.501–0.503 mm along the entire north
  edge** (both pitches, both sides) — the designed 0.50 mm. The
  PCB already sits at its clearance; there is no slack to absorb.
- **North of the pocket wall is a solid tray rim land**, not air.
  Its thickness along the tab (Y-ray, from pocket wall face to the
  D-037 outer silhouette):

  | pitch | X=±16 | X=±24 | X=±32 | X=±40 |
  |---|---|---|---|---|
  | 17 mm | 8.99 | 7.84 | 6.80 | 5.86 |
  | 16 mm | 7.67 | 6.69 | 5.80 | 5.01 |

  The land is thickest at the inner (bay-side) end because the
  convex D-037 sweep does not hug the Wing's slanted north edge.
- **Max extension** keeping the 0.50 mm pocket clearance and
  ≥ 2.0 mm residual land (the #228 minimum-wall yardstick):
  E = land − 2.0 → **uniform over the tab: 3.86 mm (17 mm) /
  3.01 mm (16 mm)**, limited by the outer tab end; tapered,
  up to **6.99 mm (17) / 5.67 mm (16)** at the inner end.
- Limiters, named: the fixed outer silhouette + 2.0 mm residual
  land (binding); pocket clearance 0.50 (preserved, not consumed).
  The north raised strips sit at Z ≥ 13.55 above the plate and do
  not consume PCB-band space; the Fly seat zone (|X| ≲ 10) does
  not reach the tab (X ±16…40); no E-R post or plate spacer sits
  in the tab strip (the land intervals are continuous at both
  measured Z bands). The open samples at |X| ≲ 12 are the bay
  waist (no wall) — a different region, not tab space.
- Above the PCB band the same land carries the plate ledge;
  deepening the pocket in the PCB band steps the wall, it does
  not remove the ledge (ledger, §4).

**Premise: CONFIRMED, with numbers.** ≈3–4 mm uniform (more if
tapered) is really there. What it can buy is decided in Stages 1–2.

## 2. Stage 1 — connector relocation options + Wing re-route

J_WING today: SM14B-GHS-TB on the existing north tab, anchor case
(±27, −41), pin row Y = −42.85, opening facing SOUTH; wires exit
south and run under the board (connector/placement.json, #235).

### 2.1 Options

- **N1 — translate north, keep south-facing opening.** Connector
  moves E mm north on the extension; plug/wire exit stay south.
  Buys the harness only a 3.5 mm shorter under-board run.
- **N2 — rotate 180°, opening faces NORTH.** Wires exit north into
  a channel cut in the rim land, run along the wall to the bay
  waist, then south to Main. The under-Wing traverse disappears.
  Fanout permutation at the pads reverses (pin 1 ↔ pin 14 ends) —
  the round-4 lesson applies: correspondence derived from the
  physical presentation; D-024 cavity order at the connector is
  unchanged (the board fanout absorbs the reversal).
- **N3 — bay-facing axis at the extension's inner corner.** Pad
  row runs along the slanted edge, wires exit toward the bay with
  no northward bend at all. Formulated but NOT taken to routing in
  this pass (see §2.4).

### 2.2 KRT re-route feasibility (D-021 yardsticks, Rev.4 pipeline)

Modified inputs built with pcbnew from the Rev.4 inputs: J_WING
translated by case-north 3.5 mm in native coords (per-variant
transform solved from pads 1/14 against placement.json), N2
additionally rotated +180°. Routed with the #235 KRT invocation
(0.10 tracks / 0.30 power, clearance 0.10, via 0.60/0.30,
escalation off), single pass, no cleanup/repair pipeline.
Verdicts are KiCad DRC on the routed boards (`stage1/*-drc.json`);
Rev.4's own first passes needed the same cleanup + local-repair
rounds to reach 0/0, so residuals are judged by class.

| variant | option | DRC | unconnected | residual classes |
|---|---|---|---|---|
| 17L | N1 | 15 | 5 | pads 1–3 + escapes cross the **un-extended** Bézier edge (10× copper_edge_clearance); GND/HALL_5V/MUX_A0/A1/WING_EN stubs |
| 17L | N2 | 3 | 1 | MUX_OUT_B stub + dangling via (local-repair class, cf. #235 round 3); MP pad copper_edge_clearance (needs the tab extension); 1 silk warning |
| 17R | N2 | 2 | 0 | MP pad edge clearance + silk warning — **fully routed first pass** |
| 16L | N2 | 2 | 1 | HALL_5V stub at U_MUX_C.13 — the exact residual #235 round 2 showed and round 3 closed by local repair |
| 16R | N2 | 2 | 0 | MP pad edge clearance + silk warning — **fully routed first pass** |

- **N2 fanout is FEASIBLE on all four variants.** Every other
  placement byte-identical to Rev.4; only J_WING moved/rotated.
  The two residuals (MP-pad edge clearance; one local-repair net
  on the left variants) are the classes the Rev.4 qualification
  already knows how to close; the MP-pad item is precisely what
  the production tab extension (Stage 0: 3.0–3.9 mm available)
  removes.
- **N1 is NOT demonstrated**: with the outline un-extended its
  pads sit across the Bézier edge line and the router cannot
  escape them; a fair N1 test needs the Bézier split/re-shape
  first. N1's harness upside is small (§2.1), so it was not
  pursued further.
- Floor-gap yardstick (Rev.4): the N2 mated envelope is the same
  4.35 mm part rotated; underside clearance to the tray floor is
  unchanged (≥3.15 mm after allowance) — the plug now occupies
  the rim-land channel instead of the pocket mouth (Stage 2).
- Not run in this pass (belongs to a Wing Rev.5 qualification):
  via-pad audit (≥0.10 floor / 0.125-class target), electrical
  requal Vfar at 127 mA, ERC-equivalent contract check. The
  Stage-1 claim is fanout feasibility only.

### 2.3 What a Wing Rev.5 respin reopens (backtracking axis)

D-039 adoption requal: placement certificate, DRC/connectivity,
via-pad audit, electrical requal, tray-pocket fit, harness
re-qualification — i.e. the full #235 gate set on a new outline.
The PCB cost delta is small (outline grows ≈3.5 mm × tab width;
same layer count/material). The case delta is interior-only (§4).

### 2.4 N3 note

Stage 2's bend finding (§3.2) is exactly what N3 avoids: with the
connector axis pointing at the bay, wires never bend northward.
N3's own open questions are the pad-row fit along the slanted
edge and a third fanout permutation. It is the named follow-up,
not part of this pass's verdicts.

## 3. Stage 2 — harness at the low deck with N2

### 3.1 Construction

Fitted bodies per pitch from the #248 set, modified: J_WING
bodies rotated 180° about the case anchor (±27, −42.60) and
translated north (E = 3.5 in iteration 1; E = 2.0 in iteration 2);
a wiring channel cut into each tray's north rim land
(X ±3.5…36.5, Y −52.6…−49.3, Z 2.2…10.0; residual outer land
≥ 2.0 mm at every tab X — verified against Stage-0 intervals).
Wires (28, strict R5 build, fitlib18): exit the plug northward,
gather into a 3 × 6 (Y × Z) lane grid inside the channel, run to
the bay waist, south along the bay margin, climb onto the
**unchanged round-9 [bow, P, G, ep] Main approach**. Scored with
the repaired audit (round-10 standard), same as the frontier
study. Incumbent at this deck: round-18 gate 1 = 96 @17 / 98 @16.

### 3.2 Results — and the binding squeeze

| iteration | E | built | gate 1 @17 | gate 1 @16 | longest finished |
|---|---|---|---|---|---|
| 1 | 3.5 | 28/28 | 300 | 312 | — |
| 2 | 2.0 | 28/28 | 272 | 284 | 135.63 mm (≤200 PASS) |

Iteration 2 by body (@17): every wire still grazes its own
J_WING body (2–10 mm³), tray (14/side), Wing PCB (14/side);
WW = 156 pairs (both constructions' lane/climb fans cross);
Main-GH reservations 6/side and C5 envelopes 3/side are inherited
from the unchanged tail. No wire×Fly hits (Fly 170 gate preserved);
USB insertion untouched (PASS inherited).

Why it does not close — the geometry, measured:

- The mated plug + modeled tails are 8.15 mm long. Facing north
  from the moved header, the **plug tip lands at Y = −53.75
  (E = 3.5) / −52.25 (E = 2.0)**, i.e. **1.25 mm / 2.75 mm from
  the outer silhouette** at the inner tab (outer face −55.02).
- From the tip, an R5 bend to westbound displaces the centreline
  a further **5.0 mm north** (R·(v_in + v_out) for a 90° planar
  bend; 4.57 mm for a 45° pre-bend then diagonal). Even at
  E = 0.5 (tip −50.75, 4.27 mm to the face) the full bend does
  not fit; the 45° scheme is ≈0.1–0.3 mm short at the inner pins
  (X ±19…24, outer face −55.0…−55.3). That is a thin-margin
  failure of exactly the class PO priority 2 excludes.
- The fitted constructions confirm it from the other side: the
  exit/gather zone is where the wire×J_WING-body and wire×tray
  hits concentrate, and the lane fan that must form inside the
  shallow channel crosses itself (WW 156) before the route even
  reaches the bay. Two constructions do not prove impossibility —
  but combined with the bend-reach arithmetic above, the squeeze
  is structural, not a tuning gap: **the extension's depth is
  spent by the connector that was supposed to benefit from it.**

### 3.3 Service, other gates

- Gate 2 (length): PASS (135.63 mm worst, iteration 2).
- Gate 3 (unplug-first service): NOT qualified — the fitted route
  is not clean, so no motion audit was run. The intended
  procedure (unplug at Main, slide the harness west/east out of
  the channel, lift the Wing with its plug mated) is recorded
  here as design intent only. Note the Wing plug itself can no
  longer be the service disconnect: axial extraction northward
  has ≤1.25–2.75 mm of room, not the ≈6 mm needed.
- Gates 4/5 (Fly 170, USB): PASS inherited — no hits, geometry
  untouched. Gate 7 (print envelopes): outer silhouette
  byte-unchanged; the channel is interior. Gate 6 (Junana
  physical): OPEN, inherited, PO-side.
- Heights above 13.55 were NOT swept for this direction: the
  binding constraint (plug tip vs silhouette, in the PCB plane)
  is deck-height-invariant, so the frontier method would repeat
  the same wall at every height.

### 3.4 Compatibility with Issue #252 (candidate C, carrier split)

Compatible but not curative. The bay/waist space C needs is
unchanged, and a split point at the waist (where the north
channel opens) is geometrically natural; C would also restore a
service disconnect near the Wing (the carrier), which N2's
service procedure lacks. But C does not remove this study's
binding constraint — the Wing plug's northward bend happens
upstream of any split. C + north extension should not be expected
to beat C alone at the low deck on this evidence.

## 4. Case-delta ledger (interior only; silhouette byte-unchanged)

- Tray pockets deepen northward over the tab strip by E
  (≤3.86 @17 / ≤3.01 @16 uniform; tapered more at the inner end),
  residual rim land ≥2.0 mm; pocket wall steps at the plate-ledge
  band (ledge support land narrows by E, ledge itself unchanged).
- North rim-land wiring channel (Stage 2 geometry): X ±3.5…36.5,
  Y −52.6…−49.3, Z 2.2…10.0, both trays; opens into the bay waist.
- Wing PCB outline: tab extension as above (Wing Rev.5);
  tray pocket follows. Plates, shells, strips, Fly seat, Main:
  unchanged. No E-R post or spacer moves (none in the tab strip).

## 5. PO-priority assessment

- **Cost:** PCB +≈3.5 mm of outline (negligible per-board delta);
  tray reprint is filament-class. The real cost is engineering:
  a Wing Rev.5 requalification round (§2.3).
- **Backtracking:** adopting the extension reopens D-039. The
  Stage-2 result says the reopening would NOT buy the low deck —
  high backtracking risk for no gate closure. The bend margin at
  the inner pins (≈0.1–0.3 mm short in the best scheme) is a
  priority-2 thin margin even where it "fits".
- **Freedom:** the channel + extension do not foreclose Δ+6
  (D-041) or candidate C; N3 remains open and is arguably
  strengthened as a direction (it spends the extension on a
  bay-facing axis instead of a north-facing one).
- **Speed:** not weighted (PO: lowest).

## 6. Verdict

- Premise: **true** — 3.86 mm (17) / 3.01 mm (16) uniform, more
  tapered (Stage 0, measured).
- Connector relocation: **N2 is PCB-feasible on all 4 variants**
  (Stage 1, KRT + DRC, local-repair residuals only).
- Low deck via north extension: **NO** — not at 13.55, and the
  binding constraint is height-invariant, so not at 15.0/16.2
  either, on this evidence. The plug + R5 bend consume the land
  (bend reach 5.0/4.57 mm vs 1.25–4.27 mm available).
- With what else: the only named lever left in this direction is
  **N3 (bay-facing axis)**, which removes the northward bend by
  construction; it needs its own Stage-1 routing pass before any
  harness claim. Candidate C is compatible but does not change
  the bend arithmetic.

## 7. Draft decision text (for PO gate; decisions.md NOT edited)

> D-04x (draft) — Wing north extension / connector relocation
> study (Issue #253): the north rim land affords a measured
> 3.86 mm (17 mm) / 3.01 mm (16 mm) Wing PCB extension under the
> unchanged D-037 silhouette. A north-facing J_WING (Rev.5
> candidate) is fanout-feasible on all four variants, but the
> low-deck harness does not close in this direction: the mated
> plug tip sits 1.25–4.25 mm from the outer silhouette against a
> 5.0 mm R5 bend reach, and fitted north-channel constructions
> score gate 1 = 272–312 vs the incumbent 96–98. The extension
> is NOT adopted as a low-deck enabler. The bay-facing connector
> variant (N3) is recorded as the remaining named direction;
> D-039 (Wing Rev.4) and D-041 (Δ+6 case) stand unchanged.

## Round 2 — corrected premise: minimal strip, connector south, 3D bend examined

PO correction (2026-11-16): do not maximise the extension — open only a
connector's worth of space, place the connector as far south as its
footprint allows, and use the tall volume above the north margin for a
3D climb-and-turn. Round 2 tests exactly that.

### R2-1 Strip budget (extension E minimal)

Placement variable t = northward shift of the 180°-rotated SM14B-GHS-TB
from the Rev.4 anchor (round 1 used t = +3.5). Binding element at every t
is the MP (mounting) pad's copper-to-edge clearance against the
un-extended D-037 outline; board rule = 0.30 mm.

| quantity | 17 mm | 16 mm |
|---|---|---|
| MP edge clearance at t = +3.5 (round 1) | 0.000 (violates 0.30 rule; matches round-1 DRC) | 0.000 |
| south shift Δ* restoring the 0.30 rule | 1.887 | 1.968 |
| t_min (northernmost legal placement) | +1.613 | +1.532 |
| **MP edge clearance at t = 0 (rotate in place, extension = 0)** | **1.889** | **1.815** |
| nearest foreign pad at t = 0 (TP_W_A1) | 4.7 (all variants) | 4.7 |

**Adopted placement: t = 0 — the rotated header fits the EXISTING tab
with zero outline extension**, >1.5 mm clear of the edge rule. The strip
budget is therefore [header footprint + plug + exit room] only, as the PO
directed; no PCB area is added at all. Practical southward limit is the
fanout/test-pad field (TP_W_A1 at 4.7 mm), not copper.

Plug tip at t = 0: case Y = −50.25 (body spans Y −50.25..−42.1).
Tip-to-silhouette at the pin row (17 mm): inner pins ≈ 4.86 mm, outer
pins ≈ 5.54 mm. Planar R5 westward turn needs 5.0 mm of northward reach
(inner pins short by ≈0.14); a 45° pre-bend needs 4.57 mm (margin ≈0.29,
thin). At 16 mm the silhouette face sits ≈1.4 mm closer, so tip-to-face
≈ 3.4–4.1 mm and even the pre-bend need is unmet.

Fanout confirmation at t = 0 (fresh KRT route of textually shifted input
boards + KiCad DRC): **17L 0 violations / 0 unconnected; 17R 0/0; 16L
0/0; 16R 2 via_dangling + 1 unconnected** (one stub of the same
local-repair class #235 round 3 closed; flagged, not repaired here).
t = 0 is strictly better than round 1's t = +3.5 screen (which left 17L
with the MP edge violation and a MUX_OUT_B stub). Round 1's N2
position-independent fanout verdict (pad order along the row) carries
over unchanged.

### R2-2 The at-plug 3D climb-and-turn: decomposed failure

Profiles scanned numerically (integrated centrelines, azimuth 0→90°
while climbing ΔZ up to 15.15 mm into the under-strip volume; min
circumradius over ~1 mm triples; script r2_curve.py):

- Best min radius over all variants (σ profile × entry radius × growth
  delay): **0.91–1.70 mm — R ≥ 5 is not approached in any variant.** The
  pitch rotation concentrates where the arc speed is lowest (profile
  ramp at the bottom, level-off at the top).
- Analytic bound: pitching from northbound-horizontal to climb tilt β
  on an R ≥ 5 arc costs northward reach 5·sin β (≈4.9 mm at β = 80°,
  ≈4.3 mm at 60°) before the wire is even established on its climb.
- Available centreline reach budgets (exit line to notch wall =
  silhouette − 2.0 mm land − 0.5 mm wire surface): **worst wire (inner
  pins) = 1.66 mm @17 / 0.27 mm @16.** Even with land and surface margin
  both set to zero, the 17 mm inner-pin absolute maximum is 4.36 mm <
  4.3–4.9 mm; 16 mm reaches only ≈2.9 mm.
- Binding body: the tray rim land / D-037 outer silhouette at the tab.
  Round 1's "height-invariant squeeze" verdict is confirmed and
  strengthened: the squeeze is not planar-only — it is the R5 pitch-up
  reach against the silhouette, and no profile shaping removes it.
- Single closing change: none inside the frozen set. Cutting the notch
  through the wall (land 2.0 → 0) still leaves 17 mm at 4.36 mm < 4.9 mm
  and is structurally absurd; moving the connector south does not deepen
  the notch (the notch wall, not the tip, sets the budget).
- Companion bound (fan): the exit row is a comb along the travel
  direction (pitch 1.25 mm vs wire OD 1.0 mm). Any fan from the common
  exit point puts adjacent blends ≈0.1–0.5 mm apart — below OD — which
  is the analytic counterpart of round 1's WW = 156 in the channel.

### R2-3 Constructive fallback built and audited: low channel + waist climb

Construction: t = 0 connector; wires exit into the low north channel
(per-pitch cut, ≥2.0 mm land retained: north edge −52.6 @17 / −51.6
@16, Z 2.2–10.0), fan smoothly (smoothstep blend over each wire's own
westward travel, fan completes at X = ±9) to a (Y,Z) lane grid, then
climb at the waist — where the bay margin has horizontal room — onto
the round-9 tail at the round-1 junction. This spends the tall volume
at the waist/under-shell region instead of at the plug, where the R5
pitch-up has room. Fitted repaired audit (round-10 standard):

| gate | 17 mm | 16 mm |
|---|---|---|
| wires built | 26/28 (Wire-03 L/R fail R5 trim at a fan corner; excluded — counts are lower bounds) | 26/28 |
| **gate 1 unexpected contacts** | **261 (WW 155 + WF 106)** | **292 (WW 156 + WF 136)** |
| gate 2 longest finished | 139.37 mm PASS | 140.46 mm PASS |
| gate 3 service | not qualified (no fitted-clean state) | not qualified |
| gates 4/5 (Fly 170 / USB) | NOT inherited clean: WF includes Fly-seat hardware hits (screw-fly MH1/MH2, Fly body, 6 wires) at the junction | same |

WF composition @17: tray 13/side, J_WING-N2t0 body 13/side, plate
7/side, Fly-seat hardware 6, Main-GH drawing-bound 6. WW structure is
the comb signature: Wire-01 (westernmost exit) crosses nearly every
other wire — the analytic fan bound of R2-2 made visible. Comparison:
round 1's abrupt fan scored 272–312; the smooth staggered fan + waist
climb improves this only to 261/292, the same class, and far from the
#248 incumbent's 96/98 (itself failing). The fan, not the fan's
polish, is the binding constraint.

### R2-4 Verdict

**The north-extension direction does NOT make the low deck achievable,
with the PO's corrected premise applied in full.** The placement half
of the premise is vindicated — the connector needs no extension at all
(t = 0, fanout closes on 3 of 4 variants, better than round 1) — but
the harness fails for placement-independent reasons, now decomposed
to numbers: (1) the at-plug 3D climb-and-turn is impossible at R ≥ 5
(pitch-up reach ≈4.3–4.9 mm vs usable budgets 1.66 mm @17 / 0.27 mm
@16; even the zero-margin absolute maximum at 17 mm inner pins,
4.36 mm, is below the 80°-climb need of ≈4.9 mm); (2) the low-channel
fan is comb-bound (two fitted constructions, 272–312 and 261/292,
WW ≈ 155 in both). **Single binding number: R5 pitch-up reach
≈ 4.9 mm vs tip-to-silhouette 4.86 mm at the 17 mm inner pins —
negative before any land or surface margin is applied.** The
extension is not adopted as a low-deck enabler; D-039 and D-041 stand.
The bay-facing variant (N3, named in round 1) remains the only
untested connector direction; it avoids the north wall entirely by
construction but was not routed in this study.

### Case-delta ledger (round 2 changes vs round 1)
- North channel: north edge now per pitch (17: −52.6 as round 1;
  16: −51.6) so the ≥2.0 mm residual land holds at BOTH pitches (round
  1's single box left only ≈1.03 mm land at 16 mm — disclosed here).
- No through-rim tall notch is cut in the v2 construction (the climb is
  at the waist); the under-strip volume is not consumed by the harness.
- PCB outline extension: 0 (t = 0) — round 1's tab extension is NOT
  needed for the connector itself.

### Candidate C compatibility (updated)
Unchanged in substance: a waist carrier split remains geometrically
compatible (the v2 route passes the waist, a natural split point) and
would restore a near-Wing service disconnect. It does not cure the
Wing-side fan/exit geometry, which is upstream of any split.
