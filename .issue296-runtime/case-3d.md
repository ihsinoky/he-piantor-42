# Issue #296 Stage 3D — wireless case, 3D design note

Status: built and verified 2026-11-21. Models in
`hardware/case/issue-296-wireless/` (STEP + STL per part; build123d
source `.issue296-runtime/build_case3d.py`). Verification script
`.issue296-runtime/verify_case3d.py` (final run: `verify-out3.txt`);
localisation scans `localise.py`, `localise2.py`, `scan2.py`.

Frame: assembly coordinates (X centred, +Y south), case Z
(geometry17 Z − 2.65). All dimensions below are measured from the
built solids unless marked as an input.

## Inputs consumed

Stage B 2D package (approved 2026-11-21, δ=9.5 + Wing corner trim):
outline 310 × 146.1, south edge straightened, plate tip notch at
|X| = 22.47, bay floor −0.65, cavity 56.5 × 60.0, cover top 16.65,
power board 52.5 × 58.0 (datum = bay north inner face Y −62.37),
Fly right at dx=+38, trackpad island Ø44 at (0, 48), antenna band
11.8 deep, SW1 (−15.5, +64.50), DLED (−4.0, +13.00), 209-clip wall
land 1.52–1.78. Z-check: removal envelope, assembly order, flags.

**Correction recorded, not silently harmonised:** Stage B item 2
prints the bay cavity south inner face as +2.37; the correct value
is **−2.37** (cavity depth 60.0 from −62.37; footprint depth 64.0 =
60.0 + 2 × 2.0 walls; board south clearance 2.0 from board edge
−4.37). The build uses −2.37 throughout. With −2.37 the Main tab
gap is 2.64 (no conflict).

## Case parts (11)

tray-left, tray-right, centre-infill, shell-central, strip-left,
strip-right, plate-left, plate-right, battery-cover, plunger-sw1,
light-pipe-dled. Assembly bbox: X ±155.02 (W 310.04), Y −64.37..81.70
(D 146.07), Z −2.65..22.00. South edge straight: Ymax = 81.70 at
every X in −50..+50 (scan D). The 22.00 datum is still **provisional**
(Junana cap measurement open); cover top 16.65 keeps the 5.35 margin.

## Battery bay re-form

- Floor levelled to −0.65 across the footprint (X ±30.25,
  Y −64.37..−0.37); the Z-check tray post (X 22.73..26.25,
  Y −12.23..−8.70, top 9.40) is removed by the level cut.
- North wall: new wall Y −64.37..−62.37, top 15.15, **except the
  middle-cell span X −7.50..+7.50, capped at 7.80** — the middle
  cell's north top corner sweeps Z ≥ 8.08 through the wall band when
  tipped about its north contact point (verification E, first run).
  The cover carries a north skirt (X ±7.50, Z 7.80..15.15) closing
  that span; the skirt leaves with the cover, so the envelope is
  unaffected. Wing tips (Y −61.60) clear the wall face (−62.37) by
  0.77 in plan.
- E/W walls are a **stepped sill**, tops set by the measured
  crossing scan (`scan2.py`, wall band X 28.25..30.25, both sides
  identical): the plate covers the band along the whole bay (cap
  9.15); the finger span caps at 7.40; the Wing board crosses the
  band from Y −47 south (board bottom 4.70; underside bodies to
  3.30 physical, J_WING study envelope to −0.15). Profile (Y → top):
  −62.37..−59.62 → 9.15; −59.62..−47.00 → 7.40; −47.00..−20.00 →
  2.45; −20.00..−2.37 → 4.45.
- South wall (Y −2.37..−0.37): top 15.15 for |X| ≤ 10.90; **4.45
  sill beyond** — the Wing boards' south edges cross the wall band
  from |X| ≈ 11.14 out (measured tray∩wings), board bottom 4.70 −
  0.25.
- Side closure is a sandwich: wall sill + Wing board / plate tip +
  cover skirt (below). Residual hairline slots (≤0.25 + the
  7.40..9.40 shadow gap under the plate tip on the E/W sides) are
  accepted as designed; the bay interior is not reachable through
  them beyond the side gap the Z-check already accepted.

## Power-board fixing — DECIDED (the open Stage B item)

The tray slab under the bay floor is only 2.0 thick (floor top
−0.65 = tray floor top; tray bottom −2.65), so screws/inserts into
the floor are too weak. Fixing is **screws-free**:

