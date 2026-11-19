# Wireless Main — JLCPCB quote handoff (DRAFT package, NOT FOR ORDER)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv`.
Status: DRAFT for the D-057 adoption gate — do not order from this
package. The U1 footprint is derived (REPORT.md deviation 1) and
must be replaced with Insight SiP official CAD first.
**Fix-round note (2026-11-19):** the official footprint is now in
`wmain.pretty` and in the working board, but this package is NOT
regenerated: the tree board is unchanged, and re-routing the
official footprint needs a fanout-rule decision (REPORT.md
deviation 9 — the land pattern fans out at ≈0.05 mm class in the
module field, per the maker's own test board). At quote time,
confirm JLCPCB's capability and pricing for the module-field
fanout rules the PO adopts; the U1 pre-order terms below are
unchanged.

- BOM: 55 designators / 32 consolidated lines. LCSC codes are
  filled only where a repo record verifies them (TPS63070 C109322,
  TPS22919 C2149796, FH12 C5378715, EZmate 781710004 C588524,
  XFL4020 C3033018, 100k C25803, 10k C25804, 1k C21190,
  100nF C1525, 1nF C1523). All other lines are marked
  "verify at quote" — confirm each at the matching screen.
- U1 module line: ISP1807-LR-RS = LCSC **C5264268**, JLCPCB
  **Pre-order Part (Extended)**: shelf stock 0 at JLCPCB and LCSC,
  estimated unit price $11.78, estimated lead time ~28 days
  (verified live 2026-11-19). Alternatives if pre-order is not
  acceptable: DigiKey purchase + consigned parts, or hand-fit
  with the SWD/continuity bring-up in FABRICATION.md.
- JBATT (JST GH 2-pin): LCSC code unconfirmed — verify at quote.
- No-part rows (test points, mounting holes, JSWD pads, JPAD
  land) are listed in the BOM with an explicit note so the
  matching screen can be cleared line by line.
