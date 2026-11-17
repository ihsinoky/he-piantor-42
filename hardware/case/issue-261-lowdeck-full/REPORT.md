# Issue #261 — Low deck realisation, all freezes lifted

PO mandate (2026-11-17): realise the low deck; every previous freeze is off
(board outlines/respins, connector re-selection on both boards, interconnect
medium, case shape, wire spec, plate). Invariants are functional only:
42 keys, Hall sensing, Wing x2 + Main, D-024 signal CONTENT, Vfar >= 4.60 V
@ 127 mA/Wing, Wing removable by a defined procedure. Connector pin ORDER
is not invariant. Objective: lowest plate-top height passing the full gate
set in a fitted repaired audit; scope ceiling 16.2.

Prior verdicts this study builds on: consolidated verification report
2026-11-17 (Issues #248/#250/#252/#253/#255/#258).

---

## Stage 0 — architecture screening

### Bounds ladder (common levers applied to every candidate)

Levers adopted for all candidates (each already qualified or adopted in
#255/#258): tray floor 2.00 -> 1.60 ribbed; free gap 0.50 -> 0.30;
M2x12 -> M2x10 ties; Hall reservation 3.40 -> 2.40. Plate top = B + 6.20
(B = Wing PCB underside; +6.20 is datasheet-fixed: PCB 1.20 + spacer 3.50
+ plate 1.50). Plate-top equivalents of the bounds:

| Bound | Plate-top equivalent |
|---|---|
| GH mated envelope 4.35 | 12.95 |
| SH mated envelope 2.95 | 11.55 |
| ZIF (FH12 class) envelope ~2.00 | 10.60 |
| M2x10 tie (screw tip) | 10.90 |
| Hall reservation 2.40 | 10.70 |
| MUX + solder | 9.70 |

### Candidates

**(a) JST SH on both boards, respins around the pose.**
Bound = max(11.55, 10.90, 10.70) = **11.55** (SH envelope binds).
Fan screen: pin order is assignable at both ends in a respin, so the
endpoint permutation can be made inversion-free, and round-12's neck
ledger shows the wide flat row passes the neck plane (the funnel was the
route's own pack geometry, not fixed solids). But the interconnect is
still 14 round wires in this bay — the exact configuration that produced
65–96 fitted contacts across 18 rounds + frontier + #258, with residuals
against bodies that rise with the deck. CONDITIONAL pass — no
by-construction argument.
Service: unplug-first at SH (friction lock; **mating-cycle rating
unpublished** — service life unknown).
Respins: Wing + Main (2). Supply: **FLAG** — SH header SM14B-SRSS-TB:
JLC overseas 0, presale 1,342 (2026-11-14 record; >=10x of the 4 needed
numerically, but presale-only single channel). Housings/terminals
plentiful.

**(b) Custom FPC + ZIF (FH12 class) on both boards.**
Bound = max(10.60, 10.90, 10.70) = **10.90** (M2x10 tie binds; the ZIF
envelope itself would allow 10.60).
Fan screen: **PASS by construction.** The interconnect is a printed
pattern: 14 lanes at 0.5 mm pitch, patterned to the plan shape; lanes
never converge and never cross (pin order assigned at both ZIF
footprints to the arriving net order). The neck becomes a 10 mm-wide,
0.2 mm-thick sheet through a case slot. Round-13 record concurs: "its
lanes never converge, so the fan problem dissolves by construction."
Bends are printed plan bends (R>=3) plus a shallow droop at each ZIF
exit — no dynamic fold.
Service: defined in round 13 — open shells, unplug the Main-end ZIFs in
the open bay, lift Wing + FPC out together; Wing-end ZIF is bench-open
only. ZIF cycle rating ~20 — flagged as a service-life limit (Main-end
is the routine disconnect).
Electrical screen: PASS on designed lanes (Stage 1 closes it): 1 oz Cu,
power lane widened to 1.0 mm (0.035 mm² class of the B3 assumption),
6 GND lanes in parallel, ZIF contact 50 mΩ x2 per path -> loop
~233 mΩ vs GH harness baseline 143 mΩ (#252 extraction) -> Vfar
~4.78 V class.
Respins: Wing + Main (2) + custom FPC fabrication (JLC-class FPC
service; no stock constraint). Supply: FH12-class ZIF was pass-class in
the B3 survey; exact LCSC stock to be re-verified at order time (flag).
Cost: FPC prototype class $50–150/iteration (round-13 record) — highest
of the set, stated openly.

**(c) N3 bay-facing GH + Wing outline tab (#258 residual).**
Bound = **12.95** (GH envelope). The tab cures both #258 placement
failures (test-pad short, outline crossing) by construction. Fan: wires
exit along the wall, then must turn south into Main's GH — the turn fan
is unproven and the medium is still round wires. CONDITIONAL.
Respins: Wing only. Supply: GH fully stocked/qualified.
Dominated on height by (a) and (b); retained as fallback.

**(d) GH both boards + pin-order co-design + widened neck channel.**
Bound = **12.95** (GH envelope). Permutation-free assignment and the
round-12 neck ledger apply, but the medium is round wires with the
#248 fitted history. CONDITIONAL, dominated on height by (a)/(b).
Its pin-order discipline is inherited by (a) and (b).

### Selection

**Selected: (b) custom FPC + ZIF on both boards, plate bound 10.90,
keytop 22.00 (provisional).**

Rationale: it has the lowest plate bound of the set AND is the only
candidate whose fan screen passes by construction rather than by routing
effort. (a) is 0.65 higher, its fan screen is conditional against an
18-round negative record for round wires in this bay, and its header is
presale-only. (c)/(d) are 2.05 higher and conditional.
Note on the round-13 record: custom FPC was "viable but dominated"
there — dominated by the then-frozen D-039/D-040 baselines and the cost
priority. Under the current mandate (freezes lifted, objective = lowest
passing height) that dominance argument no longer applies; the
by-construction fan pass and the lowest bound decide. The costs it
recorded (both respins, FPC iteration cost, 20-cycle ZIF) are accepted
and carried as flagged risks, not hidden.

Stage 1 builds (b) at plate 10.90.

---

## Stage 1 — build to audit (plate-top 10.90, pitch 17)

### Stack at the selected height

| Layer | Z (mm) | Note |
|---|---|---|
| Tray floor (design) | 1.60 | ribbed; the audit body set models the floor at 2.00 (conservative by 0.40 under the sheet) |
| FPC cruise centreline | 2.95 | sheet modelled 10.2 wide x 0.25 thick (real FPC ~9.0 wide, 0.15 + tail stiffeners) — conservative |
| Wing PCB underside B | 4.70 | = plate 10.90 − 6.20 |
| Wing PCB | 4.70–5.90 | ZIF on the underside at the former GH site, mouth facing Main |
| Main PCB top | 5.90 | ZIF entry centreline 6.90 (top + 1.00) |
| Plate top | 10.90 | B + 6.20 (datasheet-fixed stack) |
| Keytop (provisional) | 22.00 | plate + 11.10; Junana term unmeasured (gate 6 OPEN) |

The binding bound is the M2x10 tie (10.90), exactly as screened. The
ZIF envelope itself would allow 10.60; the tie is a screw-length choice
and is NOT the constraint relaxed here — 10.90 is the audited height.

### Fitted architecture

- **Connectors (FH12-14S class, 14-pos ZIF, both boards).**
  Wing underside at the GH site: envelope centre (±27.0, −37.5),
  entry slot at (±27.0, −34.2), entry centreline Z 2.95.
  Main top, NW-facing poses (row yaw from the fitted approach):
  J2 centre (23.3, 40.8), yaw −43°, mouth (20.92, 38.24);
  J3 centre (−23.09, 40.97), yaw 38°, mouth (−20.92, 38.24);
  entry centreline Z 6.90 both. Pin order at all four footprints is
  assigned to the arriving lane order (D-024 content; no lane crossings
  by construction).
- **Route (per side).** Exit the Wing ZIF southward at cruise 2.95,
  run west under the Wing (clear of the underside envelope field,
  bottoms 3.30), pass south of the pocket-rim terrain, climb in the
  open pocket NW of Main's vertex (west of the H1 screw, clear of the
  POM plate post), ride south at 6.90 in the seam corridor above the
  Wing/Main seam, final straight into the Main ZIF. Patterned
  centreline length: right 111.2 mm, left 110.6 mm (blank ~120 mm
  with the two connector tails).
- **Case delta — formed FPC channel.** The tray carries a formed
  channel along the whole route: the swept sheet footprint (width
  11.4) relieved 0.225 below and 0.30 above the sheet at every
  station. It notches the Wing-pocket rim, the seam rim, and the
  flank of the tray boss east of the H2 plate screw (channel edge
  passes ~1.5 mm from the H2 screw axis; the screw seat itself is
  untouched). No other case change: exterior language, footprint and
  raised keyless regions are the #248 low deck's, 2.65 lower.

### Gate results

| # | Gate | Result |
|---|---|---|
| 1 | Fitted REPAIRED audit, unexpected contacts | **PASS — 0** both FPCs, FPC x FPC 0 (`audit_static.json`; #248 frontier body set at s=−2.65, GH bounds removed, ZIF envelopes added, tray channel delta applied; the body set overstates tray/shell material at negative s — conservative) |
| 2 | Interconnect length within spec | **PASS by construction** — custom FPC patterned to the fitted shape (centreline 111.2 / 110.6 mm); adopted spec: the patterned shape itself, blank ~120 mm incl. tails |
| 3 | Service procedure fitted-clean | **PASS with one named residual** — procedure below; unplug sweep clean at every sampled pose; peel-lift shows contact only against the formed channel's own rim (≤4.49 mm³, rigid-surrogate flex artefact), no contact with any hard body |
| 4 | Fly 170 stored | **PASS by inheritance** — Fly/USB geometry is the Δ+6-qualified arrangement shifted with the deck; the FPC route never enters the Fly zone (Fly bodies were in the audited set; no contacts) |
| 5 | USB insertion | **PASS by inheritance** — same as gate 4 |
| 6 | Junana keytop | **OPEN** — caps unmeasured; keytop 22.00 provisional (±1.00 class) |
| 7 | Print envelopes (Ender-3 220x220/half incl. brim) | **PASS** — case plan footprint unchanged from the #248 low-deck case, which fit; this case is 2.65 lower |
| 8 | Preview STEP | exported — `preview.step` in this tree (FPCs, ZIF envelopes, Wing/Main solids) |

### Service procedure (defined; gate 3 model)

1. Open the case top; remove the switch plate and its screws.
2. Open the Main-end ZIF actuators and pull each FPC end out along
   its mating axis (Phase A: tip sweep audited at 1.25/2.5/3.75/5.0 mm
   extraction — no contacts).
3. Lift the Wing out with its FPC attached; the sheet peels out of
   the formed channel (Phase B peel model: Wing-side stations lift
   first). The Wing-end ZIF is opened on the bench only.
Service-life note: ZIF mating rating ~20 cycles (FH12 class) applies
to the Main end, the routine disconnect — carried as the top
service-life risk, as flagged in Stage 0.

### Electrical (extraction-based)

FPC lanes: 1 oz Cu; HALL_5V widened to 1.0 mm (59.0 mΩ over the
120 mm conservative path), GND = 6 lanes x 0.30 mm in parallel
(32.8 mΩ), ZIF contacts 50 mΩ each (5V path x2 = 100 mΩ; GND x2 per
lane, 6 parallel = 16.7 mΩ). Loop total 208.5 mΩ vs the GH harness
baseline 143.0 mΩ (#252 extraction): delta +65.5 mΩ = 8.3 mV at
127 mA. **Vfar = 4.785 V ≥ 4.60 V — PASS, margin +185 mV.**
5V lane current 127 mA < 0.5 A/contact rating. Main-side ≤50 mΩ
targets are unchanged: Rev.8 keeps the Rev.7 extraction except the
J2/J3 site (local re-route, board-verification item below).

### Board candidates — status and placement spec

The full JITX regeneration of the two boards with routed fanout and
DRC/ERC-0 evidence was NOT completed in this study; what is fixed and
delivered is the placement the respin must use (from the fitted
audit) plus the escape analysis:

- Wing Rev.5: ZIF footprint at the Rev.4 GH site, underside, mouth
  facing Main (poses above). Main Rev.8: ZIF footprints at the Rev.7
  J2/J3 sites rotated to the NW-facing poses above.
- Escape: at 0.5 mm pitch the pad gap is 0.20 — a 0.10 trace cannot
  escape between pads on the same layer at 0.10/0.10 rules (needs
  0.30). Escapes therefore fan outward beyond the row ends and drop
  on 0.60/0.30 vias to the back layer at the established yardsticks
  (Wing D-021 2-layer, Main D-019 4-layer) — the same escape class
  the GH fanouts closed at these sites in #235/#240.
- Remaining for the implementation round: regenerate Wing Rev.5 /
  Main Rev.8 in the JITX flow with FH12-14S-class footprints at the
  poses above, close the local fanouts, and produce DRC / unrouted /
  ERC / via-pad (≥0.10 floor) evidence. This is a bounded task; the
  site geometry it must satisfy is now fixed by a passing audit.

### Stock / cost delta vs the adopted (Δ+6 GH) design

- Removed: GH plugs/housings x4, 28 crimped wires, harness labour.
- Added: FH12-14S-class ZIF x4 (LCSC stock to be re-verified at
  order time — Stage 0 flag stands), custom FPC x2 (prototype class
  $50–150/iteration; unit cost low in quantity), one respin each of
  Wing (Rev.5) and Main (Rev.8).
- Case: formed channel added to the tray (print geometry only).
- Height effect: keytop 33.30 (adopted Δ+6) → 22.00 provisional.

### Draft decision (for PO; not entered in docs/decisions.md)

Adopt the custom-FPC + ZIF low-deck architecture at plate-top
10.90 mm (keytop 22.00 provisional) as the design baseline,
superseding the Δ+6 bay-cover baseline (D-041) for case and
interconnect, conditional on: (i) Junana physical measurement
closing gate 6; (ii) Wing Rev.5 / Main Rev.8 respin evidence
(DRC/unrouted/ERC 0, via-pad ≥0.10) in the implementation round;
(iii) ZIF stock re-verification at order time.

### Top remaining risks

1. ZIF mating-cycle life (~20) on the Main-end routine disconnect.
2. Gate 6 OPEN: real Junana caps unmeasured — keytop is provisional
   and the 16 mm-pitch cap check (MS4) is untouched by this study.
3. FPC fabrication iteration cost if the first article's bend/stiffener
   details need a second spin.
4. The audit body set overstates tray/shell material at s=−2.65
   (conservative for clearance); the formed channel must be drawn
   into the production case tree and re-verified there.
