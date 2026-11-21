# Issue #296 — lid-integral north shelf: plan (2026-11-21)

PO decision (2026-11-21): the battery lid （蓋） is made INTEGRAL with
the north band/shelf — one single removable part. Battery replacement
= remove the whole north shelf, swap cells, refit. This supersedes
open disposition 2 of the north-flush revision ("lid independent of
the band", PMO default).

## Current state (tip 0e55a2b62)

- battery-cover (lid): X ±30.25, Y −64.37..−0.37, top 22.00,
  underside 15.15; E/W skirts Z 11.15..15.15 over the bay sills;
  S skirts; N skirt to 7.80 over the capped wall span. Screw holes
  Ø3.0 at (±24.25, −63.37) into Ø2.7 wall pilots (Z 10.0..15.15).
- strip-left/right (band plateaus): per-1mm-column boxes
  Z 10.90..22.00, |X| from 30.25 out, north edge = flush plane
  −64.37 (|X| ≤ 116; tray outline beyond), south edge = capline
  − 1.0 (cliff at the key line). They meet the lid face-to-face at
  |X| = 30.25.
- Shell-central keeps the centre slope (22.00 @ Y −0.37 → 10.90 @
  Y 20.0) — stays with the shell, NOT part of the shelf.
- Fly at (38, −60.00), mouth +0.00 flush, mounted in tray-right
  (pocket Z 2.9..10.0, top of Fly 9.60 < plateau underside 10.90).

## Design

1. **Part**: north-shelf = fuse(cover, strip-left, strip-right) —
   one solid, exported as `north-shelf` (parts 11 → 9; the three
   replaced part files are removed from the tree).
   Boundary: north = flush plane (ends follow tray outline as the
   plateaus already do); south = Y −0.37 in the centre (meets the
   shell slope's top edge — slope does NOT move), key line on the
   halves; underside = lid underside/skirts in the centre,
   plateau underside 10.90 outboard.
2. **Bridge over the bay E/W sills**: unchanged geometry (skirt
   bottom 11.15 over wall band X ±(28.25..30.25)); measure shelf
   vs Wing boards / plate tips underneath and report clearances.
3. **Fixing** — DECIDED by measurement (diag_shelf.py /
   diag_shelf2.py, 2026-11-21):
   - The as-built centre pair (±24.25, −63.37) CANNOT be retained
     with any standard screw head: the axis is 1.00 mm from the
     flush north face, so any head of radius > 1.0 stands proud of
     the outline (a Ø5.5 flat head by 1.75). The pair is REMOVED
     (shelf holes + tray wall pilots), superseding the Stage-3D
     fixing. (The Ø3.0 hole itself already broke the face by 0.50;
     heads were never modelled in earlier stages.)
   - NEW: 4× flat-head M3, all in the plateaus, on one line
     Y = −61.37 (head rim −64.12, 0.25 inside the face; heads
     countersunk flush, head top = 22.00): pairs at **±55 and
     ±85**. Ø2.7 pilots into the tray north fill, Z 4.0..10.90.
     Measured: pilot fill fraction 100.0% at all four positions;
     shaft cylinders (r1.5, Z 3.0..10.9) vs Wings / plates 0.000;
     plateau depth at the columns 42.8 (X55) / 23.0 (X90 class,
     X85 = 25.6); right pair clear of the Fly pocket (pocket east
     face 51.3 vs pilot west edge 53.65).
   - Span justification: shelf spans 310.04; screws at ±55/±85
     give centre span 110, side spans 30, end cantilevers 70 —
     vs 130.8 cantilever per end for the old centre pair alone.
     The lid portion additionally rests on the bay walls (N wall
     top 15.15, S wall top 15.15 at |X| ≤ 10.90, E/W skirts over
     the sills) and is located by the skirt/wall sandwich.
   - Driver access: vertical; verify bit cylinder (Ø6.35) from
     each head upward vs keycap solids (both states) + report
     plan distance screw axis → nearest capline (expect ≥ 26).
4. **Fly**: untouched (stays in the tray). Shelf removal is a pure
   vertical lift — the plateau over the Fly (underside 10.90 vs
   Fly top 9.60) only gains clearance. USB opening is in the tray
   wall below the shelf; verify plug vs shelf (on) = 0.000 as
   before, and opening unobstructed with shelf off.
5. **Removal motion (assumed, to verify)**: remove 4 screws, lift
   the shelf vertically (+Z). Sample +2/+5/+10/+25 vs keycap
   solids (unpressed AND pressed), trackpad island, Fly + plug,
   trays (bay walls), Wings, shell, Main, cells, power board.
   Expect 0.000 at every lift > 0.
6. **Battery sweeps with shelf OFF**: re-run slide 2.0 + tip 35°
   sweeps vs the shelf-less case set; expect the same fin-box-only
   result vs case, 0.000 vs Wings / switch envelope.
7. **Full interference table** (shelf on): shelf vs internals,
   rest-of-case vs internals (J_WING envelope artifact 2 × 42.38
   re-confirmed, everything else 0.000), case vs case 0.000,
   outline 310.04 × 146.07 and Z ≤ 22.00 unchanged, north
   flatness 0.000 re-checked on the shelf face.

## Steps

1. This plan + checkpoint commit.
2. diag_shelf.py: plateau depth + fill backing at candidate XS;
   pick XS; record numbers.
3. build_case3d.py: shelf fuse + countersinks + outboard pilots
   (in build_tray? no — pilots go into tray_r/tray_l AFTER
   north_fill; add a shelf-fixing step after the fill) + exports
   change; rebuild; commit.
4. verify_shelf.py: all checks above → verify-shelf.txt; commit.
5. Renders: overwrite case296-3d-top.png / -persp-open.png; add
   case296-3d-shelf-off.png (shelf removed, bay open).
6. Addendum in case-3d.md (incl. the PO decision of record),
   Issue #296 comment, GOAL.md line; final commit + push.
