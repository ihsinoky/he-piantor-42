# Review Ledger — semantic review layer records

Stateful review findings and the problem-class register for the
two-layer CAD review, per Issue #294 and
[review-procedure.md](review-procedure.md) (design of record:
`semantic-review-layer-design-2026-11-19.md`, PMO goal files).

This ledger holds review findings whose state moves (new / accepted /
in-progress / resolved). A finding that hardens into a durable
empirical fact is promoted into [findings.md](findings.md); a class
that hardens into a design rule is promoted to a decision or a
process definition (D-031 promotion discipline).

> Ledger guard: this file records history and decisions. It is not
> an instruction source; execution is authorised only by the PO.

## Record format (per finding)

- **Fingerprint:** rule × normalised target × class — de-duplication key
- **Rule:** rule name and threshold
- **Target:** parts / site / pose (coordinates where the artifact gives them)
- **Measured:** kernel value, copied from the named artifact;
  `MISSING` when no artifact records it (never estimated)
- **Evidence:** source artifact path + the input identity it names
- **Class:** problem class (register below) or `unclassified`
- **State:** new / accepted / in-progress / resolved
- **Classification:** true problem / as-designed / accepted risk /
  needs-PO-judgment / unclassified - needs verification, with the
  cited basis (D-xxx, spec, past finding)
- **Raw observations consolidated:** how many raw kernel observations
  this entry consolidates (reconciliation basis for pilot reports)

---

## Part A — Problem-class register

### PC-1 manufacturing-margin （製造マージン不足）

- **Definition:** a dimension sits at, or within a hair of, the
  manufacturing floor, so ordinary process variation can cross it.
