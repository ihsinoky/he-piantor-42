# HE Piantor 42 - System Specification

Status: Engineering / sensor-evaluation design
Updated: 2026-10-04 (D-015 architecture disposition)

D-015 rebaselines physical Rev.M1 as reusable Main + Evaluation Wing(s) and
Rev.A as accepted Main + Left/Right 21-key Wings. The historical one-PCB
implementation and fixed 17.0 mm pitch below are superseded/reopened; prior
geometry/keycap rationale remains evidence. Production pitch is selected at G2
after 17.0 / 16.5 / 16.0 mm experiments. See the authoritative
[project gates](project-status.md#human-gates) and
[physical architecture](../hardware/rev-m1/architecture.md). The frozen four-key
fixture remains separate; no physical hardware is implemented in C4A.

## 1. Product concept

A 42-key one-piece Hall-effect keyboard derived from the Beekeeb Piantor layout.

Historical implementation concept: the left and right key fields were joined into one PCB and arranged in a reverse-V shape. D-015 now proposes separate Left/Right Wings connected to reusable Main; the unified keyboard intent remains. The current geometric interpretation is an internal angle of 120 degrees, equivalent to rotating the left and right key fields approximately +30 degrees for the left field and -30 degrees for the right field in the project coordinate convention (+x right, +y down).

## 2. Fixed user requirements

- 42 keys.
- Piantor-derived column stagger and thumb cluster.
- One-piece keyboard; not a split keyboard.
- Production pitch open under D-015: compare 17.0 / 16.5 / 16.0 mm.
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

## 4. Electrical architecture - provisional baseline

The keyboard shall use analog Hall-effect sensing rather than a conventional switch matrix.

Current functional baseline:

USB-C / VBUS
-> 3.3 V logic rail -> RP2040
-> TPS22919 switched HALL_5V
-> 42 analog Hall sensors
-> six TMUX1208 multiplexers arranged as two banks of three
-> three scaled ADC channels
-> RP2040 ADC0 / ADC1 / ADC2

The production scan topology uses seven active addresses per bank:
- shared MUX_A0 / MUX_A1 / MUX_A2,
- MUX_EN0 and MUX_EN1 select one 21-key bank at a time,
- three mux outputs are sampled in parallel by GPIO26 / GPIO27 / GPIO28,
- 2 banks x 7 addresses x 3 ADC channels = 42 keys.

Hall and TMUX reside on Wings; three ADC dividers/filters and RP2040 reside
on Main. The Main/Wing interconnect is part of the measured analog path.

Each mux output is scaled by a 6.8 kOhm / 10 kOhm divider and uses a 1 nF ADC-node capacitor as the initial settling/noise baseline.

Both the evaluation PCB and production PCB use 1.2 mm PCB thickness as the baseline because the selected switch's published magnetic-flux figures are specified at 1.2 mm.

The Hall sensor itself remains provisional until the evaluation PCB proves signal range, noise, travel curve, cross-key magnetic coupling, settling time, and power consumption. DRV5055A3 is the documented reference sensor; lower-current alternatives may be evaluated before the 42-key release.

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

D-015 places switch geometry on Left/Right Wings generated from the same
project-owned or explicitly approved definition; Main carries MCU/power/ADC
conditioning. Historical one-piece PCB geometry is reference evidence, not the
new manufacturing design.

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
2. Complete the Rev.A Wing geometry source / license Human Gate before
   defining project-owned or explicitly approved Left/Right geometry. Historical
   QMK/Piantor coordinate provenance/reference (REQ-004) is not an input to
   future project-owned Rev.A geometry.
3. Select Hall sensor and acquisition architecture.
4. Pass G0A/G0B and design reusable Main + Evaluation Wing(s).
5. Pass G1, manufacture and measure the actual Main/Wing path.
6. At G2 select pitch/magnetic architecture, sensor range and calibration method.
7. Reuse accepted Main with Left/Right 21-key Wings for Rev.A.
8. Implement Vial and Hall firmware.
9. Design enclosure.
10. Generate JLCPCB and 3D-print packages.
11. Bring-up, validate, revise if necessary.

## 8. Validation gates

The following historical technical checklists remain useful measurement intent;
G0A/G0B and G1-G5 in [project status](project-status.md#human-gates) govern
current release authority. No fixed-pitch or single-PCB requirement is inferred.

### Gate 1 - Requirements freeze

Required:
- Switch selected.
- Keycap fit judged acceptable.
- Production pitch selected by G2 among 17.0 / 16.5 / 16.0 mm.
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
- Exact center gap and wrist/hand spacing.
- Whether a switch plate is required or PCB mounting alone is sufficient.
- Whether advanced Rapid Trigger settings are required for v1.0.
- Final Hall-sensor part after evaluation-board current/noise/travel measurements.
