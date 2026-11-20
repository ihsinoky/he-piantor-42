import math, sys
from pathlib import Path
import pcbnew
MM = 1e6
TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
nets = {b.FindNet(n).GetNetCode() for n in ('HALL_3V3', 'HALL_3V3_SRC')}
nodes = {}
def nid(x, y):
    key = (round(x, 3), round(y, 3))
    if key not in nodes:
        nodes[key] = len(nodes)
    return nodes[key]
adj = {}
def link(a, c):
    adj.setdefault(a, set()).add(c)
    adj.setdefault(c, set()).add(a)
for t in list(b.GetTracks()):
    if t.GetNetCode() not in nets:
        continue
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        link(nid(p.x / MM, p.y / MM), nid(p.x / MM, p.y / MM))
    else:
        s, e = t.GetStart(), t.GetEnd()
        link(nid(s.x / MM, s.y / MM), nid(e.x / MM, e.y / MM))
src = nid(103.05, 129.0)
shunt1 = nid(120.156, 130.0)
shunt2 = nid(121.844, 130.0)
link(shunt1, shunt2)
seen = {src}
stack = [src]
while stack:
    n = stack.pop()
    for m in adj.get(n, ()):
        if m not in seen:
            seen.add(m)
            stack.append(m)
inv = {v: k for k, v in nodes.items()}
print('nodes:', len(nodes), 'reached:', len(seen))
print('shunt1 reached:', shunt1 in seen, 'shunt2 reached:', shunt2 in seen)
print('HA0 VCC reached:', nid(49.75, 73.3) in seen)
# if shunt1 not reached, find the SRC-side frontier: list reached nodes with y<135 sorted by x desc
if shunt1 not in seen:
    reach = sorted(inv[n] for n in seen if inv[n][1] > 125)
    print('reached strip nodes:', reach[:20])
