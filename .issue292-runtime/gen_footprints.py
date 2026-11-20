"""Generate wmain.pretty: clone donor footprints from Rev.10 + write custom ones."""
import pcbnew as p, os, shutil, math
from pathlib import Path
E = Path(__file__).resolve().parent
W = E.parent
TREE = W/'hardware/kicad/qualification/issue-292-wmain'
LIB = TREE/'wmain.pretty'
LIB.mkdir(parents=True, exist_ok=True)
REV10 = W/'hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'

b = p.LoadBoard(str(REV10))
clone = {  # ref -> saved name
 'J2': 'FH12-14S-0.5SH', 'U6': 'TPS63070RNMR', 'U5': 'TPS22919DCKR',
 'L1': 'XFL4020', 'C26': 'C_1210', 'C23': 'C_0805', 'R17': 'R_0603',
 'C18': 'C_0603', 'TP1': 'TestPoint', 'J4': 'Pico-EZmate_781710004',
 'H1': 'MountingHole_2.2mm',
}
tmp = E/'fp-tmp.pretty'; tmp.mkdir(exist_ok=True)
for ref, name in clone.items():
    f = [x for x in b.GetFootprints() if str(x.GetReference()) == ref][0]
    p.FootprintSave(str(tmp), f)
    src = tmp/(str(f.GetFPID().GetLibItemName()) + '.kicad_mod')
    dst = LIB/(name + '.kicad_mod')
    shutil.copy(src, dst)
    print('cloned', ref, '->', name)
for x in tmp.iterdir(): x.unlink()
tmp.rmdir()

# ---------- custom footprints (text format, KiCad 9) ----------
def fp_head(name, descr):
    return f'(footprint "{name}"\n\t(version 20240108)\n\t(generator "pcbnew")\n\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "{descr}")\n\t(attr smd)\n'
