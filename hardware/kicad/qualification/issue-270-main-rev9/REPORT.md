# Issue #270 — Stage 2b REPORT: Main Rev.9 + Wing Rev.6 (outline-only revision)

Date: 2026-11-17. Basis: adopted Main Rev.8 / Wing Rev.5 (D-043).
Shape spec: Stage 2a design record (`.issue270-runtime/stage2a-design.md`),
approved by the PO 2026-11-17. All work is Edge.Cuts-only in intent;
every deviation from a pure outline change is listed in §5.

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

## 6. Draft adoption line (for the PO; NOT entered in docs/decisions.md)

> **D-044 (DRAFT)** — Main Rev.9 and Wing Rev.6 (all four variants),
> the matched trapezoid-tab pair of Issue #270, supersede Main
> Rev.8 and Wing Rev.5 as the order baselines under D-042/D-043.
> Seam 0.550 mm, tray relief totals 6.52 / 6.31 mm³ adopted in the
> low-deck production record. All other D-043 terms (FH12 MP-land
> flag, pre-fold lane measurement ≤1.30 Ω, Junana measurement,
> pitch decision, Wing assembly method) are unchanged.

Methods/scripts: `.issue270-runtime/` (geom2b, build-main-rev9,
build-wing-rev6, verify-main-rev9, verify-wing-rev6, gates-2b,
case-delta, make-packages-2b) on branch `issue-270-main-outline`.
