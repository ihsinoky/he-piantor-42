"""Assert immutable Rev.3 geometry and pin identities; emit native pad obstacle map."""
from pathlib import Path
import json,hashlib,importlib.util
import pcbnew as p
from shapely.affinity import affine_transform
from shapely.geometry import mapping,box
E=Path(__file__).resolve().parent;ROOT=E.parents[3];BASE=E.parent/'issue-200-wing-rev3'
spec=importlib.util.spec_from_file_location('v',BASE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
results=[];parents=[]
for w in sorted(E.glob('wing-rev4-*')):
 src=BASE/w.name.replace('rev4','rev3');b=p.LoadBoard(str(w/'input.kicad_pcb'));old=p.LoadBoard(str(src/'input.kicad_pcb'));parents.extend([b,old]);new=v.shape_signature(b);before=v.shape_signature(old)
 ds=json.loads((w/'definition.json').read_text());os=json.loads((src/'definition.json').read_text());assert ds['keys']==os['keys'];assert ds['outline_mm']==os['outline_mm'];assert ds['mounting_holes']==os['mounting_holes']
 fixed=[k for k in before if k.startswith(('U_H','C_H','MH_','H1','H2','H3','H4'))]
 assert all(new[k]==before[k] for k in fixed)
 def edges(bb):return sorted((v.xy(d.GetStart()),v.xy(d.GetEnd())) for d in bb.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
 assert edges(b)==edges(old)
 for c in ds['components']:
  assert new[c['reference']]['side']==p.B_Cu
  assert {a.GetNumber():a.GetNetname() or None for f in b.GetFootprints() if f.GetReference()==c['reference'] for a in f.Pads()}==c['pins']
 tr=json.loads((ROOT/f'hardware/case/issue-228-final/{int(ds["pitch_mm"])}mm/dimensions.json').read_text())['wing_transforms'][w.name.split('-')[-1]];m=tr['matrix'];t=tr['translation'];af=[m[0][0],m[0][1],m[1][0],m[1][1],*t]
 pads=[]
 for f in b.GetFootprints():
  for a in f.Pads():
   # Include NPTH even though nonconductive. Local frame is x-100,100-y.
   g=v.padgeom(a,p.B_Cu if a.IsOnLayer(p.B_Cu) else p.F_Cu)
   g=affine_transform(g,[1,0,0,-1,-100,100]);g=affine_transform(g,af)
   pads.append({'id':f.GetReference()+'.'+a.GetNumber(),'geometry':mapping(g),'npth':a.GetAttribute()==p.PAD_ATTRIB_NPTH})
 v.save(w/'pad-obstacles.json',pads)
 results.append(dict(variant=w.name,keys_invariant=True,outline_invariant=True,mounts_invariant=True,sensor_and_local_cap_pad_poses_invariant=True,fixed_footprints=len(fixed),component_pin_nets_unchanged=True,top_electrical_footprints=0,bottom_electrical_footprints=len(ds['components']),purchased_placements=sum(c['kind']!='testpoint' for c in ds['components']),source_sha256=hashlib.sha256((src/'input.kicad_pcb').read_bytes()).hexdigest(),placement_sha256=hashlib.sha256((w/'input.kicad_pcb').read_bytes()).hexdigest()))
mainpath=E.parent/'issue-226-main-rev6/inspection/final/main.kicad_pcb';main=p.LoadBoard(str(mainpath));assert len(list(main.GetFootprints()))==62;assert all(f.GetLayer()==p.F_Cu for f in main.GetFootprints())
mainrows=[]
for f in main.GetFootprints():
 if f.GetReference().startswith('H'):continue
 bb=f.GetBoundingBox(False,False);g=box(bb.GetX()/1e6-100,bb.GetY()/1e6-70,(bb.GetX()+bb.GetWidth())/1e6-100,(bb.GetY()+bb.GetHeight())/1e6-70)
 mainrows.append({'ref':f.GetReference(),'geometry':mapping(g),'height_mm':8 if f.GetReference() in ('J2','J3') else 5,'basis':'actual Rev6 native footprint bbox; conservative 5mm height, GH 8mm reserved'})
v.save(E/'main-native-obstacles.json',mainrows)
v.save(E/'main-unchanged.json',{'path':str(mainpath.relative_to(ROOT)),'sha256':hashlib.sha256(mainpath.read_bytes()).hexdigest(),'F_Cu_footprints':62,'B_Cu_footprints':0,'changed':False})
v.save(E/'placement-verification.json',results);print('Placement invariants pass',len(results))
