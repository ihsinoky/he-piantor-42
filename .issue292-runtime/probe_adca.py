import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
b = load_board()
for t in b.GetTracks():
    if t.GetNetname() != 'ADC_A': continue
    L = t.GetLayerName()
    if isinstance(t, p.PCB_VIA):
        print(L, 'VIA', round(t.GetPosition().x/1e6, 3), round(t.GetPosition().y/1e6, 3))
    else:
        s, e = t.GetStart(), t.GetEnd()
        x0, y0, x1, y1 = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
        if max(x0, x1) >= 70.0 and min(x0, x1) <= 75.5 and max(y0, y1) >= 116.5 and min(y0, y1) <= 121.5:
            print(L, 'TRK', (round(x0, 3), round(y0, 3)), (round(x1, 3), round(y1, 3)), 'w', t.GetWidth()/1e6)
