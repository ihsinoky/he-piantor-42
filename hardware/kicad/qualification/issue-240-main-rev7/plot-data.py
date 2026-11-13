from common import *
import pcbnew as p
b=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'));rows=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):continue
 rows.append(dict(layer=b.GetLayerName(t.GetLayer()),net=t.GetNetname(),width=p.ToMM(t.GetWidth()),xy=[[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]]))
edge=[[[p.ToMM(g.GetStart().x),p.ToMM(g.GetStart().y)],[p.ToMM(g.GetEnd().x),p.ToMM(g.GetEnd().y)]] for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts]
pads=[dict(ref=f.GetReference(),number=a.GetNumber(),xy=[p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)]) for f in b.GetFootprints() for a in f.Pads() if f.GetReference() in ['J2','J3','J4','H1','H2','H3']]
save(E/'drawings/plot-data.json',dict(board_sha256=digest(E/'inspection/final/main.kicad_pcb'),tracks=rows,edges=edge,pads=pads))
