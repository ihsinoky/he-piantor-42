# HE Piantor 42

42-key one-piece Hall-effect keyboard derived from the Beekeeb Piantor layout.

## Target

- 42 keys
- Piantor-derived column-staggered layout
- One-piece reverse-V geometry
- 17.0 mm key pitch target
- Full-height Hall-effect magnetic switches
- USB-C wired only
- Vial-compatible keymap, 4 layers
- Dedicated power indicator LED
- Separate layer indicator LED
- JLCPCB PCBA target
- FDM-printable enclosure

## Development flow

1. Freeze switch / keycap / geometry requirements
2. Design and manufacture a small Hall-sensor evaluation PCB
3. Measure sensor range, noise and travel curve
4. Finalize the 42-key PCB
5. Implement Vial + Hall-effect firmware
6. Finalize enclosure
7. Generate JLCPCB and 3D-print manufacturing packages
8. Bring-up and validation

Project status is tracked in `task/index.html`.
