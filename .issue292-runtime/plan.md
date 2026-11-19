# Issue #292 Stage 1 — Wireless Main design study: plan

Worker: Muse (PMO-dispatched). STUDY ONLY. Worktree he-piantor-wmain,
branch issue-292-wmain (from origin/main 06de20b83).

## Sources read first
- docs/decisions.md: D-019 (4L/1.2mm/0.10 rules), D-024 (dual-Wing scheme:
  pin1 HALL_5V; 2/4/8/10/12/14 GND; 3/5/6 MUX_A0/A1/A2; 7 indep enable;
  9/11/13 MUX_OUT_A/B/C; common address + 3 ADC paths; 127 mA/Wing design
  load), D-026 (TPS63070 forced-PWM buck-boost -> 5.2 V; far target 4.60 V;
  common/branch loop targets <=50 mOhm), D-027 (input req at board
  connector), D-035 (J4 Pico-EZmate to Fly), D-042+amendment (FH12 ZIF both
  boards; stock FFC 152660149 folded; conductor order k->15-k absorbed in
  Main footprint; lane acceptance <=1.30 ohm), D-043 (FH12-14S-0.5SH(55)
  bottom-contact all sites), D-046 (Rev.10 adopted), D-047 (GH rejected).
- Rev.10 board data (issue-275-main-rev10/main-rev10/main.kicad_pcb),
  extracted 2026-11-19: outline bbox KiCad x 64.107..135.893,
  y 75.732..137.900 (south edge y=137.900, x 66.107..133.893);
  area 2644.24 mm2 (REPORT.md). Case frame: case_x = kicad_x - 100,
  case_y = kicad_y - 70 (+Y south); Main south edge = case Y 67.900.
  Holes: H1 (100, 79.268) on axis; H2 (68.107, 134.400);
  H3 (131.893, 134.400) — exact mirror pair (D-046).
  J2 FH12 (75.745, 111.824) rot +43; J3 (124.255, 111.824) rot -43
  (mirror pair). J4 EZmate (100, 90.000) rot 180 (to Fly, north centre).
  U1 RP2040 (100, 119); U3 W25Q16 (105, 110); U4 AP2112K-3.3 (87.5, 116.5);
  U5 TPS22919 (82, 126) Hall switch; U6 TPS63070 (97, 101) + L1 (101.5, 101.5).
  Vfar binding J3 4.754 V (REPORT.md §3).
- Case tree hardware/case/issue-263-lowdeck-production (low-deck baseline).

## Fixed design inputs (unmerged decisions, per brief)
D-048 NiMH AA x4 pod, external charging; D-049 TMAG5253BA3 Wings, 3.3 V
Hall rail, EN per MUX bank, divider removed, rail-drop budget <=50 mV class;
D-050/D-052 single nRF52840 module; D-053 trackpad TM040040 central bay,
dia.40 Main keep-out, antenna home = south PETG zone; case south outline
straightened (band 13.802 mm deep from Main wall line, case frame).

## Sections (checkpoint-commit each)
1. Module selection + certification verification + availability scan.
2. Power tree (NiMH -> SYS 3.3 V, Wing Hall rail, trackpad, battery sense)
   with efficiency at #284 load points and runtime delta.
3. USB-C role (Fly deleted): bare USB-C vs debug header.
4. Outline / keep-out map from Rev.10 data (trackpad dia.40 at KiCad
   (100,118) = case (0,48); module/antenna zone; south band; battery conn).
5. Wing-link electricals: 14-pin assignment vs D-024, far-Wing budget
   arithmetic at D-049 burst currents, FH12/FFC carry-over verdict.
6. wmain-design.md + .json assembly, Stage 2 outline + gates.

## Invariants
- Every carried number cites source file/decision.
- Certification only from maker/regulator pages; else UNVERIFIED.
- Keep-out map from extracted Rev.10 data above, not memory.
# Issue #292 Stage 2 — Wireless Main KiCad implementation: plan

