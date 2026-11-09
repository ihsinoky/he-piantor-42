"""Read-only inspection of Issue196 Phase B PCB, XML netlist and assembly BOM.

Run with the existing KiCad9 pcbnew runtime; TMPDIR and XDG_* must point into
.issue221-runtime. Never imports the older runners (they create scratch dirs).
"""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew

E = Path(__file__).resolve().parent
R = E.parents[3]
B = R / 'hardware/kicad/qualification/issue-196-main-rev4-phaseb'
pcb = B / 'inspection/final/main.kicad_pcb'
xml = B / 'schematic/main.net.xml'
bom = B / 'manufacturing/BOM.csv'
board = pcbnew.LoadBoard(str(pcb))
j4 = next(f for f in board.GetFootprints() if f.GetReference() == 'J4')
pcb_pins = {p.GetNumber(): p.GetNetname() for p in j4.Pads() if p.GetNumber()}
tree = ET.parse(xml)
xml_pins = {}
for net in tree.findall('.//nets/net'):
    for node in net.findall('node'):
        if node.get('ref') == 'J4':
            xml_pins[node.get('pin')] = net.get('name')
expected = {'1': 'VBUS', '2': 'USB_DM_ESD', '3': 'USB_DP_ESD', '4': 'GND'}
normalized_xml_pins = {pin: name.removeprefix('/') for pin, name in xml_pins.items()}
row = next(r for r in csv.DictReader(bom.open()) if r['Designator'] == 'J4')
assert pcb_pins == normalized_xml_pins == expected, (pcb_pins, xml_pins)
assert row['LCSC Part #'] == 'C160404'
assert j4.GetValue() == row['Comment'] == 'SM04B-SRSS-TB(LF)(SN)'
data = {
    'status': 'rev4_input_identified_only',
    'kicad_version': pcbnew.GetBuildVersion(),
    'inputs': {str(p.relative_to(R)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in [pcb, xml, bom]},
    'J4': {'value': j4.GetValue(), 'footprint': str(j4.GetFPID().GetLibNickname()) + ':' + str(j4.GetFPID().GetLibItemName()),
           'position_mm': [j4.GetPosition().x / 1e6, j4.GetPosition().y / 1e6],
           'rotation_degrees': j4.GetOrientationDegrees(),
           'pcb_pins': pcb_pins, 'xml_pins_raw': xml_pins,
           'xml_pins_normalized_root_sheet_slash': normalized_xml_pins, 'bom_row': row},
    'candidate': {'manufacturer': 'Molex', 'MPN': '781710004',
                  'LCSC': 'C588524', 'fly_pin_nets': None,
                  'status': 'not_assigned_pending_primary_pinout'},
    'assertions_passed': True,
}
(E / 'input-contract.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(data, ensure_ascii=False, indent=2))
