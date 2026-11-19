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

## S3a first attempt - COLLISION (reverted)
escapes_005.json (12 interior) and escapes.json (12 perimeter) were
computed in separate A* runs; applied together their box-edge vias
collide (ADC_A via (72.7,119.35) vs BTN via (72.85,119.35) etc.):
DRC showed 24 shorting_items, unconnected 41->31 (s3a-drc.json).
Fix: ONE unified escape run, all 24 nets, obstacle growth across
nets; GND taps re-planned afterwards. Tree board restored to the
S1+S2 state (FP swap + rule area) before the unified run.

## S3b outcome (final)
- Connected this round: all 12 interior nets, all perimeter module nets, USB_DP (B, corrected pad model), ADC_C (B south lane), RESET_N (east column x112.9), SYS_3V3 CVCC2-CVCC1 pair.
- Key fixes: pad-rotation sign error in the A* obstacle model (J2/J3 FH12 pads 0.3x1.3 @43deg were mirrored) - explained most late-stage "walls" and grazes; same-process route invisibility in batch mergers explained cross-net shorts (fixed by per-net fresh processes).
- RESIDUAL unconnected = 6 items / 5 nets (DRC curr10): GND pads 14+16 isolated pair (bridge to pad 18 chain blocked by VBAT_SENSE stub crossing; via taps illegal in the NC ring); VBUS (comp0 via (88,119.5) vs USB-side B track - w0.3 band y110-120 sealed on F/I2/B); SYS_3V3 x2 (CVCC island vs main network, and CVCC island vs module escape comp - B-end row + field congestion at w0.3, also fails at 0.15); PAD_EN (escape via trapped on B, F south corridor sealed); VBAT_SENSE (B pocket vs I2 far track, band y112-119 sealed).
- No sub-design-width tracks were drawn for the residuals (all relaxation attempts failed and were not committed); VBUS/SYS_3V3 drawn legs are all at 0.3mm.
- Shorts = 0 (DRC severity-all, zone-filled).
