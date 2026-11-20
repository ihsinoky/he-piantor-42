# Issue #292 rev2 — case margin budget + STOP report (2026-11-20)

**Outcome: STOP at the Stage 2/3 gate. The balanced trapezoidal
extension cannot carry JBATT, and the study of record's N-TAB
premise is refuted by measurement. No board change was made.**
The adopted D-058 board file is untouched (SHA 26072619…).
Baseline gates were re-run first (containment PASS, ERC 0,
DRC 702 violations / 2 unconnected pads — the adopted baseline),
so all deltas below are attributable.

## What was measured

Wing placement (the missing input of the relocation study):
Wing Rev.6 17R (tree file `wing-rev6-17mm-right/main.kicad_pcb`)
was fitted into the geometry17 assembly frame against 49
underside-component anchors (bodies 222–270): rotation −29.996°,
translation (−55.355, −23.824), **residual max 0.119 mm, mean
0.006 mm**. J_WING lands at g17 (27.0, −38.91), matching the
fitted record. The placed outline's bbox equals the geometry17
wing slab's bbox exactly; plan areas: real outline 10,755 mm² vs
slab 10,803 mm² (0.4%).

## Margin budget (line by line, board frame unless noted)

| Bound | Measured | Effect on extension |
|---|---|---|
| Wing boards (real Rev.6 outlines, fitted) | Inner diagonals exactly parallel to Main's, **2.00 mm** normal gap along the full diagonal (2.37 at the J3 root); the Wings' inner diagonals extend past Main's tab corners to board (101, 70) / mirror, then turn east/west — a hook that wraps Main's north | Extension offset d with ≥1.0 mm residual → **d ≤ 1.0 mm**. Binding constraint. |
| N-TAB region (study §C: board X 112..124, Y 74..88) | **Inside the right Wing.** A solid of exactly that region at board Z intersects wing_right by **201.60 mm³ = 100% of the tab volume**. Point tests: (118,81), (112,78), (110,74), (114,84), (116,88) all inside the Wing outline | The relocation study's "empty space in the bay" premise is **wrong** — it never placed the real Wing outline (Pilot B territory). N-TAB is dead, and with it the only JBATT site the study found. |
| Bay wall (tray, geometry17) | Wall face ~**0.50 mm** from the diagonals, top raw Z 11.55 (study Z 8.90) | Any d > 0.5 enters tray material → would be a #296 pocket-relief case delta (Rev.8-tab precedent). Not the binding bound, but the coupled case item existed only because of this. |
| North slope cover (strip bodies) | South edge at board Y 71.9, underside study Z ≥ 10.90 — Z-separated from the board | Not binding for any h ≤ 4.5. |
| Plate + installation | Plate material raw Z ≥ 12.05 (≥3.5 mm above board top); tilted settle passes above the board. Centre plate screws at board (94.9, 71.1) / (105.1, 71.1), POM posts above board top | Not binding within the envelope below (screw clearance ≥ 3.3 mm in plan at the max tab reach). |
| FFC envelopes (Wire bodies) | Strip ∩ wires = 0 at board Z for every offset tested (d ≤ 8) | Not binding for the outline. |
| Trackpad Ø40 / antenna / module field | All far from the north boundary (study §C verified) | Not binding. |

## The maximum extension the margin allows

Uniform parallel offset of the north boundary (diagonals keep
their exact 30° angles, tab edge moves north by h, symmetric
about X = 100), terminated on the SE/SW diagonal lines:

- d = 1.0 mm on the diagonals → residual to Wing = **0.96 mm**
  (the ≥1.0-class floor; d = 1.0 is the ceiling, not a target).
- Tab: h up to ~4.5 mm geometrically, but the tab narrows as it
  grows (corners slide along the shifted diagonals): width
  4.00 mm at h = 2.0, **3.19 mm at h = 2.7, 1.11 mm at h = 4.5** —
  a fragile tongue, not a connector site.
- Total gained area at (d = 1.0, h = 2.7): **77.6 mm²** of thin
  strip. JBATT needs a ~9 × 7 mm clear patch plus its VBAT
  corridor and plug envelope; the interior side of the diagonal
  is occupied by the JPAD escape fan (X 104..112, Y 88..99) and
  the converter cluster (study §C census, unchanged). **No site
  exists.** Spending the whole 2.00 mm channel (residual 0.00,
  boards touching) still leaves the study's site 9 mm inside
  the Wing.

Per the brief's rule (≥1.0 mm-class residual; stop rather than
take a thin margin) and PO priority 2 (no margin-less designs),
the respin was **not** executed.

## Executable remainders (for a PO decision)

1. **SWD-only respin — desk-verified clean.** The TC2050 field
   at centre board (111.5, 136.2) (pads X 108.57..114.43,
   Y 135.17..137.23; south pad edge 0.67 mm from the outline)
   contains ONLY JSWD's own 4 escape tracks (SYS_3V3 / SWDIO /
   SWDCLK / RESET_N) — no foreign pads, vias or tracks; RPD2/RPD3
   clear the field by ~3.1 mm and the TC2050 head body by
   ~1.25 mm. Replacing the TC2030 field with TC2050 (10 pads,
   pad-net mapping per Tag-Connect's published footprint;
   signals unchanged, no SWO) is a local change: 1 footprint +
   4 short re-escapes + re-verification. The alternative
   (TC2030 + the maker's 3 alignment holes) needs the official
   footprint's hole coordinates at implementation; the field's
   south row sits 0.67 mm from the edge, so hole placement must
   be checked against the edge — TC2050 is the cleaner option.
2. **JBATT stays south** — the relocation study's Option 1
   (case-side cable management in #296: clips/channel, parking
   clip, written assembly order) remains the standing fix.
   The ≈156 mm cable and its drape are unchanged.
3. A d ≤ 1.0 mm balanced extension is executable but carries
   nothing and was not taken.

## Coupled case item (for the PR record that now does not exist)

No extension was taken, so **Issue #296 needs NO matching recess**
for Main's outline; the bay stays as designed around the D-058
outline. If a future Wing respin ever moves the Wings' inner
diagonals, this budget must be re-measured — the 2.00 mm channel
is a Wing-side property.

## Artefacts

Scripts + data in `.issue292-runtime/`: margin1–8.py,
fit_wing.py (+ wing-fit.npz), board-dump.json, wing17R.json,
baseline-*.txt/.rpt. Board file untouched throughout.
