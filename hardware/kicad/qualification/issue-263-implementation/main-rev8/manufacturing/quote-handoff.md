# Main Rev.8 — JLCPCB quote handoff (DRAFT package, not released for manufacture)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv` (Issue #267 conversion).
Do NOT upload the KiCad-native `BOM.csv` / `CPL.csv` — their LCSC column is
empty and the CPL uses KiCad headers.

- BOM: 54 part rows / 55 designators, every orderable designator mapped
  to a real LCSC code (sources: Main Rev.6 package BOM; C26-C28 = adopted
  substitute TDK C3225X7R1C226MT000N / C342699 and R17 = Yageo
  RT0603BRD0754K9L / C728593 per docs/issue-175; L1 = C3033018 per the
  order-time rule, stock 19,053 on 2026-11-16). Unmapped parts: NONE.
- FH12: J2/J3 (Hirose FH12-14S-0.5SH(55)) carry the placeholder
  `C-HIROSE-FH12-14S` — this part is NOT sourced at JLCPCB. Expect the SMT
  flow to flag it as unmatched; the quote must state how it is handled
  (consigned / hand-fitted later). Do not substitute another connector.
- Excluded from the JLCPCB BOM (as in the Rev.6 package): mounting holes
  H1-H3 (NPTH) and test points TP1-TP4 — not orderable parts.
- CPL frame: gerber frame = native KiCad frame for this package (fitted
  offset +0.000000 / +0.000000 mm from the board Edge.Cuts vs the Edge_Cuts
  gerber; outline vertices and all 55 footprint origins verified,
  max deviation 0.000000 mm). Unlike the Rev.6 legacy CPL, no translation
  is needed — but use only the converted file, not `CPL.csv`.
- Inherited gates (from the Rev.6 handoff, unchanged): supplier DFM,
  stencil/paste acceptance, stock confirmation at order time, CPL
  rotation/pin-1 acceptance, physical fit checks. This handoff authorizes
  a quote only — no order, no manufacturing release.
