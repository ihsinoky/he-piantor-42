# Issue #280 follow-up — AA/AAA battery sizing

Study only. PO decision (2026-11-18): the battery is **AA or AAA
cells, user-replaceable** — no Li-ion pack, no in-device charging;
cells are swapped or charged externally. Basis: `unifying-spec.md`
(protocol / keep-alive) and `hw-implications.md` phase (c) (load
model, burst scan, case voids), with project numbers re-verified
against docs/decisions.md (D-009/D-024/D-026/D-027).

## Sources for every external number

| Quantity | Value used | Source |
|---|---|---|
| Hall design load | 254 mA @ 5.2 V rail, continuous (127 mA/Wing) | repo record D-026/D-027, via (c) §2a |
| DRV5055 ICC / tON | 3 typ / 5 max mA; tON 40 typ / 100 max µs | TI SBAS640 Rev. C, via (c) §2a/2c |
| Burst scan | 1 ms window; T=10 ms idle → 10% Hall duty; T=100 ms deep idle → 1% | (c) §2c |
| TPS63070 VIN range | **2.0–16 V run; ≥3.0 V to cold-start into a discharged output; UVLO falling 1.85 typ** | TI SLVSC58B datasheet (features + module extract of EC table) |
| TPS63070 IQ | 50 µA typ | TI SLVSC58B |
| Converter efficiency η | **0.85 flat** (assumption) | TI datasheet Vo=5 V efficiency curves: ~88–92% at VIN 3–5 V / Iout ≈0.3 A; 0.85 adds margin for light-load PFM and the 5.2 V setpoint |
| eneloop AA / AAA capacity | **1900 / 750 mAh minimum** (typ 2000 / 800), IEC 61951-2, 0.2C to 1.0 V | Panasonic eneloop lineup/FAQ (current generation; JP min values) |
| eneloop pro AA | 2450 mAh minimum (sensitivity only) | Panasonic eneloop lineup |
| Alkaline AA (Energizer E91) | 2850 mAh @25 mA to 0.8 V; ≈1990 @250 mA; ≈1530 @500 mA | Energizer E91 datasheet + its published discharge curves |
| Alkaline AAA (Energizer E92) | 1250 mAh @25 mA to 0.8 V; ≈670 @250 mA; ≈440 @500 mA | Energizer E92 datasheet + curves |
| nRF24L01+ currents | TX 11.3 mA @0 dBm; RX 13.5 mA; standby-I 26 µA; power-down 0.9 µA | Nordic nRF24L01+ Product Specification |
| nRF52832 sleep | System ON, RTC + RAM retention ≈ 2 µA class | Nordic product specification / DevZone (staff) |
| RP2040 currents | active ≈30 mA @3.3 V (use-case class); SLEEP 0.39 mA typ; DORMANT 0.18 mA typ (DVDD) | RP2040 datasheet §5.4 Table 635/637 |

## 1. Cell configurations vs the converter

Cell terminal behaviour (per cell):

| Chemistry | Fresh | Nominal plateau | End-of-discharge used | Series Ri class |
|---|---|---|---|---|
| NiMH (eneloop) | 1.45 V | 1.2 V (flat) | 1.0 V | ~25 mΩ (AA), ~35 mΩ (AAA) — low |
| Alkaline | 1.6 V | 1.5→1.1 V (sloping) | 0.8 V (datasheet basis) | ~150–300 mΩ fresh, rising steeply near EOD |

**Series cells add voltage, not mAh.** All comparisons below are in
Wh: pack Wh = cells × (mAh × average discharge V) × drain derating.

Converter coverage (TPS63070, VIN run 2.0–16 V, cold start ≥3.0 V,
UVLO ≈1.85 V falling):

| Config | Fresh | Nominal | At cell EOD | Verdict |
|---|---|---|---|---|
| 2× NiMH | 2.9 V | 2.4 V | 2.0 V | **FAIL-risk:** fresh pack is *below* the 3.0 V cold-start threshold, and EOD sits exactly on the 2.0 V run floor — any load sag ends the pack early. Not robust. |
| 2× alkaline | 3.2 V | 3.0 V | 1.6 V (0.8/cell) | Starts, but the converter floor (2.0 V) cuts the pack at 1.0 V/cell, discarding the 1.0→0.8 V tail (≈25% of datasheet capacity); typing-load sag (~0.75 A through ~0.4–0.6 Ω of tired alkaline Ri) hits the floor earlier still. Marginal. |
| 3× NiMH | 4.35 V | 3.6 V | 3.0 V | **Clean.** Whole discharge curve inside the range with margin at both ends. |
| 3× alkaline | 4.8 V | ~4.2 V | 2.4 V | Clean; full 0.8 V/cell depth reachable. |
| 4× NiMH | 5.8 V | 4.8 V | 4.0 V | Clean. |
| 4× alkaline | 6.4 V | ~5.6 V | 3.2 V | Clean (≤16 V abs max respected). |

