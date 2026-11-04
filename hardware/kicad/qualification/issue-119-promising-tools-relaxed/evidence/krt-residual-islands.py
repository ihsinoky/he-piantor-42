from common import *
import pcbnew as p
w=E/'inspection/main4/krt';b=p.LoadBoard(str(w/'main.kicad_pcb'));b.BuildConnectivity();c=b.GetConnectivity()
objects={t.m_Uuid.AsString():t for t in b.GetTracks()};pads={pad.m_Uuid.AsString():(f.GetReference(),pad.GetNumber(),pad) for f in b.GetFootprints() for pad in f.Pads()};objects.update({k:v[2] for k,v in pads.items()})
rows=[]
for edge in json.loads((w/'drc.json').read_text())['unconnected_items']:
 ends=[]
 for item in edge['items']:
  start=objects[item['uuid']];todo=[start];seen=set();found={}
  while todo:
   obj=todo.pop();uid=obj.m_Uuid.AsString()
   if uid in seen:continue
   seen.add(uid)
   if uid in pads:
    ref,num,pad=pads[uid];found[uid]=dict(ref=ref,pad=num,net=pad.GetNetname(),uuid=uid,pos_mm=[p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)])
   todo.extend(c.GetConnectedPads(obj));todo.extend(c.GetConnectedTracks(obj))
  ends.append(dict(drc_endpoint=item,connected_pad_component=list(found.values()),connected_copper_items=len(seen)))
 rows.append(dict(endpoints=ends))
save(w/'residual-connected-pad-components.json',dict(utc=utc(),method='Breadth-first KiCad GetConnectedPads/GetConnectedTracks over the saved independently refilled PCB. V3V3 has no zone; no nearest-pad attribution.',rows=rows))
print(json.dumps(rows,indent=2))
