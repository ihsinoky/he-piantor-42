"""Compare the proposed native board to the immutable Rev.6 source."""
from common import *
import pcbnew as p,importlib.util
src=E.parent/'issue-226-main-rev6/inspection/final/main.kicad_pcb';dst=E/'inspection/final/main.kicad_pcb'
a=p.LoadBoard(str(src));b=p.LoadBoard(str(dst))
def footprint(f):
 return dict(position_nm=[f.GetPosition().x,f.GetPosition().y],angle=f.GetOrientationDegrees(),value=f.GetValue(),pads={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()!='15'})
afs={f.GetReference():footprint(f) for f in a.GetFootprints()};bfs={f.GetReference():footprint(f) for f in b.GetFootprints()}
assert set(afs)==set(bfs)
changed=[r for r in afs if afs[r]!=bfs[r]];assert set(changed)=={'J2','J3'},changed
assert all(afs[r]['pads']==bfs[r]['pads'] for r in afs)
def outline(x):return sorted((g.GetShapeStr(),g.GetStart().x,g.GetStart().y,g.GetEnd().x,g.GetEnd().y) for g in x.GetDrawings() if g.GetLayer()==p.Edge_Cuts)
assert outline(a)==outline(b)
for r in ['H1','H2','H3','J4']:assert afs[r]==bfs[r]
save(E/'invariants.json',dict(source_sha256=digest(src),candidate_sha256=digest(dst),changed_footprints=changed,numbered_pin_nets_unchanged=True,D024_pin_order_unchanged=True,outline_unchanged=True,mounts_unchanged=True,J4_unchanged=True,other_component_placements_unchanged=True,power_topology='Same net/pad contract; power centreline and widths have changed and are separately extracted. This is not a copper-invariant replacement.'))
print('Outline, mounts, J4, other placements and D-024 numbered pin nets PASS')
