# TC2050 official footprint — provenance and extracted geometry

Primary source (maker's own published spec):
- Tag-Connect datasheet TC2050-IDC-NL, DWG TC2050-IDC-NL-FP
  "FOOTPRINT FOR TC2050-IDC-NL PLUG OF NAILS(TM) CABLE", REV A,
  dated 12/2/10, sheets 1-3. Downloaded 2026-11-20 from
  tag-connect.com:
  https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2050-IDC-NL_Datasheet_8.pdf
  (local copy: TC2050-IDC-NL_Datasheet_official.pdf, 3 pages;
  rendered page-1..3.png)

Sheet 1 (footprint drawing, PCB TOP LAYER view) states:
- Conductive contact pads: D.0310" +/- .0030 = D0.787 mm +/- .076,
  NO SOLDER PASTE (note 3: eliminate any hole in the paste mask).
- Alignment pin holes: D.0390" +/- .0030 = D0.991 mm +/- .076,
  NON-PLATED THRU HOLE, 3 places.
- Dimensions: .0500 (1.2700 mm) pad pitch; .0250 (.6350 mm) row
  offset from field centreline; .3000 (7.6200 mm) between the
  west hole centreline and the east holes' centreline;
  .0400 (1.0150 mm) east-hole offset (see cross-check below).
- Pad numbering on the drawing: bottom row (as printed) 1..5
  left to right; top row 10..6 left to right (pad 10 opposite
  pad 1). West alignment hole on the rows' centreline; two east
  alignment holes, one above the top row, one below the bottom
  row, both on the +3.81 mm centreline.
- Note 1: no tracks or vias in the shaded "KEEP OUT" AREA (the
  rectangle between the pad rows). Note 2: no other track or
  signal within 0.020" (0.508 mm) of any contact pad.
- Note 4: specify "DNL" in the BOM (do-not-load marker class).

Sheet 2 (cable drawing TC2050-IDC-NL, REV A):
- Tool end = "END VIEW 2x5 .1" IDC CONNECTOR" — the PLAIN
  TC2050-IDC-NL terminates in a 0.1" (2.54 mm) 2x5 IDC, NOT the
  DK's 10-pin 1.27 mm Cortex header. The DK-mating member of the
  family is TC2050-IDC-NL-050-ALL (1.27 mm Cortex end); both are
  wired straight through, plug pin n <-> connector pin n, so the
  board-side mapping is identical. (Study E.2's table conflated
  the two variants; the respin record corrects it.)
- Plug end view numbering matches sheet 1 (1..5 / 10..6 rows,
  alignment pins at the two outer positions).

Cross-check (independent machine-readable implementation):
- KiCad footprint library, Connector.pretty,
  Tag-Connect_TC2050-IDC-NL_2x05_P1.27mm_Vertical.kicad_mod
  (local copy: Tag-Connect_TC2050-IDC-NL.kicad_mod), which
  implements the Tag-Connect drawing. Its geometry agrees with
  every dimension readable on sheet 1:
  pads D0.7874 at x = -2.54,-1.27,0,1.27,2.54, rows y = +/-0.635;
  numbering 1..5 on y=+0.635, 10..6 on y=-0.635 (KiCad +Y = the
  drawing's downward direction, so placed at rotation 0 the
  footprint reproduces the drawing's top view exactly);
  NPTH D0.9906 at (-3.81, 0), (+3.81, +1.016), (+3.81, -1.016)
  — the +1.016/-1.016 offsets are the drawing's .0400 (1.0150 mm)
  dimension (0.001 mm rounding in the drawing's mm conversion).
  Max disagreement vs the drawing: 0.001 mm (rounding only).

Adopted local geometry (footprint-local, mm, origin = field
centre, KiCad convention +Y south):
  pads (D0.7874, F.Cu + F.Mask, NO paste):
    1 (-2.54, +0.635)   2 (-1.27, +0.635)   3 (0, +0.635)
    4 (+1.27, +0.635)   5 (+2.54, +0.635)
    6 (+2.54, -0.635)   7 (+1.27, -0.635)   8 (0, -0.635)
    9 (-1.27, -0.635)  10 (-2.54, -0.635)
  NPTH (D0.9906 drill, no copper):
    (-3.81, 0), (+3.81, +1.016), (+3.81, -1.016)

Signal mapping (pad n = Cortex 10-pin debug pin n; the cable is
straight-through pin-for-pin, Debug Store TC2050-IDC-050-ALL
pinout table + sheet-2 end views):
  1 VTref -> SYS_3V3 | 2 SWDIO -> SWDIO | 3 GND -> GND
  4 SWCLK -> SWDCLK  | 5 GND -> GND     | 6 SWO -> NC (no SWO
  net exists; study E.3: SWO pad may stay NC)
  7 KEY -> NC (Cortex key pin, no signal)
  8 TDI -> NC (JTAG not used; design is SWD-only)
  9 GNDDetect -> GND (study E.3: GNDDET ties to GND)
  10 nRESET -> RESET_N
