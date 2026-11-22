# Issue #296 — trackpad surround cover (PO 2026-11-22)

PO instruction (verbatim): 「トラックパッド周りの上蓋も設計して」
— design the top cover around the trackpad.

## Starting state (to be verified by measurement)

- Cirque TM040040-2024-302 module: Ø40 body, Ø38 sensing area,
  centre (0, 48) case frame, pad surface Z12.70.
- Seat: Ø44.6 recess cut into the shell-central island, floor
  Z11.10 (build_case3d.py build_shell). Module bottom nominally
  11.20 (0.10 above the floor, per the original 3D-stage note).
  Annular gap between module (r20) and recess wall (r22.3):
  2.3 mm wide, open today — no bezel/cover exists.
- Surround: centre field flat at Z10.90 (slope removed); island
  apron heights around the seat to be probed radially.
- Neighbours: SW1 plunger at (−15.5, +64.50) — centre distance
  from pad centre 22.64, i.e. its head/stem zone overlaps the
  cover's outer radii in plan in the NW sector; DLED pipe at
  (−4.0, +13.00) — out of scope.
- The module's electrical connection (12→6 adapter etc.) is a
  separate open item: the cover must not block the space below
  the shell that the connection will need, and must not pinch
  the module or its FFC tail.

## Design targets

1. One new part `trackpad-cover`: an annular bezel that covers
   the recess rim and the module↔seat annular gap, with a window
   exposing the Ø38 sensing area (window Ø to be fixed from
   measurement; nominally Ø39 — 0.5 radial overlap onto the
   module's non-sensing rim).
2. Finger glide: cover top at Z12.70 (flush with the pad
   surface); window edge gets a small chamfer; outer edge
   transitions down to the 10.90 field with a dimensioned
   chamfer/cone — no sharp catch in either direction.
3. Fixing: module stays replaceable — cover removable, no
   permanent adhesive as the only means. Candidate: small screws
   from above into island material outside the recess, or snap
   features; decide from the probed island geometry (material
   available around the recess, apron heights). The cover must
   not press on the module: vertical clearance between cover
   underside and module top at any overlap, stated.
4. Clearances (all measured, 0.000 interference):
   - cover vs SW1 plunger over full travel (plunger modelled at
     rest and fully pressed);
   - cover vs nearest keycaps, pressed and unpressed;
   - cover vs the north shelf's hinge arc (sweep);
   - cover vs module (Ø40 disc 11.20..12.70) and vs the Ø44
     probe envelope where it legitimately differs (the cover
     occupies the annular gap by design — the probe disc is an
     envelope, not the module; report both honestly).
5. Z max stays ≤ 22.00 (cover top 12.70, stated).

## Method

1. Probe: radial top-Z profile of shell-central around (0,48);
   plunger brep bboxes/Z bands; island material map for fixing.
2. Build: extend build_case3d.py with the cover part (exports
   STEP/STL/BREP like the other parts).
3. Verify: verify_padcover.py on the verify_corr machinery —
   closed pairwise incl. the new part, module/plunger/caps/
   hinge-arc checks for the affected region.
4. Renders: tight centre close-up of pad + cover (legible
   detail) + updated top view.
5. Records: case-3d.md addendum, Issue #296 comment, GOAL.md
   one line.
