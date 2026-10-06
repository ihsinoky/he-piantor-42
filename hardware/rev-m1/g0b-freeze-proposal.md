# G0B Rev.M1 architecture and interface freeze proposal

Status: **DRAFT PROPOSAL FOR PMO REVIEW AND PRODUCT OWNER HUMAN GATE**

Issue: [#57](https://github.com/ihsinoky/he-piantor-42/issues/57)

Baseline: `7d7f3cffe4fb98771e3ca47f800a54de22fa8c4f`

This document is a review package, not an accepted design decision. **G0B is
not accepted or complete**, EVT-002 remains locked, and physical implementation
has not started. Values labelled “proposed” below have no authority until the
Product Owner accepts the Human Gate. This proposal does not modify D-014,
D-015, or D-016 and does not reopen the JITX decision.

## 1. Authority and scope

### 1.1 Accepted inputs (not proposed here)

* D-014 makes project-owned native TypeScript/TSX through unmodified stock
  tscircuit the M1 electrical source; D-016 makes that the active forward EDA
  candidate after the JITX physical-backend NO-GO.
* D-015 fixes the reusable Main / Wing responsibility split. Main owns RP2040,
  USB and power, switched `HALL_5V`, three ADC channels, and the three
  divider/filter paths. A Wing owns Hall sensors, three TMUX1208 devices for a
  production 21-key Wing, and switch geometry.
* The acquisition baseline is three shared address lines, one enable per Wing,
  three simultaneous analog outputs, seven used inputs per mux, and only one
  enabled Wing at a time. The required measurement path is:

  ```text
  Hall -> TMUX1208 -> Wing connector/cable -> Main
       -> 6.8 kOhm / 10 kOhm divider + 1 nF -> RP2040 ADC
  ```

* Evaluate 17.0, 16.5, and 16.0 mm; two copper layers and 1.2 mm thickness are
  the baselines. The 100 x 100 mm region is an optimization, not a pitch rule.

### 1.2 Proposed G0B freeze

Subject to PO acceptance, freeze the 14-contact JST GH cable interface and
pinout in section 3, the 100 mm nominal evaluation cable in section 4, three
separate pitch-specific Wings plus an electrically full-load variant in
section 5, the coverage contract in section 6, and test access and evaluation
methods below.

### 1.3 Explicitly outside this proposal

Schematics, placement, routing, production Gerbers, manufacturing approval,
an order, a production pitch or Hall choice, measured acceptance, and final
Rev.A reuse approval remain future work. Divider/filter values remain the
accepted provisional baseline until G2 evidence. This proposal creates no
accepted D-017 and grants no USB manufacturing exception.

## 2. Connector recommendation

### 2.1 Candidate comparison

Primary electrical/mechanical claims below come from manufacturer material.
Supplier stock is only a dated availability observation, not a lifecycle
guarantee.

| Candidate | Exact proposed mating set considered | Published characteristics | Practical disposition |
| --- | --- | --- | --- |
| **JST GH (recommended)** | Main and Wing header: `BM14B-GHS-TBT(LF)(SN)`; cable housing at each end: `GHR-14V-S`; crimp contacts: `SSHL-002T-P0.2` for 30–26 AWG | 14 positions, 1.25 mm pitch, 1 A AC/DC, 50 V, initial contact resistance at most 30 mOhm and at most 50 mOhm after environmental tests; positive contact lock; top-entry keyed/shrouded SMT header. Header envelope is 20.75 mm across the 14-position body, 4.25 mm deep and approximately 4.15 mm high; housing is 18.75 mm wide and approximately 5.7 mm long. [JST GH datasheet](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) | Small, polarized, latched, cable-compatible, and permits the analog/return allocation below. A precrimped assembly is strongly preferred: reliable hand crimping needs the specified tooling. The header's SMT hold-downs suit one-side PCBA. LCSC listed the header as `C265384` with stock when researched on 2026-10-05; housing/contact stock and JLCPCB assembly classification were **not verified**. |
| Hirose DF13 | `DF13-14P-1.25DSA(25)` vertical through-hole header, `DF13-14DS-1.25C` housing, `DF13-2630SCF` contact | 14 positions, 1.25 mm, 1 A, 30 mOhm maximum, friction lock; approximately 19.5 mm header width. [Hirose DF13 product data](https://www.hirose.com/en/product/p/CL0536-0113-8-25) | Credible and hand-solderable, but through-hole header conflicts with one-side SMD preference and friction retention is weaker for repeatedly handled evaluation cabling. Current LCSC/JLCPCB availability was not verified. |
| Molex PicoBlade | `53261-1471` right-angle SMT header, `51021-1400` housing, `50079-8000` crimp terminal | 14 positions, 1.25 mm, 1 A maximum, 20 mOhm maximum contact resistance; polarized wire-to-board system. [Molex 53261 product page](https://www.molex.com/en-us/products/part-detail/532611471) | Compact and credible, but the considered version uses friction retention rather than JST GH's positive lock. Exact mating-cycle rating and current LCSC/JLCPCB availability were not verified. |

The JST set is recommended for signal integrity through abundant returns,
positive mechanical retention, small size, and a presently verifiable LCSC
header—not simply price. A 20.75 mm header edge does not determine whether a
21-key Wing fits 100 x 100 mm; it is small relative to the key field, but the
later placement proof must include cable bend/assembly clearance.

**Unverified connector properties:** the JST manufacturer catalogue consulted
does not specify a mating-cycle rating. No value is inferred. LCSC stock for
`GHR-14V-S` and `SSHL-002T-P0.2`, JLCPCB assembly eligibility/classification,
and availability of a correctly pinned 100 mm assembly must be rechecked at
implementation and pre-order reviews. The catalogue dimensions must be
transcribed and independently checked against approved manufacturer CAD before
creating the native footprint.

### 2.2 HALL_5V current and contact capacity

The calculation deliberately uses the accepted DRV5055A3 reference and
three-mux production Wing, rather than an arbitrary budget.

| Item | Primary-source value | 21-key calculation |
| --- | --- | --- |
| DRV5055 supply current | **3 mA typical and 5 mA maximum** at `VCC = 5.0 V`, `B = 0 mT`. Source: current TI datasheet **SBAS640C, Rev. C, revised June 2026**, section 5.5. [TI DRV5055 datasheet](https://www.ti.com/lit/ds/symlink/drv5055.pdf) | Typical `21 x 3 = 63 mA`; datasheet-bounded `21 x 5 = 105 mA`. These values supersede the 6 mA / 10 mA values in the first proposal revision. |
| TMUX1208 supply current | **0.02 microampere typical at 25 °C and 2.7 microamperes maximum from -40 °C to +125 °C** at the 5 V operating condition with logic inputs at 0 V or 5.5 V. Source: current TI datasheet **SCDS389C, Rev. C, revised December 2018**, section 7.5. [TI TMUX1208 datasheet](https://www.ti.com/lit/ds/symlink/tmux1209.pdf) | Three muxes: typical `3 x 0.02 microampere = 0.00006 mA`; datasheet-bounded `3 x 2.7 microamperes = 0.0081 mA`. |
| Proposed engineering allowance | Project assumption, not a measured component requirement: 20% above the component maximum sum for tolerances, local indicators/leakage if later approved, and estimation error. It is **not** permission to add loads silently. | `(105 + 0.0081) x 1.20 = 126.00972 mA`, rounded up to **127 mA per Wing design-current estimate**. |

Only one Wing is enabled for analog selection, but disabling TMUX outputs does
not necessarily remove Hall power; therefore Rev.A with both Wings connected
may draw twice the Hall contribution unless the implemented power architecture
separately switches Wings. The two-Wing datasheet-maximum component sum is
`2 x 105.0081 = 210.0162 mA`; applying the same project allowance gives a
**254 mA 42-sensor/two-Wing design-current estimate**. This lower revised
estimate is not final USB product power qualification. MCU, flash, regulators,
LEDs, load-switch loss, startup/inrush and applicable USB current policy still
belong to the later product power-budget gate. This proposal rates the single
Wing connector path, not the whole USB product.

One JST GH contact rated 1 A carries the proposed 127 mA with a 7.87x rating
ratio. At the manufacturer's 50 mOhm post-test contact-resistance limit, its
illustrative connector drop is `0.127 A x 0.050 ohm = 6.35 mV` and dissipation
is approximately 0.81 mW. These are calculations, not measurements and not a
cable-drop guarantee. Six return contacts share signal and supply return by
layout; even the conservative worst case of all 127 mA through one rated return
remains under 1 A, so no unsafe current-sharing assumption is needed.

EVT-002 must measure typical, maximum-observed, startup, and temperature-related
current at the Wing end and validate cable/connector drop. The optional
SL3102-3 current is not used to relax this reference calculation.

## 3. Proposed exact 14-pin interface

Pin numbers are the JST manufacturer circuit numbers viewed at the mating face;
native tscircuit implementation must also place a pin-1 mark on both boards and
the cable drawing. Both cable ends are wired **1:1**, circuit 1 to circuit 1;
do not mirror conductors by visual wire order.

| Pin | Signal | Direction at Main | Domain / implementation purpose |
| ---: | --- | --- | --- |
| 1 | `HALL_5V` | power out | Wing Hall and three TMUX supplies; one 1 A contact is adequate for the derived 127 mA estimate. |
| 2 | `GND_PWR` | return | Dedicated adjacency for Hall-rail supply/decoupling current. Joins the common `GND` plane at both PCBs; it is not a separate net. |
| 3 | `MUX_A0` | output | 3.3 V shared address bit. |
| 4 | `GND_CTRL` | return | Control reference and break between power and remaining controls; common `GND` net. |
| 5 | `MUX_A1` | output | 3.3 V shared address bit. |
| 6 | `MUX_A2` | output | 3.3 V shared address bit. |
| 7 | `WING_EN` | output | Active-high enable fanned out to all three Wing TMUX `EN` pins. Main maps the two physical connectors to `MUX_EN0` / `MUX_EN1`. |
| 8 | `GND_A` | return | Analog return adjacent to output A; common `GND`. |
| 9 | `MUX_OUT_A` | input | Raw Wing mux output to Main ADC0 divider/filter. |
| 10 | `GND_A` | return | Inter-output guard/return; common `GND`. |
| 11 | `MUX_OUT_B` | input | Raw Wing mux output to Main ADC1 divider/filter. |
| 12 | `GND_A` | return | Inter-output guard/return; common `GND`. |
| 13 | `MUX_OUT_C` | input | Raw Wing mux output to Main ADC2 divider/filter. |
| 14 | `GND_A` | return | Edge analog return; common `GND`. |

There are six physical ground contacts but one electrical `GND` net. Pin 2
keeps Hall load return adjacent to its supply, pin 4 gives the control bundle a
near return, and pins 8/10/12/14 create `G-A-G-B-G-C-G` so no analog conductor
is adjacent to another analog conductor or the address bus. This reduces loop
area and capacitive/digital coupling and provides a low-impedance reference for
the Main-side divider. The cable allocation must retain those individual
conductors; do not consolidate them in a harness splice.

No reserved pin is proposed: a 14th “future” signal would cost an analog guard
or force a larger connector without a justified function. `3V3`, `HALL_PWR_EN`,
and an analog reference are intentionally absent. Main controls the upstream
load switch; Wing logic is TMUX-compatible at 3.3 V while powered by `HALL_5V`;
and every analog signal is ratiometric to its local Hall supply and returned to
the common ground. If implementation discovers another required signal, it
must reopen G0B rather than repurpose a ground silently.

## 4. Representative interconnect proposal

Use two `BM14B-GHS-TBT(LF)(SN)` top-entry board headers and a **100 mm nominal
contact-to-contact, 1:1, 14-conductor cable** with `GHR-14V-S` housings and
`SSHL-002T-P0.2` contacts at both ends. Specify 28 AWG stranded copper as the
assembly target (within the named contact's supported range), with all 14
conductors separately crimped. Procurement must confirm finished length,
wire insulation, crimp pull quality, and continuity before use.

There is no overall shield at 100 mm. Instead, dedicated returns implement the
allocation in section 3; adding a shield that Rev.A will not carry would make
the evaluation less representative. Route the cable away from USB/crystal and
switch magnets, strain-relieve it at the enclosure/fixture, and rely on the GH
positive latch for connector retention—not on friction or adhesive. Record
actual conductor resistance and assembled length.

This is representative of the proposed Rev.A electrical boundary, connector,
pin allocation, and realistic short internal harness. Final Rev.A mechanical
length and enclosure restraint are unresolved; if they exceed 100 mm
materially, repeat the analog-path tests with the maximum production-intent
length. Primary qualification may not substitute a direct Hall-to-ADC jumper.

## 5. Evaluation Wing structure

### 5.1 Options considered

| Structure | Validity and isolation | Cost / Main reuse / complexity | Decision |
| --- | --- | --- | --- |
| One Wing containing all three pitch regions | Simultaneous build reduces lot variation, but three magnetic arrays can influence one another unless widely separated; switch/keycap usability and hand access are compromised. | One PCB, but likely exceeds 100 x 100 mm and complicates routing/fixtures. | Reject. |
| Mechanically configurable/common Wing | Moving sensors or switches makes alignment and return-to-position error part of the result; it cannot faithfully change fixed PCB Hall geometry. | Superficially reusable, but fixture complexity and systematic uncertainty are high. | Reject. |
| **Separate pitch-specific Wings** | Each has identical electrical topology and an isolated fixed-pitch 3 x 3 test matrix. It supports real multi-key/keycap use without another pitch region nearby. Board-to-board comparison must control lot, sensor, switch, alignment, and setup. | Three small PCBs reuse one Main and one cable. More PCB assemblies, but simplest experiment and clearest geometry. It independently reveals whether each outline can meet 100 x 100 mm. | **Recommend.** |

### 5.2 Proposed physical set

Create three otherwise common Evaluation Wing variants generated from **one
project-owned parameterized native definition**, with pitch set to 17.0,
16.5, or 16.0 mm. Each uses a 3 x 3 switch/Hall matrix, three TMUX1208 devices,
and the actual connector. Assign matrix columns A/B/C to the three muxes and
rows to addresses 0/1/2, so every scan produces three simultaneous spatially
adjacent channels. Provide non-ferromagnetic mounting and a travel fixture that
can depress center, edge, and neighboring keys independently.

The 3 x 3 field supports travel range, orthogonal/diagonal adjacent-magnet
tests, simultaneous neighbors, real switches/keycaps, repeatability/noise,
TMUX address transitions, and the complete interconnect. Keep unrelated
ferromagnetic hardware and other pitch Wings outside a documented exclusion
distance established during fixture design; characterize background with the
other Wings removed. This is more valid than choosing 16.0 mm for panel cost.

For one of the three pitch Wings (prefer 17.0 mm as the historical baseline,
not as a production choice), add 12 Hall-only electrical-load sites away from
the 3 x 3 magnetic area: four further used channels on each mux at addresses
3–6. This **21-sensor full-load Wing** directly represents three muxes, seven
used channels each, rail current, unused S7 behavior, address transitions, and
analog loading. It need not accept switches at those 12 sites; place it so
their packages and any test magnets cannot perturb the mechanical matrix.
If adequate magnetic separation cannot be demonstrated inside the board
outline, make the electrical-load coverage a fourth Wing rather than weakening
the pitch experiment. Separate Main/Wing manufacturing is explicitly allowed.

Evaluate—not require—each outline and a representative future 21-key outline
against 100 x 100 mm including connector and cable clearance. Reuse of the
Main is mandatory across all variants. The parameterized definition and
variant generation are post-G0B implementation work.

## 6. Production-equivalent MUX and bank evidence

| Production behavior | Rev.M1 evidence |
| --- | --- |
| Three ADC channels / three mux outputs | Direct: the 3 x 3 matrix drives A/B/C simultaneously through three TMUX1208s, connector, three Main filters, and ADC0/1/2. Measure pairwise coupling. |
| Seven used inputs per mux / unused S7 | Direct on the full-load Wing: addresses 0–6 have Hall sources and S7 is physically unconnected as production intends. Pitch-only Wings directly cover addresses 0–2 and bound the rest only through the full-load variant. |
| Shared A0/A1/A2 and address transitions | Direct: all three muxes share the cable controls. Sweep sequential, worst-code-change (`3 -> 4`, all bits), `6 -> 0`, and unused `7`, in both directions. |
| Left/right bank behavior | Main has two identical 14-pin Wing ports mapped to `MUX_EN0` and `MUX_EN1`. Exercise two connected Wings: disable both, enable one, transition through an enforced both-disabled interval, then enable the other. Simultaneous enable is a fault test only, never normal scan operation. |
| Bank transition and shared-output loading | Direct with two Wings physically connected to shared Main A/B/C nodes. Measure disabled-Wing leakage/loading, first sample after bank change, and accidental overlap response. |
| Production Hall current | Direct for one 21-sensor full-load Wing; two-Wing total is direct when it and another loaded Wing are connected, otherwise bounded by the datasheet calculation and remains a Rev.A validation item. |
| All-key spatial coupling and final cable mechanics | Not represented by a 3 x 3 matrix. G2 selects pitch/magnetic architecture; final 21-key geometry, enclosure cable restraint, and whole-Wing spatial effects remain Rev.A pre-release validation. |

Safe startup proposal: **each physical Main `MUX_EN0` / `MUX_EN1` output must
have its own explicit external pull-down resistor on Main**. The resistor holds
the corresponding Wing's three TMUX1208 `EN` inputs low while the RP2040 pin is
reset, high impedance, or not yet configured; both Wings therefore remain
disabled independently of firmware initialization. Normal firmware actively
drives the output high to override the pull-down. Do not rely on an RP2040
internal pull or firmware setup for this power-on state. Freeze the external
pull-down requirement here, but select its resistance during schematic work
from RP2040 guaranteed drive/leakage, three TMUX1208 input leakages, routing
leakage, and acceptable static current; this proposal has insufficient
evidence for an exact value.

The external Wing-enable pull-downs are separate from the accepted TPS22919
behavior: its own default-off control keeps `HALL_5V` off. After Main enables
and confirms the rail, firmware sets an address, waits the measured
sensor/mux/RC interval, and only then actively asserts one `WING_EN`. Hardware
implementation must prevent or explicitly test the two-enabled state.

## 7. Required test access

Use labeled, scope-probe-accessible pads; use loops only where repeated ground
clips or current insertion justify their area. Pads are not connector pins and
are not indiscriminately added to every net.

### Main

| Proposed label | Signal / measurement enabled |
| --- | --- |
| `TP_M_H5V`, `TP_M_GND` | Load-switch output, startup waveform, source-side rail current/drop reference; ground clip beside power point. |
| `TP_M_MUXA_IN`, `TP_M_MUXB_IN`, `TP_M_MUXC_IN` | Raw analog values after connector and before each divider; compare Wing-side mux output and isolate cable/contact effects. Each gets an adjacent ground pad. |
| `TP_M_ADC0`, `TP_M_ADC1`, `TP_M_ADC2` | Conditioned ADC nodes; clipping, filter settling, noise, and ADC comparison. |
| `TP_M_A0`, `TP_M_A1`, `TP_M_A2` | Address edge timing and worst-code transition correlation. A shared adjacent ground is sufficient for this compact control group. |
| `TP_M_EN0`, `TP_M_EN1` | Bank-enable startup, dead-time, overlap, and transition timing. |
| `TP_SWDIO`, `TP_SWCLK` | Standard SWD programming/debug without occupying Wing signals. |
| `TP_RUN` | Reset/startup triggering and recovery measurement. |
| `TP_BOOTSEL` | Recovery/ROM boot access if the implemented button cannot be probed; omit a duplicate pad only if the accessible button node satisfies this function. |

### Each Wing

| Proposed label | Signal / measurement enabled |
| --- | --- |
| `TP_W_H5V`, `TP_W_GND` | Far-end rail voltage, cable drop, local startup, and stable scope reference. |
| `TP_H_CTR_RAW`, `TP_H_N_RAW`, `TP_H_DIAG_RAW` | Center sensor plus nearest orthogonal and diagonal representative raw outputs for travel/coupling discrimination before the mux. Other raw nodes need not all receive pads. |
| `TP_W_MUXA`, `TP_W_MUXB`, `TP_W_MUXC` | Mux outputs before connector; settling and cable delta. Give each a nearby ground pad. |
| `TP_W_A0`, `TP_W_A1`, `TP_W_A2`, `TP_W_EN` | Optional compact pad row for address/enable propagation and probing; required on the first implemented Wing, depopulatable/omittable on identical later variants only after equivalence is documented. |

Test pads and probe loading must be included in the routing proof and recorded
in measurements. Current must be measured with a purpose-designed Main rail
shunt/header or external USB/HALL_5V instrument—not by cutting a production
trace; its exact implementation is schematic work.

## 8. Measurement acceptance framework

Classification: **A** is a numeric threshold derivable now; **B** is a
reproducible comparative G2 criterion; **C** is characterization for which no
defensible pass limit exists before physical data. Every run records hardware,
firmware, cable, sensors/switches, pitch, supply, temperature, travel, sample
rate, settle delay, and raw data. Use at least three repeated travel cycles on
at least three sensor/switch positions per pitch; retain individual results,
not only averages.

| Topic | Class | Proposed rule / derivation |
| --- | --- | --- |
| ADC clipping/headroom | **A** | No sample may violate RP2040 ADC recommended input range `0 <= V_ADC <= IOVDD`; with accepted nominal maximum USB 5.25 V and divider `10/(6.8+10)=0.595238`, the rail-derived upper input is `3.125 V`, leaving `3.3-3.125=0.175 V` nominal headroom. Verify actual resistor/rail extremes before schematic release; physical extrema and transient overshoot must remain within the device recommended range. Also report G2 usable span comparatively. [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) |
| Noise | **B** | At fixed travel and identical acquisition settings, report robust peak-to-peak, standard deviation, and percentile bands for raw Hall, mux input, and ADC. G2 rejects a pitch/architecture only through reduced calibrated actuation separation or statistically worse noise against the best viable pitch; no unsupported mV limit is invented. |
| Repeatability | **B** | Blind repeated up/down cycles; compare endpoint and chosen actuation-position distributions and hysteresis using identical fixture settings. Prefer the mechanically viable candidate with tighter normalized distributions; preserve raw cycles and confidence intervals. |
| Adjacent-key magnetic interference | **B** | Hold target travel fixed; sweep each orthogonal/diagonal neighbor alone and in worst simultaneous combinations. Normalize target shift to its own full-travel span. G2 chooses only among mechanically viable pitches whose measured interference preserves separability/calibration margin; report absolute and normalized shifts rather than inventing a percentage. |
| Settling time | **C** | For address and bank transitions, sweep delay logarithmically then around the knee; measure error relative to a long-delay reference at Wing mux and ADC node. No pre-data error band is justified. |
| Usable sampling delay | **B** | From settling data, choose the shortest delay whose distribution is statistically indistinguishable, under a predeclared test, from the long-delay reference for every tested worst transition and channel. Record first-sample discard policy. |
| Scan-speed implication | **A + C** | Architecture requires `2 banks x 7 addresses = 14` slots per full 42-key scan. Derived scan time is the measured per-slot acquisition time times 14 plus bank overhead; publish rate and latency. No minimum scan-rate requirement has accepted provenance, so adequacy remains G2 characterization/user evaluation. |
| `HALL_5V` voltage drop | **A + C** | At the Wing, remain within the common DRV5055/TMUX recommended supply intersection, **4.5–5.5 V**. Separately characterize `V_Main - V_Wing` at steady/startup and compare to the revised 6.35 mV contact-only calculation; cable and PCB are additional. |
| Hall rail current | **A + C** | A production-like Wing must not exceed the proposed 127 mA connector design-current estimate and must remain below the 1 A contact rating. Measure steady and peak current; the estimate is not a final USB/load-switch/full-product power disposition. |
| Startup behavior | **A + C** | The two external Main pull-downs must hold both `WING_EN` signals low throughout MCU reset/high impedance and until firmware has confirmed `HALL_5V` is in the 4.5–5.5 V operating range; no ADC pin may exceed its recommended range. Characterize rise time, inrush, Hall output recovery, first-valid-sample time, reset/brownout, and repeated starts. |
| Short-term thermal drift | **B** | At fixed travel, log rail, raw output, ADC value, board/ambient temperature, and time from cold start under identical power. Compare normalized drift and stabilization across candidates; no temperature/time limit has accepted provenance. |

The nominal 175 mV headroom is not a tolerance proof and therefore cannot by
itself close clipping. G1 schematic review must perform worst-case resistor,
supply, sensor-output, and ADC-limit analysis; G2 validates the physical path.

## 9. Geometry source boundary

Authoritative forward geometry may come only from project-owned native
tscircuit/project-owned parameterized geometry and approved manufacturer
datasheet/CAD geometry. Verified historical KiCad geometry, frozen historical
layout evidence, and previously accepted fixtures are secondary references.

`hardware/layout/**`, old KiCad placement/routing, and converter output without
a dedicated fidelity qualification are **not automatically authoritative** and
must not be consumed as forward geometry. [Issue #58](https://github.com/ihsinoky/he-piantor-42/issues/58) /
[PR #59](https://github.com/ihsinoky/he-piantor-42/pull/59)'s EDA-003A report
classifies the observed importer result as **`UPSTREAM_FIX_CANDIDATE`**: current
importer reuse is not approved for he-piantor-42, native TSX remains the
forward geometry path, and existing KiCad assets remain secondary/reference
evidence. Importer work remains non-blocking to G0B; future importer reuse
requires a separately accepted fidelity result after upstream fixes.

The available checkout has no configured Git remote, so PR #59's final merge
state could not be independently fetched. The paragraph above records the
candidate result reported by PR #59 and does not elevate it to an accepted
decision in this proposal. If that PR is confirmed merged, its merged EDA-003A
report—not this summary—is the accepted evidence. Any reused item still needs
explicit provenance and fidelity acceptance in its own scope.

## 10. DFM disposition

The proposal retains two copper layers, 1.2 mm finished PCB, SMD on one side
preferred, JLCPCB Economic PCBA preferred where practical, and Basic then
Promotional Extended part preference. Electrical/magnetic performance takes
priority over supplier class. The 100 x 100 mm area remains an optimization;
separate Main and Wing manufacture/order is allowed. Connector hand assembly
uses a purchased/precrimped harness where possible; hand-crimping loose GH
contacts is not treated as casual assembly.

Actual service eligibility, stock, BOM classification, footprint, assembly
orientation, cable availability, and quote remain G1/pre-order checks.

**USB NPTH: OPEN — PRE-ORDER DFM REVIEW REQUIRED.** No production exception is
granted, and this proposal authorizes no order.

## 11. Unresolved evidence gaps

1. PO/PMO acceptance of every proposed freeze value in this document.
2. JST GH mating-cycle rating was not specified in the consulted manufacturer
   catalogue; housing/contact current stock, precrimped cable availability,
   and JLCPCB assembly class remain unverified.
3. Manufacturer CAD/native footprint transcription and independent dimensional
   review have not occurred.
4. Actual cable resistance, crosstalk, crimp quality, and maximum Rev.A length
   need implementation and measurement.
5. Hall sensor choice, physical current/inrush, full USB power disposition,
   divider/filter tolerance analysis, noise, settling, interference, thermal
   drift, pitch, and final sampling timing await G1 hardware and EVT-002/G2.
6. Magnetic exclusion distance for full-load sites and whether those sites fit
   cleanly on one pitch Wing require physical-layout review; fallback is the
   separate fourth electrical-load Wing defined above.
7. Final 21-key geometry, whole-Wing coupling, cable restraint, production
   footprint availability, and Main unchanged-reuse suitability remain later
   Rev.A gates.

## 12. Post-G0B routing-proof boundary (next gate; not performed here)

Only after PO acceptance, implement a representative stock-tscircuit physical
and two-layer routing proof. Main subset: RP2040, USB-C/ESD, QSPI flash,
crystal, 3V3, switched `HALL_5V`, three ADC divider/filter paths, and the actual
14-pin JST GH connector. Wing subset: actual connector, three-output-relevant
TMUX1208 circuitry, and representative Hall load. Exercise the test access and
100 mm interconnect assumptions where physical representation applies.

That proof separately decides whether the pinned, unmodified stock tscircuit
physical workflow can complete representative two-layer routing. It is not an
automatic G0B consequence, is not performed in Issue #57, and must not update
the tscircuit dependency, fork tscircuit, modify JITX, or import a full KiCad
board.

## 13. Requested Human Gate disposition

PMO should review source accuracy, pinout, connector mechanics, coverage, and
open gaps, then make a recommendation. The Product Owner—not this document—may
accept, reject, or request changes. Until that recorded decision, **G0B remains
not-ready, EVT-002 remains locked, and physical implementation must not begin**.
