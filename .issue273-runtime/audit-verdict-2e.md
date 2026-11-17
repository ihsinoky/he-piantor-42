# Issue #273 Stage 2e — audit verdict (finisher, 2026-11-18)

## (a) Fitted audit (gate 1) — PASS, record reproduced exactly

`run-audit-2e.py` re-runs the #264 bundle (`run_final.py`) verbatim.
The `final_eval.json` it produced is **identical in every key and
value** to the preserved record
(`hardware/case/issue-263-lowdeck-production/audit-rerun/final_eval.json`),
verified by direct JSON comparison (key sets equal, zero differing
values). Therefore, exactly as recorded for #264:

- Gate 1 at the nominal fitted pose: **0 unexpected contacts**
  (the bundle's base configuration was proven by the v4 compound
  run; the sensN/sensS non-tray grazes — wing 0.2857 mm3,
  Main-study-C23 0.0191 mm3 — are the recorded mis-set-detent
  sensitivity results, unchanged).
- Service classification unchanged: drape poses relieved by the
  formed channel as recorded; tip-A5.0 fully relieved; the
  drape-static / B+2.5 / B+5.0 "real" lists are the recorded ones.

The bundle's body set is the Phase B audit set (fitlib18/fitlibF);
the Wing outline is not an input to it, so exact reproduction is
the expected and correct outcome — no regression, no change.

## (b) case-delta-2e "tray-left [FINDING]" lines — CLASSIFICATION ARTIFACT, no case change

The full-run log (`case-delta-2e-orig.log`, re-run reproduced as
`case-delta-2e.log`) prints, for the RIGHT variants only,
`tray-left` hits of 14.569 / 0.206 / 0.043 / 0.037 mm3. These are
**not real intersections**. Evidence:

1. **AABB impossibility.** The 14.569 mm3 chunk is the added
   region's main part at case X 20.92..27.77, Y 32.43..39.84
   (measured, probe2.py). The audit `tray-left` solid's bbox is
   X -145.52..+3.5 (probe-tray.py). The X ranges are disjoint by
   >17 mm, so a true common volume is geometrically impossible.
2. **Exact duplication.** The phantom tray-left volumes equal the
   same run's `wing_right` volumes to 0.001 mm3 (14.569, 0.206),
   and the small extras (0.043 / 0.037) match the thin bay sliver
   part's own prism volume (0.036 mm2 x 1.2 = 0.043). The
   tray-left entry returned the wing/solid's own results.
3. **Fresh-process re-runs.** Re-running the identical script
   restricted to ONE variant per process (all bodies scanned,
   case-delta-repro.py) for all four variants gives **own-wing
   hits only** — no tray, Main, cable or any other body, at
   either pitch. The phantom appears only for a right variant
   processed AFTER a left variant in the same process: the
   script reuses fitlibF's per-pitch cached raw solids across
   variants (`bodies_at` cache), and the shared OCC shapes are
   corrupted by the earlier variant's boolean pass.
4. The left variants (processed first in each pitch) show no
   tray hits even in the corrupted full run — consistent with
   the state-corruption mechanism, not with geometry.

Genuine delta, as measured in clean runs: the 2e added Wing
material (20.05-20.11 mm2 L / 12.30-12.38 mm2 R vs 2d and Rev.5)
intersects **only the audit Wing solid itself** (the Phase B
wing's fuller inner-corner geography — the region the straight
dive line fills back in). By the project's established case-delta
method (Stage 2b/2d: growth x own body = expected; growth x tray
= pocket relief), there is **no tray intersection and therefore
no production case-tree change** for Stage 2e. The Wing pocket
relief totals stand as adopted in 2b/2d.

Also noted: `case-delta-2e.py` crashes at its final line
(`Path` never imported; the JSON summary was never written and
the shell wrapper recorded exit=1). The printed hit lists are
unaffected by that bug, but the import is fixed in the worktree
copy so future runs complete.

## Conclusion

Gate 1 = 0 (record reproduced byte-for-byte in values); the
tray-left finding is a measurement artifact of the multi-variant
process, dispositioned with the evidence above; no case-tree
update; no unresolved contact. Stage 2e case work is CLOSED.
