# Issue 264 — Stock FFC, folded, as the cable for the adopted FPC architecture

**Verdict: REALISABLE at plate Z10.90 (the adopted D-042 height), with named
conditions.** A stock Molex Premo-Flex FFC (152660149, 152 mm, Type A),
folded on a 3D-printed jig into the #261 route, passes the fitted contact
audit (gate 1) with **zero unexpected contacts in the nominal
configuration**; the fitted service motions (gate 3) pass with one named
residual; the electrical target passes on both the assumed and the
pessimistic lane cross-section. Two sensitivity grazes at the stacked
allowance extreme are named in §5.3 (they do not occur at the nominal jig
detent). The paper guarantee for the cable's lane resistance stays open
BY DESIGN (PO's acceptance, 2026-11-17): it is closed physically by the
post-purchase measurement procedure in §6.3, whose acceptance threshold
has ~13x margin over the expected reading. Cost per keyboard drops from
the custom FPC's $50–150/iteration class to ≈$10–18 for the first
iteration (two cables + jig prints) and ≈$6–12 per re-iteration.

## 1. What was asked, what is frozen

PO (2026-11-17): D-042 adopted the FPC architecture with a CUSTOM FPC; on
cost grounds PO asked whether a STOCK (ready-made) FFC, folded to follow
the bent plan path, can realise the same configuration — accepting that
the electrical guarantee cannot be closed on paper (it will be closed by
measuring the purchased cable) — with a 3D-printed folding jig as part of
the method. Boards stay exactly as in #261: Wing Rev.5 / Main Rev.8 ZIF
poses from the #261 placement spec (Wing ZIF underside at the former GH
site, entry centreline Z2.95; Main ZIFs top, NW-facing, entry centreline
Z6.90; plate top Z10.90). The cable change must not move the connectors.

Why stock FFC was killed in round 13 / B3, and what changed:
(1) **Shape** — a stock cable is straight, the route is bent in plan.
Answered by the fold plan (§3): five jig-controlled folds map the
straight cable onto the #261 path, with the excess length absorbed by a
designed S-pair of 180° folds inside the audited geometry.
(2) **Lane resistance unpublished** — still true on paper; PO accepts
this. §6 computes the target on assumed and pessimistic cross-sections
(both pass with ≥+182 mV margin) and defines the physical closure: a
pre-folding resistance measurement of the purchased cable with a
1.30 Ω/lane acceptance threshold.
(3) **Actuator access / service** — unchanged from #261 (ZIFs are the
same); gate 3 re-verified for the folded cable in §5.4.

## 2. Cable selection

**Selected: Molex Premo-Flex FFC 152660149** — 14 circuits, 0.50 mm
pitch, **Type A (contacts on the same face at both ends)**, nominal
length 152.00 mm, cable thickness 0.27 mm, tin-plated contacts,
0.5 A/contact rating, Active status. Price class: distributor singles
≈$3–6/unit (verify at order time).

Length survey of the same family (Type A): 102 mm (15266-0145),
127 mm, **152 mm (152660149)**, 203 mm (15266-0153). The fold plan
consumes ≈153 mm of centreline at the nominal fold setting (§3.4):
127 mm cannot reach; 203 mm leaves ≈50 mm that no audited fold
configuration can absorb; **152 mm is the only viable length**.
Type D (opposite-face contacts) exists in the family and is the parity
escape hatch if the connector variant ever changes (§3.2).

Connector compatibility: the cable's 0.27 mm tail sits inside the
FH12-class ZIF adaptive band (0.30 ± 0.05 mm). **Connector variant fact
(web-verified 2026-11-17): FH12-14S-0.5SH(55) — the variant #261
selected — is the BOTTOM-contact type** ((55) = gold plating; the
top-contact sibling is FH12A-14S-0.5SH(55)). Height 2.0 mm, 0.5 A/contact,
50 mΩ/contact max, 20 mating cycles. §3.2 shows the fold plan's face
bookkeeping closes with this exact variant at all four sites:
**no board-side delta is forced by the cable.**

## 3. Fold plan

### 3.1 Route and folds (right side; left is the plan mirror)

Centreline (assembly frame, mm; full vertex list in `path-vertices.csv`,
figure in `plan-view.png`). The cable leaves the Wing ZIF at
T0 (27.0, −38.5, z2.95), runs north, and reaches the Main ZIF mouth
(20.92, 38.24, z6.90), tail end T1 (22.6, 40.0, z6.90).

