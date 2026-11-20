## SWD-only respin: JSWD converted to the official TC2050 footprint

**This PR awaits the D-061 adoption (PO review).** It also carries the margin-gate record from the same round (first two commits). Board SHA-256: `6dfbcb954e57b1a1…` (was `26072619…`, the D-058 edge-fixed board). Manufacturing package remains **DRAFT / NOT FOR ORDER**; no order placed — the JLCPCB quote re-run stays an order-stage item (the ≈$139 quote of 2026-11-19 predates both the edge fix and this respin).

### (a) TC2050 conversion + cable chain

- JSWD's TC2030-NL-class 6-pad field (which omitted the maker's alignment holes and wrongly carried solder paste) is replaced by Tag-Connect's **official TC2050 footprint** — maker's datasheet drawing DWG TC2050-IDC-NL-FP REV A, cross-checked against the KiCad library footprint (max disagreement 0.001 mm): 10 contact pads Ø0.7874 mm with **no paste**, plus the 3 alignment NPTH Ø0.9906 mm.
- Placed at **board (110.5, 135.99), rotation +1.35°** (case frame (+10.5, 148.39); top face, in-case cover-off / bench as before). The desk-study centre (111.5, 136.2) does not survive the official footprint — its east holes collide with the In2.Cu PAD_SCL jog / leave a 0.189 mm web to the outline. The −1.0/−0.21 mm shift plus the rotation keep all three holes clear of PAD_SCL and MUX_EN0 with no drill contact (residual hole clearances +0.04…+0.10 mm vs the 0.25 mm floor, itemised in the REPORT — inherent to the maker hole pattern against pre-existing In2.Cu tracks, which this respin may not move). RPD2/RPD3 clear by ~4.1 mm.
- Pin order = Cortex 10-pin debug (cable straight-through): 1 VTref→SYS_3V3, 2 SWDIO, 3 GND, 4 SWDCLK, 5 GND, 6 SWO→NC, 7 KEY→NC, 8 TDI→NC, 9 GNDDetect→GND, 10 nRESET→RESET_N.
- **Cable correction:** the plain TC2050-IDC-NL ends in a 0.1″ 2×5 IDC and does NOT mate with the nRF52840 DK. The working chain is **DK (PCA10056) debug-out → TC2050-IDC-NL-050-ALL → board**, no adapter. (The relocation study's §E.2 table conflated the two cable variants; corrected here and in the REPORT.)
- Escapes re-routed inside the field box only; nothing else moved — footprint census: only JSWD differs; track census outside the field box: 0 diffs; Edge.Cuts item-identical (14/14).

### (b) Margin gate — why no outline extension, JBATT stays south

With the real Wing Rev.6 outlines placed in the case frame, Main's north diagonals face the Wings across a **2.00 mm FFC channel** and the Wings hook past Main's tab corners. A balanced trapezoidal extension is capped at d = 1.0 mm (residual channel 0.96 mm) — a ~78 mm² strip with no JBATT site; the relocation study's N-TAB region is Wing board, not empty bay (201.60 mm³ intersection). Record: `.issue292-runtime/margin-budget.md`. **JBATT therefore stays at the south edge; its cable drape is fixed case-side (clips/channel + written assembly order) under Issue #296.** No coupled case change is needed.

### (c) Gate deltas (full table in the tree REPORT, respin section)

- Containment: **PASS** (SE hole CLOSE note: 0.489 mm web to outline).
- ERC: **0**.
- DRC (same drc2 method as baseline): 704 → **709–711**, unconnected **2 = the identical baseline GND pair** (item-diff verified), shorting_items **0**. Delta itemised: +2 annular_width / +2 via_diameter (the two Ø0.45 vias; existing-precedent class), +2 via_dangling (old-field vias still connected on inner/back layers), +1 items_not_allowed (planar field intrudes ≤~1.0 mm into the trackpad keep-out rim; J2/J3 precedent), hole_clearance +2 listed / −2 net (maker holes vs the new SYS_3V3 B.Cu route, no contact). Note: this KiCad build's DRC reporting of marginal pairs is run-unstable (709/709/711 on the identical file; variance confined to far-field decomposition items) — the load-bearing results are stable in every run.
- Pad audit vs the maker's geometry: **max error 0.0000 mm** (10 pads + 3 holes).
- Gerbers + drill regenerated (28 files); CPL changes only in the JSWD row. **BOM: no purchasable line changes** — JSWD is a pad/hole field with no part; its descriptive placeholder rows were renamed TC2030-IDC-NL → TC2050-IDC-NL.