1. **3 case fins through board slots (X/Y location).** The fins are
   the 209-clip lands at the three spring (negative) sites — one
   feature, two functions. Fin: 1.65 thick (Keystone 209 land
   1.52–1.78), cell-side face ON the contact plane (contact faces
   ±26.00 from cell centres (∓15/0/15, −34.37)), top Z 10.5, rising
   from the floor. Sites (asm): BT1− (−15, −8.37) fin X −22.00..−7.00;
   BT2− (0, −60.37) fin X −8..+8; BT3− (+15, −8.37) fin X 7.00..22.00.
   South fins end at |X| 22.00 (clears Wing edge 22.50, plate clip
   22.47, and the Wing board's SW corner dip to |X| 22.14).
   **Board slots (Stage 2 input, fin + 0.5 clearance all round):**
   S slots X 6.50..22.50 and −22.50..−6.50, Y −8.87..−6.22;
   N slot X −8.5..+8.5, Y −62.52..−59.87 (opens through the board's
   north edge — the fin enters the notch on the vertical drop).
2. **4 spring tongues (Z retention).** Lips on the E/W wall inner
   faces (X 25.75..28.25) at Y −50 and −20, underside at board top
   +0.15, Z 0.15..1.15; the board's edge snaps under them with the
   designed 0.5 working overlap (insertion sweep measures exactly
   12.000 mm³ = 4 × 0.5 × 6.0 × 1.0, and nothing else).
   **Stage 2 input:** keep the board's top edge strips component-free
   at Y −53..−47 and −23..−17 on both edges (0.5 in from the edge).
3. **North wall datum face** (board north edge on Y −62.37, per
   Stage B) for Y location.

**Stage 2 keep-outs from this stage (measured collisions):**
components must clear the three fin slots by ≥ 0.2 in plan.
Stage 1's nominal J1 at (17, −4.37) straddles the east fin slot
(fin∩J1 envelope 10.09 mm³ in the first verification run) —
**relocate J1 into the south-edge free band X −6.5..+6.5** (the
verification model places its envelope at X −3..+3, clear). F1
must sit north of the west slot: envelope Y −6.0..−4.4 used.

**Insertion:** vertical drop at the final pose, board BEFORE the
Wing boards (level insertion past seated Wings is impossible:
inter-tab gap 45.0 < board 52.5 — Z-check). Drop sweep vs
trays+infill = the 12.000 mm³ tongue snap only. FFC exit envelope:
the Z-check Flag-1 item stands (re-derive from the physical
connector at layout); the E/W sill at 2.45 keeps 0.25 under the
physical FH12 bottom (≈2.70).

## Slide switch — RELOCATED (deviation from Stage B, flagged)

Stage B put the switch on the bay east wall inner face (Y −34.37,
Z≈8). That site is unusable: the Wing tab crosses above the whole
E wall (board 4.70..5.90, J_WING at (27.00, −38.91)), so no useful
actuator height exists there. The switch moves to the **bay south
wall inner face, centred X 0**: mounting pad X −4.5..+4.5,
Y −3.37..−2.37 (1.0 proud of the face), Z 2.2..8.8 (infill part).
Verified envelope (body 8.5 × 3.5 × 4.0, X −4.25..+4.25,
Y −6.87..−3.37, Z 3.40..7.40) clears cells, board, cover and all
three removal sweeps (0.000 each); it floats above J1's new band,
wires drop to J2. Actuator centre ≈ Z 5.4 (Stage B's ≈8 was an
approximation; the S wall is the only face where a mid-height
actuator survives). Removal clearance: the middle cell's spring is
at its north end, so its south end never approaches the switch.

## Cover

Lid X ±30.25, Y −64.37..−0.37, underside 15.15 / top 16.65.
E/W skirts Z 11.15..15.15 (plate top 10.90 + 0.25 — the plate tips,
Wing tabs and the Fly all pass under the skirt line); south skirts
over the 4.45 sill spans; north skirt over the capped wall span
(above). **Fixing: 2 screws at the NORTH wall top (±24.25, −63.37)**
— Ø3.0 holes in the lid, Ø2.7 pilots in the wall. This replaces
Stage B's south-corner screw plan: the south corners are now
4.45 sills under the Wing boards and plate tips, so no screw can
reach them. (D-062 consequence 2's "spine insert pair" should be
read as this north pair.)

## Fly / gable — DECIDED: shift 1.8 north

Measured: tray wall outer face at X=38 is Y −56.04, wall material
−56.04..−49.72 at low Z; Fly (fused official bodies) bbox centre
Y −50.25 vs record centre −50.14. Unshifted, the USB mouth
(−54.40) would sit 1.64 behind the wall face (a tunnel). **Shift
the Fly 1.8 north → centre (38, −51.94); mouth at −56.20, 0.16
proud of the wall face (flush class).** EZmate route grows ≈1.8
(≈88.6 total, ≪ 170 cable). Cuts in tray-right: pocket
X 24.7..51.3, Y −56.6..−47.6, Z 2.9..10.0; USB opening
X 33.4..42.6, Y −57.5..−54.0, Z 6.1..9.5. Plate-right rim notch
X 32..44, Y −57.5..−48.5, Z 9.40..9.78 (Y extended past −50: the
Fly top sliver reaches Y −49.01, measured). Checks: Fly∩pocket
walls 0, Fly∩plate 0, mated USB plug (g17 reference bodies at the
same shift) ∩ tray 0, ∩ plate 0.

**Wing-side item (follow-up round — the Issue #299 respin batch
closed before this stage landed):** the Fly's south edge grazes
the right Wing board's north edge by 4.893 mm³ (asm X 38.39..45.96,
Y −49.11..−47.79, Z 4.70..5.90). Required: a rectangular notch in
the right Wing boards' (16R/17R) north edge, 7.57 wide × 1.32 deep,
at that asm span (file-frame transform from the established Wing
mapping), applied to the Stage-3 finals before ordering. The case
side is final as built.

