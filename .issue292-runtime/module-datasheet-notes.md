# ISP1807-LR datasheet notes (Insight SiP DS1807 R19, read 2026-11-19 via Mouser mirror)

## Pin table (§3) — pins 1..64 functional, 65..78 NC (isolated mechanical pads)
1 VSS · 2 P0.09/NFC1 · 3 P0.12 · 4 P0.10/NFC2 · 5 P0.14 · 6 P0.26 · 7 VSS ·
8 D+ (USB) · 9 P0.16 · 10 D- (USB) · 11 P0.21 · 12 VBUS (5V in for USB reg) ·
13 P0.18/RESET · 14 VSS · 15 P0.20 · 16 VSS · 17 P0.22 · 18 VSS · 19 P0.24 ·
20 OUT_ANT · 21 VSS · 22 OUT_MOD · 23 VSS · 24 VSS · 25 VSS · 26 VCC_nRF
(1.7-3.6V) · 27 P0.17 · 28 SWDIO · 29 P0.13 · 30 SWDCLK · 31 VSS · 32 P0.08 ·
33 P0.07 · 34 P0.06 · 35 P0.04/AIN2 · 36 P0.05/AIN3 · 37 P0.15 · 38 P0.03/AIN1 ·
39 P0.27 · 40 P0.02/AIN0 · 41 P0.25 · 42 P0.31/AIN7 · 43 P0.11 · 44 P0.30/AIN6 ·
45 P0.19 · 46 P0.29/AIN5 · 47 P0.23 · 48 P0.28/AIN4 · 49 P1.02 · 50 P1.06 ·
51 P1.15 · 52 P1.14 · 53 P1.13 · 54 P1.05 · 55 P1.08 · 56 P1.09 · 57 P1.00 ·
58 P1.03 · 59 P1.12 · 60 P1.10 · 61 P1.11 · 62 P1.07 · 63 P1.04 · 64 P1.01 ·
65-78 NC.
- OUT_ANT (20) MUST be connected to OUT_MOD (22) for normal operation (§3).
- NFC1/NFC2 (pins 2/4 alt functions): unused -> pads no-connect (NFC antenna
  is a firmware/antenna option, not populated).
- Integrated: 32MHz + 32.768kHz crystals, DCDC converter + loading circuit,
  RF matching + antenna (§1). NO external crystal/DCDC parts. Only a DC
  power source is required (§1).

## Land pattern (§4.2)
LGA, double row, 0.65mm pitch, QFN JEDEC 2-row standard. Recommended PCB
pads = module pad dims: 0.4x0.4mm standard, 0.8x0.8mm corner pads.
**The §3 pad-placement drawing and §4.1 dimension drawing are graphical;
no coordinate table exists in the datasheet text.** The footprint in
wmain.pretty is therefore a DERIVED JEDEC-pattern grid (see
gen_custom_fps.py header + isp1807-derived-pads.json): outer row 12/side
incl. corners (centres |c|=3.60, span -3.575..3.575), inner row 10/side
N/E/W + reduced antenna-side row, numbering CCW from pin 1 at the outer
south-west corner, antenna edge = local +X (OUT_ANT/OUT_MOD side).
**NOT verified against Insight SiP's official CAD library — carried as
an adoption-gate (D-057) condition, package is DRAFT / NOT FOR ORDER.**
Precedent: D-043 carried the reconstructed FH12 MP land the same way.

## Antenna keep-out (§4.3)
"Metal exclusion zone to the edge of the board: no metal, no traces and
no components on any application PCB layer except mechanical LGA pads."
Drawing dimensions extracted as text: 4.0 mm / 18.0 mm min (graphical
context; interpreted as: keep-out band extends from the antenna edge to
the board edge, i.e. the module's antenna edge sits ON the board outline
strip with the band south of it kept empty — implemented as a no-copper
rule area from the module's south edge to the board south edge, full
module width, all layers).
