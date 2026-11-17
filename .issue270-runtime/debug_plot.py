import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

g = json.load(open('geometry.json'))
mp = g['main_rev8_outline']
fig, ax = plt.subplots(figsize=(10, 10))
for side, col in (('left', 'tab:blue'), ('right', 'tab:orange')):
    o = g['wings'][side]['outline']
    ax.plot([c[0] for c in o], [c[1] for c in o], color=col, lw=0.7)
    kx = [k[0] for k in g['wings'][side]['keys']]
    ky = [k[1] for k in g['wings'][side]['keys']]
    ax.plot(kx, ky, '.', color=col, ms=3)
ax.plot([c[0] for c in mp], [c[1] for c in mp], color='red', lw=1.2)
ax.set_aspect('equal')
ax.invert_yaxis()
fig.savefig('debug-layout.png', dpi=110)
print('saved')
