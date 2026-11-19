"""Place LED tail segments; verify RAW exact-shape clearance >= 0.050 vs other nets on F."""
import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import LineString
SEGS = [((71.10,121.00),(71.10,120.875)), ((71.10,120.875),(72.10,120.875)),
        ((72.10,120.875),(72.21,121.30)), ((72.21,121.30),(72.21,121.85)),
        ((72.21,121.85),(71.95,121.85))]
obs = [(n2, s2) for n2, s2 in all_obs('F') if n2 != 'LED_DRV']
worst = 9.9
for (a, c) in SEGS:
    sh = LineString([a, c]).buffer(0.025, cap_style=2)
    for n2, s2 in obs:
        d = sh.distance(s2)
        if d < worst: worst = d; wn = n2
    print(a, c, 'min dist so far', round(worst, 4), 'vs', wn)
assert worst >= 0.0499, f'FAIL {worst}'
netobj = b.FindNet('LED_DRV')
for (a, c) in SEGS:
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(int(a[0]*1e6), int(a[1]*1e6)))
    t.SetEnd(p.VECTOR2I(int(c[0]*1e6), int(c[1]*1e6)))
    t.SetWidth(int(0.05e6)); t.SetLayer(0)
    t.SetNet(netobj); b.Add(t)
p.SaveBoard(DST, b)
print('LED tail placed, worst raw clearance', round(worst, 4))
