# Sensor-test KiCad work area

Branch: `feature/sensor-test-electrical-baseline`

This directory contains the first reviewable electrical baseline for the four-key Hall sensor evaluation board.

## Current project work in this PR

These standalone sheets are project-owned and checked by KiCad ERC:

- `usb-power.kicad_sch` — USB-C sink, USB ESD, 3.3 V regulator and power indicator.
- `hall-front-end.kicad_sch` — switched HALL_5V, four Hall sensors, TMUX1208, ADC divider/filter and measurement test pads.

The following file is retained as an **ERC-clean RP2040 engineering reference**, not yet the final integrated board schematic:

- `he-piantor-sensor-test.kicad_sch`

It is derived from the BSD-3-Clause RP2040 minimal design reference and remains intentionally separate so the project does not mutate the known-good core while the USB/Hall blocks are still being integrated.

## Deliberately deferred

The next electrical-integration PR will:
1. create the project-owned RP2040 core,
2. connect USB/power and Hall blocks to it,
3. add BOOTSEL, RUN/reset, SWD and status LED,
4. reconcile final reference designators against the BOM,
5. leave a single integrated ERC-clean evaluation-board schematic.

PCB placement/routing and the 1.2 mm manufacturing package will be a later PR.

Do not generate manufacturing Gerbers from this directory yet.
