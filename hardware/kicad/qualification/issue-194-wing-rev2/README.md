# Wing Rev.2 — Issue #194 Phase B

The four `wing-rev2-{16,17}mm-{left,right}/main.kicad_pcb` files are the
independently checked board candidates. Use each matching `main.kicad_pro`.
`qualification.json` identifies the exact PCB SHA-256 and acceptance result.
Raw autorouter files (`routed`, `continued`, `power-repaired`) are intermediate
candidates and must not be ordered. The independent gate is `verify.py`, not
an autorouter's exit status or its internal success counter.

Sources: `hardware/jitx/wing/rev2.py` consumes the approved Phase A JSONs;
`build.py` authors real bottom-side Hall/local capacitors and all 46 NPTHs per
half, preserving physical pin identities. `sources/calibration.md` records the
active-point calibration and the nominal locator adoption with its limits.

Routing starts with KiCadRoutingTools, D-021 widths, ordinary0.60/0.30mm vias
and same-net pad target0.15mm. The initial automatic attempt is retained.
`local-repair.py` and `grid-search.cpp` rebuild the congested service window
with automatic two-layer A* and native collision checks. Power/plane routing
is run again with the same rules. Some router rescue stages still emitted
0.10mm power necks despite `--strict-sizes` and no-neckdown options;
`normalize-power.py` enforces the actual0.30mm floor. Such edits require a
new DRC and copper-graph check; they are not accepted by assertion alone.
`via-margin.py` applies native-checked local stub moves, targets0.15mm and
allows a documented0.125mm fallback. `finish.py` refills the two supplemental
power/ground pours and reserves2mm copper setbacks at panel break locations.

Validation uses KiCad9.0.9. `verify.py` independently checks every component
and pad pose/net, source transfer, outline, effective project, widths, via
sizes, mounting circles, required-pad physical copper components and actual
wrong-net contacts. Filled zones are included as polygon copper, never ideal
net-name connections. Full native DRC is saved separately in `drc.json`.
Every via-to-pad pair is recorded, including same-net and test pads; the nearest
gap per via and its distribution are in the qualification result.

Run stdlib source checks from the repository root:

```sh
PYTHONPATH=hardware/jitx python3 -m wing.rev2 --check
python3 hardware/case/issue-194-layout/generate.py --check
python3 hardware/case/issue-194-layout/verify.py
python3 hardware/case/issue-194-rev2/generate.py
```

Native scripts require `pcbnew`, Shapely2 and NumPy. In the provided work copy,
use `.issue194-runtime/run /usr/bin/python3` with this repository as cwd. That
wrapper points at the workspace's extracted KiCad runtime and keeps XDG and
scratch files inside `.issue194-runtime/`. Compile `grid-search.cpp` to that
runtime's `grid-search`, with `TMPDIR` set to its `tmp/` directory. The exact
routing commands and tool identity are preserved with the evidence. To
reinspect, run CLI DRC against each final PCB with its matching project, then
run `verify.py`. No network or router rerun is needed to verify saved results.

## Assembly/fabrication package

`manufacture.py` creates one independent-circuit left/right panel per pitch.
The `panel-*` directories contain Gerbers (both copper, mask, paste and silk
sides), PTH/NPTH drill files, BOM, CPL, pin1 table, CAD, manifest and fabrication
ZIP. Individual-board packages are supplied for traceability; the panel is the
intended Standard-PCBA unit. Never mix a BOM/CPL from one pitch or origin with
another Gerber set.

Use two layers,1.2mm FR-4, copper35um design basis, ordinary through vias
0.60/0.30mm with inherited front/back tenting. No via-in-pad/POFV is required by
the qualified geometry. Locator NPTH must finish at1.70+/-0.05mm; four mounting
holes per half are2.2mm. Do not replace the locator requirement with a generic
factory drill tolerance. Confirm finished-hole and positional tolerances and
physical Jade Pro fit before an order release.

The panel stacks L and R with3mm routed spacing,5mm tabs, six0.6mm mouse-bite
holes per separation row at0.9mm pitch,5mm side rails, tooling holes, and
front/rear optical marks. There is no electrical bridge between halves or
rails. Actual filled copper is checked against every tab with a2mm inward
setback. The fabrication drawing and separation process need the factory's
review. Product contours use the PO south-cut revision: five vertices, with
south at the full switch-envelope limit and the inner corner chamfered.
`manufacture.py` transfers each actual source polygon into the panel, including
the chamfer; it never substitutes a bounding rectangle.
Deburr tab residue before case-fit acceptance.

Assembly requires **Standard PCBA with two assembly sides**:42 Hall sensors
and42 local capacitors on the panel bottom;6 MUX,6 MUX capacitors and2 GH14
connectors on top. Total98 purchased placements. Test pads, holes and fiducials
are PCB features and are excluded from the purchased BOM/CPL. Part numbers
remain exact; no automatic stock substitution or supplier stock claim is made.

CPL uses the same absolute Gerber origin: X=KiCad X, Y=-KiCad Y, mm; rotation
is CCW in top-view coordinates and layer is explicit. Negative Y values are
intentional. `pin1.csv` records the actual physical pad1 coordinates and
`assembly-{top,bottom}.svg` keeps top-view coordinates for both sides. The
assembler must apply its library/machine's bottom rotation convention using
those pad1 references; do not blindly mirror or add180 degrees to all parts.

JLC's current [PCBA capability table](https://jlcpcb.com/capabilities/pcb-assembly-capabilities)
allows double-sided assembly for Standard and requires rails/fiducials;
its panel limit is250x250mm. The generated panels fit that envelope.
[Panelization guidance](https://jlcpcb.com/help/article/pcb-panelization)
is a process input, not approval of this specific panel. No order, payment,
external upload, production qualification, or pitch-selection decision is
part of this package.

Native-runtime notes: query a through-via width with an explicit copper layer
(`GetWidth(F_Cu)`); the no-layer call asserts in this KiCad9 build. Use
`BOARD.Delete(item)` for discarded copper in this binding; the `Remove` path
invalidated the SWIG track-container wrapper during the first repair attempt.
The final independent verifier reads actual saved geometry and never edits it.

## Completed south-cut qualification

The third start completed the saved candidates; see `resume-audit.md`.
All four boards have zero required opens, wrong-net contacts, material
violations and unexplained transfer changes. Full native DRC also has zero
violations and zero opens. The minimum via-pad gap is 0.125mm across 129580
pad/via pairs (including same-net); the 17mm-right minimum is 0.131375mm.
`via-pad-all-pairs.csv.gz` is the current full pair audit for each board.
Uncompressed earlier-run pair CSVs were archived in the runtime, not shipped
alongside the current audit. Raw router candidates remain historical evidence.

`verify-mechanical.py` checks all 84 switch envelopes, 168 locator keepouts,
and 336 mounting-circle/key pairs, plus saved contour/hole coordinates and
copper-to-chamfer distance. `verify-panel.py` compares every transferred
footprint/pad and track/via, preserves both chamfers, and requires native panel
DRC to be entirely zero. `verify-cam.py` reads all emitted Gerber profile
segments, PTH/NPTH drills, BOM and CPL rows and verifies CAM hashes.
Run those three scripts after `verify.py` and after fresh CLI DRC on both
panels. `render.py` regenerates the six pairs of assembly SVGs.

Panel construction retains the original native boards and serializes/reloads
all duplicated objects before zone fill to avoid native SWIG lifetime faults.
The panel tab rule areas permit NPTH mouse-bite pads; the independent actual
copper audit still enforces 2mm setback for tracks, vias, pads and filled zones.
