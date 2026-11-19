import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for path in ('.issue292-runtime/wmain-work.kicad_pcb', 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'):
    bb = p.LoadBoard(path)
    print('==', path.split('/')[-1])
    for z in bb.Zones():
        if z.GetNetname() != 'GND': continue
        ls = z.GetLayerSet()
        names = [bb.GetLayerName(l) for l in range(32) if ls.Contains(l)]
        try: area = round(z.GetFilledPolysList(z.GetFirstLayer()).Area() / 1e12, 1)
        except Exception: area = 'ERR'
        print('  GND zone layers', names, 'filled area mm2:', area, 'isFilled:', z.IsFilled())
