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

## North-flush + PO-profile revision (2026-11-21)

PO instructions: (1) north edge flush — a straight flat face at the
outline limit Y −64.37, the curve removed; (2) north band at the
keytop datum Z22.00 across the full width, continuing south to just
before the keys; (3) centre (trackpad surround) and south at plate
top Z10.90, D-053 trackpad geometry intact; (4) transition slope
where space allows, cliff acceptable. This revision supersedes the
Stage-3D north slope cover and the 16.65 battery lid.

### What the curve was (measured, BREP slab sampling)

The tray north wall + old strip form ONE vertical face (tray
−2.65..10.90, strip 10.90..22.00, identical Y at every station)
whose PLAN trace is a circular arc: centre ≈ (0, −768), R ≈ 713;
sag vs the −64.37 plane: 8.9 mm at |X|=32, 5.6 at |X|=77, 0 at
|X|≈118; beyond that the outline is the angled end edge. The old
strip was a thin rim band (material within ~3 mm of the face, top
flat 22.00); the visible slope south of it was the tray's moulded
top. Shell-central's north boundary was a V of two straight
diagonals from (0, −0.37) — not curved; its centre ridge descended
22.00 (Y≈0) → 15.11 (Y=27) → 11.10 (Y≥32).

### Profile mapping onto parts

- Trays: north face filled forward to the plane in 2 mm columns
  (Z −2.65..10.90, +0.30 embed into the measured face). Result:
  flatness deviation 0.000 over |X| ≤ 117 (verify_north A).
- Strips REPLACED by band plateaus (Z 10.90..22.00): from the flush
  face south to the key line. South edge per 1 mm column = keycap
  capline − 1.0 mm clearance (caps.json: 16.5 mm cap envelopes at
  each key's own angle, extracted from the built plates, 21
  keys/side); cap-free columns take the nearest cap column's line.
  Transition on the halves is therefore a CLIFF at the key line —
  the run available is the 1.0 mm clearance only, no room for a
  slope (recorded choice per PO item 4).
- Battery lid: top raised 16.65 → 22.00 so the band is continuous
  over the bay; underside 15.15 and all skirts unchanged (cell
  clearance unchanged); screw holes lengthened. Lid lift path
  verified 0.000 at +2/+5/+10/+25 (the lid is independent of the
  band plateaus: its footprint |X| ≤ 30.25 meets the plateaus at
  |X| ≥ 30.25 face-to-face).
- Shell-central: centre profile applied — 22.00 at the bay south
  wall face (Y −0.37), linear slope to 10.90 at Y 20.0 (run 20.37,
  28.6°), flat 10.90 south of it; trackpad island exempted by the
  Ø47 keep-disc at (0, 48). SLOPE chosen for the centre (space
  allows: 20.37 run), landing 5.7 mm north of the island edge.
