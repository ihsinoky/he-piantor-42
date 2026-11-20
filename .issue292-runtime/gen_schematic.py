"""Generate wmain.kicad_sym + wmain.kicad_sch from design.py (wmatrix idiom:
stub wire + local label per connected pin, no_connect per NC pin)."""
import sys, uuid, json
sys.path.insert(0, '.')
from design import PARTS, SYMBOLS, POWER_NETS
from pathlib import Path
E = Path('.').resolve(); W = E.parent
TREE = W/'hardware/kicad/qualification/issue-292-wmain'
SHEET_UUID = '292f292f-292f-4292-8292-292929292929'

def U():
    return str(uuid.uuid4())

HW = {'R': 1.27, 'C': 1.27, 'L': 1.27, 'D': 1.27, 'LED': 1.27, 'TP': 1.27,
      'MH': 1.27, 'CONN2': 1.27, 'TACT': 1.27, 'SOT23': 5.08,
      'TPS22919': 5.08, 'TPS63070': 5.08, 'EZMATE': 5.08, 'FH12': 5.08,
      'FFC6': 5.08, 'TC2030': 5.08, 'ISP1807': 7.62}
REFPFX = {'ISP1807': 'U', 'TPS63070': 'U', 'TPS22919': 'U', 'SOT23': 'Q',
          'FH12': 'J', 'FFC6': 'J', 'TC2030': 'J', 'EZMATE': 'J', 'CONN2': 'J'}

def pin_ys(k):
    return [(k - 1) * 1.27 - i * 2.54 for i in range(k)]

def sym_def(name, for_sch=False):
    left, right = SYMBOLS[name]
    hw = HW[name]
    maxk = max(len(left), len(right), 1)
    hh = (maxk - 1) * 1.27 + 3.81
    nm = ('wmain:' + name) if for_sch else name
    s = f'(symbol "{nm}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)'
    s += f' (property "Reference" "{REFPFX.get(name, name)}" (at 0 {hh + 2.54:.2f} 0) (effects (font (size 1 1))))'
    s += f' (property "Value" "{name}" (at 0 {-hh - 2.54:.2f} 0) (effects (font (size 1 1))))'
    s += ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))'
    s += ' (property "Datasheet" "" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))'
    s += f' (symbol "{name}_0_1" (rectangle (start {-hw} {hh:.2f}) (end {hw} {-hh:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))'
    s += f' (symbol "{name}_1_1"'
    for (num, pname), y in zip(left, pin_ys(len(left))):
        s += (f' (pin passive line (at {-(hw + 2.54):.2f} {y:.2f} 0) (length 2.54)'
              f' (name "{pname}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))')
    for (num, pname), y in zip(right, pin_ys(len(right))):
        s += (f' (pin passive line (at {hw + 2.54:.2f} {y:.2f} 180) (length 2.54)'
              f' (name "{pname}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))')
    s += '))'
    return s

PWR_FLAG_DEF = ('(symbol "wmain:PWR_FLAG" (power) (pin_names (offset 0)) (exclude_from_sim no) (in_bom no) (on_board no)'
 ' (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1))))'
 ' (property "Value" "PWR_FLAG" (at 0 5.08 0) (effects (font (size 1 1))))'
 ' (symbol "PWR_FLAG_0_1" (polyline (pts (xy -1.27 0) (xy 0 1.27) (xy 1.27 0) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none))))'
 ' (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))')
PWR_FLAG_DEF_LIB = PWR_FLAG_DEF.replace('"wmain:PWR_FLAG"', '"PWR_FLAG"')

used_syms = []
for (_, _, sym, _, _) in PARTS:
    if sym not in used_syms:
        used_syms.append(sym)

lib = '(kicad_symbol_lib (version 20241209) (generator "gen_schematic.py") (generator_version "9.0")'
for nm in used_syms:
    lib += ' ' + sym_def(nm)
lib += ' ' + PWR_FLAG_DEF_LIB + ')'
(TREE/'wmain.kicad_sym').write_text(lib)

# ---------- schematic ----------
sch = ('(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0")'
       f' (uuid "{SHEET_UUID}") (paper "A1")'
       ' (title_block (title "Issue 292 wireless Main (ISP1807-LR / nRF52840)") (rev "S2-draft")'
       ' (comment 1 "DRAFT - NOT FOR ORDER")) (lib_symbols')
