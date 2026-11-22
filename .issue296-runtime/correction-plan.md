# Issue #296 — shelf correction round (PO 2026-11-22)

PO verbatim: 「北側はキーの近くまで棚にするよ。削除したかった
のはキーボードの東西のハジ側にあったやつだよ」 — the shelf DOES
run along the north, reaching close to the keys, across the key
fields. What should be removed is only the shelf portions at
the far east/west ENDS of the keyboard — beyond the outermost
keys.

## What went wrong (recorded honestly)

The trim round (tip `53512f62a`) cut the shelf back to the
cover alone (|X| <= 30.25). That overshot: PMO misread the PO's
trim instruction as removing the whole band over the Wing key
fields, when the PO meant only the end portions beyond the
outermost keys. This round restores the band over the keys and
removes only the ends.

Base: branch tip `53512f62a` (trim round). Pre-trim full shelf
geometry is at `99478610a` (hinge round): shelf =
fuse(cover, strip_l, strip_r), strips built by build_plateau
(band at Z22.00, south edge = per-cap offset polyline, cap gap
1.30 nominal), spanning X +-153.25.

## Plan

1. PROBE (measure first): outermost keycap extents on each
   side from caps.json cap_polys (actual cap outlines, not
   switch centres); strip span and end geometry at 99478610a;
   what the restored band would cover (tray bosses +-55/+-85
   are plain geometry since the hinge round).
2. DECIDE shelf end: outermost cap edge + a stated margin;
   clean vertical end faces at the cut. State the resulting
   shelf X span.
3. RESTORE the strips via build_case3d.py: build_plateau is
   called again and the shelf fuses cover + both strips, with
   each strip clipped in X at the decided end. EXCEPTION: the
   hinge-round latch cuts inside build_plateau (slider groove
   X 67.7..96.3, centring dip, stem web slot on the right
   plateau) belong to the ABOLISHED X+85 seat and are NOT
   restored — the latch stays at the trim round's X+12 rib
   seat, mechanism unchanged. Verify the restored band does
   not conflict with the X+12 seat/slider (different X span,
   but prove it numerically).
4. Centre lid portion, hinge (axis Y -0.57 / Z 19.30, knuckles
   |X| 4.3..8.6), and the slope-free centre step are unchanged.
5. REBUILD; re-run the full verification (closed suite, hinge
   arc sweep, open-state cell extraction, Fly/plug) — 0.000
   except the two accepted artifacts (J_WING envelope; plunger
   vs O44 probe disc). Cap gap 1.30 verified along the restored
   band AND at the new end faces (state end-face clearance to
   the nearest cap).
6. Renders (closed top + open state), case-3d.md addendum
   (the overshoot recorded, measured outermost-cap extents,
   chosen end margins, final shelf span, latch disposition,
   re-verification numbers), Issue #296 comment, GOAL.md line.

Invariants: outline 310.04 x 146.07; Z <= 22.00; north face
flush over the shelf's span (deviation 0.000); south
unification, slope-free centre step, antenna band as built.
