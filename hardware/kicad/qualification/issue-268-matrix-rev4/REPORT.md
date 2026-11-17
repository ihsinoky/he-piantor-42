# Issue #268 — Matrix Rev.4: FPC/ZIF conversion (FH12) — REPORT

Board: `board/m1-matrix18.kicad_pcb` · Package: `manufacturing/` (DRAFT / NOT FOR ORDER)
Baseline: Matrix Rev.3 (Issue #182). This report is the worker deliverable for
PO review; adoption is a separate PO decision (no `docs/decisions.md` edit).

## Change summary

- The top-side JST GH14 wing-link header (BM14B-GHS-TBT, LCSC C265384) is
  replaced by a **Hirose FH12-14S-0.5SH(55)** bottom-contact ZIF
  (LCSC **C5378715**) on **B.Cu** — the same connector and corrected
  #263 footprint (signal lands 0.30 x 1.30, pitch 0.5, land per Hirose
  CL586-0533-0) as Wing Rev.5 / Main Rev.8.
- Placement: same anchor as the GH site, footprint origin (100, 133),
  flipped (rot 180, IsFlipped). Pad row at y = 132.0, **pad 1 east**
  (103.25, 132.0) descending to pad 14 west (96.75, 132.0); MP lands at
  y = 134.2, NC. Housing front reaches y ≈ 137.2 — fully on-board
  (south edge 140.025); mouth faces the south edge, as on Wing Rev.5.
- The Rev.3 GH fanout in the connector zone was deleted (stage 1, 111
  items) and the nine D-024 link nets re-routed. That deletion had also
  severed three U_MUX_C feeds (HALL_5V / MUX_A2 / WING_EN) and split GND
  into east/west fragments plus five isolated pad stubs; all were
  reconnected (see copper disclosure — the reconnection paths are the
  honest extent of this revision's copper changes).
- GND pad stubs were trapped behind the signal-escape via wall (vias at
  y = 130.75 sit 0.50 mm from each GND lane; a 0.30 mm track needs
  0.55 mm). They escape through **0.15 mm necks** in-lane
  (y 131.00 → 129.90, clearance 0.125 mm to the flanking vias, above the
  0.10 mm floor), then join 0.30 mm bridges north of the wall. Each neck
  adds ≈ 2–3.6 mΩ in series with one GND lane — negligible for this
  bench/evaluation board; recorded here because it is a deliberate
  width exception, not an oversight.

## Pin-assignment verification (numerical, from built-board pads)

D-024 content: 1 HALL_5V · 2 GND · 3 MUX_A0 · 4 GND · 5 MUX_A1 · 6 MUX_A2 ·
7 WING_EN · 8 GND · 9 MUX_OUT_A · 10 GND · 11 MUX_OUT_B · 12 GND ·
13 MUX_OUT_C · 14 GND.

| Connector | pad n carries | Result |
|---|---|---|
| Matrix Rev.4 J_WING | D-024 signal n (all 14) | **PASS** |
| Wing Rev.5 17L J_WING | D-024 signal n (all 14) | PASS (reference) |
| Wing Rev.5 17R J_WING | D-024 signal n (all 14) | PASS (reference) |
| Main Rev.8 J2 | D-024 signal 15−n (all 14) | PASS (reversal absorbed at Main) |
| Main Rev.8 J3 | D-024 signal 15−n (all 14) | PASS — signal 7's Main-side net is named `MUX_EN1` (per-Wing enable naming on Main), content identical |

Matrix Rev.4 therefore presents **exactly the Wing Rev.5 arriving order**:
pad n = signal n, MP = NC.

## Bench connection check (vs Main Rev.8, stock FFC)

- Mouth-view handedness (viewer at the connector mouth, up = toward the
  board): Wing 17L LEFT, Wing 17R LEFT, Main J2 LEFT, Main J3 LEFT,
  **Matrix Rev.4 LEFT** — congruent with the adopted Wing↔Main pair.
- Both ends are bottom-contact FH12; the stock Molex Premo-Flex
  **152660149** FFC (the D-042 cable) connects Matrix J_WING to Main
  J2/J3 with the same geometry as a Wing: the cable's reversed arrival
  (k → 15−k) is absorbed by Main's footprint assignment (verified
  above), so Matrix pad n lands on D-024 signal n at the Main side.
- Cable length 152 mm is not a constraint on the bench (boards are
  placed freely); in-case folding is out of scope for this issue,
  as specified.

## Gates

| Gate | Result |
|---|---|
| KiCad DRC (severity-all) | **0 errors, 0 unconnected**, 1 warning (below) |
| ERC | No native KiCad schematic exists for the Matrix (JITX-generated design) — inherited gap, unchanged from Rev.3 |
| Via-pad audit (0.10 mm floor) | Different-net minimum **0.100 mm** (at floor); two same-net exceptions (below) |
| Outline invariant | Edge.Cuts identical to Rev.3, segment for segment |
| Footprint census | 65 = 65; only J_WING differs (connector swap at the same anchor). Sensor field and all measurement features untouched |
| Resistance extraction (reference) | Loop HALL+GND to U_MUX_A/B/C = 91.9 / 44.4 / 107.2 mΩ → 11.7 / 5.6 / 13.6 mV at the 127 mA per-Wing design load, used as a reference figure only (centreline graph model, 1 oz copper). Bench-board figure, not a guarantee |