| Fold | At (x, y) | Turn | Function |
|---|---|---|---|
| F_A | (25.2, −15.0) | 112.5° | plan turn toward the bay centre |
| F_B | (11.37, −22.0) | 119.6° | plan turn north; then flat to y=−19, climb y=−19..−11 to z6.90 |
| F_S1 | (14.08, 24.4) | 180° | S-pair fold 1 (length absorber): leg 1 z6.90 → leg 2 z7.22, southbound |
| F_S2 | (13.00, 0.43) | 180° | S-pair fold 2: leg 3 z7.54, northbound |
| F_V7 | (14.41, 30.60) | 37.7° | final alignment turn into the Main ZIF approach |

All folds are **R2.0 rolls over jig former pins — never creases**. The
S-pair stack is 3 layers at z centres 6.90 / 7.22 / 7.54 (0.32 layer
pitch), stack top 7.70 mm vs plate underside 9.40 mm. Fold patches
(local doubling, +0.30 mm under the sheet) are modelled at F_A/F_B
(6 mm) and F_V7 (14 mm); the 180° folds are modelled as roll boxes.
The climb is delayed to y=−19..−11 so no part of the sheet rises under
the Wing's MUX field (a 0.023 mm³ graze against U_MUX_C in the first
audit run fixed this).

### 3.2 Contact-face bookkeeping

Bottom-contact ZIFs: at the Wing (underside-mounted) the springs face
world **UP**, so the cable's contacts must face **UP** at the Wing tail;
at the Main (top-mounted) the springs face **DOWN**, so contacts must
face **DOWN** at the Main tail. A fold flips the presented face; the
required net change is therefore an **ODD** number of folds. The plan
has exactly **5 folds**:

UP →(F_A) down →(F_B) up →(F_S1) down →(F_S2) up →(F_V7) down = DOWN ✓

A Type A cable (same-face contacts) is consistent with
FH12-14S-0.5SH(55) at all four connector sites. No connector variant
change, no board-side delta.

### 3.3 Conductor mapping — binding note for Issue #263

The fold sequence's plan geometry makes the delivered conductor order a
**pure reversal, k → 15−k, on both sides** (computed from the built
model, `face_mapping.py` in the runtime record). This is absorbed by
the respin's footprint pin assignment — the same freedom #261 already
uses (pin order is assigned at each footprint to the arriving lane
order). **For Issue #263: with this cable, each Main footprint assigns
D-024 signal k to the position the Wing delivers as 15−k.** D-024's
electrical content is unchanged.

### 3.4 Length budget and the jig detent table

Sharp-corner polyline total at the nominal setting (F_S1 at y=24.4):
**153.22 mm** against the cable's 152.00 mm nominal — the S-pair is the
absorber: moving F_S1 by 1 mm changes the consumed length by ≈2 mm.
The jig's S1 former slides on a rail with five detents keyed to the
**measured** length of the actual cable unit:

| Measured cable (mm) | 148 | 150 | 152 | 154 | 156 |
|---|---|---|---|---|---|
| F_S1 detent y | 21.8 | 22.8 | 23.8 | 24.8 | 25.8 |

The audit's nominal configuration sits at F_S1 y=24.4 (≈153.2 mm unit);
the sensitivity configurations (§5.3) bracket F_S1 y=21.8..26.4.

## 4. Folding jig (PO's addition)

Printed former (right-hand version; left = mirrored print), PETG,
Ender-3 Pro envelope: **42 × 98 × 11 mm**, ≈15 g at production settings
(walls + 20% infill; 24.6 cm³ solid-equivalent). Deliverables:
`sources/jig-right.step`, `sources/jig-right.stl`,
`sources/jig-slider.step`.

Features: base plate 42 × 98 × 6; a 10.0 mm wide × 2.85 mm deep path
groove following the folded plan (the groove is the fold-position
datum); **R2.0 former pins** at F_A (25.2, −15), F_B (11.37, −22),
F_V7 (14.41, 30.60) and F_S2 (13.00, 0.43); stack fences along the
S-pair run (46 mm long, z6..10.5) that hold legs 2/3 in register; the
**S1 sliding former block on a rail with the five detent notches of
§3.4**; a Wing-tail end stop at (27.0, −39.9); a Main-end tip target
pocket at (22.6, 40.6), yaw −43°.

Folding procedure: (1) measure the cable unit's length, set the S1
slider to the matching detent; (2) register the Wing tail at the end
stop, contacts up; (3) fold F_A, then F_B around their pins; (4) lay
the climb and north run in the groove; (5) fold F_S1 back over the
slider pin (leg 2 settles between the fences); (6) fold F_S2 (leg 3);
(7) fold F_V7; (8) verify the Main tail sits in its target pocket and
the strip is seated in the groove along its whole length. Folds are
one-time: a mis-folded cable is scrapped (≈$4) rather than re-folded.
The audit geometry uses the jig's R2.0 radii and detent positions;
placement tolerance is carried as the §5.3 sensitivity stack.

