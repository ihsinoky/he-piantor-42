# Issue #280 phases (c)+(d) — plan

Basis: `.issue280-runtime/unifying-spec.md` (protocol), repo records below.
Study only; no implementation, no board changes.

## Numbers pulled from repo records (verified 2026-11-18 in this worktree)

- Design load **127 mA/Wing, 254 mA total, continuous** (docs/decisions.md
  D-026/D-027; "Plan for 127mA per Wing / 254mA total"). Per-sensor derived:
  127 / 21 = **6.05 mA per DRV5055** (21 sensors/Wing; 11 mA/sensor is the
  stress-only envelope, NOT the design load).
- Rail: **5.2 V TPS63070-class buck-boost, forced PWM**, from USB input
  4.50–5.25 V at the Main connector; **configured USB allowance 500 mA**
  total incl. all Main loads (D-027). Farthest-sensor guarantee **4.60 V**.
- Hall rail is **switched as a whole**: HALL_5V via TPS22919 load switch,
  GPIO7/HALL_PWR_EN, default-off (D-009/D-026). MUX bank enables
  (GPIO5/EN0, GPIO6/EN1) do NOT reduce sensor supply load (D-026 explicit).
- Scan topology: 42 keys = 2 banks × 3 TMUX1208, 7 addresses, 3 ADC
  channels in parallel → **14 acquisition slots per full scan** (D-010).
  No scan-rate figure exists in the records → scan rate is a STATED
  ASSUMPTION in all math below (1 kHz active / burst rates for sleep).
- Controller: RP2040 (U1). Used pins per records: GPIO5/6/7 (enables),
  GPIO26–28 = ADC0–2 (D-010/D-024). Full free-GPIO census to be taken
  from the Rev.10 schematic, not assumed.
- Case: low-deck production tree (issue-263): tray floor top **Z1.60**,
  under-board component space ≈ **3.10 mm** total, tallest flipped parts
  hang to Z2.20 (0.60 mm above floor); D-046 pocket floor Z0.60 in one
  field. **No battery cavity exists anywhere in the case records.**
- DRV5055 has no sleep/enable pin (datasheet knowledge — to be stated as
  such): duty-cycling can only happen at the HALL_5V rail switch.

## Approach

(c) Radio options (i) nRF24L01+ + RP2040/SPI, (ii) nRF52 co-processor,
    (ii') nRF52 as RP2040 replacement, (iii) donor-device harvest +
    nRF24LU1+ note. Per option: cost (search spot-check, dated), area,
    antenna vs aluminium plate, firmware scope.
    Power: (a) wired budget as recorded; (b) battery math at stated
    target 8 h/day × 5 days = 40 h, continuous vs duty-cycled Hall rail;
    (c) sensing/sleep semantics + burst-scan strategy + latency/missed-
    press cost; (d) hybrid (wireless link, USB-powered) coherence.
    Interface: SPI/GPIO budget from Rev.10 schematic census, EN interplay
    (none expected — verify), dual-mode story per option.
    Feasibility shape (e): 2–3 end states ranked cost > rework > freedom
    > speed, biggest risk each.

(d) Verification env: LOGITacker-capable sniffer (nRF52840 dongle),
    CrazyRadio-class alternative, sacrificial receiver ×2 recommendation,
    Solaar host, per-open-item (spec §6, items 1–10) capture/test mapping.
    Prices = search spot-checks labelled with date; stock claims never
    from snippets alone where avoidable — label crawl dates.

## Checkpoint plan
1. plan-cd.md (this file)
2. hw-implications.md + .json (+ feasibility shape §)
3. verification-env.md
