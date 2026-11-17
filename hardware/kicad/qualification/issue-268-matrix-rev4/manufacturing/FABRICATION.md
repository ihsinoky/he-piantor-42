# Matrix Rev.4 — fabrication and assembly review requirements

**DRAFT / NOT FOR ORDER.** Quote-review package for Issue #268.
No order, charge or manufacturing release.
Use only `../board/m1-matrix18.kicad_pcb` from this Rev.4 directory with this note.
See `../REPORT.md` for the full change record and gate results.

## What changed vs Rev.3

- Connector only: the top-side JST GH14 header (BM14B-GHS-TBT, C265384) is
  replaced by a **Hirose FH12-14S-0.5SH(55)** bottom-contact ZIF
  (LCSC **C5378715**) on the **bottom** side, same anchor point (100, 133),
  mouth facing the south board edge, pad 1 east. Pin assignment is unchanged:
  pad n carries D-024 signal n (verified numerically against Wing Rev.5 and
  Main Rev.8 — see `../REPORT.md`). Mounting (MP) lands remain NC.
- Copper changes are confined to the nine D-024 link nets (fanout re-route
  plus reconnection of the fragments the fanout replacement severed).
  Outline, all other 64 footprints, sensor field and measurement features
  are identical to Rev.3 (verified by census/outline diff).

## Board (unchanged from Rev.3)

- One **128 x 80 mm**, **two copper layer**, **1.2 mm** finished board.
  Signal traces **0.10 mm**, HALL_5V/GND traces **0.30 mm** (with disclosed
  0.15 mm GND necks at the connector escape, see REPORT), copper clearance
  **0.10 mm**. Nominal copper 35 um (1 oz).
- Four **NPTH diameter 2.2 mm** mounting holes; **diameter 5 mm copper
  reservations** retained on both layers.
- Supply ordinary plated through vias, **169 sites, diameter 0.60 mm /
  drill 0.30 mm**, inherited mask tenting on both sides. No fill/cap
  (POFV) processing is requested — see the via-pad note below.
- `gerber/`: seven artwork layers, separate PTH/NPTH drills; absolute mm
  coordinates. `.gbrjob` is informative only.
- `paste/`: front 144 apertures (42 top-side components), bottom 16
  apertures (the FH12's 14 signal + 2 MP lands). All 18 bare testpads
  intentionally have no paste.
- Assembly is now **two-sided**: 42 components top, 1 component
  (the FH12) bottom. 43 assembled components / 4 exact MPN groups:
  18 Hall sensors, 3 MUX, 21 capacitors, 1 FH12. Testpads and NPTH holes
  are excluded from the BOM; no substitutions.

## Via-pad audit (0.10 mm floor, carried from Rev.3)

Rect-model audit of every via annulus against every pad (same method as the
Rev.4 verification; Rev.3's native-shape audit minimum was 0.1075 mm):

- Minimum **different-net** gap: **0.100 mm** — at the floor, not below it
  (MUX_A2 escape via at (100.55, 128.00) vs TP_W_MUXB.1 pad).
- Two **same-net** exceptions, disclosed:
  - MUX_OUT_A via at (82.65, 127.35) overlaps the corner of its own net's
    bare test pad TP_W_MUXA.1 by 0.25 mm (annulus edge basis). The pad is a
    probe point, not a soldered component land; the remaining pad area is
    probe-able. No fill/cap process is requested for it; a fabricator DFM
    query on this site is acceptable and expected.
  - HALL_5V via at (122.40, 119.45) sits 0.048 mm from the same-net
    C_MUX_C.1 pad edge. No overlap.
- No via overlaps any **component** pad; no POFV is required.

## Inherited conditions

- The inherited `M1 MATRIX18 / ISSUE178` silk label is retained (this
  revision changes the connector and link-net traces only).
- Use nonmagnetic sensor-adjacent fixtures. Supplier DFM, stencil/paste
  acceptance, stock confirmation at order time, CPL rotation/pin-1
  acceptance for the bottom-side FH12, and the physical FFC fit check
  against Main Rev.8 remain order-time gates.