Peak battery current check (typing, worst load 1.42 W at the rails →
1.67 W from the battery at η=0.85): 3×NiMH ≈ 0.46 A (0.24 C for AA —
eneloop delivers ≥95% of its 0.2 C rating there; AAA ≈0.6 C → ~92%
used). Alkaline AA at ~0.46 A pulses sits between its 250/500 mA
curves → effective ≈1900 mAh used in §2. Alkaline AAA at that drain
is on its 500 mA curve (≈440–560 mAh) — AAA alkaline is a poor match
for the typing load.

## 2. Runtime model

### Stated usage profile (24 h day) — every number below depends on this

| Phase | Duration | Scanner | System power at rails |
|---|---|---|---|
| Active typing | 2 h/day | continuous (analog fidelity, per (c) §2c) | Hall 1.321 W + RP2040 active 0.099 W + radio ~1 mW ≈ **1.42 W** |
| Desk idle (paired) | 6 h/day | bursts T=10 ms, 1 ms window (10% Hall duty) | Hall 0.132 W + MCU ~0.011 W ≈ **0.143 W** |
| Away / deep idle | 16 h/day | bursts T=100 ms (1% Hall duty), keep-alive continues | Hall 0.013 W + MCU ~0.002 W ≈ **0.016 W** |

Keep-alive cost (spec §4, Open Item 1 — interval semantics
unresolved): assumed 1 short TX/s ≈ 0.1 mW average for both radio
options; it is two orders below the burst floor and does not move
any result. Radio sleep floors — (i) nRF24 power-down 0.9 µA,
(ii-a) nRF52 ≈2 µA — are likewise negligible *as radios*; the floor
that matters is the shared one: the RP2040 owns sensing in both
options, waking for every burst (SLEEP-class 0.4 mA between bursts).
Option (i) additionally wakes the RP2040 ~1×/s to service the radio;
(ii-a)'s nRF52 sends keep-alives autonomously. Modelled difference:
**<0.2 mW in deep idle, <1% of daily energy — the options are
runtime-identical at this precision.**

### Daily energy

Load energy 3.95 Wh/day → **battery energy 4.65 Wh/day** at η=0.85.
Targets: 1 day = 4.65 Wh; **1 week (8 h×5 d) = 23.3 Wh**; 1 month
(30 d) ≈ 140 Wh.

### Runtime per configuration (usable pack Wh → days of the profile)

| Config | Usable Wh | Runtime | 1 day | 1 week | 1 month |
|---|---|---|---|---|---|
| 2× AA NiMH | 4.33 | 0.93 d | ~just misses (and cold-start risk, §1) | ✗ | ✗ |
| 3× AA NiMH | 6.50 | **1.40 d** | ✓ | ✗ | ✗ |
| 4× AA NiMH | 8.66 | **1.86 d** | ✓ | ✗ | ✗ |
| 4× AA NiMH pro (2450 min) | 11.17 | 2.40 d | ✓ | ✗ | ✗ |
| 3× AA alkaline | 6.95 | 1.50 d | ✓ | ✗ | ✗ |
| 4× AA alkaline | 9.27 | **1.99 d** | ✓ | ✗ | ✗ |
| 2× AAA NiMH | 1.66 | 0.36 d (~3 h of awake time) | ✗ | ✗ | ✗ |
| 3× AAA NiMH | 2.48 | 0.53 d | ✗ | ✗ | ✗ |
| 4× AAA NiMH | 3.31 | 0.71 d | ✗ | ✗ | ✗ |
| 4× AAA alkaline | 2.69 | 0.58 d | ✗ | ✗ | ✗ |

### Sensitivity — what moves the answer

**Active-typing hours at continuous scan dominate, by far.** Typing
is 2.84 Wh of the 3.95 Wh load day (72%) because continuous Hall
(1.42 W) is ~10× desk-idle and ~90× deep-idle power.

| Typing h/day | Battery Wh/day | 4× AA NiMH runtime |
|---|---|---|
| 0.5 | 2.40 | 3.6 d |
| 1 | 3.15 | 2.8 d |
| **2 (profile)** | **4.65** | **1.9 d** |
| 4 | 7.66 | 1.1 d |

Second-order levers: converter η 0.80↔0.90 moves runtime ±6%;
shrinking the burst window 1 ms→0.3 ms (faster scan) cuts idle
phases ~3× on their Hall part but they are only 28% of the day —
≤ +8% total. Cell *size* (AA vs AAA) is a 2.6× capacity lever, but
that is a configuration choice, not an assumption. Note the typing
figure is fidelity-driven: burst-scanning *during* typing would cut
typing energy ~10× but adds ≤10 ms latency and destroys analog
travel data between bursts — it changes the product, per (c) §2c.

## 3. Case consequence

