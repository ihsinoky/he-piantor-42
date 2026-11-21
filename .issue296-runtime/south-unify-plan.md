# Issue #296 — south-outline unification, plan A (PO adoption 2026-11-22)

Spec of record: `files/case296-south-unify-opus-2026-11-22.md` §3 (plan A)
+ measured current state `hidden_files/design-review-opus/south-outline-data.md`.
Base: branch `issue-296-stageb` tip `d8b687d4b`.

## Items (proposal §3 numbering)

1. **S(X) outline** (trays, |X| ≤ ~60.73 replaced): straight Y_S = 81.700 to
   the tangent point X_t1, R4.0 arc (centre (±X_t1, Y_S − 4.0)) to the
   tangent point X_t2 on the existing end diagonal, diagonal unchanged
   beyond. X_t1 / X_t2 recomputed from the diagonal fitted to the built
   tray profile (proposal values from the same fit: intersection 59.636,
   X_t1 = 58.247, X_t2 = 60.726). Kills R1 (V-notch 7.414), R5 (shoulder
   waviness / −0.88 dip), the 81.702 overshoot.
   Method (mirrors the proven north-fill pattern): probe the built tray's
   south face C(X) at 0.25–0.5 mm sampling; fill = plan polygon prism
   (south boundary S(X), north boundary min(C, S) − 0.30 embed),
   Z −2.65..10.90, fused per tray; clip = prism {Y > S(X)} over the same
   span for the overshoot (peak 81.702 zone).
2. **South band top** Z 10.90: skin Z 9.30..10.90 (1.6 skin per §5),
   hollow below (antenna cavity preserved), north boundary B(X):
   70.000 for |X| ≤ 41.01; beyond, max(70.000, plateSouth(X) + 0.30)
   from the built plates' measured profile. Skin extends south to S(X)
   and is fused into tray-left / centre-infill / tray-right in their X
   slices, with 0.30 gaps at the part seams X = −6 / +13 (§3-4).
3. **Shell-central south edge** → one straight line Y = 69.700.
   AMENDED after probing (probe_shell.py, 0.25 mm sampling): the
   centre face is **69.202** flat for |X| ≤ ~39.25 (the coordinator's
   69.288 exists only as a ~0.3-wide ridge at |X| ≈ 39.4; corners
   69.700 from |X| ≈ 39.6). A slice-translate would copy the wavy
   face (+0.412 → 69.614..69.700), NOT one line — so the shell uses
   the same face-following fill as the trays: prism Z 8.90..10.90
   (the face's measured Z range), south boundary exactly 69.700,
   north boundary min(C_shell, 69.700) − 0.30 embed, |X| ≤ 41.0.
   Extension actually needed: 0.498 (not 0.412). Target line
   69.700 unchanged. Joint shell↔skin = 70.000 − 69.700 = 0.300 ✓.
   Residual: at |X| ≤ ~3.5 the trackpad seat floor (Z 11.10) keeps
   its own edge at 69.202 above the fill (0.10-high sliver under
   the pad rim, inside the seat recess — measured, recorded).
4. **C0.5 chamfer** along the south top edge, continuous over the
   unified edge (straight + both arcs, ending at the arc/diagonal
   tangent points): straight zone = triangular prism cutter
   (Y,Z): (81.20, 10.90)-(81.70, 10.40)-(81.70, 10.90); arc zones =
   cone cutters (keep-radius 3.5 @ Z 10.90 → 4.0 @ Z 10.40 about the
   arc centres, wedge-limited). Applied to trays + infill AFTER the
   fill and skin fusions so the whole top edge is one line.
5. **§3-4 infill retreat to 79.500 — NOT implemented (recorded):**
   neither tray reaches X −6..+13 (tray spans end at −6.0 / +13.0,
   the D-062 centre joint); retreating the infill there opens a
   19.0 × 2.2 through-slot in the south wall. The centre wall segment
   stays infill-formed, flush at 81.700, and the C0.5 chamfer runs
   across it continuously — the proposal's one-line intent is kept.
   The wall butt seams at X = −6 / +13 also stay (a 0.30 through-slot
   in the outer wall is not a joint, it is a hole); the 0.30 joint
   rule is applied on the band surface (shell↔skin, plate↔skin,
   skin slice seams), which is where §3-2/§3-3 define joints.

## Untouched (proposal §6 + task invariants)

North side (all P0/P1 state), Wing boards/plates positions, wedge
groove (|X| 41–50, Y < 70 — skin boundary stays at Y ≥ 70.000 there),
plate seams, antenna band (PETG only, no metal added; depth 11.8;
cavity hollow under the skin), Fly/USB, Z ≤ 22.00, outline
310.04 × 146.07.

## Verification (numbers required)

- South profile re-extraction (measure_south method, new BREPs):
  whole-case + per-part; R1/R2/R3 closure values; top-slab profile
  (Z 10.85..10.95) showing the chamfer line.
- Main vs new south material: intersection 0.000 + min distance
  Main outline → wall inner face / skin / shell extension
  (south corners included).
- Antenna band depth re-measured (79.70 − 67.90 = 11.80) + skin
  underside / cavity height.
- Full suite (verify_p0p1 basis): case vs internals, case vs case,
  shelf lift trajectory, battery sweeps shelf-off, Fly/plug —
  0.000 except accepted artifacts (J_WING envelope 42.380/side,
  Ø44 probe disc), re-confirmed. Outline + Z unchanged.

## Renders

render_p0p1 basis: top (north-up, caps fitted) + persp updated;
NEW south-side view (camera due south, slight elevation) showing
the unified line → `files/case296-3d-south.png`.
