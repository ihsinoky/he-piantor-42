# Issue #294 Pilot A — semantic layer run over the Main Rev.10 audit findings

- Date: 2026-11-19. Worker: Muse (Wonder), PMO-dispatched.
- Inputs: the Issue #275 fitted audits (normal / flipped / flipped-J4),
  pocket and case-delta verifications, Issue #275 Phase 2 GH geometric
  check, and the Issue #278 flipped-USB route audit (incl. A2) —
  artifacts in the `he-piantor-mainsym`, `he-piantor-ghcheck` and
  `he-piantor-flipusb` worktrees' runtime directories, plus the
  issue-275-main-rev10 REPORT.
- Interpretation basis: D-046, D-047, D-051.
- Output register: `docs/review-ledger.md` (43 entries, R-294-01…43);
  procedure: `docs/review-procedure.md`.
- Counting rule: a **raw observation** is one discrete kernel output
  item (a hit value, a clearance, a gate result, a control result)
  recorded in a named artifact. Each register entry counts once (its
  primary observation); every further observation consolidated into
  that entry (other pitch, other side, re-run, later sighting of the
  same value) counts as **duplicates-merged**. Intermediate
  computation lines (e.g. the case-delta growth internals) are not
  gate results and are excluded; board-level electrical gates
  (DRC/ERC/Vfar) and procurement crawl data are out of scope.

## 1. NEW findings

Three findings have no prior disposition in any decision. All three
are the same class (PC-2 interference, marginal envelope/sheet
grazes) and are grouped as one PO-judgment item in §4.

| entry | finding | measured |
|---|---|---|
| R-294-02 | Normal pose, left FFC sheet grazes the C23 study envelope | 0.488 mm³ as audited; 0.016 mm³ on re-test at the as-built J2 centre (the study envelope sits ~1.4 mm off the as-built centre) |
| R-294-05 | Flipped pose, right FFC sheet grazes a case joint screw | 0.503 mm³ |
| R-294-06 | Flipped pose, right FFC sheet grazes the flipped C23 envelope | 0.049 mm³ (0.03 mm z-touch at the envelope corner) |

The #275 REPORT calls these "marginal grazes, recorded" and the
normal-pose one a "build watch item — not a route blocker". That is
a study opinion; no D-xxx accepts them, and risk acceptance is a PO
gate (procedure §7.4), so the semantic layer cannot close them
itself. Everything else in the audit family was already disposed —
see §3.

## 2. SAME-CLASS groupings

### PC-2 interference (19 entries)

- **Marginal grazes, undisposed → NEW:** R-294-02, R-294-05,
  R-294-06 (§1). Past example of the class handled by acceptance:
  none for grazes — the class's past dispositions are variant
  rejections and adoptions below.
- **Within-corridor form contact (accepted, D-046):** R-294-03
  (normal, 290.409 mm³), R-294-07 (flipped, 246.904 mm³) — the #264
  containment class: overlap with the channel support form inside
  the corridor, plan footprint outside corridor 0.000 mm².
- **Own-engagement (excluded class, confirmed):** R-294-13 (J4 plug
  vs its own header, 22.75 / 22.862 / 35.417 mm³ across runs).
- **Failed routes/variants (true problems, closed by superseding
  adoption):** R-294-14 (west escape, sheet hop 5.385 mm³ — the
  D-046 named residual, closed by D-051), R-294-22 (A0, tray
  321.58 mm³), R-294-25 (D, 191.72 mm length + posts 2.413 ×2),
  R-294-26 (B, sheet hop 3.215 mm³), R-294-27 (A1, shallow channel
  296.584 mm³), R-294-10 (pocket variant B, screw hit 2.011 mm³).
- **GH configuration (closed by D-047 rejection):** R-294-17 (plug
  vs tray floor at 10.90, 310.209 mm³, margin −1.25 mm),
  R-294-19 (plug envelope vs component reservations at 12.95,
  ≤ 5.8387 mm³).
