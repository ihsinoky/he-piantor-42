# Issue #248 — REPORT A2: row-aligned slope drawings

2026-11-14. **2D alignment revision only; no Phase B or production CAD.**
[Plan PNG](plan-a2.png) / [SVG](plan-a2.svg),
[sections PNG](sections-a2.png) / [SVG](sections-a2.svg),
[tables](tables-a2.json), [region masks](raised-regions-a2.geojson).
Phase A files remain unchanged; this report supersedes their slope geometry and
clarifies their south-fastener assessment. Latest [issue/comments snapshot](sources/issue248-a2.json)
records the aluminium decision after the superseded printed-plate proposal.
Main Rev.7, Wing Rev.4 and **D-038 aluminium plates remain fixed**.

**Every Z value below and in the drawings is provisional**, on Phase A's
unmeasured Junana **q=1.50** assumption and conditional low stack: PCB underside
7.35, plate top 13.55, highest keytop/plateau 24.65, drop 11.10 mm.
Phase A's ±1.75 mm keytop sensitivity, cap/skirt measurement gates and all route,
service, USB and fabrication pass conditions remain open. No new assembly PASS.

## Band and interpretation

The ramp now spans the **whole central keyless width**, including both inner
Wing plate margins and the bay above Main, with every intersecting key cut out
by the original rotated 18 mm well. It is no longer limited to the shell triangle.
North of the start is the 24.65 plateau; north strips retain Phase A's outlines.
South of the toe is 13.55. Outer/palm/thumb margins remain low. Plan colours
separate all four regions; dotted red boxes show conservative GH XY projections.

The issue text/comments contain no image attachment or image URL. Consequently
these explicit choices implement the written PO intent; they do not claim a
pixel comparison against an unavailable PO image:

- “Second row” is R1; “third row” is R2 in the aperture CSVs. Row edges are
  **17 mm pitch-cell edges**, ±8.50 from centres, consistent with the requested
  approximately 34 mm band. They are not measured Junana rims. Using the assumed
  16 mm cap rims instead gives 33 mm and about 18.59°, a different interpretation.
- Follow the staggered row-centre polyline offset by those half pitches, in each
  Wing's actual rotated coordinates. Extend its innermost-column C5 segment
  straight across each half of the bay; mirrored segments meet at X0, making
  chevron start/toe lines and two planar ramp facets. No arbitrary horizontal
  connector or widened centre run is introduced. At C5 the start is local
  Y27.50 and toe Y−6.50: **34.00 mm normal run, 18.08°**.
- The centre cut has start **Y27.944**, toe **Y67.204**, run **39.260** and
  apparent section angle **15.79°**, because it crosses the facets obliquely.
  This is the same 18.08° surface, not a relaxation of the local 34 mm band.
  In the bay `Ystart=27.943753−|X|/√3`; `Ytoe=67.203571−|X|/√3`.
- Extend the central footprint over each inner Wing margin from 9 mm outward
  of the C5 centre inward to the deck edge, then subtract all wells. No narrow
  infill between regular keys. Section B-B uses left local X45, beyond the
  inner regular wells, and runs normal to the row edges.

The 42 assumed 16 mm swept caps have ≥1.00 mm planar gap to raised masks;
Phase A's 0.50 allowance leaves ≥0.50, against the unchanged ≥0.30 requirement.
These remain envelope calculations, not measured full-press or puller acceptance.

## Main and Fly verdicts

Use **2.00 mm vertical roof skin** and **0.30 mm free clearance**, as in Phase A.
Dimensions derive from the adopted #246 17 mm assembly index, translated −8.65 Z;
GH checks deliberately use complete conservative AABBs, not an X0 intersection.

| Obstacle | Top Z | Lowest nominal underside | Raw vertical gap | Verdict |
|---|---:|---:|---:|---|
| Main GH, each projected box | 13.10 | 11.55 | **−1.55** | FAIL conservative envelope screen |
| Actual south cover screw heads | 13.55 | 11.55 | **−2.00** | Cannot retain closed roof here; openings required |
| Actual south cover spacers | 12.05 | 11.55 | **−0.50** | Unchanged spacer/roof geometry conflicts |
| Restored bare Main screw reference | 10.65 | 11.55 | +0.90 | Clears by 0.60 beyond requirement; **not adopted hardware** |
| Translated Fly south storage, OD2 | 12.95 | 11.55 | **−1.40** | FAIL nominal roof screen |

