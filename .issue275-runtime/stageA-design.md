# Issue #275 Stage A — Main symmetrization design study (FPC premise)

Study only; no board was modified. All board numbers are measured from the
saved Rev.9 board file (`issue-270-main-rev9/main-rev9/main.kicad_pcb`,
extract: `.issue275-runtime/extract.json`); case numbers from the #261/#264
records and the low-deck production tree README.

Frames: board frame = KiCad (mm, Y-down). Fitted case frame is a pure
translation of the board frame — **case = (board_x − 100, board_y − 70)** —
derived from `issue-263-implementation/pose-verification.json` (J2/J3
origins match to 0.001 mm at both sites) and cross-confirmed by the H2/H3
openings recorded in #248 at case (∓31.892683, 64.40).

## 0. Measured starting point

- Symmetry axis: **board x = 100.000 = case x = 0**. The board body is
  already mirror-symmetric (south edge 100 ± 33.8927 exact; north vertex
  flat centred on 100; J4 and H1 exactly on axis). Only the Stage 2d tab
  regions and the connector poses break symmetry.
- J2 pose: centre (76.048074, 112.073215), rot **+38.0°**.
  J3 pose: centre (124.254798, 111.823895), rot **−43.0°**.
- Asymmetry to eliminate: centre offset **0.392 mm**, rotation **5.0°**
  (the Stage 2c skew pair 22°/17° seen from the board edges).

## 1. Symmetric connector pose pairs

Mirror operator about x=100: (x, y, θ) → (200−x, y, −θ).

| candidate | changed site | new pose (board) | centre shift | max pad displacement |
|---|---|---|---|---|
| (a) mirror J2 | J3 | (123.951926, 112.073215), −38.0° | 0.392 | 0.640 |
| (b) mirror J3 | J2 | (75.745202, 111.823895), +43.0° | 0.392 | 0.649 |
| (c) meet-in-middle | both | J2 (75.896638, 111.948555), +40.5°; J3 (124.103362, 111.948555), −40.5° | 0.196 each | 0.322 / 0.317 |

**Tab consequences.** Tabs become a mirror pair in all three.
(a) both tabs take the J2 pattern: front 19.228 mm, rising corner d = 7.35,
and the diving corner d = 0.15 whose build fillet is **capped at R0.50 by a
0.1739 mm wall stub** (Stage 2d §6.1) — that capped feature would exist on
both sides. (b) both tabs take the J3 pattern: front 17.950 mm, rising
corner d = 6.95, no capped-fillet feature anywhere in the Stage 2c/2d
record. (c) both tabs are new shapes (front ≈ 18.6 mm class), neither
inherited. All patterns are inside the D-037 silhouette (each is an
existing, audited tab shape mirrored about the case centreline, or an
interpolation of two such); Stage B re-audits.

**Fanout room (measured).** Capsule sweep of the FH12 pad lands (0.30 ×
1.30 mm land model) against all 1,268 segments + 138 vias of the saved
board: in the current pose and in **every** candidate pose, **no
foreign-net segment or via comes within 0.30 mm of any pad** — all copper
in that neighbourhood belongs to the site's own 14 nets (sweep validated:
with no net exclusion, 56 own-net items register < 0.30 mm at J2, the
connected fanout stubs overlapping the capsule model as expected). The
re-route at a changed site is therefore confined to that site's own
fanout escape; no component, via field, or foreign route blocks any
candidate rotation. (Zones/pours are outside the sweep; pour interaction
at outline deltas has been fringe-only in every #263/#270 round and is
re-filled under the project's clearance rules in Stage B.) Nearest fixed
obstacles to a changed site are ≥ 23.9 mm away (candidate (b) J2 centre →
U6 23.9 mm, L1 27.7 mm, J4 32.6 mm); the only tight neighbour is the tab
outline itself, whose pad clearance is 1.4864 mm at the J3 pattern
(Stage 2d binding value) and is inherited by symmetry under (b).

**FFC path impact.** The mouth of a changed site moves 0.392 mm and
5.0°; the final-approach fold (F_V7 role) re-derives, and the length
change is far inside the S-pair absorption (detents cover 148–156 mm
measured cable; nominal route ≈ 153 mm). Cable length class unchanged:
152 mm remains the only viable family length. Under (a) the left route
stays proven and the right becomes its mirror; under (b) vice versa;
under (c) both routes re-derive.

**Recommendation: (b) — mirror J3 onto J2.** By the PO priority order:
- *Cost:* same parts, same board size; one site's fanout re-route (ties
  with (a); (c) re-routes both).
