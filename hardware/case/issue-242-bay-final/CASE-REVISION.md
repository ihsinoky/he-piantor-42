# Issue 242 case revision proposal — study only

This is one coherent routing revision, **not adopted production CAD**. Exact
coordinates and changed tray BReps are delivered for each pitch. Main Rev.7,
Wing Rev.4, D-024 nets, Main/Fly heights, Fly seat and USB opening are fixed.

| Item | Delta | Purpose / manufacturing consequence |
|---|---|---|
| Rack | Remove the complete detachable #232 rack | Nothing crosses the lid plane from this accessory. |
| Lower cable route | Replace the elevated #232 detour with two U paths: (±27,−24,5) → (±7,−16,5) → (±7,38,5) → (±23,38,5) → (±23,8,5), R5 centreline | OD5 conservative connected bundle; two 16mm removable leg extensions represent 32mm per side. |
| Lower channels | Subtract OD6 R5 sweeps along those U paths from both trays | Nominal 0.5 radial envelope clearance; centre Z5, cutter bottom Z2 preserves nominal floor surface. No detached slack locker. |
| Rising channels | Subtract a sampled projected route groove with 0.32mm allowance around each OD1 conductor, from Z3.9 to13.9 | Open tray grooves; these alter case material only and cannot clear a fixed PCB. Sampling/rounding limits are recorded; no tolerance clearance certificate is claimed. |
| Splice fasteners, both rows | (−5,−8)/(12,−8) → (0,−8)/(15,−8); (−5,55)/(12,55) → (0,55)/(15,55) | Retain four M2x8 screws. Leave old pilots unused, remove original elevated Ø7 bosses and add Ø7 bosses at new axes, top Z8; redrill Ø1.7 pilots. Splices retain outside dimensions and nominal floor seating. Leave original splice holes unused; drill clearance holes Ø2.2 at new axes. |
| Inner rim / lid edge | Trim inward rim only south of Y−39 at Z14.699…16.201; north of Y−39 fit the lid perimeter around retained rim AABBs with0.30 clearance | Entire D-037 Fly seat/opening protected region remains unchanged. Perimeter fitting keeps the top Z16.20 and cuts no top-face pockets. |
| North lid supports | Two integral OD8 floor-rooted pillars at (−8,−30), (8,−30), top Z14.70 | Print with trays. M2 nut AF4/t1.6 in side-loading4.2×1.7 pocket Z11.4…13.1;1.6 roof. Root Z1 within2mm floor. |
| South supports | Two removable POM spacers OD4.5/ID2.2×3.0 at existing Main H2/H3, (±31.89268,64.4), Z11.70…14.70 | Bear on unchanged Main washers. No bridge traps Main. Removing lid screws releases spacers; Main's north screw still holds the board until service. Main PCB, position and hole pattern stay fixed. |
| Retention | Two M2x6 countersunk screws/two M2 captive nuts north; two M2x10 countersunk screws into existing Main H2/H3 bosses south | South screws replace two original Main M2x6, adding3.8mm nominal boss engagement and no new board hole. OD4×1 heads top Z16.20. Load paths and limits in mechanics.json. |
| Cover | 6061-T6 aluminium; top16.20, bottom14.70; underside-only GH/Fly/USB pockets | GH ceiling15.95/skin0.25, Fly15.80/skin0.40, USB15.20/skin1.00. No upper bulges. Supported machining of thin floors required. |

The groove and screw deltas are actual geometry, not collision exclusions.
Neither PCB may be notched. Every changed tray is checked for BRep validity and
single-solid connectivity. A failure of the completed route rejects this
revision at the evaluated height. The PO's 2026-11-14 update continues with a
separate height-variable round; this close-out only supplies its collision map.
The delta list is not permission to
modify or manufacture production parts.
