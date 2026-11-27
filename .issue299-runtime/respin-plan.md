# Issue #299 — GND respin round plan (worker, 2026-11-21)

Continues branch `issue-299-wwing-gndfix` (tips 2f3371690 boards /
834ddbf4e report). Executes PO decisions 2026-11-21: sensor pockets =
local pocket respin on the 16L pattern (option d); cap islands =
stitch vias + HALL_3V3 carve (option b); Wing south-inner-corner trim
approved via Issue #296.

## Targets

| Variant | Sensor pocket(s) | Cap island | Trim |
|---|---|---|---|
| 16R | U_HA2.2/.5 | — | verify corner empty, then trim |
| 17R | U_HA2.2/.5 | C_HC2.2 (pre-staged in scratch) | verify, trim |
| 17L | U_HB5.2/.5, U_HC5.2/.5 | C_HB5.2 | verify, trim |
| 16L | — (79/79 already) | — | verify, trim |

## Sequence

1. **Reproduce first.** gndcheck.py on base boards (scratch/*-base =
   3fcad246f) → must reproduce Codex M6 / gndfix §1 exactly
   (76/77/74/75 per 79 and same off-pad sets). Then on current branch
   files → 79/79 (16L), 77/79 (16R), 74/79 (17L), 76/79 (17R).
2. **Pocket anatomy.** For each target pocket: dump island polygon,
   ring tracks/pads, F.Cu occupancy, the 16L HB2 reference geometry
   (its pocket via + fill cutout), and where F.Cu return copper /
   B.Cu main pour can be reached. Design per pocket:
   GND via inside the pocket (lands on island fragment), F.Cu GND
   egress (track, possibly via-B down to B.Cu main pour), then
   HALL_3V3 zone refill so the fill carves rings around the new GND
   copper — return path exists by construction, as in 16L.
   Cap islands: same shape, smaller (17R C_HC2 pre-staged:
   via A (117.473,81.950), via B (116.473,83.000), 0.30 F.Cu track,
   fill −1.662 mm² — verify against current file, then execute;
   17L C_HB5 analogous, own design).
3. **Apply in scratch copies first**; verify each with gndcheck +
   a HALL_3V3 pad-connectivity check (carve must not strand any
   VCC pad) + pairscan; only then write the tree files.
   Checkpoint commit per variant.
4. **Trim.** Per variant: establish board↔asm correspondence of the
   south inner corner (17R: fitted transform R/t in case296b
   zcheck_transform.json, residual 0.0007; 17L: fit from mirrored
   outline; 16mm: corresponding corner by outline topology + J_WING
   anchor). Verify the corner zone (asm X 14..24, Y −8..−2
   equivalent) is empty of pads/tracks/vias in that variant; if not
   empty → do NOT trim, flag with evidence. Cut = clean chamfer
   removing the rim-roll clip region (asm X 15.86..22.25,
   Y −6.68..−3.09) inside the verified-empty zone.
5. **Full verification on saved files** (fresh reload, no refill
   before measuring): gndcheck 79/79 ×4 (negative control still
   reproduces base islands); gates 1/2/4/6/7 re-run; Gate 8 =
   outline diff itemised = trims only; Gate 5 re-run on every
   variant whose HALL_3V3 fill was carved (all three respin
   variants); pairscan caveats not worsened (16R 0.0829 class,
   17L 0.0904–0.0994 + its two extra pairs — nudge only if the
   respin makes it natural); ERC 0; DRC shorting 0, unconnected 0;
   diff census vs branch base: non-GND/non-trim geometry identical.
6. Deliverables: respin-report.md, REPORT.md addendum, Issue #299
   comment, GOAL.md line, branch pushed.

## Invariants

Sensors never move; TMAG land unchanged; only GND-net copper,
HALL_3V3 fill (carve rings around new GND copper), and the outline
trims change. Via size = board standard Ø0.60/0.30. Clearance floor
0.100 everywhere; no hair necks (< 0.10 features) as connections.

## Tooling

pcbnew/kicad-cli 9.0.9 from he-piantor-42 .issue129-runtime extract;
gndcheck.py / census.py / pairscan.py / rail-budget.py in this
runtime dir; gate scripts s2_gates.py / s2_gate5.py / s2_gate7.py in
he-piantor-wwing/.issue299-runtime.

## Progress log

- Refill rule discovered: zone refills only reproduce inside the full
  project directory (.kicad_pro present). All respin work happens in
  full copies under scratch/respin/<V>/; refill.py (HALL_3V3 only)
  reproduces both fill areas exactly on an unchanged board.
- netcheck.py = gndcheck generalised (any net/root). HALL_3V3 baseline:
  50/50 pads on-return on all four variants (carve invariant).
- 17R C_HC2 pre-stage applied + HALL refill: fill -1.6626 mm2 (rings
  only, matches pre-stage), GND 77/79, HALL 50/50. DONE.
- 17R HA2: respin_stitch.py (nearest-14 via-B goals) FAILED - all 14
  nearest via-B sites are F.Cu-unreachable. Diagnosis (respin_diag.py):
  via-A ok 179, via-B ok 20872 - candidates abound. A* with the FULL
  via-B union as goal finds a 0.30 mm path, length 1.25, ending near
  (150.28, 89.97). respin_stitch2.py implements the union-goal search.
- Trim: notch = Z-check clip bbox + 0.25 mm margin, in asm coords.
  Zone fills (HALL_3V3 F.Cu, GND B.Cu) DO blanket the corner
  (12.17 mm2 each on 17R) - "empty" in the Z-check means no
  pads/tracks/vias. Trim therefore = outline cut + full zone refill
  (fills recede by their 0.15 clearance); locality verified by census.
  Transforms for all variants fitted and validated: 17L exact mirror
  (Hausdorff 0.0000), 16L exact mirror of 16R (0.0000), 16R anchored
  on J_WING at 17R's asm J_WING position (west tip X=1.00 matches).
- 17R DONE (commit a8c7ec796): C_HC2 stitch (pre-stage), HA2 stitch
  via A(151.451,90.720) B(150.001,89.870) w=0.30; trim removed
  14.515 mm2; GND 79/79, HALL 50/50, containment 0.0000.
- Refill lesson 2: multi-zone Fill in one process silently skips the
  GND zone (with list AND with a per-zone loop). Proven route: one
  zone per process (refill_one.py). HALL delta at trim -15.4249 and
  GND delta -15.4249 match exactly (both blanket the corner).
- 17L: C_HB5 stitch A(116.212,98.560) B(117.362,98.510); U_HB5 stitch
  A(116.203,95.899) B(116.853,95.199); both w=0.30.
- 17L U_HC5: NO via-A exists at 0.60 (tally ok=0; EN-pad corner to
  RAW centreline 0.617 mm total vs 0.40+0.45 needed; smaller vias
  fail too - bisector bound ~0.28). Pocket respin: F.Cu H_C5_RAW
  jogged north (reroute_raw.py): (133.250,99.175)->(133.300,100.200)
  ->(131.900,100.200)->(131.900,97.400)->(132.000,96.300). Via-A
  candidates 0 -> 41. HC5 stitch running on the jogged board.
- 16L DONE (commit db88c6bf1): trim only (removed 14.515 mm2),
  GND 79/79, HALL 50/50, containment 0.0000.
