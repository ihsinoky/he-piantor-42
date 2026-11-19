import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
CUTS = {((76.92,111.03),(77.33,110.62)), ((77.33,110.62),(77.38,110.62)), ((77.38,110.62),(77.72,110.28)),
        ((77.72,110.28),(77.88,110.28)), ((77.88,110.28),(78.03,110.12))}
c = 0
for m in list(MODEL):
    if not m['alive'] or m['net'] != 'SYS_3V3': continue
    o = m['obj']
    if isinstance(o, p.PCB_VIA) or 'B' not in m['shapes']: continue
    s, e = o.GetStart(), o.GetEnd()
    k = ((round(mm2(s.x),2), round(mm2(s.y),2)), (round(mm2(e.x),2), round(mm2(e.y),2)))
    if k in CUTS or (k[1], k[0]) in CUTS:
        b.Remove(o); m['alive'] = False; c += 1
p.SaveBoard(DST, b)
print('cut SYS B items:', c)
