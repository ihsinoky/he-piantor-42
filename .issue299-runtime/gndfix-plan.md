# GND repair round — plan (worker, 2026-11-21)

## Sequence
1. **Reproduce first.** Write `gndcheck.py`: pad-level GND connectivity
   from saved copper only (zone fills as saved + tracks + via annuli +
   pads; layers joined at plated vias). Run on the four base boards at
   3fcad246f → must reproduce Codex M6 exactly (76/79, 77/79, 74/79,
   75/79 and the same off-return pad sets). This is the negative
   control for every later pass.
2. **Survey each island**: what seals it (which other-net tracks, what
   gaps), F.Cu occupancy over the seal line, distance island→main pour,
   room for a 0.60/0.30 GND via in/near the island.
3. **Repair per variant** (method decided from the survey; candidates:
   B.Cu GND bridge track through a ≥0.30 mm gap; or via-stitch —
   GND via in the island, F.Cu GND track, GND via down into the main
   pour). Only GND-net copper changes. Checkpoint commit per variant.
4. **Verify on the saved files** (fresh reload, no refill): gndcheck
   79/79 ×4; ERC 0; DRC shorting 0 / unconnected 0; gates 1/2/4/6/7/8
   re-run; diff census vs 3fcad246f (non-GND geometry identical);
   clearance caveats not worsened (16R ≥0.0829 class, 17L pairs,
   via-pad minima 0.100/0.1016/0.100/0.1052).
5. **17L secondary pairs** (0.098958 C_HA2.1↔GND track; 0.099503 GND
   track↔HALL_3V3 track): fix only by moving GND copper; else
   disposition with measurements.
6. Deliverables: gndfix-report.md, REPORT.md addendum, Issue #299
   comment, GOAL.md line, branch pushed.

## Islands (from Codex M6)
- 16L: C_HB2.2 + U_HB2.2/.5 — polygons 1 (3.939 mm²) + 2 (4.185 mm²) near (67, 91–94)
- 16R: U_HA2.2/.5 — polygon 2 (0.825 mm²) near (148.9, 90.9)
- 17L: U_HB5.2/.5 (poly 3, 1.258), U_HC5.2/.5 (poly 2, 0.799), C_HB5.2 (poly 1, 2.216)
- 17R: U_HA2.2/.5 (poly 1, 1.534), C_HB3.2 (poly 2, 3.437), C_HC2.2 (poly 3, 2.859)

## Tooling
kicad-cli / pcbnew 9.0.9 from the he-piantor-42 .issue129-runtime
extract; checker in Python (pcbnew geometry + shapely if available).
