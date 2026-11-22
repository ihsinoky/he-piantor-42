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

## Step 2 — Level the surround

Redesign so that outside the cover's glide cone, the surface
around the pad meets the surrounding field flush at plate
height Z10.90 — no trench/groove remains around the pad.

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
