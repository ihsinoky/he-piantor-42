# ISP1807-LR official CAD — provenance and verification (fix round, 2026-11-19)

## Source (maker, authorized channel only)
Insight SiP official file tree, directory index
`https://www.insightsip.com/fichiers_insightsip/pdf/ble/ISP1807/`
(the maker's own site; the same folder hosts the DS1807 datasheet):

| file | bytes | SHA-256 |
|---|---|---|
| ISP1807_Altium_Library.zip | 566453 | 14fa64ebbf49463fed5995b4b86e274bbed63ada876463b42fba73878345eae1 |
| ISP1807_Eagle_Library.zip | 4676 | 6e9409e1dfca600753d505df1919a98fb1986ded1f80276d6579b629d9d728e6 |
| ISP1807_LR_TB_Gerber.zip | — | ac1dfb31bd4b50889f0854442165ac97c00a1b1237b6068315001a0723af8237 |
| isp_ble_DS1807.pdf (R19) | — | 6a1fc5729a9d146c63aa00b064a879ebd7b9ae91aa016fe061c745c81c1bfa73 |

Contents: Altium `ISP1807-LR_Footprint.PcbLib` + `.SchLib`;
Eagle `ISP1807LR_Int.lbr` (its description states it was imported
from the maker's Altium `ISP1807LR_Int.IntLib`); TB gerbers RevB
(Altium Designer 18 export, maker's manufactured test board).

## Triangulation (all script-generated, this folder)
1. **Geometry**: Eagle pad set == TB top-copper pad cluster
   (apertures 0.4x0.4 / 0.8x0.8, 78 flashes): max error
   **0.000 mm, 78/78** under rot180/flipy (`cmp_tb.py`).
2. **Numbering**: Altium PcbLib (read via KiCad 9 import) vs Eagle:
   by-number max error **0.0000 mm**, sizes 78/78 match (`flipy`,
   the Eagle-y-up/KiCad-y-down convention).
3. **Functions**: maker SchLib pin names vs datasheet R19 §3 table
   (design.py ISP_PINS): 64/64 functional pins agree (pin 13 name
   spelled P0.18/NRESET in SchLib vs P0.18/RESET in §3 — same pin).
   Pins 65–78 = NC (§3), isolated mechanical pads (§3/§4.2:
   "connected to isolated metal pads on the application PCB").
4. **Orientation**: datasheet §3 pad-placement drawing is labelled
   TOP VIEW: pin 1 at NW corner, functional rows in the north 2/3,
   NC ring (65–78) wrapping the empty south zone; §4.3 keep-out
   drawing shows the exclusion band on that same south side,
   >=18.0 mm wide, to the board edge. The official CAD frame
   (KiCad import) matches this drawing exactly: pin 1 (-3.5,-3.5),
   antenna edge = local +Y (south), NC row 69–74 on that edge.

## Verdict on the derived footprint
The derived footprint (isp1807-derived-pads.json) differs from the
official CAD in BOTH geometry and number placement: it is a JEDEC
ring approximation (outer 12/side + inner rows) with numbering CCW
from a SW pin 1 and the antenna edge on local +X. No rotation or
mirror of the official set reproduces it (set alignment 0/69
within 0.05 mm under all 8 dihedral transforms). It is replaced
wholesale; pad NETS follow pad NUMBERS (the schematic/symbol side
was built from the §3 table and is unaffected).

Full by-number diff: `isp1807-pad-diff-final.md` (official positions
in the official frame; derived positions in the derived frame;
frames differ by construction — see orientation note above).

## CORRECTION (fix round, later same day): pin-function binding re-verified

An early spot check in this fix round used design.py's ISP_PINS table
(the layout study's transcription) and appeared to show pad-net
mismatches at pins 2/24. That table is WRONG: from pin 24 onward it is
shifted by +2 (it puts VCC at 24; the datasheet puts VCC_nRF at 26).
Authoritative binding, three-way, all 78 pins:
- DS1807 R19 pin table, pp.9-10 (pdftotext): 24 VSS, 25 VSS,
  26 VCC_nRF, 27 P0.17, 28 SWDIO, 29 P0.13, 30 SWDCLK, 65-78 NC.
- Maker Eagle library connects (eagle-pinmap.json, parsed from
  ISP1807LR_Int.lbr XML): identical binding.
- Project schematic symbol (wmain.kicad_sym ISP1807): identical
  (only case differs at VCC_nRF).
So the schematic and the board pad-net assignment were always correct;
the earlier "SchLib vs design.py 64/64 agree" note in this file was a
set-based comparison that masked the shift - superseded by this
number-keyed three-way check. The footprint GEOMETRY triangulation
(Altium/Eagle/TB gerber, number-keyed positions) is unaffected.
