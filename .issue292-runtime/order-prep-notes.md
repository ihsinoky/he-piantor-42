# Issue #292 order-prep notes (2026-11-19)

## Measured land patterns (from tree board, SHA 509e52a7)
- JBATT fp "GH2": 2 SMD pads 0.6x1.7 @ +/-0.625 (pitch 1.25),
  outline 5.9 x 4.4. Design intent (FABRICATION.md / REPORT
  dev.7): JST GH top entry, BM02B-GHS-TB class, 1.25 pitch,
  2.9 mm tall. JST GH datasheet (jst-mfg.com eGH.pdf):
  BM02B-GHS-TBT = top entry 2-ckt, A=1.25, B=5.75.
- SW1 fp "TACT_2pad": 2 SMD pads 1.2x1.8 @ +/-1.6
  (terminal pitch 3.2), outline 5.2 x 3.0.
- D1/D2 fp "SOD-123": pads 0.9x1.1 @ +/-1.35 (pitch 2.7,
  span 3.6) = SOD-123 gull-wing land. Pad1 net VIN_IN,
  pad2 net VBUS (D1) / VBAT+ (D2) -> pad1=K, pad2=A
  convention. PMEG4020ER (Nexperia) is SOD123W/CFP3 flat
  lead, pin1=K pin2=A, 40V 2A (datasheet 2023-01-01):
  pinout matches, package/land differs -> see PMEG section.

## Session 2 verification results (2026-11-19)
- SW1: KiCad std-lib TS-1187A footprint checked as a candidate class — REJECTED (4 pads at ±3.0mm span, ~5.5mm body; does not match land ±1.6mm). No stocked part's terminal pitch (3.2mm) could be verified from a published drawing/listing → SW1 = DO NOT PLACE / hand-fit at bring-up. Intended class: 3x4x2mm 2-pin turtle tact (YIZHI YZA-009 C49108621, LCSC InStock $0.0136, terminal width 1.5mm per maker's diagram) — pitch unverified, confirm on physical part before any future placement.
- DLED C12624 KENTO KT-0603G: LCSC live InStock, emerald green 525nm, Vf 3.1V, 430mcd, 0603. Board pad1 = anode (LED_A via RLED), pad2 = cathode (GND) per design.py. JLCPCB library pin-1 polarity not published → quote-stage check recorded in BOM note (rotate CPL 180deg if library pin1 = cathode).
- Q1 C8545 JSCJ 2N7002: LCSC live InStock, SOT-23 60V/115mA, RDS(on) 5ohm@10V. Standard 2N7002 pinout = board mapping (1=G,2=S,3=D).
- 22uF C45783 Samsung CL21A226MAQNNNE: JLCPCB part page live = Basic, InStock (assembly pool). LCSC retail page momentarily OutOfStock — different pool; assembly channel governs.
- DigiKey ISP1807-LR-RS (for quote-handoff): DigiKey JP crawl (2026-11-17) stock 13,850 (global), CT 50+ JPY 2,249.60, TR 500 JPY 1,837.90; US: 50+ $13.6476, 500 $11.15, in-stock 29,500 (crawl 2026-11-07). DK part 1786-1019-1-ND (CT) / -2-ND (TR). Small-qty single price ~JPY 2,000-2,300 class excl. tax/shipping.
