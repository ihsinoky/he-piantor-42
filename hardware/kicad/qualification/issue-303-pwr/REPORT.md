# Issue #303 — wireless power board (3× AA NiMH floor board)

**Stage 1 (circuit design): COMPLETE 2026-11-21. DRAFT — NOT FOR ORDER. No layout yet**
(Stage 2 waits for the Wing δ, Issue #299, and case geometry, Issue #296).

- Schematic: `pwr.kicad_sch` — **ERC 0 violations**.
- Topology: alternating cell orientation; bridges BRIDGE_N (BT1+↔BT2−) and BRIDGE_S
  (BT2+↔BT3−); PACK_POS_RAW return pour along the east edge; series path machine-verified
  from the schematic file (each cell traversed once, no cell shorted by any net).
- Protection: F1 = Littelfuse 1206L050/24WR PTC in the + leg. Switch: off-board bay-wall
  SS-12D10 class via J2 loop pads. Output: J1 = JST BM02B-GHS-TBT, pin1 + / pin2 −,
  matching Main's JBATT on a straight GH–GH cable (~100 mm).
- Full design note (topology proof table, parts + availability, recommendations,
  Stage 2 input list): `.issue303-runtime/design-note.md` on this branch.
