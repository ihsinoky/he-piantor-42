# Second opinion request: ADC_B escape on a saturated 4-layer PCB (KiCad)

You are an advisor. Deliverable: a concrete, verifiable ROUTE PROPOSAL (layers, waypoint coordinates, via sites) — do NOT edit the board.

## Board
- File: /home/hatch/workspace/projects/he-piantor-wmain-fix/.issue292-runtime/wmain-work.kicad_pcb (KiCad 9, 4 layers F/In1/In2/B; In1 is a pure GND plane — never route signals on it).
- Rules: 0.10mm track/clearance board-wide; 0.05mm clearance permitted inside the module fanout field rect (69.3,119.05)-(80.9,128.9) and the two FH12 fanout rects (70.93,107.10)-(81.97,117.89) and (118.03,107.10)-(129.07,117.89). Vias 0.6/0.3mm. All copper >=0.5mm inside the Edge.Cuts outline. Antenna keep-out rect (70.3,128.9)-(79.9,137.9) all layers. Trackpad keep-out circle centre (100,118) r20 on F/B (adopted copper exists inside; new tracks there are suspect).

## Problem
Net ADC_B is split: comp 1 = ONLY pad U1.46 (module pad, centre (73.15,121.15), 0.4x0.4, spans (72.95,120.95)-(73.35,121.35)). Comp 0 = CFB.1 + RFB.2 (east, x~124-125) with chains whose western frontiers are: In2 chain items around (85.2-86.7, 120.85-121.55) and (87.1,121.95)-(87.25,122.1), (88.3,122.5); F chains around (110.95-121.05, 127.45-133.15); vias at (110.2,121.8), (111.0,127.8), (123.7,119.0), (125.7,123.7). No B tracks in comp 0.

## Verified facts about the pad's neighbourhood (module pad map, centres)
- Pad row y=121.15: ADC_A (72.5), ADC_B (73.15), NC (73.8), ADC_C (74.45), VBAT_SENSE (75.1), NC (75.75), NC (76.4), NC (77.05), PAD_SDA (77.7); big GND pads (71.6,121.35) 0.8x0.8 and (78.6,121.35) 0.8x0.8.
- Staggered rows: y=121.8: BTN (72.83), NC (73.47), NC (74.12), NC (74.78), NC (75.42), NC (76.08), NC (76.72), PAD_EN (77.38). y=122.58: PAD_SCL (72.05), LED_DRV (72.83), NC (73.47), NC (74.12), NC (74.78), NC (75.42), NC (76.08), PAD_DR (76.72), NC (77.38), NC (78.15). y=123.22: MUX_A0 (72.05), NC (72.83), NC (73.47), NC (74.12), NC (74.78), NC (75.42), NC (76.08), NC (76.72), NC (77.38), VBAT_GATE_M (78.15). y=123.55: MUX_A1 (71.4), SYS_3V3 (78.8). y=124.0: NC (73.47), RESET_N (74.12), HALL_PWR_EN (74.78), MUX_EN0 (75.42), MUX_EN1 (76.08). More rows continue south to ~128.5.
- The F column x=73.15 south from the pad is FREE of pads (stagger) and of tracks down to y=123.60 (verified). At y 124.17-124.4, MUX_A2's F staircase occupies (73.0-73.6, 124.17-125.88) and dives SE to (74.53,125.88).
- F street between rows 123.22 and 124.0 is y 123.42-123.80; it is crossed by F feeds of RESET_N, HALL_PWR_EN, MUX_EN1 (diving north from row 124.0) and by SYS_3V3's F trunk. No via (0.6 disc) fits anywhere inside the pad field (stagger holes < 0.6mm) — vias only outside the field (x>80.9 or y>~128.9, but y>128.9 x 70.3-79.9 is the antenna keep-out).
- West of the pad: BTN's F track at x~72.85 (0.075 from pad). East: RESET_N's F picket x~73.5. The original (defective) design escaped west on B at y~123.1-123.8 to x=69.6 (outside the outline) — that corridor is now occupied by newer routes: USB_DP B run x~72.27 y 122.3-124.5, MUX_A0 In2 run (71.95,125.65)-(72.0,121.98), PAD_SCL F track (72.35,123.0)-(72.35,124.08).
- A 0.05-grid router (F/In2/B) and single-layer BFS on F both report NO PATH for ADC_B on the current board.
- In2 south-mid region: HALL_PWR_EN In2 vertical x=74.03 y 118.97-120.15; SYS_3V3 In2 run y=119.78 x 75.03-76.72; MUX_A2 In2 diagonal (76.75,119.38)-(77.95,120.58).

## Question
Propose a legal ADC_B connection from U1.46 to comp 0: exact layer sequence, waypoints (0.05mm grid), via sites. You may propose small moves of other nets' recently-placed stitches if you specify how that net stays connected. You may inspect the board file by parsing the .kicad_pcb s-expressions (pcbnew is NOT available in your sandbox). State the clearances you rely on. If impossible without moving a placed component, say so and name the cheapest move.
