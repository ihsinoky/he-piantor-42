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
