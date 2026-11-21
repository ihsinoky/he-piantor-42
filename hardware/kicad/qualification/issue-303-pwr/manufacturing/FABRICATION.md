# Wireless power board (Issue #303) — fabrication and assembly note

**DRAFT / NOT FOR ORDER.** Stage 2 review package for Issue #303. No order,
charge or manufacturing release. Use only `../pwr.kicad_pcb` from this
Issue #303 directory with this note.
Board SHA-256:
`98e4e46ef5c73214937ef9c814f44a3410cec5d41c910d2a80719dc89c7e0c85`.
See `../REPORT.md` (Stage 2 section) for verification results.

## Board

- One **52.5 x 58.0 mm**, **two copper layer**, **0.8 mm finished thickness**
  board. The thickness is explicit and binding: the stackup stored in the
  board file is solder mask 0.01 + Cu 0.035 + FR4 core 0.71 + Cu 0.035 +
  solder mask 0.01 = **0.80 mm**. Do not substitute a 1.0/1.2 mm stackup —
  the board sits on the levelled battery-bay floor and the cell stack
  height budget (cover top vs the 22.00 mm keytop datum) assumes 0.8 mm.
- Coordinate frame for `CPL-jlcpcb.csv`: origin at the board **north-west
  corner**, X east, Y south — identical to the `.kicad_pcb` frame.
  Rotations are the KiCad placement angles.
- Copper: pours and tracks as drawn; narrowest routed track 0.5 mm,
  narrowest different-net copper gap 0.30 mm (zone carve at F1.1).
  Ordinary plated through vias, 4 sites, diameter 0.60 mm / drill 0.30 mm.
  No via-in-pad, no fill/cap processing.
- No mounting holes in this revision. Two 6 x 6 mm corner zones at the
  south-west and south-east corners (marked on Dwgs.User in the board
  file) are kept free of components and vias for the board fixing;
  **the fixing method itself is an open input** (case 3D stage decides
  screw vs clip; plain copper in the zones is intentional).

## PCBA (JLCPCB assembly, top side only)

Only two parts are machine-placed (`BOM-jlcpcb.csv` / `CPL-jlcpcb.csv`):

| Ref | Part | LCSC |
|---|---|---|
| F1 | Littelfuse 1206L050/24WR PTC resettable fuse, 24 V / 0.5 A hold | C2154056 |
| J1 | JST BM02B-GHS-TBT, GH 1.25 mm vertical SMT header, 2P | C161690 |

J1 pin 1 (west pad) = VBAT+ (fused, switched), pin 2 (east pad) = pack
negative / GND — matches the Main board JBATT pinout.

## Hand-fit (NOT in the PCBA BOM — fit by hand after PCBA)

| Qty | Part | Where |
|---|---|---|
| 3 | Keystone 209 leaf-spring battery contact | Negative cell ends: BT1 south, BT2 north, BT3 south — soldered to the 5.0 x 5.4 mm contact lands |
| 3 | Keystone 5231 button battery contact | Positive cell ends: BT1 north, BT2 south, BT3 north — soldered to the 5.0 x 5.4 mm contact lands |

Springs on every negative end and buttons on every positive end are also
the reverse-insertion keying: a cell only seats in the correct polarity.
Contact faces sit ±26.00 mm from each cell centre (IEC AA 50.5 mm +
contact working allowance, per the Stage 1 derivation).

## Off-board (NOT on this PCB at all)

| Part | Notes |
|---|---|
| Slide switch, SS-12D10 class (LCSC C5155552) | Mounted on the battery-bay east wall (case assembly Y −34.37, Z ≈ 8). Two wires solder to the J2 lands on this board (local (33.4, 52.3) = fused side, (33.4, 56.3) = output side); wire run ≈ 50 mm class: east to the wall, then north along the wall and up to the switch. |
| GH–GH cable to Main JBATT | JST GHR-02V-S housings + SSGH-002T-P0.2 crimp contacts (or pre-crimped GH leads), ≈ 100 mm class per the case Stage B route (≈ 86 mm + slack). Pin 1 = VBAT+, pin 2 = GND at both ends. |

## Assembly order (case integration)

The power board seats on the bay floor **before** the Wing boards are
fitted (the Wing underside clears the seated board and cells); service
removal is the reverse order. Cells load from above after the board and
contacts are in place.

## Test points

TP1 (east edge, on the return pour) = pack positive **before** the PTC
(PACK_POS_RAW); TP2 (south-west) = pack negative (PACK_NEG). A tripped
PTC therefore cannot mask a pack reading.
