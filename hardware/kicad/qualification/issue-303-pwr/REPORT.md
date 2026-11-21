# Issue #303 — wireless power board (3× AA NiMH floor board)

**Stage 1 (circuit design): COMPLETE 2026-11-21.**
**Stage 2 (layout): COMPLETE 2026-11-21. DRAFT — NOT FOR ORDER.**

- Schematic: `pwr.kicad_sch` — **ERC 0 violations**.
- Board: `pwr.kicad_pcb` — 52.5 × 58.0 mm, 2 layers, **0.8 mm** thick
  (stackup stored in file), SHA-256
  `98e4e46ef5c73214937ef9c814f44a3410cec5d41c910d2a80719dc89c7e0c85`.
  **DRC 0 violations / 0 unconnected pads / 0 footprint errors.**
- Topology: alternating cell orientation; bridges BRIDGE_N (BT1+↔BT2−) and
  BRIDGE_S (BT2+↔BT3−); PACK_POS_RAW return pour along the east edge;
  series path J1.2 → BT1 → BT2 → BT3 → F1 → J2 → J1.1 machine-verified on
  the ROUTED board file (board checker: 83 PASS / 0 FAIL — each cell
  traversed once, no cell shorted by any net, contact faces ±26.00 mm
  covered by the contact pads, outline exact).
- Protection: F1 = Littelfuse 1206L050/24WR PTC in the + leg (PCBA).
  Switch: off-board bay-wall SS-12D10 class via J2 loop pads (wire run
  ≈50 mm class). Output: J1 = JST BM02B-GHS-TBT (PCBA), pin1 + / pin2 −,
  matching Main's JBATT on a straight GH–GH cable (~100 mm class).
- Contacts (hand-fit): Keystone 209 leaf springs on all negative ends,
  Keystone 5231 buttons on all positive ends — also the reverse-insertion
  keying.
- Manufacturing package draft: `manufacturing/` (BOM + CPL for the two
  PCBA parts, FABRICATION.md with the full hand-fit/off-board list).
- **One open input:** the board fixing method (case 3D stage). Two 6 × 6 mm
  corner zones (SW/SE) are kept free of components and vias until it lands.
- Full design note (topology proof, parts + availability, Stage 2
  addendum with placement decisions and verification):
  `.issue303-runtime/design-note.md` on this branch.
