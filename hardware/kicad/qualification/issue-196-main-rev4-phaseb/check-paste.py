from common import *
import pcbnew as p
b=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'));vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)];graphics=list(b.GetDrawings())+[g for f in b.GetFootprints() for g in f.GraphicalItems()];rows=[]
for v in vias:
 hits=[]
 disk=p.SHAPE_CIRCLE(v.GetPosition(),v.GetWidth(p.F_Cu)//2);hole=p.SHAPE_CIRCLE(v.GetPosition(),v.GetDrillValue()//2)
 for layer in [p.F_Paste,p.B_Paste]:
  shapes=[(g.m_Uuid.AsString(),g.GetEffectiveShape(layer)) for g in graphics if g.GetLayer()==layer]+[(a.m_Uuid.AsString(),a.GetEffectiveShape(layer)) for f in b.GetFootprints() for a in f.Pads() if a.IsOnLayer(layer)]
  for uid,shape in shapes:
   if shape.Collide(disk):hits.append(dict(layer=b.GetLayerName(layer),object_uuid=uid,drill_overlap=shape.Collide(hole)))
 rows.append(dict(via_uuid=v.m_Uuid.AsString(),paste_hits=hits))
save(E/'paste-via-check.json',dict(board_sha256=digest(E/'inspection/final/main.kicad_pcb'),vias_checked=len(rows),via_copper_overlaps_paste=sum(bool(r['paste_hits']) for r in rows),drill_overlaps_paste=sum(any(h['drill_overlap'] for h in r['paste_hits']) for r in rows),rows=rows));assert not any(r['paste_hits'] for r in rows)
print('All113 via copper/drill vs both paste layers: zero overlaps')