Worker: Muse (PMO-dispatched). Worktree he-piantor-wmain, branch
issue-292-wmain, Draft PR #293. Study: .issue292-runtime/wmain-design.md.

## Entry gates (BEFORE board work; FAIL = stop and report)
- G1 Module stock TODAY: EYSKDNZWB / ED2840AA2 at >=2 channels
  (LCSC/JLCPCB, Mouser, DigiKey, TME, Chip1Stop/Kaga FEI). Need:
  comfortably above prototype qty (5 boards + spares).
- G2 Model-transition pin compatibility: from Taiyo Yuden's own
  documents, EYSKDNZWB -> ED2840AA2 pin/footprint compatibility;
  design for the part that can actually be ordered.

## Implementation (new tree hardware/kicad/qualification/issue-292-wmain/)
- Rev.10 outline + symmetric holes UNCHANGED.
- Module in SW pocket (x 69.5..79.1, y 118.4..131.3 KiCad), antenna
  end south; antenna shadow (y 131.3..137.9, same x span) copper-free
  all layers; >=0.5 mm margins to J2 body / H2 reservation / circle /
  outline verified from placed data.
- TPS63070 re-set 5.2 V -> 3.3 V SYS, forced PWM dropped; AP2112K
  LDO deleted. TPS22919 -> HALL_3V3 -> J2/J3 pin 1. Trackpad load
  switch -> PAD_3V3. Diode-OR VBUS into converter input; blocking
  element on pack line (no back-feed by construction).
- Battery connector at SE south edge ~(124,136) KiCad; gated 1M/1M
  divider -> module AIN.
- J2/J3 FH12-14S-0.5SH(55) inherited; assignment per study §5.1
  (pin1 HALL_3V3, pin7 per-Wing EN, k->15-k absorbed in footprint).
- Trackpad interface (I2C SDA/SCL + DR + PAD_3V3/GND) to bay
  disconnect footprint in north sliver (study §4.2: y 98..103,
  x 84..91 or 109..116).
- USB-C: run study §3 placement decision — mini-tab (<=10x12 mm,
  north apex) vs J4-footprint carrier; fitted check decides; take
  the passing option. 16-pin receptacle, USBLC6-class ESD, 5.1k CC.
- Trackpad keep-out: circle r20 @ KiCad (100,118) — no components.
- SWD test pads retained (Rev.10 TP precedent). Button + LED (15-GPIO
  budget, study §1.1).

## Gates to report (all with numbers)
Native schematic + ERC 0; DRC severity-all; unconnected 0; via-pad
audit (diff-net min vs 0.10 floor / 0.125 target, sub-target sites
listed); keep-out audit from placed data (trackpad dia.40, antenna
shadow, south band); Wing-link assignment census both connectors
(14 pins each) vs study §5.1 AND wireless Matrix/Wing signal content;
far-Wing rail budget recomputed from routed board (branch loop
<=250 mOhm target; far-point drop @20 mA burst vs <=50 mV);
fitted check module + USB vs case production tree.

## Package
manufacturing/ per #267: BOM-jlcpcb.csv (module LCSC code verified
character-exact or hand-fit with reason), CPL-jlcpcb-gerber-frame.csv,
FABRICATION.md, quote-handoff.md (DRAFT / NOT FOR ORDER), REPORT.md
with gate table + draft adoption line.

## Invariants
- Failing gate states shown before changes.
- Assignment/keep-out tables generated from placed board data.
- Checkpoint-commit per stage; never /tmp.
# Issue #292 Stage 2 RESUMED (D-055 basis) — plan addendum 2026-11-19

Module basis CHANGED by D-055: Raytac MDBT50Q-1MV2. North tab
outline addition ACCEPTED (study est. +~420mm2); symmetric holes
unchanged. Everything else in Stage 1 stands.

## Entry checks (checkpoint-commit BEFORE board work)
- E1: MDBT50Q-1MV2 stock re-verified TODAY at DigiKey Marketplace
  + TME; LCSC code existence for BOM (no code -> hand-fit, stated).
