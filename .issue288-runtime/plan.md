# Issue #288 Stage 1 plan — wireless Matrix evaluation board design study

STUDY ONLY. No KiCad implementation in this stage.

## Sources to ground in (read before writing)
- docs/decisions.md (this branch: D-001..D-047; D-024 dual-Wing scheme, D-026/D-027 power)
- Issue #288 body (D-048/049/050/052 summaries)
- Matrix Rev.4 REPORT.md — in worktree ~/workspace/projects/he-piantor-matrix4 (PR #272 branch, not this branch)
- Issue #282 comparison — ~/workspace/projects/he-piantor-tmag/.issue282-runtime/tmag-comparison.md (PR #283 branch)
- Matrix Rev.3 tree: hardware/kicad/qualification/issue-182-matrix-rev3/
- Wing Rev.6 trees: hardware/kicad/qualification/issue-270-wing-rev6/ (16/17mm, L/R)

## Sections of wmatrix-design.md (checkpoint-commit after each)
1. Role & carried-over facts (what the eval board must represent; per-figure source cites)
2. Sensor-field layout (Q1): sensor/switch count & arrangement; travel+noise with real Jade Pro/Junana stack; crosstalk for 16 vs 17mm pitch; one board both pitches? cost in size/parts
3. MCU form comparison: XIAO nRF52840 (verify JP radio cert as check item) vs RayTac MDBT50Q-class vs bare-module carrier; socketed/carrier option
4. Power feed: exercise D-049 regime (3.3V rail, per-bank EN bursts, nRF ADC); USB bench vs NiMH+boost lineage
5. MUX: TMUX1208 vs CD74HC4067 for this channel count; recommendation
6. Measurement access (Q2): test points/headers/signals for raw ADC per sensor, EN timing, rail droop under burst
7. Assembly (Q3): D-049 condition-(2) X2SON yield vehicle; PCBA scope; footprint/process notes
8. Firmware scope outline (Q4): scan + log via USB/BLE; no code
9. Availability scan (Q5): exact SKUs, stock+lifecycle observed 2026-11-19, 2+ distributors, thin-stock flags
10. Recommendation + rejected alternatives; Stage 2 outline + gate list (DRC/ERC/via-pad/assignment)

## Deliverables
- .issue288-runtime/wmatrix-design.md + .json

---
# Issue #288 Stage 2 plan — KiCad implementation (appended 2026-11-19)

New tree: `hardware/kicad/qualification/issue-288-wmatrix/` (board/ + manufacturing/ + REPORT.md).
Donor: Rev.3 board file (field routing + MUX placement preserved by in-place edit).

## Frozen design table (from study; pin map frozen here, gate §10.4)
- Field: 18x TMAG5253BA3, Rev.3 coordinates exact; sensor->MUX-input assignment
  preserved from Rev.3 (extracted from donor pads, not retyped).
- MUX out A/B/C -> XIAO D0 (AIN0) / D1 (AIN1) / D2 (AIN4).
- XIAO pin map: D0=MUXA_OUT, D1=MUXB_OUT, D2=MUXC_OUT (AIN); D6/D7/D8=A0/A1/A2;
  D9/D10/D3=EN_A/EN_B/EN_C; D5=status LED; D4=spare. 10 of 11 header GPIO used.
- Spare MUX inputs per group: S7->GND (offset ref), S8->sensor rail via divider
  (10k/10k from HALL_3V3, node = rail/2) (rail ref).
- Power: VIN node <- board USB-C (CC 5.1k x2) OR battery 2-pin header via
  AO3401 P-MOS reverse-polarity protection. VIN -> AP2112K-3.3 LDO (600 mA)
  -> HALL_3V3 sensor rail (sensors + MUX VDD). Shunt position (0-ohm jumper
  footprint + sense pads) in HALL_3V3 after the LDO.
- TPs: raw per-pitch CTR/N/DIAG (from Rev.3 pattern), TP_MUXA/B/C, TP_A0/A1/A2,
  TP_EN_A/B/C, TP rail at LDO out + far end of each section, TP_VIN, TP_GND.
- Board: Rev.3 outline 128x80, 2L, 1.2 mm, 0.10/0.30 mm widths, 0.10 clearance;
  south strip (ex-GH zone) hosts XIAO socket (antenna end at board edge,
  copper keep-out), USB-C, LDO, battery header.

## Steps
- S2.0 plan + toolchain env (KiCad 9.0.9 runtime from main clone .issue129-runtime)
- S2.1 fact extraction: donor inventory (pads/nets/outline/netclasses);
  TMAG pinout + DMR land pattern (tmag worktree sources / TI SBASAI5);
  XIAO pinout (PO he_kbd_module lib / Seeed); TMUX1208 pad map (donor board);
  LCSC codes (Rev.3 BOM + LCSC pages for new parts)
- S2.2 footprints: TMAG X2SON-4 DMR (cited), XIAO socket; project .pretty lib
- S2.3 native schematic (.kicad_sch generated; project symbol lib) -> ERC 0;
  schematic<->PCB pad/net consistency diff = assignment verification
- S2.4 PCB build: donor in-place edit via pcbnew (sensor swap, rail rename,
  readout-end replacement, south-strip routing); DRC iterate to 0/0
- S2.5 gates: DRC severity-all, ERC, via-pad audit (donor method), field
  deviation table (from placed data), assignment table (from placed pads),
  rail droop extraction (graph model, 1 oz, worst path @ 90 mA)
- S2.6 package per #267 conventions + TMAG stock re-observation at package time
- S2.7 REPORT.md (gates with numbers, deviations, draft adoption line)
