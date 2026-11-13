# Issue #232 — E-R full-cover Wing plates and receiving case

New case tree for 16 and 17 mm pitches. The two Wing decks follow the D-037
silhouette and include the complete south shelves. The central Main/Fly service
bay remains open; its connectors and #235 cable rises cannot fit under a solid
Z16.2 lid. No Wing connector notch exists in either plate. Review this scope in
[REPORT.md](REPORT.md).

Read [the verification report](REPORT.md) before using the files. The complete
physical acceptance gate remains open because no actual keycap skirt profile
was supplied. The cap solids in `assembly.step` are named **cap-gauge** and are
acceptance/reference envelopes, not validated purchased caps. Their collisions
are disclosed separately; they must not be mistaken for qualified cap geometry.
D-037's accepted official Fly USB-shell model limit remains unchanged.

- `16mm/` and `17mm/`: new tray STEP/STLs, retained splice/rack STEP/STLs,
  assembly STEP, connected 160 mm Wing harnesses, re-dressed connected 170 mm
  Fly harness, post positions, dimensions and verification JSON.
- Each `plate-package/`: separate left/right DXF + STEP, drawing notes, local
  aperture and tie-hole tables, outlines and geometry metadata. **Package only;
  plate ordering remains a PO gate.**
- `support-post.step/.stl`: common printable insulating split-peg post. Twelve
  per keyboard. Files retain Z1.20–10.00 assembly datums; bed translation is
  described in [ASSEMBLY.md](ASSEMBLY.md).
- `review-top.svg/.png`: plate outlines, service routing and post locations.
  Dashed lines are route control polygons; STEP contains R5 swept paths.
  `review-section.svg/.png` shows the fixed Z stack and required skirt plane.
- `exports-sha256.json`: all new-tree sources, artifacts and evidence.

Run `./hardware/case/issue-232-final/reproduce.sh` from the checkout root with
Python dependencies in `requirements.txt`. The defaults reuse the host's
read-only CAD and geometry environments documented by #235; override
`CAD_PYTHON` and `GEOMETRY_SITE` on another host. All temporary files, caches
and logs belong in `.issue232-runtime/`, never `/tmp`. No source study or prior
production tree is written. STEP timestamps may change on regeneration; rerun
the checks and manifest generation together.

For a read-only artifact check: `python3 hardware/case/issue-232-final/manifest.py`.
Assembly and physical gauges: [ASSEMBLY.md](ASSEMBLY.md). Material and finish:
[plate-package-notes.md](plate-package-notes.md). No print/order/push/PR is part
of this design work.
