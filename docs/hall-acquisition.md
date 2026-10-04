# Hall acquisition architecture

Status: provisional acquisition baseline, to be proven on physical Rev.M1 Main + Evaluation Wing(s) under D-015.

## 1. Switch reference

Gateron Magnetic Jade Pro HE is the current full-height switch baseline.

Published magnetic flux at 1.2 mm PCB:
- top position: 120 +/- 8 G = approximately 12 mT
- bottom position: 700 +/- 30 G = approximately 70 mT

Both physical Rev.M1 and Rev.A therefore use 1.2 mm board thickness as the baseline.

## 2. Hall sensor candidates

### Candidate A - TI DRV5055A3QDBZR

- LCSC: C266128
- Package: SOT-23
- Supply: 3.0-3.63 V or 4.5-5.5 V
- Bipolar ratiometric analog output centered around VCC/2
- Nominal sensitivity at 5 V: 25 mV/mT
- Field range: approximately +/-85 mT
- Bandwidth: 20 kHz
- Magnet temperature compensation
- Known pinout for SOT-23: pin 1 VCC, pin 2 OUT, pin 3 GND

Reason to keep it as the reference:
- strong documentation,
- magnetic range covers the nominal Jade Pro bottom field,
- sensitivity gives a large useful voltage span,
- current LCSC availability.

### Candidate B - Slkor SL3102-3

- LCSC: C50087579
- Package: SOT-23
- Supply: 3.0-5.5 V
- Bipolar ratiometric VDD/2 analog output
- Field range: +/-90 mT
- Sensitivity: 1.65 mV/G at 3.3 V; 2.5 mV/G at 5 V
- Supply current: 4.5 mA at 3.3 V; 5.4 mA at 5 V
- Bandwidth: 30 kHz

Reason to evaluate:
- magnetic range and 5 V sensitivity are close to the TI A3 reference,
- lower stated current and lower component cost,
- but its documentation and long-term field history are weaker than TI.

The Rev.M1 Evaluation Wing experiments shall not make the production sensor decision by assumption. It shall produce comparable travel curves and noise measurements.

## 3. Sensor power rail

### Decision

Run the Hall sensors and analog multiplexers from a switched USB VBUS rail, named HALL_5V.

Power path:

USB VBUS
-> TPS22919DCKR load switch
-> HALL_5V
-> Hall sensors + TMUX1208 multiplexers

The RP2040 and its 3.3 V logic remain on the separate 3V3 rail.

### Reason

Forty-two always-powered linear Hall sensors are a meaningful load. Supplying them from a 3.3 V LDO would waste power and heat the regulator. Supplying the analog section from the 5 V USB rail avoids that regulator loss.

The TPS22919 load switch is controlled by an RP2040 GPIO. It defaults off through its internal pull-down behavior, allowing firmware to keep the Hall bank off during early USB startup and fault handling.

## 4. Rev.A Wing multiplexing baseline

### Device

TI TMUX1208PWR / LCSC C494728.

Important properties for this design:
- 8:1 single-ended analog multiplexer
- 1.08-5.5 V supply
- 5 ohm typical on-resistance
- 1.8 V compatible digital logic while the analog device is operated at 5 V
- active-high EN
- three address inputs A0..A2

This avoids the logic-level ambiguity that would occur with a conventional 5 V 74HC4067 driven directly from 3.3 V RP2040 GPIO.

### Topology

Use six TMUX1208 devices arranged as two banks of three: Left and Right
21-key Wings each carry three TMUX1208. Main retains three ADC paths.

Each mux handles seven Hall sensors.

- Bank 0: MUX0A, MUX0B, MUX0C = 21 keys
- Bank 1: MUX1A, MUX1B, MUX1C = 21 keys

Shared signals:
- MUX_A0
- MUX_A1
- MUX_A2

Bank enables:
- MUX_EN0 enables all three Bank 0 muxes
- MUX_EN1 enables all three Bank 1 muxes

Outputs:
- group A -> ADC0 / GPIO26
- group B -> ADC1 / GPIO27
- group C -> ADC2 / GPIO28

Only one bank is enabled at a time.

Seven address positions per bank cover 42 keys:
2 banks x 7 selections x 3 ADC channels = 42 key samples.

The eighth TMUX input remains unused and is tied to no signal.

## 5. ADC level scaling

HALL_5V analog outputs can approach the 5 V rail, but RP2040 ADC pins must remain within the 3.3 V domain.

