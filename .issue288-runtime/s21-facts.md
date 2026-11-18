# Issue #288 Stage 2 — S2.1 extracted facts (all measured/observed, sources cited)

## Donor (Rev.3, `issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb`, via pcbnew)
- Outline bbox x 36..164, y 60..140 (128x80), thickness 1.2, 2 Cu layers.
- Netclasses: Default (track 0.10, clr 0.10, via 0.60/0.30), Power (track 0.30,
  clr 0.10, via 0.60/0.30). Power nets: GND, HALL_5V.
- 65 footprints: 18 hall, 3 mux, 21 capacitor, 18 testpoint, 4 mounting, 1 connector.
- Sensor sites (footprint centres = field coordinates):
  16mm section x=50/66/82, y=74/90/106; 17mm x=117/134/151, y=73/90/107.
- Sensor refs by group (group = MUX): A: U_HA0(50,74) U_HA1(50,90) U_HA2(50,106)
  U_HA3(117,73) U_HA4(117,90) U_HA5(117,107); B: x=66 col + x=134 col (B0..B5);
  C: x=82 col + x=151 col (C0..C5). Sensor i in group -> net H_<G><i>_RAW.
- Donor hall footprint (SOT-23): pad1 VCC local (-1.0156,-0.95), pad2 OUT
  (-1.0156,+0.95), pad3 GND (+1.0156,0); pads 1.31x0.46.
- Per-sensor cap C_H<G><i> (100nF 0603, GRM188R71C104KA01D, LCSC C45000) at
  sensor + (3.5, 0); pads N-S: p1 HALL_5V (y-0.844), p2 GND (y+0.844).
  MUX caps C_MUX_A(87,121) B(105,121) C(123,121), same part/orientation.
- TMUX1208PWR (LCSC C494728) at A(82,122) B(100,122) C(118,122), TSSOP-16:
  pin1=A0, 2=EN(WING_EN), 3=VSS(nc), 4=S1, 5=S2, 6=S3, 7=S4, 8=D(out),
  9=S8(nc), 10=S7(nc), 11=S6, 12=S5, 13=VDD(HALL_5V), 14=GND, 15=A2, 16=A1.
  Sensor i -> S(i+1): i0..3 = pins 4..7, i4 = pin12 (S5), i5 = pin11 (S6).
  Address (A2A1A0)=k selects S(k+1) => sensor i at address i; spares:
  addr 6 = S7 = pin10, addr 7 = S8 = pin9.
- Raw TPs (PCB_PAD_1.2MM): H16 CTR=H_B1(62.5,90) N=H_B0(62.5,74) DIAG=H_A0(46.5,74);
  H17 CTR=H_B4(130.5,90) N=H_B3(130.5,73) DIAG=H_A3(113.5,73).
  Link TPs north y=63: A0(98) A1(102) A2(106) EN(110) H5V(90) GND(94);
  south y=127: MUXA(82) MUXB(100) MUXC(118) GND_A(85) GND_B(103) GND_C(121).
- Mounting: NPTH d2.2 at (39,63) (161,63) (39,137) (161,137); 4 no-net zones
  5x5 at corners (d5 copper reservations).
- J_WING GH at (100,134.95), pads y=133 (removed in this design).
- Zones: none for copper pour (only the 4 corner reservations). All
  connectivity is tracks/vias.

## TMAG5253 (TI SBASAI5E, sources in he-piantor-tmag worktree)
- Pins (DMR X2SON-4): 1=VCC, 2=GND, 3=EN, 4=OUT, 5=thermal pad (NC; float or
  GND; must be soldered). EN VIH 0.65xVCC. Hall element CENTRED in package
  (Fig 8-3), 130um below top; Z-axis sensing only.
