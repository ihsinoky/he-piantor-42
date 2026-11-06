# Issue #190 Stage 1 data

Read [the report](../../../docs/issue-190-wing-layout-stage1.md) for coordinate frames, fit conditions, dimensions and Stage 2 decisions. These files are proposals and planar screening evidence, not fabrication inputs.

- `coordinates-u.csv`: all 21 original centers, exact rational u/v, source angles.
- `coordinates-{16,17}mm.csv`: proposed board-local centers and KiCad absolute conversion; zero key rotations.
- `keys-{16,17}mm.csv`: proposed replacements for #150 CSVs, preserving header, row order, key/sensor mapping and zero rotations.
- `deltas-{16,17}mm.csv`: new minus current centers, including fixed-anchor and reanchored cases. Local Y is up; explicit KiCad ΔY is down.
- `clearances-{16,17}mm.csv`: per-key center-to-edge/hole distances and square-to-drill/keepout clearances for both anchor and angle cases. Positive gap means separation; negative means overlap/overhang.
- `pair-screen-{16,17}mm.csv`: all 210 pairs for each envelope and angle case. Signed SAT separation is a separating-axis screening metric, not the shortest Euclidean distance.
- `geometry-summary.json`: bounds, minima, overlap counts and outline-policy dimensions. `source` angles are independently retained mechanical angles, not a shear/stretch of the physical switch.
- `definition-*.proposal.json`: concrete JSON replacement operations for center-related fields, with unresolved whole-board fields clearly listed. Do not apply as a production definition.
- `placements-*.proposal.csv`: row/reference replacement plan for the 21 Hall sites, 21 associated capacitors and three dependent raw testpoints. Other components still require Stage 2 review.
- `layout-comparison.svg`: current/proposed center overlay on existing outlines, with proposed Jade envelope and mounting keepouts; explanatory drawing only.
- `inputs/`: frozen #150 CSVs, published drawing excerpts and their prior source records, Issue/instructions, independently extracted upstream center/angle tables, pinned source revisions and PCB hashes. The #150 input CSVs are historical geometry, not corrected coordinates. `input-hashes.json` also pins the existing representative21 definition/placements files.
- `verification.json`: successful source, proposal and coordinate checks.

From the git-copy root, verify without writing files:

```sh
python3 hardware/case/issue-190-layout/analyze.py --check
python3 hardware/case/issue-190-layout/verify.py
```

The second command additionally checks input hashes and applies each proposed JSON patch in memory to compare all moved components with the proposed placement rows. `analyze.py` without `--check` regenerates only data files in this new directory.

For an independent upstream extraction check, download the two fixed-revision PCB URLs in `inputs/upstream.json` under `.issue190-runtime/sources/` as `cantor.kicad_pcb` and `piantor.kicad_pcb`. Run `verify.py --upstream-dir <that-directory>`; it verifies hashes and parses balanced footprint blocks. The recorded verification used that mode. Keep all downloads/runtime under `.issue190-runtime/`, never `/tmp`.

`zero` retains #150 mechanical rotation 0; `source` screens the extracted source angles (+5/−10/−25 degrees on thumbs). Finger-column 180-degree differences have the same square envelope. Neither a narrow 15 mm cap product nor 3D/production compatibility is certified here. No layout, routing, manufacturing data, case CAD, order or payment is produced.
