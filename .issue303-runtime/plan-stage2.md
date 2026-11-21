# Issue #303 Stage 2 (layout) — plan

> EXECUTED 2026-11-21. As-built supersessions (DRC pass 1): F1 centre
> (37.3, 55.9) → **(36.6, 55.9)**, J2 centre (34.0, 54.3) → **(33.4, 54.3)**,
> PACK_POS_RAW stub now lands on the F1.1 pad centre. See the Stage 2
> addendum in design-note.md for the as-built record.

## Frame

Board-local frame: origin at board NW corner, +x east, +y south (KiCad native).
Board 52.5 (X) × 58.0 (Y), 2 layers, 0.8 mm thick.
Asm frame → local: local = asm − (−26.25, −62.37). Cell centres local
(11.25, 28) / (26.25, 28) / (41.25, 28); contact face lines local Y 2.00 (N)
and 54.00 (S) = ±26.00 from cell centres (Stage 1 derivation). Block envelope
local X 2.0..50.5, Y 0..56.0 (48.5 × 56.0, north-anchored, Stage B item 2).

## Footprint refinement (pwr.pretty, Stage 1 placeholders → Stage 2)

- CELL_AA_CONTACT_PAIR: pads 5.0 × 5.4 at (0, ∓25.0) — pad centres 25.0 from
  the cell centre so the pads sit fully on the board (board edge is 28.0 from
  centre) while still covering the ±26.00 face lines (N pad spans local
  Y 0.3..5.7, S pad 50.3..55.7). The contact FACE planes stay at ±26.00
  (case/cell geometry); the pads are the solder lands for the contact ears.
