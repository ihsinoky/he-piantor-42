# Issue173 evidence — terminal preflight failure, no routing

Read [the report](../../../../docs/issue-173-main-dual-wing-final.md) first. The 1210 candidate is NOT qualified. DRC found C26.2 touching J3.15 after C26 was moved away from SW2. The mandatory guard stopped before native routing. Global runs 0 / limit 1; local runs 0. No further attempt is authorized by this result.

- `inputs/final/`, `Stage173.pretty`: rejected un-routed 1210 candidate. The inherited directory label `final` does not mean accepted.
- `preparation.json`, `placement-check.json`: only C26 and its two paste apertures moved; other 65 placements and all seed tracks/vias retained. SW2 cleared, J3 overlap confirmed.
- `preflight.json`, `preflight-receipt.json`: native DRC and hash-bound FAIL receipt. Expected pre-route opens are not treated as final qualification.
- `processes/preflight-drc/`, `processes/guard-rejection/`: native DRC exit0 with actual blocking violations; guard exit1 before router setup. Raw logs are unedited.
- `route.py`: repaired #169 guard predicate, exact input binding and atomic single-attempt reservation. **Do not rerun.** Failure is terminal under the user instruction; unused routing allowance is not approval to resume.
- `routing-scope.json`, `runtime-check.json`: unchanged D-019 intended conditions and 2055 matching KRT source files. No resolver run is claimed.
- `fallback-seed-a/`: unchanged #169 qualified 0805 board, its matching BOM/CPL, review CAM, source schematic, old qualification/POFV/resistance evidence. No new manufacturing data, extraction, classification or account quotation.
- `fallback-provenance.json`: file-by-file sources and hashes. `verify.py` also checks each source against base commit `c741ade9`.
- `verification.json`, `status.json`, `manifest.json`, `publication.json`: integrity checks, terminal state, hashes and commit/push/Draft PR attempt.

Known limitation: seed-a's 0805 output capacitors lose more than half their nominal capacitance near 5.35V on the typical curve, with tolerance, temperature and ageing reducing margin further. Effective output capacitance and transient behavior are not guaranteed. Do not combine seed-a CAM with the selected 1210 BOM. PO must decide disposition; manufacturing release, order, billing and merge are not performed.

Runtime and alternate Git metadata are `.issue173-runtime/` in the same working directory. Existing dependencies are read from the prior runtimes. For read-only verification, use a fresh process name:

```sh
python3 .issue173-runtime/run.py NEW-NAME /usr/bin/python3 hardware/kicad/qualification/issue-173-main-dual-wing-final/verify.py
git --git-dir=.issue173-runtime/git --work-tree=. log -3 --oneline
```
