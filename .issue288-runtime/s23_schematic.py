"""S2.3: generate the native KiCad schematic + symbol library for issue #288.

Label-style generated schematic (same dialect as the repo's Rev.8 tree):
every pin gets a stub wire + local net label; NC pins get no_connect markers;
PWR_FLAGs drive the power nets for ERC.
"""
import uuid
from pathlib import Path

from s2_design import COMPONENTS, FOOTPRINTS, NC, PWR_FLAG_NETS, SYMBOLS

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
TREE.mkdir(parents=True, exist_ok=True)


def u():
    return str(uuid.uuid4())


REF_PREFIX = {'TMAG5253': 'U', 'TMUX1208': 'U', 'XIAO': 'U', 'AP2112': 'U',
              'AO3401A': 'Q', 'USB_C': 'J', 'CONN2': 'J', 'R': 'R', 'C': 'C',
              'LED': 'D', 'TP': 'TP'}


def symbol_def(name, prefix_lib=None):
    """Return the symbol definition text (unit sub-symbols included)."""
    spec = SYMBOLS[name]
    hw = spec['hw']
    ys = [p[4] for p in spec['pins']] or [0]
    top, bot = max(ys) + 1.27, min(ys) - 1.27
    libname = f'{prefix_lib}:{name}' if prefix_lib else name
    s = (f'(symbol "{libname}" (pin_names (offset 1.016)) (exclude_from_sim no) '
         f'(in_bom yes) (on_board yes) '
         f'(property "Reference" "{REF_PREFIX[name]}" (at 0 {top + 1.27:.2f} 0) (effects (font (size 1 1)))) '
         f'(property "Value" "{name}" (at 0 {bot - 1.27:.2f} 0) (effects (font (size 1 1)))) '
         f'(property "Footprint" "{FOOTPRINTS[name]}" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) '
         f'(property "Datasheet" "" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) ')
    if name == 'TP':
        s += (f'(symbol "{name}_0_1" (circle (center 0 0) (radius 1.27) '
              f'(stroke (width 0.254) (type default)) (fill (type background)))) ')
    else:
        s += (f'(symbol "{name}_0_1" (rectangle (start {-hw + 1.27 if hw > 3 else -1.9:.2f} {top:.2f}) '
              f'(end {hw - 1.27 if hw > 3 else 1.9:.2f} {bot:.2f}) '
              f'(stroke (width 0.254) (type default)) (fill (type background)))) ')
    s += f'(symbol "{name}_1_1" '
    for num, pname, etype, side, ly in spec['pins']:
        if side == 'L':
            x, rot = -hw, 0
        elif side == 'R':
            x, rot = hw, 180
        else:  # 'T' TP centre pin
            x, rot = 0, 90
        length = 0 if name == 'TP' else (2.54 if hw <= 3.81 else 5.08)
        s += (f'(pin {etype} line (at {x:.2f} {ly:.2f} {rot}) (length {length}) '
              f'(name "{pname}" (effects (font (size 1.0 1.0)))) '
              f'(number "{num}" (effects (font (size 1.0 1.0))))) ')
    s += ')'
    s += ')'
    return s


PWR_FLAG_DEF = ('(symbol "wmatrix:PWR_FLAG" (power) (pin_names (offset 0)) (exclude_from_sim no) '
                '(in_bom no) (on_board no) '
                '(property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)))) '
                '(property "Value" "PWR_FLAG" (at 0 5.08 0) (effects (font (size 1 1)))) '
                '(symbol "PWR_FLAG_0_1" (polyline (pts (xy -1.27 0) (xy 0 1.27) (xy 1.27 0) (xy -1.27 0)) '
                '(stroke (width 0.254) (type default)) (fill (type none)))) '
                '(symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) '
                '(name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))')
PWR_FLAG_DEF_PLAIN = PWR_FLAG_DEF.replace('"wmatrix:PWR_FLAG"', '"PWR_FLAG"')

# ---------------------------------------------------------------- placement
PLACE = {}


def place(ref, x, y):
    PLACE[ref] = (x, y)


def G(v):
    """grid units (1.27mm) -> mm"""
    return round(v * 1.27, 2)


for gi, g in enumerate('ABC'):
    x = G(56 + gi * 102)
    for i in range(6):
        y = G(56 + i * 26)
        place(f'U_H{g}{i}', x, y)
        place(f'C_H{g}{i}', G(56 + gi * 102 + 25), y)
    place(f'U_MUX{g}', x, G(246))
    place(f'C_MUX{g}', G(56 + gi * 102 + 26), G(246))
