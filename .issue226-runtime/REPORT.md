# Issue #226 — Main Rev.6 implementation report

Status: all nine data pass conditions PASS. D-036 is proposed; PO gate pending.
Branch: `issue-226-main-rev6`, based on `cd96d799` (origin/main at dispatch).
Git state: `.issue226-runtime/git`, work tree: this checkout. No push, PR, merge,
external submission, order or manufacturing release performed.

## Chamfer decisions

All three vertices are pointed; all three are cut. Equal nominal legs **4 mm ×
4 mm**, measured along the two original sides, make a **4 mm new face** and remove
**3.464102 mm normal tip depth**. Each former 60° vertex becomes two 120° corners;
all six actual final interior angles are independently checked within 0.0001°.
This is a substantive 4 mm edge, not a nick. 4 mm retains all Ø5 mm mounting-support
disks. 6 mm legs would leave about 0.65 mm to the hole boundary and intersect these
support disks. 5 mm legs would leave only about 0.12 mm face-to-support margin;
4 mm avoids that near-tangent support condition. No cut was silently reduced.
The 1 nm KiCad coordinate grid produces <=2 nm rounding of nominal leg lengths.

| Vertex (KiCad XY mm) | Original interior angle | Actual legs mm | New face mm | Nearest hole boundary mm |
| --- | --- | --- | --- | --- |
| V1 (62.107317, 137.9) | 59.999999550° | 4.000000000 / 4.000001699 | 4.000000699 | 2.382050160 |
| V2 (100.0, 72.267949) | 60.000000246° | 4.000000333 / 4.000000333 | 4.000000000 | 2.435898000 |
| V3 (137.892682, 137.9) | 60.000000204° | 4.000001699 / 4.000000000 | 4.000000699 | 2.382050160 |

## Pass conditions and evidence

Paths below are relative to `hardware/kicad/qualification/issue-226-main-rev6/`.

1. **DRC 0 / unrouted 0 / ERC 0.** Fresh KiCad 9.0.9 native calls with all severities
   and `--exit-code-violations`: `inspection/final/drc.json`,
   `schematic/erc-final.json`, `processes/native-{drc,erc}/record.json` (exit 0).
   Schematic and net XML are byte-identical to Rev.5. No exclusions or rule changes.
2. **Independent connectivity clean.** `inspection/final/connectivity.json` and
   `graph-method.json`: same Rev.5 actual-copper four-layer union-find predicates,
   no net-name unions; 40 nets, no disconnected required pads, no wrong-net contact.
   `processes/physical-connectivity/` records the fresh call. Every netted pad is
   cross-checked against the graph and unchanged schematic XML by `verify.py`.
3. **Via-pad audit rerun.** `inspection/final/audit/via-pad/`: all 130 vias × 232
   copper pads = 30,160 unique pairs, no overlaps/violations; minimum **0.145 mm**.
   `all-pairs.json.gz` is the complete matrix, with nearest-pad CSV/JSON and summary.
   Holes are additionally included in the independent new-edge clearance check.
4. **Diff versus Rev.5.** `rev5-diff-and-clearance.json`: all 62 complete footprint
   structures are identical (including positions/angles, J2/J3/J4 and mounting holes).
   All 1,143 track segments, 130 vias, net definitions, rules and other design nodes
   are identical. Exactly three old outline segments become six. The only copper
   edit is the In1.Cu GND plane boundary/fill at the three corners (22.605497 mm²
   removed). No route, pad, via or power conductor was moved. See precision note below.
5. **Measured new-edge clearance.** Every one of 1,509 native-derived copper/hole
   objects was compared with each of the three new faces, using actual pad polygons,
   track/via extents, hole radii and filled zones on every copper layer. Minimum
   **0.549999609 mm**, from the GND plane at V1. V2: 0.550000000 mm;
   V3: 0.549999656 mm. Nearest hole boundary: **2.382050160 mm**. Distances refer
   to the Edge.Cuts centerline, the physical board-edge datum. The unchanged legacy
   sides retain their Rev.5 clearances; the >=0.5 mm requirement is applied to every
   newly cut face. See `new_edge_clearance` in the geometry/diff report.
