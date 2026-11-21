# Issue #299 Stage 1 — Wireless Wing design study plan

Worktree: ~/workspace/projects/he-piantor-wwing, branch issue-299-wwing (from origin/main d3c834d46).
Deliverables: .issue299-runtime/wwing-design.md + wwing-design.json, committed + pushed; summary comment on Issue #299.

## Inputs (from Issue #299)
- D-049: TMAG5253BA3 (X2SON), 3.3V Hall rail, EN per MUX bank, divider removed.
- D-024 link: pin1 = HALL_3V3; common address / common 3 ADC / independent EN per side (Main J2 pin7 = EN0, J3 pin7 = EN1).
- D-058 Main: HALL_3V3 via TPS22919; far-point budget <=50mV class (Main layout <=39mV).
- Wing Rev.6 geometry inherited EXACTLY (field deviation target 0.0000mm); outline/notches/mounting/flip (D-046/D-051) preserved.
- D-042 FH12-14S-0.5SH(55) + stock FFC. D-021 routing: 2L, signals 0.10 / power 0.30. Via-pad floor 0.10, target 0.125.
- Reference implementation: #288 wireless Matrix tree.

## Steps
1. Explore #288 tree (hardware/kicad/qualification/issue-288-wmatrix/): schematic + REPORT.md — extract TMAG channel circuit, TMUX1208 bank wiring, EN-per-bank, decoupling/rail practice. File-level citations.
2. Explore Wing Rev.6 tree (hardware/kicad/qualification/issue-270-wing-rev6/): per-variant sensor census, existing MUX scheme (DRV5055 era), bank structure, connector pinout, field geometry source.
3. Explore #292 tree (issue-292-wmain) for TPS22919 HALL_3V3 feed characteristics + FFC lane resistance figures used in prior budgets; #284/D-050 power model assumptions for the sensor term (16.2d basis).
4. Sensor swap study: DRV5055 SOT-23 -> TMAG5253BA3 X2SON. TI datasheet (primary) for package/land; JLCPCB X2SON assembly practice; pin-map translation; output/reference implications (DRV5055 ratiometric vs TMAG5253 fixed sensitivity / VCC-dependence) for Main ADC reference; keep-out/height delta in switch footprint.
5. Rail budget at 3.3V: recompute worst-case far-sensor voltage from tree resistance figures (FFC lane, connector, Main-side drop) and per-variant current census; compare sensor current vs D-050 model; flag runtime deltas.
6. Variant plan: 16L/16R/17L/17R shared vs per-variant; flip preservation check (Wing-side consequences of Main EN0/EN1 swap).
7. Availability scan: TMAG5253BA3 C22401868, TMUX1208PWR (find LCSC code from #288 BOM), FH12 C5378715 — JLCPCB/LCSC stock with dates/sources; need = 4 variants x 5 boards; flag <10x.
8. Risk register for Stage 2 incl. D-049 gate (Matrix yield -> land pattern) and sequencing to minimise rework.
9. Write wwing-design.md + .json; commit, push; comment summary on #299.

## Invariants
- Every reuse claim cites a file in the #288/#270/#292 trees.
- Rail budget recomputed from tree figures, not memory.
- Missing datum -> primary datasheet, cited.