- **Passes:** R-294-01, R-294-04 (zero-contact poses), R-294-18
  (GH at 12.95: 0 contacts), R-294-30 (A2 final: 0 unexpected
  contacts).
- **Open:** R-294-39 — the A2 route against the *unmodified*
  production tray still measures 457.478 mm³; expected (the channel
  is not cut there yet), in-progress under Issue #278.
- **Method artefacts (class unclassified, grouped here by
  mechanism):** R-294-15 (duplicate cable model, 4.157 mm³),
  R-294-16 (fail-open intersect vs the tray-left fragment compound,
  22.75 mm³ at every z offset). Both verified artefacts; no gate
  number depends on either.

### PC-3 clearance-shortfall (8 entries)

- **Resolved by an adopted feature:** R-294-08 — flipped component
  residual 0.60 mm, restored to 1.60 mm by pocket A (D-046).
- **Mechanism pair (same measurement, two levels):** R-294-28 —
  under-sheet crossing at tray-surface level, 0.025/0.032 mm
  (marginless, superseded); R-294-29 — at A2 channel level,
  0.325/0.326 mm (the adopted geometry, D-051). Past example
  handling: a marginless clearance is not accepted at face value;
  the configuration was changed until the same measurement carried
  margin.
- **Accepted with the number in the decision basis (D-051):**
  R-294-31 (A2 extrema 0.314 mm), R-294-36 (cable 0.10 mm above the
  splice plate), R-294-37 (FFC channel floor notches ≤ 7.5 mm).
- **Basis measurement:** R-294-38 (tray top ≈ Z2.0 / Z3.0 on the
  route — the fact that killed the shallow-channel variants).
- **Non-adopted configuration:** R-294-20 (GH at 12.95: 0.236 /
  0.232 mm; moot under D-047).

### PC-4 assembly-escape-shortfall (7 entries)

- **Accepted service consequence:** R-294-12 — flipped FFC
  (un)locking requires lifting the Main board (D-046; D-051
  confirms unchanged). Contrast inside the same class: R-294-34 —
  the EZmate plugs need **no** board lift (2.0 mm straight-down
  sweep, hits {}), and R-294-35 — USB-C insertion unaffected.
- **Positive instances in the adopted A2:** R-294-33 (centreline
  168.64 ≤ 170 mm), R-294-34, R-294-35, R-294-40 (bend radii
  R ≈ 5.25–5.5 ≥ 5 mm discipline).
- **Impossible variant:** R-294-42 — Fly seat rotation puts the
  USB-C mouth 8.30 mm from the only wall opening.
- **Non-adopted configuration:** R-294-21 — GH in-situ detach
  reserve ≈ 0–2 mm vs the old ≥ 30 mm cover bound (reported in the
  study; moot under D-047).

### PC-1 manufacturing-margin (3 entries)

- R-294-43 — Wing↔Main seam 0.5593 mm vs the 0.55 mm floor
  (margin 0.0093 mm), adopted in D-046's text.
- R-294-09 — pocket A remaining-web production note (audit model
  2.623 mm remaining; nominal web 0.60 mm to be confirmed at the
  case-print gate), D-046.
- R-294-32 — A2 channel removal 931.3 mm³ with web thicker than
  pocket A's, D-051.
