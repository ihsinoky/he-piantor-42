# Layout geometry

## Source

The column stagger is taken from QMK's current `keyboards/cantor/keyboard.json`, layout `LAYOUT_split_3x6_3`.

Piantor is derived from Cantor, so the Cantor logical x/y positions are used as a compact machine-readable source rather than parsing the approximately 2 MB Piantor PCB file.

## Baseline transformation

- Pitch: 17.0 mm per QMK key unit.
- Keycap envelope used for preview: 16.5 x 16.5 mm.
- Left rotation: +30 degrees.
- Right rotation: -30 degrees.
- Included obtuse angle between the two row directions: 120 degrees.
- Left pivot: inner home-row center at QMK (5, 1.25).
- Right pivot: inner home-row center at QMK (8, 1.25).
- Inner home-row center-to-center gap: 34.0 mm **provisional**.

The 34 mm gap is deliberately a parameter. It is not inherited from the QMK visual gap. It will be adjusted after the first full monoblock outline preview and before the PCB outline is frozen.

## Files

- `layout_source.json`: logical Cantor key centers plus transformation parameters.
- `generate_layout.py`: deterministic transformation.
- `key_positions.csv`: generated physical key-center coordinates in millimetres.
- `layout_preview.svg`: generated 16.5 mm keycap-envelope preview.

## Coordinate convention

+x is right and +y is down. Rotation follows the SVG/PCB-plan-view convention used by the generator.

## Review point

The next layout review shall focus on only two geometric questions:

1. Whether the chosen sign of the +/-30 degree rotation matches the intended "reverse-Ha" orientation.
2. Whether the 34 mm inner-home center gap is comfortable and leaves enough central structure/electronics space.

The Cantor/Piantor column stagger and 17 mm pitch remain independent of those two parameters.
