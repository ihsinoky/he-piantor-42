# Re-route round notes (Issue #292, D-057)

## S0 baseline (working copy wmain-v28-fp.kicad_pcb, SHA b7629fe9...)
- tracks 855, vias 187, zones 21; U1 official FP, 78 pads, centre
  (75.1, 124.85), rot 0deg; tracks fully inside module 24mm box: 10
  (module field effectively unrouted).
- DRC severity-all (kicad-cli): 112 violations; unconnected_items 41.
  Top types: copper_edge_clearance 36, hole_clearance 18,
  track_dangling 18, silk_over_copper 13, via_dangling 9.
  (baseline-s0-drc.json, baseline_s0.py)

## S1 tree-board swap verification
- compare_boards.py: footprint diffs tree-vs-work = U1 ONLY
  (69 pads rot 90 -> 78 pads rot 0). Zones identical, Edge.Cuts
  identical (14 segments).
- 21 tracks present in tree but absent in work: ALL are U1 nets
  (ADC_A/B/C, HALL_PWR_EN, LED_DRV, MUX_A0/A1/A2, MUX_EN0/1,
  PAD_EN, PAD_SCL, PAD_SDA, RESET_N, SWDCLK, SWDIO, SYS_3V3,
  VBAT_GATE_M, VBAT_SENSE) -> the work copy is exactly
  tree-minus-module-routing; adopting it == swapping the FP in the
  tree board + ripping the module field.
- verify_padnet.py (tree=old, work=new): assignment diffs = pads
  70-78 only (added, no net). All 11 spot checks vs DS1807 OK.
  NC pads 65-78 carry no net.
- Action taken: preswap tree board backed up to
  wmain-tree-preswap-derived.kicad_pcb; work copy installed as
  the tree board wmain.kicad_pcb.