- Class seed (design §5, outside this pilot's scope): wireless
  Matrix via-pad 0.1002 mm vs the 0.10 mm floor (Issue #288).

### PC-5 symmetry-break (1 entry)

- R-294-11 — tray relief pair 6.305 / 6.305 mm³ under Rev.10,
  replacing the asymmetric Rev.9 pair 6.521 / 6.305 mm³ (positive
  instance: asymmetry removed, D-046). Supporting observation in
  R-294-26: the Type D FFC sheets are exact mirror images (inner
  edges x = ±2.059), which is why the east mirror route failed
  identically to the west.

### Method controls (unclassified, 2 entries)

- R-294-23 — synthetic overlap pair: 13.5 mm³ known → 13.5 mm³
  measured (exact), three identical sightings.
- R-294-24 — body-cache fidelity: A0 vs tray-right recomputed from
  the STEP cache = 321.58 mm³, identical to the in-process value.

## 3. SUPPRESSION breakdown

39 of the 42 observation-bearing entries were already known and are
suppressed from the NEW list with these reasons (every one remains
in the ledger with its basis):

| reason | entries | count |
|---|---|---|
| accepted by D-046 | R-294-03, 07, 08, 09, 10, 12, 43 | 7 |
| accepted by D-047 | R-294-17, 19, 20, 21 | 4 |
| accepted by D-051 | R-294-29, 31, 32, 33, 36, 37, 40 | 7 |
| in-progress under Issue #278 | R-294-39 | 1 |
| resolved-confirmed | R-294-01, 04, 11, 13, 14, 15, 16, 18, 22, 23, 24, 25, 26, 27, 28, 30, 34, 35, 38, 42 | 20 |
| **suppressed total** | | **39** |

Carried separately: R-294-41 (real-cable build-time confirmations)
— measured **MISSING**, classification
`unclassified - needs verification`, in-progress under Issue #278
as the D-051 build-time gate. It contributes 0 raw observations
(no kernel observation of the real cable exists), so it does not
enter the arithmetic below; it is listed here so the MISSING path
is visible, not silent.

### Reconciliation (computed from the register)

```
raw observations        = 92   (sum of "Raw observations consolidated" over 43 entries)
entries with ≥1 obs.    = 42   (+ R-294-41 with 0)
new                     =  3   (R-294-02, 05, 06)
suppressed              = 39   (table above)
duplicates-merged       = 50   (92 − 42: pitch repeats ×3, L/R second-side
                                items ×4, re-tests and repeat sightings of
                                the same value ×15, supporting items
                                consolidated into one finding ×28)
check: 3 + 39 + 50      = 92   ✓
```

## 4. Needs-PO-judgment items (choices)

**J-1 — The three marginal FFC grazes (R-294-02 / 05 / 06).**
Technical points, explained by PMO: in both poses the flexible FFC
sheet's conservative solid model touches fixed bodies by
0.049–0.503 mm³. The largest (0.488 mm³) is measured against a
study envelope known to sit ~1.4 mm away from the as-built
connector centre; re-measured at the true centre it is 0.016 mm³
(a corner touch). The flipped joint-screw graze (0.503 mm³) is
against a real body, at the sheet's bend corner. The #275 study
judged all three non-blocking ("build watch item"); no decision
has accepted them.

- **(a)** Accept all three as recorded build-watch items: at first
  build, visually confirm the sheet dresses clear at the three
  sites; no model or design change.
- **(b)** Fix the study-envelope offset (~1.4 mm, #264 lineage) and
  re-run gate 1 for both poses before accepting anything, so the
  C23 numbers are measured against correctly placed envelopes.
- **(c)** Accept the two C23 envelope grazes (artefact-dominated)
  under (a), and treat only the joint-screw graze (real body) as a
  build-watch item with a photo check at first assembly.

No other item in this pilot needs a PO judgment: every remaining
finding is disposed by D-046 / D-047 / D-051, confirmed resolved,
or tracked under Issue #278 (R-294-39 implementation, R-294-41
build-time measurement).

## 5. Notes for the record

- D-051 is recorded on the Issue #278 branch (PR #286, unmerged at
  pilot time); it is used as an interpretation basis per the pilot
  brief. If PR #286's record changes, R-294-29…41 classifications
  citing D-051 must be re-checked.
- The artifacts record no input STEP hash; ledger evidence cites
  the body-set identity the artifacts name (procedure §2 allows the
  named identity; future kernel runs should record the hash).
- Promotion candidates when they harden: the under-sheet crossing
  rule (cross under, never over — R-294-14/26/28/29) and the
  envelope-offset lesson (R-294-02) are findings.md material once
  the PO disposes J-1.
