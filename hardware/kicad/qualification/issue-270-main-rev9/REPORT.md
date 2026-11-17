# Issue #270 — REPORT: Main Rev.9 + Wing Rev.6 (outline-only revision)

Date: 2026-11-17 (Stage 2b) / 2026-11-18 (Stage 2d, §6).
Basis: adopted Main Rev.8 / Wing Rev.5 (D-043).
Shape spec: Stage 2a design record (`.issue270-runtime/stage2a-design.md`),
approved by the PO 2026-11-17; Stage 2d shape: Stage 2c study,
approved by the PO 2026-11-18. All work is Edge.Cuts-only in intent;
every deviation from a pure outline change is listed in §5 / §6.6.

## 1. What changed

**Main Rev.9** (`issue-270-main-rev9/main-rev9/`) — Rev.8 with the two
connector-tab outlines replaced by identical trapezoids at both ZIF
sites: depth 4.738 mm past the Rev.7 slanted edges, front length
16.689 mm, wall run 2.735 mm/side, base width 22.160 mm, walls at
60° to the slanted edges (base interior angle 60°, front interior
120°), centred on the Rev.8 tab centres. 9 Edge.Cuts segments
removed, 9 added per board (both sites in one pass). The board file
sits in a `main-rev9/` subdir so the fp-lib-table `${KIPRJMOD}/../..`
paths resolve exactly as they did for Rev.8 (see §5.5).

**Wing Rev.6 ×4** (`issue-270-wing-rev6/wing-rev6-<variant>/`) — Rev.5
with the inner-corner notch floor re-cut as the **exact 0.55 mm
offset of the implemented Rev.9 tab outline** (shapely buffer
construction on the as-built Rev.9 outline, resolution 64). The new
boundary departs from the Rev.5 boundary in three stretches per
board (south mouth 2.23 mm, main floor run 13.76 mm, north mouth
2.47 mm on 17L); the stretches between them are the Rev.5 boundary
itself, which already lay on the new floor within 2 µm, and are
kept as the original items. Emitted as faceted segments — the
Rev.5 board's own style (its R1.0 fillets are facet chains);
simplification deviation ≤0.002 mm. Removed plan area vs Rev.5:
2.626 mm² (left), 3.335 mm² (right), both pitches.

**MATCHED PAIR — Rev.9 requires Rev.6 and vice versa.** The Rev.9
tabs overlap the Rev.5 notch mouths (plan overlap up to the tab
flares; the pair was designed together in Stage 2a), and the Rev.6
floor sits 0.55 mm from the Rev.9 tab but as little as ~0.52 mm
from — and in the mouths inside — the Rev.8 tab region. Do not mix
revisions in a build.

## 2. Gates (#263 yardsticks)

| Board | DRC (material) | Unconnected (DRC / graph) | Wrong-net | Via-pad min (floor 0.10) | ERC | Verdict |
|---|---|---|---|---|---|---|
| Main Rev.9 | comparative — see below | 0 / 0 | 0 | **0.1596** (= Rev.8) | **0** | PASS |
| Wing Rev.6 16mm-left | 0 | 0 / 0 | 0 | **0.1032** (= Rev.5) | — | PASS |
| Wing Rev.6 16mm-right | 0 | 0 / 0 | 0 | **0.1063** (= Rev.5) | — | PASS |
| Wing Rev.6 17mm-left | 0 | 0 / 0 | 0 | **0.1252** (= Rev.5) | — | PASS |
| Wing Rev.6 17mm-right | 0 | 0 / 0 | 0 | **0.1400** (= Rev.5) | — | PASS |