- *Low rework / margin:* J3 is the electrically binding site (branch
  240.9 mΩ; Vfar 4.754 V is the configuration floor) — (b) leaves J3
  bit-identical, putting zero new electrical risk where margin is
  thinnest, while J2's branch (114.2 mΩ) has > 2× headroom to absorb its
  re-route. Geometrically (b) deletes the board's only capped-fillet
  feature (J2's R0.50 / 0.1739 mm stub) instead of duplicating it onto
  the worst site, as (a) would.
- *Freedom:* the pair is symmetric under any candidate; (b) additionally
  makes the whole left interconnect (tab, notch, FFC route) the mirror
  of the proven right side.
- (c) is rejected: it disturbs both sites and inherits neither proven
  tab, for no benefit over (b).

## 2. Mounting holes — already symmetric; no moves

Measured from the saved board (all NPTH, drill Ø2.2):

| hole | board | case | mirror offset |
|---|---|---|---|
| H1 | (100.000000, 79.267949) | (0, 9.268) | 0.000 (on axis) |
| H2 | (68.107317, 134.400000) | (−31.893, 64.400) | 0.000 (= H3) |
| H3 | (131.892682, 134.400000) | (+31.893, 64.400) | 0.000 (= H2) |

**Full mirror symmetry already exists; no hole moves, so no on-board
collisions and no case boss moves.** The case side was built on these
exact coordinates (#248 record: Ø5.10 through-openings at
(∓31.892683, 64.40); #261 REPORT discusses the H1/H2 screw seats in the
tray as designed). Boss symmetry in the printed tray inherits from the
mirrored case design and is re-verified by the Stage B fitted audit.
Flipped-install consequence: the same three bosses accept the board in
either orientation with no case change.

## 3. Flip feasibility (FPC premise)

### (a) FFC contact faces — CLOSES, via Type D cable or an even fold count
Bookkeeping per #264 §3.2 (FH12-14S-0.5SH(55) is bottom-contact):
Wing sites (underside-mounted): springs face world UP → cable contacts
must face **UP** at the Wing tails. Normal Main (top-mounted): springs
DOWN → contacts **DOWN** at the Main tail → odd parity required; the
#264 plan's 5 folds close it. **Flipped Main: its connectors hang below
the board exactly like the Wing's — springs face UP → contacts must
face UP at the Main tail → EVEN parity required.** The #264 5-fold
Type A plan therefore does **not** close for a flipped Main. Two
closures: (i) **Type D cable** (opposite-face contacts — the family's
parity escape hatch, recorded in #264 §2) with the same 5-fold
plan-view geometry; (ii) Type A with an even fold count, which disturbs
the S-pair length absorption and is the worse option. Either way the
route's Z-profile near Main re-derives: the mouths move from the
z 6.90 top plane to the underside plane (z ≈ 2.95 class, the Wing ZIF
slot level). Service note: flipped FH12 actuators face the tray, so
the service procedure changes (board lift before actuator access) —
Stage B service gate must re-qualify it.

### (b) Flipped component clearance — PASS with a shallow pocket recommended
Datum (production tree): Main underside plane Z4.70, tray floor Z1.60 →
3.10 mm free below the flipped board. Tallest Main components
(datasheet heights; BOM of the Rev.9 package):

| part | height | lowest point flipped | residual to floor |
|---|---|---|---|
| C26/C27/C28 — TDK C3225X7R1C226M (1210) | 2.5 | Z2.20 | **0.60** |
| L1 — Coilcraft XFL4020-152MEC | 2.1 | Z2.60 | 1.00 |
| J2/J3 — FH12-14S-0.5SH | 2.0 | Z2.70 | 1.10 |
| J4 — Molex 781710004 header | 1.55 | Z3.15 | 1.55 |
| C23/C24 — 22 µF 0805 | 1.25 | Z3.45 | 1.85 |

Nominal stack passes with **no pocket**, but the 0.60 mm residual at
the three 1210 caps is thin once rib height on the "1.60 ribbed" floor
and print tolerance are counted. A **1.0 mm-deep pocket** under the
power-stage field (case x −6…+13, y 28…48; holds C26–C28, L1, U6)
restores the residual to 1.60 mm. The pocket hits nothing: the FPC
channel corridor runs north of the field, the H1 boss (case (0, 9.27))
is outside it, and no component sits within 10 mm of a hole centre
(nearest: J4, 10.7 mm from H1 — clear of the Ø4.5 boss). Remaining
floor thickness under a 1.0 mm pocket is a Stage B confirmation item.
The flipped FH12 envelopes occupy z 2.70–4.70 at the tabs — the same
envelope class as the Wing ZIFs; tab reliefs re-derive in Stage B.

### (c) J4 / Fly — NO as-is; conditional with a pocket + looped approach
J4 sits on the axis (board (100, 90) → case (0, 20), rot 180°), so the
flip keeps its XY position but faces it DOWN and mirrors its pin row.
Two geometric blocks with the shipped 170 mm EZmate cable:
1. **Stack:** the mated plug (≈1.55 mm) plus its wire-exit bend
   (≥ 2.0 mm for the cable's wire class) needs ≈ 3.55 mm under the
   board; the vertex field offers 3.10 mm. Does not fit as-is.
2. **Pin order:** the mirrored row swaps the VBUS/GND ends relative to
   the cable's verified presentation (measurement A) unless the plug
   approaches rotated 180° in plan — i.e. a looped approach from the
   south, adding ≈ 30 mm of path. The seat-to-J4 span is ≈ 70 mm
   class, so 170 mm has the length; the stack is the binding block.
Verdict: **not reachable as-is**. With the (b) pocket programme
extended north to the vertex field and the looped approach, it becomes
geometrically possible — Stage B audits the stored-cable dressing.

### (d) Electrical identity under flip — CONFIRMED, EN-only swap
Pad-net assignments read from the saved board: **J2 and J3 carry the
identical assignment on all 14 pads except pad 8** — J2 pad 8 =
`WING_EN` (EN0), J3 pad 8 = `MUX_EN1`. (Numbering note: the enable is
footprint pad 8; D-024's GH pin 7 maps to FH12 pad 8 in the Main
assignment because the interleaved GND pattern differs.) All other
signals (HALL_5V, GND ×6, MUX_A0/A1/A2, MUX_OUT_A/B/C) are common per
D-024, and both MP pads are unconnected. Lane-order parity under flip
closes by mirror symmetry: the #264 routes are plan mirrors of each
other (§3.1) and the assignments are mirror-identical except EN, so
the flipped assembly is the mirror image of the verified one. The
only functional swap is **EN0 ↔ EN1**, absorbable in firmware (assert
the other EN per side). **No exception found.**

## 4. Wing impact — scope only
Under recommendation (b) the right tab is unchanged, so the **16R/17R
notches stand as adopted-pending** (seam 0.5585). The left tab becomes
the mirror of the right tab, so **16L/17L notch chains re-derive as the
mirror of the right notch chain** (the Stage 2e simplified chain,
7 elements, mirrored), seam target ≥ 0.55 (expect 0.5585 class),
overlap 0, both pitches. Left tray relief recomputes (expect the
mirror of the right side's 6.305 mm³). Wing copper and routing are
untouched (outline-only; pour fringe re-fill per the #263 procedure).
Fitted audit re-runs for the final pair at both pitches, plus the new
flipped-Main configuration (§5).

## 5. Stage B brief outline (implementation)
1. New tree `issue-275-main-rev10/` from Rev.9. J3 footprint, fanout,
   and tab byte-identical. J2 footprint moved to
   (75.745202, 111.823895), rot +43.0°; J2 fanout re-escaped (own 14
   nets only; local change, Rev.5-J4 precedent).
2. Outline: left tab chain := mirror of the right tab chain (including
   the base step); verify pad-corner clearance ≥ 0.70 (expect
   1.4864 class by symmetry), copper cuts 0, min edge-to-copper
   ≥ 0.323 class, inside D-037 silhouette.
3. Gates (#263 yardsticks): DRC profile no new class vs Rev.9,
   unconnected 0, wrong-net 0, ERC 0, via-pad min ≥ 0.10 floor
   (0.1596 class target); extraction re-run — J3 figures unchanged by
   construction, J2 branch + configuration Vfar ≥ 4.60 required.
4. Wing 16L/17L notch mirror re-derivation; seam measured from the
   saved boards; packages for changed boards regenerated
   (DRAFT / NOT FOR ORDER).
5. Case: left tray relief mirror; flip pocket (1.0 mm, power field;
   J4 vertex extension decided by the (c) audit); flipped-pose audit
   bodies (Main component envelopes on the underside, flipped ZIF
   envelopes at the underside mouth plane, Type D / even-fold cable
   variant, J4 looped plug body).
6. Fitted audit: gate 1 = 0 and service gate for BOTH poses (normal +
   flipped) at both pitches; FFC face/order mapping re-computed for
   the flipped configuration (face_mapping machinery of #264).
7. REPORT with the full gate table + draft adoption line (Rev.10 as
   the symmetric, flip-installable Main). PO adoption remains a gate;
   no order impact (Order 1 already targets the Main shape — quote
   refresh class unchanged: same size, same parts).

Figure: `.issue275-runtime/fig-sym-tabs.png` (Rev.9 outline vs
candidate (b), from measured geometry; copied to the goal files/).
