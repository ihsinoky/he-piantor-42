# Issue #284 — wireless-variant MCU architecture: POWER-ONLY comparison

Study only. Design cost (redesign effort, firmware work,
re-qualification) is **excluded by the PO's instruction** and is not
weighed anywhere in this report, including the verdict.

**Question:** with the sensor fixed as TMAG5253BA3 (D-049), is
replacing the RP2040 with an nRF-series MCU worth it on power alone?

- **A** — RP2040 (sensing) + nRF52840 module as radio co-processor.
- **B1** — nRF52840 module alone (sensing + radio).
- **B2** — nRF54L15 module alone (sensing + radio).

## Method

The Issue #282 model is extended, not rebuilt. **Sensor terms are
copied verbatim** (#282, per-bank EN): continuous Hall power 0.19 W
typing; 67 µJ per sweep; sweep 0.37 ms; profile unchanged (typing
2 h continuous, desk 6 h bursts T=10 ms, away 16 h bursts T=100 ms);
pack 4× AA NiMH = 8.66 Wh usable; converter η=0.85. Sensor energy is
**430.9 mWh/day** in every architecture (typing 380.0 / desk 40.2 /
away 10.7). Only the MCU/radio terms vary, each derived from a named
datasheet (full trace in `datasheet-notes.md`; computation in
`model.py`, results in `mcu-power.json`).

**Transparency note:** #282's MCU terms were coarse placeholders
(RP2040 99/11/2 mW by state + radio ~1 mW flat ≈ 320 mWh/day).
Replaced by the datasheet terms below, architecture A improves from
#282's 9.7-day headline to 14.2 days *on the same sensor model*.
The A→B delta — the deliverable of this study — is computed on one
consistent datasheet basis for all three architectures.

## 1. Term-by-term (per architecture)

### (a) Sleep floor between bursts — the floor that can wake on the burst timer

| | Mode used | Floor |
|---|---|---|
| A desk | RP2040 **SLEEP** (RTC on internal clock, fast wake; DORMANT's 1 ms XOSC restart would eat 10% of the 10 ms period) | **1.45 mW** (DVDD 0.39 typ + IOVDD allowance, RP2040 DS Table 637) |
| A away | RP2040 **DORMANT** + external RTC clock (required: all internal clocks stop in DORMANT) | **0.66 mW** (DVDD 0.18 typ mA) |
| A co-pro | nRF52840 System ON, full RAM retention, RTC | 9.5 µW (3.16 µA @3.0 V) |
| B1 | nRF52840 System ON, full RAM retention, RTC (µs-class wake) | **9.5 µW** (3.16 µA @3.0 V) |
| B2 | nRF54L15 System ON IDLE, GRTC, 256 KB RAM | **8.7 µW** (2.9 µA @3.0 V) |

System OFF is excluded on both nRF parts for the burst states: it
has no timer wake with retention on nRF52840 (0.4 µA buys a reset),
and on nRF54L15 the GRTC-wake System OFF (0.9 µA) is likewise a
reset-class wake. The headline sleep numbers (0.4/0.7 µA) are
therefore *not* used — per the study invariant.

### (b) Energy per burst (identical scan work: 42 channels, 14 MUX steps, 0.35 ms sensor window)

| Term | A (RP2040) | B1 (nRF52840) | B2 (nRF54L15) |
|---|---|---|---|
| Wake | desk 0.1 µJ (SLEEP) / away **31.7 µJ** (XOSC 1 ms startup delay + PLL relock, DS §2.16.3) | 0.05 µJ | 0.05 µJ |
| Sweep-active (peripherals run, CPU in WFI) | PIO steps MUX, ADC free-run + DMA: 20 mW × 0.37 ms = **7.4 µJ** | PPI/TIMER steps MUX, SAADC+EasyDMA: (1.24 SAADC + 0.65 TIMER + 0.3 PPI mA) 6.6 mW × 0.40 ms = **2.6 µJ** | DPPI/TIMER + SAADC: ≈6.0 mW × 0.37 ms = **2.2 µJ** |
| Processing (42 samples → key state; 8k cycles M0+ / 5k cycles M4F/M33, stated assumption) | 64 µs @46 mW = **2.9 µJ** | 78 µs @9.9 mW = **0.8 µJ** | 39 µs @7.8 mW = **0.3 µJ** |
| **Per-burst MCU total** | **desk 10.4 µJ / away 42.0 µJ** | **3.5 µJ** | **2.6 µJ** |

Peripheral automation is real on all three (RP2040 PIO+DMA;
nRF PPI/DPPI + SAADC + EasyDMA): on no architecture does the CPU
sit at run current for the whole sweep. The nRF ADCs are slower per
conversion than the RP2040's (SAADC 200 ksps / 54L 250 ksps @12-bit
vs 500 ksps), but the 42 conversions (210/168 µs) interleave with
the 196 µs of MUX settling inside the sweep — B1's peripheral
window grows by 0.03 ms and is charged for it above.

### (c) Continuous-scan (typing) MCU power

Per-sweep MCU energy ÷ 0.37 ms sweep period (sweeps back-to-back):

| A | B1 | B2 |
|---|---|---|
| **28.2 mW** (+0.02 mW SPI share, see (e)) | **9.4 mW** | **7.0 mW** |

### (d) Radio energy per day (Issue #280 traffic model)

Keep-alive 1/s over desk+away (interval semantics are Open Item 1
in the #280 spec — assumed, identical for all) + 30 report frames/s
average while typing. Per-event ≈6–7 µJ (radio ramp + TX + ACK
listen + CPU handling; nRF52840 TX 0 dBm 4.8 mA / RX 4.6 mA;
nRF54L15 4.8 / 3.4 mA). **Day total ≈0.55 mWh (A, B1) / 0.50 mWh
(B2)** — a rounding term. In A the co-processor originates
keep-alives autonomously; the RP2040 is never woken for one.

### (e) Second-chip overhead in A — each item numbered or dismissed

- Co-processor sleep floor: 9.5 µW × 24 h = **0.23 mWh/day** (counted).
- SPI event transfer: ≈0.5 µJ per report × typing traffic =
  **0.03 mWh/day** (counted inside A's typing/radio terms).
- SPI wakeups of the RP2040 by the co-processor (e.g. LED frames):
  dismissed — receiver→device frames are rare, GPIO wake from
  SLEEP/DORMANT is already the burst mechanism, no extra standing cost.
- Level/domain losses: dismissed — both chips sit on the same
  3.3 V/3.0 V-class rail accounting used throughout; no second
  converter exists in the term model.
- **Total second-chip overhead ≈0.26 mWh/day — immaterial.** A's
  penalty is not the second chip; it is the RP2040's own terms.

## 2. Daily totals (load mWh/day; battery = load / 0.85; pack 8.66 Wh)

| State | A | B1 | B2 |
|---|---|---|---|
| Sensor (fixed) | 430.9 | 430.9 | 430.9 |
| MCU typing (2 h) | 56.5 | 18.7 | 13.9 |
| MCU desk (6 h) | 14.6 | 2.1 | 1.6 |
| MCU away (16 h) | 17.1 | 0.7 | 0.6 |
| Co-pro floor + radio | 0.8 | 0.6 | 0.5 |
| **MCU+radio total** | **89.0** | **22.1** | **16.6** |
| **Load total** | **519.9** | **453.0** | **447.5** |
| **Battery Wh/day** | **0.612** | **0.533** | **0.526** |
| **NiMH AA×4 runtime** | **14.2 d** | **16.2 d** | **16.4 d** |

**Delta decomposition (load mWh/day, A → B):**

| | Typing | Desk | Away | Floor+radio | Total |
|---|---|---|---|---|---|
| A → B1 (−66.9) | −37.8 (56%) | −12.5 (19%) | −16.4 (25%) | −0.2 (0%) | −66.9 |
| A → B2 (−72.4) | −42.6 (59%) | −13.0 (18%) | −16.6 (23%) | −0.3 (0%) | −72.4 |

Reference ceiling: with a zero-power MCU the sensor term alone
caps runtime at **17.1 days**. A reaches 83% of that ceiling,
B1 95%, B2 96%.

## Sensitivity (does any plausible correction flip the order? No)

- **RP2040 at datasheet-max sleep currents** (Table 637 max average:
  SLEEP DVDD 4.5 mA, DORMANT 4.2 mA — worst-corner across temperature
  and voltage): A's desk/away MCU terms balloon to 92/226 mWh/day
  and A falls to **≈9.1 days**. The nRF sleep figures available are
  typ-only, so this bound is one-sided; the typ basis is the
  planning standard used across the project (#282 likewise). Even
  so: at max, B's lead grows — the order never flips.
- A typing with no PIO/DMA automation (CPU at run for the whole
  sweep): A typing MCU 54 mW → A ≈12.9 d. Order unchanged.
- B1 with no PPI automation (CPU at run during the sweep): B1
  ≈16.0 d. Order unchanged.
- Processing cost doubled (16k/10k cycles): A ≈13.7 d, B1 ≈16.1 d.
- Traffic 10× the model: radio ≤6 mWh/day everywhere. No effect.

## 3. Feasibility footnotes (factual, one line each — not weighed)

- 技適 B1: certified nRF52840 modules exist for Japan — Seeed XIAO
  nRF52840 carries MIC (Japan construction-type certificate;
  Seeed states certification is at the physical layer), and
  RayTac MDBT50Q / Taiyo Yuden families offer MIC variants.
- 技適 B2: Seeed XIAO nRF54L15 holds a Japan MIC type certification
  (TIMCO cert. 217-252398, 2025-07-24); Panasonic PAN B611
  (nRF54L15) is a module family with regional variants.
- ESB: the nRF Connect SDK ESB library supports both parts —
  samples build for nrf52840dk and nrf54l15dk, and NCS v2.8.0
  lists ESB as supported on nRF54L15; the #280 protocol needs no
  ESB feature beyond DPL + ACK payloads, present on both.
- ADC quality: RP2040 ADC (12-bit, ENOB ~9-bit class) vs SAADC
  (12-bit, oversampling available) vs 54L SAADC (12-bit @250 ksps /
  14-bit @31.25 ksps) — the scan is sensor-noise-limited (#282) and
  uses no oversampling on any architecture, so ADC quality changes
  no conversion counts and no energy term.

## 4. Verdict (power only)

- **B1 gains +2.1 days over A (14.2 → 16.2 d, +15%); B2 gains
  +2.3 days (→ 16.4 d, +16%). B2's edge over B1 is +0.2 day —
  negligible in this workload.**
- The gain is **concentrated in typing (≈56%)**, then away (25%)
  and desk (19%) — i.e. mostly in the state the usage profile
  weights *least* by hours but where absolute power is highest,
  plus a long thin contribution from the 16 away hours, where A's
  per-cycle energy (DORMANT wake 31.7 µJ + floor share ≈65 µJ +
  sweep/processing ≈10 µJ ≈ 107 µJ) is ~24× B1's (≈4.4 µJ).
- **The single deciding number: typing-state MCU power — A 28 mW
  vs B1 9 mW / B2 7 mW** — worth ~38–43 mWh/day of the ~67–72
  mWh/day delta. Everything else (sleep floors, radio, second-chip
  overhead) is second-order, because the fixed sensor term
  (430.9 mWh/day) caps any MCU saving at the 17.1-day ceiling:
  B recovers most of the MCU headroom that exists, and no MCU
  choice can go further without touching the sensor/scan design.
- On power alone, the replacement **is worth a real but bounded
  gain: about +2 days on a ~14-day base**, with B1 and B2
  effectively tied.
