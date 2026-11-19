import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for t in b.GetTracks():
    if t.GetNetname() != 'LED_DRV' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    x0, y0, x1, y1 = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
    if max(x0, x1) >= 73.0 and min(x0, x1) <= 77.5 and max(y0, y1) >= 110.5 and min(y0, y1) <= 116.5:
        print(t.GetLayerName(), (round(x0, 3), round(y0, 3)), (round(x1, 3), round(y1, 3)), 'w', round(t.GetWidth()/1e6, 3))
