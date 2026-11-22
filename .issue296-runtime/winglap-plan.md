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

probe_winggroove.py (slab method; winggroove.json). Plate: top
10.90, bottom 9.40, inner tip edge |X| = 22.47, inner long edge
diagonal (both boundaries of the slot drift east together as Y
grows — shell edge and plate edge are parallel diagonals).

**The groove system (Wing inner perimeter):**

- **Centre segment, Y ≈ 20..65 (both sides)** — a constant
  **9.21–9.36 wide** open slot between the shell-central edge and
  the Wing plate's inner edge. Depth varies with what lies under
  it: floor 8.90 (depth 2.0, tray step) at Y 25/50/55/60; floor
  9.60 (depth 1.3) at Y 35; floor 4.70 (depth 6.2, boss tops) at
  Y 40; **floor −0.65 (depth 11.55 — open to the interior floor)
  at Y 45**. Adjacent case top: shell at 10.90 (some stations
  read 10.30 = the pad rabbet stations bleeding into the slab).
  This is the long slot inside the PO's horizontal red loop.
- **Tip segment, Y ≈ 10..15** — slot west of the plate tip:
  width **4.90 (Y10) / 2.01 (Y15)**, floor **−0.65** (open),
  case side = tray top 10.90. Inside the PO's vertical red loop.
- **North edge (plate vs tray north fill)** — hairline only:
  width **0.13–0.18**, floor 9.40 (= plate bottom; a tight butt
  seam against the tray fill at 10.90). Not a trench.
- **South edge** — NO groove: the south-unification skin already
  holds a true 0.30 offset at top 10.90 flush. Done already.
- Rows Y −60..5 in the inner window show no in-band PLATE↔CASE
  gap (the neighbour there is the shelf above the band and the
  bay below — profile scan follows).

Full row profiles (probe_wingprofile.py, wingprofile.json):

- Y −64..−2 (bay stretch): the plate's inner strip lies over the
  bay E/W wall (sills 9.15/7.40/2.45/4.45); west of the tip is
  the battery bay opening, covered by the shelf when closed
  (skirt bottom 11.15). **Functional opening — stays open.**
- Y −0.4..~17 (tip/valley segment): slot between the plate tip
  and the centre valley (Main board below at 4.70..~6.3); width
  to the shell edge up to ~14 at Y 10, tray island at 10.90 on
  the left (X −17.7..−16.0); floor −0.65.
- Y ~17..66 (centre segment): the 9.21 slot; under it the tray
  valley shoulder at **8.90** over most stations (Y 20/25/50/
  55/60), deep wells at Y 40 (4.70) and Y 45 (−0.65).
- Y 66..72 (SE corner): shell corner recedes (39.16 at Y 66),
  slot widens to ~10.5 with the 8.90 shoulder under it and a
  tray island at 10.90 at the plate edge (48.32..50.05 at Y 66);
  at Y 70 the tray field at 10.90 takes over (residual ~2.15
  slot at the corner station).
- Y 72..82: south skin / tray field at 10.90 — closed already.

## Lap design decision

Candidates (plate kept plain; all work case-side):

- **A — case flange laps OVER the plate edge: REJECTED.**
  Best appearance (seam inset on the plate) and total gap
  immunity, but the flange would sit on the plate's top edge:
  the plate installs vertically after the PCB and must lift
  straight out — an over-lap blocks both. Assembly kills it.
- **B — flush filler + under-tongue lap: CHOSEN.** A case-side
  filler rib fills the slot with its top flush at **10.90**,
  ending **0.30** from the plate edge (the south skin's seam
  idiom). Below, a **tongue** (Z 8.65..9.15, i.e. 0.25 under
  the plate bottom 9.40) reaches **1.50 under the plate edge**.
  *Appearance*: one hairline at the plate edge, field and plate
  coplanar — the trench is gone. *Assembly*: nothing crosses
  the plate's plan above its bottom plane; drop-in and lift-out
  are exactly as before; Wing PCB (top ~6.3) and the FFC pass
  under the rib (underside 8.65) with ≥ 2.3 clearance; power-
  board-before-Wings order untouched. *Rigidity*: the rib is
  integral with the tray, fused along the valley shoulder
  (tongue merges into the 8.90 shoulder where present) and
  face-seated against the shell edge; section 9.15..10.90 plus
  the tongue. *Tolerance*: plate placement ±0.30 → hairline
  0.0..0.60, tongue reach ≥ 1.20 always; case print ±0.20 →
  hairline 0.10..0.50; tongue top worst corner 9.35 < 9.40 —
  a vertical sight line through any widened hairline lands on
  the tongue: **no through-gap at any corner**.
- **C — rabbet/reveal (stepped-down channel): REJECTED.** It
  tolerates everything but leaves a deliberate 0.85 × 0.55
  channel — a shallow groove, against the PO's levelling ask.
- **D — reverse lap (plate over a case tongue): REJECTED.**
  Needs a step on the manufactured plate (outlines unchanged
  per the brief) and risks drop-in collision.

**Band geometry**: plan = plate outline (outer wire only)
dilated +10.30 minus dilated +0.30, Z 9.15..10.90; tongue =
dilated +0.30 minus eroded −1.50, Z 8.65..9.15; clipped to the
inner-edge mask, Y −0.40..72; conform-cut against shell-central
and centre-infill; fused into tray-right / tray-left. North
hairline (0.13–0.18, blind, floor 9.40) and the south skin are
already flush — untouched.
