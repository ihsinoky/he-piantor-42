import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# case frame: cx = bx - 100, cy = by - 70  (fitted pose, pose-verification.json)
def C(p): return (p[0]-100.0, p[1]-70.0)

outline_board = [
 (98.0,75.7321),(82.0535,103.3522),(81.7441,103.458),(66.7282,115.1898),
 (70.9735,122.5433),(64.1073,134.4359),(66.1073,137.9),(133.8927,137.9),
 (135.8927,134.4359),(128.9362,122.3869),(132.9488,115.4381),(119.8213,103.1964),
 (117.8562,103.1958),(102.0,75.7321)]
cur = [C(p) for p in outline_board] + [C(outline_board[0])]

# candidate (b): right half kept; left half = mirror of right half about cx=0
right_chain = [(102.0,75.7321),(117.8562,103.1958),(119.8213,103.1964),
 (132.9488,115.4381),(128.9362,122.3869),(135.8927,134.4359),(133.8927,137.9),
 (100.0,137.9)]
left_chain = [(200.0-x, y) for (x, y) in reversed(right_chain)]
cand_board = right_chain + left_chain[1:]
cand = [C(p) for p in cand_board] + [C(cand_board[0])]

d = json.load(open('.issue275-runtime/extract.json'))
def pads(ref):
    f = next(x for x in d['footprints'] if x['ref'] == ref)
    return [C(tuple(p['abs'])) for p in sorted(f['pads'], key=lambda p: int(p['num']) if p['num'].isdigit() else 99) if p['num'].isdigit()]
def rot2d(x, y, deg):
    r = math.radians(deg); return (x*math.cos(r)-y*math.sin(r), x*math.sin(r)+y*math.cos(r))
j2 = next(x for x in d['footprints'] if x['ref'] == 'J2')
locals_ = []
for p in j2['pads']:
    if not p['num'].isdigit(): continue
    lx, ly = p['abs'][0]-j2['at'][0], p['abs'][1]-j2['at'][1]
    locals_.append(rot2d(lx, ly, -j2['rot']))
newc, newr = (75.745202, 111.823895), 43.0
newpads = []
for ux, uy in locals_:
    rx, ry = rot2d(ux, uy, newr)
    newpads.append(C((newc[0]+rx, newc[1]+ry)))

fig = plt.figure(figsize=(13.5, 5.6))
ax0 = fig.add_subplot(1, 3, 1)
ax0.plot(*zip(*cur), color='0.45', lw=1.4, label='Main Rev.9 outline (current)')
ax0.plot(*zip(*cand), color='tab:blue', lw=1.6, label='Symmetric (candidate b)')
ax0.axvline(0, color='k', ls='--', lw=0.8)
ax0.set_title('Main board, fitted case frame\n(grey = Rev.9, blue = symmetric pair)')
ax0.set_xlabel('case frame X [mm]'); ax0.set_ylabel('case frame Y [mm]')
ax0.set_aspect('equal'); ax0.legend(fontsize=7.5, loc='lower center'); ax0.grid(alpha=0.25)

for ax, site, xr, yr, ttl in (
    (fig.add_subplot(1, 3, 2), 'J2', (-38, -8), (28, 56), 'LEFT tab (J2 site) - CHANGES'),
    (fig.add_subplot(1, 3, 3), 'J3', (8, 38), (28, 56), 'RIGHT tab (J3 site) - unchanged')):
    ax.plot(*zip(*cur), color='0.45', lw=1.6)
    ax.plot(*zip(*cand), color='tab:blue', lw=1.8)
    ax.axvline(0, color='k', ls='--', lw=0.8)
    pp = pads(site)
    ax.plot(*zip(*pp), 'o', ms=3.5, color='0.45', label='connector pads (Rev.9)')
    if site == 'J2':
        ax.plot(*zip(*newpads), 'o', ms=3.5, color='tab:blue', label='pads at symmetric pose')
    ax.set_xlim(*xr); ax.set_ylim(*yr); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_title(ttl); ax.set_xlabel('case frame X [mm]'); ax.legend(fontsize=7.5)

fig.tight_layout()
fig.savefig('.issue275-runtime/fig-sym-tabs.png', dpi=200)
print('saved')
