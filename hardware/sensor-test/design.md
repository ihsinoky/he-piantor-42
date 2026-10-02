# Sensor-test board electrical design

Status: M1 native electrical-model implementation under review; placement, routing, DRC, and first-board measurement remain pending.

## Purpose

This board is not a generic macropad. It exists to de-risk the production HE Piantor 42 board.

It must answer:
1. Does the selected full-height Gateron magnetic switch produce a usable analog curve with the candidate Hall sensor?
2. Is the TMUX1208 multiplexed path quiet and fast enough?
3. What ADC settling time is needed after a mux address change?
4. What per-key calibration model is sufficient?
5. What current does the Hall rail actually draw?

## PCB stack

- The evaluation board and current production baseline use 2 copper layers.
- Board thickness is fixed at 1.2 mm because switch-to-sensor distance is part of the measurement.
- Production board thickness is also 1.2 mm. A layer-count change requires a separate decision and Human Gate.

## Functional blocks

### USB-C device port

Connector: HRO TYPE-C-31-M-12, LCSC C165948.

USB 2.0 only:
- A6/B6 joined as USB_D+
- A7/B7 joined as USB_D-
- CC1 -> 5.1 kOhm -> GND
- CC2 -> 5.1 kOhm -> GND
- VBUS -> 5V input rail
- shell -> chassis/ground strategy to be finalized in PCB layout

RP2040 USB pins use the 27 ohm series termination required by the RP2040 hardware guide, placed close to the MCU.

- USB shell grounding strategy remains a layout/G1 design decision; the native electrical model exposes `USB_SHIELD` without selecting direct, RC, or chassis coupling.

### MCU core

MCU: Raspberry Pi RP2040, LCSC C2040.

The MCU core follows Raspberry Pi's minimal hardware design:
- 3.3 V I/O rail
- internal 1.1 V core regulator wiring and decoupling
- external QSPI flash
- 12 MHz crystal
- USB D+/D- with 27 ohm series resistors
- RUN reset access
- BOOTSEL access
- SWD test pads

Crystal:
- Abracon ABM8-272-T3
- 12 MHz, 10 pF load, 50 ohm max ESR
- 15 pF load capacitor each side
- 1 kOhm series resistor on the XOUT side
- crystal loop kept very short

Flash baseline:
- Winbond W25Q16JVUXIQ, 16 Mbit, 2 x 3 mm USON-8
- 3.3 V

### 3.3 V logic regulator

Baseline: Diodes AP2112K-3.3TRG1, LCSC C51118.

This rail powers the RP2040 core and low-voltage indicators only. Hall sensors are not powered by the LDO.

Required local capacitors follow the regulator and RP2040 reference requirements.

### Hall power switching

Load switch: TI TPS22919DCKR, LCSC C2149796.

- IN = USB VBUS
- OUT = HALL_5V
- ON = GPIO7 / HALL_PWR_EN
- default state = OFF until firmware enables the rail
- input and output decoupling close to the device
- HALL_5V has a dedicated test point

### Hall sensor positions

Four magnetic switch positions at 17.0 mm pitch.

Reference Hall sensor: TI DRV5055A3QDBZR / C266128.

Each sensor:
- pin 1 VCC -> HALL_5V
- pin 2 OUT -> Hx_RAW -> TMUX input
- pin 3 GND -> GND
- local 100 nF decoupling from VCC to GND
- raw-output test point

The magnetic-switch footprint is based on the vendored marbastlib HE footprint and places the SOT-23 sensor beneath the magnet axis.

### Analog multiplexer

U_MUX = TI TMUX1208PWR / C494728, powered from HALL_5V.

Connections:
- pin 1 A0 -> GPIO2 / MUX_A0
- pin 2 EN -> GPIO5 / MUX_EN0
- pin 3 NC -> no connect
- pin 4 S1 -> H0_RAW
- pin 5 S2 -> H1_RAW
- pin 6 S3 -> H2_RAW
- pin 7 S4 -> H3_RAW
- pin 8 D -> MUX_D
- pin 9 S8 -> spare test pad
- pin 10 S7 -> spare test pad
- pin 11 S6 -> spare test pad
- pin 12 S5 -> spare test pad
- pin 13 VDD -> HALL_5V
- pin 14 GND -> GND
- pin 15 A2 -> GPIO4 / MUX_A2
- pin 16 A1 -> GPIO3 / MUX_A1

Use at least 100 nF local VDD decoupling.

### ADC interface

MUX_D -> 6.8 kOhm -> ADC_SENSE
ADC_SENSE -> 10 kOhm -> GND
ADC_SENSE -> 1 nF -> GND
ADC_SENSE -> RP2040 GPIO26 / ADC0

Test points:
- MUX_D
- ADC_SENSE

The divider allows the mux and Hall sensors to run from the 5 V rail without exceeding the RP2040 ADC range.

### Indicators

Power indicator:
- driven directly from 3V3, not from an MCU GPIO
- green LED baseline
- target LED current approximately 1 mA
- purpose: show that logic power exists even if firmware does not run

Evaluation status indicator:
- separate MCU-controlled LED
- not the final layer RGB LED
- used by bring-up firmware for error/status signaling

The final production board will use a separate RGB layer indicator.

## RP2040 GPIO allocation

See `pinmap.csv`.

Reserved production-compatible pins are allocated now so the evaluation firmware can be reused later.

## Grounding / layout constraints

1. Use a continuous ground reference under the MCU/USB/analog area.
2. Keep USB D+/D- short, coupled and away from Hall analog lines.
3. Keep crystal traces extremely short and isolated.
4. Keep the Hall sensor directly under the switch magnet using the known HE footprint.
5. Keep HALL_5V switching currents away from ADC_SENSE.
6. Route raw Hall outputs away from USB and crystal.
7. Place divider/filter parts adjacent to the RP2040 ADC pin.
8. Include generous labeled test pads; this board is an instrumented prototype.
9. Avoid ferromagnetic fasteners immediately below a Hall sensor.

## Native electrical source and footprint provenance

The canonical electrical source is
`hardware/tscircuit/src/evaluation/m1-four-key.tsx`. Its stock footprinter
package descriptions follow the package land-pattern dimensions in the
respective RP2040, Winbond W25Q16JV, Diodes AP2112, TI TPS22919, TI TMUX1208,
Abracon ABM8-272-T3, and passive manufacturer data. The HRO
TYPE-C-31-M-12 native primitive is transcribed from the manufacturer's
recommended PCB layout; repository verification fixes its 12 physical contact
lands (including the paired VBUS/GND contacts), four plated shell stakes, and
two locating NPTHs. It is not converted from a KiCad footprint.

Because stock tscircuit net selectors cannot begin with a digit, the generated
source-net identifiers `V3V3` and `V1V1` mean the schematic rails **3V3** and
**1V1**, respectively. This spelling accommodation does not change either
rail's electrical identity.

**DESIGN DATA GAP:** supplier part numbers remain unapproved for passives,
LEDs, buttons, and test points. No supplier identities are invented here.

## Initial firmware measurement sequence

1. Boot with HALL_PWR_EN low.
2. Complete USB initialization.
3. Drive HALL_PWR_EN high.
4. Wait for Hall rail and sensor outputs to settle.
5. Set MUX_EN0 high.
6. For each MUX address 0..3:
   - set A2..A0,
   - wait conservative 20 us,
   - take multiple ADC readings,
   - discard the first sample after switching,
   - average / log remaining samples.
7. Stream timestamp, key index, raw ADC and normalized value over USB serial/HID diagnostic endpoint.

The settle delay and number of samples are measurement parameters, not fixed product constants.
