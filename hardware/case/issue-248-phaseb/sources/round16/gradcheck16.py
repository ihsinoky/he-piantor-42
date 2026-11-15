"""FD-check opt_feed_curr's analytic gradient on ALL 84 vars at X0."""
import sys
sys.argv = ['opt_feed_curr.py', '--stage', sys.argv[1] if len(sys.argv) > 1 else '1',
            '--init', 'state', '--wmul', '1.0', '--trimul', '3.0']
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round16')
import numpy as np
import opt_feed_curr as ofc

x = ofc.X0.copy()
f0, g0 = ofc.objective(x)
print('f0', round(float(f0), 2), flush=True)
bad = []
for k in range(84):
    xp = x.copy(); xp[k] += 1e-6
    fp, _ = ofc.objective(xp)
    fd = (fp - f0) / 1e-6
    err = abs(fd - g0[k])
    rel = err / max(1.0, abs(fd), abs(g0[k]))
    if rel > 0.05 and err > 0.5:
        bad.append((k, round(float(fd), 2), round(float(g0[k]), 2), round(float(err), 2)))
print('vars checked 84; mismatches:', len(bad), flush=True)
for b in bad[:20]: print('  var', b, flush=True)
