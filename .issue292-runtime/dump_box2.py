import os, sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
X0, Y0, X1, Y1 = (float(v) for v in os.environ['D_BOX'].split(','))
LAYS = os.environ.get('D_LAYS', 'I2,B').split(',')
for m in MODEL:
    if not m['alive']: continue
    for L, sh in m['shapes'].items():
        if L not in LAYS: continue
        bx = sh.bounds
        if bx[2] < X0 or bx[0] > X1 or bx[3] < Y0 or bx[1] > Y1: continue
        print(L, m['net'], ' '.join(f'{v:.2f}' for v in bx))
        break
