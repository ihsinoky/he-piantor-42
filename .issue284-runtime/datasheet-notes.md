# Issue #284 — datasheet figures used (all values traced)

Accounting conventions: nRF figures at their PS condition (3.0 V,
DCDC). RP2040 figures are pin currents from the datasheet; rail power
= 3.3 V × (I_DVDD + I_IOVDD) — the internal core regulator's input
current equals its output current in the LDO configuration, so this
is the auditable pin-sum at the 3.3 V rail (an external-SMPS-fed
DVDD would lower the DVDD share ~2.5×; sensitivity in the report).

## RP2040 — Raspberry Pi, *RP2040 Datasheet*

| Figure | Value | Source |
|---|---|---|
| DORMANT current (DVDD) | **0.18 typ / 4.2 max mA** | §5.7.2 Table 637, `hello_dormant` use case |
| SLEEP current (DVDD) | **0.39 typ / 4.5 max mA** | §5.7.2 Table 637, `hello_sleep` use case |
| IOVDD in dormant/sleep use cases | ≈0 (reported "—") | ibid. — model allows 0.02/0.05 mA |
| DVDD vs frequency, both cores FFT | ≈0.18 mA/MHz | §5.7.2.1 Fig. 172 → one core ≈0.09 mA/MHz → **≈11 mA @125 MHz** |
| ADC | 500 ksps, 12-bit | §4.9 → 2 µs/sample; 42 samples = 84 µs |
| XOSC startup delay | **1 ms default** (counts of 256 cycles); "of the order of a few ms"; exiting DORMANT with XOSC restarts XOSC + PLLs | §2.16.2/§2.16.3, §2.17.7 |
| ROSC restart | ≈1 µs | §2.17.7 (not used: ADC/RTC need XOSC accuracy) |
| DORMANT timer wake | RTC must be clocked from an **external** clock source in DORMANT (all internal clocks stop) | §2.11/§2.17.7 + SDK `hello_dormant` |

Model inputs derived: dormant floor 0.20 mA → 0.66 mW; sleep floor
0.44 mA → 1.45 mW; run (1 core + ADC/IO allowance 3 mA IOVDD)
14 mA → 46 mW; sweep-active (PIO+ADC+DMA, CPU in WFI) 6 mA →
20 mW (stated estimate between SLEEP and run); dormant wake
1.2 ms @ 8 mA → 31.7 µJ; sleep wake ≈0.1 µJ.

## nRF52840 — Nordic, *nRF52840 Product Specification* (PS values as
## reproduced in the PS electrical-specification tables / Product Brief)

| Figure | Value | Source |
|---|---|---|
| System ON, full 256 KB RAM retention, wake on RTC | **3.16 µA @3.0 V DCDC** | PS, I_ON_RAMON_RTC |
| System ON, full retention, wake on any event | 2.35 µA | PS, I_ON_RAMON_EVENT |
| System OFF, no retention | 0.4 µA | PS (excluded: no timer wake, no retention) |
| CPU CoreMark from flash | **3.3 mA @3.0 V DCDC** (52 µA/MHz × 64 MHz) | PS |
| SAADC running | **1.24 mA** (sampling @16 ksps, acq 20 µs, HFXO, DCDC) | PS, I_SAADC,RUN |
| TIMER running (HFXO) | 0.65 mA | PS, I_TIMER2 |
| Radio TX 0 dBm / RX (DCDC, 3.0 V) | **4.8 / 4.6 mA** | PS radio currents (Product Brief v2.0 table) |
| Cross-check: CPU + TX 0 dBm scenario | 8.1 mA = 3.3 + 4.8 ✓ | PS, I_S0 |
| SAADC rate | 200 ksps max, 12-bit | PS → 5 µs/sample; 42 = 210 µs |
| Wake from System ON | fast wake-up via 64 MHz internal oscillator, µs class | PS |

Model inputs: floor 3.16 µA → 9.5 µW; run 3.3 mA → 9.9 mW;
sweep peripherals (SAADC 1.24 + TIMER 0.65 + PPI/GPIOTE allowance
0.3) ≈ 2.2 mA → 6.6 mW over a 0.40 ms peripheral window (SAADC
210 µs of conversions interleaved with the 196 µs of MUX settling);
wake 0.05 µJ.

## nRF54L15 — Nordic, *nRF54L15 Datasheet v1.0* (Sep 2025),
## "Power consumption highlights" (@3.0 V)

| Figure | Value |
|---|---|
| TX 1 Mbps @0 dBm / RX 1 Mbps | **4.8 / 3.4 mA** |
| CPU CoreMark from RRAM with cache (128 MHz) | **2.6 mA** → 7.8 mW |
| Sleep: System ON IDLE, GRTC (XOSC), 256 KB RAM | **2.9 µA** → 8.7 µW |
| Sleep: System OFF with GRTC wakeup / System OFF | 0.9 / 0.7 µA (footnote only: System OFF wake is reset-class) |
| SAADC | 14-bit @31.25 ksps / **12-bit @250 ksps** / 10-bit @2 Msps → 12-bit mode used: 4 µs/sample; 42 = 168 µs |

Model inputs: floor 2.9 µA → 8.7 µW; run 2.6 mA → 7.8 mW; sweep
peripherals ≈2.0 mA → 6.0 mW (SAADC current not in the highlights
table; same class as nRF52840's 1.24 mA + timer — stated estimate);
wake 0.05 µJ.

## Traffic model (from Issue #280 spec, §4 + Open Item 1)

Keep-alive interval semantics are an open item in the sources; the
model assumes **1 keep-alive/s** during desk+away and **30 report
frames/s average** during the 2 typing hours — identical traffic for
all architectures. Per-event charge (radio ramp 40 µs @3 mA + TX
150 µs + ACK-listen 250 µs + CPU handling 100 µs):
B1/A ≈ 7.0 µJ per report, ≈6 µJ per keep-alive; B2 ≈ 6.4/5.5 µJ
(cheaper RX). Radio day total ≈ **0.55 mWh (A/B1), 0.50 mWh (B2)**
— a rounding term; even a 10× traffic error moves no total by >1%.

## Processing assumption (identical algorithm, all architectures)

Per sweep, reducing 42 samples to key state (threshold + linearized
joint estimation pass): **8,000 cycles** on Cortex-M0+ (RP2040),
**5,000 cycles** on Cortex-M4F/M33 (DSP/FPU instruction advantage) —
stated assumption, varied in the sensitivity check.
