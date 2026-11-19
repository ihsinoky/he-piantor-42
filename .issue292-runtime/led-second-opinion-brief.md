# Second opinion request: LED_DRV reconnection on a saturated 4-layer PCB (KiCad)

You are an advisor. Deliverable: a concrete, verifiable ROUTE PROPOSAL (layers, waypoint coordinates, via sites) — do NOT edit the board.

## Board
- File: /home/hatch/workspace/projects/he-piantor-wmain-fix/.issue292-runtime/wmain-work.kicad_pcb (KiCad 9, 4 layers F/In1/In2/B; In1 is a pure GND plane — never route signals on it).
- Design rules: 0.10mm track/clearance board-wide; inside the module fanout field rect (69.3,119.05)-(80.9,128.9) and the two FH12 fanout rects, 0.05mm clearance is permitted. Vias 0.6/0.3mm. Copper must stay >=0.5mm inside the Edge.Cuts outline (hard rule of this round).

## Problem
Net LED_DRV is split into 2 components:
- Comp A (module side): pad U1.56 (71.85-72.25, 122.67-123.07 approx), an F fanout, a via at (70.50,118.00), an In2 mesh: vertical segment x=70.45, y 119.15-120.80; short segments around (69.95-70.5, 120.75-121.73); plus a NEW In2 chain I placed: (70.45,119.35)->(70.45,116.40)->(72.00,113.90), ending dangling at (72.00,113.90).
- Comp B (load side): RLED.1 and an In2 chain whose western items are: diagonal (73.75,115.25)->(76.90,112.10) w0.10; a stub (73.7,115.2)-(73.8,115.9); chain along y~111.25 x 76.9-82.15; diagonal (82.05,106.0)-(87.35,111.3); vias at (97.3,104.7),(97.3,100.3),(98.9,95.0),(99.0,96.3) with F/In2 chains x~97-99, y 83-105.

## Why it is hard (all verified geometrically this round)
- The direct In2 diagonal (70.45,119.15)->(73.75,115.85) existed in the original design but now conflicts with a MUX_A0 In2 bridge I placed: segments (71.20,117.76)->(71.35,119.20)->(71.10,119.95)->(70.92,120.30). A0 is complete and must not be broken.
- The In2 band x 71-77, y 111-120 is a braid of completed nets' chains (MUX_A0/A1/A2, USB_DM, PAD_SCL, ADC_A via at (70.9,119.35), ADC_C wall x 72.35-73.05 y 118.85-125, CVCC2 pad (71.33-72.27,119.02-119.83) on F).
- B layer in the same band carries A0/A1/MUX_OUT trunks (y~113.1-113.55, x 74.3-95.4), A0 B diagonal (71.52,114.96)-(73.53,116.96), USB_DM B via (73.6,126.8), ADC_C B staircase.
- F layer: J2 FH12 fanout pickets fill (70.93,107.10)-(81.97,117.89); module NC pads at x 71.2-71.6, several y rows; a GND via shape (71.33-72.27,117.38-118.18).
- A grid router (0.05mm grid, F/In2/B, 0.05/0.10 passes) and a single-layer BFS both report NO PATH for LED_DRV on the current board. Via sites in the west pocket are essentially zero (verified by exhaustive probe).
- Antenna keep-out: rect (70.3,128.9)-(79.9,137.9) all layers. Trackpad keep-out: circle centre (100,118) r20 on F/B (existing adopted copper sits inside it; treat new tracks there as suspect).

## Question
Propose a legal LED_DRV connection: exact layer sequence, waypoint coordinates (0.05mm grid), via sites if any. You may propose small moves of OTHER nets' recently-placed stitches (USB_DM / MUX_A0 / PAD_SCL micro-segments in the band) if you also specify how that net stays connected. You may inspect the board file with python (pcbnew is NOT available in your sandbox; parse the .kicad_pcb s-expressions or use the geometry dumps in .issue292-runtime/: edge-work7.json, west-nets.json). State clearances you rely on. If you conclude it is impossible without moving a placed component or a module pad, say so explicitly and name the cheapest such move.
