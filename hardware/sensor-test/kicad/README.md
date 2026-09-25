# Sensor-test KiCad work area

Branch: `design/sensor-test-v0`

This directory contains an **openable KiCad work base**, derived from the BSD-3-Clause RP2040 minimal design by Raspberry Pi / Tommy Gilligan.

It is intentionally marked **WIP** and is **not manufacturing-ready**.

Current contents:
- RP2040 core schematic copied as the working root sheet.
- Required local footprint and symbol libraries.
- License retained.

Next modifications on this branch:
1. Replace the old connector/power assumptions with the project USB-C power tree.
2. Update crystal network to the current RP2040 recommendation.
3. Add TPS22919 Hall 5 V load switch.
4. Add one TMUX1208.
5. Add four Gateron Magnetic Jade / DRV5055A3 sensor positions.
6. Add 5 V-to-ADC divider/filter.
7. Add independent power LED, status LED, BOOTSEL, RESET, and test points.
8. Run KiCad ERC in GitHub Actions.
9. Only after ERC passes, start the evaluation PCB layout.

Do not generate Gerbers from this WIP directory until the evaluation-board release checklist explicitly says it is allowed.
