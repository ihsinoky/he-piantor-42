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
