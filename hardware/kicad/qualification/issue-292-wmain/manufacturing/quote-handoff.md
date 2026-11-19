# Wireless Main — JLCPCB quote handoff (DRAFT package, NOT FOR ORDER)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv`.
Status: DRAFT for the D-058 adoption gate — do not order from this
package until the PO adopts. Regenerated 2026-11-19 (re-route
round) from the finished tree board, SHA-256 `2f0b4526…`.

**⚠ FINE FIELD — confirm at quote:** the ISP1807-LR module field
(rule area MODULE_FIELD_FINE, 11.6 × 9.85 mm = 114.26 mm² around
the module at board coords x 69.3–80.9, y 119.05–128.9) is routed
at the **0.05 mm class** under design decision D-057: measured
minima inside the field are track width 0.050 mm, track–track
0.066 mm, track–pad 0.046 mm, via-to-copper 0.050 mm. This is
below JLCPCB's standard-process minima — **confirm capability
and any price/lead-time impact for the fine field explicitly at
quotation**. The rest of the board is at the D-019 rules
(0.10/0.10 mm). The maker's own ISP1807 test board uses the same
fanout class (REPORT.md deviation 9).

**Residuals:** 6 unconnected items remain on this board
(REPORT.md deviation 10: module GND pads 14/16 pair, VBUS,
SYS_3V3 ×2, PAD_EN, VBAT_SENSE). The package is complete as a
manufacturing record of the current design state; it is not an
order-ready board.

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
