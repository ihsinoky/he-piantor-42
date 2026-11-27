# Issue #303 — layout revision: consume the case 3D fixing decision (Issue #296)

Status: IN PROGRESS. Base: Stage 2 complete on `issue-303-pwr` (PR #304),
board SHA-256 `98e4e46e…`. Source of the fixing decision:
`he-piantor-case296b/.issue296-runtime/case-3d.md` (fixing section) +
Issue #296 comment 7058037232; envelope boxes from the case verify script
`verify_case3d.py` lines 102–103.

## Transform (case/asm frame → board-local)

Board-local: origin NW corner, +x east, +y south, board 52.5 × 58.0.
Case frame: board north edge on the bay north inner face Y −62.37,
board centred on X 0 (edges ±26.25).

    local X = case X + 26.25
    local Y = case Y + 62.37

Anchors verified against Stage 2 as-built values:
- cell centres case (−15/0/15, −34.37) → local (11.25/26.25/41.25, 28.0) ✓
- contact faces case −8.37 / −60.37 → local 54.00 / 2.00 (= centres ±26.00) ✓
- Stage 2 J1 local (43.5, 56.9) → case (17.25, −5.47) = the design note's
  recorded assembly position ✓

## Case inputs converted to board-local

| Item | Case | Board-local |
|---|---|---|
| West S slot | X −22.50..−6.50, Y −8.87..−6.22 | X 3.75..19.75, Y 53.50..56.15 |
| East S slot | X 6.50..22.50, Y −8.87..−6.22 | X 32.75..48.75, Y 53.50..56.15 |
| North slot (open notch) | X −8.5..8.5, Y −62.52..−59.87 | X 17.75..34.75, edge → Y 2.50 deep |
| West fin (in slot, +0.5 clr) | X −22.00..−7.00, face Y −8.37 | X 4.25..19.25, Y 54.00..55.65 |
| East fin | X 7.00..22.00, face Y −8.37 | X 33.25..48.25, Y 54.00..55.65 |
| North fin | X −8..8, face Y −60.37 | X 18.25..34.25, Y 0.35..2.00 |
| Tongue strips W | X −26.25..−25.75, Y −53..−47 / −23..−17 | X 0..0.5, Y 9.37..15.37 / 39.37..45.37 |
| Tongue strips E | X 25.75..26.25, same Y | X 52.0..52.5, same Y bands |
| J1 envelope (verified) | X −3..3, Y −7.3..−4.37, Z ..3.05 | X 23.25..29.25, Y 55.07..58.0 |
| F1 envelope (verified) | X −20..−16.8, Y −6.0..−4.4, Z ..1.15 | X 6.25..9.45, Y 56.37..57.97 |
| Switch (off-board) | centre X 0, pads Y −3.37..−2.37, Z 2.2..8.8 | board S edge at (−, 58.0); J2 near local (20.2, 57.1) |

Fin-face check (the ±26.00 contact planes, board-local faces 54.00 S /
2.00 N): S slots' fin cell-side face = slot N edge + 0.5 = 53.50+0.50 =
54.00 ✓; N notch fin face = notch floor − 0.5 = 2.50−0.50 = 2.00 ✓.
The fins ARE the 209 lands at the three negative ends (BT1− S, BT2− N,
BT3− S) — the slots sit at the negative pads by design.

## Dispositions

1. **Slots**: cut the 3 slots as Edge.Cuts (S rects closed; N as an open
   notch in the north edge path). BT− pads are swallowed by the slots in
   plan → reshape footprint pad 2 (see 4). Re-pour zones (BRIDGE_S east
   lobe dropped — its pad no longer reaches past Y 53.25; BRIDGE_N /
   PACK_POS_RAW fills clip at the notch/slot edges, verified in checker).
2. **Tongue strips**: formalise in the checker — no footprint pad and no
   via in the 4 strips (flush copper/tracks allowed; the Stage 2 east
   tab-column rule already covers the E2 band's Y range).
3. **J1**: centre → local (26.25, 56.9) (case X 0, inside the verified
   envelope; pads X 25.33..27.18 ⊂ envelope). Pinout unchanged
   (pin 1 west = VBAT_OUT, pin 2 east = PACK_NEG).
   JBATT route re-check: J1 centre asm (0, −5.47) → Main JBATT asm
   (+24.0, +64.50): Δ(24.0, 69.97), straight-line 73.9 mm (was 70.3 mm
   from the Stage 2 position); routed ≈90 mm + slack → still the
   ≈100 mm GH–GH class of record. No cable change.
4. **Footprint land refinements** (forced by the 1.85 mm south strip:
   any copper there must sit in Y 56.35..57.80 to keep ≥0.2 from both
   the slot edge and the board edge):
   - CELL_AA_CONTACT_PAIR pad 2: 5.0 × 5.4 @ +25.0 → 5.0 × 2.95 @
     +23.775 (span rel +22.30..+25.25; 0.25 clear of the slot edge on
     every site — S sites: pad S edge 53.25 vs slot 53.50; BT2 rot 180:
     pad N edge 2.75 vs notch floor 2.50). The fin face, not the pad,
     now lies on the ±26.00 plane at negative ends; positive pads
     unchanged and still span their face lines.
   - PTC_1206 pads: 1.1 × 1.8 → 1.1 × 1.2 (land Y narrowed; the 1.6-wide
     chip overhangs the land 0.2/side in Y — DFM watch item, recorded;
     the alternative is leaving the case-verified envelope).
   - SW_PADS_2P pads: 2.2 × 2.2 → 1.6 × 1.4 (same strip constraint).
5. **F1**: centre → local (7.85, 57.17), rot 0 (F1.1 west = PACK_POS_RAW,
   F1.2 east = PACK_POS_FUSED), inside the case-verified envelope
   (pads X 6.35..9.35 ⊂ 6.25..9.45; pads Y 56.57..57.77 ⊂ 56.37..57.97;
   slot gap 0.42, board-edge gap 0.23).
6. **J2**: centre → local (20.2, 57.075), rot ±90 (pads E-W):
   J2.1 west (18.2, 57.075) PACK_POS_FUSED, J2.2 east (22.2, 57.075)
   VBAT_OUT. Pad gaps: slot 0.225 (Y), GH housing W edge (local
   23.40) 0.40. Wire run: switch pads case (X ±~2, Y −3.37, Z 2.2..8.8)
   → J2 case (−8.05/−4.05, −5.37, Z 0.15): ≈7–10 mm + service slack →
   **≈15 mm class** (supersedes Stage 2's ≈50 mm estimate).
7. **Re-routing** (slots sever the Stage 2 B.Cu PACK_NEG south run at
   X 15.5 and the F1 feed via at (36.9, 53.6), which sits inside the
   east slot):
   - PACK_NEG: BT1.2 pad → F.Cu (2.5..15.5, 52.7) → via (15.5, 52.7) →
     B.Cu (15.5,52.7)→(20.6,52.7)→(20.6,55.2) → via (20.6, 55.2) →
     F.Cu (20.6,55.2)→(26.875,55.2)→(26.875,56.9) J1.2 (passes N of the
     J1.1 pad with 0.55 track-edge gap).
   - PACK_POS_RAW: pour → via (48.0, 50.6) (kept) → B.Cu (48,50.6)→
     (30.0,50.6)→(30.0,57.3)→(5.7,57.3) → via (5.7, 57.3) → F.Cu stub
     → F1.1 (6.90, 57.17).
   - PACK_POS_FUSED: F.Cu F1.2 (8.80, 57.17) → J2.1 (18.2, 57.075).
   - VBAT_OUT: F.Cu J2.2 (22.2, 57.075) → J1.1 (25.625, 56.9).
   - TP2 moves to local (2.5, 56.6) (old spot is inside the west slot's
     X range and its link crossed the slot); link: F.Cu up X 2.5 to the
     PACK_NEG run at Y 52.7 (0.95 clear of the slot's west edge).
8. **Superseded Stage 2 reservations**: the SW/SE 6×6 corner fixing
   zones and their checker item are retired (the fin+tongue scheme
   replaces them); Dwgs.User marks redrawn (slots, tongue strips, J1
   band). The SE-zone plain-copper note is moot — the east slot now
   cuts that corner.

## Acceptance (per brief)

ERC 0; DRC 0/0 on the saved file; checker re-run: pad→net map, series
walk, BT+ face coverage, BT− fin-face geometry, slot rects exact,
tongue strips pad/via-free, J1/F1 envelopes, zone fills present and not
crossing the slots; manufacturing package regenerated; .kicad_pro
guard (restore from git if the save cycle rewrote it, re-verify on the
committed pair).
