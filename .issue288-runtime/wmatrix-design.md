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

## 3. MCU form (Q-supplement: D-052 module class)

The MCU is not the thing under test — the sensor chain is — so the
form is chosen for iteration speed and zero RF risk, while keeping
the silicon (nRF52840) and the SAADC behaviour identical to the
product path.

| Form | Radio cert (JP) | Flash/debug | Sourcing | Verdict |
|---|---|---|---|---|
| **Seeed XIAO nRF52840, socketed** on 2x7 2.54 mm headers | Seeed publishes a TELEC certificate in the XIAO cert bundle; the retrievable construction-type certificate (No. 222-257139, issued 2025-04-25) names the **Plus** models — see check item below | UF2 bootloader + USB-C fitted; no debugger needed | DigiKey JP 2,025 in stock @ JPY 1,711 (crawl 2026-11-18); Seeed store $9.99 | **RECOMMENDED** |
| RayTac MDBT50Q-1MV2, soldered | **Telec (MIC) pre-certified** — confirmed (DigiKey product page; Zephyr board docs) | SWD only (no USB bootloader unless pre-flashed); needs a debugger probe | DigiKey Marketplace only: 35 pcs @ $6.15 + $25 ship, ~14 days; LCSC C5118826 listed, zero stock | Product path (variant Main), not this board |
| MDBT50Q on a custom carrier, socketed | as above | as above | module channel as above + a second PCB project first | Rejected: spends a board spin before the first measurement |

XIAO rationale: PO already holds footprint assets for it (their
he_kbd_module project); it is hand-replaceable if a wiring mistake
kills it, reusable across respins, and its USB-C/UF2 flow makes
firmware iteration a cable swap. GPIO budget (to be frozen in
Stage 2): 3 AIN (MUX outputs) + 3 address + 3 EN + 1 status LED = 10
GPIO, inside the XIAO's 11 header GPIO with its 6 AIN-capable pads —
feasible but tight; the Stage 2 pin map is a named gate (§10).
Antenna: the XIAO's on-board chip antenna needs the carrier keep-out
observed (Stage 2 layout note); BLE on this board is a logging
convenience (§8), not a measurement path.

**Check item (not assumed, per brief):** the base XIAO nRF52840's own
Japan construction-type certificate number was not directly
retrieved in this study — Seeed's bundle claims TELEC for the family
and the retrievable certificate names the Plus variants. This does
not block a bench evaluation board using the module as bought; it
MUST be pinned before any product relies on the XIAO form. The
MDBT50Q-1MV2's Telec status, by contrast, is confirmed above and is
one reason it stays the recorded product-path module class (D-052).

