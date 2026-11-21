#!/usr/bin/env python3
"""Generate the Issue #303 Stage 1 schematic (pwr.kicad_sch) + symbol/footprint libs.
Repo pattern: short wire stub + local label per pin (as in issue-288/292 trees)."""
import uuid, os, json

TREE = os.path.expanduser("~/workspace/projects/he-piantor-pwr/hardware/kicad/qualification/issue-303-pwr")
os.makedirs(TREE + "/pwr.pretty", exist_ok=True)

def u(): return str(uuid.uuid4())

SHEET_UUID = u()

def sym_def(name, ref, pins, body=(-3.81, 5.08, 3.81, -5.08), fp=""):
    """pins: list of (num, pname, x, y, rot, type)"""
    pin_s = ""
    for num, pname, x, y, rot, ptype in pins:
        pin_s += (f'(pin {ptype} line (at {x} {y} {rot}) (length 5.08) '
                  f'(name "{pname}" (effects (font (size 1.0 1.0)))) '
                  f'(number "{num}" (effects (font (size 1.0 1.0))))) ')
    return (f'(symbol "pwr:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) '
            f'(property "Reference" "{ref}" (at 0 7.62 0) (effects (font (size 1 1)))) '
            f'(property "Value" "{name}" (at 0 -7.62 0) (effects (font (size 1 1)))) '
            f'(property "Footprint" "{fp}" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) '
            f'(property "Datasheet" "" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) '
            f'(symbol "{name}_0_1" (rectangle (start {body[0]} {body[1]}) (end {body[2]} {body[3]}) '
            f'(stroke (width 0.254) (type default)) (fill (type background)))) '
            f'(symbol "{name}_1_1" {pin_s}))')

P2 = [(1, "P1", -5.08, 2.54, 0, "passive"), (2, "P2", -5.08, -2.54, 0, "passive")]
CELL_PINS = [(1, "POS", -5.08, 2.54, 0, "passive"), (2, "NEG", -5.08, -2.54, 0, "passive")]

lib_symbols = "\n".join([
    sym_def("CELL_AA", "BT", CELL_PINS, fp="pwr:CELL_AA_CONTACT_PAIR"),
    sym_def("PTC_1206", "F", P2, fp="pwr:PTC_1206"),
    sym_def("GH_2P", "J", P2, fp="pwr:GH_2P"),
    sym_def("SW_PADS", "J", P2, fp="pwr:SW_PADS_2P"),
    sym_def("TESTPOINT", "TP", [(1, "TP", -5.08, 0.0, 0, "passive")], body=(-3.81, 2.54, 3.81, -2.54), fp="pwr:TESTPOINT"),
])

# instances: (lib, ref, value, x, y, [(pinnum, netlabel), ...]) pin offsets: pin1 (-5.08,+2.54), pin2 (-5.08,-2.54); TP pin (-5.08,0)
Y = 60.96
instances = [
    ("CELL_AA", "BT1", "AA_NiMH_CELL1_WEST", 40.64, Y, [(1, "BRIDGE_N"), (2, "PACK_NEG")]),
    ("CELL_AA", "BT2", "AA_NiMH_CELL2_MID", 76.20, Y, [(1, "BRIDGE_S"), (2, "BRIDGE_N")]),
    ("CELL_AA", "BT3", "AA_NiMH_CELL3_EAST", 111.76, Y, [(1, "PACK_POS_RAW"), (2, "BRIDGE_S")]),
    ("PTC_1206", "F1", "1206L050/24WR", 147.32, Y, [(1, "PACK_POS_RAW"), (2, "PACK_POS_FUSED")]),
    ("SW_PADS", "J2", "SW_LOOP_TO_WALL_SWITCH", 182.88, Y, [(1, "PACK_POS_FUSED"), (2, "VBAT_OUT")]),
    ("GH_2P", "J1", "BM02B-GHS-TBT", 218.44, Y, [(1, "VBAT_OUT"), (2, "PACK_NEG")]),
    ("TESTPOINT", "TP1", "TP_PACK_POS", 147.32, 91.44, [(1, "PACK_POS_RAW")]),
    ("TESTPOINT", "TP2", "TP_PACK_NEG", 40.64, 91.44, [(1, "PACK_NEG")]),
]
PIN_OFF = {1: (-5.08, 2.54), 2: (-5.08, -2.54)}
TP_OFF = (-5.08, 0.0)

body = []
for lib, ref, val, x, y, nets in instances:
    iu = u()
    props = (f'(property "Reference" "{ref}" (at {x} {y-8.89} 0) (effects (font (size 1 1)))) '
             f'(property "Value" "{val}" (at {x} {y+8.89} 0) (effects (font (size 1 1)))) '
             f'(property "Footprint" "" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes))) '
             f'(property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))')
    body.append(f'(symbol (lib_id "pwr:{lib}") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{iu}") {props} '
                f'(instances (project "pwr" (path "/{SHEET_UUID}" (reference "{ref}") (unit 1)))))')
    for pinnum, net in nets:
        off = TP_OFF if lib == "TESTPOINT" else PIN_OFF[pinnum]
        px, py = x + off[0], y - off[1]  # schematic y is inverted vs symbol y
        ex = px - 7.62
        body.append(f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type solid)) (uuid "{u()}"))')
        body.append(f'(label "{net}" (at {ex} {py} 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "{u()}"))')

notes = [
    (25.4, 25.4, "Issue #303 wireless power board - Stage 1 CIRCUIT DESIGN (DRAFT - NOT FOR ORDER - NO LAYOUT)"),
    (25.4, 30.48, "3x AA NiMH in series. BRIDGE_N / BRIDGE_S are copper bridges on the floor board; PACK_POS_RAW returns along the east edge (return pour)."),
    (25.4, 35.56, "F1 = series PTC. J2 = pads to the off-board bay-wall slide switch (SS-12D10 class, >=0.5 A); short J2 only for bench use."),
    (25.4, 40.64, "J1 pin1 = VBAT_OUT (+), pin2 = PACK_NEG (-): matches Main JBATT (BM02B-GHS-TBT, pin1 VBAT+ / pin2 GND) on a straight GH-GH cable."),
]
for x, y, t in notes:
    body.append(f'(text "{t}" (at {x} {y} 0) (effects (font (size 1.27 1.27))) (uuid "{u()}"))')

sch = (f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{SHEET_UUID}") '
       f'(paper "A3") (title_block (title "Issue 303 wireless power board (3x AA NiMH floor board)") (rev "S1-draft") '
       f'(comment 1 "DRAFT - NOT FOR ORDER - STAGE 1 CIRCUIT ONLY")) '
       f'(lib_symbols {lib_symbols}) ' + " ".join(body) + ")")
open(TREE + "/pwr.kicad_sch", "w").write(sch)
open(TREE + "/pwr.kicad_sym", "w").write(f'(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") (generator_version "9.0") {lib_symbols.replace("(symbol " + chr(34) + "pwr:", "(symbol " + chr(34))})')

open(TREE + "/sym-lib-table", "w").write('(sym_lib_table (version 7) (lib (name "pwr")(type "KiCad")(uri "${KIPRJMOD}/pwr.kicad_sym")(options "")(descr "Issue 303 symbols")))')
open(TREE + "/fp-lib-table", "w").write('(fp_lib_table (version 7) (lib (name "pwr")(type "KiCad")(uri "${KIPRJMOD}/pwr.pretty")(options "")(descr "Issue 303 footprints")))')
print("schematic written, sheet uuid", SHEET_UUID)
