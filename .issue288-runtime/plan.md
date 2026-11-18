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