6. **Power reverified because plane copper changed.** Fresh positive-path extraction
   (16 cases) and GND sheet FEM (four cases: two mesh densities × two width factors)
   using the Rev.5 models, actual fill, thermal spokes and barrels. Analytic rectangle,
   reciprocity, superposition and KCL checks pass in `ground-model-verification.json`.
   Input loop: **48.682869992 mΩ** versus Rev.5
   48.686447631 mΩ. Farthest point: **4.797985723 V**
   at 127 mA/Wing, above 4.60 V. The apparent 3.578 µΩ decrease is remeshing
   sensitivity, not an improvement claim. `power-impact.json`, `resistance-summary.json`,
   `power-budget.json`, `power-sensitivity.csv` and both `*-extraction-final.json`
   record assumptions and results. Retains 125°C, track width×0.8, assumed 35 µm
   copper / 20 µm barrel, 200 mm AWG28-equivalent GH conductors and six returns.
   Rev.5 reference results are inherited, hash-linked, with identical extraction
   scripts; Rev.6 was freshly run. This remains a model, not a material or prototype guarantee.
7. **New manufacturing directory regenerated.** `manufacturing/` contains the
   11-member fabrication ZIP (four copper, masks, silks, six-edge outline, PTH/NPTH),
   paste, drill report, BOM, CPL, Gerber-frame CPL and native absolute positions.
   `export-provenance.json` hashes the final source board; native export did not
   mutate it. `cam-check.json` independently reads back all copper, GND polygons,
   outline, holes, masks, paste and assembly data. GND polygon symmetric difference
   versus native source <1e-8 mm². BOM/CPL are byte-identical to Rev.5, regenerated
   from the final native board, not copied.
   `gerber-frame-cpl.py` rederives **ΔX=62.107318 mm, ΔY=-137.900000 mm**
   from final board coordinates and all CPL rows. It verifies all six actual Gerber
   edges against PCB edges, all 55 rows against secondary native absolute position
   export, and all 1,485 pairwise placement vectors. Maximum axis error **0 mm**.
   The offset matches Rev.5 because its CPL datum was retained; it was not assumed.
   Evidence: `cpl-frame-check.json`, `processes/release-*`, `processes/cam-readback`.
8. **PO outline comparison figure.** `outline-comparison.png` (PNG, visually reviewed):
   full-board Rev.5 versus Rev.6 overlay and all three enlarged corners, with hole
   and support-disk circles. Reproducible with `plot-outline.py`.
9. **Decision/findings drafts.** D-036 appended to `docs/decisions.md`, explicitly
   **proposed**. F-014 appended to `docs/findings.md`, explicitly **draft**, recording
   the corner-plane finding, model limits and failed implementation trials.

## Case fit and protected scope

Rev.6 is an **exact subset of Rev.5**, with outside area **0 mm²**, verified from
actual final PCB edge coordinates. Material removal only. All mounting locations
and full Ø5 mm support disks are unchanged/preserved; minimum support-disk margin
to the full perimeter is 0.946152 mm. Mounting and case interference are unaffected:
no added material or component pose changes can introduce new interference into
the existing case envelope. Case data, Matrix and Wing boards were not touched.
This is geometric compatibility evidence; no new physical assembly test was run.

## Precision and implementation trials

No substantive-cut constraint forced a stop or compromise. The only necessary
extra design change is the explicitly permitted local corner GND setback.
A nominal 0.55 mm setback leaves ~50 µm margin above the 0.5 mm requirement.

Cutting oblique polygons creates endpoints on KiCad's 1 nm integer grid. Their
rounding causes **0.000002698 mm²** of raw remote difference slivers and
**0.000003246 mm²** total added numerical sliver area. The independent comparison
requires all remote differences to fall within **2 nm of the original boundary**;
area outside that envelope is **0 mm²**. This is the Rev.5 graph/audit numeric
scale, 500× finer than Gerber coordinate resolution (1 µm). It is disclosed rather
than called bitwise-identical copper. All routing/pad/via/footprint objects are
structurally identical, and actual new-edge distances must still pass >=0.5 mm
without deducting any numeric tolerance.

Rejected implementation trials are retained in `.issue226-runtime/debug-runs/`:
temporary PCB without a matching project selected defaults; global refill caused
remote grid changes; polygon re-fracture lost/shifted hole bridges. Native DRC and
independent geometric comparison rejected these. The final build clips the
inherited fractured fill directly, preserving holes and remote vertices; final
process records and manufacturing artifacts refer only to the final board hash.
No rejected trial was accepted by suppressing a DRC rule or shrinking a chamfer.

## Reproducibility and handoff

See the qualification README for generation order. `manifest.json` hashes all
final artifacts and inherited input dependencies; `python3 .../verify.py` checks
hashes, cross-file evidence and authorized Git path scope. Final verification is
saved as `verification.json`. Git index/objects/refs are confined to the isolated
Git directory. `.issue226-runtime/REPORT.md` is intentionally committed; runtime
Git data, scratch and Codex run logs are not staged.

PO adoption, physical handling/assembly and the existing D-035 manufacturing /
first-power gates remain pending. No push or PR was requested or performed.
