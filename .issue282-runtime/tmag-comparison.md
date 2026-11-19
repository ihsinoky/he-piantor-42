# Issue #282 — TMAG5253 vs DRV5055A3 formal comparison

Study only. No board/case changes, no orders. All electrical numbers
trace to a named datasheet (document + revision, PDFs in `sources/`)
or a repo record (file + section). Prices/stock in §5 observed
2026-11-18.

## Basis records

- Field & baseline chain: `docs/hall-acquisition.md` §1/§5/§6 — Jade Pro
  field at the sensor (1.2 mm PCB): **12 ±0.8 mT (top) → 70 ±3 mT
  (bottom)**, unipolar positive swing, span 58 mT over total travel
  **3.5 ±0.1 mm** (`docs/specification.md`). DRV5055A3 output 2.80 →
  4.25 V; after the 6.8 kΩ/10 kΩ divider (×0.595): **1.67 → 2.53 V,
  span 0.86 V at the ADC**.
- Wing scheme & guarantees: D-024 (common HALL_5V, shared address/3 ADC
  buses, independent bank enables, enables do **not** gate sensor
  power), D-026/D-027 (5.2 V rail ±2%, design load 127 mA/Wing,
  farthest-sensor target **4.60 V**, 50 mΩ loop targets, 11 mA/sensor
  stress-only).
- DRV burst basis: sibling `hw-implications.md` §2c (tON 40 typ /
  100 max µs; 1 ms planning window).
- Usage profile & pack: sibling `aa-sizing.md` §2 (profile unchanged
  in §4 below; 4× AA NiMH usable 8.66 Wh).

## 1. Datasheet table

| Parameter | DRV5055A3 (TI SBAS640C, Jan 2018–rev. Jun 2026) | TMAG5253BA3 (TI SBASAI5E, May 2023–rev. Apr 2026) |
|---|---|---|
| Supply range | 3.0–3.63 V **or** 4.5–5.5 V (two windows) | **1.65–3.6 V** (continuous) |
| Active current | **3 typ / 5 max mA @5.0 V**; 2/4 mA @3.3 V | **2.6 typ / 5 max mA @3.3 V**; 2/3.3 mA @1.8 V |
| Shutdown current | none — **no EN pin**; only the rail switch gates it | **8 nA typ @3.3 V** (EN < VIL); EN VIH 0.65×VCC |
| Power-on time | tON **40 typ / 100 max µs** (repo record, hw-impl. §2c, ex SBAS640; definition §6.3.7: VCC cross 3 V → OUT within 5% of VQ) | tON **20 typ / 45 max µs** (EN or VCC) |
| Sensitivity (typ) | A3: **25 mV/mT @5 V** (23.8–26.2, ±5%); 15 mV/mT @3.3 V. Ratiometric ∝ VCC | BA3: **15 mV/mT @3.3 V** (12.75–17.25, **±15%**); 8.12 mV/mT @1.8 V. Ratiometric ∝ VCC |
| Linear range | A3: **±85 mT @5 V** (±88 @3.3 V) | BA3: **±80 mT** (BA1 ±20 / BA2 ±40 / BA4 ±160) |
| Sensitivity tempco | STC 0.12 %/°C typ (magnet compensation, A-variants) | STC 0.12 %/°C typ — same class |
| Linearity / symmetry error | SLE ±1%, SSE ±1% | SLE ±0.55% max, SSE ±0.1% — slightly better |
| Quiescent drift | VQΔT ±1% × VCC (−40…125 °C) → ±50 mV @5 V ≡ ±2.0 mT | VQΔT ±30 mV @3.3 V (0…85 °C) ≡ ±2.0 mT — equivalent |
| Noise density | **130 nT/√Hz @5 V** (215 @3.3 V) | **220 nT/√Hz @3.3 V** |
| Input-referred noise (full BW) | BN **0.12 mTpp**; VN(A3) 3 mVpp | BN **0.17 mTpp**; VN(BA3) 2.3 mVpp @3.3 V |
| Bandwidth | 20 kHz | 15 kHz |
| Output swing (linear) | 0.2 V … VCC−0.2 V | 0.2 V … VCC−0.2 V |
| Package | SOT-23 (DBZ), 3-pin, hand-solderable | **X2SON-4 (DMR), 1.40 × 1.10 mm**, no leads + thermal pad; EN is pin 3 |

