"""S2.2: build the wmatrix.pretty footprint library in the new tree."""
import shutil
import uuid
from pathlib import Path

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
LIB = TREE / 'wmatrix.pretty'
LIB.mkdir(parents=True, exist_ok=True)
DONOR_PRETTY = WT / 'hardware/kicad/qualification/issue-182-matrix-rev3/PCBA.pretty'


def u():
    return str(uuid.uuid4())


def hdr(name, descr=''):
    return (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "pcbnew")\n'
            f'\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "{descr}")\n'
            f'\t(property "Reference" "REF**"\n\t\t(at 0 -2.2 0)\n\t\t(layer "F.SilkS")\n\t\t(hide yes)\n\t\t(uuid "{u()}")\n'
            '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            f'\t(property "Value" "{name}"\n\t\t(at 0 2.2 0)\n\t\t(layer "F.Fab")\n\t\t(hide yes)\n\t\t(uuid "{u()}")\n'
            '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            '\t(attr smd)\n')


def rect_lines(x0, y0, x1, y1, layer='F.Fab', w=0.1):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    out = ''
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        out += (f'\t(fp_line (start {ax} {ay}) (end {bx} {by})\n'
                f'\t\t(stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{u()}"))\n')
    return out


def pad_smd(num, x, y, w, h, shape='rect', rratio=None):
    extra = ''
    if shape == 'roundrect':
        extra = f'\n\t\t(roundrect_rratio {rratio})'
    return (f'\t(pad "{num}" smd {shape}\n\t\t(at {x} {y})\n\t\t(size {w} {h})\n'
            f'\t\t(layers "F.Cu" "F.Paste" "F.Mask"){extra}\n\t\t(uuid "{u()}")\n\t)\n')


def pad_pth(num, x, y, d, drill, shape='circle'):
    return (f'\t(pad "{num}" thru_hole {shape}\n\t\t(at {x} {y})\n\t\t(size {d} {d})\n'
            f'\t\t(drill {drill})\n\t\t(layers "*.Cu" "*.Mask")\n\t\t(remove_unused_layers no)\n'
            f'\t\t(uuid "{u()}")\n\t)\n')


def write(name, body, attr=None):
    s = hdr(name)
    if attr:
        s = s.replace('\t(attr smd)\n', f'\t(attr {attr})\n')
    s += body + '\t(embedded_fonts no)\n)\n'
    (LIB / f'{name}.kicad_mod').write_text(s)


# --- TMAG5253BA3 X2SON-4 (TI DMR0004A land pattern; see s21-facts.md) ---
body = rect_lines(-0.55, -0.70, 0.55, 0.70)                       # body 1.1 x 1.4 (F.Fab)
body += rect_lines(-0.75, -0.90, 0.75, 0.90, 'F.CrtYd', 0.05)     # courtyard
body += (f'\t(fp_circle (center -0.45 -0.95) (end -0.35 -0.95)\n'
         f'\t\t(stroke (width 0.1) (type solid)) (fill no) (layer "F.SilkS") (uuid "{u()}"))\n')  # pin1 dot NW
body += pad_smd('1', -0.25, -0.70, 0.22, 0.40, 'roundrect', 0.227)  # VCC
body += pad_smd('4',  0.25, -0.70, 0.22, 0.40, 'roundrect', 0.227)  # OUT
body += pad_smd('2', -0.25,  0.70, 0.22, 0.40, 'roundrect', 0.227)  # GND
body += pad_smd('3',  0.25,  0.70, 0.22, 0.40, 'roundrect', 0.227)  # EN
body += pad_smd('5', 0, 0, 0.80, 0.60)                              # thermal pad -> GND
write('TMAG5253BA3_X2SON-4', body)

# --- XIAO nRF52840 socket (Seeed DIP: rows y=+/-7.62, pitch 2.54, drill 0.889) ---
body = rect_lines(-10.5, -8.9, 10.5, 8.9)                          # module 21 x 17.8
body += rect_lines(-11.0, -9.4, 11.0, 9.4, 'F.CrtYd', 0.05)
for i in range(7):  # pads 1..7 on y=-7.62 row, x from +7.62 down to -7.62
    body += pad_pth(str(i + 1), 7.62 - 2.54 * i, -7.62, 1.524, 0.889)
for i in range(7):  # pads 8..14 on y=+7.62 row, x from -7.62 up to +7.62
    body += pad_pth(str(i + 8), -7.62 + 2.54 * i, 7.62, 1.524, 0.889)
write('XIAO_nRF52840_SOCKET', body, attr='through_hole')

# --- AP2112 SOT-23-5 (1=VIN 2=GND 3=EN south row W->E; 5=VOUT 4=NC north row) ---
body = rect_lines(-1.45, -0.80, 1.45, 0.80)
body += rect_lines(-1.70, -1.05, 1.70, 1.05, 'F.CrtYd', 0.05)
for num, x in (('1', -0.95), ('2', 0), ('3', 0.95)):
    body += pad_smd(num, x, 1.0, 0.55, 1.0)
for num, x in (('5', -0.95), ('4', 0.95)):
    body += pad_smd(num, x, -1.0, 0.55, 1.0)
write('AP2112_SOT-23-5', body)

# --- AO3401A SOT-23 (donor hall land geometry; 1=G SW, 2=S NW, 3=D E) ---
body = rect_lines(-1.50, -0.65, 1.50, 0.65)
body += rect_lines(-1.75, -0.90, 1.75, 0.90, 'F.CrtYd', 0.05)
body += pad_smd('1', -1.015565, 0.95, 1.308868, 0.459999)
body += pad_smd('2', -1.015565, -0.95, 1.308868, 0.459999)
body += pad_smd('3', 1.015565, 0, 1.308868, 0.46)
write('AO3401A_SOT-23', body)

# --- JST XH B2B-XH-A 1x02 vertical (JST catalog: pitch 2.5, housing 7.4 wide) ---
body = rect_lines(-3.70, -2.80, 3.70, 2.80)
body += rect_lines(-3.95, -3.05, 3.95, 3.05, 'F.CrtYd', 0.05)
body += pad_pth('1', -1.25, 0, 1.7, 0.9, 'rect')
body += pad_pth('2', 1.25, 0, 1.7, 0.9)
write('JST_XH_B2B-XH-A_1x02', body, attr='through_hole')

# --- LED 0805 (KT-0805G; 1=anode, 2=cathode) ---
body = rect_lines(-1.0, -0.625, 1.0, 0.625)
body += rect_lines(-1.25, -0.875, 1.25, 0.875, 'F.CrtYd', 0.05)
body += pad_smd('1', -0.95, 0, 1.05, 1.15)
body += pad_smd('2', 0.95, 0, 1.05, 1.15)
write('LED_0805', body)

# --- copies from the donor library (project-proven lands) ---
for src, dst in (('capacitor', 'C_0603'), ('capacitor', 'R_0603'),
                 ('testpoint', 'TP_1.2mm'), ('mounting', 'NPTH_2.2mm'),
                 ('mux', 'TMUX1208PWR_TSSOP-16')):
    s = (DONOR_PRETTY / f'{src}.kicad_mod').read_text()
    s = s.replace(f'(footprint "{src}"', f'(footprint "{dst}"', 1)
    (LIB / f'{dst}.kicad_mod').write_text(s)

# --- USB-C: copy the project's J1 footprint (TYPE-C-31-M-12) ---
src = WT / 'hardware/kicad/qualification/eda-004g/resume-02/library/Qualification.pretty/J1.kicad_mod'
s = src.read_text().replace('(footprint "J1"', '(footprint "TYPE-C-31-M-12"', 1)
(LIB / 'TYPE-C-31-M-12.kicad_mod').write_text(s)

print('library:', sorted(p.name for p in LIB.glob('*.kicad_mod')))