- Land pattern (TI drawing DMR0004A, EXAMPLE BOARD LAYOUT, verified by pixel
  measurement of the PDF at 600dpi, scale 35x): lands 4x 0.22 (X) x 0.40 (Y);
  pin columns x = +/-0.25 (2x 0.5 pitch); pin rows y = +/-0.70 (the (1.4)
  dimension between pin centrelines); thermal land 0.8 (X) x 0.6 (Y) centred,
  optional d0.2 via. NSMD preferred (mask opening = metal +0.05 max all around).
- Pin placement (top view, TI frame: Y = 1.4mm axis): 1=(-0.25,+0.70) VCC,
  4=(+0.25,+0.70) OUT, 2=(-0.25,-0.70) GND, 3=(+0.25,-0.70) EN.
  Cross-checked against PO's he_kbd_module SW_HE_1.00u_PTMAG5253 footprint
  (same arrangement rotated 90 CCW, lands extended) - consistent.

## XIAO nRF52840 (Seeed official symbol/footprint, PO he_kbd_module repo)
- Pads (DIP): rows y=+/-7.62, pitch 2.54, PTH drill 0.889, pad 1.524.
  Row y=-7.62 (x +7.62 -> -7.62): pads 1..7 = D0 D1 D2 D3 D4 D5 D6.
  Row y=+7.62 (x -7.62 -> +7.62): pads 8..14 = D7 D8 D9 D10 3V3 GND VBUS.
- Pin functions: 1 D0=P0.02/AIN0, 2 D1=P0.03/AIN1, 3 D2=P0.28/AIN4,
  4 D3=P0.29/AIN5, 5 D4=P0.04/AIN2, 6 D5=P0.05/AIN3, 7 D6=P1.11/TX,
  8 D7=P1.12/RX, 9 D8=P1.13/SCK, 10 D9=P1.14/MISO, 11 D10=P1.15/MOSI,
  12 3V3(out), 13 GND, 14 VBUS(5V).
- Frozen pin map (Stage 2): MUX_OUT_A->D0, B->D1, C->D2; A0->D6, A1->D7,
  A2->D8; EN_A->D9, EN_B->D10, EN_C->D3; LED->D5; D4 spare (nc).

## New parts (LCSC codes verified 2026-11-19 as noted)
- TMAG5253BA3IQDMRR = C22401868 (Extended; JLCPCB/LCSC InStock; price from
  $0.6224 JLCPCB / $0.628 study 1+. Numeric stock: 1,126 at Stage 1
  (2026-11-19); re-observation at package time pending - fetched pages
  expose InStock but not the count in text; LCSC API is bot-blocked.)
- AP2112K-3.3TRG1 = C51118 (Diodes; SOT-23-5: 1=VIN 2=GND 3=EN 4=NC 5=VOUT;
  600mA, dropout 250mV typ @600mA; EN tied to VIN = always on).
- AO3401A = C15127 (AOS P-ch SOT-23: 1=G 2=S 3=D; JLCPCB Basic, tracker
  stock 1,563,623 on 2026-11-13 crawl).
- TYPE-C-31-M-12 = C165948 (project precedent: Main J1, issue-124 ledger;
  signal SMD 12 + shell PTH 4 + NPTH 2 - mid-mount, shell legs PTH).
- 100nF 0603 GRM188R71C104KA01D = C45000 (donor BOM).
- 10uF 0805 CL21A106KAYNNNE = C15850 (Samsung; Basic, stock 8,447,899).
- 10K 0603 0603WAF1002T5E = C25804 (UNI-ROYAL Basic). 5.1K = C23186
  (0603WAF5101T5E). 1K = C21190 (0603WAF1001T5E). 0R = C21189 (0603WAF0000T5E).
- LED green 0805 KT-0805G = C2297 (KENTO, Basic, InStock; Vf 2.6-3.1V).
- Battery connector: JST B2B-XH-A(LF)(SN), footprint = KiCad stock
  Connector_JST JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical. LCSC code NOT yet
  verified (LCSC search/API not fetchable from this environment) - resolve
  at package time or disclose.
