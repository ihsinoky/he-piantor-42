# Trackpad surround levelling + lap joint — plan (PO 2026-11-22)

PO verbatim: 「パットの周りに溝ができてるので、プレートと高さが合う
ようにして。継ぎ目は厳密には揃わないと思うので、どう重なる
（重ねる）と良いか（見栄え、組み立て手順、剛性など）を考えてくれ」

Base: branch `issue-296-stageb` tip `644f9434f` (trackpad cover
round landed). Parts: `shell-central`, `trackpad-cover` (bezel,
window Ø40.4, top ring 12.70 flush with pad, cone 34.7° to foot
ring at r25.60 on the 10.90 field, underside 11.35, 4× M2 ears
into shell bosses). Seat Ø44.6 floor 11.10 (patches 10.90);
shell trimmed to Z ≤ 11.25 within r25.6 of pad centre (0, 48).

## Step 1 — MEASURE the groove (before changing anything)

- Radial top-height profiles through the pad centre (0, 48),
  azimuths every 15° (finer near features), r 15..40, sampled
  on thin-box columns from the asm3d breps:
  (a) shell only, (b) shell + cover, (c) assembled incl. module.
- Characterise the groove: r-range, width, depth below 10.90
  (or below the neighbouring surfaces), and which surfaces
  form it (seat recess / r25.6 trim zone / cover foot & cone /
  south clip shadow gap). Numbers into this note + addendum.

## Step 1 results — the groove, measured (probe_groove2/3.py)

- Assembled radial profiles (24 azimuths, mesh-sampled):
  NO depression below the 10.90 field anywhere around the
  pad. The only sub-10.90 readings (9.60) are inside the
  Ø2.2 screw holes (boss tops seen through the open holes).
- Shell annulus r22.5..34 top histogram: 10.90 dominant;
  an 11.25 band (202 cells ≈ the trim plateau r22.3..23.5);
  seat floor 11.10 inside r22.3.
- So the "groove" is a seam/pan system, three parts:
  1. **South shadow slot**: the cover's clipped south face
     bottoms at 11.25/11.35 over the 10.90 field — an open
     slot 0.35..0.45 tall × ≈29 wide under the face.
  2. **Butt seam at the foot ring** (r24.4..25.6): a
     zero-overlap contact line; any print deviation opens
     it into a circular groove and the cover rocks on a
     line contact.
  3. **Raised pan**: seat floor +0.20 / rim plateau +0.35
     over the field ring the pad under the cover — the
     cover sits IN a shallow pan whose rim step coincides
     with the foot radius, doubling the seam line; the
     surround is not at plate height at the cover base.
- Constraints found: shell-central's top at Y=48 extends to
  |X| ≈ 30.1 with a narrow slot at |X| ≈ 28.5 (wedge/seam
  line) → the lap's outer wall must stay ≤ r28.0. SW1 boss
  (centre (−15.5, 64.5), pad-radial 22.64, top already
  10.90) must be excluded from the deeper rabbet cut.

## Step 2 — Level the surround

Redesign so that outside the cover's glide cone, the surface
around the pad meets the surrounding field flush at plate
height Z10.90 — no trench/groove remains around the pad.
Shell: level the annulus r22.3..24.6 to 10.90 (rim plateau
gone; seat floor r<22.3 untouched — it is under the module;
plunger disc excluded, its top is already 10.90).

## Step 3 — Lap joint design (PO's explicit ask)

The cover↔shell seam will not align exactly in print, so the
joint must be an intentional overlap, not a butt seam.
Candidates to compare (at least two):
- A: cover foot laps OVER a shell rim/lip (cover skirt outside,
  shell lip rises inside the skirt).
- B: shiplap — stepped recess in the shell receiving the cover
  foot (shell steps down, cover foot drops in, cover surface
  runs over the step).
Judge on: appearance (seam line / shadow placement from above;
no open gap at tolerance extremes), assembly order (cover
still last from above; module still replaceable), rigidity
(lap length; screws clamp through the lap), tolerance
behaviour (assumed print tolerance ±0.20 per the project's
stack-up records; show both corners: no interference, no
visible through-gap). Implement the winner; record reasoning.

### Decision (measured design)

- **A — cover skirt over a shell lip: REJECTED.** Lap length
  = lip height only (0.35); the lip is a fragile ~1.2-wide
  raised ring that itself breaks the levelling; no clamping
  through the lap; the visible seam stays a field-level butt
  line at the skirt's bottom edge.
- **B — shiplap rabbet + flush flange: CHOSEN.** Shell gets
  an annular rabbet (inner wall r24.6, floor 10.30, outer
  wall r28.0 — inside the 28.5 slot). The cover's cone ends
  in a shoulder onto a flange whose TOP is at 10.90 (flush
  with the field) and whose bottom (10.30) seats on the
  rabbet floor: radial lap/seat r25.6..27.55. Seam = one
  hairline at the rabbet's outer step corner (0.45 nominal
  clearance), backed by the 0.60-tall flange face — no
  through-gap at any corner. Screws move out to r26.7,
  through low pads on the flange (top 11.90, as the current
  ears) into bosses under the rabbet floor — clamping acts
  through the lap stack; pads bridge the outer wall (a
  second lap at the 4 screw points). South: no lap is
  possible (shell edge at r21.7) — instead the cover's
  clipped south face gets an apron down to the field,
  conform-cut to the shell, closing the shadow slot.
  Tolerance corners (±0.20/part): radial clearances 0.45
  nominal → 0.05..0.85 (never interference; worst case a
  0.85 hairline in the step corner, shadowed, floor-backed);
  glide step nominal 0.00, worst ≈ ±0.30 — the same stack
  structure as the current design (seat reference moves
  from field to rabbet floor, same part, local tolerance).
- Reverse lap (shell over cover tongue): rejected in one
  line — the cover could not be installed from above.

## Keep (invariants)

- Pad glide: cover top 12.70, step 0.00 vs pad surface.
- Window Ø40.4: cover never touches the module (0.20 radial).
- SW1 plunger notch + full travel; hinge arc clearance.
- 4-screw fixing concept (positions may move if the lap
  requires it — record any move).
- Connector zone below the shell untouched; module
  replaceable; cover installs last from above.
- Outline 310.04 × 146.07; Z max 22.00; accepted artifacts
  only (J_WING envelope, Ø44 probe disc).

## Verification & deliverables

- Before/after section profiles through the pad centre
  (groove depth → flush 10.90, numbers).
- Tolerance-corner checks of the lap (both extremes).
- Full interference re-run (affected region) + verify_corr
  regression vs the correction-round baseline.
- Renders: updated close-up, NEW section view through the pad
  centre showing the lap, updated top view.
- case-3d.md addendum; Issue #296 comment; GOAL.md line.
