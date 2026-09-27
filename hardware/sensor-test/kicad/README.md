# Sensor-test KiCad project

This directory contains the electrical design for the four-key Hall evaluation board.

## Integrated design

`integrated-sensor-test.kicad_sch` is the review and PCB-source schematic. It combines:

- the RP2040 core, flash, crystal, BOOTSEL, RUN/reset and SWD access from the
  Raspberry Pi minimal-design baseline;
- the USB-C sink, USB ESD, 3.3 V regulator and always-on power indicator;
- switched `HALL_5V`, four DRV5055 sensors, TMUX1208, and the protected
  `ADC_SENSE` input; and
- a GPIO11 evaluation-status LED. The production layer RGB LED (`GPIO8`–`GPIO10`)
  remains reserved and is deliberately not fitted on this evaluation board.

The Hall control nets are connected directly at the RP2040 pins rather than via
an external-controller placeholder: GPIO2=`MUX_A0`, GPIO3=`MUX_A1`,
GPIO4=`MUX_A2`, GPIO5=`MUX_EN0`, GPIO7=`HALL_PWR_EN`, and GPIO26/ADC0=`ADC_SENSE`.

The three older schematics remain as traceable source blocks and standalone ERC
fixtures. Do not use them independently as the PCB source.

## Evaluation PCB

`integrated-sensor-test.kicad_pcb` is the routed PCB derived from the integrated
schematic. It uses four copper layers and a 1.2 mm finished thickness. `In1.Cu`
is the continuous ground reference; `F.Cu`, `In2.Cu`, and `B.Cu` carry local
signals and power distribution.

The board outline is 110 mm x 75 mm. The combined Hall/switch footprints are at
(36, 31), (53, 31), (36, 48), and (53, 48) mm, giving an exact 17.0 mm pitch in
both axes. The USB connector is on the right board edge. The RP2040, flash,
crystal, and their local support parts form the digital core to the right of the
Hall array, while the TMUX1208 is between the array and the ADC input network.
Probe pads are arranged along the unobstructed top and bottom edges so that
they remain accessible with switches and keycaps installed.

This directory intentionally contains no Gerber, drill, BOM, CPL, or other
manufacturing package. Manufacturing output and the G1 review are the next
increment; do not order boards from this directory yet.
