# Design Decisions

This file records decisions that materially affect hardware, firmware, manufacturing, or enclosure design.

## D-001 - One-piece geometry

Status: provisional

Interpret "120-degree reverse-V" as an internal angle of 120 degrees between left and right key fields, with each field rotated approximately 30 degrees from horizontal in opposite directions.

Reason: this is the simplest consistent geometric interpretation and is easy to review visually once the Piantor key centers are transformed.

## D-002 - Key pitch

Status: provisional baseline

Use 17.0 mm pitch rather than 16.5 mm.

Reason: 16.5 mm square narrow MX-stem keycaps exist. At 17.0 mm center spacing this leaves a nominal 0.5 mm cap-to-cap gap. A 16.5 mm pitch would leave no nominal gap.

## D-003 - Magnetic switch

Status: provisional baseline

Use Gateron Magnetic Jade Pro HE / KS-20-compatible as the primary design reference.

Reason: it is a full-height HE switch, has published magnetic values at 1.2 mm PCB thickness, and has current Japanese availability.

Do not release the 42-key production PCB based only on nominal switch data. Validate the sensor range with a small evaluation board first.

## D-004 - Power indication

Status: accepted

Use a dedicated power indicator LED independent of the MCU.

Reason: it provides a basic hardware diagnostic when firmware or USB enumeration fails.

## D-005 - Layer indication

Status: accepted

Use a separate MCU-controlled RGB LED for four-layer indication.

## D-006 - Manufacturing strategy

Status: accepted

Target JLCPCB PCBA for the assembled PCB and FDM printing for the first enclosure.

## D-007 - Project tracking

Status: accepted

task/index.html is the human-readable project dashboard. It is a single self-contained HTML file and will be updated together with engineering work.
