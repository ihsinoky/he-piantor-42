# Issue #248 — REPORT A4: north strips trimmed to slope start

2026-11-14. **Small 2D revision only; no production CAD or Phase B.**
[Plan PNG](plan-a4.png) / [SVG](plan-a4.svg),
[sections PNG](sections-a4.png) / [SVG](sections-a4.svg),
[tables](tables-a4.json), [region masks](raised-regions-a4.geojson).
A–A3 artifacts are retained. A4 implements the PO-approved strip trim; it
supersedes A3's conflicting north-strip outlines only.
**Every Z is provisional on unmeasured Junana q=1.50. No assembly PASS.**

| Strip | Material trimmed from A3 (mm²) | South-of-start material retained outside slope footprint (mm²) |
|---|---:|---:|
| Left | 13.614775389 (13.614776 rounded) | 0 |
| Right | 13.614775514 (13.614776 rounded) | 0 |
| Total | **27.229550903** | **0** |

Areas count actual strip material after the unchanged wells are cut. The tiny
left/right difference is inherited coordinate rounding. Each revised strip is
exactly its A3 mask minus its intersection with the slope: no other extents
change. All original south-of-start material is inside the slope footprint;
none needs retaining outside it. Removed material spans Y1.935592550…5.369357464.
Each strip shares a 7.929940 mm boundary with the slope on the start line.
**Overlap area is now exactly 0 mm²; maximum height disagreement is 0 mm**
(previously 27.229551 mm² / 1.041990 mm). At the shared edge both surfaces are
Z24.65. Section E at X−6, mirrored at X+6, shows the plateau ending at the line
and the slope taking over; dotted A3 extensions are removed-material references.
The original slope surface fills the trimmed footprints.

**Cap clearance: PASS for the unchanged assumed 2D swept envelopes.** All 42
assumed 16 mm cap squares remain at least 1.00 mm from the revised raised
material; the existing 0.50 allowance leaves at least **0.50 mm**, above the
unchanged **0.30 mm** requirement. Every rotated 18 mm well still wins over
every surface, including R0/C5 where start crosses the wells. Lines through
wells are references, not filled edges. Actual Junana skirt, full 3.70 travel,
rocking and extraction-tool clearance remain physical gates.

**Current agreed 2D design:** fixed Main Rev.7, Wing Rev.4 and D-038 aluminium
plates; conditional low deck/plate top **Z13.55**, PCB underside Z7.35 and
plateau/north strips **Z24.65**, drop 11.10. Assembly Y increases south. The
unchanged X-parallel start is **Y1.935593**, the northmost assumed R1/C5 cap
corner; the unchanged X-parallel toe is **Y38.514431**, the southmost R2/C5 cap
corner. The single slope has assembly-Y run **36.578838 mm**, angle
**16.880638°**, and height `24.65−11.10×clamp((Y−start)/(toe−start),0,1)`.
The central footprint remains the cover plus 20 mm waist bridge and inner Wing
margins: plateau north of start, slope between lines, low surface south of toe.
North strips stay at plateau height up to start wherever they meet that slope;
outer, palm and thumb margins stay low. All 18 mm wells are subtracted. Retain
2.00 mm vertical roof skin and +0.30 mm free gap. All Z remain provisional on
q=1.50; this is the current 2D geometry, not an adopted qualified assembly.

**Still open:** the three A3 conflict screens remain unchanged FAIL:
Main GH **−1.55 mm**, #246 south cover screws **−2.00 mm** (POM spacers
−0.50), and Fly storage **−1.40 mm** raw gaps. Their handling decision is
**pending PO/PMO review**: GH needs a reviewed clearance/roof solution; south
heads need an access-opening/retention redesign with spacer clearance addressed;
Fly needs reviewed redressing while preserving exactly 170 mm and R≥5.
No pocket, opening, reroute or local roof change is adopted by A4. Simple
pockets leave only 0.15 mm GH / 0.30 mm Fly skin, so remain unacceptable against
2.00 mm. Measure the selected installed Junana types (q, skirt, swept envelope,
full press and extraction); retain the ±1.75 mm keytop sensitivity until resolved.
All Phase B gates remain: fourteen complete conductors ≤200 mm with R≥5 and
~30 mm service reserve; exact Fly 170 storage; USB insertion/overmold/cable
30 mm sweeps and physical mating; removable retention, supports and tool/service
access; complete solid collision audit including components, floors, channels,
splices, bosses, joints and the unresolved plate-contact feather edge; physical
cap/palm seam/step, load and inversion acceptance; fabrication, mesh, oriented
220×220 mm bed including brim, fit and tolerance checks. No pass condition is
relaxed and Phase B is not started.

Reproduce: `TMPDIR="$PWD/.issue248-runtime" python3 hardware/case/issue-248-lowdeck-raise/analyze-a4.py`.
Assertions verify exact trim, zero overlap/disagreement, all 42 cap gaps and
well exclusion, and unchanged A3 slope/plateau/low masks, lines, Z, obstacle
minimum gaps and Fly failing-sample count. PNG/SVG drawings were visually checked.
[Hash manifest](artifact-sha256-a4.json) binds the A4 package and source inputs.
