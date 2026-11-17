# Wing Rev.6 16mm-right — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv` (Issue #267 conversion,
carried over unchanged — Issues #270/#273 changed the notch-zone
outline only; parts, footprints and positions are identical to
Wing Rev.5). Gerbers in this package were regenerated in Stage 2e
(Issue #273) from the final Rev.6 boards.
Do NOT upload the KiCad-native `BOM.csv` / `CPL.csv` — their LCSC column is
empty (except FH12) and the CPL uses KiCad headers.

- BOM: 4 part rows / 49 designators, every orderable designator mapped to a
  real LCSC code (sources: Matrix Rev.3 package BOM — DRV5055A3QDBZR /
  C266128, GRM188R71C104KA01D / C45000, TMUX1208PWR / C494728).
  Unmapped parts: NONE.
- FH12: J_WING (Hirose FH12-14S-0.5SH(55)) = LCSC **C5378715** — verified
  orderable at JLCPCB in the Issue #267 quote run (Extended part, stock
  3,907 on 2026-11-17, auto-matched in the PCBA quotes). No consignment
  needed. Do not substitute another connector. Re-confirm stock at order
  time.
- Excluded from the JLCPCB BOM (as in the adopted packages): NPTH mounting
  holes (MH_*, H1-H4) and test-point pads (TP_*) — not orderable parts.
- Assembly is single-sided, all parts on the BOTTOM layer (Layer column of
  the CPL says `bottom` throughout).
- CPL frame: gerber frame = native KiCad frame for this package (offset
  +0.000000 / +0.000000 mm; all 49 footprint origins re-verified against
  the fresh Rev.6 CPL export, max deviation < 0.000001 mm). Use only the
  converted file, not `CPL.csv`.
- Board change vs Rev.5: Edge.Cuts only (Stage 2e notch: straights
  following the Main Rev.9 tab + single fillets/arcs, whole notch span
  replaced; pour fringe refilled, fill delta confined to the
  removed+added notch band). Routing and footprints unchanged;
  see the Issue #270 REPORT.md, Stage 2e section.
- Inherited gates: supplier DFM, stencil/paste acceptance, stock
  confirmation at order time, CPL rotation/pin-1 acceptance (bottom-side
  parts), physical fit checks. Wing assembly method (PCBA vs hand) is NOT
  decided — it waits on the Matrix evaluation; this handoff supports the
  PCBA quote and the bare-board price only. No order, no release.
