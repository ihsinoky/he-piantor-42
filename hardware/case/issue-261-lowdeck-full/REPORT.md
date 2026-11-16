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
