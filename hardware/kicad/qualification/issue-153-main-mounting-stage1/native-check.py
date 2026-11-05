"""Read-only KiCad 9 effective-shape crosscheck; no SaveBoard/refill/router calls.

Run at repository root with pcbnew on PYTHONPATH. JSON to stdout.
Uses the independent stdlib survey for comparison, not for native geometry.
"""
from pathlib import Path
import hashlib
import json
import pcbnew
import measure

inv=measure.inventory()
survey=measure.survey(inv)
path=measure.ROOT/measure.PCB
before=hashlib.sha256(path.read_bytes()).hexdigest()
board=pcbnew.LoadBoard(str(path))
def uid(i): return i.m_Uuid.AsString()
def mm(n): return pcbnew.ToMM(n)
def xy(v): return [mm(v.x),mm(v.y)]
padmap={uid(p):p for f in board.GetFootprints() for p in f.Pads()}
trackmap={uid(t):t for t in board.GetTracks() if not isinstance(t,pcbnew.PCB_VIA)}
viamap={uid(t):t for t in board.GetTracks() if isinstance(t,pcbnew.PCB_VIA)}
assert len(padmap)==199 and len(trackmap)==540 and len(viamap)==66
for p in inv['pads']:
    n=padmap[p['uuid']]
    assert all(abs(a-b)<1e-6 for a,b in zip(p['xy'],xy(n.GetPosition())))
    assert abs(p['angle']-n.GetOrientationDegrees())<1e-6
    assert p['size']==xy(n.GetSize())
groups={
    'pads':[(k,p.GetEffectiveShape(pcbnew.F_Cu)) for k,p in padmap.items() if p.GetAttribute()!=pcbnew.PAD_ATTRIB_NPTH],
    'tracks':[(k,t.GetEffectiveShape(t.GetLayer())) for k,t in trackmap.items()],
    'vias':[(k,t.GetEffectiveShape(pcbnew.F_Cu)) for k,t in viamap.items()]}
holes=[(uid(p),p.GetEffectiveHoleShape()) for p in padmap.values() if p.GetDrillSize().x>0]
holes += [(uid(v),v.GetEffectiveHoleShape()) for v in viamap.values()]
assert len(holes)==72
native_lines=sorted((tuple(xy(g.GetStart())),tuple(xy(g.GetEnd()))) for g in board.GetDrawings() if g.GetLayer()==pcbnew.F_CrtYd)
parsed=measure.parse(path)
parsed_lines=sorted((tuple(measure.pair(g,'start')),tuple(measure.pair(g,'end'))) for g in measure.children(parsed,'gr_line') if measure.child(g,'layer')[1]=='F.CrtYd')
assert native_lines==parsed_lines and len(native_lines)==188
court_shapes=[]
for c in inv['board_graphic_courtyards']:
    poly=pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x,y in c['points']:
        poly.Append(pcbnew.FromMM(x),pcbnew.FromMM(y))
    court_shapes.append((c['ref'],poly))
rows=[]
for r in survey['candidates']:
    pos=pcbnew.VECTOR2I(*[pcbnew.FromMM(x) for x in r['xy']])
    circle=pcbnew.SHAPE_CIRCLE(pos,pcbnew.FromMM(2.5))
    drill=pcbnew.SHAPE_CIRCLE(pos,pcbnew.FromMM(1.1))
    checks={}
    for key,items in groups.items():
        ds=[(mm(shape.Distance(pos)),uuid) for uuid,shape in items]
        d,k=min(ds)
        hits=sorted(uuid for uuid,shape in items if shape.Collide(circle))
        # All chosen points are off exact tangencies, so inclusive API collision matches strict math.
        expected=r['groups'][key]
        assert abs(d-expected['center_to_copper'])<=2e-6,(r['label'],key,d,expected['center_to_copper'])
        assert hits==sorted(h['item']['uuid'] for h in expected['keepout_hits']),(r['label'],key,hits)
        checks[key]=dict(nearest_uuid=k,center_to_copper_mm=d,keepout_gap_mm=d-2.5,keepout_hit_uuids=hits)
    hd,huid=min((mm(shape.Distance(pos)),uuid) for uuid,shape in holes)
    assert abs(hd-1.1-r['nearest_existing_drill']['proposed_drill_edge_gap'])<=2e-6
    cd,cref=min((max(0,mm(poly.Distance(pos))-.025),ref) for ref,poly in court_shapes)
    assert abs(cd-r['actual_courtyard_nearest']['center_distance'])<=2e-6
    zones=[]
    for z in board.Zones():
        for layer in board.GetEnabledLayers().CuStack():
            if not z.IsOnLayer(layer): continue
            shape=z.GetFilledPolysList(layer)
            zones.append(dict(uuid=uid(z),net=z.GetNetname(),layer=board.GetLayerName(layer),
                disk_5mm_hits_existing_fill=shape.Collide(circle),drill_2_2mm_hits_existing_fill=shape.Collide(drill)))
    rows.append(dict(label=r['label'],xy_mm=r['xy'],groups=checks,zones=zones,
        nearest_existing_drill=dict(uuid=huid,edge_gap_mm=hd-1.1),
        nearest_actual_courtyard=dict(ref=cref,center_distance_mm=cd,keepout_gap_mm=cd-2.5)))
assert hashlib.sha256(path.read_bytes()).hexdigest()==before
print(json.dumps(dict(status='pass',kicad=pcbnew.GetBuildVersion(),board_sha256=before,
    all_pad_positions_sizes_orientations_checked=199,existing_drills_checked=72,
    courtyard_line_coordinates_checked=188,courtyard_polygons_checked=40,
    candidates_checked=len(rows),maximum_distance_tolerance_mm=.000002,
    method='Native GetEffectiveShape Distance/Collide on pad/track/via; saved filled zone polygons separately. No writes or refill.',
    rows=rows),indent=2))
