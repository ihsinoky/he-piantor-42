#!/usr/bin/env python3
"""Stage 3 of the SWD TC2050 respin: replace the TC2030 symbol with a
10-pin TC2050 symbol in wmain.kicad_sym and wmain.kicad_sch (embedded
lib copy + JSWD instance + wiring), per the pin mapping in
tc2050/PROVENANCE.md:
  1 VTREF->SYS_3V3  2 SWDIO  3 GND  4 SWDCLK  5 GND
  6 SWO=NC  7 KEY=NC  8 TDI=NC  9 GNDDET->GND  10 RESET->RESET_N
Existing pins keep their schematic side where possible; new GND pins
get labelled wires; unused pins get no_connect markers (as pin 6 had).
"""
import re, sys, uuid

TREE = 'hardware/kicad/qualification/issue-292-wmain'

def block_span(txt, start):
    d = 0; i = start
    while True:
        c = txt[i]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: return start, i + 1
        i += 1

def replace_block(txt, start, new):
    s, e = block_span(txt, start)
    return txt[:s] + new + txt[e:]

PINS = [  # (x, angle, y, name, number)
    (-7.62, 0,   5.08, 'VTREF',  '1'),
    (-7.62, 0,   2.54, 'SWDIO',  '2'),
    (-7.62, 0,   0.00, 'GND',    '3'),
    (-7.62, 0,  -2.54, 'GNDDET', '9'),
    (-7.62, 0,  -5.08, 'RESET',  '10'),
    ( 7.62, 180, 5.08, 'SWDCLK', '4'),
    ( 7.62, 180, 2.54, 'GND',    '5'),
    ( 7.62, 180, 0.00, 'SWO',    '6'),
    ( 7.62, 180, -2.54, 'KEY',   '7'),
    ( 7.62, 180, -5.08, 'TDI',   '8'),
]

def pin_txt(x, ang, y, name, num):
    return ('(pin passive line (at %s %.2f %d) (length 2.54) '
            '(name "%s" (effects (font (size 1.0 1.0)))) '
            '(number "%s" (effects (font (size 1.0 1.0)))))'
            % (('%g' % x), y, ang, name, num))

def symbol_block(name):
    pins = ' '.join(pin_txt(*p) for p in PINS)
    return ('(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) '
            '(in_bom yes) (on_board yes) '
            '(property "Reference" "J" (at 0 10.16 0) (effects (font (size 1 1)))) '
            '(property "Value" "TC2050" (at 0 -10.16 0) (effects (font (size 1 1)))) '
            '(property "Footprint" "" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) '
            '(property "Datasheet" "" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) '
            '(symbol "TC2050_0_1" (rectangle (start -5.08 7.62) (end 5.08 -7.62) '
            '(stroke (width 0.254) (type default)) (fill (type background)))) '
            '(symbol "TC2050_1_1" %s))' % (name, pins))

# ---- 1. symbol library file ----
p = TREE + '/wmain.kicad_sym'
sym = open(p).read()
i = sym.find('(symbol "TC2030"')
assert i >= 0
sym = replace_block(sym, i, symbol_block('TC2050'))
assert 'TC2030' not in sym and '(symbol "TC2050"' in sym
open(p, 'w').write(sym)
print('kicad_sym: TC2030 -> TC2050 done')

# ---- 2. schematic ----
p = TREE + '/wmain.kicad_sch'
sch = open(p).read()

# 2a. embedded lib symbol
i = sch.find('(symbol "wmain:TC2030"')
assert i >= 0
sch = replace_block(sch, i, symbol_block('wmain:TC2050'))
print('sch: embedded lib symbol replaced')

# 2b. JSWD instance strings
j = sch.find('(symbol (lib_id "wmain:TC2030"')
assert j >= 0
s, e = block_span(sch, j)
inst = sch[s:e]
assert '"JSWD"' in inst
inst2 = (inst.replace('"wmain:TC2030"', '"wmain:TC2050"')
             .replace('"Value" "TC2030-IDC-NL"', '"Value" "TC2050-IDC-NL"')
             .replace('"Footprint" "wmain:TC2030-IDC-NL_Pads"',
                      '"Footprint" "wmain:TC2050-IDC-NL"'))
assert inst2 != inst and 'TC2030' not in inst2
sch = sch[:s] + inst2 + sch[e:]
print('sch: JSWD instance updated')

# 2c. remove old wires / labels / no_connect (exact find patterns)
OLD = [
    '(wire (pts (xy 246.38 123.18999999999998)',
    '(wire (pts (xy 246.38 125.72999999999999)',
    '(wire (pts (xy 246.38 128.26999999999998)',
    '(wire (pts (xy 261.62 123.18999999999998)',
    '(wire (pts (xy 261.62 125.72999999999999)',
    '(label "SYS_3V3" (at 241.29999999999998 123.18999999999998',
    '(label "SWDIO" (at 241.29999999999998 125.72999999999999',
    '(label "RESET_N" (at 241.29999999999998 128.26999999999998',
    '(label "SWDCLK" (at 266.7 123.18999999999998',
    '(label "GND" (at 266.7 125.72999999999999',
    '(no_connect (at 261.62 128.26999999999998',
]
spans = []
for pat in OLD:
    i = sch.find(pat)
    assert i >= 0, pat
    spans.append(block_span(sch, i))
for s, e in sorted(spans, reverse=True):
    sch = sch[:s] + sch[e:]
print('sch: 11 old wiring items removed')

# 2d. add new wiring
BASE = 125.72999999999999
def Y(dy): return repr(BASE - dy)
def wire(x1, y, x2):
    return ('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type solid)) '
            '(uuid "%s"))' % (x1, y, x2, y, uuid.uuid4()))
def label(name, x, y, just):
    return ('(label "%s" (at %s %s 0) (effects (font (size 1 1)) '
            '(justify %s bottom)) (uuid "%s"))' % (name, x, y, just, uuid.uuid4()))
def nocon(x, y):
    return '(no_connect (at %s %s) (uuid "%s"))' % (x, y, uuid.uuid4())

WEST = [  # (dy, net)  pins 1,2,3,9,10
    (5.08, 'SYS_3V3'), (2.54, 'SWDIO'), (0.0, 'GND'),
    (-2.54, 'GND'), (-5.08, 'RESET_N'),
]
EAST = [(5.08, 'SWDCLK'), (2.54, 'GND')]  # pins 4,5
NOC = [0.0, -2.54, -5.08]                 # pins 6,7,8 (east)

items = []
for dy, net in WEST:
    items.append(wire('246.38', Y(dy), '241.29999999999998'))
    items.append(label(net, '241.29999999999998', Y(dy), 'right'))
for dy, net in EAST:
    items.append(wire('261.62', Y(dy), '266.7'))
    items.append(label(net, '266.7', Y(dy), 'left'))
for dy in NOC:
    items.append(nocon('261.62', Y(dy)))

k = sch.find('(sheet_instances')
assert k >= 0
sch = sch[:k] + ' '.join(items) + ' ' + sch[k:]
open(p, 'w').write(sch)
print('sch: %d new wiring items added' % len(items))
print('OK')