PMO spot-check verification: TMAG active 2 mA is the **1.8 V** figure
(3.3 V: 2.6 typ); tON "<25 µs" is the 20 µs typ (45 max); sensitivity
error 15% confirmed as the min/max band. DRV5055 tON/ICC confirmed.

## 2. Field compatibility

Field presented: **+12 → +70 mT** (offset unipolar swing, not ±).
A bipolar sensor idles at VQ = VCC/2 and uses only its positive half
range — the variant must cover +70 mT plus tolerances (field ±3 mT,
geometry spread unrecorded → margin judged against the ±80/±85 class).

| Variant | Range | Output @3.3 V, 12→70 mT | Verdict |
|---|---|---|---|
| BA1 (60 mV/mT) | ±20 mT | saturates at 20 mT | **FAIL** |
| BA2 (30 mV/mT) | ±40 mT | saturates at 40 mT | **FAIL** |
| **BA3 (15 mV/mT)** | **±80 mT** | **1.83 → 2.70 V** (VQ 1.65), span **0.87 V** | **PASS** |
| BA4 (7.5 mV/mT) | ±160 mT | 1.74 → 2.18 V, span 0.44 V | PASS but dominated (½ span, same noise → ½ resolution) |

BA3 worst-case check (invariant: distrust the first match): sensitivity
at max 17.25 mV/mT and VQ at max 1.69 V → output at 70 mT = 2.90 V <
VL max 3.10 V ✓; at 73 mT (field +tol) = 2.95 V ✓. Range usage 70/80 =
87.5% — margin 10 mT, same class as the DRV5055A3 baseline (70/85 =
82%, output 4.25 V vs VL max 4.80 V ✓). Per-key endpoint calibration
(already the design's method, hall-acquisition §6) absorbs the ±15%
sensitivity spread; what it cannot absorb — saturation — does not occur.

**Effective travel resolution (noise-limited).** Same method both
sides: RMS noise = BNpp/6.6; travel via the average field slope
58 mT / 3.5 mm = 16.6 mT/mm (the true curve is nonlinear; the ratio
between sensors is slope-independent).

| | DRV5055A3 @5 V (via divider) | TMAG5253BA3 @3.3 V (native) |
|---|---|---|
| Span at ADC | 0.86 V | 0.87 V |
| Noise at ADC | 3 mVpp × 0.595 = 1.79 mVpp | 2.3 mVpp |
| Noise-equiv. field | 0.12 mTpp / 0.018 mT RMS | 0.17 mTpp / 0.026 mT RMS |
| Noise-equiv. travel | **7.2 µm pp / 1.1 µm RMS** | **10.3 µm pp / 1.6 µm RMS** |

TMAG5253BA3 delivers the **same ADC span** with **~1.4× worse
noise-equivalent travel** (its 220 vs 130 nT/√Hz density is the whole
story). Both sit at a few RP2040 ADC LSBs pp (LSB = 0.81 mV); scan-rate
averaging shrinks both equally. Resolution cost is real but small;
it does not block adoption. (ADC quantization and divider Johnson
noise are common-mode to the comparison method and excluded, as in
the baseline record.)

## 3. Architecture impact

### (a) 3.3 V Hall rail vs the D-026/D-027 guarantee structure

The 4.60 V farthest-point target exists for one reason: the DRV5055's
high supply window starts at 4.5 V, so the design must deliver
≥4.5 V (+100 mV margin) at the far end of a 127 mA/Wing chain fed
from 5.2 V — only 0.6 V of total drop budget, hence the 50 mΩ loop
targets and the whole conductor-resistance programme.

TMAG5253's floor is **1.65 V**. On a 3.3 V rail the same recorded-class
drops (≤0.3 V worst) leave ≥3.0 V at the far sensor — the absolute-
floor problem **disappears**; a 3.3 V rail makes the far-point problem
strictly easier. What replaces the guarantee metric is the
**ratiometric mismatch**: the sensor output scales with its *local*
VCC while the RP2040 ADC references Main's 3.3 V, so a VCC difference
δ between Wing node and ADC reference appears as a δ/3.3 scale error.
(The issue-165 study already recorded that this cancellation does
not occur across the interconnect for the 5 V chain either.) A
sensible successor guarantee: **far-point drop ≤50 mV at design load**
(≤1.5% scale error, inside per-key endpoint calibration) — a drop
budget, not a floor. The 5.2 V buck-boost sizing, the 127 mA/Wing
load definition and D-027's 500 mA USB accounting are all artefacts
of the 5 V chain and would be re-derived, not carried over.

### (b) TMUX1208 at 3.3 V (TI SCDS389C)

Native: supply range 1.08–5.5 V. RON rises 5 Ω typ @5 V → **9 Ω typ
@3.3 V** (15 Ω max over temp) — immaterial into a high-impedance ADC
node. Transition time 25 ns @3.3 V. Settling is set by the ADC-node
RC, not the MUX: with the divider deleted (see (c)) the source
resistance collapses from ~4 kΩ to ~10 Ω (ROUT 1.27 Ω + RON 9 Ω),
so the 1 nF node τ falls from ~4 µs to ~10 ns and per-step settling
stops being the scan-rate term.

### (c) RP2040 ADC interface

Current design (hall-acquisition §5, D-010): the DRV5055's output can
approach the 5 V rail, above the ADC's 3.3 V domain, so each MUX
output passes a **6.8 kΩ/10 kΩ divider (×0.595) + 1 nF** — costing
span (0.86 V of the 1.45 V swing reaches the ADC) and setting the
4 µs settle τ. TMAG5253 at 3.3 V is **native**: its 1.83–2.70 V swing
lands directly in the ADC range, the divider is deleted, and the
full 0.87 V span reaches the converter. (For the record: the
DRV5055 also has a 3.3 V window at 15 mV/mT — issue-165 studied it —
but it keeps the no-EN limitation and its noise density *worsens* to
215 nT/√Hz at 3.3 V; it is not a substitute for the sensor change.)

### (d) EN control options (Wing side)

| Option | Routing / GPIO cost | Sensors on | Burst energy | Continuous Hall power |
|---|---|---|---|---|
| Ganged (EN = rail enable) | none — EN net is the existing Wing power enable | all 42 | 117 µJ | 0.360 W |
| **Per-bank (EN = MUX_EN0/1)** | **none** — both enables already run to every Wing's MUXes (D-024); EN pins tie to the same net | 21 (active bank) | 67 µJ | **0.19 W** |
| Per-sensor (EN decoded from A0–A2 + bank) | +1 decoder IC class per MUX group per Wing, 21 EN traces/Wing | 3 (one per MUX) | ~15 µJ (est.) | ~0.03 W |

Per-bank is the sweet spot: it exploits D-024's existing independent
enables — the very nets D-024/D-026 record as *not* reducing sensor
load with the DRV5055 (they gate only the MUXes) become true sensor
power gates with an EN-pin part. Its cost is one extra tON (45 µs
max) per bank per sweep. Per-sensor buys another ~6× on sensor power
but pays decoder parts, routing and a slower sweep (tON per address
step); it only matters if sensor power still binds after per-bank —
§4 shows it does not for the 7-day target.

## 4. Revised power model (aa-sizing profile, unchanged)

Profile (aa-sizing §2, verbatim): typing 2 h continuous; desk idle
6 h bursts T=10 ms; away 16 h bursts T=100 ms; MCU terms identical
(RP2040 active 0.099 W typing; 0.011 W desk; 0.002 W away; radio
~1 mW); converter η=0.85; pack 4× AA NiMH = 8.66 Wh usable.

**Burst window re-derived** (per full 14-step sweep; sources in
brackets): sensor power-on 45 µs max [SBASAI5E tON] + per step:
MUX transition 0.025 µs [SCDS389C] + node settling allowance 14 µs
[divider deleted, §3b/c; conservative vs the 10 ns τ] + 3 sequential
ADC conversions 6 µs [RP2040 single ADC core, 500 ksps class] →
step 20 µs. **Ganged window = 45 + 14×20 = 325 µs → planning
0.35 ms** (rail-ramp/slack absorbed, as the DRV model's 1 ms did);
per-bank = 2×45 + 14×20 = 370 µs at half the sensors-on power.
DRV baseline window: 1 ms (hw-impl. §2c).

| Quantity | DRV5055A3 @5 V (aa-sizing) | TMAG BA3 ganged | TMAG BA3 per-bank EN |
|---|---|---|---|
| Hall power, continuous | 1.321 W (recorded load) | 0.360 W | 0.19 W |
| Typing system power | 1.42 W | 0.460 W | 0.290 W |
| Desk-idle system power | 0.143 W | 0.024 W | 0.019 W |
| Away system power | 0.016 W | 0.004 W | 0.004 W |
| Load energy | 3.95 Wh/day | 1.13 Wh/day | 0.76 Wh/day |
| **Battery energy (η=0.85)** | **4.65 Wh/day** | **1.33 Wh/day** | **0.89 Wh/day** |
| **NiMH AA×4 runtime** | **1.86 d** | **6.5 d** | **9.7 d** |

**7-day test:** budget = 8.66 Wh / 7 d = 1.237 Wh/day battery
(1.051 Wh load). Per-bank EN **reaches it with margin (9.7 d)**.
Ganged alone falls short by 0.08 Wh load/day (6.5 d): its typing
power would need ≤0.42 W vs 0.46 W actual. Ganged could also reach
7 days by burst-scanning *during* typing (T=2 ms → typing 0.16 W →
~14 d), but that destroys inter-burst travel data — the product
change flagged in hw-impl. §2c, recorded here as a boundary, not a
lever. Per-sensor EN (typing 0.13 W) would give ~17 d and is not
needed for the target.

**Sensitivity (invariant: check the max, not the typ):** at
ICC max 5 mA @3.3 V, ganged battery energy rises to 2.20 Wh/day
(3.9 d) and per-bank to 1.32 Wh/day (6.6 d) — per-bank stays at the
7-day boundary even at datasheet-max current; the DRV model's
recorded-load basis (254 mA vs 126–210 mA datasheet) was comparably
conservative in the other direction.

## 5. Availability scan (observed 2026-11-18)

| Part | Channel | Stock | Unit price | Class |
|---|---|---|---|---|
| **TMAG5253BA3IQDMRR** (X2SON-4) | LCSC **C22401868** | **6,314** | $0.566 (1+) / $0.481 (10+) / $0.346 (1000+) | **Extended** (JLCPCB SMT) |
| TMAG5253BA3IQDMRR | Mouser 595-TMAG5253BA3IQDMRR | 3,802–4,187 | $0.80 (1) / $0.515 (10) / $0.421 (100) | — |
| DRV5055A3QDBZR (reference) | LCSC **C266128** | 1,732 (project live check 2026-11-16) | not re-observed today | Extended (per project BOM records) |

Variant-level trap check: the BA1 sibling (C-code adjacent, ±20 mT)
is also stocked (3,835) at a similar price — ordering must pin the
**BA3** orderable exactly; a variant slip is a saturation failure
(§2), not a graceful degradation. Stock depth is comfortable on both
sensors (≫10× the 42–54 pcs a build needs); TMAG5253 is a current TI
catalogue part (datasheet rev. Apr 2026), not a legacy risk.

## 6. Verdict

**(a) Wireless variant sensor: ADOPT TMAG5253BA3 as the design
input — conditional** on two items that only hardware can close:
(1) travel-curve/noise measurement on an evaluation Wing (the
project's standing method, hall-acquisition §7/§8 — the 1.4× noise
penalty and the ±15% sensitivity spread are datasheet-bound, the
actual field geometry spread is not recorded); (2) X2SON assembly
yield at JLCPCB (Extended class, no-lead 1.4 × 1.1 mm package —
process differs from the SOT-23 baseline). With per-bank EN wiring
(zero-cost, §3d) the NiMH AA×4 runtime goes **1.86 d → 9.7 d** and
the 7-day target is met with margin; even at datasheet-max sensor
current it holds ~6.6 d.

**(b) Wired design: no bearing.** Wired power is USB-supplied and
unconstrained at these levels; the 5 V DRV5055 chain, its D-026/
D-027 guarantees and the qualified boards stand exactly as they are.
Nothing in this comparison argues for touching the wired product.

**(c) What a sensor change would force (wireless-variant Wing
respin, one paragraph):** new sensor footprint (SOT-23 → X2SON-4
with EN pin) on both Wing pitches; Hall rail re-defined at 3.3 V
(new regulator/converter tree from the battery input, replacing the
5.2 V buck-boost sizing for the variant); TMUX1208 supply moved to
3.3 V (same part); EN nets tied to MUX_EN0/1 on the Wing; Main-side
ADC dividers deleted for the variant's sense path; re-qualification
list = per-key travel curves + noise, far-point drop under the new
≤50 mV budget metric, scan-settling measurement, X2SON assembly
yield, and the D-024 bank-switching sequence re-verified with
sensor wake (tON) inside it. The FFC/ZIF link, pin assignment and
signal content are unchanged.
