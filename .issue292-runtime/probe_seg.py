import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(round(s.x/1e6, 2), round(s.y/1e6, 2)), (round(e.x/1e6, 2), round(e.y/1e6, 2))]
    if (81.2, 103.55) in pts or (84.25, 103.55) in pts:
        print(t.GetNetname(), t.GetLayerName(), pts, 'w', round(t.GetWidth()/1e6, 2))
