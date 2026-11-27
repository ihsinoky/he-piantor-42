# Wireless power board (Issue #303) — fabrication and assembly note

**DRAFT / NOT FOR ORDER.** Stage 2 fixing-revision review package for Issue
#303. No order, charge or manufacturing release. Use only
`../pwr.kicad_pcb` from this Issue #303 directory with this note.
Board SHA-256:
`8b5ca19f8bfbb3b30a448bbe20b062a02650f4ca32e7f1c74cb00c7b4548427a`.
See `../REPORT.md` (Stage 2 revision section) for verification results.

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
- Copper: pours and tracks as drawn; narrowest routed track 0.5 mm, all
  copper respects the 0.20 mm design clearance (DRC 0 violations).
  Ordinary plated through vias, 4 sites, diameter 0.60 mm / drill 0.30 mm.
  No via-in-pad, no fill/cap processing.

## Board fixing (case 3D stage, Issue #296 — DECIDED, no screws)

The bay floor slab is only 2.0 mm thick, so no screws. The board is held
by the case, in three features:

- **3 case fins through board slots.** The fins are the Keystone 209 lands
  at the three spring (negative) cell ends — one feature, two functions.
  Fin 1.65 thick, cell-side face on the contact plane (±26.00 mm from the
  cell centres), top Z 10.5. Slots in Edge.Cuts (board-local):
  - South W: X 3.75..19.75, Y 53.50..56.15 (BT1− fin)
  - South E: X 32.75..48.75, Y 53.50..56.15 (BT3− fin)
  - North: X 17.75..34.75, from the north edge to Y 2.50 — an **open
    notch**; the BT2− fin enters it on the vertical drop.
  The slots interrupt copper by design: the negative-end lands are
  trimmed to 5.0 x 2.95 mm ear lands ending 0.25 mm clear of the slot
  edges, and the series routing runs around the slots (see REPORT.md).
- **4 snap tongues** on the E/W wall inner faces press the board's top
  edge strips (0.5 mm working overlap). The strips — X 0..0.5 and
  52.0..52.5, Y 9.37..15.37 and 39.37..45.37 (marked on Dwgs.User) — are
  free of components and vias.
- **North wall datum face**: the board's north edge registers on the bay
  north inner face.

The south-west / south-east 6 x 6 mm corner fixing zones of Stage 2 are
**retired** — superseded by the fin + tongue scheme.

## Gerbers

`gerbers/` is generated from the board file above (kicad-cli): F.Cu,
B.Cu, F.Mask, B.Mask, F.Silkscreen, B.Silkscreen, F.Paste, B.Paste,
Edge.Cuts, `pwr.drl` (Excellon), `pwr-job.gbrjob`.

## PCBA (JLCPCB assembly, top side only)

Only two parts are machine-placed (`BOM-jlcpcb.csv` / `CPL-jlcpcb.csv`):

| Ref | Part | LCSC |
|---|---|---|
| F1 | Littelfuse 1206L050/24WR PTC resettable fuse, 24 V / 0.5 A hold | C2154056 |
| J1 | JST BM02B-GHS-TBT, GH 1.25 mm vertical SMT header, 2P | C161690 |

F1 sits at local (7.85, 57.17), rotation 0. J1 sits at local
(26.25, 56.9), rotation 0 — inside the south-edge free band
(case X −6.5..+6.5). J1 pin 1 (west pad) = VBAT+ (fused, switched),
pin 2 (east pad) = pack negative / GND — matches the Main board
JBATT pinout.

**DFM watch item:** F1's lands are 1.1 x 1.2 mm (shrunk in Y so the
pads stay clear of the west fin slot and the board edge); the 1206
chip overhangs the lands 0.2 mm/side in Y. Inspect the first assembled
board's F1 solder joints.

## Hand-fit (NOT in the PCBA BOM — fit by hand after PCBA)

| Qty | Part | Where |
|---|---|---|
| 3 | Keystone 209 leaf-spring battery contact | Negative cell ends: BT1 south, BT2 north, BT3 south — fitted to the case fin (the fin is the 209 land; its cell-side face is the contact plane) and the leaf's tail soldered to the board's 5.0 x 2.95 mm ear land beside the slot |
| 3 | Keystone 5231 button battery contact | Positive cell ends: BT1 north, BT2 south, BT3 north — soldered to the 5.0 x 5.4 mm contact lands |

Springs on every negative end and buttons on every positive end are also
the reverse-insertion keying: a cell only seats in the correct polarity.
Contact faces sit ±26.00 mm from each cell centre (IEC AA 50.5 mm +
contact working allowance, per the Stage 1 derivation).

## Off-board (NOT on this PCB at all)

| Part | Notes |
|---|---|
| Slide switch, SS-12D10 class (LCSC C5155552) | Mounted on the battery-bay **south wall inner face** (case centre X 0, pads Z 2.2..8.8, actuator ≈ Z 5.4). Two wires solder to the J2 lands on this board (local (18.2, 57.075) = fused side, (22.2, 57.075) = output side); wire run ≈ 15 mm class — a short hop south to the wall. Supersedes the Stage 2 ≈ 50 mm east-wall estimate. |
| GH–GH cable to Main JBATT | JST GHR-02V-S housings + SSGH-002T-P0.2 crimp contacts (or pre-crimped GH leads), ≈ 100 mm class per the case Stage B route (straight-line 73.9 mm from the relocated J1 at case (0, −5.47) to Main JBATT at case (+24.0, +64.50), + slack). Pin 1 = VBAT+, pin 2 = GND at both ends. |

## Assembly order (case integration)

The power board seats on the bay floor **before** the Wing boards are
fitted (the Wing underside clears the seated board and cells); service
removal is the reverse order. Cells load from above after the board and
contacts are in place.

## Test points

TP1 (east edge, on the return pour) = pack positive **before** the PTC
(PACK_POS_RAW); TP2 (south-west) = pack negative (PACK_NEG). A tripped
PTC therefore cannot mask a pack reading.
