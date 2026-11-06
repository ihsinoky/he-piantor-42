# Issue #165 evidence

Architecture study only. No schematic/PCB writer, router, refill, CAM export,
order or billing operation is used. The report is
[docs/issue-165-dual-wing-power-study.md](../../../../docs/issue-165-dual-wing-power-study.md).

## Reproduce

From the repository root, Python 3 stdlib is enough for the main sweep:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-165-dual-wing-power-study/compare.py
```

The copper study additionally needs NumPy and Shapely 2. This run reuses the
already installed read-only packages under `.issue141-runtime/geometry/`;
there is no package installation. Every temporary/cache location belongs to
`.issue165-runtime/`, not `/tmp` or another Issue's runtime:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 \
  PYTHONPATH="$PWD/.issue141-runtime/geometry/lib/python3.12/site-packages" \
  TMPDIR="$PWD/.issue165-runtime" \
  python3 hardware/kicad/qualification/issue-165-dual-wing-power-study/copper-study.py
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-165-dual-wing-power-study/compare.py
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-165-dual-wing-power-study/verify.py
```

`verify.py` runs both calculations in order, saves process logs and checks the
pre-existing worktree hashes. On a different checkout, use its own NumPy/
Shapely installation and perform the equivalent clean-base/addition-only check;
the original runtime Git metadata is intentionally not committed. All paths
in the scripts resolve relative to the evidence folder, except this session's
explicit runtime/dependency paths used by the verification runner.

## Files and boundaries

| File | Meaning |
| --- | --- |
| instructions.md, issue.json, start.json | Complete instruction/Issue inputs, exact base and pre-existing changes |
| input-hashes.json | Hashes of original read-only reports, decision record, resistance models and inventories |
| inputs/ | Byte-preserving snapshots of unmerged #163 and the working decision record; **source material, not adopted changes** |
| sources.json | Manufacturer PDF URLs, retrieval times, revisions/section checks and SHA256; PDFs stay in runtime |
| compare.py, model.json | Equations, assumptions, bounds, 768-row #157 reproduction and conditional current thresholds |
| sensitivity.csv | 14,976 rows: 13 architecture variants × common input sensitivities; no reduced current applied to envelope rows |
| primary.csv | 52 rows: all architectures at the primary conditions × four Main resistance pairs |
| copper-study.py, copper-study.json | Read original #141 graph without modifying its function; fixed pad/via, conductance multipliers 1/2/4/10 and exact zero-variable-resistance node contraction; both pitches, all 21 points |
| primary-fixed-pad-via.csv | Primary copper corner with the actual x2 conductor result, all three loads, six/one returns and four Main pairs (96 rows) |
| converter-power.csv | 5.2V output, 80/85/90/95% efficiency scenarios, no implied guaranteed efficiency |
| duty-timing.csv | Switch/Hall wait assumptions and arithmetic scan-rate impact, no timing qualification |
| protected-start.json.gz, verification.json, processes/ | Preservation baseline, verification outcome and process evidence |
| draft-pr-body.md, publication.json | Review text and actual commit/push/Draft PR outcome |
| manifest.json | SHA256 of all evidence except the manifest itself, plus the report |

The copied input Markdown retains its original bytes and original relative
links. Those historical links refer to the input's original directory and are
not rewritten or included in the authored-link check. Original sources are
identified by `input-hashes.json`; #163 publication is PR #164, not merged main.

The uniform Wing resistance factor 0.5 in `sensitivity.csv` is an optimistic
target. It is **not** the result of doubling only conductor conductance. The
report's combined rows use `primary-fixed-pad-via.csv`, where the 17mm drop
ratio is 0.5209797964 and pad/via resistance is retained. `None` conductance in
the copper JSON denotes exact contraction of variable resistors, not a
manufacturable infinite-width PCB or a general lower bound for all layouts.

All voltages are sensor-local VCC minus its own GND. Duty voltages apply only
after settling while powered; the off bank is approximately 0V. Alternate 3.3V
rows use a separately declared 3.0V minimum, **not** the current 4.5V guarantee.
Reduced-current rows are named targets, not substitutes for the 127mA primary
case or the unchanged 11mA/278mA sensitivities. Ron remains the #157 bracket.

Costs in the report are engineering budget allowances in USD per complete
42-key system, not supplier quotes. Component count, assembly, POFV, shipping,
tax and redesign/qualification can change total cost. No cart/order/payment
was created. Passing this reproducibility/preservation check does not qualify
a circuit, a PCB, USB power, noise, thermal behavior or key-distance accuracy.