- E2: Module facts from Raytac primary docs: footprint/pin table,
  antenna keep-out rules, DCDC inductor provision, 32.768kHz
  crystal provision, required externals, reference design followed.

## Additional PO requirement (2026-11-19): SWD debug provision
- PO owns nRF52840 DK (PCA10056); its onboard J-Link drives an
  external board's SWD via Debug Out (P19/P20).
- Add pads-only SWD footprint (TC2030-class 6-pin or 2x5 1.27mm
  pad array; choice justified) wired SWDIO/SWCLK/RESET/GND/
  VDD-sense; placed for pogo access with case open, clear of the
  trackpad keep-out and battery pod zone; in schematic, board,
  assignment + keep-out audits.
- USB-C re-run with SWD as service lifeline: USB-C = bench power
  + no-open-case FW updates (convenience). If the tab relaxes,
  take the smaller outline and report the delta; else one line why.
- REPORT.md notes DK Debug Out (P19/P20) as assumed programmer;
  pad pinout follows standard SWD ordering.

## Implementation (tree hardware/kicad/qualification/issue-292-wmain/)
- Rev.10 outline + ONE change: minimal north tab derived from
  module footprint + keep-out + USB-C placement (tab may host
  USB-C; arrangement that keeps tab smallest wins).
- Module antenna end toward south PETG zone if tab geometry
  allows; else best placement + explicit antenna report.
- TPS63070 @3.3V (forced PWM off, AP2112K deleted); J2/J3 FH12
  3.3V assignment (pin1 HALL_3V3 via TPS22919, per-bank EN, ADC
  returns); trackpad I2C+DR+switched supply to bay disconnect;
  battery input + gated divider sense; dia.40 keep-out enforced.
- Case fitted check vs case production tree; shell north-edge
  impact stated with size; case tree NOT edited.

## Gates (all numbers): ERC 0; DRC severity-all; unconnected;
via-pad audit (0.10 floor / 0.125 target, sub-target listed);
keep-out audit from placed data (trackpad dia.40, module antenna,
south band, SWD zone); Wing-link assignment census (2x14 pins,
from board data); far-Wing rail budget from routed board
(<=50mV class @ burst peak); outline delta (tab dims + area,
holes unchanged verified from data).

## Package: manufacturing/ per #267 (BOM verified codes or
hand-fit marks, CPL gerber frame, FABRICATION.md, quote-handoff
DRAFT/NOT FOR ORDER) + REPORT.md (gates, antenna, shell impact,
SWD note, deviations, draft adoption line D-056).
# Stage 2a (PO 2026-11-19): LAYOUT STOPPED. Module basis REOPENED.
# D-055's Raytac choice was a fallback under old constraints; tab +
# daughterboard-USB + DK-SWD relaxed them. New deliverable:
# .issue292-runtime/module-selection.md + .json (survey commit,
# then shortlist commit). No layout until the study reports.
# MDBT50Q footprint data already extracted (sources/) stays as
# candidate evidence, not as a design basis.
# Issue #292 Stage 2 LAYOUT (D-056 basis) — plan addendum 2026-11-19

Module = Insight SiP ISP1807-LR (D-056). North tab DROPPED:
outline + symmetric holes = Rev.10 EXACTLY (zero delta is a gate).

## Verified procurement fact (PMO, live 2026-11-19)
ISP1807-LR-RS = LCSC C5264268: JLCPCB stock 0 / LCSC stock 0, but
registered as JLCPCB **Pre-order Part** (Extended), est. $11.78,
est. lead 28 days. BOM line = PCBA via Pre-order Parts; alternatives
noted (DigiKey + consigned parts; hand-fit + SWD/continuity
bring-up). Never claim shelf stock; never plain hand-fit.

