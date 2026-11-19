src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
import pcbnew as p
from shapely.geometry import Point, LineString
b = g['b']
# tentative rip: RESET_N B tracks with both endpoints in x 77.5..80.5, y 118.5..120.5
# and PAD_SDA B track from its via (79.1,119.3) heading NE
ripped = []
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]
    net = t.GetNetname()
    if net == 'RESET_N' and t.GetLayer() == p.B_Cu and all(77.5 < x < 80.5 and 118.5 < y < 120.5 for x, y in pts):
        ripped.append(t); b.Remove(t)
    elif net == 'PAD_SDA' and t.GetLayer() == p.B_Cu and any(abs(x - 79.1) < 0.2 and abs(y - 119.3) < 0.2 for x, y in pts):
        ripped.append(t); b.Remove(t)
print('tentatively ripped:', len(ripped))
# NOTE: g['items'] is stale now (still contains ripped items) - rebuild by reloading is not possible mid-state;
# instead verify with pcbnew connectivity via DRC later. For A* we need a fresh process.
b.Save(str(g['BPATH']))
