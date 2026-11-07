"""Native review schematic from explicit circuit-source.py, never read a PCB.
All numbered electrical pins are displayed separately with net labels and NCs.
"""
from common import *
import importlib.util,uuid
spec=importlib.util.spec_from_file_location('circuit',E/'circuit-source.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
components=m.components
U=lambda:str(uuid.uuid4())
Q=lambda s:json.dumps(str(s),ensure_ascii=False)
root=U();libs=[];instances=[];connections=[]
font='(effects (font (size 1.0 1.0)))'
def prop(name,value,x,y,hide=False):return f'(property {Q(name)} {Q(value)} (at {x} {y} 0) (effects (font (size 1 1))'+(' (hide yes)' if hide else '')+'))'
# MCU gets a dedicated left column; remaining devices use a readable 7x9 grid.
refs=['U1']+sorted(r for r in components if r!='U1')
for i,ref in enumerate(refs):
 c=components[ref];pins=sorted(c['pins'],key=lambda n:int(n));N=len(pins);height=max(10,(N+1)*2.54);name='Rev4:'+ref
 x,y=(65,125) if i==0 else (210+((i-1)%7)*140,55+((i-1)//7)*82)
 symbols=[]
 for j,n in enumerate(pins):
  yy=round((N-1)*1.27-j*2.54,6);role=c['pin_roles'].get(n,{});pn=role.get('name',n);kind=role.get('role','passive')
  symbols.append(f'(pin {kind} line (at -15.24 {yy} 0) (length 5.08) (name {Q(pn)} {font}) (number {Q(n)} {font}))')
  px=round(x-15.24,6);py=round(y-yy,6);end=round(px-7.62,6);nnet=c['pins'][n]
  if nnet is None:
   connections.append(f'(no_connect (at {px} {py}) (uuid {Q(U())}))')
  else:
   connections.append(f'(wire (pts (xy {px} {py}) (xy {end} {py})) (stroke (width 0) (type default)) (uuid {Q(U())}))')
   connections.append(f'(label {Q(nnet)} (at {end} {py} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {Q(U())}))')
 lib=f'(symbol {Q(name)} (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) '+prop('Reference',ref,0,height/2+3)+prop('Value',c['value'],0,-height/2-3)+f' (symbol {Q(ref+"_0_1")} (rectangle (start -10.16 {height/2}) (end 22.86 {-height/2}) (stroke (width .254) (type default)) (fill (type background)))) (symbol {Q(ref+"_1_1")} '+''.join(symbols)+'))'
 libs.append(lib)
 inst=f'(symbol (lib_id {Q(name)}) (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid {Q(U())}) '+prop('Reference',ref,x,y-height/2-3)+prop('Value',c['value'],x,y+height/2+3)+prop('Footprint','Rev4:'+ref,x,y,True)+prop('SourceID',c['source'],x,y,True)+f'(instances (project "main" (path {Q("/"+root)} (reference {Q(ref)}) (unit 1)))))'
 instances.append(inst)
w=E/'schematic';w.mkdir(exist_ok=True)
text=f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid {Q(root)}) (paper "A0") (title_block (title "Issue 196 Main Rev.4 / UDB / forced-PWM 5.2V")) (lib_symbols '+''.join(libs)+')'+''.join(instances+connections)+')\n'
(w/'main.kicad_sch').write_text(text)
save(E/'schematic-source.json',dict(utc=now(),author='Explicit independent circuit-source.py; per-pin box schematic',components=len(components),logical_contract_sha256=digest(E/'logical-contract.json'),schematic_sha256=digest(w/'main.kicad_sch'),physical_footprints='Rev4 snapshots; native pcb layouts are separate from logical schematic'))
print('Native schematic authored',len(components),'components')
