import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for path in ('.issue292-runtime/wmain-work.kicad_pcb', 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'):
    tb = p.LoadBoard(path)
    n = 0; found = False
    for t in tb.GetTracks():
        if t.GetNetname() != 'ADC_B': continue
        n += 1
        if not isinstance(t, p.PCB_VIA):
            s = t.GetStart()
            if abs(s.x/1e6 - 73.15) < 0.01 and abs(s.y/1e6 - 121.15) < 0.01: found = True
    print(path.split('/')[-1], 'ADC_B items:', n, 'F-vertical present:', found)
