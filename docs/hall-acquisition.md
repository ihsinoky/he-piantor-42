# Hall acquisition architecture

Status: provisional, to be proven on sensor-test PCB.

## Switch reference

Gateron Magnetic Jade Pro HE is the current full-height switch baseline.

Published magnetic flux at 1.2 mm PCB:
- top position: 120 +/- 8 G = approximately 12 mT
- bottom position: 700 +/- 30 G = approximately 70 mT

The production PCB and sensor-test PCB therefore use 1.2 mm PCB thickness as the baseline.

## Sensor candidates for the evaluation board

### Candidate A - TI DRV5055A3QDBZR

- LCSC: C266128
- SOT-23.
- 3.3 V or 5 V supply.
- Bipolar, ratiometric analog output centered around VCC/2.
- Nominal 25 mV/mT at 5 V.
- Nominal field range approximately +/-85 mT.
- 20 kHz sensor bandwidth.
- Magnet temperature compensation.
- Current is materially higher than a simple digital key matrix; the full 42-key power budget must include all sensors.

Why evaluate it:
- well documented,
- current LCSC stock,
- range is close to but above the nominal Jade Pro bottom field,
- good reference device for validating cheaper alternatives.

### Candidate B - Slkor SL3102-3

- LCSC: C50087579.
- SOT-23.
- 3.0 V to 5.5 V supply.
- Bipolar, ratiometric VDD/2 analog output.
- +/-90 mT field range.
- 4.5 mA stated supply current at 3.3 V.
- 30 kHz stated bandwidth.
- Lower component cost than the TI part.

Why evaluate it:
- range is appropriate for the nominal Jade Pro flux,
- lower stated current and cost,
- current LCSC availability,
- but documentation and field history are weaker than TI, so it must not be selected solely on price.

## Main-board multiplexing baseline

Use three 16:1 analog multiplexers, one feeding each of three RP2040 ADC-capable GPIO inputs.

Baseline mux: Nexperia 74HC4067PW,118 / LCSC C179326.

The four address lines are shared among all three muxes.

Mapping concept:

- MUX-A: 14 Hall sensors -> ADC0
- MUX-B: 14 Hall sensors -> ADC1
- MUX-C: 14 Hall sensors -> ADC2
- S0..S3 shared
- two mux positions remain unused on each device

One address step therefore exposes three keys. Fourteen address values cover all 42 keys.

## Evaluation-board architecture

The sensor-test board shall deliberately include a 16:1 mux even though it has only four switches. This validates the real analog path, not merely the Hall sensor.

Planned chain:

Hall sensor -> 74HC4067 -> RP2040 ADC

The PCB shall provide:
- four switch positions,
- two positions populated with the TI sensor and two with the Slkor sensor, or equivalent selectable population,
- test points for each raw Hall output,
- test point for mux output,
- 3.3 V and GND test points,
- USB-C,
- independent power LED,
- firmware-controlled status LED,
- boot/reset access.

## Power note

Continuous Hall sensors consume far more power than ordinary switch contacts.

Before the main PCB is frozen, measure actual board current with all sensors powered. If the resulting 3.3 V load creates excessive regulator dissipation or USB-attach current, evaluate:
- a more efficient 3.3 V buck regulator,
- sensor-bank power gating,
- or a lower-current Hall sensor.

The evaluation board is explicitly intended to answer this before committing 42 channels.