def refval():
    return ('\t(property "Reference" "REF**"\n\t\t(at 0 -3 0)\n\t\t(layer "F.SilkS")\n\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            '\t(property "Value" ""\n\t\t(at 0 3 0)\n\t\t(layer "F.Fab")\n\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n')
def pad(num, x, y, sx, sy, shape='rect'):
    return (f'\t(pad "{num}" smd {shape}\n\t\t(at {x:.3f} {y:.3f})\n\t\t(size {sx:.3f} {sy:.3f})\n'
            f'\t\t(layers "F.Cu" "F.Paste" "F.Mask")\n\t)\n')
def rect_lines(cx, cy, hx, hy, layer='F.SilkS', w=0.12):
    pts = [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy),(-hx,-hy)]
    s = ''
    for (x1,y1),(x2,y2) in zip(pts, pts[1:]):
        s += (f'\t(fp_line\n\t\t(start {cx+x1:.3f} {cy+y1:.3f})\n\t\t(end {cx+x2:.3f} {cy+y2:.3f})\n'
              f'\t\t(stroke (width {w}) (type solid))\n\t\t(layer "{layer}")\n\t)\n')
    return s

# --- ISP1807-LR: DERIVED JEDEC dual-row QFN grid (see module-datasheet-notes.md).
# Outer row: 12/side incl corners, centres |c|=3.60, pitch 0.65, span -3.575..3.575.
# Inner row: 10/side on N/E/W (radius 2.95, span -2.925..2.925), 6 on antenna side.
# Numbering: pin 1 = outer south-west corner; CCW from top along south edge E-ward,
# then E edge N-ward, N edge W-ward, W edge S-ward; inner row continues same sense.
# Antenna edge = local +X (east) side: OUT_ANT/OUT_MOD (20/22) land there.
pads = {}   # pin -> (x, y, sx, sy)
span_o = [round(-3.575 + 0.65*i, 3) for i in range(12)]
span_i = [round(-2.925 + 0.65*i, 3) for i in range(10)]
span_a = [round(-1.625 + 0.65*i, 3) for i in range(6)]
n = 0
def add(x, y, corner=False):
    global n
    n += 1
    s = 0.78 if corner else 0.40
    pads[n] = (x, y, s, s)
# outer row CCW: south edge W->E (y=+3.60), east edge S->N (x=+3.60),
# north edge E->W (y=-3.60), west edge N->S (x=-3.60)
for x in span_o: add(x, 3.60, corner=(abs(abs(x)-3.575) < 0.01))
for y in reversed(span_o[1:-1]): add(3.60, y)
for x in reversed(span_o): add(x, -3.60, corner=(abs(abs(x)-3.575) < 0.01))
for y in span_o[1:-1]: add(-3.60, y)
assert n == 44, n
# inner row: south (y=+2.95) W->E 10, east (x=+2.95) S->N 8 (skip corners),
# north (y=-2.95) E->W 10, west (x=-2.95) N->S 8 -> 36; need 34: antenna side
# is EAST: use 6 on east instead of 8 -> 34. Total 44+34 = 78.
for x in span_i: add(x, 2.95)
for y in [round(1.625 - 0.65*i, 3) for i in range(6)]: add(2.95, y)
for x in reversed(span_i): add(x, -2.95)
for y in span_i[1:-1]: add(-2.95, y)
assert n == 78, n
s = fp_head('ISP1807-LR', 'Insight SiP ISP1807-LR LGA-78, DERIVED JEDEC 2-row QFN grid 0.65 pitch (datasheet R19 pin table; pad map NOT maker-CAD verified)') + refval()
s += rect_lines(0, 0, 4.0, 4.0)
s += '\t(fp_circle\n\t\t(center -4.6 4.6)\n\t\t(end -4.3 4.6)\n\t\t(stroke (width 0.12) (type solid))\n\t\t(fill none)\n\t\t(layer "F.SilkS")\n\t)\n'
for num, (x, y, sx, sy) in sorted(pads.items()):
    s += pad(str(num), x, y, sx, sy)
s += ')\n'
(LIB/'ISP1807-LR.kicad_mod').write_text(s)
import json
(E/'isp1807-derived-pads.json').write_text(json.dumps({str(k): v for k, v in pads.items()}, indent=0))
print('ISP1807 pads:', n, ' pin20 at', pads[20], ' pin22 at', pads[22], ' pin26 at', pads[26])

# --- TC2030-IDC-NL pads-only (geometry extracted from jrwatch.kicad_pcb, KiCad 10 text)
s = fp_head('TC2030-IDC-NL_Pads', 'Tag-Connect TC2030-IDC-NL 2x03 P1.27 pads-only SWD (geometry from jrwatch board text extract)') + refval()
tc = {'1': (-1.27, -0.635), '2': (-1.27, 0.635), '3': (0, -0.635), '4': (0, 0.635), '5': (1.27, -0.635), '6': (1.27, 0.635)}
for num, (x, y) in tc.items():
    s += pad(num, x, y, 0.7874, 0.7874, 'circle')
# locator holes for TC2030 (nominal 2x 0.9mm NPTH at +-2.54... use jrwatch: skip, add silk marks)
s += rect_lines(0, 0, 2.2, 1.6)
s += ')\n'
(LIB/'TC2030-IDC-NL_Pads.kicad_mod').write_text(s)

# --- JST B2B-XH-A 2-pin (PTH, 2.50 pitch)
s = ('(footprint "JST_B2B-XH-A_2pin"\n\t(version 20240108)\n\t(generator "pcbnew")\n\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "JST B2B-XH-A vertical 2-pin, hand-fit battery connector")\n\t(attr through_hole)\n') + refval()
for num, x in (('1', -1.25), ('2', 1.25)):
    s += (f'\t(pad "{num}" thru_hole circle\n\t\t(at {x} 0)\n\t\t(size 1.7 1.7)\n\t\t(drill 1.0)\n\t\t(layers "*.Cu" "*.Mask")\n\t)\n')
s += rect_lines(0, 0, 2.6, 2.5)
s += ')\n'
(LIB/'JST_B2B-XH-A_2pin.kicad_mod').write_text(s)

# --- SOT-23 (2N7002)
s = fp_head('SOT-23', 'SOT-23 standard') + refval()
for num, (x, y) in {'1': (-0.95, -0.65), '2': (-0.95, 0.65), '3': (0.95, 0)}.items():
    s += pad(num, x, y, 0.6, 1.0)
s += rect_lines(0, 0, 1.5, 1.6)
s += ')\n'
(LIB/'SOT-23.kicad_mod').write_text(s)

# --- SOD-123 (Schottky)
s = fp_head('SOD-123', 'SOD-123 diode') + refval()
s += pad('1', -1.35, 0, 0.9, 1.1) + pad('2', 1.35, 0, 0.9, 1.1)
s += rect_lines(0, 0, 1.9, 0.9)
s += ')\n'
(LIB/'SOD-123.kicad_mod').write_text(s)

# --- FH12-6S-class FFC land (derived from FH12 family pad geometry 0.3 wide, 0.5 pitch)
s = fp_head('FFC6_0.5mm_land', '6-contact 0.5mm FFC land, FH12-6S-class (derived from FH12-14S pad geometry)') + refval()
for i in range(6):
    s += pad(str(i+1), -1.25 + 0.5*i, 0, 0.3, 1.8)
s += pad('MP', -2.2, 1.6, 1.0, 1.2) + pad('MP', 2.2, 1.6, 1.0, 1.2)
s += rect_lines(0, 0.6, 2.9, 1.7)
s += ')\n'
(LIB/'FFC6_0.5mm_land.kicad_mod').write_text(s)

# --- generic tact-switch land 2-pad (bring-up button provision)
s = fp_head('TACT_2pad', 'generic 2-pad tact switch land (bring-up button)') + refval()
s += pad('1', -1.6, 0, 1.2, 1.8) + pad('2', 1.6, 0, 1.2, 1.8)
s += rect_lines(0, 0, 2.6, 1.5)
s += ')\n'
(LIB/'TACT_2pad.kicad_mod').write_text(s)
print('library written:', sorted(os.listdir(LIB)))
