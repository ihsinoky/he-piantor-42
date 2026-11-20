import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
TARGETS = {((78.45,122.05),(78.55,121.95)), ((78.55,121.95),(78.95,121.95)),
           ((78.95,121.95),(79.10,121.80)), ((79.10,121.80),(79.10,119.35))}
# keep the vertical (79.10,121.80)-(79.10,119.35)? NO - it is in TARGETS? It is listed; we keep the via end: actually remove only the jog trio + keep vertical.
TARGETS.discard(((79.10,121.80),(79.10,119.35)))
n = 0
for m in list(MODEL):
    if not m['alive'] or m['net'] != 'PAD_SDA': continue
    o = m['obj']
    if isinstance(o, p.PCB_VIA): continue
    s, e = o.GetStart(), o.GetEnd()
    k = ((round(mm(s.x),2), round(mm(s.y),2)), (round(mm(e.x),2), round(mm(e.y),2)))
    if k in TARGETS or (k[1], k[0]) in TARGETS:
        b.Remove(o); m['alive'] = False; n += 1
p.SaveBoard(DST, b)
print('cut SDA jog items:', n)
