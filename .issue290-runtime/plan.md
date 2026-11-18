# Issue #290 — Trackpad addition study: plan

Study only. Wireless variant first; placement geometry shared with the wired case.
Deliverables: `.issue290-runtime/trackpad-study.md` + `.json`.

## Inputs read first
- docs/decisions.md D-037 (outline, Fly seat), D-038 (aluminium switch plate, full-cover
  shape follows case silhouette), D-041 (Delta+6 bay cover — superseded baseline),
  D-042 (low deck, plate top Z10.90, keytop Z22.00 provisional).
- Case geometry source of truth: `hardware/case/issue-261-lowdeck-full/`
  (REPORT.md + preview.step + sources/audit_static.py body set).
  Datum: tray floor Z1.60 ribbed, Wing PCB underside B=4.70, plate top 10.90.
- Carried inputs (unmerged branches): antenna in un-plated central bay / south PETG
  zone; NiMH AA x4 under-case pod (D-048); runtime baseline 0.533 Wh/day = 16.2 days
  on 8.65 Wh delivered (Issue #284); MCU nRF52840 (D-052); Unifying mouse frames
  exist, one device type per pairing, latest fw blocks char keys from non-keyboard
  types (Issue #280).

## Sections
1. Parts — Cirque GlidePoint TM040040 / TM035035 / TM023023 + successors.
   Datasheet dims (active area, module OD, thickness, overlay/clearance needs),
   interface, V/I (active + idle). Availability scan: exact SKU, 2+ distributors,
   stock observed 2026-11-19, lifecycle, price. Channels: Cirque store, Mouser,
   DigiKey, beekeeb / keyboard-community channels.
2. Placement — measure from the case tree data (never from summaries):
   (a) central bay, (b) one Wing thumb cluster, (c) south-centre below Wings.
   Fitted check per site vs plate-10.90 stack + key field; second-way check
   (corner section heights) for the winner. Conflicts: (a) antenna zone + cover
   RF opacity, (b) Wing sensor field + outline, (c) battery pod + palm space.
   Any height raise stated in mm.
3. Power — part draw (active/idle, stated usage assumption) added to the #284
   daily model (0.533 Wh/day); new runtime on 8.65 Wh. Wake/poll behaviour.
4. Protocol/FW — Unifying: combo devices (K400/K830 class) device type and
   frame mix under one pairing, from LOGITacker/Solaar/logiops sources
   (repo+file cited). New open items for the Issue #287 bench proof.
   FW: nRF52840 I2C + ZMK/QMK Cirque prior art state.
5. Verdict — rank by PO priorities (cost > low rework > freedom > speed);
   each rejection names its binding constraint with the binding number.

## Verification invariants
- Geometry measured from case tree data; winner re-checked a second way.
- Datasheet numbers cited per figure (doc + section where feasible).
- Prices/stock observed today and dated; UNVERIFIED where a page cannot be read.
