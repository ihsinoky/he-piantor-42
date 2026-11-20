import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for t in b.GetTracks():
    if t.GetNetname() != 'MUX_A2': continue
    if isinstance(t, p.PCB_VIA):
        print('VIA', round(t.GetPosition().x/1e6, 2), round(t.GetPosition().y/1e6, 2)); continue
    s, e = t.GetStart(), t.GetEnd()
    x0, y0, x1, y1 = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
    if max(x0, x1) >= 72.4 and min(x0, x1) <= 73.6 and max(y0, y1) >= 120.5 and min(y0, y1) <= 125.5:
        print(t.GetLayerName(), (round(x0, 2), round(y0, 2)), (round(x1, 2), round(y1, 2)), 'w', round(t.GetWidth()/1e6, 2))
