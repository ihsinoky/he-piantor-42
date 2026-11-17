# Wing Rev.5 16mm-right — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv` (Issue #267 conversion).
Do NOT upload the KiCad-native `BOM.csv` / `CPL.csv` — their LCSC column is
empty and the CPL uses KiCad headers.

- BOM: 4 part rows / 49 designators, every orderable designator mapped to a
  real LCSC code (sources: Matrix Rev.3 package BOM — DRV5055A3QDBZR /
  C266128, GRM188R71C104KA01D / C45000, TMUX1208PWR / C494728).
  Unmapped parts: NONE.
- FH12: J_WING (Hirose FH12-14S-0.5SH(55)) carries the placeholder
  `C5378715` — this part is NOT sourced at JLCPCB. Expect the SMT
  flow to flag it as unmatched; the quote must state how it is handled
  (consigned / hand-fitted later). Do not substitute another connector.
- Excluded from the JLCPCB BOM (as in the adopted packages): NPTH mounting
  holes (MH_*, H1-H4) and test-point pads (TP_*) — not orderable parts.
- Assembly is single-sided, all parts on the BOTTOM layer (Layer column of
  the CPL says `bottom` throughout).
- CPL frame: gerber frame = native KiCad frame for this package (fitted
  offset +0.000000 / +0.000000 mm from the board Edge.Cuts vs the Edge_Cuts
  gerber; outline vertices and all 49 footprint origins verified,
  max deviation < 0.000001 mm). Use only the converted file, not `CPL.csv`.
- Inherited gates: supplier DFM, stencil/paste acceptance, stock
  confirmation at order time, CPL rotation/pin-1 acceptance (bottom-side
  parts), physical fit checks. Wing assembly method (PCBA vs hand) is NOT
  decided — it waits on the Matrix evaluation; this handoff supports the
  PCBA quote and the bare-board price only. No order, no release.
