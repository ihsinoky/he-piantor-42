import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
n = 0
for m in list(MODEL):
    if not m['alive'] or m['net'] != 'MUX_A0': continue
    o = m['obj']
    if isinstance(o, p.PCB_VIA):
        v = o.GetPosition()
        if abs(mm2(v.x) - 74.90) < 0.01 and abs(mm2(v.y) - 112.73) < 0.01:
            b.Remove(o); m['alive'] = False; n += 1
p.SaveBoard(DST, b)
print('deleted A0 via:', n)
