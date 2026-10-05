# EDA-002C4B4A — JLCPCB USB NPTH DFM coupon

**Qualification package prepared; external DFM evidence pending.** Issue
[#49](https://github.com/ihsinoky/he-piantor-42/issues/49). The coupon preserves
the accepted connector geometry. **USB manufacturing disposition remains
unresolved.** No external DFM result or supplier approval exists yet. This
increment neither fixes the footprint nor decides C4C/G0A. Do not order.

## Baseline and source authority

Clean HEAD, local main, freshly fetched origin/main and merge-base all equaled
`e4d6a54252ebf698006d1221e9620fb5f13569ef` before implementation. Issue #49
was read completely; it had no comments. Branch:
`eda-002c4b4a-jlcpcb-dfm-coupon`. [Preflight](c4b4a-evidence/preflight.json)
records 46 protected historical report/evidence hashes and all 35 accepted
C4B source/configuration hashes. All remain unchanged before and after work.
The accepted C4B3 report, analytic measurements, reconciliation, handoff,
validation and margin/thickness disposition govern this narrow fixture.

Exact accepted source:
`hardware/jitx/he_piantor_42_jitx/components/connectors/hro_type_c_31_m_12.py`,
`TYPE_C_31_M_12` -> `TYPEC31M12Landpattern`.
Its SHA-256 is recorded in preflight and pipeline evidence. The coupon imports
and instantiates this actual component directly; it does not redraw or copy its
pads. The component still maps its twelve lands and four shell stakes exactly
as before. No accepted source, substrate, rule, lockfile or historical evidence
was edited.

Generation source checkpoint:
`a8b47937f4746163d572bf74393d98a253004686`. That commit contains the complete
coupon, measurement and generation source used for the retained runs.
The later reconciliation observer's SHA-256 is recorded separately in
[upload manifest](c4b4a-evidence/upload-manifest.json). Final branch/head SHA is
recorded in the Draft PR, avoiding a self-referential commit hash in this report.

## Environment and construction

**JITX 4.4.3; jitxlib-standard 4.4.0; JITX runtime 4.4.2; KiCad CLI 9.0.9
using `kicad/kicad:9.0.9`.** Image ID:
`sha256:e638b79b0321f29395a5b783e94bb9f3c73303e8da15da27b8f5cb4b67a37729`.
`uv sync --locked --group dev` passed without upgrades. Python 3.14.2.

`USBDFMCoupon` composes a 40 x 25 mm rectangular board, the unchanged
`QualificationSubstrate`, and one `TYPE_C_31_M_12` at (0, -5) mm on top,
zero rotation. All twelve rectangular contact lands, all four plated shell
slots and both 0.60 mm NPTH holes remain present. No net wiring, copper pours,
additional pads, holes, tracks, routes or vias. This is an unpowered geometry
coupon, not a functional USB circuit; there are no connected-net ratsnest items.
Two top silkscreen lines say **DFM TEST ONLY / DO NOT ORDER**, away from the
connector. [Architecture](c4b4a-evidence/ARCHITECTURE.md).

The existing stackup is 0.015 mask / 0.035 copper / 1.10 FR-4 / 0.035 copper /
0.015 mask mm: 1.20 mm including masks, 1.17 mm excluding masks. Outer copper
is nominal 1 oz. The 0.25 mm copper-to-hole qualification rule stays unchanged.
No exception or rule relaxation is added.

## Independent measurement and source/output fidelity

[Source measurement](c4b4a-evidence/source-measurements.json) uses public
`TestCase`, `visit`, and actual pad/cutout instances. It computes the Euclidean
distance from the NPTH circle center to the nearest point on each source
rectangle, then subtracts the analytic hole radius. No circle display
polygonization enters these four gap measurements. The values are recomputed,
then compared with accepted C4B3 evidence; difference >= 0.000001 mm fails.

| Relationship | Source gap (mm) | Gerber/Excellon gap (mm) |
| --- | ---: | ---: |
| A1_B12 | 0.2000999900 | 0.2000999900 |
| A12_B1 | 0.2000999900 | 0.2000999900 |
| A4_B9 | 0.2348831648 | 0.2348831648 |
| A9_B4 | 0.2348831648 | 0.2348831648 |

[Reconciliation](c4b4a-evidence/reconciliation.json) independently reads the
actual copper Gerber aperture macros/flashes and Excellon tools/hits. The
observer is bounded to this fixture's positive, absolute metric 4.6-coordinate
copper flashes, KiCad outline macros and oval apertures; unexpected drawing
commands fail. Actual rectangle bounds and analytic Gerber/drill gaps match
source to < 0.000001 mm; maximum observed gap delta is 1.35e-14 mm.
The existing 0.001 mm observer tolerance is also enforced for every source
copper pad in CAD/top Gerber and all four shell pads in bottom Gerber. Maximum
Gerber Hausdorff distance is 0.000542045 mm at shell curves due to the source
observer's curve tessellation; relevant rectangle bounds are effectively exact.
This tolerance is not a manufacturing margin or approval.

Both NPTH centers and diameters, and all four PTH slot diameters/endpoints,
reconcile independently with source within 0.000001 mm. The actual outline is a
closed 40 x 25 mm rectangle. There is one footprint and no tracks/vias/zones.
Top silk plotted geometry is separated above board y=2 mm. The two fresh runs'
PCB semantics match; all eleven fabrication files match byte-for-byte after
removing only the frozen comparator's timestamp lines. All raw differences and
both raw hashes are retained in [two-run differences](c4b4a-evidence/two-run-fabrication-differences.json).
No fabrication file is normalized or modified for packaging.

KiCad DRC executes in each run with code 5: four expected `hole_clearance`
errors involving contacts0/1/10/11 and one `lib_footprint_issues` warning.
No other finding or unconnected item exists. Raw DRC is retained in evidence;
this is not a full DRC pass or a JLCPCB result. The small pair's production
margin remains the accepted C4B3 blocker.

## Supported generation and reproducibility

From `hardware/jitx`, using the existing environment:

```bash
UV_CACHE_DIR=/tmp/eda-c4b4a-uv-cache uv sync --locked --group dev
source .venv/bin/activate
python -m physical.reproduce_c4b4a
python -m physical.qualify_c4b4a
python -m unittest discover -v
ruff check he_piantor_42_jitx physical parity tests
ruff format --check he_piantor_42_jitx physical parity tests
python -m compileall -q he_piantor_42_jitx physical parity tests
```

At repository root: `node --check task/data/project-status.js` and
`git diff --check`. The generation driver measures source before packaging,
restarts the existing runtime and removes only this coupon's ignored generated
state before each of two sequential fresh builds. Supported commands are:
`jitx design build ... --no-dependency-check`, `jitx design export legacy-kicad ...`,
then pinned Docker `kicad-cli pcb drc`, `pcb export gerbers`, and
`pcb export drill --format excellon --excellon-units mm --excellon-separate-th`.
The KiCad input mount is read-only, and before/after input hashes match.
[Pipeline](c4b4a-evidence/pipeline.json) records exact argv, versions, source
hashes, return codes and the full raw output inventory/hashes for each run.
No private runtime API, exporter patch or fabrication geometry post-processing.

Reproduction produces equivalent geometry; generated timestamps mean new raw
bytes/ZIP hashes can differ. For this handoff use the retained ZIP and its
recorded hash. Packaging uses fixed ZIP entry metadata and exact original
member bytes. Repeating packaging against these retained inputs reproduces the
same ZIP SHA-256.

## Human-upload artifact

Exact local path:

```text
/workspaces/he-piantor-42/hardware/jitx/designs/c4b4a/USB-NPTH-DFM-TEST-ONLY-DO-NOT-ORDER-HUMAN-UPLOAD.zip
```

ZIP SHA-256:
`11660b19f2b465bc5ec5d1b0566b1e486077677cbba032f2c1c9a326b09cd16a`

36,365 bytes; selected run 1. Nine Gerbers: F/B copper, mask, paste,
silkscreen and Edge.Cuts; separate PTH and NPTH Excellon. Empty bottom paste
and silk are normal layer outputs. An exact whitelist and archive member-byte
checks exclude all CAD/project files, `.gbrjob`, drill reports, BOM/PnP, logs
and other generated files. Member names, byte sizes and SHA-256 hashes are in
the committed [upload manifest](c4b4a-evidence/upload-manifest.json).
The generated ZIP is ignored under `designs/` per project policy and is not
committed. It is **qualification-only, HUMAN DFM UPLOAD ONLY, DO NOT ORDER**.

The raw KiCad PCB and Gerber Job still report the known incorrect 1.6 mm
thickness while exported material layers sum to 1.2 mm. Neither enters the
upload ZIP. This is the accepted C4B3 job-free handoff limitation, not a repair
of CAD/job metadata. The PO must select/confirm 1.2 mm if prompted.

## PO handoff and acceptance

Follow the concise [human handoff README](c4b4a-evidence/README.md): upload only
the named ZIP, interpret standard rigid two-layer FR-4 / 1 oz copper / 1.2 mm,
run PCB DFM Check in metric units, inspect every NPTH-to-copper/track or
hole-clearance finding, capture overall and detailed views, measured values
and alert levels. Do not order. The README includes the copy-paste support
question describing the actual 0.2000999900 / 0.2348831648 mm geometry and asking
about normal production without special process or manual CAM modification.
No support approval is claimed. The agent did not log in, upload, contact
JLCPCB, order, interpret an external result or decide production disposition.

[Validation](c4b4a-evidence/validation.json) records all 20 existing C0/C1/C2
regressions PASS, lint/format/syntax PASS, protected evidence/source checks,
byte-preserving ZIP checks and observer fault guards. Static type checking is
unavailable in the existing environment. [Review](c4b4a-evidence/code-review.md)
records the bounded observer limitations and task/phase acceptance.
Applicable CI is engineering-ci; no layout/product-KiCad/firmware or tscircuit
trigger paths changed. Actual Draft PR CI status is reported on GitHub.

PMO reviews geometry fidelity, upload inventory, measurements and PO handoff.
PO decides MERGE/HOLD. No Main/Wing or G0B work, autorouter, completed routing,
production exception or C4C/G0A decision. High-level project status remains
unchanged: USB manufacturing margin unresolved pending external evidence.
