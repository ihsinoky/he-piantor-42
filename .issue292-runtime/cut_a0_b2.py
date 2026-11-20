import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
X0, Y0, X1, Y1 = 75.42, 111.85, 76.15, 112.35
n = 0
for m in list(MODEL):
    if not m['alive'] or m['net'] != 'MUX_A0': continue
    o = m['obj']
    if isinstance(o, p.PCB_VIA): continue
    if 'B' not in m['shapes']: continue
    s, e = o.GetStart(), o.GetEnd()
    for (px, py) in ((mm2(s.x), mm2(s.y)), (mm2(e.x), mm2(e.y))):
        if X0 <= px <= X1 and Y0 <= py <= Y1:
            b.Remove(o); m['alive'] = False; n += 1; break
p.SaveBoard(DST, b)
print('cut A0 B items:', n)
