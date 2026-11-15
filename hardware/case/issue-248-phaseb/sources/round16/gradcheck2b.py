"""Term-isolated FD check for var 11 (strand 1 M2.z)."""
import sys
sys.argv = ['opt_feed_curr.py', '--stage', '1', '--init', 'state', '--wmul', '1.0', '--trimul', '3.0']
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round16')
import numpy as np
import opt_feed_curr as ofc

x = ofc.X0.copy(); K = 11; h = 1e-6
def fd_and_an():
    f0, g0 = ofc.objective(x)
    xp = x.copy(); xp[K] += h
    fp, _ = ofc.objective(xp)
    return (fp - f0) / h, g0[K]
WB0, WW0, WC0, TR0 = ofc.WB, ofc.WW, ofc.WC, ofc.ARGS.trimul
for name, (wb, ww, wc, tr) in {
    'ALL': (WB0, WW0, WC0, TR0), 'BODY': (WB0, 0.0, 0.0, 0.0),
    'WW': (0.0, WW0, 0.0, 0.0), 'CEIL': (0.0, 0.0, WC0, 0.0),
    'TRIM': (0.0, 0.0, 0.0, TR0), 'REST': (0.0, 0.0, 0.0, 0.0)}.items():
    ofc.WB, ofc.WW, ofc.WC, ofc.ARGS.trimul = wb, ww, wc, tr
    fd, an = fd_and_an()
    print(name, 'FD', round(float(fd), 2), 'analytic', round(float(an), 2), flush=True)
