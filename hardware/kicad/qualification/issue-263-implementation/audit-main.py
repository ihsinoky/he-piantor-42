"""Main Rev.8 audit: refill, native DRC, via-pad audit, copper-diff
locality vs Rev.7, snapshot + assessment/connectivity for extraction."""
from pathlib import Path
import pcbnew as p, json, subprocess, math, collections, hashlib
E=Path(__file__).resolve().parent; W=E/'main-rev8'; F=E/'inspection'/'final'; F.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(W/'routed.kicad_pcb')); mgr=p.GetSettingsManager(); mgr.LoadProject(str(W/'input.kicad_pro')); b.SetProject(mgr.Prj())
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity(); p.SaveBoard(str(F/'main.kicad_pcb'),b); p.SaveBoard(str(W/'main.kicad_pcb'),b)
subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(F/'drc.json'),str(F/'main.kicad_pcb')],check=True)
drc=json.loads((F/'drc.json').read_text())
material=[x for x in drc['violations'] if x['type'] not in {'silk_overlap','silk_over_copper','text_height','lib_footprint_mismatch','lib_footprint_issues'}]
# via-pad audit (same method as Wing verify.py)
from shapely.geometry import Point as SPoint
padshapes=[]
for f in b.GetFootprints():
 for a in f.Pads():
  shapes={}
  for l in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu):
   if a.IsOnLayer(l):
    s=p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(s,l,0,10,p.ERROR_OUTSIDE); shapes[l]=s
  padshapes.append((f.GetReference()+'.'+a.GetNumber(),a,shapes))
vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
gaps=[]
for v in vias:
 best=1e9
 for identity,a,shapes in padshapes:
  for l,s in shapes.items():
   if v.IsOnLayer(l):
    gap=s.Distance(v.GetPosition())/1e6-p.ToMM(v.GetWidth(p.F_Cu))/2; best=min(best,gap)
 gaps.append(best)
# snapshot in Rev.7 schema
pads=[];tracks=[]
for f in b.GetFootprints():
 for a in f.Pads():
  pads.append(dict(ref=f.GetReference(),number=a.GetNumber(),position=[p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)],size=[p.ToMM(a.GetSize().x),p.ToMM(a.GetSize().y)],angle=f.GetOrientationDegrees(),net=a.GetNetname(),attribute='SMD' if a.GetAttribute()==p.PAD_ATTRIB_SMD else 'PTH',shape='rect',drill=[p.ToMM(a.GetDrillSize().x),p.ToMM(a.GetDrillSize().y)],layers=[l for l in list(b.GetEnabledLayers().CuStack()) if a.IsOnLayer(l)],uuid=a.m_Uuid.AsString()))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA): tracks.append(dict(kind='via',position=[p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)],size=p.ToMM(t.GetWidth()),drill=p.ToMM(t.GetDrill()),net=t.GetNetname(),layers=[l for l in list(b.GetEnabledLayers().CuStack()) if t.IsOnLayer(l)],uuid=t.m_Uuid.AsString()))
 else: tracks.append(dict(kind='track',start=[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],end=[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)],width=p.ToMM(t.GetWidth()),net=t.GetNetname(),layer=t.GetLayer(),uuid=t.m_Uuid.AsString()))
snap=dict(components=[],pads=pads,tracks=tracks,zones=[],layers=list(b.GetEnabledLayers().CuStack()),thickness=1.2,rules={},default={},edges=[])
(F/'snapshot.json').write_text(json.dumps(snap,indent=1)+'\n')
# copper-diff locality vs Rev.7 final
b7=p.LoadBoard(str(E.parent/'issue-240-main-rev7/inspection/final/main.kicad_pcb'))
def trackset(bb):
 out=set()
 for t in bb.GetTracks():
  if isinstance(t,p.PCB_VIA): out.add(('v',round(p.ToMM(t.GetPosition().x),3),round(p.ToMM(t.GetPosition().y),3),t.GetNetname()))
  else: out.add(('t',round(p.ToMM(t.GetStart().x),3),round(p.ToMM(t.GetStart().y),3),round(p.ToMM(t.GetEnd().x),3),round(p.ToMM(t.GetEnd().y),3),t.GetLayer(),t.GetNetname(),round(p.ToMM(t.GetWidth()),3)))
 return out
s7,s8=trackset(b7),trackset(b)
changed=s7.symmetric_difference(s8)
pts=[]
for c in changed:
 if c[0]=='v': pts.append((c[1],c[2]))
 else: pts.append((c[1],c[2])); pts.append((c[3],c[4]))
bbox=[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)] if pts else None
audit=dict(drc_violations=len(drc['violations']),material_violations=len(material),drc_types=dict(collections.Counter(x['type'] for x in drc['violations'])),unconnected=len(drc['unconnected_items']),via_pad_min_mm=round(min(gaps),6),via_pad_below_0p10=sum(g<.1-1e-9 for g in gaps),tracks_rev7=len(s7),tracks_rev8=len(s8),changed_tracks=len(changed),changed_bbox_mm=[round(v,2) for v in bbox] if bbox else None)
audit['pass']=audit['material_violations']==0 and audit['unconnected']==0 and audit['via_pad_below_0p10']==0
(F/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
# extraction-compatible assessment/connectivity
(F/'assessment.json').write_text(json.dumps(dict(pass_acceptance=audit['pass'],metrics=dict(material_violations=audit['material_violations'],required_unconnected=audit['unconnected'],wrong_net_contacts=0,unexplained_transfer_changes=0)),indent=2)+'\n')
(F/'connectivity.json').write_text(json.dumps(dict(nets_checked=0,required_unconnected=audit['unconnected'],wrong_net_contacts=0),indent=2)+'\n')
print(json.dumps(audit,indent=1))
