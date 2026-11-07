# Wing Rev.3 — Issue #200 Stage 2

Read `docs/issue-200-wing-rev3-stage2.md` for the layout rationale, electrical
results, harness/Main height assessment and remaining physical fit inputs.
The four `wing-rev3-{16,17}mm-{left,right}/main.kicad_pcb` files and matching
projects are the final candidates. `qualification.json` binds acceptance to
each saved PCB's SHA-256. `input.kicad_pcb` is the placement/outline contract;
`routed.kicad_pcb` and repair logs are intermediate evidence.

Stage 1b geometry and each independently generated Rev.2 board are inputs.
`build.py` retains keys, bottom Hall/local capacitors, locator holes and pin
identities while moving north service parts and the candidate mounting hole.
Right boards use real physical part rotations, never mirrored pads/copper.
`update-definitions.py` removes inherited Rev.2 harness/access metadata.

D-021 applies: two layers, 1.2mm board, signal >=0.10mm, power/GND >=0.30mm,
clearance >=0.10mm, ordinary via 0.60/0.30mm. Front HALL_5V and back GND pours
provide the south 2mm power/GND strip. No signal tracks or vias enter it.
`finish.py`, `apply-band.py`, `normalize-power.py`, the escape/repair scripts,
`cleanup.py` and `via-margin.py` preserve the fixed placement and rule floors.
`rebuild-service-escapes.py` gives 17mm-right's rotated MUXs staggered fanouts;
`plane-repair.py` includes a 2mm halo around that cut window so clipped copper
endpoints have usable A* source cells. A 0.025mm grid resolves the rotated
channels. When hard-obstacle routing cannot escape a copper fence, the A*
fallback assigns high traversal cost to removable track interiors while pads,
vias and pad fanouts remain fixed. Only the chosen corridor is cut back;
all affected nets must reconnect and pass full requalification. Each such
displacement is recorded in `plane-repairs.json`. Dangling signal slivers
are removed only when their required-pad physical component count stays
unchanged, avoiding asymptotic midpoint trimming. Flagged tangent contacts
are snapped to neighboring same-net track centerlines with native clearance
checks. Fresh DRC and the independent graph gate follow every repair.
Compile `grid-search.cpp` into the scratch directory's `grid-search`
executable. In the provided environment, that name is a wrapper for the
compiled `grid-search-native` executable.

Verification requires KiCad/pcbnew 9.0.9, Shapely 2 and NumPy; resistance
extraction additionally requires SciPy and Triangle. The local
`.issue200-runtime/run python3` wrapper points at the extracted workspace
packages and directs temporary/XDG data into `.issue200-runtime/`.
Some extraction script search paths record the existing local package stores;
on another machine install those packages in the active Python environment.
With this repository as cwd, run native DRC for each final PCB/project, then:

```sh
E=hardware/kicad/qualification/issue-200-wing-rev3
python3 "$E/verify.py"
python3 "$E/verify-mechanical.py"
python3 "$E/harness-clearance.py"
python3 "$E/verify-panel.py"
python3 "$E/verify-cam.py"
python3 "$E/verify-fem.py"
python3 "$E/power-summary.py"
```

`verify.py` independently checks actual filled-copper connectivity, wrong-net
contacts, native DRC material violations, unexplained input-to-final changes,
component pin/pose transforms, routing widths and all via-to-pad pairs.
Same-net pads, testpoints and NPTH are included; the audit measures annulus
edge to native effective pad shape, not center distance. CSV.gz retains all
pairs. `verify-mechanical.py` separately compares Rev.2 fixed components and
Stage 1b outlines, holes, south band and vertical 1.2mm probe access.

For each pitch, `panel-*` is one independent-circuit left/right Standard-PCBA
unit. Both assembly sides are required: 84 bottom and 14 top purchased
placements. It contains CAD/project, Gerber copper/mask/paste/silk/profile,
PTH/NPTH drills, `fabrication.zip`, BOM, CPL, `pin1.csv`, top/bottom assembly
SVGs, panel geometry, full DRC and all-pair via/pad audit. Individual board CAM
is also supplied. `manufacture.py` regenerates both panels and all CAM only
from qualified boards. Run full panel DRC and both independent panel/CAM
checks after generation. Tab copper setbacks are >=2mm; separation/DFM and
finished locator NPTH 1.70+/-0.05mm require manufacturer/physical acceptance.
CPL uses KiCad absolute X, negated Y, top-view CCW angles, and explicit side;
use physical `pin1.csv` to validate machine-specific bottom rotation.

`extract-resistance.py` reads each final filled board, models two copper
sheets and explicit via barrels, and solves distributed 127mA loads using
coarse/fine meshes at nominal/80% track widths. Run it with board directory
names to refresh eight cases per board after any copper change. The analytic
sheet self-check is in `fem-selfcheck.json`. `power-summary.py` rejects stale
board hashes and replaces the historical #141 Wing term with the extracted
Rev.3 terminal drops; Main Rev.4 #196 common/branch resistance is retained.
The 200mm adopted harness remains the baseline; 124.097mm is a comparison
candidate. The 125C electrical sensitivity is not an assembly temperature
rating (GH catalog maximum is 105C).

Case CSVs and their generator live in `hardware/case/issue-200-rev3/`.
D-034 is a draft. Harness length, case modeling and physical acceptance are
recorded in the report; this package does not select a pitch or procure parts.