Available space (adopted low-deck case, from (c) §2b): under-board
void ≈ **3.10 mm**, already spent (FPC channels, component
hang-down, D-046 pocket). Cell + holder needs ≈ Ø + 2 mm of wall:
**AAA ≈ 12.5 mm, AA ≈ 16.5 mm** of clear height wherever cells lie
flat. Nothing fits under the boards, full stop. Placements:

**(a) South-margin pod (cells flat, axes E–W, in the palm band).**
Sketch (side view, south band): tray floor ──[holder wall 1 mm]──
cell Ø10.5 (AAA) ──[lid 1 mm] → local top ≈ 12.5 mm above the tray
floor, vs the plate plane at 10.90 above the *board* datum — i.e. a
local hump roughly **+2 mm over the plate line at the palm band
only** for AAA (4× AAA side by side ≈ 46 mm wide × 44.5 mm long —
the south band is ~291 mm wide, so width is free). AA in the same
spot: Ø14.5 → **+5.6 mm local hump**, and 4× AA ≈ 58 × 50.5 mm
begins to crowd the Fly/Main zone. Keytop plane (22.00) is
untouched in both — the *plate* does not rise; the case grows a
palm-side bulge. Low-deck mandate: survives in letter (plate stays
10.90) but the case is no longer uniformly low, and the south band
is exactly where the PO's slope/palm geometry was most carefully
tuned (Issue #248 lineage) — expect palm-rest rework.

**(b) Central-bay hump (raised cover over the bay, cells under it).**
The bay holds Main + Fly + FFC channels; cells would stack *over*
the Main zone under a raised cover — a return of the Δ-era bay
cover, now ≈ +12.5 mm (AAA) over the bay top. Worse: the bay is
where the radio antenna must live ((c) §1.4) and a metal-free zone
matters there; cells (metal cans) beside/over the antenna detune
it. Deck cost is local but it spends the antenna site. Not
recommended.

**(c) Under-case pod (cells in a tray under the case bottom).**
Top of the keyboard is *exactly* the adopted design — plate 10.90,
keytop 22.00, zero rework above the tray floor. The pod adds
≈ +12.5 mm (AAA) / +16.5 mm (AA) *underneath*, so the keyboard sits
~23–27 mm tall overall at the pod and needs the pod shaped as a
full-width foot/tilt base to sit stably. Footprint unchanged.
Low-deck mandate: the *deck* survives perfectly; the *product*
becomes a keyboard on a battery plinth. This is the only placement
with zero interference with plate, antenna, FFC and palm geometry.

No placement is free: (a) taxes the palm geometry, (b) taxes the
antenna, (c) taxes total height/stability. **(c) is the least-bad;
(a) with AAA is second.**

## 4. Verdict

- **One week (23.3 Wh) is unreachable with AA/AAA — plainly.** The
  best legal pack (4× AA alkaline, 9.27 Wh; 4× eneloop pro,
  11.17 Wh) reaches ~40–48% of the week. The binding number is the
  daily energy: **4.65 Wh/day**, of which 72% is 2 h of continuous
  Hall scanning. No cell-count within the AA/AAA × ≤4 envelope
  closes a 2.5× gap.
- **One day is reachable, AA only, ≥3 cells:** 3× AA NiMH (1.40 d)
  is the smallest *robust* configuration (clean converter coverage,
  rechargeable, flat curve); 4× AA NiMH (1.86 d) or 4× AA alkaline
  (1.99 d) buys a comfortable 2-day rhythm. AAA in any count does
  not reach one day (best 0.71 d) — AAA is a half-day battery at
  this load.
- **One month is out of scope of the format** (~140 Wh ≈ 60+
  eneloop AA).
- **Effect on the (c) ranking: no flip — (i) nRF24+RP2040 still
  leads, and AA/AAA slightly widens its lead.** The feared mechanism
  ("sleep floor matters more with small cells") does not engage:
  in *both* options the RP2040 owns sensing and sets the floor
  (mW-class Hall bursts + 0.4 mA MCU sleep), while the radios'
  sleep difference is µA-class — under 1% of daily energy either
  way. Meanwhile AA/AAA makes runtime short enough that cells
  become a recurring consumable, which prices (ii-a)'s $4–14
  module premium against zero runtime gain. The ranking could
  flip only under a design change outside both studied options:
  nRF52 owning burst timing + the HALL rail and power-gating the
  RP2040 between bursts (an (ii-b)-ward step, with its rework).
- **What AA/AAA really decides:** it converts "battery wireless"
  from *impossible in this case* ((c), Li-ion framing) into
  *possible as a ~2-day, pod-or-hump product* — the remaining gate
  is no longer energy chemistry but whether the PO accepts
  placement (c) or (a) and a swap-every-2-days rhythm at the
  stated typing profile. If the PO's real typing load is closer to
  0.5 h/day of continuous scan, the same 4× AA pack is a 3.6-day
  battery and the proposition improves materially — the typing
  assumption, not the cells, is the decision variable.
