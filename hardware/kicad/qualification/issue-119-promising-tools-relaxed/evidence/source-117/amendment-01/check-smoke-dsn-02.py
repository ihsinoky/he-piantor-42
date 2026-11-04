"""Read only: explicit four-layer roles, then exact outer-layer projection parity.

The historical two-layer DSN is already independently reconciled against native
geometry by #115. Equality of all projected AST records proves unchanged pin
positions/shapes, placement/faces/values, networks, outline, rules and wiring.
Every discarded inner-layer shape must be an exact copy of its outer PTH shape.
"""
from helpers import *
import sexpdata as sx
import re,copy,collections,importlib.util
def children(t,tag):return [x for x in t if isinstance(x,list) and x and str(x[0])==tag]
def one(t,tag):
 x=children(t,tag);assert len(x)==1,(tag,len(x));return x[0]
def parse(text):
 text=re.sub(r'(?<![\w"])(?:Round|Rect|Oval)\[(?:T|A|B)\]Pad_[^\s()"]+',lambda m:json.dumps(m.group()),text)
 return sx.loads(text.replace('(string_quote ")','(string_quote quote_character)'))
old=R/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01'
spec=importlib.util.spec_from_file_location('restore',old/'restore-clearance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results={}
for stage in ['smoke']:
 w=A/'inputs'/'smoke-02';raw=(w/'raw.dsn').read_bytes();fixed,mutation=m.restore(raw)
 (w/'corrected.dsn').write_bytes(fixed);save(w/'dsn-rule-restoration.json',mutation)
 t=parse(fixed.decode());s=one(t,'structure');layers=children(s,'layer')
 assert [(str(x[1]),str(one(x,'type')[1])) for x in layers]==[('F.Cu','signal'),('In1.Cu','power'),('In2.Cu','signal'),('B.Cu','signal')]
 planes=children(s,'plane');assert len(planes)==1
 if planes:assert str(planes[0][1])=='N' and str(one(planes[0],'polygon')[1])=='In1.Cu'
 native=parse((w/'main.kicad_pcb').read_text())
 native_nets={str(x[2]) for x in children(native,'net') if str(x[2])}
 dsn_nets={str(x[1]) for x in children(one(t,'network'),'net')};assert native_nets==dsn_nets
 extras=[];projected=copy.deepcopy(t);ps=one(projected,'structure')
 ps[:]=[x for x in ps if not (isinstance(x,list) and x and (str(x[0])=='plane' or str(x[0])=='layer' and str(x[1]) in ['In1.Cu','In2.Cu']))]
 for l in children(ps,'layer'):
  if str(l[1])=='B.Cu':one(one(l,'property'),'index')[1]=1
 lib=one(projected,'library')
 for pad in children(lib,'padstack'):
  inner=[x for x in children(pad,'shape') if str(x[1][1]) in ['In1.Cu','In2.Cu']]
  if inner:
   outer=[x for x in children(pad,'shape') if str(x[1][1]) in ['F.Cu','B.Cu']]
   assert len(inner)==2 and len(outer)==2
   assert all([x[1][0]]+x[1][2:]==[outer[0][1][0]]+outer[0][1][2:] for x in inner+outer)
   extras.extend(copy.deepcopy(inner));pad[:]=[x for x in pad if x not in inner]
 for image in children(lib,'image'):
  inner=[x for x in children(image,'keepout') if str(x[2][1]) in ['In1.Cu','In2.Cu']]
  for x in inner:
   assert any(x[:2]+[[x[2][0],sx.Symbol('F.Cu')]+x[2][2:]]==o for o in children(image,'keepout'))
  extras.extend(copy.deepcopy(inner));image[:]=[x for x in image if x not in inner]
 def rename(n):
  if isinstance(n,list):return [rename(x) for x in n]
  if isinstance(n,str) and n=='Via[0-3]_600:300_um':return 'Via[0-1]_600:300_um'
  return n
 projected=rename(projected)
 reference=R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs'/stage/'corrected.dsn'
 baseline=parse(reference.read_text());projected[1]=baseline[1]
 # Exact AST sequence equality is stronger than unordered inventory equality.
 same=projected==baseline
 save(w/'dsn-projection.json',dict(utc=utc(),pass_=same,baseline=str(reference.relative_to(R)),baseline_sha256=sha(reference),new_sha256=sha(w/'corrected.dsn'),roles=[dict(name=str(x[1]),type=str(one(x,'type')[1])) for x in layers],planes=planes,inner_PTH_and_NPTH_extensions=extras,full_native_net_inventory=sorted(native_nets),exact_projected_AST_equals_previously_verified_DSN=same,scope='Readback equality only; no router execution, no smoke acceptance'))
 if not same:
  (w/'projected-ast.txt').write_text(sx.dumps(projected));(w/'baseline-ast.txt').write_text(sx.dumps(baseline))
 assert same,stage
 results[stage]=dict(dsn_readback_pass=True,net_inventory_match=True,plane_GND_present=bool(planes),native_geometry_via_transitive_exact_AST_equality=True)
save(A/'dsn-equivalence-02.json',dict(utc=utc(),inputs=results,overall_gate_pass=True,reason='Amendment 01: smoke-only N plane; no added or renamed nets.'))
