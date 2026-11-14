# Issue #248 — REPORT A3: straight cap-end lines

2026-11-14. **2D alignment only; no production CAD or Phase B.**
[Plan PNG](plan-a3.png) / [SVG](plan-a3.svg),
[sections PNG](sections-a3.png) / [SVG](sections-a3.svg),
[numeric tables](tables-a3.json), [region masks](raised-regions-a3.geojson).
The newest [Issue comment](sources/issue248-a3.json) was read first: the toe
must be X-parallel. A/A2 files are retained; A3 supersedes their band geometry.
Main Rev.7, Wing Rev.4 and D-038 aluminium plates remain fixed.

**ALL Z values are provisional on unmeasured Junana q=1.50:** PCB underside
7.35, plate top 13.55, plateau/north-strip top 24.65; drop 11.10 mm. Retain
2.00 mm vertical roof skin and **+0.30 mm minimum free gap**. The ±1.75 mm
keytop sensitivity and all cap/skirt, extraction, route/R5, service, USB,
fastener-retention and fabrication gates remain open. No assembly PASS.

## Band geometry and exact cap references

Use A/A2's **assumed 16 mm swept cap squares**, not A2's 17 mm pitch cells.
“Top/bottom end” means minimum/maximum **assembly Y** of the transformed cap;
for these rotated squares each supporting X-parallel line touches a corner.
Assembly Y increases south. Mirrored corners have equal Y to <1e−9 mm.

| Line | Left Wing-local cap corner (mm) | Assembly XY, left / right (mm) |
|---|---|---|
| Start: R1/C5 northmost | (25.055556, 27.000000) | (∓46.047455, **1.935593**) |
| Toe: R2/C5 southmost | (41.055556, −6.000000) | (∓48.691049, **38.514431**) |

Right local X is the negative of left local X; local Y is identical.
**Start is a PMO ASSUMPTION pending PO**, explicitly drawn despite the north-strip
inconsistency below. Toe is the binding PO correction. Both lines are single
assembly-X-parallel lines, with **no chevron**.

Centre A-A and all assembly-Y cuts at the C5 reference X positions have
**36.578838 mm run / 16.880638°**. The height field is independent of X:
`Z=24.65−11.10×clamp((Y−1.935593)/36.578838,0,1)`.
For comparison with A2's Wing-local row-normal section, the new run is
**42.237604 mm / 14.724330°**, including at C5 local |X|33.055556
(start local Y31.618802; toe −10.618802). These are oblique sections of the
same plane. B-B retains A2's left local X45 cut; its start/toe local Y are
38.514930 / −3.722674. Wells interrupt the nominal surface at keys.

The central footprint, inner Wing margins, north-strip outlines and rotated
18 mm wells are unchanged from A2. Plateau lies north of start; low surface
lies south of toe. All intersecting wells remain removed.

## Re-run conflict screens

Raw gap = lowest nominal underside minus obstacle top; passing needs ≥+0.30.
Use complete conservative GH/hardware projected AABBs, as in A2, and the same
translated sampled Fly OD2 envelope (radius-one XY square per sample).

| Screen | Obstacle top Z | Minimum underside Z | Raw gap (mm) | Verdict and change from A2 |
|---|---:|---:|---:|---|
| Main GH, each side | 13.10 | 11.55 | **−1.55** | **FAIL; worsens extent**, same minimum |
| #246 south cover screw heads | 13.55 | 11.55 | **−2.00** | **FAIL; unchanged** |
| #246 south POM spacers | 12.05 | 11.55 | **−0.50** | **FAIL; unchanged** |
| Fly 170 south storage | 12.95 | 11.55 | **−1.40** | **FAIL; worsens extent**, same minimum |

GH area below +0.30 grows **40.56→322.10 mm² per full projected box**
(40.49→319.10 inside the footprint). No improvement: the roof reaches its low
level sooner. A pocket expanded 0.30 mm per XY side (17.167 ×22.145 mm), with ceiling
Z13.40, still needs up to 1.85 mm removal,
leaving only **0.15 mm skin**, unacceptable against 2.00. Detail C shows this.
The AABBs include ~3.48 mm² outside the central footprint; the minimum also
occurs inside it. Exact GH solids could reduce these conservative envelopes.

Adopted #246 hardware is `cover-screw-2/3` and 3 mm POM spacers, **not** restored
bare Main screws. Both remain wholly under the low surface in A2 and A3.
A head access opening / retention redesign remains necessary; spacer clearance
to Z12.35 would leave only 1.20 mm skin. A2's concepts are not adopted here.

Fly samples retain the correct +6−8.65=**−2.65 Z** translation and connected
length **170.000 mm**. Samples below +0.30 increase **257→869 of 2001**;
these counts indicate extent, not arc length. An A3 limiting sample is
(X0, Y37.538119), axis Z11.95; A2's worst south excursion also still fails.
A pocket to Z13.25 leaves only **0.30 mm skin**. No reroute or new R5 qualification.

## New inconsistencies and edge checks

- **North strips versus start:** retained Z24.65 strips overlap the new slope
  by **27.229551 mm²**, over Y1.935593…5.369357. Maximum height disagreement is
  **1.041990 mm**. Plan red hatch preserves both incompatible instructions;
  no height priority or local transition has been silently chosen.
- Within the central footprint the start crosses R0/C5 wells (19.630 mm chord)
  and clips R1/C4 wells (1.155 mm); its R1/C5 reference well chord is 3.155 mm.
  Toe clips R2/C5 wells (3.155 mm) and crosses T1 thumb wells (12.830 mm),
  including a 10.866 mm cap chord. Values are per Wing. Thus the straight
  *reference lines* cannot be uninterrupted material edges through these wells.
  All wells are cut, so **no new nominal cap collision** results: all 42 caps
  retain ≥1.00 mm planar gap; after the existing 0.50 allowance, ≥0.50 exceeds
  the unchanged 0.30 requirement. T0/T2 have no toe intersection inside this footprint.
- Band ends still meet unchanged low Wing decks with unresolved sidewall/joint
  treatment (up to 11.10 mm rise); boards and plates are not modified.
  B-B's plate-contact wedge grows **6.13→7.61 mm** and tapers to zero at toe.
  The feather edge remains unqualified; a hollow 2 mm underside cannot extend
  through the fixed aluminium. This is an existing construction issue, not a new PASS.

Reproduce from repository root:
`TMPDIR="$PWD/.issue248-runtime" python3 hardware/case/issue-248-lowdeck-raise/analyze-a3.py`.
Assertions check reference symmetry, run, endpoints, 42 cap gaps, well exclusion,
both Wing intersections, central coverage, Fly length and A2 minimum-gap comparison.
PNG/SVG drawings were visually checked; [hash manifest](artifact-sha256-a3.json)
binds A3 artifacts and inputs. Screens remain envelope calculations, not production
solid collisions or physical validation.
