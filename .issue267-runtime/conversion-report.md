# Issue #267 — package conversion report

Converted the five Issue #263 DRAFT packages to JLCPCB-ready form
(`BOM-jlcpcb.csv` + `CPL-jlcpcb-gerber-frame.csv` + `quote-handoff.md` per
package). Native `BOM.csv` / `CPL.csv` untouched. Script:
`.issue267-runtime/convert.py`; raw results: `conversion-results.json`.

## Per-board results

| Board | BOM rows (native → JLCPCB) | Designators mapped | Unmapped | Frame offset (mm) | Outline max dev | CPL max dev |
|---|---|---|---|---|---|---|
| main-rev8 | 61 → 54 | 55 / 55 | none | (+0.000000, +0.000000) | 0.000000 mm | 0.000000 mm |
| wing-rev5-17mm-left | 7 → 4 | 49 / 49 | none | (+0.000000, +0.000000) | <0.000001 mm | 0.000000 mm |
| wing-rev5-17mm-right | 7 → 4 | 49 / 49 | none | (+0.000000, +0.000000) | <0.000001 mm | 0.000000 mm |
| wing-rev5-16mm-left | 7 → 4 | 49 / 49 | none | (+0.000000, +0.000000) | <0.000001 mm | 0.000000 mm |
| wing-rev5-16mm-right | 7 → 4 | 49 / 49 | none | (+0.000000, +0.000000) | <0.000001 mm | 0.000000 mm |

## BOM mapping sources
- Main: Main Rev.6 package BOM (Rev.7 has no manufacturing package in the
  tree; Rev.7 = Rev.6 + J2/J3 connector swap only, and Rev.8 replaces those
  connectors with the FH12 anyway). Two Rev.6 blank rows filled with the
  adopted substitutes from docs/issue-175-main-dual-wing-final2.md
  (PR #177/#189): C26/C27/C28 → TDK C3225X7R1C226MT000N / **C342699**;
  R17 → Yageo RT0603BRD0754K9L / **C728593**. L1 = **C3033018** (order-time
  rule; stock 19,053 on 2026-11-16). J4 = **C588524**.
- Wing: Matrix Rev.3 package BOM (same parts): DRV5055A3QDBZR / C266128,
  GRM188R71C104KA01D / C45000, TMUX1208PWR / C494728.
- Excluded as non-orderable (Rev.6/Matrix practice): NPTH mounting holes and
  test points — Main: H1–H3, TP1–TP4 (7 rows); Wing: NPTH_1.7 (42),
  NPTH_2.2 (4), test-point pads (15) per variant.
- BOM format: Rev.6 4-column header `Comment,Designator,Footprint,LCSC Part #`,
  grouped rows as in the native BOM (Main J2,J3 share one row → 54 rows for
  55 designators).

## FH12 — known unsourced item (all five packages)
Hirose FH12-14S-0.5SH(55) (Main J2/J3, Wing J_WING) keeps the placeholder
`C-HIROSE-FH12-14S`. No LCSC code exists in any project source and none was
invented. The JLCPCB quote flow will flag it unmatched; how it is handled
(consignment / separate purchase + hand-fit) is for the quote round to state.

## CPL frame verification
Unlike the Rev.6 legacy CPL (which needed a +62.107318 / −137.9 mm shift),
the #263 packages were exported by kicad-cli with gerbers and positions in
the same absolute frame. Per board, the translation was fitted from the
source board's Edge.Cuts geometry against the package's Edge_Cuts gerber
(robust point-pairing fit; the gerbers carry a stray move to the origin that
breaks naive bbox fitting) and came out **(0, 0)** everywhere; every outline
vertex then matched a gerber vertex within float noise (≤2.9e-14 mm), and
every converted CPL point matched the source board's footprint origin
through the same transform with max deviation **0.000000 mm**. Wing CPLs
are all `bottom` layer (single-sided underside assembly), rotations carried
from the native export unchanged, as in the project's earlier packages.

## Remaining for the quote round (not this task)
JLCPCB upload + quote figures; FH12 sourcing verdict (DigiKey-class price);
Wing bare-board price; Matrix Rev.3 quote refresh (its package was already
JLCPCB-ready). Wing assembly method stays undecided (Matrix evaluation).