## Build method (repo precedent: scripted pcbnew, KiCad 9.0.9
## extracted runtime at he-piantor-42/.issue129-runtime/kicad/usr)
1. Extract donor data from Rev.10 board (outline, holes, J2/J3
   FH12 footprints + pad-net assignment, power-stage footprints).
   Extract ISP1807 footprint from sources/jrwatch.kicad_pcb;
   cross-check pad table vs Insight SiP datasheet pin table.
2. Netlist as data (parts/pins/nets) -> generate native schematic
   (.kicad_sch + project .kicad_sym), ERC via kicad-cli.
3. Board: Rev.10 outline/holes/J2/J3 carried; fresh placement
   outside the dia.40 keep-out; module in SW pocket, antenna end
   south, antenna keep-out (no copper all layers) in the south
   strip; TPS63070 re-set 3.3V; TPS22919 -> HALL_3V3; trackpad
   switch -> PAD_3V3; diode-OR VBUS (no pack back-feed); gated
   1M/1M VBAT divider -> AIN; SWD pads (TC2030-class 6-pin);
   trackpad conn (I2C+DR+PAD_3V3/GND) in north sliver.
4. USB comparison (i) mini-tab bare / (ii) EZmate daughterboard
   (stocked Fly servability from recorded spec) / (iii) bare on
   existing outline -> pick by cost/rework/freedom; any tab is
   THE flagged deviation in REPORT.md.
5. Route (DSN/Freerouting or KRT per availability), DRC, audits
   from placed data: via-pad, keep-outs, Wing-link census 2x14,
   far-Wing budget from routed copper, outline delta = 0 check.
6. Case fitted check vs issue-263-lowdeck-production tree.
7. Package: manufacturing/ (BOM with C5264268 Pre-order line,
   CPL gerber frame, FABRICATION.md, quote-handoff DRAFT) +
   REPORT.md (gates, USB pick, antenna, shell, deviations,
   draft adoption line D-057).

## Stage 2 layout — COMPLETE (2026-11-19)
Final board: wmain-v27 lineage -> tree wmain.kicad_pcb. Gates: ERC 0;
DRC unconnected 3 (module GND pads only, dispositioned); shorts 0;
via-pad min 0.100; antenna strip 0 items; census 14/14 x2;
outline delta 0 (undirected segment equality). USB pick (ii)
EZmate daughterboard (stocked Fly serves), outline delta 0.
Deviations 1-8 in REPORT.md (lead: derived ISP1807 footprint ->
D-057 condition). Package: manufacturing/ DRAFT / NOT FOR ORDER
(module line C5264268 Pre-order Parts, +~28d, est. $11.78).
Key incidents: FH12 clone pad-rotation defect found by bbox audit
and fixed (43->0 local); GND band went F-band -> B-via design;
A-net escapes completed after band redesign; U4.2 = via-in-pad.

## Stage 2 FIX ROUND — discharge D-057 condition (deviation 1)
1. Obtain Insight SiP OFFICIAL CAD for ISP1807-LR (maker site /
   official library / DigiKey-linked ECAD only). Record source,
   version/date, SHA-256 of the downloaded file.
2. Script-diff official vs derived footprint pad-by-pad
   (number/position/size) -> full table in runtime notes.
3. Swap footprint into wmain.kicad_pcb (incl. south NC pads
   70-78 as maker specifies, if present in official CAD);
   repair routing only where the swap disturbs it.
4. Re-run FULL gate set: ERC, DRC severity-all, unconnected,
   via-pad audit, antenna + trackpad keep-outs, Wing census,
   far-Wing budget, outline delta = 0. Re-verify module
   pad-net assignment vs selection-study pin table from
   board data after the swap.
5. Regenerate manufacturing package if gerber/CPL change;
   note in quote-handoff.md. Update REPORT.md: deviation 1
   -> DISCHARGED with diff summary; board SHA updated.
   STOP condition: official CAD unobtainable from an
   authorized source -> report attempts, keep derived fp
   explicitly UNVERIFIED.
Other 7 deviations untouched.

## Fix round outcome (2026-11-19) — STOPPED at PO decision point

