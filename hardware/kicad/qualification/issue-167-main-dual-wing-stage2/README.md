# Issue #167 evidence

[Report](../../../../docs/issue-167-main-dual-wing-stage2.md).

Status: stopped on the required converter input voltage budget. Mechanical
hardware checks are downstream, not a gate. No revised PCB, router output,
manufacturing data, POFV classification or updated quote is supplied.

Reproduce the bounded calculations from the repository root (Python 3 stdlib):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-167-main-dual-wing-stage2/power-preflight.py
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-167-main-dual-wing-stage2/verify.py
```

The full preservation check in verify.py additionally requires this session's
historical untracked inputs listed in protected-start.json.gz. A clean checkout
can reproduce power-preflight.py, but cannot reconstruct those unrelated files
from this PR; their absence is not a passing preservation audit.

The native input check uses KiCad 9's pcbnew module. This session uses the
existing read-only `.issue129-runtime/kicad/` installation, with libraries
and XDG/temp paths redirected to `.issue167-runtime/`. See the recorded
process arguments and environment in processes/native-readback/record.json.
It never saves the board. A different checkout can use its installed pcbnew.

| Artifact | Meaning |
| --- | --- |
| instructions.md, issue.json, start.json | Full task inputs, main SHA, four-hour deadline and Git location |
| import-proof.json | All 70 main-to-PR164 paths; original byte equality before D-026 |
| input-hashes.json, native-readback.json | Starting inputs and KiCad read-only board identity |
| inputs/ | Historical #165 report and 12-row converter table; original Markdown links retained |
| power-preflight.py, power-preflight.json | Constant-power supply equations and decisive input-voltage obstruction |
| current-budget.csv | Design/stress loads, nominal/high rail, efficiency sensitivities, USB current headroom |
| upstream-sensitivity.csv | 4,320 conditional operating points; all R/efficiency/Main-current values are sensitivities |
| conditional-downstream.csv | 48 Wing points at ideal/target Main R; never actual revised-board extraction |
| sources.json | USB-IF/TI primary source links, hashes, versions and sections |
| status.json | Explicit unimplemented work, zero route attempts and null independent metrics |
| verification.json | Import, preservation, arithmetic and authored-link checks; not board qualification |
| protected-start.json.gz | Pre-existing non-runtime file hashes |
| draft-pr-body.md, publication.json | Review text and actual publication outcome |

The source obstruction does not mean a TPS63070 cannot operate below 4.75 V.
It means the particular converter input guarantee required by this Issue has
not been met. Lowering that requirement or silently restricting the USB source
would change the conditions. No such change is made.