- SW_PADS_2P: pads 2.2 × 2.2 at (0, ∓2.0) (hand-soldered switch wires;
  Stage 1's 3×3 @ ±2.54 does not fit the south strip — see J2 below).
- GH_2P: unchanged (real BM02B-GHS-TBT land pattern, ex-Main JBATT:
  pads 0.6 × 1.7 @ 1.25 pitch, no tab pads).
- PTC_1206: unchanged (standard 1206 land).
- TESTPOINT: Ø2.0, layers F.Cu + F.Mask only (no paste).

## Placement (local mm)

| Ref | Pos | Rot | Notes |
|---|---|---|---|
| BT1 | (11.25, 28) | 0 | pad1 N = BRIDGE_N (+, button), pad2 S = PACK_NEG (−, spring) |
| BT2 | (26.25, 28) | 180 | pad1 S = BRIDGE_S (+), pad2 N = BRIDGE_N (−) |
| BT3 | (41.25, 28) | 0 | pad1 N = PACK_POS_RAW (+), pad2 S = BRIDGE_S (−) |
| F1 | (50.60, 47.00) | 90/270 | east strip; pin1 (PACK_POS_RAW) must end up NORTH — assert in build script, flip rot if needed |
| J1 | (43.50, 56.90) | 0 | pad1 W = VBAT_OUT, pad2 E = PACK_NEG; centre asm X +17.25 ≈ Stage B route start (+17, −4.37) |
| J2 | (36.00, 54.30) | 0 | pads stacked N-S: pin1 N (36, 52.3) = PACK_POS_FUSED, pin2 S (36, 56.3) = VBAT_OUT |
| TP1 | (51.00, 30.00) | — | on the return pour (PACK_POS_RAW), east strip |
| TP2 | (7.60, 56.60) | — | PACK_NEG, south strip west |

Component-free areas honoured: nothing under the cells (cell footprints
X 4.0..48.75, Y 2.75..53.25) except flat contact pads/zones/tracks/vias;
east strip (local X ≥ 48.75, the Wing-tab column) carries pour + TP1 pad
only — F1 sits at its south end with body X ≤ 48.4 wait no: F1 pads
X 49.7..51.5 — F1 IS in the strip's south end, south of the tab column's
Y range (tab column local Y 17.4..53.7 at X ≥ 48.75; F1 at Y 45.4..48.6
is INSIDE that Y range!). Re-check: Z-check §2 says the strips under the
tabs must present bare board at +0.15; F1 (top ≈ +1.15) at (50.6, 47)
would stand in the tab column. Tab underside features: U_MUX bottom 3.30
at asm X 24.95..30.05 = local X 51.2..56.3 — outside board (≤52.5) except
51.2..52.5 sliver at asm Y −27.3..−20.7 = local Y 35.1..41.7. F1 at local
Y 45.4..48.6, X 49.7..51.5: the only tab feature reaching X ≤ 52.5 is
that U_MUX sliver at local Y 35.1..41.7 — no Y overlap with F1. J_WING
envelope west edge asm 25.62 = local 51.87, Y local 19.3..27.4 — no
overlap. So F1 clears every physical tab feature by ≥3.15 mm vertically
anyway (top 1.15 vs lowest feature 3.30 → 2.15 hmm: 3.30 − 1.15 = 2.15 mm).
Task instruction says east strip = pour only, no components. F1 at
X 49.7.. is unambiguously "east strip". => MOVE F1 (see below).

## F1 relocation (resolves the strip conflict)

F1 must leave the east strip. Free area: south strip Y 53.25..58 west of
J1, plus the band between the south contact pads. F1 (1206, rot 0, pads
E-W) at (44.60, 56.30)?? — J1 is at (43.5, 56.9), pads X 42.6..44.4.
Collision. F1 west of BT3 pad, in the notch band: the BRIDGE_S zone notch
(local X 29.1..38.4, zone only to Y 53.6) — F1 at (33.75, 55.9) rot 0:
pads (32.8, 55.9) X 32.25..33.35, (34.7, 55.9) X 34.15..35.25, Y 55.0..56.8;
body X 32.15..35.35, Y 55.1..56.7. Conflicts: J2 pad_b (36, 56.3) spans
X 34.9..37.1, Y 55.2..57.4 → body/pad overlap with F1 pad2 (X ≤35.25 vs
34.9) ✗ marginal. Shift J2 west: J2 at (34.0, 54.3): pads (34, 52.3)
X 32.9..35.1 Y 51.2..53.4; (34, 56.3) X 32.9..35.1, Y 55.2..57.4. F1 then
east of J2: F1 (38.6, 55.9): pads (37.65) X 37.1..38.2, (39.55) X 39.0..40.1,
Y 55.0..56.8; body 37.0..40.2 × 55.1..56.7. Conflicts: BT3 pad X ≥38.75,
Y ≤55.7: F1 pad2 X 39.0..40.1 × Y 55.0..55.7 overlap ✗ (pad2 vs BT3 pad
corner). F1 rot 90 at (37.6, 55.6): pads (37.6, 54.65) 1.8×1.1 →
X 36.7..38.5, Y 54.1..55.2; (37.6, 56.55) X 36.7..38.5, Y 56.0..57.1;
body X 36.8..38.4, Y 54.0..57.2. Conflicts: BT3 pad (X≥38.75) ✓ gap 0.25;
J2 pad_b (≤35.1) ✓ gap 1.6; BRIDGE_S zone (notch X ..38.4 to Y 53.6;
X 38.4..44.1 segment to 55.75): F1 pad1 (Y 54.1..55.2, X 36.7..38.5) —
zone at X 36.7..38.4 reaches Y 53.6 → pad1 Y starts 54.1 ✓ gap 0.5;
at X 38.4..38.5 zone reaches 55.75 → pad1 X ≤38.5 overlap 0.1 × Y
54.1..55.2 ⊂ zone Y range → zone yields around pad1 (different net,
legal; zone link survives — checked by DRC). Hmm, tight. Shift F1 west
0.3: (37.3, 55.6): pads X 36.4..38.2 ✓ fully west of 38.4 segment;
gap to BT3 pad 38.75−38.2 = 0.55 ✓; J2 pad_b gap 36.4−35.1 = 1.3 ✓.
F1 rot: pin1 must be PACK_POS_RAW — feed comes from the return pour
(east/north). With rot 90/270 pin1 is N or S pad; the pour feed reaches
the F1 area from the north-east along the south band... PACK_POS_RAW
copper in the south: none yet — the pour ends at the east strip
(Y ≤46.9). Feed F1 pin1 by a track: from pour south edge (49.6, 46.9)
south along X 49.6?? that's the strip — a TRACK on the strip is copper,
not a component; the strip rule = pour only/no components/no connector.
A track is not the pour... The Z-check's physical point: strip must be
FLAT (nothing standing). A track is flat. But the task text says
"return pour only". A 2 mm-wide track along the strip edge is pour-class
copper; I'll widen it into the pour itself: extend the PACK_POS_RAW zone
south along the strip to Y 54.0 (zone polygon step at X 49.6..52.3 down
to 54.0, west edge stepping to X 44.3 only north of Y 46.9 — wait the
zone already spans X 44.3..52.3 to Y 46.9; extending the X ≥49.6 part
south to 54.0 keeps F1's pin2 out: F1 is at X ≤38.5, far west — the pour
extension is just copper reaching toward F1. Then F1 pin1 feed: track
from pour west edge (49.6, 53.0) west at Y 53.0?? crosses BRIDGE_S zone
(X ≤44.1, Y ..55.75 at X 38.4..44.1) ✗. Track at Y 53.0 from X 49.6 west
to F1 pin1 (37.3, 54.65)… crosses zone east segment (X 38.4..44.1,
Y ≤55.75) ✗✗. Via B.Cu: pour → via at (48.6, 52.0) (in pour extension,
annulus X 48.3..48.9 — east of cell3 (48.75)? annulus crosses 48.75
line but a via is flat/tented, fine; SE zone starts Y 52: via at Y 52.0
X 48.3..48.9 ⊂ SE zone X≥46.5 × Y≥52 ✗ via in fixing zone! via at
(48.6, 50.6): annulus Y 50.3..50.9 ✓ north of 52 ✓). B.Cu run:
(48.6,50.6) → west at Y 50.6 to (38.2,50.6) → south at X 38.2 to
(38.2,53.9) → via up (38.2,53.9)?? annulus Y 53.6..54.2, X 37.9..38.5:
zone notch edge 53.6 at X ≤38.4 → via touches zone area X 37.9..38.4 ×
Y 53.6.. → zone yields ✓ legal; F.Cu stub (38.2,53.9) → F1 pin1
(37.3,54.65)?? pin1 must be the pad the stub reaches: stub from
(38.2,53.9) SW to pad at (37.3,54.1..55.2) north edge ✓ if pin1 = north
pad. Set F1 rotation so pin1 = north pad (assert in script).
B.Cu crossings: PACK_NEG B.Cu run (Y 53, X 15.5..46.2 + stub X 46.2
Y 53..54.6): FUSED... wait this feed is PACK_POS_RAW (pre-PTC). Call it
RAW feed. RAW B.Cu segments: Y 50.6 (X 38.2..48.6), X 38.2 (Y 50.6..53.9).
PACK_NEG B.Cu at Y 53: crosses X 38.2 segment at (38.2,53) ✗✗.
Move PACK_NEG B.Cu run north: Y 49.4 (X 15.5..46.2): RAW X-38.2 segment
spans Y 50.6..53.9 → no cross ✓ (49.4 < 50.6). PACK_NEG via2 stub
X 46.2 (Y 49.4..54.6): RAW Y-50.6 run spans X 38.2..48.6 → crosses
(46.2,50.6) ✗. Move RAW via west: via at (44.0,50.6)?? pour extension
west edge is 49.6 — via must be IN pour copper: pour extension covers
X 49.6..52.3 only. Widen extension: X 47.5..52.3 to Y 54.0 (still strip
copper, flat ✓; cell3 X ≤48.75 — pour under cell edge is existing
design). via RAW at (48.0,50.6) ✓ in pour. PACK_NEG stub X 46.2 vs RAW
run Y 50.6 X 38.2..48.0 → cross at (46.2,50.6) ✗ STILL. Move PACK_NEG
stub east: via2 at (47.0, 54.6)?? annulus X 46.7..47.3 ⊂ SE zone X≥46.5
✗ (Y 54.6 ≥52). PACK_NEG stub at X 45.9 (annulus ≤46.2 ✓): B.Cu path
(15.5,49.4) → (45.9,49.4) → (45.9,54.6) via2. RAW run Y 50.6 crosses
X 45.9 stub ✗✗✗. 

RESOLUTION: swap layers for the RAW feed's west run: RAW feed on F.Cu
is blocked by BRIDGE_S zone; on B.Cu blocked by PACK_NEG. Move PACK_NEG
run to Y 56.9-south?? B.Cu south band: PACK_NEG B.Cu: via1 (15.5,53) →
south X 15.5 to (15.5,56.9) → east Y 56.9 to (45.9,56.9) → north X 45.9
to via2 (45.9,54.6)?? that stub crosses its own east run — fine (same
net, it's a path: (15.5,53)→(15.5,56.9)→(45.9,56.9)→(45.9,54.6)). Crossings
on B.Cu: FUSED B.Cu segments (Y 47.95 X 47..48; X 47 Y 47.95..51; Y 51
X 33.5..47): PACK_NEG X-45.9 stub spans Y 54.6..56.9 ✓ no; east run
Y 56.9 ✓ no; X-15.5 ✓ no. RAW B.Cu (Y 50.6 X 38.2..48; X 38.2 Y 50.6..53.9):
PACK_NEG segments: Y 56.9 run ✓, X 15.5 ✓, X 45.9 (54.6..56.9) ✓ — NO
CROSSINGS ✓✓. FUSED B.Cu vs RAW B.Cu: FUSED Y-51 run (X 33.5..47) vs
RAW X-38.2 segment (Y 50.6..53.9) → cross at (38.2,51) ✗✗. Move FUSED
west run south: Y 52.4 (X 33.5..47): RAW X-38.2 spans Y 50.6..53.9 →
cross (38.2,52.4) ✗. Move RAW X-segment west: RAW via at (48,50.6) →
west Y 50.6 to (35.0,50.6) → south X 35.0 to (35.0,53.9) via-up →
stub to F1 pin1 (37.3,54.65): stub (35,53.9)→(36.8,54.3)→pin1 N edge
(37.3,54.1)?? pin1 pad spans X 36.4..38.2, Y 54.1..55.2 (F1 at
(37.3,55.6) rot-pin1-north: pads (37.3,54.65) size 1.8×1.1 → X 36.4..38.2,
Y 54.1..55.2 ✓). Stub from (35,53.9) east to (36.4,54.3) lands on pad
west edge ✓. RAW X-35 segment vs FUSED Y-51 run (X 33.5..47, Y 51):
cross at (35,51) ✗✗✗. FUSED west run to Y 49.8?? FUSED B.Cu: viaA
(48,47.95) → X-47 segment (47.95..51) → Y-51 run. Change: viaA →
south X 47.6 to Y 49.8 → west Y 49.8 (X 33.5..47.6) → viaB (33.5,49.8):
RAW segments: Y 50.6 run (X 35..48) — FUSED Y-49.8 run is north of it ✓;
X-47.6 segment Y 47.95..49.8 vs RAW run Y 50.6 ✓ no cross; RAW X-35
segment Y 50.6..53.9 vs FUSED Y-49.8 ✓ no; FUSED viaB (33.5,49.8)
annulus (33.2..33.8, 49.5..50.1) vs BRIDGE_S zone F.Cu — via is through;
F.Cu annulus at (33.5,49.8): zone band Y 49.9.. at X 29.1..38.4 → annulus
Y ≤50.1 overlaps zone Y ≥49.9 by 0.2 in X 33.2..33.8 → zone yields ✓.
F.Cu stub viaB → J2 pad_a: J2 at (34,54.3) pads (34,52.3) X 32.9..35.1,
Y 51.2..53.4: stub (33.5,49.8) → (33.8,51.2) pad_a north edge ✓ crosses
zone band (yields ✓, link survives north strip? band Y 49.9..53.6,
stub carve X ~33.2..35.4 Y 49.8..53.4 + pad_a carve X 32.65..35.35
Y 50.95..53.65: remaining band links: west X 29.1..32.65 full height ✓
(3.55 wide) — connected ✓✓.
PACK_NEG via1 (15.5,53): F.Cu stub from BT1.2 pad (X ≤13.75, Y 50.3..55.7)
east edge (13.75,53) → via (15.5,53) ✓. PACK_NEG B.Cu: (15.5,53) →
(15.5,56.9) → (45.9,56.9) → (45.9,54.6) via2 → F.Cu stub (45.9,54.6) →
(44.7,55.5) → J1.2 N edge (44.125,56.05) ✓ (as before).
VBAT_OUT F.Cu: J2 pad_b (34,56.3) X 32.9..35.1 → east edge (35.1,56.3)
→ (37.5,56.9) → J1.1 W edge (42.575,56.9) ✓ clear of F1 (X ≤38.2,
Y ≤57.65?? F1 at (37.3,55.6): pad2 (37.3,56.55) X 36.4..38.2, Y 56.0..57.1;
body Y ..57.2): VBAT_OUT track at Y 56.9 from X 37.5 east — F1 pad2
spans X 36.4..38.2 × Y 56.0..57.1: track (0.8 wide, Y 56.5..57.3) at
X 37.5..38.2 overlaps pad2 ✗. Route VBAT_OUT from pad_b SOUTH edge:
(34,57.4) → south?? edge 58 ✗. From pad_b east edge at Y 55.6: (35.1,55.6)
→ east at Y 55.6 (55.2..56.0) to (41,55.6) → south-east to J1.1
(42.575,56.9) W edge: crosses F1 pad2 (X 36.4..38.2, Y 56.0..57.1)?
Track Y ≤56.0, pad2 Y ≥56.0 → touching at 56.0 ✗ marginal. Track at
Y 55.45 (55.05..55.85): clear of pad2 (≥56.0) ✓ gap 0.15 — thin. Move
F1 north 0.3: F1 (37.3,55.3): pad1 (37.3,54.35) Y 53.8..54.9, pad2
(37.3,56.25) Y 55.7..56.8. VBAT track Y 55.45 (55.05..55.85) vs pad2
Y ≥55.7 → overlap 55.7..55.85 ✗. Track Y 55.2 (54.8..55.6): vs pad2
55.7 ✓ gap 0.1 ✗. F1 west: (36.9,55.6): pads X 36.0..37.8; VBAT track
from pad_b (35.1,55.6)?? pad_b centre Y 56.3, east edge point (35.1,55.9):
track (35.1,55.9) → east Y 55.9 (55.5..56.3) vs F1 pad2 (36.0..37.8 ×
56.0..57.1): overlap X 36..37.8 × Y 56.0..56.3 ✗. 

F1 vs VBAT_OUT is the last knot. Put F1's axis VERTICAL with pin1 WEST:
rot 0 but mirrored?? PTC is symmetric — pin1/pin2 are interchangeable
electrically! F1 is a PTC: the schematic walk F1.1=RAW, F1.2=FUSED is a
labelling; physically either orientation works (PTC has no polarity).
So place F1 rot 0 (pads E-W) at (37.3,55.9): pad W (36.35,55.9) X
35.8..36.9, Y 55.0..56.8; pad E (38.25,55.9) X 37.7..38.8, Y 55.0..56.8;
body 35.7..38.9 × 55.1..56.7. Assign W pad = RAW (feed from north via
stub), E pad = FUSED?? FUSED then goes east → J2 is WEST ✗. Assign
W = FUSED (to J2 pad_b?? no — FUSED goes to J2.1 = pad_a (34,52.3)).
Hmm: F1 W pad (36.35,55.9) → FUSED → J2 pad_a (34,52.3): track north
at X 36.35 (36.0..36.7) from Y 55.0 to 53.4 (pad_a south edge 53.4):
crosses zone notch (X 29.1..38.4 to Y 53.6): track enters zone area
Y 53.4..55.0 at X 36.0..36.7 — zone south edge there is 53.6 → track
Y from 55.0 north to 53.4 crosses 53.6 boundary into zone region
Y 53.4..53.6 sliver → zone yields 0.2 around track — legal ✓ (track
ends ON pad_a at 53.4; the yield carve is tiny). ✓ F1 E pad (38.25,55.9)
= RAW: feed from RAW via-up stub: RAW B.Cu X-segment at X 35.0??
Rework RAW: via (48,50.6) → west Y 50.6 to (40.0,50.6) → south X 40.0
to (40.0,54.2) → via-up (40.0,54.2) [annulus X 39.7..40.3, Y 53.9..54.5:
zone X 38.4..44.1 segment reaches Y 55.75 → via inside zone area →
yields ✓; BT3 pad (X 38.75..43.75, Y ..55.7): via annulus ⊂ pad rect ✗✗
via ON BT3 pad again. X 40 is inside BT3 pad's X range and Y 54.2
inside its Y range. Via-up must avoid X 38.75..43.75 × Y 50.3..55.7
(BT3 pad) and X 23.75..28.75 (BT2 pad). Corridor X 35.1..38.75 (between
J2 pad_b X ≤35.1... J2 pad_b (34,56.3) X 32.9..35.1, Y 55.2..57.4) and
BT3 pad: via at (37.0,54.2): annulus X 36.7..37.3, Y 53.9..54.5 ✓ clear
of BT3 pad (≥38.75) ✓, clear of J2 pads (pad_a Y ≤53.4: annulus Y ≥53.9
✓ gap 0.5; pad_b X ≤35.1 ✓). RAW B.Cu: (48,50.6) → west to (37,50.6) →
south X 37 to (37,54.2) via-up → F.Cu stub (37,54.2) → east-south to
F1 E pad (37.7,55.0) N edge... stub (37,54.2)→(37.9,55.0) lands on pad
E north-west ✓ clear of F1 W pad (X ≤36.9, stub X ≥37 ✓ at Y 54.2;
at Y 55.0 stub X 37.9 ✓). RAW B.Cu crossings: FUSED B.Cu (Y 49.8 run
X 33.5..47.6; X 47.6 seg; viaA (48,47.95)): RAW Y-50.6 run crosses
X-47.6 segment (Y 47.95..49.8)? 50.6 > 49.8 ✓ no. RAW X-37 segment
(Y 50.6..54.2) vs FUSED Y-49.8 ✓ no. PACK_NEG B.Cu (X 15.5; Y 56.9;
X 45.9 Y 54.6..56.9): RAW X-37 (≤54.2) ✓; RAW Y-50.6 (X 37..48) vs
PACK_NEG X-45.9 stub (Y 54.6..56.9) ✓ no. ✓✓✓ ALL CLOSED (again).
FUSED F.Cu stub: F1 W pad (36.35,55.9) north at X 36.35 to J2 pad_a
(34,52.3)?? pad_a centre X 34, spans 32.9..35.1 — the vertical track at
X 36.35 (36.0..36.7) reaches Y 53.4 (pad_a south edge line) at X 36.35
— pad_a X range ends 35.1 ✗ track misses the pad. Diagonal: (36.35,55.0)
→ (35.3,53.6) → pad_a SE corner (35.1,53.4) ✓ lands on corner; path
crosses zone notch region (yields ✓). OK.
And J2 pad_b (34,56.3) = VBAT_OUT → J1.1: east edge (35.1,56.3) →
(36.9,56.9)?? F1 W pad spans X 35.8..36.9, Y 55.0..56.8; F1 body
X 35.7..38.9, Y 55.1..56.7. VBAT track from (35.1,56.3) east at Y 56.3
hits F1 W pad (X ≥35.8, Y ..56.8 ∋ 56.3) ✗. From pad_b south edge
(34,57.4) → east at Y 57.55 (57.25..57.85): clear of F1 body (Y ≤56.7)
✓ gap 0.55; clear of F1 E pad (Y ≤56.8) ✓ 0.45; board edge 58: track
edge 57.85 → 0.15 ✗ thin but it's a track-to-edge (fab min ~0.2)...
track 0.5 wide at Y 57.5 (57.25..57.75): edge gap 0.25 ✓, F1 E pad gap
57.25−56.8 = 0.45 ✓. Then north into J1.1: (42.0,57.5) → (42.575,56.9)
pad1 W edge ✓ diagonal clear of J1 pad2 (X ≥43.825) ✓. ✓ CLOSED.

## Final routing summary (build script asserts every pad/net/coordinate)

- Zones F.Cu: BRIDGE_N rect (8.0,0.2)-(30.5,6.2); BRIDGE_S stepped
  polygon; PACK_POS_RAW stepped polygon incl. strip extension
  X 47.5..52.3 to Y 54.0 (via RAW at (48,50.6) sits in it; extension
  south edge 54.0 vs SE zone Y ≥52 × X ≥46.5: pour copper in the
  fixing zone is "plain copper" = allowed; no via/component there —
  via RAW at Y 50.6 ✓ north of 52).
  Wait: pour extension X 47.5..52.3, Y 46.9..54.0 — F1 was going to be
  fed from it at (48,50.6) ✓. But TP1 (51,30) already in main pour ✓.
  Pour polygon final: (38.4,0.2)(52.3,0.2)(52.3,54.0)(47.5,54.0)
  (47.5,46.9)(44.3,46.9)(44.3,5.9)(38.4,5.9) close. Check F1-old-site
  conflicts: none (F1 moved west). Check pour vs J2/J1: pour X ≥44.3
  Y ≤46.9 + strip X ≥47.5 Y ≤54: J1 pads X ≤44.4 ✓; via2 PACK_NEG
  (45.9,54.6) annulus X 45.6..46.2 vs pour strip west edge 47.5 ✓.
  SE-zone: pour occupies X 47.5..52.3 × Y 52..54 of the zone as plain
  copper — allowed per brief ("plain copper/keep-out is fine").
- Tracks/vias per the closed plan above. Via Ø0.6/0.3. Track widths:
  PACK_NEG B.Cu 1.0; RAW B.Cu 1.0; FUSED B.Cu 0.8; F.Cu links 0.8.
- Fixing zones (open input — no decision on Issue #296 as of build):
  SW (0..6, 52..58), SE (46.5..52.5, 52..58): no components, no vias.
  Checker asserts: footprint pads/bodies(as footprint bbox) + vias
  outside; J1 housing overhang computed from datasheet width 5.7 max
  → 46.35 < 46.5 ✓ (note in design note).

## Verification

- Board topology checker (Stage 1 approach on the routed .kicad_pcb):
  pad→net walk J1.2 → BT1 → BT2 → BT3 → F1 → J2 → J1.1; short check;
  geometry assertions (centres, face lines, outline, fixing zones).
- kicad-cli: ERC (schematic, unchanged) 0; DRC 0 errors / 0 unconnected.
- Manufacturing package: manufacturing/BOM-jlcpcb.csv,
  CPL-jlcpcb.csv (F1 + J1 only), FABRICATION.md (0.8 mm explicit,
  hand-fit list, assembly order: power board before Wings).