- Fly: shifted north to centre (38, −60.00) — a further 8.06 from
  the Stage-3D pose — mouth exactly flush with the new face
  (measured protrusion +0.00; a first pass at −60.11 measured
  +0.11 proud on the fused official body and was corrected).
  Pocket / USB opening / plate rim notch shifted with it.
  EZmate ≈ 96.7 mm ≪ 170 stock. Fly vs Wings now 0.000 (the
  Stage-3D 4.893 item is closed by this shift at the case side;
  the #299 north-edge notch stands as built there).
- Forced local adjustments: DLED light pipe re-trimmed to the
  slope surface at (−4, 13) → top 14.71 (= profile at Y 13);
  SW1 plunger re-trimmed to the 10.90 surface (stem 7.2..10.9,
  head 10.9..12.1); DLED hole re-cut after the slope work.

### Successor fixes (the partial build was NOT trusted as-is)

The predecessor's checkpoint (65a0a8fbb) plus dirty tree was
assessed: its verify-out2.txt is internally inconsistent (fin-box
breakdown ≠ totals; tongue overlap vanished) and came from a
partial build — discarded. The build was re-run from the scripts;
two real defects in the revised design were then found by
measurement and fixed in build_case3d.py:

1. **Centre slope hole.** The profile cut alone deletes the
   centre skin wherever its underside (~2.1 under the old ridge
   top) sits above the new profile: measured hole along the spine
   |X| ≤ ~9, Y 6..27, plus the apron widening (diag_grid.py, old
   vs new top-Z maps). Fix: a slope SHEET whose top is the
   profile (2.0 thick), limited to the pre-cut shell's plan
   footprint (downward sweep): zone A |X| ≤ 22.4 full 2.0
   thickness; zone B (lobe bands 22.4 < |X| ≤ 30.25) floored at
   the plate top 10.90. After the fix the spine slab audit
   (verify_north F) shows shell top = profile at every 2 mm bin
   Y 0..22. Zone B produced no surviving sheet — the old shell
   had only a ≤1.94 mm-deep strip sliver along the bay wall
   there; that region's surface is now the plate top 10.90,
   which matches the centre = plate-height reading.
2. **SW1 boss left at 11.10.** The trackpad keep-disc (r 23.5 at
   (0,48)) also exempts the SW1 boss (centre distance 22.6) from
   the profile cut; the re-trimmed plunger intersected it
   (0.211 mm³). Fix: local cap cut over the boss → shell top at
   the SW1 column 10.90, plunger vs shell 0.000.

### Verification (final runs: verify-rev2.txt, verify-north-rev2.txt, audit-rev.txt)

| Check | Result |
|---|---|
| Case (with cover) vs Main / cells / power board / Fly / trackpad / switch envelopes | 0.000 (all) |
| Case vs Wings+underside | 84.76 = 2 × 42.38, the accepted J_WING envelope ∩ E/W sill artifact (physical FH12 clears by 0.25), unchanged |
| Case vs case | 0.000 (no nonzero pair) |
| Removal sweeps ×3 (cover off) vs case | exactly each cell's own spring-fin box (175.806 / 176.803 / 175.806); vs Wings 0.000; vs switch env 0.000 |
| Power-board vertical drop | 12.000 = the 4 tongue snap overlaps, by design |
| Outline | 310.04 × 146.07; Z max 22.00; south Ymax 81.70 for |X| ≤ 50 |
| North face flatness | max deviation from −64.37 = 0.000 over |X| ≤ 117 |
| Band tops / lid top | 22.00 at all sample columns / 22.00 |
| Keycap clearance | cap solids vs case 0.000 unpressed (top 22.00) AND pressed model (top 19.00, 3.0 travel — plan-invariant, verified with solids at both heights) |
| Lid lift path | 0.000 at +2 / +5 / +10 / +25 |
| Fly mouth protrusion | +0.00 (flush); Fly/plug vs tray, plate, band 0.000 |
| Shell centre profile (spine slab) | top = profile at every bin Y 0..22; DLED pipe top 14.71 = profile at Y 13; pipe/plunger vs shell 0.000 |
| Finger zones (full, Z 7.40..16.65) vs case | E 1261.330 / W 1263.904 — changed from Stage 3D (661/693), see disposition 4 |
| Trackpad island probe | shell vs pad disc 0.000 |

### Open dispositions (PO confirmation pending; defaults used and stated)

1. **Key clearance value.** Design offset = capline − 1.0 mm per
   1 mm column. Because the plateau south edge is a 1 mm
   staircase and the caps are rotated rectangles, the true
   minimum solid-to-solid distance measures **0.571 mm** (both
   sides, audit_rev §3) — positive everywhere, no contact in
   either key state (solids check above). Default: accept
   1.0 mm nominal / 0.571 mm true minimum. Cap size itself is
   assumed 16.5 mm (17-pitch class; g17 switch envelope 15.8);
   the Junana physical cap measurement is still open and would
   shift these numbers by the cap-size delta.
2. **Lid independence.** The battery lid is a separate part from
   the band plateaus and lifts vertically clear of them
   (verified). Its top is part of the band surface (22.00) when
   seated. Default: keep independent (battery access does not
   disturb the band).
3. **Centre-height reading.** "Centre at plate height" is read
   as the shell field at plate top 10.90 around the trackpad and
   to the south. The battery lid over the bay is NOT at 10.90 —
   it sits at the band height 22.00 (it is part of the north
   band, and its underside must clear the 14.65 cell tops).
   Default: bay lid = band (22.00); trackpad surround + south
   field = 10.90.
4. **Finger-zone bounds.** The full-zone volume vs case rose
   (661/693 → 1261/1264) because the band plateaus now occupy
   the zone slice above the plate top outboard of the bay
   (X 30.25..32.25), and the working band Z 7.40..9.40 gained
   32.822 (E) / 34.802 (W) of tray-right/left deck outboard of
   the bay wall, south of the relocated Fly pocket. Inboard of
   the bay walls (|X| ≤ 30.25) the working band remains
   **0.000 both sides** (diag_band.py) — the grip criterion
   holds where fingers actually reach the cells. Recorded as
   the zone's real bounds in the final configuration.
5. **Keep-disc exemptions.** Inside the Ø47 keep-disc the D-053
   island keeps pre-revision heights: island apron top 12.55
   measured at X~20, Y 20..35 (old 13.85 — partially trimmed),
   and one spine-foot land at top 15.15 in the ring
   22.3 < dist((0,48)) < 23.5 (audit_rev §5). Both are island
   seat structure, below/around the pad (pad top 12.70);
   the shell slab at X ±3, Y 26..30 is the pad seat opening —
   empty in the Stage-3D shell too, not a regression.
6. **Old strips.** 1.42k of each old strip's 1.45k lies inside
   the new strip+shell; 0.02k/side removed (the slivers south of
   the key line not absorbed by the plateau/lobe transfer).

Renders: case296-3d-top.png / case296-3d-persp-open.png /
case296-3d-persp.png overwritten; case296-3d-section-centre.png
added (Y-Z at X=0: band 22.00 over the bay, slope to the trackpad
field at 10.90, pad at 12.70).

## Lid-integral north shelf (PO decision 2026-11-21) — implemented + verified

**PO decision of record (2026-11-21):** 「天地蓋部分は北辺棚と一体で作ってくれ。電池交換の時は北辺棚を外して交換する」 — the battery lid is made INTEGRAL with the north band/shelf as ONE removable part; battery replacement = remove the whole north shelf and swap the cells. This supersedes open disposition 2 of the north-flush revision above ("keep the lid an independent part").

### Part boundary (defined and measured)

The new part **`north-shelf`** = fuse(previous `battery-cover`, `strip-left`, `strip-right`), minus the new screw holes. One solid (verified: solids = 1), bbox X −152.25..152.25, Y −64.37..−0.37, Z 7.80..22.00, vol 99.22k mm³.

- North boundary: the flush plane Y −64.37; the ends follow the tray outline (plateau columns to |X| = 152.25).
- South boundary: the lid's south edge Y −0.37 at centre — meeting the shell slope's TOP edge, so the centre slope (22.00 → 10.90) stays with `shell-central` unchanged — and the key line (capline − 1.0 mm per column) on the halves, exactly as built in the profile revision.
- Underside: centre = the lid underside (Z 15.15) + the E/W bay skirts (bottom 11.15); outboard = the plateau underside (10.90).
- **Bridge over the bay E/W sills, measured:** in the wall bands (|X| 22.50..30.25) the shelf's lowest point is the skirt bottom **Z 11.15**; the plate below tops at **10.90 → clearance 0.25**; the Wing board below tops at **5.90 → clearance 5.25**. Shelf vs Wings+underside (incl. J_WING envelopes) = **0.000**; shelf vs plates = **0.000**. (The Wing boards do not pass under the shelf in the removal path either — see trajectory below.)

### Fixing — decided: 4× flat-head M3 in the plateaus; the centre wall pair is REMOVED

The as-built lid pair (±24.25, −63.37, into the tray north wall top) **cannot be retained in any standard form**: its axis sits 1.00 mm from the flush north face, so any screw head of radius > 1.0 stands proud of the outline (a Ø5.5 flat head by 1.75 mm; even a Ø3.0 clearance hole breaks the face by 0.50 mm). The earlier stages never modelled heads — the pair only ever worked as bare holes. The pair is removed from both the shelf and the tray wall (the wall pilots are filled back).

**New fixing: 4× flat-head M3, countersunk flush in the band plateaus, all on one line Y = −61.37, pairs at X ±55 and ±85.**
- Head rim at Y −64.12 — 0.25 inside the flush face; head top flush at Z 22.00 (verified with an undersize-modelled head envelope: top Z 22.00, rim −64.07 at r 2.70, vs shelf/caps 0.000).
- Pilots Ø2.7 into the tray north fill, Z 4.0..10.90; **pilot fill fraction 100.0 %** at all four positions (the fill under the plateau is solid there — no arc voids); pilot shaft cylinders vs Wings/plates = 0.000. Ø2.7 pilots into printed PETG for M3 self-tap/form, same practice as the previous lid fixing.
- Span justification: the old pair alone left 130.8 mm cantilevers to each end; the new layout gives centre span 110, side spans 30, end cantilevers 70 — and the lid portion additionally rests on the bay walls (N wall top 15.15; S wall top 15.15 for |X| ≤ 10.90; E/W skirts over the sills) and is located by the skirt/wall sandwich, so the screws clamp, they do not locate.
- **Driver access, assembled:** vertical Ø6.35 bit cylinders from Z 22 to 55 vs keycap solids = **0.000** in BOTH cap states (unpressed and pressed) at all four screws; axis-to-capline distance 21.36 mm (worst, +85), 21.89 (−85), 32.90 (+55), 33.43 (−55).
- Alternatives measured and rejected (plan note `shelf-plan.md`): relocating the centre pair into the lid top (bosses foul the power-board drop path and the cells' tilted-insertion arc); south-wall centre screws (intersect the shell slope); grub/set screws from the north face (no clamp, wall too thin); keeping the centre holes as pure locators (unnecessary — skirts locate).

### Fly / USB — undisturbed

The Fly stays in the tray-right pocket (unchanged); shelf vs Fly = **0.000**; the shelf's removal path never touches it (trajectory below includes the Fly and a seated plug envelope: both 0.000 at every lift step). USB opening (X 33.4..42.6, Z 6.1..9.5, in the tray wall below the shelf) is fully usable with the shelf on AND off: plug envelope vs shelf = 0.000, vs the shelf-less case = 0.000. Fly mouth protrusion re-measured **+0.00** (flush).

### Removal motion and verification (`verify_shelf.py`)

Removal motion assumed: remove the 4 screws, then a **pure vertical (+Z) lift** of the shelf (no tilt, no slide). Battery swap then proceeds with the shelf OFF, using the established cell motion (slide 2.0 toward the spring end + tip 35°).

| Check | Result |
|---|---|
| Shelf = 1 solid; bbox / Z ≤ 22.00 | 1 solid; X ±152.25, Y −64.37..−0.37, Z 7.80..22.00 ✓ |
| Shelf vs old 3-part union | shelf-minus-old 86.2 mm³ (≈ the filled centre holes, 96.8 nominal), old-minus-shelf 351.5 (≈ the 4 new holes+countersinks, 386.6 nominal); residual ≤ 0.03 % = cross-build boolean noise |
| Fixing voids (pilot / hole / countersink), 4 screws | 0.000 / 0.000 / 0.000 at all four |
| Head envelopes: top / rim / vs shelf / vs caps | 22.00 / −64.07 / 0.000 / 0.000 (both cap states) |
| Driver bit Ø6.35 vs caps | 0.000 unpressed and pressed, all four |
| Bridge: skirt-to-plate / skirt-to-Wing-board | 0.25 / 5.25 |
| **Shelf lift trajectory** (+2/+5/+10/+25) vs rest of case, caps (un+pressed), trackpad, Fly, plug, Wings+underside, Main, cells, power board, switch envs | **0.000 everywhere, all steps** |
| Battery sweeps, shelf OFF (slide 2.0 + tip 35°) | vs case = own-fin box only (175.806 / 176.803 / 175.806); vs Wings 0.000; vs switch env 0.000 |
| Finger zones, shelf OFF | outboard relief 0.000 both; inboard working band (Z 7.40..9.40) **0.000 both** (the full-height zone still contains the known plate-tip occupation 509.080 above the band, Z 9.40..10.90 — unchanged) |
| Case vs Main / cells / power board / Fly / switch envs | 0.000 |
| Case vs Wings+underside | 84.760 = 2 × 42.38, trays only (accepted J_WING envelope artifact, re-confirmed; shelf contributes 0) |
| Case vs case | none > 0.01 |
| Power-board drop re-check (after the tray pilot changes) | 12.000 = tongue snaps only ✓ |
| Outline / north flatness | 310.04 × 146.07, Z −2.65..22.00; flatness deviation 0.000 over \|X\| ≤ 117 |

**Carried observation (pre-existing, NOT a shelf regression):** the table now computes plunger-sw1 vs the trackpad probe disc (Ø44 envelope) = **5.806 mm³** — earlier tables never included the plunger in the case set, so this pair was never computed before. The plunger is untouched by this revision. Against the real Ø40 Cirque module the plunger head (Ø5, centre 22.64 from the pad centre) clears by 0.14 mm in plan; the 5.806 is against the Ø44 island-envelope probe only. Flagged for the record; no change made (out of this revision's scope).

### Parts / files

Parts 11 → **9**: `north-shelf.step/.stl` replaces `battery-cover` + `strip-left` + `strip-right` (removed from the tree). Renders: `case296-3d-top.png` and `case296-3d-persp-open.png` overwritten, `case296-3d-persp.png` refreshed, **`case296-3d-shelf-off.png` added** (shelf lifted 95 mm above its seat, bay open with cells — the battery-swap state).

## Addendum 2026-11-21 (evening) — P0/P1 revision (Opus design review fold-in)

PO decision: 「P0/P1を反映した改訂を回す」. Review of record:
`files/case296-design-review-opus-2026-11-21.md`. Plan:
`.issue296-runtime/p0p1-plan.md`; scripts `diag_p0p1*.py`,
`verify_p0p1.py` (+ `verify_p0p1b.py`), `render_p0p1.py`,
`export_caps_stl.py`. The shelf stays ONE part: bbox
X −153.25..153.25, Y −64.37..−0.57, Z 8.00..22.00, vol 96.64k mm³,
1 solid. Assembly invariants unchanged: 310.04 × 146.07,
Z ≤ 22.00, north flatness deviation 0.000.

### P0-1 — tolerance stack-up, shelf south edge (nominal gap 1.30)

| term | value | basis |
|---|---|---|
| cap northern-extent growth | ≤ 0.20 | cap 16.5 × 16.5 ASSUMED, size tolerance ±0.25/dimension (ASSUMED); worst northern-row key angle 60° |
| cap seating play | 0.15 | assumed |
| shelf edge print tolerance (FDM PETG) | 0.20 | assumed |
| shelf placement play (southward) | 0.30 | 0.2 design mating gap + screw radial play, combined bound |
| plate placement | 0.10 | assumed |

Worst-case sum 0.95 → nominal 1.30 leaves **+0.35**; RSS typical
0.45 → typical gap ≈ 0.85. **PRINT GATE (PO-side, NOT done): the
Junana keycap physical measurement — the Z22.00 datum and the
16.5 cap assumption stay provisional until then.** Implemented
edge: per-cap-rectangle disc-offset keep-out (radius 1.30) — the
1.0 staircase is gone. Measured: shelf↔caps min distance **1.300**
in BOTH cap states, intersections 0.000. Side effect: the −0.05
pre-trim south limit lets one more end column pass the ≥1.0 depth
rule, so the shelf X extent grows 152.25 → 153.25, still inside
the tray outline (overhang probe `diag_p0p1c.py`: the only shelf
points without tray below are 5/side on the diagonal end edge —
the established column-step approximation, unchanged in kind;
none in the new column).

### P0-2 — screw row Y −60.37, rim 1.25 + heat-set inserts

Row −61.37 → −60.37. Countersink Ø5.5 top flush at Z22.00; rim
= 64.37 − 60.37 − 2.75 = **1.25 nominal** (undersize-head
envelope Ø5.4: 1.30 measured); head envelope vs shelf and vs caps
0.000 both states. Axis-to-capline: +55 → 31.90, −55 → 32.43,
+85 → 20.36, −85 → 20.89 (the trade-off the review warned of;
Ø6.35 driver bit vs caps 0.000 everywhere, pressed and
unpressed). Insert landings: at ±55 the tray material at the hole
is solid (fraction 1.000), min wall ≥ 1.50 (+55) / ≥ 1.75 (−55)
by ring grow test. At ±85 a 0.207 mm³ sliver void sat at the
hole's top south rim (the plate-seat step) → boss r4.6,
Z 4.0..10.90 added; ring fraction 1.000 after the plate trim
(clipped to the outline). Two boss trims: the flush plane (the
raw cylinder would stand 0.60 proud of the north face) and the
Wing bodies — the board's north corner sits in a tray recess at
(±85, −56.1, Z 4.70..5.90) and the raw boss filled 0.611 mm³ of
it; caught by the verification interference table (the
plan-stage probe had not tested the wings), fixed by trimming
the boss with the Wing solids; boss wall south of the hole in
the board's Z band ≥ 1.92. **Fixing spec of record (changed):
M3 × 5.7-class heat-set inserts, hole Ø4.2 × depth 5.9, insert
top flush with tray top 10.90 (bottom 5.2); screws M3 × 14
flat-head machine screws (DIN 965 class), engagement ≈ 4.0 in
the insert. Shelf holes Ø3.4 clearance + countersink. The
direct-tap pilots are gone.**

### P0-3 — bed fit: ONE PIECE, 45° diagonal on a 256-class bed

Measured on the FINAL shelf outline hull (12 vertices): rotated
bbox 235.6 × 235.6 at 45°. Slack: 220-class **−15.56 (no fit)**,
256-class **+20.44** (≈10.2/side, brim fits), 300-class +64.44.
A single-piece path exists → no 3-piece split. Bed classes are
standard sizes (design assumption per the task rule); the PO's
actual printer bed is not recorded — on a 220-class the split
fallback applies (joint cross-section at |X| 30.25 measured
anyway: common material Y −64.37..−5.88 in the Z≥15 slab).

### P1 dispositions

- **Offset south edge** — done (P0-1).
- **Inserts + machine screws** — done (P0-2).
- **Mating gaps 0.2** — plateau underside 11.10 vs plate top
  10.90 = 0.20; lid underside 15.35 vs N wall top 15.15 = 0.20;
  N skirt bottom 8.00 vs capped wall top 7.80 = 0.20;
  shelf↔shell min distance 0.200. (E/W skirt bottoms already had
  0.25 over the plate — left.) Bridge clearances unchanged:
  skirt↔plate 0.25, skirt↔Wing board top 5.25.
- **Pry notches ×2** — X [121, 129] / [−129, −121] on the angled
  end edges (the outline leaves the flush plane at |X| ≈ 119.5),
  cut Z 11.10..14.60; shelf material inside the notch boxes
  0.000; the flush plane in the bands is untouched (0.000) — the
  notch opens on the end edge only (the review's own fallback
  for its P2-13 conflict).
- **Plunger head Ø5 → Ø4** — plan clearance to the real Ø40
  module 0.14 → **0.638 measured**; vs the Ø44 PROBE disc the
  intersection is 3.305 (was 5.806).
- **Renders** — redrawn WITH keycaps fitted (42 caps), top view
  NORTH-UP (`files/case296-3d-top.png`; persp / persp-open /
  shelf-off refreshed; centre section refreshed). The first
  perspective set came out blank (camera rotation-mode bug after
  the roll fix) — caught on read-back, fixed, re-rendered.
- **Verbalisation doc** — caveat header added to
  `files/case296-cover-design-2026-11-21.md` (coordinate error /
  inverted PO preference order / invented requirement / stale
  premises, pointer to the review). Body untouched.

### Full re-verification (`verify_p0p1.py` + `verify_p0p1b.py`)

Shelf lift +2/+5/+10/+25: 0.000 vs everything. Battery sweeps
shelf-OFF: vs Wings 0.000 (own-fin boxes only; the finger working
band Z 7.40..9.40 = 0.000; the full-height finger-zone figure
509.080 is the known plate-tip occupation above the band,
unchanged). Interference table: all 0.000 except case vs
trackpad 3.305 (plunger vs the Ø44 PROBE disc; vs the real Ø40
module 0.638 clear) and trays vs the J_WING study envelope
42.380/side — the accepted artifact, back at the pre-revision
value after the boss trim. Power-board drop re-check: 12.000 =
tongue snaps only. Fly: mouth protrusion +0.00; plug 0.000 in
both shelf states.

Assumption register: the review's general claims are treated as
design assumptions — extrusion width ~0.4 (enters only via the
rim ≥ 1.25 requirement), bed classes 220/256/300, cap size
tolerance ±0.25. Everything measurable from the model was
measured (bed fit included, on the final outline).

## South unification — plan A addendum (2026-11-22)

Implementation of the Opus proposal
`files/case296-south-unify-opus-2026-11-22.md` §3 (plan A, PO
adoption 2026-11-22), as a new SOUTH UNIFICATION section in
`build_case3d.py` (after the inserts, before exports). All inputs
re-measured from the built solids in-build (the north_fill
pattern). Probes: `probe_south.py` / `probe_shell.py`.
Verification: `verify_south.py` + `verify_south_fix.py` +
`verify_south_loc.py`; regression `verify_p0p1.py` unchanged.

### New outline numbers

- Diagonal refit on the built trays (least squares over the tray
  face, |X| 61..70): Y = 128.2161 − 0.7798|X|. Intersection with
  Y_S: Xi 59.650 (proposal 59.636). R4.0 tangent points:
  **Xt1 58.275** (proposal 58.247), **Xt2 60.735** (proposal
  60.726); arc centre (±58.275, 77.700). S(X): 81.700 straight for
  |X| ≤ 58.275; arc to (60.735, 80.855); existing diagonal beyond.
- Post-change profile (0.5 mm slabs on the fused case): straight
  zone min = max = **81.700**; arc zone matches the built arc to
  −0.001 at every sampled column (slab west-edge comparison);
  junction step at Xt2 **+0.023** (arc endpoint vs the pre-change
  face interpolated at Xt2 — the diagonal-fit residual, recorded).
- Assembly outline unchanged: **310.04 × 146.07**, Z −2.65..22.00;
  north flatness deviation 0.000 (north side untouched).

### Per-item disposition (proposal §3)

1. **§3-1 outline S(X)** — DONE as specified. R1 closed: profile
   at |X| 50.25 = 81.700 (was 74.286; notch depth 7.414 → 0).
   Shoulder peak 81.702 abolished (clip at S(X)); the −0.88 dip
   is inside the arc/fill region.
2. **§3-2 south band** — DONE. Skin Z 9.30..10.90 (1.6 top skin,
   underside 9.30), top measured flush 10.90 across Y 70..81.7
   at X = 0/30/45 (was trench floor −0.65). North boundary
   70.000 for |X| ≤ 41.01 and over the 41..50 run; plate + 0.30
   beyond — built as station chords, then carved with the plate
   plan dilated by exactly 0.30 (2D offset of the plate top
   face): the first build's chords cut across the plate's step
   corner at |X| ≈ 50 (measured added-material↔plate gap
   0.043); after the carve the gap is **0.300** with
   intersection 0.000. Skin split at the part boundaries with
   exact 0.30 seams (X −6.15..−5.85 and 12.85..13.15). Antenna
   cavity preserved: material in the trench box (X=0, Y
   70..79.7, Z 0..9.30) = 0.000; wall inner face (measured
   below the skin) 79.700 → **band depth 11.800** (Main south
   edge 67.900); Main plan gaps: shell edge 1.80, skin boundary
   2.10, outer line 13.80; case vs Main 0.000 (full table).
3. **§3-3 shell south edge** — DONE, method changed on measured
   evidence. Probing at 0.25 mm showed the centre face is
   **69.202** flat for |X| ≤ ~39.25 (the coordinator's 69.288
   exists only as a ~0.3-wide ridge at |X| ≈ 39.4; corners
   69.700 from |X| ≈ 39.6). A slice-translate would have copied
   the step (69.614..69.700), so the edge was built with a
   face-following fill to exactly **69.700** (prism Z
   8.90..10.90, 0.30 embed), measured 69.700 at every sampled
   station |X| ≤ 41.25. Extension actually required: 0.498
   (not 0.412). Residual: at |X| ≤ ~3.5 the trackpad seat floor
   (Z 11.10) keeps its own edge at 69.202 above the fill — a
   0.10-high sliver inside the seat recess under the pad rim;
   the field edge (the proposal's subject) is the straight
   69.700 line.
4. **§3-4 south face by the trays only / infill retreat to
   79.500** — NOT implemented, with measured reason: neither
   tray reaches X −6..+13 (tray-left ends at −6.0, tray-right
   starts at +13.0), so the centre wall segment is necessarily
   infill-formed; retreating it to 79.500 would open a
   19.0 × 2.2 through-slot in the south wall. The centre
   segment stays flush at 81.700 and the C0.5 chamfer runs
   across it continuously, so the one-line intent holds. The
   wall butt seams at X = −6/+13 also stay (a 0.30 through-slot
   in the outer wall would be a hole, not a joint); the 0.30
   joint rule is applied on the band surface where §3-2/§3-3
   define joints — shell↔skin 0.300 measured, plate↔skin
   0.300 measured, skin slice seams 0.30.
5. **C0.5 chamfer** — DONE along the unified edge: triangular
   cutter on the straight, annular-cone cutters about the arc
   centres (keep radius 4.0 @ Z 10.40 → 3.5 @ Z 10.90). Top
   slab profile (Z 10.85..10.95) reads **81.250** at
   X = −30/0/+30/+55 = the C0.5 line at the slab bottom.
   Range scoped to straight + arcs (the proposal's "unified
   south top edge"); the diagonals beyond Xt2 keep their
   existing edge, with a ≤0.3 blend where the cone cutter
   fades at the tangent point.
6. **Unchanged items** — north side (flatness 0.000; shelf,
   fixing, cap clearances re-verified identical), Wing
   positions / δ, wedge groove (skin starts at Y 70.000, the
   groove is Y < 70), plate seams (plates untouched), Fly/USB
   (mouth +0.00, plug 0.000 in both shelf states), Z ≤ 22.00.

### Full re-verification (final models)

`verify_p0p1.py` output byte-identical to the pre-change run:
shelf lift +2/+5/+10/+25 all 0.000; battery sweeps shelf-OFF =
own-fin boxes exactly (175.806/176.803/175.806); power-board
drop 12.000; interference table all 0.000 except the two
accepted artifacts — case vs Wings+underside **84.760 =
42.380/side** (J_WING study envelope) and plunger vs the Ø44
probe disc **3.305** (vs the real Ø40 module 0.638 clear);
case-vs-case no nonzero pairs; shelf↔caps 1.300 both states.
Note: `verify_south.py` S3's "wall inner face 75.000 / depth
7.100" line is a contaminated measurement (the skin slab fell
inside its own probe box) — superseded by `verify_south_fix.py`
F1 (79.700 / 11.800). F2–F4: plate gap 0.300, arc −0.001,
junction step +0.023, as above.

Renders: top (north-up, keycaps fitted), persp, persp-open and
shelf-off refreshed; NEW south-side view
`files/case296-3d-south.png` — the south wall reads as one
straight line with a continuous top edge.

## Hinge + latch (A) and centre-slope removal (B) — addendum (2026-11-22)

PO decisions of 2026-11-22, one round. Plan note:
`.issue296-runtime/hinge-plan.md` (committed first, c0831653c);
build `build_case3d.py`; verification `verify_hinge.py`
(final run `verify-hinge3.log`); renders refreshed + NEW
open-state view `files/case296-hinge-open.png`.

### (A) Premise change

The shelf no longer comes off; it stays attached and OPENS.
This supersedes the removal half of the 2026-11-21 lid-integral
decision; the lid stays integral with the band — one part —
either way. The 4-screw fixing is abolished (below).

### (B) Centre slope removed

PO verbatim: 「中央の傾斜は無しで。無駄に複雑になるだけだ」.
The shell-central's sloped transition (22.00 → 10.90 over
Y −0.37..20) is replaced by a straight step: the profile cut is
flat at 10.90 for Y ≥ −0.37 (trackpad keep-disc exempt, as
before), and the slope sheet is replaced by a flat sheet
(Z 8.90..10.90, same footprint machinery) restoring any skin
the flat cut deletes. This makes the cliff the design — it
supersedes the slope element of the 2026-11-21 profile (whose
text had allowed a cliff). Dispositions: the DLED light pipe
at (−4, +13) is re-trimmed 14.71 → 10.90 (it now meets the flat
field; pipe∩shell = 0.000); the shelf's south edge at centre
now meets the vertical step (0.20 gap disposition unchanged);
SW1 boss/plunger re-verified (plunger∩shell = 0.000, rest
surface 10.90); trackpad seat unchanged. Audit (`audit_flat.py`):
centre-field top = 10.90 at every sampled column outside the
trackpad disc, no skin holes. One fix during (A) verification:
the flat sheet overlapped tray-left's top by 3.993 mm³ at the
shell's north-west (the south-tip pair measured 0.000) — the
shell is now trimmed by the final trays/infill at the end of
the build; pairwise is 0.000 again.

### Hinge placement — measured, not assumed

- The only straight southern boundary of the shelf is the
  lid's south edge (Y −0.570): plateau south edges measure
  −10.219 (X ±40), −29.849 (±60), −33.313 (±100). The Opus
  spec's knuckle candidates at X ±40/±100 cannot reach a
  straight axis there. Axis A = (Y −0.57, Z 19.30) on the lid
  edge line, wrap radius 2.70 (cylinder top exactly 22.00).
  (The spec of record's own geometry argument puts the axis on
  the south edge; a north-edge axis lands inside the flush
  north face — deviation from the round brief's "north edge"
  phrase, per the spec.)
- Wall posts at the spec-scale spans (X 14..18 / 25..28) are
  impossible: the Wing boards' south edges cross the bay south
  wall band (Y −2.37..−0.37, Z 4.70..5.90) at every |X| ≥ 11.14
  (measured post∩Wing 9.47 / 7.20 mm³); the shell does not
  reach the hinge line at those X either (north edge Y 22.71
  at X16, 29.64 at X20). The hinge groups therefore sit
  centrally on the board-free wall span (|X| ≤ 10.90, top
  15.15): per side boss X ±(0.5..4.0), shelf knuckle
  ±(4.3..8.6), boss ±(8.9..10.9).

### Hinge design (numbers)

- Bosses: post (Y −2.37..−0.37, Z 4.0..19.30, on the wall) +
  wrap cylinder r 2.70 on A. Infill carries both boss1s and
  boss2-right; tray-left carries boss2-left.
- Pins: TWO, one per side, Ø2.0 non-magnetic (SUS316/brass —
  ferromagnetic parts near the Wing Hall sensors are
  prohibited). Shaft from the boss1 inner face (|X| 0.5) to
  tip |X| 10.80 in the boss2 blind hole (floor 10.85); head
  flange Ø3.4 × 0.4 at the centre (X 0.1..0.5 / −0.5..−0.1 —
  the 1.0 centre gap takes both flanges side by side). Each
  pin is inserted from the bay centre outward after the
  plates are on, captive between head and blind floor. (A
  single centre-spanning pin measured 0.628 mm³ into the
  lid's south edge at the centre gap — the axis lies on the
  edge line — hence two pins.) Holes Ø2.1; knuckle holes
  slotted +0.3 in Y, so closed positioning is by the north
  sandwich + underside, not the pin. Knuckle wall
  (5.4 − 2.1)/2 = 1.65. Pin fit measured: 0.000 vs infill,
  tray-left and shelf.
- Shelf notches at the boss spans (boss ±0.3; boss1 notch from
  X 0.0 so the pin heads sit inside): lid notch
  Y −3.5..+2.4, Z 15.0..22.3; skirt notch Y −2.67..−0.17,
  Z 10.9..15.6.
- Opening stop: a post on the shell-central (X −0.45..+0.45,
  Y +1.88..+3.38, top Z 19.10) in the gap between the boss1
  wraps (a first site at X −2.6..−0.8 measured 0.255 mm³ into
  the west wrap). The standing shelf's lid top edge lands on
  it. **Final opening angle: 95.0°** (first shelf×shell
  contact in the arc sweep, exactly on target).
- Arc-sweep finding, fixed: the E/W skirt fins
  (X ±(28.25..30.25), Z 11.15..15.35) hang with their north
  faces coplanar with the north wall's inner face (Y −62.37);
  their bottom corners (radius 62.33 > 61.80 from A) clipped
  the wall's top inner corner (0.700 mm³/side at 2.5°). The
  fins' low north ends are trimmed to Y −61.57 (max radius
  61.54 < 61.80); the lid above is untouched.

### Latch design (numbers)

One finger latch, right side (per spec), line Y = −61.00.
NEW printed part `latch-slider` (10 parts total): body
X 72..92, Y −61.3..−55.7, Z 19.8..22.0 in a groove cut into
the plateau top (X 67.7..96.3, Y −61.8..−55.2, floor 19.8;
grip grooves on the slider's top, top stays flush 22.00);
stem X 81..83, Y −62..−60 down a web slot in the plateau
(X 76.2..87.8, Y −62.2..−59.8); collar Ø4.4 at (82, −61),
Z 9.30..10.00. Receiver (cuts in tray-right under the +85
boss): pocket X 75..89, Y −63.3..−58.7, Z 9.25..10.00;
keyhole entries Ø5.0 elongated +0.3 north at stem X 78.2 and
85.8, Z 10.00..10.95; neck X 80.2..83.8, Y −62.15..−59.85,
Z 10.00..10.95. Locked = slider centred: collar trapped in
the pocket under the tray web (collar top 10.00, tray top
10.90; retention overlap (4.4 − 3.6)/2 = 0.4/side in plan).
Release = slide ±3.8 to either entry. Centring: one PETG
finger under the slider body (arm ~7 × 0.6, tooth into a dip
in the groove floor) — unloaded in the dip at centre
(locked), deflection 0.75 at full travel, strain ≈ 1.3%,
return ≈ 0.5 N vs the 0.28k mm³ slider. Proof (rigid model):
slider centred + pair lifted 1 mm → collar×tray 3.202 mm³
(ENGAGED); at either entry → 0.000 (RELEASED); slider vs
tray/plate/shelf = 0.000 at centre; at the slid positions the
only intersection is the finger tooth's 1.125 mm³ = its
working deflection volume, by design. (First build had the
collar 0.30 too tall — 1.601 mm³ beside the neck; collar top
set to 10.00, stem extended into it.)

### Abolished fixings — dispositions

The 4 plateau screw holes + countersinks: removed. The 4
tray insert holes (Ø4.2 at (±55/±85, −60.37)): removed. The
pry notches (X 121..129): removed (the shelf is never pried
off; it opens). The ±85 tray bosses stay as geometry: −85
plain, +85 hosts the latch receiver.

### New swap step list — 12 actions (baseline 20)

1. Slide the latch to an entry (finger, ~4 mm).
2. Raise the shelf to the 95° stop.
3–11. Cells (9, unchanged motions: slide 2.0 toward the
   spring end, tip 35°, lift; reverse to fit).
12. Lower the shelf holding the slider at the entry; release
    → the finger centres it → locked.
Tool-less; no driver, no ~90 screw rotations.

### Durability (assumptions with numbers)

Weekly opening ≈ 50 cycles/year. Hinge: Ø2 metal pins in
Ø2.1 holes, full-circumference PETG knuckles/bosses (wall
1.65) — at ~100 open/close cycles/year the bearing stress is
negligible and wear is not life-limiting; the pins are
captive (head + blind floor, 0.05 axial play). Latch: collar
engagement as above; the centring finger is unloaded in the
locked state (creep-safe by the spec's rule), peak strain
≈ 1.3% only during the slide. Stop post: the shelf's
tip-over moment at 95° is small (CoM ≈ 3.6 mm south of the
axis vertical); the post's contact face is 0.9 × 1.5.

### Verification (verify_hinge.py, final run)

- Closed: case parts pairwise 0.000 (all 10 parts); case vs
  internals 0.000 except the two accepted artifacts (J_WING
  envelope 42.380/side; plunger vs Ø44 probe disc 3.672, real
  Ø40 module clearance 0.638 unchanged). Pin fit 0.000.
- Closed cell sweeps (shelf off): exactly the recorded
  baseline — each cell's own spring-fin working space
  175.806 / 176.803 / 175.806, plus the 0.014 graze vs the
  synthetic power-board tongue (unchanged model, unchanged
  sweep). Power-board drop overlap 12.000 (tongue) unchanged
  — the hinge parts are all north of the board.
- Arc sweep 0..100° (2.5° steps, 0.5° over 88..100) vs caps
  pressed AND unpressed, trackpad Ø44, real Fly, real
  plugged USB-C plug (g17 reference solids), desk plane, pin,
  and every fixed case part: the ONLY contact is the stop,
  first at 95.0°. (An earlier draft obstacle — a hand-made
  plug box at Z 12..20 — reported 15.02 mm³ at 2.5°; the
  project's real plug reference sits at Z 5.02..11.02 and
  measures 0.000 at every angle.)
- Open state at 95°: all 3 cells extract on the established
  motions with 0.000 vs the open shelf (+slider riding with
  it) and every fixed part — the Opus objection (opened shelf
  = a ~64 mm wall cramping the middle cell) does not bite:
  the wall stands SOUTH of the bay and the middle cell's
  sweep clears it completely (0.000).
- Invariants: outline 310.04 × 146.07; Z max 22.00; north
  face at Y −64.370 exactly (deviation 0.000 — the 12.155 in
  the raw log is the probe band's own 0.005 slice of the face
  plane); south unification, antenna band, Wing/plate
  positions unchanged; battery sweeps and power-board fixing
  unchanged in the closed state.

## Addendum — shelf trim round (PO 2026-11-22)

PO verbatim: 「wingの両端側に伸びてる細い部分は省略して。
面を合わせるのは北側だけでいいよ」 — the shelf's thin
extensions toward both Wing ends are OMITTED; the flush/height
matching matters only on the north side. This supersedes the
"full width" element of the 2026-11-21 profile (the band
plateaus at Z22.00 across the Wing key fields). The decision
is a simplification: the strips carried no function besides
the band look and the original screw/latch seats, both of
which had already moved off them once (hinge round) — except
the latch, see below.

### What was removed; final shelf

- The shelf is now the COVER ALONE (lid plate + E/W skirts +
  S skirts + N skirt + hinge knuckles): X −30.25..+30.25
  (60.5 wide — the lid span, incl. the skirt/bridge structure
  over the bay sills at |X| 28.25..30.25), Y −64.37..2.13
  (knuckle wrap), Z 8.00..22.00, 1 solid, 26.42k mm³
  (was 96.52k with the strips). The end faces are the cover's
  own faces at X ±30.25 — no new cut faces were created.
- build_plateau is no longer called; its groove/dip/slot for
  the old latch died with the right strip.
- North face over the shelf's span: flush at Y −64.370
  (deviation 0.000 — the 2.563 in the raw probe is the probe
  band's own 0.005 slice of the face plane, same reading as
  the hinge round's 12.155 over the wider shelf), top at
  Z22.00. The keycap-gap rule (1.30 nominal) where the shelf
  remains: closed shelf vs caps pressed AND unpressed 0.000;
  shelf vs the 1.30 cap keep-out prisms 0.000.

### Latch — seat relocated (forced consequence, mechanism kept)

The hinge-round latch sat ON the right strip (slider X
72..92, receiver in tray-right at X 75..89): cutting the arms
removed its seat. The mechanism is unchanged — slider in a
top groove, stem through a web slot, collar in a pocket under
a fixed web, keyhole entries at the two slide positions
(±3.8), PETG centring finger, 1 mm lift proof — but the seat
moved to the bay north wall rib inside the lid span, and two
shapes adapted to that seat (probe_trim*.py):

- Rib geometry: top 15.15, Y −64.37..−62.0, lid underside
  15.35 (0.20 gap). The corridor between the north face
  (−64.37) and the middle-cell face (−59.37) is 4.99 wide and
  the rib is ~2.4 of it, so the round Ø4.4 collar cannot be
  pocketed: the collar is now a BAR 4.4 (X) × 2.2 (Y) × 0.75
  at Z 13.35..14.10, and the stem is 2.0 (X) × 1.2 (Y).
- Stem centre (12, −62.55). Bar Y −63.65..−61.45: pocket
  north wall 0.57 of rib-face material, cell-face clearance
  1.92. Pocket X 5.6..18.4, Y −63.80..−61.40, Z 13.30..14.15
  in the rib (hosts: centre-infill + tray-right). Web = rib
  top 14.15..15.15; neck slot Y −63.25..−61.85 (stem width);
  entries Y −64.37..−61.40 at stem X 12±3.8, opened to the
  north face so the bar's arc drift (northward, 0.16 by web
  exit) cannot jam. Retention is over the bar's north chord:
  the web strip Y −63.65..−63.25 (0.40) × X 10.6..13.4 —
  lift proof below.
- FIRST SEAT FAILED, recorded honestly: the receiver was
  first placed at X 0 and the lift proof read 0.000 — the
  wall's middle span (|X| ≤ 7.5, the cover skirt's span) is
  capped at 7.80 and has NO web at pocket height; the probes
  had sampled the rib at |X| 12..28 only. The seat moved to
  X +12, where the rib top 15.15 is measured. A second defect
  of the first build — the bar's travel sweep (X ±6.0)
  clipped the north skirt by 0.960 mm³ at full slide — was
  fixed by widening the lid stem slot to the sweep (centre
  ±6.2). (The remaining slider-vs-shelf 1.125 at the entries
  is the centring finger's tooth riding out of its dip —
  rigid-model reading of a designed flex, identical value at
  the original X+85 site in the hinge round.)
- The slider's other numbers carry over: body 20 long in the
  lid-top groove (X −2.3..26.3, floor 19.8), top flush
  22.00, finger strain ~1.3% at full travel.
- The OLD receiver in tray-right (pocket + keyholes at
  X 75..89) is REMOVED: tray-right material in the old pocket
  box measures 48.300 mm³ = the full box volume (was 0.000
  with the pocket cut). The ±85 bosses are plain geometry
  again on both sides.

### Exposed-tray audit (where the strips sat)

- Tray material above the 10.90 tray top in either strip
  footprint (|X| 30.25..154, Y −64.4..0): 0.000 — the trays
  present a clean 10.90 surface; nothing floated on, hung
  from, or was supported by the strips. The Fly (top 9.60)
  and the plates were already independent of them.
- Nothing else referenced the strips: the shell's south
  lobes came from the OLD strips in the profile round and
  are shell parts, untouched.

### Verification (verify_trim.py, final run)

- Closed: case parts pairwise 0.000 (all 10 parts); case vs
  internals 0.000 except the two accepted artifacts (J_WING
  envelope 42.380/side; plunger vs Ø44 probe disc 3.672,
  real Ø40 clearance 0.638 unchanged). Pin fit 0.000.
- Closed cell sweeps (shelf off): exactly the recorded
  baselines (each cell's own spring-fin space 175.806 /
  176.803 / 175.806 + the 0.014 tongue graze). The
  power-board drop test was not re-run: its parts (board,
  trays, tongues) are untouched by this round and the board
  model reads 0.000 vs every case part above.
- Arc sweep 0..100°, shelf + slider fused with the slider at
  the EAST ENTRY (the opening configuration — a stronger
  check than the hinge round's shelf-only sweep): the ONLY
  contact is the stop, first at 95.0°; caps pressed and
  unpressed, trackpad Ø44, real Fly, real plugged USB-C plug,
  desk plane, pin, every fixed part otherwise 0.000 — the
  relocated bar exits through its entry cleanly.
- Open state at 95°: all 3 cells extract with 0.000 vs the
  open shelf+slider and every fixed part.
- Latch proof (relocated seat): at rest, slider vs receiver
  0.000 at all 3 positions; lifted 1 mm — locked (centred):
  0.840 (ENGAGED, the web strip over the bar's north chord);
  east/west entries: 0.000 (released). Engagement is smaller
  than the original site's 3.202 (full collar) — recorded as
  the chord-engagement trade of the rib seat; the latch's
  load case is incidental lift only.
- Invariants: outline 310.04 × 146.07; Z max 22.00; north
  face flush over the shelf span; south unification,
  slope-free centre step, antenna band, Wing/plate positions
  unchanged.

## Addendum — shelf CORRECTION round (PO 2026-11-22)

PO verbatim: 「北側はキーの近くまで棚にするよ。削除したかった
のはキーボードの東西のハジ側にあったやつだよ」 — the shelf
DOES run along the north, reaching close to the keys, across
the key fields; what should be removed is only the shelf
portions at the far east/west ENDS of the keyboard, beyond
the outermost keys.

### The trim round overshot (recorded honestly)

The trim round above cut the shelf back to the cover alone
(|X| <= 30.25, 26.42k mm³). That was PMO's misreading of the
PO's trim instruction: "omit the thin parts toward the Wing
ends" was executed as removing the whole band over the Wing
key fields, when the PO meant only the end portions beyond
the outermost keys. This round restores the band over the
keys and removes only the ends. The trim round's latch
relocation (below) is NOT undone — it stays.

### What was restored; final shelf

- The band plateaus are built again (build_plateau, the
  pre-trim geometry: band at Z22.00 north of the keys, south
  edge = per-cap offset polyline) and the shelf is again
  fuse(cover, strip_l, strip_r), one solid, 96.61k mm³.
- Measured outermost keycap extents (probe_corr.py, from
  caps.json cap_polys — the actual cap outlines): |X| =
  151.001 on BOTH sides (the outer Wing cap's east/west
  corner at Y -3.234; the pre-trim shelf ran to +-153.25,
  i.e. 2.249 past the last cap, ending in a tapering tail —
  the 153.0..153.25 column held only 3.0 mm³/side).
- Shelf end: outermost cap extent + 1.30 = X +-152.30 — the
  project's own cap-gap rule applied at the end face. Each
  strip is clipped there; the end faces are clean vertical
  planes. Removed vs pre-trim: 0.95 of X per side (the tail
  beyond the last key).
- NOT restored: the hinge round's X+85 latch seat features
  in the right plateau (slider groove, centring dip, stem
  web slot). That seat was abolished in the trim round; the
  band is the plain P0/P1 band there. Audit: the old stem
  slot box (X 76.2..87.8, Y -62.2..-59.8, Z 10.5..22.5)
  holds 303.456 mm³ of solid band (it was a through-slot in
  the hinge round), and the old tray-right receiver pocket
  box still reads the full 48.300 mm³ of plain fill.

### Latch — disposition

Unchanged from the trim round: seat on the bay north-wall
rib at stem (12, -62.55), bar collar, mechanism and numbers
identical (proof below re-reads locked 0.840 engaged /
entries 0.000 — byte-for-byte the trim round's values, so
the restored band provably does not touch the latch: the
slider also reads 0.000 vs the shelf at rest in all 3
positions, and the closed pairwise suite is 0.000).

### Verification (verify_corr.py, final run)

- Closed: case parts pairwise 0.000 (all 10 parts); case vs
  internals 0.000 except the two accepted artifacts (J_WING
  envelope 42.380/side; plunger vs Ø44 probe disc 3.672).
  Pin fit 0.000. Shelf vs caps (pressed and unpressed)
  0.000; shelf vs the 1.30 cap keep-outs 0.000.
- Cap gap at the ends: minimum distance shelf <-> caps
  (unpressed) = 1.300 overall, and 1.300 to EACH outermost
  cap — the end faces keep exactly the band's gap rule.
- Closed cell sweeps (shelf off): exactly the recorded
  baselines (own spring-fin spaces 175.806 / 176.803 /
  175.806 + the 0.014 tongue graze).
- Arc sweep 0..100°, shelf + slider at the EAST ENTRY: no
  contact with caps (pressed/unpressed), trackpad Ø44, real
  Fly, real plugged USB-C plug, desk plane, pin or any fixed
  part; the only contact is the stop at 95.0°, as in the
  hinge and trim rounds.
- Open state at 95°: all 3 cells extract with 0.000 vs the
  open shelf+slider and every fixed part.
- Invariants: outline 310.04 × 146.07; Z max 22.00; shelf
  bbox Y min exactly -64.370 (north face flush over the
  shelf span, deviation 0.000); south unification,
  slope-free centre step, antenna band, Wing/plate
  positions unchanged. Centre lid, hinge and latch are
  untouched geometry from the previous rounds.

---

## Trackpad cover round (PO 2026-11-22: 「トラックパッド周りの
上蓋も設計して」) — DONE

New part `trackpad-cover` (11th case part): a bezel finishing
the Cirque module's seat. Plan note:
`.issue296-runtime/trackpad-cover-plan.md` (committed first,
0f586b8f7). Probes: probe_padcover{,2,3}.py, probe_boss.py.

### Measured starting state

- Module Ø40 / sensing Ø38, centre (0, 48), top Z 12.70,
  bottom 11.20, in the Ø44.6 seat (floor 11.10 where the slab
  is thick, 10.90 patches elsewhere — the floor is NOT
  uniform). Annular gap r20..r22.3.
- The keep-disc (r23.5) island exemption left leftovers
  around the seat: E/W rim bumps at 12.55 (r≈22.5) and a
  north rise to 15.09 (r22.3..23) — both ABOVE the pad
  surface, i.e. finger-catching edges around the pad.
- Field is 10.90 at r≥24 in all directions; the shell south
  edge (Y 69.70) is only 21.7 from the pad centre, so a full
  circular foot cannot close toward the south.
- SW1 plunger: centre (−15.5, +64.50), 22.64 from the pad
  centre; head Ø4.0 spans pad-radial 20.64..24.64 in the SW
  sector; stem Ø2.9 Z7.2..10.9, head Z10.9..12.1 on the
  field. Nearest keycap vertex 48.949 from the pad centre.
- Shell slab uniformly 10.90/8.90 and continuous at all four
  candidate screw points (boss/pilot probes).

### Cover geometry (revolved annulus about the pad axis)

Profile (r, Z): window edge r20.20 at 11.25..12.38 →
0.32×0.32 chamfer to the top ring at (20.52, 12.70) → top
ring flat at **12.70 = the pad surface (glide step 0.00)**
out to r23.00 → outer cone 34.7° down to the foot ring at
(25.60, 10.90) → foot ring on the 10.90 field → underside at
11.35 (0.25 over the seat floor, 0.10 over the trimmed rim)
→ inner skirt r20.20..21.00, bottom edge 11.25.

- **Window Ø40.4 (r20.2)**: 0.20 radial clearance from the
  Ø40 module at EVERY height — the cover never overlaps the
  module, so it cannot pinch it; the Ø38 sensing disc is
  fully exposed (cover × sensing disc 0.000). The window
  edge's 0.32 chamfer sits over the module's outer
  non-sensing rim only in plan; there is no contact.
- Bbox X −26.67..26.67, Y 22.40..69.00, Z 10.90..12.70,
  volume 784.9 mm³. **Cover top Z = 12.70.**

### Fixing (module stays replaceable; no adhesive)

4× M2 flat-head screws FROM ABOVE through ear pads on the
cover (ears at r22.8..28.2, tangential width 9.0, top 11.90,
at 30/150/210/330°), Ø2.2 clearance + countersink cone
(r1.1→1.7, Z11.20..11.90) at r25.5, into NEW shell bosses:
Ø6.0 cylinders Z7.30..9.60 fused under the slab at the four
points (22.06, 60.75), (−22.06, 60.75), (22.06, 35.25),
(−22.06, 35.25), with Ø1.6 pilot holes. Modelled screws:
shank∩shell engagement 3.73 (south pair) / 3.11 (north
pair) mm³ > 0 at all four; screw × main/module/plunger/
cover 0.000; boss bottom 7.30 = 1.40 above the Main top
(5.90); boss cylinders × tray-left/tray-right/centre-infill
0.000 (they land in shell material only). Removal: 4 screws
from above → cover lifts off → module lifts out of its
seat. The seat opening (X ±3, Y 26..30) and the below-shell
connector zone are untouched (cover and bosses × zone box
0.000) — the electrical connection spec stays a separate
open item, and nothing the cover adds blocks its space.

### Shell changes (shell-central)

1. **Island trim**: shell cut to Z ≤ 11.25 within r25.6 of
   the pad centre (removes the 12.55 E/W bumps and the
   ≤15.09 north rise; completes the slope-removal flattening
   inside the cover footprint; the seat rim becomes a
   uniform 11.25 max). Audit: shell above 11.25 within
   r25.6 = 0.000.
2. The four bosses + pilot holes above.
3. The cover's underside is conformed to the finished shell
   (the project's own idiom): the north ears' flat 10.90
   bottoms otherwise cut 2 × 1.750 mm³ into the trimmed
   island shoulder (found in the first verify run, fixed).

### South edge and SW1 notch

- The cone foot cannot close toward the south (edge 21.7
  away), so the cover is clipped at Y 69.00 (0.70 inside the
  shell edge) with a 45° top chamfer from (67.90, 12.70) to
  (69.00, 11.60) — verified: cover top at (0, 68.9) = 12.10
  (the chamfer line), ring at (0, 26.5) = 12.70. Below the
  chamfer the clipped face drops to the underside (0.35
  shadow gap over the field = the intended joint line, no
  upward catch). No south apron (deliberate simplification).
- **Plunger notch**: Ø5.2 clearance cylinder at the plunger
  centre through the whole cover — head r2.0 → 0.60 plan
  clearance at every height; the notch opens through the
  cone, so the head stays side-accessible and pressable
  exactly as on the open field. Notch's closest approach to
  the pad centre 20.04 > module r20 (module edge not
  exposed).

### Verification (verify_padcover.py + verify_corr.py regression)

- Closed: all 11 case parts pairwise 0.000 (worst 0.0000);
  case vs internals 0.000 except the accepted artifacts
  (J_WING envelope 42.380/side; plunger vs Ø44 probe disc
  3.672 — the probe disc is Ø44, the real Ø40 module reads
  cover × module 0.000 and module clearance to the seat
  0.638 as before).
- Cover × the legacy Ø44 study envelope = 278.44 mm³ —
  BY DESIGN: filling that annular gap is the cover's job;
  against the REAL module solid the interference is 0.000.
- Cover × plunger at rest and pressed (−1.0): 0.000, min
  distance 0.600. Cover × caps pressed/unpressed: 0.000,
  min distance 20.541.
- Hinge arc sweep (shelf + latch slider at east entry,
  0..100°) vs cover: 0.000. Full verify_corr regression
  identical to the correction-round baseline (cell sweeps,
  latch proof 0.840/0.000, stop contact at 95.0° only).
- Invariants: outline 310.04 × 146.07; Z max 22.00; north
  face unchanged (the "north of −64.365" probe reads
  12.1550, identical to the pre-round baseline — the probe
  plane sits 0.005 inside the nominal face; the shelf was
  not touched this round).

### Renders

NEW tight centre close-up `files/case296-padcover-closeup.png`
(pad + bezel + ears + plunger notch, module fitted, cover in
a contrasting tone); standing top view refreshed
`files/case296-3d-top.png`. Script: render_padcover.py.

---

## Addendum — trackpad lap round (PO 2026-11-22): groove levelled, seam = shiplap

PO: 「パットの周りに溝ができてるので、プレートと高さが合うように
して。継ぎ目は厳密には揃わないと思うので、どう重なる（重ねる）と
良いか（見栄え、組み立て手順、剛性など）を考えてくれ」. Plan note:
`.issue296-runtime/trackpad-lap-plan.md` (committed first,
`0f9969183`); probes `probe_groove2/3.py`; verification
`verify_lap.py` (+ `verify_corr.py` regression).

### The groove, measured (before)

Assembled radial profiles (24 azimuths) and a 0.5 mm mesh grid
over the pad region: **no depression below the 10.90 field
anywhere around the pad** (the only sub-field readings, 9.60,
are the boss tops seen through the open Ø2.2 screw holes). The
"groove" is a seam/pan system of three parts:

1. **South shadow slot** — the cover's clipped south face
   bottomed at 11.25/11.35 over the 10.90 field: an open slot
   0.35..0.45 tall × ≈29 wide under the face.
2. **Butt seam at the foot ring** (r24.4..25.6) — a
   zero-overlap contact line; any print deviation opens it
   into a circular groove, and the cover rocks on a line
   contact.
3. **Raised pan** — the seat floor sits +0.20 over the field
   and the trim plateau r22.3..~23.5 at +0.35 (shell annulus
   histogram: 11.25 band = 202 cells); the pad sits in a
   shallow raised pan whose rim step coincides with the foot
   radius, doubling the seam line.

### Lap candidates

- **A — cover skirt laps over a shell lip: REJECTED.** Lap
  length = lip height only (0.35); the lip is a fragile
  ~1.2-wide raised ring that itself breaks the levelling; no
  screw clamping through the lap; the visible seam stays a
  field-level butt line at the skirt's bottom edge.
- **Reverse lap (shell over a cover tongue): REJECTED** —
  the cover could not be installed from above.
- **B — shiplap rabbet + flush flange: CHOSEN.** The shell
  receives an annular rabbet and the cover's cone ends in a
  flange whose top is flush with the field and whose bottom
  seats on the rabbet floor. Judged on the PO's axes:
  *appearance* — one hairline at the rabbet's outer step
  corner (0.45 nominal), backed by the 0.60-tall flange face,
  no through-gap at any tolerance corner (ray test below);
  *assembly* — cover still installs last from above, module
  still replaceable, 4-screw concept kept; *rigidity* — seat
  annulus 1.95 wide (vs a line contact), screws clamp through
  the lap stack into bosses under the rabbet floor, pads
  bridge the outer wall (a second lap at the screw points);
  *tolerance* — radial clearances 0.45 nominal absorb the
  ±0.20/part print tolerance with ≥0.25 to spare at the lap
  itself (below).

### Implemented geometry

- **Shell**: annulus r22.3..24.6 levelled to Z ≤ 10.90 (the
  11.25 rim plateau is gone; seat floor r<22.3 untouched);
  rabbet annulus r24.6..28.0, floor 10.30, clipped to Y ≤ 69.0
  like the cover (south band skin beyond keeps 10.90). Both
  cutters exclude a r3.2 disc at the SW1 plunger centre — the
  plunger boss cap stays at 10.90 (verified: cap material
  present, plunger checks unchanged); the rabbet therefore
  has a 10.90 island at the SW1 sector and the cover's
  conform cut trims its flange there — the lap is locally
  interrupted at the SW1 sector, as the notch already
  interrupts the cone (recorded deviation, by geometry).
- **Cover profile** (r, Z): … cone (25.00, 11.31) → shoulder
  (26.30, 10.90) → flange top (27.55, 10.90) = flush with the
  field → outer edge → lead chamfer → flange bottom
  (25.60, 10.30) seating on the rabbet floor → descent
  crossing 10.90 at r25.05 → underside 11.35 → skirt as
  before. Window Ø40.4, top ring 12.70 (glide step 0.00),
  notch Ø5.2 — all unchanged.
- **Screws r25.5 → r26.7** (single source `SCREW_PTS`;
  bosses Ø6.0 Z7.30..9.60 and Ø1.6 pilots move with it);
  pads r24.8..28.6 × 9.0, top 11.90, bridging the rabbet's
  outer wall onto the field.
- **South apron**: no lap is possible on the south (shell
  edge at r21.7), so the clipped face is extended down to the
  field — an annular sector (Y 68.55..69.0) top-limited by a
  cap solid revolved from the cover's own top chain, bottom
  conform-cut onto the shell: face min Z = 10.90 measured,
  the 0.35..0.45 shadow slot is closed.
- **Bug caught by verification**: the first build's screw
  clearance holes started at Z10.80 (first-round value) and
  left the new flange web (10.30..10.80) unpierced —
  modelled screw × cover read 1.457 mm³. Hole cut extended
  to Z10.20; re-check reads 0.000 at all 4 points.

### Verification (verify_lap.py; verify_corr.py regression)

- **Profiles after**: shell annulus histogram — the 11.25
  band is GONE (0 cells); the surround is the 10.90 field
  everywhere. Remaining sub-field features, all by design:
  the seam channel at the rabbet step (0.45 wide, floor
  10.30, backed by the flange face) and the Ø2.2 screw holes
  (boss tops 9.60 through them, as any screwed cover).
- **Lap audits**: shell above 10.90 in r22.3..24.6 = 0.000;
  shell above 10.31 in the rabbet = 0.000; rabbet floor
  present; cover × shell = 0.000 (face contacts only).
- **Through-path ray test** (probes r23.5..29.5 × 4 bands
  Z10.32..10.88 × 19 lap azimuths; the south clip sector is
  covered by the apron checks): no open path anywhere —
  worst free ratio 0.803 at a screw azimuth, where the probe
  threads the screw hole itself (the modelled screw fills
  it; screw × cover/Main/module/plunger all 0.000, shank
  engagement 3.054/2.441 mm³).
- **Tolerance corners** (±0.20/part): radial shifts ±0.20
  X/Y — the lap proper (flange/walls/floor) shows ZERO
  interference (clearances 0.45 → ≥0.25 remain); the only
  overlaps (≤1.01 mm³ total) sit at the zero-clearance
  conformed faces (SW1 island trim, apron seat, south clip
  face — localised by probe_shift.py), the same conform
  idiom as previous rounds: in print they become light press
  contacts, and the 4 screws locate the cover (real
  placement error ≪ ±0.20). Z: the cover seats on the
  rabbet floor under screw clamping; a floor printed ±0.20
  off moves the flange top ∓/±0.20 against the field while
  the flange face still overlaps the outer wall by ≥0.40 —
  no through-gap (a hypothetical +0.20 unseated lift opens a
  0.20 slit at the lowest band only; seating is the clamped
  state, as designed).
- **Regression**: closed pairwise worst 0.0000; case vs
  internals 0.000 except accepted artifacts (42.380/side,
  plunger vs Ø44 envelope 3.672); cover × module 0.000;
  cover × plunger rest/pressed 0.000, min dist 0.600;
  cover × caps 0.000 (min dist 20.161); hinge arc sweep vs
  cover 0.000; full verify_corr identical to the
  correction-round baseline (cell sweeps, latch proof
  0.840/0.000, stop contact 95.0°, shelf span ±152.30);
  invariants: outline 310.04 × 146.07, Z max 22.00, north
  face probe 12.1550 = baseline.

### Renders

Updated close-up `files/case296-padcover-closeup.png`; NEW
section through the pad centre `files/case296-padsection.png`
(Y=48 half-section, south half kept: flange seated in the
rabbet on both sides, module sectioned in its seat); top view
refreshed `files/case296-3d-top.png`. Scripts:
make_section.py + render_lap.py.

## Addendum — Wing lap round (PO 2026-11-22, corrected referent): the Wing<->case groove closed with a flush filler rib + under-tongue lap

PO correction: 「溝はwing側との溝を指してた」, with an annotated
render — the red loops mark the perimeter slot between each
Wing plate and the surrounding case/centre structure (right
Wing's inner edge; left side between the shelf/hinge structure
and the left Wing). The previous round's pad shiplap stands
(it fixed real defects) but was not this referent. Plan note:
`.issue296-runtime/winglap-plan.md`; probes
`probe_winggroove.py` / `probe_wingprofile.py` /
`probe_seam2.py`; verification `verify_winglap.py` +
`verify_lap.py` + `verify_corr.py` regression.

### The groove, measured (before)

Plate: top 10.90, bottom 9.40, tip edge |X| = 22.47, inner
long edge diagonal (drifts ~0.58 in X per 1 in Y).

- **Centre segment, Y ≈ 17..66 (both sides)** — a constant
  **9.21–9.36 wide open slot** between the shell-central edge
  and the plate's inner edge; depth 2.0 (tray valley shoulder
  at 8.90 under most stations), 6.2 at Y 40 (boss tops 4.70),
  **11.55 at Y 45 (floor −0.65, open to the interior)**.
- **Tip/valley segment, Y ≈ −0.4..17** — slot west/east of the
  plate tips over the centre valley (Main below): width 4.90
  (Y 10) / 2.01 (Y 15) to the first case material, up to ~14
  to the shell edge; floor −0.65.
- **SE corner, Y 66..72** — shell corner recedes; slot widens
  to ~10.5 (shoulder 8.90 under it, tray island at 10.90 at
  the plate edge); at Y 70 the tray field at 10.90 takes over
  with a ~2.15 residual at the corner station.
- **North edge** — hairline only (0.13–0.18 wide, floor 9.40,
  blind): already flush, untouched.
- **South edge** — no groove: the south-unification skin
  already holds a true 0.30 offset at 10.90. Untouched.
- **Bay stretch, Y −64..−2** — the plate's inner strip lies
  over the bay E/W wall; west of the tip is the battery bay
  opening, covered by the shelf when closed. Functional
  opening — stays open by design.

### Lap candidates

- **A — case flange laps OVER the plate edge: REJECTED.** Best
  appearance and total gap immunity, but the plate installs
  vertically after the PCB and must lift straight out; an
  over-lap blocks both.
- **B — flush filler rib + under-tongue lap: CHOSEN** (below).
- **C — rabbet/reveal channel: REJECTED** — leaves a deliberate
  0.85 × 0.55 channel; a shallow groove, against the
  levelling ask.
- **D — reverse lap (plate over a case tongue): REJECTED** —
  needs a step on the manufactured plate (outlines unchanged)
  and risks drop-in collision.

### Implemented geometry (candidate B)

Per side, a tray-owned filler rib along the plate's inner
edge, Y −0.40..72: plan = plate outline (outer wire only)
dilated +10.30 minus dilated +0.30, Z 8.65..10.90 (top flush
with the plate at 10.90); plus a **tongue** Z 8.65..9.15
reaching **1.50 under the plate edge** (plate bottom 9.40 —
0.25 clear). The band's bottom (8.65) overlaps the tray
valley shoulder (top 8.90) by 0.25 wherever the shoulder runs
under the slot, which fuses the rib to the tray (both trays
remain single solids); over the deep stations it is a
2.25-tall rib face-seated against the shell edge. Conform-cut
against shell-central, centre-infill and the trackpad cover
(its screw pads bridged the old slot — see verification).
Judged on the PO's axes: *appearance* — field and plate
coplanar, one hairline at the plate edge; *assembly* —
nothing crosses the plate's plan above its bottom plane, so
drop-in/lift-out are unchanged (Wing PCB top ~6.3 and the FFC
pass under the rib, underside 8.65); power-board-before-Wings
untouched; *rigidity* — case-integral rib, shoulder-fused,
tongue-stiffened edge; *tolerance* — below.

**Measured seam** (thin-slab rows, after): **0.30** at the
tip edge (Y −0.4..16), **0.23** along the diagonal, **0.12**
at the SE-corner stations (Y 64..72) — the OCC face offset
returns slightly less than the nominal 0.30 on the diagonal/
corner; every value is still looser than the plate<->recess
fit itself (nominal zero — the recess was cut by the plate
solid), so the band is never the tightest fit in the
assembly. Recorded as measured, not as the nominal.

### Verification (verify_winglap.py; verify_lap.py + verify_corr.py regression)

- **Re-profile after**: worst PLATE<->CASE seam along the
  inner perimeter = **0.30** (was 9.21–9.36 over Y 17..66).
  The 9.38 readings in the first pass were a detector artifact
  (a shell sub-run pairing across the spanning tray run) —
  fixed in the detector and re-run clean.
- **Tongue/through-path**: tongue present at all 18 probed
  stations (full columns); seam-centre columns blocked by
  plate/band or tongue at every station.
- **Tolerance corners**: plate shifted 0.30 AWAY — band-region
  interference 0.000, and the widened 0.60 hairline still has
  tongue under it at all probed stations (reach 1.20 ≥ 0.60):
  **no through-gap**. Shifted 0.30 TOWARD — 1.12 (R) / 2.66
  (L) mm³ in the band region, i.e. a light press where the
  local seam (0.12..0.23) is under the shift; the same class
  as the plate<->recess fit (a 0.30 toward-shift presupposes
  the full print clearance on the opposite recess wall).
  ±Y shifts: 0.000 except 0.37 at the band's north end face.
- **Assembly**: plate lifted +2.5 / +5.0 (shelf off — the
  service state; plate x shelf is unchanged by this round)
  vs tray/shell/infill/cover = **0.000** both plates.
- **Defect caught by verification**: the first band build
  overlapped the trackpad cover's screw pads (27.04 mm³/side
  in verify_lap's pairwise — the pads were designed to bridge
  the old slot). The band is now conform-cut against the
  cover as well; pairwise worst back to **0.0000**.
- **Regression**: verify_corr identical to the correction-
  round baseline (pairwise worst 0.0000; case vs internals
  0.000 except the accepted J_WING envelope artifact
  42.380/side, unchanged; hinge arc stop contact first at
  95.0°; latch proof 0.840/0.000; shelf span ±152.30; cell
  sweeps unchanged); verify_lap green (pad shiplap intact,
  band dips under the cover pads by conform cut); tray x caps
  (pressed/unpressed) 0.000; invariants: outline
  310.04 × 146.07, Z max 22.00, north face probe 12.1550.

### Renders

Perspective in the PO's annotated framing (from the
south-west) `files/case296-winglap-persp.png`; NEW section at
Y=44 through the Wing<->case seam `files/case296-wingsection.png`
(Y=44 slab, from the south: band flush at 10.90, seam,
tongue under the plate edge, Wing board below); top view
refreshed `files/case296-3d-top.png`. Scripts:
make_section_wing.py + render_winglap.py.
