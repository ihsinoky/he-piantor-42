# Issue #284 — plan: wireless-variant MCU architecture, POWER-ONLY comparison

Study only. Design cost (redesign, firmware, re-qualification) is
explicitly out of scope and is not weighed anywhere.

## Question

With the sensor fixed as TMAG5253BA3 (D-049), is replacing the RP2040
with an nRF-series MCU worth it **on power consumption alone**?

## Architectures

- **A** — RP2040 (sensing) + nRF52840 module as radio co-processor (SPI).
- **B1** — nRF52840 module alone (sensing + radio).
- **B2** — nRF54L15 module alone (sensing + radio).

## Model discipline

Extend the #282 model (`.issue282-runtime/tmag-comparison.md` §4,
per-bank EN column). **Sensor terms are copied verbatim and never
recomputed:**

| Sensor term (fixed) | Value | Source |
|---|---|---|
| Hall power, continuous (typing) | 0.19 W | #282 §4 |
| Sensor energy per sweep (per-bank) | 67 µJ | #282 §3d |
| Sensor window per sweep | 0.35 ms planning (0.37 ms per-bank actual) | #282 §4 |
| Desk sensor avg (T=10 ms) | 6.7 mW | 67 µJ / 10 ms |
| Away sensor avg (T=100 ms) | 0.67 mW | 67 µJ / 100 ms |

Usage profile (aa-sizing §2, unchanged): typing 2 h continuous scan;
desk idle 6 h bursts T=10 ms; away 16 h bursts T=100 ms.
Pack: 4× AA NiMH, 8.66 Wh usable (#282) / 8.65 Wh delivered (task
brief — same figure, rounding); converter η=0.85 applied to load
energy exactly as in #282.

Only the MCU/radio terms vary per architecture. #282's placeholder
MCU terms (RP2040: 0.099 W typing / 0.011 W desk / 0.002 W away;
radio ~1 mW flat) are replaced by the datasheet-derived terms below.

## MCU-dependent terms to derive (per architecture)

| # | Term | Needed datasheet figures |
|---|---|---|
| T1 | Sleep floor between bursts (desk + away) | Sleep current in the mode that wakes on the burst timer AND retains firmware state; supply voltage stated. RP2040: DORMANT vs SLEEP choice justified. nRF: System ON + RAM retention + RTC (System OFF cannot wake on timer — excluded). |
| T2 | Wake energy per burst | Wake-up time from T1's mode × current during wake; clock-restart cost (RP2040 XOSC restart if DORMANT). |
| T3 | Sweep-active MCU energy per burst | MCU+ADC+peripheral power while the 0.35 ms sensor window runs (42 conversions, 14 MUX steps — identical work). Peripheral automation (RP2040 PIO+DMA / nRF PPI+SAADC+EasyDMA) credited only where the datasheet supports CPU-asleep operation. |
| T4 | Post-sweep processing energy per burst | CPU active time to reduce 42 samples to key state (assumption stated, same algorithm all arch.) × run power at the clock used. |
| T5 | Typing (continuous) MCU power | CPU run current at the clock the scan workload needs + ADC streaming current + (A only) co-processor active share. |
| T6 | Radio energy per day | #280 traffic model: keep-alive frames on the announced interval discipline + key-event frames during typing. Per-event energy from radio TX/RX currents + startup, per chip. In A the co-processor sends keep-alives autonomously (RP2040 not woken); in B the floor is shared. |
| T7 | (A only) second-chip overhead | Co-processor sleep floor (adds to T1), SPI event-transfer energy per key event, any always-on domain loss. Each numbered or explicitly dismissed with a reason. |

## Datasheet sources to consult (named, with section)

- RP2040 Datasheet (Raspberry Pi) — §5.4 electrical characteristics:
  run/sleep/dormant currents, ADC performance (500 ksps), XOSC startup.
- nRF52840 Product Specification (Nordic) — electrical specification:
  System ON/OFF sleep currents, CPU current (µA/MHz, DCDC), radio
  TX/RX currents, SAADC current & sample rate, wake-up times.
- nRF54L15 Product Specification (Nordic) — same set.
- Module/技適 footnotes: maker/distributor statements only (Seeed
  XIAO nRF52840 / XIAO nRF54L15, RayTac, Taiyo Yuden); NCS ESB
  library supported-boards documentation for nRF54L ESB support.

## Outputs

- `.issue284-runtime/mcu-power.md` + `.json`: term table, daily
  totals, delta decomposition by state, feasibility footnotes,
  power-only verdict.
- Computation script kept alongside for auditability.