Each mux output therefore uses a passive divider before the ADC:

- R_TOP = 6.8 kOhm from mux output to ADC node
- R_BOTTOM = 10 kOhm from ADC node to GND
- scale factor = 10 / (6.8 + 10) = approximately 0.595

At the USB upper nominal region around 5.25 V, the divided voltage is approximately 3.125 V, below 3.3 V.

A small capacitor at each ADC node is included as an anti-noise / charge-settling element:
- C_ADC = 1 nF baseline

The effective source resistance of the divider is approximately 4 kOhm, giving an RC time constant of roughly 4 us with 1 nF. Firmware will use a conservative settle delay initially and then reduce it after measurement.

## 6. Expected signal span with Jade Pro + DRV5055A3

At 5.0 V the DRV5055A3 quiescent output is approximately 2.5 V.

With the published Jade Pro field moving nominally from approximately 12 mT to 70 mT and the A3 sensitivity at 25 mV/mT, the expected undivided output excursion for the increasing-polarity orientation is approximately:

- top: 2.5 + 0.025 * 12 = 2.80 V
- bottom: 2.5 + 0.025 * 70 = 4.25 V

After the 0.595 divider:
- top: approximately 1.67 V
- bottom: approximately 2.53 V

Expected travel span: approximately 0.86 V at the ADC, before tolerance and geometry effects.

The opposite magnet polarity produces a decreasing voltage rather than an increasing one. Firmware calibration must therefore derive direction from measured endpoints rather than assume polarity.

## 7. Physical Rev.M1 Main / Evaluation Wing architecture

D-015 replaces the manufactured one-piece RP2040 + four-key board assumption.
The frozen four-key fixture and `hardware/sensor-test/design.md` / `pinmap.csv`
remain unchanged historical qualification inputs, not the new product design.

```text
Main: USB-C / protection -> RP2040 + 3V3 + debug
      USB VBUS -> switched HALL_5V -> Wing
Wing: Hall positions -> TMUX1208 -> representative connector/interconnect
Main: 6.8k / 10k divider + 1 nF -> ADC0/1/2
```

Main owns power generation, address/bank control, all ADC dividers/filters,
ADC and RP2040/USB. Wing owns Hall sensors, TMUX and switch pitch geometry.
Evaluate 17.0 / 16.5 / 16.0 mm; production pitch remains open. The interface
must support Rev.A's three-output Wings even if the first Wing uses fewer
channels. Exact connector and test-Wing channel structure are TBD at G0B.

Test access must cover VBUS, 3V3, HALL_5V and GND at both boards, raw Hall
outputs, MUX outputs across the interconnect, filtered ADC nodes, address and
enable, SWDIO/SWCLK, BOOTSEL and RUN/reset. Evaluate travel/polarity/range,
noise/repeatability, magnetic coupling, rail current/startup and thermal drift,
plus settling, source/address changes and connector/cross-channel effects on
the actual Hall -> TMUX -> Wing connector -> Main divider/filter -> ADC path.
See [logical interface](../hardware/rev-m1/main-wing-interface.md) and
[evaluation plan](../hardware/rev-m1/evaluation-plan.md). Divider/filter values
above remain provisional; no circuit or connector implementation occurs here.

## 8. Sensor comparison plan

The reference assembly shall use DRV5055A3 sensors because its pinout and transfer behavior are fully documented.

A second assembly variant may substitute SL3102-3 after its exact package pin assignment is checked against the production footprint. Do not place a different SOT-23 sensor merely because the package outline matches: pin order and magnetic sensing direction must also match.

## 9. Power budget gate

Before releasing the 42-key PCB:
- measure actual sensor current at 5 V,
- extrapolate worst-case 42-key current,
- include MCU, flash, LEDs, muxes and regulator losses,
- confirm operation under default USB current assumptions,
- confirm Hall rail turn-on does not cause an unacceptable transient.

If the candidate sensor makes the full board power margin poor, the fallback order is:
1. select a lower-current Hall sensor proven by the evaluation PCB,
2. split HALL_5V into independently switched banks,
3. only then consider a more complex scan-time sensor power scheme.

## 10. Status

The previous 3 x 74HC4067 architecture is superseded by the 6 x TMUX1208 two-bank architecture because TMUX1208 explicitly accepts low-voltage digital control while operating from the 5 V analog rail.
