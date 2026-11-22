# Issue #296 — shelf arm trim round (PO 2026-11-22)

PO verbatim: 「wingの両端側に伸びてる細い部分は省略して。
面を合わせるのは北側だけでいいよ」 — omit the shelf's thin
extensions toward both Wing ends; the flush/height matching
matters only on the north side.

Base: branch tip `99478610a` (hinge round). Shelf today =
fuse(cover |X|<=30.25, strip_l, strip_r) spanning X +-153.25,
Y -64.37..-0.37, Z 7.80..22.00, plus hinge knuckles
|X| 4.3..8.6 and the E/W skirt fins at X +-(28.25..30.25).

## Plan

1. PROBE (measure first): shelf/cover/strip spans; what the
   strips touch or support (tray north wall tops under the
   strips, the +-55/+-85 bosses, latch site); candidate latch
   sites inside the remaining span.
2. DECIDE final shelf span: the lid span (|X| <= 30.25) plus
   the bridge/skirt structure over the bay sills (the skirt
   fins at |X| 28.25..30.25 are inside the lid span). Clean
   vertical end faces at the cut.
3. LATCH: the slider (X 72..92) and its tray-right receiver
   (X 75..89) sit ON the right strip — removing the arms
   removes their seat. Keep the MECHANISM unchanged (slider +
   keyhole receiver + PETG centring finger, lift proof) and
   relocate the site into the remaining span at a measured
   equivalent seat; record the relocation as a forced
   consequence of the PO cut, not a redesign.
4. AUDIT the exposed tray areas where the strips sat: tray
   north wall tops, the +-55/+-85 bosses (insert holes were
   already abolished in the hinge round; +85 hosts the latch
   receiver today — after relocation it must be clean),
   nothing floating, no wall that only existed for a strip.
5. REBUILD via build_case3d.py edits; re-run the full
   verification (closed suite, hinge arc sweep, open-state
   cell extraction, Fly/plug) — 0.000 except the two accepted
   artifacts (J_WING envelope; plunger vs O44 probe disc).
6. Renders (closed top + open state), case-3d.md addendum
   (final span, what was removed, latch relocation, exposed-
   tray audit, re-verification numbers), Issue #296 comment,
   GOAL.md line.

Invariants: outline 310.04 x 146.07; Z <= 22.00; north face
flush over the shelf's span (deviation 0.000); south
unification, slope-free centre step, antenna band as built;
keycap gap 1.30 nominal where the shelf remains.