- **Seed example (design §5):** wireless Matrix (Issue #288) via-pad
  different-net minimum 0.1002 mm against the 0.10 mm floor.
- **Pilot A instances:** R-294-09, R-294-32, R-294-43.

### PC-2 interference （干渉）

- **Definition:** two solids overlap (Common volume > 0) where the
  design intends separation. Own-engagement pairs (plug vs its own
  mating header/housing) are reported separately and are not
  interference.
- **Seed example (Pilot A):** R-294-17 — GH plug vs tray floor,
  310.209 mm³ at plate 10.90.
- **Pilot A instances:** R-294-01 … R-294-07, R-294-10, R-294-13,
  R-294-14, R-294-17 … R-294-19, R-294-22, R-294-25 … R-294-27,
  R-294-30, R-294-39.

### PC-3 clearance-shortfall (クリアランス不足）

- **Definition:** a positive gap below the applicable threshold —
  short of interference, but without the intended margin.
- **Seed example (Pilot A):** R-294-31 — A2 extrema clearance
  0.314 mm against the 0.3 mm example threshold of the design §3.
- **Pilot A instances:** R-294-08, R-294-20, R-294-28, R-294-29,
  R-294-31, R-294-36, R-294-37, R-294-38.

### PC-4 assembly-escape-shortfall （逃げ不足）

- **Definition:** the escape needed for assembly, cabling, tool or
  service motion is insufficient, or a service action needs an
  unplanned workaround (e.g. lifting a board to reach an actuator).
- **Seed example (Pilot A):** R-294-12 — flipped-pose FFC (un)locking
  requires lifting the Main board (D-046 service consequence).
- **Pilot A instances:** R-294-12, R-294-21, R-294-33, R-294-34,
  R-294-35, R-294-40, R-294-42.

### PC-5 symmetry-break （対称性の崩れ）

- **Definition:** asymmetry at a site whose premise is symmetry
  (mirror pair, shared case features), or — as a positive instance —
  a recorded asymmetry found removed.
- **Seed example (Pilot A):** R-294-11 — tray relief pair was
  6.521 / 6.305 mm³ under Rev.9; Rev.10 measures 6.305 / 6.305 mm³.
- **Pilot A instances:** R-294-11.

---

## Part B — Findings register

Pilot A scope: the Main Rev.10 two-posture 3D audit family —
Issue #275 fitted audits (normal / flipped / flipped-J4), pocket and
case-delta verifications, Issue #275 Phase 2 GH geometric check, and
the Issue #278 flipped-USB route audit incl. the adopted A2 channel.
Board-level electrical gates (DRC / ERC / Vfar / via-pad) are a
different audit family and are out of scope here; procurement crawl
data (Issue #278 family F) is not a kernel observation and is
excluded. Input identities are the ones the artifacts name; the
artifacts record no input STEP hash, so none is cited.

### R-294-01 — Normal pose, right FFC link: zero non-tray contacts

- **Fingerprint:** interference-volume × FFC-sheet-right × all-non-tray-bodies @normal-pose × PC-2
- **Rule:** gate 1 — cable vs non-tray bodies, Common volume must be 0 mm³
- **Target:** Type A FFC sheet, right link, normal pose
- **Measured:** hits {} (0 contacts; 22 bbox-tested)
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-normal.json` (+ `.log`); input: fitted body set `fitlibF.bodies_at(17, -2.65)`, 343 bodies
- **Class:** PC-2 interference (pass)
- **State:** resolved — **Classification:** as-designed. Basis: gate result itself; configuration adopted by D-046.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-02 — Normal pose, left FFC sheet grazes the C23 study envelope

- **Fingerprint:** interference-volume × FFC-sheet-left × Main-study-C23-envelope @normal-pose × PC-2
- **Rule:** gate 1 — cable vs non-tray bodies, Common volume must be 0 mm³
- **Target:** Type A FFC sheet, left link, vs C23 envelope (intersection bbox x −8.92..−7.99, y 27.80..30.20, z 6.78..7.03; penetration dx 0.94, dy 2.40, dz 0.25 mm)
- **Measured:** 0.488 mm³ as audited; 0.016 mm³ on re-test with the approach re-run to the as-built Rev.10 J2 centre (the study ZIF envelope sits ~1.4 mm from the as-built connector centre, a pre-existing offset of the #264 lineage)
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-normal.json`; `c23-check.log` (re-test); REPORT §5 in `he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/REPORT.md`; input: fitted body set `fitlibF.bodies_at(17, -2.65)`
- **Class:** PC-2 interference (marginal envelope graze)
- **State:** new — **Classification:** needs-PO-judgment. Basis: no D-xxx disposes this graze; the #275 REPORT classifies it "marginal envelope graze, build watch item — not a route blocker", which is a study opinion, not a PO acceptance (acceptance is a PO gate, procedure §7.4). Same-class group with R-294-05 / R-294-06.
- **Suppression:** none — surfaced as NEW.
- **Raw observations consolidated:** 2

### R-294-03 — Normal pose: FFC sheet / tray form contact inside the corridor

- **Fingerprint:** interference-volume × FFC-sheet × tray-form @normal-pose × PC-2
- **Rule:** containment — cable plan footprint outside the channel corridor must be 0 mm²; overlap with the channel support form inside the corridor is the disposed class of the #264 containment argument
- **Target:** FFC sheets (both links) vs tray-left body (channel form), normal pose
- **Measured:** overlap 290.409 mm³ (each side); plan footprint outside corridor 0.000 mm² (each side)
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-normal.json`; REPORT §5 (disposition); input: fitted body set `fitlibF.bodies_at(17, -2.65)`
- **Class:** PC-2 interference (within-corridor form contact)
- **State:** accepted — **Classification:** as-designed. Basis: REPORT §5 disposition (contact with the channel support form inside the corridor, the #264 class); configuration adopted by D-046.
- **Suppression:** accepted by D-046.
- **Raw observations consolidated:** 2

### R-294-04 — Flipped pose, left FFC link: zero non-tray contacts

- **Fingerprint:** interference-volume × FFC-sheet-left × all-non-tray-bodies @flipped-pose × PC-2
- **Rule:** gate 1 — Common volume must be 0 mm³
- **Target:** Type D FFC sheet, left link, flipped pose (pocket A cut)
- **Measured:** hits {} (0 contacts; 7 bbox-tested)
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-flipped.json` (+ `.log`); input: fitted body set `fitlibF.bodies_at(17, -2.65)`, Main bodies flipped about the slab centre
- **Class:** PC-2 interference (pass)
- **State:** resolved — **Classification:** as-designed. Basis: gate result; flip qualified by D-046.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-05 — Flipped pose, right FFC sheet grazes a case joint screw

- **Fingerprint:** interference-volume × FFC-sheet-right × joint-screw-1-12_0 @flipped-pose × PC-2
- **Rule:** gate 1 — Common volume must be 0 mm³
- **Target:** Type D FFC sheet bend corner vs joint screw upper end (intersection bbox x 14.20..15.80, y −8.80..−7.20, z 2.82..3.08)
- **Measured:** 0.503 mm³
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-flipped.json`; `c23-check.log` (recomputation); REPORT §5; input: fitted body set `fitlibF.bodies_at(17, -2.65)`, flipped
- **Class:** PC-2 interference (marginal graze)
- **State:** new — **Classification:** needs-PO-judgment. Basis: REPORT §5 records "marginal grazes, recorded — gate 1 is not a literal 0 on this side"; D-046 adopts the flip qualification without naming the grazes, so no PO acceptance of this item is on record. Same-class group with R-294-02 / R-294-06.
- **Suppression:** none — surfaced as NEW.
- **Raw observations consolidated:** 1

### R-294-06 — Flipped pose, right FFC sheet grazes the flipped C23 envelope

- **Fingerprint:** interference-volume × FFC-sheet-right × Main-study-C23-envelope-flipped @flipped-pose × PC-2
- **Rule:** gate 1 — Common volume must be 0 mm³
- **Target:** Type D FFC sheet vs flipped C23 envelope (intersection bbox x 7.99..8.92, y 27.80..30.20, z 3.05..3.08; 0.03 mm z-touch at the envelope corner)
- **Measured:** 0.049 mm³
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-flipped.json`; `c23-check.log`; REPORT §5; input: fitted body set `fitlibF.bodies_at(17, -2.65)`, flipped
- **Class:** PC-2 interference (marginal envelope graze)
- **State:** new — **Classification:** needs-PO-judgment. Basis: as R-294-05; same-class group with R-294-02 / R-294-05.
- **Suppression:** none — surfaced as NEW.
- **Raw observations consolidated:** 1

### R-294-07 — Flipped pose: FFC sheet / tray form contact inside the corridor

- **Fingerprint:** interference-volume × FFC-sheet × tray-form @flipped-pose × PC-2
- **Rule:** containment — plan footprint outside corridor must be 0 mm² (as R-294-03)
- **Target:** Type D FFC sheets (both links) vs tray form, flipped pose
- **Measured:** overlap 246.904 mm³ (each side); plan footprint outside corridor 0.000 mm² (each side); identical results with normal-profile and flat-profile channel cuts — the normal trays serve both poses
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-flipped.json`; REPORT §5; input: fitted body set `fitlibF.bodies_at(17, -2.65)`, flipped
- **Class:** PC-2 interference (within-corridor form contact)
- **State:** accepted — **Classification:** as-designed. Basis: REPORT §5; D-046.
- **Suppression:** accepted by D-046.
- **Raw observations consolidated:** 2

### R-294-08 — Flipped pose: component residual clearance under the flipped Main

- **Fingerprint:** clearance × flipped-Main-underside-parts × tray-floor @flipped-pose × PC-3
- **Rule:** flipped underside parts must clear the tray floor; free span = underside plane Z4.70 − tray floor Z1.60 = 3.10 mm
- **Target:** C26/C27/C28 (2.5 mm tall), L1 (2.1 mm), FH12 (2.0 mm), J4 header (1.55 mm), flipped pose
- **Measured:** residual before pocket A: C26/C27/C28 0.60 mm; restored to 1.60 mm by pocket A; L1 1.00 mm; FH12 1.10 mm; J4 header 1.55 mm. Issue #278 basis re-states the hang-down set (ZIF envelopes bottom Z 2.70; C26/27/28 envelopes bottom Z 1.70; L1 bottom Z 2.40)
- **Evidence:** REPORT §5 (`he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/REPORT.md`); `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §1; input: fitted body set, flipped
- **Class:** PC-3 clearance-shortfall (the 0.60 mm pre-pocket residual)
- **State:** accepted — **Classification:** as-designed. Basis: pocket A (1.0 mm, case X −6..+13, Y 28..48, floor Z0.60) adopted by D-046 precisely to restore this residual.
- **Suppression:** accepted by D-046.
- **Raw observations consolidated:** 2

### R-294-09 — Pocket A verification (adopted pocket, both pitches)

- **Fingerprint:** removed-volume/web × pocket-A × tray @case × PC-1
- **Rule:** pocket box must remove tray material only, touch no other body; remaining web is a case-print gate note
- **Target:** case pocket A (X −6..+13, Y 28..48, floor Z0.60), pitches 17 and 16
- **Measured:** pocket removes exactly 380.00 mm³ of tray; other-body hits {}; above-floor tray volume 85.5 mm³ (tray-left) / 85.5 mm³ (tray-right); below-pocket slab 996.55 mm³ over 380.0 mm² → remaining 2.623 mm in the audit body set (floor modelled at Z2.00, conservative). REPORT production note: nominal remaining web 0.60 mm (design floor Z1.60) — to be confirmed at the case-print gate
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/case-pocket-275.log`; REPORT §5; input: audit body set, both pitches identical
- **Class:** PC-1 manufacturing-margin (remaining-web note for the print gate)
- **State:** accepted — **Classification:** as-designed. Basis: D-046 adopted pocket A; the web figure is carried as a production note, not an open design question.
- **Suppression:** accepted by D-046.
- **Raw observations consolidated:** 2

### R-294-10 — Pocket variant B (j4ext): pocket box hits a Main screw

- **Fingerprint:** interference-volume × pocket-B-j4ext × screw-main-H1 @case × PC-2
- **Rule:** pocket box must touch no non-tray body (as R-294-09)
- **Target:** pocket variant B_j4ext (416 mm² floor area), pitches 17 and 16
- **Measured:** pocket removes 416.00 mm³ of tray; other-body hit screw-main-H1 2.011 mm³; above-floor tray 204.45 mm³ (left) / 72.88 mm³ (right); remaining 2.631 mm (audit model)
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/case-pocket-275.log`; input: audit body set, both pitches identical
- **Class:** PC-2 interference (in the variant)
- **State:** resolved — **Classification:** true problem (variant-scoped). Basis: the hit is real in variant B; variant B was not adopted — D-046 adopted pocket A (R-294-09), disposing the variant set.
- **Suppression:** accepted by D-046 (adoption of A over B).
- **Raw observations consolidated:** 2

### R-294-11 — Tray relief symmetry under Rev.10 tabs

- **Fingerprint:** relief-volume-pair × tab9 × tray-left/tray-right @case × PC-5
- **Rule:** symmetric tabs (D-046 premise) must produce symmetric tray relief; supersedes the Rev.9 pair 6.521 / 6.305 mm³
- **Target:** tray relief for the Rev.10 tab chain, both pitches
- **Measured:** left 6.305 mm³ / right 6.305 mm³ (both pitches; the right reproduces the Rev.9 figure, the left becomes its mirror)
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/case-delta-275.log`; REPORT §5; input: production-tree audit rerun (case-delta-275)
- **Class:** PC-5 symmetry-break (positive instance — asymmetry removed)
- **State:** resolved — **Classification:** as-designed. Basis: D-046 records the relief as symmetric (6.305 mm³/side).
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 2

### R-294-12 — Flipped pose: FFC (un)locking requires lifting the Main board

- **Fingerprint:** service-escape × FH12-actuators × tray @flipped-pose × PC-4
- **Rule:** cable service must be possible in the installed pose, or the workaround must be a recorded service step
- **Target:** Main-side FH12 ZIF actuators, flipped pose (actuators face the tray); Wing-side actuators remain accessible as in the normal pose
- **Measured:** no kernel volume — recorded service consequence of the flipped fitted audit (actuator faces the tray; board lift required before (un)locking)
- **Evidence:** REPORT §5 (`he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/REPORT.md`); restated by D-051 ("the D-046 FFC board-lift service consequence is unchanged")
- **Class:** PC-4 assembly-escape-shortfall
- **State:** accepted — **Classification:** accepted risk. Basis: D-046 records the board lift as the service procedure for flipped installation; D-051 confirms it unchanged.
- **Suppression:** accepted by D-046.
- **Raw observations consolidated:** 1

### R-294-13 — Flipped J4 plug: fits; only contact is its own header engagement

- **Fingerprint:** interference-volume × EZmate-plug-J4 × Main-study-J4-header @flipped-pose × PC-2
- **Rule:** gate 1 — Common volume must be 0 mm³, own-engagement pairs excluded (procedure §1.3)
- **Target:** flipped J4 EZmate plug (hangs to Z2.80 over the plain floor, 1.20 mm clear)
- **Measured:** plug-vs-header 22.75 mm³ (plug-hits test) and 22.862 mm³ (gate-1 context) in the #275 run; J4 header engagement 35.417 mm³ in the #278 A2 run — all mating-interface engagement, expected
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-j4flip.json`; `he-piantor-flipusb/.issue278-runtime/audit278.json` (A2 engagement); input: fitted body set, flipped
- **Class:** PC-2 interference (own-engagement, excluded class)
- **State:** resolved — **Classification:** as-designed. Basis: procedure §1.3 engagement exclusion; REPORT §5 ("its only audit contact is its own mating header envelope, expected").
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 3

### R-294-14 — Flipped USB west escape FAILS (the D-046 named residual)

- **Fingerprint:** interference-volume × EZmate-cable-west-route × FFC-sheet-left/tray @flipped-pose × PC-2
- **Rule:** gate 1 — Common volume must be 0 mm³ along the whole route
- **Target:** Stage B west escape (flat bundle 4.5 × 1.2 mm, plan loop west, hop over the left FFC sheet)
- **Measured:** hop transition contacts the left FFC sheet 5.385 mm³; leg vs tray-left 501.788 mm³ (a new tray channel would be needed along the whole run); Fly body graze 0.189 mm³ in the same run; vs FFC right 0.0 mm³; vs tray-right 0.0 mm³. Any west-side southbound path crosses the left sheet's plan exactly once and the sheet's S-curve leaves no transition window; the fold-back alternative needs a sub-1 mm bend radius
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-j4flip.json` (+ `.log`); REPORT §5 ("NAMED RESIDUAL"); input: fitted body set, flipped
- **Class:** PC-2 interference
- **State:** resolved — **Classification:** true problem. Basis: route failed the audit; recorded as the named residual in D-046 and closed by the different (under-sheet) route adopted in D-051 — see R-294-30.
- **Suppression:** resolved-confirmed (closed by D-051).
- **Raw observations consolidated:** 5

### R-294-15 — Artefact: "hit" against the normal-pose cable model in the flipped audit

- **Fingerprint:** interference-volume × EZmate-cable-flipped × Fly-170mm-normal-pose-model @flipped-pose × unclassified
- **Rule:** gate 1 — Common volume must be 0 mm³
- **Target:** flipped cable vs the body-set's normal-pose cable model `Fly-170mm`
- **Measured:** 4.157 mm³
- **Evidence:** `he-piantor-mainsym/.issue275-runtime/audit275-j4flip.json`; disposition in `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §1 (the model is the same physical cable in the other pose; excluded from the #278 body set)
- **Class:** unclassified (modelling artefact — no physical pair exists)
- **State:** resolved — **Classification:** as-designed (no physical finding; the "target" is a duplicate model of the same cable). Basis: flip-usb.md §1 exclusion note.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-16 — Artefact: fail-open intersect against the tray-left fragment compound

- **Fingerprint:** self-test × EZmate-plug × tray-left-fragment @method × unclassified
- **Rule:** audit self-test — a disjoint pair must measure 0
- **Target:** body-set `tray-left` (fragment compound, 7 solids, 7.4 mm³, z ≤ 0.4) vs the EZmate plug model
- **Measured:** 22.75 mm³ returned at every z offset (dz 0 / −1.6 / z-centre 1.85) — `Shape.intersect` against the disjoint fragment compound returns the first operand (the plug's own volume). Verified in-process; no gate number depends on it (cable z ≥ 1.30, bbox-disjoint)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/decisive.log`; `flip-usb.md` §2 (correction of the earlier reading); same 22.75 figure sighted in `audit278.json` (self_test) and `route_audit.log` (self-test line)
- **Class:** unclassified (method artefact)
- **State:** resolved — **Classification:** as-designed (no physical finding; method repaired per the #248 lesson — boolean Common via `Shape.intersect`, volumes summed over pieces). Basis: flip-usb.md §2.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 3

### R-294-17 — GH conversion at plate 10.90: mated plug intersects the tray floor

- **Fingerprint:** interference-volume × GH-plug-Wing-end × tray-floor @flipped-GH × PC-2
- **Rule:** Q1 — the mated GH plug must clear the tray floor at the adopted plate height 10.90 mm (D-042/D-046)
- **Target:** Wing-end mated GH plug (4.35 mm nominal / 4.85 mm with project allowance) vs tray floor (top Z1.60); available gap 3.10 mm; Wing PCB underside Z4.70
- **Measured:** margin −1.25 mm (nominal) / −1.75 mm (with allowance); plug bottom Z0.35 (nominal) / −0.25 (reserved); plug-floor intersection 310.209 mm³ — FAIL, height-coupled and absolute: no routing change at 10.90 can pass it
- **Evidence:** `he-piantor-ghcheck/.issue275gh-runtime/gh-check.json` (q1_wing_end_at_plate_10_90, q4_height_ladder); input: frontier bodies at (17, −0.60), low-deck production case + D-046 pocket
- **Class:** PC-2 interference
- **State:** resolved — **Classification:** true problem (configuration-scoped). Basis: disposed by D-047 — GH conversion rejected, FPC configuration final at plate 10.90.
- **Suppression:** accepted by D-047.
- **Raw observations consolidated:** 1

### R-294-18 — GH harness at plate 12.95: full audit passes

- **Fingerprint:** interference-volume × GH-harness-28-wires × fixed-bodies @flipped-GH-12.95 × PC-2
- **Rule:** Q2 — 0 wire-wire and 0 wire-fixed contacts, 0 plan crossings, wire lengths ≤ 200 mm
- **Target:** 14 wires/side GH harness, flipped Main, plate 12.95 mm (the minimum passing plate of the Q4 ladder; arithmetic zero-gap at 12.65)
- **Measured:** wire-wire contacts 0; wire-fixed contacts 0; plan crossings 0; lengths 75.36–86.57 mm (bound 200); no wire contact with the Fly model, its 170 mm cable or its plug (normal pose)
- **Evidence:** `he-piantor-ghcheck/.issue275gh-runtime/gh-check.json` (q2_full_audit_at_plate_12_95, q4_height_ladder); input: 331 fixed bodies at (17, −0.60)
- **Class:** PC-2 interference (pass)
- **State:** resolved — **Classification:** as-designed. Basis: D-047 records plate 12.95 as the geometric precondition should GH ever be revisited; the configuration itself was not adopted.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 4

### R-294-19 — GH plug envelope overlaps flipped component reservations (12.95)

- **Fingerprint:** interference-volume × GH-plug-envelope × flipped-Main-component-reservations @flipped-GH-12.95 × PC-2
- **Rule:** conversion-stage keep-out — the plug envelope (21.76 × 8.15 × 4.85 mm reserved) must not overlap component reservations around J2/J3
- **Target:** plug envelope vs flipped Main-study reservations (bounding reservations, not physical parts; overlaps are height-invariant)
- **Measured:** wire-side placement: U4 5.8387, C28 4.2943, C17 3.0091, C2 0.382, C27 0.1338 mm³; board-side placement: C2 0.1824, Y1 0.0222, C22 0.0181 mm³ — a conversion respin must keep out or relocate U4 / C17 / C27 / C28 (and watch C2 / Y1 / C22), or fit lower-profile parts
- **Evidence:** `he-piantor-ghcheck/.issue275gh-runtime/gh-check.json` (q2 plug_envelope_vs_flipped_component_reservations); input: 331 fixed bodies at (17, −0.60)
- **Class:** PC-2 interference (reservation-level)
- **State:** resolved — **Classification:** true problem (conversion-stage item). Basis: moot under D-047 (GH rejected); reopens only if GH is revisited at plate 12.95.
- **Suppression:** accepted by D-047.
- **Raw observations consolidated:** 8

### R-294-20 — GH at 12.95: nearest clearances below the 0.3 mm example threshold

- **Fingerprint:** clearance × GH-exit-wires × Wing-underside-reservation/wire-pair @flipped-GH-12.95 × PC-3
- **Rule:** clearance ≥ 0.3 mm (design §3 example threshold)
- **Target:** exit wires R13/R14, L1/L2 vs Wing underside U_HC1 reservation; wire pair R1 vs R2 (spot BRepExtrema)
- **Measured:** 0.236 mm (wires vs U_HC1 reservation); 0.232 mm (R1 vs R2)
- **Evidence:** `he-piantor-ghcheck/.issue275gh-runtime/gh-check.json` (q2 nearest_clearances); input: 331 fixed bodies at (17, −0.60)
- **Class:** PC-3 clearance-shortfall
- **State:** resolved — **Classification:** true problem (configuration-scoped, minor). Basis: recorded in the passing 12.95 audit; configuration not adopted (D-047), so no live disposition is needed.
- **Suppression:** accepted by D-047.
- **Raw observations consolidated:** 2

### R-294-21 — GH at 12.95: in-situ service reserve far below the old cover bound

- **Fingerprint:** service-escape × GH-plug-detach × audited-corridor @flipped-GH-12.95 × PC-4
- **Rule:** accessible detach reserve — the #242/#246 cover-design bound was ≥ 30 mm; the study reports against it without failing on it alone
- **Target:** GH plug detach in the audited corridor; bow variant (fan bowed 6 mm toward case centre)
- **Measured:** clean detach reserve ≈ 0–2 mm (a 6 mm bow already grazes); bow grazes: R1 vs joint-screw-1 post 0.7083 mm³, L13 vs flip-Main-study-C26 0.0179 mm³; practical detach sequence is board removal then hand-held plug extraction (7.15 mm axial)
- **Evidence:** `he-piantor-ghcheck/.issue275gh-runtime/gh-check.json` (service_reserve); input: 331 fixed bodies at (17, −0.60)
- **Class:** PC-4 assembly-escape-shortfall
- **State:** resolved — **Classification:** true problem (configuration-scoped). Basis: reported in the study; configuration not adopted (D-047).
- **Suppression:** accepted by D-047.
- **Raw observations consolidated:** 3

### R-294-22 — Route A0 (no case change): cable rides the tray and contacts it

- **Fingerprint:** interference-volume × EZmate-cable-A0 × tray-right/screw/ZIF @flipped-pose × PC-2
- **Rule:** gate — unexpected contacts must be 0; centreline must consume the stock 170 mm cable
- **Target:** route A0 (pack z 1.60..2.80 on the tray surface), flipped pose
- **Measured:** tray-right 321.58 mm³; joint-screw-1 post graze 0.162 mm³; ZIF-main-right graze 0.302 mm³; centreline 148.5 mm (21.5 mm short of consuming the 170 mm cable)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (A0); `route_audit.log`; `flip-usb.md` §3-A; input: fitted body set (343 bodies), Main-attached bodies flipped about Z = 5.30, pocket A applied
- **Class:** PC-2 interference
- **State:** resolved — **Classification:** true problem (route variant). Basis: variant failed; superseded by the adopted A2 channel (D-051, R-294-30).
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 4

### R-294-23 — Positive control: synthetic overlap pair

- **Fingerprint:** self-test × synthetic-box-pair × method × unclassified
- **Rule:** control — a pair with known overlap 13.5 mm³ must measure 13.5 mm³
- **Target:** synthetic box pair, repaired Common method
- **Measured:** 13.5 mm³ (exact), sighted identically in the final audit log, in `audit278.json` (self_test_cache.synthetic) and in the A2-implementation controls
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/final_audit.log`; `audit278.json`; `a2-impl-flipped.json` (controls)
- **Class:** unclassified (method control)
- **State:** resolved — **Classification:** as-designed (method verified). Basis: flip-usb.md §2 positive controls.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 3

### R-294-24 — Positive control: body-cache fidelity on a genuine overlapping pair

- **Fingerprint:** self-test × route-A0-cable × tray-right-cache @method × unclassified
- **Rule:** control — the cached STEP body set must reproduce the in-process value for a genuine overlapping pair
- **Target:** route A0 cable vs tray-right, computed from the STEP body cache
- **Measured:** 321.58 mm³ — identical to the in-process value (R-294-22)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/final_audit.log`; `audit278.json` (self_test_cache.A0_vs_tray_right_cache); `a2-impl-flipped.json` (controls); `decisive.log` (tray-right vol 85092.8, cache said 85092.8)
- **Class:** unclassified (method control)
- **State:** resolved — **Classification:** as-designed (cache fidelity and the Common path both exercised on a genuine pair). Basis: flip-usb.md §2.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 3

### R-294-25 — Route D (south-margin loop): too long, and contacts both east screw posts

- **Fingerprint:** interference-volume × EZmate-cable-D × tray-right/joint-screw-posts @flipped-pose × PC-2
- **Rule:** gate — unexpected contacts 0; centreline ≤ 170 mm (stock cable)
- **Target:** route D (exit south, dress to the true south margin y ≈ 72–74.5, return north west of the flipped ZIF envelope)
- **Measured:** centreline 191.72 mm > 170 mm — binding; joint-screw-1 post 2.413 mm³; joint-screw-2 post 2.413 mm³; tray-right 465.15 mm³. The Stage B estimate ("loop adds ~30 mm, 170 mm has the length") is not confirmed by measurement
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (D); `route_audit.log`; `flip-usb.md` §3-D; input: fitted body set (343 bodies), flipped
- **Class:** PC-2 interference
- **State:** resolved — **Classification:** true problem (route variant). Basis: variant failed on length and contacts; superseded by A2 (D-051).
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 4

### R-294-26 — Route B (east channel): hop over the right FFC sheet contacts it

- **Fingerprint:** interference-volume × EZmate-cable-B × FFC-sheet-right/tray-right @flipped-pose × PC-2
- **Rule:** gate — unexpected contacts 0
- **Target:** route B (Stage B west construction mirrored east; floor-level loop in a 1.0-deep east channel, hop over the right FFC sheet at y 1..−5)
- **Measured:** FFC-sheet-right contact 3.215 mm³ at the hop transition; tray-right 165.253 mm³ outside its channel. No east/west asymmetry exists to exploit: the Type D sheets are exact mirror images (inner edges at x = ±2.059), J4 and the Fly are on-axis, and the hop failure reproduces in mirror (west 5.385 mm³ in R-294-14 vs east 3.215 mm³ here)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (B); `route_audit2.log`; `flip-usb.md` §3-B; input: fitted body set (343 bodies), flipped
- **Class:** PC-2 interference
- **State:** resolved — **Classification:** true problem (route variant). Basis: variant failed; the passing A2 differs by crossing mode — under the sheet, never over it (R-294-28/R-294-29).
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 2

### R-294-27 — Route A1 (shallow channel): channel too shallow for the real tray top

- **Fingerprint:** interference-volume × EZmate-cable-A1 × tray-right @flipped-pose × PC-2
- **Rule:** gate — unexpected contacts 0
- **Target:** route A1 (channel 0.35 deep, floor Z1.25, plan fixed vs posts/ZIF); plan variants W = 0 / +2 / −2
- **Measured:** tray-right 296.584 mm³ (channel too shallow — the tray top on the route is ≈ Z2.0, see R-294-38); centreline lengths: W = 0 → 172.35 mm, W = +2 → 168.64 mm (the fixed plan), W = −2 → 176.28 mm
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (A1_fixed, A1_fixed_plan); `route_audit2.log`; `flip-usb.md` §3-A; input: fitted body set (343 bodies), flipped
- **Class:** PC-2 interference
- **State:** resolved — **Classification:** true problem (route variant). Basis: superseded by A2 (floor Z1.20), adopted by D-051.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 3

### R-294-28 — Under-sheet crossing at tray-surface level: marginless

- **Fingerprint:** clearance × EZmate-cable-C-test × FFC-sheets @tray-surface-level × PC-3
- **Rule:** clearance ≥ 0.3 mm (design §3 example threshold); crossing volume must be 0
- **Target:** family C straight test segment crossing under both sheets inside the tray corridor, pack top Z2.80 (tray-surface level)
- **Measured:** crossing volume 0 (both sides); extrema distance 0.032 mm (left sheet), 0.025 mm (right sheet) — geometrically real but marginless
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (C_floor); `route_audit.log`; `flip-usb.md` §3-C; input: fitted body set (343 bodies), flipped
- **Class:** PC-3 clearance-shortfall
- **State:** resolved — **Classification:** true problem (at this level). Basis: mechanism test only; the adopted configuration crosses at channel level (R-294-29), where the same measurement is 0.325 mm.
- **Suppression:** resolved-confirmed (superseded by the A2 geometry, D-051).
- **Raw observations consolidated:** 2

### R-294-29 — Under-sheet crossing at A2 channel level: passes with margin

- **Fingerprint:** clearance × EZmate-cable-C-test × FFC-sheets @A2-channel-level × PC-3
- **Rule:** clearance ≥ 0.3 mm (design §3 example threshold); crossing volume must be 0
- **Target:** family C test segment at A2 channel level, pack top Z2.50
- **Measured:** crossing volume 0 (both sides); extrema distance 0.326 mm (left), 0.325 mm (right)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (C_channel); `route_audit.log`; `flip-usb.md` §3-C; input: fitted body set (343 bodies), flipped
- **Class:** PC-3 clearance-shortfall (pass at the adopted level)
- **State:** accepted — **Classification:** as-designed. Basis: this is the crossing geometry the adopted A2 channel uses (D-051).
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 2

### R-294-30 — A2 final audit: zero unexpected contacts in the full flipped set

- **Fingerprint:** interference-volume × EZmate-cable-A2 × all-fixed-bodies @flipped-pose × PC-2
- **Rule:** gate — unexpected contacts must be 0 over the full fitted body set
- **Target:** adopted A2 route (channel floor Z1.20; centreline per flip-usb.md §4), flipped pose, 343 bodies
- **Measured:** hits {} — unexpected contacts 0; engagement only with the J4 header (35.417 mm³), the Fly EZmate housing (1.552 mm³) and the body-set plug model (22.73 mm³), all mating interfaces
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (A2); `final_audit.log`; `flip-usb.md` §4; input: fitted body set (343 bodies), flipped, channel cutter fused (gross 2661.4 mm³)
- **Class:** PC-2 interference (pass)
- **State:** resolved — **Classification:** as-designed. Basis: D-051 adopts A2 on this audit ("unexpected contacts 0").
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-31 — A2 extrema clearance to the right FFC sheet: 0.314 mm

- **Fingerprint:** clearance × EZmate-cable-A2-final-solid × FFC-sheet-right @flipped-pose × PC-3
- **Rule:** clearance ≥ 0.3 mm (design §3 example threshold)
- **Target:** dressed A2 cable, final solid, vs right FFC sheet (left sheet for contrast)
- **Measured:** 0.314 mm (right sheet); 5.29 mm (left sheet); gate sheet volume = 0. Sighted identically in `audit278.json` (A2.sheet_clearance), `final_audit.log`, and flip-usb.md §4
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json`; `final_audit.log`; `flip-usb.md` §4; input: fitted body set (343 bodies), flipped, A2 channel cut
- **Class:** PC-3 clearance-shortfall (near-threshold pass — 0.014 mm over the example threshold)
- **State:** accepted — **Classification:** accepted risk. Basis: D-051 adopts A2 with this figure in its basis text ("final-solid extrema to the right FFC sheet 0.314mm"). The 0.3 mm figure is the design document's example threshold, not a project specification; the PO acceptance is of the measured value itself.
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 3

### R-294-32 — A2 channel: material removed and remaining web

- **Fingerprint:** removed-volume/web × A2-channel × tray-right @case × PC-1
- **Rule:** the channel must remove tray material only, break no boss or screw feature, and leave a web thicker than pocket A's adopted 0.60 mm
- **Target:** A2 route channel (7.5 mm wide, floor Z1.20, from the J4 exit apron into pocket A's east side); channel cutter gross volume 2661.4 mm³
- **Measured:** removed 931.3 mm³, all from tray-right (tray-left 0.0 mm³); the plan dodges both joint-screw posts and the H1 screw (zero hits on all screw/post bodies in the A1-fixed/A2 audits); remaining web under the channel floor is the untouched tray section below Z1.20 — thicker than pocket A's 0.60 mm web
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (A2.channel_removed_mm3, channel_gross_mm3); `final_audit.log`; `flip-usb.md` §3-A/§4; input: fitted body set (343 bodies), flipped
- **Class:** PC-1 manufacturing-margin (case material / web aspect)
- **State:** accepted — **Classification:** as-designed. Basis: D-051 adopts the channel with these figures ("removing 931.3mm3").
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 3

### R-294-33 — A2 cable length fits the stock 170 mm cable

- **Fingerprint:** length-fit × EZmate-cable-A2-centreline × stock-170mm @flipped-pose × PC-4
- **Rule:** dress centreline ≤ 170 mm (stock on-hand cable), without tension
- **Target:** A2 route centreline (Catmull-Rom between plug centres), flipped pose
- **Measured:** 168.64 mm ≤ 170 mm; the residual ~1.4 mm is absorbed by the dress's natural bow — the cable is not tensioned. Sighted in the A2 gate, the A1-fixed gate, and the A2-implementation baseline (all 168.64 mm)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (A2, A1_fixed); `a2-impl-flipped.json` (baseline_unmodified.length_mm); `flip-usb.md` §4; input: fitted body set (343 bodies), flipped
- **Class:** PC-4 assembly-escape-shortfall (positive instance — length escape sufficient)
- **State:** accepted — **Classification:** as-designed. Basis: D-051 ("A2 centreline 168.64mm <= 170mm stock cable").
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 3

### R-294-34 — A2 service: both EZmate plugs pull straight down clear

- **Fingerprint:** service-escape × EZmate-plugs-J4-and-Fly × all-fixed-bodies @flipped-pose × PC-4
- **Rule:** service sweep — a 2.0 mm downward sweep of each plug box must hit no fixed body (no board lift for the USB plugs)
- **Target:** J4-end plug and Fly-end plug, flipped pose, A2 configuration
- **Measured:** sweep hits {} at both ends (J4 {}, Fly {}); cable removal is then a slide-out along the open-top channel toward the Fly end — the under-sheet crossings are passed by sliding, never trapped
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/audit278.json` (service_sweep_down2); `route_audit.log` (sweep lines); `flip-usb.md` §4 service sequence; input: fitted body set (343 bodies), flipped
- **Class:** PC-4 assembly-escape-shortfall (positive instance)
- **State:** resolved — **Classification:** as-designed. Basis: D-051 ("both EZmate plugs pull straight down 2.0mm clear of all fixed bodies (no board lift for the USB plugs)").
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 2

### R-294-35 — Flipped pose: USB-C insertion at the Fly is unaffected

- **Fingerprint:** service-escape × USB-C-insertion × gate-set @flipped-pose × PC-4
- **Rule:** USB-C insertion bodies in the gate set must show 0 contacts
- **Target:** USB-C plug insertion at the Fly Daughterboard (mouth at the north wall opening), flipped pose, A2 configuration
- **Measured:** 0 contacts (insertion bodies were in the gate set of the A2 final audit)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §4; gate set of `audit278.json` (A2); input: fitted body set (343 bodies), flipped
- **Class:** PC-4 assembly-escape-shortfall (positive instance)
- **State:** resolved — **Classification:** as-designed. Basis: D-051 ("USB-C insertion unaffected").
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-36 — A2: cable passes 0.10 mm above the splice plate

- **Fingerprint:** clearance × EZmate-cable-A2 × splice-plate @flipped-pose × PC-3
- **Rule:** clearance ≥ 0.3 mm (design §3 example threshold)
- **Target:** A2 cable over the splice plate (separate body, top Z1.20, locally forming the channel floor), flipped pose
- **Measured:** cable 0.10 mm above the splice plate
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §3-A (disclosure); input: fitted body set (343 bodies), flipped
- **Class:** PC-3 clearance-shortfall
- **State:** accepted — **Classification:** accepted risk. Basis: disclosed in the study that D-051 adopts as its basis; the plate is a fixed floor feature, not a moving or mating part.
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 1

### R-294-37 — A2 crossings locally notch the FFC channel floor

- **Fingerprint:** clearance/support × A2-channel × FFC-channel-floor @case × PC-3
- **Rule:** the FFC sheet must remain supported and unaffected outside the disclosed notches; gate cable-vs-sheets = 0
- **Target:** 2–3 crossings where the A2 channel crosses the FFC formed channels
- **Measured:** FFC channel floor locally lowered to Z1.20 in a ≤ 7.5 mm notch at each crossing; the FFC sheet (z 2.825..3.075) bridges the notch and is otherwise unaffected; gate cable vs sheets = 0
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §3-A (disclosure); D-051 text ("the FFC channel floor is locally notched <=7.5mm at 2–3 crossings, as disclosed in the study")
- **Class:** PC-3 clearance-shortfall (support geometry aspect)
- **State:** accepted — **Classification:** accepted risk. Basis: explicitly named in D-051.
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 1

### R-294-38 — Tray top along the J4→Fly path is ≈ Z2.0 (Z3.0 at the pocket rim)

- **Fingerprint:** clearance-basis × tray-surface-probes × J4-to-Fly-path @case × PC-3
- **Rule:** route design must use the measured tray surface, not the Wing bay's Z1.60
- **Target:** 1 × 1 mm probe columns on the route points, flipped configuration
- **Measured:** tray material up to Z ≈ 2.0 along the path; Z 3.0 at the pocket-A east rim (14, 47). This is the measured basis that defeats shallow reliefs (R-294-27)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §1; `diag_tray.json` / `diag2.log` (diagnostics); input: fitted body set (343 bodies)
- **Class:** PC-3 clearance-shortfall (basis measurement)
- **State:** resolved — **Classification:** as-designed (measured basis fact, carried into the A2 design). Basis: flip-usb.md §1.
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-39 — A2 implementation baseline: unmodified production tray still contacts the route cable

- **Fingerprint:** interference-volume × EZmate-cable-A2-route × tray-right-unmodified @production-tree × PC-2
- **Rule:** gate — unexpected contacts must be 0 once the A2 channel is implemented in the production case tree
- **Target:** A2 route cable vs the production tray-right **before** the channel cut (implementation-stage baseline, Issue #278 follow-on)
- **Measured:** tray-right 457.478 mm³ (baseline_unmodified; engagements as in R-294-30's family: J4 header 35.417, Fly housing 1.552, plug model 22.73)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/a2-impl-flipped.json`; controls in the same file reproduce R-294-23/R-294-24; input: fitted body set, flipped, production tree unmodified
- **Class:** PC-2 interference
- **State:** in-progress — **Classification:** true problem (in the unmodified tree — expected: the channel is not yet cut there). Basis: D-051 records that implementation of the channel into the production case tree follows as separate work; that work was stopped mid-run at the 2026-11-19 wireless pivot and is deferred until the wireless case work touches the tray.
- **Suppression:** in-progress under Issue #278.
- **Raw observations consolidated:** 1

### R-294-40 — A2 dress bend radii stay inside the modelled discipline

- **Fingerprint:** bend-radius × EZmate-cable-A2-dress × serpentine-U-turns @flipped-pose × PC-4
- **Rule:** centreline bend radius ≥ 5 mm (modelled discipline for the 4-wire flat pack)
- **Target:** A2 dress minimum radii (serpentine U-turns)
- **Measured:** R ≈ 5.25–5.5 mm centreline at the tightest U-turns — inside the discipline
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §4; input: A2 route model (pack 4.5 × 1.2 mm)
- **Class:** PC-4 assembly-escape-shortfall (positive instance)
- **State:** accepted — **Classification:** as-designed. Basis: part of the A2 configuration adopted by D-051; the real-cable side of this figure is R-294-41.
- **Suppression:** accepted by D-051.
- **Raw observations consolidated:** 1

### R-294-41 — Real-cable build-time confirmations: NOT YET MEASURED

- **Fingerprint:** verification × real-EZmate-cable × modelled-values @build-time × unclassified
- **Rule:** at build time, measure the on-hand cable against the study's modelled values before relying on the flipped USB route (D-051 build-time confirmation)
- **Target:** the physical stock 170 mm EZmate cable (PO-owned, ×2)
- **Measured:** MISSING — no artifact records a measurement of the real cable. Modelled values awaiting confirmation (from flip-usb.md §5): flat-bundle thickness 1.2 mm (sets the A2 under-sheet clearance 1:1 — modelled 0.325 mm at channel level, R-294-29); plug envelope 5.0 × 3.5 × 1.30 mm (from the #275 audit model, not a datasheet); minimum comfortable bend radius vs the modelled R ≥ 5 mm discipline (R-294-40); cable length tolerance around the 170 mm nominal (dress consumes 168.64 mm, R-294-33)
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §5 (the measurement list); D-051 (build-time confirmation paragraph). No measurement artifact exists.
- **Class:** unclassified
- **State:** in-progress — **Classification:** unclassified - needs verification. Basis: D-051 makes the confirmation a build-time gate; until the cable is measured, the A2 margins that depend on the bundle thickness (R-294-29, R-294-31) rest on the modelled 1.2 mm.
- **Suppression:** in-progress under Issue #278 (build-time gate) — carried with 0 raw observations: no kernel observation exists yet, so this entry contributes 0 to the pilot reconciliation arithmetic.
- **Raw observations consolidated:** 0

### R-294-42 — Family E: the Fly seat cannot rotate 180°

- **Fingerprint:** service-escape × Fly-daughterboard-seat-rotation × north-wall-opening @case × PC-4
- **Rule:** a rotated seat must keep the USB-C mouth at the wall opening (W16, north wall only)
- **Target:** Fly Daughterboard seat (mounting symmetric: holes at ±9.50 mm, EZmate housing centred x −3.3..3.3), rotated 180°
- **Measured:** the board would physically sit rotated, but the USB-C mouth (0.30 mm inside the north wall opening in the adopted pose) would land 8.30 mm south of the opening, facing the case interior — no USB-C plug could ever reach it
- **Evidence:** `he-piantor-flipusb/.issue278-runtime/flip-usb.md` §3-E; input: adopted low-deck production tree Fly seat (centre (0, −50.136) at 17 mm pitch)
- **Class:** PC-4 assembly-escape-shortfall (orientation impossible)
- **State:** resolved — **Classification:** true problem (variant). Basis: family E rejected on this measurement; the adopted pose is unchanged (D-051 configuration).
- **Suppression:** resolved-confirmed.
- **Raw observations consolidated:** 1

### R-294-43 — Wing↔Main seam at the fitted pose: 0.5593 mm against the 0.55 floor

- **Fingerprint:** seam-clearance × Wing-Rev.6 × Main-Rev.10 @fitted-pose × PC-1
- **Rule:** seam ≥ 0.55 mm (project floor of the #275 audit); overlap must be 0
- **Target:** Wing Rev.6 / Main Rev.10 seam, from the saved boards at the fitted pose, both pitches, both sides
- **Measured:** seam 0.5593 mm (both pitches, both sides); overlap 0 — margin over the floor: 0.0093 mm
- **Evidence:** REPORT §4 (`he-piantor-mainsym/hardware/kicad/qualification/issue-275-main-rev10/REPORT.md`); D-046 text ("継ぎ目 0.5593mm（両ピッチ・両側）")
- **Class:** PC-1 manufacturing-margin (near-floor pass)
- **State:** accepted — **Classification:** as-designed. Basis: adopted by D-046 with this figure in the decision text.
- **Suppression:** accepted by D-046.
- **Raw observations consolidated:** 1
