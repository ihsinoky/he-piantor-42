# Issue #303 — wireless power board, Stage 1 design note (circuit design)

Status: Stage 1 complete. Schematic `hardware/kicad/qualification/issue-303-pwr/pwr.kicad_sch`,
**ERC 0 violations** (`.issue303-runtime/erc.json`). **No board layout** — outline and
placement wait for the Wing redesign δ (Issue #299) and case geometry (Issue #296 Stage B).
Footprints in `pwr.pretty` are Stage 1 placeholders carrying the contact-field geometry;
Stage 2 refines them.

## Cell datum

- Cell: AA NiMH, eneloop-class BK-3MCD (D-048/D-062). Dimensional datum = IEC 60086 AA
  envelope: **length max 50.5 mm, diameter max 14.5 mm** (the values the centre study used).
- Allowances (centre study, same set as D-062): cell pitch **15.0 mm** E-W (0.5 mm between
  cells), axial contact allowance **0.75 mm/end**, case wall allowance 2.0 mm.
- Derived contact field (board-local frame, origin at block centre, +x east, +y south):
  cell centres at x = −15 / 0 / +15; contact faces at **±26.00 mm** from each cell centre
  along the axis (50.5/2 + 0.75). Reconstructed block envelope = **48.5 × 56.0 mm** —
  exactly the D-062 study envelope (independent recomputation, `topology_check.py`).

## Series topology — proof

Orientation alternates so both bridges are short end-row links (centre study §7, 3-cell):

| Contact | Position (x, y) | Cell terminal | Contact part | Net |
|---|---|---|---|---|
| BT1 north | (−15, −26) | cell 1 (west) **+** | button (positive) | BRIDGE_N |
| BT1 south | (−15, +26) | cell 1 **−** | leaf spring 209 | PACK_NEG |
| BT2 north | (0, −26) | cell 2 (mid) **−** | leaf spring 209 | BRIDGE_N |
| BT2 south | (0, +26) | cell 2 **+** | button (positive) | BRIDGE_S |
| BT3 north | (+15, −26) | cell 3 (east) **+** | button (positive) | PACK_POS_RAW |
| BT3 south | (+15, +26) | cell 3 **−** | leaf spring 209 | BRIDGE_S |

- **Bridge B1 (north row)** joins BT1+ ↔ BT2− = net BRIDGE_N. **Bridge B2 (south row)**
  joins BT2+ ↔ BT3− = net BRIDGE_S. Both bridges are plain copper on the floor board.
- **Return pour:** pack + is BT3+ at the north-east; the PACK_POS_RAW pour runs down the
  board's east edge to the south side, where F1/J2/J1 sit — both pack terminals exit south
  toward Main, as D-062 requires. Pack − (BT1−) is already at the south-west.
- Series path (machine-checked by parsing the schematic file, `.issue303-runtime/topology_check.py`,
  output in `topology.json`): J1.2 → BT1 → BRIDGE_N → BT2 → BRIDGE_S → BT3 → PACK_POS_RAW →
  F1 (PTC) → PACK_POS_FUSED → J2 (switch loop) → VBAT_OUT → J1.1. Each cell is traversed
  exactly once; **no net touches both terminals of any cell** (the shorted-cell failure mode
  is excluded by construction and by the check).
- Springs sit on **all three negative ends**, buttons on **all three positive ends**
  (standard practice; also the keying geometry — see parts).

## Circuit (as drawn)

PACK+ path: BT3+ → F1 PTC → J2 switch loop → J1.1 (VBAT_OUT). PACK− path: BT1− → J1.2.
TP1/TP2 = test pads on PACK_POS_RAW / PACK_NEG (raw pack voltage, measurable with cells
inserted and the switch open — included because they cost two pads and are the only
assembly/QC measurement point on a board with no other electronics; they sit before the
PTC, so a tripped PTC cannot mask a pack reading).

## Parts & availability (observed 2026-11-21, web listings — re-verify at order)

| Ref | Part | Source / stock observed | LCSC | Disposition |
|---|---|---|---|---|
| BT− ×3 | Keystone **209** leaf-spring contact, AA, spring steel Ni-plate, snap-on (clips onto 1.52–1.78 mm wall), solder ear | DigiKey 36-209-ND; Newark 95F3294; element14 908708 (5-pack); TME KEYS209 ≈1,671 pcs (crawl); distributor aggregator 7,500 pcs | none | **Hand-fit / mechanical.** Not PCBA. |
| BT+ ×3 | Keystone **5231** button contact, positive, with solder tab, AA (recessed button = the D-059 "location facility") | distributor aggregator 15,000 pcs (crawl) | none | **Hand-fit / mechanical.** Not PCBA. |
| F1 | Littelfuse **1206L050/24WR** PTC, 1206, Ih 0.5 A / Itrip 1 A / Vmax 24 V, Ri ≥0.15 Ω | LCSC **C2154056: 5,430 in stock** (crawl 2026-11-18), $0.26 @5 | C2154056 | **PCBA-capable** (SMT 1206) or hand-solder. |
| J1 | JST **BM02B-GHS-TBT** (GH 1.25 mm 2P, vertical SMT) — same part as Main's JBATT | project record: LCSC **C161690** (Main BOM, #292) | C161690 | **PCBA-capable** or hand-solder. |
| cable | JST GHR-02V-S housings ×2 + SSGH-002T-P0.2 crimp pins (GH–GH, ~100 mm, straight) | standard JST GH cable parts | — | Hand-assembled cable. Pinout straight: pin1↔pin1 (+), pin2↔pin2 (−); Main JBATT pin1 = VBAT+, pin2 = GND (verified from the adopted Main schematic). |
| SW1 (off-board) | **SS-12D10 class** slide switch, SPST/SPDT, rated **DC 50 V / 0.5 A** (class rating; e.g. G-Switch SS-12D10-G090) | LCSC **C5155552: 1,775 in stock** (crawl), $0.36 @5 | C5155552 | **Hand-fit, off-board** (bay wall). C&K OS102011MA1QN1 (0.1 A) NOT used — undersized. |

Notes: the switch's 0.5 A rating is the class floor set by the brief; the protected rail
behind it is PTC-limited to 0.5 A hold, and the product load (TPS63070 input from a 3.6 V
pack) is far below that in normal operation, so rating and protection are consistent.
PTC resistance (Ri min 0.15 Ω, post-trip R1 max 0.75 Ω) drops ≤ ~30 mV at a 200 mA-class
load — inside the Main power tree's existing budget class; no change on Main.

## Recommendations (Stage 1 study points)

1. **Switch: OFF-BOARD (bay wall), wired into the J2 loop.** Reasons: (a) the floor board
   lies under the cells — a board-mounted switch would be unreachable without removing
   cells, and its ~4–5 mm height would break the thin stack (0.8 board + Ø14.5 cell =
   15.3 mm is the D-059/D-062 stack); (b) switch position is a case-design output
   (Issue #296), not yet fixed — J2 pads decouple the board from that decision;
   (c) true 0-current OFF is preserved (series in the + leg, after the PTC).
   Bench/QC use: short J2 with a jumper link. The switch itself is a hand-fit case part.
2. **Output termination: GH connector on this board (J1 = BM02B-GHS-TBT), GH–GH cable.**
   Reasons: (a) identical part and pinout to Main's JBATT → one cable type, keyed at both
   ends, no soldered cable to fatigue or mis-wire; (b) the pack/board stays removable for
   service (freedom priority) — solder pads would tie the ~100 mm cable to the board;
   (c) cost delta is one connector (~the Main BOM line) against a real assembly-error
   risk. Solder pads remain the fallback if Stage 2 finds the connector height (2.9 mm
   class at the board's south edge, outside the cell field) impossible — it is not
   expected to bind, since J1 sits south of the cell block, clear of the cells.
3. **Test points: included** (TP1/TP2, see circuit note above).

## Stage 2 (layout) inputs needed — exact list

From Issue #299 (Wing redesign) / Issue #296 (case):
1. Proven δ (Wing separation) → final case outline and **bay inner width/depth** available
   to this board (block needs 48.5 × 56.0 + contact/board margins).
2. **Levelled bay floor Z** (D-062: floor at case Z −0.65 after levelling) and the board
   fixing method/positions in the floor.
3. **Cable exit position**: J1's position on the south edge relative to Main's JBATT
   (asm (+24.0, +67.9) in the centre study frame) so the ~100 mm GH–GH cable routes
   without crossing the FFC channel stack.
4. **Switch position on the bay wall** (case output) → J2 wire length/routing; if the case
   instead lands the switch on the block's south wall, J2 pad position follows it.
5. Contact retention detail: Keystone 209 clips need a **1.52–1.78 mm wall** — the case
   end walls (or a board-edge doubler) must present that thickness at the 6 contact sites;
   the 5231 button's solder tab lands on the board pads shown in the placeholder footprint.
   Keying verification (reversed cell cannot make contact) is a Stage 2 fit check with
   real contacts and a real cell.
6. Board thickness confirmation (0.8 mm per D-059 construction (a)) and whether F1/J1 go
   PCBA or hand-solder in the order configuration.

## Stage 2 (layout) — addendum, 2026-11-21

**Status: COMPLETE (draft, not for order).** Released by the PO's 2D approval of
the case package at δ=9.5 + Wing corner trim (Issue #296, 2026-11-21). Board:
`pwr.kicad_pcb`, SHA-256
`98e4e46ef5c73214937ef9c814f44a3410cec5d41c910d2a80719dc89c7e0c85`.
Build/check tooling: `.issue303-runtime/build_board.py`, `board_check.py`.

### Stage 1 input list — disposition

1. Bay geometry (δ proven): CONSUMED from case Stage B — cavity 56.5 × 60.0,
   board 52.5 × 58.0 on the north datum face, floor levelled at case Z −0.65.
2. Fixing method: **STILL OPEN — the one open input.** Issue #296's comments
   carry no fixing decision yet (checked 2026-11-21). Per the brief, two
   6 × 6 mm corner zones (SW local (0..6, 52..58), SE local (46.5..52.5,
   52..58)) are kept free of components and vias (plain copper only, marked
   on Dwgs.User) so either a screw or a clip fits when the case 3D stage
   decides.
3. Cable exit: CONSUMED — J1 centre at assembly (+17.25, −5.47); Stage B's
   route start was X +17, so the GH–GH route (≈86 mm + slack, ≈100 mm class)
   is unchanged.
4. Switch position: CONSUMED — bay east wall, asm Y −34.37, Z ≈ 8. J2 sits at
   local (33.4, 54.3) (asm (+7.15, −8.07)). **Deviation:** the as-built wire
   run is ≈50 mm class (east to the wall, north along it, up to the switch),
   not Stage B's ≈35 mm estimate — J2 cannot sit further east/south: BT3's
   south contact pad and the SE fixing zone bound that corner.
5. Contact retention (1.52–1.78 mm wall at the six sites): case-side
   requirement, unchanged; the fit/keying check with real contacts and a
   real cell remains a build-time check.
6. Thickness / PCBA split: CONSUMED — 0.8 mm (stackup stored in the board
   file: 0.01 mask / 0.035 Cu / 0.71 core / 0.035 Cu / 0.01 mask); F1 + J1
   are PCBA, contacts hand-fit, switch off-board.

### Layout as built (board-local: origin NW corner, X east, Y south)

- Cells: centres (11.25/26.25/41.25, 28.0), pitch 15.0, alternating
  orientation (BT1 N+, BT2 S+, BT3 N+). Contact pads 5.0 × 5.4 at ±25.0 from
  centres; every pad's span covers its ±26.00 contact-face line (checker).
- Pours (F.Cu): BRIDGE_N north strip; BRIDGE_S stepped south pour with a
  notch (X 29.1..38.4 below Y 53.6) that houses F1 clear of the pour;
  PACK_POS_RAW east-edge return pour, extending south to Y 54.0 inside the
  SE fixing zone as plain copper (allowed there; no parts/vias).
- East edge strip stays flat per the Z-check (physical FH12 clears the
  board top by 2.55 mm): pour + TP1 only; the checker proves no other pad
  and no via in the tab column (X ≥ 48.75, Y 17.4..53.7).
- F1 at (36.6, 55.9) rot 180 in the BRIDGE_S notch; J2 at (33.4, 54.3);
  J1 at (43.5, 56.9), pin 1 west = VBAT+, pin 2 east = PACK_NEG.
- Feeds: PACK_POS_RAW pour → via (48.0, 50.6) → B.Cu → via (36.9, 53.6) →
  F1.1; PACK_NEG BT1.2 → via (15.5, 53.0) → B.Cu south run → via (45.9, 54.6)
  → J1.2; PACK_POS_FUSED and VBAT_OUT routed on F.Cu in the south band.
- J1 housing vs SE fixing zone: pads/vias are checker-proven clear; the GH
  housing (body ≈5.7 mm wide class, centred X 43.5) reaches ≈46.35 < 46.5,
  so the body also clears the zone — from the connector class dimension,
  not a measured courtyard; confirm when the fixing decision lands.

### Verification (as-saved files, restored Stage 1 project file)

- ERC 0 violations (schematic unchanged from Stage 1).
- DRC **0 violations / 0 unconnected pads / 0 footprint errors**
  (kicad-cli, `.issue303-runtime/drc-s2.rpt`).
- Board checker (`.issue303-runtime/board_check.py`, loads the routed
  `.kicad_pcb` as saved): **83 PASS / 0 FAIL** — pad→net map equals the
  Stage 1 topology; series walk J1.2 → BT1 → BT2 → BT3 → F1 → J2 → J1.1
  traverses each cell exactly once with net order PACK_NEG, BRIDGE_N,
  BRIDGE_S, PACK_POS_RAW, PACK_POS_FUSED, VBAT_OUT; no net on both
  terminals of any cell; outline exactly 52.5 × 58.0; contact-face
  coverage; fixing zones and tab column clear; all three pours carry
  stored fill.
- **DRC caught a real defect in the first layout pass:** F1.1 overlapped
  BT3's south contact pad by a 0.05 mm sliver (a BRIDGE_S↔PACK_POS_RAW
  short). F1 moved west (37.3 → 36.6) and J2 west (34.0 → 33.4); narrowest
  remaining different-net gap is 0.30 mm (zone carve at F1.1). The same
  pass exposed a 0.05 mm graze where the PACK_POS_RAW stub met F1.1 —
  DRC called it connected, but the stub now lands on the pad centre.
- Process note: the pcbnew save cycle rewrote `pwr.kicad_pro` (rule
  minimums reset to defaults; the unused template "Power" netclass and its
  patterns dropped). The Stage 1 `.kicad_pro` was restored verbatim from
  git and the final ERC/DRC above ran against that restored pair, so the
  verified state is exactly what is committed.

## Stage 2 fixing revision — addendum, 2026-11-21

The case 3D stage (Issue #296, comment 7058037232 and
`.issue296-runtime/case-3d.md`) decided the board fixing. This revision
folds it into the layout; the Stage 2 open input is closed.

### Coordinate transform

Case assembly frame ↔ board-local (origin NW corner, X east, Y south):

    local X = case X + 26.25
    local Y = case Y + 62.37

(the board datum is the bay north inner face, case Y −62.37; the board
west edge sits at case X −26.25). Anchors checked: cell centres case
(−15/0/+15, −34.37) → local (11.25/26.25/41.25, 28.00); contact-face
lines case Y −8.37 / −60.37 → local Y 54.00 / 2.00; Stage 2's J1 at
local (43.5, 56.9) → case (17.25, −5.47), matching Stage 1's nominal
case position (17, −4.37) once the GH housing centre offset is counted.

### What changed

- **Fin slots in Edge.Cuts** (case fins pass through; the fins are the
  Keystone 209 lands): S-W rect local X 3.75..19.75, Y 53.50..56.15;
  S-E rect X 32.75..48.75, Y 53.50..56.15; north slot executed as an
  **open notch** X 17.75..34.75, north edge to Y 2.50. Slot edges sit
  exactly 0.50 beyond the ±26.00 contact-face lines, so each fin's
  cell-side face lies ON its face line.
- **Negative-end lands trimmed**: CELL_AA_CONTACT_PAIR pad 2 is now
  5.0 × 2.95 at (0, +23.775) — the ear land ends 0.25 clear of the slot
  edge on all three negative sites; the fin, not the pad, carries the
  contact face. Positive lands unchanged (5.0 × 5.4, spanning the face
  lines).
- **J1 relocated** to local (26.25, 56.9) — inside the case-verified
  envelope (case X −3..+3 → local 23.25..29.25). Pinout unchanged
  (pin 1 west = VBAT+, pin 2 east = GND). JBATT cable re-check: J1 asm
  (0, −5.47) → Main JBATT asm (+24.0, +64.50): straight-line 73.9 mm
  (Stage 2: 70.3 mm) → still ≈100 mm class, no cable change.
- **F1 relocated** to local (7.85, 57.17), rotation 0 — inside its
  case-verified envelope and clear of the west slot; F1.1 west =
  PACK_POS_RAW, F1.2 east = PACK_POS_FUSED. Lands shrunk to 1.1 × 1.2
  (the 1.85 mm south strip bound); the 1206 chip overhangs the lands
  0.2 mm/side in Y — DFM watch item recorded in FABRICATION.md.
- **J2 relocated** to local (20.2, 57.075), pads E-W: J2.1 (fused)
  (18.2, 57.075), J2.2 (output) (22.2, 57.075). The slide switch moved
  to the case south wall inner face (centre X 0, pads Z 2.2..8.8), so
  the wire run is now **≈15 mm class**, superseding Stage 2's ≈50 mm
  east-wall estimate. Pads 1.4 × 1.6 local, presenting 1.6 (X) × 1.4 (Y)
  after the 90° placement (see DRC catch below).
- **Tongue strips formalised**: E/W edge strips local X 0..0.5 and
  52.0..52.5 × Y 9.37..15.37 and 39.37..45.37 are pad/via-free
  (checker-enforced; marked on Dwgs.User). The SW/SE 6 × 6 corner
  fixing zones and their checker item are **retired**.
- **Re-routing around the slots**: PACK_NEG runs F.Cu to a via at
  (15.5, 52.7), B.Cu east and south to a via at (29.6, 56.9), F.Cu into
  J1.2. PACK_POS_RAW keeps its pour via at (48.0, 50.6), runs B.Cu west
  along Y 50.6 and south at X 2.5 (west of the W slot) to a via at
  (5.7, 57.3), F.Cu stub into F1.1. PACK_POS_FUSED and VBAT_OUT are
  short F.Cu runs in the south strip. BRIDGE_S pour lost its east lobe
  (the trimmed BT3− pad no longer reaches it); BRIDGE_N pour is stepped
  to stay 0.25 clear of the notch; both pours' fills verified clear of
  all slots by probe points in the checker.

### Reproduce-before-fixing measurement

Before editing, the current (Stage 2) board was measured against the
slot rects (`.issue303-runtime/measure_slots.py`): **23 copper items
intersect the slots** — all three BT− pads (by design; they are the fin
sites), F1.1/F1.2, J1.1/J1.2, J2.2 and TP2 pads, the PACK_NEG B.Cu south
runs on both sides, the PACK_POS_RAW feed via at (36.9, 53.6) (inside
the east slot), and several F.Cu stubs. J1's housing envelope overlaps
the east fin (the case note's precise figure is 10.09 mm³).

### Verification (as-saved files, restored project file)

- ERC **0** (schematic unchanged). DRC **0 violations / 0 unconnected /
  0 footprint errors** (`.issue303-runtime/drc-rev.rpt`).
- Board checker **269 PASS / 0 FAIL**: pad→net map; series walk
  J1.2 → BT1 → BT2 → BT3 → F1 → J2 → J1.1 intact, each cell once;
  positive pads span the ±26.00 faces; negative ends verified in the
  fin geometry (pad ends 0.25 clear of the slot edge, slot edge 0.50
  beyond the face, fin face on the face); slot rects + notch sides
  present in Edge.Cuts at the case numbers; every pad ≥0.2 clear of
  every slot; vias ≥0.2 copper-clear; tongue strips pad/via-free;
  J1 and F1 pads inside their case-verified envelopes; all three pours
  filled and probe-verified clear of the slots.
- Board SHA-256:
  `8b5ca19f8bfbb3b30a448bbe20b062a02650f4ca32e7f1c74cb00c7b4548427a`.
- **DRC caught two real defects in revision pass A** (both fixed before
  this record): (1) the first PACK_NEG F.Cu jog at Y 55.2 crossed BT2's
  positive pad (spans to Y 55.7) — a BRIDGE_S↔PACK_NEG short, plus the
  two mask-bridge errors it caused; the return now stays on B.Cu under
  the pad (SMD pads are F.Cu-only) and surfaces east of it. (2) J2's
  pads were sized 1.6 × 1.4 in the footprint's local frame; the 90°
  placement presents the 1.6 side in board Y, leaving only 0.125 mm to
  the south edge — the footprint pads are now 1.4 × 1.6 local. A third
  item, the TP2 silkscreen label clipped by the west slot edge
  (warning), was fixed by moving the label.
- Checker note: pad boxes are now taken from `GetBoundingBox()` (board
  frame); `GetSize()` is footprint-local and swaps axes under 90°
  rotation — pass A's J2 slot check was a false alarm from exactly
  that, while DRC (true geometry) was clean.
- Process note: the pcbnew save cycle rewrote `pwr.kicad_pro` again;
  it was restored verbatim from git and the final ERC/DRC/checker ran
  against the restored pair (the AGENTS.md lesson).
- Manufacturing package regenerated: BOM (unchanged parts), CPL from
  the board file (F1 (7.85, 57.17) rot 0; J1 (26.25, 56.9) rot 0),
  Gerbers + Excellon drill in `manufacturing/gerbers/`, FABRICATION.md
  fixing section rewritten to the fin + tongue scheme.