for nm in used_syms:
    sch += ' ' + sym_def(nm, for_sch=True)
sch += ' ' + PWR_FLAG_DEF + ')'

def pin_endpoints(sym, x, y):
    """returns {pinnum: (ex, ey, side)} world coords of connection points."""
    left, right = SYMBOLS[sym]
    hw = HW[sym]
    out = {}
    for (num, _), py in zip(left, pin_ys(len(left))):
        out[num] = (x - (hw + 2.54), y - py, 'L')
    for (num, _), py in zip(right, pin_ys(len(right))):
        out[num] = (x + (hw + 2.54), y - py, 'R')
    return out

items = []   # (ref, value, sym, fp, pins, x, y)
col_x, col_y = 38.1, 38.1
for (ref, value, sym, fp, pins) in PARTS:
    left, right = SYMBOLS[sym]
    maxk = max(len(left), len(right), 1)
    hh = (maxk - 1) * 1.27 + 3.81
    need = 2 * hh + 15.24
    if col_y + need > 558.8:
        col_x += 95.25; col_y = 38.1
    x, y = col_x + 25.4, col_y + hh + 5.08
    items.append((ref, value, sym, fp, pins, x, y))
    col_y += need

body = ''
labels = ''
for (ref, value, sym, fp, pins, x, y) in items:
    body += (f' (symbol (lib_id "wmain:{sym}") (at {x} {y} 0) (unit 1) (exclude_from_sim no)'
             f' (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")'
             f' (property "Reference" "{ref}" (at {x} {y - 8} 0) (effects (font (size 1 1))))'
             f' (property "Value" "{value}" (at {x} {y + 8} 0) (effects (font (size 1 1))))'
             f' (property "Footprint" "wmain:{fp}" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))'
             f' (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))'
             f' (instances (project "wmain" (path "/{SHEET_UUID}" (reference "{ref}") (unit 1)))))')
    eps = pin_endpoints(sym, x, y)
    for num, net in pins.items():
        ex, ey, side = eps[num]
        if net is None:
            labels += f' (no_connect (at {ex} {ey}) (uuid "{U()}"))'
        else:
            lx = ex - 5.08 if side == 'L' else ex + 5.08
            just = 'right' if side == 'L' else 'left'
            labels += (f' (wire (pts (xy {ex} {ey}) (xy {lx} {ey})) (stroke (width 0) (type solid)) (uuid "{U()}"))'
                       f' (label "{net}" (at {lx} {ey} 0) (effects (font (size 1 1)) (justify {just} bottom)) (uuid "{U()}"))')
# PWR_FLAGs
fx = col_x + 25.4
for i, net in enumerate(POWER_NETS):
    fy = 38.1 + i * 15.24
    body += (f' (symbol (lib_id "wmain:PWR_FLAG") (at {fx} {fy} 0) (unit 1) (exclude_from_sim no)'
             f' (in_bom no) (on_board no) (dnp no) (uuid "{U()}")'
             f' (property "Reference" "#FLG{i+1:02d}" (at {fx} {fy - 3} 0) (effects (font (size 1 1))))'
             f' (property "Value" "PWR_FLAG" (at {fx} {fy + 3} 0) (effects (font (size 1 1))))'
             f' (instances (project "wmain" (path "/{SHEET_UUID}" (reference "#FLG{i+1:02d}") (unit 1)))))')
    labels += (f' (wire (pts (xy {fx} {fy}) (xy {fx + 5.08} {fy})) (stroke (width 0) (type solid)) (uuid "{U()}"))'
               f' (label "{net}" (at {fx + 5.08} {fy} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{U()}"))')
sch += body + labels
sch += f' (sheet_instances (path "/" (page "1"))))'
(TREE/'wmain.kicad_sch').write_text(sch)
(TREE/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "wmain")(type "KiCad")(uri "${KIPRJMOD}/wmain.kicad_sym")(options "")(descr "Issue 292 symbols")))')
(TREE/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "wmain")(type "KiCad")(uri "${KIPRJMOD}/wmain.pretty")(options "")(descr "Issue 292 footprints")))')
print('schematic + symbol lib written;', len(PARTS), 'parts')
