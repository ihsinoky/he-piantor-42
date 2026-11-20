import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
tb = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
n = 0
for t in tb.GetTracks():
    if t.GetNetname() != 'ADC_B': continue
    n += 1
    if isinstance(t, p.PCB_VIA):
        print('VIA', round(t.GetPosition().x/1e6, 2), round(t.GetPosition().y/1e6, 2)); continue
    s, e = t.GetStart(), t.GetEnd()
    x0, y0, x1, y1 = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
    if max(x0, x1) <= 90:
        print(t.GetLayerName(), (round(x0, 2), round(y0, 2)), (round(x1, 2), round(y1, 2)), 'w', round(t.GetWidth()/1e6, 2))
print('total ADC_B tracks+vias:', n)
