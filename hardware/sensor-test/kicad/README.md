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

## Scope

This milestone stops at an ERC-clean integrated schematic. PCB placement,
routing, Gerbers and assembly outputs are intentionally deferred. Do not order
boards from this directory yet.
