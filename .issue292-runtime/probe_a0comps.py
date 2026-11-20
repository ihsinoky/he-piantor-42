import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
# replicate component analysis: use the router's own grouping via a K-style dry run is complex;
# instead list all MUX_A0 items in the west zone grouped by layer
for m in MODEL:
    if not m['alive'] or m['net'] != 'MUX_A0': continue
    for L, sh in m['shapes'].items():
        x0, y0, x1, y1 = sh.bounds
        if x1 >= 69.5 and x0 <= 76 and y1 >= 112 and y0 <= 126:
            print(L, 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
