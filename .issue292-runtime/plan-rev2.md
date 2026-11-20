# Issue #292 wireless Main RESPIN (rev2) — plan

PO instruction 2026-11-20: extend outline using case margin, trapezoid
direction, balanced; relocate JBATT to north (battery) side. Respin
route chosen over case-only cable fix. If adopted -> D-061 (board
file only superseded; configuration otherwise unchanged).

Branch: issue-292-wmain-rev2 (from origin/issue-292-wmain f5860df9e)
Tree: hardware/kicad/qualification/issue-292-wmain/
Baseline board SHA-256: 260726192947a090... (edge-fixed D-058 board)
Study of record: hidden_files/wmain-jbatt-relocation-2026-11-20.md
  - JBATT now board (124,134.5) south; case = board-(100,-12.398)
  - north boundary = centre tab X98..102 @Y75.73 + two diagonals
    NE (102,75.73)->(117.86,103.20)->J3 tab; NW mirror via J2 tab
  - N-TAB minimum escape: X112..124 / Y74..88, JBATT (118,81)
  - VBAT+ rejoin corridor X112..116, Y88..102 -> existing run
    (106.5,98.9)->(118.6,109.5)->D2 (121.5,124.8); width 0.30
  - JSWD TC2030 field at (113.5,136.2), missing 3x D0.99 NPTH
    alignment holes; TC2050 alt site (111.5,136.2), west shift
    needed to clear RPD2/RPD3 (117.5..118.5, 135.8..136.1)

## Stages
0. [x] worktree + this plan
1. [ ] Baseline gates on UNMODIFIED board: containment PASS,
       ERC 0, DRC baseline counts recorded (delta attribution)
2. [ ] Case margin measurement (geometry17 bodies + case296 2D):
       bay north wall, slope cover underside, plate patches +
       tilted install motion (stack2), Wing/FFC envelopes.
       Margin budget line by line; extension taken; residual
       clearance to bay wall >= 1.0mm class (else STOP+report)
3. [ ] New outline: both north diagonals keep angles, extended
       equally (symmetric about X=100); rest of outline identical
4. [ ] JBATT -> new north edge, mating faces north (tray);
       plug envelope + cable bend vs case in placed pose;
       VBAT+/GND re-route to OR node; VBAT_SENSE tap stays valid;
       downstream of OR untouched; new cable length (case frame)
5. [ ] SWD: add 3 alignment holes to TC2030 field; evaluate
       TC2050 at shifted site — adopt TC2050 only if it fits
       cleanly with verified clearances; else TC2030+holes.
       Signals unchanged, no SWO.
6. [ ] Full re-verification (measured): containment, ERC, DRC
       (item-level dispositions only), J2/J3 census 14/14,
       module fine-field minima, trackpad D40 keep-out, antenna
       keep-out, far-Wing budget, board-vs-case audit of new
       outline region (bay wall / plate incl. tilt / cover /
       Fly) interference volumes = 0 expected
7. [ ] Manufacturing package regen (gerbers; BOM delta stated),
       REPORT update, quote re-run handoff note (prepare only,
       DO NOT run/order)
8. [ ] Checkpoint commits + push; Draft PR (title: respin JBATT
       north + balanced outline extension; refs #292; PR body
       records coupled case item: bay needs matching recess,
       #296 absorbs; new outline case-frame coords as input)

## Invariants
- Module field (ISP1807-LR fanout, D-057 area) untouched; if a
  route MUST cross it -> STOP and report
- Wing link pins unchanged; USB/J4 pose unchanged; power tree
  topology unchanged (battery feed local geometry only)
- Decisions never edited; this is a proposal until PO adopts
