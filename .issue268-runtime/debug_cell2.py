exec(open('.issue268-runtime/bridge_base.py').read())
import numpy as np
blocked = raster_blocked('GND', 0.3)
def cell(x, y, l=1):
    ix = int(round((x-WIN[0])/STEP)); iy = int(round((y-WIN[2])/STEP))
    return blocked[l][iy, ix]
for y in (130.0, 129.9, 129.8, 129.75, 129.7):
    print('y=%.2f' % y, ''.join('#' if cell(97.9+0.05*i, y) else '.' for i in range(25)), '(x 97.90..99.10)')
# which item blocks (98.55,129.75) on B.Cu?
X = np.array([98.55]); Y = np.array([129.75])
best = []
for it in items:
    if it.net == 'GND': continue
    if 2 not in it.layers: continue
    d = dist_to_item(it, X, Y)[0]
    if d < 0.6: best.append((round(float(d), 3), it.net, it.kind))
print('near items B.Cu:', sorted(best)[:6])
