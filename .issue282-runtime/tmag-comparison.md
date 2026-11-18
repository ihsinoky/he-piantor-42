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
