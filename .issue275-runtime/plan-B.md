# Issue #275 Stage B plan (from stageA-design.md §5 + task brief)

Base: origin/main 06efd9a18 + Stage A commits. Rev.9 tree:
`hardware/kicad/qualification/issue-270-main-rev9/` (board `main-rev9/main.kicad_pcb`).
Symmetry axis board x=100. Mirror: (x,y,θ) → (200−x, y, −θ).

## Stage B1 — Main Rev.10 board build
- New tree `hardware/kicad/qualification/issue-275-main-rev10/` copied from Rev.9 tree.
- J3 site BIT-IDENTICAL (footprint, fanout, tab chain) — verify by diff.
- J2 footprint → centre (75.745202, 111.823895), rot +43.0°. Re-route ONLY J2's
  own 14-net fanout (Stage A sweep: no foreign copper within 0.30 mm of new pads).
- Outline: left tab chain := exact mirror of the right (J3-pattern) tab chain,
  incl. base step. J2 dive-corner R0.50/stub feature disappears.
- Mounting holes UNCHANGED (already symmetric — do not touch).
- Checks at build: pad-corner clearance ≥ 0.70 (expect 1.4864), copper cuts 0,
  min edge-to-copper ≥ 0.323 class, inside D-037 silhouette, outline closed.
- Commit.

## Stage B2 — Main gates
- unconnected 0, wrong-net 0, ERC 0 (kicad-cli, #263/#270 invocation class).
- DRC comparative vs Rev.9: pre-existing phantom population must not grow.
- via-pad minimum (report actual; Rev.9 = 0.1596 class).
- Resistance extraction both branches: J3 must reproduce 4.754 V (untouched);
  J2 re-route reported, Vfar ≥ 4.60 V both branches.
- Non-J2 diff audit vs Rev.9 (byte/item level outside the J2 fanout + left tab).
- Commit.

## Stage B3 — Wing Rev.6 left notch mirror (16L/17L)
- Right variants untouched (verify hash unchanged at end).
- Left notch chain := exact mirror of the SAVED right chain (Stage 2e
  construction, 7 elements). Seam ≥ 0.55 vs new left tab, both pitches; overlap 0.
- Gates per variant: material DRC 0, unconnected 0, wrong-net 0, via-pad minima
  unchanged (16L 0.1032 / 17L 0.1252). Pour fringe re-fill per #263 procedure.
- Regenerate LEFT packages only (DRAFT / NOT FOR ORDER). Commit.

## Stage B4 — Case: flip pocket + flipped J4 attempt
- Production tree: add 1.0 mm pocket under power-stage field
  (case x −6..+13, y 28..48). Confirm remaining floor thickness.
- Flipped J4: extend pocket toward vertex + model looped 180° Fly-cable
  approach. Decider = flipped fitted audit (B5). If it cannot pass: STOP,
  record flipped-J4 as named residual; keep the power-field pocket.
- Commit.

## Stage B5 — Fitted audits, both poses (#264 bundle method)
- Normal pose: final pair (Rev.10 + Wing Rev.6 final), Type A 5-fold FFC.
  Expect gate 1 = 0, service as recorded.
- Flipped pose: Main flipped (components underside, ZIF mouths at underside
  plane z ≈ 2.95 class), Type D cable variant of the same 5-fold plan
  (even parity not needed — Type D opposite-face contacts), re-derived
  Z-profile at underside mouths. Gate 1 = 0 required.
- Record flipped service consequence (actuators face tray → board lift first).
- Tray reliefs: left relief recomputed (expect mirror of right 6.305 mm³).
- Commit.

## Stage B6 — Package + REPORT
- Main Rev.10 manufacturing package (JLCPCB BOM/CPL per #267 conventions,
  FH12 = C5378715, DRAFT / NOT FOR ORDER).
- REPORT.md in Rev.10 tree: change set, gate table, both audits, flipped-J4
  disposition, draft adoption line D-046. No decisions.md edit. No push.
- Final compact report to PMO.

## Verification invariants
1. Reproduce before fixing (extract/diff from SAVED boards, not design intent).
2. Distrust first passing test — check it exercises the claim (e.g. seam
   measured from saved boards; J3 bit-identity proven by diff, not assumed).
3. Do not stop at the edit — verification complete + evidenced before done.
