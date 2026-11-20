import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
net = ARGS[0]; x0, y0, x1, y1 = [float(v) for v in ARGS[1:5]]
n = 0
for m in MODEL:
    if not m['alive'] or m['net'] != net: continue
    if any(x0 <= (sh.bounds[0] + sh.bounds[2]) / 2 <= x1 and y0 <= (sh.bounds[1] + sh.bounds[3]) / 2 <= y1
           for sh in m['shapes'].values()):
        b.Remove(m['obj']); m['alive'] = False; n += 1
print(net, 'cut', n, 'items in bbox')
p.SaveBoard(DST, b)
print('saved')
