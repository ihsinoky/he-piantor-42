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