## Main bosses, SW1, DLED, trackpad, south straightening

- Old H boss columns (asm ∓41.39, 64.40) cut; new bosses Ø8, top
  4.70 (= Main underside) at asm (∓31.89, 64.40) on the trays and
  (0, 9.27) on the infill (Pilot B washer centres). First-run
  "tray∩Main" volumes were an artefact of a downward extrusion in
  the checker (the solids were the boss/support tops at exactly
  4.70); with the Main at its true Z 4.70..5.90 the intersection
  is 0.000.
- SW1: Ø3.0 vertical plunger hole through the shell column at
  (−15.5, +64.50); plunger part: stem Ø2.9 Z 7.2..12.9, head Ø5
  Z 12.9..14.1. Pin bottom 7.2 leaves 1.3 above the Main top
  (5.90) for the future tact switch (a Main-respin item, D-063).
- DLED: Ø2.1 hole at (−4.0, +13.00); light pipe Ø2.0, Z 6.4..19.55
  (0.5 above the Main top).
- Trackpad: Ø44.6 seat recess cut into the shell island, floor
  Z 11.10; the Ø44 pad disc (11.20..12.70) checks 0.000 against
  the shell. Antenna band south of the Main (67.90 → wall inner
  79.70 = 11.8 PETG) stays plastic-only; H2/H3 at Y 64.40 are
  north of the band.
- South straightening: dent wall (Y 68.4..70.6) cut for |X| ≤ 50,
  band floor + new wall at Y 79.70..81.70, top 10.90.

## Verification (final run, verify-out3.txt)

| Check | Result |
|---|---|
| Case (with cover) vs Main (D-063 outline, Z 4.70..5.90) | 0.000 |
| Case vs cells (seated) | 0.000 |
| Case vs power board (+ J1/F1 envelopes, fin slots cut) | 0.000 |
| Case vs Fly / mated USB plug | 0.000 / 0.000 |
| Case vs trackpad disc | 0.000 |
| Case vs slide-switch envelope | 0.000 |
| Case vs Wings+underside | 84.76 total = 2 × 42.38: **J_WING study envelope ∩ the 2.45 E/W sill** (envelope bottom −0.15, Y −43.10..−34.95). Z-check Flag-1 artifact class: the envelope is a keep-out block, not the connector; physical FH12 bottom ≈2.70 clears the sill by 0.25. Accepted on that basis. |
| Fly vs Wings | 4.893 — Wing north-edge notch item (above), batched to #299 |
| Case vs case (all pairs) | 0.000 (boss/support contacts are face contacts at 4.70) |
| Removal sweeps (slide 2.0 + tip 35° about the end-face contact point, cover off) vs Wings | 0.000 all three cells |
| Removal sweeps vs case | each cell: exactly its own spring-fin box (175.8 / 176.8 / 175.8 mm³) — the spring working space; nothing else |
| Removal sweeps vs switch envelope | 0.000 |
| Finger zones (10 mm, Z 7.40..16.65) vs Wings | 0.000 (the Z-check criterion, preserved) |
| Finger zones vs case | working band Z 7.40..9.40: 0.000. Above it the zone is occupied by the plate tip (509.1 mm³, Z 9.40..10.90, the approved δ=9.5 plate) and, in the outer 2 mm (X 30.25..32.25), the shell cheek roof (152.0 E / 184.1 W). Recorded as the zone's real bounds in the final configuration; the grip band below the plate tip is clear. |
| Power-board vertical drop (Wings not seated) | 12.000 mm³ = the 4 tongue snap overlaps, by design; nothing else |
| Outline | 310.04 × 146.07; south Ymax 81.70 for all |X| ≤ 50; Z max 22.00 (shell/strips, unchanged) |
| Cover margins | top 16.65; cell top 14.65 → 0.50 under the lid underside (15.15); 5.35 under the provisional 22.00 datum |

Sweep sampling: 5° steps about the contact point, direction chosen
by free-end height (an early run's direction test was faulty for
the middle cell and produced a spurious below-floor sweep; fixed
and re-run — the final numbers above are from the corrected run).

## Open flags carried forward

- 22.00 datum provisional (Junana cap measurement, PO).
- FFC-1 (Stage B follow-up): re-select the ~100 mm straight FFC or
  D-042 custom FPC for the 11.5 channel; ≤0.30 Ω/lane acceptance.
- Wing north-edge Fly notch → follow-up round on the Issue #299
  Stage-3 finals (the respin batch closed in parallel).
- RECONCILE: Issue #303 Stage 2 (layout) completed in parallel
  with only the SW/SE 6×6 corner zones reserved for fixing — the
  fin slots, J1 relocation band and tongue strips decided here
  are NOT yet in the routed layout. The layout is still a draft
  (PR #304, un-ordered), so a layout revision can take them; if
  the slots prove unroutable, the case fixing falls back to
  corner features in the reserved zones. Parent to route.
- SW1 tact switch itself remains a Main respin item (D-063).
