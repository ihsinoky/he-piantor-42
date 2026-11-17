# Issue #270 Stage 2c — Connector-aligned Main tabs (2D design study)

PO request (2026-11-18): the Main tab front edge should FOLLOW THE
CONNECTOR — parallel to the FH12's own long axis — because the visible
skew between the connector angle and the board-edge angle bothers them.
This stage is 2D only: no board or case files were modified.
Figures (2D outline drawings): `fig-2c-full-current.png`,
`fig-2c-full-candidate.png`, `fig-2c-zoom-j2.png`, `fig-2c-zoom-j3.png`,
`fig-2c-overlay.png`. Numbers: `stage2c.json` (scripts `s2c_measure.py`,
`s2c_probe.py`, `s2c_design3.py`; failed iterations `s2c_design.py` = v1,
`s2c_design2.py` = v2, diagnosis `s2c_diag.py`).

## Measured angles (from the Rev.9 board file, harness case frame)

Connector long axis = direction of the 14-signal-pad row (PCA over pad
centres; identical to the footprint's mouth line). Board slanted edge =
the Rev.7 edge line each tab sits on. Rev.9 tab front measured from the
built board's Edge.Cuts: length 16.689 at depth d = 4.738, exactly
parallel to the slanted edge at both sites (120.000° / 60.000°).

| Site | Slanted edge line | Connector axis line | **Skew** | Footprint yaw (KiCad) |
|---|---|---|---|---|
| J2 | 120.0° | 142.0° | **22.0°** | +38° |
| J3 | 60.0° | 43.0° | **17.0°** | −43° |

The two sites are NOT mirror-identical: the skew differs (22° vs 17°),
so a connector-aligned tab is a different shape at each site.
Pad field (connector frame about the pad-row centroid): pad corners
span s ∈ ±5.78, w_max = +0.80 (J2) / +0.80 (J3); connector courtyard
s ∈ ±5.05, w ∈ [−5.10, +0.30] (body extends inward from the pad row).

## Candidate design (per site)

Construction (minimal change from Rev.9): keep the Rev.9 trapezoid
body — same 60° walls on the same wall lines, same base — and replace
only the front edge:

- front edge = a straight line **parallel to the connector axis**;
- the front segment runs between the two existing wall lines (the wall
  on the rising side is extended to meet it, the wall on the diving
  side is trimmed back to it);
- the line's position is set by copper, not by the pads (see below):
  w_front = pad w_max + 0.8364 + **0.65 raise** (J2 w = 2.282,
  J3 w = 2.286 in the connector frame).

Why the raise is needed: a front line placed only from the pads
(perpendicular pad clearance 0.8364) dives on its low side into the ZIF
fanout — the fanout tracks fill the tab up to d ≈ 3.5, and at a
17–22° tilt the line drops ~0.3–0.4 mm per mm of run. That version
CUTS 4 fanout tracks (v2, diagnosed in `s2c_diag.py`). Raising the line
parallel by +0.65 mm is the smallest 0.05-step that restores
copper cuts = 0 AND min edge-to-copper clearance ≥ Rev.9's 0.284
(actual 0.323). An earlier v1 (whole trapezoid rotated about the pad
centroid, walls at 60° to the axis) was worse: 5 Main copper cuts and
a Wing pad hit at 16 mm — discarded.

Resulting front segments:

| Site | Length | d range (edge frame) | s range (connector frame) |
|---|---|---|---|
| J2 | 19.228 mm | 0.151 … 7.353 | −9.965 … +9.263 |
| J3 | 17.950 mm | 1.701 … 6.949 | −8.823 … +9.126 |

(d = height above the slanted-edge line; Rev.9's front is a constant
4.738. The candidate front crosses that height near the connector
centre and reaches ≈7.4 / 6.9 at the rising corner, ≈0.2 / 1.7 at the
diving corner — the diving corner still stays outside the board edge
line, d > 0, at both sites.)

## Checks (stage-2a yardsticks; baseline = Rev.9 as built)

Rev.9 baseline reproduced by the same harness: pad clearance 0.8365
(worst J3.14), min copper clearance 0.284, silk min 0.15 — matches the
2b record (0.8364 / 0.284), so the comparison is apples-to-apples.

| Check | Floor / Rev.9 | Candidate | Verdict |
|---|---|---|---|
| Pad-corner → outline clearance | ≥ 0.70 (Rev.9: 0.8364) | **1.4864** (J3.14) | PASS |
| Pads uncovered | 0 | 0 | PASS |
| Main copper cuts vs Rev.9 | 0 | **0** | PASS |
| Min edge-to-copper clearance | Rev.9: 0.284 | **0.323** | PASS |
| Silk min distance / uncovered | 0.15 / 0 | 1.482 / 0 | PASS |
| Inside D-037 silhouette | yes | yes | PASS |
| Case tray relief delta vs Rev.9 | — | **−0.0 L / +0.0 R mm³** | no change |
| Board area | 2650.26 mm² | 2637.72 mm² (+19.85 / −32.40 vs Rev.9) | — |

Wing notches re-derived as the exact 0.55 mm offset of the candidate
Main (same construction as Rev.6, applied on top of it):

| Variant | Seam | Overlap | Extra notch area vs Rev.6 | Copper hits | Min dist to copper |
|---|---|---|---|---|---|
| 17mm-left | 0.550 | 0 | +11.54 mm² | none | 11.50 mm |
| 17mm-right | 0.550 | 0 | +10.29 mm² | none | 1.90 mm |
| 16mm-left | 0.550 | 0 | +11.54 mm² | none | 5.70 mm |
| 16mm-right | 0.550 | 0 | +10.29 mm² | none | 1.90 mm |

All Wing outlines stay inside the D-037 silhouette.

## Honest costs

- The tabs become **asymmetric and site-specific**: J2's front runs
  19.2 mm long and climbs to d = 7.35 at its rising corner (≈2.6 mm
  prouder than Rev.9's front at that corner); J3's reaches d = 6.95.
  Both stay inside the case silhouette, and the tray relief does not
  change (the proud corners fall outside the tray pocket polygons) —
  but the case tray / Wing notch pairing must be adopted together,
  exactly as with Rev.9/Rev.6: the candidate Main overlaps the Rev.6
  notch on the rising side.
- The Wing notch grows by ≈10–12 mm² per side (bare corner area only;
  nearest Wing copper ≥1.9 mm away).
- The diving-side front corner sits low (d = 0.15 at J2): the front
  edge nearly grazes the slanted-edge line there. It is a thin sliver
  of tab — mechanically the weakest-looking point of the outline, and
  the first place a build-time fillet (R ≤ 1.0, as allowed in 2a/2b)
  would be spent.
- Pad clearance grows to 1.4864 — the connector sits deeper in the
  tab than Rev.9. No electrical change (outline only), but the FFC
  mouth clearance to the board edge grows on the rising side and
  shrinks in angle on the diving side; the fitted-audit would need a
  re-run at build stage, as in 2b.

## Verdict

**Feasible within all floors.** A connector-aligned tab exists at both
sites with every stage-2a yardstick satisfied — pad clearance 1.4864
(floor 0.70), copper cuts 0, min copper clearance 0.323 ≥ Rev.9's
0.284, seam 0.550 / overlap 0 at both pitches, silhouette contained,
tray relief unchanged. The price is a longer, asymmetric front that
stands up to ≈2.6 mm prouder at the rising corner and a ≈10–12 mm²
deeper Wing notch per side.