## 5. Fitted audit at plate Z10.90

Machinery inherited from #261/#248: `bodies_at(17, −2.65)` fixed-body
set, repaired-audit volumes (exact Common; zero-volume pairs resolved
by exact distance, then partitioned Common), hit threshold 0.005 mm³.
The folded cable is modelled as a compound of segment boxes (9.6 mm
wide × 0.32 mm envelope — the 0.27 mm cable plus tolerance) with fold
patches and 180° roll boxes; the left cable is the exact mirror of the
right (volumes verified equal). ZIF envelopes are #261's, with the
insertion slots deepened to the connector's full depth (the stock
tail inserts 2.4 mm past the mouth; #261's custom sheet stopped at the
mouth).

### 5.1 Audit-method disclosure (read before the gate table)

Two environment facts shaped the method, and are disclosed rather than
hidden:
(a) **OCCT fuse chains and complex Cut operations on this body set are
unreliable** (verified repeatedly during this study): sequential fuses
of the pitched/stacked cable boxes collapse or bloat (a fused channel
read 7.4 mm³ against a ~1,400 mm³ design volume; a tray cut with such a
tool returned a negative volume). All results below therefore rest on
**compound (unfused) cable solids and Common-only pair evaluation**,
the method that reproduced sane, cross-checkable numbers throughout.
(b) **Tray pairs**: the audit's tray bodies are 'extend' unions (the
tray fused with its height-shifted copy — the frontier machinery's
deliberate conservatism). A cut-solid audit against a channel-cut tray
could not be produced reliably under (a). The tray disposition instead
rests on a per-box overlap census (§5.2) plus the channel design
definition (§5.5): every overlapping cable box is a route box, and the
overlaps lie along the route corridor that the formed channel removes.

### 5.2 Gate table (pitch 17)

| Gate | Result |
|---|---|
| 1 — unexpected contacts, nominal | **PASS — 0** unexpected contacts, both cables, against all non-tray bodies; cable-vs-cable 0. Own-termination overlap vs the Wing connector site (J_WING underside envelope) 9.36 mm³/side — the project's standing "own termination" classification (the tail inside its own connector site; the governing ZIF envelope is clean via its slot), not a gate failure. Tray pairs: per-box census vs the extended-union tray = 51.07 mm³ total (right side), all on route-corridor boxes — dispositioned by the formed channel, §5.5. |
| 2 — length | **PASS by construction**: patterned centreline 153.22 mm at the nominal detent, absorbed per §3.4; cable 152.00 mm nominal. |
| 3 — service motions | **PASS with one named residual** (§5.4). |
| 4/5 — Fly 170 / USB insertion | **PASS by inheritance** (geometry unchanged from #261). |
| 6 — Junana keycap clearance | **OPEN** (as in every study to date; needs physical caps). |
| 7 — print envelopes | **PASS**: case parts as #261; jig 42 × 98 × 11 mm fits the Ender-3 Pro. |
| 8 — preview | `sources/preview264.step` (both cables + ZIF envelopes). |

### 5.3 Sensitivity configurations (allowance stack)

Two sensitivity configurations re-audit the allowance stack: sheet
width 10.4 mm (nominal 9.6), fold patches 0.35 mm (nominal 0.30), and
F_S1 at its extremes — sensN: F_S1 +2.0 mm (y=26.4, beyond the 156 mm
detent); sensS: F_S1 −2.6 mm (y=21.8, the 148 mm detent).

- **sensS: clean** — 0 unexpected contacts, both sides.
- **sensN: two named grazes** — sheet edge vs Wing PCB underside
  **0.286 mm³ per side** (symmetric), and vs Main-study-C23
  **0.019 mm³** (left). Both occur only when the +2.0 mm S1 extreme and
  the full width/patch allowance stack coincide. At the nominal detent
  for a true 152 mm cable (F_S1 y=23.8) the configuration is the §5.2
  nominal (clean). Disposition: the detent is set from the measured
  cable length (§4 step 1), so the stacked extreme corresponds to a
  mis-set detent, not to production spread; the grazes are recorded
  here so the case-production step can add local relief at the climb's
  Wing-edge crossing if desired.

### 5.4 Gate 3 — service motions (detail)

Phase A (Main-end unplug, tip sweep 1.25 / 2.5 / 3.75 / 5.0 mm along
the extraction axis): **all poses clean**. Phase B (Wing lift with the
cable attached, 6 poses to +Z 30): clean under the same exclusion set
#261's final service audit used (Wing-attached bodies move with the
Wing). **Named residual:** in the static drape pose (Main end
unplugged, tail resting), the drape end rests on the Main top face —
model overlap 0.499 mm³ at 0.07 mm penetration; physically the cable
lies on the surface. Same character as #261's peel-lift residual.
Tray overlaps in lift poses are the §5.1(b) union artefact (the union
spans both deck heights by construction); against the physical
channel-formed tray the lift path is the open groove.

