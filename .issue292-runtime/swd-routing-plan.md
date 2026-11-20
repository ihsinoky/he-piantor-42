# SWD TC2050 respin — centre shift + routing plan (Stage 2/4 record)

## Centre: (110.5, 135.85), rotation 0 — shifted from the desk site

The margin round's desk verification centred the field at board
(111.5, 136.2) from the PAD extents only. The OFFICIAL footprint's
alignment holes (PROVENANCE.md) break that centre twice:
- East holes at (115.31, 135.184/137.216): the NORTH-east hole's
  drill disc (r 0.495) CUTS the In2.Cu PAD_SCL jog — track segments
  (115.3,135.5)->(115.3,135.15) and (84.15,135.5)->(115.3,135.5)
  pass through the disc (centre-to-track 0.034 mm). DRC
  hole_clearance (floor 0.25) would fail by ~0.47 mm.
- The SOUTH-east hole's south edge sits 137.711, leaving a
  0.189 mm web to the outline (Y 137.9, verified by polygon probe
  across X 105..116) — margin-less, rejected per PO priority 2.
Shift taken (smallest that clears both, with margin): centre
(110.5, 135.85) = desk centre + (-1.0, -0.35). Resulting margins:
PAD_SCL to east holes 0.47 (N) / 0.52 (S) vs 0.25 floor; SE hole
web to outline 0.539 (0.5 class); RPD2/RPD3 clear the field by
~4.1 mm, the plug body (10.15 wide, sheet 2) by ~1.5 mm.

## Congestion map (measured, all layers, X 100..121 / Y 130..139.5)

- F.Cu walls: PAD_EN run y=132.6 (x 89.1..116.4); SWDCLK run
  y=133.5 (x 91.1..110.0). No via fits between them at project
  clearances — no new via may cross that corridor.
- In2.Cu walls: SWDIO vertical x=109.4 (y ..134.0); MUX_EN0 wall
  y=134.3..134.5 (segments x 101.25..109.6 at 134.45 and
  x 109.75..115.81 at 134.3, jogged — continuous, no gap);
  PAD_SCL y=135.5 (x 84.15..115.3) + jog x=115.3..116.45.
  In2 is sealed for E-W and N-S travel inside the box.
- B.Cu: empty in the box except SYS_3V3 NE corner — relief layer.
- GND: board-wide F.Cu GND zone (bbox 64.11..135.89 x
  75.73..137.9); existing GND via tap at (115.72,135.565).
- Operative clearances (wmain.kicad_pro): Default netclass
  clearance 0.2; board setup min_hole_clearance 0.25,
  min_copper_edge_clearance 0.5, min_via_diameter 0.5,
  min_through_hole_diameter 0.3. (One 0.45 via exists in the
  design — GND at (118.3,132.0) — its via_diameter class items
  are part of the dispositioned baseline.)

## Deletions (old field + its local escape ends only)

- JSWD footprint (TC2030 pads).
- SYS_3V3 F.Cu stub (112.2,133.3)->(112.2,135.6). (Via stays,
  unconnected on F.Cu afterwards — it remains tied to SYS via
  its In2/B.Cu annuli; DRC arbitrates.)
- RESET_N F.Cu stub (113.5,133.4)->(113.5,135.6) south of the
  via (113.4,133.3) junction; y=131.3 run + vias stay.
- SWDIO F.Cu segment (109.4,134.0)->(112.2,136.8); via stays.
- SWDCLK F.Cu chain east of (110.0,133.5) (5 segments to
  (113.5,136.8)); the y=133.5 run west of (110.0,133.5) stays.
- GND F.Cu stub (114.77,135.565)->(115.72,135.565); via stays.

## New routes (centre (110.5,135.85); pads per PROVENANCE)

Pad coords: 1 SYS (107.96,136.485) | 2 SWDIO (109.23,136.485) |
3 GND (110.50,136.485) | 4 SWDCLK (111.77,136.485) | 5 GND
(113.04,136.485) | 6 NC (113.04,135.215) | 7 NC (111.77,135.215)
| 8 NC (110.50,135.215) | 9 GND (109.23,135.215) | 10 RESET
(107.96,135.215). Holes: W (106.69,135.85), E (114.31,134.834),
E (114.31,136.866). All vias 0.6/0.3 except RESET up-via 0.45/0.3.

- P1 SYS_3V3: via (100.5,134.95) [In2 annulus clears MUX_EN0
  staircase by >=0.45, PAD_SCL by 0.225]; F.Cu w0.2
  (100.5,134.95)->(100.5,136.9)->(107.96,136.9)->pad 1;
  B.Cu w0.3 (100.5,134.95)->(115.2,134.95)->(115.2,131.0)
  joining the existing B.Cu SYS run.
- P2 SWDIO: F.Cu w0.1 (109.4,134.0)->(108.85,134.0)->
  (108.85,136.485)->pad 2.
- P3 GND: F.Cu stub (110.5,136.485)->(110.9,137.05); via
  (110.9,137.05) [web to outline 0.55; drill clears pad circle].
- P4 SWDCLK: F.Cu (110.0,133.5)->(110.0,133.95); via A
  (110.0,133.95); B.Cu (110.0,133.95)->(110.0,136.95)->
  (112.15,136.95); via B (112.15,136.95); F.Cu
  (112.15,136.95)->(112.15,136.485)->pad 4.
- P5 GND: F.Cu stub (113.04,136.485)->(113.04,137.05); via
  (113.04,137.05) [web 0.55; SE hole clearance 0.51]. (The
  earlier channel/gap idea is DEAD: the SE hole's drill disc +
  0.25 clearance reaches Y 137.611, sealing the south channel.)
- P9 GND: F.Cu stub (109.23,135.215)->(109.23,134.55); highway
  (109.23,134.55)->(115.72,134.55); drop (115.72,134.55)->
  (115.72,135.565) into the existing GND via. [Highway clears
  N-row pad edges 0.221, via A annulus 0.25, RESET down-via
  annulus 0.225.]
- P10 RESET_N: stub re-laid (113.5,133.4)->(113.5,133.75)->
  (113.2,133.75); down-via (113.2,133.75); B.Cu
  (113.2,133.75)->(108.3,133.75)->(108.3,133.975); up-via
  0.45/0.3 at (108.3,133.975) [the unique window between the
  F.Cu SWDCLK run (south edge 133.55) and the In2 MUX_EN0 wall
  (south edge 134.4): annulus gaps exactly 0.2/0.2, drill gaps
  0.275/0.275 — at the class floor, mirroring the design's
  existing 0.45-via precedent; +1 via_diameter item expected];
  F.Cu (108.3,133.975)->(108.3,135.0)->pad 10.
- P6/P7/P8: NC — no tracks (maker mapping: SWO/KEY/TDI unused).

Iteration rule: after the scripted edit, DRC on the filled work
copy; every NEW violation inside X 100..118 / Y 130..139.5 gets
fixed by local adjustment or itemised for the REPORT delta
table; no violation outside the box may change at all.
