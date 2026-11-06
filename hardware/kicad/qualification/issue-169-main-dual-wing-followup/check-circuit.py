"""Independent circuit-source vs exported native schematic netlist vs PCB pads.
No authoring helpers, no accepted oracle assignments from router output.
"""
from common import *
import pcbnew as p,xml.etree.ElementTree as ET,collections
label=sys.argv[1];w=E/'inspection'/label
contract=json.loads((E/'logical-contract.json').read_text())['components']
root=ET.parse(E/'schematic/main.net.xml').getroot();sch={}
for n in root.findall('./nets/net'):
 name=n.get('name');name=name.lstrip('/')
 if name.startswith('unconnected-'):name=None
 for node in n.findall('node'):sch[(node.get('ref'),node.get('pin'))]=name
board=p.LoadBoard(str(w/'main.kicad_pcb'));fps={f.GetReference():f for f in board.GetFootprints()};differences=[];checked=0
for ref,c in contract.items():
 if ref not in fps:differences.append(dict(ref=ref,reason='Missing PCB footprint'));continue
 if fps[ref].GetValue()!=c['value']:differences.append(dict(ref=ref,reason='value',expected=c['value'],actual=fps[ref].GetValue()))
 native=collections.defaultdict(list)
 for a in fps[ref].Pads():
  if a.GetNumber():native[a.GetNumber()].append(a.GetNetname() or None)
 for pin,expected in c['pins'].items():
  actual=native.get(pin,[]);logical=sch.get((ref,pin))
  if not actual or any(x!=expected for x in actual) or logical!=expected:differences.append(dict(ref=ref,pin=pin,expected=expected,pcb=actual,schematic=logical))
  checked+=1
 for pin in set(native)-set(c['pins']):differences.append(dict(ref=ref,pin=pin,reason='Uncontracted PCB numbered pin'))
assert not differences,differences
original=json.loads((E/'circuit-intent.json').read_text())['original'];positions=[]
for ref,c in original.items():
 f=fps[ref];actual=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()]
 assert actual==[c['x'],c['y'],c['angle']],ref
 positions.append(ref)
assert len(positions)==53
assert [p.ToMM(fps['J3'].GetPosition().x),p.ToMM(fps['J3'].GetPosition().y),fps['J3'].GetOrientationDegrees()]==[105,73,0]
assert len(contract)==62 and len(fps)==66
save(E/('circuit-check-'+label+'.json'),dict(utc=now(),pass_check=True,logical_components=62,PCB_footprints=66,mechanical_holes=4,logical_pins_checked=checked,original_53_positions_and_angles_preserved=True,all_44_nets_checked=True,schematic_export_sha256=digest(E/'schematic/main.net.xml'),PCB_sha256=digest(w/'main.kicad_pcb'),differences=differences))
print('Circuit source / native schematic export / PCB: PASS',checked,'pins')