### 5.5 Case delta

The formed FPC channel of #261, re-laid along the folded path: swept
corridor 11.4 mm wide, relieved 0.225 mm below and 0.30 mm above the
sheet (deeper at fold-patch and roll zones per §3.1). No other case
change; the channel remains the only case delta of the architecture.

## 6. Electrical

Anchor: #261's extraction (loop 208.5 mΩ → Vfar 4.785 V at
127 mA/Wing; slope −0.127 V/Ω). The stock cable replaces the patterned
lanes; per path: 2 ZIF contacts × 50 mΩ, lane resistance per the case
below; the GND return is 6 lanes in parallel (D-024).

| Case | Lane section | R_lane | Loop | Vfar @127 mA | Margin vs 4.60 V |
|---|---|---|---|---|---|
| (i) B3 assumed | 0.035 mm² | 74.7 mΩ | 203.8 mΩ | **4.786 V** | +186 mV — PASS |
| (ii) Pessimistic | 0.026 mm² | 100.6 mΩ | 234.0 mΩ | **4.782 V** | +182 mV — PASS |
| (iii) Extreme check | 0.020 mm² | — | 269.2 mΩ | 4.777 V | +177 mV — PASS |

The loop is contact-dominated; even the extreme section passes. **This
does not close the paper guarantee** — the maker does not publish the
lane resistance; the numbers above are computations on stated
assumptions, exactly as PO accepted.

### 6.3 Physical closure — post-purchase measurement procedure

Acceptance algebra: Vfar ≥ 4.60 V ⇔ loop ≤ 1,665 mΩ ⇔ **single-lane
resistance ≤ 1.33 Ω → acceptance threshold 1.30 Ω per lane**. The
expected reading is ≈0.075–0.10 Ω, so the threshold carries ~13x
margin: the measurement catches gross defects and wrong parts; it is
not a precision gate, and a 2-wire measurement with the multimeter PO
owns is sufficient (4-wire/Kelvin is an optional refinement).

Procedure (per cable unit, BEFORE folding): (1) short the multimeter
leads and record the lead resistance; (2) probe the 5V lane (position
1) end-to-end and subtract the lead resistance; (3) repeat for one GND
lane (any of positions 2/4/8/10/12/14); (4) accept the unit if both
readings are ≤ 1.30 Ω; (5) record the readings with the unit's
measured length (the length also sets the jig detent, §4 step 1).

## 7. Cost comparison

| | Stock FFC + jig (this study) | Custom FPC (D-042 as adopted) |
|---|---|---|
| Cables / keyboard | 2 × ≈$3–6 = $6–12 | included below |
| Jig | one-time ≈$3–5 filament (both hands) | — |
| **First iteration** | **≈$10–18** | **$50–150** |
| **Re-iteration** | **≈$6–12** (jig reused; a mis-fold scraps ≈$4) | **$50–150** (new fabrication) |

Prices are distributor-single price classes observed 2026-11-17;
verify at order time. The stock route also removes the custom FPC's
fabrication lead time from every iteration.

## 8. Draft decision text — D-042 cable-clause amendment (REPORT ONLY)

> D-042 amendment (draft): the interconnect cable of the adopted
> low-deck architecture may be realised EITHER as the custom FPC of
> Issue #261 OR as a stock Molex Premo-Flex FFC 152660149 (152 mm,
> Type A) folded on the Issue #264 jig, at the same ZIF poses and
> plate Z10.90. Conditions: (i) each cable unit passes the §6.3
> measurement (≤1.30 Ω/lane) before folding, and its measured length
> sets the jig detent; (ii) the Main footprint pin assignment follows
> the §3.3 reversal (k → 15−k); (iii) the case channel is formed along
> the folded path per §5.5; (iv) Junana measurement (gate 6) and the
> Rev.5/Rev.8 respin evidence (Issue #263) remain conditions of the
> architecture as a whole. The custom FPC remains the fallback if a
> condition fails in production.

## Sources in this tree

- `plan-view.png` — fold-plan figure (final geometry).
- `path-vertices.csv` — centreline vertices, both sides.
- `sources/preview264.step` — fitted cables + ZIF envelopes.
- `sources/jig-right.step` / `jig-right.stl` / `jig-slider.step` —
  folding jig (right hand; mirror for left).
- Audit scripts, logs and intermediate results: worktree
  `.issue264-runtime/` (build_audit264*.py, run_final.py,
  audit264v4.log, final_eval.log/.json, service264.log, electrical.py,
  face_mapping.py).
