# Issue 167 resume evidence — NOT QUALIFIED

The current report is [docs/issue-167-main-dual-wing-stage2.md](../../../../../docs/issue-167-main-dual-wing-stage2.md).
No board here is a fabrication release. Final bounded attempt metrics: **3 / 0 / 2 / 24**, all 44 nets checked.

- `start.json`, `instructions-167*.md`: authorized redefinition, timebox and previous head.
- `previous-run-report.md`, `prior-*.json`: byte copies of historical records. Historical Markdown links retain their original context.
- `circuit-source.py`, `logical-contract.json`, `schematic/`: explicit circuit and native schematic/export, independent of PCB routing output.
- `prepare.py`, `circuit-intent.json`, `Stage167.pretty/`: candidate authoring and footprint snapshots. Passive MPNs/production lands remain unqualified. Frozen-input overwrite is prohibited.
- `routing-scope.json`, `preflight-*.json`, `global-seed-ripup.json`: preparation limit, raw DRC, exact two remaining seed segments handed to the one global route.
- `inputs/global`, `runs/global`, `inspection/global`: first attempt, measured 3 / 0 / 0 / 1.
- `local-scope.json`, `inputs/local`, `runs/local`, `inspection/local`: last permitted repair, measured 3 / 0 / 2 / 24. Input project rules govern independent inspection.
- `inspection/*/{drc,connectivity,transfer-diff,assessment}.json`: raw all-net qualification evidence. Assessment accepted metrics remain null on opens; `status.json` separately exposes observed counts.
- `circuit-check-*.json`: 245 logical pins agree among explicit source, native schematic export and candidate PCB; 53 existing component placements preserved. This does not establish physical continuity.
- `power-extraction-local.json`, `power-budget.json`, `connector-current-sensitivity.csv`: actual positive copper diagnostics, connector range and conditional budgets; current/ripple/GND guarantees are unclosed.
- `mechanical-readback.json`, `pofv-reclassification.json`, `pofv-sites.csv`: diagnostic inventory on the unqualified candidate, 108 vias / 26 POFV candidates.
- `pcba-update-status.json`: new quote/CAM/BOM/CPL withheld behind failed gates; 13 additions / 58 planned assembled parts; no purchase or charge.
- `runtime-check.json`, `verification.json`, `processes/`: pinned unchanged tools and audited executions. `publication.json` records commit/push/PR metadata.

Dependencies are the existing read-only KiCad environment under `.issue129-runtime` and pinned KRT under `.issue155-runtime`. All writable runtime paths are `.issue167-runtime`. The runner is `common.py`; e.g. from repository root:

```sh
python3 hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/common.py verify-resume /usr/bin/python3 hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/verify.py
```

Do not rerun routing: the one-global/one-local allowance is exhausted. A new run needs a newly authorized bounded scope. Inspection scripts intentionally preserve completed evidence and refuse overwrites where applicable. The generated native schematic uses per-pin box symbols for review; it is not an ERC or production-library qualification claim.