**Disclosed DRC warning (1):** `track_dangling` on the Rev.3-original
HALL_5V F.Cu bus tail at (112.6, 127.2), 0.20 mm end segment. The tail's
Rev.3 continuation to the old GH fanout was deleted in stage 1 by design;
the tail itself is connected copper (the east HALL bus feeding real
pads). No same-net copper lies within 2.6 mm on either layer to
terminate it on, and removing the arm would delete ≈ 15 mm of original
power copper. Rev.3's DRC was fully clean, so this is a (cosmetic,
electrically inert) regression against that baseline, accepted here
under disclosure rather than by deleting original copper.

**Via-pad exceptions (same-net, disclosed):**
- MUX_OUT_A via at (82.65, 127.35) overlaps the corner of its own net's
  bare test pad TP_W_MUXA.1 by 0.25 mm (annulus-edge basis). The pad is
  a probe point, not a soldered land; no via fill/cap is requested and a
  fabricator DFM query on this site is expected/acceptable.
- HALL_5V via at (122.40, 119.45) is 0.048 mm from the same-net
  C_MUX_C.1 pad edge (no overlap).
- The different-net minimum (MUX_A2 escape via (100.55, 128.00) vs
  TP_W_MUXB.1) sits exactly at the 0.100 mm floor — marginless by the
  project's own yardstick, recorded as such.

## Copper-diff disclosure (Rev.3 → Rev.4, measured)

Changes are confined to the **nine D-024 link nets** — zero changes in
any sensor/measurement net. Segment/via item counts (added / removed)
and change extents:

| Net | + / − | Change extent (mm) |
|---|---|---|
| GND | 67 / 49 | x 85.30–106.90, y 126.70–135.00 |
| HALL_5V | 61 / 5 | x 100.10–122.40, y 115.25–133.00 |
| MUX_A0 | 28 / 1 | x 102.25–105.60, y 127.58–133.00 |
| MUX_A1 | 17 / 10 | x 101.25–103.12, y 128.30–133.00 |
| MUX_A2 | 59 / 17 | x 100.55–111.25, y 125.35–134.10 |
| MUX_OUT_A | 44 / 14 | x 82.00–99.25, y 127.00–133.00 |
| MUX_OUT_B | 19 / 4 | x 95.60–98.70, y 128.50–134.10 |
| MUX_OUT_C | 45 / 5 | x 90.40–117.90, y 111.75–135.40 |
| WING_EN | 28 / 10 | x 97.03–109.70, y 124.20–134.30 |

The core fanout zone is x 95–115 / y 124–135.4 around the connector.
Three reconnection paths reach beyond it to rejoin fragments severed by
the stage-1 fanout deletion: HALL_5V's northern bridge to the east
component (to y 115.25, x 122.40), MUX_OUT_C's path to its island
(to y 111.75), MUX_OUT_A's westward link (to x 82.00) and GND's west
joint (x 85.30). This is more than a connector-only neighbourhood
re-route; the extent above is the measured truth of what the conversion
required.

## Manufacturing package (`manufacturing/`, DRAFT / NOT FOR ORDER)

- `gerber/` — 7 artwork layers + PTH/NPTH drills + job file (same set
  as the Rev.3 package); `m1-matrix18-gerber-review.zip` of the same.
- `paste/` — front 144 apertures (42 top components), bottom 16
  (FH12 lands). Assembly is two-sided in Rev.4: 42 top + FH12 bottom.
- `BOM-jlcpcb.csv` — 43 rows, real LCSC codes carried from the Rev.3
  BOM; J_WING = FH12-14S-0.5SH(55) / **C5378715**. Unmapped: NONE.
- `BOM-jlcpcb-consolidated.csv` — 4 MPN groups with quantities.
- `CPL-jlcpcb-gerber-frame.csv` + `CPL-jlcpcb-gerber-frame-NOTES.md` —
  gerber frame = KiCad (X, −Y), offset (+36, −140) vs the legacy frame
  (#219 method). 42 rows carried over from the verified Rev.3 file;
  J_WING recomputed: housing centroid (100.000000, −134.400000),
  bottom, rotation 180.000000.
- `FABRICATION.md` — board/process requirements incl. the via-pad
  disclosure; `quote-handoff.md` — upload set and inherited gates;
  `drc.json` — the final DRC record (0 errors / 0 unconnected).

## Draft adoption line (for PO decision; not recorded in decisions.md)

> Matrix Rev.4 (FH12-14S-0.5SH(55) on B.Cu, pad n = D-024 signal n,
> DRC 0 errors / 0 unconnected with one disclosed dangling warning on a
> Rev.3-original HALL_5V tail, via-pad exceptions as disclosed) is
> adopted as the Matrix bench-board baseline for the first Main+Matrix
> order, superseding Rev.3's GH14 interface.
