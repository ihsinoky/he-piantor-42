# HE Piantor 42 - System Specification

Status: Draft / Requirements phase
Updated: 2026-09-25

## 1. Product concept

A 42-key one-piece Hall-effect keyboard derived from the Beekeeb Piantor layout.

The left and right key fields are joined into one PCB and arranged in a reverse-V shape. The current geometric interpretation is an internal angle of 120 degrees, equivalent to rotating the left and right key fields approximately -30 and +30 degrees from horizontal.

## 2. Fixed user requirements

- 42 keys.
- Piantor-derived column stagger and thumb cluster.
- One-piece keyboard; not a split keyboard.
- Target key pitch: 17.0 mm.
- Full-height Hall-effect magnetic switches; low-profile switches are not desired.
- Wired USB only.
- Vial-compatible keymap.
- Four planned layers.
- Layer indicator LED.
- Separate power indicator LED.
- PCB assembly by JLCPCB is preferred.
- Enclosure is intended for a home FDM 3D printer. External manufacturing is a fallback.

## 3. Provisional component direction

### 3.1 Magnetic switch

Primary candidate: Gateron Magnetic Jade Pro HE, KS-20 compatible.

Reasons for selecting it as the current baseline:

- Full-height magnetic switch.
- MX-style keycap stem.
- Widely used KS-20 magnetic ecosystem.
- Manufacturer publishes magnetic-flux values at 1.2 mm PCB thickness.
- Nominal initial force 36 +/- 5 gf.
- Total travel 3.5 +/- 0.1 mm.
- Initial magnetic flux 120 +/- 8 Gs at 1.2 mm PCB.
- Bottom-out magnetic flux 700 +/- 30 Gs at 1.2 mm PCB.
- More than 100 million rated keystrokes.
- Current Japanese retail channels exist.

This remains provisional until the Hall sensor and switch-to-sensor geometry are validated on the evaluation PCB.

### 3.2 Keycaps

A normal approximately 18 mm wide MX keycap cannot be used at 17.0 mm pitch without interference.

Current baseline:
- 16.5 x 16.5 mm keycap.
- MX-style cross stem.
- Nominal gap at 17.0 mm pitch: 0.5 mm.

Beekeeb / Tai-Hao MT165-MX is the current reference part because it is explicitly 16.5 x 16.5 mm and supports an MX-style stem. Physical fit with the selected Hall-effect switch will still be checked before committing the main PCB.

## 4. Electrical architecture - provisional

The keyboard shall use analog Hall-effect sensing rather than a conventional switch matrix.

Planned functional blocks:

USB-C
-> ESD / protection
-> 3.3 V power
-> MCU
-> Hall-sensor acquisition
-> 42 Hall sensors

The exact Hall sensor, analog multiplexer, and ADC topology are not frozen yet. They will be chosen with the following priorities:

1. Adequate magnetic range with the selected switch.
2. Stable analog readings with enough margin for calibration.
3. Sufficient scan rate for 42 keys.
4. Low noise.
5. Reasonable current consumption.
6. Parts that can be assembled by JLCPCB without exceptional sourcing cost.

### Power indicator

A dedicated power LED shall be connected to the regulated supply and shall not depend on firmware. Its purpose is to confirm that the board is powered even if the MCU or firmware does not start.

### Layer indicator

A separate firmware-controlled RGB LED is the baseline. Four layers will be distinguishable by color or by off/color combinations.

## 5. Firmware

Vial will be used for ordinary keyboard configuration such as keymap, layers, macros, and related QMK/Vial functions.

Hall-effect-specific configuration, including adjustable actuation or Rapid Trigger, may require a separate implementation or configuration path. These features are not a blocker for the first hardware revision.

The first firmware milestones are:

1. Raw Hall sensor acquisition.
2. Per-key calibration.
3. Reliable key press/release detection.
4. Vial keymap support.
5. Layer indicator.
6. Optional advanced Hall-effect behavior after measurement.

## 6. Mechanical architecture

The main PCB will also define the switch locations and the one-piece reverse-V geometry.

The enclosure will be parameterized and generated as STEP and STL. The first design target is FDM printing.

Mechanical design shall account for:

- The narrow center region of a one-piece reverse-V PCB.
- Torsional stiffness.
- USB-C connector opening.
- Component clearance below the PCB.
- Accessible fasteners.
- No ferromagnetic parts close enough to Hall sensors to materially change measurements.

## 7. Development sequence

1. Freeze magnetic switch and narrow keycap candidates.
2. Extract Piantor key-center geometry.
3. Select Hall sensor and acquisition architecture.
4. Design a small Hall-effect evaluation PCB.
5. Manufacture and measure it.
6. Freeze sensor range and calibration method.
7. Design the 42-key main PCB.
8. Implement Vial and Hall firmware.
9. Design enclosure.
10. Generate JLCPCB and 3D-print packages.
11. Bring-up, validate, revise if necessary.

## 8. Validation gates

### Gate 1 - Requirements freeze

Required:
- Switch selected.
- Keycap fit judged acceptable.
- 17.0 mm pitch retained or intentionally changed.
- 120-degree geometry definition confirmed.
- Hall sensor candidate selected.

### Gate 2 - Sensor evaluation

Required:
- No saturation over useful travel.
- Adequate signal change from top to bottom.
- Repeatable readings.
- Noise small enough for desired actuation resolution.
- Scan architecture proven.

### Gate 3 - Main PCB release

Required:
- Schematic review complete.
- ERC/DRC clean or documented exceptions.
- Mechanical fit reviewed.
- JLCPCB BOM/CPL generated.
- Firmware can bring up USB and read all channels.

## 9. Open design questions

- Final Hall sensor part.
- Final analog multiplexer / ADC architecture.
- Exact Piantor-to-17-mm coordinate transformation.
- Exact center gap and wrist/hand spacing.
- Whether a switch plate is required or PCB mounting alone is sufficient.
- Whether advanced Rapid Trigger settings are required for v1.0.
