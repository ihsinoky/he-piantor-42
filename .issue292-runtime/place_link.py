"""Hand-place a link for NET: segments [(layer,x1,y1,x2,y2,width)] and vias [(x,y)].
Verifies exact clearances (>= CLR) of every new shape vs other nets' copper
(per layer; vias on all layers) BEFORE adding; aborts without saving on any
violation. Usage: kpy.sh place_link.py NET CLR 'F:x1,y1,x2,y2,w;...' 'x,y;...'"""
import pcbnew as p, sys, os
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import LineString, Point

NET = os.environ['L_NET']; CLR = float(os.environ.get('L_CLR', '0.049'))
segs = []
for s in os.environ.get('L_SEGS', '').split(';'):
    if not s: continue
    lay, rest = s.split(':')
    x1, y1, x2, y2, w = [float(v) for v in rest.split(',')]
    segs.append((lay, x1, y1, x2, y2, w))
vias = []
for s in os.environ.get('L_VIAS', '').split(';'):
    if not s: continue
    x, y = [float(v) for v in s.split(',')]
    vias.append((x, y))

bad = []
for lay, x1, y1, x2, y2, w in segs:
    sh = LineString([(x1, y1), (x2, y2)]).buffer(w / 2)
    for n2, s2 in all_obs(lay):
        if n2 != NET and sh.distance(s2) < CLR:
            bad.append(f'seg {lay} ({x1},{y1})-({x2},{y2}) vs {n2} d={sh.distance(s2):.3f}')
for x, y in vias:
    disc = Point(x, y).buffer(0.30)
    for L in ('F', 'I2', 'B'):
        for n2, s2 in all_obs(L):
            if n2 != NET and disc.distance(s2) < CLR:
                bad.append(f'via ({x},{y}) on {L} vs {n2} d={disc.distance(s2):.3f}')
    if OUTLINE.exterior.distance(Point(x, y)) < 0.80:
        bad.append(f'via ({x},{y}) too close to outline')
if bad:
    print('ABORT:'); [print('  ', b) for b in bad]; sys.exit(1)

b = p.LoadBoard(DST)
netobj = b.FindNet(NET)
LAYID = {'F': p.F_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}
for lay, x1, y1, x2, y2, w in segs:
    t = p.PCB_TRACK(b)
    t.SetNet(netobj)
    t.SetLayer(LAYID[lay])
    t.SetWidth(int(w * 1e6))
    t.SetStart(p.VECTOR2I(int(x1 * 1e6), int(y1 * 1e6)))
    t.SetEnd(p.VECTOR2I(int(x2 * 1e6), int(y2 * 1e6)))
    b.Add(t)
for x, y in vias:
    v = p.PCB_VIA(b)
    v.SetNet(netobj)
    v.SetPosition(p.VECTOR2I(int(x * 1e6), int(y * 1e6)))
    v.SetWidth(int(0.6 * 1e6)); v.SetDrill(int(0.3 * 1e6))
    b.Add(v)
p.SaveBoard(DST, b)
print(f'{NET}: placed {len(segs)} segments + {len(vias)} vias, all clearances >= {CLR}')
