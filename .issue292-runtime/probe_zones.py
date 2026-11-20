import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for path in ('.issue292-runtime/wmain-work.kicad_pcb', 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'):
    bb = p.LoadBoard(path)
    print('==', path.split('/')[-1])
    for z in bb.Zones():
        fp = z.GetFilledPolysList(z.GetFirstLayer()) if z.GetZoneName() is not None else None
        try:
            area = z.GetFilledPolysList(z.GetFirstLayer()).Area() / 1e12
        except Exception as ex:
            area = f'ERR {ex}'
        print('  zone', z.GetZoneName(), 'net', z.GetNetname(), 'layer', z.GetFirstLayer(), 'filled area mm2:', area)
