# Issue #296 — P0/P1 revision plan (Opus design review fold-in)

PO decision 2026-11-21: fold the Opus design review's P0/P1 items
(`files/case296-design-review-opus-2026-11-21.md`) into the case.
Base state: branch `issue-296-stageb` tip `21028fc06` (shelf
integration verified). Review claims that are general assertions
(extrusion width ~0.4, bed classes) are treated as DESIGN
ASSUMPTIONS and recorded as such; everything measurable from the
model is measured.

## P0-1 — tolerance stack-up, shelf south edge vs keycaps

Assumptions (stated, not measured — Junana caps are UNMEASURED;
the physical measurement stays a PO-side PRINT GATE):
- cap size 16.5 x 16.5 nominal, tolerance +-0.25/dimension
  -> northern-extent growth <= 0.20 (worst key angle 60 deg)
- cap seating play on switch/plate: 0.15
- shelf edge print tolerance (FDM PETG): 0.20
- shelf placement play southward: 0.30 (0.2 design mating gap +
  screw clearance-hole radial play, combined bound)
- plate placement in case: 0.10
Worst-case sum = 0.95. Nominal gap g = 1.30 (review P1-4 range)
-> worst-case residual +0.35 > 0. RSS typical 0.45 -> ~0.85 typ.
Construction: plateau boxes extend to capline - 0.05, then cut
per-cap DISC-OFFSET keep-out prisms (rect prism + 4 edge quads +
4 vertex cylinders, radius g) -> south edge = true offset curve
of the cap rectangles (uniform perpendicular gap g), replacing
the 1.0 mm staircase (whose true min was 0.571 at nominal 1.0).
Verify: true 3D min distance shelf<->cap solids (both cap states).

## P0-2 — screw row south, rim >= 1.25

Row Y -61.37 -> -60.37. Head env: flat-head M3, head O5.5 top
flush Z 22.00; rim = 64.37 - 60.37 - 2.75 = 1.25 nominal.
Shelf hole becomes clearance O3.4 (machine screw, P1-5);
countersink cone r1.7 -> r2.75, 90 deg, h 1.05, base Z 20.95.

## P0-3 — bed fit of the 304.5 mm shelf

Measure the shelf plan outline (convex hull) from the built
solid; test rotated fit on 220 / 256 / 300 square beds, raw and
with 5 mm total margin. Rule (task): single-piece path on a
256-class bed -> keep one piece + record orientation plan.
Else: 3-piece split at |X| 30.25, pin + glue joints (2x O3
dowel pins per joint in the measured common cross-section),
still removable as one assembly; re-verify joints + pieces
(each piece must fit a 220 bed).

## P1 items

- South edge offset polyline: see P0-1 (g = 1.30).
- Fixing: pilots -> heat-set inserts. Tray hole O4.2, depth
  Z 5.0..10.90 (5.9), insert = M3 x 5.7 class, top flush with
  tray top 10.90. Screw: M3 x 14 flat-head machine screw
  (DIN 965 class), engagement ~4.0 in the insert. Boss: measure
  hole material fraction + min wall on current trays first
  (restore the -61.37 pilot void in the probe); add a fused
  boss cylinder only if the measurement fails, then re-check
  boss vs Fly pocket / Wings / plate.
- Mating gaps 0.2 on every shelf<->case mating surface:
  plateau underside 10.90 -> 11.10 (vs plate/tray top);
  lid underside 15.15 -> 15.35 (vs wall tops 15.15), skirts
  extended up to 15.35; N skirt bottom 7.80 -> 8.00 (vs capped
  wall top 7.80); shelf centre south edge Y -0.37 -> -0.57
  (vs slope top edge). E/W skirt bottoms already 0.25 over the
  plate — unchanged.
- Pry notches x2 at the angled end faces near |X| ~ 120, at the
  shelf underside seam: cut Z 11.10..14.60, band placed from the
  measured outline so the north face plane (|X| <= 117 claim)
  is untouched. Shelf must stay connected (solids count).
- SW1 plunger head O5 -> O4 (r 2.5 -> 2.0): plan clearance to
  the real O40 module 22.64 - 20 - 2.0 = 0.64.
- Renders: north-up, keycaps fitted (top + persp + shelf-off;
  caps from caps.json solids, unpressed). Section refreshed.
- Verbalisation doc: caveat header added (body untouched).

## Invariants

Outline 310.04 x 146.07, Z <= 22.00, north face flat; full
interference suite re-run (lift trajectory, battery sweeps
shelf-off, case vs internals, case vs case) = 0.000 except the
accepted J_WING envelope artifact (trays only); Fly undisturbed.

## Steps

1. Diag (pre-change): insert-hole material/wall at the new row;
   shelf outline + bed fit; notch band probe; joint section.
2. Decide split vs one piece from the bed numbers.
3. Edit build_case3d.py (both copies), rebuild, verify_p0p1.py.
4. Renders; doc annotation; case-3d.md addendum; Issue comment;
   GOAL.md line; push.
