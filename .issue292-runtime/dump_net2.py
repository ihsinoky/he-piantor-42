import os, sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
NET = os.environ['D_NET']; LAY = os.environ.get('D_LAY', '')
X0, Y0, X1, Y1 = (float(v) for v in os.environ['D_BOX'].split(','))
for m in MODEL:
    if not m['alive'] or m['net'] != NET: continue
    for L, sh in m['shapes'].items():
        if LAY and L != LAY: continue
        bx = sh.bounds
        if bx[2] < X0 or bx[0] > X1 or bx[3] < Y0 or bx[1] > Y1: continue
        o = m['obj']
        if isinstance(o, p.PCB_VIA):
            print(L, 'VIA @', f"{mm(o.GetPosition().x):.2f},{mm(o.GetPosition().y):.2f}")
        else:
            s, e = o.GetStart(), o.GetEnd()
            print(L, f"TRK ({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f}) w{mm(o.GetWidth()):.2f}")
        break
