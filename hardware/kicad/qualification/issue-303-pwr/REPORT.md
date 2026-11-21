# Issue #303 — wireless power board (3× AA NiMH floor board)

**Stage 1 (circuit design): COMPLETE 2026-11-21.**
**Stage 2 (layout): COMPLETE 2026-11-21.**
**Stage 2 fixing revision (Issue #296 case fixing folded in): COMPLETE
2026-11-21. DRAFT — NOT FOR ORDER.**

- Schematic: `pwr.kicad_sch` — **ERC 0 violations**.
- Board: `pwr.kicad_pcb` — 52.5 × 58.0 mm, 2 layers, **0.8 mm** thick
  (stackup stored in file), SHA-256 (fixing revision)
  `8b5ca19f8bfbb3b30a448bbe20b062a02650f4ca32e7f1c74cb00c7b4548427a`
  (Stage 2 as-built was `98e4e46e…`).
  **DRC 0 violations / 0 unconnected pads / 0 footprint errors.**
- Topology: alternating cell orientation; bridges BRIDGE_N (BT1+↔BT2−) and
  BRIDGE_S (BT2+↔BT3−); PACK_POS_RAW return pour along the east edge;
  series path J1.2 → BT1 → BT2 → BT3 → F1 → J2 → J1.1 machine-verified on
  the ROUTED board file (board checker: 83 PASS / 0 FAIL — each cell
  traversed once, no cell shorted by any net, contact faces ±26.00 mm
  covered by the contact pads, outline exact).
- Protection: F1 = Littelfuse 1206L050/24WR PTC in the + leg (PCBA).
  Switch: off-board SS-12D10 class on the case south wall via J2 loop
  pads (wire run ≈15 mm class, revision). Output: J1 = JST
  BM02B-GHS-TBT (PCBA), pin1 + / pin2 −, matching Main's JBATT on a
  straight GH–GH cable (~100 mm class).
- Contacts (hand-fit): Keystone 209 leaf springs on all negative ends,
  Keystone 5231 buttons on all positive ends — also the reverse-insertion
  keying.
- Manufacturing package: `manufacturing/` (BOM + CPL for the two PCBA
  parts, Gerbers + drill, FABRICATION.md with the full hand-fit /
  off-board list).
- **Fixing revision (2026-11-21):** the case 3D stage's fixing decision
  is folded in — 3 fin slots (S-W / S-E rects + north open notch; the
  case fins are the 209 lands, fin faces on the ±26.00 planes, negative
  ear lands trimmed to 5.0 × 2.95 ending 0.25 clear of the slots),
  4 snap-tongue edge strips kept pad/via-free, J1 relocated into the
  south-edge free band (case X −6.5..+6.5), F1 into its case-verified
  envelope, J2 beside J1 for the south-wall switch run. Series topology
  re-verified on the revised routed file (board checker:
  **269 PASS / 0 FAIL**). The Stage 2 corner fixing zones are retired.
  DRC caught a BRIDGE_S↔PACK_NEG short in revision pass A (PACK_NEG jog
  crossing BT2+); fixed by keeping the return on B.Cu under the pad —
  see the design-note revision addendum.
- Full design note (topology proof, parts + availability, Stage 2
  addendum, fixing-revision addendum with the coordinate transform and
  dispositions): `.issue303-runtime/design-note.md` on this branch.