- Official CAD obtained + triangulated (PROVENANCE.md); pad diff:
  same 0 / moved 69 / resized 8 / added 9 (NC 70-78). Library
  footprint replaced and reload-verified. Board swap done on
  wmain-v28-fp.kicad_pcb (SHA b7629fe9...): centre kept, orient
  90->0, pad-net assignment preserved exactly (verify_padnet.py;
  datasheet 3-way function binding in PROVENANCE.md, incl. the
  design.py ISP_PINS +2 transcription error - schematic/board
  were always correct).
- Re-route under 0.10/0.10 project rules is geometrically
  impossible for the 12 interior pads (0.25mm streets < 0.30mm
  needed). Evidence: KRT x3 configs fail identically; exact
  A* sensitivity: 0.10/0.10 -> interior 0/12; 0.075 -> 5-8/12
  (order-dependent); 0.05w/0.10c -> 7/12; 0.05/0.05 -> 12/12
  (escapes_005.json). Maker TB fans out at ~0.05mm field
  clearances (measured from its GTL).
- REPORT.md deviation 1 updated (footprint DISCHARGED, D-057
  condition stays open) + new deviation 9 (fanout rule wall,
  options a/b/c). quote-handoff.md flagged. Tree board and
  manufacturing package unchanged (not regenerated).
- PO PNGs from the swapped working board:
  goals/he-piantor-42-keyboard-pmo/files/wmain-2d-topview.png,
  wmain-2d-zoom-module.png, wmain-2d-zoom-service.png
  (module field labelled unrouted / PO decision pending).
- Not done (gated on the deviation-9 decision): tier-2 routing,
  GND taps (gnd_taps.py written, unrun), full gate re-run,
  package regeneration.

## Re-route round plan (2026-11-19, D-057 granted)

Basis: D-057 (decisions.md) - rule exception ONLY inside the ISP1807-LR
fanout field (footprint + minimal escape zone, explicit rule area);
0.05mm class is the ceiling, use the minimum exception that routes;
D-019 (0.10/0.10) unchanged elsewhere; all gates re-run on the
finished tree board; adoption draft renumbered D-058.

Stages:
- S0 baseline: reproduce the unrouted state of the swapped working
  board (wmain-v28-fp.kicad_pcb, SHA b7629fe9...) - DRC/unconnected
  counts recorded BEFORE any edit (verification invariant 1).
- S1 tree-board footprint swap: U1 footprint in the tree board ->
  verified library footprint wmain.pretty/ISP1807-LR.kicad_mod;
  pad-number->net assignment script-verified against the working
  copy (only delta = 9 added NC pads 70-78, no net).
- S2 rule area: explicit KiCad rule area = module footprint +
  minimal escape zone derived from escapes_005.json geometry;
  report boundary dimensions/area. Inside: 0.05-class netclass/rules;
  outside: D-019 enforced.
- S3 route module field: 12 interior pads first (escapes_005.json
  paths as the proven-feasible seed), then remaining module nets +
  anything the swap disturbed; largest clearance per segment;
  record measured minima (w/w, w-pad, pad-pad) inside the field.
  GND pads 7/14/18: retry taps in the new geometry; disposition
  stated either way.
- S4 gates on the finished TREE board: ERC; DRC severity-all with
  rule area active + exception-dependence list (every clearance
  that only passes because of the exception); unconnected;
  via-pad audit; antenna + trackpad keep-outs; Wing census 14/14x2
  from board data; far-Wing budget; outline delta = 0 re-verified.
- S5 REPORT.md: deviation 1 DISCHARGED, deviation 9 RESOLVED by
  D-057 (exception minima + rule-area size), 2-8 restated as they
  stand, adoption draft -> D-058, board SHA updated.
- S6 manufacturing package regenerated from the finished board;
  quote-handoff flags the 0.05mm-class field explicitly.
- S7 PO 2D drawings regenerated from the finished board (3 PNGs in
  goals files/); zoom-module inset draws the rule-area boundary
  as a labelled outline.

Checkpoint-commit per stage. Never /tmp.
