import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
tb = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm2(v): return v / 1e6
for t in tb.GetTracks():
    n = t.GetNetname()
    if n not in ('LED_DRV', 'GND'): continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); print(n, 'VIA', f"{mm2(v.x):.2f},{mm2(v.y):.2f}")
    else:
        s, e = t.GetStart(), t.GetEnd()
        bx = (min(mm2(s.x), mm2(e.x)), min(mm2(s.y), mm2(e.y)), max(mm2(s.x), mm2(e.x)), max(mm2(s.y), mm2(e.y)))
        if bx[2] < 70.3 or bx[0] > 72.2 or bx[3] < 120.8 or bx[1] > 122.2: continue
        print(n, 'TRK', f"({mm2(s.x):.2f},{mm2(s.y):.2f})-({mm2(e.x):.2f},{mm2(e.y):.2f})", 'L', t.GetLayer(), 'w', mm2(t.GetWidth()))
