# Matrix Rev.4 — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents
(`m1-matrix18-gerber-review.zip` is provided), `BOM-jlcpcb.csv` and
`CPL-jlcpcb-gerber-frame.csv` (Issue #268 conversion, Rev.3/#219 frame
method). Do NOT upload any KiCad-native BOM/CPL — none is included here.

- BOM: 43 part rows / 43 designators in 4 MPN groups, every orderable
  designator mapped to a real LCSC code carried from the adopted Matrix
  Rev.3 BOM. Only the connector line changed:
  J_WING = Hirose **FH12-14S-0.5SH(55)**, LCSC **C5378715**
  (Extended part; the same code auto-matched in the Issue #267 Main/Wing
  PCBA quotes). Unmapped parts: NONE.
- Excluded from the BOM: test points and the four NPTH mounting holes —
  not orderable parts (as in the Rev.3 package).
- Assembly is **two-sided** in Rev.4: 42 components on top, the FH12
  alone on the bottom. The quote must price the bottom-side placement.
- CPL frame: gerber frame = KiCad frame via (X, -Y); vs the legacy
  KiCad-frame CPL the offset is +36.000000 / -140.000000 mm. 42 rows are
  carried over from the verified Rev.3 file; the J_WING row is recomputed
  (housing body centroid (100.000000, -134.400000), bottom, rotation
  180.000000). See `CPL-jlcpcb-gerber-frame-NOTES.md`.
- DRC for this board (KiCad, severity-all): **0 errors, 0 unconnected**,
  1 warning — a dangling-track warning on the Rev.3-original HALL_5V bus
  tail at (112.6, 127.2), connected copper whose Rev.3 continuation was
  removed with the old fanout by design. Full record in `../REPORT.md`;
  the DRC JSON is `drc.json` in this directory.
- Via-pad: minimum different-net gap 0.100 mm (at the 0.10 mm floor);
  two same-net exceptions are disclosed in `FABRICATION.md`, including a
  MUX_OUT_A via clipping its own test pad's corner — expect a possible
  fabricator DFM query there; no via fill/cap processing is requested.
- Inherited gates: supplier DFM, stencil/paste acceptance, stock
  confirmation at order time, CPL rotation/pin-1 acceptance for the
  bottom-side FH12, and the bench FFC fit check against Main Rev.8 with
  the stock Molex 152660149 cable. This handoff authorizes a quote
  only — no order, no manufacturing release.
