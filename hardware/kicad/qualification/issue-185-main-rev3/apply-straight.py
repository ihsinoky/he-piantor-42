from common import *
import pcbnew as p,shutil,uuid
old=E.parent/'issue-175-main-dual-wing-final2';w=E/'straight33';w.mkdir(exist_ok=True)
src=old/'inspection/final/main.kicad_pcb'
assert digest(src)=='acab039f3b5f5ea30500d2f8537e320e198f881c227a3c3042753fc021c30f1c'
shutil.copyfile(old/'inputs/final/main.kicad_pro',w/'main.kicad_pro')
b=p.LoadBoard(str(src));vias={v.m_Uuid.AsString():v for v in b.GetTracks() if isinstance(v,p.PCB_VIA)}
probes=json.loads((E/'source183/move-probes.json').read_text());changes=[]
for r in probes:
 pos=r['straight_stub_candidate_mm']
 if pos is None:continue
 v=vias[r['via_uuid']];assert [p.ToMM(v.GetPosition().x),p.ToMM(v.GetPosition().y)]==r['origin_mm']
 v.SetPosition(p.VECTOR2I(round(pos[0]*1e6),round(pos[1]*1e6)))
 stubs=[];seen=set()
 for a in r['anchors']:
  key=(a['layer'],tuple(a['position_mm']),a['width_mm'])
  if key in seen:continue
  seen.add(key);t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(round(a['position_mm'][0]*1e6),round(a['position_mm'][1]*1e6)));t.SetEnd(v.GetPosition());t.SetWidth(p.FromMM(a['width_mm']));t.SetLayer(b.GetLayerID(a['layer']));t.SetNetCode(v.GetNetCode());b.Add(t)
  stubs.append(dict(uuid=t.m_Uuid.AsString(),anchor=a))
 changes.append(dict(via_uuid=r['via_uuid'],origin_mm=r['origin_mm'],position_mm=pos,net=r['net'],stubs=stubs))
assert len(changes)==33
assert p.SaveBoard(str(w/'before-fill.kicad_pcb'),b)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
save(w/'changes.json',changes);save(w/'provenance.json',dict(source_sha256=digest(src),before_fill_sha256=digest(w/'before-fill.kicad_pcb'),refilled_sha256=digest(w/'main.kicad_pcb'),moved_vias=33,global_routing_attempts=0))
print('Moved 33 vias, added',sum(len(c['stubs']) for c in changes),'stubs; refilled')
