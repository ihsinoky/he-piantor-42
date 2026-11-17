"""Trim v2: shorten dangling tracks from their free end to the nearest real
junction; delete the dead GND taper spur east of (123.2,112.3)."""
import pcbnew as p
from shapely.geometry import LineString, Point
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
V = lambda a: p.VECTOR2I(round(a[0] * 1e6), round(a[1] * 1e6))
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')

def connections(pt, net, layer, exclude):
    n = 0
    for o in b.GetTracks():
        if o is exclude or o.GetNetname() != net:
            continue
        if isinstance(o, p.PCB_VIA):
            if Point(xy(o.GetPosition())).distance(Point(pt)) < 0.05:
                n += 1
        elif o.GetLayer() == layer:
            for e in (xy(o.GetStart()), xy(o.GetEnd())):
                if Point(e).distance(Point(pt)) < 0.05:
                    n += 1
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname() == net and a.IsOnLayer(layer) and Point(xy(a.GetPosition())).distance(Point(pt)) < 0.8:
                n += 1
    return n

def junctions_on(t, a, z):
    seg = LineString([a, z]); out = []
    for o in b.GetTracks():
        if o is t or o.GetNetname() != t.GetNetname():
            continue
        if isinstance(o, p.PCB_VIA):
            pt = Point(xy(o.GetPosition()))
            if seg.distance(pt) < 0.30:
                out.append((seg.project(pt), xy(o.GetPosition())))
        elif o.GetLayer() == t.GetLayer():
            for e in (xy(o.GetStart()), xy(o.GetEnd())):
                pt = Point(e)
                if seg.distance(pt) < 0.06:
                    out.append((seg.project(pt), e))
    return sorted(out)

targets = ['7208c3d7-d118-445c-ab6d-298d734594d8', 'e8390f4e-8c28-4316-be3f-402b3d5c1f91',
           'c40f794e-3d54-48b4-9162-9f061a21767f']
tracks = {t.m_Uuid.AsString(): t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA)}
for u in targets:
    t = tracks[u]
    a, z = xy(t.GetStart()), xy(t.GetEnd())
    ca, cz = connections(a, t.GetNetname(), t.GetLayer(), t), connections(z, t.GetNetname(), t.GetLayer(), t)
    js = junctions_on(t, a, z)
    print(f'{t.GetNetname()} {a}->{z} conn {ca}/{cz} junctions {[(round(d,2), p) for d, p in js]}')
    L = LineString([a, z]).length
    if ca == 0 and cz > 0:
        keep_from = max([d for d, _ in js], default=None)
        if keep_from is not None:
            new_a = LineString([a, z]).interpolate(keep_from)
            t.SetStart(V((new_a.x, new_a.y)))
            print(f'  trimmed start to {(round(new_a.x,2), round(new_a.y,2))}')
    elif cz == 0 and ca > 0:
        keep_to = min([d for d, _ in js], default=None)
        if keep_to is not None:
            new_z = LineString([a, z]).interpolate(keep_to)
            t.SetEnd(V((new_z.x, new_z.y)))
            print(f'  trimmed end to {(round(new_z.x,2), round(new_z.y,2))}')
    else:
        print('  skipped (ambiguous)')

# dead taper spur: GND F tracks at y=112.3 with both endpoints x in (123.19, 123.71)
spur = []
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA) or t.GetNetname() != 'GND' or t.GetLayer() != p.F_Cu:
        continue
    a, z = xy(t.GetStart()), xy(t.GetEnd())
    if abs(a[1] - 112.3) < 0.01 and abs(z[1] - 112.3) < 0.01 and 123.19 < a[0] < 123.71 and 123.19 < z[0] < 123.71:
        spur.append(t)
for t in spur:
    b.Remove(t)
print('spur segments removed:', len(spur))
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
p.SaveBoard(f'{E}/main-rev8/routed.kicad_pcb', b)
print('saved')
