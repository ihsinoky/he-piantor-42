"""Read saved, independently refilled boards; report KiCad plane connectivity."""
from helpers import *
import pcbnew as p
stage,router=sys.argv[1:3];label=sys.argv[3] if len(sys.argv)>3 else stage
w=A/'inspection'/label/router
b=p.LoadBoard(str(w/'main.kicad_pcb'));b.BuildConnectivity();c=b.GetConnectivity();c.RecalculateRatsnest()
refs={a.m_Uuid.AsString():f.GetReference() for f in b.GetFootprints() for a in f.Pads()}
rows=[]
for zone in b.Zones():
 pads=list(c.GetConnectedPads(zone));tracks=list(c.GetConnectedTracks(zone))
 rows.append(dict(net=zone.GetNetname(),layer=b.GetLayerName(zone.GetLayer()),filled=zone.IsFilled(),filled_area_mm2=zone.CalculateFilledArea()/1e12,directly_connected_pads=[dict(ref=refs[x.m_Uuid.AsString()],pad=x.GetNumber(),uuid=x.m_Uuid.AsString(),net=x.GetNetname()) for x in pads],directly_connected_tracks_or_vias=[dict(uuid=x.m_Uuid.AsString(),kind='via' if isinstance(x,p.PCB_VIA) else 'track',net=x.GetNetname(),layer=b.GetLayerName(x.GetLayer())) for x in tracks]))
save(w/'plane-connectivity.json',dict(utc=utc(),board_sha256=sha(w/'main.kicad_pcb'),method='KiCad CONNECTIVITY_DATA GetConnectedPads/GetConnectedTracks on reloaded independently refilled output; direct zone adjacency, not a router claim.',global_ratsnest_count=c.GetUnconnectedCount(False),zones=rows))
print(json.dumps(rows,indent=2))
