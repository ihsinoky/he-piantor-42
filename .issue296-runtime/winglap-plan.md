# Issue #296 Wing↔case lap round — plan (2026-11-22)

## PO instruction (corrected referent)

PO verbatim (earlier): 「パットの周りに溝ができてるので、プレートと
高さが合うようにして。継ぎ目は厳密には揃わないと思うので、どう重
なる（重ねる）と良いか（見栄え、組み立て手順、剛性など）を考えて
くれ」 — corrected 2026-11-22: 「溝はwing側との溝を指してた」 with
an annotated render. The red loops mark:

1. the long slot between the centre field and the RIGHT Wing's
   plate, along the Wing's inner edge;
2. the slot on the LEFT between the shelf/hinge structure and the
   left Wing.

Referent = the **perimeter gap between each Wing plate and the
surrounding case/centre structure** (shell-central centre field,
trays, north-shelf band, centre-infill). The previous round's pad
shiplap stands (it fixed real defects) but was not this referent.

## Steps

1. **Measure first** (this note gets the numbers appended before
   any geometry change): profile the groove around both Wing
   plates — run segments, width, depth, forming surfaces, and the
   height offset between the plate top (Z10.90) and each adjacent
   case surface.
2. **Level**: bring case-side surfaces along the Wing perimeter
   flush with 10.90 so no trench remains.
3. **Lap design**: ≥2 candidate lap forms compared on appearance /
   assembly (power board BEFORE Wings; plate after PCB; FFC/Fly
   paths cross this boundary and stay open) / rigidity /
   tolerance behaviour. Implement the winner, case-side only.
4. **Verify**: before/after perimeter profiles; tolerance corners;
   Wing install/remove path simulation with the lap in place;
   FFC/Fly re-verified; full interference re-run + verify_corr
   regression identical outside the changed region.
5. **Deliver**: renders (perspective matching the PO's annotated
   angle, top, section through the Wing↔case seam), addendum in
   case-3d.md, Issue #296 comment, GOAL.md line.

## Keep

Wing boards' separation/outlines unchanged; keycap clearances
(innermost caps pressed/unpressed); hinge arc; pad cover + its
shiplap; outline 310.04 × 146.07; Z ≤ 22.00.

## Measurement (appended before changes)

(pending — probe_winggroove.py)
