import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
CUTS = {((71.80,120.50),(72.30,121.00)), ((72.30,121.00),(72.35,121.00))}
c = 0
for m in list(MODEL):
    if not m['alive'] or m['net'] != 'ADC_A': continue
    o = m['obj']
    if isinstance(o, p.PCB_VIA): continue
    s, e = o.GetStart(), o.GetEnd()
    k = ((round(mm2(s.x),2), round(mm2(s.y),2)), (round(mm2(e.x),2), round(mm2(e.y),2)))
    if k in CUTS or (k[1], k[0]) in CUTS:
        b.Remove(o); m['alive'] = False; c += 1
p.SaveBoard(DST, b)
print('cut ADC_A items:', c)