place('U_XIAO', G(378), G(88))
place('R_LED', G(456), G(118))
place('D_LED', G(492), G(118))
place('J_USB', G(370), G(236))
place('J_BATT', G(370), G(300))
place('Q_PROT', G(446), G(236))
place('U_LDO', G(504), G(236))
place('R_SHUNT', G(564), G(236))
place('C_LDO_IN', G(446), G(300))
place('C_LDO_OUT', G(504), G(300))
place('R_CC1', G(410), G(358))
place('R_CC2', G(456), G(358))
place('R_DIV1', G(564), G(300))
place('R_DIV2', G(564), G(334))
tp_refs = [r for r, s, v, p in COMPONENTS if s == 'TP']
for k, ref in enumerate(tp_refs):
    place(ref, G(48 + (k % 12) * 26), G(398 + (k // 12) * 32))

# ---------------------------------------------------------------- generate
sheet_uuid = u()
items = []          # schematic body items
label_points = {}   # net -> list of (x, y) label anchor points
pin_points = {}     # (ref, pin) -> label anchor point

for ref, sym, value, pins in COMPONENTS:
    X, Y = PLACE[ref]
    spec = SYMBOLS[sym]
    hw = spec['hw']
    ys = [p[4] for p in spec['pins']] or [0]
    top = Y - (max(ys) + 3.5)
    bot = Y - (min(ys) - 3.5)
    inst = (f'(symbol (lib_id "wmatrix:{sym}") (at {X} {Y} 0) (unit 1) (exclude_from_sim no) '
            f'(in_bom yes) (on_board yes) (dnp no) (uuid "{u()}") '
            f'(property "Reference" "{ref}" (at {X} {top:.2f} 0) (effects (font (size 1 1)))) '
            f'(property "Value" "{value}" (at {X} {bot:.2f} 0) (effects (font (size 1 1)))) '
            f'(property "Footprint" "{FOOTPRINTS[sym]}" (at {X} {Y} 0) (effects (font (size 1 1)) (hide yes))) '
            f'(property "Datasheet" "" (at {X} {Y} 0) (effects (font (size 1 1)) (hide yes))) '
            f'(instances (project "wmatrix" (path "/{sheet_uuid}" (reference "{ref}") (unit 1)))))')
    items.append(inst)
    pinmap = {p[0]: p for p in spec['pins']}
    for num, net in pins.items():
        _, _, _, side, ly = pinmap[num]
        if side == 'L':
            cx, cy = X - hw, Y - ly
            ex, ey = cx - 5.08, cy
            justify = 'right bottom'
        elif side == 'R':
            cx, cy = X + hw, Y - ly
            ex, ey = cx + 5.08, cy
            justify = 'left bottom'
        else:
            cx, cy = X, Y
            ex, ey = cx, cy - 5.08
            justify = 'left bottom'
        if net == NC:
            items.append(f'(no_connect (at {cx} {cy}) (uuid "{u()}"))')
        else:
            items.append(f'(wire (pts (xy {cx} {cy}) (xy {ex} {ey})) '
                         f'(stroke (width 0) (type solid)) (uuid "{u()}"))')
            items.append(f'(label "{net}" (at {ex} {ey} 0) '
                         f'(effects (font (size 1 1)) (justify {justify})) (uuid "{u()}"))')
            label_points.setdefault(net, []).append((ex, ey))
            pin_points[(ref, num)] = (ex, ey)

# PWR_FLAGs on nets with no power_out driver, hosted on pins in sparse areas
# (host ref, host pin, branch dy). HALL_3V3_SRC is driven by the LDO power_out
# pin, so it takes no flag (two power_out pins on one net is an ERC error).
FLAG_HOSTS = [('VIN_SRC', 'J_USB', '2', -10.16), ('VIN', 'U_LDO', '1', -10.16),
              ('HALL_3V3', 'R_SHUNT', '2', -10.16), ('GND', 'J_USB', '13', 10.16)]
for k, (net, href, hpin, dy) in enumerate(FLAG_HOSTS):
    lx, ly = pin_points[(href, hpin)]
    fx, fy = lx, ly + dy
    items.append(f'(wire (pts (xy {lx} {ly}) (xy {fx} {fy})) '
                 f'(stroke (width 0) (type solid)) (uuid "{u()}"))')
    items.append(f'(symbol (lib_id "wmatrix:PWR_FLAG") (at {fx} {fy} 0) (unit 1) '
                 f'(exclude_from_sim no) (in_bom no) (on_board no) (dnp no) (uuid "{u()}") '
                 f'(property "Reference" "#FLG{k+1:02d}" (at {fx} {fy - 3:.2f} 0) (effects (font (size 1 1)))) '
                 f'(property "Value" "PWR_FLAG" (at {fx} {fy - 6:.2f} 0) (effects (font (size 1 1)))) '
                 f'(instances (project "wmatrix" (path "/{sheet_uuid}" (reference "#FLG{k+1:02d}") (unit 1)))))')

lib_syms = ' '.join([symbol_def(n, 'wmatrix') for n in SYMBOLS] + [PWR_FLAG_DEF])
sch = (f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") '
       f'(uuid "{sheet_uuid}") (paper "A1") '
       f'(title_block (title "Issue 288 wireless Matrix evaluation board (TMAG5253BA3 / TMUX1208 / XIAO nRF52840)") '
       f'(rev "S2-draft") (comment 1 "DRAFT - NOT FOR ORDER")) '
       f'(lib_symbols {lib_syms}) ' + ' '.join(items) + ')')
(TREE / 'wmatrix.kicad_sch').write_text(sch)

lib = ('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") (generator_version "9.0") '
       + ' '.join([symbol_def(n) for n in SYMBOLS] + [PWR_FLAG_DEF_PLAIN]) + ')')
(TREE / 'wmatrix.kicad_sym').write_text(lib)

(TREE / 'sym-lib-table').write_text(
    '(sym_lib_table (version 7) (lib (name "wmatrix")(type "KiCad")'
    '(uri "${KIPRJMOD}/wmatrix.kicad_sym")(options "")(descr "Issue 288 symbols")))')
(TREE / 'fp-lib-table').write_text(
    '(fp_lib_table (version 7) (lib (name "wmatrix")(type "KiCad")'
    '(uri "${KIPRJMOD}/wmatrix.pretty")(options "")(descr "Issue 288 footprints")))')
(TREE / 'wmatrix.kicad_pro').write_text(
    '{\n  "meta": {"filename": "wmatrix.kicad_pro", "version": 1},\n'
    '  "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},\n'
    '  "board": {}, "cvpcb": {}, "erc": {}, "libraries": {}\n}\n')
print('schematic bytes:', len(sch), '| components placed:', len(PLACE))
