# Issue #288 Stage 1 — Wireless Matrix evaluation board: design study

STUDY ONLY. No KiCad implementation in this stage. Every carried-over
number cites its source file. Prices/stock in §9 observed 2026-11-19
(crawl dates noted where the page was not fetched live).

## 1. Role and carried-over facts

This board succeeds the Matrix Rev.4 evaluation role
(`hardware/kicad/qualification/issue-268-matrix-rev4/REPORT.md`, read in
its worktree) for the wireless variant. It is the vehicle for both
D-049 conditions: (1) measured travel curve + noise of the
TMAG5253BA3 chain with the real magnet/switch stack, and (2) X2SON
assembly yield at JLCPCB. It also serves the open MS4 pitch decision
(16 vs 17 mm). Design inputs: D-048 (NiMH AA x4 product power),
D-049 (TMAG5253BA3, 3.3 V rail, per-bank EN, no divider), D-050
(nRF single-chip), D-052 (nRF52840 module class).

Facts carried in, with sources:

- Sensor field of the incumbent Matrix (measured from
  `hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb`
  in this repo): **18 Hall sensors in two 3x3 sections** — west section
  at **16 mm pitch** (x = 50/66/82, y = 74/90/106), east section at
  **17 mm pitch** (x = 117/134/151, y = 73/90/107); 3 MUX
  (TMUX1208PWR, LCSC C494728) x 6 sensors; per-pitch raw test points
  TP_H16_CTR/N/DIAG_RAW and TP_H17_CTR/N/DIAG_RAW; link test points
  TP_W_A0/A1/A2, TP_W_EN, TP_W_MUXA/B/C, TP_W_H5V, TP_W_GND_x.
  Rev.4 changed only the link connector (REPORT.md: footprint census
  65 = 65, "sensor field and all measurement features untouched").
- Wing field (measured from
  `hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb`):
  21 sensors as 3 MUX groups x 7 (U_HA0-6, U_HB0-6, U_HC0-6) — the same
  3-ADC-channel x 8:1 MUX architecture the Matrix samples at 6/group.
- Jade Pro field at the sensor, 1.2 mm PCB: **12 +/-0.8 mT (top) ->
  70 +/-3 mT (bottom)**, travel 3.5 +/-0.1 mm
  (`docs/hall-acquisition.md` via the Issue #282 comparison,
  `tmag-comparison.md` §Basis/§2 in the issue-282 worktree). PCB
  thickness stays 1.2 mm (decisions.md: the Jade Pro flux data is
  published at 1.2 mm; evaluation and production geometry stay equal).
- TMAG5253BA3 (TI SBASAI5E, via #282 §1): VCC 1.65-3.6 V; ICC 2.6 typ /
  5 max mA @3.3 V; shutdown 8 nA typ (EN pin 3); tON 20 typ / 45 max us;
  output over the Jade Pro field **1.83 -> 2.70 V (span 0.87 V)** at
  3.3 V, no divider; noise-equivalent travel **10.3 um pp / 1.6 um RMS**
  (modelled); X2SON-4 (DMR) 1.40 x 1.10 mm + thermal pad.
- D-049 power regime (#282 §3d/§4): per-bank EN planning burst window
  **0.35 ms class** (per-bank 370 us = 2 x tON 45 us + 14 steps x
  20 us); successor rail metric = **far-point drop <= 50 mV** at design
  load (ratiometric-error budget), replacing the 4.60 V floor.
- TMUX1208 @3.3 V (#282 §3b): RON 9 ohm typ; with the divider deleted
  the ADC-node tau falls to ~10 ns, so per-step settling stops being
  the scan-rate term — on the RP2040 model. The nRF52840 SAADC step
  timing is NOT modelled anywhere yet; measuring it is one of this
  board's jobs (§6, §8).

## 2. Sensor-field layout (Q1)

**Keep the Rev.3 field geometry exactly.** Same 18 sites, same
coordinates (§1), same 3 MUX groups (columns A/B/C), 6 sensors per
MUX. Changes are confined to the sensor part (DRV5055A3 SOT-23 ->
TMAG5253BA3 X2SON-4), the rail (5 V -> 3.3 V), EN wiring (§5), and
the readout end (Wing-link connector -> on-board MCU, §3).

Why this layout answers the questions:

- **(a) Travel curve + noise:** each 3x3 section's centre sensor sits
  in the full neighbour environment of the product field, so its
  travel curve (real Jade Pro switch + Junana cap stack above the
  board, actuated through the 3.5 mm travel) is the product-relevant
  curve, not an isolated-sensor curve. Corner and edge sensors give
  the environment-asymmetry spread. Per-key endpoint calibration is
  the product's method (hall-acquisition §6, via #282 §2), so the
  +/-15% sensitivity spread is measured, not feared.
- **(b) Crosstalk / pitch:** a 3x3 section is exactly the support of
  the firmware's joint-estimation coupling matrix (C sparse, <= 8
  neighbours). Actuating the centre key while logging all 9 channels
  of the section yields one full row of C per pitch, same board, same
  session, same sensor batch — the 16 vs 17 mm comparison carries no
  unit-to-unit or session confound. The opposite section's centre
  channel, logged simultaneously, is the far-field control.
- **One board covers both pitches** — it already does (Rev.3/Rev.4).
  Cost of the second section vs a single-pitch board: +9 sensors
  (~$0.63 ea at LCSC 1+ pricing, §9) + 9 decoupling caps + ~35 mm of
  board width (field span x 50 -> 151 mm). The alternative — two
  single-pitch boards — doubles fabrication and assembly minimums
  and reintroduces the session confound. Rejected.
- **Not a full 21-key Wing field:** the open questions are per-site
  physics (curve, noise, coupling, yield), not full-Wing scan
  behaviour; 18 sites at 6/MUX also leaves 2 spare MUX inputs per
  group, which §6 turns into per-sweep self-calibration channels.
  A full-field check belongs to the wireless Wing respin, which this
  board de-risks. Rejected for this stage.
