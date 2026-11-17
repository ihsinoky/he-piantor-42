"""Hand-trim the 5 dangling tracks on the final Main board: delete a track only
if no other copper touches its interior (no T-junction); otherwise shorten it
to the junction. Then refill + save to routed.kicad_pcb for the final audit."""
import pcbnew as p
from shapely.geometry import LineString, Point
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
V = lambda a: p.VECTOR2I(round(a[0] * 1e6), round(a[1] * 1e6))
UUIDS = ['0087a2d6-5c6f-4087-8b73-06103a9109dd', '1a379d9b-e304-4ab5-8a73-dbb7c3cdc05e',
         '7208c3d7-d118-445c-ab6d-298d734594d8', 'e8390f4e-8c28-4316-be3f-402b3d5c1f91',
         'c40f794e-3d54-48b4-9162-9f061a21767f']
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')
tracks = {t.m_Uuid.AsString(): t for t in b.GetTracks()}
for u in UUIDS:
    t = tracks.get(u)
    if t is None:
        print(u, 'NOT FOUND'); continue
    a, z = xy(t.GetStart()), xy(t.GetEnd())
    seg = LineString([a, z])
    # interior junctions: other tracks/vias/pads of the same net touching the
    # segment at a point that is not one of its endpoints
    junctions = []
    for o in b.GetTracks():
        if o is t or o.GetNetname() != t.GetNetname():
            continue
        if isinstance(o, p.PCB_VIA):
            pt = Point(xy(o.GetPosition()))
            if seg.distance(pt) < 0.31 and pt.distance(Point(a)) > 0.31 and pt.distance(Point(z)) > 0.31:
                junctions.append(xy(o.GetPosition()))
        elif o.GetLayer() == t.GetLayer():
            for e in (xy(o.GetStart()), xy(o.GetEnd())):
                pt = Point(e)
                if seg.distance(pt) < p.ToMM(o.GetWidth()) / 2 + 0.01 and pt.distance(Point(a)) > 0.06 and pt.distance(Point(z)) > 0.06:
                    junctions.append(e)
    print(f'{t.GetNetname()} ({a})->({z}) junctions: {junctions}')
    if not junctions:
        b.Remove(t)
        print('  deleted')
    else:
        print('  KEPT (T-junction) - not trimmed by hand')
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
p.SaveBoard(f'{E}/main-rev8/routed.kicad_pcb', b)
print('saved')
