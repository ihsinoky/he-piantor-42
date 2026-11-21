# Issue #296 Stage 3D — plan (2026-11-21)

Inputs: case-2d-stageb.md (approved), wing-bay-zcheck.md, geom_v2.json,
geometry17 body set (g17 Z − 2.65 = case Z; halves shift ±9.5).

## Correction found at entry (flag, do not silently harmonise)

Stage B item 2 prints the bay cavity inner faces as "Y −62.37..+2.37".
+2.37 cannot be right: (a) cavity depth 60.0 from −62.37 lands at
−2.37; (b) the bay footprint depth 64.0 = 60.0 + 2×2.0 walls closes
only with the south face at −2.37 (footprint −64.37..−0.37 — exactly
what the v2 figure drew); (c) the power board's recorded clearances
(0 north datum, 2.0 south from board edge −4.37) give −2.37. With
+2.37 the south wall would also hit Main's north tab (tip +2.27);
with −2.37 the gap is 2.64. **This stage uses −2.37** and flags the
note text as a sign slip.

## Measured at entry (g17, case Z)

- Trays meet at X +3.50 (δ=0); shifted edges −6.0 / +13.0 ✓ item 8.
  Tray Z −2.65..20.00; Y −64.37..+81.70 ✓ outline 310×146.1 at δ=9.5.
- Tray slab under the bay floor (−0.65): bottom −2.65 → ≤2.0 mm of
  material → screw-into-floor fixing is weak (drives the fixing
  decision toward fins + wall tongues, see build).
- shell-central: X ±41.01, Y −53.66..+69.70, Z 8.81..22.00 — its north
  portion overhangs the bay (cells to 14.65) → cut the bay column.
- strips: X from ±0.54, Y −64.37..+1.94, Z 10.90..22.00 — inner ends
  overhang the bay footprint → cut at the bay wall line X ±30.25.
- The Z-check tray post (22.73..26.25, −12.23..−8.70, top 9.40) is
  moulded tray-right material (not a post-* body) → the bay level cut
  removes it. post-* bodies are Wing supports, none inside the bay.
- Main (g17 body) Y 2.27..67.90, Z 4.70..5.90, unshifted.

## Build ops (build_case3d.py, cad-venv)

1. tray-right/left: shift ±9.5 after g17-coord edits:
   - remove old Main bosses at H1 (tray-left (0,9.27)) and H2/H3
     (g17 (∓31.89, 64.40)) — level to floor; add new H2/H3 bosses at
     g17 (∓22.39, 64.40) → asm (∓31.89, 64.40).
   - bay level cut: remove material above Z −0.65 inside the bay
     footprint (X ±30.25, Y −64.37..−0.37); fuse floor slab to −0.65.
   - bay walls: N wall = existing (gap span via infill); E/W walls
     2.0 thick (X ±(28.25..30.25)): top 15.15 outside the finger-zone
     Y span (−59.62..−9.12), top 7.40 inside it (cover skirt closes
     the side); S wall (Y −2.37..−0.37) top 15.15.
   - 209 fins at the 3 spring sites only: (−15, −8.37) S, (0, −60.37)
     N, (+15, −8.37) S; 1.65 thick, face at the contact plane, 16 wide,
     top Z 10.5. Board slots for them → Stage-2 input.
   - fixing tongues: 2 per E/W wall over the board edge strips.
   - slide-switch recess on the E wall inner face (Y −34.37, Z ≈8):
     pocket + actuator slot (SS-12D10 class envelope).
   - Fly seat at (38, −50.14) or (38, −51.94) per the gable decision;
     USB opening cut through the north wall at X=38.
   - south-edge straightening: profile the south wall to Y +81.70
     across the centre span (cut proud / fill dent).
2. centre infill (X −6.0..+13.0, full Y): north wall segment, bay
   floor + S wall segment, field floor matching tray floor top,
   H1 boss at (0, 9.27), south wall segment to +81.70.
3. shell-central: cut bay column (X ±30.25, Y −64.37..−0.37);
   Ø3 plunger hole through the south slope at (−15.5, +64.50);
   Ø2 light-pipe hole through the north slope at (−4.0, +13.00).
4. strips: cut at X ±30.25 inside the bay Y span.
5. plates: half-space clip at |X| 22.47 (tip notch, as drawn in v2);
   USB rim notch on plate-right over the Fly shell.
6. battery cover (new part): top 16.65, underside 15.15, E/W skirts
   down to 7.40 over the low wall span, 2 screws at the block's south
   corners into the S wall top; north edge tucks to the N wall face.
7. small new parts: plunger pin (Ø2.9) for SW1; light pipe (Ø2).

## Verification (verify_case3d.py)

- Assembly interference: case parts vs Main (D-063 outline extrusion),
  Wings + underside bodies @δ9.5, plates, cells, power board + south
  features, Fly set, trackpad disc, switch envelopes. Itemise volumes.
- Removal envelope re-run (zcheck method): sweep + finger zones vs
  final walls/fins/cover-off; spring-end fin = pivot furniture,
  dispositioned separately.
- Power-board insertion path: vertical drop at final pose with the
  fins entering slots + tongue flex note; Wing-seated blockage
  re-stated (order: power board first).
- Margins restated: cover top 16.65 vs datum 22.00 (provisional).

## Outputs

hardware/case/issue-296-wireless/ (build123d source + STEP/STL per
part), renders case296-3d-*.png (goal files/), case-3d.md, Issue #296
comment, GOAL.md line, checkpoint commits.
