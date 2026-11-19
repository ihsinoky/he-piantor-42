import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
def cut(net, a, c):
    n = 0
    for m in list(MODEL):
        if not m['alive'] or m['net'] != net: continue
        o = m['obj']
        if isinstance(o, p.PCB_VIA): continue
        s, e = o.GetStart(), o.GetEnd()
        k = ((round(mm2(s.x),2), round(mm2(s.y),2)), (round(mm2(e.x),2), round(mm2(e.y),2)))
        if k == (a, c) or k == (c, a):
            b.Remove(o); m['alive'] = False; n += 1
    return n
print('BTN cut:', cut('BTN', (72.85,119.35), (72.85,121.75)))
print('PAD_DR cut:', cut('PAD_DR', (76.10,119.45), (76.10,121.40)))
p.SaveBoard(DST, b)