**Main GH pocket concept:** each reservation is X10.529…27.096 (mirrored
negative on left), Y30.315…51.860. Add 0.30 horizontally on every side: each
pocket footprint **17.167 ×22.145**. Its ceiling must be **Z13.40**, requiring
up to **1.85 mm** removal from the nominal underside. At the south/outward
projected corner, the external surface is already Z13.55: only **0.15 mm skin**
remains. Section C hatches this removal. It gives nominal geometric clearance,
**not an acceptable printed closed roof**; Phase A's 2 mm roof is not silently
waived. The boxes are conservative projections, so exact component geometry may
reduce the pocket; that possibility is not a clearance claim.

The nearest closed-roof alternative retaining 2 mm and 0.30 gap is a local
external blister to at least **Z15.40**, up to **1.85 above** the specified low
surface. A through opening preserves the surrounding slope but sacrifices a
continuous closed face. Both depart from the requested uninterrupted row-band
form and require review. Neither is adopted in the main plan.

**South hardware correction:** #246 `study.py` deletes `screw-main-H2/H3` and
uses `cover-screw-2/3` plus 3 mm POM spacers. Phase A's Z10.65 screw calculation
therefore described a restored bare-head concept, not unchanged adopted
hardware. For unchanged cover screws, concept access openings must clear the
Ø4.00 heads: **Ø4.60 minimum** with 0.30 radial clearance, centred at
X±31.892683 / Y64.40. These are intentional exterior openings, not screws
clearing an intact roof. Spacer Ø4.50 needs **Ø5.10** clearance-pocket footprint;
ceiling **Z12.35**, removal **0.80**, leaves **1.20 skin**. To retain an intact
2 mm roof, an unsupported-clearance concept instead shortens the 3 mm spacer
to **2.20 mm** (top 11.25), but it then ceases to bear on that roof. Support,
screw seating/length, service access and retention must be redesigned together;
none is qualified here. Restoring bare screws and independent shell retention
is another unassessed alternative. Boards and holes remain fixed.

**Fly:** saved path samples are before Delta+6; apply +6−8.65 = **−2.65 Z**,
not −8.65 directly to those samples. Connected length stays 170.000 mm; radius
1 and unchanged curvature retain the baseline length/R5 evidence, but not the
new collision gate. The screen evaluates the lowest roof over a conservative
radius-one XY square per sample. Minimum gap is **−1.40** on the south excursion
near Y61.12. A pocket ceiling **Z13.25** gives 0.30 gap but needs **1.70** depth,
leaving **0.30 skin**, also unaccepted. The nearest alternative preserving the
PO exterior is to redress south storage northward, retaining exactly 170,
R≥5 and the other harness/service/USB gates. No replacement route is drawn or
certified. A local 2 mm roof blister would require Z15.25, +1.70, and would
change the PO exterior.

**Wing toe:** a 2 mm hollow roof would intersect the intact aluminium near the
toe. B-B clips the underside to the plate top: the last **6.13 mm** is a solid
wedge tapering from 2 mm to zero. This is an explicit drawing concept, not a
manufacturable feather-edge approval. Joint termination, attachment and loads
remain unresolved; the aluminium is not cut, replaced or formed with the raise.

## Verification and reproduction

Run `TMPDIR="$PWD/.issue248-runtime" python3 hardware/case/issue-248-lowdeck-raise/analyze-a2.py`
from repository root, using Phase A's Matplotlib/Shapely environment. The script
asserts 42 cap gaps, 34 mm normal band width, both Wing intersections, bay
coverage and exclusion of wells. PNG/SVGs were visually checked. Numeric checks
screen Main boxes and the sampled Fly envelope only; no production solids,
complete collisions, physical cap tests or new route qualification were run.
[Hashes](artifact-sha256-a2.json) bind the new artifacts and their source inputs.
