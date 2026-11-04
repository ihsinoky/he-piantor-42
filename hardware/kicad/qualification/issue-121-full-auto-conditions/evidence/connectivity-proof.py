from common import *
import pcbnew as p
w=E/'inspection/main-cell1/krt';b=p.LoadBoard(str(w/'main.kicad_pcb'));b.BuildConnectivity();c=b.GetConnectivity()
pads={pad.m_Uuid.AsString():(f.GetReference(),pad.GetNumber(),pad) for f in b.GetFootprints() for pad in f.Pads()}
start=next(pad for ref,num,pad in pads.values() if ref=='U1' and num=='48');todo=[start];seen=set();found=[]
while todo:
 obj=todo.pop();uid=obj.m_Uuid.AsString()
 if uid in seen:continue
 seen.add(uid)
 if uid in pads:
  ref,num,pad=pads[uid];found.append(dict(ref=ref,pad=num,net=pad.GetNetname(),uuid=uid))
 todo.extend(c.GetConnectedPads(obj));todo.extend(c.GetConnectedTracks(obj))
assert any(x['ref']=='U1' and x['pad']=='49' for x in found)
assert any(x['ref']=='U4' and x['pad']=='5' for x in found)
assert all(x['net']=='V3V3' for x in found)
save(w/'V3V3-connected-component.json',dict(utc=utc(),method='KiCad GetConnectedPads/GetConnectedTracks from U1.48, no nearest-neighbour inference',pads=found,copper_and_pad_objects=len(seen),U1_48_49_and_U4_5_connected=True))