Rejected: bare nRF52840 chip on this board — RF layout + own
certification is exactly the risk an evaluation board must not take
on; RP2040 (PO's earlier he_kbd_es used one) — D-050/D-052 foreclose
it, and the eval must characterise the product's SAADC, not the
RP2040 ADC the #282 model used.

## 4. Power feed

The D-049 regime's electrically relevant features are: a 3.3 V rail,
per-bank EN bursts with real tON, and droop under burst load. The
feed design reproduces those three; converter ripple/efficiency of
the product's buck-boost lineage is a variant-Main question, not a
sensor-chain question (boundary recorded deliberately).

- **Primary: USB 5 V bench feed** into a dedicated **sensor-rail
  3.3 V regulator** (500 mA class LDO or buck; worst-case Hall draw =
  18 sensors x 5 mA max = 90 mA with all banks on in continuous mode,
  plus MUX/logic — 500 mA class gives >5x headroom). The sensor rail
  is NOT the XIAO's 3.3 V output: coupling MCU rail noise into the
  rail whose noise floor is the measurement would corrupt D-049
  condition (1).
- **Battery option on the same input node:** a 2-pin header (with
  reverse-polarity protection) accepting the D-048 pack directly —
  4x AA NiMH = 4.8 V nominal, ~4.0-5.8 V over discharge/charge —
  feeding the same 5 V-class input node and the same regulator, so
  burst behaviour can be re-checked on the real source impedance
  without a second power tree. No on-board charging (D-048: external
  charging only).
- **Ratiometric observability:** the nRF ADC references the XIAO's
  VDD while sensors sit on the sensor rail; per #282 §3a the delta
  appears as scale error. The design therefore routes one spare MUX
  input to the sensor rail through a fixed divider (§6), so every
  sweep logs the rail as the ADC sees it and the mismatch is data,
  not an unknown.
- Rail budget gate for Stage 2: sensor-rail droop <= 50 mV at worst
  burst load (the #282 successor metric), verified by extraction
  before fabrication release (§10).

## 5. MUX choice

**TMUX1208PWR x3 (LCSC C494728) — the incumbent Wing/Matrix part.**
One 8:1 per ADC channel, common address A0-A2: at each address step
the three channels present three sensors simultaneously, which is
the product's scan shape (Wing: 3 groups x 7; here 3 x 6). At 3.3 V:
RON 9 ohm typ (#282 §3b) into the SAADC — settling stays a non-term.

**CD74HC4067 (PO's earlier eval board part) — rejected for this
board.** It is a single 16:1 (CD74HC4067M96, LCSC C496123): 18
sensors need two of them and the readout collapses to one ADC
channel scanned sequentially — a different timing regime from the
product, so burst-window and settling measurements would not
transfer. Its RON is 70 ohm typ @4.5 V (TI SCHS209D), higher again
at 3.3 V, in series with the SAADC sampling network — a
channel-dependent settling error inside the noise measurement the
board exists to make. Its genuine merits (one part covers 16
channels; PO has used it) do not offset measuring the wrong regime.

**EN wiring:** EN is routed **per MUX group** (3 nets, EN_A/B/C),
each group's 6 sensor EN pins tied to their MUX's net. Firmware can
then emulate every candidate regime on one board: ganged (all EN
on), per-bank (one group at a time — finer than the product's
per-Wing split, strictly more informative), and the #282 planning
cases in between. Cost vs a single ganged net: 2 extra GPIO (§3
budget already carries 3 EN lines).

## 6. Measurement access (Q2)

Retained from the Rev.3 pattern (it was designed for exactly this):
per-pitch raw outputs **TP_H16_CTR/N/DIAG_RAW, TP_H17_CTR/N/DIAG_RAW**
(pre-MUX sensor OUT), MUX outputs **TP_MUXA/B/C** (post-MUX, pre-ADC),
address **TP_A0/A1/A2**. New for the D-049 regime:

- **TP_EN_A/B/C** — a scope triggers on the EN rising edge and reads
  OUT settling on the raw TPs: tON verified against the 45 us max
  (SBASAI5E) in the real stack, not the model.
- **Rail access:** TP at the regulator output and one at the far end
  of each section's rail run; a series shunt position (0-ohm jumper
  footprint / sense pads) in the sensor rail for droop-under-burst
  measurement with a meter or differential scope probe.
- **Self-calibration channels:** each MUX has 2 spare inputs (6 of 8
  used). Wire input 6 -> GND (offset reference) and input 7 -> the
  sensor rail via a fixed divider (rail/ratiometric reference, §4).
  Every logged sweep then carries its own offset + rail references;
  ADC drift cannot masquerade as sensor noise.
- **Firmware-visible signals:** all 18 raw ADC codes per sweep; the
  6 reference-channel codes per sweep; EN-assert -> ADC-complete
  timer counts per bank (the real burst window on nRF silicon);
  sweep-period jitter statistics in burst modes.
- SWD: the XIAO's UF2 flow is primary. Exposing the XIAO's underside
  SWD pads via pogo lands is a Stage 2 option, not a gate.

## 7. Assembly (Q3) — the D-049 condition-(2) vehicle

- **Full PCBA at JLCPCB for everything except the XIAO**: sensors,
  MUXes, regulator, passives, connectors — placed in one run under
  the production-intent process (the yield question is only answered
  by the process a Wing respin would actually use). The XIAO is
  hand-socketed afterwards; it is a bought module on headers and is
  not a JLCPCB SMT line item in any case.
- **X2SON specifics:** TMAG5253BA3IQDMRR is JLCPCB **Extended** class
  (#282 §5). Footprint = TI DMR land pattern (SBASAI5 package data:
  1.40 x 1.10 mm body + thermal pad) — Stage 2 cites the drawing it
  builds from (§10 gate). No-lead 1.4 mm-class parts are the known
  yield risk (paste volume / tombstone-free but inspection-blind
  joints); that risk is the measurement, so no hand-solder fallback
  is designed in.
- **Yield metric, defined now:** after assembly, the firmware
  self-test (EN on -> OUT inside the VQ band, per sensor) counts
  functional sensors. Yield = functional / 18 per board. At the
  project's standard 5-board quantity that is 90 sensor sites — a
  first yield read, not a production statistic; the Stage 2 report
  must present it as such.
- **Variant trap (from #282 §5):** the BA1 sibling (LCSC C22445458,
  +/-20 mT) is stocked and adjacent; a variant slip saturates in the
  Jade Pro field and is a hard failure, not a degradation. The BOM
  pins **TMAG5253BA3IQDMRR** exactly, and the travel-curve self-test
  detects a slip functionally (BA1 clips at 20 mT) — record both
  defences in the Stage 2 package.

## 8. Firmware scope (Q4) — outline only, no code

Platform: nRF52840 on the XIAO (NCS/Zephyr-class stack, so the scan
engine ports to the D-052 product module without behavioural
change). Scope:

- **Scan engine:** address sequencing A0-A2; per-group EN control
  (ganged / per-bank / held-static regimes); SAADC burst sampling
  with configurable acquisition time per step (the nRF step-timing
  characterisation #282 could not model); per-bank EN->complete
  timing counters.
- **Modes:** (i) continuous scan — travel-curve capture under a
  pressed key; (ii) burst T=10 ms and T=100 ms — the D-049 desk/away
  regimes, with measured (not modelled) window and jitter; (iii)
  single-sensor held mode — one address + EN held for scope work
  against §6 test points; (iv) assembly self-test — per-sensor VQ
  band check feeding the §7 yield count.
- **Data out:** USB CDC stream of per-sweep records (sweep index,
  18 raw codes, 6 reference codes, rail-reference code, timing
  counters) in a line-oriented CSV/JSONL form any serial logger can
  capture; BLE NUS mirror as a convenience only. **No estimator in
  firmware** — joint estimation / coupling-matrix fitting runs
  host-side on the logged raw data, where it can be re-run as the
  method evolves.
- Out of scope: Unifying/ESB transmission (Issue #287's bench
  proof owns the protocol risk), keymap/HID behaviour, sleep-state
  product firmware.

## 9. Availability scan (Q5) — observed 2026-11-19

| Part | SKU | Channel | Stock (observed) | Price | Lifecycle | Flag |
|---|---|---|---|---|---|---|
| TMAG5253BA3IQDMRR | LCSC **C22401868** | LCSC | **1,126** (page fetched 2026-11-19) | $0.628 (1+) / $0.5421 (10+) | TI ACTIVE (SBASAI5) | **WATCH**: 6,314 observed 2026-11-18 (#282 §5) -> 1,126 today. Still >=20x the <=54 pcs a 5-board run needs, but re-observe at Stage 2 before BOM commit |
| TMAG5253BA3IQDMRR | Mouser 595-MAG5253BA3IQDMRR | Mouser | ~3,805 (crawl ~86 days old — stale) | $0.80 (1) | ACTIVE | Second source exists; figure stale, re-check if needed |
| TMUX1208PWR | LCSC **C494728** | LCSC / DigiKey | InStock (LCSC offer data); DigiKey ~110,000 (recent crawls) | $0.2792 (LCSC 1+) | TI Active | none |
| CD74HC4067M96 (rejected alt) | LCSC **C496123** | LCSC | 5,043 (crawl 2 days old) | $0.4021 (1+) | TI Active (SCHS209D rev. 2024) | n/a — not selected (§5) |
| Seeed XIAO nRF52840 | DigiKey listing "XIAO NRF52840" (Seeed) | DigiKey JP / Seeed store | **2,025** @ DigiKey JP (crawl 2026-11-18); Seeed store in stock | JPY 1,711 (DigiKey JP 1+); $9.99 (Seeed) | Active | none |
| RayTac MDBT50Q-1MV2 (product path, not this board) | LCSC C5118826 / DigiKey Marketplace 3271-MDBT50Q-1MV2 | DigiKey Marketplace | **35** (crawl 1 day old), ships ~14 days + $25 fee; LCSC listed at **zero stock** (third-party report, 2026-07) | $6.15 (1+) | Active; Telec pre-cert (§3) | **THIN**: no mainstream first-party channel observed; a variant-Main sourcing question to solve at that design stage, recorded now |

Variant trap restated: TMAG5253**BA1**IQDMRR (LCSC C22445458,
6,654 in stock, 6-day-old crawl) sits adjacent to the BA3 — the
orderable must be pinned character-exact (§7).

## 10. Recommendation, rejected alternatives, Stage 2 outline

**Recommended architecture (one paragraph):** Rev.3's 18-site,
two-pitch-section field carried over unchanged (16 mm west / 17 mm
east, 3x3 each), re-sensored with TMAG5253BA3 on a dedicated 3.3 V
sensor rail, TMUX1208PWR x3 with EN wired per MUX group, read by a
socketed Seeed XIAO nRF52840; USB bench feed primary with the D-048
NiMH pack accepted on the same input node; full JLCPCB PCBA (XIAO
excepted) so the run doubles as the X2SON yield vehicle; Rev.3's
measurement-access pattern retained and extended with EN/rail test
points and per-MUX GND + rail-reference spare channels.

Rejected alternatives, with reasons: two single-pitch boards
(§2 — cost + session confound); full 21-key Wing field (§2 — not
the open question); CD74HC4067 (§5 — wrong scan regime, RON);
soldered MDBT50Q-1MV2 (§3 — thin channel, SWD-only, spends effort
on the non-tested part); custom module carrier (§3 — a board spin
before the first measurement); bare nRF52840 (§3 — RF/cert risk);
battery-only feed (§4 — bench ergonomics; pack accepted as an
option instead); sensor rail from the XIAO's 3.3 V output (§4 —
noise coupling into the measured rail); RP2040 readout (§3 —
D-050/D-052; wrong ADC).

**Stage 2 (implementation) outline + gates.** Implementation is a
separate GO. The implementation will be held to:

1. **DRC** (KiCad, severity-all): 0 errors, 0 unconnected; every
   warning individually disclosed in the report (Rev.4 precedent:
   no silent warnings).
2. **ERC: 0** — this board gets a native KiCad schematic (new
   design), closing the Matrix line's inherited no-schematic ERC
   gap (Rev.4 REPORT.md records it as inherited from Rev.3).
3. **Via-pad audit:** different-net minimum >= 0.10 mm binding
   floor, 0.125 mm project target (issue-183 yardstick); any
   at-floor site disclosed in writing with coordinates (Rev.4's
   at-floor 0.100 mm site is the cautionary precedent).
4. **Assignment verification (numerical, from built-board pads):**
   sensor -> MUX input -> SAADC channel map equals the design
   table for all 18 + 6 reference channels; EN net per MUX group
   verified; XIAO pin map frozen in the report and checked against
   the module's AIN-capable pads (§3 budget: 10 GPIO).
5. **Field-geometry preservation:** sensor coordinates identical
   to Rev.3 (16 mm: x 50/66/82, y 74/90/106; 17 mm: x 117/134/151,
   y 73/90/107 — measured §1); PCB thickness 1.2 mm; any deviation
   justified in writing or the gate fails.
6. **Power extraction:** sensor-rail droop <= 50 mV at worst-case
   burst load (all-bank continuous 90 mA sensor draw + logic),
   verified by resistance extraction before fabrication release.
7. **Manufacturing package** per the issue-267 conventions:
   BOM-jlcpcb with real LCSC codes and zero unmapped parts, the
   BA3 orderable pinned character-exact, CPL in the gerber frame,
   FABRICATION.md, DRAFT / NOT FOR ORDER; X2SON footprint traced to
   the TI DMR land-pattern drawing by citation.
8. **Availability re-scan at Stage 2 start** (TMAG stock moved
   6,314 -> 1,126 within a day during this study; §9 flags stand
   until re-observed).
