"""Verify immutable substrate and export both silkscreen derivatives."""
import json,re,shutil,hashlib
from collections import Counter
import pcbnew as p
from common import R,E,T,SOURCE,save,digest,run,environment

def xy(v):return [v.x/1e6,v.y/1e6]
def snap(b):
 tracks=[];vias=[];pads=[];edges=[]
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):vias.append(dict(uuid=t.m_Uuid.AsString(),pos=xy(t.GetPosition()),diameter_mm=t.GetWidth(p.F_Cu)/1e6,drill_mm=t.GetDrillValue()/1e6,net=t.GetNetname(),layers=list(t.GetLayerSet().Seq()),tented_front=t.IsTented(p.F_Mask),tented_back=t.IsTented(p.B_Mask)))
  else:tracks.append(dict(uuid=t.m_Uuid.AsString(),start=xy(t.GetStart()),end=xy(t.GetEnd()),width_mm=t.GetWidth()/1e6,net=t.GetNetname(),layer=b.GetLayerName(t.GetLayer())))
 for f in b.GetFootprints():
  for q in f.Pads():pads.append(dict(uuid=q.m_Uuid.AsString(),ref=f.GetReference(),number=q.GetNumber(),pos=xy(q.GetPosition()),size=xy(q.GetSize()),drill=xy(q.GetDrillSize()),angle_deg=q.GetOrientationDegrees(),attribute=int(q.GetAttribute()),shape=int(q.GetShape()),net=q.GetNetname(),layers=[b.GetLayerName(i) for i in q.GetLayerSet().Seq()]))
 for g in b.GetDrawings():
  if g.GetLayer()==p.Edge_Cuts:edges.append(dict(start=xy(g.GetStart()),end=xy(g.GetEnd()),width_mm=g.GetWidth()/1e6))
 return dict(tracks=sorted(tracks,key=str),vias=sorted(vias,key=str),pads=sorted(pads,key=str),edges=sorted(edges,key=str))

checks=[]
for pitch in (16,17):
 d=E/f'{pitch}mm';pcb=d/f'wing-{pitch}mm-silk149.kicad_pcb';src=SOURCE/f'runs/KRT-{pitch}-2L-P0300/out.kicad_pcb'
 srcbytes=src.read_bytes();new=pcb.read_bytes();idx=srcbytes.rfind(b')');tail=srcbytes[idx:]
 assert new[:idx]==srcbytes[:idx] and new[-len(tail):]==tail
 added=new[idx:-len(tail)]
 assert new[:idx]+new[-len(tail):]==srcbytes
 # Source ends at the same top-level insertion offset. Every new native drawing is F.SilkS.
 old=p.LoadBoard(str(src));b=p.LoadBoard(str(pcb));a=snap(old);z=snap(b);assert a==z
 drawings={g.m_Uuid.AsString() for g in old.GetDrawings()};extra=[g for g in b.GetDrawings() if g.m_Uuid.AsString() not in drawings]
 evidence=json.loads((d/'design-evidence.json').read_text());assert len(extra)==evidence['added_nodes']
 assert all(g.GetLayer()==p.F_SilkS for g in extra)
 assert len(list(b.GetFootprints()))==len(list(old.GetFootprints()))
 assert digest(src.with_suffix('.kicad_pro'))==digest(pcb.with_suffix('.kicad_pro'))
 inv=json.loads((SOURCE/f'KRT-{pitch}-2L-P0300-inventory.json').read_text())
 # Independently compare every #141 inventory trace with native source/derived output.
 def tk(t):return (tuple(t['start']),tuple(t['end']),t['width_mm'],t['layer'],t['net'])
 assert Counter(tk(t) for t in inv['tracks'])==Counter(tk(t) for t in z['tracks'])
 assert len(evidence['squares'])==21 and all(s['side_mm']==pitch for s in evidence['squares'])
 texts=[g.GetText() for g in extra if isinstance(g,p.PCB_TEXT)]
 assert all(texts.count(f.GetReference())==1 for f in b.GetFootprints())
 oldpre=json.loads((E/f'inputs/issue147/{pitch}mm/preflight.json').read_text())
 assert oldpre['sha256']==digest(src)
 # Reuse immutable substrate inventory only after exact source hash/native comparison above.
 pre={**oldpre,'sha256':digest(pcb),'source_sha256':digest(src),'visible_silk_count':len(extra),'findings':[]}
 save(d/'preflight.json',pre)
 save(d/'native-geometry.json',z)
 result=dict(pitch_mm=pitch,source_sha256=digest(src),derived_sha256=digest(pcb),project_byte_identical=True,source_recovered_byte_for_byte=True,insertion_offset=idx,added_bytes=len(added),only_new_F_SilkS_drawings=True,added_nodes=len(extra),tracks=len(z['tracks']),vias=len(z['vias']),pads=len(z['pads']),npth=sum(q['attribute']==int(p.PAD_ATTRIB_NPTH) for q in z['pads']),all_native_geometry_equal=True,inventory_tracks_equal=True,all_references_once=True,square_count=21)
 checks.append(result);save(d/'identity-check.json',result)
 cli=environment()['KICAD_CLI'];work=T/f'{pitch}mm';work.mkdir(exist_ok=True)
 for f in (pcb,pcb.with_suffix('.kicad_pro'),d/'fp-lib-table'):shutil.copyfile(f,work/f.name)
 active=work/pcb.name
 run(f'{pitch}mm-drc',[cli,'pcb','drc','--format','json','--severity-all','--all-track-errors','--exit-code-violations','-o',d/'drc.json',active],timeout=600)
 drc=json.loads((d/'drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
 fab=d/'gerber';fab.mkdir(exist_ok=False)
 run(f'{pitch}mm-gerbers',[cli,'pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts','--precision','6','--subtract-soldermask','-o',str(fab)+'/',active])
 run(f'{pitch}mm-drill',[cli,'pcb','export','drill','--format','excellon','--drill-origin','absolute','--excellon-units','mm','--excellon-zeros-format','decimal','--excellon-oval-format','alternate','--excellon-separate-th','--generate-report','--report-path',d/'drill-report.txt','-o',str(fab)+'/',active])
 run(f'{pitch}mm-paste-reference',[cli,'pcb','export','gerbers','--layers','F.Paste,B.Paste','-o',str(d/'paste-reference-not-for-order')+'/',active])
 assert digest(pcb)==result['derived_sha256'] and digest(active)==digest(pcb)
 print('qualified',pitch,flush=True)
save(E/'identity-checks.json',checks)
