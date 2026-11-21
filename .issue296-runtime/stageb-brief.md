# Stage B brief — wireless case 2D package on D-062 + delta=9.5 (Issue #296)

## Context

The wireless case design (Issue #296) had its Stage 1 package superseded
when the battery moved to the centre bay (D-062). Two inputs were open;
both are now settled:

- **Battery: D-062** — 3× AA NiMH, axes N-S, side by side E-W in the
  centre bay, on a floor power board over a levelled case floor; cover
  re-formed as the battery cover, top 16.65; Fly relocated RIGHT, USB
  opening on the north gable wall; JBATT cable ≈100 mm.
- **Wing separation: delta = 9.5 mm/side** (PO decision 2026-11-21,
  D-062 amendment on PR #301): reached by a **plate tip notch only** —
  the wireless Wing boards are unchanged. Outline **310 × 146.1 mm**;
  FFC channel **11.5 mm**.

## Inputs of record (read first)

- Issue #296 (gh issue view 296) including the D-062 scope comment and
  the delta guidance comment.
- Centre study: `~/workspace/goals/he-piantor-42-keyboard-pmo/hidden_files/cell-arrangement-centre-2026-11-20.md`
- Wing-shape study: `~/workspace/goals/he-piantor-42-keyboard-pmo/hidden_files/wing-shape-centre3-2026-11-21.md`
  (option A = the adopted delta: plate notch geometry, channel 11.5).
- D-062 + its amendment: on branch `issue-296-centre3`
  (`git show origin/issue-296-centre3:docs/decisions.md`, D-062 section).
- Superseded Stage 1 package (geometry reference, do not copy its
  layout): worktree `~/workspace/projects/he-piantor-case296`,
  `.issue296-runtime/case-2d.md`. Its durable findings (antenna band,
  cable lengths for the old geometry, switch/button/LED proposals) are
  inputs to re-check, not conclusions.
- Power board Stage 1 design note (Issue #303):
  `~/workspace/projects/he-piantor-pwr/.issue303-runtime/design-note.md`
  — its Stage-2 input list (bay inner dimensions, floor level, cable
  exit, switch position, wall thickness for the contact clips) is a
  checklist your package must answer.
- Board files of record: wireless Main on origin/main (SHA 75db72bc…,
  D-063); wireless Wing Stage-2 set (PR #300 tree at commit 3fcad246f);
  wireless Matrix (origin/main).
- Case production tree: `hardware/case/issue-263-lowdeck-production/`
  (D-042 low deck, plate 10.90, keytop datum 22.00 provisional) + the
  south-straightened outline (going-forward outline per the 2026-11-19
  study, branch `case-south-notch`).

## Deliverable 1 — 2D approval package

Top-view figure(s) + section figure(s) at legible scale (differences
visible; tight zooms where a dimension is decided), covering:

1. Outline 310 × 146.1 with the south edge straightened; Wing poses at
   delta=9.5 with the **plate tip notch** drawn from the wing-shape
   study's geometry.
2. Centre bay: levelled floor (state the floor Z and what moulding is
   removed), the 3-cell block (48.5 × 56 envelope + assembly margin),
   floor power board outline derived from the bay (this is the power
   board Stage-2 input — give its dimensions and datum), cover form
   (top 16.65, under the 22.00 datum).
3. Fly at the right position: exact offset, USB opening on the north
   gable wall, EZmate route length re-measured at delta=9.5.
4. FFC channel 11.5 mm: Main J2/J3 to Wing J_WING spans re-measured;
   state what FFC/FPC solution the 11.5 mm channel implies (the D-062
   record expects the stock folded-FFC qualification to lapse — assess
   and name the follow-up precisely).
5. JBATT route: power board south exit to Main JBATT, length at the
   final geometry; the GH–GH cable (power board Stage 1 decision).
6. Trackpad island (D-053, Ø44, centre shell (0,48), surface Z12.70)
   against the final outline; antenna south PETG band depth at the
   straightened outline.
7. Placements re-checked at the final geometry: bay-wall slide switch
   (power board Stage 1: off-board, wired to the board's loop pads —
   give its case position and wire route), pairing-button access
   (plunger proposal from Stage 1 — keep, move, or drop, with reasons),
   LED light pipe position vs DLED's exact board position.
8. Main fixing: tray centre joint + centre floor infill, Main bosses
   (D-062 consequences) at the final geometry.
9. Reconcile the outline-depth ledger discrepancy (145.6 vs 146.1)
   found in the record — state which is right and why.

Figures go to `~/workspace/goals/he-piantor-42-keyboard-pmo/files/`
(case296b-2d-topview.png, case296b-2d-sections.png); design note to
`.issue296-runtime/case-2d-stageb.md` with every dimension's source.

## Deliverable 2 — Issue #294 Pilot B (alongside)

Run the semantic-review Pilot B per `docs/review-procedure.md`:
board-vs-case kernel audit of the wireless set at the files of record.
Numbers only from the kernel or recorded kernel artifacts; every
interpretation cites its basis; suppressions visible. Entries go to
`docs/review-ledger.md` on this branch. Its concrete output for this
issue: the exact case-frame coordinates of JBATT, DLED and SW1 on the
wireless Main, consumed by Deliverable 1 item 7.

## Pass conditions / limits

- This is a 2D approval package: **no 3D modelling** (PO approves the
  2D figures first — standing project rule).
- Every clearance the package claims is measured, not eyeballed;
  zero-margin items are flagged as such (the unlevelled-floor cover at
  exactly 22.00 was the known trap — the levelled design must show its
  margin).
- Comment on Issue #296 with the package summary + figure paths; one
  line to `~/workspace/goals/he-piantor-42-keyboard-pmo/GOAL.md`.
- Checkpoint commits on branch `issue-296-stageb`, pushed. No PR yet
  (the PO approves figures first; the PR follows with the 3D stage).

Working style: plan note first; short response segments; scripts and
evidence in `.issue296-runtime/`; if a sub-item cannot be verified,
record it as unverified with the reason rather than estimating.
