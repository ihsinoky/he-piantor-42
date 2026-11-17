# Issue #270 Stage 2d — plan

PO approvals:
- Stage 2c design approved 2026-11-18: Main tab fronts parallel to the
  FH12 connector axis (J2 skew 22°, J3 skew 17°), front line raised
  +0.65 (stage2c.json / stage2c-design.md).
- PO redirect 2026-11-18 (Wing): do NOT use the exact 0.55 offset notch.
  Design a SIMPLE notch: a few straight segments parallel to the tab
  front/walls + simple fillets; MIN seam >= 0.55 everywhere (uniformity
  not required); overlap 0 at both pitches; no Wing copper hits;
  inside D-037 silhouette. Document segment counts (exact-offset vs
  simplified), seam min + location, notch area change. Figure
  fig-2d-wing-notch.png (tab + simplified notch zoom, exact-offset
  ghosted) -> goal files/.

## Main Rev.9 (update in place, tree issue-270-main-rev9/)
1. 2D: take stage2c candidate polygon (case frame); fillet the J2
   diving corner (d=0.151). Fillet R <= 1.0, chosen as the largest
   0.05-step R that keeps all 2c checks: pad clr (exp ~1.486), copper
   cuts 0, min edge-to-copper >= 0.284. Re-run s2c-style checks on the
   filleted polygon; save stage2d.json.
2. Board: splice new tab-zone Edge.Cuts into the current Rev.9 board
   (walls on the same lines, new front corners PL/PR from 2c, fillet
   emitted at the J2 diving corner). Everything else byte-identical:
   verify non-Edge.Cuts item census + hashes vs the pre-2d Rev.9.
3. Checkpoint commit after Main.

## Wing Rev.6 (update in place, tree issue-270-wing-rev6/, x4 variants)
1. Per variant, in case frame at the fitted pose: floor chain =
   wall-parallel segment + front-parallel segment + wall-parallel
   segment (each at perpendicular distance >= 0.55 from the FINAL
   filleted Main outline), fillets R at the two junctions; ends blend
   into the existing Wing boundary. Dense-sample verify: min distance
   floor->Main >= 0.550, overlap 0, removed region vs copper (fills
   only, as 2b; refill + confined-delta check), inside silhouette.
   If a fillet dips the seam below 0.55, raise offsets uniformly by
   the smallest 0.01 step that restores >= 0.550 and record it.
2. Splice floor chain into each Rev.5-derived Rev.6 board (adapt
   build-wing-rev6.py splice machinery; source = current Rev.6 board
   is NOT the base — rebuild from Rev.5 like 2b, with the new floor).
   Wait: 2b built Rev.6 from Rev.5 boards. Do the same: Rev.5 +
   simplified notch = new Rev.6. Copper/fill handling as 2b.
3. Count notch-zone Edge.Cuts segments: Rev.6 (2b exact offset) vs
   Rev.6 (2d simplified), per variant; record in REPORT.
4. Checkpoint commit after the Wing set.

## Gates (gates-2d.py, 2b yardsticks)
- Per board: DRC comparative vs 2b results (no new class), unconnected
  0, wrong-net 0, via-pad minima unchanged, Main pad-corner clearance
  (expect ~1.486), Main ERC 0.
- Seam from final saved files: min >= 0.550, overlap 0, both pitches.
- Case: tray relief delta vs 2b Rev.9 (2c estimated 0.0 — verify from
  final geometry; touch production tree only if changed). Re-run the
  #264 fitted-audit bundle with the final pair (expect gate 1 = 0,
  exact reproduction as in 2b).

## Packages + REPORT
- Regenerate manufacturing packages (Main Rev.9 + Wing Rev.6 x4):
  gerbers from final boards; BOM/CPL re-verified, JLCPCB set,
  FH12 = C5378715, DRAFT / NOT FOR ORDER (adapt make-packages-2b.py).
- REPORT.md (Rev.9 tree): add Stage 2d section — connector-aligned
  fronts, skews 22/17, fillet decision, simplified-notch design +
  segment counts + seam min/location + notch area change, final check
  table; update draft D-044 line to the FINAL shape. Do NOT edit
  docs/decisions.md. Do NOT push.
