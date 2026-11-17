"""F2 probe: list #261 audit bodies; extract Main PCB XY footprint + tray bounds."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
from build123d import Box, Pos

bodies = FF.bodies_at(17, -2.65)
names = [n for n, s in bodies]
print('total bodies:', len(names))
sel = [n for n in names if 'ain' in n or 'tray' in n.lower()]
print('main/tray bodies:', sel)
out = {}
for n, s in bodies:
    if n not in sel:
        continue
    bb = s.bounding_box()
    out[n] = {'min': [round(bb.min.X, 2), round(bb.min.Y, 2), round(bb.min.Z, 2)],
              'max': [round(bb.max.X, 2), round(bb.max.Y, 2), round(bb.max.Z, 2)],
              'volume': round(s.volume, 1)}
print(json.dumps(out, indent=1))
# Main PCB footprint: intersect with a thin slab at mid-Z of the board
for n, s in bodies:
    if 'Main' in n and 'PCB' in n.upper():
        bb = s.bounding_box(); zmid = (bb.min.Z + bb.max.Z) / 2
        slab = Pos(bb.center().X, bb.center().Y, zmid) * Box(1000, 1000, 0.1)
        sec = s & slab
        verts = sorted({(round(v.X, 2), round(v.Y, 2)) for v in sec.vertices()})
        print(n, 'mid-Z section vertices:', len(verts))
        json.dump(verts, open('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime/f2-main-section.json', 'w'))
