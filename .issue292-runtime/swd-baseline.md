# SWD TC2050 respin — baseline gates (Stage 1)

Board: tree wmain.kicad_pcb, SHA-256
260726192947a0903e6e3a9268877f3b77868542bcaec29d4777eaa49f9b0689
(= edge-fixed D-058 board, unmodified). Re-run 2026-11-20 by this
worker, same board file the margin round used.

- Containment (checks/copper_containment.py): **PASS**, zero
  crossings/touchings. Log: swd-baseline-containment.txt.
- ERC (kicad-cli sch erc, JSON): **0 violations**. swd-baseline-erc.json.
- DRC (project drc2.sh: zone refill + kicad-cli pcb drc JSON,
  severity-all): **704 violations + 2 unconnected**.
  Full list: swdbase-drc2.json (this is THE baseline for the
  respin delta — same tool/settings before and after).

## Reconciliation vs the recorded "702 violations / 2 unconnected"

The margin round's baseline-drc-counts.txt (from baseline-drc.rpt,
as-saved board, report format) totals 702 + 2 unconnected_items.
Class-by-class, my JSON run matches the recorded counts in every
class except exactly two method deltas:
- lib_footprint_issues +1: "configuration does not include the
  footprint library 'wmain'" attached to U1 — a harness artifact
  of running DRC in the drcwork dir without the fp-lib-table;
  not a board property. Appears identically after the edit, so
  it cancels in the delta.
- hole_clearance +1 (97 vs 96): the drc2.sh run refills zones
  before DRC; the recorded .rpt ran on the board as saved. One
  hole-clearance pair is refill-sensitive. Both my runs use the
  refill method, so the delta stays attributable.
All other 15 classes identical (clearance 502, track_dangling 36,
copper_edge_clearance 17, silk_over_copper 14, via_dangling 11,
hole_to_hole 5, silk_edge_clearance 4, via_diameter 3,
solder_mask_bridge 3, holes_co_located 3, annular_width 3,
silk_overlap 2, items_not_allowed 2, drill_out_of_range 1).

## The 2 unconnected items (must remain exactly these)

1. CVCC2 pad 2 [GND] (71.8, 117.775) <-> GND track (71.6, 121.35)
   — module GND U1.7 area (REPORT deviation 13).
2. GND track (74.45, 124.65) <-> GND track (75.75, 124.65)
   — module GND pads U1.14/U1.16 (REPORT deviation 13).

## SWD-area baseline items (context for the delta)

- hole_clearance: SWDCLK track (79.5, 123.05) vs SWDIO via —
  actual 0.2243 vs 0.2500. This is at the MODULE end of the SWD
  escapes (inside the fine field), present in both records; the
  respin does not touch it.
- The JSWD field's own 4 escapes (SYS_3V3/SWDIO/SWDCLK/RESET_N)
  leave the field southward; they will be re-escaped to the new
  TC2050 pads. Any baseline violation attached to those specific
  track segments may legitimately disappear; the Stage-5 diff
  itemises every change.