Main DRC, stated comparatively because of a baseline-records defect
(§5.3): kicad-cli run identically on the saved Rev.8 and Rev.9 files
gives clearance@0.2-rule 500 = 500, track_dangling 5 = 5 (same
items: pour-tie ends), copper_edge_clearance **14 → 6** (12 old tab
items removed; 4 new at the J3 tab wall with min actual 0.2821 mm —
the designed 0.284 mm edge-to-copper clearance of Stage 2a; the
0.5 mm board-setup edge constraint is unmeetable at a board-edge
connector and was already violated by Rev.8's tabs). No new
violation class or location appears.

Invariance proofs (programmatic, from the saved files):
- Main: all 1,684 non-Edge.Cuts items (footprints incl. pad geometry,
  tracks, vias, zone fill hashes) **identical** to Rev.8. ZIF
  pad-corner edge clearance **0.8364 mm** at J3.14 (Stage 2a value;
  Rev.8 was 0.8197); no pad uncovered. Whole-board min
  edge-to-copper unchanged (0.2005 mm, a pre-existing fill point far
  from the tabs).
- Wing ×4: copper signature identical to Rev.5 excluding fills;
  fills dispositioned in §5.2. Outline vs the buffer construction:
  area match within 0.07 mm² symdiff (facet noise), valid, seam
  **0.5500 mm** in the tab zone at the fitted pose of each variant,
  overlap with Rev.9 = 0.

Electrical (carried over, with the reasoning the brief requires):
- Main Vfar **4.754 V (J3) / 4.770 V (J2)** — copper byte-identical,
  no re-extraction needed or performed.
- Wing configuration Vfar **4.934 / 4.934 / 4.929 / 4.931 V**
  (16L/16R/17L/17R) — routing and fills unchanged except the
  terminal-free pour fringe of §5.2, which carries no DC path in
  the FEM model (no pad/via/track inside it; pour component counts
  unchanged), so the Rev.5 FEM drops stand.

## 3. Case (low-deck production tree)

Updated record: `hardware/case/issue-263-lowdeck-production/README.md`,
Issue #270 section; evidence in its `audit-rerun/`
(`audit270-rerun.log`, `final_eval.json`, `case-delta-270.log`).

- Seam (final files, both pitches, both sides): overlap 0,
  distance **0.550 mm** ≥ 0.52 target — PASS.
- Tray pocket relief: Rev.9 tab solid ∩ trays = **6.52 mm³ (L) /
  6.31 mm³ (R)** total, i.e. **+2.58 / +2.70 mm³** over the adopted
  Rev.8 reliefs (3.94 / 3.61). Adopted into the production record
  as the new totals; cuts into existing tray material only, D-037
  silhouette not exceeded. (Stage 2a estimated +1.81 / +1.94 on its
  superseded script geometry — §5.1.)
- Growth-vs-bodies census (both pitches, identical): the Rev.9
  growth solid touches only tray-left/right (the relief above) and
  the un-notched audited Wing solids (dispositioned by the Rev.6
  notch). No shell, plate or Fly body is touched.
- Fitted audit: the #264 bundle re-run reproduces the recorded
  audit **exactly** (final_eval.json identical on every key):
  gate 1 = 0 unexpected contacts, service PASS with the one named
  #264 residual.

## 4. Manufacturing packages (DRAFT / NOT FOR ORDER)

Per board, in `<board dir>/manufacturing/`: fresh gerbers + drill
(28 files Main, 26 Wing), native `BOM.csv` / `CPL.csv`, the JLCPCB
set `BOM-jlcpcb.csv` + `BOM-jlcpcb-consolidated.csv` +
`CPL-jlcpcb-gerber-frame.csv` carried from Issue #267 and
re-verified against the new boards (designator sets equal; all CPL
origins match the fresh exports exactly; frame offset (0,0)), plus
`FABRICATION.md` and `quote-handoff.md`.

- FH12-14S-0.5SH(55) carries the real LCSC code **C5378715** in
  every BOM (the #267 quote run proved it orderable at JLCPCB,
  Extended, stock 3,907 on 2026-11-17; the stale "not sourced"
  wording in the #267 handoffs is corrected in the new ones).
- Unmapped parts: NONE (Main 54 rows / 55 designators; Wing 4 rows
  / 49 designators per variant; exclusions as in #267: NPTH holes
  and test points).
- The 16mm consolidated BOMs are new: #267 never quoted 16mm, so
  they are derived from the per-designator BOM by the #267 grouping
  rule; the derivation is asserted byte-equivalent (after
  normalisation) on Main and both 17mm boards, where both forms
  exist.

## 5. Deviations and disclosures

1. **60° vs the Stage 2a script.** The Stage 2a design record
   specifies true-60° walls (base ±11.080 mm), but its generator
   script actually built a 67.9° shape (2.735 mm run spread over
   Δd = 6.738 mm); its derived quantities (seam excepted) describe
   the 67.9° shape. Implemented here is the **design record**
   (true 60°, the PO's stated "60度くらい" intent). Consequences:
   implemented Main outline area 2650.26 mm²; the Wing floor was
   derived from the implemented Main, so the seam is 0.550 by
   construction and verified from the final files; the tray delta
   grew vs the 2a estimate (§3). The Stage 2a seam/pad-clearance
   values (0.550 / 0.8364) reproduce exactly.
2. **Wing pour fringe refill.** The removed notch region contains
   HALL_5V / GND pour fringe (0.86 mm²/layer left, 1.13 mm²/layer
   right; zone outlines overlap more, actual fill as stated) — the
   brief's "touches no copper" premise held for tracks/vias/pads
   (nearest ≥1.9 mm, verified) but not for pour fringe. Zones were
   refilled on the new outline, exactly the #263 respin procedure;
   from-file verification: fill delta confined to the removed
   region + 0.75 mm inset band (nothing outside), pour component
   counts unchanged (6 → 6 both pours). Main was NOT refilled: its
   delta region contains no fill (one 0.0012 mm² zone-polygon
   hairline on the east edge, attributable to the Stage 1
   extraction residue; the implemented outline reuses Rev.8's own
   segments outside the tab zones), so Rev.8's fills carry over
   byte-identical.
3. **Main DRC baseline defect (pre-existing, not introduced
   here).** The #263 tree's Main `main.kicad_pro` carries only a
   Default netclass at 0.2 mm clearance (the Wing projects carry
   the correct 0.1 mm classes), so standalone kicad-cli DRC reports
   ~500 phantom clearance items on the qualified Rev.8 baseline
   itself; the Rev.8 `drc.json` saved in the tree (448) is also
   stale against a fresh run on the same file (500). The operative
   gates are the copper-graph metrics (§2), which are
   rule-independent and all zero. Recommend a follow-up fix of the
   project file's netclasses to the D-019 values — not done here
   (outside the outline-only brief; it changes the qualification
   basis and belongs with the adoption decision).
4. **Wing notch emission is faceted**, not true R0.55 arcs (see
   §1) — geometry is the exact offset construction within
   0.002 mm; the seam measured from the final files is 0.5500 mm.
5. **Main tree nesting.** Rev.9's board sits in
   `issue-270-main-rev9/main-rev9/` (Rev.8 sat three levels below
   `qualification/`; the fp-lib-table uses `${KIPRJMOD}/../..`).
   In the flat layout the schematic ERC reported 59
   footprint_link_issues purely from library paths; nested, ERC =
   0 and the DRC library class disappears. The schematic file is
   md5-identical to Rev.8's.
6. **Mouth blends.** The Stage 2a allowance for R≤1.0 mouth fillets
   was not needed: the buffer construction's mouths are the offset
   lines/arcs themselves, and no gate failed.

## 6. Stage 2d — connector-aligned tab fronts + simplified Wing notch

Basis: the Stage 2c study (`.issue270-runtime/stage2c-design.md`,
PO-approved 2026-11-18). Measured skew between each FH12 connector
axis (the 14-pad row / mouth line) and the board's slanted edge:
**J2 22.0°** (edge 120.0°, axis 142.0°), **J3 17.0°** (edge 60.0°,
axis 43.0°) — the sites are not mirror-identical, so the tabs are
per-site shapes. The Rev.9 trapezoid bodies are kept; only each
tab's front edge is replaced by a line parallel to its connector
axis, raised +0.65 mm (the smallest 0.05 step restoring zero copper
cuts at a minimum edge clearance ≥ the 2b value).

### 6.1 Main Rev.9 (in place, outline only)

- J2's diving corner (front-line depth d = 0.151 mm) carries a
  build fillet. The corner's wall stub is only 0.1739 mm and the
  interior angle is 142.0°, capping the radius at ≈0.50 mm:
  R0.55 is infeasible (tangent length 0.1894 > stub); **R0.50**
  chosen (tangent length 0.1722, pocket removed 0.0032 mm², stub
  residual 0.0017 mm). The arc's wall tangent point was snapped
  1.7 µm onto the existing base vertex W0 (disclosed; below the
  board's own coordinate significance for the outline chain).
- Final-board checks (all Stage 2c checks re-verified on the
  filleted outline): pad-corner clearance **1.4864 mm** (J3.14;
  floor 0.70, 2b value 0.8364), pads uncovered 0, **copper cuts
  0**, minimum edge-to-copper **0.323 mm** (2b: 0.284), silk
  minimum 1.482 mm, inside the D-037 silhouette. Board area
  2637.71 mm² (−12.55 vs the 2b Rev.9, matching the Stage 2c
  prediction). Non-outline census identical to the 2b board
  (1919 items); the board-file diff is 39 lines, Edge.Cuts only.

### 6.2 Wing Rev.6 — simplified notch (PO redirect, 2026-11-18)

The notch is NOT the exact 0.55 mm offset of the new tab (the PO
judged that outline unnecessarily complex). It is a simple floor
of **three straights parallel to the tab's diving wall / front /
rising wall**, joined by tangent fillets, standing off the final
tab so the **minimum seam is ≥ 0.55 mm everywhere** (uniformity
not required), overlap 0 at both pitches, inside the D-037
silhouette. Fillet radius chosen by sweep: RF = 1.0 needs the
floor raised δ = 0.12/0.10 mm (L/R) to hold the minimum;
RF = 0.75 needs δ = 0.05; **RF = 0.55 needs δ = 0.01** and removes
the least material — adopted (it is also the project's established
notch-arc radius from the exact-offset chain). Offsets therefore
sit at 0.56 mm.

- **Seam minimum 0.5600 mm** (design polygons), occurring at case
  (−29.92, 52.11) left — against the tab's rising base corner —
  and (18.45, 32.64) right. From the final saved boards: **0.5595
  (L) / 0.5585 (R)**, identical at 16 mm and 17 mm; overlap
  0.0000 everywhere. (The ≈0.001–0.002 below the design value is
  KiCad's arc faceting in the saved outline.)
- **Copper:** the notch removes only zone-fill fringe (GND pour:
  fill L 19.51 / R 17.61 mm² per layer set, refilled per the #263
  procedure with the delta confined to the removed region +
  0.75 mm band, component counts unchanged). **No routed copper
  is touched** — the non-outline census is identical on all four
  variants and DRC wrong-net / unconnected stay 0.
- **Segment counts** (same rule both stages: Edge.Cuts items whose
  midpoint lies in that board's removed region vs Rev.5, buffered
  1.0 mm): left **22 → 17**, right **26 → 23**. The 2b counts are
  all straight facets (the exact-offset chain was emitted faceted,
  no arcs); the 2d counts include true arcs (L: 16 seg + 1 arc;
  R: 21 seg + 2 arcs). The new floor itself is emitted as exact
  design elements — L: 4 elements in 2 parts (3 lines + 1 arc),
  R: 7 elements in 3 parts (5 lines + 2 arcs) — the remaining
  stretches of the new boundary are surviving Rev.5 boundary,
  which already stands deeper than the new floor there.
  Figure: `.issue270-runtime/fig-2d-wing-notch.png` (tab +
  simplified notch, exact-offset outline ghosted).
- **Notch area change:** material removed vs Rev.5 is L 12.91 /
  R 12.68 mm², against the 2b exact-offset notch's 2.70 / 3.40 —
  **+10.21 / +9.28 mm²**. The increase is the price of following
  the larger connector-aligned tab (its rising side reaches
  d = 7.35 mm vs the trapezoid's 4.74) with straight segments at a
  guaranteed minimum seam; all removed material is bare corner /
  pour fringe, no routed copper (§6.2 above).

### 6.3 Gates (Stage 2d, #263 yardsticks; `gates-2d.json` per board)

| board | DRC total | unconnected | wrong-net | via-pad min | verdict |
|---|---|---|---|---|---|
| Main Rev.9 | 509 = clearance 500 (pre-existing phantom class, as 2b) + copper_edge_clearance **4** (2b: 6) + track_dangling 5 | 0 | 0 | 0.1596 | no new class; pass profile as 2b |
| Wing 16L | silk warning only (excluded class) | 0 | 0 | 0.1032 | pass |
| Wing 16R | 0 | 0 | 0 | 0.1063 | pass |
| Wing 17L | silk warning only (excluded class) | 0 | 0 | 0.1252 | pass |
| Wing 17R | 0 | 0 | 0 | 0.1400 | pass |

Main ERC 0 (schematic unchanged, run for the record). The two
fewer copper_edge_clearance items on Main match the improved
minimum edge-to-copper (0.284 → 0.323). Via-pad minima are
unchanged on every board. One build defect was found and fixed
during 2d: an endpoint snap in the left variants' same-item
splice emitted a zero-length Edge.Cuts segment (DRC
invalid_outline); the splice now guards zero-length pieces and
the rebuilt boards are clean.

### 6.4 Case and fitted audit

- Tray relief for the final tab, recomputed from the final
  geometry against the #264 audit body set: **6.521 (L) / 6.305
  (R) mm³ — identical to the 2b totals** at both pitches, so the
  low-deck production tree is NOT modified.
- Fitted audit: the #264 verification bundle re-run with the
  final Rev.9/Rev.6 pair reproduces the recorded audit EXACTLY —
  `final_eval.json` byte-identical (md5 079ccaa78c2f4046e38ab9ed5ee2dc4e)
  to the recorded `audit-rerun/final_eval.json`: gate 1 = 0
  unexpected contacts at nominal, service PASS with the one
  named #264 residual (records:
  `audit-rerun/audit270-2d-rerun.log`,
  `audit-rerun/case-delta-270-2d.log`).

### 6.5 Packages

Manufacturing packages regenerated for Main Rev.9 and Wing Rev.6
×4 from the final boards (fresh gerbers/drill/POS; BOM/CPL
re-verified row-by-row against the #267 JLCPCB set, FH12 =
C5378715). DRAFT / NOT FOR ORDER.

### 6.6 Deviations from the Stage 2c numbers

1. Seam from saved boards 0.5585–0.5595 vs the 0.5600 design
   value (KiCad arc faceting; the ≥0.55 floor holds).
2. Saved-outline symdiff vs the design polygons 0.055–0.079 mm²
   per Wing — µm-wide transform/rounding slivers plus endpoint
   snaps (largest genuine component 0.017 mm² at a splice
   junction); no shape deviation.
3. The Main fillet's wall tangent point snapped 1.7 µm onto the
   existing vertex W0 (§6.1).

## 7. Draft adoption line (for the PO; NOT entered in docs/decisions.md)

> **D-044 (DRAFT)** — Main Rev.9 and Wing Rev.6 (all four variants),
> the matched pair of Issue #270 **in its final Stage 2d shape** —
> Main tabs with connector-aligned fronts (J2 skew 22°, J3 skew
> 17° to the board edges; R0.50 fillet at the J2 diving corner),
> Wing notches simplified to three tab-parallel straights with
> R0.55 fillets at a minimum seam of 0.56 mm (overlap 0) —
> supersede Main Rev.8 and Wing Rev.5 as the order baselines
> under D-042/D-043. Tray relief totals 6.52 / 6.31 mm³ stand as
> adopted in the low-deck production record. All other D-043
> terms (FH12 MP-land flag, pre-fold lane measurement ≤1.30 Ω,
> Junana measurement, pitch decision, Wing assembly method) are
> unchanged.

Methods/scripts: `.issue270-runtime/` (geom2b, build-main-rev9,
build-wing-rev6, verify-main-rev9, verify-wing-rev6, gates-2b,
case-delta, make-packages-2b; Stage 2d: plan-2d, design-main-2d,
build-main-rev9-2d, verify-main-2d, design-notch-2d,
build-wing-rev6-2d, count-segments-2d, gates-2d, case-delta-2d)
on branch `issue-270-main-outline`.
